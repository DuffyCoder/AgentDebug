"""Explicit, post-validation GAIA scoring, independent of experimental runners.

The fixed-denominator accounting functions are extracted from the recorded
scorer. The protocol registry and import-time runner mutations are eliminated.
"""
from __future__ import annotations
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

from agentdebug.diagnostics import protocol as selected_protocol
from .dataset import load_agent_error_bench
from .metrics import compute_metrics
from .prediction_manifest import load_prediction_manifest, stable_sha256
from .reporting import write_outputs

AGENT_JUDGE_METHOD = "agent_judge"
PROTOCOL = "AgentDebug"
COHORT_NAME = "gaia-paper-v1"
EXPECTED_COUNT = 50
DATASET_SHA256 = (
    "fa78de42eb1de06e3566555bd8c68f09deaa6930f2b07ac8937ded858cc6ac11"
)
COHORT_SHA256 = (
    "193dea48f9f9cd672215a8bdf4c82ab771836cb3fffe8768468facd5c6870240"
)
COHORT_FILE_SHA256 = (
    "31140b667a479431abf5e0e274752cb9a486ec5f4a9d80b471b617e586b48126"
)
PREDICTION_MANIFEST_SHA256 = (
    "56aa8a2994ae793545b6620c665a945375e48cd6c05a4b9b1afc1f4f2885a3e5"
)
PREDICTION_MANIFEST_FILE_SHA256 = (
    "77815b429514b136d715c5914eee912637a2e942979dd23f7d614aa33ee508cc"
)


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def resolve_agent_judge_protocol(name: str = PROTOCOL):
    if name != PROTOCOL:
        raise ValueError("Only the supported AgentDebug protocol can be scored")
    return SimpleNamespace(
        version=selected_protocol.AGENT_JUDGE_GAIA_V3_83_VERSION,
        model=selected_protocol.AGENT_JUDGE_GAIA_V3_83_MODEL,
        reasoning_effort=selected_protocol.AGENT_JUDGE_GAIA_V3_83_REASONING_EFFORT,
        semantic_topology=("three_fresh_gpt55_sessions_with_exact_v3_20_packet_state_anchor_"
                           "earliest_causal_challenger_and_default_keep_arbiter"),
    )


def validate_agent_judge_run(*, prediction_manifest_path, cohort_manifest_path,
                             predictions_path, audit_path=None, protocol=PROTOCOL):
    resolve_agent_judge_protocol(protocol)
    audit = selected_protocol.validate_agent_judge_gaia_v3_83_predictions(
        prediction_manifest_path, cohort_manifest_path, predictions_path)
    if audit_path is not None:
        _atomic_json(Path(audit_path).expanduser().resolve(), audit)
    return audit


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def validate_paper_gaia_inputs(
    *,
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
) -> dict[str, Any]:
    """Fail closed unless inputs are the exact frozen 50-source release scope."""

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    manifest, cases = load_prediction_manifest(prediction_path)
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    if not isinstance(cohort, dict):
        raise RuntimeError("paper GAIA cohort must be an object")
    body = dict(cohort)
    claimed_hash = body.pop("cohort_sha256", None)
    if claimed_hash != stable_sha256(body):
        raise RuntimeError("paper GAIA cohort content hash is invalid")
    entries = cohort.get("entries")
    trajectory_ids = cohort.get("trajectory_ids")
    case_ids = [case.trajectory_id for case in cases]
    if (
        len(cases) != EXPECTED_COUNT
        or not isinstance(entries, list)
        or not isinstance(trajectory_ids, list)
        or len(entries) != EXPECTED_COUNT
        or len(trajectory_ids) != EXPECTED_COUNT
        or len(set(trajectory_ids)) != EXPECTED_COUNT
        or case_ids != trajectory_ids
        or any(
            not isinstance(entry, dict)
            or entry.get("environment") != "gaia"
            or entry.get("trajectory_id") != trajectory_ids[index]
            or entry.get("rank") != index + 1
            for index, entry in enumerate(entries)
        )
    ):
        raise RuntimeError("paper GAIA inputs must contain all 50 ordered cases")
    expected = {
        "cohort_name": COHORT_NAME,
        "dataset_manifest_sha256": DATASET_SHA256,
        "cohort_sha256": COHORT_SHA256,
        "prediction_manifest_sha256": PREDICTION_MANIFEST_SHA256,
    }
    observed = {
        "cohort_name": manifest.get("cohort_name"),
        "dataset_manifest_sha256": manifest.get("dataset_manifest_sha256"),
        "cohort_sha256": manifest.get("cohort_sha256"),
        "prediction_manifest_sha256": manifest.get(
            "prediction_manifest_sha256"
        ),
    }
    if observed != expected:
        raise RuntimeError("prediction inputs are not the frozen paper GAIA identity")
    if (
        cohort.get("cohort_name") != COHORT_NAME
        or cohort.get("dataset_manifest_sha256") != DATASET_SHA256
        or claimed_hash != COHORT_SHA256
        or _file_sha256(cohort_path) != COHORT_FILE_SHA256
        or _file_sha256(prediction_path) != PREDICTION_MANIFEST_FILE_SHA256
    ):
        raise RuntimeError("paper GAIA input file identity is invalid")
    return {
        **expected,
        "trajectory_count": EXPECTED_COUNT,
        "environment_counts": {"gaia": EXPECTED_COUNT},
        "paper_release_label_count": EXPECTED_COUNT,
        "source_only_membership": True,
        "paper_comparison_scope": True,
        "development_cohort": False,
        "generalization_claim_permitted": False,
        "prediction_manifest_path": str(prediction_path),
        "cohort_manifest_path": str(cohort_path),
    }


