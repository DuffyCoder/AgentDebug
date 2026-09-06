"""Canonical, gold-isolated Codex Agent Judge v2.4 protocol.

V2.4 is a standalone semantic specification.  It preserves the strict
ten-field prediction contract and gold-free mechanical validation shared by
the earlier protocols, while defining its own census, critical-root, owner,
and evidence-source rules in one internally consistent task.
"""

from __future__ import annotations

import json
import os
import shlex
from pathlib import Path
from typing import Any

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    GOLD_ISOLATION_READ_DENYLIST,
    AgentJudgeValidationError,
    _assert_safe_path,
    _execution_fact_lines,
    _file_sha256,
    _string_leaves,
    _validate_agent_judge_predictions_with_owner_sources,
)
from .judge_view import JudgeView
from .taxonomy import AgentModule, ErrorType, taxonomy_prompt


AGENT_JUDGE_V2_4_VERSION = "agentdebug.codex-agent-judge.v2.4"
AGENT_JUDGE_V2_4_MODEL = "gpt-5.6-terra"
AGENT_JUDGE_V2_4_REASONING_EFFORT = "medium"
AGENT_JUDGE_V2_4_AUDIT_SCHEMA_VERSION = (
    "agentdebug.codex-agent-judge-audit.v1"
)

GOLD_ISOLATION_V2_4_READ_ALLOWLIST = (
    "the exact prediction_manifest_path named in the task",
    "the exact cohort_manifest_path named in the task",
    "agentdebug/diagnostics/_owner_sources.py",
    "agentdebug/diagnostics/taxonomy.py",
)


def _module_residual_sources(
    view: JudgeView,
    predicted_step: int,
) -> tuple[str, ...]:
    """Return separate raw-output gaps outside all recognized module spans.

    Invalid span geometry fails closed.  Overlapping and adjacent spans are
    merged so no returned source can cross recognized module-owned text.
    """

    step = view.steps[predicted_step - 1]
    raw = step.assistant_raw_output
    if not raw or not step.module_spans:
        return ()

    intervals: list[tuple[int, int]] = []
    for span in step.module_spans:
        start = span.tag_start_char
        end = span.tag_end_char
        if start < 0 or end <= start or end > len(raw):
            return ()
        intervals.append((start, end))

    ordered = sorted(intervals)
    # Nested or otherwise overlapping recognized tags make ownership
    # ambiguous: an outer owner's source would contain the inner owner's text.
    # Fail closed rather than leak cross-owner evidence.  Adjacent tags are
    # unambiguous and remain separate boundaries.
    if any(
        start < previous_end
        for (_previous_start, previous_end), (start, _end)
        in zip(ordered, ordered[1:])
    ):
        return ()

    residual_ranges: list[tuple[int, int]] = []
    cursor = 0
    for start, end in ordered:
        if cursor < start:
            residual_ranges.append((cursor, start))
        cursor = end
    if cursor < len(raw):
        residual_ranges.append((cursor, len(raw)))

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

    # Source text blocks are concatenated in assistant_raw_output without a
    # delimiter.  Split residuals at those otherwise invisible boundaries so
    # a quote cannot be assembled across two distinct source blocks.
    residuals: list[str] = []
    for residual_start, residual_end in residual_ranges:
        for block_start, block_end in block_ranges:
            start = max(residual_start, block_start)
            end = min(residual_end, block_end)
            if start < end and raw[start:end].strip():
                residuals.append(raw[start:end])
    return tuple(residuals)


