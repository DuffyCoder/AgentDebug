from __future__ import annotations

import copy
import json

import pytest

from research.tools.rsi.check_readiness import DEFAULT, check
from research.tools.rsi.contracts import assert_no_label_fields, audit_split, score_step_exact


def inputs():
    cases = [
        {"trajectory_id": "synthetic-a", "steps": [
            {"step": 1, "owners": {"planning": "Propose an unverified route."}},
            {"step": 2, "owners": {"action": "The request failed."}},
        ]},
        {"trajectory_id": "synthetic-b", "steps": [
            {"step": 1, "owners": {"action": "The request succeeded."}},
        ]},
    ]
    labels = [{"trajectory_id": "synthetic-a", "step": 1}, {"trajectory_id": "synthetic-b", "step": 1}]
    predictions = [{"trajectory_id": "synthetic-a", "status": "success", "predicted_step": 1,
                    "predicted_module": "planning", "predicted_error_type": "synthetic-type",
                    "evidence_quote": "unverified route"}]
    return cases, labels, predictions, {("planning", "synthetic-type"), ("action", "synthetic-type")}


def test_missing_cases_stay_in_denominator():
    result = score_step_exact(*inputs())
    assert result["value"] == 0.5
    assert result["denominator"] == 2
    assert result["invalid_or_missing"] == 1
    assert result["normalized_rsi_score"] is None


@pytest.mark.parametrize("change", [
    {"predicted_step": True}, {"predicted_step": 100},
    {"predicted_module": "action"}, {"predicted_module": []},
    {"predicted_error_type": "not-in-taxonomy"}, {"evidence_quote": ""},
    {"evidence_quote": "  "}, {"evidence_quote": "fabricated text"},
    {"status": "failed"}, {"gold_step": 1},
])
def test_illegal_outputs_earn_zero_without_dropping_cases(change):
    cases, labels, predictions, pairs = inputs()
    predictions[0].update(change)
    result = score_step_exact(cases, labels, predictions, pairs)
    assert result["value"] == 0
    assert result["denominator"] == 2


def test_valid_but_wrong_step_earns_zero():
    cases, labels, predictions, pairs = inputs()
    predictions[0].update(predicted_step=2, predicted_module="action", evidence_quote="request failed")
    result = score_step_exact(cases, labels, predictions, pairs)
    assert result["value"] == 0
    assert result["invalid_or_missing"] == 1


@pytest.mark.parametrize("duplicate", [True, False])
def test_duplicate_or_unknown_identity_is_rejected(duplicate):
    cases, labels, predictions, pairs = inputs()
    if duplicate:
        predictions.append(copy.deepcopy(predictions[0]))
    else:
        predictions[0]["trajectory_id"] = "unknown"
    with pytest.raises(ValueError):
        score_step_exact(cases, labels, predictions, pairs)


def test_empty_output_zero_and_empty_dataset_rejected():
    cases, labels, _, pairs = inputs()
    assert score_step_exact(cases, labels, [], pairs)["value"] == 0
    with pytest.raises(ValueError):
        score_step_exact([], [], [], pairs)


def test_released_unmappable_gold_is_not_silently_removed():
    cases, labels, predictions, pairs = inputs()
    labels[0]["step"] = 99
    result = score_step_exact(cases, labels, predictions, pairs)
    assert result["value"] == 0 and result["denominator"] == 2


@pytest.mark.parametrize("field", ["gold_step", "step_annotations", "critical_failure_step", "labels",
                                  "critical_failure_type", "predicted_step", "failure_reasonings"])
def test_nested_labels_cannot_enter_visible_structured_input(field):
    with pytest.raises(ValueError, match="label field"):
        assert_no_label_fields({"steps": [{field: 1}]})


def manifest(identity="rollout-a", task="underlying-task-a", digest="a"):
    return [{"trajectory_id": identity, "source_task_id": task, "trajectory_sha256": digest * 64}]


def test_split_audit_does_not_publish_hidden_ids():
    report = audit_split(manifest(), manifest("private-rollout", "private-task", "b"))
    assert report["passed"]
    assert "private" not in json.dumps(report)
    assert report["semantic_near_duplicate_review_required"]


@pytest.mark.parametrize("field", ["trajectory_id", "source_task_id", "trajectory_sha256"])
def test_split_rejects_shared_tasks_even_if_rollout_model_or_id_differs(field):
    visible, hidden = manifest(), manifest("another-model-rollout", "other-task", "b")
    hidden[0][field] = visible[0][field]
    with pytest.raises(ValueError, match="overlap"):
        audit_split(visible, hidden)


def test_split_rejects_empty_or_duplicate_records():
    with pytest.raises(ValueError):
        audit_split([], manifest())
    with pytest.raises(ValueError, match="duplicate"):
        audit_split(manifest() * 2, manifest("b", "b", "b"))


def test_readiness_does_not_claim_completed_benchmark():
    report = check()
    assert report["ledger_valid"]
    assert not report["formal_task_ready"]
    assert report["open_gate_count"] == 8
    assert all(x is None for x in report["sealed_anchors"].values())


def test_cannot_mark_a_gate_verified_without_evidence(tmp_path):
    data = json.loads(DEFAULT.read_text())
    data["requirements"][0]["status"] = "verified"
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="evidence"):
        check(path)


def test_cannot_remove_required_gate(tmp_path):
    data = json.loads(DEFAULT.read_text())
    data["requirements"].pop()
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="removed"):
        check(path)
