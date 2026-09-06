"""Luna GAIA v3: lane-ordered chronology with a frozen step checkpoint."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    AgentJudgeValidationError,
    _assert_safe_path,
)
from ._evidence_policy import (
    AGENT_JUDGE_LUNA_GAIA_V2_1_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_GAIA_V2_1_MODEL,
    AGENT_JUDGE_LUNA_GAIA_V2_1_REASONING_EFFORT,
    AGENT_JUDGE_LUNA_GAIA_V2_1_VERSION,
    build_agent_judge_luna_gaia_v2_1_task,
    validate_agent_judge_luna_gaia_v2_1_predictions,
)


AGENT_JUDGE_LUNA_GAIA_V3_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v3"
)
AGENT_JUDGE_LUNA_GAIA_V3_MODEL = AGENT_JUDGE_LUNA_GAIA_V2_1_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V2_1_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V2_1_AUDIT_SCHEMA_VERSION
)
STEP_FREEZE_FILENAME = "step-freeze.json"
STEP_FREEZE_FIELDS = ("trajectory_id", "predicted_step")


_LANE_ORDERED_DECISION_RULES = """\
THE ONLY DECISION ORDER

LANE-ORDERED CHRONOLOGICAL SCAN -> WRITE IMMUTABLE STEP CHECKPOINT ->
SAME-STEP OWNER -> TAXONOMY TYPE -> LITERAL EVIDENCE -> FINAL PREDICTION

Select the first concrete material breakpoint in chronological order.  Do not
choose a whole-episode "dominant unrecovered interval," the most persistent
problem, or the latest obvious symptom.  Recovery is only a narrow veto listed
below, not a general reason to erase an earlier error.

1. BUILD THE TASK CHECKLIST

List internally every required entity, fact, calculation, source constraint,
prerequisite, evidence modality, and output condition.  At each step mark what
literal observations establish and which checklist items remain open.  Do not
use a recalled domain fact to invent an early error unless the task, interface,
or an observation directly contradicts it.

2. SCAN STEP 1, STEP 2, ... IN THREE LANES

Finish all three lanes at one step before moving to the next step.  The first
admissible candidate freezes the step.

LANE A — MEMORY AND REFLECTION FACT FIDELITY

Compare every new Memory and Reflection claim with literal prior observations
and the task checklist.  Admit a candidate for an invented entity→fact link,
salient result omission or oversimplification, false no-progress, false
success/completion, result/outcome misreading, or wrong cause.  Finding one
useful subgoal result is not completing the overall task.  A later plan or
answer that consumes the false state cannot replace this earlier owner.

A concrete Memory/Reflection state error is not erased merely because a later
search happens to recover the answer.  Inspect this lane before adjacent tool
feedback and before Planning/Action at the same step.

LANE B — HARD TASK, INTERFACE, AND EXECUTION CONDITIONS

Check, in this order:

- explicit source/output constraints and missing prerequisites;
- whether the plan's required corpus and modality can be exposed by the chosen
  tool (dynamic video narration/frames, database UI flags, static page/PDF
  text, arithmetic, and academic-paper corpora are distinct);
- whether the plan targets the subgoal it says is next;
- whether Action faithfully implements an otherwise adequate plan with valid
  operation, syntax, and documented argument types;
- literal adjacent external exceptions.

Tool availability is not capability.  If a tool description/corpus cannot
contain the requested evidence, select the first plan that relies on it; do
not wait for later retries.  arXiv/PubMed cannot reveal another database's UI
flag state, and a static URL text extractor cannot observe dynamic video
narration or frames.

For a source constraint, a proposal to try another source becomes the material
breakpoint when the disallowed value is actually consumed by later reasoning,
unless the proposal itself immediately emits a terminal/destructive result.

System is eligible only when adjacent feedback literally reports an external
execution exception such as `Error executing tool`, invalid model/service/
configuration, or platform failure for a well-formed request.  Raw PDF bytes,
empty results, normal no-match output, access-denied/403 text returned by an
extractor, and an uninformative page are not System.  A wrong-typed argument is
Action.  Because adjacent feedback occurs after the assistant blocks, any
concrete same-step Memory, Reflection, Planning, or Action error found first
owns instead of System.  Otherwise freeze the action step carrying the literal
external exception even if the agent later tries a workaround.

LANE C — STRATEGY EPOCHS AND TERMINAL ABANDONMENT

Normalize a strategy as (unresolved subgoal, source/corpus, modality,
discriminating query/target).  The first reasonable probe is not an error.  A
repeat matures at the first consecutive recommitment to the same normalized
strategy after direct contrary or uninformative feedback.  Wording-only query
changes do not create a new strategy.  Do not wait for a later more literal
copy.

