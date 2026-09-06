"""Public release bookkeeping must not expose algorithm selectors or run models."""
import json

import pytest

from scripts.reproduction import release


def test_verify_filters_presentation_not_frozen_identity(capsys):
    assert release.main(["verify"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["method"] == "AgentDebug"
    assert result["step_exact"] == "26/50"
    assert result["source_hashes_verified"] is True
    assert "experiment" not in result and "release" not in result


@pytest.mark.parametrize("command", ["prepare", "rescore", "score"])
def test_release_commands_reject_existing_output(command, tmp_path):
    arguments = [command, "--output-dir", str(tmp_path)]
    if command == "prepare":
        arguments += ["--source-root", "unused"]
    else:
        arguments += ["--dataset", "unused", "--prediction-manifest", "unused"]
        if command == "score":
            arguments += ["--run-dir", "unused"]
    with pytest.raises(ValueError, match="already exists"):
        release.main(arguments)


def test_unvalidated_live_run_is_rejected_before_gold_access(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    (run / "run.json").write_text(json.dumps({"method": "AgentDebug", "status": "failed"}))
    with pytest.raises(ValueError, match="validated AgentDebug run"):
        release.main(["score", "--run-dir", str(run), "--dataset", "does-not-exist",
            "--prediction-manifest", "does-not-exist", "--output-dir", str(tmp_path / "score")])
    assert not (tmp_path / "score").exists()
