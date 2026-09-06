"""Write reproducible JSONL, CSV, JSON, and Markdown benchmark artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .models import BenchmarkDataset
from .prediction_manifest import stable_sha256


ARTIFACT_MANIFEST_SCHEMA_VERSION = (
    "agentdebug.benchmark.output-artifact-manifest.v1"
)


CSV_FIELDS = [
    "trajectory_id",
    "environment",
    "source_llm",
    "method",
    "status",
    "failure_stage",
    "failure_code",
    "gold_step",
    "gold_event_id",
    "gold_raw_module",
    "gold_module",
    "gold_raw_error_type",
    "gold_error_type",
    "predicted_step",
    "judge_reported_step",
    "predicted_event_id",
    "predicted_module",
    "predicted_error_type",
    "step_exact",
    "step_module_exact",
    "all_correct",
    "specialist_finding_count",
    "latency_seconds",
    "cache_hit",
    "model",
    "temperature",
    "prompt_version",
    "trajectory_sha256",
]


def _percent(value: Any) -> str:
    return "N/A" if value is None else f"{100 * float(value):.2f}%"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _metric_row(method: str, values: Mapping[str, Any]) -> str:
    return (
        f"| {method} | {values['trajectory_count']} | "
        f"{_percent(values['step_exact']['accuracy'])} "
        f"({values['step_exact']['correct']}/{values['step_exact']['denominator']}) | "
        f"{_percent(values['step_module_exact']['accuracy'])} "
        f"({values['step_module_exact']['correct']}/"
        f"{values['step_module_exact']['denominator']}) | "
        f"{_percent(values['all_correct']['accuracy'])} "
        f"({values['all_correct']['correct']}/"
        f"{values['all_correct']['denominator']}) | "
        f"{values['failed_prediction_count']} |"
    )


def _representative_errors(
    predictions: list[Mapping[str, Any]],
    limit: int = 12,
) -> list[Mapping[str, Any]]:
    errors = [
        row
        for row in predictions
        if not str(row.get("status", "")).startswith("success")
        or row.get("all_correct") is False
    ]
    errors.sort(
        key=lambda row: (
            str(row.get("environment")),
            str(row.get("trajectory_id")),
            str(row.get("method")),
        )
    )
    selected: list[Mapping[str, Any]] = []
    selected_ids: set[int] = set()

    def add_first(predicate: Any) -> None:
        for row in errors:
            identity = id(row)
            if identity not in selected_ids and predicate(row):
                selected.append(row)
                selected_ids.add(identity)
                return

    # Start with one genuine semantic disagreement for every
    # environment/method pair. This prevents lexicographic trajectory order
    # from filling the entire report with ALFWorld formatting failures.
    environments = sorted({str(row.get("environment")) for row in errors})
    methods = sorted({str(row.get("method")) for row in errors})
    for environment in environments:
        for method in methods:
            add_first(
                lambda row, environment=environment, method=method: (
                    str(row.get("environment")) == environment
                    and str(row.get("method")) == method
                    and str(row.get("status", "")).startswith("success")
                    and row.get("all_correct") is False
                )
            )

    # Then ensure every observed failure/validation status is represented.
    for status in sorted({str(row.get("status")) for row in errors}):
        add_first(lambda row, status=status: str(row.get("status")) == status)

    # Fill deterministically if the available strata produced fewer cases.
    for row in errors:
        if len(selected) >= limit:
            break
        if id(row) not in selected_ids:
            selected.append(row)
            selected_ids.add(id(row))
    return selected[:limit]


def render_report(
    *,
    dataset: BenchmarkDataset,
    predictions: list[Mapping[str, Any]],
    metrics: Mapping[str, Any],
    run_metadata: Mapping[str, Any],
) -> str:
    by_method = metrics["by_method"]
    provider_telemetry = run_metadata.get("provider_telemetry")
    lines = [
        "# AgentErrorBench evaluation report",
        "",
        "## Run identity",
        "",
        f"- Dataset path: `{dataset.root}`",
        f"- Dataset version: `{dataset.version}`",
        f"- Dataset manifest SHA-256: `{dataset.dataset_sha256}`",
        f"- Cohort: `{(run_metadata.get('selection') or {}).get('cohort')}`",
        f"- Cohort manifest: `{(run_metadata.get('selection') or {}).get('cohort_manifest_path')}`",
        f"- Cohort SHA-256: `{(run_metadata.get('selection') or {}).get('cohort_sha256')}`",
        f"- Run started: `{run_metadata.get('started_at')}`",
        f"- Run finished: `{run_metadata.get('finished_at')}`",
        f"- Duration seconds: `{run_metadata.get('duration_seconds')}`",
        f"- Provider: `{run_metadata.get('provider')}`",
        f"- Endpoint: `{run_metadata.get('endpoint')}`",
        f"- Model: `{run_metadata.get('model')}`",
        f"- Temperature: `{run_metadata.get('temperature')}`",
        f"- Max output tokens: `{run_metadata.get('max_output_tokens')}`",
        f"- Timeout seconds: `{run_metadata.get('timeout')}`",
        f"- Max retries: `{run_metadata.get('max_retries')}`",
        f"- Workers: `{run_metadata.get('workers')}`",
        f"- Execution order: `{run_metadata.get('execution_order')}`",
        f"- Prompt versions: `{json.dumps(run_metadata.get('prompt_versions'), sort_keys=True)}`",
        (
            "- Production two-stage pipeline: "
            f"`{run_metadata.get('production_two_stage_pipeline_version')}`"
        ),
        (
            "- Evidence validation version: "
            f"`{run_metadata.get('evidence_validation_version')}`"
        ),
        f"- Transport policy: `{run_metadata.get('transport_policy_version')}`",
        (
            "- Preregistration: "
            f"`{json.dumps(run_metadata.get('preregistration'), sort_keys=True)}`"
        ),
        f"- Released labels: **{len(dataset.labels)}**",
        f"- Source trajectories found: **{len(dataset.trajectory_file_sha256)}**",
        f"- Canonical adaptations completed: **{dataset.canonical_conversion_count}**",
        f"- Gold-mappable judge inputs: **{len(dataset.examples)}**",
        f"- LLM-evaluated trajectories: **{run_metadata.get('judge_input_count')}**",
        f"- Metric cohort trajectories: **{run_metadata.get('metric_cohort_count')}**",
        f"- Prediction records: **{len(predictions)}**",
        "",
        "This run evaluates the available AgentErrorBench release cohort. The "
        "release has no official train/dev/test field, so these results are not "
        "described as held-out test results. No gold reasoning or label is sent "
        "to either judge.",
        "",
        "## Overall exact metrics",
        "",
        "| Method | N | Step Exact | Step+Module | All Correct | Failed outputs |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method, values in sorted(by_method.items()):
        lines.append(_metric_row(method, values["overall"]))

    lines.extend(
        [
            "",
            "Failed calls, malformed JSON, illegal taxonomy values, evidence "
            "validation failures, and unmapped event IDs remain in every eligible "
            "denominator and receive no credit. All Correct excludes only rows "
            "whose released `failure_type` is empty; those rows remain in Step "
            "and Step+Module.",
            "",
            "## Environment breakdown",
            "",
        ]
    )
    for environment in ("alfworld", "gaia", "webshop"):
        lines.extend(
            [
                f"### {environment}",
                "",
                "| Method | N | Step Exact | Step+Module | All Correct | Failed outputs |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for method, values in sorted(by_method.items()):
            lines.append(_metric_row(method, values["by_environment"][environment]))
        lines.append("")

    lines.extend(["## Error-type breakdown", ""])
    for method, values in sorted(by_method.items()):
        lines.extend(
            [
                f"### {method}",
                "",
                "| Gold error type | N | Step Exact | Step+Module | All Correct |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for error_type, result in values["by_error_type"].items():
            lines.append(
                f"| `{error_type}` | {result['trajectory_count']} | "
                f"{_percent(result['step_exact']['accuracy'])} | "
                f"{_percent(result['step_module_exact']['accuracy'])} | "
                f"{_percent(result['all_correct']['accuracy'])} |"
            )
        lines.append("")

    lines.extend(["## Direct Prompting vs two-stage", ""])
    comparison = metrics.get("method_comparison") or {}
    if comparison:
        lines.extend(
            [
                "| Metric | Direct | Two-stage | Delta |",
                "|---|---:|---:|---:|",
            ]
        )
        for metric_name, values in comparison.items():
            lines.append(
                f"| {metric_name} | {_percent(values['direct'])} | "
                f"{_percent(values['two_stage'])} | "
                f"{_percent(values['two_stage_minus_direct'])} |"
            )
    else:
        lines.append("Both methods were not present, so no paired comparison is available.")

    phase1 = metrics["phase1_metrics"]
    lines.extend(
        [
            "",
            "## Intermediate local-candidate metrics",
            "",
            (
                "**Not computable.** The release supplies only one final "
                "critical annotation rather than exhaustive local-candidate "
                f"labels. {phase1['reason']}"
            ),
        ]
    )

    lines.extend(["", "## Provider transport telemetry", ""])
    if isinstance(provider_telemetry, Mapping):
        token_totals = provider_telemetry.get(
            "provider_usage_token_totals"
        )
        if not isinstance(token_totals, Mapping):
            token_totals = {}
        finish_reasons = provider_telemetry.get("finish_reason_counts")
        if not isinstance(finish_reasons, Mapping):
            finish_reasons = {}
        lines.extend(
            [
                f"- Logical completions: **{provider_telemetry.get('logical_completion_count', 0)}**",
                f"- Actual HTTP attempts: **{provider_telemetry.get('http_attempt_count', 0)}**",
                f"- Retry attempts: **{provider_telemetry.get('retry_count', 0)}**",
                f"- Request input characters across HTTP attempts: **{provider_telemetry.get('request_input_chars', 0)}**",
                f"- Responses with provider usage: **{provider_telemetry.get('provider_usage_response_count', 0)}**",
                f"- Provider input tokens: **{token_totals.get('input_tokens', 0)}**",
                f"- Provider output tokens: **{token_totals.get('output_tokens', 0)}**",
                f"- Provider total tokens: **{token_totals.get('total_tokens', 0)}**",
                f"- Finish reasons: `{json.dumps(dict(finish_reasons), sort_keys=True)}`",
                "",
                "Telemetry is aggregate-only. Input characters include retries; "
                "credentials and request/response bodies are never retained in "
                "the benchmark artifacts.",
            ]
        )
    else:
        lines.append(
            "The configured judge does not expose provider transport telemetry."
        )

    isolation = run_metadata.get("gold_isolation")
    telemetry_coverage = run_metadata.get("provider_telemetry_coverage")
    lines.extend(
        [
            "",
            "## Production integrity",
            "",
            (
                "- Gold-isolated prediction: "
                f"`{json.dumps(isolation, sort_keys=True)}`"
            ),
            (
                "- Provider telemetry coverage: "
                f"`{json.dumps(telemetry_coverage, sort_keys=True)}`"
            ),
            (
                "- Evidence repair eligible / attempted / applied: "
                f"**{run_metadata.get('repair_eligible_count')} / "
                f"{run_metadata.get('repair_attempt_count')} / "
                f"{run_metadata.get('repair_applied_count')}**"
            ),
            (
                "- Logical-completion budget used / maximum: "
                f"**{run_metadata.get('logical_completion_budget_used')} / "
                f"{run_metadata.get('max_logical_completions')}**"
            ),
        ]
    )

    lines.extend(
        [
            "",
            "## Output and provider failures",
            "",
            "| Method | Status counts | Failure-code counts |",
            "|---|---|---|",
        ]
    )
    for method, values in sorted(by_method.items()):
        overall = values["overall"]
        lines.append(
            f"| {method} | `{json.dumps(overall['status_counts'], sort_keys=True)}` | "
            f"`{json.dumps(overall['failure_code_counts'], sort_keys=True)}` |"
        )

    lines.extend(
        [
            "",
            "## Conversion and release integrity",
            "",
            f"- Missing trajectory files: **{len(dataset.unavailable)}**",
            f"- Conversion failures: **{len(dataset.conversion_failures)}**",
            f"- Canonical adaptations: **{dataset.canonical_conversion_count}/{len(dataset.labels)}**",
            f"- Evaluation-ready after gold mapping: **{len(dataset.examples)}/{len(dataset.labels)}**",
            f"- All Correct gold-type eligible: **{sum(label.error_type is not None for label in dataset.labels)}/{len(dataset.labels)}**",
            f"- Step mapping rule: {dataset.examples[0].mapping.step_rule if dataset.examples else 'N/A'}",
            "",
            "Raw release labels are preserved. Schema normalization is recorded "
            "separately:",
            "",
        ]
    )
    lines.extend(f"- {rule}" for rule in dataset.normalization_rules)
    if dataset.unavailable:
        lines.extend(["", "Unavailable trajectory IDs:", ""])
        lines.extend(
            f"- `{row['trajectory_id']}`: {row['reason']}"
            for row in dataset.unavailable[:50]
        )
        if len(dataset.unavailable) > 50:
            lines.append(
                f"- … {len(dataset.unavailable) - 50} more; see `metrics.json`."
            )
    if dataset.conversion_failures:
        lines.extend(["", "Conversion failures:", ""])
        lines.extend(
            f"- `{row.get('trajectory_id')}`: {row.get('reason')}"
            for row in dataset.conversion_failures[:50]
        )

    cases = _representative_errors(predictions)
    lines.extend(
        [
            "",
            "## Representative error cases",
            "",
        ]
    )
    if cases:
        for index, row in enumerate(cases, 1):
            lines.extend(
                [
                    f"### {index}. {row.get('trajectory_id')} / {row.get('method')}",
                    "",
                    f"- Environment: `{row.get('environment')}`",
                    f"- Status: `{row.get('status')}`"
                    + (
                        f" (`{row.get('failure_code')}`)"
                        if row.get("failure_code")
                        else ""
                    ),
                    f"- Gold: step `{row.get('gold_step')}`, module "
                    f"`{row.get('gold_module')}`, type `{row.get('gold_error_type')}`",
                    f"- Prediction: step `{row.get('predicted_step')}`, module "
                    f"`{row.get('predicted_module')}`, type "
                    f"`{row.get('predicted_error_type')}`",
                    f"- Root summary: {str(row.get('root_cause') or row.get('failure_message') or 'N/A')[:500]}",
                    "",
                ]
            )
    else:
        lines.append(
            "No incorrect or failed prediction exists in this run, so ten genuine "
            "error cases cannot be fabricated."
        )

    lines.extend(
        [
            "## Limits for real OpenClaw generalization",
            "",
            "AgentErrorBench measures agreement with its released critical-step, "
            "module, and error-type annotations. Its trajectories use benchmark "
            "environment message logs with embedded module markup; they do not "
            "exercise OpenClaw session-v3 branches, runtime dispatch records, "
            "tool-call/result joins, permissions, long-lived memory, or production "
            "connector failures. A positive benchmark result therefore validates "
            "the Canonical-Trace judge pipeline on AgentErrorBench, not generalization "
            "to real OpenClaw deployments.",
            "",
            "The label release also provides only one critical annotation per "
            "trajectory. It cannot validate Phase 1 recall over all actual errors.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    *,
    output_dir: str | Path,
    dataset: BenchmarkDataset,
    predictions: list[Mapping[str, Any]],
    metrics: dict[str, Any],
    run_metadata: Mapping[str, Any],
) -> dict[str, str]:
    root = Path(output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    predictions_path = root / "predictions.jsonl"
    predictions_path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, default=str) + "\n"
            for row in predictions
        ),
        encoding="utf-8",
    )
    csv_path = root / "per_example.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in predictions:
            writer.writerow({field: row.get(field) for field in CSV_FIELDS})

    metrics_document = {
        "run": dict(run_metadata),
        "dataset": dataset.audit_dict(),
        "metrics": metrics,
    }
    metrics_path = root / "metrics.json"
    metrics_path.write_text(
        json.dumps(metrics_document, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    report_path = root / "report.md"
    report_path.write_text(
        render_report(
            dataset=dataset,
            predictions=predictions,
            metrics=metrics,
            run_metadata=run_metadata,
        ),
        encoding="utf-8",
    )
    final_files = {
        "predictions": predictions_path,
        "per_example": csv_path,
        "metrics": metrics_path,
        "report": report_path,
    }
    isolation = run_metadata.get("gold_isolation")
    upstream: dict[str, dict[str, Any]] = {}
    if isinstance(isolation, Mapping):
        for name, field in (
            ("prediction_manifest", "prediction_manifest_path"),
            ("unscored_predictions", "unscored_predictions_path"),
            ("predict_run", "predict_run_metadata_path"),
        ):
            raw_path = isolation.get(field)
            if not isinstance(raw_path, str):
                continue
            path = Path(raw_path).expanduser().resolve()
            if not path.is_file():
                continue
            upstream[name] = {
                "path": str(path),
                "file_sha256": _file_sha256(path),
            }
    artifact_manifest = {
        "schema_version": ARTIFACT_MANIFEST_SCHEMA_VERSION,
        "dataset_manifest_sha256": dataset.dataset_sha256,
        "cohort_sha256": (
            (run_metadata.get("selection") or {}).get("cohort_sha256")
            if isinstance(run_metadata.get("selection"), Mapping)
            else None
        ),
        "production_pipeline_version": run_metadata.get(
            "production_two_stage_pipeline_version"
        ),
        "predict_run_sha256": (
            isolation.get("predict_run_sha256")
            if isinstance(isolation, Mapping)
            else None
        ),
        "files": {
            name: {
                "path": str(path),
                "file_sha256": _file_sha256(path),
            }
            for name, path in final_files.items()
        },
        "upstream": upstream,
    }
    artifact_manifest["artifact_manifest_sha256"] = stable_sha256(
        artifact_manifest
    )
    artifact_manifest_path = root / "artifact-manifest.json"
    artifact_manifest_path.write_text(
        json.dumps(
            artifact_manifest,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        **{
            name: str(path)
            for name, path in final_files.items()
        },
        "artifact_manifest": str(artifact_manifest_path),
    }
