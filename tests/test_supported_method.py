"""Synthetic end-to-end tests use the real frozen validators, never model calls."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdebug import method
from agentdebug.benchmark.adapter import adapt_trajectory
from agentdebug.benchmark.prediction_manifest import (
    load_prediction_manifest, stable_sha256, write_prediction_manifest,
)


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read(path):
    return json.loads(path.read_text())


@pytest.fixture
def inputs(tmp_path):
    source = tmp_path / "trace.json"
    write(source, {"messages": [
        {"role": "user", "content": "Inspect fact-a once."},
        {"role": "assistant", "content": "<memory>No prior work.</memory><reflection>Work has not started.</reflection><plan>Inspect fact-a.</plan><action>inspect[fact-a]</action>"},
        {"role": "user", "content": "fact-a was already checked."},
        {"role": "assistant", "content": "<memory>fact-a was checked.</memory><reflection>The task is incomplete.</reflection><plan>repeat known-bad search</plan><action>inspect[fact-a]</action>"},
    ], "metadata": {"steps": 2, "won": False, "success": False}})
    trace, mapping = adapt_trajectory(source, trajectory_id="synthetic-gaia")
    cohort = {"schema_version": "fixture.public-cohort.v1", "cohort_name": "synthetic",
              "dataset_manifest_sha256": "d" * 64, "trajectory_ids": [trace.trace_id],
              "entries": [{"trajectory_id": trace.trace_id, "environment": "gaia"}]}
    cohort["cohort_sha256"] = stable_sha256(cohort)
    cohort_path, manifest = tmp_path / "cohort.json", tmp_path / "prediction-manifest.json"
    write(cohort_path, cohort)
    write_prediction_manifest(traces_and_mappings=[(trace, mapping)],
        dataset_manifest_sha256="d" * 64, cohort_name="synthetic",
        cohort_sha256=cohort["cohort_sha256"], selection_identity={"algorithm": "synthetic"},
        output_path=manifest)
    return {"prediction_manifest": manifest, "cohort_manifest": cohort_path,
            "output_dir": tmp_path / "run"}


def complete_stage(request):
    """Generate structurally legal synthetic outputs, without bypassing validators."""
    directory = request.work_dir
    if request.stage == "anchor":
        _, cases = load_prediction_manifest(next((directory.parents[3] / "inputs").glob("*/prediction-manifest.json")))
        case = cases[0]
        prediction = {"trajectory_id": case.trajectory_id, "trajectory_sha256": case.trajectory_sha256,
            "status": "success", "predicted_step": 2, "predicted_module": "planning",
            "predicted_error_type": "inefficient_plan", "evidence_quote": "repeat known-bad search",
            "root_cause": "The plan repeats completed work.",
            "causal_summary": "Removing repetition prevents the failed detour.",
            "rejected_adjacent_owner": "Action faithfully implements the bad plan."}
        row = {"step": 1, "lane_a": "clear", "lane_b": "clear", "system": "clear",
            "lane_c": "veto_initial_probe", "surviving_lane": None, "evidence_quote": None,
            "decision_basis": "state_scope=memory_reflection; state_fidelity=faithful; Initial probe."}
        ledger = {"trajectory_id": case.trajectory_id, "rows": [row,
            {**row, "step": 2, "lane_c": "candidate", "surviving_lane": "lane_c",
             "evidence_quote": prediction["evidence_quote"],
             "decision_basis": "state_scope=memory_reflection; state_fidelity=faithful; Repeats completed work."}],
             "selected_step": 2}
        write(directory / "step-candidates.json", ledger)
        write(directory / "step-freeze.json", {"trajectory_id": case.trajectory_id, "predicted_step": 2})
        write(request.artifact_path, [prediction])
    else:
        anchor = read(directory / "anchor-predictions.json")[0]
        if request.stage == "challenger":
            challenger = {"trajectory_id": anchor["trajectory_id"], "trajectory_sha256": anchor["trajectory_sha256"],
                "anchor_prediction_sha256": stable_sha256(anchor),
                "anchor_ledger_sha256": stable_sha256(read(directory / "step-candidates.json")),
                "anchor_checkpoint_sha256": stable_sha256(read(directory / "step-freeze.json")),
                "anchor_step": 2, "challenge_status": "no_challenge", "anchor_classification": "critical_root",
                "anchor_veto_evidence_step": None, "anchor_veto_evidence_quote": None, "proposed_prediction": None,
                "anchor_falsifier": "No falsifier exists.", "anchor_only_repair_counterfactual": "Repair avoids repetition.",
                "proposal_only_repair_counterfactual": "No later step exists.",
                "direct_timeline_comparison": "No later step exists.", "search_summary": "Retain the anchor."}
            write(request.artifact_path, [challenger])
        else:
            challenger = read(directory / "challenger.json")[0]
            write(request.artifact_path, [{"trajectory_id": anchor["trajectory_id"],
                "trajectory_sha256": anchor["trajectory_sha256"],
                "anchor_prediction_sha256": stable_sha256(anchor), "challenger_sha256": stable_sha256(challenger),
                "anchor_step": 2, "decision": "keep_anchor", "frozen_step": 2,
                "selected_prediction_sha256": stable_sha256(anchor), "selected_prediction": anchor,
                "decision_basis": "No qualifying challenger.", "rejected_alternative_basis": "No later step exists."}])


def test_dry_run_is_neutral_and_does_not_call_executor(inputs):
    result = method.analyze(**inputs, executor=lambda request: pytest.fail("No inference"))
    assert result["method"] == "AgentDebug"
    assert result["status"] == "prepared"
    assert result["planned_sessions"] == 3
    assert result["model"] == "gpt-5.5"
    assert result["reasoning_effort"] == "medium"
    assert "v3" not in json.dumps(result)
    assert "v3.83" in (inputs["output_dir"] / "provenance.json").read_text()
    with pytest.raises(ValueError, match="already exists"):
        method.analyze(**inputs)


def test_dry_run_records_execution_budget_and_sandbox(inputs):
    result = method.analyze(**inputs, executor=method.CodexExecutor("custom-codex", 90))
    assert result["execution_backend"] == "codex-cli"
    assert result["runtime"]["binary"] == "custom-codex"
    assert result["runtime"]["stage_timeout_seconds"] == 90
    assert result["runtime"]["sandbox"] == "workspace-write"
    assert result["runtime"]["ephemeral"] is True


def test_full_run_uses_unchanged_prompt_and_real_validators(inputs):
    requests = []
    def execute(request):
        requests.append(request)
        complete_stage(request)
    result = method.analyze(**inputs, execute=True, executor=execute)
    assert result["status"] == "validated"
    assert [item.stage for item in requests] == list(method.STAGES)
    assert len({item.work_dir for item in requests}) == 3
    assert "PACKET-STATE CLOSURE" in requests[0].task
    assert "EARLIEST-CAUSAL SINGLE-CHALLENGER" in requests[1].task
    assert "Do not repair, rewrite, or invent a third prediction" in requests[2].task
    manifest = next((inputs["output_dir"] / "inputs").glob("*/prediction-manifest.json"))
    cohort = manifest.parent / "cohort.json"
    assert requests[0].task == method._protocol.build_anchor_task(manifest, cohort, requests[0].artifact_path)
    audit = read(inputs["output_dir"] / "prediction-audit.json")
    assert audit["all_selected_predictions_exact_copies"] is True
    assert audit["gold_free_validation"] is True
    assert read(inputs["output_dir"] / "predictions.json") == read(requests[0].artifact_path)


def test_invalid_output_retries_in_new_session_then_fails(inputs):
    requests = []
    def invalid(request):
        requests.append(request)
        write(request.artifact_path, [])
    with pytest.raises(RuntimeError, match="cases failed"):
        method.analyze(**inputs, execute=True, executor=invalid)
    assert [(item.stage, item.attempt) for item in requests] == [("anchor", 1), ("anchor", 2)]
    assert read(inputs["output_dir"] / "run.json")["status"] == "failed"
    assert not (inputs["output_dir"] / "predictions.json").exists()


def test_frozen_anchor_tampering_is_fatal(inputs):
    requests = []
    def mutate(request):
        requests.append(request)
        complete_stage(request)
        if request.stage == "challenger":
            write(request.work_dir / "anchor-predictions.json", [])
    with pytest.raises(RuntimeError, match="cases failed"):
        method.analyze(**inputs, execute=True, executor=mutate)
    assert [item.stage for item in requests] == ["anchor", "challenger"]


def test_transport_configuration_is_fixed_and_sandboxed(tmp_path, monkeypatch):
    captured = []
    def run(command, **kwargs):
        captured.append((command, kwargs))
        return type("Completed", (), {"returncode": 0})()
    monkeypatch.setattr(method.subprocess, "run", run)
    method.CodexExecutor()(method.StageRequest("anchor", 1, tmp_path, "synthetic", tmp_path / "anchor.json"))
    command, options = captured[0]
    assert command[command.index("--model") + 1] == "gpt-5.5"
    assert command[command.index("--sandbox") + 1] == "workspace-write"
    assert "--ephemeral" in command
    assert 'model_reasoning_effort="medium"' in command
    assert options["timeout"] == 1800
    assert options["input"] == "synthetic"


def test_retry_can_recover_without_reusing_failed_outputs(inputs):
    requests = []
    def execute(request):
        requests.append(request)
        if request.stage == "anchor" and request.attempt == 1:
            write(request.artifact_path, [])
        else:
            assert not request.artifact_path.exists()
            complete_stage(request)
    result = method.analyze(**inputs, execute=True, executor=execute)
    assert result["status"] == "validated"
    assert [(r.stage, r.attempt) for r in requests] == [
        ("anchor", 1), ("anchor", 2), ("challenger", 1), ("arbiter", 1)]


def test_arbiter_cannot_rewrite_anchor_even_with_recomputed_hash(inputs):
    def execute(request):
        complete_stage(request)
        if request.stage == "arbiter":
            value = read(request.artifact_path)
            value[0]["selected_prediction"]["root_cause"] = "Invented third prediction."
            value[0]["selected_prediction_sha256"] = stable_sha256(value[0]["selected_prediction"])
            write(request.artifact_path, value)
    with pytest.raises(RuntimeError, match="cases failed"):
        method.analyze(**inputs, execute=True, executor=execute)
    assert not (inputs["output_dir"] / "predictions.json").exists()


@pytest.mark.parametrize("mode", ["gold", "hash", "environment"])
def test_invalid_inputs_fail_before_creating_run_or_calling_model(inputs, mode):
    manifest_path, cohort_path = inputs["prediction_manifest"], inputs["cohort_manifest"]
    manifest = read(manifest_path)
    if mode == "gold":
        manifest["gold_answer"] = "forbidden"
    elif mode == "hash":
        manifest["prediction_manifest_sha256"] = "0" * 64
    else:
        cohort = read(cohort_path)
        cohort["entries"][0]["environment"] = "webshop"
        cohort.pop("cohort_sha256")
        cohort["cohort_sha256"] = stable_sha256(cohort)
        write(cohort_path, cohort)
        manifest["cohort_sha256"] = cohort["cohort_sha256"]
        manifest.pop("prediction_manifest_sha256")
        manifest["prediction_manifest_sha256"] = stable_sha256(manifest)
    write(manifest_path, manifest)
    with pytest.raises(ValueError):
        method.analyze(**inputs, execute=True, executor=lambda r: pytest.fail("No model allowed"))
    assert not inputs["output_dir"].exists()


def test_timeout_is_recorded_and_does_not_create_a_successful_run(inputs):
    def execute(request):
        raise method.subprocess.TimeoutExpired("synthetic", 1)
    with pytest.raises(RuntimeError, match="cases failed"):
        method.analyze(**inputs, execute=True, executor=execute, max_attempts=1)
    assert read(inputs["output_dir"] / "run.json")["status"] == "failed"


def test_final_validation_failure_updates_run_status(inputs, monkeypatch):
    def reject(**kwargs):
        raise ValueError("synthetic final validation failure")
    monkeypatch.setattr(method, "validate_predictions", reject)
    with pytest.raises(ValueError, match="final validation"):
        method.analyze(**inputs, execute=True, executor=complete_stage)
    assert read(inputs["output_dir"] / "run.json")["status"] == "failed"


def test_string_execution_flag_cannot_accidentally_start_model(inputs):
    with pytest.raises(ValueError, match="explicit boolean"):
        method.analyze(**inputs, execute="false")
    assert not inputs["output_dir"].exists()


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan")])
def test_invalid_executor_timeout_is_rejected_before_preparation(timeout):
    with pytest.raises(ValueError, match="positive finite"):
        method.CodexExecutor(timeout=timeout)
