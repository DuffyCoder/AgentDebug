"""The installed framework has one protocol and no research/runtime dependency."""
from zipfile import ZipFile

import pytest

from scripts.maintenance.check_distribution import audit as audit_distribution
from scripts.maintenance.check_layout import ROOT, audit, verify_protocol_mapping


def test_active_package_is_independent_and_extraction_is_exact():
    assert audit()["issues"] == []
    assert verify_protocol_mapping() == {"verified_protocol_components": 13,
                                         "only_declared_path_changes": True}


@pytest.mark.parametrize("module", ["scripts.reproduction", "research.tools"])
def test_package_import_of_repository_tools_is_rejected(tmp_path, module):
    package = tmp_path / "agentdebug"
    package.mkdir()
    (package / "broken.py").write_text(f"import {module}\n")
    assert audit(tmp_path)["issues"][0]["issue"] == "framework_depends_on_repository_tools"


def test_experiments_cannot_return_to_active_script_and_module_dirs(tmp_path):
    package = tmp_path / "agentdebug/diagnostics"
    package.mkdir(parents=True)
    (package / "agent_judge_luna_gaia_v999.py").write_text("")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "run_v999.py").write_text("")
    assert {i["issue"] for i in audit(tmp_path)["issues"]} == {
        "experimental_module_in_active_package", "flat_script_backlog"}


@pytest.mark.parametrize("member", ["agentdebug/diagnostics/agent_judge_luna_v1.py",
                                    "agentdebug/benchmark/runner.py", "agentdebug/engines/factory.py"])
def test_distribution_rejects_stale_build_products(tmp_path, member):
    wheel = tmp_path / "fixture.whl"
    with ZipFile(wheel, "w") as archive:
        archive.writestr("agentdebug/__init__.py", "")
        archive.writestr(member, "")
    assert "retired_implementation_in_distribution" in {
        i["issue"] for i in audit_distribution(wheel)["issues"]}
