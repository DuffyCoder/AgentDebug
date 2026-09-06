"""Cross-source reconciliation for canonical OpenClaw traces."""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any, Iterable, Mapping, Optional

from ._common import normalize_tool_name, stable_id, stable_json, unique_dicts
from .models import (
    AssistantTurn,
    CanonicalMessage,
    CanonicalRun,
    CanonicalTask,
    CanonicalTrace,
    ContentBlock,
    DispatchStatus,
    MessageRole,
    SourceKind,
    ToolCall,
    ToolCallStatus,
    ToolDispatch,
    ToolResult,
    ToolResultStatus,
    TraceFragment,
    merge_source_refs,
)


_SOURCE_PRIORITY = {
    SourceKind.SESSION_V3: 0,
    SourceKind.RUNTIME_V1: 1,
    SourceKind.CLAW_EVAL: 2,
    SourceKind.MANIFEST: 3,
    SourceKind.TASK: 4,
    SourceKind.CANONICAL: 5,
}


def _priority(entity: Any) -> int:
    refs = getattr(entity, "source_refs", None) or []
    if refs:
        return _SOURCE_PRIORITY.get(refs[0].source_kind, 99)
    return 99


def _block_payload(block: ContentBlock) -> Mapping[str, Any]:
    data = block.data
    if isinstance(data, Mapping) and isinstance(data.get("source_block"), Mapping):
        return data["source_block"]
    return data if isinstance(data, Mapping) else {}


def _message_semantic_key(message: CanonicalMessage) -> str:
    call_ids: list[str] = []
    result_ids: list[str] = []
    for block in message.content_blocks:
        data = _block_payload(block)
        if block.block_type == "tool_call":
            value = (
                data.get("id")
                or data.get("toolCallId")
                or data.get("tool_use_id")
                or data.get("call_id")
            )
            if value is not None:
                call_ids.append(str(value))
        elif block.block_type == "tool_result":
            value = (
                data.get("tool_use_id")
                or data.get("toolCallId")
                or data.get("call_id")
            )
            if value is not None:
                result_ids.append(str(value))
    metadata = message.metadata
    if not result_ids:
        value = (
            metadata.get("toolCallId")
            or metadata.get("tool_use_id")
            or metadata.get("call_id")
        )
        if value is not None:
            result_ids.append(str(value))
    if result_ids:
        return stable_json(["tool_results", result_ids])
    visible = [
        block.text or ""
        for block in message.content_blocks
        if block.block_type == "text"
    ]
    reasoning = [
        block.text or ""
        for block in message.content_blocks
        if block.block_type in {"thinking", "reasoning"}
    ]
    if message.role == MessageRole.ASSISTANT and (visible or reasoning):
        # Some session providers omit toolCall blocks even though Claw-Eval
        # observed the dispatch.  Completion text/reasoning aligns those views.
        return stable_json(["assistant_content", reasoning, visible])
    if call_ids:
        return stable_json(["assistant_calls", call_ids])
    return stable_json([message.role.value, visible if visible else reasoning])


def _turn_semantic_key(turn: AssistantTurn) -> str:
    # Content is the most portable identity: certain OpenClaw provider adapters
    # recorded thinking + stopReason=toolUse but lost the actual call block,
    # while the corresponding Claw-Eval message retained the call ID.
    if turn.thinking_texts or turn.text_outputs:
        return stable_json(["content", turn.thinking_texts, turn.text_outputs])
    if turn.tool_call_ids:
        return stable_json(["calls", turn.tool_call_ids])
    if turn.response_id:
        return stable_json(["response", turn.response_id])
    return stable_json(["empty", turn.stop_reason, turn.error_message])


def _merge_metadata(primary: dict[str, Any], alternate: dict[str, Any]) -> None:
    variants = primary.setdefault("source_variants", [])
    summary = {
        "source_format": alternate.get("source_format"),
        "trace_id": alternate.get("trace_id"),
        "snapshot_index": alternate.get("snapshot_index"),
    }
    if summary not in variants:
        variants.append(summary)


