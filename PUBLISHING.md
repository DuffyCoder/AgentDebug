# Publication checklist

This guide is for maintainers preparing a GitHub source release or Python
distribution. Passing automated checks does not authorize publication of data,
quoted evidence, or a destination repository.

## Review the release surface

| Content | Treatment |
|---|---|
| Framework, scripts, tests, configuration | Review source, dependency completeness, and compatibility |
| Documentation and derived score tables | Review accuracy, attribution, private paths, and copied content |
| Frozen prediction and audit artifacts | Review privacy and redistribution rights for quoted evidence |
| Dependency lock and transport requirements | Preserve exact reproduction requirements; keep optional transports separate |
| `data/`, `output/`, credentials, environments, caches | Keep out of Git and package archives |
| Private evaluation data and service credentials | Keep outside the repository, including Git history |

The active package contains only the selected method and its dependencies.
Historical modules/scripts/tests are retained in a hash-verified source snapshot;
review its contents as well as the visible tree before publishing the archive.
No runtime import may depend on repository scripts or research code.
The Python wheel provides the framework; reproduction scripts and evaluation
evidence belong to the source checkout. The source distribution intentionally
excludes research material and data-derived artifacts as well.

## Prepare a commit without changing Git state

```bash
make prepare-commit
```

This runs public checks, scans reachable local Git history for common key
patterns, and writes a timestamped review directory under the ignored
`output/commit-preparation/`. It does not stage, commit, push, install Git hooks,
or rewrite history.

The review directory contains:

- `inventory.json`: source hashes, additions/modifications/deletions, existing
  staged paths, and the scope and limitations of hygiene/history checks.
- `changes.txt`: the exact proposed paths for manual review.
- `candidate-paths.nul`: those paths in NUL-separated machine-readable form.
- `commit-message.txt`: a suggested message, not an executed commit.

The inventory describes the working-tree candidate, not necessarily what is
already staged. Review inherited removals and data-derived evidence separately.
Regenerate it if files change. A negative pattern scan does not establish that
all secrets are absent or grant permission to redistribute data.

The current-file check also verifies and scans decompressed source-snapshot
members. It does not replace review of nested attachments, data-derived excerpts
or historical blobs outside its documented pattern/manifest coverage.

To also export exactly the reviewed present files without ignored local state:

```bash
uv run python -m scripts.maintenance.prepare_commit --scan-history --export-source
```

Use the export for an independent source check. It contains no `.git` history;
initialize a temporary local repository there before Git-based hygiene checks.
The export is a source candidate, not a published or committed checkout.

## Verify a source checkout

```bash
uv sync --frozen --extra dev
make check
git diff --check
```

Repeat these checks in a fresh checkout without `data/` or `output/` before
making a release. `make check` covers public tests, documentation links,
repository hygiene, and selected artifact integrity. It is not a fresh model
evaluation. [Validation status](docs/release-status.md) explains the boundaries.

If publishing the research archive, also run `make research-check` and review
its contents under [the archive's procedures](research/README.md). Archives
remain visible and searchable even when absent from the project introduction.

## Check distributions

```bash
uv build
uv run python -m scripts.maintenance.check_distribution dist/agentdebug-0.4.0*
```

Build in a fresh source export to avoid stale build products from retired
modules. Inspect both wheel and source-distribution contents. In a fresh environment,
install the wheel and check the public command and its three compatibility
names. Run synthetic ingestion/validation outside the checkout to detect accidental imports
from the working directory. Builds and local installs do not upload anything.

## Before a public push

- Confirm the intended repository owner, URL, release version, and permissions.
- Review [data provenance](docs/data-provenance.md), upstream attribution, and
  evidence excerpts. Unknown redistribution permission remains unresolved.
- Review staged additions, modifications, and deletions individually. Do not
  indiscriminately stage a research workspace with `git add -A`.
- Inspect Git history as well as current files for secrets and private data.
  The built-in hygiene check examines current candidate files, not all past commits.
- If a secret has been exposed, revoke/rotate it before coordinating cleanup.
- Configure repository-specific private vulnerability reporting, branch
  protections, and release permissions on GitHub.
- Publish only after a clean-checkout test and owner approval of the release contents.

Keep the original [MIT license](LICENSE). Do not label this fork as the upstream
official implementation or claim that local scores reproduce paper results.
