"""Enforce a small active surface and independence from the research archive."""
from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

from scripts.maintenance.archive import verified_members

ROOT = Path(__file__).resolve().parents[2]


def verify_protocol_mapping(root: Path = ROOT, *, snapshot: dict | None = None) -> dict:
    if snapshot is None:
        snapshot = dict(verified_members(root / "research/archive/source-snapshot.json"))
    document = json.loads((root / "artifacts/protocol-source-map.json").read_text())
    rows = document["modules"]
    if len(rows) != 13 or len({row["current_path"] for row in rows}) != 13:
        raise ValueError("selected protocol component set changed")
    mapping = {Path(row["original_path"]).stem: Path(row["current_path"]).stem for row in rows}
    token = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(
        re.escape(name) for name in sorted(mapping, key=len, reverse=True)
    ) + r")(?![A-Za-z0-9_])")
    for row in rows:
        before = snapshot[row["original_path"]]
        path = root / row["current_path"]
        if (Path(row["current_path"]).is_absolute() or not path.resolve().is_relative_to(root)
                or path.is_symlink()):
            raise ValueError("unsafe current protocol path")
        expected = token.sub(lambda match: mapping[match[0]], before.decode()).encode()
        after = path.read_bytes()
        if (after != expected or hashlib.sha256(before).hexdigest() != row["original_sha256"]
                or hashlib.sha256(after).hexdigest() != row["current_sha256"]):
            raise ValueError(f"undeclared protocol modification: {row['current_path']}")
    return {"verified_protocol_components": len(rows), "only_declared_path_changes": True}


def audit(root: Path = ROOT) -> dict:
    issues = []
    files = sorted((root / "agentdebug").rglob("*.py"))
    for path in files:
        relative = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(), filename=relative)
        for node in ast.walk(tree):
            modules = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                       else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            if any(module.split(".")[0] in {"research", "scripts"} for module in modules):
                issues.append({"path": relative, "issue": "framework_depends_on_repository_tools"})
        if "diagnostics" in path.parts and re.search(r"(?:luna|gaia_v|agent_judge_v)", path.stem):
            issues.append({"path": relative, "issue": "experimental_module_in_active_package"})
    flat_scripts = [path.name for path in (root / "scripts").glob("*.py") if path.name != "__init__.py"]
    if flat_scripts:
        issues.append({"issue": "flat_script_backlog", "files": sorted(flat_scripts)})
    return {"active_python_files": len(files), "issue_count": len(issues), "issues": issues}


def main() -> int:
    result = audit()
    result.update(verify_protocol_mapping())
    print(json.dumps(result, indent=2))
    return int(bool(result["issues"]))


if __name__ == "__main__":
    raise SystemExit(main())