def _v2_4_owner_source_resolver(
    view: JudgeView,
    predicted_step: int,
    module: AgentModule,
    error_type: ErrorType,
) -> tuple[str, ...]:
    """Resolve v2.4 evidence sources without changing older protocols.

    A tag-free assistant output is the common lossless source for every agent
    owner, even when an Action tool call also exists.  With recognized spans,
    normal owner spans remain isolated; Planning additionally receives each
    residual segment, while Action receives residuals only for its two
    malformed-emission classifications.
    """

    if module == AgentModule.SYSTEM:
        if predicted_step != len(view.steps):
            return ()
        return _execution_fact_lines(view.execution_facts)

    step = view.steps[predicted_step - 1]
    raw = step.assistant_raw_output
    sources: list[str] = []

    ordered_spans = sorted(
        step.module_spans,
        key=lambda span: (span.tag_start_char, span.tag_end_char),
    )
    span_geometry_valid = all(
        span.tag_start_char >= 0
        and span.tag_end_char > span.tag_start_char
        and span.tag_end_char <= len(raw)
        for span in ordered_spans
    ) and all(
        current.tag_start_char >= previous.tag_end_char
        for previous, current in zip(ordered_spans, ordered_spans[1:])
    )

    for span in ordered_spans if span_geometry_valid else ():
        start = span.tag_start_char
        end = span.tag_end_char
        if (
            span.module == module.value
            and start >= 0
            and end > start
            and end <= len(raw)
        ):
            sources.append(raw[start:end])

    if not step.module_spans and raw.strip():
        # This is unconditional with respect to tool calls.  In particular,
        # Action must not lose the tag-free raw source merely because concrete
        # call leaves are also available.
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
            and error_type
            in {ErrorType.FORMAT_ERROR, ErrorType.INVALID_ACTION}
        )
    ):
        sources.extend(_module_residual_sources(view, predicted_step))

    return tuple(dict.fromkeys(source for source in sources if source.strip()))


def _validator_command(
    prediction_path: Path,
    cohort_path: Path,
    output_path: Path,
    audit_path: Path,
) -> str:
    """Build the exact local gold-free v2.4 validation command."""

    prediction = prediction_path.expanduser().resolve()
    cohort = cohort_path.expanduser().resolve()
    output = output_path.expanduser().resolve()
    audit = audit_path.expanduser().resolve()
    code = (
        "import json; "
        "from agentdebug.diagnostics._owner_sources import "
        "validate_and_write_agent_judge_v2_4_audit as run; "
        "print(json.dumps(run("
        f"{str(prediction)!r}, {str(cohort)!r}, "
        f"{str(output)!r}, {str(audit)!r}"
        "), ensure_ascii=False, indent=2))"
    )
    return "PYTHONPATH=. python3 -c " + shlex.quote(code)


def build_agent_judge_v2_4_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build the complete standalone v2.4 task for one fresh subagent."""

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    output_path = Path(predictions_path).expanduser().resolve()
    audit_path = output_path.parent / "prediction-audit.json"
    repository_root = Path(__file__).resolve().parents[2]
    _assert_safe_path(prediction_path, role="prediction manifest")
    _assert_safe_path(cohort_path, role="cohort manifest")
    _assert_safe_path(output_path, role="prediction output", is_output=True)
    _assert_safe_path(audit_path, role="prediction audit output", is_output=True)

    schema = {
        "trajectory_id": "exact manifest trajectory ID",
        "trajectory_sha256": "exact manifest trajectory SHA-256",
        "status": "success",
        "predicted_step": "positive integer",
        "predicted_module": "taxonomy module",
        "predicted_error_type": "valid type for that module",
        "evidence_quote": "exact non-empty owner substring",
        "root_cause": "concise root-cause explanation",
        "causal_summary": "counterfactual, cascade, and recovery conclusion",
        "rejected_adjacent_owner": "strongest alternative and rejection reason",
    }
    allowlist = "\n".join(
        f"- {item}" for item in GOLD_ISOLATION_V2_4_READ_ALLOWLIST
    )
    allowlist += (
        f"\n- {output_path} only after you write this run's complete predictions"
        f"\n- {audit_path} only after the local validator creates it"
    )
    denylist = "\n".join(
        f"- {item}" for item in GOLD_ISOLATION_READ_DENYLIST
    )
    validator_command = _validator_command(
        prediction_path,
        cohort_path,
        output_path,
        audit_path,
    )

    return f"""\
Run the frozen Codex Agent Judge protocol {AGENT_JUDGE_V2_4_VERSION}.