def paper_gaia_prediction_diagnostics(
    *,
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    protocol: str = PROTOCOL,
) -> dict[str, Any]:
    """Strictly validate the complete 50-record prediction artifact."""

    validate_paper_gaia_inputs(
        prediction_manifest_path=prediction_manifest_path,
        cohort_manifest_path=cohort_manifest_path,
    )
    audit = validate_agent_judge_run(
        prediction_manifest_path=prediction_manifest_path,
        cohort_manifest_path=cohort_manifest_path,
        predictions_path=predictions_path,
        protocol=protocol,
    )
    predictions = json.loads(Path(predictions_path).read_text(encoding="utf-8"))
    if not isinstance(predictions, list) or len(predictions) != EXPECTED_COUNT:
        raise RuntimeError("paper GAIA predictions must contain exactly 50 records")
    return {
        "scope": COHORT_NAME,
        "trajectory_count": len(predictions),
        "strict_validation_passed": True,
        "paper_release_label_count": EXPECTED_COUNT,
        "generalization_claim_permitted": False,
        "module_counts": dict(
            sorted(Counter(row["predicted_module"] for row in predictions).items())
        ),
        "error_type_counts": dict(
            sorted(
                Counter(row["predicted_error_type"] for row in predictions).items()
            )
        ),
        "validation_audit": audit,
    }


