"""Post-validation scoring retains original released-step and denominator rules."""
from types import SimpleNamespace

import pytest

from agentdebug.benchmark import scoring
from agentdebug.benchmark.metrics import compute_metrics
from agentdebug.benchmark.models import GoldLabel


def score(*, gold_step=2, error_type="inefficient_plan", mapped=True):
    label = GoldLabel("synthetic", "gaia", "fixture", gold_step, "planning", "planning",
                      "inefficient_plan", error_type, "synthetic", "fixture")
    case = SimpleNamespace(trajectory_sha256="a" * 64,
                           event_for_step=lambda step: "synthetic-event" if step in {1, 2} else None)
    prediction = dict(predicted_step=2, predicted_module="planning",
                      predicted_error_type="inefficient_plan", evidence_quote="synthetic",
                      root_cause="synthetic", causal_summary="synthetic", rejected_adjacent_owner="synthetic")
    return scoring._score_record(label=label, case=case, prediction=prediction,
        manifest_sha256="b" * 64, mapping_valid=mapped, runtime_metadata={"provider": "fixture"})


def test_unmappable_released_gold_stays_in_denominator():
    good, unmapped = score(), score(gold_step=99, mapped=False)
    assert unmapped["gold_event_id"] is None
    assert unmapped["step_exact"] is unmapped["all_correct"] is False
    result = compute_metrics([good, unmapped])["by_method"]["agent_judge"]["overall"]
    assert result["step_exact"] == {"correct": 1, "denominator": 2, "accuracy": 0.5}
    assert result["all_correct"]["denominator"] == 2


def test_untyped_label_does_not_get_an_invented_all_correct_score():
    row = score(error_type=None)
    assert row["step_exact"] and row["step_module_exact"]
    assert row["all_correct"] is None
    assert row["provider"] == "fixture"


def test_invalid_predictions_stop_scoring_before_gold_is_opened(tmp_path, monkeypatch):
    def reject(**kwargs):
        raise ValueError("synthetic validation failure")
    monkeypatch.setattr(scoring, "validate_agent_judge_run", reject)
    monkeypatch.setattr(scoring, "load_agent_error_bench", lambda *a: pytest.fail("gold opened before validation"))
    with pytest.raises(ValueError, match="validation failure"):
        scoring.score_paper_gaia50(dataset=tmp_path, prediction_manifest=tmp_path / "manifest.json",
            cohort_manifest=tmp_path / "cohort.json", predictions=tmp_path / "predictions.json", run_dir=tmp_path)


def test_no_historical_protocol_selector_can_be_scored():
    with pytest.raises(ValueError, match="Only the supported"):
        scoring.resolve_agent_judge_protocol("legacy")
