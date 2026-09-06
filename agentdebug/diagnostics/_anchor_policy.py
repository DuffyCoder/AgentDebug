"""Luna GAIA v3.1: v3 plus an external-exception step-packet fence."""

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
from ._step_freeze import (
    AGENT_JUDGE_LUNA_GAIA_V3_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_GAIA_V3_MODEL,
    AGENT_JUDGE_LUNA_GAIA_V3_REASONING_EFFORT,
    AGENT_JUDGE_LUNA_GAIA_V3_VERSION,
    STEP_FREEZE_FIELDS,
    STEP_FREEZE_FILENAME,
    build_agent_judge_luna_gaia_v3_task,
    validate_agent_judge_luna_gaia_v3_predictions,
)


AGENT_JUDGE_LUNA_GAIA_V3_1_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v3.1"
)
AGENT_JUDGE_LUNA_GAIA_V3_1_MODEL = AGENT_JUDGE_LUNA_GAIA_V3_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_1_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V3_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_1_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V3_AUDIT_SCHEMA_VERSION
)


_PACKET_FENCE = """\
EXTERNAL-EXCEPTION STEP-PACKET FENCE

A step packet consists of the assistant's Memory, Reflection, Planning, and
Action blocks at step N followed by the adjacent feedback produced by that
action.  Close the entire packet before inspecting any assistant text at step
N+1:

1. Inspect assistant-module candidates inside step N in the lane order above.
2. Then inspect step N's adjacent feedback for an eligible literal external
   exception.
3. If that exception exists and no admissible assistant-module error already
   exists inside step N, freeze step N as System immediately.
4. Do not read or compare Memory, Reflection, Planning, or Action at step N+1
   first.  A step-N+1 explanation of the exception is later evidence and can
   never be a same-step competitor to System at step N.

This fence changes ordering only.  Raw PDF bytes, empty/no-match results,
normal 403/access-denied content, uninformative pages, and agent-caused
argument errors remain ineligible for System exactly as specified above.

"""


def build_agent_judge_luna_gaia_v3_1_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build v3 with one explicit cross-step System ordering fence."""

    task = build_agent_judge_luna_gaia_v3_task(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    task = task.replace(
        AGENT_JUDGE_LUNA_GAIA_V3_VERSION,
        AGENT_JUDGE_LUNA_GAIA_V3_1_VERSION,
    )
    task = task.replace(
        "agentdebug/diagnostics/_step_freeze.py",
        "agentdebug/diagnostics/_anchor_policy.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._step_freeze import "
        "validate_and_write_agent_judge_luna_gaia_v3_audit as run",
        "from agentdebug.diagnostics._anchor_policy import "
        "validate_and_write_agent_judge_luna_gaia_v3_1_audit as run",
    )
    lane_c = "LANE C — STRATEGY EPOCHS AND TERMINAL ABANDONMENT\n"
    if task.count(lane_c) != 1:
        raise RuntimeError("Luna GAIA v3 lane-C boundary changed unexpectedly")
    return task.replace(lane_c, _PACKET_FENCE + lane_c, 1)


def validate_agent_judge_luna_gaia_v3_1_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v3_predictions(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V3_1_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_1_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_1_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_1_REASONING_EFFORT,
        "selection_policy": (
            "lane_ordered_chronology_limited_recovery_veto_"
            "external_exception_step_packet_fence"
        ),
        "external_exception_packet_fence": True,
    }


def validate_and_write_agent_judge_luna_gaia_v3_1_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v3_1_predictions(
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
    "AGENT_JUDGE_LUNA_GAIA_V3_1_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V3_1_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V3_1_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V3_1_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "STEP_FREEZE_FIELDS",
    "STEP_FREEZE_FILENAME",
    "build_agent_judge_luna_gaia_v3_1_task",
    "validate_agent_judge_luna_gaia_v3_1_predictions",
    "validate_and_write_agent_judge_luna_gaia_v3_1_audit",
]