A materially different intervening source, modality, target, or discriminating
constraint resets ordinary repetition.  However, exact reuse of a target or
operation already demonstrated to fail remains a candidate.  A low-probability
but genuinely new source is exploratory, not automatically inefficient.

A terminal plan/answer that gives up while materially different viable
strategies or required calculations remain is a Planning candidate.  It may
defeat an earlier merely exploratory query, but not a concrete Lane-A or Lane-B
error or a known-failing repeat.

3. THE ONLY RECOVERY VETOES

Reject an otherwise early candidate only when one of these is literally true:

- a mechanical Action syntax/argument error is fully replaced by a successful
  different route before any false state consumes it;
- the attempt is an initial or materially different reasonable probe;
- an earlier query is merely exploratory and a later terminal premature
  abandonment is the first material error.

Do not use recovery to erase Memory/Reflection fact errors, explicit external
exceptions, hard constraints/prerequisites, corpus/modality impossibility, or a
repeat of a known-failing strategy.  Recovery of a task predicate requires
actually satisfying that predicate: finding one paper does not prove it is the
first paper.

4. FREEZE STEP BEFORE OWNER OR TYPE

Once the scan finds the first admissible candidate, stop comparing steps and
write the mandatory step-freeze checkpoint.  Do not consider module taxonomy,
error-type vocabulary, quote convenience, or a later competitor until the
checkpoint is written.  The checkpoint is immutable and the final
predicted_step must match it.

5. SAME-STEP OWNER AFTER THE CHECKPOINT

At only the frozen step, follow information flow:

- Memory owns new unsupported/omitted historical or world state.
- Reflection owns a false reading of result, outcome, progress, or cause.
- Planning owns strategy, query, target, constraint, prerequisite, capability,
  repetition, or premature-abandonment defects when upstream state is sound.
- Action owns concrete plan deviation, invalid/unparseable emission, unavailable
  operation, or mechanical argument error.
- System owns only an admitted literal external exception.

If false Memory is accepted by later blocks, Memory owns.  If Memory is sound
and Reflection misreads it, Reflection owns.  If both are sound and Planning
makes the bad choice, Planning owns.  A faithful Action never steals Planning
ownership.  Final answers obey the same handoff.

6. TYPE AND EVIDENCE LAST

Choose one legal type for the frozen owner.  A bad/repeated query is Planning
`inefficient_plan`, not Action `parameter_error`; `parameter_error` is only a
mechanically missing, malformed, wrong-typed, or misfilled argument.
`impossible_action` covers a plan whose required corpus/modality is unavailable.
`misalignment` requires contradiction of an otherwise adequate current plan.
`tool_execution_error` requires the literal external exception admitted above.

In rejected_adjacent_owner, name the strongest competitor and identify it as a
later symptom, faithful propagation, reasonable alternate probe, narrowly
recovered mechanical Action, or ineligible normal tool result.

