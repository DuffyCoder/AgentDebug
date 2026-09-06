"""Frozen, reproducible benchmark cohort manifests.

Cohort membership is deliberately independent of benchmark gold annotations.
The only inputs to an individual ranking digest are the environment,
trajectory ID, dataset manifest digest, and a fixed cohort salt.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .models import BenchmarkDataset, BenchmarkExample


COHORT_SCHEMA_VERSION = "agentdebug.benchmark.cohort.v1"
COHORT_SUITE_SCHEMA_VERSION = "agentdebug.benchmark.cohort-suite.v1"
SELECTION_ALGORITHM = (
    "sha256-json-array(environment,trajectory_id,dataset_manifest_sha256,salt)"
    "-rank-v1"
)
DEFAULT_ENVIRONMENTS = ("alfworld", "gaia", "webshop")
DEFAULT_COHORT_SPECS = (
    ("tuning-v1", "agentdebug-agenterrorbench-tuning-v1-2026-07-24"),
    ("smoke-v1", "agentdebug-agenterrorbench-smoke-v1-2026-07-24"),
)
GAIA_SMOKE_COHORT_NAME = "gaia-smoke-v1"
GAIA_SMOKE_ENVIRONMENT = "gaia"
GAIA_SMOKE_PER_ENVIRONMENT = 30
# Reuse the original smoke-v1 salt so that its ten GAIA cases are exactly the
# first ten members of the expanded development cohort.
GAIA_SMOKE_SALT = "agentdebug-agenterrorbench-smoke-v1-2026-07-24"


class CohortManifestError(ValueError):
    """A cohort manifest is invalid or does not belong to this dataset."""


@dataclass(frozen=True)
class CohortManifest:
    """A validated immutable cohort selection."""

    path: Path | None
    cohort_name: str
    cohort_sha256: str
    dataset_manifest_sha256: str
    trajectory_ids: tuple[str, ...]
    entries: tuple[Mapping[str, Any], ...]
    document: Mapping[str, Any]

    def examples_from(self, dataset: BenchmarkDataset) -> list[BenchmarkExample]:
        by_id = {
            example.label.trajectory_id: example for example in dataset.examples
        }
        return [by_id[trajectory_id] for trajectory_id in self.trajectory_ids]


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _document_sha256(document: Mapping[str, Any], *, hash_field: str) -> str:
    body = dict(document)
    body.pop(hash_field, None)
    return hashlib.sha256(_canonical_json(body)).hexdigest()


def _selection_digest(
    *,
    environment: str,
    trajectory_id: str,
    dataset_manifest_sha256: str,
    salt: str,
) -> str:
    inputs = [
        environment,
        trajectory_id,
        dataset_manifest_sha256,
        salt,
    ]
    return hashlib.sha256(_canonical_json(inputs)).hexdigest()


def _stable_conversion_exclusions(
    dataset: BenchmarkDataset,
) -> list[dict[str, Any]]:
    """Return conversion exclusions without machine-specific absolute paths."""

    exclusions: list[dict[str, Any]] = []
    for category, rows in (
        ("unavailable", dataset.unavailable),
        ("conversion_failure", dataset.conversion_failures),
    ):
        for row in rows:
            item: dict[str, Any] = {
                "trajectory_id": row.get("trajectory_id"),
                "environment": row.get("environment"),
                "category": category,
                "reason": row.get("reason", "unspecified_conversion_failure"),
            }
            conversion = row.get("conversion")
            if isinstance(conversion, Mapping):
                issues = conversion.get("issues")
                if isinstance(issues, list):
                    item["issue_codes"] = [
                        issue.get("code")
                        for issue in issues
                        if isinstance(issue, Mapping)
                        and isinstance(issue.get("code"), str)
                    ]
            if isinstance(row.get("error_type"), str):
                item["error_type"] = row["error_type"]
            exclusions.append(item)
    exclusions.sort(
        key=lambda row: (
            str(row.get("environment")),
            str(row.get("trajectory_id")),
            str(row.get("category")),
            str(row.get("reason")),
        )
    )
    return exclusions


def _rank_environment(
    examples: Iterable[BenchmarkExample],
    *,
    environment: str,
    dataset_manifest_sha256: str,
    salt: str,
    reserved_ids: set[str],
) -> list[tuple[str, BenchmarkExample]]:
    ranked = []
    for example in examples:
        if example.label.environment != environment:
            continue
        trajectory_id = example.label.trajectory_id
        if trajectory_id in reserved_ids:
            continue
        digest = _selection_digest(
            environment=environment,
            trajectory_id=trajectory_id,
            dataset_manifest_sha256=dataset_manifest_sha256,
            salt=salt,
        )
        ranked.append((digest, example))
    ranked.sort(key=lambda item: (item[0], item[1].label.trajectory_id))
    return ranked


def build_default_cohort_documents(
    dataset: BenchmarkDataset,
    *,
    per_environment: int = 10,
    environments: Sequence[str] = DEFAULT_ENVIRONMENTS,
    cohort_specs: Sequence[tuple[str, str]] = DEFAULT_COHORT_SPECS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build disjoint deterministic cohort documents and their suite index."""

    if per_environment < 1:
        raise CohortManifestError("per_environment must be positive")
    if not environments:
        raise CohortManifestError("at least one environment is required")
    if len(set(environments)) != len(environments):
        raise CohortManifestError("environments must be unique")
    names = [name for name, _ in cohort_specs]
    salts = [salt for _, salt in cohort_specs]
    if not cohort_specs or len(set(names)) != len(names):
        raise CohortManifestError("cohort names must be non-empty and unique")
    if len(set(salts)) != len(salts):
        raise CohortManifestError("every cohort must use a distinct fixed salt")

    conversion_exclusions = _stable_conversion_exclusions(dataset)
    reserved_ids: set[str] = set()
    documents: list[dict[str, Any]] = []
    prior_cohorts: list[dict[str, str]] = []
    for cohort_name, salt in cohort_specs:
        entries: list[dict[str, Any]] = []
        for environment in environments:
            ranked = _rank_environment(
                dataset.examples,
                environment=environment,
                dataset_manifest_sha256=dataset.dataset_sha256,
                salt=salt,
                reserved_ids=reserved_ids,
            )
            if len(ranked) < per_environment:
                raise CohortManifestError(
                    f"{cohort_name} needs {per_environment} eligible "
                    f"{environment} trajectories after disjoint reservation, "
                    f"but only {len(ranked)} are available"
                )
            for rank, (selection_sha256, example) in enumerate(
                ranked[:per_environment],
                1,
            ):
                entries.append(
                    {
                        "environment": environment,
                        "trajectory_id": example.label.trajectory_id,
                        "rank": rank,
                        "selection_sha256": selection_sha256,
                    }
                )

        trajectory_ids = [entry["trajectory_id"] for entry in entries]
        document: dict[str, Any] = {
            "schema_version": COHORT_SCHEMA_VERSION,
            "cohort_name": cohort_name,
            "dataset_manifest_sha256": dataset.dataset_sha256,
            "selection": {
                "algorithm": SELECTION_ALGORITHM,
                "rank_input_fields": [
                    "environment",
                    "trajectory_id",
                    "dataset_manifest_sha256",
                    "salt",
                ],
                "salt": salt,
                "environments": list(environments),
                "per_environment": per_environment,
                "disjoint_from": list(prior_cohorts),
                "reserved_trajectory_ids": sorted(reserved_ids),
                "eligibility_rule": (
                    "canonical conversion and gold-step mapping must pass; "
                    "no gold classification field participates in ranking"
                ),
            },
            "trajectory_ids": trajectory_ids,
            "entries": entries,
            "conversion_exclusions": conversion_exclusions,
        }
        document["cohort_sha256"] = _document_sha256(
            document,
            hash_field="cohort_sha256",
        )
        documents.append(document)
        reserved_ids.update(trajectory_ids)
        prior_cohorts.append(
            {
                "cohort_name": cohort_name,
                "cohort_sha256": document["cohort_sha256"],
            }
        )

    suite: dict[str, Any] = {
        "schema_version": COHORT_SUITE_SCHEMA_VERSION,
        "dataset_manifest_sha256": dataset.dataset_sha256,
        "selection_algorithm": SELECTION_ALGORITHM,
        "cohorts": [
            {
                "cohort_name": document["cohort_name"],
                "filename": f"{document['cohort_name']}.json",
                "cohort_sha256": document["cohort_sha256"],
                "trajectory_count": len(document["trajectory_ids"]),
            }
            for document in documents
        ],
    }
    suite["suite_sha256"] = _document_sha256(
        suite,
        hash_field="suite_sha256",
    )
    return documents, suite


