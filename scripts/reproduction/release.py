"""Version-neutral commands for the single supported AgentDebug release."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path

from scripts.reproduction.verify import ROOT, verify_release


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="Verify frozen result and implementation hashes")
    prepare = commands.add_parser("prepare", help="Build gold-free GAIA inputs from licensed trajectories")
    prepare.add_argument("--source-root", type=Path, required=True)
    prepare.add_argument("--output-dir", type=Path, default=ROOT / "output/gaia-inputs")
    prepare.add_argument("--cohort", type=Path, default=ROOT / "benchmarks/cohorts/gaia-paper-v1.json")
    rescore = commands.add_parser("rescore", help="Recompute the saved release result without model calls")
    score = commands.add_parser("score", help="Score a new, validated full-cohort AgentDebug run")
    score.add_argument("--run-dir", type=Path, required=True)
    for sub in (verify, rescore, score):
        required = sub is not verify
        sub.add_argument("--dataset", type=Path, required=required)
        sub.add_argument("--prediction-manifest", type=Path, required=required)
        sub.add_argument("--cohort", type=Path, default=ROOT / "benchmarks/cohorts/gaia-paper-v1.json")
        if required:
            sub.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "verify":
        result = verify_release(dataset=args.dataset, prediction_manifest=args.prediction_manifest,
                                cohort=args.cohort)
        print(json.dumps({"method": "AgentDebug", **{key: value for key, value in result.items()
                          if key not in {"release", "experiment"}}}, indent=2))
        return 0
    if args.output_dir.exists():
        raise ValueError("output directory already exists; choose a new directory")
    if args.command == "prepare":
        from agentdebug.benchmark.preparation import main as prepare_main
        with contextlib.redirect_stdout(io.StringIO()):
            result = prepare_main(["--source-root", str(args.source_root),
                "--cohort-output", str(args.cohort), "--output-dir", str(args.output_dir)])
        print(json.dumps({"status": "prepared", "output_dir": str(args.output_dir)}))
        return result
    if args.command == "rescore":
        from scripts.reproduction.rescore import main as rescore_main
        with contextlib.redirect_stdout(io.StringIO()):
            result = rescore_main(["--dataset", str(args.dataset), "--prediction-manifest",
                str(args.prediction_manifest), "--cohort", str(args.cohort),
                "--output-dir", str(args.output_dir)])
        print(json.dumps({"method": "AgentDebug", "step_exact": "26/50",
                          "output_dir": str(args.output_dir)}))
        return result
    from agentdebug.method import validate_predictions
    from agentdebug.benchmark.scoring import score_paper_gaia50

    run_dir = args.run_dir.resolve()
    run = json.loads((run_dir / "run.json").read_text())
    if run.get("method") != "AgentDebug" or run.get("status") != "validated":
        raise ValueError("score requires a complete, validated AgentDebug run")
    predictions = run_dir / "predictions.json"
    # Finish all gold-free checks before the existing scorer opens labels.
    validate_predictions(prediction_manifest=args.prediction_manifest,
                         cohort_manifest=args.cohort, predictions=predictions)
    score_paper_gaia50(dataset=args.dataset.resolve(),
        prediction_manifest=args.prediction_manifest.resolve(), cohort_manifest=args.cohort.resolve(),
        predictions=predictions, run_dir=args.output_dir.resolve(),
        runtime_metadata={"provider": run["execution_backend"], "endpoint": "offline-score",
                          "workers": run["max_workers"], "max_retries": run["max_attempts_per_stage"] - 1})
    metrics = json.loads((args.output_dir / "scored/metrics.json").read_text())
    print(json.dumps({"method": "AgentDebug", "metrics": metrics["metrics"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
