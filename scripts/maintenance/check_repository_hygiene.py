#!/usr/bin/env python3
"""Fail closed on common repository-publishing mistakes."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from scripts.maintenance.archive import verified_members


ROOT = Path(__file__).resolve().parents[2]
MAX_FILE_BYTES = 10 * 1024 * 1024
FORBIDDEN_PATHS = re.compile(rb"/(?:home|Users)/[^/]+/(?:workspace|projects?)/")
SECRET_PATTERNS = {
    "openai_key": re.compile(rb"sk-(?:(?:proj|svcacct)-[A-Za-z0-9_-]{20,}|[A-Za-z0-9]{32,})"),
    "google_key": re.compile(rb"AIza[0-9A-Za-z_-]{30,}"),
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    "slack_token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer_token": re.compile(rb"Bearer [A-Za-z0-9._-]{40,}"),
}
PRIVATE_ROOTS = {"data", "output", "AgentDebug", ".venv", "venv", "env", ".codex", ".ssh", ".aws"}
PRIVATE_FILENAMES = {"auth.json", "credentials.json", "id_rsa", "id_ed25519"}
ABSOLUTE_PATH_PATTERN_ALLOWLIST = {
    # Only for members in the frozen original snapshot, not active files.
    # Historical audit utilities recognize the original workspace path.
    "scripts/build_v3p64_inference_access_audit.py",
    "scripts/build_v3p65_inference_access_audit.py",
}


def _candidate_paths(root: Path | None = None) -> list[Path]:
    root = ROOT if root is None else root.resolve()
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / item.decode("utf-8") for item in completed.stdout.split(b"\0") if item]


def audit_repository(root: Path | None = None) -> dict[str, object]:
    paths = _candidate_paths() if root is None else _candidate_paths(root)
    root = ROOT if root is None else root.resolve()
    issues: list[dict[str, object]] = []
    checked = 0
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            issues.append({"path": relative, "issue": "unreviewed_symlink"})
            continue
        if not path.is_file():
            continue
        checked += 1
        if path.relative_to(root).parts[0] in PRIVATE_ROOTS or path.name in PRIVATE_FILENAMES:
            issues.append({"path": relative, "issue": "private_local_state"})
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            issues.append({"path": relative, "issue": "file_too_large", "size_bytes": size})
            continue
        if (path.name == ".env" or path.name.startswith(".env.")) and path.name not in {".env.example", ".env.template"}:
            issues.append({"path": relative, "issue": "local_env_file"})
            continue
        value = path.read_bytes()
        if FORBIDDEN_PATHS.search(value):
            issues.append({"path": relative, "issue": "absolute_workspace_path"})
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(value):
                issues.append({"path": relative, "issue": name})
    archived_checked = 0
    manifest = root / "research/archive/source-snapshot.json"
    if manifest.is_file():
        # Compressed bytes alone do not constitute a source-content scan.
        # Verify the full manifest and inspect each original file's contents.
        for name, value in verified_members(manifest):
            archived_checked += 1
            locator = f"research/archive/source-snapshot.tar.gz::{name}"
            if name not in ABSOLUTE_PATH_PATTERN_ALLOWLIST and FORBIDDEN_PATHS.search(value):
                issues.append({"path": locator, "issue": "absolute_workspace_path"})
            for kind, pattern in SECRET_PATTERNS.items():
                if pattern.search(value):
                    issues.append({"path": locator, "issue": kind})
    return {
        "schema_version": "agentdebug.repository-hygiene.v1",
        "checked_file_count": checked,
        "checked_snapshot_member_count": archived_checked,
        "max_file_bytes": MAX_FILE_BYTES,
        "issue_count": len(issues),
        "issues": issues,
    }


def main() -> int:
    result = audit_repository()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["issue_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