def build_gaia_smoke_cohort_document(
    dataset: BenchmarkDataset,
) -> dict[str, Any]:
    """Expand smoke-v1's GAIA ranking to one frozen 30-case cohort.

    The original tuning-v1 reservation and smoke-v1 salt are deliberately
    retained.  Consequently ranks 1--10 are the existing smoke-v1 GAIA cases,
    while ranks 11--30 are a deterministic continuation of the same ranking.
    Gold classification fields never participate in membership or order.
    """

    default_documents, _ = build_default_cohort_documents(dataset)
    tuning = next(
        document
        for document in default_documents
        if document["cohort_name"] == "tuning-v1"
    )
    reserved_ids = set(tuning["trajectory_ids"])
    ranked = _rank_environment(
        dataset.examples,
        environment=GAIA_SMOKE_ENVIRONMENT,
        dataset_manifest_sha256=dataset.dataset_sha256,
        salt=GAIA_SMOKE_SALT,
        reserved_ids=reserved_ids,
    )
    if len(ranked) < GAIA_SMOKE_PER_ENVIRONMENT:
        raise CohortManifestError(
            f"{GAIA_SMOKE_COHORT_NAME} needs "
            f"{GAIA_SMOKE_PER_ENVIRONMENT} eligible GAIA trajectories after "
            f"the tuning-v1 reservation, but only {len(ranked)} are available"
        )
    entries = [
        {
            "environment": GAIA_SMOKE_ENVIRONMENT,
            "trajectory_id": example.label.trajectory_id,
            "rank": rank,
            "selection_sha256": selection_sha256,
        }
        for rank, (selection_sha256, example) in enumerate(
            ranked[:GAIA_SMOKE_PER_ENVIRONMENT],
            1,
        )
    ]
    document: dict[str, Any] = {
        "schema_version": COHORT_SCHEMA_VERSION,
        "cohort_name": GAIA_SMOKE_COHORT_NAME,
        "dataset_manifest_sha256": dataset.dataset_sha256,
        "selection": {
            "algorithm": SELECTION_ALGORITHM,
            "rank_input_fields": [
                "environment",
                "trajectory_id",
                "dataset_manifest_sha256",
                "salt",
            ],
            "salt": GAIA_SMOKE_SALT,
            "environments": [GAIA_SMOKE_ENVIRONMENT],
            "per_environment": GAIA_SMOKE_PER_ENVIRONMENT,
            "disjoint_from": [
                {
                    "cohort_name": tuning["cohort_name"],
                    "cohort_sha256": tuning["cohort_sha256"],
                }
            ],
            "reserved_trajectory_ids": sorted(reserved_ids),
            "eligibility_rule": (
                "canonical conversion and gold-step mapping must pass; "
                "no gold classification field participates in ranking"
            ),
        },
        "trajectory_ids": [entry["trajectory_id"] for entry in entries],
        "entries": entries,
        "conversion_exclusions": _stable_conversion_exclusions(dataset),
    }
    document["cohort_sha256"] = _document_sha256(
        document,
        hash_field="cohort_sha256",
    )
    return document


