"""Luna GAIA v2: recovery-aware causal-state ledger.

This protocol keeps GAIA v1's ownership-safe nested evidence geometry while
replacing v3's stateless first-mature scan.  Candidate errors have causal
intervals that can be closed by demonstrated recovery; strategy repetitions
are normalized by subgoal/source/modality; and provenance-backed adjacent tool
failures may be owned by System at the action step where they occur.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    AgentJudgeValidationError,
    _assert_safe_path,
    _execution_fact_lines,
    _validate_agent_judge_predictions_with_owner_sources,
)
from ._nested_sources import (
    AGENT_JUDGE_LUNA_GAIA_V1_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_GAIA_V1_MODEL,
    AGENT_JUDGE_LUNA_GAIA_V1_REASONING_EFFORT,
    AGENT_JUDGE_LUNA_GAIA_V1_VERSION,
    _luna_gaia_v1_owner_source_resolver,
    build_agent_judge_luna_gaia_v1_task,
)
from .judge_view import JudgeView
from .taxonomy import AgentModule, ErrorType


AGENT_JUDGE_LUNA_GAIA_V2_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v2"
)
AGENT_JUDGE_LUNA_GAIA_V2_MODEL = AGENT_JUDGE_LUNA_GAIA_V1_MODEL
AGENT_JUDGE_LUNA_GAIA_V2_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V1_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V2_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V1_AUDIT_SCHEMA_VERSION
)


def _adjacent_external_feedback_sources(
    view: JudgeView,
    predicted_step: int,
) -> tuple[str, ...]:
    """Expose only the incremental result portion of adjacent feedback.

    AgentErrorBench wraps tool feedback in a cumulative user prompt.  Its
    gold-free ``BenchmarkInputProjection`` gives the exact current-observation
    range, so System evidence need not gain access to the repeated task,
    history, interface, or available-tool text.  Native tool-role messages are
    already result-only and use their incremental text.
    """

    step = view.steps[predicted_step - 1]
    sources: list[str] = []
    for feedback in step.adjacent_feedback:
        projection = feedback.benchmark_input
        if projection is not None:
            source = feedback.text[
                projection.observation_start_char :
                projection.observation_end_char
            ]
        elif feedback.role == "tool":
            source = feedback.incremental_text
        else:
            continue
        if source.strip():
            sources.append(source)
    return tuple(dict.fromkeys(sources))


def _luna_gaia_v2_owner_source_resolver(
    view: JudgeView,
    predicted_step: int,
    module: AgentModule,
    error_type: ErrorType,
) -> tuple[str, ...]:
    """Use v1 owner isolation plus non-final adjacent System evidence."""

    if module != AgentModule.SYSTEM:
        return _luna_gaia_v1_owner_source_resolver(
            view,
            predicted_step,
            module,
            error_type,
        )

    sources = list(_adjacent_external_feedback_sources(view, predicted_step))
    if predicted_step == len(view.steps):
        sources.extend(_execution_fact_lines(view.execution_facts))
    return tuple(dict.fromkeys(source for source in sources if source.strip()))


_LEDGER_DECISION_RULES = """\
THE ONLY DECISION ORDER

TASK/OBSERVATION LEDGER -> CANDIDATE CAUSAL INTERVALS -> RECOVERY CLOSURE ->
DOMINANT UNRECOVERED INTERVAL -> FREEZE STEP -> SAME-STEP OWNER -> TYPE ->
LITERAL EVIDENCE

Do not choose the globally strongest-looking symptom.  Do not mechanically
choose the earliest imperfection.  Reconstruct what evidence state each defect
changed, whether that state remained on the failure path, and whether a later
successful strategy replacement retired it.

1. RECOVERY-AWARE CAUSAL-STATE LEDGER

Before selecting a step, scan the entire JudgeView chronologically and keep
these compact internal ledgers:

- TASK PREDICATES: every required entity, fact, calculation, source,
  constraint, and output condition; mark each unsatisfied, observed, inferred,
  contradicted, or complete.
