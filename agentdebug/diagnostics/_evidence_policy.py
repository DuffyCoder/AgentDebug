"""Luna GAIA v2.1: v2 semantics with copy-safe execution addressing."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    AgentJudgeValidationError,
    _assert_safe_path,
)
from ._feedback_sources import (
    AGENT_JUDGE_LUNA_GAIA_V2_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_GAIA_V2_MODEL,
    AGENT_JUDGE_LUNA_GAIA_V2_REASONING_EFFORT,
    AGENT_JUDGE_LUNA_GAIA_V2_VERSION,
    build_agent_judge_luna_gaia_v2_task,
    validate_agent_judge_luna_gaia_v2_predictions,
)


AGENT_JUDGE_LUNA_GAIA_V2_1_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v2.1"
)
AGENT_JUDGE_LUNA_GAIA_V2_1_MODEL = AGENT_JUDGE_LUNA_GAIA_V2_MODEL
AGENT_JUDGE_LUNA_GAIA_V2_1_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V2_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V2_1_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V2_AUDIT_SCHEMA_VERSION
)


def build_agent_judge_luna_gaia_v2_1_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build v2's unchanged semantic task under a distinct frozen version."""

    task = build_agent_judge_luna_gaia_v2_task(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    task = task.replace(
        AGENT_JUDGE_LUNA_GAIA_V2_VERSION,
        AGENT_JUDGE_LUNA_GAIA_V2_1_VERSION,
    )
    task = task.replace(
        "agentdebug/diagnostics/_feedback_sources.py",
        "agentdebug/diagnostics/_evidence_policy.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._feedback_sources import "
        "validate_and_write_agent_judge_luna_gaia_v2_audit as run",
        "from agentdebug.diagnostics._evidence_policy import "
        "validate_and_write_agent_judge_luna_gaia_v2_1_audit as run",
    )
    return task


def validate_agent_judge_luna_gaia_v2_1_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v2_predictions(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V2_1_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V2_1_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V2_1_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V2_1_REASONING_EFFORT,
        "execution_addressing": "short_indexed_write_once_aliases",
    }


def validate_and_write_agent_judge_luna_gaia_v2_1_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v2_1_predictions(
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
    "AGENT_JUDGE_LUNA_GAIA_V2_1_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V2_1_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V2_1_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V2_1_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "build_agent_judge_luna_gaia_v2_1_task",
    "validate_agent_judge_luna_gaia_v2_1_predictions",
    "validate_and_write_agent_judge_luna_gaia_v2_1_audit",
]
