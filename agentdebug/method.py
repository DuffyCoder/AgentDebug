"""The single supported AgentDebug method and its gold-free execution adapter.

Protocol logic is mechanically extracted from the verified source snapshot.
Only module/import paths in generated commands have changed; the historical
bytes and the declared relocation map remain separately verifiable.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from agentdebug.benchmark.shards import create_agent_judge_case_shards
from agentdebug.diagnostics import protocol as _protocol
from agentdebug.diagnostics._contract import AgentJudgeValidationError
from agentdebug.diagnostics._debate import _load_cases

NAME = "AgentDebug"
MODEL = _protocol.AGENT_JUDGE_GAIA_V3_83_MODEL
REASONING_EFFORT = _protocol.AGENT_JUDGE_GAIA_V3_83_REASONING_EFFORT
STAGES = ("anchor", "challenger", "arbiter")
_ANCHOR = _protocol.ANCHOR_PREDICTIONS_FILENAME
_LEDGER = "step-candidates.json"
_CHECKPOINT = "step-freeze.json"
_CHALLENGER = _protocol.CHALLENGER_FILENAME
_ARBITER = _protocol.ARBITER_FILENAME


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class StageRequest:
    """A fresh session must write the requested artifact and its sidecars."""

    stage: str
    attempt: int
    work_dir: Path
    task: str
    artifact_path: Path
    model: str = MODEL
    reasoning_effort: str = REASONING_EFFORT


@dataclass(frozen=True)
class CodexExecutor:
    """Standalone Codex CLI adapter; not a claim of measured backend parity."""

    binary: str = "codex"
    timeout: float = 1800.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError("stage timeout must be a positive finite number")
        if not isinstance(self.binary, str) or not self.binary.strip():
            raise ValueError("Codex binary must be nonempty text")

    def __call__(self, request: StageRequest) -> None:
        command = [
            self.binary, "exec", "--ephemeral", "--ignore-user-config",
            "--skip-git-repo-check", "--sandbox", "workspace-write",
            "--model", MODEL, "-c", f'model_reasoning_effort="{REASONING_EFFORT}"',
            "-c", 'web_search="disabled"', "-C", str(request.work_dir), "--json", "-",
        ]
        environment = dict(os.environ)
        # Frozen validation commands use python3. Resolve it in this installation.
        environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
        with (request.work_dir / "execution.jsonl").open("w", encoding="utf-8") as stdout, \
             (request.work_dir / "execution.stderr").open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(
                command, input=request.task, text=True, cwd=request.work_dir,
                env=environment, stdout=stdout, stderr=stderr,
                timeout=self.timeout, check=False,
            )
        if completed.returncode:
            raise RuntimeError(f"Codex exited with status {completed.returncode}")


def _stage_contract(stage: str, manifest: Path, cohort: Path, directory: Path):
    paths = (manifest, cohort, directory / _ANCHOR, directory / _LEDGER,
             directory / _CHECKPOINT)
    if stage == "anchor":
        artifact = directory / _ANCHOR
        task = _protocol.build_anchor_task(manifest, cohort, artifact)
        validate = lambda: _protocol.validate_and_write_anchor_audit(
            manifest, cohort, artifact, directory / "stage-audit.json")
    elif stage == "challenger":
        artifact = directory / _CHALLENGER
        task = _protocol.build_challenger_task(*paths, artifact)
        validate = lambda: _protocol.validate_and_write_challenger_audit(
            *paths, artifact, directory / "stage-audit.json")
    elif stage == "arbiter":
        artifact = directory / _ARBITER
        task = _protocol.build_arbiter_task(*paths, directory / _CHALLENGER, artifact)
        validate = lambda: _protocol.validate_and_write_arbiter_audit(
            *paths, directory / _CHALLENGER, artifact, directory / "stage-audit.json")
    else:
        raise ValueError("unsupported stage")
    return artifact, task, validate


def _check_hashes(bindings: dict[Path, str]) -> None:
    for path, expected in bindings.items():
        if not path.is_file() or _hash(path) != expected:
            raise RuntimeError(f"immutable input changed: {path.name}")


def _run_case(descriptor, root: Path, executor: Callable[[StageRequest], None],
              max_attempts: int) -> dict[str, Any]:
    case_dir = root / "cases" / f"case-{descriptor.index:03d}"
    manifest, cohort = descriptor.prediction_manifest_path, descriptor.cohort_manifest_path
    frozen: dict[str, Path] = {}
    bindings = {path: _hash(path) for path in (manifest, cohort)}
    attempts = []
    try:
        for stage in STAGES:
            for attempt in range(1, max_attempts + 1):
                directory = case_dir / stage / f"attempt-{attempt:02d}"
                directory.mkdir(parents=True, exist_ok=False)
                for name, source in frozen.items():
                    (directory / name).write_bytes(source.read_bytes())
                copied = {directory / name: _hash(directory / name) for name in frozen}
                artifact, task, validate = _stage_contract(stage, manifest, cohort, directory)
                (directory / "task.md").write_text(task, encoding="utf-8")
                record = {"stage": stage, "attempt": attempt,
                          "task_sha256": hashlib.sha256(task.encode()).hexdigest()}
                try:
                    executor(StageRequest(stage, attempt, directory, task, artifact))
                    _check_hashes({**bindings, **copied})
                    validate()
                except (AgentJudgeValidationError, OSError, RuntimeError,
                        subprocess.TimeoutExpired, ValueError) as error:
                    record.update(status="failed", error=str(error))
                    attempts.append(record)
                    # Mutated inputs are fatal, not a retry with changed evidence.
                    _check_hashes({**bindings, **copied})
                    if attempt == max_attempts:
                        raise RuntimeError(f"{stage} failed after {attempt} attempts") from error
                    continue
                record["status"] = "validated"
                attempts.append(record)
                names = (_ANCHOR, _LEDGER, _CHECKPOINT) if stage == "anchor" else (artifact.name,)
                for name in names:
                    frozen[name] = directory / name
                    bindings[directory / name] = _hash(directory / name)
                break
        return {"index": descriptor.index, "files": frozen, "bindings": bindings}
    finally:
        _write(case_dir / "execution-summary.json", {"attempts": attempts})


def validate_predictions(*, prediction_manifest: str | Path,
                         cohort_manifest: str | Path, predictions: str | Path) -> dict:
    """Validate all three frozen stages, their hashes and exact-copy selection."""
    _validated_inputs(prediction_manifest, cohort_manifest)
    return _protocol.validate_agent_judge_gaia_v3_83_predictions(
        prediction_manifest, cohort_manifest, predictions)


def _validated_inputs(prediction_manifest, cohort_manifest):
    manifest, cohort, cases = _load_cases(prediction_manifest, cohort_manifest)
    entries = _read(cohort).get("entries", [])
    if (not isinstance(entries, list) or len(entries) != len(cases)
            or any(not isinstance(item, dict) or item.get("environment") != "gaia"
                   for item in entries)):
        raise ValueError("AgentDebug diagnosis supports processed AgentErrorBench GAIA inputs only")
    return manifest, cohort, cases


def analyze(*, prediction_manifest: str | Path, cohort_manifest: str | Path,
            output_dir: str | Path, execute: bool = False,
            max_workers: int = 4, max_attempts: int = 2,
            executor: Callable[[StageRequest], None] | None = None) -> dict:
    """Prepare or run the fixed method on gold-free processed GAIA inputs.

    No labels are accepted. Existing output directories are never reused.
    A dry run validates and shards inputs but does not construct a model client.
    """
    if type(execute) is not bool:
        raise ValueError("execute must be an explicit boolean")
    if (type(max_workers) is not int or type(max_attempts) is not int
            or not 1 <= max_workers <= 4 or not 1 <= max_attempts <= 2):
        raise ValueError("workers must be 1..4 and attempts must be 1..2")
    manifest, cohort, cases = _validated_inputs(prediction_manifest, cohort_manifest)
    root = Path(output_dir).expanduser().resolve()
    if root.exists():
        raise ValueError("output directory already exists; choose a new directory")
    root.mkdir(parents=True, exist_ok=False)
    descriptors = create_agent_judge_case_shards(
        prediction_manifest_path=manifest, cohort_manifest_path=cohort,
        output_dir=root / "inputs")
    bindings = {path: _hash(path) for path in (manifest, cohort)}
    selected_executor = executor if executor is not None else CodexExecutor()
    runtime = ({
        "adapter": "codex-cli", "binary": selected_executor.binary,
        "stage_timeout_seconds": selected_executor.timeout,
        "sandbox": "workspace-write", "web_search": "disabled",
        "ephemeral": True, "ignore_user_config": True,
    } if isinstance(selected_executor, CodexExecutor) else {"adapter": "caller-supplied"})
    plan = {
        "method": NAME, "status": "prepared", "model": MODEL,
        "reasoning_effort": REASONING_EFFORT, "stages": list(STAGES),
        "case_count": len(cases), "planned_sessions": len(cases) * 3,
        "max_workers": max_workers, "max_attempts_per_stage": max_attempts,
        "execution_backend": runtime["adapter"], "runtime": runtime,
        "fresh_session_per_stage": True, "labels_used": False,
        "output_dir": str(root),
    }
    _write(root / "run.json", plan)
    # Provenance is deliberately separate from the neutral public method name.
    _write(root / "provenance.json", {
        "implementation": _protocol.AGENT_JUDGE_GAIA_V3_83_VERSION,
        "source_layout": "extracted protocol with relocated executable module paths",
        "execution_adapter_sha256": _hash(Path(__file__)),
        "prediction_manifest_sha256": bindings[manifest],
        "cohort_file_sha256": bindings[cohort],
        "fresh_result_not_inherited_from_published_score": True,
    })
    if not execute:
        return plan
    completed, failures = [], []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_run_case, item, root, selected_executor, max_attempts): item
                   for item in descriptors}
        for future in as_completed(futures):
            try:
                completed.append(future.result())
            except Exception as error:
                failures.append({"case": futures[future].index, "error": str(error)})
    if failures:
        _write(root / "run.json", {**plan, "status": "failed", "failures": failures})
        raise RuntimeError("one or more cases failed; see run.json (no partial score produced)")
    try:
        _check_hashes(bindings)
        for item in completed:
            _check_hashes(item["bindings"])
        return _finalize(root, completed, plan, manifest, cohort)
    except Exception as error:
        _write(root / "run.json", {**plan, "status": "failed", "error": str(error)})
        raise


def _finalize(root, completed, plan, manifest, cohort):
    completed.sort(key=lambda item: item["index"])
    aggregates = {
        _ANCHOR: (_ANCHOR, True),
        _protocol.ANCHOR_LEDGER_AGGREGATE_FILENAME: (_LEDGER, False),
        _protocol.ANCHOR_CHECKPOINT_AGGREGATE_FILENAME: (_CHECKPOINT, False),
        _protocol.CHALLENGERS_FILENAME: (_CHALLENGER, True),
        _protocol.ARBITERS_FILENAME: (_ARBITER, True),
    }
    for destination, (source, is_list) in aggregates.items():
        records = [_read(item["files"][source]) for item in completed]
        _write(root / destination, [record[0] if is_list else record for record in records])
    predictions = [item["selected_prediction"] for item in _read(root / _protocol.ARBITERS_FILENAME)]
    _write(root / "predictions.json", predictions)
    audit = validate_predictions(prediction_manifest=manifest, cohort_manifest=cohort,
                                 predictions=root / "predictions.json")
    _write(root / "prediction-audit.json", audit)
    _write(root / "artifact-hashes.json", {
        path.name: _hash(path) for path in sorted(root.glob("*.json"))
        if path.name != "run.json"
    })
    result = {**plan, "status": "validated", "predictions": str(root / "predictions.json")}
    _write(root / "run.json", result)
    return result


__all__ = ["NAME", "MODEL", "REASONING_EFFORT", "STAGES", "StageRequest",
           "CodexExecutor", "analyze", "validate_predictions"]