- CLAIM SUPPORT: for every new Memory or Reflection claim, identify the exact
  prior observation that supports it.  Mark omitted salient results, invented
  entity/fact links, false success, false no-progress, wrong cause, and a
  completed subgoal mistaken for the completed task.
- CAPABILITY: for each plan, state the required evidence corpus and modality
  (for example database metadata, dynamic video narration/frames, PDF text, or
  arithmetic) and whether the selected tool can actually expose it.  A tool's
  mere availability does not make an informationally incapable plan possible.
- STRATEGY EPOCH: normalize each acquisition attempt as
  (unresolved subgoal, source/corpus, evidence modality, discriminating query
  or target).  Wording changes alone do not make a new strategy.  A genuinely
  new source, modality, target, or discriminating constraint is exploratory.
- EXTERNAL EVENTS: inspect the exact adjacent feedback of every action for a
  provenance-backed service/model/tool execution failure.

Audit Memory and Reflection claims before downstream Planning and Action.
Compare claims to literal observations, not to what the trajectory later
assumes.  Check plan/tool capability before judging repeated-search aesthetics.

2. OPEN, PROPAGATE, AND CLOSE CAUSAL INTERVALS

Open a candidate interval only for a concrete material defect demonstrable
from information available at that step.  Record its introduction step, the
task predicate or state it corrupts, and downstream blocks that consume it.
A merely failed reasonable probe, vague suboptimality, or hindsight is not a
candidate.

Keep an interval OPEN while the same false state, incapable strategy, ignored
constraint, or external boundary continues to cause waste or the answer.
A recovered candidate is CLOSED only when a later action successfully replaces
its route, obtains a viable prerequisite, and later reasoning no longer
depends on the faulty state.  A syntactic parameter error followed by a
successful different tool can be closed.  Merely acknowledging an error or
rephrasing the same query cannot close it.

For repetition, the first probe is normally reasonable.  Open the repetition
interval at the first attempt made after direct feedback has shown that the
same normalized epoch is uninformative, redundant, constraint-violating, or
incapable.  Do not wait for a later literal copy.  Conversely, do not mature a
single alternate-source probe merely because its probability is low.

3. SELECT THE DOMINANT UNRECOVERED FAILURE INTERVAL

After the full scan, identify the interval that actually explains the wrong
answer, non-answer, wasted terminal sequence, or blocked interaction.  Select
the introduction step of that interval.

- A persistent earlier interval defeats a more obvious later symptom.
- A fully closed/recovered interval cannot defeat the later interval that
  actually remains on the failure path.
- A terminal answer that gives up while viable task predicates and materially
  different strategies remain is itself a Planning candidate.  It can defeat
  an earlier exploratory retry that did not exhaust the episode.
- A final unsupported answer does not defeat an earlier false Memory,
  Reflection, or persistent incapable plan that it faithfully consumes.

Freeze predicted_step only after this recovery/closure comparison.  Taxonomy
fit and quote convenience must never move it.

4. SYSTEM COMPETES AT THE ACTION STEP

System may own at any step when literal adjacent feedback proves that a
well-formed request failed because of external model ID/configuration, service,
tool execution, environment, or platform state.  Use the assistant action step
whose adjacent feedback contains that failure.  It need not be the final step.

System does not automatically win.  Compare its interval with earlier agent
defects and later recovery.  Wrong-typed or malformed arguments documented by
the interface remain Action; empty search results, ordinary inaccessible URLs,
and 403 text returned normally by an extraction tool are evidence about the
chosen plan/source, not automatically System.  A false completion or causal
claim written before a later tool failure can still own.

At the final step, provenance-backed execution_facts remain eligible for step
limits, model limits, or environment termination.

5. SAME-STEP OWNER AFTER STEP FREEZE

At the frozen step follow information flow:

- Memory owns a new unsupported historical/world assertion, salient omission,
  oversimplification, or retrieval failure consumed downstream.
- Reflection owns a new false reading of direct feedback, result, progress,
  outcome, or cause consumed downstream.
- Planning owns a new defective strategy, query, target, constraint decision,
  prerequisite, capability mismatch, repetition epoch, or premature give-up
  when upstream state is accurate.
