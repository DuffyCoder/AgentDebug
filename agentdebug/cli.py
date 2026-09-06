"""One public command line for the supported AgentDebug method."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Sequence

from .trace.cli import _add_source_arguments, _command_ingest, _command_validate


def _command_analyze(args: argparse.Namespace) -> int:
    from .method import CodexExecutor, analyze

    if not math.isfinite(args.stage_timeout) or args.stage_timeout <= 0:
        raise ValueError("--stage-timeout must be a positive finite number")
    result = analyze(
        prediction_manifest=args.prediction_manifest,
        cohort_manifest=args.cohort_manifest, output_dir=args.output_dir,
        execute=args.execute, max_workers=args.max_workers,
        max_attempts=args.max_attempts,
        executor=CodexExecutor(args.codex_binary, args.stage_timeout) if args.execute else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _command_validate_predictions(args: argparse.Namespace) -> int:
    from .method import validate_predictions

    validate_predictions(prediction_manifest=args.prediction_manifest,
                         cohort_manifest=args.cohort_manifest, predictions=args.predictions)
    print(json.dumps({"method": "AgentDebug", "status": "validated"}))
    return 0


def _method_inputs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prediction-manifest", type=Path, required=True,
                        help="Hash-locked, gold-free processed GAIA prediction inputs")
    parser.add_argument("--cohort-manifest", type=Path, required=True,
                        help="Matching ordered GAIA cohort")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentdebug", allow_abbrev=False,
        description="AgentDebug: anchored diagnosis, a single challenger, and conservative arbitration",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text, handler in (
        ("ingest", "Normalize a trace locally (no diagnosis)", _command_ingest),
        ("validate", "Check trace integrity locally", _command_validate),
    ):
        command = commands.add_parser(name, help=help_text, allow_abbrev=False)
        _add_source_arguments(command)
        command.set_defaults(handler=handler)
    analyze = commands.add_parser(
        "analyze", aliases=["run"], allow_abbrev=False,
        help="Prepare or execute the fixed AgentDebug diagnosis method",
        description="Fixed GPT-5.5 / medium; three fresh stages per processed GAIA case. No model calls without --execute.",
    )
    _method_inputs(analyze)
    analyze.add_argument("--output-dir", type=Path, required=True, help="New, nonexistent run directory")
    analyze.add_argument("--execute", action="store_true", help="Start model sessions (may incur charges)")
    analyze.add_argument("--codex-binary", default="codex")
    analyze.add_argument("--stage-timeout", type=float, default=1800.0)
    analyze.add_argument("--max-workers", type=int, choices=range(1, 5), default=4)
    analyze.add_argument("--max-attempts", type=int, choices=(1, 2), default=2)
    analyze.set_defaults(handler=_command_analyze)
    validate = commands.add_parser("validate-predictions", allow_abbrev=False,
                                   help="Audit the complete three-stage prediction bundle without labels")
    _method_inputs(validate)
    validate.add_argument("--predictions", type=Path, required=True)
    validate.set_defaults(handler=_command_validate_predictions)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, TypeError, ValueError, RuntimeError) as error:
        print(f"agentdebug: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