IMMUTABLE EXECUTION CONFIGURATION
- model: {AGENT_JUDGE_V2_4_MODEL}
- reasoning_effort: {AGENT_JUDGE_V2_4_REASONING_EFFORT}
- mode: independent open-ended Agent Judge
- external LLM/API/network calls: forbidden
- scoring or gold-label access: forbidden

INPUT/OUTPUT BOUNDARY
- prediction manifest: {prediction_path}
- prediction manifest file sha256: {_file_sha256(prediction_path)}
- cohort manifest: {cohort_path}
- cohort manifest file sha256: {_file_sha256(cohort_path)}
- write predictions only to: {output_path}
- local validation audit: {audit_path}

Read cases only from the prediction manifest and process each exactly once in
cohort order.  Do not inspect directories for context.  Each persisted
JudgeView is the complete authoritative semantic input.

GOLD-ISOLATION READ ALLOWLIST
{allowlist}

GOLD-ISOLATION READ DENYLIST
{denylist}

CANONICAL DECISION ORDER
PHASE 1 LOCAL CENSUS → PHASE 2 GLOBAL CRITICAL ROOT →
PHASE 3 TAXONOMY AND EVIDENCE

Apply these phases once, in this order, for every case.  Keep all candidate
cards and comparisons internal; predictions.json contains only the final
ten-field records.

PHASE 1 — COMPLETE LOCAL CENSUS

Reconstruct the objective, explicit constraints, action interface,
chronological world and information state, assistant outputs, concrete calls,
direct results, later feedback, and terminal execution facts.  When judging a
local output, use only task information and observations already available
when that output was written.  Later evidence may establish propagation or
recovery, but it cannot turn an initially reasonable probe into a hindsight
error.

Audit every Cartesian pair
(step, module) for every step and every module in
{{memory, reflection, planning, action, system}}.  The candidate unit is
exactly one (step, module), never a step with its owner deferred.  Do not stop
after finding several plausible candidates: the census has no candidate cap.
Do not lock a step before the global comparison, and do not use module order
as a preference.

For every pair, make an internal candidate card containing at least:
- local proposition/decision: the literal claim, assessment, strategy,
  invocation, final emission, or external boundary under review;
- module-local defect/evidence then: what is wrong in that module's own source
  and the exact evidence already available then, or why no defect is shown;
- novelty vs upstream: whether this source newly introduces the defect or
  only carries an upstream defect forward;
- correction effect: what changes if only this source is corrected;
- downstream dependence: which later decisions or failures rely on it;
- recovery: none, partial, or complete, with the concrete restored and
  unrestored state identified.

Retain every directly evidenced, locally mature NEW-DEFECT candidate for
Phase 2.  Unsupported exhaustiveness and a concrete operation that cannot
produce task-required information may be locally mature without waiting for
later failure.  Conversely, lack of progress on a reasonable first probe is
not itself a defect.  Feedback can make a later recommitment mature when
continuing that branch has become unreasonable.

Populate all three diagnostic lanes without choosing a winner yet:
1. terminal boundary — every provenance-backed external termination or
   failure and whether it independently prevents completion;
2. earliest important locally demonstrated defect — the first consequential
   local defect in each causal chain, without assuming it remains critical;
3. mature branch commitment — each first or renewed commitment to a branch
   after then-available evidence makes that commitment defective.

PHASE 2 — GLOBAL CRITICAL-ROOT COMPARISON

Compare all retained (step, module) candidates from all three lanes together.
For each one, test whether a single-point correction would fundamentally
redirect the failed trajectory, not merely improve wording or one local turn.
Compare the redirected path, the cascade explained by the candidate,
downstream dependence, recovery, and any independent later cause, including a
later cause sufficient by itself.  A candidate is critical only when its own
correction plausibly changes
the root path and its unrepaired effect remains relevant to the failure.

Recovery is a causal finding, not a mechanical exclusion.  Complete recovery
normally removes an earlier candidate when the required state or evidence was
actually restored and an independent cause produced the later failure.  Keep
an earlier candidate only if concrete unrepaired consequences still control
the trajectory.  Partial recovery does not erase the remaining causal effect.

