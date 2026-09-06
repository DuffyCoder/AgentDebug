"""Luna GAIA v3.14: earliest-causal refinement of the v3.13 challenger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from . import _debate as parent


AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger"
)
AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL = parent.AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT = (
    parent.AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_14_AUDIT_SCHEMA_VERSION = (
    parent.AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION
)

# Compatibility aliases let the proven v3.13 runner execute this protocol without
# weakening any input, sidecar, exact-copy, or gold-free validation contract.
AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION = AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION
AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL = AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V3_14_AUDIT_SCHEMA_VERSION
)

ANCHOR_PREDICTIONS_FILENAME = parent.ANCHOR_PREDICTIONS_FILENAME
ANCHOR_LEDGER_AGGREGATE_FILENAME = parent.ANCHOR_LEDGER_AGGREGATE_FILENAME
ANCHOR_CHECKPOINT_AGGREGATE_FILENAME = parent.ANCHOR_CHECKPOINT_AGGREGATE_FILENAME
CHALLENGER_FILENAME = parent.CHALLENGER_FILENAME
CHALLENGERS_FILENAME = parent.CHALLENGERS_FILENAME
ARBITER_FILENAME = parent.ARBITER_FILENAME
ARBITERS_FILENAME = parent.ARBITERS_FILENAME
CHALLENGER_AUDIT_FILENAME = parent.CHALLENGER_AUDIT_FILENAME
ARBITER_AUDIT_FILENAME = parent.ARBITER_AUDIT_FILENAME
PREDICTION_AUDIT_FILENAME = parent.PREDICTION_AUDIT_FILENAME
CHALLENGER_FIELDS = parent.CHALLENGER_FIELDS
ARBITER_FIELDS = parent.ARBITER_FIELDS


_EARLIEST_CAUSAL_RULES = """\
EARLIEST-CAUSAL SINGLE-CHALLENGER RULE

The frozen v3.4 prediction is the incumbent anchor, not merely one candidate.
Do not enumerate a candidate pool. Emit at most one strictly later proposal.

First evaluate anchor repair as an intervention on the path:

1. Ask what the trace could do if only the anchor defect were repaired.
2. Do not hold an observed later reaction fixed when successful anchor repair
   could prevent that reaction from occurring.
3. In particular, retain an eligible external System/tool-execution-failure
   anchor for a well-formed task-relevant call when successful execution could
   avert the later path. A later reaction to that failure is not independent
   merely because it has its own local plan/Action mismatch.
4. Override such an anchor only when literal chronology proves that the same
   later defect was already present or necessarily remains after successful
   anchor execution.

If literal evidence instead proves the anchor is a reasonable information-
gathering probe or a noncritical predecessor, scan Step anchor+1, anchor+2, and
so on in strict chronological order. The proposal must be the EARLIEST later
Step that remains independently failure-causing under anchor-only repair. Stop
at the first qualifying Step. Do not skip an earlier repeated-strategy boundary,
false outcome/progress state, or failure-causing commitment for a later System
exception, stronger wording, persistence, severity, or terminal symptom.

A repeated-strategy Step qualifies only when the preceding observation already
rules out the normalized strategy for the unresolved subgoal and the new Step
makes no material change. A System exception qualifies only at its actual owner
Step and only if it is not path-dependent on an earlier repair.

Keep the anchor when its exact defect persists, evidence is uncertain, or no
later Step passes both causal independence and earliest-boundary checks. Keep
direct unsupported state, explicit constraint or plan/Action contradiction,
terminal abandonment, and direct capability roots unless literal recovery or
path-intervention evidence falsifies their criticality.

