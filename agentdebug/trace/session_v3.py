"""Parser for OpenClaw session JSONL version 3."""

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
    MessageRole,
    SourceKind,
    ToolCall,
    ToolCallStatus,
    ToolResult,
    ToolResultStatus,
    TraceFragment,
)


def _call_fields(block: Mapping[str, Any]) -> tuple[Optional[str], str, Any, Any]:
    function = block.get("function")
    function = function if isinstance(function, Mapping) else {}
    call_id = (
        block.get("id")
        or block.get("toolCallId")
        or block.get("tool_use_id")
        or block.get("call_id")
    )
    name = str(
        block.get("name")
        or block.get("toolName")
        or function.get("name")
        or ""
    )
    arguments = (
        block.get("arguments")
        if "arguments" in block
        else block.get("input", function.get("arguments"))
    )
    partial = block.get("partialArgs") or block.get("partial_arguments")
    return str(call_id) if call_id is not None else None, name, arguments, partial


def parse_session_v3(path: str | Path) -> TraceFragment:
    """Parse an OpenClaw v3 session without inventing semantic modules.

    A canonical assistant turn corresponds exactly to one source assistant
    message/completion.  All tool calls in that message remain nested under the
    same turn.
    """

    source = JsonlSource(path, SourceKind.SESSION_V3)
    fragment = TraceFragment(source_kind=SourceKind.SESSION_V3)
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

        record_type = raw.get("type")
        if record_type == "session":
            version = raw.get("version")
            source.artifact.metadata["declared_version"] = version
            source.artifact.metadata["cwd"] = raw.get("cwd")
            fragment.trace_id_hint = str(raw.get("id") or "") or None
            fragment.session_id_hint = fragment.trace_id_hint
            continue
        if record_type != "message":
            continue

        payload = raw.get("message")
        if not isinstance(payload, Mapping):
            continue
        role = message_role(payload.get("role"))
        blocks = content_blocks(payload.get("content"), provenance)
        raw_message_id = raw.get("id") or payload.get("id")
        message_id = (
            str(raw_message_id)
            if raw_message_id is not None
            else stable_id("message", source.source_id, line_number, payload)
        )
        run_id = raw.get("runId") or payload.get("runId")
        metadata = {key: value for key, value in payload.items() if key != "content"}
        metadata["source_format"] = "openclaw_session_v3"
        message = CanonicalMessage(
            message_id=message_id,
            event_id=event.event_id,
            role=role,
            timestamp=event.timestamp,
            run_id=str(run_id) if run_id is not None else None,
            parent_id=event.parent_id,
            content_blocks=blocks,
            metadata=metadata,
            source_refs=[provenance],
        )
        fragment.messages.append(message)

        if role == MessageRole.ASSISTANT:
            turn_id = f"turn:{message_id}"
            call_ids: list[str] = []
            content = payload.get("content")
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
                            "call", source.source_id, line_number, block_index, block
                        )
                    call_ids.append(call_id)
                    fragment.tool_calls.append(
                        ToolCall(
                            call_id=call_id,
                            turn_id=turn_id,
                            event_id=event.event_id,
                            name=name,
                            normalized_name=normalize_tool_name(name),
                            arguments=arguments,
                            partial_arguments=partial,
                            timestamp=event.timestamp,
                            run_id=message.run_id,
                            status=ToolCallStatus.PENDING,
                            metadata={
                                "content_block_index": block_index,
                                "source_format": "openclaw_session_v3",
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
                    run_id=message.run_id,
                    parent_id=event.parent_id,
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
                        "source_format": "openclaw_session_v3",
                        "inner_timestamp": payload.get("timestamp"),
                    },
                    source_refs=[provenance],
                )
            )
            continue

        if role == MessageRole.TOOL_RESULT:
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
                    result_id=f"result:{message_id}",
                    call_id=str(call_id) if call_id is not None else None,
                    event_id=event.event_id,
                    name=str(name) if name is not None else None,
                    normalized_name=(
                        normalize_tool_name(str(name)) if name is not None else None
                    ),
                    content_blocks=blocks,
                    is_error=is_error if isinstance(is_error, bool) else None,
                    status=status,
                    timestamp=event.timestamp,
                    run_id=message.run_id,
                    details=payload.get("details"),
                    metadata={
                        "source_format": "openclaw_session_v3",
                        "inner_timestamp": payload.get("timestamp"),
                    },
                    source_refs=[provenance],
                )
            )

    return fragment