def _merge_entity_observations(primary: Any, alternate: Any) -> None:
    primary.source_refs = merge_source_refs(
        primary.source_refs, alternate.source_refs
    )
    _merge_metadata(primary.metadata, alternate.metadata)
    if isinstance(primary, AssistantTurn) and isinstance(alternate, AssistantTurn):
        primary.tool_call_ids = list(
            dict.fromkeys([*primary.tool_call_ids, *alternate.tool_call_ids])
        )
        primary.tool_result_ids = list(
            dict.fromkeys([*primary.tool_result_ids, *alternate.tool_result_ids])
        )
        for field_name in (
            "stop_reason",
            "error_message",
            "provider",
            "model",
            "model_api",
            "response_id",
            "run_id",
        ):
            if getattr(primary, field_name) is None:
                setattr(primary, field_name, getattr(alternate, field_name))
        if not primary.usage and alternate.usage:
            primary.usage = copy.deepcopy(alternate.usage)


def _branch_selection(fragments: list[TraceFragment]) -> dict[str, Any]:
    """Resolve the active session path from the latest runtime transcript leaf.

    Session v3 is a graph, not inherently a linear transcript.  When runtime
    evidence names the compiled transcript leaf, only descendants of that anchor
    can be active.  A unique terminal message selects the path; multiple terminal
    messages are intentionally left unresolved for the integrity gate.
    """

    session_events = [
        event
        for fragment in fragments
        if fragment.source_kind == SourceKind.SESSION_V3
        for event in fragment.events
        if isinstance(event.raw, Mapping)
    ]
    if not session_events:
        return {"status": "not_applicable", "reason": "no_session_events"}

    event_by_raw_id: dict[str, Any] = {}
    parent_by_raw_id: dict[str, Optional[str]] = {}
    children: dict[str, list[str]] = defaultdict(list)
    message_ids: set[str] = set()
    for event in session_events:
        raw_id = event.raw.get("id")
        if raw_id is None:
            continue
        entity_id = str(raw_id)
        event_by_raw_id[entity_id] = event
        parent = event.raw.get("parentId") or event.raw.get("parent_id")
        parent_id = str(parent) if parent is not None else None
        parent_by_raw_id[entity_id] = parent_id
        if parent_id is not None:
            children[parent_id].append(entity_id)
        if event.raw.get("type") == "message":
            message_ids.add(entity_id)

    if not message_ids:
        return {"status": "not_applicable", "reason": "no_session_messages"}

    transcript_leaf_ids: list[str] = []
    for fragment in fragments:
        if fragment.source_kind != SourceKind.RUNTIME_V1:
            continue
        for event in fragment.events:
            if event.event_type != "context.compiled" or not isinstance(
                event.raw, Mapping
            ):
                continue
            data = event.raw.get("data")
            if not isinstance(data, Mapping):
                continue
            leaf = data.get("transcriptLeafId")
            if leaf is not None:
                transcript_leaf_ids.append(str(leaf))

    selected_anchor = transcript_leaf_ids[-1] if transcript_leaf_ids else None
    if selected_anchor is not None and selected_anchor not in event_by_raw_id:
        return {
            "status": "missing_anchor",
            "reason": "latest runtime transcriptLeafId is absent from session",
            "transcript_leaf_ids": transcript_leaf_ids,
            "selected_anchor_id": selected_anchor,
            "candidate_leaf_ids": [],
        }
    if selected_anchor is None and not any(
        parent_by_raw_id.get(message_id) in event_by_raw_id
        for message_id in message_ids
    ):
        return {
            "status": "not_applicable",
            "reason": "session messages do not expose a parent graph",
            "transcript_leaf_ids": [],
        }

    allowed_ids: set[str]
    if selected_anchor is not None:
        allowed_ids = set()
        pending = [selected_anchor]
        while pending:
            entity_id = pending.pop()
            if entity_id in allowed_ids:
                continue
            allowed_ids.add(entity_id)
            pending.extend(children.get(entity_id, []))
    else:
        allowed_ids = set(event_by_raw_id)

    def has_message_descendant(entity_id: str) -> bool:
        pending = list(children.get(entity_id, []))
        seen: set[str] = set()
        while pending:
            child = pending.pop()
            if child in seen or child not in allowed_ids:
                continue
            seen.add(child)
            if child in message_ids:
                return True
            pending.extend(children.get(child, []))
        return False

    terminal_messages = sorted(
        entity_id
        for entity_id in message_ids & allowed_ids
        if not has_message_descendant(entity_id)
    )
    if len(terminal_messages) != 1:
        return {
            "status": "ambiguous",
            "reason": "session graph has multiple possible active terminal messages",
            "transcript_leaf_ids": transcript_leaf_ids,
            "selected_anchor_id": selected_anchor,
            "candidate_leaf_ids": terminal_messages,
        }

    active_leaf = terminal_messages[0]
    active_raw_ids: list[str] = []
    seen_path: set[str] = set()
    current: Optional[str] = active_leaf
    while current is not None and current not in seen_path:
        seen_path.add(current)
        active_raw_ids.append(current)
        current = parent_by_raw_id.get(current)
    active_raw_ids.reverse()
    active_message_ids = [
        entity_id for entity_id in active_raw_ids if entity_id in message_ids
    ]
    return {
        "status": "selected",
        "reason": (
            "selected from latest runtime transcriptLeafId"
            if selected_anchor is not None
            else "session graph has one terminal message"
        ),
        "transcript_leaf_ids": transcript_leaf_ids,
        "selected_anchor_id": selected_anchor,
        "active_leaf_id": active_leaf,
        "active_raw_ids": active_raw_ids,
        "active_message_ids": active_message_ids,
        "candidate_leaf_ids": [active_leaf],
    }


