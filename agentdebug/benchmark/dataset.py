"""Load and audit the real AgentErrorBench release schema."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from agentdebug.diagnostics.taxonomy import (
    AgentModule,
    ErrorType,
    is_valid_classification,
)
from agentdebug.trace._common import sha256_bytes

from .adapter import AdapterError, adapt_trajectory, validate_conversion
from .models import BenchmarkDataset, BenchmarkExample, GoldLabel


LABEL_FILES = {
    "alfworld_labels.json": "alfworld",
    "gaia_labels.json": "gaia",
    "webshop_labels.json": "webshop",
}
NORMALIZATION_RULES = [
    "Preserve raw_module and raw_error_type on every GoldLabel.",
    "Trim surrounding whitespace and lowercase module/error-type spelling.",
    "Map release module alias 'plan' to taxonomy module 'planning'.",
    "Do not infer an error type when failure_type is empty or not a taxonomy value.",
    "In particular, preserve 'plan_inefficient' as raw release data and mark "
    "its All Correct gold type unscorable rather than rewriting its meaning.",
]


class DatasetSchemaError(ValueError):
    """The release does not match the inspected AgentErrorBench schema."""


def _normalize_module(value: str) -> tuple[str | None, list[str]]:
    raw = value
    normalized = raw.strip().casefold()
    notes: list[str] = []
    if normalized != raw:
        notes.append("module_trim_or_case_normalization")
    if normalized == "plan":
        normalized = "planning"
        notes.append("module_alias_plan_to_planning")
    try:
        return AgentModule(normalized).value, notes
    except ValueError:
        notes.append("unknown_module")
        return None, notes


def _normalize_error_type(value: str) -> tuple[str | None, list[str]]:
    raw = value
    normalized = raw.strip().casefold()
    notes: list[str] = []
    if normalized != raw:
        notes.append("error_type_trim_or_case_normalization")
    if not normalized:
        notes.append("empty_release_error_type")
        return None, notes
    try:
        return ErrorType(normalized).value, notes
    except ValueError:
        notes.append("unknown_error_type")
        return None, notes


def _parse_label(
    row: Any,
    *,
    environment: str,
    label_path: Path,
    index: int,
) -> GoldLabel:
    location = f"{label_path.name}[{index}]"
    if not isinstance(row, Mapping):
        raise DatasetSchemaError(f"{location} must be an object")
    required = {
        "trajectory_id",
        "LLM",
        "task_type",
        "critical_failure_step",
        "critical_failure_module",
        "step_annotations",
    }
    missing = required - set(row)
    if missing:
        raise DatasetSchemaError(
            f"{location} missing fields: {', '.join(sorted(missing))}"
        )
    trajectory_id = row["trajectory_id"]
    if not isinstance(trajectory_id, str) or not trajectory_id.strip():
        raise DatasetSchemaError(f"{location}.trajectory_id must be text")
    step = row["critical_failure_step"]
    if isinstance(step, bool) or not isinstance(step, int) or step < 1:
        raise DatasetSchemaError(
            f"{location}.critical_failure_step must be a positive integer"
        )
    raw_module = row["critical_failure_module"]
    if not isinstance(raw_module, str) or not raw_module.strip():
        raise DatasetSchemaError(
            f"{location}.critical_failure_module must be text"
        )
    annotations = row["step_annotations"]
    if not isinstance(annotations, list) or len(annotations) != 1:
        raise DatasetSchemaError(
            f"{location}.step_annotations must contain exactly one annotation"
        )
    annotation = annotations[0]
    if not isinstance(annotation, Mapping):
        raise DatasetSchemaError(f"{location}.step_annotations[0] must be an object")
    if annotation.get("step") != step:
        raise DatasetSchemaError(
            f"{location} critical step and annotation step differ"
        )
    module_keys = [key for key in annotation if key != "step"]
    if module_keys != [raw_module]:
        raise DatasetSchemaError(
            f"{location} critical module and nested annotation module differ"
        )
    detail = annotation[raw_module]
    if not isinstance(detail, Mapping):
        raise DatasetSchemaError(
            f"{location}.step_annotations[0].{raw_module} must be an object"
        )
    raw_error_type = detail.get("failure_type")
    reasoning = detail.get("reasoning")
    if not isinstance(raw_error_type, str):
        raise DatasetSchemaError(f"{location} failure_type must be text")
    if not isinstance(reasoning, str):
        raise DatasetSchemaError(f"{location} reasoning must be text")

    module, module_notes = _normalize_module(raw_module)
    error_type, error_notes = _normalize_error_type(raw_error_type)
    notes = [*module_notes, *error_notes]
    if module is not None and error_type is not None:
        if not is_valid_classification(
            AgentModule(module),
            ErrorType(error_type),
        ):
            notes.append("invalid_taxonomy_pair")
            error_type = None

    task_type = str(row["task_type"]).strip().casefold()
    if task_type != environment:
        raise DatasetSchemaError(
            f"{location}.task_type {task_type!r} differs from label file "
            f"environment {environment!r}"
        )
    return GoldLabel(
        trajectory_id=trajectory_id,
        environment=environment,
        source_llm=str(row["LLM"]),
        original_step=step,
        raw_module=raw_module,
        module=module,
        raw_error_type=raw_error_type,
        error_type=error_type,
        reasoning=reasoning,
        label_path=str(label_path),
        normalization_notes=tuple(notes),
    )


def _dataset_digest(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative_path, checksum in sorted(files.items()):
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(checksum.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def load_agent_error_bench(root: str | Path) -> BenchmarkDataset:
    """Load every label and convert every trajectory available under ``root``."""

    dataset_root = Path(root).expanduser().resolve()
    label_root = dataset_root / "Label"
    trajectory_root = dataset_root / "Original_Failure_Trajectory"
    if not label_root.is_dir():
        raise DatasetSchemaError(f"missing AgentErrorBench Label directory: {label_root}")
    if not trajectory_root.is_dir():
        raise DatasetSchemaError(
            "missing AgentErrorBench Original_Failure_Trajectory directory: "
            f"{trajectory_root}"
        )

    labels: list[GoldLabel] = []
    label_checksums: dict[str, str] = {}
    seen_ids: set[str] = set()
    for filename, environment in LABEL_FILES.items():
        path = label_root / filename
        if not path.is_file():
            raise DatasetSchemaError(f"missing required label file: {path}")
        raw_bytes = path.read_bytes()
        label_checksums[str(path.relative_to(dataset_root))] = sha256_bytes(raw_bytes)
        try:
            rows = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise DatasetSchemaError(f"invalid label JSON {path}: {error}")
        if not isinstance(rows, list):
            raise DatasetSchemaError(f"{path} must contain a JSON array")
        for index, row in enumerate(rows):
            label = _parse_label(
                row,
                environment=environment,
                label_path=path,
                index=index,
            )
            if label.trajectory_id in seen_ids:
                raise DatasetSchemaError(
                    f"duplicate trajectory_id in labels: {label.trajectory_id}"
                )
            seen_ids.add(label.trajectory_id)
            labels.append(label)

    paths_by_stem: dict[str, list[Path]] = {}
    trajectory_checksums: dict[str, str] = {}
    for path in sorted(trajectory_root.rglob("*.json")):
        paths_by_stem.setdefault(path.stem, []).append(path)
        trajectory_checksums[str(path.relative_to(dataset_root))] = sha256_bytes(
            path.read_bytes()
        )

    examples: list[BenchmarkExample] = []
    canonical_conversion_count = 0
    unavailable: list[dict[str, Any]] = []
    conversion_failures: list[dict[str, Any]] = []
    for label in labels:
        matching = paths_by_stem.get(label.trajectory_id, [])
        if not matching:
            unavailable.append(
                {
                    "trajectory_id": label.trajectory_id,
                    "environment": label.environment,
                    "reason": "trajectory_file_missing",
                }
            )
            continue
        if len(matching) > 1:
            conversion_failures.append(
                {
                    "trajectory_id": label.trajectory_id,
                    "environment": label.environment,
                    "reason": "duplicate_trajectory_files",
                    "paths": [str(path) for path in matching],
                }
            )
            continue
        path = matching[0]
        try:
            trace, mapping = adapt_trajectory(
                path,
                trajectory_id=label.trajectory_id,
            )
            canonical_conversion_count += 1
            source_document = json.loads(path.read_text(encoding="utf-8"))
            conversion = validate_conversion(
                source_document=source_document,
                trace=trace,
                mapping=mapping,
                gold=label,
            )
        except (AdapterError, OSError, UnicodeError, json.JSONDecodeError) as error:
            conversion_failures.append(
                {
                    "trajectory_id": label.trajectory_id,
                    "environment": label.environment,
                    "reason": "adapter_exception",
                    "error_type": type(error).__name__,
                    "message": str(error),
                    "path": str(path),
                }
            )
            continue
        if not conversion.valid:
            conversion_failures.append(
                {
                    "trajectory_id": label.trajectory_id,
                    "environment": label.environment,
                    "reason": "conversion_integrity_failure",
                    "path": str(path),
                    "conversion": conversion.to_dict(),
                }
            )
            continue
        examples.append(
            BenchmarkExample(
                label=label,
                trajectory_path=path,
                trace=trace,
                mapping=mapping,
                conversion=conversion,
            )
        )

    orphan_paths = sorted(set(paths_by_stem) - seen_ids)
    for stem in orphan_paths:
        conversion_failures.append(
            {
                "trajectory_id": stem,
                "environment": None,
                "reason": "trajectory_has_no_gold_label",
                "paths": [str(path) for path in paths_by_stem[stem]],
            }
        )

    all_checksums = {**label_checksums, **trajectory_checksums}
    dataset_sha = _dataset_digest(all_checksums)
    return BenchmarkDataset(
        root=dataset_root,
        version=f"official-google-drive-unversioned-{dataset_sha[:12]}",
        dataset_sha256=dataset_sha,
        label_file_sha256=label_checksums,
        trajectory_file_sha256=trajectory_checksums,
        labels=labels,
        examples=examples,
        canonical_conversion_count=canonical_conversion_count,
        unavailable=unavailable,
        conversion_failures=conversion_failures,
        phase1_gold_available=False,
        phase1_gold_reason=(
            "The inspected release has exactly one step_annotations record per "
            "trajectory, and it is the same critical_failure_step. It does not "
            "provide exhaustive positive/negative multi-label truth for every "
            "step, so Phase 1 precision/recall/F1 is not computable."
        ),
        normalization_rules=list(NORMALIZATION_RULES),
    )
