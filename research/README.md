# Research archive

This is the single navigation entry for optimization history and RSI-Exam
task-authoring work. It is not a runtime dependency. Return to
[user documentation](../docs/README.md) for the supported method.

Moving material here does not make it private, undo prior exposure, or turn it
into hidden evaluation data. Scores, exclusions and actual backends remain explicit.

## Evidence and original source

| Resource | Contents |
|---|---|
| [Source restoration](archive/README.md) | Hash-verified pre-cleanup source: historical scripts, modules, tests, configs and diaries |
| [Source-layout record](source-layout-2026-09-06.md) | Physical migration, current checks and limits |
| [Complete history](results/experiment-history-2026-09-05/README.md) | 227 run-by-method records, including failures and exclusions |
| [Fixed-configuration curves](results/fixed-config-history-2026-09-06/README.md) | Model/runtime-separated iteration curves |
| [LLM API curves](results/llm-api-history-2026-09-06/README.md) | API experiments and explicit frozen-upstream reuse |
| [Method-family policy](results/method-family-policy.md) | Codex-family reporting without changing actual backend provenance |
| [Counts by exact case set](results/method-family-counts.md) | 209 valid runs: 110 LLM API and 99 Codex-family runs |
| [Historical GAIA shortlist](results/gaia50-leaderboard.md) | Selected observations, not a hidden leaderboard |
| [Reproduction profiles](configs/reproduction-profiles.json) | Original runner identifiers and fixed configuration |
| [Score ledger](results/accounting/per-case-ledger.json) | Text-free per-case accounting |
| [Original bindings](results/accounting/manifest.json) | Unchanged historical manifest; source paths resolve inside the snapshot |
| [SDK comparison](notes/sdk-comparison.md) | Backend-specific reproduction limitations |
| [Post-archive inventory](results/experiment-history-2026-09-05/post-archive-inventory.json) | Discoveries not added to reviewed valid-run counts |

The reviewed results end on 2026-09-05; GAIA-50 is exposed development data.
Only seven fresh GAIA-50 records have GPT-5.5/medium at every recorded stage;
four share the strict recorded three-stage host configuration. The 99-family-run
total is not 99 fixed-GPT-5.5 iterations.

Historical identifiers in profiles, report text and source manifests are archival
locators. Retired `scripts/...`, `docs/experiments/...` and versioned module
paths are available after [restoration](archive/README.md), not active entry points.

## RSI-Exam materials

- [Proposal package](rsi/agentdebug_gaia/README.md)
- [Copy-ready form](rsi/agentdebug_gaia/proposal.md)
- [中文填写说明](rsi/agentdebug_gaia/submission-guide.zh-CN.md)
- [Reviewer attachments](rsi/agentdebug_gaia/attachments/README.md)
- [Readiness ledger](rsi/agentdebug_gaia/readiness.json)
- [Data and split notes](data-and-splits.md)

Eight formal-task readiness gates remain open, including final dataset-rights
documentation, unexposed hidden instances, approved model access, calibration,
isolation and difficulty. The maintainer separately confirmed current repository
and evidence publication permission on 2026-09-06. This is a proposal, not a
sealed or submitted task. Never put this
archive, historical answers, or the full repository into a participant container.

## Continue recording experiments

Start new records under `research/iterations/<date>-<name>/`; do not restore
one-off runners to `scripts/` or add selectable alternatives to the public method.

Before execution record the parent, hypothesis, precise code change, immutable
source identity, per-stage model/backend, data/case-set identities, validation
rules, budgets, retry policy and primary metric. Afterward add output hashes,
coverage, failures, all scores and acceptance/rejection, including stage reuse.

Retain negative results. Use new output directories and a new reviewed snapshot
for new observations. Never regenerate old source hashes to make changed code
pass, or silently add records to the dated history.

## Maintainer commands

```bash
make research-check
make -f research/Makefile proposal-build
make -f research/Makefile rsi-ready
```

The last command intentionally fails while readiness gates remain open.
Current tools live in [tools/](tools/README.md). Full historical testing and
original report regeneration require a separate restored workspace, with any
licensed data/local outputs obtained separately; see [archive instructions](archive/README.md).
