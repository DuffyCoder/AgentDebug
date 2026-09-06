"""Reproduce the selected protocol components from the verified source snapshot.

Only module identifiers/import paths change. Audit identities, function names,
prompt decisions and validation logic are retained. This is not a new score.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

from scripts.maintenance.archive import verified_members

ROOT = Path(__file__).resolve().parents[2]
MODULE_MAP = {
    "agent_judge": "_contract",
    "agent_judge_v2_4": "_owner_sources",
    "agent_judge_luna_v3": "_causal_task",
    "agent_judge_luna_gaia_v1": "_nested_sources",
    "agent_judge_luna_gaia_v2": "_feedback_sources",
    "agent_judge_luna_gaia_v2_1": "_evidence_policy",
    "agent_judge_luna_gaia_v3": "_step_freeze",
    "agent_judge_luna_gaia_v3_1": "_anchor_policy",
    "agent_judge_luna_gaia_v3_4": "_candidate_ledger",
    "agent_judge_luna_gaia_v3_13_conservative_challenger": "_debate",
    "agent_judge_luna_gaia_v3_14_earliest_causal_challenger": "_protocol_challenger",
    "agent_judge_luna_gaia_v3_20_packet_state_closure": "_state_closure",
    "agent_judge_gaia_v3_83_clean_v3p20_model_only_gpt55_medium": "protocol",
}
TOKEN = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(
    re.escape(name) for name in sorted(MODULE_MAP, key=len, reverse=True)
) + r")(?![A-Za-z0-9_])")


def relocate(text: str) -> str:
    return TOKEN.sub(lambda match: MODULE_MAP[match[0]], text)


def run(*, check: bool = True, root: Path = ROOT) -> dict:
    sources = dict(verified_members(root / "research/archive/source-snapshot.json"))
    mapping = []
    for original, current in MODULE_MAP.items():
        old = f"agentdebug/diagnostics/{original}.py"
        new = f"agentdebug/diagnostics/{current}.py"
        before = sources[old]
        after = relocate(before.decode()).encode()
        ast.parse(after)
        target = root / new
        if check:
            if not target.is_file() or target.read_bytes() != after:
                raise ValueError(f"protocol component differs from declared relocation: {new}")
        else:
            if target.exists():
                raise ValueError(f"refusing to overwrite protocol component: {new}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(after)
        mapping.append({"original_path": old, "current_path": new,
                        "original_sha256": hashlib.sha256(before).hexdigest(),
                        "current_sha256": hashlib.sha256(after).hexdigest()})
    document = {
        "schema_version": "agentdebug.protocol-relocation.v1",
        "transformation": "bounded module-token substitution only, including executable paths in prompts",
        "semantic_constants_and_audit_identities_unchanged": True,
        "fresh_accuracy_measured": False,
        "modules": mapping,
    }
    manifest = root / "artifacts/protocol-source-map.json"
    if check:
        if json.loads(manifest.read_text()) != document:
            raise ValueError("protocol source map differs from verified extraction")
    else:
        manifest.write_text(json.dumps(document, indent=2) + "\n")
    return {"verified_protocol_components": len(mapping), "only_declared_path_changes": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing files; never overwrite")
    args = parser.parse_args()
    print(json.dumps(run(check=not args.write), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
