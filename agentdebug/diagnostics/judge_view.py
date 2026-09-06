"""Compact, evidence-preserving projection of a :class:`CanonicalTrace`.

``JudgeView`` is deliberately a projection rather than another trace schema:

* one view step corresponds to exactly one canonical assistant turn;
* every displayed entity retains its canonical event/entity identifiers;
* text is never truncated;
* optional XML-like module tags are exposed as spans, not interpreted as
  diagnoses; and
* tool results are joined to calls only through canonical call/result links.

The projection does not read benchmark labels or evaluator annotations.  It is
therefore safe to construct before a benchmark evaluator loads its gold data.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

from agentdebug.trace.models import (
    AssistantTurn,
    CanonicalMessage,
    CanonicalTrace,
    ContentBlock,
    MessageRole,
    Provenance,
    SourceKind,
    ToolCall,
    ToolResult,
)


JUDGE_VIEW_VERSION = (
    "canonical-judge-view-v3-aeb-incremental-execution-facts"
)

# These are observable markup conventions in released AgentErrorBench traces.
# Finding a tag does not assert that the corresponding behavior is correct or
# erroneous.  Missing and malformed tags simply yield no ModuleSpan.
_TAG_TO_MODULE = {
    "memory": "memory",
    "reflection": "reflection",
    "plan": "planning",
    "action": "action",
    "memory_recall": "memory",
    "tool_call": "action",
    "answer": "action",
    "think": "planning",
}
_MODULE_TAGS = tuple(_TAG_TO_MODULE)
_CUMULATIVE_PREFIX_MIN_CHARS = 64
_STATIC_REFERENCE_MIN_CHARS = 80

_BENCHMARK_HISTORY_RE = re.compile(
    r"^Prior to this step, you have already taken "
    r"(?P<count>\d+) step\(s\)\.",
    flags=re.IGNORECASE | re.MULTILINE,
)
_BENCHMARK_CURRENT_RE = re.compile(
    r"^You are now at step (?P<step>\d+)"
    r"(?P<final_marker>[ \t]+and[ \t]+this[ \t]+is[ \t]+the"
    r"[ \t]+final[ \t]+step\.)?"
    r"(?:[ \t]+and[ \t]+your current observation is:"
    r"|(?:\.)?[ \t]*\r?\nCurrent Observation:)[ \t]*",
    flags=re.IGNORECASE | re.MULTILINE,
)
_BENCHMARK_OBSERVATION_END_PATTERNS = (
    (
        "admissible_actions",
        re.compile(
            r"^Your admissible actions of the current situation are:",
            flags=re.IGNORECASE | re.MULTILINE,
        ),
    ),
    (
        "available_tools",
        re.compile(
            r"^Available Tools\s*:",
            flags=re.IGNORECASE | re.MULTILINE,
        ),
    ),
    (
        "instructions",
        re.compile(
            r"^Instructions\s*:",
            flags=re.IGNORECASE | re.MULTILINE,
        ),
    ),
)
_BENCHMARK_FORMAT_START_RE = re.compile(
    r"^Now it['’]s your turn",
    flags=re.IGNORECASE | re.MULTILINE,
)
_BENCHMARK_FINAL_ANSWER_RE = re.compile(
    r"^You must provide your final answer within",
    flags=re.IGNORECASE | re.MULTILINE,
)


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _indent(text: str, prefix: str = "    ") -> list[str]:
    # split("\n") preserves intentional trailing blank lines in source text.
    return [f"{prefix}{line}" for line in text.split("\n")]


@dataclass(frozen=True)
class SourceReference:
    """Compact pointer to exact canonical provenance."""

    source_id: str
    source_kind: str
    path: str
    line_start: int
    line_end: int
    raw_sha256: str


@dataclass(frozen=True)
class TextBlockRange:
    """A source content block's half-open range in ``assistant_raw_output``."""

    event_id: str
    block_index: int
    block_type: str
    start_char: int
    end_char: int
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class ThinkingSpan:
    """An explicit thinking/reasoning block in assistant output."""

    event_id: str
    block_index: int
    kind: str
    start_char: int
    end_char: int
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class ModuleSpan:
    """One complete observable module tag and its source-relative offsets.

    All offsets are zero-based, half-open character ranges into the enclosing
    step's ``assistant_raw_output``.  ``tag_*`` covers the opening tag, content,
    and closing tag; ``content_*`` covers only the tag body.
    """

    tag: str
    module: str
    event_id: str
    block_index: int
    tag_start_char: int
    tag_end_char: int
    content_start_char: int
    content_end_char: int
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class BenchmarkInputProjection:
    """Auditable ranges for one cumulative AgentErrorBench user message.

    The projection exists only when all structural markers are unambiguous and
    the declared current/prior step counts agree.  Every range is zero-based
    and half-open in :attr:`JudgeObservation.text`.
    """

    declared_step: int
    declared_prior_step_count: int
    prefix_start_char: int
    prefix_end_char: int
    history_start_char: int
    history_end_char: int
    step_marker_start_char: int
    step_marker_end_char: int
    observation_start_char: int
    observation_end_char: int
    interface_start_char: int
    interface_end_char: int
    suffix_start_char: int
    suffix_end_char: int
    observation_end_marker: str


@dataclass(frozen=True)
class JudgeObservation:
    """A non-assistant message visible immediately around a decision."""

    event_id: str
    message_id: str
    role: str
    text: str
    # If set, ``text[:repeated_prefix_chars]`` is exactly the complete text of
    # the referenced earlier observation.  Renderers may safely show only the
    # suffix while retaining ``text`` here for audit and evidence lookup.
    repeated_prefix_event_id: Optional[str] = None
    repeated_prefix_chars: int = 0
    linked_tool_result_ids: tuple[str, ...] = ()
    source_refs: tuple[SourceReference, ...] = ()
    benchmark_input: Optional[BenchmarkInputProjection] = None

    @property
    def incremental_text(self) -> str:
        return self.text[self.repeated_prefix_chars :]


