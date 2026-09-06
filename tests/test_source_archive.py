"""Small synthetic archives exercise safety without touching the frozen snapshot."""
import hashlib
import io
import json
import tarfile

import pytest

from scripts.maintenance import archive
from research.tools.archive_runner import validate_workspace


def snapshot(tmp_path, entries=None, bindings=None):
    entries = entries or [("package/module.py", b"# fixture\n", None)]
    packed = tmp_path / "fixture.tar.gz"
    with tarfile.open(packed, "w:gz") as stream:
        for name, value, kind in entries:
            info = tarfile.TarInfo(name)
            info.size = len(value)
            if kind is not None:
                info.type, info.linkname = kind, "outside"
            stream.addfile(info, io.BytesIO(value))
    files = bindings or {name: {"bytes": len(value), "sha256": archive.digest(value)}
                         for name, value, _ in entries}
    manifest = tmp_path / "fixture.json"
    manifest.write_text(json.dumps({"schema_version": "agentdebug.source-snapshot.v1",
        "archive": packed.name, "archive_sha256": archive.digest(packed.read_bytes()),
        "file_count": len(files), "files": files}))
    return manifest


def test_restore_preserves_bytes_and_refuses_overwrites(tmp_path):
    manifest = snapshot(tmp_path)
    destination = tmp_path / "restored"
    assert archive.verify(manifest)["verified_snapshot_files"] == 1
    archive.extract(destination, manifest)
    assert (destination / "package/module.py").read_bytes() == b"# fixture\n"
    with pytest.raises(ValueError, match="must not exist"):
        archive.extract(destination, manifest)
    validate_workspace(destination, manifest)
    (destination / "package/module.py").write_text("changed")
    with pytest.raises(ValueError, match="changed or missing"):
        validate_workspace(destination, manifest)


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a/../../b", ".git/config", "a\\b", "a//b", "./a"])
def test_unsafe_paths_rejected_before_creating_destination(tmp_path, name):
    manifest = snapshot(tmp_path, [(name, b"x", None)])
    with pytest.raises(ValueError, match="unsafe"):
        archive.extract(tmp_path / "restored", manifest)
    assert not (tmp_path / "restored").exists()


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE])
def test_links_and_special_files_are_never_extracted(tmp_path, kind):
    manifest = snapshot(tmp_path, [("link", b"", kind)])
    with pytest.raises(ValueError, match="unsafe"):
        archive.extract(tmp_path / "restored", manifest)
    assert not (tmp_path / "restored").exists()


@pytest.mark.parametrize("mutation", ["outer_hash", "member_hash", "size", "missing", "duplicate"])
def test_archive_tampering_is_rejected_before_any_restore(tmp_path, mutation):
    entries = [("item.py", b"fixture", None)]
    if mutation == "duplicate":
        entries *= 2
    manifest = snapshot(tmp_path, entries)
    document = json.loads(manifest.read_text())
    if mutation == "outer_hash":
        document["archive_sha256"] = "0" * 64
    elif mutation == "member_hash":
        document["files"]["item.py"]["sha256"] = "0" * 64
    elif mutation == "size":
        document["files"]["item.py"]["bytes"] = 1
    elif mutation == "missing":
        document["files"]["missing.py"] = {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}
        document["file_count"] += 1
    manifest.write_text(json.dumps(document))
    with pytest.raises(ValueError):
        archive.extract(tmp_path / "restored", manifest)
    assert not (tmp_path / "restored").exists()


def test_create_is_inventory_bound_and_write_once(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "fixture.py").write_bytes(b"# fixture\n")
    (source / "unreviewed.txt").write_text("do not include")
    inventory = tmp_path / "inventory.json"
    inventory.write_text(json.dumps({"head": "synthetic", "files": [
        {"path": "fixture.py", "sha256": archive.digest(b"# fixture\n"), "bytes": 10}]}))
    manifest = tmp_path / "saved.json"
    assert archive.create(source, inventory, manifest)["verified_snapshot_files"] == 1
    assert set(dict(archive.verified_members(manifest))) == {"fixture.py"}
    with pytest.raises(ValueError, match="write-once"):
        archive.create(source, inventory, manifest)
    (source / "fixture.py").write_text("changed")
    with pytest.raises(ValueError, match="differs from inventory"):
        archive.create(source, inventory, tmp_path / "another.json")


def test_hygiene_scans_uncompressed_snapshot_members(tmp_path, monkeypatch):
    from scripts.maintenance import check_repository_hygiene as hygiene

    archived = tmp_path / "research/archive"
    archived.mkdir(parents=True)
    synthetic = ("sk-" + "Z" * 40).encode()
    manifest = snapshot(archived, [("old/module.py", synthetic, None)])
    manifest.rename(archived / "source-snapshot.json")
    monkeypatch.setattr(hygiene, "ROOT", tmp_path)
    monkeypatch.setattr(hygiene, "_candidate_paths", lambda: [])
    report = hygiene.audit_repository()
    assert report["checked_snapshot_member_count"] == 1
    assert report["issues"][0]["issue"] == "openai_key"
    assert synthetic.decode() not in json.dumps(report)