def _select_session_branch(
    fragments: list[TraceFragment], selection: Mapping[str, Any]
) -> list[TraceFragment]:
    """Filter session-derived entities to the selected path, retaining events."""

    if selection.get("status") != "selected":
        return fragments
    active_message_ids = {
        str(value) for value in selection.get("active_message_ids", [])
    }
    active_turn_ids = {f"turn:{message_id}" for message_id in active_message_ids}
    active_raw_ids = {str(value) for value in selection.get("active_raw_ids", [])}

    selected: list[TraceFragment] = []
    for fragment in fragments:
        if fragment.source_kind != SourceKind.SESSION_V3:
            selected.append(fragment)
            continue
        event_raw_ids = {
            event.event_id: str(event.raw.get("id"))
            for event in fragment.events
            if isinstance(event.raw, Mapping) and event.raw.get("id") is not None
        }
        filtered = copy.copy(fragment)
        filtered.messages = [
            item for item in fragment.messages if item.message_id in active_message_ids
        ]
        filtered.assistant_turns = [
            item
            for item in fragment.assistant_turns
            if item.message_id in active_message_ids
        ]
        filtered.tool_calls = [
            item for item in fragment.tool_calls if item.turn_id in active_turn_ids
        ]
        filtered.tool_results = [
            item
            for item in fragment.tool_results
            if event_raw_ids.get(item.event_id) in active_raw_ids
        ]
        selected.append(filtered)
    return selected


def _recoverable_non_authoritative_item(item: Any) -> bool:
    """Whether an unmatched projection contains an observable decision.

    Runtime snapshots and Claw-Eval can emit empty/pure-error completion
    projections which are not additional model decisions.  Visible output,
    reasoning, or a tool call is sufficient evidence to recover a genuinely
    missing session completion.
    """

    if isinstance(item, AssistantTurn):
        return bool(
            item.text_outputs
            or item.thinking_texts
            or item.tool_call_ids
        )
    if isinstance(item, CanonicalMessage):
        return any(
            bool(block.text)
            or block.block_type in {"tool_call", "tool_result"}
            for block in item.content_blocks
        )
    return True


