"""Shared, private parser helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Optional

from .models import (
    CanonicalEvent,
    ContentBlock,
    MessageRole,
    Provenance,
    SourceArtifact,
    SourceKind,
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )


def stable_id(prefix: str, *parts: Any) -> str:
    payload = "\x1f".join(stable_json(part) for part in parts)
    return f"{prefix}:{sha256_text(payload)[:20]}"


def normalize_tool_name(name: Optional[str]) -> str:
    value = name or ""
    if "__" in value:
        return value.rsplit("__", 1)[-1]
    return value


def message_role(value: Any) -> MessageRole:
    normalized = str(value or "").replace("-", "_").lower()
    aliases = {
        "user": MessageRole.USER,
        "assistant": MessageRole.ASSISTANT,
        "toolresult": MessageRole.TOOL_RESULT,
        "tool_result": MessageRole.TOOL_RESULT,
        "tool": MessageRole.TOOL_RESULT,
        "system": MessageRole.SYSTEM,
        "developer": MessageRole.DEVELOPER,
        "custom": MessageRole.CUSTOM,
    }
    return aliases.get(normalized, MessageRole.UNKNOWN)


def _block_text(block: Mapping[str, Any], block_type: str) -> Optional[str]:
    for key in ("text", "thinking", "reasoning", "content"):
        value = block.get(key)
        if isinstance(value, str):
            return value
    if block_type in {"text", "thinking", "reasoning"}:
        return ""
    return None


def content_blocks(
    content: Any,
    provenance: Provenance,
    *,
    decode_eval_thinking: bool = False,
) -> list[ContentBlock]:
    """Convert content to blocks without discarding the original value."""

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
    if not isinstance(content, list):
        return [
            ContentBlock(
                block_type="structured",
                text=None,
                data=content,
                source_refs=[provenance],
            )
        ]

    result: list[ContentBlock] = []
    for item in content:
        if isinstance(item, str):
            result.append(
                ContentBlock(
                    block_type="text",
                    text=item,
                    data=item,
                    source_refs=[provenance],
                )
            )
            continue
        if not isinstance(item, Mapping):
            result.append(
                ContentBlock(
                    block_type="unknown",
                    data=item,
                    source_refs=[provenance],
                )
            )
            continue
        source_type = str(item.get("type") or "unknown")
        block_type = {
            "toolCall": "tool_call",
            "toolUse": "tool_call",
            "tool_use": "tool_call",
            "toolResult": "tool_result",
            "tool_result": "tool_result",
            "reasoning_content": "reasoning",
        }.get(source_type, source_type)
        text = _block_text(item, block_type)
        metadata: Any = dict(item)
        if (
            decode_eval_thinking
            and block_type == "text"
            and isinstance(text, str)
            and text.startswith("[thinking]\n")
        ):
            block_type = "thinking"
            text = text[len("[thinking]\n") :]
            metadata = {
                "source_block": dict(item),
                "encoding": "claw_eval_thinking_prefix",
            }
        result.append(
            ContentBlock(
                block_type=block_type,
                text=text,
                data=metadata,
                source_refs=[provenance],
            )
        )
    return result


class JsonlSource:
    """Read a JSONL artifact once while retaining exact source lines."""

    def __init__(self, path: str | Path, kind: SourceKind):
        self.path = Path(path).expanduser().resolve()
        self.kind = kind
        data = self.path.read_bytes()
        self.file_sha256 = sha256_bytes(data)
        self.text = data.decode("utf-8")
        self.lines = self.text.splitlines()
        self.source_id = f"{kind.value}:{self.file_sha256[:16]}"
        self.artifact = SourceArtifact(
            source_id=self.source_id,
            kind=kind,
            path=str(self.path),
            sha256=self.file_sha256,
            line_count=len(self.lines),
            nonblank_line_count=sum(bool(line.strip()) for line in self.lines),
        )

    def rows(
        self,
    ) -> Iterator[tuple[int, str, Optional[dict[str, Any]], Provenance, Optional[str]]]:
        for line_number, raw_line in enumerate(self.lines, 1):
            if not raw_line.strip():
                continue
            provenance = Provenance(
                source_id=self.source_id,
                source_kind=self.kind,
                path=str(self.path),
                line_start=line_number,
                line_end=line_number,
                raw_sha256=sha256_text(raw_line),
                raw_text=raw_line,
            )
            try:
                value = json.loads(raw_line)
                if not isinstance(value, dict):
                    error = "JSON line is not an object"
                    yield line_number, raw_line, None, provenance, error
                else:
                    yield line_number, raw_line, value, provenance, None
            except (json.JSONDecodeError, UnicodeError) as exc:
                yield line_number, raw_line, None, provenance, str(exc)

    def event(
        self,
        line_number: int,
        raw: Optional[dict[str, Any]],
        provenance: Provenance,
        parse_error: Optional[str] = None,
        *,
        event_type: Optional[str] = None,
        timestamp: Optional[str] = None,
        sequence: Optional[int] = None,
        run_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> CanonicalEvent:
        value = raw or {}
        source_event_id = value.get("id") or value.get("eventId")
        event_id = (
            f"{self.source_id}:{source_event_id}"
            if source_event_id
            else f"{self.source_id}:line:{line_number}"
        )
        return CanonicalEvent(
            event_id=event_id,
            source_id=self.source_id,
            source_kind=self.kind,
            event_type=event_type or str(value.get("type") or "parse_error"),
            timestamp=timestamp
            if timestamp is not None
            else value.get("timestamp") or value.get("ts"),
            sequence=sequence
            if sequence is not None
            else value.get("seq") or value.get("sourceSeq"),
            run_id=run_id if run_id is not None else value.get("runId"),
            parent_id=parent_id
            if parent_id is not None
            else value.get("parentId") or value.get("parent_id"),
            raw=raw,
            provenance=provenance,
            parse_error=parse_error,
        )


def unique_dicts(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values:
        key = stable_json(value)
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result