Select the single globally strongest critical root.  Use earlier chronology
only to break a tie when criticality is genuinely comparable.  Do not reward
a candidate merely for being early, terminal, concrete, locally true, easy to
quote, or the first visible failure.  A locally valid later plan does not
automatically outrank a more critical earlier or later candidate.  A
reasonable exploratory probe does not outrank a mature post-feedback
recommitment merely because it occurred first.

System candidates participate in this same global comparison.  They are
admissible only at the final step, only from provenance-backed execution_facts,
and only when the external boundary is independently causal.  Episode failure
alone is not system evidence.

PHASE 3 — NEW-DEFECT OWNERSHIP, TAXONOMY, AND EVIDENCE

The owner is the module in the selected (step, module) candidate whose own
defect-bearing source newly introduces the demonstrated defect.  A downstream
source that faithfully repeats or executes it does not take ownership.  Do
not substitute Planning merely because an Action ownership test is
unpersuasive; either module must establish its own NEW-DEFECT from its own
source and compete globally.

Apply this single NEW-DEFECT rule uniformly:
- memory owns when its text newly drops or fails to retrieve historical state,
  fabricates historical state, or makes an unsupported exhaustive historical
  assertion;
- reflection owns when its text newly misreads a direct result, outcome,
  progress state, or cause;
- planning owns when its strategy, constraint handling, prerequisite, target,
  or deliberative derivation is itself defective;
- action owns when the concrete invocation or final emission independently
  introduces a deviation, malformed syntax, unavailable operation, wrong
  concrete parameter, or an operation informationally incapable of producing
  the required evidence;
- system owns only the independently causal final provenance fact described
  in Phase 2.

A defective plan followed faithfully by its action is Planning.  An adequate
plan followed by a deviating concrete emission is Action.  If there is no
same-step plan, Action is neither automatically accepted nor automatically
rejected: decide whether the concrete emission itself first introduces a
demonstrable defect.  Treat a final answer identically.  It is Action only
when that final emission newly deviates, contradicts, malforms, or adds an
unsupported conclusion; if it faithfully emits an already defective
derivation, ownership stays with that derivation's source.

Step 1 is not categorically barred from Memory or Reflection.  Admit either
only when the actual task, current input, or other prior-history/direct-result
source available before that output supports its module semantics.  The mere
absence of an earlier assistant turn proves neither admission nor rejection.

REPRESENTATION IS NOT OWNERSHIP

Module spans, partial or tag-free representation, thinking_spans, and the
presence or absence of a tool call determine only which literal sources are
eligible for evidence validation.  They never decide the semantic owner.
In particular, a thinking span is not automatically Planning, a tool call is
not automatically Action, and access to a Planning residual is not evidence
that Planning is the critical root.  Apply the same NEW-DEFECT and global
criticality tests regardless of representation.

After ownership is established, select exactly one legal taxonomy type within
that owner.  A final emission still needs a legal Action taxonomy pair.  If a
candidate has no legal pair for its demonstrated defect, do not force it into
Action or use a defect-free adjacent Planning source to fill the contract;
continue the global comparison among genuinely defect-bearing candidates.
Misalignment specifically requires a concrete contradiction of a current
plan.  When there is no current plan, do not label an Action as misalignment,
although its concrete emission may independently satisfy another Action type.

Distinguish parameter_error from inefficient_plan by the source of the new
defect.  A bad strategy, target, or repeated query first selected by the plan
is Planning/inefficient_plan when it is unnecessarily wasteful.  A sufficient
plan followed by a mechanically missing, malformed, wrong-typed, or misfilled
concrete argument is Action/parameter_error.  Do not relabel a strategy choice
as a parameter error merely because it appears inside call arguments.

Taxonomy labels never determine the step or owner.  Planning
evidence must quote the actual defective commitment or derivation, not an
arbitrary legal or generic substring from a plan.  In
rejected_adjacent_owner, identify the strongest competing local or causal
owner and state the concrete NEW-DEFECT or global-criticality test it loses.

V2.4 EVIDENCE SOURCE AND COPY RULES

