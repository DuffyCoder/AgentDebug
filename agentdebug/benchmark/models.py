"""Typed records used by the AgentErrorBench evaluation adapter."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from agentdebug.trace import CanonicalTrace


@dataclass(frozen=True)
class GoldLabel:
    trajectory_id: str
    environment: str
    source_llm: str
    original_step: int
    raw_module: str
    module: Optional[str]
    raw_error_type: str
    error_type: Optional[str]
    reasoning: str
    label_path: str
    normalization_notes: tuple[str, ...] = ()

    @property
    def all_correct_eligible(self) -> bool:
        return self.module is not None and self.error_type is not None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StepMapping:
    """One benchmark assistant decision step and its canonical entities."""

    original_step: int
    source_message_indices: tuple[int, ...]
    canonical_event_ids: tuple[str, ...]
    critical_event_id: str
    assistant_turn_id: str
    tool_call_ids: tuple[str, ...]
    rule: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceMapping:
    trajectory_id: str
    trajectory_path: str
    trajectory_sha256: str
    step_rule: str
    steps: list[StepMapping]
    ignored_inputs: list[dict[str, Any]] = field(default_factory=list)

    def event_for_step(self, original_step: int) -> Optional[str]:
        row = next(
            (item for item in self.steps if item.original_step == original_step),
            None,
        )
        return row.critical_event_id if row else None

    def step_for_event(self, event_id: str) -> Optional[int]:
        matches = [
            item.original_step
            for item in self.steps
            if event_id == item.critical_event_id
        ]
        return matches[0] if len(matches) == 1 else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "trajectory_id": self.trajectory_id,
            "trajectory_path": self.trajectory_path,
            "trajectory_sha256": self.trajectory_sha256,
            "step_rule": self.step_rule,
            "steps": [item.to_dict() for item in self.steps],
            "ignored_inputs": list(self.ignored_inputs),
        }


@dataclass(frozen=True)
class ConversionIssue:
    code: str
    severity: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConversionReport:
    trajectory_id: str
    valid: bool
    input_message_count: int
    preserved_message_count: int
    assistant_decision_count: int
    mapped_step_count: int
    gold_step: int
    gold_event_id: Optional[str]
    issues: list[ConversionIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "issues": [item.to_dict() for item in self.issues],
        }


@dataclass
class BenchmarkExample:
    label: GoldLabel
    trajectory_path: Path
    trace: CanonicalTrace
    mapping: TraceMapping
    conversion: ConversionReport


@dataclass
class BenchmarkDataset:
    root: Path
    version: str
    dataset_sha256: str
    label_file_sha256: dict[str, str]
    trajectory_file_sha256: dict[str, str]
    labels: list[GoldLabel]
    examples: list[BenchmarkExample]
    canonical_conversion_count: int
    unavailable: list[dict[str, Any]]
    conversion_failures: list[dict[str, Any]]
    phase1_gold_available: bool
    phase1_gold_reason: str
    normalization_rules: list[str]

    def example_by_id(self, trajectory_id: str) -> Optional[BenchmarkExample]:
        return next(
            (
                example
                for example in self.examples
                if example.label.trajectory_id == trajectory_id
            ),
            None,
        )

    def audit_dict(self) -> dict[str, Any]:
        environments = ("alfworld", "gaia", "webshop")
        return {
            "dataset_path": str(self.root),
            "dataset_version": self.version,
            "dataset_sha256": self.dataset_sha256,
            "label_file_sha256": self.label_file_sha256,
            "trajectory_file_sha256": self.trajectory_file_sha256,
            "label_count": len(self.labels),
            "source_trajectory_count": len(self.trajectory_file_sha256),
            "canonical_conversion_count": self.canonical_conversion_count,
            "evaluation_ready_count": len(self.examples),
            # Kept as an explicit alias for older audit consumers.
            "available_trajectory_count": len(self.examples),
            "unavailable_count": len(self.unavailable),
            "conversion_failure_count": len(self.conversion_failures),
            "counts_by_environment": {
                environment: {
                    "labels": sum(
                        label.environment == environment for label in self.labels
                    ),
                    "evaluation_ready": sum(
                        example.label.environment == environment
                        for example in self.examples
                    ),
                    "conversion_or_gold_mapping_failures": sum(
                        row.get("environment") == environment
                        for row in self.conversion_failures
                    ),
                    "unavailable": sum(
                        row.get("environment") == environment
                        for row in self.unavailable
                    ),
                }
                for environment in environments
            },
            "phase1_gold_available": self.phase1_gold_available,
            "phase1_gold_reason": self.phase1_gold_reason,
            "gold_label_coverage": {
                "step_gold_count": sum(label.original_step >= 1 for label in self.labels),
                "module_gold_count": sum(
                    label.module is not None for label in self.labels
                ),
                "error_type_gold_count": sum(
                    label.error_type is not None for label in self.labels
                ),
                "all_correct_unscorable_count": sum(
                    label.error_type is None for label in self.labels
                ),
                "unscorable_error_type_trajectory_ids": [
                    label.trajectory_id
                    for label in self.labels
                    if label.error_type is None
                ],
            },
            "normalization_rules": self.normalization_rules,
            "unavailable": self.unavailable,
            "conversion_failures": self.conversion_failures,
        }
