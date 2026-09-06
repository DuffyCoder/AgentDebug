# Development and testing

## Environment

Use the committed lockfile with Python 3.11:

```bash
uv sync --frozen --extra dev
make check
```

`PYTHON` can select an existing environment without modifying it:

```bash
make check PYTHON=.venv/bin/python
```

## Test boundaries

| Command | Scope | External data or live inference |
|---|---|---|
| `make test` / `make test-public` | Current method, trace, benchmark, archive and public-interface tests | Neither |
| `make verify` | Documentation, layout, hygiene and selected artifact integrity | Neither |
| `make check` | Both of the above | Neither |
| `make prepare-commit` | Public checks, review-only file inventory and local-history pattern scan | Neither |
| `make research-check` | Current research tools/accounting plus a restored frozen research suite | No live inference; uses repository archive files |
| `make test-all ARCHIVE_WORKSPACE=PATH` | Original test files in a verified restored workspace | Some files need local `data/` and `output/` |

The default suite is intentionally the public framework suite, not a claim that
all historical tests pass. Historical modules live only in the source snapshot. Some mutate shared globals
at import time, so their full suite runs one file per process inside an explicit
restored workspace, never against the current package. Logs are written under
that workspace's `output/test-reports/`. Restoration and data requirements are
in the [research archive](../research/README.md). Do not skip failing assertions.

Individual synthetic tests can run directly:

```bash
uv run python -m pytest -q tests/test_public_interface.py
```

Optional local commit hooks check documentation, layout, hygiene and artifact
integrity; they do not rewrite files. Archive-specific maintenance commands
live in `research/Makefile` and are documented through the research gateway.

The [validation status](release-status.md) distinguishes current public checks
from earlier private-input tests and their unresolved failures.

## Repository conventions

Use small, focused changes. Keep examples synthetic and use temporary directories
in tests. Stub provider calls rather than requiring credentials. Preserve frozen
protocol and artifact identities; version semantic changes separately.

Public documentation links are checked by `make docs-check`. The checker covers
the maintained public pages and the research gateway/current proposal, not every
historical notebook or network URL. Preserve a single research navigation entry
instead of adding iteration diaries to the user-facing introduction.

See [Contributing](../CONTRIBUTING.md) for review expectations and
[Publishing](../PUBLISHING.md) for wheel/source-distribution checks.