def _score_record(
    *,
    label: Any,
    case: Any,
    prediction: Mapping[str, Any],
    manifest_sha256: str,
    mapping_valid: bool,
    runtime_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    protocol = resolve_agent_judge_protocol(PROTOCOL)
    runtime = dict(runtime_metadata or {})
    predicted_step = int(prediction["predicted_step"])
    predicted_module = str(prediction["predicted_module"])
    predicted_error_type = str(prediction["predicted_error_type"])
    predicted_event_id = case.event_for_step(predicted_step)
    if predicted_event_id is None:
        raise RuntimeError("validated paper GAIA prediction has no event mapping")
    step_exact = predicted_step == label.original_step
    step_module_exact = step_exact and predicted_module == label.module
    all_correct = (
        None
        if label.error_type is None
        else step_module_exact and predicted_error_type == label.error_type
    )
    return {
        "trajectory_id": label.trajectory_id,
        "environment": label.environment,
        "source_llm": label.source_llm,
        "method": AGENT_JUDGE_METHOD,
        "status": "success",
        "failure_stage": None,
        "failure_code": None,
        "failure_message": None,
        "gold_step": label.original_step,
        "gold_event_id": case.event_for_step(label.original_step),
        "gold_raw_module": label.raw_module,
        "gold_module": label.module,
        "gold_raw_error_type": label.raw_error_type,
        "gold_error_type": label.error_type,
        "gold_normalization_notes": list(label.normalization_notes),
        "predicted_step": predicted_step,
        "judge_reported_step": predicted_step,
        "predicted_event_id": predicted_event_id,
        "predicted_module": predicted_module,
        "predicted_error_type": predicted_error_type,
        "step_exact": step_exact,
        "step_module_exact": step_module_exact,
        "all_correct": all_correct,
        "evidence_quote": prediction["evidence_quote"],
        "root_cause": prediction["root_cause"],
        "causal_summary": prediction["causal_summary"],
        "rejected_adjacent_owner": prediction["rejected_adjacent_owner"],
        "specialist_finding_count": None,
        "specialist_counts_by_module": None,
        "evidence_validation_issues": [],
        "latency_seconds": None,
        "cache_hit": False,
        "trajectory_sha256": case.trajectory_sha256,
        "prediction_manifest_sha256": manifest_sha256,
        "agent_judge_version": protocol.version,
        "prompt_version": protocol.version,
        "pipeline_version": protocol.version,
        "model": protocol.model,
        "reasoning_effort": protocol.reasoning_effort,
        "temperature": runtime.get("temperature"),
        "provider": runtime.get("provider", "codex-subagent"),
        "endpoint": runtime.get("endpoint", "orchestrator"),
        "released_gold_step_has_public_event_mapping": mapping_valid,
    }


def score_paper_gaia50(
    *,
    dataset: Path,
    prediction_manifest: Path,
    cohort_manifest: Path,
    predictions: Path,
    run_dir: Path,
    runtime_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit before gold load, then score all 50 labels by released step."""

    started = datetime.now(timezone.utc)
    pre_gold_audit = validate_agent_judge_run(
        prediction_manifest_path=prediction_manifest,
        cohort_manifest_path=cohort_manifest,
        predictions_path=predictions,
        audit_path=run_dir / "prediction-audit.json",
        protocol=PROTOCOL,
    )
    validate_paper_gaia_inputs(
        prediction_manifest_path=prediction_manifest,
        cohort_manifest_path=cohort_manifest,
    )
    manifest, cases = load_prediction_manifest(prediction_manifest)
    raw_predictions = json.loads(predictions.read_text(encoding="utf-8"))
    if not isinstance(raw_predictions, list) or len(raw_predictions) != EXPECTED_COUNT:
        raise RuntimeError("paper GAIA score input must contain 50 audited predictions")

    # Gold-bearing release data is first opened below, after the strict audit.
    loaded_dataset = load_agent_error_bench(dataset)
    labels = [label for label in loaded_dataset.labels if label.environment == "gaia"]
    labels_by_id = {label.trajectory_id: label for label in labels}
    case_ids = [case.trajectory_id for case in cases]
    if (
        len(labels) != EXPECTED_COUNT
        or len(labels_by_id) != EXPECTED_COUNT
        or set(labels_by_id) != set(case_ids)
        or loaded_dataset.dataset_sha256 != DATASET_SHA256
    ):
        raise RuntimeError("released GAIA gold identity does not match frozen inputs")
    unmappable_ids = {
        str(row.get("trajectory_id"))
        for row in loaded_dataset.conversion_failures
        if row.get("environment") == "gaia"
    }
    runtime = dict(runtime_metadata or {})
    scored = [
        _score_record(
            label=labels_by_id[case.trajectory_id],
            case=case,
            prediction=prediction,
            manifest_sha256=manifest["prediction_manifest_sha256"],
            mapping_valid=case.trajectory_id not in unmappable_ids,
            runtime_metadata=runtime,
        )
        for case, prediction in zip(cases, raw_predictions, strict=True)
    ]
    metrics = compute_metrics(
        scored,
        phase1_gold_available=loaded_dataset.phase1_gold_available,
        phase1_gold_reason=loaded_dataset.phase1_gold_reason,
    )
    evaluation_ready_rows = [
        row for row in scored if row["trajectory_id"] not in unmappable_ids
    ]
    subset = compute_metrics(
        evaluation_ready_rows,
        phase1_gold_available=loaded_dataset.phase1_gold_available,
        phase1_gold_reason=loaded_dataset.phase1_gold_reason,
    )
    metrics["paper_release_accounting"] = {
        "released_gaia_label_count": EXPECTED_COUNT,
        "prediction_count": len(scored),
        "strictly_audited_prediction_count": len(scored),
        "released_gold_step_mappable_count": len(evaluation_ready_rows),
        "released_gold_step_unmappable_count": len(unmappable_ids),
        "released_gold_step_unmappable_trajectory_ids": sorted(unmappable_ids),
        "denominator_policy": (
            "All 50 released GAIA labels remain in the paper-comparison "
            "denominator. A released gold step outside the public source-step "
            "mapping cannot receive Step credit."
        ),
        "evaluation_ready_49_overall": subset["by_method"][AGENT_JUDGE_METHOD][
            "overall"
        ],
    }
    finished = datetime.now(timezone.utc)
    protocol = resolve_agent_judge_protocol(PROTOCOL)
    run_metadata = {
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": (finished - started).total_seconds(),
        "experiment": protocol.version,
        "method": AGENT_JUDGE_METHOD,
        "semantic_topology": protocol.semantic_topology,
        "provider": runtime.get("provider", "codex-subagent"),
        "endpoint": runtime.get("endpoint", "orchestrator"),
        "model": protocol.model,
        "reasoning_effort": protocol.reasoning_effort,
        "temperature": runtime.get("temperature"),
        "max_output_tokens": None,
        "timeout": None,
        "max_retries": runtime.get("max_retries"),
        "workers": runtime.get("workers", 1),
        "execution_order": "cohort",
        "prompt_versions": {"agent_judge": protocol.version},
        "production_two_stage_pipeline_version": protocol.version,
        "evidence_validation_version": protocol.version,
        "transport_policy_version": runtime.get(
            "transport_policy_version", "codex-orchestrator-subagent"
        ),
        "judge_input_count": len(scored),
        "metric_cohort_count": EXPECTED_COUNT,
        "selected_trajectory_ids": case_ids,
        "selection": {
            "cohort": COHORT_NAME,
            "cohort_manifest_path": str(cohort_manifest),
            "cohort_sha256": COHORT_SHA256,
            "paper_release_scope": True,
        },
        "gold_isolation": {
            "raw_artifacts_validated_before_dataset_load": True,
            "prediction_process_received_gold": False,
            "prediction_manifest_path": str(prediction_manifest),
            "unscored_predictions_path": str(predictions),
            "prediction_audit": pre_gold_audit,
        },
        "paper_release_accounting": metrics["paper_release_accounting"],
    }
    artifacts = write_outputs(
        output_dir=run_dir / "scored",
        dataset=loaded_dataset,
        predictions=scored,
        metrics=metrics,
        run_metadata=run_metadata,
    )
    policy_path = run_dir / "scored" / "paper-release-score-policy.json"
    _atomic_json(
        policy_path,
        metrics["paper_release_accounting"],
    )
    artifacts["paper_release_score_policy"] = str(policy_path)
    summary = {
        "returncode": 0,
        "artifacts": artifacts,
        "paper_release_accounting": metrics["paper_release_accounting"],
        "stdout_sha256": hashlib.sha256(
            json.dumps(artifacts, sort_keys=True).encode()
        ).hexdigest(),
        "stderr_sha256": hashlib.sha256(b"").hexdigest(),
    }
    _atomic_json(run_dir / "score-stdout.json", summary)
    _atomic_text(run_dir / "score-stderr.log", "")
    return summary