def _merge_occurrences(
    fragments: list[TraceFragment],
    attr: str,
    key_fn: Any,
    *,
    authoritative_kind: Optional[SourceKind] = None,
    stats: Optional[dict[str, Any]] = None,
) -> list[Any]:
    """Merge equivalent observations while retaining repeated real occurrences."""

    merged: dict[tuple[str, int], Any] = {}
    order: list[tuple[str, int]] = []
    authority_active = bool(
        authoritative_kind is not None
        and any(
            fragment.source_kind == authoritative_kind
            and bool(getattr(fragment, attr))
            for fragment in fragments
        )
    )
    authority_keys: set[tuple[str, int]] = set()
    retained_non_authoritative = 0
    suppressed_non_authoritative = 0
    for fragment in fragments:
        local_counts: dict[str, int] = defaultdict(int)
        for item in getattr(fragment, attr):
            semantic = key_fn(item)
            occurrence = local_counts[semantic]
            local_counts[semantic] += 1
            key = (semantic, occurrence)
            unmatched_non_authoritative = bool(
                authority_active
                and fragment.source_kind != authoritative_kind
                and key not in authority_keys
            )
            if unmatched_non_authoritative and not _recoverable_non_authoritative_item(
                item
            ):
                suppressed_non_authoritative += 1
                continue
            recovered = unmatched_non_authoritative
            if recovered:
                # A persisted session can be truncated or partially written.
                # Runtime/Claw-Eval observations that have no session match are
                # therefore recovery evidence, not disposable projections.
                retained_non_authoritative += 1
            if (
                authority_active
                and fragment.source_kind == authoritative_kind
            ):
                authority_keys.add(key)
            if key not in merged:
                merged[key] = copy.deepcopy(item)
                if recovered:
                    merged[key].metadata[
                        "recovered_from_non_authoritative_source"
                    ] = True
                order.append(key)
                continue
            existing = merged[key]
            if _priority(item) < _priority(existing):
                replacement = copy.deepcopy(item)
                _merge_entity_observations(replacement, existing)
                merged[key] = replacement
            else:
                _merge_entity_observations(existing, item)
    if stats is not None:
        stats[f"suppressed_non_authoritative_{attr}"] = (
            suppressed_non_authoritative
        )
        stats[f"retained_non_authoritative_{attr}"] = retained_non_authoritative
        stats[f"authoritative_{attr}"] = (
            authoritative_kind.value if authority_active else None
        )
    return [merged[key] for key in order]


def _merge_calls(fragments: list[TraceFragment]) -> list[ToolCall]:
    # A call ID identifies a logical call across different artifacts, but it is
    # not safe to assume uniqueness inside one artifact.  Pair it with the local
    # occurrence so same-source reuse remains observable; integrity validation
    # can then reject the ambiguous ID instead of reconciliation hiding it.
    merged: dict[tuple[str, int], ToolCall] = {}
    order: list[tuple[str, int]] = []
    for fragment in fragments:
        local_counts: dict[str, int] = defaultdict(int)
        for item in fragment.tool_calls:
            occurrence = local_counts[item.call_id]
            local_counts[item.call_id] += 1
            key = (item.call_id, occurrence)
            if key not in merged:
                merged[key] = copy.deepcopy(item)
                order.append(key)
                continue
            existing = merged[key]
            if _priority(item) < _priority(existing):
                replacement = copy.deepcopy(item)
                replacement.source_refs = merge_source_refs(
                    replacement.source_refs, existing.source_refs
                )
                replacement.metadata.setdefault("argument_variants", []).append(
                    {
                        "name": existing.name,
                        "arguments": existing.arguments,
                        "partial_arguments": existing.partial_arguments,
                    }
                )
                merged[key] = replacement
            else:
                existing.source_refs = merge_source_refs(
                    existing.source_refs, item.source_refs
                )
                variant = {
                    "name": item.name,
                    "arguments": item.arguments,
                    "partial_arguments": item.partial_arguments,
                }
                variants = existing.metadata.setdefault("argument_variants", [])
                if variant not in variants and (
                    item.arguments != existing.arguments or item.name != existing.name
                ):
                    variants.append(variant)
    return [merged[key] for key in order]