"""


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_step_freeze_checkpoint(
    predictions_path: Path,
) -> dict[str, Any]:
    """Validate one immutable step-only checkpoint against one prediction."""

    try:
        predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentJudgeValidationError(
            "invalid_predictions_json",
            "predictions are unavailable for step checkpoint validation",
        ) from error
    if not isinstance(predictions, list) or len(predictions) != 1:
        raise AgentJudgeValidationError(
            "invalid_step_freeze_scope",
            "step checkpoint validation requires exactly one prediction",
        )
    checkpoint_path = predictions_path.parent / STEP_FREEZE_FILENAME
    _assert_safe_path(checkpoint_path, role="step freeze checkpoint")
    try:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentJudgeValidationError(
            "missing_or_invalid_step_freeze",
            "single-case prediction requires a valid step-freeze.json",
        ) from error
    if not isinstance(checkpoint, dict) or tuple(checkpoint) != STEP_FREEZE_FIELDS:
        raise AgentJudgeValidationError(
            "invalid_step_freeze_schema",
            "step checkpoint must contain only trajectory_id and predicted_step",
        )
    prediction = predictions[0]
    if checkpoint["trajectory_id"] != prediction.get("trajectory_id"):
        raise AgentJudgeValidationError(
            "step_freeze_identity_mismatch",
            "checkpoint trajectory does not match prediction",
        )
    step = checkpoint["predicted_step"]
    if isinstance(step, bool) or not isinstance(step, int) or step < 1:
        raise AgentJudgeValidationError(
            "invalid_step_freeze_step",
            "checkpoint predicted_step must be a positive integer",
        )
    if step != prediction.get("predicted_step"):
        raise AgentJudgeValidationError(
            "step_freeze_prediction_mismatch",
            "final predicted_step differs from immutable checkpoint",
        )
    return {
        "required": True,
        "valid": True,
        "path": str(checkpoint_path.resolve()),
        "sha256": _file_sha256(checkpoint_path),
        "predicted_step": step,
    }


def build_agent_judge_luna_gaia_v3_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build the lane-ordered task and require step freeze before taxonomy."""

    prediction_output = Path(predictions_path).expanduser().resolve()
    checkpoint = prediction_output.parent / STEP_FREEZE_FILENAME
    task = build_agent_judge_luna_gaia_v2_1_task(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction_output,
    )
    task = task.replace(
        AGENT_JUDGE_LUNA_GAIA_V2_1_VERSION,
        AGENT_JUDGE_LUNA_GAIA_V3_VERSION,
    )
    task = task.replace(
        "agentdebug/diagnostics/_evidence_policy.py",
        "agentdebug/diagnostics/_step_freeze.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._evidence_policy import "
        "validate_and_write_agent_judge_luna_gaia_v2_1_audit as run",
        "from agentdebug.diagnostics._step_freeze import "
        "validate_and_write_agent_judge_luna_gaia_v3_audit as run",
    )

    decision_start = task.find("THE ONLY DECISION ORDER\n")
    taxonomy_start = task.find("AGENT ERROR TAXONOMY\n")
    if decision_start < 0 or taxonomy_start <= decision_start:
        raise RuntimeError("Luna GAIA v2.1 decision section changed unexpectedly")
    task = (
        task[:decision_start]
        + _LANE_ORDERED_DECISION_RULES
        + task[taxonomy_start:]
    )

    old_boundary = f"- write predictions only to: {prediction_output}"
    new_boundary = (
        f"- write immutable step checkpoint only to: {checkpoint}\n"
        f"- write final predictions only to: {prediction_output}"
    )
    if old_boundary not in task:
        raise RuntimeError("Luna GAIA v2.1 output boundary changed unexpectedly")
    task = task.replace(old_boundary, new_boundary)

    audit_allowlist_line = (
        f"- {prediction_output} only after writing this run's prediction"
    )
    if audit_allowlist_line not in task:
        raise RuntimeError("Luna GAIA v2.1 output allowlist changed unexpectedly")
    task = task.replace(
        audit_allowlist_line,
        f"- {checkpoint} only after writing the frozen step checkpoint\n"
        + audit_allowlist_line,
    )

    checkpoint_rule = f"""\
MANDATORY STEP FREEZE CHECKPOINT

After the lane scan selects a step, before deciding module or error type, write
exactly this two-field JSON object to `{checkpoint}`:

{{
  "trajectory_id": "exact manifest trajectory ID",
  "predicted_step": "positive integer selected by the lane scan"
}}

Do not add fields and never edit this file after writing it.  Only then assign
the same-step owner/type/evidence and write the final ten-field prediction.
The validator rejects a missing checkpoint or any final predicted_step that
differs from it.

"""
    strict_contract = "STRICT TEN-FIELD CONTRACT\n"
    if strict_contract not in task:
        raise RuntimeError("Luna GAIA v2.1 strict contract changed unexpectedly")
    task = task.replace(
        strict_contract,
        checkpoint_rule + strict_contract,
        1,
    )
    return task


def validate_agent_judge_luna_gaia_v3_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    prediction_path = Path(predictions_path).expanduser().resolve()
    audit = validate_agent_judge_luna_gaia_v2_1_predictions(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction_path,
    )
    checkpoint = (
        _validate_step_freeze_checkpoint(prediction_path)
        if audit["case_count"] == 1
        else {
            "required": False,
            "valid": None,
            "reason": "merged full-cohort validation follows validated case shards",
        }
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V3_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_REASONING_EFFORT,
        "selection_policy": "lane_ordered_chronology_limited_recovery_veto",
        "step_freeze_checkpoint": checkpoint,
    }


def validate_and_write_agent_judge_luna_gaia_v3_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v3_predictions(
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
    "AGENT_JUDGE_LUNA_GAIA_V3_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V3_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V3_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V3_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "STEP_FREEZE_FIELDS",
    "STEP_FREEZE_FILENAME",
    "build_agent_judge_luna_gaia_v3_task",
    "validate_agent_judge_luna_gaia_v3_predictions",
    "validate_and_write_agent_judge_luna_gaia_v3_audit",
]
