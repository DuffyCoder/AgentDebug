#!/usr/bin/env python3
"""Rescore the saved reference predictions against a verified AgentErrorBench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.reproduction.verify import ROOT, verify_release


CONFIG_PATH = ROOT / "configs/reproduction/release.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--prediction-manifest", type=Path, required=True)
    parser.add_argument(
        "--cohort",
        type=Path,
        default=ROOT / "benchmarks/cohorts/gaia-paper-v1.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    release_dir = ROOT / config["artifact_dir"]
    verification = verify_release(
        config_path=CONFIG_PATH,
        dataset=args.dataset.resolve(),
        prediction_manifest=args.prediction_manifest.resolve(),
        cohort=args.cohort.resolve(),
    )

    from agentdebug.benchmark import scoring as paper

    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise ValueError("output directory already exists; choose a new directory")
    result = paper.score_paper_gaia50(
        dataset=args.dataset.resolve(),
        prediction_manifest=args.prediction_manifest.resolve(),
        cohort_manifest=args.cohort.resolve(),
        predictions=release_dir / "predictions.json",
        run_dir=output_dir,
        runtime_metadata={
            "provider": "frozen-release",
            "endpoint": "offline-rescore",
            "workers": 0,
            "max_retries": 0,
        },
    )
    metrics = json.loads((output_dir / "scored/metrics.json").read_text(encoding="utf-8"))
    step = metrics["metrics"]["by_method"]["agent_judge"]["overall"]["step_exact"]
    saved = json.loads((release_dir / "scored/metrics.json").read_text())
    expected = saved["metrics"]["by_method"]["agent_judge"]["overall"]["step_exact"]
    if (
        step["correct"] != expected["correct"]
        or step["denominator"] != expected["denominator"]
    ):
        raise RuntimeError("offline rescore did not reproduce saved Step Exact")
    print(
        json.dumps(
            {
                "verification": verification,
                "rescore_returncode": result["returncode"],
                "step_exact": step,
                "output_dir": str(output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
