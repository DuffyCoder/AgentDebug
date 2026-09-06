"""Public navigation, portable links, and package boundaries are regression-tested."""
from __future__ import annotations

import tarfile
from io import BytesIO
from zipfile import ZipFile

from scripts.maintenance import check_public_docs as docs
from scripts.maintenance import check_repository_hygiene as hygiene
from scripts.maintenance.check_distribution import audit as audit_distribution


def test_public_documentation_is_connected_and_separated():
    result = docs.audit()
    assert result["issues"] == []
    assert result["checked_local_links"] > 100
    assert result["network_links_checked"] is False
    home = (docs.ROOT / "README.md").read_text()
    assert home.count("](research/README.md)") == 1


def test_link_parser_ignores_examples_and_network():
    content = "[local](guide.md#usage)\n```md\n[example](missing.md)\n```\n[web](https://example.org)"
    assert list(docs.local_links(content)) == [("guide.md#usage", "guide.md", "usage")]
    assert "python-api" in docs.anchors("## Python API\n")


def test_broken_link_and_archive_bypass_are_rejected(tmp_path):
    for relative in docs.PUBLIC_PAGES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Fixture\n")
    (tmp_path / "research").mkdir()
    (tmp_path / "research/README.md").write_text("# Research\n")
    (tmp_path / "research/data-and-splits.md").write_text("# Notes\n")
    (tmp_path / "README.md").write_text("[broken](missing.md)\n[direct](research/data-and-splits.md)\n")
    issues = {issue["issue"] for issue in docs.audit(tmp_path)["issues"]}
    assert {"broken_local_link", "bypasses_archive_gateway"} <= issues


def test_wheel_rejects_data_and_credentials(tmp_path):
    path = tmp_path / "fixture.whl"
    with ZipFile(path, "w") as archive:
        archive.writestr("agentdebug/__init__.py", "")
        archive.writestr("data/private.json", "{}")
        archive.writestr("agentdebug/auth.json", "{}")
    issues = {issue["issue"] for issue in audit_distribution(path)["issues"]}
    assert {"outside_framework_distribution", "private_or_generated_member"} <= issues


def test_sdist_rejects_archive_escape(tmp_path):
    path = tmp_path / "fixture.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        for name in ("agentdebug-0.4.0/agentdebug/__init__.py", "agentdebug-0.4.0/../../private"):
            info = tarfile.TarInfo(name)
            archive.addfile(info, BytesIO())
    assert "unsafe_archive_member" in {issue["issue"] for issue in audit_distribution(path)["issues"]}


def test_minimal_framework_wheel_is_accepted(tmp_path):
    path = tmp_path / "fixture.whl"
    with ZipFile(path, "w") as archive:
        archive.writestr("agentdebug/__init__.py", "")
        archive.writestr("agentdebug-0.4.0.dist-info/METADATA", "Name: agentdebug\n")
    assert audit_distribution(path)["issues"] == []


def test_hygiene_rejects_tracked_private_state_and_env_files(tmp_path, monkeypatch):
    private = tmp_path / "data/example.json"
    private.parent.mkdir()
    private.write_text("{}")
    secret_env = tmp_path / ".env.production"
    secret_env.write_text("CONFIG=value\n")
    monkeypatch.setattr(hygiene, "ROOT", tmp_path)
    monkeypatch.setattr(hygiene, "_candidate_paths", lambda: [private, secret_env])
    issues = {issue["issue"] for issue in hygiene.audit_repository()["issues"]}
    assert {"private_local_state", "local_env_file"} <= issues


def test_hygiene_does_not_follow_a_symlink(tmp_path, monkeypatch):
    link = tmp_path / "link"
    link.symlink_to(tmp_path / "missing-private-target")
    monkeypatch.setattr(hygiene, "ROOT", tmp_path)
    monkeypatch.setattr(hygiene, "_candidate_paths", lambda: [link])
    assert hygiene.audit_repository()["issues"] == [{"path": "link", "issue": "unreviewed_symlink"}]
