"""Luna GAIA v3.4: v3.1 with a validated chronological step ledger."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Sequence

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    AgentJudgeValidationError,
    _assert_safe_path,
)
from ._step_freeze import (
    STEP_FREEZE_FIELDS,
    STEP_FREEZE_FILENAME,
    _file_sha256,
)
from ._anchor_policy import (
    AGENT_JUDGE_LUNA_GAIA_V3_1_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_GAIA_V3_1_MODEL,
    AGENT_JUDGE_LUNA_GAIA_V3_1_REASONING_EFFORT,
    AGENT_JUDGE_LUNA_GAIA_V3_1_VERSION,
    build_agent_judge_luna_gaia_v3_1_task,
    validate_agent_judge_luna_gaia_v3_1_predictions,
)


AGENT_JUDGE_LUNA_GAIA_V3_4_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v3.4"
)
AGENT_JUDGE_LUNA_GAIA_V3_4_MODEL = AGENT_JUDGE_LUNA_GAIA_V3_1_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_4_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V3_1_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_4_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V3_1_AUDIT_SCHEMA_VERSION
)

STEP_CANDIDATE_LEDGER_FILENAME = "step-candidates.json"
STEP_CANDIDATE_LEDGER_FIELDS = (
    "trajectory_id",
    "rows",
    "selected_step",
)
STEP_CANDIDATE_ROW_FIELDS = (
    "step",
    "lane_a",
    "lane_b",
    "system",
    "lane_c",
    "surviving_lane",
    "evidence_quote",
    "decision_basis",
)
STEP_CANDIDATE_LANES = ("lane_a", "lane_b", "system", "lane_c")
STEP_CANDIDATE_STATUSES = frozenset(
    {
        "clear",
        "candidate",
        "veto_mechanical_repair",
        "veto_initial_probe",
        "veto_different_probe",
        "veto_terminal_supersession",
    }
)


_LEDGER_PROCESS_RULES = """\
STRUCTURED STEP-ONLY CANDIDATE LEDGER

This section changes process only.  All v3.1 admission, capability, recovery,
packet-fence, ownership, and taxonomy semantics remain unchanged.

Before writing the immutable step checkpoint, scan chronologically and write
one compact row for every inspected step from 1 through the first surviving
candidate.  A row records four ordered statuses:

1. `lane_a`: Memory/Reflection fact fidelity.
2. `lane_b`: hard task, interface, plan/Action, and prerequisite conditions.
3. `system`: eligible literal adjacent external exception after closing the
   assistant part of the same step packet.
4. `lane_c`: strategy epochs or terminal abandonment.

Each status must be exactly one of:

- `clear`: no candidate in that lane;
- `candidate`: a concrete material candidate survives;
- `veto_mechanical_repair`: only the existing narrow mechanical-repair veto;
- `veto_initial_probe`: only the existing initial reasonable-probe veto;
- `veto_different_probe`: only the existing materially-different-probe veto;
- `veto_terminal_supersession`: only the existing rule under which a later
  terminal abandonment defeats an earlier merely exploratory query.

Do not use a veto status as a new semantic exception.  All rows before the
selected step must have no `candidate` status and `surviving_lane: null`.  The
last row must contain at least one `candidate`; `surviving_lane` must be the
first candidate in the exact order lane_a, lane_b, system, lane_c.  Stop there:
do not add later rows.  `evidence_quote` is null on earlier rows and is one
literal substring from the selected step packet on the last row.

Write the ledger before the checkpoint.  Once written, never edit it.  The
checkpoint step is mechanically derived from the ledger's last row, not from
a later comparison or a more salient error.

