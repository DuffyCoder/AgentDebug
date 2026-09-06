"""Strict AgentErrorBench exact-match metrics."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping


SUCCESS_STATUSES = {"success", "success_needs_review"}


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _aggregate(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    step_denominator = sum(isinstance(row.get("gold_step"), int) for row in rows)
    module_denominator = sum(
        isinstance(row.get("gold_step"), int)
        and row.get("gold_module") is not None
        for row in rows
    )
    all_denominator = sum(
        isinstance(row.get("gold_step"), int)
        and row.get("gold_module") is not None
        and row.get("gold_error_type") is not None
        for row in rows
    )
    step_correct = sum(row.get("step_exact") is True for row in rows)
    module_correct = sum(row.get("step_module_exact") is True for row in rows)
    all_correct = sum(row.get("all_correct") is True for row in rows)
    statuses = Counter(str(row.get("status") or "missing_status") for row in rows)
    failure_codes = Counter(
        str(row.get("failure_code"))
        for row in rows
        if row.get("failure_code")
    )
    return {
        "trajectory_count": total,
        "successful_prediction_count": sum(
            status in SUCCESS_STATUSES for status in statuses.elements()
        ),
        "failed_prediction_count": sum(
            status not in SUCCESS_STATUSES for status in statuses.elements()
        ),
        "step_exact": {
            "correct": step_correct,
            "denominator": step_denominator,
            "accuracy": _ratio(step_correct, step_denominator),
        },
        "step_module_exact": {
            "correct": module_correct,
            "denominator": module_denominator,
            "accuracy": _ratio(module_correct, module_denominator),
        },
        "all_correct": {
            "correct": all_correct,
            "denominator": all_denominator,
            "accuracy": _ratio(all_correct, all_denominator),
            "unscorable_missing_gold_type": module_denominator - all_denominator,
            "gold_type_coverage": _ratio(all_denominator, module_denominator),
        },
        "status_counts": dict(sorted(statuses.items())),
        "failure_code_counts": dict(sorted(failure_codes.items())),
    }


def compute_metrics(
    predictions: Iterable[Mapping[str, Any]],
    *,
    phase1_gold_available: bool = False,
    phase1_gold_reason: str = "",
) -> dict[str, Any]:
    """Compute exact metrics; invalid outputs remain in every eligible denominator."""

    rows = list(predictions)
    methods = sorted({str(row.get("method")) for row in rows})
    environments = ("alfworld", "gaia", "webshop")
    by_method: dict[str, Any] = {}
    for method in methods:
        method_rows = [row for row in rows if row.get("method") == method]
        by_method[method] = {
            "overall": _aggregate(method_rows),
            "by_environment": {
                environment: _aggregate(
                    [
                        row
                        for row in method_rows
                        if row.get("environment") == environment
                    ]
                )
                for environment in environments
            },
            "by_error_type": {
                error_type: _aggregate(
                    [
                        row
                        for row in method_rows
                        if (row.get("gold_error_type") or "__missing__")
                        == error_type
                    ]
                )
                for error_type in sorted(
                    {
                        str(row.get("gold_error_type") or "__missing__")
                        for row in method_rows
                    }
                )
            },
        }

    comparison: dict[str, Any] = {}
    if "direct" in by_method and "two_stage" in by_method:
        for key in ("step_exact", "step_module_exact", "all_correct"):
            direct = by_method["direct"]["overall"][key]["accuracy"]
            two_stage = by_method["two_stage"]["overall"][key]["accuracy"]
            comparison[key] = {
                "direct": direct,
                "two_stage": two_stage,
                "two_stage_minus_direct": (
                    two_stage - direct
                    if direct is not None and two_stage is not None
                    else None
                ),
            }

    return {
        "metric_policy": {
            "primary_matching": "exact",
            "failed_or_invalid_outputs": (
                "Counted as incorrect in every metric for which gold is available."
            ),
            "missing_gold_error_type": (
                "Excluded only from All Correct, reported explicitly as unscorable; "
                "retained in Step and Step+Module."
            ),
            "step_mapping": (
                "predicted_step is recovered from the exact critical_event_id "
                "through the adapter's bidirectional map; judge-reported "
                "critical_step is audit metadata only."
            ),
        },
        "phase1_metrics": {
            "available": phase1_gold_available,
            "reason": phase1_gold_reason,
            "micro_precision_recall_f1": None,
            "macro_precision_recall_f1": None,
            "by_module": None,
            "by_error_type": None,
        },
        "by_method": by_method,
        "method_comparison": comparison,
    }
