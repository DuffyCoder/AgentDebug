"""Luna GAIA v1: v3 semantics with ownership-safe nested-span evidence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    AgentJudgeValidationError,
    _assert_safe_path,
    _execution_fact_lines,
    _string_leaves,
    _validate_agent_judge_predictions_with_owner_sources,
)
from ._causal_task import (
    AGENT_JUDGE_LUNA_V3_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_V3_MODEL,
    AGENT_JUDGE_LUNA_V3_REASONING_EFFORT,
    AGENT_JUDGE_LUNA_V3_VERSION,
    build_agent_judge_luna_v3_task,
)
from .judge_view import JudgeView, ModuleSpan
from .taxonomy import AgentModule, ErrorType


AGENT_JUDGE_LUNA_GAIA_V1_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v1"
)
AGENT_JUDGE_LUNA_GAIA_V1_MODEL = AGENT_JUDGE_LUNA_V3_MODEL
AGENT_JUDGE_LUNA_GAIA_V1_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_V3_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V1_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_V3_AUDIT_SCHEMA_VERSION
)


def _properly_nested_or_disjoint(
    spans: Iterable[ModuleSpan],
    *,
    raw_length: int,
) -> bool:
    """Accept in-bounds disjoint/contained spans and reject crossed geometry."""

    ordered = sorted(
        spans,
        key=lambda span: (span.tag_start_char, -span.tag_end_char),
    )
    if any(
        span.tag_start_char < 0
        or span.tag_end_char <= span.tag_start_char
        or span.tag_end_char > raw_length
        or span.content_start_char < span.tag_start_char
        or span.content_end_char < span.content_start_char
        or span.content_end_char > span.tag_end_char
        for span in ordered
    ):
        return False
    if any(
        current.tag_start_char == previous.tag_start_char
        and current.tag_end_char == previous.tag_end_char
        for previous, current in zip(ordered, ordered[1:])
    ):
        return False

    open_spans: list[ModuleSpan] = []
    for span in ordered:
        while open_spans and span.tag_start_char >= open_spans[-1].tag_end_char:
            open_spans.pop()
        if open_spans and span.tag_end_char > open_spans[-1].tag_end_char:
            # The new interval begins inside an open interval but ends outside.
            return False
        open_spans.append(span)
    return True


def _subtract_intervals(
    start: int,
    end: int,
    cutouts: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    """Return disjoint pieces of [start, end) after subtracting cutouts."""

    clipped = sorted(
        (max(start, left), min(end, right))
        for left, right in cutouts
        if left < end and right > start
    )
    merged: list[tuple[int, int]] = []
    for left, right in clipped:
        if left >= right:
            continue
        if merged and left <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], right))
        else:
            merged.append((left, right))
    pieces: list[tuple[int, int]] = []
    cursor = start
    for left, right in merged:
        if cursor < left:
            pieces.append((cursor, left))
        cursor = max(cursor, right)
    if cursor < end:
        pieces.append((cursor, end))
    return tuple(pieces)


def _nested_owner_span_sources(
    view: JudgeView,
    predicted_step: int,
    module: AgentModule,
) -> tuple[str, ...]:
    """Return owner fragments without leaking nested different-owner spans."""

    step = view.steps[predicted_step - 1]
    raw = step.assistant_raw_output
    spans = tuple(step.module_spans)
    if not _properly_nested_or_disjoint(spans, raw_length=len(raw)):
        return ()
    sources: list[str] = []
    for owner in spans:
        if owner.module != module.value:
            continue
        different_owner_descendants = (
            (candidate.tag_start_char, candidate.tag_end_char)
            for candidate in spans
            if candidate.module != module.value
            and candidate.tag_start_char >= owner.tag_start_char
            and candidate.tag_end_char <= owner.tag_end_char
        )
        for start, end in _subtract_intervals(
            owner.tag_start_char,
            owner.tag_end_char,
            different_owner_descendants,
        ):
            source = raw[start:end]
            if source.strip():
                sources.append(source)
    return tuple(dict.fromkeys(sources))


def _nested_residual_sources(
    view: JudgeView,
    predicted_step: int,
) -> tuple[str, ...]:
    """Return raw-output regions outside the union of all recognized tags."""

    step = view.steps[predicted_step - 1]
    raw = step.assistant_raw_output
    spans = tuple(step.module_spans)
    if not raw or not spans or not _properly_nested_or_disjoint(
        spans,
        raw_length=len(raw),
    ):
        return ()
    residual_ranges = _subtract_intervals(
        0,
        len(raw),
        ((span.tag_start_char, span.tag_end_char) for span in spans),
    )
    if not step.text_blocks:
        return tuple(
            raw[start:end]
            for start, end in residual_ranges
            if raw[start:end].strip()
        )
    block_ranges = sorted(
        (block.start_char, block.end_char) for block in step.text_blocks
    )
    if any(
        start < 0 or end <= start or end > len(raw)
        for start, end in block_ranges
    ) or any(
        start < previous_end
        for (_previous_start, previous_end), (start, _end)
        in zip(block_ranges, block_ranges[1:])
    ):
        return ()
    sources: list[str] = []
    for residual_start, residual_end in residual_ranges:
        for block_start, block_end in block_ranges:
            start = max(residual_start, block_start)
            end = min(residual_end, block_end)
            if start < end and raw[start:end].strip():
                sources.append(raw[start:end])
    return tuple(sources)


def _luna_gaia_v1_owner_source_resolver(
    view: JudgeView,
    predicted_step: int,
    module: AgentModule,
    error_type: ErrorType,
) -> tuple[str, ...]:
    """Resolve literal evidence while supporting unambiguous nested tags."""

    if module == AgentModule.SYSTEM:
        if predicted_step != len(view.steps):
            return ()
        return _execution_fact_lines(view.execution_facts)

    step = view.steps[predicted_step - 1]
    raw = step.assistant_raw_output
    sources: list[str] = []
    if step.module_spans:
        sources.extend(_nested_owner_span_sources(view, predicted_step, module))
    elif raw.strip():
        sources.append(raw)

    if module == AgentModule.ACTION:
        for call in step.tool_calls:
            sources.append(call.name)
            sources.extend(_string_leaves(call.arguments))
            sources.extend(_string_leaves(call.partial_arguments))

    if step.module_spans and (
        module == AgentModule.PLANNING
        or (
            module == AgentModule.ACTION
            and error_type in {ErrorType.FORMAT_ERROR, ErrorType.INVALID_ACTION}
        )
    ):
        sources.extend(_nested_residual_sources(view, predicted_step))
    return tuple(dict.fromkeys(source for source in sources if source.strip()))


def build_agent_judge_luna_gaia_v1_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build v3's semantic prompt with the nested-span evidence contract."""

    task = build_agent_judge_luna_v3_task(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    task = task.replace(AGENT_JUDGE_LUNA_V3_VERSION, AGENT_JUDGE_LUNA_GAIA_V1_VERSION)
    task = task.replace(
        "agentdebug/diagnostics/_causal_task.py",
        "agentdebug/diagnostics/_nested_sources.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._causal_task import "
        "validate_and_write_agent_judge_luna_v3_audit as run",
        "from agentdebug.diagnostics._nested_sources import "
        "validate_and_write_agent_judge_luna_gaia_v1_audit as run",
    )
    old_rule = """\
evidence_quote must be exact, contiguous, case-sensitive selected-owner text
at predicted_step.  With no recognized module spans, any non-system owner may
quote assistant_raw_output.  With spans, normally quote only the owner's span;
Planning may also quote a deliberative residual, and Action may quote tool-call
name/string arguments.  Action residual text is available only for
format_error or invalid_action.  System must quote one accepted execution_facts
line at the final step.  Never quote observations, task text, another step, or
another recognized owner.
"""
    new_rule = """\
evidence_quote must be exact, contiguous, case-sensitive selected-owner text
at predicted_step.  TextBlockRange and ModuleSpan objects contain offsets, not
a separate `text` field: obtain literal text by slicing assistant_raw_output.
With no recognized module spans, any non-system owner may quote
assistant_raw_output.  Recognized spans may be disjoint or properly nested.  A
nested different-owner span is excluded from its outer owner's evidence: quote
one contiguous fragment before or after that nested range, never across it.
Planning may also quote a deliberative residual outside all recognized tags,
and Action may quote tool-call name/string arguments.  Action residual text is
available only for format_error or invalid_action.  Crossing (non-contained)
span geometry remains invalid.  System must quote one accepted execution_facts
line at the final step.  Never quote observations, task text, another step, or
another recognized owner.
"""
    if old_rule not in task:
        raise RuntimeError("Luna v3 evidence rule changed unexpectedly")
    return task.replace(old_rule, new_rule)


def validate_agent_judge_luna_gaia_v1_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    audit = _validate_agent_judge_predictions_with_owner_sources(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
        owner_source_resolver=_luna_gaia_v1_owner_source_resolver,
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V1_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V1_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V1_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V1_REASONING_EFFORT,
        "evidence_geometry": "disjoint_or_properly_nested_owner_fragments",
    }


def validate_and_write_agent_judge_luna_gaia_v1_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v1_predictions(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    target = Path(audit_path).expanduser().resolve()
    _assert_safe_path(target, role="prediction audit output", is_output=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(f"{target.suffix}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)
    return audit


__all__ = [
    "AGENT_JUDGE_LUNA_GAIA_V1_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V1_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V1_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V1_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "build_agent_judge_luna_gaia_v1_task",
    "validate_agent_judge_luna_gaia_v1_predictions",
    "validate_and_write_agent_judge_luna_gaia_v1_audit",
]