def _validate_manifest_document(
    document: Any,
    *,
    dataset: BenchmarkDataset,
    path: Path | None,
) -> CohortManifest:
    location = str(path) if path is not None else "cohort manifest"
    if not isinstance(document, Mapping):
        raise CohortManifestError(f"{location} must contain a JSON object")
    required = {
        "schema_version",
        "cohort_name",
        "dataset_manifest_sha256",
        "selection",
        "trajectory_ids",
        "entries",
        "conversion_exclusions",
        "cohort_sha256",
    }
    missing = required - set(document)
    if missing:
        raise CohortManifestError(
            f"{location} missing fields: {', '.join(sorted(missing))}"
        )
    if document["schema_version"] != COHORT_SCHEMA_VERSION:
        raise CohortManifestError(
            f"{location} has unsupported schema_version "
            f"{document['schema_version']!r}"
        )
    expected_hash = _document_sha256(
        document,
        hash_field="cohort_sha256",
    )
    if document["cohort_sha256"] != expected_hash:
        raise CohortManifestError(
            f"{location} cohort_sha256 does not match its contents"
        )
    if document["dataset_manifest_sha256"] != dataset.dataset_sha256:
        raise CohortManifestError(
            f"{location} targets dataset manifest "
            f"{document['dataset_manifest_sha256']!r}, but the loaded dataset "
            f"is {dataset.dataset_sha256!r}"
        )
    cohort_name = document["cohort_name"]
    if not isinstance(cohort_name, str) or not cohort_name:
        raise CohortManifestError(f"{location}.cohort_name must be non-empty text")
    selection = document["selection"]
    if not isinstance(selection, Mapping):
        raise CohortManifestError(f"{location}.selection must be an object")
    if selection.get("algorithm") != SELECTION_ALGORITHM:
        raise CohortManifestError(f"{location} uses an unsupported selection algorithm")
    salt = selection.get("salt")
    if not isinstance(salt, str) or not salt:
        raise CohortManifestError(f"{location}.selection.salt must be non-empty text")
    environments = selection.get("environments")
    per_environment = selection.get("per_environment")
    if (
        not isinstance(environments, list)
        or not environments
        or any(not isinstance(item, str) or not item for item in environments)
    ):
        raise CohortManifestError(
            f"{location}.selection.environments must be non-empty text values"
        )
    if (
        isinstance(per_environment, bool)
        or not isinstance(per_environment, int)
        or per_environment < 1
    ):
        raise CohortManifestError(
            f"{location}.selection.per_environment must be positive"
        )

    trajectory_ids = document["trajectory_ids"]
    entries = document["entries"]
    if not isinstance(trajectory_ids, list) or any(
        not isinstance(item, str) or not item for item in trajectory_ids
    ):
        raise CohortManifestError(
            f"{location}.trajectory_ids must contain non-empty text values"
        )
    if len(set(trajectory_ids)) != len(trajectory_ids):
        raise CohortManifestError(f"{location} contains duplicate trajectory IDs")
    if not isinstance(entries, list) or len(entries) != len(trajectory_ids):
        raise CohortManifestError(
            f"{location}.entries must align one-to-one with trajectory_ids"
        )
    known = {
        example.label.trajectory_id: example for example in dataset.examples
    }
    counts = {environment: 0 for environment in environments}
    for index, (trajectory_id, entry) in enumerate(zip(trajectory_ids, entries)):
        if not isinstance(entry, Mapping):
            raise CohortManifestError(f"{location}.entries[{index}] must be an object")
        if entry.get("trajectory_id") != trajectory_id:
            raise CohortManifestError(
                f"{location}.entries[{index}] does not match trajectory_ids"
            )
        example = known.get(trajectory_id)
        if example is None:
            raise CohortManifestError(
                f"{location} references unavailable trajectory {trajectory_id!r}"
            )
        environment = entry.get("environment")
        if environment != example.label.environment:
            raise CohortManifestError(
                f"{location} records the wrong environment for {trajectory_id!r}"
            )
        if environment not in counts:
            raise CohortManifestError(
                f"{location} uses undeclared environment {environment!r}"
            )
        counts[environment] += 1
        expected_selection_hash = _selection_digest(
            environment=environment,
            trajectory_id=trajectory_id,
            dataset_manifest_sha256=dataset.dataset_sha256,
            salt=salt,
        )
        if entry.get("selection_sha256") != expected_selection_hash:
            raise CohortManifestError(
                f"{location} has an invalid selection digest for {trajectory_id!r}"
            )
    wrong_counts = {
        environment: count
        for environment, count in counts.items()
        if count != per_environment
    }
    if wrong_counts:
        raise CohortManifestError(
            f"{location} does not contain {per_environment} trajectories for "
            f"every environment: {wrong_counts}"
        )

    if cohort_name == GAIA_SMOKE_COHORT_NAME:
        expected_document = build_gaia_smoke_cohort_document(dataset)
    else:
        expected_documents, _ = build_default_cohort_documents(
            dataset,
            per_environment=per_environment,
            environments=tuple(environments),
        )
        expected_document = next(
            (
                item
                for item in expected_documents
                if item["cohort_name"] == cohort_name
            ),
            None,
        )
    if expected_document is None:
        raise CohortManifestError(
            f"{location} cohort_name {cohort_name!r} is not a supported frozen "
            "cohort"
        )
    if dict(document) != expected_document:
        raise CohortManifestError(
            f"{location} does not match the deterministic selection for "
            f"{cohort_name!r}"
        )

    return CohortManifest(
        path=path,
        cohort_name=cohort_name,
        cohort_sha256=expected_hash,
        dataset_manifest_sha256=dataset.dataset_sha256,
        trajectory_ids=tuple(trajectory_ids),
        entries=tuple(entries),
        document=document,
    )


