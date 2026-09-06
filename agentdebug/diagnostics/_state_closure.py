"""Luna GAIA v3.20: validator-audited packet Memory/Reflection closure."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from . import _protocol_challenger as parent
from . import _debate as shared
from ._candidate_ledger import (
    STEP_CANDIDATE_LEDGER_FILENAME,
    validate_agent_judge_luna_gaia_v3_4_predictions,
)


AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure"
)
AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL = parent.AGENT_JUDGE_LUNA_GAIA_V3_14_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT = (
    parent.AGENT_JUDGE_LUNA_GAIA_V3_14_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_20_AUDIT_SCHEMA_VERSION = (
    parent.AGENT_JUDGE_LUNA_GAIA_V3_14_AUDIT_SCHEMA_VERSION
)

# Compatibility aliases used by the shared three-stage runner.
AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION = AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION
AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL = AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V3_20_AUDIT_SCHEMA_VERSION
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


_STATE_PREFIX = re.compile(
    r"^state_scope=(memory_reflection|none); "
    r"state_fidelity=(faithful|dropped_necessary_fact|unsupported_fact|outcome_misread|not_applicable); "
)

_PACKET_STATE_GATE = """\
PACKET-STATE CLOSURE — BINDING BEFORE ALL LANE DECISIONS

For every inspected Step, close the literal relation between adjacent feedback
and the packet's Memory/Reflection before applying probe, capability, System,
repetition, or terminal rules. Begin decision_basis exactly:

`state_scope=<memory_reflection|none>; state_fidelity=<faithful|dropped_necessary_fact|unsupported_fact|outcome_misread|not_applicable>; `

Use state_scope=memory_reflection when the packet contains Memory or Reflection
that retains or interprets the current information state. Otherwise use
state_scope=none with state_fidelity=not_applicable.

The non-faithful statuses are narrow and task-material:

- `dropped_necessary_fact`: adjacent feedback contains a concrete fact necessary
  for the unresolved subgoal or next decision, and Memory/Reflection omits or
  materially distorts it. Ordinary compression, wording changes, and facts
  still available to the next decision do not qualify.
- `unsupported_fact`: Memory/Reflection asserts a new task-material entity,
  credential, value, or relation unsupported by visible observation/history.
  Harmless speculation not retained downstream does not qualify.
- `outcome_misread`: Memory/Reflection makes a success, failure, progress, or
  constraint claim literally contradicted by adjacent feedback.

Use a non-faithful status only when that false or lost state feeds the current
or next plan and repairing it can change the later path. Then lane_a MUST be
candidate. With state_fidelity=faithful, lane_a MUST be clear and all existing
lanes and vetoes run unchanged. Do not promote stylistic summary differences,
minor omissions, or locally false but causally irrelevant wording.

