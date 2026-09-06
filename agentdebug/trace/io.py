"""Public loading and serialization API for canonical traces."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from .artifacts import parse_manifest, parse_task
from .claw_eval import parse_claw_eval_trace
from .integrity import validate_trace
from .models import CanonicalTrace, TraceFragment
from .reconcile import reconcile_trace
from .runtime_v1 import parse_runtime_v1
from .session_v3 import parse_session_v3


def load_trace_bundle(
    session_path: str | Path | None = None,
    runtime_path: str | Path | None = None,
    eval_trace_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    task_path: str | Path | None = None,
    *,
    strict: bool = False,
) -> CanonicalTrace:
    """Load, reconcile, and validate an OpenClaw evidence bundle.

    ``session_path`` is normally the primary source but may be ``None`` when
    only a runtime or Claw-Eval artifact survived.  No source text is truncated
    and no legacy AgentDebug message format is produced.
    """

    if (
        session_path is None
        and runtime_path is None
        and eval_trace_path is None
    ):
        raise ValueError(
            "at least one trajectory source is required: "
            "session_path, runtime_path, or eval_trace_path"
        )

    fragments: list[TraceFragment] = []
    if session_path is not None:
        fragments.append(parse_session_v3(session_path))
    if runtime_path is not None:
        fragments.append(parse_runtime_v1(runtime_path))
    if eval_trace_path is not None:
        fragments.append(parse_claw_eval_trace(eval_trace_path))
    if task_path is not None:
        fragments.append(parse_task(task_path))

    task_id = next(
        (fragment.task_id_hint for fragment in reversed(fragments) if fragment.task_id_hint),
        None,
    )
    if manifest_path is not None:
        fragments.append(
            parse_manifest(
                manifest_path,
                session_path=session_path,
                task_id=task_id,
            )
        )
    trace = reconcile_trace(fragments)
    validate_trace(trace, strict=strict)
    return trace


def save_canonical_trace(
    trace: CanonicalTrace,
    path: str | Path,
    *,
    indent: Optional[int] = 2,
) -> Path:
    """Atomically write a complete canonical trace as UTF-8 JSON."""

    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        trace.to_dict(),
        ensure_ascii=False,
        indent=indent,
        sort_keys=False,
    )
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(payload)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def load_canonical_trace(
    path: str | Path,
    *,
    validate: bool = True,
    strict: bool = False,
) -> CanonicalTrace:
    """Load a previously serialized canonical trace."""

    source = Path(path).expanduser().resolve()
    with source.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("canonical trace JSON must contain an object")
    trace = CanonicalTrace.from_dict(data)
    if validate:
        validate_trace(trace, strict=strict)
    return trace
