"""Luna GAIA v3.13: v3.4 anchor with one conservative later challenger.

The first session runs the frozen v3.4 protocol as an anchor. A second fresh
session may emit at most one later challenger after falsifying the anchor's
criticality with literal trace evidence. A third fresh session defaults to the
anchor and may select only that exact challenger. No candidate census exists.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
from pathlib import Path
from typing import Any, Sequence

from ._contract import (
    AGENT_JUDGE_PREDICTION_FIELDS,
    AgentJudgeValidationError,
    _assert_gold_free,
    _assert_safe_path,
    _cohort_document,
    _file_sha256,
    _load_json,
    _stable_sha256,
    _validate_agent_judge_predictions_with_owner_sources,
)
from ._feedback_sources import _luna_gaia_v2_owner_source_resolver
from ._step_freeze import STEP_FREEZE_FILENAME
from ._candidate_ledger import (
    AGENT_JUDGE_LUNA_GAIA_V3_4_AUDIT_SCHEMA_VERSION,
    AGENT_JUDGE_LUNA_GAIA_V3_4_MODEL,
    AGENT_JUDGE_LUNA_GAIA_V3_4_REASONING_EFFORT,
    STEP_CANDIDATE_LEDGER_FILENAME,
    build_agent_judge_luna_gaia_v3_4_task,
    validate_agent_judge_luna_gaia_v3_4_predictions,
)
from .taxonomy import AgentModule, ErrorType, is_valid_classification, taxonomy_prompt


AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION = (
    "agentdebug.codex-agent-judge.luna-gaia-v3.13-conservative-challenger"
)
AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL = AGENT_JUDGE_LUNA_GAIA_V3_4_MODEL
AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT = (
    AGENT_JUDGE_LUNA_GAIA_V3_4_REASONING_EFFORT
)
AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION = (
    AGENT_JUDGE_LUNA_GAIA_V3_4_AUDIT_SCHEMA_VERSION
)

ANCHOR_PREDICTIONS_FILENAME = "anchor-predictions.json"
ANCHOR_LEDGER_AGGREGATE_FILENAME = "anchor-step-candidates.json"
ANCHOR_CHECKPOINT_AGGREGATE_FILENAME = "anchor-step-freezes.json"
CHALLENGER_FILENAME = "challenger.json"
CHALLENGERS_FILENAME = "challengers.json"
ARBITER_FILENAME = "arbiter.json"
ARBITERS_FILENAME = "arbiters.json"
CHALLENGER_AUDIT_FILENAME = "challenger-audit.json"
ARBITER_AUDIT_FILENAME = "arbiter-audit.json"
PREDICTION_AUDIT_FILENAME = "prediction-audit.json"

CHALLENGER_FIELDS = (
    "trajectory_id",
    "trajectory_sha256",
    "anchor_prediction_sha256",
    "anchor_ledger_sha256",
    "anchor_checkpoint_sha256",
    "anchor_step",
    "challenge_status",
    "anchor_classification",
    "anchor_veto_evidence_step",
    "anchor_veto_evidence_quote",
    "proposed_prediction",
    "anchor_falsifier",
    "anchor_only_repair_counterfactual",
    "proposal_only_repair_counterfactual",
    "direct_timeline_comparison",
    "search_summary",
)
CHALLENGE_STATUSES = frozenset({"no_challenge", "challenge"})
ANCHOR_CLASSIFICATIONS = frozenset(
    {"critical_root", "reasonable_probe", "noncritical_predecessor", "uncertain"}
)
OVERRIDE_CLASSIFICATIONS = frozenset(
    {"reasonable_probe", "noncritical_predecessor"}
)

ARBITER_FIELDS = (
    "trajectory_id",
    "trajectory_sha256",
    "anchor_prediction_sha256",
    "challenger_sha256",
    "anchor_step",
    "decision",
    "frozen_step",
    "selected_prediction_sha256",
    "selected_prediction",
    "decision_basis",
    "rejected_alternative_basis",
)
ARBITER_DECISIONS = frozenset({"keep_anchor", "accept_challenger"})


def _fail(code: str, message: str) -> None:
    raise AgentJudgeValidationError(code, message)


def _nonempty_text(value: Any, *, location: str, maximum: int = 1800) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        _fail("invalid_conservative_artifact_text", f"{location} must be compact text")


def _load_cases(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
) -> tuple[Path, Path, list[Any]]:
    manifest_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    _assert_safe_path(manifest_path, role="prediction manifest")
    _assert_safe_path(cohort_path, role="cohort manifest")
    from agentdebug.benchmark.prediction_manifest import (  # noqa: PLC0415
        PredictionManifestError,
        load_prediction_manifest,
    )

    try:
        manifest, cases = load_prediction_manifest(manifest_path)
    except PredictionManifestError as error:
        _fail("invalid_prediction_manifest", str(error))
    cohort = _cohort_document(cohort_path)
    if [case.trajectory_id for case in cases] != cohort["trajectory_ids"]:
        _fail("manifest_cohort_order_mismatch", "manifest and cohort order differ")
    if (
        manifest.get("cohort_name") != cohort.get("cohort_name")
        or manifest.get("cohort_sha256") != cohort.get("cohort_sha256")
        or manifest.get("dataset_manifest_sha256")
        != cohort.get("dataset_manifest_sha256")
    ):
        _fail("manifest_cohort_identity_mismatch", "manifest and cohort differ")
    return manifest_path, cohort_path, cases


def _single_case_paths(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
) -> tuple[Path, Path, Any]:
    manifest, cohort, cases = _load_cases(
        prediction_manifest_path, cohort_manifest_path
    )
    if len(cases) != 1:
        _fail("conservative_stage_requires_one_case", "each stage needs one case")
    return manifest, cohort, cases[0]


def _load_artifact(path: str | Path, *, role: str) -> tuple[Path, Any]:
    target = Path(path).expanduser().resolve()
    _assert_safe_path(target, role=role)
    value = _load_json(target, role=role)
    _assert_gold_free(value, location=role)
    return target, value


def _one_record(value: Any, *, role: str) -> dict[str, Any]:
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        _fail("invalid_conservative_artifact_count", f"{role} needs one record")
    return value[0]


def _packet_sources(case: Any, step_number: int) -> tuple[str, ...]:
    if step_number < 1 or step_number > len(case.judge_view.steps):
        return ()
    step = case.judge_view.steps[step_number - 1]
    sources = [step.assistant_raw_output]
    sources.extend(item.text for item in step.adjacent_feedback)
    return tuple(source for source in sources if source.strip())


def _validate_prediction_record(
    raw: Any,
    *,
    case: Any,
    location: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != AGENT_JUDGE_PREDICTION_FIELDS:
        _fail("invalid_embedded_prediction_fields", f"{location} fields differ")
    for field in AGENT_JUDGE_PREDICTION_FIELDS - {"predicted_step"}:
        _nonempty_text(raw.get(field), location=f"{location}.{field}", maximum=2400)
    if raw["status"] != "success":
        _fail("invalid_embedded_prediction_status", f"{location}.status")
    if (
        raw["trajectory_id"] != case.trajectory_id
        or raw["trajectory_sha256"] != case.trajectory_sha256
    ):
        _fail("embedded_prediction_identity_mismatch", location)
    step = raw["predicted_step"]
    if (
        isinstance(step, bool)
        or not isinstance(step, int)
        or step < 1
        or step > len(case.judge_view.steps)
    ):
        _fail("invalid_embedded_prediction_step", location)
    try:
        module = AgentModule(raw["predicted_module"])
        error_type = ErrorType(raw["predicted_error_type"])
    except ValueError:
        _fail("invalid_embedded_prediction_taxonomy", location)
    if not is_valid_classification(module, error_type):
        _fail("invalid_embedded_prediction_taxonomy", location)
    sources = _luna_gaia_v2_owner_source_resolver(
        case.judge_view, step, module, error_type
    )
    if not sources or not any(raw["evidence_quote"] in source for source in sources):
        _fail("invalid_embedded_prediction_evidence", location)
    return raw


def _validate_anchor_bundle(
    manifest: Path,
    cohort: Path,
    anchor_path: Path,
    ledger_path: Path,
    checkpoint_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if ledger_path.name != STEP_CANDIDATE_LEDGER_FILENAME:
        _fail("invalid_anchor_ledger_name", "anchor ledger filename changed")
    if checkpoint_path.name != STEP_FREEZE_FILENAME:
        _fail("invalid_anchor_checkpoint_name", "anchor checkpoint filename changed")
    if anchor_path.parent != ledger_path.parent or anchor_path.parent != checkpoint_path.parent:
        _fail("anchor_bundle_directory_mismatch", "anchor files must be co-located")
    audit = validate_agent_judge_luna_gaia_v3_4_predictions(
        manifest, cohort, anchor_path
    )
    anchor = _one_record(_load_json(anchor_path, role="anchor predictions"), role="anchor")
    ledger = _load_json(ledger_path, role="anchor ledger")
    checkpoint = _load_json(checkpoint_path, role="anchor checkpoint")
    _assert_gold_free(anchor, location="anchor")
    _assert_gold_free(ledger, location="anchor ledger")
    _assert_gold_free(checkpoint, location="anchor checkpoint")
    if checkpoint.get("predicted_step") != anchor.get("predicted_step"):
        _fail("anchor_checkpoint_step_mismatch", "anchor Step differs")
    if ledger.get("selected_step") != anchor.get("predicted_step"):
        _fail("anchor_ledger_step_mismatch", "anchor ledger Step differs")
    if audit.get("gold_free_validation") is not True:
        _fail("anchor_not_gold_free", "v3.4 anchor audit did not pass")
    return anchor, ledger, checkpoint


def _validate_challenger_record(
    raw: Any,
    *,
    case: Any,
    anchor: dict[str, Any],
    ledger: dict[str, Any],
    checkpoint: dict[str, Any],
    location: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict) or tuple(raw) != CHALLENGER_FIELDS:
        _fail("invalid_challenger_schema", f"{location} fields/order differ")
    if (
        raw["trajectory_id"] != case.trajectory_id
        or raw["trajectory_sha256"] != case.trajectory_sha256
    ):
        _fail("challenger_identity_mismatch", location)
    bindings = {
        "anchor_prediction_sha256": _stable_sha256(anchor),
        "anchor_ledger_sha256": _stable_sha256(ledger),
        "anchor_checkpoint_sha256": _stable_sha256(checkpoint),
    }
    if any(raw[key] != value for key, value in bindings.items()):
        _fail("challenger_anchor_hash_mismatch", location)
    anchor_step = anchor["predicted_step"]
    if raw["anchor_step"] != anchor_step:
        _fail("challenger_anchor_step_mismatch", location)
    if raw["challenge_status"] not in CHALLENGE_STATUSES:
        _fail("invalid_challenge_status", location)
    if raw["anchor_classification"] not in ANCHOR_CLASSIFICATIONS:
        _fail("invalid_anchor_classification", location)
    for field in (
        "anchor_falsifier",
        "anchor_only_repair_counterfactual",
        "proposal_only_repair_counterfactual",
        "direct_timeline_comparison",
        "search_summary",
    ):
        _nonempty_text(raw[field], location=f"{location}.{field}")

    if raw["challenge_status"] == "no_challenge":
        if any(
            raw[field] is not None
            for field in (
                "anchor_veto_evidence_step",
                "anchor_veto_evidence_quote",
                "proposed_prediction",
            )
        ):
            _fail("no_challenge_must_not_propose", location)
        return raw

    if raw["anchor_classification"] not in OVERRIDE_CLASSIFICATIONS:
        _fail("challenge_lacks_anchor_veto", location)
    veto_step = raw["anchor_veto_evidence_step"]
    veto_quote = raw["anchor_veto_evidence_quote"]
    if (
        isinstance(veto_step, bool)
        or not isinstance(veto_step, int)
        or veto_step < anchor_step
        or veto_step > len(case.judge_view.steps)
        or not isinstance(veto_quote, str)
        or not veto_quote.strip()
        or len(veto_quote) > 1200
        or not any(veto_quote in source for source in _packet_sources(case, veto_step))
    ):
        _fail("invalid_anchor_veto_evidence", location)
    proposal = _validate_prediction_record(
        raw["proposed_prediction"], case=case, location=f"{location}.proposal"
    )
    if proposal["predicted_step"] <= anchor_step:
        _fail("challenger_must_be_later_than_anchor", location)
    return raw


def validate_challenger(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    anchor_path: str | Path,
    ledger_path: str | Path,
    checkpoint_path: str | Path,
    challenger_path: str | Path,
) -> dict[str, Any]:
    manifest, cohort, case = _single_case_paths(
        prediction_manifest_path, cohort_manifest_path
    )
    anchor_file = Path(anchor_path).expanduser().resolve()
    ledger_file = Path(ledger_path).expanduser().resolve()
    checkpoint_file = Path(checkpoint_path).expanduser().resolve()
    challenger_file, raw = _load_artifact(challenger_path, role="challenger")
    anchor, ledger, checkpoint = _validate_anchor_bundle(
        manifest, cohort, anchor_file, ledger_file, checkpoint_file
    )
    record = _one_record(raw, role="challenger")
    _validate_challenger_record(
        record,
        case=case,
        anchor=anchor,
        ledger=ledger,
        checkpoint=checkpoint,
        location="challenger[0]",
    )
    return {
        "schema_version": "agentdebug.conservative-challenger-audit.v1",
        "stage": "challenger",
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT,
        "gold_free_validation": True,
        "case_count": 1,
        "challenge_status": record["challenge_status"],
        "later_only": True,
        "single_challenger_maximum": True,
        "input_sha256": {
            ANCHOR_PREDICTIONS_FILENAME: _file_sha256(anchor_file),
            STEP_CANDIDATE_LEDGER_FILENAME: _file_sha256(ledger_file),
            STEP_FREEZE_FILENAME: _file_sha256(checkpoint_file),
        },
        "output_sha256": {CHALLENGER_FILENAME: _file_sha256(challenger_file)},
    }


def _validate_arbiter_record(
    raw: Any,
    *,
    case: Any,
    anchor: dict[str, Any],
    challenger: dict[str, Any],
    location: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict) or tuple(raw) != ARBITER_FIELDS:
        _fail("invalid_arbiter_schema", f"{location} fields/order differ")
    if (
        raw["trajectory_id"] != case.trajectory_id
        or raw["trajectory_sha256"] != case.trajectory_sha256
    ):
        _fail("arbiter_identity_mismatch", location)
    if raw["anchor_prediction_sha256"] != _stable_sha256(anchor):
        _fail("arbiter_anchor_hash_mismatch", location)
    if raw["challenger_sha256"] != _stable_sha256(challenger):
        _fail("arbiter_challenger_hash_mismatch", location)
    anchor_step = anchor["predicted_step"]
    if raw["anchor_step"] != anchor_step:
        _fail("arbiter_anchor_step_mismatch", location)
    if raw["decision"] not in ARBITER_DECISIONS:
        _fail("invalid_arbiter_decision", location)
    _nonempty_text(raw["decision_basis"], location=f"{location}.decision_basis")
    _nonempty_text(
        raw["rejected_alternative_basis"],
        location=f"{location}.rejected_alternative_basis",
    )
    selected = _validate_prediction_record(
        raw["selected_prediction"], case=case, location=f"{location}.selected"
    )
    if raw["selected_prediction_sha256"] != _stable_sha256(selected):
        _fail("arbiter_selected_prediction_hash_mismatch", location)
    if raw["frozen_step"] != selected["predicted_step"]:
        _fail("arbiter_frozen_step_mismatch", location)
    if raw["decision"] == "keep_anchor":
        if selected != anchor or raw["frozen_step"] != anchor_step:
            _fail("arbiter_anchor_copy_mismatch", location)
    else:
        if challenger["challenge_status"] != "challenge":
            _fail("arbiter_accepts_missing_challenge", location)
        if challenger["anchor_classification"] not in OVERRIDE_CLASSIFICATIONS:
            _fail("arbiter_accepts_unfalsified_anchor", location)
        if selected != challenger["proposed_prediction"]:
            _fail("arbiter_challenger_copy_mismatch", location)
        if raw["frozen_step"] <= anchor_step:
            _fail("arbiter_override_not_later", location)
    return raw


def validate_arbiter(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    anchor_path: str | Path,
    ledger_path: str | Path,
    checkpoint_path: str | Path,
    challenger_path: str | Path,
    arbiter_path: str | Path,
) -> dict[str, Any]:
    manifest, cohort, case = _single_case_paths(
        prediction_manifest_path, cohort_manifest_path
    )
    anchor_file = Path(anchor_path).expanduser().resolve()
    ledger_file = Path(ledger_path).expanduser().resolve()
    checkpoint_file = Path(checkpoint_path).expanduser().resolve()
    challenger_file, challenger_raw = _load_artifact(
        challenger_path, role="challenger"
    )
    arbiter_file, arbiter_raw = _load_artifact(arbiter_path, role="arbiter")
    anchor, ledger, checkpoint = _validate_anchor_bundle(
        manifest, cohort, anchor_file, ledger_file, checkpoint_file
    )
    challenger = _one_record(challenger_raw, role="challenger")
    _validate_challenger_record(
        challenger,
        case=case,
        anchor=anchor,
        ledger=ledger,
        checkpoint=checkpoint,
        location="challenger[0]",
    )
    arbiter = _one_record(arbiter_raw, role="arbiter")
    _validate_arbiter_record(
        arbiter,
        case=case,
        anchor=anchor,
        challenger=challenger,
        location="arbiter[0]",
    )
    return {
        "schema_version": "agentdebug.conservative-arbiter-audit.v1",
        "stage": "arbiter",
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT,
        "gold_free_validation": True,
        "case_count": 1,
        "decision": arbiter["decision"],
        "default_anchor_policy": True,
        "selected_prediction_exact_copy": True,
        "input_sha256": {
            ANCHOR_PREDICTIONS_FILENAME: _file_sha256(anchor_file),
            CHALLENGER_FILENAME: _file_sha256(challenger_file),
        },
        "output_sha256": {ARBITER_FILENAME: _file_sha256(arbiter_file)},
    }


def validate_agent_judge_luna_gaia_v3_13_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    manifest, cohort, cases = _load_cases(
        prediction_manifest_path, cohort_manifest_path
    )
    prediction_file = Path(predictions_path).expanduser().resolve()
    base_audit = _validate_agent_judge_predictions_with_owner_sources(
        manifest,
        cohort,
        prediction_file,
        owner_source_resolver=_luna_gaia_v2_owner_source_resolver,
    )
    anchor_file, anchors = _load_artifact(
        prediction_file.parent / ANCHOR_PREDICTIONS_FILENAME,
        role="merged anchors",
    )
    ledger_file, ledgers = _load_artifact(
        prediction_file.parent / ANCHOR_LEDGER_AGGREGATE_FILENAME,
        role="merged anchor ledgers",
    )
    checkpoint_file, checkpoints = _load_artifact(
        prediction_file.parent / ANCHOR_CHECKPOINT_AGGREGATE_FILENAME,
        role="merged anchor checkpoints",
    )
    challenger_file, challengers = _load_artifact(
        prediction_file.parent / CHALLENGERS_FILENAME,
        role="merged challengers",
    )
    arbiter_file, arbiters = _load_artifact(
        prediction_file.parent / ARBITERS_FILENAME,
        role="merged arbiters",
    )
    predictions = _load_json(prediction_file, role="predictions")
    values = (anchors, ledgers, checkpoints, challengers, arbiters, predictions)
    if any(not isinstance(value, list) or len(value) != len(cases) for value in values):
        _fail("invalid_merged_conservative_count", "all merged artifacts need all cases")
    decisions: list[str] = []
    for index, (case, anchor, ledger, checkpoint, challenger, arbiter, prediction) in enumerate(
        zip(cases, anchors, ledgers, checkpoints, challengers, arbiters, predictions, strict=True)
    ):
        location = f"merged[{index}]"
        _validate_prediction_record(anchor, case=case, location=f"{location}.anchor")
        if (
            ledger.get("trajectory_id") != case.trajectory_id
            or ledger.get("selected_step") != anchor["predicted_step"]
            or checkpoint.get("trajectory_id") != case.trajectory_id
            or checkpoint.get("predicted_step") != anchor["predicted_step"]
        ):
            _fail("merged_anchor_sidecar_mismatch", location)
        _validate_challenger_record(
            challenger,
            case=case,
            anchor=anchor,
            ledger=ledger,
            checkpoint=checkpoint,
            location=f"{location}.challenger",
        )
        _validate_arbiter_record(
            arbiter,
            case=case,
            anchor=anchor,
            challenger=challenger,
            location=f"{location}.arbiter",
        )
        if prediction != arbiter["selected_prediction"]:
            _fail("final_prediction_differs_from_arbiter", location)
        decisions.append(arbiter["decision"])
    return {
        **base_audit,
        "schema_version": AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION,
        "model": AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL,
        "reasoning_effort": AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT,
        "selection_policy": (
            "v3_4_anchor_one_later_challenger_independent_default_keep_arbiter"
        ),
        "gold_free_validation": True,
        "case_count": len(cases),
        "all_selected_predictions_exact_copies": True,
        "arbiter_decision_counts": {
            decision: decisions.count(decision) for decision in sorted(set(decisions))
        },
        "input_sidecar_sha256": {
            ANCHOR_PREDICTIONS_FILENAME: _file_sha256(anchor_file),
            ANCHOR_LEDGER_AGGREGATE_FILENAME: _file_sha256(ledger_file),
            ANCHOR_CHECKPOINT_AGGREGATE_FILENAME: _file_sha256(checkpoint_file),
            CHALLENGERS_FILENAME: _file_sha256(challenger_file),
            ARBITERS_FILENAME: _file_sha256(arbiter_file),
        },
    }


def _write_audit(audit: dict[str, Any], audit_path: str | Path) -> dict[str, Any]:
    target = Path(audit_path).expanduser().resolve()
    _assert_safe_path(target, role="stage audit output", is_output=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(f"{target.suffix}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(target)
    return audit


def validate_and_write_challenger_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_challenger(*paths[:-1]), paths[-1])


def validate_and_write_arbiter_audit(*paths: str | Path) -> dict[str, Any]:
    return _write_audit(validate_arbiter(*paths[:-1]), paths[-1])


def validate_and_write_agent_judge_luna_gaia_v3_13_audit(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    audit_path: str | Path,
) -> dict[str, Any]:
    return _write_audit(
        validate_agent_judge_luna_gaia_v3_13_predictions(
            prediction_manifest_path, cohort_manifest_path, predictions_path
        ),
        audit_path,
    )


def _command(arguments: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(item)) for item in arguments)


def _boundary(
    *,
    manifest: Path,
    cohort: Path,
    reads: Sequence[Path],
    output: Path,
) -> str:
    read_lines = "\n".join(f"- {path}" for path in reads) or "- none"
    return f"""\
