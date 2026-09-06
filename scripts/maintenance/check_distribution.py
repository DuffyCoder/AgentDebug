"""Inspect built framework distributions without extracting or installing them."""
from __future__ import annotations

import argparse
import json
import re
import stat
import tarfile
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

SDIST_TOP = {
    "agentdebug", "agentdebug.egg-info", "README.md", "LICENSE",
    "pyproject.toml", "setup.py", "setup.cfg", "PKG-INFO", "MANIFEST.in",
}


def audit(path: Path) -> dict:
    wheel = path.suffix == ".whl"
    if wheel:
        with ZipFile(path) as archive:
            entries = [(info.filename, stat.S_ISLNK(info.external_attr >> 16))
                       for info in archive.infolist() if not info.is_dir()]
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            entries = [(info.name, not info.isfile()) for info in archive.getmembers() if not info.isdir()]
    else:
        raise ValueError("Expected a .whl or .tar.gz distribution")
    issues = []
    roots = set()
    seen = set()
    for name, unsafe_type in entries:
        parts = PurePosixPath(name).parts
        if name in seen:
            issues.append({"path": name, "issue": "duplicate_member"})
        seen.add(name)
        if unsafe_type or not parts or name.startswith("/") or ".." in parts or "\\" in name:
            issues.append({"path": name, "issue": "unsafe_archive_member"})
            continue
        roots.add(parts[0])
        package_parts = parts if wheel else parts[1:]
        if not package_parts:
            issues.append({"path": name, "issue": "missing_distribution_root"})
            continue
        top = package_parts[0]
        allowed = (top == "agentdebug" or (top.startswith("agentdebug-") and top.endswith(".dist-info"))) if wheel else top in SDIST_TOP
        if not allowed:
            issues.append({"path": name, "issue": "outside_framework_distribution"})
        if (top == "agentdebug" and
                (any(part in {"engines", "environments", "rollout", "memory", "research", "scripts"}
                     for part in package_parts[1:]) or
                 re.search(r"(?:agent_judge_v|agent_judge_luna|agent_judge_gaia_v|runner\.py$)", name))):
            issues.append({"path": name, "issue": "retired_implementation_in_distribution"})
        if any(part in {"__pycache__", ".git", ".venv", ".codex", ".env", "auth.json", "credentials.json"}
               or part.startswith(".env.") or part.endswith((".pyc", ".pyo")) for part in package_parts):
            issues.append({"path": name, "issue": "private_or_generated_member"})
    if not wheel and len(roots) != 1:
        issues.append({"issue": "nonunique_distribution_root"})
    expected = "agentdebug/__init__.py"
    if not any(name == expected or (not wheel and name.endswith("/" + expected)) for name, _ in entries):
        issues.append({"issue": "missing_framework_package"})
    return {"archive": path.name, "member_count": len(entries), "issue_count": len(issues), "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    args = parser.parse_args()
    reports = [audit(path) for path in args.archives]
    print(json.dumps(reports, indent=2))
    return int(any(report["issue_count"] for report in reports))


if __name__ == "__main__":
    raise SystemExit(main())