"""


def _ledger_error(code: str, message: str) -> None:
    raise AgentJudgeValidationError(code, message)


def _validate_step_candidate_ledger_document(
    value: Any,
    *,
    trajectory_id: str,
    step_count: int,
    predicted_step: int,
    selected_packet_sources: Sequence[str],
) -> None:
    """Validate a write-once chronological ledger without using gold."""

    if not isinstance(value, dict) or tuple(value) != STEP_CANDIDATE_LEDGER_FIELDS:
        _ledger_error(
            "invalid_step_candidate_ledger_schema",
            "step ledger must contain only trajectory_id, rows, selected_step",
        )
    if value["trajectory_id"] != trajectory_id:
        _ledger_error(
            "step_candidate_ledger_identity_mismatch",
            "step ledger trajectory does not match the prediction manifest",
        )
    selected_step = value["selected_step"]
    if (
        isinstance(selected_step, bool)
        or not isinstance(selected_step, int)
        or selected_step < 1
        or selected_step > step_count
        or selected_step != predicted_step
    ):
        _ledger_error(
            "step_candidate_ledger_step_mismatch",
            "ledger selected_step must be the in-range frozen prediction step",
        )
    rows = value["rows"]
    if not isinstance(rows, list) or len(rows) != selected_step:
        _ledger_error(
            "invalid_step_candidate_ledger_rows",
            "ledger rows must cover exactly steps 1 through selected_step",
        )

    for index, row in enumerate(rows, start=1):
        location = f"step ledger row {index}"
        if not isinstance(row, dict) or tuple(row) != STEP_CANDIDATE_ROW_FIELDS:
            _ledger_error(
                "invalid_step_candidate_row_schema",
                f"{location} has unexpected fields or field order",
            )
        if row["step"] != index:
            _ledger_error(
                "invalid_step_candidate_row_order",
                f"{location} must identify chronological step {index}",
            )
        for lane in STEP_CANDIDATE_LANES:
            if row[lane] not in STEP_CANDIDATE_STATUSES:
                _ledger_error(
                    "invalid_step_candidate_status",
                    f"{location}.{lane} has an unknown status",
                )
        basis = row["decision_basis"]
        if not isinstance(basis, str) or not basis.strip() or len(basis) > 600:
            _ledger_error(
                "invalid_step_candidate_basis",
                f"{location}.decision_basis must be compact non-empty text",
            )

        candidate_lanes = [
            lane for lane in STEP_CANDIDATE_LANES if row[lane] == "candidate"
        ]
        if index < selected_step:
            if candidate_lanes:
                _ledger_error(
                    "step_candidate_before_selected_step",
                    f"{location} contains a surviving earlier candidate",
                )
            if row["surviving_lane"] is not None or row["evidence_quote"] is not None:
                _ledger_error(
                    "invalid_unselected_step_candidate_row",
                    f"{location} must not select a lane or evidence",
                )
            continue

        if not candidate_lanes:
            _ledger_error(
                "missing_selected_step_candidate",
                "the selected ledger row must contain a candidate",
            )
        if row["surviving_lane"] != candidate_lanes[0]:
            _ledger_error(
                "step_candidate_lane_order_mismatch",
                "surviving_lane must be the first candidate in frozen lane order",
            )
        quote = row["evidence_quote"]
        if (
            not isinstance(quote, str)
            or not quote.strip()
            or len(quote) > 1000
            or not any(quote in source for source in selected_packet_sources)
        ):
            _ledger_error(
                "invalid_step_candidate_evidence",
                "selected ledger evidence must be literal selected-packet text",
            )


def _validate_step_candidate_ledger(
    prediction_manifest_path: str | Path,
    predictions_path: Path,
) -> dict[str, Any]:
    """Load and validate the per-case ledger against public JudgeView data."""

    manifest_path = Path(prediction_manifest_path).expanduser().resolve()
    _assert_safe_path(manifest_path, role="prediction manifest")
    # Local import avoids a diagnostics/benchmark package initialization cycle.
    from agentdebug.benchmark.prediction_manifest import (  # noqa: PLC0415
        PredictionManifestError,
        load_prediction_manifest,
    )

    try:
        _, cases = load_prediction_manifest(manifest_path)
    except PredictionManifestError as error:
        _ledger_error("invalid_prediction_manifest", str(error))
    if len(cases) != 1:
        _ledger_error(
            "invalid_step_candidate_ledger_scope",
            "step ledger validation requires exactly one manifest case",
        )

    try:
        predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentJudgeValidationError(
            "invalid_predictions_json",
            "predictions are unavailable for step ledger validation",
        ) from error
    if not isinstance(predictions, list) or len(predictions) != 1:
        _ledger_error(
            "invalid_step_candidate_ledger_scope",
            "step ledger validation requires exactly one prediction",
        )

    ledger_path = predictions_path.parent / STEP_CANDIDATE_LEDGER_FILENAME
    _assert_safe_path(ledger_path, role="step candidate ledger")
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentJudgeValidationError(
            "missing_or_invalid_step_candidate_ledger",
            "single-case prediction requires a valid step-candidates.json",
        ) from error

    case = cases[0]
    prediction = predictions[0]
    selected_step = prediction.get("predicted_step")
    if isinstance(selected_step, bool) or not isinstance(selected_step, int):
        _ledger_error(
            "step_candidate_ledger_step_mismatch",
            "prediction step is unavailable for ledger validation",
        )
    step = case.judge_view.steps[selected_step - 1]
    packet_sources = [step.assistant_raw_output]
    packet_sources.extend(item.text for item in step.adjacent_feedback)
    _validate_step_candidate_ledger_document(
        ledger,
        trajectory_id=case.trajectory_id,
        step_count=len(case.judge_view.steps),
        predicted_step=selected_step,
        selected_packet_sources=packet_sources,
    )
    return {
        "required": True,
        "valid": True,
        "path": str(ledger_path.resolve()),
        "sha256": _file_sha256(ledger_path),
        "row_count": len(ledger["rows"]),
        "selected_step": ledger["selected_step"],
        "surviving_lane": ledger["rows"][-1]["surviving_lane"],
    }


def build_agent_judge_luna_gaia_v3_4_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build v3.1 with a write-once chronological candidate ledger."""

    prediction_output = Path(predictions_path).expanduser().resolve()
    ledger_path = prediction_output.parent / STEP_CANDIDATE_LEDGER_FILENAME
    task = build_agent_judge_luna_gaia_v3_1_task(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction_output,
    )
    task = task.replace(
        AGENT_JUDGE_LUNA_GAIA_V3_1_VERSION,
        AGENT_JUDGE_LUNA_GAIA_V3_4_VERSION,
    )
    task = task.replace(
        "agentdebug/diagnostics/_anchor_policy.py",
        "agentdebug/diagnostics/_candidate_ledger.py",
    )
    task = task.replace(
        "from agentdebug.diagnostics._anchor_policy import "
        "validate_and_write_agent_judge_luna_gaia_v3_1_audit as run",
        "from agentdebug.diagnostics._candidate_ledger import "
        "validate_and_write_agent_judge_luna_gaia_v3_4_audit as run",
    )

    old_order = (
        "LANE-ORDERED CHRONOLOGICAL SCAN -> WRITE IMMUTABLE STEP CHECKPOINT ->\n"
        "SAME-STEP OWNER -> TAXONOMY TYPE -> LITERAL EVIDENCE -> FINAL PREDICTION"
    )
    new_order = (
        "LANE-ORDERED CHRONOLOGICAL SCAN -> WRITE STEP CANDIDATE LEDGER ->\n"
        "WRITE IMMUTABLE STEP CHECKPOINT -> SAME-STEP OWNER -> TAXONOMY TYPE ->\n"
        "LITERAL EVIDENCE -> FINAL PREDICTION"
    )
    if task.count(old_order) != 1:
        raise RuntimeError("Luna GAIA v3.1 decision order changed unexpectedly")
    task = task.replace(old_order, new_order, 1)

    section_four = "4. FREEZE STEP BEFORE OWNER OR TYPE\n"
    if task.count(section_four) != 1:
        raise RuntimeError("Luna GAIA v3.1 freeze section changed unexpectedly")
    task = task.replace(section_four, _LEDGER_PROCESS_RULES + section_four, 1)

    checkpoint_boundary = (
        f"- write immutable step checkpoint only to: "
        f"{prediction_output.parent / STEP_FREEZE_FILENAME}"
    )
    if task.count(checkpoint_boundary) != 1:
        raise RuntimeError("Luna GAIA v3.1 output boundary changed unexpectedly")
    task = task.replace(
        checkpoint_boundary,
        f"- write immutable step candidate ledger only to: {ledger_path}\n"
        + checkpoint_boundary,
        1,
    )

    checkpoint_allowlist = (
        f"- {prediction_output.parent / STEP_FREEZE_FILENAME} only after writing "
        "the frozen step checkpoint"
    )
    if task.count(checkpoint_allowlist) != 1:
        raise RuntimeError("Luna GAIA v3.1 allowlist changed unexpectedly")
    task = task.replace(
        checkpoint_allowlist,
        f"- {ledger_path} only after writing the frozen step candidate ledger\n"
        + checkpoint_allowlist,
        1,
    )

    ledger_contract = f"""\
MANDATORY WRITE-ONCE STEP CANDIDATE LEDGER

Before the step checkpoint, write exactly one JSON object to `{ledger_path}`.
Use exactly these top-level fields in this order:

{{
  "trajectory_id": "exact manifest trajectory ID",
  "rows": [
    {{
      "step": 1,
      "lane_a": "clear",
      "lane_b": "clear",
      "system": "clear",
      "lane_c": "veto_initial_probe",
      "surviving_lane": null,
      "evidence_quote": null,
      "decision_basis": "compact literal step assessment"
    }},
    {{
      "step": 2,
      "lane_a": "candidate",
      "lane_b": "clear",
      "system": "clear",
      "lane_c": "clear",
      "surviving_lane": "lane_a",
      "evidence_quote": "literal substring from selected step packet",
      "decision_basis": "compact reason this is the first surviving candidate"
    }}
  ],
  "selected_step": 2
}}

The example illustrates shape only; derive row count, statuses, lane, quote,
and selected step solely from the one JudgeView.  Rows must be consecutive,
must stop at selected_step, and must obey the status and lane-order rules
above.  Write this file once and never edit it.  Then derive and write the
two-field step checkpoint from its last row before considering owner/type.

"""
    checkpoint_contract = "MANDATORY STEP FREEZE CHECKPOINT\n"
    if task.count(checkpoint_contract) != 1:
        raise RuntimeError("Luna GAIA v3.1 checkpoint contract changed unexpectedly")
    return task.replace(
        checkpoint_contract,
        ledger_contract + checkpoint_contract,
        1,
    )