IMMUTABLE EXECUTION CONFIGURATION
- model: {AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL}
- reasoning_effort: {AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT}
- one isolated case; fresh session; no cross-case state or prior predictions
- external LLM/API/network calls: forbidden
- scoring or gold-label access: forbidden

INPUT/OUTPUT BOUNDARY
- prediction manifest: {manifest}
- prediction manifest file sha256: {_file_sha256(manifest)}
- cohort manifest: {cohort}
- cohort manifest file sha256: {_file_sha256(cohort)}
- permitted frozen stage inputs:
{read_lines}
- write the sole stage artifact only to: {output}

Read only those exact inputs plus
`agentdebug/diagnostics/_debate.py`
and `agentdebug/diagnostics/taxonomy.py`. Do not inspect directories or infer
from trajectory/source-model/environment names. Never read labels, metrics,
scored artifacts, promotion files, docs/experiments, old predictions, cached
replies, case studies, git history, or external resources.
"""


_CONSERVATIVE_RULES = """\
CONSERVATIVE SINGLE-CHALLENGER RULE

The frozen v3.4 prediction is the incumbent anchor, not merely one candidate.
Do not enumerate a candidate pool. Search only for direct evidence that this
specific anchor is not the critical root, and emit at most one later proposal.

A challenge is permitted only when literal chronology proves the anchor is:

