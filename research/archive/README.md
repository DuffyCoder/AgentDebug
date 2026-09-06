# Original source snapshot

[source-snapshot.json](source-snapshot.json) indexes all 1,234 files in the
reviewed working-tree candidate immediately before physical source separation.
[source-snapshot.tar.gz](source-snapshot.tar.gz) preserves their exact bytes and
relative paths. Every member and the compressed archive have SHA-256 bindings.

This is a pre-cleanup source candidate, **not** proof that all historical
experiments used this exact checkout. Original as-run provenance and its limits
remain in the result records. Git history, ignored data/output, environments
and credentials are not included. Archived prediction evidence still requires
privacy and data-rights review before redistribution.

## Verify and restore

From the current repository root, using the locked development environment:

```bash
uv run python -m scripts.maintenance.archive verify
uv run python -m scripts.maintenance.archive extract \
  --destination output/restored-source
```

The destination must not exist. Verification rejects changed bytes, missing or
duplicate members, links and unsafe paths before restoration. The command does
not stage, commit or modify the live framework. Historical paths then resolve
inside `output/restored-source/`, including:

- `scripts/`: original runners and one-off audits;
- `agentdebug/`: original protocol modules and registry;
- `tests/`: original regression files;
- `configs/experiments/`: original configurations;
- `docs/experiments/`: hypotheses, preregistrations and investigations;
- `research/`: earlier cleanup/validation records and the previous reviewer ZIP.

## Run historical checks

`make research-check` already restores a temporary tree and runs its 80 frozen
research tests; it neither imports the old code into the active runtime nor
needs data/model access. The temporary tree is removed afterward.

For the complete historical suite, restore explicitly, provide any licensed
`data/` and original `output/` artifacts separately, then run:

```bash
make test-all ARCHIVE_WORKSPACE=output/restored-source
```

The launcher verifies original source bytes first and runs each historical test
file in a separate process. It does not create a model experiment. Logs go to
the restored workspace's `output/test-reports/`. Do not edit source hashes or
skip assertions to get a green report. Missing private fixtures are not passing
tests; adding fixtures does not justify including them in Git.

The previously recorded complete run covered 237 files: 236 passed, one known
recovery-ledger identity check failed, no timeouts. This result belongs to the
pre-cleanup layout. The failure remains recorded in
[the migration report](../source-layout-2026-09-06.md); it is not erased by the
current public suite passing.

## Regenerate a historical report

Use the restored original tools only in a disposable restored workspace with
the exact required source outputs. They write derived files in that workspace.
Compare before promoting any new report; never replace the frozen snapshot,
original manifests or reviewed result counts in place. The current
`research.tools.research_release verify` checks relocated results against the
unchanged original bindings and intentionally has no re-signing command.

[Research entry](../README.md)