def _result_key(result: ToolResult) -> str:
    if result.call_id:
        return f"call:{result.call_id}"
    return f"orphan:{result.result_id}"


def _merge_results(fragments: list[TraceFragment]) -> list[ToolResult]:
    merged: dict[str, ToolResult] = {}
    order: list[str] = []
    for fragment in fragments:
        local_counts: dict[str, int] = defaultdict(int)
        for item in fragment.tool_results:
            base = _result_key(item)
            # Multiple results for one call in the same artifact are retained.
            occurrence = local_counts[base]
            local_counts[base] += 1
            key = f"{base}:{occurrence}"
            if key not in merged:
                merged[key] = copy.deepcopy(item)
                order.append(key)
                continue
            existing = merged[key]
            if _priority(item) < _priority(existing):
                replacement = copy.deepcopy(item)
                replacement.source_refs = merge_source_refs(
                    replacement.source_refs, existing.source_refs
                )
                replacement.metadata.setdefault("content_variants", []).append(
                    [block.to_dict() for block in existing.content_blocks]
                )
                merged[key] = replacement
            else:
                existing.source_refs = merge_source_refs(
                    existing.source_refs, item.source_refs
                )
                existing_text = [block.to_dict() for block in existing.content_blocks]
                alternate_text = [block.to_dict() for block in item.content_blocks]
                if alternate_text != existing_text:
                    variants = existing.metadata.setdefault("content_variants", [])
                    if alternate_text not in variants:
                        variants.append(alternate_text)
                if existing.is_error is None and item.is_error is not None:
                    existing.is_error = item.is_error
                    existing.status = item.status
    return [merged[key] for key in order]


def _merge_dispatches(fragments: list[TraceFragment]) -> list[ToolDispatch]:
    merged: dict[str, ToolDispatch] = {}
    order: list[str] = []
    for fragment in fragments:
        local_counts: dict[str, int] = defaultdict(int)
        for item in fragment.dispatches:
            base = (
                f"call:{item.call_id}"
                if item.call_id
                else f"id:{item.dispatch_id}"
            )
            occurrence = local_counts[base]
            local_counts[base] += 1
            key = f"{base}:{occurrence}"
            if key not in merged:
                merged[key] = copy.deepcopy(item)
                order.append(key)
                continue
            existing = merged[key]
            existing.source_refs = merge_source_refs(
                existing.source_refs, item.source_refs
            )
            if existing.status == DispatchStatus.UNKNOWN:
                existing.status = item.status
            if existing.response is None:
                existing.response = item.response
            if existing.request is None:
                existing.request = item.request
    return [merged[key] for key in order]


def _merge_runs(fragments: list[TraceFragment]) -> list[CanonicalRun]:
    merged: dict[str, CanonicalRun] = {}
    order: list[str] = []
    for fragment in fragments:
        for item in fragment.runs:
            if item.run_id not in merged:
                merged[item.run_id] = copy.deepcopy(item)
                order.append(item.run_id)
                continue
            existing = merged[item.run_id]
            for field_name in (
                "session_id",
                "started_at",
                "ended_at",
                "status",
                "provider",
                "model",
                "model_api",
            ):
                if getattr(existing, field_name) is None:
                    setattr(existing, field_name, getattr(item, field_name))
            existing.tool_inventory = unique_dicts(
                [*existing.tool_inventory, *item.tool_inventory]
            )
            existing.metadata.update(item.metadata)
            existing.source_refs = merge_source_refs(
                existing.source_refs, item.source_refs
            )
    return [merged[key] for key in order]


