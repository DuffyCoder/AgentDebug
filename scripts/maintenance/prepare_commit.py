"""Create a review-only commit inventory; never stage, commit, push or rewrite history."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.maintenance.check_repository_hygiene import ROOT, SECRET_PATTERNS, audit_repository


def git(root: Path, *arguments: str, input: bytes | None = None) -> bytes:
    return subprocess.run(["git", *arguments], cwd=root, input=input,
                          capture_output=True, check=True).stdout


def paths(value: bytes) -> set[str]:
    return {item.decode("utf-8") for item in value.split(b"\0") if item}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def inventory(root: Path) -> dict:
    """Describe the working-tree candidate independently of the user's index."""
    root = root.resolve()
    if git(root, "ls-files", "--unmerged", "-z"):
        raise ValueError("resolve index conflicts before preparing a commit")
    hygiene = audit_repository(root)
    if hygiene["issue_count"]:
        # No matched secret bytes are ever included in this diagnostic.
        raise ValueError("candidate failed repository hygiene; run make hygiene for paths and issue types")
    tracked = paths(git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD"))
    candidate = paths(git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z"))
    changed = paths(git(root, "diff", "--name-only", "--no-renames", "HEAD", "-z"))
    changed |= paths(git(root, "ls-files", "--others", "--exclude-standard", "-z"))
    files = []
    for relative in sorted(candidate):
        path = root / relative
        if path.is_file():
            files.append({"path": relative, "sha256": digest(path), "bytes": path.stat().st_size})
    changes = []
    for relative in sorted(changed):
        if (root / relative).is_file():
            kind = "modified" if relative in tracked else "added"
        elif relative in tracked:
            kind = "deleted"
        else:
            continue  # A staged new file removed again has no final-tree content.
        changes.append({"path": relative, "kind": kind})
    return {
        "schema_version": "agentdebug.commit-candidate.v1",
        "head": git(root, "rev-parse", "HEAD").decode().strip(),
        "branch": git(root, "branch", "--show-current").decode().strip(),
        "index_diff_sha256": hashlib.sha256(git(root, "diff", "--cached", "--binary")).hexdigest(),
        "existing_staged_paths": sorted(paths(git(root, "diff", "--cached", "--name-only", "-z"))),
        "change_counts": dict(sorted(Counter(item["kind"] for item in changes).items())),
        "present_file_count": len(files), "total_bytes": sum(item["bytes"] for item in files),
        "hygiene": hygiene, "files": files, "changes": changes,
        "scope": "working-tree candidate, not an automatically approved staging list",
        "owner_review_required": [
            "Review inherited removals and intentional public API compatibility changes.",
            "Review redistribution rights and privacy of data-derived evidence before public publication.",
            "Review any pre-existing staged changes; this tool does not alter the index.",
        ],
        "staged": False, "committed": False, "pushed": False,
    }


def audit_history(root: Path) -> dict:
    """Scan reachable Git blobs for common key patterns without printing matches.

    Only local refs are inspected; no fetch, reflog scan, or unreachable-object
    recovery is attempted. A negative pattern scan is not a full security audit.
    """
    objects = {}
    for line in git(root, "rev-list", "--objects", "--all").splitlines():
        oid, _, name = line.partition(b" ")
        objects[oid] = name.decode("utf-8", errors="replace")
    if not objects:
        raise ValueError("Git history is empty")
    descriptions = git(root, "cat-file", "--batch-check", input=b"\n".join(objects) + b"\n")
    blobs = [parts[0] for line in descriptions.splitlines()
             if len(parts := line.split()) == 3 and parts[1] == b"blob"]
    findings = []
    byte_count = 0
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL) as process:
        assert process.stdin is not None and process.stdout is not None
        for oid in blobs:
            process.stdin.write(oid + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[:2] != [oid, b"blob"]:
                raise ValueError("unexpected Git blob response")
            remaining = int(header[2])
            byte_count += remaining
            tail, matched = b"", set()
            while remaining:
                block = process.stdout.read(min(remaining, 1024 * 1024))
                if not block:
                    raise ValueError("truncated Git blob response")
                remaining -= len(block)
                window = tail + block
                matched.update(name for name, pattern in SECRET_PATTERNS.items() if pattern.search(window))
                tail = window[-512:]
            if process.stdout.read(1) != b"\n":
                raise ValueError("invalid Git blob terminator")
            for name in sorted(matched):
                findings.append({"blob": oid.decode(), "path_hint": objects[oid], "issue": name})
        process.stdin.close()
        if process.wait():
            raise ValueError("Git history scan failed")
    shallow = git(root, "rev-parse", "--is-shallow-repository").strip() == b"true"
    return {
        "scope": "blobs reachable from all existing local refs; no network fetch",
        "commit_count": int(git(root, "rev-list", "--all", "--count")),
        "blob_count": len(blobs), "bytes_scanned": byte_count,
        "shallow_repository": shallow, "issue_count": len(findings), "issues": findings,
        "patterns": sorted(SECRET_PATTERNS), "matched_values_included": False,
        "limitations": "Pattern scan only; excludes unreferenced objects, reflogs, remote-only history and unknown secret formats.",
    }


def export_source(root: Path, destination: Path, manifest: dict) -> None:
    """Copy exactly the reviewed present files, without .git or ignored state."""
    destination.mkdir(parents=True, exist_ok=False)
    for entry in manifest["files"]:
        source = root / entry["path"]
        if source.is_symlink() or not source.is_file() or digest(source) != entry["sha256"]:
            raise ValueError(f"candidate changed before export: {entry['path']}")
        target = destination / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if digest(target) != entry["sha256"]:
            raise ValueError(f"candidate changed during export: {entry['path']}")


def prepare(root: Path, output_dir: Path, *, scan_history: bool = False,
            export: bool = False) -> dict:
    root, output_dir = root.resolve(), output_dir.resolve()
    if output_dir.exists():
        raise ValueError("review output directory must not exist")
    if output_dir.is_relative_to(root):
        ignored = subprocess.run(["git", "check-ignore", "-q", "--", str(output_dir)], cwd=root)
        if ignored.returncode:
            raise ValueError("review output inside the repository must be Git-ignored")
    report = inventory(root)
    report["history_scan"] = audit_history(root) if scan_history else {"status": "not_run"}
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "inventory.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    # The NUL-separated list is for exact path review, not automatic staging.
    (output_dir / "candidate-paths.nul").write_bytes(
        b"".join(item["path"].encode() + b"\0" for item in report["changes"]))
    (output_dir / "changes.txt").write_text(
        "".join(f"{item['kind']:8} {json.dumps(item['path'], ensure_ascii=False)}\n" for item in report["changes"]))
    (output_dir / "commit-message.txt").write_text(
        "refactor: prepare the unified AgentDebug framework for release\n\n"
        "- Unify supported diagnosis, public interfaces and reproducible evaluation.\n"
        "- Separate research workflows from user-facing documentation.\n"
        "- Preserve frozen protocol evidence and add submission safeguards.\n")
    if export:
        export_source(root, output_dir / "source", report)
    # An export and report generation must never change the user's staging state.
    if hashlib.sha256(git(root, "diff", "--cached", "--binary")).hexdigest() != report["index_diff_sha256"]:
        raise ValueError("index changed during preparation; review concurrent changes")
    return {"output_dir": str(output_dir), "change_counts": report["change_counts"],
            "present_file_count": report["present_file_count"], "source_exported": export,
            "hygiene_issues": report["hygiene"]["issue_count"], "history_scan": report["history_scan"],
            "staged": False, "committed": False, "pushed": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--scan-history", action="store_true")
    parser.add_argument("--export-source", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    result = prepare(ROOT, args.output_dir or ROOT / "output/commit-preparation" / stamp,
                     scan_history=args.scan_history, export=args.export_source)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return int(bool(result["history_scan"].get("issue_count")))


if __name__ == "__main__":
    raise SystemExit(main())