def load_cohort_manifest(
    path: str | Path,
    *,
    dataset: BenchmarkDataset,
) -> CohortManifest:
    """Read and strictly validate one frozen cohort manifest."""

    manifest_path = Path(path).expanduser().resolve()
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CohortManifestError(
            f"invalid cohort manifest JSON {manifest_path}: {error}"
        ) from error
    return _validate_manifest_document(
        document,
        dataset=dataset,
        path=manifest_path,
    )


def write_default_cohort_manifests(
    dataset: BenchmarkDataset,
    *,
    output_dir: str | Path,
    per_environment: int = 10,
) -> dict[str, Any]:
    """Create the default frozen tuning/smoke manifests without replacement."""

    output_root = Path(output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    documents, suite = build_default_cohort_documents(
        dataset,
        per_environment=per_environment,
    )
    paths: dict[str, str] = {}
    for document in documents:
        path = output_root / f"{document['cohort_name']}.json"
        text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") != text:
            raise CohortManifestError(
                f"refusing to replace frozen cohort manifest with different "
                f"contents: {path}"
            )
        if not path.exists():
            path.write_text(text, encoding="utf-8")
        paths[document["cohort_name"]] = str(path)

    suite_path = output_root / "cohort-suite-v1.json"
    suite_text = json.dumps(suite, ensure_ascii=False, indent=2) + "\n"
    if suite_path.exists() and suite_path.read_text(encoding="utf-8") != suite_text:
        raise CohortManifestError(
            f"refusing to replace frozen cohort suite with different contents: "
            f"{suite_path}"
        )
    if not suite_path.exists():
        suite_path.write_text(suite_text, encoding="utf-8")
    return {
        "dataset_manifest_sha256": dataset.dataset_sha256,
        "suite_sha256": suite["suite_sha256"],
        "cohort_sha256": {
            document["cohort_name"]: document["cohort_sha256"]
            for document in documents
        },
        "paths": {**paths, "suite": str(suite_path)},
    }


def write_gaia_smoke_cohort_manifest(
    dataset: BenchmarkDataset,
    *,
    output_path: str | Path,
) -> dict[str, Any]:
    """Create the frozen expanded GAIA smoke manifest without replacement."""

    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    document = build_gaia_smoke_cohort_document(dataset)
    text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise CohortManifestError(
            "refusing to replace frozen GAIA smoke cohort manifest with "
            f"different contents: {path}"
        )
    if not path.exists():
        path.write_text(text, encoding="utf-8")
    return {
        "cohort_name": document["cohort_name"],
        "dataset_manifest_sha256": dataset.dataset_sha256,
        "cohort_sha256": document["cohort_sha256"],
        "trajectory_count": len(document["trajectory_ids"]),
        "path": str(path),
    }