@dataclass(frozen=True)
class JudgeToolResult:
    result_id: str
    call_id: Optional[str]
    event_id: str
    name: Optional[str]
    status: str
    is_error: Optional[bool]
    output: str
    details: Any = None
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class JudgeToolCall:
    call_id: str
    event_id: str
    name: str
    normalized_name: str
    arguments: Any
    partial_arguments: Any
    status: str
    content_block_index: Optional[int]
    results: tuple[JudgeToolResult, ...] = ()
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class JudgeStep:
    """One assistant decision in canonical turn order."""

    step: int
    turn_id: str
    assistant_event_id: str
    assistant_message_id: str
    current_input: tuple[JudgeObservation, ...]
    assistant_raw_output: str
    text_blocks: tuple[TextBlockRange, ...]
    thinking_spans: tuple[ThinkingSpan, ...]
    module_spans: tuple[ModuleSpan, ...]
    tool_calls: tuple[JudgeToolCall, ...]
    adjacent_feedback: tuple[JudgeObservation, ...]
    stop_reason: Optional[str] = None
    error_message: Optional[str] = None
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class JudgeTask:
    task_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    user_request: Optional[str]
    source_refs: tuple[SourceReference, ...] = ()

    @property
    def display_text(self) -> str:
        parts: list[str] = []
        if self.user_request:
            parts.append(self.user_request)
        if self.description and self.description != self.user_request:
            parts.append(self.description)
        return "\n".join(parts)


@dataclass(frozen=True)
class JudgeExecutionFacts:
    """Strictly whitelisted observable execution facts.

    ``metadata_steps``, ``metadata_won``, and ``metadata_success`` come only
    from one provenance-backed AgentErrorBench ``benchmark.metadata`` event.
    They are source execution metadata, never benchmark gold annotations.
    Canonical turn facts are included only while that source event is present,
    so an OpenClaw trace without AgentErrorBench metadata is unchanged.
    """

    source_event_id: str
    source_kind: str
    metadata_steps: Optional[int]
    metadata_won: Optional[bool]
    metadata_success: Optional[bool]
    canonical_turn_count: int
    final_stop_reason: Optional[str] = None
    final_error_message: Optional[str] = None
    source_refs: tuple[SourceReference, ...] = ()


@dataclass(frozen=True)
class _StaticReference:
    observation: JudgeObservation
    start_char: int
    end_char: int


@dataclass(frozen=True)
class _RegionPiece:
    start_char: int
    end_char: int
    reference: Optional[_StaticReference]


def _is_agent_error_bench(observation: JudgeObservation) -> bool:
    return any(
        ref.source_kind == "agent_error_bench"
        for ref in observation.source_refs
    )


def _paragraph_ranges(text: str, start: int, end: int) -> list[tuple[int, int]]:
    """Split a source range at blank lines while retaining every character."""

    if start >= end:
        return []
    result: list[tuple[int, int]] = []
    cursor = start
    for match in re.finditer(r"\r?\n[ \t]*\r?\n", text[start:end]):
        boundary = start + match.end()
        if boundary > cursor:
            result.append((cursor, boundary))
        cursor = boundary
    if cursor < end:
        result.append((cursor, end))
    return result


def _first_static_reference(
    fragment: str,
    prior_observations: Sequence[JudgeObservation],
) -> Optional[_StaticReference]:
    if len(fragment.strip()) < _STATIC_REFERENCE_MIN_CHARS:
        return None
    for prior in prior_observations:
        start = prior.text.find(fragment)
        if start >= 0:
            return _StaticReference(
                observation=prior,
                start_char=start,
                end_char=start + len(fragment),
            )
    return None


def _region_pieces(
    observation: JudgeObservation,
    *,
    start: int,
    end: int,
    prior_observations: Sequence[JudgeObservation],
) -> list[_RegionPiece]:
    pieces: list[_RegionPiece] = []
    for piece_start, piece_end in _paragraph_ranges(
        observation.text,
        start,
        end,
    ):
        fragment = observation.text[piece_start:piece_end]
        reference = _first_static_reference(fragment, prior_observations)
        piece = _RegionPiece(piece_start, piece_end, reference)
        if pieces:
            previous = pieces[-1]
            both_verbatim = previous.reference is None and reference is None
            same_reference = (
                previous.reference is not None
                and reference is not None
                and previous.reference.observation.message_id
                == reference.observation.message_id
                and previous.reference.end_char == reference.start_char
            )
            if (
                previous.end_char == piece_start
                and (both_verbatim or same_reference)
            ):
                pieces[-1] = _RegionPiece(
                    start_char=previous.start_char,
                    end_char=piece_end,
                    reference=(
                        None
                        if both_verbatim
                        else _StaticReference(
                            observation=previous.reference.observation,
                            start_char=previous.reference.start_char,
                            end_char=reference.end_char,
                        )
                    ),
                )
                continue
        pieces.append(piece)
    return pieces


def _render_benchmark_region(
    lines: list[str],
    *,
    heading: str,
    observation: JudgeObservation,
    start: int,
    end: int,
    prior_observations: Sequence[JudgeObservation],
) -> None:
    lines.append(f"        {heading}")
    if start >= end:
        lines.append("            (none)")
        return
    for piece in _region_pieces(
        observation,
        start=start,
        end=end,
        prior_observations=prior_observations,
    ):
        reference = piece.reference
        if reference is not None:
            lines.append(
                "            [exact prior text omitted: "
                f"event_id={observation.event_id} "
                f"source_chars={piece.start_char}:{piece.end_char}; "
                f"first_shown_event_id={reference.observation.event_id} "
                f"source_chars={reference.start_char}:{reference.end_char}]"
            )
            continue
        lines.append(
            "            [verbatim "
            f"event_id={observation.event_id} "
            f"source_chars={piece.start_char}:{piece.end_char}]"
        )
        lines.extend(
            _indent(
                observation.text[piece.start_char:piece.end_char]
                or "(empty)",
                "            ",
            )
        )


