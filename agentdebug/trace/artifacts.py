"""Parsers for task definitions and external evaluation manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - conservative fallback for minimal installs
    yaml = None

from ._common import JsonlSource, sha256_bytes, sha256_text, stable_id
from .models import (
    CanonicalEvent,
    CanonicalTask,
    Evaluation,
    EvaluationStatus,
    Provenance,
    SourceArtifact,
    SourceKind,
    TraceFragment,
)


_TOP_LEVEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")


def _unquote(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    result = value.strip()
    if len(result) >= 2 and result[0] == result[-1] and result[0] in {'"', "'"}:
        return result[1:-1]
    return result


def _yaml_top_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = _TOP_LEVEL.match(line)
        if match and match.group(2) not in {None, "", "|", ">", "|-", ">-"}:
            values[match.group(1)] = _unquote(match.group(2)) or ""
    return values


def _yaml_section(text: str, name: str) -> str:
    lines = text.splitlines()
    start: Optional[int] = None
    for index, line in enumerate(lines):
        if line == f"{name}:" or line.startswith(f"{name}: "):
            start = index
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if _TOP_LEVEL.match(lines[index]):
            end = index
            break
    return "\n".join(lines[start:end])


def _yaml_nested_block(text: str, section: str, key: str) -> Optional[str]:
    lines = text.splitlines()
    section_index: Optional[int] = None
    for index, line in enumerate(lines):
        if line == f"{section}:":
            section_index = index
            break
    if section_index is None:
        return None
    key_index: Optional[int] = None
    key_indent = 0
    for index in range(section_index + 1, len(lines)):
        line = lines[index]
        if line and not line.startswith((" ", "\t")):
            break
        match = re.match(r"^(\s+)" + re.escape(key) + r":\s*(.*)$", line)
        if match:
            key_index = index
            key_indent = len(match.group(1))
            inline = match.group(2).strip()
            if inline not in {"", "|", ">", "|-", ">-"}:
                return _unquote(inline)
            break
    if key_index is None:
        return None
    collected: list[str] = []
    content_indent: Optional[int] = None
    for line in lines[key_index + 1 :]:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            if indent <= key_indent:
                break
            if content_indent is None:
                content_indent = indent
            collected.append(line[min(content_indent, len(line)) :])
        elif collected:
            collected.append("")
    return "\n".join(collected).rstrip("\n")


def _yaml_top_block(text: str, key: str) -> Optional[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^" + re.escape(key) + r":\s*(.*)$", line)
        if not match:
            continue
        inline = match.group(1).strip()
        if inline not in {"", "|", ">", "|-", ">-"}:
            return _unquote(inline)
        collected: list[str] = []
        indent: Optional[int] = None
        for child in lines[index + 1 :]:
            if child.strip():
                child_indent = len(child) - len(child.lstrip())
                if child_indent == 0:
                    break
                if indent is None:
                    indent = child_indent
                collected.append(child[min(indent, len(child)) :])
            elif collected:
                collected.append("")
        return "\n".join(collected).rstrip("\n")
    return None


def _yaml_tools(text: str) -> list[dict[str, Any]]:
    section = _yaml_section(text, "tools")
    if not section:
        return []
    tools: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None
    for line in section.splitlines()[1:]:
        match = re.match(r"^\s{2}-\s+name:\s*(.+?)\s*$", line)
        if match:
            current = {"name": _unquote(match.group(1))}
            tools.append(current)
            continue
        if current is not None:
            description = re.match(r"^\s{4}description:\s*(.+?)\s*$", line)
            if description:
                current["description"] = _unquote(description.group(1))
    return tools


def _task_from_yaml(text: str, provenance: Provenance) -> CanonicalTask:
    top = _yaml_top_values(text)
    reference = _yaml_top_block(text, "reference_solution")
    scoring = _yaml_section(text, "scoring_components")
    expected = _yaml_section(text, "expected_actions")
    safety = _yaml_section(text, "safety_checks")
    obligations: list[Any] = []
    if scoring:
        obligations.append({"source": "scoring_components", "raw_yaml": scoring})
    if expected and expected.strip() != "expected_actions: []":
        obligations.append({"source": "expected_actions", "raw_yaml": expected})
    if reference:
        obligations.append({"source": "reference_solution", "text": reference})
    prohibitions: list[Any] = []
    if safety:
        prohibitions.append({"source": "safety_checks", "raw_yaml": safety})
    return CanonicalTask(
        task_id=top.get("task_id"),
        title=top.get("task_name") or top.get("title"),
        description=top.get("description"),
        user_request=_yaml_nested_block(text, "prompt", "text"),
        obligations=obligations,
        prohibitions=prohibitions,
        tool_inventory=_yaml_tools(text),
        raw_text=text,
        raw={"format": "yaml", "text": text},
        metadata={
            key: top[key]
            for key in ("version", "category", "difficulty", "tags")
            if key in top
        },
        source_refs=[provenance],
    )


def _task_from_mapping(
    value: Any, text: str, provenance: Provenance
) -> CanonicalTask:
    data = value if isinstance(value, Mapping) else {}
    prompt = data.get("prompt")
    if isinstance(prompt, Mapping):
        request = prompt.get("text")
    else:
        request = prompt
    tools = data.get("tools")
    scoring = data.get("scoring_components")
    expected_actions = data.get("expected_actions")
    obligations: list[Any] = []
    if isinstance(scoring, list):
        for item in scoring:
            if isinstance(item, Mapping):
                obligations.append(
                    {
                        "source": "scoring_component",
                        "name": item.get("name"),
                        "weight": item.get("weight"),
                        "check": item.get("check"),
                        "raw": dict(item),
                    }
                )
            else:
                obligations.append(
                    {"source": "scoring_component", "raw": item}
                )
    if isinstance(expected_actions, list):
        for item in expected_actions:
            obligations.append(
                {
                    "source": "expected_action",
                    "action": dict(item) if isinstance(item, Mapping) else item,
                }
            )
    elif expected_actions is not None and expected_actions != "":
        obligations.append(
            {"source": "expected_action", "action": expected_actions}
        )
    explicit_obligations = data.get("obligations")
    if isinstance(explicit_obligations, list):
        obligations.extend(explicit_obligations)
    reference = data.get("reference_solution")
    if reference:
        obligations.append(
            {"source": "reference_solution", "text": reference}
        )
    safety = data.get("safety_checks")
    prohibitions: list[Any] = []
    if isinstance(safety, list):
        prohibitions.extend(
            {
                "source": "safety_check",
                **(dict(item) if isinstance(item, Mapping) else {"raw": item}),
            }
            for item in safety
        )
    explicit_prohibitions = data.get("prohibitions")
    if isinstance(explicit_prohibitions, list):
        prohibitions.extend(explicit_prohibitions)
    return CanonicalTask(
        task_id=data.get("task_id") or data.get("id"),
        title=data.get("task_name") or data.get("title") or data.get("name"),
        description=data.get("description"),
        user_request=request if isinstance(request, str) else None,
        obligations=obligations,
        prohibitions=prohibitions,
        tool_inventory=[
            dict(item) if isinstance(item, Mapping) else {"name": str(item)}
            for item in tools or []
        ],
        raw_text=text,
        raw=value,
        metadata={
            key: value
            for key, value in data.items()
            if key
            not in {
                "task_id",
                "id",
                "task_name",
                "title",
                "name",
                "description",
                "prompt",
                "obligations",
                "expected_actions",
                "scoring_components",
                "prohibitions",
                "safety_checks",
                "tools",
                "reference_solution",
            }
        },
        source_refs=[provenance],
    )


def parse_task(path: str | Path) -> TraceFragment:
    """Parse a task file while always retaining its exact original text."""

    task_path = Path(path).expanduser().resolve()
    raw_bytes = task_path.read_bytes()
    text = raw_bytes.decode("utf-8")
    file_sha = sha256_bytes(raw_bytes)
    source_id = f"{SourceKind.TASK.value}:{file_sha[:16]}"
    lines = text.splitlines()
    source = SourceArtifact(
        source_id=source_id,
        kind=SourceKind.TASK,
        path=str(task_path),
        sha256=file_sha,
        line_count=len(lines),
        nonblank_line_count=sum(bool(line.strip()) for line in lines),
        metadata={"format": task_path.suffix.lower().lstrip(".")},
    )
    provenance = Provenance(
        source_id=source_id,
        source_kind=SourceKind.TASK,
        path=str(task_path),
        line_start=1,
        line_end=max(1, len(lines)),
        raw_sha256=sha256_text(text),
        raw_text=text,
    )
    fragment = TraceFragment(source_kind=SourceKind.TASK, sources=[source])
    parsed: Any = None
    task_format: str
    parse_error: Optional[str] = None
    if task_path.suffix.lower() == ".json":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            parse_error = f"invalid task JSON: {exc}"
        task_format = "json"
    elif yaml is not None:
        try:
            parsed = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            parse_error = f"invalid task YAML: {exc}"
        task_format = "yaml"
    else:
        task_format = "yaml"
    if isinstance(parsed, Mapping):
        task = _task_from_mapping(parsed, text, provenance)
        raw_event = dict(parsed)
    else:
        task = _task_from_yaml(text, provenance)
        raw_event = {"format": task_format, "text": text}
        if parsed is not None and parse_error is None:
            parse_error = "task document root must be an object/mapping"
        elif yaml is not None and parse_error is None:
            parse_error = "task document is empty"
    fragment.task = task
    fragment.task_id_hint = task.task_id
    fragment.events.append(
        CanonicalEvent(
            event_id=f"{source_id}:document",
            source_id=source_id,
            source_kind=SourceKind.TASK,
            event_type="task.parse_error" if parse_error else "task.document",
            timestamp=None,
            sequence=None,
            run_id=None,
            parent_id=None,
            raw=raw_event,
            provenance=provenance,
            parse_error=parse_error,
        )
    )
    source.metadata["format"] = task_format
    return fragment


def parse_manifest(
    path: str | Path,
    *,
    session_path: str | Path | None = None,
    task_id: Optional[str] = None,
) -> TraceFragment:
    """Parse a manifest and derive evaluations for matching rows.

    Every manifest row remains a canonical source event.  Selection only
    controls which rows become evaluations for the current trace.
    """

    source = JsonlSource(path, SourceKind.MANIFEST)
    fragment = TraceFragment(source_kind=SourceKind.MANIFEST)
    fragment.sources.append(source.artifact)
    expected_session_name = (
        Path(session_path).name if session_path is not None else None
    )
    selection_scoped = expected_session_name is not None or task_id is not None
    selected_count = 0

    for line_number, _, raw, provenance, parse_error in source.rows():
        event = source.event(
            line_number,
            raw,
            provenance,
            parse_error,
            event_type="manifest.entry" if parse_error is None else "parse_error",
        )
        fragment.events.append(event)
        if parse_error or raw is None:
            continue
        row_session = raw.get("session_jsonl") or raw.get("session_path")
        row_session_name = Path(str(row_session)).name if row_session else None
        row_task = raw.get("task_id")
        # Without either a session or task identity there is no defensible way
        # to associate a manifest row with this trace.  Preserve every row as an
        # event, but select none instead of silently attaching the whole file.
        if not selection_scoped:
            continue
        session_match = expected_session_name is None or (
            row_session_name == expected_session_name
        )
        task_match = task_id is None or (
            row_task == task_id
            or (row_task and task_id.startswith(f"{row_task}_"))
            or (task_id and str(row_task).startswith(f"{task_id}_"))
        )
        if not (session_match and task_match):
            continue
        selected_count += 1
        passed = raw.get("passed")
        error = raw.get("error")
        score = raw.get("task_score")
        fragment.evaluations.append(
            Evaluation(
                evaluation_id=stable_id(
                    "manifest-evaluation", source.source_id, line_number
                ),
                evaluator="manifest",
                status=(
                    EvaluationStatus.ERROR
                    if error
                    else EvaluationStatus.PASSED
                    if passed is True
                    else EvaluationStatus.FAILED
                    if passed is False
                    else EvaluationStatus.UNKNOWN
                ),
                passed=passed if isinstance(passed, bool) else None,
                score=float(score) if isinstance(score, (int, float)) else None,
                failure_reason=(
                    str(raw.get("failure_mode"))
                    if raw.get("failure_mode") is not None
                    else str(error)
                    if error is not None
                    else None
                ),
                timestamp=raw.get("timestamp"),
                task_id=str(row_task) if row_task is not None else task_id,
                trace_id=None,
                details={
                    key: value
                    for key, value in raw.items()
                    if key
                    not in {
                        "passed",
                        "task_score",
                        "failure_mode",
                        "error",
                        "timestamp",
                    }
                },
                source_refs=[provenance],
            )
        )
    source.artifact.metadata["selected_entries"] = selected_count
    source.artifact.metadata["selection_scoped"] = selection_scoped
    source.artifact.metadata["selection_session_name"] = expected_session_name
    source.artifact.metadata["selection_task_id"] = task_id
    return fragment
