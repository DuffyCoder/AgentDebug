"""Parser for OpenClaw runtime trajectory schema version 1."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Optional

from ._common import (
    JsonlSource,
    content_blocks,
    message_role,
    normalize_tool_name,
    stable_id,
    unique_dicts,
)
from .models import (
    AssistantTurn,
    CanonicalMessage,
    CanonicalRun,
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
from .session_v3 import _call_fields


def _inventory(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [
        dict(item) if isinstance(item, Mapping) else {"name": str(item)}
        for item in value
    ]


def _parse_snapshot(
    fragment: TraceFragment,
    *,
    messages: Any,
    event_id: str,
    timestamp: Optional[str],
    run_id: Optional[str],
    provenance: Any,
    source_id: str,
    line_number: int,
    seen_snapshot_occurrences: dict[str, int],
) -> None:
    if not isinstance(messages, list):
        return
    # A cumulative snapshot repeats all earlier occurrences.  Count occurrences
    # per payload rather than using a global set: two byte-identical messages in
    # one snapshot are two observable messages, while the same two positions in
    # the next cumulative snapshot are historical copies.
    previous_occurrences = dict(seen_snapshot_occurrences)
    snapshot_occurrences: dict[str, int] = defaultdict(int)
    for message_index, payload in enumerate(messages):
        if not isinstance(payload, Mapping):
            continue
        role = message_role(payload.get("role"))
        raw_content = payload.get("content")
        if (
            role == MessageRole.ASSISTANT
            and isinstance(raw_content, list)
            and any(
                isinstance(item, Mapping)
                and item.get("text") == "[assistant reasoning omitted]"
                for item in raw_content
            )
        ):
            # A model.completed snapshot can contain a synthesized historical
            # context message.  The enclosing runtime event already preserves
            # it; it is not another completion.
            continue
        # model.completed.messagesSnapshot is cumulative across continued runs.
        # The same historical message (including its original inner timestamp)
        # can therefore appear in dozens of runtime events.  It is evidence
        # from several source lines, but it is still only one conversation
        # message/completion.  Canonical events retain every enclosing line;
        # derived messages/turns are emitted once.
        snapshot_identity = stable_id("runtime-snapshot-message", payload)
        occurrence = snapshot_occurrences[snapshot_identity]
        snapshot_occurrences[snapshot_identity] += 1
        if occurrence < previous_occurrences.get(snapshot_identity, 0):
            continue
        blocks = content_blocks(raw_content, provenance)
        call_ids_in_message: list[str] = []
        content = raw_content
        if isinstance(content, list):
            for block_index, block in enumerate(content):
                if not isinstance(block, Mapping):
                    continue
                if block.get("type") not in {
                    "toolCall",
                    "tool_call",
                    "toolUse",
                    "tool_use",
                }:
                    continue
                call_id, name, arguments, partial = _call_fields(block)
                if not call_id:
                    call_id = stable_id(
                        "call",
                        source_id,
                        line_number,
                        message_index,
                        block_index,
                        block,
                    )
                call_ids_in_message.append(call_id)

        identity_hint: Any
        if call_ids_in_message:
            identity_hint = ["calls", call_ids_in_message]
        elif role == MessageRole.TOOL_RESULT:
            identity_hint = [
                "result",
                payload.get("toolCallId")
                or payload.get("tool_use_id")
                or payload.get("call_id"),
            ]
        else:
            identity_hint = ["content", payload.get("role"), payload.get("content")]
        message_id = stable_id(
            "runtime-message", run_id, message_index, identity_hint
        )
        message = CanonicalMessage(
            message_id=message_id,
            event_id=event_id,
            role=role,
            timestamp=timestamp,
            run_id=run_id,
            parent_id=None,
            content_blocks=blocks,
            metadata={
                **{key: value for key, value in payload.items() if key != "content"},
                "source_format": "openclaw_runtime_v1",
                "snapshot_index": message_index,
            },
            source_refs=[provenance],
        )
        fragment.messages.append(message)

        if role == MessageRole.ASSISTANT:
            turn_id = f"turn:{message_id}"
            if isinstance(content, list):
                for block_index, block in enumerate(content):
                    if not isinstance(block, Mapping):
                        continue
                    if block.get("type") not in {
                        "toolCall",
                        "tool_call",
                        "toolUse",
                        "tool_use",
                    }:
                        continue
                    call_id, name, arguments, partial = _call_fields(block)
                    if not call_id:
                        call_id = stable_id(
                            "call",
                            source_id,
                            line_number,
                            message_index,
                            block_index,
                            block,
                        )
                    fragment.tool_calls.append(
                        ToolCall(
                            call_id=call_id,
                            turn_id=turn_id,
                            event_id=event_id,
                            name=name,
                            normalized_name=normalize_tool_name(name),
                            arguments=arguments,
                            partial_arguments=partial,
                            timestamp=timestamp,
                            run_id=run_id,
                            status=ToolCallStatus.PENDING,
                            metadata={
                                "source_format": "openclaw_runtime_v1",
                                "snapshot_index": message_index,
                                "content_block_index": block_index,
                            },
                            source_refs=[provenance],
                        )
                    )
            fragment.assistant_turns.append(
                AssistantTurn(
                    turn_id=turn_id,
                    message_id=message_id,
                    event_id=event_id,
                    timestamp=timestamp,
                    run_id=run_id,
                    parent_id=None,
                    content_blocks=blocks,
                    thinking_texts=[
                        block.text or ""
                        for block in blocks
                        if block.block_type in {"thinking", "reasoning"}
                    ],
                    text_outputs=[
                        block.text or ""
                        for block in blocks
                        if block.block_type == "text"
                    ],
                    tool_call_ids=call_ids_in_message,
                    stop_reason=payload.get("stopReason")
                    or payload.get("stop_reason"),
                    error_message=payload.get("errorMessage")
                    or payload.get("error_message"),
                    provider=payload.get("provider"),
                    model=payload.get("model") or payload.get("modelId"),
                    model_api=payload.get("api") or payload.get("modelApi"),
                    response_id=payload.get("responseId")
                    or payload.get("response_id"),
                    usage=dict(payload.get("usage") or {}),
                    metadata={
                        "source_format": "openclaw_runtime_v1",
                        "snapshot_index": message_index,
                        "inner_timestamp": payload.get("timestamp"),
                    },
                    source_refs=[provenance],
                )
            )

        elif role == MessageRole.TOOL_RESULT:
            call_id = (
                payload.get("toolCallId")
                or payload.get("tool_use_id")
                or payload.get("call_id")
            )
            name = payload.get("toolName") or payload.get("name")
            is_error = payload.get("isError")
            if is_error is None:
                is_error = payload.get("is_error")
            status = (
                ToolResultStatus.ERROR
                if is_error is True
                else ToolResultStatus.SUCCESS
                if is_error is False
                else ToolResultStatus.UNKNOWN
            )
            fragment.tool_results.append(
                ToolResult(
                    result_id=stable_id(
                        "runtime-result", run_id, message_index, call_id, payload
                    ),
                    call_id=str(call_id) if call_id is not None else None,
                    event_id=event_id,
                    name=str(name) if name is not None else None,
                    normalized_name=(
                        normalize_tool_name(str(name)) if name is not None else None
                    ),
                    content_blocks=blocks,
                    is_error=is_error if isinstance(is_error, bool) else None,
                    status=status,
                    timestamp=timestamp,
                    run_id=run_id,
                    details=payload.get("details"),
                    metadata={
                        "source_format": "openclaw_runtime_v1",
                        "snapshot_index": message_index,
                        "inner_timestamp": payload.get("timestamp"),
                    },
                    source_refs=[provenance],
                )
            )

    for identity, count in snapshot_occurrences.items():
        seen_snapshot_occurrences[identity] = max(
            seen_snapshot_occurrences.get(identity, 0),
            count,
        )


def parse_runtime_v1(path: str | Path) -> TraceFragment:
    """Parse an OpenClaw ``openclaw-trajectory`` v1 JSONL artifact."""

    source = JsonlSource(path, SourceKind.RUNTIME_V1)
    fragment = TraceFragment(source_kind=SourceKind.RUNTIME_V1)
    fragment.sources.append(source.artifact)
    runs: dict[str, CanonicalRun] = {}
    seen_snapshot_occurrences: dict[str, int] = {}

    for line_number, _, raw, provenance, parse_error in source.rows():
        if parse_error:
            fragment.events.append(
                source.event(line_number, raw, provenance, parse_error)
            )
            continue
        assert raw is not None
        event = source.event(line_number, raw, provenance)
        fragment.events.append(event)
        if raw.get("traceSchema"):
            source.artifact.metadata["trace_schema"] = raw.get("traceSchema")
            source.artifact.metadata["schema_version"] = raw.get("schemaVersion")
        trace_id = raw.get("traceId")
        if trace_id and not fragment.trace_id_hint:
            fragment.trace_id_hint = str(trace_id)
        session_id = raw.get("sessionId")
        if session_id and not fragment.session_id_hint:
            fragment.session_id_hint = str(session_id)

        run_id_value = raw.get("runId")
        run_id = str(run_id_value) if run_id_value is not None else None
        data = raw.get("data")
        data = data if isinstance(data, Mapping) else {}
        if run_id:
            run = runs.get(run_id)
            if run is None:
                run = CanonicalRun(
                    run_id=run_id,
                    session_id=str(session_id) if session_id is not None else None,
                    started_at=None,
                    ended_at=None,
                    status=None,
                    provider=raw.get("provider"),
                    model=raw.get("modelId"),
                    model_api=raw.get("modelApi"),
                    metadata={"event_ids": []},
                )
                runs[run_id] = run
            run.metadata.setdefault("event_ids", []).append(event.event_id)
            run.source_refs = merge_source_refs(run.source_refs, [provenance])
            if raw.get("type") == "session.started":
                run.started_at = event.timestamp
                run.metadata["start"] = dict(data)
            elif raw.get("type") == "session.ended":
                run.ended_at = event.timestamp
                run.status = data.get("status")
                run.metadata["end"] = dict(data)
            elif raw.get("type") == "trace.metadata":
                run.metadata["trace_metadata"] = {
                    "captured_at": data.get("capturedAt"),
                    "redaction": data.get("redaction"),
                    "model": data.get("model"),
                }
            elif raw.get("type") == "context.compiled":
                run.tool_inventory = unique_dicts(
                    [*run.tool_inventory, *_inventory(data.get("tools"))]
                )
                run.metadata["context"] = {
                    "images_count": data.get("imagesCount"),
                    "transcript_leaf_id": data.get("transcriptLeafId"),
                    "transport": data.get("transport"),
                    "stream_strategy": data.get("streamStrategy"),
                    # The full prompt and system prompt remain in the raw event.
                    "system_prompt_sha256": stable_id(
                        "sha", data.get("systemPrompt") or ""
                    ),
                    "prompt_sha256": stable_id("sha", data.get("prompt") or ""),
                }
            elif raw.get("type") in {"model.completed", "trace.artifacts"}:
                run.metadata[raw["type"]] = {
                    key: value
                    for key, value in data.items()
                    if key
                    in {
                        "aborted",
                        "externalAbort",
                        "timedOut",
                        "idleTimedOut",
                        "timedOutDuringCompaction",
                        "timedOutDuringToolExecution",
                        "promptErrorSource",
                        "terminalError",
                        "lastToolError",
                        "compactionCount",
                        "finalStatus",
                        "usage",
                        "itemLifecycle",
                    }
                }

        record_type = raw.get("type")
        if record_type == "model.completed":
            _parse_snapshot(
                fragment,
                messages=data.get("messagesSnapshot"),
                event_id=event.event_id,
                timestamp=event.timestamp,
                run_id=run_id,
                provenance=provenance,
                source_id=source.source_id,
                line_number=line_number,
                seen_snapshot_occurrences=seen_snapshot_occurrences,
            )

        # Newer v1 emitters may include individual runtime tool lifecycle events.
        if record_type in {
            "tool.started",
            "tool.completed",
            "tool.error",
            "tool.dispatch",
        }:
            call_id_value = (
                data.get("toolCallId")
                or data.get("toolUseId")
                or data.get("callId")
                or raw.get("toolCallId")
            )
            call_id = str(call_id_value) if call_id_value is not None else None
            tool_name = str(
                data.get("toolName") or data.get("name") or raw.get("toolName") or ""
            )
            response_status = data.get("responseStatus") or data.get("statusCode")
            error = data.get("error") or data.get("errorMessage")
            if record_type == "tool.error" or error is not None:
                dispatch_status = DispatchStatus.ERROR
            elif record_type == "tool.completed":
                dispatch_status = DispatchStatus.SUCCESS
            else:
                dispatch_status = DispatchStatus.UNKNOWN
            fragment.dispatches.append(
                ToolDispatch(
                    dispatch_id=stable_id(
                        "runtime-dispatch", source.source_id, line_number, call_id
                    ),
                    call_id=call_id,
                    event_id=event.event_id,
                    tool_name=tool_name,
                    normalized_name=normalize_tool_name(tool_name),
                    request=data.get("request") or data.get("arguments"),
                    response=data.get("response") or data.get("result"),
                    response_status=response_status,
                    status=dispatch_status,
                    timestamp=event.timestamp,
                    started_at=data.get("startedAt"),
                    latency_ms=data.get("latencyMs"),
                    run_id=run_id,
                    endpoint_url=data.get("endpointUrl"),
                    error=error,
                    metadata={"source_format": "openclaw_runtime_v1"},
                    source_refs=[provenance],
                )
            )

    fragment.runs.extend(runs.values())
    return fragment