"""


def _rewrite_parent_task(task: str) -> str:
    return (
        task.replace(
            parent.AGENT_JUDGE_LUNA_GAIA_V3_14_VERSION,
            AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION,
        )
        .replace(
            "_protocol_challenger",
            "_state_closure",
        )
        .replace(
            "agentdebug/diagnostics/_protocol_challenger.py",
            "agentdebug/diagnostics/_state_closure.py",
        )
    )


def _rewrite_anchor_validator(task: str) -> str:
    task = task.replace(
        "agentdebug/diagnostics/_candidate_ledger.py",
        "agentdebug/diagnostics/_state_closure.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._candidate_ledger import "
        "validate_and_write_agent_judge_luna_gaia_v3_4_audit as run",
        "from agentdebug.diagnostics._state_closure "
        "import validate_and_write_anchor_audit as run",
    )
    return task


def build_anchor_task(*paths: str | Path) -> str:
    task = _rewrite_anchor_validator(_rewrite_parent_task(parent.build_anchor_task(*paths)))
    marker = "STRUCTURED STEP-ONLY CANDIDATE LEDGER\n"
    if task.count(marker) != 1:
        raise RuntimeError("v3.14 ledger process marker changed unexpectedly")
    task = task.replace(marker, _PACKET_STATE_GATE + marker, 1)
    task = task.replace(
        '"decision_basis": "compact literal step assessment"',
        '"decision_basis": "state_scope=memory_reflection; state_fidelity=faithful; compact literal step assessment"',
    )
    task = task.replace(
        '"decision_basis": "compact reason this is the first surviving candidate"',
        '"decision_basis": "state_scope=memory_reflection; state_fidelity=unsupported_fact; compact reason this is the first surviving candidate"',
    )
    return task


def build_challenger_task(*paths: str | Path) -> str:
    return _rewrite_parent_task(parent.build_challenger_task(*paths))


def build_arbiter_task(*paths: str | Path) -> str:
    return _rewrite_parent_task(parent.build_arbiter_task(*paths))


def build_agent_judge_luna_gaia_v3_20_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    prediction = Path(predictions_path).expanduser().resolve()
    return build_arbiter_task(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction.parent / ANCHOR_PREDICTIONS_FILENAME,
        prediction.parent / STEP_CANDIDATE_LEDGER_FILENAME,
        prediction.parent / "step-freeze.json",
        prediction.parent / CHALLENGER_FILENAME,
        prediction.parent / ARBITER_FILENAME,
    )


def _validate_packet_state_ledgers(path: str | Path) -> dict[str, Any]:
    ledger_path, raw = shared._load_artifact(path, role="packet-state ledger")
    ledgers = raw if isinstance(raw, list) else [raw]
    if not ledgers or any(not isinstance(item, dict) for item in ledgers):
        shared._fail("invalid_packet_state_ledger", "ledger records unavailable")

    counts: Counter[str] = Counter()
    row_count = 0
    nonfaithful_count = 0
    for ledger_index, ledger in enumerate(ledgers):
        rows = ledger.get("rows")
        if not isinstance(rows, list) or not rows:
            shared._fail(
                "invalid_packet_state_rows",
                f"ledger[{ledger_index}] rows unavailable",
            )
        for row_index, row in enumerate(rows):
            basis = row.get("decision_basis") if isinstance(row, dict) else None
            match = _STATE_PREFIX.match(basis or "")
            if match is None:
                shared._fail(
                    "missing_packet_state_prefix",
                    f"ledger[{ledger_index}].rows[{row_index}]",
                )
            scope, fidelity = match.groups()
            location = f"ledger[{ledger_index}].rows[{row_index}]"
            if scope == "none":
                if fidelity != "not_applicable":
                    shared._fail("invalid_none_state_pairing", location)
            elif fidelity == "not_applicable":
                shared._fail("missing_memory_reflection_state_fidelity", location)

            if fidelity in {
                "dropped_necessary_fact",
                "unsupported_fact",
                "outcome_misread",
            }:
                if row.get("lane_a") != "candidate":
                    shared._fail("nonfaithful_state_lacks_lane_a_candidate", location)
                nonfaithful_count += 1
            elif fidelity == "faithful" and row.get("lane_a") != "clear":
                shared._fail("faithful_state_lacks_lane_a_clear", location)
            counts[f"{scope}:{fidelity}"] += 1
            row_count += 1
    return {
        "required": True,
        "valid": True,
        "path": str(ledger_path),
        "ledger_count": len(ledgers),
        "row_count": row_count,
        "state_counts": dict(sorted(counts.items())),
        "nonfaithful_state_admission_count": nonfaithful_count,
    }


def validate_anchor_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v3_4_predictions(
        prediction_manifest_path, cohort_manifest_path, predictions_path
    )
    ledger = Path(predictions_path).expanduser().resolve().parent / STEP_CANDIDATE_LEDGER_FILENAME
    state = _validate_packet_state_ledgers(ledger)
    return {
        **audit,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT,
        "selection_policy": "v3_4_anchor_with_packet_state_closure",
        "packet_state_closure": state,
    }


def validate_challenger(*paths: str | Path) -> dict[str, Any]:
    audit = parent.validate_challenger(*paths)
    state = _validate_packet_state_ledgers(paths[3])
    return {
        **audit,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT,
        "packet_state_closure": state,
    }


def validate_arbiter(*paths: str | Path) -> dict[str, Any]:
    audit = parent.validate_arbiter(*paths)
    state = _validate_packet_state_ledgers(paths[3])
    return {
        **audit,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT,
        "packet_state_closure": state,
    }


def validate_agent_judge_luna_gaia_v3_20_predictions(*paths: str | Path) -> dict[str, Any]:
    audit = parent.validate_agent_judge_luna_gaia_v3_14_predictions(*paths)
    predictions = Path(paths[2]).expanduser().resolve()
    state = _validate_packet_state_ledgers(
        predictions.parent / ANCHOR_LEDGER_AGGREGATE_FILENAME
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V3_20_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT,
        "selection_policy": (
            "packet_state_closure_v3_4_anchor_one_earliest_causal_later_"
            "challenger_default_keep_exact_copy_arbiter"
        ),
        "packet_state_closure": state,
    }


def _write_audit(audit: dict[str, Any], path: str | Path) -> dict[str, Any]:
    return parent._write_audit(audit, path)


def validate_and_write_anchor_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    return _write_audit(
        validate_anchor_predictions(
            prediction_manifest_path, cohort_manifest_path, predictions_path
        ),
        audit_path,
    )


def validate_and_write_challenger_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_challenger(*paths[:-1]), paths[-1])


def validate_and_write_arbiter_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_arbiter(*paths[:-1]), paths[-1])


def validate_and_write_agent_judge_luna_gaia_v3_20_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    return _write_audit(
        validate_agent_judge_luna_gaia_v3_20_predictions(
            prediction_manifest_path, cohort_manifest_path, predictions_path
        ),
        audit_path,
    )


# Compatibility names used by the shared paper-50 runner.
build_agent_judge_luna_gaia_v3_13_task = build_agent_judge_luna_gaia_v3_20_task
validate_agent_judge_luna_gaia_v3_13_predictions = (
    validate_agent_judge_luna_gaia_v3_20_predictions
)
validate_and_write_agent_judge_luna_gaia_v3_13_audit = (
    validate_and_write_agent_judge_luna_gaia_v3_20_audit
)


def run_compact_validation(stage: str, paths: Sequence[str]) -> int:
    try:
        if stage == "anchor" and len(paths) == 4:
            audit = validate_and_write_anchor_audit(*paths)
        elif stage == "challenger" and len(paths) == 7:
            audit = validate_and_write_challenger_audit(*paths)
        elif stage == "arbiter" and len(paths) == 8:
            audit = validate_and_write_arbiter_audit(*paths)
        elif stage == "prediction" and len(paths) == 4:
            audit = validate_and_write_agent_judge_luna_gaia_v3_20_audit(*paths)
        else:
            shared._fail("invalid_compact_validation_arguments", "stage/path count differs")
    except shared.AgentJudgeValidationError as error:
        print(json.dumps({"ok": False, "code": error.code}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "audit": audit}, ensure_ascii=False))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--compact-validate", action="store_true")
    parser.add_argument("stage", choices=("anchor", "challenger", "arbiter", "prediction"))
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
    "AGENT_JUDGE_LUNA_GAIA_V3_20_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V3_20_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION",
    "ANCHOR_CHECKPOINT_AGGREGATE_FILENAME",
    "ANCHOR_LEDGER_AGGREGATE_FILENAME",
    "ANCHOR_PREDICTIONS_FILENAME",
    "ARBITER_FILENAME",
    "ARBITERS_FILENAME",
    "CHALLENGER_FILENAME",
    "CHALLENGERS_FILENAME",
    "build_agent_judge_luna_gaia_v3_20_task",
    "build_anchor_task",
    "build_arbiter_task",
    "build_challenger_task",
    "validate_agent_judge_luna_gaia_v3_20_predictions",
    "validate_anchor_predictions",
    "validate_and_write_agent_judge_luna_gaia_v3_20_audit",
    "validate_and_write_anchor_audit",
    "validate_and_write_arbiter_audit",
    "validate_and_write_challenger_audit",
    "validate_arbiter",
    "validate_challenger",
]