1. a reasonable information-gathering probe for its immediate subgoal, where
   successful use could contribute a needed identifier, page, citation,
   transcript lead, or context even though it could not prove the final answer;
   or
2. a noncritical predecessor whose correction alone would not avert failure,
   followed by a later independent false outcome/progress state, eligible
   external System exception, or independently failure-causing commitment.

No challenge is allowed merely because a later defect is more severe, long,
salient, persistent, or strongly worded. Keep the anchor when its exact defect
persists, evidence is uncertain, or it is an explicit constraint violation,
plan/Action target contradiction, unsupported state, or terminal abandonment.
Also keep direct capability roots where an already identified exact video/URL
is assigned to static extraction for frames, narration, or timestamp evidence,
or an interactive UI predicate is directly assigned to an interface that
cannot observe UI state.

For a repeated-strategy anchor, later repetition alone is insufficient. A
challenge needs literal proof that the anchor still made a material change or
that a later independent false-success/System event, not repetition salience,
is the critical root. When uncertain, emit no_challenge.
"""


def build_anchor_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    anchor_path: str | Path,
) -> str:
    task = build_agent_judge_luna_gaia_v3_4_task(
        prediction_manifest_path, cohort_manifest_path, anchor_path
    )
    return (
        f"Run {AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION} stage 1/3: frozen v3.4 "
        "anchor. The following v3.4 task is the complete anchor contract; do "
        "not perform challenger or arbiter work in this session.\n\n" + task
    )


def build_challenger_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    anchor_path: str | Path,
    ledger_path: str | Path,
    checkpoint_path: str | Path,
    challenger_path: str | Path,
) -> str:
    manifest, cohort, case = _single_case_paths(
        prediction_manifest_path, cohort_manifest_path
    )
    anchor_file = Path(anchor_path).expanduser().resolve()
    ledger_file = Path(ledger_path).expanduser().resolve()
    checkpoint_file = Path(checkpoint_path).expanduser().resolve()
    anchor, ledger, checkpoint = _validate_anchor_bundle(
        manifest, cohort, anchor_file, ledger_file, checkpoint_file
    )
    output = Path(challenger_path).expanduser().resolve()
    _assert_safe_path(output, role="challenger output", is_output=True)
    audit = output.parent / CHALLENGER_AUDIT_FILENAME
    command = _command(
        (
            "PYTHONPATH=. python3 -m",
            "agentdebug.diagnostics._debate",
            "--compact-validate",
            "challenger",
            manifest,
            cohort,
            anchor_file,
            ledger_file,
            checkpoint_file,
            output,
            audit,
        )
    ).replace("'PYTHONPATH=. python3 -m'", "PYTHONPATH=. python3 -m")
    schema = {
        "trajectory_id": case.trajectory_id,
        "trajectory_sha256": case.trajectory_sha256,
        "anchor_prediction_sha256": _stable_sha256(anchor),
        "anchor_ledger_sha256": _stable_sha256(ledger),
        "anchor_checkpoint_sha256": _stable_sha256(checkpoint),
        "anchor_step": anchor["predicted_step"],
        "challenge_status": "no_challenge or challenge",
        "anchor_classification": "critical_root/reasonable_probe/noncritical_predecessor/uncertain",
        "anchor_veto_evidence_step": "integer or null",
        "anchor_veto_evidence_quote": "literal packet substring or null",
        "proposed_prediction": "exact ten-field prediction object or null",
        "anchor_falsifier": "compact literal-evidence explanation",
        "anchor_only_repair_counterfactual": "compact counterfactual",
        "proposal_only_repair_counterfactual": "compact counterfactual",
        "direct_timeline_comparison": "anchor-versus-proposal comparison",
        "search_summary": "why exactly one later proposal exists or none qualifies",
    }
    return f"""\
