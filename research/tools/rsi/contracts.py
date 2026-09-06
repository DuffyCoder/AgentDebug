"""Offline, deterministic prototype contracts for the proposed diagnosis task.

These functions neither execute submissions nor establish a security boundary.
The official two-container harness must call them (or its reviewed equivalent)
after executing submitted CODE on sealed inputs. Never grade answer uploads.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence

IDENTITY_FIELDS = ("trajectory_id", "source_task_id", "trajectory_sha256")
GOLD_KEYS = {"critical_failure_step", "critical_failure_module", "step_annotations",
             "critical_failure_type", "failure_types", "failure_reasonings", "failure_modules",
             "predicted_step", "predicted_module", "predicted_error_type", "score",
             "all_correct", "step_exact", "step_module_exact", "labels"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def assert_no_label_fields(value) -> None:
    """Structural screen only; text and semantic leakage also need human review."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).casefold()
            require(normalized not in GOLD_KEYS and not normalized.startswith("gold_"),
                    "label field in agent-visible input")
            assert_no_label_fields(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_label_fields(child)


def _split_identity(rows: Sequence[dict]) -> dict[str, set[str]]:
    require(isinstance(rows, list) and bool(rows), "each split must be a non-empty list")
    sets = {key: set() for key in IDENTITY_FIELDS}
    for row in rows:
        require(isinstance(row, dict), "invalid split row")
        for key in IDENTITY_FIELDS:
            value = row.get(key)
            require(isinstance(value, str) and bool(value.strip()), f"missing {key}")
            require(value == value.strip(), f"non-canonical {key}")
            sets[key].add(value)
        digest = row["trajectory_sha256"]
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "invalid trajectory SHA-256")
    require(len(sets["trajectory_id"]) == len(rows), "duplicate trajectory IDs within split")
    require(len(sets["trajectory_sha256"]) == len(rows), "duplicate trajectories within split")
    return sets


def audit_split(visible: list[dict], hidden: list[dict]) -> dict:
    """Group by reviewed underlying task identity, not source-model prefix.

    Repeated rollouts for one source task may stay WITHIN a split, never across.
    The returned audit intentionally contains no hidden IDs or content hashes.
    """
    left, right = _split_identity(visible), _split_identity(hidden)
    for key in IDENTITY_FIELDS:
        require(not left[key] & right[key], f"visible/hidden overlap in {key}")
    return {"schema_version": "agentdebug.rsi-split-audit.v1", "passed": True,
            "visible_count": len(visible), "hidden_count": len(hidden),
            "visible_source_task_count": len(left["source_task_id"]),
            "hidden_source_task_count": len(right["source_task_id"]),
            "identity_fields_checked": list(IDENTITY_FIELDS),
            "semantic_near_duplicate_review_required": True,
            "source_task_mapping_review_required": True}


def score_step_exact(cases: list[dict], labels: list[dict], predictions: list[dict],
                     allowed_pairs: set[tuple[str, str]]) -> dict:
    """Fixed-denominator Step Exact with deterministic output legality gates.

    cases: [{trajectory_id, steps: [{step, owners: {module: exact_text}}]}]
    labels: [{trajectory_id, step}] (trusted, never passed to candidate code)
    predictions: [{trajectory_id, status, predicted_step, predicted_module,
                   predicted_error_type, evidence_quote}]
    Owner projection and taxonomy are trusted inputs, never submission fields.
    This proposed projection is NOT yet a validated adapter for the old runs.
    """
    require(bool(cases) and isinstance(cases, list), "empty evaluation split")
    require(bool(allowed_pairs), "trusted taxonomy is required")
    assert_no_label_fields(cases)
    case_map = {}
    for case in cases:
        identity = case.get("trajectory_id")
        require(isinstance(identity, str) and bool(identity), "invalid case identity")
        require(identity not in case_map, "duplicate case identity")
        steps = case.get("steps")
        require(isinstance(steps, list) and bool(steps), "case has no steps")
        owners = {}
        for item in steps:
            step = item.get("step")
            require(type(step) is int and step > 0 and step not in owners, "invalid source step")
            require(isinstance(item.get("owners"), dict) and bool(item["owners"]), "missing owner projection")
            require(all(isinstance(k, str) and isinstance(v, str) for k, v in item["owners"].items()), "invalid owner text")
            owners[step] = item["owners"]
        case_map[identity] = owners
    gold = {}
    for label in labels:
        identity, step = label.get("trajectory_id"), label.get("step")
        require(isinstance(identity, str) and identity in case_map and identity not in gold, "invalid gold identity")
        require(type(step) is int and step > 0, "invalid gold step")
        # A released out-of-range gold step remains in the denominator. Do not
        # silently fix or drop it after seeing which method gets it wrong.
        gold[identity] = step
    require(set(gold) == set(case_map), "gold membership differs from cases")
    require(isinstance(predictions, list), "predictions must be a list")
    predicted = {}
    for item in predictions:
        require(isinstance(item, dict), "prediction must be an object")
        identity = item.get("trajectory_id")
        require(isinstance(identity, str) and identity in case_map, "unknown prediction identity")
        require(identity not in predicted, "duplicate prediction identity")
        predicted[identity] = item
    correct = invalid = 0
    fields = {"trajectory_id", "status", "predicted_step", "predicted_module",
              "predicted_error_type", "evidence_quote"}
    for identity, owners in case_map.items():
        item = predicted.get(identity, {})
        step, module = item.get("predicted_step"), item.get("predicted_module")
        error_type, quote = item.get("predicted_error_type"), item.get("evidence_quote")
        legal = (set(item) == fields and item.get("status") == "success"
                 and type(step) is int and step in owners
                 and isinstance(module, str) and isinstance(error_type, str)
                 and (module, error_type) in allowed_pairs
                 and isinstance(quote, str) and bool(quote.strip())
                 and module in owners[step] and quote in owners[step][module])
        if not legal:
            invalid += 1
        else:
            correct += int(step == gold[identity])
    return {"metric": "step_exact", "direction": "maximize", "unit": "fraction",
            "value": correct / len(cases), "correct": correct,
            "denominator": len(cases), "invalid_or_missing": invalid,
            "normalized_rsi_score": None}
