"""Verify frozen score accounting and its original, archived source bindings.

No historical manifest is re-signed for the new layout. Source identities refer
to the pre-cleanup snapshot, not the active package or every as-run tree.
No model calls or original gold labels are needed for this accounting check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from research.tools.result_taxonomy import classification
from scripts.maintenance.archive import verified_members

ROOT = Path(__file__).resolve().parents[2]
HISTORY = Path("research/results/experiment-history-2026-09-05")
RELEASE = Path("research/results/accounting")
PROFILE_PATH = Path("research/configs/reproduction-profiles.json")
METRICS = ("step_exact", "step_module_exact", "all_correct")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def relocated(relative: str) -> Path:
    path = Path(relative)
    if relative == "configs/reproduction/research-profiles.json":
        return PROFILE_PATH
    for old, new in (("docs/results", "research/results"),
                     ("artifacts/results", "research/results/accounting")):
        if path.is_relative_to(old):
            return Path(new) / path.relative_to(old)
    raise ValueError(f"unmapped historical result path: {relative}")


def verify(root: Path = ROOT) -> dict:
    snapshot = dict(verified_members(root / "research/archive/source-snapshot.json"))
    manifest_path = root / RELEASE / "manifest.json"
    require(manifest_path.read_bytes() == snapshot["artifacts/results/manifest.json"],
            "original historical manifest was modified")
    manifest = load(manifest_path)
    for relative, digest in manifest["current_release_source_files"].items():
        require(hashlib.sha256(snapshot[relative]).hexdigest() == digest,
                f"archived source hash mismatch: {relative}")
    for relative, digest in manifest["files"].items():
        require(hashlib.sha256(snapshot[relative]).hexdigest() == digest,
                f"original artifact hash mismatch: {relative}")
        path = root / relocated(relative)
        require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), "unsafe result path")
        require(path.is_file() and sha256(path) == digest, f"relocated artifact hash mismatch: {relative}")
    rows = load(root / HISTORY / "all-results.json")
    records = load(root / RELEASE / "per-case-ledger.json")["records"]
    require(len(rows) == len(records) == manifest["row_count"], "result count mismatch")
    by_id = {r["id"]: r for r in rows}
    require(len(by_id) == len(rows), "duplicate history IDs")
    require(len({r['id'] for r in records}) == len(records), "duplicate ledger IDs")
    for record in records:
        row = by_id[record["id"]]
        require(all(row.get(k) == v for k, v in classification(row["transport"]).items()),
                f"result classification mismatch: {row['id']}")
        cases = record["cases"]
        require(len(cases) == row["n"], f"denominator changed: {row['id']}")
        ids = [c["trajectory_id"] for c in cases]
        require(len(set(ids)) == len(ids), f"duplicate case: {row['id']}")
        identity = hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()
        require(identity == row["case_set_sha256"], f"case membership changed: {row['id']}")
        for key in METRICS:
            require(all(c[key] is None or type(c[key]) is bool for c in cases), "invalid score flag")
            require(sum(c[key] is True for c in cases) == row[key], f"numerator mismatch: {row['id']}/{key}")
            denominator = sum(c[key] is not None for c in cases) if key == "all_correct" else len(cases)
            require(denominator == row[key + "_denominator"], f"denominator mismatch: {row['id']}/{key}")
    profiles = load(root / RELEASE / "reproduction-index.json")["profiles"]
    require(len({p['record']['case_set_sha256'] for p in profiles}) == 1,
            "curated profiles do not share the same case set")
    require(all(p['record']['n'] == 50 for p in profiles), "curated profiles are not full GAIA-50")
    for p in profiles:
        require(p["record"] == by_id[p["history_id"]], "curated profile differs from ledger")
        require([p['record'][k] for k in METRICS] == p['expected_counts'], "profile score mismatch")
        require(hashlib.sha256(snapshot[p["runner_path"]]).hexdigest() == p["current_release_runner_sha256"],
                "archived release runner changed")
    return {"verified_records": len(records), "verified_files": len(manifest["files"]),
            "verified_snapshot_source_files": len(manifest["current_release_source_files"]),
            "source_binding_scope": "original pre-cleanup snapshot, not the active package",
            "original_manifest_unchanged": True,
            "profiles": {p["id"]: p["expected_counts"] for p in profiles},
            "status_counts": dict(Counter(r["status"] for r in rows)),
            "fresh_inference_performed": False, "gold_rescoring_performed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("verify",))
    parser.parse_args()
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
