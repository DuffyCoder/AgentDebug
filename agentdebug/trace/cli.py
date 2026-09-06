"""Local trace ingestion and integrity commands; no model construction."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

_SOURCE_ARGUMENTS = (
    ("session", "OpenClaw session v3 JSONL"),
    ("runtime_trace", "OpenClaw runtime trajectory JSONL"),
    ("eval_trace", "Claw-Eval trace JSONL"),
    ("manifest", "Evaluation manifest JSONL"),
    ("task", "Task definition YAML or JSON"),
)

def _json_value(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "to_json"):
        rendered = value.to_json()
        return json.loads(rendered) if isinstance(rendered, str) else rendered
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError(f"{type(value).__name__} cannot be serialized as a JSON document")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(_json_value(value), ensure_ascii=False, indent=2) + "\n"
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def _default_output(args: argparse.Namespace, kind: str) -> Path:
    source = next(
        (
            Path(getattr(args, name))
            for name, _ in _SOURCE_ARGUMENTS
            if getattr(args, name) is not None
        ),
        None,
    )
    if source is None:
        raise ValueError("at least one trajectory source path is required")
    return source.with_name(f"{source.stem}.{kind}.json")


def _load_trace(args: argparse.Namespace) -> Any:
    from agentdebug.trace import load_trace_bundle

    return load_trace_bundle(
        session_path=args.session,
        runtime_path=args.runtime_trace,
        eval_trace_path=args.eval_trace,
        manifest_path=args.manifest,
        task_path=args.task,
        strict=False,
    )


def _validate(trace: Any) -> Any:
    from agentdebug.trace import validate_trace

    # Strict-mode control belongs to the CLI so an integrity artifact can still
    # be written before returning a non-zero status.
    return validate_trace(trace, strict=False)


def _normalise_severity(value: Any) -> str:
    if hasattr(value, "value"):
        value = value.value
    return str(value or "").strip().lower()


def _integrity_summary(report: Any) -> dict[str, Any]:
    payload = _json_value(report)
    issues = payload.get("issues", [])
    counts = {"error": 0, "critical": 0, "warning": 0, "info": 0}
    if isinstance(issues, list):
        for issue in issues:
            if not isinstance(issue, Mapping):
                continue
            severity = _normalise_severity(issue.get("severity"))
            if severity in counts:
                counts[severity] += 1

    supplied = payload.get("summary")
    if isinstance(supplied, Mapping):
        for key in counts:
            candidate = supplied.get(key, supplied.get(f"{key}s"))
            if isinstance(candidate, int):
                counts[key] = candidate

    valid = payload.get("valid")
    if not isinstance(valid, bool):
        valid = payload.get("ok")
    status = _normalise_severity(payload.get("status"))
    if status:
        valid = status not in {"fail", "failed", "error", "critical", "invalid"}
    if not isinstance(valid, bool):
        valid = counts["error"] == 0 and counts["critical"] == 0

    return {
        "valid": valid,
        "errors": counts["error"] + counts["critical"],
        "critical": counts["critical"],
        "warnings": counts["warning"],
        "info": counts["info"],
    }


def _integrity_has_errors(report: Any) -> bool:
    return not _integrity_summary(report)["valid"]


def _output_path(args: argparse.Namespace, kind: str) -> Path:
    return args.output or _default_output(args, kind)


def _command_ingest(args: argparse.Namespace) -> int:
    from agentdebug.trace import save_canonical_trace

    trace = _load_trace(args)
    output = _output_path(args, "canonical")
    save_canonical_trace(trace, output)

    integrity = _validate(trace)
    print(f"canonical: {output}")
    if args.strict and _integrity_has_errors(integrity):
        print("ingest: integrity errors found", file=sys.stderr)
        return 2
    return 0


def _command_validate(args: argparse.Namespace) -> int:
    trace = _load_trace(args)
    integrity = _validate(trace)
    output = _output_path(args, "integrity")
    _write_json(output, integrity)
    print(f"integrity: {output}")

    if args.strict and _integrity_has_errors(integrity):
        print("validate: integrity errors found", file=sys.stderr)
        return 2
    return 0


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--session",
        type=Path,
        help=_SOURCE_ARGUMENTS[0][1],
    )
    parser.add_argument(
        "--runtime-trace",
        dest="runtime_trace",
        type=Path,
        help=_SOURCE_ARGUMENTS[1][1],
    )
    parser.add_argument(
        "--eval-trace",
        dest="eval_trace",
        type=Path,
        help=_SOURCE_ARGUMENTS[2][1],
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help=_SOURCE_ARGUMENTS[3][1],
    )
    parser.add_argument(
        "--task",
        type=Path,
        help=_SOURCE_ARGUMENTS[4][1],
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path (defaults beside the first trajectory source)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when integrity contains an error",
    )
