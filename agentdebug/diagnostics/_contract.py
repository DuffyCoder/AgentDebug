"""Persisted, gold-isolated Codex Agent Judge protocol.

This module deliberately stops at the prediction boundary.  It can construct
the complete task given to a Codex subagent and can audit the resulting
predictions against label-free inputs.  It never loads benchmark gold and it
does not score predictions.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .judge_view import JudgeExecutionFacts, JudgeView
from .taxonomy import (
    AgentModule,
    ErrorType,
    is_valid_classification,
    taxonomy_prompt,
)


AGENT_JUDGE_VERSION = "agentdebug.codex-agent-judge.v1"
AGENT_JUDGE_MODEL = "gpt-5.6-terra"
AGENT_JUDGE_REASONING_EFFORT = "medium"
AGENT_JUDGE_AUDIT_SCHEMA_VERSION = "agentdebug.codex-agent-judge-audit.v1"

# The subagent receives complete semantic inputs in the PredictionManifest.
# Keeping the read allowlist this small prevents accidental benchmark leakage.
GOLD_ISOLATION_READ_ALLOWLIST = (
    "the exact prediction_manifest_path named in the task",
    "the exact cohort_manifest_path named in the task",
    "agentdebug/diagnostics/_contract.py",
    "agentdebug/diagnostics/taxonomy.py",
)
GOLD_ISOLATION_READ_DENYLIST = (
    "data/AgentErrorBench/Label/**",
    "metrics.json and any scoring or comparison artifact",
    "scored*.json* and per-example*.json*",
    "promotion.json",
    "docs/experiments/**",
    "old predictions, including unscored-predictions.jsonl",
    "cached model replies or provider responses",
    "any gold label, prior answer, case study, or evaluator annotation",
    "git history",
)

AGENT_JUDGE_PREDICTION_FIELDS = frozenset(
    {
        "trajectory_id",
        "trajectory_sha256",
        "status",
        "predicted_step",
        "predicted_module",
        "predicted_error_type",
        "evidence_quote",
        "root_cause",
        "causal_summary",
        "rejected_adjacent_owner",
    }
)

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_FORBIDDEN_INPUT_FILENAMES = {
    "metrics.json",
    "promotion.json",
    "unscored-predictions.jsonl",
}
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


class AgentJudgeValidationError(ValueError):
    """A frozen Agent Judge artifact violates its gold-free contract."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _fail(code: str, message: str) -> None:
    raise AgentJudgeValidationError(code, message)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail("duplicate_json_key", f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_json(path: Path, *, role: str) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except AgentJudgeValidationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _fail("invalid_json", f"{role} is missing or invalid JSON: {error}")


def _assert_safe_path(path: Path, *, role: str, is_output: bool = False) -> None:
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
        _fail(
            "forbidden_artifact_path",
            f"{role} is covered by the Agent Judge gold-isolation denylist",
        )
    if not is_output and not path.is_file():
        _fail("missing_input", f"{role} does not exist: {path}")


def _assert_gold_free(value: Any, *, location: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).casefold()
            if (
                normalized in _FORBIDDEN_CONTENT_KEYS
                or normalized.startswith("gold_")
            ):
                _fail(
                    "forbidden_gold_field",
                    f"{location} contains forbidden field {key!r}",
                )
            _assert_gold_free(item, location=f"{location}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_gold_free(item, location=f"{location}[{index}]")


def _execution_fact_lines(facts: JudgeExecutionFacts | None) -> tuple[str, ...]:
    if facts is None:
        return ()
    lines: list[str] = []
    if facts.metadata_steps is not None:
        lines.append(f"benchmark.metadata.steps={facts.metadata_steps}")
    if facts.metadata_won is not None:
        lines.append(
            "benchmark.metadata.won="
            + json.dumps(facts.metadata_won, ensure_ascii=False)
        )
    if facts.metadata_success is not None:
        lines.append(
            "benchmark.metadata.success="
            + json.dumps(facts.metadata_success, ensure_ascii=False)
        )
    lines.append(f"canonical.turn_count={facts.canonical_turn_count}")
    if facts.final_stop_reason is not None:
        lines.append(
            "canonical.final_stop_reason="
            + json.dumps(facts.final_stop_reason, ensure_ascii=False)
        )
    if facts.final_error_message is not None:
        lines.append(
            "canonical.final_error_message="
            + json.dumps(facts.final_error_message, ensure_ascii=False)
        )
    return tuple(lines)


def _string_leaves(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Mapping):
        return tuple(
            text
            for item in value.values()
            for text in _string_leaves(item)
        )
    if isinstance(value, (list, tuple)):
        return tuple(
            text for item in value for text in _string_leaves(item)
        )
    return ()


def _owner_sources(
    view: JudgeView,
    *,
    predicted_step: int,
    module: AgentModule,
) -> tuple[str, ...]:
    """Return exact source strings available to one selected owner.

    Tagged traces use their observable module spans.  Action also owns its
    concrete tool-call name and string arguments.  For tag-free OpenClaw
    traces the complete assistant output is the only lossless semantic source,
    so deterministic validation binds the quote to that step while the Agent
    Judge remains responsible for semantic ownership.  System is stricter:
    only one of the provenance-backed execution-fact lines at the final step
    is accepted.
    """

    if module == AgentModule.SYSTEM:
        if predicted_step != len(view.steps):
            return ()
        return _execution_fact_lines(view.execution_facts)

    step = view.steps[predicted_step - 1]
    sources = [
        step.assistant_raw_output[span.tag_start_char : span.tag_end_char]
        for span in step.module_spans
        if span.module == module.value
    ]
    if module == AgentModule.ACTION:
        for call in step.tool_calls:
            sources.append(call.name)
            sources.extend(_string_leaves(call.arguments))
            sources.extend(_string_leaves(call.partial_arguments))
    if not sources and not step.module_spans and step.assistant_raw_output.strip():
        sources.append(step.assistant_raw_output)
    return tuple(dict.fromkeys(source for source in sources if source.strip()))


def _cohort_document(path: Path) -> dict[str, Any]:
    value = _load_json(path, role="cohort manifest")
    if not isinstance(value, dict):
        _fail("invalid_cohort", "cohort manifest must be a JSON object")
    _assert_gold_free(value, location="cohort manifest")
    required = {
        "cohort_name",
        "cohort_sha256",
        "dataset_manifest_sha256",
        "trajectory_ids",
    }
    if not required.issubset(value):
        _fail("invalid_cohort", "cohort manifest is missing public identity fields")
    trajectory_ids = value["trajectory_ids"]
    if (
        not isinstance(trajectory_ids, list)
        or not trajectory_ids
        or any(not isinstance(item, str) or not item for item in trajectory_ids)
        or len(set(trajectory_ids)) != len(trajectory_ids)
    ):
        _fail("invalid_cohort", "cohort trajectory_ids are invalid")
    body = dict(value)
    claimed_sha = body.pop("cohort_sha256")
    if not isinstance(claimed_sha, str) or claimed_sha != _stable_sha256(body):
        _fail("invalid_cohort_sha256", "cohort content hash is invalid")
    return value


def build_agent_judge_task(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> str:
    """Build the complete frozen task for a future Codex Agent Judge.

    The caller must spawn the subagent with :data:`AGENT_JUDGE_MODEL` and
    :data:`AGENT_JUDGE_REASONING_EFFORT`; the prompt records those immutable
    settings but cannot configure the orchestrator itself.
    """

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    output_path = Path(predictions_path).expanduser().resolve()
    _assert_safe_path(prediction_path, role="prediction manifest")
    _assert_safe_path(cohort_path, role="cohort manifest")
    _assert_safe_path(output_path, role="prediction output", is_output=True)

    schema = {
        "trajectory_id": "exact manifest trajectory ID",
        "trajectory_sha256": "exact manifest trajectory SHA-256",
        "status": "success",
        "predicted_step": "positive integer",
        "predicted_module": "taxonomy module",
        "predicted_error_type": "valid type for that module",
        "evidence_quote": "exact non-empty owner substring",
        "root_cause": "concise root-cause explanation",
        "causal_summary": "counterfactual and recovery conclusion",
        "rejected_adjacent_owner": "adjacent alternative and rejection reason",
    }
    allowlist = "\n".join(f"- {item}" for item in GOLD_ISOLATION_READ_ALLOWLIST)
    denylist = "\n".join(f"- {item}" for item in GOLD_ISOLATION_READ_DENYLIST)

    return f"""\
Run the frozen Codex Agent Judge protocol {AGENT_JUDGE_VERSION}.

IMMUTABLE EXECUTION CONFIGURATION
- model: {AGENT_JUDGE_MODEL}
- reasoning_effort: {AGENT_JUDGE_REASONING_EFFORT}
- mode: independent open-ended Agent Judge
- external LLM/API/network calls: forbidden
- scoring or gold-label access: forbidden

INPUT/OUTPUT BOUNDARY
- prediction manifest: {prediction_path}
- prediction manifest file sha256: {_file_sha256(prediction_path)}
- cohort manifest: {cohort_path}
- cohort manifest file sha256: {_file_sha256(cohort_path)}
- write predictions only to: {output_path}

Read cases only from the prediction manifest and process exactly once in the
cohort order.  Do not inspect directories to look for more context.  The
JudgeView in each manifest entry is complete and authoritative.

GOLD-ISOLATION READ ALLOWLIST
{allowlist}

GOLD-ISOLATION READ DENYLIST
{denylist}

THREE-STAGE / FIVE-STEP AGENT JUDGE PROTOCOL

Stage I — evidence investigation
1. Reconstruct the task objective, explicit constraints, chronological world
   state, actions, observations, and observable terminal facts.  Use only
   facts available at each candidate output; never use hindsight to turn a
   reasonable initial probe into an error.
2. Enumerate at most three directly evidenced root candidates in chronological
   order.  Distinguish an independently defective owner output from a failed
   result, recoverable exploration, and a downstream symptom.

Stage II — causal attribution
3. For each candidate, run the causal counterfactual and recovery test: explain
   whether correcting only that output could prevent the failed trajectory,
   and whether the exact defect was later fully repaired.  Reject fully
   recovered defects and candidates that are merely improvable.
4. Compare adjacent ownership explicitly.  Audit memory against earlier
   history, reflection against the result/progress it assesses, planning with
   action hidden, and action against the current plan/interface.  Reject the
   strongest adjacent alternative in rejected_adjacent_owner.  Independently
   check system boundaries; use system only for an observable external limit
   or failure, never merely because the episode failed.  Step 1 has no earlier
   episode memory or feedback, so it cannot be memory/reflection ownership.

Stage III — final decision
5. Select the earliest mature, unrecovered, causally sufficient root.  Emit one
   legal taxonomy pair and one exact, contiguous, case-sensitive evidence
   substring owned by that module at that step.  For system, select the final
   step and quote only one observable execution_facts line.  Before writing,
   verify order, ID, SHA, step range, pair legality, ownership, and exact schema.

OWNERSHIP RULES
- memory: the memory text itself drops, fails to retrieve, or invents prior
  information; do not assign it a later planning consequence.
- reflection: the assessment itself misreads outcome, progress, or cause.
- planning: the plan remains defective when the concrete action is hidden.
- action: the concrete invocation/answer fails to implement an otherwise
  adequate plan, uses an invalid operation, bad syntax, or bad parameters.
- system: a provenance-backed external boundary/failure in execution_facts;
  it is available only at the final step.

AGENT ERROR TAXONOMY
{taxonomy_prompt()}

STRICT PREDICTION CONTRACT
Write one JSON array, with no envelope, Markdown, commentary, or trailing
content.  It must contain exactly one record per cohort case in exact cohort
and manifest order.  Every record must contain exactly these ten fields:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Every text field must be non-empty.  status must be exactly "success".
predicted_step must be a non-boolean positive integer within that JudgeView.
Do not emit confidence, score, probability, rank, vote, audit internals, source
IDs, aliases, nulls, or any additional field.  Do not copy or consult a prior
prediction.  The deterministic validator will reject rather than repair any
contract violation.
"""


OwnerSourceResolver = Callable[
    [JudgeView, int, AgentModule, ErrorType],
    tuple[str, ...],
]


def _v1_owner_source_resolver(
    view: JudgeView,
    predicted_step: int,
    module: AgentModule,
    _error_type: ErrorType,
) -> tuple[str, ...]:
    """Adapt the frozen v1 source policy to the injectable validator hook."""

    return _owner_sources(
        view,
        predicted_step=predicted_step,
        module=module,
    )


def _validate_agent_judge_predictions_with_owner_sources(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
    *,
    owner_source_resolver: OwnerSourceResolver,
) -> dict[str, Any]:
    """Validate predictions with one explicitly selected evidence policy.

    Protocol variants may inject only their selected-owner source resolver.
    Identity, order, structure, taxonomy, and all other fail-closed checks stay
    shared.  The function intentionally has no gold-label or scoring argument.
    """

    prediction_path = Path(prediction_manifest_path).expanduser().resolve()
    cohort_path = Path(cohort_manifest_path).expanduser().resolve()
    output_path = Path(predictions_path).expanduser().resolve()
    _assert_safe_path(prediction_path, role="prediction manifest")
    _assert_safe_path(cohort_path, role="cohort manifest")
    _assert_safe_path(output_path, role="prediction output")

    # Local import avoids a diagnostics/benchmark package initialization cycle.
    from agentdebug.benchmark.prediction_manifest import (  # noqa: PLC0415
        PredictionManifestError,
        load_prediction_manifest,
    )

    try:
        manifest, cases = load_prediction_manifest(prediction_path)
    except PredictionManifestError as error:
        _fail("invalid_prediction_manifest", str(error))
    cohort = _cohort_document(cohort_path)

    manifest_ids = [case.trajectory_id for case in cases]
    cohort_ids = cohort["trajectory_ids"]
    if manifest_ids != cohort_ids:
        _fail(
            "manifest_cohort_order_mismatch",
            "prediction manifest IDs must exactly match cohort order",
        )
    if (
        manifest.get("cohort_name") != cohort.get("cohort_name")
        or manifest.get("cohort_sha256") != cohort.get("cohort_sha256")
        or manifest.get("dataset_manifest_sha256")
        != cohort.get("dataset_manifest_sha256")
    ):
        _fail(
            "manifest_cohort_identity_mismatch",
            "prediction manifest and cohort public identities differ",
        )

    raw_predictions = _load_json(output_path, role="predictions")
    if not isinstance(raw_predictions, list):
        _fail("invalid_prediction_envelope", "predictions must be one JSON array")
    if len(raw_predictions) != len(cases):
        _fail(
            "invalid_prediction_count",
            "prediction count must equal the complete cohort count",
        )

    predicted_ids: list[str] = []
    for index, (raw, case) in enumerate(zip(raw_predictions, cases, strict=True)):
        location = f"predictions[{index}]"
        if not isinstance(raw, dict):
            _fail("invalid_prediction_record", f"{location} must be an object")
        fields = set(raw)
        if fields != AGENT_JUDGE_PREDICTION_FIELDS:
            missing = sorted(AGENT_JUDGE_PREDICTION_FIELDS - fields)
            extra = sorted(fields - AGENT_JUDGE_PREDICTION_FIELDS)
            _fail(
                "invalid_prediction_fields",
                f"{location} fields differ; missing={missing}, extra={extra}",
            )

        for field in AGENT_JUDGE_PREDICTION_FIELDS - {"predicted_step"}:
            if not isinstance(raw[field], str) or not raw[field].strip():
                _fail(
                    "invalid_prediction_value",
                    f"{location}.{field} must be non-empty text",
                )
        if raw["status"] != "success":
            _fail("invalid_status", f"{location}.status must equal 'success'")
        if raw["trajectory_id"] != case.trajectory_id:
            _fail(
                "cohort_order_mismatch",
                f"{location}.trajectory_id is not the expected cohort case",
            )
        predicted_ids.append(raw["trajectory_id"])
        if (
            _SHA256_RE.fullmatch(raw["trajectory_sha256"]) is None
            or raw["trajectory_sha256"] != case.trajectory_sha256
        ):
            _fail(
                "trajectory_sha256_mismatch",
                f"{location}.trajectory_sha256 differs from the manifest",
            )

        step = raw["predicted_step"]
        if (
            isinstance(step, bool)
            or not isinstance(step, int)
            or step < 1
            or step > len(case.judge_view.steps)
        ):
            _fail(
                "predicted_step_out_of_range",
                f"{location}.predicted_step must identify one JudgeView step",
            )
        try:
            module = AgentModule(raw["predicted_module"])
            error_type = ErrorType(raw["predicted_error_type"])
        except ValueError:
            _fail(
                "invalid_taxonomy_pair",
                f"{location} contains an unknown module or error type",
            )
        if not is_valid_classification(module, error_type):
            _fail(
                "invalid_taxonomy_pair",
                f"{location} contains an illegal module/error_type pair",
            )

        sources = owner_source_resolver(
            case.judge_view,
            step,
            module,
            error_type,
        )
        quote = raw["evidence_quote"]
        if not sources or not any(quote in source for source in sources):
            _fail(
                "invalid_evidence_ownership",
                f"{location}.evidence_quote is not owned by its step/module",
            )

    if predicted_ids != cohort_ids or len(set(predicted_ids)) != len(predicted_ids):
        _fail(
            "cohort_order_mismatch",
            "prediction IDs must be unique and follow the complete cohort order",
        )

    return {
        "schema_version": AGENT_JUDGE_AUDIT_SCHEMA_VERSION,
        "agent_judge_version": AGENT_JUDGE_VERSION,
        "model": AGENT_JUDGE_MODEL,
        "reasoning_effort": AGENT_JUDGE_REASONING_EFFORT,
        "gold_free_validation": True,
        "case_count": len(cases),
        "unique_trajectory_ids": len(set(predicted_ids)),
        "cohort_order_matches": True,
        "manifest_order_matches": True,
        "all_status_success": True,
        "all_predicted_steps_in_range": True,
        "all_taxonomy_pairs_valid": True,
        "all_evidence_quotes_found_in_selected_step_module": True,
        "forbidden_read_occurred": False,
        "input_sha256": {
            "prediction_manifest": _file_sha256(prediction_path),
            "cohort": _file_sha256(cohort_path),
        },
        "output_sha256": {
            "predictions.json": _file_sha256(output_path),
        },
        "validation_method": (
            "Gold-free exact JSON, cohort/manifest order, trajectory identity, "
            "step range, taxonomy pair, and selected-owner evidence checks."
        ),
    }


def validate_agent_judge_predictions(
    prediction_manifest_path: str | Path,
    cohort_manifest_path: str | Path,
    predictions_path: str | Path,
) -> dict[str, Any]:
    """Gold-free, fail-closed validation of frozen v1 predictions.

    V1 retains its original evidence-source behavior.  The private resolver
    hook exists so a later, independently versioned protocol can make a
    narrower evidence-policy change without mutating this public contract.
    """

    return _validate_agent_judge_predictions_with_owner_sources(
        prediction_manifest_path,
        cohort_manifest_path,
        predictions_path,
        owner_source_resolver=_v1_owner_source_resolver,
    )


__all__ = [
    "AGENT_JUDGE_AUDIT_SCHEMA_VERSION",
    "AGENT_JUDGE_MODEL",
    "AGENT_JUDGE_PREDICTION_FIELDS",
    "AGENT_JUDGE_REASONING_EFFORT",
    "AGENT_JUDGE_VERSION",
    "AgentJudgeValidationError",
    "GOLD_ISOLATION_READ_ALLOWLIST",
    "GOLD_ISOLATION_READ_DENYLIST",
    "build_agent_judge_task",
    "validate_agent_judge_predictions",
]
