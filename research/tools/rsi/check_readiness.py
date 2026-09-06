"""Validate the proposal's readiness ledger; fail closed for formal release."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT = ROOT / "research/rsi/agentdebug_gaia/readiness.json"
REQUIRED = {"data_rights", "hidden_split", "offline_runtime", "starter_and_reference",
            "sealed_calibration", "container_seal", "budget_and_difficulty", "shortcut_audit"}


def check(path: Path = DEFAULT) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    requirements = data["requirements"]
    if {r["id"] for r in requirements} != REQUIRED or len(requirements) != len(REQUIRED):
        raise ValueError("required readiness gates were removed or duplicated")
    for gate in requirements:
        if gate["status"] not in ("open", "verified") or not gate.get("reason"):
            raise ValueError("invalid gate status or missing rationale")
        if gate["status"] == "verified":
            evidence = gate.get("evidence", [])
            if not evidence:
                raise ValueError("verified gates need hash-bound review evidence")
            for binding in evidence:
                file = ROOT / binding["path"]
                if not file.resolve().is_relative_to(ROOT) or not file.is_file():
                    raise ValueError("review evidence must be a public, safe audit summary")
                if not file.stat().st_size or hashlib.sha256(file.read_bytes()).hexdigest() != binding["sha256"]:
                    raise ValueError("invalid review evidence hash")
    blockers = [r for r in requirements if r["status"] != "verified"]
    if not blockers:
        anchors = data["sealed_anchors"]
        baseline = anchors.get("baseline")
        if type(baseline) not in (int, float) or not 0 <= baseline <= 1:
            raise ValueError("formal release requires a measured sealed baseline")
        for key in ("reference", "upper_bound"):
            value = anchors.get(key)
            if value is not None and (type(value) not in (int, float) or not baseline < value <= 1):
                raise ValueError("invalid optional sealed anchor")
    return {"stage": data["stage"], "ledger_valid": True,
            "formal_task_ready": not blockers, "open_gate_count": len(blockers),
            "open_gates": [r["id"] for r in blockers],
            "sealed_anchors": data["sealed_anchors"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    report = check()
    print(json.dumps(report, indent=2))
    return int(args.require_ready and not report["formal_task_ready"])


if __name__ == "__main__":
    raise SystemExit(main())
