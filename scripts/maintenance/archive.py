"""Create, verify and restore an explicit source snapshot without Git writes."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "research/archive/source-snapshot.json"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_path(value: str) -> bool:
    path = PurePosixPath(value)
    return (bool(value) and not path.is_absolute() and path.as_posix() == value
            and all(part not in {"..", ".", ".git"} for part in path.parts)
            and "\\" not in value)


def read_manifest(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema_version") != "agentdebug.source-snapshot.v1":
        raise ValueError("unsupported snapshot manifest")
    if not safe_path(document["archive"]) or len(PurePosixPath(document["archive"]).parts) != 1:
        raise ValueError("unsafe snapshot archive path")
    files = document["files"]
    if not files or any(not safe_path(name) for name in files):
        raise ValueError("unsafe snapshot member path")
    if len(files) != document["file_count"]:
        raise ValueError("snapshot member count mismatch")
    for binding in files.values():
        if (type(binding["bytes"]) is not int or not 0 <= binding["bytes"] <= 10 * 1024**2
                or len(binding["sha256"]) != 64):
            raise ValueError("invalid snapshot file binding")
    return document


def verified_members(manifest: Path):
    document = read_manifest(manifest)
    path = manifest.parent / document["archive"]
    if digest(path.read_bytes()) != document["archive_sha256"]:
        raise ValueError("snapshot archive hash mismatch")
    seen = set()
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            name = member.name
            if (not member.isfile() or not safe_path(name) or name in seen
                    or name not in document["files"]):
                raise ValueError("unexpected or unsafe snapshot member")
            binding = document["files"][name]
            if member.size != binding["bytes"]:
                raise ValueError(f"snapshot member size mismatch: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("unreadable snapshot member")
            payload = stream.read()
            if digest(payload) != binding["sha256"]:
                raise ValueError(f"snapshot member hash mismatch: {name}")
            seen.add(name)
            yield name, payload
    if seen != set(document["files"]):
        raise ValueError("snapshot is incomplete")


def verify(manifest: Path = DEFAULT_MANIFEST) -> dict:
    count = sum(1 for _ in verified_members(manifest))
    return {"verified_snapshot_files": count, "byte_identity_verified": True,
            "scope": "pre-cleanup source candidate, not every historical as-run checkout"}


def extract(destination: Path, manifest: Path = DEFAULT_MANIFEST) -> dict:
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("snapshot destination must not exist")
    # Verify every byte before creating output; never extract links or paths
    # supplied only by the archive. Restoration does not include local state.
    verify(manifest)
    destination.mkdir(parents=True, exist_ok=False)
    for name, payload in verified_members(manifest):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(payload)
    return {"destination": str(destination), "restored": True, "git_state_changed": False}


def create(source: Path, inventory_path: Path, manifest: Path) -> dict:
    """Freeze exactly a previously reviewed export, excluding later new files."""
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    archive_path = manifest.with_suffix(".tar.gz")
    if manifest.exists() or archive_path.exists():
        raise ValueError("snapshots are write-once")
    entries = inventory["files"]
    if len({entry["path"] for entry in entries}) != len(entries):
        raise ValueError("duplicate inventory path")
    for entry in entries:
        name, path = entry["path"], source / entry["path"]
        if (not safe_path(name) or path.is_symlink() or not path.is_file()
                or digest(path.read_bytes()) != entry["sha256"]):
            raise ValueError(f"snapshot source differs from inventory: {name}")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as archive:
                for entry in sorted(entries, key=lambda item: item["path"]):
                    payload = (source / entry["path"]).read_bytes()
                    if digest(payload) != entry["sha256"]:
                        raise ValueError("snapshot source changed during creation")
                    member = tarfile.TarInfo(entry["path"])
                    member.size, member.mode, member.mtime = len(payload), 0o644, 0
                    archive.addfile(member, io.BytesIO(payload))
    document = {
        "schema_version": "agentdebug.source-snapshot.v1",
        "archive": archive_path.name, "archive_sha256": digest(archive_path.read_bytes()),
        "file_count": len(entries), "source_head": inventory["head"],
        "scope": "reviewed working-tree candidate before physical source separation; not an as-run identity claim",
        "excluded": ["Git history", "ignored data/", "ignored output/", "credentials", "local environments"],
        "files": {entry["path"]: {k: entry[k] for k in ("sha256", "bytes")} for entry in entries},
    }
    with manifest.open("x", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2)
        stream.write("\n")
    return verify(manifest)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("command", choices=("verify", "extract", "create"))
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--inventory", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        result = verify(args.manifest)
    elif args.command == "extract":
        if args.destination is None:
            parser.error("extract requires --destination")
        result = extract(args.destination, args.manifest)
    else:
        if args.source is None or args.inventory is None:
            parser.error("create requires --source and --inventory")
        result = create(args.source, args.inventory, args.manifest)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
