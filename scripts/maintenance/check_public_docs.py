"""Check maintained local Markdown links and the public/archive navigation boundary."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_PAGES = (
    "README.md", "CONTRIBUTING.md", "PUBLISHING.md", "REPRODUCING.md",
    "SECURITY.md", "CHANGELOG.md", "examples/README.md", "artifacts/README.md",
    "docs/README.md", "docs/getting-started.md", "docs/architecture.md",
    "docs/development.md", "docs/reference/cli.md", "docs/framework-guide.md",
    "docs/results/README.md", "docs/data-provenance.md", "docs/release-status.md",
    "scripts/README.md", "tests/README.md", "configs/README.md", "benchmarks/README.md",
)
ARCHIVE_ROOTS = (
    "research", "docs/experiments",
    "docs/results/experiment-history-2026-09-05",
    "docs/results/fixed-config-history-2026-09-06",
    "docs/results/llm-api-history-2026-09-06",
)
ARCHIVE_FILES = {
    "docs/results/gaia50-leaderboard.md", "docs/results/method-family-counts.md",
    "docs/results/method-family-counts.json", "docs/results/method-family-counts.csv",
    "docs/reproduction/sdk-comparison.md",
}
GATEWAY = "research/README.md"
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)")


def prose(text: str) -> str:
    # Ignore fenced examples: links in quoted sample documents aren't navigation.
    result = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            result.append(line)
    return "\n".join(result)


def anchors(text: str) -> set[str]:
    used: dict[str, int] = {}
    result = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prose(text), re.MULTILINE):
        base = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        suffix = used.get(base, 0)
        result.add(base if not suffix else f"{base}-{suffix}")
        used[base] = suffix + 1
    return result


def local_links(text: str):
    for match in LINK.finditer(prose(text)):
        raw = match[1].strip("<>")
        parsed = urlsplit(raw)
        if parsed.scheme or parsed.netloc:
            continue
        yield raw, unquote(parsed.path), unquote(parsed.fragment)


def audit(root: Path = ROOT) -> dict:
    root = root.resolve()
    archive_pages = [GATEWAY, "research/data-and-splits.md"]
    archive_pages += [relative for relative in (
        "research/archive/README.md", "research/tools/README.md",
        "research/notes/sdk-comparison.md", "research/source-layout-2026-09-06.md",
    ) if (root / relative).is_file()]
    archive_pages += [p.relative_to(root).as_posix()
                      for p in sorted((root / "research/rsi").rglob("*.md"))]
    pages = [*PUBLIC_PAGES, *archive_pages]
    issues = []
    checked_links = 0
    for relative in pages:
        path = root / relative
        if not path.is_file():
            issues.append({"file": relative, "issue": "missing_document"})
            continue
        content = path.read_text(encoding="utf-8")
        public = relative in PUBLIC_PAGES
        if public and re.search(r"\b(?:RSI(?:-Exam)?|Airtable)\b", content, re.IGNORECASE):
            issues.append({"file": relative, "issue": "authoring_purpose_in_public_guide"})
        if public and re.search(r"\b(?:E5|luna-v1|v3[.p]83|v3[.p]107)\b", content, re.IGNORECASE):
            issues.append({"file": relative, "issue": "experimental_method_name_in_public_guide"})
        for raw, target, fragment in local_links(content):
            checked_links += 1
            resolved = (path.parent / target).resolve() if target else path.resolve()
            if Path(target).is_absolute() or not resolved.is_relative_to(root):
                issues.append({"file": relative, "link": raw, "issue": "nonportable_link"})
                continue
            destination = resolved.relative_to(root).as_posix()
            archived = destination in ARCHIVE_FILES or any(
                destination == prefix or destination.startswith(prefix + "/")
                for prefix in ARCHIVE_ROOTS
            )
            if public and archived and destination != GATEWAY:
                issues.append({"file": relative, "link": raw, "issue": "bypasses_archive_gateway"})
            if not resolved.exists():
                issues.append({"file": relative, "link": raw, "issue": "broken_local_link"})
            elif fragment and resolved.suffix == ".md" and fragment not in anchors(resolved.read_text(encoding="utf-8")):
                issues.append({"file": relative, "link": raw, "issue": "missing_heading"})
    return {"checked_documents": len(pages), "checked_local_links": checked_links,
            "issue_count": len(issues), "issues": issues,
            "network_links_checked": False, "scope": "maintained_public_docs_and_research_gateway"}


def main() -> int:
    result = audit()
    print(json.dumps(result, indent=2))
    return int(bool(result["issue_count"]))


if __name__ == "__main__":
    raise SystemExit(main())