def _assign_run_ids(
    runs: list[CanonicalRun],
    messages: list[CanonicalMessage],
    turns: list[AssistantTurn],
    calls: list[ToolCall],
    results: list[ToolResult],
    dispatches: list[ToolDispatch],
) -> None:
    if not runs:
        return
    if len(runs) == 1:
        run_id = runs[0].run_id
        for group in (messages, turns, calls, results, dispatches):
            for item in group:
                if item.run_id is None:
                    item.run_id = run_id
        return

    for group in (messages, turns, calls, results, dispatches):
        for item in group:
            if item.run_id is not None or item.timestamp is None:
                continue
            candidates = [
                run
                for run in runs
                if (run.started_at is None or run.started_at <= item.timestamp)
                and (run.ended_at is None or item.timestamp <= run.ended_at)
            ]
            if len(candidates) == 1:
                item.run_id = candidates[0].run_id


def _sort_timestamp(items: list[Any]) -> list[Any]:
    indexed = list(enumerate(items))
    indexed.sort(
        key=lambda pair: (
            getattr(pair[1], "timestamp", None) is None,
            getattr(pair[1], "timestamp", None) or "",
            pair[0],
        )
    )
    return [item for _, item in indexed]


def _derive_task(
    fragments: list[TraceFragment], messages: list[CanonicalMessage]
) -> Optional[CanonicalTask]:
    explicit = [fragment.task for fragment in fragments if fragment.task is not None]
    if explicit:
        return copy.deepcopy(explicit[0])
    first_user = next(
        (message for message in messages if message.role == MessageRole.USER), None
    )
    task_id = next(
        (fragment.task_id_hint for fragment in fragments if fragment.task_id_hint),
        None,
    )
    if first_user is None and task_id is None:
        return None
    return CanonicalTask(
        task_id=task_id,
        user_request=first_user.text if first_user is not None else None,
        metadata={"derived_from_trace": True},
        source_refs=first_user.source_refs if first_user is not None else [],
    )


