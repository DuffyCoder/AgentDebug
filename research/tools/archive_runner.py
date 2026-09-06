"""Run frozen historical tests in a separate source tree, never the live package."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.maintenance.archive import DEFAULT_MANIFEST, ROOT, extract, verified_members

RESEARCH_TESTS = (
    "tests/test_gaia_v3p83_reproduction_release.py",
    "tests/test_research_release.py",
    "tests/test_rsi_authoring_contracts.py",
    "tests/test_isolated_test_runner.py",
    "tests/test_result_taxonomy_and_proposal.py",
    "tests/test_fixed_config_history.py",
    "tests/test_llm_api_history.py",
)


def validate_workspace(workspace: Path, manifest: Path = DEFAULT_MANIFEST) -> None:
    if workspace.resolve() == ROOT.resolve():
        raise ValueError("historical tests cannot run in the active checkout")
    for name, payload in verified_members(manifest):
        path = workspace / name
        if (not path.is_file() or path.is_symlink() or
                not path.resolve().is_relative_to(workspace.resolve()) or path.read_bytes() != payload):
            raise ValueError(f"restored source changed or missing: {name}")


def run(workspace: Path, arguments: list[str]) -> int:
    environment = {**os.environ, "PYTHONPATH": str(workspace.resolve()), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, *arguments], cwd=workspace, env=environment, check=False).returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("command", choices=("test", "test-all"))
    parser.add_argument("--workspace", help="An explicitly restored snapshot with separately obtained local data/output")
    args = parser.parse_args(argv)
    if args.command == "test-all":
        if not args.workspace:
            parser.error("test-all requires --workspace; see research/archive/README.md for restoration")
        workspace = Path(args.workspace).resolve()
        validate_workspace(workspace)
        return run(workspace, ["-m", "scripts.reproduction.run_isolated_tests"])
    with tempfile.TemporaryDirectory(prefix="agentdebug-history-") as parent:
        workspace = Path(parent) / "source"
        extract(workspace)
        return run(workspace, ["-m", "pytest", "-q", *RESEARCH_TESTS])


if __name__ == "__main__":
    raise SystemExit(main())
