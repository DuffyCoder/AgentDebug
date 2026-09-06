"""Parser for Claw-Eval JSONL traces and evaluation records."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional

from ._common import (
    JsonlSource,
    content_blocks,
    message_role,
    normalize_tool_name,
    stable_id,
)
from .models import (
    AssistantTurn,
    CanonicalMessage,
    DispatchStatus,
    Evaluation,
    EvaluationStatus,
    MessageRole,
    SourceKind,
    ToolCall,
    ToolCallStatus,
    ToolDispatch,
    ToolResult,
    ToolResultStatus,
    TraceFragment,
)


def _tool_use(block: Mapping[str, Any]) -> bool:
    return block.get("type") in {"tool_use", "toolUse", "toolCall", "tool_call"}


def _tool_result(block: Mapping[str, Any]) -> bool:
    return block.get("type") in {"tool_result", "toolResult"}


def _evaluation_status(passed: Any, error: Any = None) -> EvaluationStatus:
    if error:
        return EvaluationStatus.ERROR
    if passed is True:
        return EvaluationStatus.PASSED
    if passed is False:
        return EvaluationStatus.FAILED
    return EvaluationStatus.UNKNOWN


def parse_claw_eval_trace(path: str | Path) -> TraceFragment:
    """Parse a Claw-Eval trace, including dispatches and final grader output."""

    source = JsonlSource(path, SourceKind.CLAW_EVAL)
    fragment = TraceFragment(source_kind=SourceKind.CLAW_EVAL)
    fragment.sources.append(source.artifact)

    for line_number, _, raw, provenance, parse_error in source.rows():
        if parse_error:
            fragment.events.append(
                source.event(line_number, raw, provenance, parse_error)
            )
            continue
        assert raw is not None
        event = source.event(line_number, raw, provenance)
        fragment.events.append(event)
        trace_id_value = raw.get("trace_id") or raw.get("traceId")
        trace_id = str(trace_id_value) if trace_id_value is not None else None
        if trace_id and not fragment.trace_id_hint:
            fragment.trace_id_hint = trace_id
        record_type = raw.get("type")

        if record_type == "trace_start":
            task_id = raw.get("task_id")
            fragment.task_id_hint = str(task_id) if task_id is not None else None
            source.artifact.metadata.update(
                {
                    "task_id": task_id,
                    "model": raw.get("model"),
                    "persona": raw.get("persona"),
                }
            )
            continue

        if record_type == "message":
            payload = raw.get("message")
            if not isinstance(payload, Mapping):
                continue
            raw_role = message_role(payload.get("role"))
            raw_content = payload.get("content")
            if (
                raw_role == MessageRole.ASSISTANT
                and isinstance(raw_content, list)
                and any(
                    isinstance(item, Mapping)
                    and item.get("text") == "[assistant reasoning omitted]"
                    for item in raw_content
                )
            ):
                # Claw-Eval may emit a synthesized historical context message
                # after a run boundary.  It is evidence and remains in events,
                # but it is not another model completion/assistant turn.
                source.artifact.metadata["context_snapshot_message_count"] = (
                    int(
                        source.artifact.metadata.get(
                            "context_snapshot_message_count", 0
                        )
                    )
                    + 1
                )
                continue
            blocks = content_blocks(
                raw_content, provenance, decode_eval_thinking=True
            )
            content_items = raw_content if isinstance(raw_content, list) else []
            result_items = [
                item
                for item in content_items
                if isinstance(item, Mapping) and _tool_result(item)
            ]
            normalized_role = (
                MessageRole.TOOL_RESULT
                if result_items
                and all(
                    isinstance(item, Mapping) and _tool_result(item)
                    for item in content_items
                )
                else raw_role
            )
            call_ids = [
                str(item.get("id") or item.get("tool_use_id"))
                for item in content_items
                if isinstance(item, Mapping)
                and _tool_use(item)
                and (item.get("id") or item.get("tool_use_id")) is not None
            ]
            result_call_ids = [
                str(item.get("tool_use_id") or item.get("toolCallId"))
                for item in result_items
                if (item.get("tool_use_id") or item.get("toolCallId")) is not None
            ]
            identity = (
                ["calls", call_ids]
                if call_ids
                else ["results", result_call_ids]
                if result_call_ids
                else ["content", payload.get("role"), raw_content]
            )
            message_id = stable_id(
                "eval-message", trace_id, line_number, identity
            )
            message = CanonicalMessage(
                message_id=message_id,
                event_id=event.event_id,
                role=normalized_role,
                timestamp=event.timestamp,
                run_id=None,
                parent_id=None,
                content_blocks=blocks,
                metadata={
                    **{
                        key: value
                        for key, value in payload.items()
                        if key != "content"
                    },
                    "source_format": "claw_eval_trace",
                    "source_role": payload.get("role"),
                    "trace_id": trace_id,
                    "usage": raw.get("usage"),
                },
                source_refs=[provenance],
            )
            fragment.messages.append(message)

            if raw_role == MessageRole.ASSISTANT:
                turn_id = f"turn:{message_id}"
                for block_index, item in enumerate(content_items):
                    if not isinstance(item, Mapping) or not _tool_use(item):
                        continue
                    call_id_value = item.get("id") or item.get("tool_use_id")
                    call_id = (
                        str(call_id_value)
                        if call_id_value is not None
                        else stable_id(
                            "eval-call",
                            source.source_id,
                            line_number,
                            block_index,
                            item,
                        )
                    )
                    name = str(item.get("name") or item.get("tool_name") or "")
                    fragment.tool_calls.append(
                        ToolCall(
                            call_id=call_id,
                            turn_id=turn_id,
                            event_id=event.event_id,
                            name=name,
                            normalized_name=normalize_tool_name(name),
                            arguments=(
                                item.get("input")
                                if "input" in item
                                else item.get("arguments")
                            ),
                            partial_arguments=item.get("partialArgs"),
                            timestamp=event.timestamp,
                            run_id=None,
                            status=ToolCallStatus.PENDING,
                            metadata={
                                "source_format": "claw_eval_trace",
                                "content_block_index": block_index,
                                "trace_id": trace_id,
                            },
                            source_refs=[provenance],
                        )
                    )
                fragment.assistant_turns.append(
                    AssistantTurn(
                        turn_id=turn_id,
                        message_id=message_id,
                        event_id=event.event_id,
                        timestamp=event.timestamp,
                        run_id=None,
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
                        tool_call_ids=call_ids,
                        stop_reason=None,
                        error_message=None,
                        provider=None,
                        model=None,
                        model_api=None,
                        response_id=None,
                        usage=dict(raw.get("usage") or {}),
                        metadata={
                            "source_format": "claw_eval_trace",
                            "trace_id": trace_id,
                        },
                        source_refs=[provenance],
                    )
                )

            for block_index, item in enumerate(result_items):
                call_id_value = item.get("tool_use_id") or item.get("toolCallId")
                call_id = str(call_id_value) if call_id_value is not None else None
                is_error = item.get("is_error")
                if is_error is None:
                    is_error = item.get("isError")
                inner_blocks = content_blocks(item.get("content"), provenance)
                fragment.tool_results.append(
                    ToolResult(
                        result_id=stable_id(
                            "eval-result",
                            source.source_id,
                            line_number,
                            block_index,
                            call_id,
                        ),
                        call_id=call_id,
                        event_id=event.event_id,
                        name=None,
                        normalized_name=None,
                        content_blocks=inner_blocks,
                        is_error=is_error if isinstance(is_error, bool) else None,
                        status=(
                            ToolResultStatus.ERROR
                            if is_error is True
                            else ToolResultStatus.SUCCESS
                            if is_error is False
                            else ToolResultStatus.UNKNOWN
                        ),
                        timestamp=event.timestamp,
                        run_id=None,
                        details=None,
                        metadata={
                            "source_format": "claw_eval_trace",
                            "content_block_index": block_index,
                            "trace_id": trace_id,
                        },
                        source_refs=[provenance],
                    )
                )
            continue

        if record_type == "tool_dispatch":
            call_id_value = raw.get("tool_use_id") or raw.get("toolCallId")
            call_id = str(call_id_value) if call_id_value is not None else None
            status_code = raw.get("response_status")
            error = raw.get("error") or raw.get("error_message")
            if error is not None or (
                isinstance(status_code, int) and not 200 <= status_code < 400
            ):
                status = DispatchStatus.ERROR
            elif isinstance(status_code, int):
                status = DispatchStatus.SUCCESS
            else:
                status = DispatchStatus.UNKNOWN
            name = str(raw.get("tool_name") or "")
            fragment.dispatches.append(
                ToolDispatch(
                    dispatch_id=stable_id(
                        "eval-dispatch",
                        source.source_id,
                        line_number,
                        call_id,
                        raw.get("call_seq"),
                    ),
                    call_id=call_id,
                    event_id=event.event_id,
                    tool_name=name,
                    normalized_name=normalize_tool_name(name),
                    request=raw.get("request_body"),
                    response=raw.get("response_body"),
                    response_status=status_code,
                    status=status,
                    timestamp=event.timestamp,
                    started_at=raw.get("started_at"),
                    latency_ms=raw.get("latency_ms"),
                    run_id=None,
                    endpoint_url=raw.get("endpoint_url"),
                    error=error,
                    metadata={
                        "source_format": "claw_eval_trace",
                        "call_seq": raw.get("call_seq"),
                        "trace_id": trace_id,
                    },
                    source_refs=[provenance],
                )
            )
            continue

        if record_type == "trace_end":
            passed = raw.get("passed")
            failure_modes = raw.get("failure_modes")
            failure_reason: Optional[str]
            if isinstance(failure_modes, list) and failure_modes:
                failure_reason = ", ".join(str(item) for item in failure_modes)
            else:
                failure_reason = raw.get("failure_mode") or raw.get("error")
            score = raw.get("task_score")
            fragment.evaluations.append(
                Evaluation(
                    evaluation_id=stable_id(
                        "evaluation", source.source_id, line_number, trace_id
                    ),
                    evaluator="claw_eval",
                    status=_evaluation_status(passed, raw.get("error")),
                    passed=passed if isinstance(passed, bool) else None,
                    score=float(score) if isinstance(score, (int, float)) else None,
                    failure_reason=(
                        str(failure_reason) if failure_reason is not None else None
                    ),
                    timestamp=event.timestamp,
                    task_id=fragment.task_id_hint,
                    trace_id=trace_id,
                    details={
                        key: value
                        for key, value in raw.items()
                        if key
                        not in {
                            "type",
                            "timestamp",
                            "trace_id",
                            "passed",
                            "task_score",
                            "failure_modes",
                            "failure_mode",
                            "error",
                        }
                    },
                    source_refs=[provenance],
                )
            )

    return fragment
