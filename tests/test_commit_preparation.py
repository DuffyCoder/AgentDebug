"""Commit preparation is a read-only Git operation with explicit export boundaries."""
import json
from pathlib import Path

import pytest

from scripts.maintenance.prepare_commit import audit_history, export_source, git, inventory, prepare


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "-q")
    (root / ".gitignore").write_text("/output/\n/private/\n")
    (root / "kept.txt").write_text("original\n")
    (root / "removed.txt").write_text("old\n")
    git(root, "add", ".gitignore", "kept.txt", "removed.txt")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "synthetic fixture")
    return root


def test_inventory_separates_additions_modifications_and_removals(repository):
    (repository / "kept.txt").write_text("changed\n")
    (repository / "removed.txt").unlink()
    (repository / "new file.txt").write_text("new\n")
    private = repository / "private"
    private.mkdir()
    (private / "not-for-export.txt").write_text("local state\n")
    result = inventory(repository)
    assert result["change_counts"] == {"added": 1, "deleted": 1, "modified": 1}
    assert result["present_file_count"] == 3
    assert not any("private/" in item["path"] for item in result["files"])
    assert result["existing_staged_paths"] == []


def test_prepare_preserves_existing_index_and_uses_nul_paths(repository):
    path = repository / "staged file.txt"
    path.write_text("staged\n")
    git(repository, "add", "staged file.txt")
    before = git(repository, "diff", "--cached", "--binary")
    output = repository / "output/review"
    result = prepare(repository, output, scan_history=True, export=True)
    assert git(repository, "diff", "--cached", "--binary") == before
    assert (output / "candidate-paths.nul").read_bytes() == b"staged file.txt\0"
    assert (output / "source/staged file.txt").read_text() == "staged\n"
    assert not (output / "source/.git").exists()
    assert result["history_scan"]["issue_count"] == 0
    assert result["staged"] is result["committed"] is result["pushed"] is False
    assert json.loads((output / "inventory.json").read_text())["existing_staged_paths"] == ["staged file.txt"]


def test_prepare_refuses_unignored_outputs_and_overwrites(repository):
    with pytest.raises(ValueError, match="Git-ignored"):
        prepare(repository, repository / "review")
    output = repository / "output/existing"
    output.mkdir(parents=True)
    with pytest.raises(ValueError, match="must not exist"):
        prepare(repository, output)


def test_export_detects_files_changed_after_review(repository):
    manifest = inventory(repository)
    (repository / "kept.txt").write_text("concurrent change\n")
    with pytest.raises(ValueError, match="changed before export"):
        export_source(repository, repository.parent / "export", manifest)


def test_inventory_rejects_symlinks(repository):
    (repository / "link").symlink_to(repository / "kept.txt")
    with pytest.raises(ValueError, match="hygiene"):
        inventory(repository)


def test_history_scan_detects_deleted_secret_without_disclosing_it(repository):
    synthetic = "sk-" + "X" * 40
    path = repository / "configuration.txt"
    path.write_text(synthetic + "\n")
    git(repository, "add", "configuration.txt")
    git(repository, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "synthetic historical secret")
    path.unlink()
    git(repository, "add", "configuration.txt")
    git(repository, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "remove fixture")
    report = audit_history(repository)
    assert report["commit_count"] == 3
    assert report["issue_count"] == 1
    assert report["issues"][0]["issue"] == "openai_key"
    assert report["issues"][0]["path_hint"] == "configuration.txt"
    assert synthetic not in json.dumps(report)


def test_history_scan_handles_keys_across_chunk_boundaries(repository):
    synthetic = "sk-" + "Y" * 40
    (repository / "large.txt").write_text("." * (1024 * 1024 - 2) + synthetic)
    git(repository, "add", "large.txt")
    git(repository, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "synthetic chunk boundary")
    assert audit_history(repository)["issue_count"] == 1


def test_precommit_hooks_are_local_and_non_mutating():
    import yaml

    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / ".pre-commit-config.yaml").read_text())
    assert len(config["repos"]) == 1
    assert config["repos"][0]["repo"] == "local"
    for hook in config["repos"][0]["hooks"]:
        assert hook["always_run"] and not hook["pass_filenames"]
        assert "--fix" not in hook["entry"]
        assert "--execute" not in hook["entry"]


def test_root_makefile_keeps_authoring_and_versioned_targets_in_archive():
    root = Path(__file__).resolve().parents[1]
    makefile = (root / "Makefile").read_text()
    assert "prepare-commit:" in makefile
    assert "research/Makefile" in makefile
    for word in ("rsi-", "proposal-", "v3p83"):
        assert word not in makefile