Use anchor_only_repair_counterfactual to state whether repair changes the later
path. Use proposal_only_repair_counterfactual to show why the earliest proposal
can avert failure. direct_timeline_comparison must compare anchor, every earlier
later Step that could plausibly qualify, and the proposed Step. search_summary
must certify that no earlier later Step qualifies. When uncertain, no_challenge.
"""


def _rewrite_parent_task(task: str) -> str:
    return (
        task.replace(parent._CONSERVATIVE_RULES, _EARLIEST_CAUSAL_RULES)
        .replace(parent.AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION, AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION)
        .replace(
            "_debate",
            "_protocol_challenger",
        )
        .replace("CONSERVATIVE SINGLE-CHALLENGER", "EARLIEST-CAUSAL SINGLE-CHALLENGER")
    )


def build_anchor_task(*paths: str | Path) -> str:
    return _rewrite_parent_task(parent.build_anchor_task(*paths))


def build_challenger_task(*paths: str | Path) -> str:
    return _rewrite_parent_task(parent.build_challenger_task(*paths))


def build_arbiter_task(*paths: str | Path) -> str:
    task = _rewrite_parent_task(parent.build_arbiter_task(*paths))
    return task.replace(
        "Accept it only if every anchor-falsification and proposal-\n"
        "materiality claim is supported by literal chronology.",
        "Accept it only if every path-intervention, earliest-boundary, anchor-\n"
        "falsification, and proposal-materiality claim is supported by literal chronology.",
    )


def build_agent_judge_luna_gaia_v3_14_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    prediction = Path(predictions_path).expanduser().resolve()
    return build_arbiter_task(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction.parent / ANCHOR_PREDICTIONS_FILENAME,
        prediction.parent / "step-candidates.json",
        prediction.parent / "step-freeze.json",
        prediction.parent / CHALLENGER_FILENAME,
        prediction.parent / ARBITER_FILENAME,
    )


def validate_challenger(*paths: str | Path) -> dict[str, Any]:
    audit = parent.validate_challenger(*paths)
    return {
        **audit,
        "schema_version": "agentdebug.earliest-causal-challenger-audit.v1",
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT,
        "path_intervention_required": True,
        "earliest_later_boundary_required": True,
    }


def validate_arbiter(*paths: str | Path) -> dict[str, Any]:
    audit = parent.validate_arbiter(*paths)
    return {
        **audit,
        "schema_version": "agentdebug.earliest-causal-arbiter-audit.v1",
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT,
        "default_anchor_policy": True,
        "path_intervention_review_required": True,
        "earliest_later_boundary_review_required": True,
    }


def validate_agent_judge_luna_gaia_v3_14_predictions(
    *paths: str | Path,
) -> dict[str, Any]:
    audit = parent.validate_agent_judge_luna_gaia_v3_13_predictions(*paths)
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V3_14_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT,
        "selection_policy": (
            "v3_4_anchor_one_earliest_causal_later_challenger_"
            "independent_default_keep_arbiter"
        ),
        "path_intervention_required": True,
        "earliest_later_boundary_required": True,
    }


def _write_audit(audit: dict[str, Any], path: str | Path) -> dict[str, Any]:
    return parent._write_audit(audit, path)


def validate_and_write_challenger_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_challenger(*paths[:-1]), paths[-1])


def validate_and_write_arbiter_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_arbiter(*paths[:-1]), paths[-1])


def validate_and_write_agent_judge_luna_gaia_v3_14_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    return _write_audit(
        validate_agent_judge_luna_gaia_v3_14_predictions(
            prediction_manifest_path, cohort_manifest_path, predictions_path
        ),
        audit_path,
    )


# Compatibility names used by the shared paper-50 runner.
build_agent_judge_luna_gaia_v3_13_task = build_agent_judge_luna_gaia_v3_14_task
validate_agent_judge_luna_gaia_v3_13_predictions = (
    validate_agent_judge_luna_gaia_v3_14_predictions
)
validate_and_write_agent_judge_luna_gaia_v3_13_audit = (
    validate_and_write_agent_judge_luna_gaia_v3_14_audit
)


def run_compact_validation(stage: str, paths: Sequence[str]) -> int:
    try:
        if stage == "challenger" and len(paths) == 7:
            audit = validate_and_write_challenger_audit(*paths)
        elif stage == "arbiter" and len(paths) == 8:
            audit = validate_and_write_arbiter_audit(*paths)
        elif stage == "prediction" and len(paths) == 4:
            audit = validate_and_write_agent_judge_luna_gaia_v3_14_audit(*paths)
        else:
            parent._fail(
                "invalid_compact_validation_arguments", "stage/path count differs"
            )
    except parent.AgentJudgeValidationError as error:
        print(json.dumps({"ok": False, "code": error.code}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "audit": audit}, ensure_ascii=False))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--compact-validate", action="store_true")
    parser.add_argument("stage", choices=("challenger", "arbiter", "prediction"))
    parser.add_argument("paths", nargs="+")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.compact_validate:
        raise SystemExit("only --compact-validate is supported")
    return run_compact_validation(args.stage, args.paths)


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AGENT_JUDGE_LUNA_GAIA_V3_14_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION",
    "ANCHOR_CHECKPOINT_AGGREGATE_FILENAME",
    "ANCHOR_LEDGER_AGGREGATE_FILENAME",
    "ANCHOR_PREDICTIONS_FILENAME",
    "ARBITER_FILENAME",
    "ARBITERS_FILENAME",
    "CHALLENGER_FILENAME",
    "CHALLENGERS_FILENAME",
    "build_agent_judge_luna_gaia_v3_14_task",
    "build_anchor_task",
    "build_arbiter_task",
    "build_challenger_task",
    "validate_agent_judge_luna_gaia_v3_14_predictions",
    "validate_and_write_agent_judge_luna_gaia_v3_14_audit",
    "validate_and_write_arbiter_audit",
    "validate_and_write_challenger_audit",
    "validate_arbiter",
    "validate_challenger",
]
