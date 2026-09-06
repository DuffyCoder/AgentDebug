"""Luna Agent Judge v3: conflict-free chronological breakpoint scan.

Unlike Luna v1/v2, this frozen protocol does not inherit v2.4's global-root
prompt.  It retains only the shared strict contract and v2.4 evidence-source
policy, then gives Luna one unambiguous decision order: scan chronologically,
freeze the first mature causal error, resolve its same-step owner, and classify
it last.
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
    _file_sha256,
    _validate_agent_judge_predictions_with_owner_sources,
)
from ._owner_sources import (
    AGENT_JUDGE_V2_4_AUDIT_SCHEMA_VERSION,
    _v2_4_owner_source_resolver,
)
from .taxonomy import taxonomy_prompt


AGENT_JUDGE_LUNA_V3_VERSION = "agentdebug.codex-agent-judge.luna-v3"
AGENT_JUDGE_LUNA_V3_MODEL = "gpt-5.6-luna"
AGENT_JUDGE_LUNA_V3_REASONING_EFFORT = "medium"
AGENT_JUDGE_LUNA_V3_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_V2_4_AUDIT_SCHEMA_VERSION
)

GOLD_ISOLATION_LUNA_V3_READ_ALLOWLIST = (
    "the exact prediction_manifest_path named in the task",
    "the exact cohort_manifest_path named in the task",
    "agentdebug/diagnostics/_causal_task.py",
    "agentdebug/diagnostics/taxonomy.py",
)


def _validator_command(
    prediction_path: Path,
    cohort_path: Path,
    output_path: Path,
    audit_path: Path,
) -> str:
    code = (
        "import json; "
        "from agentdebug.diagnostics._causal_task import "
        "validate_and_write_agent_judge_luna_v3_audit as run; "
        "print(json.dumps(run("
        f"{str(prediction_path)!r}, {str(cohort_path)!r}, "
        f"{str(output_path)!r}, {str(audit_path)!r}"
        "), ensure_ascii=False, indent=2))"
    )
    return "PYTHONPATH=. python3 -c " + shlex.quote(code)


def build_agent_judge_luna_v3_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build the standalone chronological-breakpoint Luna v3 task."""

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    output_path = Path(predictions_path).expanduser().resolve()
    audit_path = output_path.parent / "prediction-audit.json"
    repository_root = Path(__file__).resolve().parents[2]
    _assert_safe_path(prediction_path, role="prediction manifest")
    _assert_safe_path(cohort_path, role="cohort manifest")
    _assert_safe_path(output_path, role="prediction output", is_output=True)
    _assert_safe_path(audit_path, role="prediction audit output", is_output=True)

    allowlist = "\n".join(
        f"- {item}" for item in GOLD_ISOLATION_LUNA_V3_READ_ALLOWLIST
    )
    allowlist += (
        f"\n- {output_path} only after writing this run's prediction"
        f"\n- {audit_path} only after the validator creates it"
    )
    denylist = "\n".join(f"- {item}" for item in GOLD_ISOLATION_READ_DENYLIST)
    schema = {
        "trajectory_id": "exact manifest trajectory ID",
        "trajectory_sha256": "exact manifest trajectory SHA-256",
        "status": "success",
        "predicted_step": "positive integer",
        "predicted_module": "taxonomy module",
        "predicted_error_type": "valid type for that module",
        "evidence_quote": "exact non-empty owner substring",
        "root_cause": "concise first-breakpoint explanation",
        "causal_summary": "local counterfactual and downstream propagation",
        "rejected_adjacent_owner": "strongest alternative and rejection reason",
    }
    validator_command = _validator_command(
        prediction_path,
        cohort_path,
        output_path,
        audit_path,
    )

    return f"""\
Run the frozen Codex Agent Judge protocol {AGENT_JUDGE_LUNA_V3_VERSION}.

IMMUTABLE EXECUTION CONFIGURATION
- model: {AGENT_JUDGE_LUNA_V3_MODEL}
- reasoning_effort: {AGENT_JUDGE_LUNA_V3_REASONING_EFFORT}
- one isolated case; no cross-case state or prior predictions
- external LLM/API/network calls: forbidden
- scoring or gold-label access: forbidden

INPUT/OUTPUT BOUNDARY
- prediction manifest: {prediction_path}
- prediction manifest file sha256: {_file_sha256(prediction_path)}
- cohort manifest: {cohort_path}
- cohort manifest file sha256: {_file_sha256(cohort_path)}
- write predictions only to: {output_path}
- local validation audit: {audit_path}

Read only the one complete JudgeView in the prediction manifest.  Do not infer
anything from trajectory ID, source model name, environment name, filenames,
or any cross-case pattern.  Those identifiers are identity fields, never
diagnostic evidence.

GOLD-ISOLATION READ ALLOWLIST
{allowlist}

GOLD-ISOLATION READ DENYLIST
{denylist}

THE ONLY DECISION ORDER

CHRONOLOGICAL SCAN -> FIRST MATURE CAUSAL ERROR -> FREEZE STEP ->
SAME-STEP OWNER -> TAXONOMY TYPE -> LITERAL EVIDENCE

Do not use a whole-episode "strongest root" comparison.  Do not prefer the
latest unrecovered problem.  The requested critical step is where a material
error is first introduced, not where its consequences become most visible.

1. CHRONOLOGICAL SCAN

Scan STEP 1, STEP 2, ... in order.  At every step, inspect the actual Memory,
Reflection, Planning, and Action sources that are present.  Internally mark
each source either OK or one concrete error proposition.  A candidate must be
demonstrably wrong using the task, interface, observations, and feedback
available at that time.  Vague suboptimality, hindsight, and a merely failed
reasonable probe are not candidates.

Check exact facts before strategy aesthetics.  In particular, actively look
for: a memory claim that drops or invents observed state; a reflection that
misreads a direct result, progress, or cause; a plan that ignores an explicit
constraint/prerequisite or recommits after contrary feedback; an action that
deviates from an adequate plan, cannot parse, invokes an unavailable operation,
or mechanically misfills an argument.

2. FIRST MATURE CAUSAL ERROR

Select the earliest candidate whose correction at that point would prevent a
material wrong branch, wasted sequence, unsupported answer, or failed
interaction.  Freeze predicted_step immediately.  Later recovery does not
move the critical step forward: it is evidence about downstream propagation,
not permission to replace the introduction with a later symptom.  Reject an
early candidate only if it caused no material consequence before being fully
corrected, or if it was reasonable under the evidence then.

For a repeated search, pagination, navigation, target, or claim, choose the
FIRST mature member of that repetition chain.  The first probe may be
reasonable.  The chain becomes mature at the first output written after direct
feedback or accumulated observations make continuing it unsupported,
redundant, constraint-violating, or informationally incapable.  Never choose a
later copy because repetition is more obvious there.

Do not invent an early planning error merely to be early.  A candidate needs a
literal false assertion, ignored constraint, contradicted observation,
unavailable prerequisite, needless repeat already demonstrated then, or
concrete interface defect.  When an early candidate is speculative but a
later one is directly demonstrated, choose the directly demonstrated step.

3. SAME-STEP OWNER AFTER STEP FREEZE

At the frozen step, follow the direction of information flow:
- Memory owns a new omission, retrieval failure, or invented historical/world
  state that later blocks consume.
- Reflection owns a new false reading of direct feedback, outcome, progress,
  or cause that later blocks consume.
- Planning owns a new defective strategy, constraint decision, prerequisite,
  target, or query when Memory and Reflection did not already introduce it.
- Action owns only a concrete deviation from an adequate current plan,
  unparseable syntax, unavailable operation, or mechanically wrong argument.

If a false Memory statement is accepted by Reflection and Plan in the same
step, Memory owns.  If accurate state is followed by false Reflection and an
implementing Plan, Reflection owns.  If Reflection is accurate but Plan makes
the bad choice, Planning owns.  A faithful action never steals ownership from
its plan.  Module tags and quote convenience establish source boundaries only;
they do not establish semantic ownership.

Final answers obey the same rule.  Action owns only when adequate upstream
reasoning is followed by a newly wrong or malformed emission.  If the answer
faithfully emits an earlier false belief, assessment, or derivation, select
that earlier introduction.

4. TERMINAL SYSTEM CHECK

Inspect provenance-backed execution_facts on every case.  System can own only
at the final step and only when a step limit, tool failure, model limit, or
environment fault independently prevents otherwise reasonable progress.  A
normal failed episode is not System.  Conversely, do not replace a genuine
external boundary with a merely improvable agent plan.

5. TYPE AND EVIDENCE ONLY AFTER STEP/OWNER FREEZE

Choose one legal type within the frozen owner.  Taxonomy fit must never move
the step.  Important admission boundaries:
- inefficient_plan is the first demonstrated wasteful/repetitive strategy,
  not a generic label for late failure;
- parameter_error is a mechanically missing, malformed, wrong-typed, or
  misfilled argument, not a bad query strategy or wrong conclusion;
- format_error is unparseable interface syntax, not merely a wrong answer;
- invalid_action requires an operation absent from the available action space;
- impossible_action requires a genuinely impossible state or prerequisite;
- misalignment requires a concrete contradiction of an adequate current plan.

In rejected_adjacent_owner, name the strongest same-step or later competitor
and say concretely why it is faithful propagation, a merely failed result, a
reasonable probe, or a later copy of the frozen error.

AGENT ERROR TAXONOMY
{taxonomy_prompt()}

EVIDENCE COPY RULE

evidence_quote must be exact, contiguous, case-sensitive selected-owner text
at predicted_step.  With no recognized module spans, any non-system owner may
quote assistant_raw_output.  With spans, normally quote only the owner's span;
Planning may also quote a deliberative residual, and Action may quote tool-call
name/string arguments.  Action residual text is available only for
format_error or invalid_action.  System must quote one accepted execution_facts
line at the final step.  Never quote observations, task text, another step, or
another recognized owner.

STRICT TEN-FIELD CONTRACT

Write one JSON array containing exactly one record and exactly these fields:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Every text field is non-empty; status is "success"; predicted_step is a
non-boolean in-range integer.  Emit no confidence, score, rank, vote, aliases,
nulls, or extra fields.  Before writing, re-check that no later symptom has
replaced the first mature causal error and that the evidence is literal owner
text.

MANDATORY LOCAL VALIDATION

Write the prediction, then run exactly:

cd {shlex.quote(str(repository_root))}
{validator_command}

The task is complete only after validation exits zero and creates the audit.
On failure inspect only the validator error and allowlisted current artifacts,
correct the prediction, and rerun.  Never inspect scores, labels, older
predictions, case studies, directories, git history, or external resources.
"""


def validate_agent_judge_luna_v3_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    audit = _validate_agent_judge_predictions_with_owner_sources(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
        owner_source_resolver=_v2_4_owner_source_resolver,
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_V3_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_V3_VERSION,
        "model": AGENT_JUDGE_LUNA_V3_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_V3_REASONING_EFFORT,
    }


def validate_and_write_agent_judge_luna_v3_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_v3_predictions(
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
    "AGENT_JUDGE_LUNA_V3_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_V3_MODEL",
    "AGENT_JUDGE_LUNA_V3_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_V3_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "GOLD_ISOLATION_LUNA_V3_READ_ALLOWLIST",
    "build_agent_judge_luna_v3_task",
    "validate_agent_judge_luna_v3_predictions",
    "validate_and_write_agent_judge_luna_v3_audit",
]
