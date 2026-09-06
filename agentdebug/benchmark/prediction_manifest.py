"""Hash-locked, gold-free inputs for production semantic prediction.

The benchmark adapter may need labels to establish that a released gold step
has one unambiguous canonical mapping.  The provider process must not inherit
those labels.  This module defines the process-boundary artifact: a reversible
``JudgeView`` plus the public step/event mapping and content identities needed
for prediction.  It intentionally contains no ``GoldLabel`` and no scored
fields.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from agentdebug.diagnostics import JUDGE_VIEW_VERSION, build_judge_view
from agentdebug.diagnostics.judge_view import JudgeView
from agentdebug.trace import CanonicalTrace

from .adapter import ADAPTER_VERSION
from .models import TraceMapping


PREDICTION_MANIFEST_SCHEMA_VERSION = (
    "agentdebug.benchmark.production-prediction-manifest.v1"
)


class PredictionManifestError(ValueError):
    """A production prediction boundary is unsafe or internally inconsistent."""


@dataclass(frozen=True)
class PredictionCase:
    """One label-free semantic prediction input."""

    trajectory_id: str
    trajectory_sha256: str
    judge_view: JudgeView
    step_event_mapping: tuple[tuple[int, str], ...]
    case_input_sha256: str

    def event_for_step(self, step: int) -> str | None:
        values = [
            event_id
            for mapped_step, event_id in self.step_event_mapping
            if mapped_step == step
        ]
        return values[0] if len(values) == 1 else None

    def step_for_event(self, event_id: str) -> int | None:
        values = [
            step
            for step, mapped_event_id in self.step_event_mapping
            if mapped_event_id == event_id
        ]
        return values[0] if len(values) == 1 else None


_FORBIDDEN_KEYS = {
    "all_correct",
    "confidence",
    "critical_failure_module",
    "critical_failure_step",
    "critical_failure_type",
    "gold_error_type",
    "gold_event_id",
    "gold_module",
    "gold_normalization_notes",
    "gold_raw_error_type",
    "gold_raw_module",
    "gold_reasoning",
    "gold_step",
    "predicted_error_type",
    "predicted_event_id",
    "predicted_module",
    "predicted_step",
    "score",
    "step_annotations",
    "step_exact",
    "step_module_exact",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def stable_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _assert_gold_free(value: Any, *, location: str) -> None:
    if isinstance(value, Mapping):
        forbidden = sorted(
            str(key)
            for key in value
            if str(key).casefold() in _FORBIDDEN_KEYS
            or str(key).casefold().startswith("gold_")
        )
        if forbidden:
            raise PredictionManifestError(
                f"{location} contains forbidden scored/gold fields: "
                + ", ".join(forbidden)
            )
        for key, item in value.items():
            _assert_gold_free(item, location=f"{location}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_gold_free(item, location=f"{location}[{index}]")


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def build_prediction_case(
    trace: CanonicalTrace,
    mapping: TraceMapping,
) -> dict[str, Any]:
    """Project one trace without accepting or consulting a benchmark label."""

    if not isinstance(trace, CanonicalTrace):
        raise TypeError("prediction input construction requires CanonicalTrace")
    if not isinstance(mapping, TraceMapping):
        raise TypeError("prediction input construction requires TraceMapping")
    if trace.trace_id != mapping.trajectory_id:
        raise PredictionManifestError(
            "CanonicalTrace and TraceMapping trajectory IDs differ"
        )
    view = build_judge_view(trace)
    step_mapping = [
        {
            "step": item.original_step,
            "assistant_event_id": item.critical_event_id,
        }
        for item in mapping.steps
    ]
    expected_steps = list(range(1, len(view.steps) + 1))
    if [item["step"] for item in step_mapping] != expected_steps:
        raise PredictionManifestError(
            "public benchmark step mapping is not contiguous"
        )
    if [
        item["assistant_event_id"] for item in step_mapping
    ] != [step.assistant_event_id for step in view.steps]:
        raise PredictionManifestError(
            "JudgeView decisions differ from the public benchmark mapping"
        )
    record: dict[str, Any] = {
        "trajectory_id": mapping.trajectory_id,
        "trajectory_sha256": mapping.trajectory_sha256,
        "adapter_version": ADAPTER_VERSION,
        "judge_view_version": JUDGE_VIEW_VERSION,
        "judge_view": view.to_dict(),
        "step_event_mapping": step_mapping,
    }
    _assert_gold_free(record, location="prediction case")
    record["case_input_sha256"] = stable_sha256(record)
    return record


def write_prediction_manifest(
    *,
    traces_and_mappings: Iterable[tuple[CanonicalTrace, TraceMapping]],
    dataset_manifest_sha256: str,
    cohort_name: str,
    cohort_sha256: str,
    selection_identity: Mapping[str, Any],
    output_path: str | Path,
) -> dict[str, Any]:
    """Persist the complete label-free input set before provider execution."""

    for name, value in (
        ("dataset_manifest_sha256", dataset_manifest_sha256),
        ("cohort_name", cohort_name),
        ("cohort_sha256", cohort_sha256),
    ):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be non-empty text")
    entries = [
        build_prediction_case(trace, mapping)
        for trace, mapping in traces_and_mappings
    ]
    if not entries:
        raise ValueError("prediction manifest requires at least one case")
    trajectory_ids = [entry["trajectory_id"] for entry in entries]
    if len(set(trajectory_ids)) != len(trajectory_ids):
        raise PredictionManifestError(
            "prediction manifest trajectory IDs must be unique"
        )
    document: dict[str, Any] = {
        "schema_version": PREDICTION_MANIFEST_SCHEMA_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "judge_view_version": JUDGE_VIEW_VERSION,
        "dataset_manifest_sha256": dataset_manifest_sha256,
        "cohort_name": cohort_name,
        "cohort_sha256": cohort_sha256,
        "selection_identity": dict(selection_identity),
        "entry_count": len(entries),
        "entries": entries,
    }
    _assert_gold_free(document, location="prediction manifest")
    document["prediction_manifest_sha256"] = stable_sha256(document)
    _atomic_json(Path(output_path).expanduser().resolve(), document)
    return document


def _case_from_dict(entry: Mapping[str, Any]) -> PredictionCase:
    expected_fields = {
        "trajectory_id",
        "trajectory_sha256",
        "adapter_version",
        "judge_view_version",
        "judge_view",
        "step_event_mapping",
        "case_input_sha256",
    }
    if set(entry) != expected_fields:
        raise PredictionManifestError(
            "prediction case fields do not match the schema"
        )
    body = dict(entry)
    claimed_hash = body.pop("case_input_sha256")
    if claimed_hash != stable_sha256(body):
        raise PredictionManifestError(
            "prediction case content hash is invalid"
        )
    if (
        entry["adapter_version"] != ADAPTER_VERSION
        or entry["judge_view_version"] != JUDGE_VIEW_VERSION
    ):
        raise PredictionManifestError(
            "prediction case implementation version is unsupported"
        )
    raw_view = entry["judge_view"]
    if not isinstance(raw_view, Mapping):
        raise PredictionManifestError("prediction JudgeView must be an object")
    try:
        view = JudgeView.from_dict(raw_view)
    except (KeyError, TypeError, ValueError) as error:
        raise PredictionManifestError(
            "prediction JudgeView cannot be reconstructed"
        ) from error
    raw_mapping = entry["step_event_mapping"]
    if not isinstance(raw_mapping, list) or not raw_mapping:
        raise PredictionManifestError(
            "prediction step/event mapping must be a non-empty array"
        )
    step_event_mapping: list[tuple[int, str]] = []
    for index, value in enumerate(raw_mapping, 1):
        if (
            not isinstance(value, Mapping)
            or set(value) != {"step", "assistant_event_id"}
            or isinstance(value.get("step"), bool)
            or value.get("step") != index
            or not isinstance(value.get("assistant_event_id"), str)
            or not value["assistant_event_id"]
        ):
            raise PredictionManifestError(
                "prediction step/event mapping is invalid"
            )
        step_event_mapping.append(
            (value["step"], value["assistant_event_id"])
        )
    if tuple(
        event_id for _, event_id in step_event_mapping
    ) != tuple(step.assistant_event_id for step in view.steps):
        raise PredictionManifestError(
            "prediction mapping diverges from the JudgeView"
        )
    if entry["trajectory_id"] != view.trace_id:
        raise PredictionManifestError(
            "prediction trajectory ID diverges from the JudgeView"
        )
    return PredictionCase(
        trajectory_id=str(entry["trajectory_id"]),
        trajectory_sha256=str(entry["trajectory_sha256"]),
        judge_view=view,
        step_event_mapping=tuple(step_event_mapping),
        case_input_sha256=str(entry["case_input_sha256"]),
    )


def load_prediction_manifest(
    path: str | Path,
) -> tuple[dict[str, Any], list[PredictionCase]]:
    """Load and fail closed on any identity, content, or schema mismatch."""

    manifest_path = Path(path).expanduser().resolve()
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PredictionManifestError(
            "prediction manifest is missing or invalid JSON"
        ) from error
    if not isinstance(document, dict):
        raise PredictionManifestError(
            "prediction manifest must be a JSON object"
        )
    expected_fields = {
        "schema_version",
        "adapter_version",
        "judge_view_version",
        "dataset_manifest_sha256",
        "cohort_name",
        "cohort_sha256",
        "selection_identity",
        "entry_count",
        "entries",
        "prediction_manifest_sha256",
    }
    if set(document) != expected_fields:
        raise PredictionManifestError(
            "prediction manifest fields do not match the schema"
        )
    if (
        document["schema_version"] != PREDICTION_MANIFEST_SCHEMA_VERSION
        or document["adapter_version"] != ADAPTER_VERSION
        or document["judge_view_version"] != JUDGE_VIEW_VERSION
    ):
        raise PredictionManifestError(
            "prediction manifest implementation version is unsupported"
        )
    claimed_hash = document["prediction_manifest_sha256"]
    body = dict(document)
    body.pop("prediction_manifest_sha256")
    if claimed_hash != stable_sha256(body):
        raise PredictionManifestError(
            "prediction manifest content hash is invalid"
        )
    entries = document["entries"]
    if (
        not isinstance(entries, list)
        or not entries
        or len(entries) != document["entry_count"]
    ):
        raise PredictionManifestError(
            "prediction manifest entries/count are invalid"
        )
    _assert_gold_free(document, location="prediction manifest")
    cases = [_case_from_dict(entry) for entry in entries]
    ids = [case.trajectory_id for case in cases]
    if len(set(ids)) != len(ids):
        raise PredictionManifestError(
            "prediction manifest trajectory IDs are duplicated"
        )
    return document, cases


__all__ = [
    "PREDICTION_MANIFEST_SCHEMA_VERSION",
    "PredictionCase",
    "PredictionManifestError",
    "build_prediction_case",
    "load_prediction_manifest",
    "stable_sha256",
    "write_prediction_manifest",
]