Run {AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION} stage 2/3: challenger.

{_boundary(manifest=manifest, cohort=cohort, reads=(anchor_file, ledger_file, checkpoint_file), output=output)}

{_CONSERVATIVE_RULES}

The frozen anchor Step is {anchor['predicted_step']}. Inspect the complete
timeline only to falsify or retain this anchor. A proposal must be strictly later.
If no single proposal meets every rule, emit no_challenge with null
veto/proposal fields and explain the search in all five compact text fields.
If challenging, proposed_prediction must be a complete legal ten-field record
with literal evidence owned by the proposed Step/module.

AGENT ERROR TAXONOMY
{taxonomy_prompt()}

Write one JSON array with one object and fields in exactly this order:
{json.dumps(schema, ensure_ascii=False, indent=2)}

After writing, run exactly:
cd {Path(__file__).resolve().parents[2]}
{command}
Complete only when it exits zero and creates {audit}.
"""


def build_arbiter_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    anchor_path: str | Path,
    ledger_path: str | Path,
    checkpoint_path: str | Path,
    challenger_path: str | Path,
    arbiter_path: str | Path,
) -> str:
    manifest, cohort, case = _single_case_paths(
        prediction_manifest_path, cohort_manifest_path
    )
    anchor_file = Path(anchor_path).expanduser().resolve()
    ledger_file = Path(ledger_path).expanduser().resolve()
    checkpoint_file = Path(checkpoint_path).expanduser().resolve()
    challenger_file, challenger_raw = _load_artifact(
        challenger_path, role="challenger"
    )
    anchor, ledger, checkpoint = _validate_anchor_bundle(
        manifest, cohort, anchor_file, ledger_file, checkpoint_file
    )
    challenger = _one_record(challenger_raw, role="challenger")
    _validate_challenger_record(
        challenger,
        case=case,
        anchor=anchor,
        ledger=ledger,
        checkpoint=checkpoint,
        location="challenger[0]",
    )
    output = Path(arbiter_path).expanduser().resolve()
    _assert_safe_path(output, role="arbiter output", is_output=True)
    audit = output.parent / ARBITER_AUDIT_FILENAME
    command = _command(
        (
            "PYTHONPATH=. python3 -m",
            "agentdebug.diagnostics._debate",
            "--compact-validate",
            "arbiter",
            manifest,
            cohort,
            anchor_file,
            ledger_file,
            checkpoint_file,
            challenger_file,
            output,
            audit,
        )
    ).replace("'PYTHONPATH=. python3 -m'", "PYTHONPATH=. python3 -m")
    schema = {
        "trajectory_id": case.trajectory_id,
        "trajectory_sha256": case.trajectory_sha256,
        "anchor_prediction_sha256": _stable_sha256(anchor),
        "challenger_sha256": _stable_sha256(challenger),
        "anchor_step": anchor["predicted_step"],
        "decision": "keep_anchor or accept_challenger",
        "frozen_step": "selected prediction Step",
        "selected_prediction_sha256": "stable JSON hash of exact selected prediction",
        "selected_prediction": "exact unchanged anchor or challenger prediction object",
        "decision_basis": "literal-evidence threshold decision",
        "rejected_alternative_basis": "why the other exact prediction loses",
    }
    return f"""\
