# Physical source separation — 2026-09-06

This is a local working-tree change, not a commit, tag, push or new model run.

## What moved

The pre-cleanup candidate contained 1,234 files. A reviewed migration moved
1,137 original files into an ignored local recovery directory; 98 maintained or
browsable copies were placed at their new locations. The complete pre-cleanup
candidate is also retained in [the verified source snapshot](archive/README.md).
No original history, runner source, test or configuration was discarded.

Local recovery copies remain under `output/reorganization/retired/`; the exact
pre-cleanup export is under `output/reorganization/before-2026-09-06/source/`.
These ignored working directories are not included in the source candidate.

| Previous active surface | Current location |
|---|---|
| Historical flat scripts, experimental modules/tests/configs, dated diaries | Exact original paths inside the source snapshot |
| General source-checkout checks | `scripts/maintenance/` |
| Supported release commands | `scripts/reproduction/` |
| Research utilities and authoring checks | `research/tools/` and `research/tests/` |
| Historical tables, curves and per-case accounting | `research/results/` |
| Selected prediction bundle | `artifacts/releases/reference/` |

The active framework shrank from 245 to 44 Python files. It imports neither
`scripts` nor `research`. The source package and wheel contain only the current
framework; original protocols/runners are not alternate public defaults.

## Source and experimental identity

The selected historical method is v3.83, publicly named AgentDebug. Its 13
required protocol components were extracted with bounded module-token
substitutions. Original audit identities and function contracts are retained.
[The source map](../artifacts/protocol-source-map.json) binds both original and
current bytes. Generated executable module paths differ, so this is not an
unchanged-prompt-byte claim or proof of fresh empirical equivalence.

A golden comparison caught a short-name collision during the migration: a
rewriter for `_challenger` also changed the output value `accept_challenger`.
The module was renamed `_protocol_challenger`; the complete three-stage prompts
now compare exactly after only declared module tokens and installation root
relocation, and stage validator audits match the original restored code.

The original research manifest is unchanged: 227 records, 21 bound result files
and 822 source bindings verify against the original snapshot. Per-case flags
retain 209 valid runs (110 API, 99 Codex family). The complete history JSON SHA:
`8c7b610e8281e6404854885cdcc6894bd65b30ca9f3f2cc5c4c07195b89445d0`.

All 16 selected evidence artifacts verify. Offline rescoring with the local
licensed data retained 26/50 Step, 16/50 Step+Module and 13/50 All; all 50
per-case predictions and score flags matched the original table. This is
rescoring, not fresh inference. No accuracy is assigned to the new execution
adapter from this check. All original GAIA-50 cases remain exposed.

## Verification and unresolved history

The current verification summary is in [validation status](../docs/release-status.md).
The working checkout and an independent export passed 94 public tests and 36
current research tests. The independent wheel passed 18 method tests, four CLI
aliases and synthetic ingestion/validation outside either source tree. Its 50
members and the source distribution's 57 members passed boundary inspection.
The frozen 80-test research suite was rerun successfully in a temporary restored
tree, separately from current source tests. The original full historical suite
was not rerun as part of physical relocation.

Its preceding local run covered 237 files: 236 passed, one known failure, no
timeouts. The retained failure is
`tests/test_v58_smoke_recovery_v3.py::test_v3_boundary_is_exact_and_provider_free`:

- expected recovery ledger SHA:
  `177cc0d197496ec3416873e18a37e9aa0cf4ff1d992e66787674da54e4110b50`;
- available ledger SHA:
  `d2ea34f80101600321df896a6545a59ee2ad20d6a8d070f6c58e29f327843a28`.

The prior local report is
`output/test-reports/final-commit-reviewed-2026-09-06/summary.json`, SHA
`288f04fbbc23e01ab5329ea8a0cea5454952f52025301939ac59ce7440334bf4`.
It remains local, not a public fixture. Neither hash was re-signed, and the
test was not marked as skipped or expected-failing.

## Publication and task boundaries

The refreshed reviewer packet describes the new source locations while
retaining historical backends/scores. The eight formal RSI gates remain open.
No hidden set, calibrated anchor or approved offline service was fabricated.

Historical source is available, not private: do not include it, prior solutions,
the evidence bundle or the full repository in a participant container.
Data/excerpt rights and final publication scope still need owner review.
Git index and HEAD are not changed by migration/verification; review the
generated commit candidate before staging anything.

The final inventory is written locally under
`output/commit-preparation/source-layout-2026-09-06/`. It supersedes earlier
inventories whose paths still describe the old physical layout.