def _render_benchmark_current_input(
    lines: list[str],
    *,
    observation: JudgeObservation,
    step: JudgeStep,
    all_steps: Sequence[JudgeStep],
    prior_observations: Sequence[JudgeObservation],
) -> bool:
    projection = observation.benchmark_input
    if (
        projection is None
        or projection.declared_step != step.step
        or projection.declared_prior_step_count != step.step - 1
    ):
        return False

    lines.append(
        "        [AgentErrorBench cumulative input safely projected: "
        f"event_id={observation.event_id} "
        f"source_chars=0:{len(observation.text)}; "
        "JudgeObservation.text remains complete]"
    )
    _render_benchmark_region(
        lines,
        heading="STATIC HEADER / TASK",
        observation=observation,
        start=projection.prefix_start_char,
        end=projection.prefix_end_char,
        prior_observations=prior_observations,
    )

    prior_steps = all_steps[: step.step - 1]
    first_event = prior_steps[0].assistant_event_id
    last_event = prior_steps[-1].assistant_event_id
    lines.append("        PRIOR OBSERVATION / ACTION HISTORY")
    lines.append(
        "            [history omitted: "
        f"event_id={observation.event_id} "
        f"source_chars={projection.history_start_char}:"
        f"{projection.history_end_char}; "
        f"represented_by=STEP 1..{step.step - 1}; "
        f"first_assistant_event_id={first_event}; "
        f"last_assistant_event_id={last_event}]"
    )

    lines.append("        CURRENT STEP MARKER (verbatim)")
    lines.append(
        "            ["
        f"event_id={observation.event_id} "
        f"source_chars={projection.step_marker_start_char}:"
        f"{projection.step_marker_end_char}]"
    )
    lines.extend(
        _indent(
            observation.text[
                projection.step_marker_start_char:
                projection.step_marker_end_char
            ],
            "            ",
        )
    )

    lines.append("        CURRENT OBSERVATION (verbatim, never truncated)")
    lines.append(
        "            ["
        f"event_id={observation.event_id} "
        f"source_chars={projection.observation_start_char}:"
        f"{projection.observation_end_char}; "
        f"terminated_by={projection.observation_end_marker}]"
    )
    lines.extend(
        _indent(
            observation.text[
                projection.observation_start_char:
                projection.observation_end_char
            ]
            or "(empty)",
            "            ",
        )
    )

    if projection.interface_start_char < projection.interface_end_char:
        lines.append("        CURRENT ADMISSIBLE INTERFACE (verbatim)")
        lines.append(
            "            ["
            f"event_id={observation.event_id} "
            f"source_chars={projection.interface_start_char}:"
            f"{projection.interface_end_char}]"
        )
        lines.extend(
            _indent(
                observation.text[
                    projection.interface_start_char:
                    projection.interface_end_char
                ],
                "            ",
            )
        )

    _render_benchmark_region(
        lines,
        heading="REMAINING TOOL / FORMAT INSTRUCTIONS",
        observation=observation,
        start=projection.suffix_start_char,
        end=projection.suffix_end_char,
        prior_observations=prior_observations,
    )
    return True