Run {AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION} stage 3/3: independent arbiter.

{_boundary(manifest=manifest, cohort=cohort, reads=(anchor_file, ledger_file, checkpoint_file, challenger_file), output=output)}

{_CONSERVATIVE_RULES}

The anchor is the default. Re-read the complete trace and the one frozen
challenger. Accept it only if every anchor-falsification and proposal-
materiality claim is supported by literal chronology. Salience, persistence,
or later position alone never passes. If there is no challenge, keep_anchor.

selected_prediction must be an exact field-for-field copy of the anchor when
keeping it, or the proposed_prediction when accepting. Do not repair, rewrite, or invent a third prediction. Compute selected_prediction_sha256 as stable
sorted compact JSON content hash of that exact object.

Write one JSON array with one object and fields in exactly this order:
{json.dumps(schema, ensure_ascii=False, indent=2)}

After writing, run exactly:
cd {Path(__file__).resolve().parents[2]}
{command}
Complete only when it exits zero and creates {audit}.
"""


def build_agent_judge_luna_gaia_v3_13_task(
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
        prediction.parent / STEP_FREEZE_FILENAME,
        prediction.parent / CHALLENGER_FILENAME,
        prediction.parent / ARBITER_FILENAME,
    )


def run_compact_validation(stage: str, paths: Sequence[str]) -> int:
    try:
        if stage == "challenger" and len(paths) == 7:
            audit = validate_and_write_challenger_audit(*paths)
        elif stage == "arbiter" and len(paths) == 8:
            audit = validate_and_write_arbiter_audit(*paths)
        elif stage == "prediction" and len(paths) == 4:
            audit = validate_and_write_agent_judge_luna_gaia_v3_13_audit(*paths)
        else:
            _fail("invalid_compact_validation_arguments", "stage/path count differs")
    except AgentJudgeValidationError as error:
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
    "AGENT_JUDGE_LUNA_GAIA_V3_13_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_LUNA_GAIA_V3_13_MODEL",
    "AGENT_JUDGE_LUNA_GAIA_V3_13_REASONING_EFFORT",
    "AGENT_JUDGE_LUNA_GAIA_V3_13_VERSION",
    "ANCHOR_CHECKPOINT_AGGREGATE_FILENAME",
    "ANCHOR_LEDGER_AGGREGATE_FILENAME",
    "ANCHOR_PREDICTIONS_FILENAME",
    "ARBITER_FILENAME",
    "ARBITERS_FILENAME",
    "CHALLENGER_FILENAME",
    "CHALLENGERS_FILENAME",
    "build_agent_judge_luna_gaia_v3_13_task",
    "build_anchor_task",
    "build_arbiter_task",
    "build_challenger_task",
    "validate_agent_judge_luna_gaia_v3_13_predictions",
    "validate_and_write_agent_judge_luna_gaia_v3_13_audit",
    "validate_and_write_arbiter_audit",
    "validate_and_write_challenger_audit",
    "validate_arbiter",
    "validate_challenger",
]
