# Validation status

Source repository: [DuffyCoder/AgentDebug](https://github.com/DuffyCoder/AgentDebug).
This page records local validation, not a release tag or a Python package upload.
The reference environment is Linux with Python 3.11.

## Validation scope

The supported method is checked with synthetic inputs, real frozen validators,
stubbed model execution, public CLI routing tests and saved-artifact verification.
The CLI aliases and Python API must all select the same method. Tests check
stage order, fixed configuration, fresh attempt directories, exact-copy
arbitration and rejection of altered frozen inputs.

The public checks do not require private datasets or call model services.
Original source and result hashes remain independently verifiable through the
snapshot and the declared current module mapping. The existing
26/50 observation is not a fresh accuracy measurement of the public adapter.

## Recorded local checks — 2026-09-06

The public suite passed 94 tests in both the working checkout and an independent
source export with a fresh locked environment. Current research tools passed
36 tests, and the frozen historical research suite passed 80 tests in a separate
restored tree. All four non-mutating local commit hooks passed in the export.

A separately installed wheel passed 18 supported-method tests and synthetic
ingestion/validation outside the checkout. Its four command names produced
identical help output. Wheel and source-distribution inspection found no package
boundary issues (50 wheel members, 57 source-archive members). The installed
framework contains 44 Python files and imports neither research tools nor
repository scripts. The 16 selected release artifacts, the original 1,234-file
source snapshot and all 13 protocol-component relocations verified successfully.
Whole-stage synthetic prompts and validator audits match the restored original
after only declared module paths and installation-root relocation.

Local offline rescoring retained 26/50, 16/50 and 13/50; all 50 per-case prediction
and metric flags matched the saved table. Current-file hygiene additionally
scans decompressed snapshot members for common key patterns. These are local
checks, not fresh model inference, a hosted CI run, or a published release.

## Commands

| Check | What it establishes |
|---|---|
| `make test-public` | Supported method, shared public interface, data tools and publication checks |
| `make docs-check` | Maintained links, neutral public naming and archive navigation boundary |
| `make verify` | Documentation, layout, current/snapshot-content hygiene and saved release integrity |
| Distribution inspection | Wheel/source archive boundaries and absence of bundled raw data |
| Installed-wheel smoke checks | Public commands work outside the source checkout |

## Limitations

No new paid model experiment is part of this refactor. Hosted output may differ
across runs, backends or service changes. Passing synthetic tests establishes
the adapter contract, not empirical backend equivalence.

The public suite does not claim that every archived experiment test passes.
The preceding full run, before physical source separation, covered 237 test files: 236 passed, one
previously recorded recovery-ledger identity check failed, and none timed out.
That full suite was not rerun during relocation. The failure was retained,
not skipped or repaired by changing historical hashes.
Details and earlier validation reports remain accessible
through the [research archive](../research/README.md).

The maintainer authorized this source publication and confirmed data/evidence
distribution permission on 2026-09-06; see [data provenance](data-provenance.md).
The destination is the maintainer-selected DuffyCoder repository. Local checks
do not establish hosted CI success; inspect [GitHub Actions](https://github.com/DuffyCoder/AgentDebug/actions)
for the status of the pushed commit. Subsequent releases should repeat
[the publication checklist](../PUBLISHING.md).
