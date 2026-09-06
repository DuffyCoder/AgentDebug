"""GAIA v3.83: an exact v3.20 protocol replay with GPT-5.5/medium.

The only semantic change from the accepted v3.20 incumbent is the model ID.
All prompts, stage contracts, selectors, and validators come directly from
v3.20; only experiment identity and truthful model provenance are retagged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import _state_closure as parent


AGENT_JUDGE_GAIA_V3_83_VERSION = (
    "agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium"
)
AGENT_JUDGE_GAIA_V3_83_MODEL = "gpt-5.5"
AGENT_JUDGE_GAIA_V3_83_REASONING_EFFORT = "medium"
AGENT_JUDGE_GAIA_V3_83_AUDIT_SCHEMA_VERSION = (
    parent.AGENT_JUDGE_LUNA_GAIA_V3_20_AUDIT_SCHEMA_VERSION
)
SEMANTIC_PARENT = parent.AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION

# Compatibility names consumed by the frozen shared v3.20 three-stage runner.
AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION = AGENT_JUDGE_GAIA_V3_83_VERSION
AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL = AGENT_JUDGE_GAIA_V3_83_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT = (
    AGENT_JUDGE_GAIA_V3_83_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_GAIA_V3_83_AUDIT_SCHEMA_VERSION
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


def _retag_task(task: str) -> str:
    version_marker = parent.AGENT_JUDGE_LUNA_GAIA_V3_20_VERSION
    model_marker = f"- model: {parent.AGENT_JUDGE_LUNA_GAIA_V3_20_MODEL}"
    if task.count(version_marker) != 1:
        raise RuntimeError("v3.20 task identity marker changed unexpectedly")
    if task.count(model_marker) != 1:
        raise RuntimeError("v3.20 task model marker changed unexpectedly")
    return task.replace(version_marker, AGENT_JUDGE_GAIA_V3_83_VERSION, 1).replace(
        model_marker,
        f"- model: {AGENT_JUDGE_GAIA_V3_83_MODEL}",
        1,
    )


def build_anchor_task(*paths: str | Path) -> str:
    return _retag_task(parent.build_anchor_task(*paths))


def build_challenger_task(*paths: str | Path) -> str:
    return _retag_task(parent.build_challenger_task(*paths))


def build_arbiter_task(*paths: str | Path) -> str:
    return _retag_task(parent.build_arbiter_task(*paths))


def build_agent_judge_gaia_v3_83_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    prediction = Path(predictions_path).expanduser().resolve()
    return build_arbiter_task(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction.parent / ANCHOR_PREDICTIONS_FILENAME,
        prediction.parent / parent.STEP_CANDIDATE_LEDGER_FILENAME,
        prediction.parent / "step-freeze.json",
        prediction.parent / CHALLENGER_FILENAME,
        prediction.parent / ARBITER_FILENAME,
    )


def _retag_audit(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        **audit,
        "agent_judge_version": AGENT_JUDGE_GAIA_V3_83_VERSION,
        "model": AGENT_JUDGE_GAIA_V3_83_MODEL,
        "reasoning_effort": AGENT_JUDGE_GAIA_V3_83_REASONING_EFFORT,
        "semantic_parent": SEMANTIC_PARENT,
        "model_only_swap": True,
    }


def validate_anchor_predictions(*paths: str | Path) -> dict[str, Any]:
    return _retag_audit(parent.validate_anchor_predictions(*paths))


def validate_challenger(*paths: str | Path) -> dict[str, Any]:
    return _retag_audit(parent.validate_challenger(*paths))


def validate_arbiter(*paths: str | Path) -> dict[str, Any]:
    return _retag_audit(parent.validate_arbiter(*paths))


def validate_agent_judge_gaia_v3_83_predictions(
    *paths: str | Path,
) -> dict[str, Any]:
    return _retag_audit(
        parent.validate_agent_judge_luna_gaia_v3_20_predictions(*paths)
    )


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
            prediction_manifest_path,
            cohort_manifest_path,
            predictions_path,
        ),
        audit_path,
    )


def validate_and_write_challenger_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_challenger(*paths[:-1]), paths[-1])


def validate_and_write_arbiter_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_arbiter(*paths[:-1]), paths[-1])


def validate_and_write_agent_judge_gaia_v3_83_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    return _write_audit(
        validate_agent_judge_gaia_v3_83_predictions(
            prediction_manifest_path,
            cohort_manifest_path,
            predictions_path,
        ),
        audit_path,
    )


# Compatibility names consumed by the shared paper-50 runner.
build_agent_judge_luna_gaia_v3_13_task = build_agent_judge_gaia_v3_83_task
validate_agent_judge_luna_gaia_v3_13_predictions = (
    validate_agent_judge_gaia_v3_83_predictions
)
validate_and_write_agent_judge_luna_gaia_v3_13_audit = (
    validate_and_write_agent_judge_gaia_v3_83_audit
)


__all__ = [
    "AGENT_JUDGE_GAIA_V3_83_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_GAIA_V3_83_MODEL",
    "AGENT_JUDGE_GAIA_V3_83_REASONING_EFFORT",
    "AGENT_JUDGE_GAIA_V3_83_VERSION",
    "SEMANTIC_PARENT",
    "build_agent_judge_gaia_v3_83_task",
    "build_anchor_task",
    "build_arbiter_task",
    "build_challenger_task",
    "validate_agent_judge_gaia_v3_83_predictions",
    "validate_and_write_agent_judge_gaia_v3_83_audit",
]
