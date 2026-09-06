"""Gold-free environment and single-case sharding for Agent Judge execution.

The benchmark's prediction manifest is the complete semantic input to a judge.
This module can split that input into smaller environment-homogeneous manifests
or one manifest per case, then mechanically restore the resulting predictions
to the original cohort order.  It never loads labels, scores, prior predictions,
or judge output other than the shard files explicitly supplied to a merge API.

Shards are execution artifacts, not official benchmark cohorts.  Every derived
cohort and prediction manifest records its parent lineage and receives a new
content hash.  Both creation and merge are write-once: repeating the exact same
operation is idempotent, while any conflicting on-disk artifact is rejected.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agentdebug.diagnostics._contract import AGENT_JUDGE_PREDICTION_FIELDS

from .prediction_manifest import load_prediction_manifest, stable_sha256


AGENT_JUDGE_SHARD_SCHEMA_VERSION = (
    "agentdebug.benchmark.agent-judge-environment-shard.v1"
)
AGENT_JUDGE_SHARD_SELECTION_ALGORITHM = (
    "parent-cohort-environment-partition-preserve-order-v1"
)
AGENT_JUDGE_CASE_SHARD_SCHEMA_VERSION = (
    "agentdebug.benchmark.agent-judge-case-shard.v1"
)
AGENT_JUDGE_CASE_SHARD_SELECTION_ALGORITHM = (
    "parent-cohort-single-case-preserve-order-v1"
)

_FORBIDDEN_CONTENT_KEYS = {
    "all_correct",
    "confidence",
    "critical_failure_module",
    "critical_failure_step",
    "critical_failure_type",
    "gold_error_type",
    "gold_event_id",
    "gold_module",
    "gold_reasoning",
    "gold_step",
    "score",
    "step_annotations",
    "step_exact",
    "step_module_exact",
}
_FORBIDDEN_INPUT_FILENAMES = {
    "metrics.json",
    "promotion.json",
    "unscored-predictions.jsonl",
}
_SAFE_COMPONENT_RE = re.compile(r"[^a-z0-9]+")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class AgentJudgeShardError(ValueError):
    """A gold-free shard boundary is unsafe or internally inconsistent."""


@dataclass(frozen=True)
class AgentJudgeEnvironmentShard:
    """Immutable identity and paths for one environment shard."""

    index: int
    environment: str
    trajectory_ids: tuple[str, ...]
    cohort_name: str
    cohort_sha256: str
    prediction_manifest_sha256: str
    cohort_manifest_path: Path
    prediction_manifest_path: Path


@dataclass(frozen=True)
class AgentJudgeCaseShard:
    """Immutable identity and paths for one single-case execution shard."""

    index: int
    parent_index: int
    environment: str
    trajectory_id: str
    cohort_name: str
    cohort_sha256: str
    prediction_manifest_sha256: str
    cohort_manifest_path: Path
    prediction_manifest_path: Path

    @property
    def trajectory_ids(self) -> tuple[str, ...]:
        """Expose the one-item case tuple expected by shared record checks."""

        return (self.trajectory_id,)


@dataclass(frozen=True)
class _ShardMaterial:
    descriptor: AgentJudgeEnvironmentShard
    cohort_document: dict[str, Any]
    prediction_manifest: dict[str, Any]


@dataclass(frozen=True)
class _CaseShardMaterial:
    descriptor: AgentJudgeCaseShard
    cohort_document: dict[str, Any]
    prediction_manifest: dict[str, Any]


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise AgentJudgeShardError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_json(path: Path, *, role: str) -> Any:
    _assert_safe_path(path, role=role)
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except AgentJudgeShardError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AgentJudgeShardError(
            f"{role} is missing or invalid JSON: {path}"
        ) from error


def _assert_safe_path(path: Path, *, role: str, output: bool = False) -> None:
    parts = tuple(part.casefold() for part in path.parts)
    name = path.name.casefold()
    forbidden = (
        "label" in parts
        or ".git" in parts
        or any(
            parts[index : index + 2] == ("docs", "experiments")
            for index in range(max(0, len(parts) - 1))
        )
        or name in _FORBIDDEN_INPUT_FILENAMES
        or name.startswith("scored")
        or name.startswith("per-example")
        or "case-study" in name
        or "comparison" in name
    )
    if forbidden:
        raise AgentJudgeShardError(
            f"{role} is covered by the Agent Judge gold-isolation denylist"
        )
    if not output and not path.is_file():
        raise AgentJudgeShardError(f"{role} does not exist: {path}")


def _assert_gold_free(value: Any, *, location: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).casefold()
            if normalized in _FORBIDDEN_CONTENT_KEYS or normalized.startswith(
                "gold_"
            ):
                raise AgentJudgeShardError(
                    f"{location} contains forbidden gold/scored field {key!r}"
                )
            _assert_gold_free(item, location=f"{location}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_gold_free(item, location=f"{location}[{index}]")


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _preflight_write_once(path: Path, text: str, *, role: str) -> bool:
    _assert_safe_path(path, role=role, output=True)
    if not path.exists():
        return True
    if not path.is_file():
        raise AgentJudgeShardError(f"existing {role} is not a file: {path}")
    try:
        existing = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise AgentJudgeShardError(f"existing {role} is unreadable: {path}") from error
    if existing != text:
        raise AgentJudgeShardError(
            f"existing {role} conflicts with the frozen shard artifact: {path}"
        )
    return False


def _write_once_many(items: Sequence[tuple[Path, str, str]]) -> None:
    """Preflight every item before writing any missing artifact."""

    missing = [
        (path, text)
        for path, text, role in items
        if _preflight_write_once(path, text, role=role)
    ]
    for path, text in missing:
        _atomic_text(path, text)


def _load_public_cohort(path: Path) -> dict[str, Any]:
    value = _load_json(path, role="full cohort manifest")
    if not isinstance(value, dict):
        raise AgentJudgeShardError("full cohort manifest must be a JSON object")
    _assert_gold_free(value, location="full cohort manifest")
    required = {
        "cohort_name",
        "cohort_sha256",
        "dataset_manifest_sha256",
        "trajectory_ids",
        "entries",
    }
    if not required.issubset(value):
        raise AgentJudgeShardError(
            "full cohort manifest is missing public identity or environment entries"
        )
    for key in ("cohort_name", "cohort_sha256", "dataset_manifest_sha256"):
        if not isinstance(value[key], str) or not value[key]:
            raise AgentJudgeShardError(f"full cohort manifest {key} is invalid")
    body = dict(value)
    claimed_sha256 = body.pop("cohort_sha256")
    if claimed_sha256 != stable_sha256(body):
        raise AgentJudgeShardError("full cohort manifest content hash is invalid")

    trajectory_ids = value["trajectory_ids"]
    entries = value["entries"]
    if (
        not isinstance(trajectory_ids, list)
        or not trajectory_ids
        or any(not isinstance(item, str) or not item for item in trajectory_ids)
        or len(set(trajectory_ids)) != len(trajectory_ids)
    ):
        raise AgentJudgeShardError("full cohort trajectory order is invalid")
    if not isinstance(entries, list) or len(entries) != len(trajectory_ids):
        raise AgentJudgeShardError(
            "full cohort entries do not align with trajectory_ids"
        )
    for index, (trajectory_id, entry) in enumerate(
        zip(trajectory_ids, entries, strict=True)
    ):
        if not isinstance(entry, Mapping):
            raise AgentJudgeShardError(f"full cohort entries[{index}] is not an object")
        if entry.get("trajectory_id") != trajectory_id:
            raise AgentJudgeShardError(
                f"full cohort entries[{index}] does not match trajectory order"
            )
        environment = entry.get("environment")
        if not isinstance(environment, str) or not environment.strip():
            raise AgentJudgeShardError(
                f"full cohort entries[{index}].environment is invalid"
            )
    return value


def _load_full_inputs(
    prediction_manifest_path: Path,
    cohort_manifest_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    # The unique-key parse closes an ambiguity that the shared loader otherwise
    # cannot observe after JSON object construction.
    raw_manifest = _load_json(
        prediction_manifest_path,
        role="full prediction manifest",
    )
    _assert_gold_free(raw_manifest, location="full prediction manifest")
    try:
        manifest, cases = load_prediction_manifest(prediction_manifest_path)
    except (OSError, TypeError, ValueError) as error:
        raise AgentJudgeShardError(
            f"full prediction manifest is invalid: {error}"
        ) from error
    cohort = _load_public_cohort(cohort_manifest_path)
    case_ids = [case.trajectory_id for case in cases]
    if case_ids != cohort["trajectory_ids"]:
        raise AgentJudgeShardError(
            "full prediction manifest and cohort case order differ"
        )
    if (
        manifest["dataset_manifest_sha256"]
        != cohort["dataset_manifest_sha256"]
        or manifest["cohort_name"] != cohort["cohort_name"]
        or manifest["cohort_sha256"] != cohort["cohort_sha256"]
    ):
        raise AgentJudgeShardError(
            "full prediction manifest and cohort lineage differ"
        )
    for case in cases:
        if _SHA256_RE.fullmatch(case.trajectory_sha256) is None:
            raise AgentJudgeShardError(
                f"full prediction manifest has an invalid trajectory SHA-256 "
                f"for {case.trajectory_id!r}"
            )
    return manifest, cohort


def _safe_environment_component(environment: str) -> str:
    normalized = _SAFE_COMPONENT_RE.sub("-", environment.casefold()).strip("-")
    return (normalized or "environment")[:48]


def _environment_groups(cohort: Mapping[str, Any]) -> list[tuple[str, list[int]]]:
    positions: dict[str, list[int]] = {}
    for index, entry in enumerate(cohort["entries"]):
        environment = entry["environment"]
        positions.setdefault(environment, []).append(index)
    return list(positions.items())


def _build_shard_materials(
    *,
    manifest: Mapping[str, Any],
    cohort: Mapping[str, Any],
    output_dir: Path,
) -> list[_ShardMaterial]:
    materials: list[_ShardMaterial] = []
    for shard_index, (environment, positions) in enumerate(
        _environment_groups(cohort),
        1,
    ):
        environment_hash = stable_sha256(environment)[:8]
        component = _safe_environment_component(environment)
        shard_key = f"{shard_index:02d}-{component}-{environment_hash}"
        cohort_name = f"{cohort['cohort_name']}--agent-judge-env-{shard_key}"
        trajectory_ids = tuple(cohort["trajectory_ids"][index] for index in positions)
        cohort_entries = [
            {
                "trajectory_id": cohort["trajectory_ids"][index],
                "environment": environment,
                "parent_cohort_index": index,
            }
            for index in positions
        ]
        cohort_body: dict[str, Any] = {
            "schema_version": AGENT_JUDGE_SHARD_SCHEMA_VERSION,
            "cohort_name": cohort_name,
            "dataset_manifest_sha256": cohort["dataset_manifest_sha256"],
            "parent_lineage": {
                "cohort_name": cohort["cohort_name"],
                "cohort_sha256": cohort["cohort_sha256"],
                "prediction_manifest_sha256": manifest[
                    "prediction_manifest_sha256"
                ],
            },
            "partition": {
                "algorithm": AGENT_JUDGE_SHARD_SELECTION_ALGORITHM,
                "shard_index": shard_index,
                "environment": environment,
                "parent_cohort_indices": positions,
            },
            "trajectory_ids": list(trajectory_ids),
            "entries": cohort_entries,
        }
        cohort_document = dict(cohort_body)
        cohort_document["cohort_sha256"] = stable_sha256(cohort_body)

        shard_entries = [manifest["entries"][index] for index in positions]
        manifest_body: dict[str, Any] = {
            "schema_version": manifest["schema_version"],
            "adapter_version": manifest["adapter_version"],
            "judge_view_version": manifest["judge_view_version"],
            "dataset_manifest_sha256": manifest["dataset_manifest_sha256"],
            "cohort_name": cohort_name,
            "cohort_sha256": cohort_document["cohort_sha256"],
            "selection_identity": {
                "algorithm": AGENT_JUDGE_SHARD_SELECTION_ALGORITHM,
                "parent_cohort_name": cohort["cohort_name"],
                "parent_cohort_sha256": cohort["cohort_sha256"],
                "parent_prediction_manifest_sha256": manifest[
                    "prediction_manifest_sha256"
                ],
                "shard_index": shard_index,
                "environment": environment,
                "trajectory_ids": list(trajectory_ids),
                "execution_order": "parent-cohort-order",
                "expected_count": len(trajectory_ids),
            },
            "entry_count": len(shard_entries),
            "entries": shard_entries,
        }
        shard_manifest = dict(manifest_body)
        shard_manifest["prediction_manifest_sha256"] = stable_sha256(
            manifest_body
        )
        _assert_gold_free(cohort_document, location=f"shard {shard_index} cohort")
        _assert_gold_free(shard_manifest, location=f"shard {shard_index} manifest")

        shard_dir = output_dir / f"shard-{shard_key}"
        descriptor = AgentJudgeEnvironmentShard(
            index=shard_index,
            environment=environment,
            trajectory_ids=trajectory_ids,
            cohort_name=cohort_name,
            cohort_sha256=cohort_document["cohort_sha256"],
            prediction_manifest_sha256=shard_manifest[
                "prediction_manifest_sha256"
            ],
            cohort_manifest_path=(shard_dir / "cohort.json").resolve(),
            prediction_manifest_path=(
                shard_dir / "prediction-manifest.json"
            ).resolve(),
        )
        materials.append(
            _ShardMaterial(
                descriptor=descriptor,
                cohort_document=cohort_document,
                prediction_manifest=shard_manifest,
            )
        )
    return materials


def _build_case_shard_materials(
    *,
    manifest: Mapping[str, Any],
    cohort: Mapping[str, Any],
    output_dir: Path,
) -> list[_CaseShardMaterial]:
    materials: list[_CaseShardMaterial] = []
    for parent_index, (trajectory_id, cohort_entry, manifest_entry) in enumerate(
        zip(
            cohort["trajectory_ids"],
            cohort["entries"],
            manifest["entries"],
            strict=True,
        )
    ):
        shard_index = parent_index + 1
        environment = cohort_entry["environment"]
        environment_component = _safe_environment_component(environment)
        trajectory_hash = stable_sha256(trajectory_id)[:8]
        shard_key = f"{shard_index:03d}-{environment_component}-{trajectory_hash}"
        cohort_name = f"{cohort['cohort_name']}--agent-judge-case-{shard_key}"

        cohort_body: dict[str, Any] = {
            "schema_version": AGENT_JUDGE_CASE_SHARD_SCHEMA_VERSION,
            "cohort_name": cohort_name,
            "dataset_manifest_sha256": cohort["dataset_manifest_sha256"],
            "parent_lineage": {
                "cohort_name": cohort["cohort_name"],
                "cohort_sha256": cohort["cohort_sha256"],
                "prediction_manifest_sha256": manifest[
                    "prediction_manifest_sha256"
                ],
            },
            "partition": {
                "algorithm": AGENT_JUDGE_CASE_SHARD_SELECTION_ALGORITHM,
                "shard_index": shard_index,
                "parent_cohort_index": parent_index,
                "environment": environment,
                "trajectory_id": trajectory_id,
            },
            "trajectory_ids": [trajectory_id],
            "entries": [
                {
                    "trajectory_id": trajectory_id,
                    "environment": environment,
                    "parent_cohort_index": parent_index,
                }
            ],
        }
        cohort_document = dict(cohort_body)
        cohort_document["cohort_sha256"] = stable_sha256(cohort_body)

        manifest_body: dict[str, Any] = {
            "schema_version": manifest["schema_version"],
            "adapter_version": manifest["adapter_version"],
            "judge_view_version": manifest["judge_view_version"],
            "dataset_manifest_sha256": manifest["dataset_manifest_sha256"],
            "cohort_name": cohort_name,
            "cohort_sha256": cohort_document["cohort_sha256"],
            "selection_identity": {
                "algorithm": AGENT_JUDGE_CASE_SHARD_SELECTION_ALGORITHM,
                "parent_cohort_name": cohort["cohort_name"],
                "parent_cohort_sha256": cohort["cohort_sha256"],
                "parent_prediction_manifest_sha256": manifest[
                    "prediction_manifest_sha256"
                ],
                "shard_index": shard_index,
                "parent_cohort_index": parent_index,
                "environment": environment,
                "trajectory_ids": [trajectory_id],
                "execution_order": "parent-cohort-order",
                "expected_count": 1,
            },
            "entry_count": 1,
            "entries": [manifest_entry],
        }
        shard_manifest = dict(manifest_body)
        shard_manifest["prediction_manifest_sha256"] = stable_sha256(
            manifest_body
        )
        _assert_gold_free(
            cohort_document,
            location=f"case shard {shard_index} cohort",
        )
        _assert_gold_free(
            shard_manifest,
            location=f"case shard {shard_index} manifest",
        )

        shard_dir = output_dir / f"case-{shard_key}"
        descriptor = AgentJudgeCaseShard(
            index=shard_index,
            parent_index=parent_index,
            environment=environment,
            trajectory_id=trajectory_id,
            cohort_name=cohort_name,
            cohort_sha256=cohort_document["cohort_sha256"],
            prediction_manifest_sha256=shard_manifest[
                "prediction_manifest_sha256"
            ],
            cohort_manifest_path=(shard_dir / "cohort.json").resolve(),
            prediction_manifest_path=(
                shard_dir / "prediction-manifest.json"
            ).resolve(),
        )
        materials.append(
            _CaseShardMaterial(
                descriptor=descriptor,
                cohort_document=cohort_document,
                prediction_manifest=shard_manifest,
            )
        )
    return materials


def create_agent_judge_environment_shards(
    *,
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    output_dir: str | Path,
) -> tuple[AgentJudgeEnvironmentShard, ...]:
    """Create stable, gold-free execution shards in first-environment order."""

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    root = Path(output_dir).expanduser().resolve()
    _assert_safe_path(root, role="shard output directory", output=True)
    if root.exists() and not root.is_dir():
        raise AgentJudgeShardError("shard output path is not a directory")
    manifest, cohort = _load_full_inputs(prediction_path, cohort_path)
    materials = _build_shard_materials(
        manifest=manifest,
        cohort=cohort,
        output_dir=root,
    )
    writes = [
        item
        for material in materials
        for item in (
            (
                material.descriptor.cohort_manifest_path,
                _json_text(material.cohort_document),
                f"environment {material.descriptor.environment!r} cohort",
            ),
            (
                material.descriptor.prediction_manifest_path,
                _json_text(material.prediction_manifest),
                f"environment {material.descriptor.environment!r} manifest",
            ),
        )
    ]
    _write_once_many(writes)
    return tuple(material.descriptor for material in materials)


def create_agent_judge_case_shards(
    *,
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    output_dir: str | Path,
) -> tuple[AgentJudgeCaseShard, ...]:
    """Create one stable, gold-free execution shard per parent case.

    Shards follow parent cohort order.  Their ``parent_index`` is zero-based,
    while ``index`` is a one-based execution/display index.
    """

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    root = Path(output_dir).expanduser().resolve()
    _assert_safe_path(root, role="case shard output directory", output=True)
    if root.exists() and not root.is_dir():
        raise AgentJudgeShardError("case shard output path is not a directory")
    manifest, cohort = _load_full_inputs(prediction_path, cohort_path)
    materials = _build_case_shard_materials(
        manifest=manifest,
        cohort=cohort,
        output_dir=root,
    )
    writes = [
        item
        for material in materials
        for item in (
            (
                material.descriptor.cohort_manifest_path,
                _json_text(material.cohort_document),
                f"case shard {material.descriptor.index} cohort",
            ),
            (
                material.descriptor.prediction_manifest_path,
                _json_text(material.prediction_manifest),
                f"case shard {material.descriptor.index} manifest",
            ),
        )
    ]
    _write_once_many(writes)
    return tuple(material.descriptor for material in materials)


def _validate_descriptor(
    actual: AgentJudgeEnvironmentShard,
    expected: _ShardMaterial,
) -> None:
    if not isinstance(actual, AgentJudgeEnvironmentShard):
        raise AgentJudgeShardError("shard descriptors have the wrong type")
    identity_fields = (
        "index",
        "environment",
        "trajectory_ids",
        "cohort_name",
        "cohort_sha256",
        "prediction_manifest_sha256",
    )
    for field in identity_fields:
        if getattr(actual, field) != getattr(expected.descriptor, field):
            raise AgentJudgeShardError(
                f"shard descriptor {field} does not match the full inputs"
            )

    cohort_document = _load_json(
        actual.cohort_manifest_path.expanduser().resolve(),
        role=f"shard {actual.index} cohort manifest",
    )
    _assert_gold_free(cohort_document, location=f"shard {actual.index} cohort")
    if cohort_document != expected.cohort_document:
        raise AgentJudgeShardError(
            f"shard {actual.index} cohort identity or order was tampered"
        )

    raw_manifest = _load_json(
        actual.prediction_manifest_path.expanduser().resolve(),
        role=f"shard {actual.index} prediction manifest",
    )
    _assert_gold_free(raw_manifest, location=f"shard {actual.index} manifest")
    try:
        loaded_manifest, cases = load_prediction_manifest(
            actual.prediction_manifest_path
        )
    except (OSError, TypeError, ValueError) as error:
        raise AgentJudgeShardError(
            f"shard {actual.index} prediction manifest is invalid: {error}"
        ) from error
    if loaded_manifest != expected.prediction_manifest:
        raise AgentJudgeShardError(
            f"shard {actual.index} manifest identity or order was tampered"
        )
    if tuple(case.trajectory_id for case in cases) != actual.trajectory_ids:
        raise AgentJudgeShardError(
            f"shard {actual.index} manifest case order is invalid"
        )


def _validate_case_descriptor(
    actual: AgentJudgeCaseShard,
    expected: _CaseShardMaterial,
) -> None:
    if not isinstance(actual, AgentJudgeCaseShard):
        raise AgentJudgeShardError("case shard descriptors have the wrong type")
    identity_fields = (
        "index",
        "parent_index",
        "environment",
        "trajectory_id",
        "cohort_name",
        "cohort_sha256",
        "prediction_manifest_sha256",
    )
    for field in identity_fields:
        if getattr(actual, field) != getattr(expected.descriptor, field):
            raise AgentJudgeShardError(
                f"case shard descriptor {field} does not match the full inputs"
            )

    cohort_document = _load_json(
        actual.cohort_manifest_path.expanduser().resolve(),
        role=f"case shard {actual.index} cohort manifest",
    )
    _assert_gold_free(
        cohort_document,
        location=f"case shard {actual.index} cohort",
    )
    if cohort_document != expected.cohort_document:
        raise AgentJudgeShardError(
            f"case shard {actual.index} cohort identity was tampered"
        )

    raw_manifest = _load_json(
        actual.prediction_manifest_path.expanduser().resolve(),
        role=f"case shard {actual.index} prediction manifest",
    )
    _assert_gold_free(
        raw_manifest,
        location=f"case shard {actual.index} manifest",
    )
    try:
        loaded_manifest, cases = load_prediction_manifest(
            actual.prediction_manifest_path
        )
    except (OSError, TypeError, ValueError) as error:
        raise AgentJudgeShardError(
            f"case shard {actual.index} prediction manifest is invalid: {error}"
        ) from error
    if loaded_manifest != expected.prediction_manifest:
        raise AgentJudgeShardError(
            f"case shard {actual.index} manifest identity was tampered"
        )
    if tuple(case.trajectory_id for case in cases) != actual.trajectory_ids:
        raise AgentJudgeShardError(
            f"case shard {actual.index} manifest case identity is invalid"
        )


def _load_prediction_records(
    path: Path,
    *,
    descriptor: AgentJudgeEnvironmentShard | AgentJudgeCaseShard,
    sha256_by_id: Mapping[str, str],
) -> list[dict[str, Any]]:
    value = _load_json(path, role=f"shard {descriptor.index} predictions")
    if not isinstance(value, list):
        raise AgentJudgeShardError(
            f"shard {descriptor.index} predictions must be a JSON array"
        )
    if len(value) != len(descriptor.trajectory_ids):
        raise AgentJudgeShardError(
            f"shard {descriptor.index} predictions do not completely cover its cases"
        )
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, (expected_id, record) in enumerate(
        zip(descriptor.trajectory_ids, value, strict=True)
    ):
        if not isinstance(record, dict):
            raise AgentJudgeShardError(
                f"shard {descriptor.index} prediction {index} is not an object"
            )
        _assert_gold_free(
            record,
            location=f"shard {descriptor.index} predictions[{index}]",
        )
        if set(record) != AGENT_JUDGE_PREDICTION_FIELDS:
            raise AgentJudgeShardError(
                f"shard {descriptor.index} prediction {index} does not have "
                "the exact ten-field Agent Judge structure"
            )
        trajectory_id = record.get("trajectory_id")
        if trajectory_id in seen:
            raise AgentJudgeShardError(
                f"shard {descriptor.index} predictions duplicate trajectory "
                f"{trajectory_id!r}"
            )
        seen.add(trajectory_id)
        if trajectory_id != expected_id:
            raise AgentJudgeShardError(
                f"shard {descriptor.index} prediction order or identity differs "
                "from its manifest"
            )
        trajectory_sha256 = record.get("trajectory_sha256")
        if (
            not isinstance(trajectory_sha256, str)
            or _SHA256_RE.fullmatch(trajectory_sha256) is None
            or trajectory_sha256 != sha256_by_id[expected_id]
        ):
            raise AgentJudgeShardError(
                f"shard {descriptor.index} trajectory SHA-256 is invalid for "
                f"{expected_id!r}"
            )
        records.append(record)
    return records


def merge_agent_judge_shard_predictions(
    *,
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    shard_descriptors: Sequence[AgentJudgeEnvironmentShard],
    shard_prediction_paths: Sequence[str | Path],
    output_path: str | Path,
) -> list[dict[str, Any]]:
    """Strictly validate and mechanically merge environment shard predictions.

    No field is inferred or repaired.  The returned and persisted array follows
    the complete parent cohort order and is ready for a full protocol validator.
    """

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    _assert_safe_path(destination, role="merged prediction output", output=True)
    manifest, cohort = _load_full_inputs(prediction_path, cohort_path)
    expected_materials = _build_shard_materials(
        manifest=manifest,
        cohort=cohort,
        # Descriptor paths are deliberately ignored while deriving identities.
        output_dir=Path("/").resolve(),
    )
    if isinstance(shard_descriptors, (str, bytes)) or len(shard_descriptors) != len(
        expected_materials
    ):
        raise AgentJudgeShardError(
            "shard descriptors do not provide the complete environment partition"
        )
    if isinstance(shard_prediction_paths, (str, bytes, Path)) or len(
        shard_prediction_paths
    ) != len(expected_materials):
        raise AgentJudgeShardError(
            "shard prediction paths do not align with the environment partition"
        )

    covered_ids: set[str] = set()
    records_by_id: dict[str, dict[str, Any]] = {}
    input_prediction_paths: set[Path] = set()
    sha256_by_id = {
        entry["trajectory_id"]: entry["trajectory_sha256"]
        for entry in manifest["entries"]
    }
    for actual, expected, raw_prediction_path in zip(
        shard_descriptors,
        expected_materials,
        shard_prediction_paths,
        strict=True,
    ):
        _validate_descriptor(actual, expected)
        overlap = covered_ids.intersection(actual.trajectory_ids)
        if overlap:
            raise AgentJudgeShardError(
                "shard descriptors overlap trajectories: "
                + ", ".join(sorted(overlap))
            )
        covered_ids.update(actual.trajectory_ids)

        shard_prediction_path = Path(raw_prediction_path).expanduser().resolve()
        if shard_prediction_path in input_prediction_paths:
            raise AgentJudgeShardError("shard prediction paths are duplicated")
        input_prediction_paths.add(shard_prediction_path)
        records = _load_prediction_records(
            shard_prediction_path,
            descriptor=actual,
            sha256_by_id=sha256_by_id,
        )
        for record in records:
            trajectory_id = record["trajectory_id"]
            if trajectory_id in records_by_id:
                raise AgentJudgeShardError(
                    f"shard predictions duplicate trajectory {trajectory_id!r}"
                )
            records_by_id[trajectory_id] = record

    full_ids = cohort["trajectory_ids"]
    if covered_ids != set(full_ids) or set(records_by_id) != set(full_ids):
        raise AgentJudgeShardError(
            "shard descriptors or predictions do not completely cover the full cohort"
        )
    if destination in {
        prediction_path,
        cohort_path,
        *input_prediction_paths,
    }:
        raise AgentJudgeShardError("merged output path aliases an input artifact")

    merged = [records_by_id[trajectory_id] for trajectory_id in full_ids]
    _write_once_many(
        [
            (
                destination,
                _json_text(merged),
                "merged Agent Judge predictions",
            )
        ]
    )
    return merged


def merge_agent_judge_case_predictions(
    *,
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    shard_descriptors: Sequence[AgentJudgeCaseShard],
    shard_prediction_paths: Sequence[str | Path],
    output_path: str | Path,
) -> list[dict[str, Any]]:
    """Validate and merge one-case shard predictions in parent cohort order.

    Every parent case must have exactly one untampered descriptor and one
    corresponding prediction file.  No prediction field is inferred or
    repaired, and the merged output is persisted write-once.
    """

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    _assert_safe_path(destination, role="merged case prediction output", output=True)
    manifest, cohort = _load_full_inputs(prediction_path, cohort_path)
    expected_materials = _build_case_shard_materials(
        manifest=manifest,
        cohort=cohort,
        # Descriptor paths are deliberately ignored while deriving identities.
        output_dir=Path("/").resolve(),
    )
    if isinstance(shard_descriptors, (str, bytes)) or len(shard_descriptors) != len(
        expected_materials
    ):
        raise AgentJudgeShardError(
            "case shard descriptors do not completely cover the parent cohort"
        )
    if isinstance(shard_prediction_paths, (str, bytes, Path)) or len(
        shard_prediction_paths
    ) != len(expected_materials):
        raise AgentJudgeShardError(
            "case shard prediction paths do not align with the parent cohort"
        )

    covered_ids: set[str] = set()
    records_by_id: dict[str, dict[str, Any]] = {}
    input_prediction_paths: set[Path] = set()
    sha256_by_id = {
        entry["trajectory_id"]: entry["trajectory_sha256"]
        for entry in manifest["entries"]
    }
    for actual, expected, raw_prediction_path in zip(
        shard_descriptors,
        expected_materials,
        shard_prediction_paths,
        strict=True,
    ):
        _validate_case_descriptor(actual, expected)
        if actual.trajectory_id in covered_ids:
            raise AgentJudgeShardError(
                f"case shard descriptors duplicate trajectory "
                f"{actual.trajectory_id!r}"
            )
        covered_ids.add(actual.trajectory_id)

        shard_prediction_path = Path(raw_prediction_path).expanduser().resolve()
        if shard_prediction_path in input_prediction_paths:
            raise AgentJudgeShardError("case shard prediction paths are duplicated")
        input_prediction_paths.add(shard_prediction_path)
        records = _load_prediction_records(
            shard_prediction_path,
            descriptor=actual,
            sha256_by_id=sha256_by_id,
        )
        if len(records) != 1:
            # This is structurally guaranteed by the descriptor, but retaining
            # the explicit invariant keeps the merge boundary fail-closed.
            raise AgentJudgeShardError(
                f"case shard {actual.index} must contain exactly one prediction"
            )
        record = records[0]
        trajectory_id = record["trajectory_id"]
        if trajectory_id in records_by_id:
            raise AgentJudgeShardError(
                f"case shard predictions duplicate trajectory {trajectory_id!r}"
            )
        records_by_id[trajectory_id] = record

    full_ids = cohort["trajectory_ids"]
    if covered_ids != set(full_ids) or set(records_by_id) != set(full_ids):
        raise AgentJudgeShardError(
            "case shard descriptors or predictions do not completely cover "
            "the parent cohort"
        )
    if destination in {
        prediction_path,
        cohort_path,
        *input_prediction_paths,
    }:
        raise AgentJudgeShardError("merged case output path aliases an input artifact")

    merged = [records_by_id[trajectory_id] for trajectory_id in full_ids]
    _write_once_many(
        [
            (
                destination,
                _json_text(merged),
                "merged Agent Judge case predictions",
            )
        ]
    )
    return merged


__all__ = [
    "AGENT_JUDGE_CASE_SHARD_SCHEMA_VERSION",
    "AGENT_JUDGE_CASE_SHARD_SELECTION_ALGORITHM",
    "AGENT_JUDGE_SHARD_SCHEMA_VERSION",
    "AGENT_JUDGE_SHARD_SELECTION_ALGORITHM",
    "AgentJudgeCaseShard",
    "AgentJudgeEnvironmentShard",
    "AgentJudgeShardError",
    "create_agent_judge_case_shards",
    "create_agent_judge_environment_shards",
    "merge_agent_judge_case_predictions",
    "merge_agent_judge_shard_predictions",
]
