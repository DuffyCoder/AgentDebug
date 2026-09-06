#!/usr/bin/env python3
"""Freeze gold-free inputs for all 50 released AgentErrorBench GAIA traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from agentdebug.benchmark.adapter import adapt_trajectory
from agentdebug.benchmark.prediction_manifest import (
    stable_sha256,
    write_prediction_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
DATASET_MANIFEST_SHA256 = (
    "fa78de42eb1de06e3566555bd8c68f09deaa6930f2b07ac8937ded858cc6ac11"
)
COHORT_NAME = "gaia-paper-v1"
EXPECTED_COUNT = 50
SOURCE_ROOT = ROOT / "data/AgentErrorBench/Original_Failure_Trajectory/GAIA"
DEFAULT_COHORT_PATH = ROOT / "benchmarks/cohorts/gaia-paper-v1.json"
DEFAULT_OUTPUT_DIR = (
    ROOT / "output/gaia-inputs"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze one label-free JudgeView for every released GAIA source "
            "trajectory. This command never opens the Label directory."
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-root", default=str(SOURCE_ROOT))
    parser.add_argument("--cohort-output", default=str(DEFAULT_COHORT_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_once(path: Path, value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise RuntimeError(f"refusing to replace frozen artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def prepare_paper_gaia_inputs(
    *,
    source_root: str | Path,
    cohort_output: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Create a source-only cohort and prediction manifest without labels."""

    sources = Path(source_root).expanduser().resolve()
    cohort_path = Path(cohort_output).expanduser().resolve()
    output_root = Path(output_dir).expanduser().resolve()
    paths = sorted(sources.glob("*.json"), key=lambda path: path.stem)
    if len(paths) != EXPECTED_COUNT or len({path.stem for path in paths}) != EXPECTED_COUNT:
        raise RuntimeError("the released GAIA source directory must contain 50 unique JSON traces")

    entries = []
    traces_and_mappings = []
    for rank, path in enumerate(paths, 1):
        raw_bytes = path.read_bytes()
        trajectory_id = path.stem
        trace, mapping = adapt_trajectory(path, trajectory_id=trajectory_id)
        entries.append(
            {
                "environment": "gaia",
                "trajectory_id": trajectory_id,
                "rank": rank,
                "trajectory_file_sha256": _sha256_bytes(raw_bytes),
            }
        )
        traces_and_mappings.append((trace, mapping))

    cohort_body: dict[str, Any] = {
        "schema_version": "agentdebug.benchmark.paper-release-cohort.v1",
        "cohort_name": COHORT_NAME,
        "dataset_manifest_sha256": DATASET_MANIFEST_SHA256,
        "selection": {
            "algorithm": "all-released-environment-source-files-lexical-id-v1",
            "environment": "gaia",
            "membership_rule": "all 50 JSON files in the released GAIA trajectory directory",
            "ordering_rule": "trajectory_id lexical order",
            "source_only": True,
            "development_cohort": False,
            "paper_comparison_scope": True,
        },
        "trajectory_ids": [entry["trajectory_id"] for entry in entries],
        "entries": entries,
    }
    cohort = dict(cohort_body)
    cohort["cohort_sha256"] = stable_sha256(cohort_body)
    _write_once(cohort_path, cohort)

    prediction_path = output_root / "prediction-manifest.json"
    manifest = write_prediction_manifest(
        traces_and_mappings=traces_and_mappings,
        dataset_manifest_sha256=DATASET_MANIFEST_SHA256,
        cohort_name=COHORT_NAME,
        cohort_sha256=cohort["cohort_sha256"],
        selection_identity={
            "selection_name": COHORT_NAME,
            "algorithm": cohort["selection"]["algorithm"],
            "environment": "gaia",
            "trajectory_ids": cohort["trajectory_ids"],
            "execution_order": "cohort-manifest",
            "expected_count": EXPECTED_COUNT,
            "source_only": True,
        },
        output_path=prediction_path,
    )
    result = {
        "schema_version": "agentdebug.paper-gaia-input-preparation.v1",
        "cohort_name": COHORT_NAME,
        "trajectory_count": EXPECTED_COUNT,
        "dataset_manifest_sha256": DATASET_MANIFEST_SHA256,
        "cohort_path": str(cohort_path),
        "cohort_file_sha256": _sha256_bytes(cohort_path.read_bytes()),
        "cohort_sha256": cohort["cohort_sha256"],
        "prediction_manifest_path": str(prediction_path),
        "prediction_manifest_file_sha256": _sha256_bytes(prediction_path.read_bytes()),
        "prediction_manifest_sha256": manifest["prediction_manifest_sha256"],
        "source_root": str(sources),
        "source_only_preparation": True,
        "label_directory_opened": False,
        "gold_free": True,
        "external_calls": 0,
    }
    _write_once(output_root / "input-preparation.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = prepare_paper_gaia_inputs(
        source_root=args.source_root,
        cohort_output=args.cohort_output,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