def reconcile_trace(fragments: Iterable[TraceFragment]) -> CanonicalTrace:
    """Reconcile independently parsed sources into one canonical trace."""

    fragment_list = list(fragments)
    if not fragment_list:
        raise ValueError("at least one trace fragment is required")
    fragment_list.sort(key=lambda fragment: _SOURCE_PRIORITY[fragment.source_kind])
    branch_selection = _branch_selection(fragment_list)
    working_fragments = _select_session_branch(fragment_list, branch_selection)

    sources = []
    seen_sources: set[str] = set()
    for fragment in fragment_list:
        for source in fragment.sources:
            if source.source_id not in seen_sources:
                sources.append(copy.deepcopy(source))
                seen_sources.add(source.source_id)
    events = [
        copy.deepcopy(event)
        for fragment in fragment_list
        for event in fragment.events
    ]
    reconciliation_stats: dict[str, Any] = {}
    messages = _merge_occurrences(
        working_fragments,
        "messages",
        _message_semantic_key,
        authoritative_kind=SourceKind.SESSION_V3,
        stats=reconciliation_stats,
    )
    turns = _merge_occurrences(
        working_fragments,
        "assistant_turns",
        _turn_semantic_key,
        authoritative_kind=SourceKind.SESSION_V3,
        stats=reconciliation_stats,
    )
    calls = _merge_calls(working_fragments)
    results = _merge_results(working_fragments)
    dispatches = _merge_dispatches(working_fragments)
    runs = _merge_runs(working_fragments)
    evaluations = [
        copy.deepcopy(item)
        for fragment in working_fragments
        for item in fragment.evaluations
    ]

    _assign_run_ids(runs, messages, turns, calls, results, dispatches)

    turn_by_call: dict[str, AssistantTurn] = {}
    for turn in turns:
        turn.tool_result_ids = []
        for call_id in turn.tool_call_ids:
            turn_by_call[call_id] = turn
    calls_by_id = {call.call_id: call for call in calls}
    results_by_call: dict[str, list[ToolResult]] = defaultdict(list)
    for result in results:
        if result.call_id:
            results_by_call[result.call_id].append(result)
    dispatches_by_call: dict[str, list[ToolDispatch]] = defaultdict(list)
    for dispatch in dispatches:
        if dispatch.call_id:
            dispatches_by_call[dispatch.call_id].append(dispatch)

    for call in calls:
        turn = turn_by_call.get(call.call_id)
        if turn is not None:
            call.turn_id = turn.turn_id
            if call.run_id is None:
                call.run_id = turn.run_id
        linked_results = results_by_call.get(call.call_id, [])
        linked_dispatches = dispatches_by_call.get(call.call_id, [])
        call.result_ids = [result.result_id for result in linked_results]
        call.dispatch_ids = [
            dispatch.dispatch_id for dispatch in linked_dispatches
        ]
        if any(result.status == ToolResultStatus.ERROR for result in linked_results):
            call.status = ToolCallStatus.ERROR
        elif linked_results:
            call.status = ToolCallStatus.COMPLETED
        elif any(
            dispatch.status == DispatchStatus.ERROR for dispatch in linked_dispatches
        ):
            call.status = ToolCallStatus.ERROR
        else:
            call.status = ToolCallStatus.MISSING_RESULT
        if turn is not None:
            turn.tool_result_ids.extend(call.result_ids)

    for result in results:
        call = calls_by_id.get(result.call_id or "")
        if call is not None:
            if result.name is None:
                result.name = call.name
                result.normalized_name = call.normalized_name
            if result.run_id is None:
                result.run_id = call.run_id
    for dispatch in dispatches:
        call = calls_by_id.get(dispatch.call_id or "")
        if call is not None and dispatch.run_id is None:
            dispatch.run_id = call.run_id

    task = _derive_task(working_fragments, messages)
    tool_inventory = unique_dicts(
        [
            *(
                task.tool_inventory
                if task is not None
                else []
            ),
            *[
                tool
                for run in runs
                for tool in run.tool_inventory
            ],
        ]
    )

    turns = _sort_timestamp(turns)
    messages = _sort_timestamp(messages)
    visible_turns = [turn for turn in turns if turn.text_outputs]
    final_candidates = [
        turn for turn in visible_turns if not turn.tool_call_ids
    ] or visible_turns
    final_turn = final_candidates[-1] if final_candidates else None
    final_answer = (
        "".join(final_turn.text_outputs) if final_turn is not None else None
    )

    session_id = next(
        (
            fragment.session_id_hint
            for fragment in fragment_list
            if fragment.session_id_hint
        ),
        None,
    )
    trace_id = next(
        (
            fragment.trace_id_hint
            for fragment in fragment_list
            if fragment.source_kind == SourceKind.SESSION_V3
            and fragment.trace_id_hint
        ),
        None,
    ) or next(
        (
            fragment.trace_id_hint
            for fragment in fragment_list
            if fragment.source_kind == SourceKind.RUNTIME_V1
            and fragment.trace_id_hint
        ),
        None,
    ) or next(
        (
            fragment.trace_id_hint
            for fragment in fragment_list
            if fragment.trace_id_hint
        ),
        stable_id("trace", [source.sha256 for source in sources]),
    )

    return CanonicalTrace(
        schema_version=1,
        trace_id=str(trace_id),
        session_id=session_id,
        sources=sources,
        events=events,
        messages=messages,
        assistant_turns=turns,
        tool_calls=calls,
        tool_results=results,
        dispatches=dispatches,
        runs=runs,
        evaluations=evaluations,
        task=task,
        tool_inventory=tool_inventory,
        final_turn_id=final_turn.turn_id if final_turn is not None else None,
        final_answer=final_answer,
        metadata={
            "source_trace_ids": {
                fragment.source_kind.value: fragment.trace_id_hint
                for fragment in fragment_list
                if fragment.trace_id_hint
            },
            "source_task_ids": [
                fragment.task_id_hint
                for fragment in fragment_list
                if fragment.task_id_hint
            ],
            "reconciliation": {
                "fragment_count": len(fragment_list),
                "source_count": len(sources),
                **reconciliation_stats,
            },
            "branch_selection": branch_selection,
        },
    )
