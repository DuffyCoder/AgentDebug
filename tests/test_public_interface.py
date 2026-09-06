"""The documented quick start must work with synthetic input and no model access."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentdebug import cli
from agentdebug import method
from agentdebug.trace import load_canonical_trace

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("command", ["ingest", "validate"])
def test_documented_local_commands(command, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Quick start must not construct a model client")
    monkeypatch.setattr(method.CodexExecutor, "__call__", forbidden)
    output = tmp_path / f"{command}.json"
    code = cli.main([
        command, "--session", str(ROOT / "examples/moltbot_failure_session.jsonl"),
        "--task", str(ROOT / "examples/email_triage_task.yaml"),
        "--output", str(output), "--strict",
    ])
    assert code == 0
    value = json.loads(output.read_text())
    assert value
    if command == "ingest":
        trace = load_canonical_trace(output)
        assert trace.assistant_turns
        assert trace.tool_calls
    else:
        assert value["status"] == "pass"
        assert not any(issue["severity"] in {"error", "critical"} for issue in value["issues"])


def test_invalid_input_exits_without_a_model(tmp_path, monkeypatch):
    monkeypatch.setattr(method.CodexExecutor, "__call__", lambda *_: pytest.fail("No model allowed"))
    assert cli.main(["validate", "--session", str(tmp_path / "missing.jsonl")]) == 2


def test_cli_help_contract():
    parser = cli.build_parser()
    arguments = parser.parse_args(["analyze", "--prediction-manifest", "inputs.json",
                                  "--cohort-manifest", "cohort.json", "--output-dir", "run"])
    assert arguments.execute is False
    assert arguments.max_workers == 4
    assert arguments.max_attempts == 2
    assert not hasattr(arguments, "protocol")
    assert not hasattr(arguments, "judge_model")


@pytest.mark.parametrize("option", ["--method", "--protocol", "--judge-model", "--judge-provider"])
def test_retired_method_selection_is_rejected(option):
    with pytest.raises(SystemExit) as error:
        cli.build_parser().parse_args(["analyze", "--prediction-manifest", "inputs.json",
            "--cohort-manifest", "cohort.json", "--output-dir", "run", option, "old"])
    assert error.value.code == 2


def test_all_executable_aliases_and_python_apis_share_one_method(monkeypatch):
    import agentdebug
    import agentdebug.diagnostics
    from agentdebug.benchmark import cli as benchmark, agent_judge_cli as judge

    marker = {"method": "AgentDebug"}
    monkeypatch.setattr(method, "analyze", lambda **kwargs: marker)
    assert agentdebug.analyze() is marker
    assert agentdebug.diagnostics.analyze() is marker
    monkeypatch.setattr(cli, "main", lambda argv: 42)
    assert benchmark.main([]) == judge.main([]) == 42
    metadata = (ROOT / "pyproject.toml").read_text()
    for command in ("agentdebug", "agentdebug-trace", "agentdebug-benchmark", "agentdebug-agent-judge"):
        assert f'{command} = "agentdebug.cli:main"' in metadata
