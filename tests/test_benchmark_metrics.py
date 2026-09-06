from agentdebug.benchmark.metrics import compute_metrics


def _record(
    trajectory_id,
    *,
    step,
    module,
    error_type,
    status="success",
):
    return {
        "trajectory_id": trajectory_id,
        "environment": "alfworld",
        "method": "direct",
        "status": status,
        "failure_code": None,
        "gold_step": 2,
        "gold_module": "planning",
        "gold_error_type": "inefficient_plan",
        "predicted_step": step,
        "predicted_module": module,
        "predicted_error_type": error_type,
        "step_exact": status == "success" and step == 2,
        "step_module_exact": (
            status == "success" and step == 2 and module == "planning"
        ),
        "all_correct": (
            status == "success"
            and step == 2
            and module == "planning"
            and error_type == "inefficient_plan"
        ),
    }


def test_three_exact_metrics_have_hand_checked_denominators():
    rows = [
        _record(
            "all-correct",
            step=2,
            module="planning",
            error_type="inefficient_plan",
        ),
        _record(
            "step-only",
            step=2,
            module="reflection",
            error_type="progress_misjudge",
        ),
        _record(
            "wrong-step",
            step=1,
            module="planning",
            error_type="inefficient_plan",
        ),
    ]
    result = compute_metrics(rows)["by_method"]["direct"]["overall"]

    assert result["step_exact"] == {
        "correct": 2,
        "denominator": 3,
        "accuracy": 2 / 3,
    }
    assert result["step_module_exact"] == {
        "correct": 1,
        "denominator": 3,
        "accuracy": 1 / 3,
    }
    assert result["all_correct"]["correct"] == 1
    assert result["all_correct"]["denominator"] == 3
    assert result["all_correct"]["accuracy"] == 1 / 3
    assert "confidence" not in result


def test_invalid_output_remains_in_denominator_and_gets_no_credit():
    invalid = _record(
        "invalid",
        step=2,
        module="planning",
        error_type="inefficient_plan",
        status="invalid_taxonomy",
    )
    result = compute_metrics([invalid])["by_method"]["direct"]["overall"]

    assert result["trajectory_count"] == 1
    assert result["failed_prediction_count"] == 1
    assert result["step_exact"]["denominator"] == 1
    assert result["step_exact"]["correct"] == 0
    assert result["all_correct"]["denominator"] == 1
    assert result["all_correct"]["correct"] == 0
