"""Strict AgentErrorBench JSON-document to Canonical Trace adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from agentdebug.trace import (
    AssistantTurn,
    CanonicalEvent,
    CanonicalMessage,
    CanonicalTask,
    CanonicalTrace,
    ContentBlock,
    MessageRole,
    Provenance,
    SourceArtifact,
    SourceKind,
    validate_trace,
)
from agentdebug.trace._common import sha256_bytes, sha256_text, stable_json

from .models import (
    ConversionIssue,
    ConversionReport,
    GoldLabel,
    StepMapping,
    TraceMapping,
)


ADAPTER_VERSION = "agenterrorbench-canonical-v1"
STEP_MAPPING_RULE = (
    "Each assistant-role source message is one 1-based benchmark decision step. "
    "Its assistant message event is the unique critical_event_id. Messages after "
    "the previous assistant message and before this assistant message are context "
    "events for the same step. Embedded <memory>/<reflection>/<plan>/<action> "
    "text is preserved as text and is not converted into invented tool calls."
)


class AdapterError(ValueError):
    """A trajectory cannot be converted without guessing its source semantics."""


def _role(raw: Any) -> MessageRole:
    normalized = str(raw or "").strip().lower().replace("-", "_")
    return {
        "user": MessageRole.USER,
        "assistant": MessageRole.ASSISTANT,
        "system": MessageRole.SYSTEM,
        "developer": MessageRole.DEVELOPER,
        "tool": MessageRole.TOOL_RESULT,
        "tool_result": MessageRole.TOOL_RESULT,
        "custom": MessageRole.CUSTOM,
    }.get(normalized, MessageRole.UNKNOWN)


def _raw_text(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _provenance(
    *,
    source_id: str,
    path: Path,
    ordinal: int,
    value: Any,
) -> Provenance:
    raw_text = _raw_text(value)
    return Provenance(
        source_id=source_id,
        source_kind=SourceKind.AGENT_ERROR_BENCH,
        path=str(path),
        # These are logical JSON-document record ordinals, not physical lines.
        line_start=ordinal,
        line_end=ordinal,
        raw_sha256=sha256_text(raw_text),
        raw_text=raw_text,
    )


def _blocks(content: Any, provenance: Provenance) -> list[ContentBlock]:
    # The benchmark stores module markup inside strings. Keep it exactly as one
    # text block: interpreting those tags would change the released trajectory.
    if isinstance(content, str):
        return [
            ContentBlock(
                block_type="text",
                text=content,
                data=content,
                source_refs=[provenance],
            )
        ]
    if content is None:
        return []
    return [
        ContentBlock(
            block_type="structured",
            data=content,
            source_refs=[provenance],
        )
    ]


def adapt_trajectory(
    trajectory_path: str | Path,
    *,
    trajectory_id: str | None = None,
) -> tuple[CanonicalTrace, TraceMapping]:
    """Convert one release trajectory without consulting its gold label."""

    path = Path(trajectory_path).expanduser().resolve()
    data_bytes = path.read_bytes()
    file_sha = sha256_bytes(data_bytes)
    try:
        document = json.loads(data_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AdapterError(f"trajectory is not a valid UTF-8 JSON document: {error}")
    if not isinstance(document, Mapping):
        raise AdapterError("trajectory top level must be a JSON object")
    messages_raw = document.get("messages")
    if not isinstance(messages_raw, list):
        raise AdapterError("trajectory.messages must be an array")
    if any(not isinstance(message, Mapping) for message in messages_raw):
        raise AdapterError("every trajectory.messages item must be an object")

    trace_id = trajectory_id or path.stem
    if not trace_id.strip():
        raise AdapterError("trajectory_id must not be empty")
    source_id = f"{SourceKind.AGENT_ERROR_BENCH.value}:{file_sha[:16]}"
    physical_lines = data_bytes.decode("utf-8").splitlines()

    # Every message is a logical source record. Every remaining top-level field
    # is another logical record, so no document field disappears.
    extra_keys = [key for key in document if key != "messages"]
    record_count = len(messages_raw) + len(extra_keys)
    source = SourceArtifact(
        source_id=source_id,
        kind=SourceKind.AGENT_ERROR_BENCH,
        path=str(path),
        sha256=file_sha,
        line_count=len(physical_lines),
        nonblank_line_count=sum(bool(line.strip()) for line in physical_lines),
        metadata={
            "adapter_version": ADAPTER_VERSION,
            "record_count": record_count,
            "provenance_unit": "logical_json_document_record_ordinal",
            "message_count": len(messages_raw),
            "top_level_extra_keys": extra_keys,
        },
    )

    events: list[CanonicalEvent] = []
    messages: list[CanonicalMessage] = []
    turns: list[AssistantTurn] = []
    step_rows: list[StepMapping] = []
    context_event_ids: list[str] = []
    context_message_indices: list[int] = []
    assistant_step = 0
    metadata = document.get("metadata")
    source_model = (
        str(metadata.get("model"))
        if isinstance(metadata, Mapping) and metadata.get("model") is not None
        else None
    )

    for index, raw_message in enumerate(messages_raw):
        raw = dict(raw_message)
        ordinal = index + 1
        provenance = _provenance(
            source_id=source_id,
            path=path,
            ordinal=ordinal,
            value=raw,
        )
        event_id = f"{source_id}:message:{ordinal}"
        role = _role(raw.get("role"))
        event = CanonicalEvent(
            event_id=event_id,
            source_id=source_id,
            source_kind=SourceKind.AGENT_ERROR_BENCH,
            event_type=f"message.{role.value}",
            timestamp=(
                str(raw.get("timestamp"))
                if raw.get("timestamp") is not None
                else None
            ),
            sequence=ordinal,
            run_id=None,
            parent_id=None,
            raw=raw,
            provenance=provenance,
        )
        events.append(event)
        blocks = _blocks(raw.get("content"), provenance)
        message_id = f"{source_id}:canonical-message:{ordinal}"
        message = CanonicalMessage(
            message_id=message_id,
            event_id=event_id,
            role=role,
            timestamp=event.timestamp,
            run_id=None,
            parent_id=None,
            content_blocks=blocks,
            metadata={
                "benchmark_message_index": index,
                "source_role": raw.get("role"),
                "unmodeled_source_fields": {
                    key: value
                    for key, value in raw.items()
                    if key not in {"role", "content", "timestamp"}
                },
            },
            source_refs=[provenance],
        )
        messages.append(message)

        if role != MessageRole.ASSISTANT:
            context_event_ids.append(event_id)
            context_message_indices.append(index)
            continue

        assistant_step += 1
        turn_id = f"{source_id}:assistant-turn:{assistant_step}"
        text_outputs = [
            block.text
            for block in blocks
            if block.block_type == "text" and block.text is not None
        ]
        turn = AssistantTurn(
            turn_id=turn_id,
            message_id=message_id,
            event_id=event_id,
            timestamp=event.timestamp,
            run_id=None,
            parent_id=None,
            content_blocks=blocks,
            thinking_texts=[],
            text_outputs=text_outputs,
            tool_call_ids=[],
            provider=None,
            model=source_model,
            metadata={
                "benchmark_original_step": assistant_step,
                "benchmark_message_index": index,
                "embedded_module_markup_interpreted": False,
            },
            source_refs=[provenance],
        )
        turns.append(turn)
        step_rows.append(
            StepMapping(
                original_step=assistant_step,
                source_message_indices=tuple([*context_message_indices, index]),
                canonical_event_ids=tuple([*context_event_ids, event_id]),
                critical_event_id=event_id,
                assistant_turn_id=turn_id,
                tool_call_ids=(),
                rule=STEP_MAPPING_RULE,
            )
        )
        context_event_ids = []
        context_message_indices = []

    # Preserve metadata and any future release fields as their own events.
    for offset, key in enumerate(extra_keys, start=1):
        ordinal = len(messages_raw) + offset
        value = document[key]
        provenance = _provenance(
            source_id=source_id,
            path=path,
            ordinal=ordinal,
            value=value,
        )
        events.append(
            CanonicalEvent(
                event_id=f"{source_id}:top-level:{key}",
                source_id=source_id,
                source_kind=SourceKind.AGENT_ERROR_BENCH,
                event_type=f"benchmark.{key}",
                timestamp=None,
                sequence=ordinal,
                run_id=None,
                parent_id=None,
                raw=value,
                provenance=provenance,
            )
        )

    first_user = next(
        (message for message in messages if message.role == MessageRole.USER),
        None,
    )
    task = (
        CanonicalTask(
            task_id=trace_id,
            title=f"AgentErrorBench {trace_id}",
            description=None,
            user_request=first_user.text,
            raw_text=first_user.text,
            raw=first_user.content_blocks[0].data
            if first_user.content_blocks
            else None,
            metadata={
                "derivation": "complete first user-role message; no task extraction",
            },
            source_refs=list(first_user.source_refs),
        )
        if first_user is not None
        else None
    )
    trace = CanonicalTrace(
        schema_version=1,
        trace_id=trace_id,
        session_id=None,
        sources=[source],
        events=events,
        messages=messages,
        assistant_turns=turns,
        tool_calls=[],
        tool_results=[],
        dispatches=[],
        runs=[],
        evaluations=[],
        task=task,
        tool_inventory=[],
        final_turn_id=None,
        final_answer=None,
        metadata={
            "adapter": ADAPTER_VERSION,
            "benchmark": "AgentErrorBench",
            "trajectory_id": trace_id,
            "trajectory_sha256": file_sha,
            "step_mapping_rule": STEP_MAPPING_RULE,
            "final_answer_omitted_reason": (
                "The release stores bounded decision steps, not a separately "
                "typed final-answer record."
            ),
        },
    )
    validate_trace(trace, strict=False)
    mapping = TraceMapping(
        trajectory_id=trace_id,
        trajectory_path=str(path),
        trajectory_sha256=file_sha,
        step_rule=STEP_MAPPING_RULE,
        steps=step_rows,
        ignored_inputs=[],
    )
    return trace, mapping


def validate_conversion(
    *,
    source_document: Mapping[str, Any],
    trace: CanonicalTrace,
    mapping: TraceMapping,
    gold: GoldLabel,
) -> ConversionReport:
    """Check preservation, step traceability, and gold-event existence."""

    issues: list[ConversionIssue] = []
    raw_messages = source_document.get("messages")
    if not isinstance(raw_messages, list):
        raw_messages = []
        issues.append(
            ConversionIssue(
                code="invalid_source_messages",
                severity="error",
                message="Source messages is not an array.",
            )
        )
    if len(trace.messages) != len(raw_messages):
        issues.append(
            ConversionIssue(
                code="message_count_mismatch",
                severity="error",
                message="Not every input message became one CanonicalMessage.",
                details={
                    "input": len(raw_messages),
                    "canonical": len(trace.messages),
                },
            )
        )

    event_by_id = {event.event_id: event for event in trace.events}
    for index, raw_message in enumerate(raw_messages):
        if index >= len(trace.messages):
            break
        event = event_by_id.get(trace.messages[index].event_id)
        if event is None or stable_json(event.raw) != stable_json(raw_message):
            issues.append(
                ConversionIssue(
                    code="message_content_mismatch",
                    severity="error",
                    message="A CanonicalMessage event differs from its input message.",
                    details={"message_index": index},
                )
            )

    assistant_count = sum(
        isinstance(message, Mapping)
        and _role(message.get("role")) == MessageRole.ASSISTANT
        for message in raw_messages
    )
    if assistant_count != len(mapping.steps):
        issues.append(
            ConversionIssue(
                code="step_count_mismatch",
                severity="error",
                message="Assistant decisions and mapped benchmark steps differ.",
                details={
                    "assistant_decisions": assistant_count,
                    "mapped_steps": len(mapping.steps),
                },
            )
        )
    declared_steps = source_document.get("metadata", {})
    declared_steps = (
        declared_steps.get("steps")
        if isinstance(declared_steps, Mapping)
        else None
    )
    if isinstance(declared_steps, int) and declared_steps != assistant_count:
        issues.append(
            ConversionIssue(
                code="declared_step_count_differs",
                severity="warning",
                message=(
                    "Source metadata.steps differs from the observable assistant "
                    "decision count; both values are retained."
                ),
                details={
                    "metadata_steps": declared_steps,
                    "assistant_decisions": assistant_count,
                },
            )
        )

    gold_event_id = mapping.event_for_step(gold.original_step)
    if gold_event_id is None or gold_event_id not in event_by_id:
        issues.append(
            ConversionIssue(
                code="gold_step_unmapped",
                severity="error",
                message="Gold critical step does not map to an existing event.",
                details={"gold_step": gold.original_step},
            )
        )
    elif mapping.step_for_event(gold_event_id) != gold.original_step:
        issues.append(
            ConversionIssue(
                code="gold_mapping_not_bidirectional",
                severity="error",
                message="Gold step/event mapping is not uniquely reversible.",
                details={
                    "gold_step": gold.original_step,
                    "gold_event_id": gold_event_id,
                },
            )
        )

    integrity = validate_trace(trace, strict=False)
    if not integrity.ok:
        issues.append(
            ConversionIssue(
                code="canonical_integrity_failure",
                severity="error",
                message="Converted trace failed the Canonical Trace integrity gate.",
                details={
                    "integrity_codes": [
                        issue.code for issue in integrity.issues
                    ]
                },
            )
        )
    if mapping.ignored_inputs:
        issues.append(
            ConversionIssue(
                code="ignored_source_inputs",
                severity="warning",
                message="Some source inputs were ignored with recorded reasons.",
                details={"ignored": mapping.ignored_inputs},
            )
        )

    return ConversionReport(
        trajectory_id=gold.trajectory_id,
        valid=not any(issue.severity == "error" for issue in issues),
        input_message_count=len(raw_messages),
        preserved_message_count=len(trace.messages),
        assistant_decision_count=assistant_count,
        mapped_step_count=len(mapping.steps),
        gold_step=gold.original_step,
        gold_event_id=gold_event_id,
        issues=issues,
    )