evidence_quote must be a non-empty, exact, contiguous, case-sensitive
substring from one source allowed below for the selected step and owner:
- With no recognized module spans at the step, every non-system owner may use
  the complete assistant_raw_output.  Action may additionally use that step's
  concrete tool-call name and string argument leaves.  The shared raw source
  makes validation symmetric; semantic ownership still requires the selected
  module's demonstrated NEW-DEFECT.
- With one or more recognized module spans, each non-system owner normally may
  use only its own complete recognized span.  Action may additionally use its
  concrete tool-call name and string argument leaves.
- In a partially tagged output, Planning may additionally use one whole or
  partial contiguous residual segment outside all recognized spans, but only
  when the quoted residual is deliberative derivation or answer construction
  and itself contains the selected Planning defect.
- In a partially tagged output, Action may use one residual segment only for
  action/format_error or action/invalid_action and only when it is the
  malformed concrete emission.  Other Action types cannot use residual text.
- System must select the final step and quote one exact line from the
  provenance-backed execution_facts source accepted by the validator.

Overlapping or nested recognized module spans have ambiguous owner geometry
and cannot supply tagged-span or residual evidence.  Residual evidence also
cannot cross a source text-block boundary that was invisibly concatenated in
assistant_raw_output.  Independently recorded Action tool-call leaves remain
available under the rules above.

Never cross a recognized span boundary or combine residual segments.  Never
copy from current_input, task text, adjacent_feedback, an observation, a tool
result, another step, or another owner's recognized span.  Never paraphrase,
normalize, translate, repair, or change case or punctuation.  JSON escaping
is transport only; after decoding, the quote must remain the literal source
substring.

AGENT ERROR TAXONOMY
{taxonomy_prompt()}

STRICT TEN-FIELD PREDICTION CONTRACT
Write one JSON array with no envelope, Markdown, commentary, or trailing
content.  It must contain exactly one record per cohort case in exact cohort
and manifest order.  Every record must contain exactly these ten fields:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Every text field must be non-empty.  status must be exactly "success".
predicted_step must be a non-boolean positive integer within that JudgeView.
Do not emit confidence, score, probability, rank, vote, audit internals, source
IDs, aliases, nulls, or any additional field.  Do not copy or consult an older
prediction.  Before writing each record, verify ID, SHA, order, step range,
taxonomy legality, literal evidence ownership, and exact fields.

MANDATORY LOCAL VALIDATION LOOP — DO NOT STOP AFTER WRITING

First write the complete predictions array for every cohort case to the fixed
output path.  Then actually run these exact local shell commands:

cd {shlex.quote(str(repository_root))}
{validator_command}

The task is complete only when the command exits zero and atomically writes
the audit to {audit_path}.  If it fails, inspect only the validator error, your
own current {output_path}, and the allowlisted manifests or v2.4
protocol/taxonomy source.  Correct the complete output and rerun the same
command until it passes.  Do not inspect other predictions, scores, gold,
metrics, case studies, evaluator annotations, directory listings, Git
history, or external resources.  Do not call an external API or network
service during generation, correction, or validation.
"""


def validate_agent_judge_v2_4_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    """Validate v2.4 sources and bind audit metadata to this protocol."""

    audit = _validate_agent_judge_predictions_with_owner_sources(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
        owner_source_resolver=_v2_4_owner_source_resolver,
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_V2_4_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_V2_4_VERSION,
        "model": AGENT_JUDGE_V2_4_MODEL,
        "reasoning_effort": AGENT_JUDGE_V2_4_REASONING_EFFORT,
    }


def validate_and_write_agent_judge_v2_4_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    """Validate first, then atomically persist the v2.4 audit."""

    audit = validate_agent_judge_v2_4_predictions(
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
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AGENT_JUDGE_V2_4_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_V2_4_MODEL",
    "AGENT_JUDGE_V2_4_REASONING_EFFORT",
    "AGENT_JUDGE_V2_4_VERSION",
    "AgentJudgeValidationError",
    "GOLD_ISOLATION_V2_4_READ_ALLOWLIST",
    "build_agent_judge_v2_4_task",
    "validate_and_write_agent_judge_v2_4_audit",
    "validate_agent_judge_v2_4_predictions",
]
