"""Maintained research entry points verify original records, not new inference."""
import json

from research.tools import extract_protocol, research_release
from research.tools.rsi import build_proposal_bundle as proposal
from research.tools.result_taxonomy import valid_record


def test_relocated_ledger_keeps_original_source_identity():
    result = research_release.verify()
    assert result["verified_records"] == 227
    assert result["verified_snapshot_source_files"] == 822
    assert result["original_manifest_unchanged"]
    assert not result["fresh_inference_performed"]
    assert not result["gold_rescoring_performed"]


def test_current_extractor_only_changes_declared_paths():
    assert extract_protocol.run()["verified_protocol_components"] == 13


def test_current_reviewer_bundle_reports_real_backends_and_open_gates():
    result = proposal.check()
    assert result["verified_bundle_files"] == 31
    assert result["valid_runs"] == 209
    assert result["families"]["LLM API"]["runs"] == 110
    assert result["families"]["Codex SDK"]["runs"] == 99
    assert result["gpt55_medium_gaia50_fresh_runs"] == 7
    assert not result["new_inference"] and not result["sealed_task_ready"]


def test_cached_fixed_configuration_evidence_is_usable_without_private_outputs():
    from research.tools import plot_fixed_config_history as plot

    rows = json.loads(plot.HISTORY.read_text())
    supplement = plot.read_supplement(rows)
    recorded = {r["id"]: r for r in json.loads((plot.DEST / "fixed-config-records.json").read_text())}
    for row in rows:
        if row["id"] in recorded:
            assert plot.configuration(row, supplement) == recorded[row["id"]]["fixed_config"]


def test_record_classification_still_retains_invalid_and_excluded_observations():
    rows = json.loads((research_release.ROOT / proposal.HISTORY).read_text())
    assert len(rows) == 227
    valid = [row for row in rows if valid_record(row)]
    assert len(valid) == 214
    assert len({row["run_dir"] for row in valid}) == 209
    assert any(row["status"] == "scored_failures_zero" for row in valid)
    assert any(row["status"] == "audit_invalid" for row in rows)