def validate_agent_judge_luna_gaia_v3_4_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    prediction_path = Path(predictions_path).expanduser().resolve()
    audit = validate_agent_judge_luna_gaia_v3_1_predictions(
        prediction_manifest_path,
        cohort_manifest_path,
        prediction_path,
    )
    ledger = (
        _validate_step_candidate_ledger(prediction_manifest_path, prediction_path)
        if audit["case_count"] == 1
        else {
            "required": False,
            "valid": None,
            "reason": "merged full-cohort validation follows validated case shards",
        }
    )
    return {
        **audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V3_4_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_4_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_4_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_4_REASONING_EFFORT,
        "selection_policy": (
            "lane_ordered_chronology_validated_step_candidate_ledger_"
            "limited_recovery_veto_external_exception_packet_fence"
        ),
        "step_candidate_ledger": ledger,
    }


def validate_and_write_agent_judge_luna_gaia_v3_4_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    audit = validate_agent_judge_luna_gaia_v3_4_predictions(
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
    "AGENT_JUDGE_LUNA_GAIA_V3_4_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V3_4_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V3_4_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V3_4_VERSION",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AgentJudgeValidationError",
    "STEP_CANDIDATE_LEDGER_FIELDS",
    "STEP_CANDIDATE_LEDGER_FILENAME",
    "STEP_CANDIDATE_LANES",
    "STEP_CANDIDATE_ROW_FIELDS",
    "STEP_CANDIDATE_STATUSES",
    "STEP_FREEZE_FIELDS",
    "STEP_FREEZE_FILENAME",
    "build_agent_judge_luna_gaia_v3_4_task",
    "validate_agent_judge_luna_gaia_v3_4_predictions",
    "validate_and_write_agent_judge_luna_gaia_v3_4_audit",
]