- Action owns a concrete deviation from an adequate current plan, unparseable
  syntax, unavailable operation, or mechanically missing/wrong argument.
- System owns only the external conditions admitted above.

If false Memory is accepted by Reflection/Plan, Memory owns.  If Memory is
accurate and Reflection misreads it, Reflection owns.  If both are accurate
and Plan makes the bad choice, Planning owns.  A faithful action never steals
ownership from its plan.  Final answers obey the same causal handoff.

6. TYPE AND EVIDENCE AFTER STEP/OWNER FREEZE

Choose one legal type within the frozen owner.  Important boundaries:

- inefficient_plan is demonstrated waste, repetition, premature abandonment,
  or a poor acquisition strategy, not a generic label for failure;
- impossible_action includes a plan whose required corpus/modality cannot be
  observed by the chosen tool or available action space;
- parameter_error is a mechanically missing, malformed, wrong-typed, or
  misfilled argument, not a poor query strategy;
- misalignment is a concrete contradiction of an otherwise adequate current
  plan;
- tool_execution_error is a literal external execution failure, not agent
  misuse or ordinary negative content.

In rejected_adjacent_owner, name the strongest competing interval and state
whether it is recovered, exploratory, faithful propagation, external rather
than agent-owned, or a later symptom.

"""


def build_agent_judge_luna_gaia_v2_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build the frozen recovery-aware single-case semantic task."""

    task = build_agent_judge_luna_gaia_v1_task(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    task = task.replace(
        AGENT_JUDGE_LUNA_GAIA_V1_VERSION,
        AGENT_JUDGE_LUNA_GAIA_V2_VERSION,
    )
    task = task.replace(
        "agentdebug/diagnostics/_nested_sources.py",
        "agentdebug/diagnostics/_feedback_sources.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._nested_sources import "
        "validate_and_write_agent_judge_luna_gaia_v1_audit as run",
        "from agentdebug.diagnostics._feedback_sources import "
        "validate_and_write_agent_judge_luna_gaia_v2_audit as run",
    )

    decision_start = task.find("THE ONLY DECISION ORDER\n")
    taxonomy_start = task.find("AGENT ERROR TAXONOMY\n")
    if decision_start < 0 or taxonomy_start <= decision_start:
        raise RuntimeError("Luna GAIA v1 decision section changed unexpectedly")
    task = task[:decision_start] + _LEDGER_DECISION_RULES + task[taxonomy_start:]

    old_system_rule = (
        "System must quote one accepted execution_facts\n"
        "line at the final step."
    )
    new_system_rule = (
        "System must quote either literal current-observation text from the\n"
        "selected step's adjacent feedback that contains the external failure,\n"
        "or one accepted execution_facts line at the final step."
    )
    if old_system_rule not in task:
        raise RuntimeError("Luna GAIA v1 System evidence rule changed unexpectedly")
    task = task.replace(old_system_rule, new_system_rule)
    task = task.replace(
        "re-check that no later symptom has\nreplaced the first mature causal "
        "error and that the evidence is literal owner\ntext.",
        "re-check causal-interval recovery and closure, then verify that the\n"
        "evidence is literal selected-owner text.",
    )
    return task


def validate_agent_judge_luna_gaia_v2_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    audit = _validate_agent_judge_predictions_with_owner_sources(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
        owner_source_resolver=_luna_gaia_v2_owner_source_resolver,
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V2_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V2_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V2_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V2_REASONING_EFFORT,
        "evidence_geometry": "disjoint_or_properly_nested_owner_fragments",
        "system_evidence": "adjacent_projected_observation_or_final_execution_facts",
    }


def validate_and_write_agent_judge_luna_gaia_v2_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v2_predictions(
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
    "AGENT_JUDGE_LUNA_GAIA_V2_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V2_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V2_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V2_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "build_agent_judge_luna_gaia_v2_task",
    "validate_agent_judge_luna_gaia_v2_predictions",
    "validate_and_write_agent_judge_luna_gaia_v2_audit",
]