@dataclass(frozen=True)
class JudgeView:
    """Readable diagnostic input derived exclusively from a canonical trace."""

    version: str
    trace_id: str
    task: Optional[JudgeTask]
    execution_facts: Optional[JudgeExecutionFacts]
    steps: tuple[JudgeStep, ...]

    def to_dict(self) -> dict[str, Any]:
        return _json_value(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "JudgeView":
        """Reconstruct a persisted, gold-free reasoning projection.

        Production benchmark prediction runs consume a serialized
        :class:`JudgeView` instead of a ``BenchmarkExample``.  Keeping the
        inverse constructor beside :meth:`to_dict` makes that process boundary
        explicit and avoids reloading benchmark labels in the provider
        process.
        """

        return _judge_view_from_dict(data)

    def event_for_step(self, step: int) -> Optional[str]:
        if step < 1 or step > len(self.steps):
            return None
        return self.steps[step - 1].assistant_event_id

    def step_for_event(self, event_id: str) -> Optional[int]:
        for item in self.steps:
            if item.assistant_event_id == event_id:
                return item.step
        return None

    def render_timeline(self, *, compact: bool = True) -> str:
        """Render a prompt-ready timeline without truncating evidence.

        In compact mode, content already rendered as the task, a prior step's
        feedback, or a linked tool result is referenced by ID instead of copied.
        Exact cumulative prefixes are likewise referenced, while their complete
        incremental suffix remains verbatim.  ``compact=False`` repeats every
        observation's full text for debugging the projection itself.
        """

        lines = [
            f"TRACE trace_id={self.trace_id} judge_view={self.version}",
        ]
        if self.execution_facts is not None:
            facts = self.execution_facts
            lines.append(
                "EXECUTION FACTS "
                "(OBSERVABLE SOURCE METADATA; NOT GOLD LABELS)"
            )
            lines.append(
                f"    source_kind={facts.source_kind} "
                f"source_event_id={facts.source_event_id}"
            )
            if facts.metadata_steps is not None:
                lines.append(
                    "    benchmark.metadata.steps="
                    f"{facts.metadata_steps}"
                )
            if facts.metadata_won is not None:
                lines.append(
                    "    benchmark.metadata.won="
                    f"{_stable_json(facts.metadata_won)}"
                )
            if facts.metadata_success is not None:
                lines.append(
                    "    benchmark.metadata.success="
                    f"{_stable_json(facts.metadata_success)}"
                )
            lines.append(
                f"    canonical.turn_count={facts.canonical_turn_count}"
            )
            if facts.final_stop_reason is not None:
                lines.append(
                    "    canonical.final_stop_reason="
                    f"{_stable_json(facts.final_stop_reason)}"
                )
            if facts.final_error_message is not None:
                lines.append(
                    "    canonical.final_error_message="
                    f"{_stable_json(facts.final_error_message)}"
                )
        rendered_messages: set[str] = set()
        rendered_results: set[str] = set()
        prior_benchmark_observations: list[JudgeObservation] = []
        prior_benchmark_message_ids: set[str] = set()
        benchmark_current_step_by_message = {
            observation.message_id: step.step
            for step in self.steps
            for observation in step.current_input
            if _is_agent_error_bench(observation)
        }
        task_text = self.task.display_text if self.task is not None else ""
        if self.task is not None:
            lines.append("TASK")
            lines.extend(_indent(task_text or "(not provided)"))

        def remember_benchmark(observation: JudgeObservation) -> None:
            if (
                _is_agent_error_bench(observation)
                and observation.message_id not in prior_benchmark_message_ids
            ):
                prior_benchmark_observations.append(observation)
                prior_benchmark_message_ids.add(observation.message_id)

        def render_observations(
            heading: str,
            observations: Sequence[JudgeObservation],
            *,
            step: JudgeStep,
            is_current_input: bool,
        ) -> None:
            lines.append(heading)
            if not observations:
                lines.append("    (none)")
                return
            for observation in observations:
                identity = observation.message_id
                label = (
                    f"[{observation.role} event_id={observation.event_id} "
                    f"message_id={observation.message_id}]"
                )
                lines.append(f"    {label}")
                future_step = benchmark_current_step_by_message.get(identity)
                if (
                    compact
                    and not is_current_input
                    and future_step is not None
                    and future_step > step.step
                ):
                    lines.append(
                        "        (content deferred to its non-duplicated "
                        f"STEP {future_step} current input; "
                        f"event_id={observation.event_id})"
                    )
                    continue
                if compact and identity in rendered_messages:
                    lines.append("        (content already shown; referenced by IDs)")
                    continue
                if (
                    compact
                    and observation.linked_tool_result_ids
                    and all(
                        result_id in rendered_results
                        for result_id in observation.linked_tool_result_ids
                    )
                ):
                    result_ids = ", ".join(observation.linked_tool_result_ids)
                    lines.append(
                        "        (content shown with linked tool result(s): "
                        f"{result_ids})"
                    )
                    rendered_messages.add(identity)
                    continue
                if compact and task_text and observation.text == task_text:
                    lines.append("        (content is identical to TASK above)")
                    rendered_messages.add(identity)
                    if is_current_input:
                        remember_benchmark(observation)
                    continue
                if (
                    compact
                    and is_current_input
                    and _is_agent_error_bench(observation)
                ):
                    safely_projected = _render_benchmark_current_input(
                        lines,
                        observation=observation,
                        step=step,
                        all_steps=self.steps,
                        prior_observations=prior_benchmark_observations,
                    )
                    if not safely_projected:
                        lines.append(
                            "        [AgentErrorBench projection unavailable; "
                            "full input rendered verbatim: "
                            f"event_id={observation.event_id} "
                            f"source_chars=0:{len(observation.text)}]"
                        )
                        lines.extend(
                            _indent(
                                observation.text or "(empty)",
                                "        ",
                            )
                        )
                    rendered_messages.add(identity)
                    remember_benchmark(observation)
                    continue
                if (
                    compact
                    and observation.repeated_prefix_event_id is not None
                    and observation.repeated_prefix_chars > 0
                ):
                    lines.append(
                        "        [exact repeated prefix omitted: "
                        f"{observation.repeated_prefix_chars} chars from "
                        f"event_id={observation.repeated_prefix_event_id}]"
                    )
                    suffix = observation.incremental_text
                    lines.extend(_indent(suffix or "(no incremental content)", "        "))
                else:
                    lines.extend(_indent(observation.text or "(empty)", "        "))
                rendered_messages.add(identity)
                if is_current_input:
                    remember_benchmark(observation)

        for step in self.steps:
            lines.append(
                f"STEP {step.step} assistant_event_id={step.assistant_event_id} "
                f"turn_id={step.turn_id}"
            )
            render_observations(
                "CURRENT INPUT / OBSERVATION",
                step.current_input,
                step=step,
                is_current_input=True,
            )

            lines.append("ASSISTANT RAW OUTPUT")
            if not step.text_blocks:
                lines.append("    (no textual output)")
            for block in step.text_blocks:
                lines.append(
                    f"    [{block.block_type} block={block.block_index} "
                    f"chars={block.start_char}:{block.end_char}]"
                )
                lines.extend(
                    _indent(
                        step.assistant_raw_output[
                            block.start_char : block.end_char
                        ]
                        or "(empty)",
                        "        ",
                    )
                )

            if step.thinking_spans:
                lines.append("THINKING / REASONING SPANS")
                for span in step.thinking_spans:
                    lines.append(
                        f"    - kind={span.kind} event_id={span.event_id} "
                        f"block={span.block_index} "
                        f"chars={span.start_char}:{span.end_char}"
                    )

            if step.module_spans:
                lines.append("OBSERVED MODULE TAG SPANS")
                for span in step.module_spans:
                    lines.append(
                        f"    - tag={span.tag} module={span.module} "
                        f"event_id={span.event_id} block={span.block_index} "
                        f"tag_chars={span.tag_start_char}:{span.tag_end_char} "
                        f"content_chars="
                        f"{span.content_start_char}:{span.content_end_char}"
                    )

            lines.append("TOOL CALLS AND LINKED RESULTS")
            if not step.tool_calls:
                lines.append("    (none)")
            for call in step.tool_calls:
                lines.append(
                    f"    CALL call_id={call.call_id} event_id={call.event_id} "
                    f"name={call.name} status={call.status}"
                )
                lines.append(f"        arguments={_stable_json(call.arguments)}")
                if call.partial_arguments is not None:
                    lines.append(
                        "        partial_arguments="
                        f"{_stable_json(call.partial_arguments)}"
                    )
                if not call.results:
                    lines.append("        RESULTS (none)")
                for result in call.results:
                    lines.append(
                        f"        RESULT result_id={result.result_id} "
                        f"call_id={result.call_id} event_id={result.event_id} "
                        f"status={result.status}"
                    )
                    lines.extend(_indent(result.output or "(empty)", "            "))
                    if result.details is not None:
                        lines.append(
                            f"            details={_stable_json(result.details)}"
                        )
                    rendered_results.add(result.result_id)

            render_observations(
                "ADJACENT FEEDBACK",
                step.adjacent_feedback,
                step=step,
                is_current_input=False,
            )

        return "\n".join(lines)


def _source_reference_from_dict(data: Mapping[str, Any]) -> SourceReference:
    return SourceReference(
        source_id=str(data["source_id"]),
        source_kind=str(data["source_kind"]),
        path=str(data["path"]),
        line_start=int(data["line_start"]),
        line_end=int(data["line_end"]),
        raw_sha256=str(data["raw_sha256"]),
    )


def _source_references(
    values: Sequence[Mapping[str, Any]] | None,
) -> tuple[SourceReference, ...]:
    return tuple(
        _source_reference_from_dict(value)
        for value in (values or ())
    )


def _benchmark_input_from_dict(
    data: Mapping[str, Any] | None,
) -> Optional[BenchmarkInputProjection]:
    if data is None:
        return None
    return BenchmarkInputProjection(
        declared_step=int(data["declared_step"]),
        declared_prior_step_count=int(data["declared_prior_step_count"]),
        prefix_start_char=int(data["prefix_start_char"]),
        prefix_end_char=int(data["prefix_end_char"]),
        history_start_char=int(data["history_start_char"]),
        history_end_char=int(data["history_end_char"]),
        step_marker_start_char=int(data["step_marker_start_char"]),
        step_marker_end_char=int(data["step_marker_end_char"]),
        observation_start_char=int(data["observation_start_char"]),
        observation_end_char=int(data["observation_end_char"]),
        interface_start_char=int(data["interface_start_char"]),
        interface_end_char=int(data["interface_end_char"]),
        suffix_start_char=int(data["suffix_start_char"]),
        suffix_end_char=int(data["suffix_end_char"]),
        observation_end_marker=str(data["observation_end_marker"]),
    )


def _observation_from_dict(data: Mapping[str, Any]) -> JudgeObservation:
    benchmark_input = data.get("benchmark_input")
    if benchmark_input is not None and not isinstance(
        benchmark_input,
        Mapping,
    ):
        raise TypeError("JudgeObservation.benchmark_input must be an object")
    return JudgeObservation(
        event_id=str(data["event_id"]),
        message_id=str(data["message_id"]),
        role=str(data["role"]),
        text=str(data["text"]),
        repeated_prefix_event_id=(
            str(data["repeated_prefix_event_id"])
            if data.get("repeated_prefix_event_id") is not None
            else None
        ),
        repeated_prefix_chars=int(data.get("repeated_prefix_chars", 0)),
        linked_tool_result_ids=tuple(
            str(value) for value in data.get("linked_tool_result_ids", ())
        ),
        source_refs=_source_references(data.get("source_refs")),
        benchmark_input=_benchmark_input_from_dict(benchmark_input),
    )


def _text_block_from_dict(data: Mapping[str, Any]) -> TextBlockRange:
    return TextBlockRange(
        event_id=str(data["event_id"]),
        block_index=int(data["block_index"]),
        block_type=str(data["block_type"]),
        start_char=int(data["start_char"]),
        end_char=int(data["end_char"]),
        source_refs=_source_references(data.get("source_refs")),
    )


def _thinking_span_from_dict(data: Mapping[str, Any]) -> ThinkingSpan:
    return ThinkingSpan(
        event_id=str(data["event_id"]),
        block_index=int(data["block_index"]),
        kind=str(data["kind"]),
        start_char=int(data["start_char"]),
        end_char=int(data["end_char"]),
        source_refs=_source_references(data.get("source_refs")),
    )


def _module_span_from_dict(data: Mapping[str, Any]) -> ModuleSpan:
    return ModuleSpan(
        tag=str(data["tag"]),
        module=str(data["module"]),
        event_id=str(data["event_id"]),
        block_index=int(data["block_index"]),
        tag_start_char=int(data["tag_start_char"]),
        tag_end_char=int(data["tag_end_char"]),
        content_start_char=int(data["content_start_char"]),
        content_end_char=int(data["content_end_char"]),
        source_refs=_source_references(data.get("source_refs")),
    )


def _tool_result_from_dict(data: Mapping[str, Any]) -> JudgeToolResult:
    return JudgeToolResult(
        result_id=str(data["result_id"]),
        call_id=(
            str(data["call_id"]) if data.get("call_id") is not None else None
        ),
        event_id=str(data["event_id"]),
        name=str(data["name"]) if data.get("name") is not None else None,
        status=str(data["status"]),
        is_error=(
            bool(data["is_error"])
            if data.get("is_error") is not None
            else None
        ),
        output=str(data["output"]),
        details=copy.deepcopy(data.get("details")),
        source_refs=_source_references(data.get("source_refs")),
    )


def _tool_call_from_dict(data: Mapping[str, Any]) -> JudgeToolCall:
    return JudgeToolCall(
        call_id=str(data["call_id"]),
        event_id=str(data["event_id"]),
        name=str(data["name"]),
        normalized_name=str(data["normalized_name"]),
        arguments=copy.deepcopy(data.get("arguments")),
        partial_arguments=copy.deepcopy(data.get("partial_arguments")),
        status=str(data["status"]),
        content_block_index=(
            int(data["content_block_index"])
            if data.get("content_block_index") is not None
            else None
        ),
        results=tuple(
            _tool_result_from_dict(value)
            for value in data.get("results", ())
        ),
        source_refs=_source_references(data.get("source_refs")),
    )


def _step_from_dict(data: Mapping[str, Any]) -> JudgeStep:
    return JudgeStep(
        step=int(data["step"]),
        turn_id=str(data["turn_id"]),
        assistant_event_id=str(data["assistant_event_id"]),
        assistant_message_id=str(data["assistant_message_id"]),
        current_input=tuple(
            _observation_from_dict(value)
            for value in data.get("current_input", ())
        ),
        assistant_raw_output=str(data["assistant_raw_output"]),
        text_blocks=tuple(
            _text_block_from_dict(value)
            for value in data.get("text_blocks", ())
        ),
        thinking_spans=tuple(
            _thinking_span_from_dict(value)
            for value in data.get("thinking_spans", ())
        ),
        module_spans=tuple(
            _module_span_from_dict(value)
            for value in data.get("module_spans", ())
        ),
        tool_calls=tuple(
            _tool_call_from_dict(value)
            for value in data.get("tool_calls", ())
        ),
        adjacent_feedback=tuple(
            _observation_from_dict(value)
            for value in data.get("adjacent_feedback", ())
        ),
        stop_reason=(
            str(data["stop_reason"])
            if data.get("stop_reason") is not None
            else None
        ),
        error_message=(
            str(data["error_message"])
            if data.get("error_message") is not None
            else None
        ),
        source_refs=_source_references(data.get("source_refs")),
    )


def _judge_view_from_dict(data: Mapping[str, Any]) -> JudgeView:
    if not isinstance(data, Mapping):
        raise TypeError("JudgeView data must be an object")
    task_data = data.get("task")
    if task_data is not None and not isinstance(task_data, Mapping):
        raise TypeError("JudgeView.task must be an object")
    facts_data = data.get("execution_facts")
    if facts_data is not None and not isinstance(facts_data, Mapping):
        raise TypeError("JudgeView.execution_facts must be an object")
    task = (
        JudgeTask(
            task_id=(
                str(task_data["task_id"])
                if task_data.get("task_id") is not None
                else None
            ),
            title=(
                str(task_data["title"])
                if task_data.get("title") is not None
                else None
            ),
            description=(
                str(task_data["description"])
                if task_data.get("description") is not None
                else None
            ),
            user_request=(
                str(task_data["user_request"])
                if task_data.get("user_request") is not None
                else None
            ),
            source_refs=_source_references(task_data.get("source_refs")),
        )
        if task_data is not None
        else None
    )
    execution_facts = (
        JudgeExecutionFacts(
            source_event_id=str(facts_data["source_event_id"]),
            source_kind=str(facts_data["source_kind"]),
            metadata_steps=(
                int(facts_data["metadata_steps"])
                if facts_data.get("metadata_steps") is not None
                else None
            ),
            metadata_won=(
                bool(facts_data["metadata_won"])
                if facts_data.get("metadata_won") is not None
                else None
            ),
            metadata_success=(
                bool(facts_data["metadata_success"])
                if facts_data.get("metadata_success") is not None
                else None
            ),
            canonical_turn_count=int(facts_data["canonical_turn_count"]),
            final_stop_reason=(
                str(facts_data["final_stop_reason"])
                if facts_data.get("final_stop_reason") is not None
                else None
            ),
            final_error_message=(
                str(facts_data["final_error_message"])
                if facts_data.get("final_error_message") is not None
                else None
            ),
            source_refs=_source_references(facts_data.get("source_refs")),
        )
        if facts_data is not None
        else None
    )
    view = JudgeView(
        version=str(data["version"]),
        trace_id=str(data["trace_id"]),
        task=task,
        execution_facts=execution_facts,
        steps=tuple(
            _step_from_dict(value) for value in data.get("steps", ())
        ),
    )
    if view.version != JUDGE_VIEW_VERSION:
        raise ValueError(
            "persisted JudgeView version does not match this implementation"
        )
    if any(step.step != index for index, step in enumerate(view.steps, 1)):
        raise ValueError("persisted JudgeView steps are not contiguous")
    return view


def _source_refs(
    values: Iterable[Provenance],
) -> tuple[SourceReference, ...]:
    result: list[SourceReference] = []
    seen: set[tuple[str, int, int, str]] = set()
    for value in values:
        key = (
            value.source_id,
            value.line_start,
            value.line_end,
            value.raw_sha256,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(
            SourceReference(
                source_id=value.source_id,
                source_kind=value.source_kind.value,
                path=value.path,
                line_start=value.line_start,
                line_end=value.line_end,
                raw_sha256=value.raw_sha256,
            )
        )
    return tuple(result)


def _execution_facts(
    trace: CanonicalTrace,
) -> Optional[JudgeExecutionFacts]:
    """Project a tiny allowlist from one authentic benchmark metadata event."""

    source_ids = {
        source.source_id
        for source in trace.sources
        if source.kind == SourceKind.AGENT_ERROR_BENCH
    }
    candidates = [
        event
        for event in trace.events
        if (
            event.event_type == "benchmark.metadata"
            and event.source_kind == SourceKind.AGENT_ERROR_BENCH
            and event.provenance.source_kind == SourceKind.AGENT_ERROR_BENCH
            and event.source_id == event.provenance.source_id
            and event.source_id in source_ids
        )
    ]
    # Multiple candidates are ambiguous; do not guess which source metadata is
    # authoritative.  This also keeps arbitrary canonical/OpenClaw metadata out.
    if len(candidates) != 1:
        return None
    event = candidates[0]
    if not isinstance(event.raw, Mapping):
        return None
    metadata = event.raw

    raw_steps = metadata.get("steps")
    metadata_steps = (
        raw_steps
        if (
            isinstance(raw_steps, int)
            and not isinstance(raw_steps, bool)
            and raw_steps >= 0
        )
        else None
    )
    raw_won = metadata.get("won")
    metadata_won = raw_won if isinstance(raw_won, bool) else None
    raw_success = metadata.get("success")
    metadata_success = (
        raw_success if isinstance(raw_success, bool) else None
    )
    if (
        metadata_steps is None
        and metadata_won is None
        and metadata_success is None
    ):
        return None

    final_turn = (
        trace.turn_by_id(trace.final_turn_id)
        if trace.final_turn_id is not None
        else None
    )
    if final_turn is None and trace.assistant_turns:
        final_turn = trace.assistant_turns[-1]
    final_stop_reason = (
        final_turn.stop_reason
        if (
            final_turn is not None
            and isinstance(final_turn.stop_reason, str)
        )
        else None
    )
    final_error_message = (
        final_turn.error_message
        if (
            final_turn is not None
            and isinstance(final_turn.error_message, str)
        )
        else None
    )
    return JudgeExecutionFacts(
        source_event_id=event.event_id,
        source_kind=event.source_kind.value,
        metadata_steps=metadata_steps,
        metadata_won=metadata_won,
        metadata_success=metadata_success,
        canonical_turn_count=len(trace.assistant_turns),
        final_stop_reason=final_stop_reason,
        final_error_message=final_error_message,
        source_refs=_source_refs((event.provenance,)),
    )


def _project_block(block: ContentBlock) -> Optional[str]:
    if block.text is not None:
        return block.text
    if block.block_type in {"tool_call", "tool_result"}:
        return None
    if block.data is None:
        return None
    return _stable_json(block.data)


def _content_text(blocks: Sequence[ContentBlock]) -> str:
    return "".join(
        projected
        for block in blocks
        if (projected := _project_block(block)) is not None
    )


def _tag_pattern(tag: str) -> re.Pattern[str]:
    # Per-tag patterns allow nested tags of a different supported kind to keep
    # their own spans.  Only complete matching pairs are returned.
    return re.compile(
        rf"<\s*{re.escape(tag)}\b[^>]*>"
        rf"(?P<content>.*?)"
        rf"</\s*{re.escape(tag)}\s*>",
        flags=re.IGNORECASE | re.DOTALL,
    )


_TAG_PATTERNS = {tag: _tag_pattern(tag) for tag in _MODULE_TAGS}


def _assistant_text(
    turn: AssistantTurn,
) -> tuple[
    str,
    tuple[TextBlockRange, ...],
    tuple[ThinkingSpan, ...],
    tuple[ModuleSpan, ...],
]:
    pieces: list[str] = []
    ranges: list[TextBlockRange] = []
    thinking: list[ThinkingSpan] = []
    modules: list[ModuleSpan] = []
    offset = 0

    for block_index, block in enumerate(turn.content_blocks):
        text = _project_block(block)
        if text is None:
            continue
        start = offset
        end = start + len(text)
        refs = _source_refs(block.source_refs or turn.source_refs)
        pieces.append(text)
        ranges.append(
            TextBlockRange(
                event_id=turn.event_id,
                block_index=block_index,
                block_type=block.block_type,
                start_char=start,
                end_char=end,
                source_refs=refs,
            )
        )
        if block.block_type in {"thinking", "reasoning"}:
            thinking.append(
                ThinkingSpan(
                    event_id=turn.event_id,
                    block_index=block_index,
                    kind=block.block_type,
                    start_char=start,
                    end_char=end,
                    source_refs=refs,
                )
            )
        # Tags are scanned within a source block, never across an artificial
        # block boundary.
        if block.text is not None:
            for tag, pattern in _TAG_PATTERNS.items():
                for match in pattern.finditer(block.text):
                    modules.append(
                        ModuleSpan(
                            tag=tag,
                            module=_TAG_TO_MODULE[tag],
                            event_id=turn.event_id,
                            block_index=block_index,
                            tag_start_char=start + match.start(),
                            tag_end_char=start + match.end(),
                            content_start_char=start + match.start("content"),
                            content_end_char=start + match.end("content"),
                            source_refs=refs,
                        )
                    )
        offset = end

    modules.sort(
        key=lambda span: (
            span.tag_start_char,
            span.tag_end_char,
            span.tag,
        )
    )
    return "".join(pieces), tuple(ranges), tuple(thinking), tuple(modules)


def _tool_result(result: ToolResult) -> JudgeToolResult:
    return JudgeToolResult(
        result_id=result.result_id,
        call_id=result.call_id,
        event_id=result.event_id,
        name=result.name,
        status=result.status.value,
        is_error=result.is_error,
        output=_content_text(result.content_blocks),
        details=copy.deepcopy(result.details),
        source_refs=_source_refs(result.source_refs),
    )


def _call_block_index(call: ToolCall) -> Optional[int]:
    value = call.metadata.get("content_block_index")
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _tool_call(
    call: ToolCall,
    *,
    results_by_id: dict[str, ToolResult],
    results_by_call: dict[str, list[ToolResult]],
) -> JudgeToolCall:
    linked: list[ToolResult] = []
    seen: set[str] = set()
    for result_id in call.result_ids:
        result = results_by_id.get(result_id)
        if result is not None and result.result_id not in seen:
            linked.append(result)
            seen.add(result.result_id)
    # A valid CanonicalTrace already materializes result_ids.  The fallback is
    # useful for manually constructed traces and remains an ID equality join.
    for result in results_by_call.get(call.call_id, []):
        if result.result_id not in seen:
            linked.append(result)
            seen.add(result.result_id)
    return JudgeToolCall(
        call_id=call.call_id,
        event_id=call.event_id,
        name=call.name,
        normalized_name=call.normalized_name,
        arguments=copy.deepcopy(call.arguments),
        partial_arguments=copy.deepcopy(call.partial_arguments),
        status=call.status.value,
        content_block_index=_call_block_index(call),
        results=tuple(_tool_result(result) for result in linked),
        source_refs=_source_refs(call.source_refs),
    )


def _turn_calls(
    turn: AssistantTurn,
    calls: Sequence[ToolCall],
    claimed_indices: set[int],
) -> list[ToolCall]:
    selected: list[ToolCall] = []

    # Preserve the call ordering recorded by the assistant completion.
    for call_id in turn.tool_call_ids:
        match_index = next(
            (
                index
                for index, call in enumerate(calls)
                if index not in claimed_indices
                and call.call_id == call_id
                and call.turn_id == turn.turn_id
            ),
            None,
        )
        if match_index is None:
            match_index = next(
                (
                    index
                    for index, call in enumerate(calls)
                    if index not in claimed_indices and call.call_id == call_id
                ),
                None,
            )
        if match_index is not None:
            selected.append(calls[match_index])
            claimed_indices.add(match_index)

    # Retain canonical calls whose turn link exists even if a partially
    # captured AssistantTurn omitted the call ID.
    for index, call in enumerate(calls):
        if (
            index not in claimed_indices
            and call.turn_id == turn.turn_id
        ):
            selected.append(call)
            claimed_indices.add(index)
    return selected


def _message_call_id(message: CanonicalMessage) -> Optional[str]:
    metadata = message.metadata
    value = (
        metadata.get("toolCallId")
        or metadata.get("tool_use_id")
        or metadata.get("call_id")
    )
    return str(value) if value is not None else None


def _linked_result_ids(
    message: CanonicalMessage,
    results_by_event: dict[str, list[ToolResult]],
) -> tuple[str, ...]:
    candidates = results_by_event.get(message.event_id, [])
    call_id = _message_call_id(message)
    if call_id is not None:
        candidates = [
            result for result in candidates if result.call_id == call_id
        ]
    elif len(candidates) != 1:
        return ()
    return tuple(dict.fromkeys(result.result_id for result in candidates))


def _message_positions(
    trace: CanonicalTrace,
) -> list[Optional[int]]:
    by_message_id: dict[str, list[int]] = {}
    by_event_id: dict[str, list[int]] = {}
    for index, message in enumerate(trace.messages):
        by_message_id.setdefault(message.message_id, []).append(index)
        if message.role == MessageRole.ASSISTANT:
            by_event_id.setdefault(message.event_id, []).append(index)

    used: set[int] = set()
    positions: list[Optional[int]] = []
    for turn in trace.assistant_turns:
        candidates = by_message_id.get(turn.message_id, [])
        position = next((item for item in candidates if item not in used), None)
        if position is None:
            position = next(
                (
                    item
                    for item in by_event_id.get(turn.event_id, [])
                    if item not in used
                ),
                None,
            )
        if position is not None:
            used.add(position)
        positions.append(position)
    return positions


def _benchmark_input_projection(
    text: str,
) -> Optional[BenchmarkInputProjection]:
    """Recognize the released cumulative prompt template, failing closed."""

    history_matches = list(_BENCHMARK_HISTORY_RE.finditer(text))
    current_matches = list(_BENCHMARK_CURRENT_RE.finditer(text))
    if len(history_matches) != 1 or len(current_matches) != 1:
        return None
    history = history_matches[0]
    current = current_matches[0]
    try:
        prior_count = int(history.group("count"))
        current_step = int(current.group("step"))
    except (TypeError, ValueError):
        return None
    if (
        current_step < 2
        or prior_count != current_step - 1
        or history.end() > current.start()
    ):
        return None

    is_final_step = current.group("final_marker") is not None
    if is_final_step and current_step != 30:
        return None

    end_candidates: list[tuple[int, str, re.Match[str]]] = []
    if is_final_step:
        final_answer_matches = list(
            _BENCHMARK_FINAL_ANSWER_RE.finditer(text, current.end())
        )
        if len(final_answer_matches) != 1:
            return None
        final_answer = final_answer_matches[0]
        end_candidates.append(
            (
                final_answer.start(),
                "final_answer_instruction",
                final_answer,
            )
        )
    else:
        for marker_name, pattern in _BENCHMARK_OBSERVATION_END_PATTERNS:
            match = pattern.search(text, current.end())
            if match is not None:
                end_candidates.append((match.start(), marker_name, match))
    if not end_candidates:
        return None
    _, marker_name, observation_end = min(
        end_candidates,
        key=lambda item: item[0],
    )
    if observation_end.start() < current.end():
        return None

    if marker_name == "admissible_actions":
        format_start = _BENCHMARK_FORMAT_START_RE.search(
            text,
            observation_end.end(),
        )
        interface_end = (
            format_start.start() if format_start is not None else len(text)
        )
        suffix_start = interface_end
    else:
        # GAIA exposes a stable tool/instruction catalog after the dynamic tool
        # result.  Exact paragraph matching decides what can be referenced.
        interface_end = observation_end.start()
        suffix_start = observation_end.start()

    values = (
        0,
        history.start(),
        current.start(),
        current.end(),
        observation_end.start(),
        interface_end,
        suffix_start,
        len(text),
    )
    if any(left > right for left, right in zip(values, values[1:])):
        return None
    return BenchmarkInputProjection(
        declared_step=current_step,
        declared_prior_step_count=prior_count,
        prefix_start_char=0,
        prefix_end_char=history.start(),
        history_start_char=history.start(),
        history_end_char=current.start(),
        step_marker_start_char=current.start(),
        step_marker_end_char=current.end(),
        observation_start_char=current.end(),
        observation_end_char=observation_end.start(),
        interface_start_char=observation_end.start(),
        interface_end_char=interface_end,
        suffix_start_char=suffix_start,
        suffix_end_char=len(text),
        observation_end_marker=marker_name,
    )


def _safe_prefix(
    text: str,
    previous: Sequence[JudgeObservation],
) -> tuple[Optional[str], int]:
    best: Optional[JudgeObservation] = None
    for candidate in previous:
        prefix_length = len(candidate.text)
        if not candidate.text or not text.startswith(candidate.text):
            continue
        suffix = text[prefix_length:]
        boundary_safe = (
            not suffix
            or suffix.startswith(("\n", "\r"))
            or candidate.text.endswith(("\n", "\r"))
        )
        substantial = (
            not suffix or prefix_length >= _CUMULATIVE_PREFIX_MIN_CHARS
        )
        if boundary_safe and substantial and (
            best is None or prefix_length > len(best.text)
        ):
            best = candidate
    if best is None:
        return None, 0
    return best.event_id, len(best.text)


def _observations(
    trace: CanonicalTrace,
) -> dict[int, JudgeObservation]:
    results_by_event: dict[str, list[ToolResult]] = {}
    for result in trace.tool_results:
        results_by_event.setdefault(result.event_id, []).append(result)

    previous_users: list[JudgeObservation] = []
    result: dict[int, JudgeObservation] = {}
    for index, message in enumerate(trace.messages):
        if message.role == MessageRole.ASSISTANT:
            continue
        text = _content_text(message.content_blocks)
        refs = _source_refs(message.source_refs)
        repeated_event: Optional[str] = None
        repeated_chars = 0
        if message.role == MessageRole.USER:
            repeated_event, repeated_chars = _safe_prefix(text, previous_users)
        benchmark_input = (
            _benchmark_input_projection(text)
            if message.role == MessageRole.USER
            and any(ref.source_kind == "agent_error_bench" for ref in refs)
            else None
        )
        observation = JudgeObservation(
            event_id=message.event_id,
            message_id=message.message_id,
            role=message.role.value,
            text=text,
            repeated_prefix_event_id=repeated_event,
            repeated_prefix_chars=repeated_chars,
            linked_tool_result_ids=_linked_result_ids(message, results_by_event),
            source_refs=refs,
            benchmark_input=benchmark_input,
        )
        result[index] = observation
        if message.role == MessageRole.USER:
            previous_users.append(observation)
    return result


def _context_between(
    trace: CanonicalTrace,
    observations: dict[int, JudgeObservation],
    start: int,
    end: int,
) -> tuple[JudgeObservation, ...]:
    return tuple(
        observations[index]
        for index in range(max(start, 0), min(end, len(trace.messages)))
        if index in observations
    )


def build_judge_view(trace: CanonicalTrace) -> JudgeView:
    """Build a diagnostic view without mutating or retaining mutable trace data."""

    if not isinstance(trace, CanonicalTrace):
        raise TypeError("build_judge_view requires a CanonicalTrace")

    observations = _observations(trace)
    positions = _message_positions(trace)
    results_by_id = {
        result.result_id: result for result in trace.tool_results
    }
    results_by_call: dict[str, list[ToolResult]] = {}
    for result in trace.tool_results:
        if result.call_id is not None:
            results_by_call.setdefault(result.call_id, []).append(result)

    steps: list[JudgeStep] = []
    claimed_call_indices: set[int] = set()
    previous_position = -1
    for turn_index, turn in enumerate(trace.assistant_turns):
        position = positions[turn_index]
        if position is None:
            current_input: tuple[JudgeObservation, ...] = ()
            adjacent_feedback: tuple[JudgeObservation, ...] = ()
        else:
            current_input = _context_between(
                trace,
                observations,
                previous_position + 1,
                position,
            )
            next_position = next(
                (
                    candidate
                    for candidate in positions[turn_index + 1 :]
                    if candidate is not None and candidate > position
                ),
                len(trace.messages),
            )
            adjacent_feedback = _context_between(
                trace,
                observations,
                position + 1,
                next_position,
            )
            if position > previous_position:
                previous_position = position

        raw_output, text_blocks, thinking, modules = _assistant_text(turn)
        calls = _turn_calls(
            turn,
            trace.tool_calls,
            claimed_call_indices,
        )
        steps.append(
            JudgeStep(
                step=turn_index + 1,
                turn_id=turn.turn_id,
                assistant_event_id=turn.event_id,
                assistant_message_id=turn.message_id,
                current_input=current_input,
                assistant_raw_output=raw_output,
                text_blocks=text_blocks,
                thinking_spans=thinking,
                module_spans=modules,
                tool_calls=tuple(
                    _tool_call(
                        call,
                        results_by_id=results_by_id,
                        results_by_call=results_by_call,
                    )
                    for call in calls
                ),
                adjacent_feedback=adjacent_feedback,
                stop_reason=turn.stop_reason,
                error_message=turn.error_message,
                source_refs=_source_refs(turn.source_refs),
            )
        )

    task = (
        JudgeTask(
            task_id=trace.task.task_id,
            title=trace.task.title,
            description=trace.task.description,
            user_request=trace.task.user_request,
            source_refs=_source_refs(trace.task.source_refs),
        )
        if trace.task is not None
        else None
    )
    return JudgeView(
        version=JUDGE_VIEW_VERSION,
        trace_id=trace.trace_id,
        task=task,
        execution_facts=_execution_facts(trace),
        steps=tuple(steps),
    )


__all__ = [
    "BenchmarkInputProjection",
    "JUDGE_VIEW_VERSION",
    "JudgeExecutionFacts",
    "JudgeObservation",
    "JudgeStep",
    "JudgeTask",
    "JudgeToolCall",
    "JudgeToolResult",
    "JudgeView",
    "ModuleSpan",
    "SourceReference",
    "TextBlockRange",
    "ThinkingSpan",
    "build_judge_view",
]
