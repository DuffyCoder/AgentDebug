#!/usr/bin/env python3
"""Verify saved evidence, archived original sources and the current source mapping."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.maintenance.archive import verified_members


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "configs/reproduction/release.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_release(
    *,
    config_path: Path = DEFAULT_CONFIG,
    release_dir: Path | None = None,
    verify_source_files: bool = True,
    dataset: Path | None = None,
    prediction_manifest: Path | None = None,
    cohort: Path | None = None,
) -> dict[str, Any]:
    layout = _load_json(config_path)
    _require(layout.get("schema_version") == "agentdebug.release-layout.v1", "invalid release layout")
    for key in ("artifact_dir", "snapshot_manifest"):
        candidate = Path(layout[key])
        _require(not candidate.is_absolute() and (ROOT / candidate).resolve().is_relative_to(ROOT),
                 "unsafe release layout path")
    snapshot = dict(verified_members(ROOT / layout["snapshot_manifest"]))
    config = json.loads(snapshot[layout["snapshot_config_path"]])
    bundle = release_dir or ROOT / layout["artifact_dir"]
    manifest_path = bundle / "release-manifest.json"
    manifest = _load_json(manifest_path)

    _require(
        manifest["experiment"] == config["experiment"],
        "release experiment does not match reproduction config",
    )
    checked_files: list[str] = []
    for relative, binding in manifest["files"].items():
        path = bundle / relative
        _require(path.is_file(), f"release artifact is missing: {relative}")
        _require(path.stat().st_size == binding["size_bytes"], f"size mismatch: {relative}")
        _require(_sha256(path) == binding["sha256"], f"SHA-256 mismatch: {relative}")
        checked_files.append(relative)

    if verify_source_files:
        for relative, expected in config["source_files"].items():
            _require(relative in snapshot, f"frozen source file is missing: {relative}")
            _require(hashlib.sha256(snapshot[relative]).hexdigest() == expected,
                     f"frozen source hash mismatch: {relative}")
        from scripts.maintenance.check_layout import verify_protocol_mapping
        verify_protocol_mapping(ROOT, snapshot=snapshot)

    predictions = _load_json(bundle / "predictions.json")
    expected = config["expected_result"]
    _require(isinstance(predictions, list), "predictions.json must be a list")
    _require(
        len(predictions) == expected["prediction_count"],
        "unexpected frozen prediction count",
    )
    trajectory_ids = [row.get("trajectory_id") for row in predictions]
    _require(len(set(trajectory_ids)) == len(trajectory_ids), "duplicate trajectory IDs")

    audit = _load_json(bundle / "prediction-audit.json")
    for field in (
        "gold_free_validation",
        "cohort_order_matches",
        "manifest_order_matches",
        "all_status_success",
        "all_predicted_steps_in_range",
        "all_taxonomy_pairs_valid",
        "all_evidence_quotes_found_in_selected_step_module",
        "all_selected_predictions_exact_copies",
    ):
        _require(audit.get(field) is True, f"prediction audit failed: {field}")
    _require(audit.get("forbidden_read_occurred") is False, "gold isolation failed")

    freeze = _load_json(bundle / "gold-free-freeze-audit.json")
    for field in (
        "all_schema_taxonomy_evidence_validation_passed",
        "all_selected_predictions_exact_anchor_or_challenger_copies",
        "gold_free_validation",
    ):
        _require(freeze.get(field) is True, f"freeze audit failed: {field}")
    _require(freeze.get("case_routing") is False, "case routing must be disabled")
    _require(
        freeze.get("prior_predictions_visible_to_inference") is False,
        "prior predictions were visible to inference",
    )
    _require(freeze.get("smoke_gate_used") is False, "smoke gating must be disabled")

    execution = _load_json(bundle / "execution-summary.json")
    _require(execution.get("failed_cases") == [], "the frozen execution has failed cases")
    attempts = execution.get("stage_attempts")
    _require(isinstance(attempts, list), "execution summary has no stage attempts")
    completed_pairs = {
        (row.get("index"), row.get("stage"))
        for row in attempts
        if row.get("complete") is True
    }
    _require(
        {index for index, _ in completed_pairs} == set(range(1, 51)),
        "not all 50 cases have a completed stage",
    )
    _require(len(completed_pairs) == 150, "expected three completed stages for every case")

    metrics = _load_json(bundle / "scored/metrics.json")
    overall = metrics["metrics"]["by_method"]["agent_judge"]["overall"]
    step = overall["step_exact"]
    _require(step["correct"] == expected["step_exact_correct"], "Step Exact numerator changed")
    _require(
        step["denominator"] == expected["step_exact_denominator"],
        "Step Exact denominator changed",
    )
    _require(step["accuracy"] == expected["step_exact_accuracy"], "Step Exact changed")
    _require(
        overall["failed_prediction_count"] == expected["failed_prediction_count"],
        "failed prediction count changed",
    )

    if cohort is not None:
        _require(_sha256(cohort) == config["cohort"]["file_sha256"], "cohort file hash mismatch")
        cohort_json = _load_json(cohort)
        _require(
            cohort_json.get("cohort_sha256") == config["cohort"]["identity_sha256"],
            "cohort identity mismatch",
        )
    if prediction_manifest is not None:
        _require(
            _sha256(prediction_manifest) == config["prediction_manifest"]["file_sha256"],
            "prediction manifest file hash mismatch",
        )
        prediction_json = _load_json(prediction_manifest)
        _require(
            prediction_json.get("prediction_manifest_sha256")
            == config["prediction_manifest"]["identity_sha256"],
            "prediction manifest identity mismatch",
        )
    if dataset is not None:
        from agentdebug.benchmark.dataset import load_agent_error_bench

        loaded = load_agent_error_bench(dataset)
        _require(
            loaded.dataset_sha256 == config["dataset"]["dataset_sha256"],
            "AgentErrorBench dataset hash mismatch",
        )
        gaia_count = sum(label.environment == "gaia" for label in loaded.labels)
        _require(gaia_count == config["dataset"]["case_count"], "GAIA label count mismatch")

    return {
        "release": config["release_name"],
        "experiment": config["experiment"],
        "verified_artifact_count": len(checked_files),
        "source_hashes_verified": verify_source_files,
        "source_binding_scope": "original snapshot plus declared current protocol relocation",
        "dataset_verified": dataset is not None,
        "prediction_manifest_verified": prediction_manifest is not None,
        "cohort_verified": cohort is not None,
        "step_exact": f"{step['correct']}/{step['denominator']}",
        "accuracy": step["accuracy"],
        "legal_full_run": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--release-dir", type=Path)
    parser.add_argument("--skip-source-hashes", action="store_true")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--prediction-manifest", type=Path)
    parser.add_argument("--cohort", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = verify_release(
        config_path=args.config.resolve(),
        release_dir=args.release_dir.resolve() if args.release_dir else None,
        verify_source_files=not args.skip_source_hashes,
        dataset=args.dataset.resolve() if args.dataset else None,
        prediction_manifest=(
            args.prediction_manifest.resolve() if args.prediction_manifest else None
        ),
        cohort=args.cohort.resolve() if args.cohort else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
