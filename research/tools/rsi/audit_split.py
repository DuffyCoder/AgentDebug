"""Check independently supplied split manifests without exposing hidden IDs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.tools.rsi.contracts import audit_split

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--visible", type=Path, required=True)
    parser.add_argument("--hidden", type=Path, required=True)
    args = parser.parse_args()
    if args.hidden.resolve().is_relative_to(ROOT):
        parser.error("hidden manifest must stay outside the public repository")
    try:
        report = audit_split(json.loads(args.visible.read_text()), json.loads(args.hidden.read_text()))
    except (ValueError, OSError):
        # Do not print JSON decode excerpts or offending identifiers.
        parser.exit(1, "split audit failed; inspect private inputs locally\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
