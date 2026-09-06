# Proposal attachments — authors/reviewers only

Prepared 2026-09-06. These are evidence and design materials, not a finished
RSI task, a redistributable data release, or an uploaded submission.

Download/use [agentdebug-rsi-proposal-evidence.zip](agentdebug-rsi-proposal-evidence.zip).
The ZIP preserves repository-relative paths. It is intentionally not the full
research repository; give reviewers an actual code link in form field 5.1.

| Attachment | Purpose |
|---|---|
| [01-experiment-evidence.md](01-experiment-evidence.md) | Fixed-model evidence, development process and honest limitations |
| [02-fixed-gpt55-iterations.png](02-fixed-gpt55-iterations.png) / [PDF](02-fixed-gpt55-iterations.pdf) | All seven fresh GPT-5.5/medium GAIA-50 observations; connect only the four matched host runs |
| [Supplementary Luna PNG](../../../results/fixed-config-history-2026-09-06/01-luna-gaia50-fixed-three-stage.png) / [PDF](../../../results/fixed-config-history-2026-09-06/01-luna-gaia50-fixed-three-stage.pdf) | 31-version fixed-Luna history: early gains and subsequent plateau; not GPT-5.5 evidence |
| [03-metric-and-seal.md](03-metric-and-seal.md) | One-number objective, data boundary and shortcut tests |
| [04-reproduction-and-runtime.md](04-reproduction-and-runtime.md) | Starter/reference sources, offline verification and unresolved runtime work |
| [05-sources-and-licensing.md](05-sources-and-licensing.md) | Official sources, data provenance and permission gaps |
| [experiment-evidence.json](experiment-evidence.json) / [codex-sdk-family-runs.csv](codex-sdk-family-runs.csv) | All 99 valid family runs with actual backends, models, scores and source hashes |
| [bundle-manifest.json](bundle-manifest.json) | Exact ZIP file allowlist and SHA-256 integrity bindings |

The bundle also includes the form, agent instruction draft, design/readiness
notes, reproduction profiles, pinned SDK dependencies, score/split prototype
code and its tests, and the unified reporting/counting policy. Prototype code
does not execute submissions or provide a sandbox; it is not an official grader.

Excluded: raw trajectories, gold labels, prediction/evidence quotations,
model transcripts, authentication files, hidden data, all of output/, data/,
.git/, and the stronger solution implementations. Thus this ZIP cannot itself
reproduce model inference; the reviewed code repository and authorized data
are also needed. Reference locations in documents are not bundled file promises.

Do not copy these attachments into the participant image. Even without raw
data they disclose strong methods and development scores. The final agent
image must be separately allowlisted after proposal review.

Rebuild (from the full repository; numerical analysis only, no model calls):

```bash
make -f research/Makefile proposal-build
make -f research/Makefile proposal-check
```

Matplotlib is needed only for author-side figure generation. The check command
uses the standard library and the already generated evidence packet.

The extracted ZIP can run its synthetic metric/split/readiness tests with
Python and pytest installed, from the extraction root:

```bash
python -m pytest -q tests/test_rsi_authoring_contracts.py
```

These synthetic tests do not use real trajectory labels or execute a model.
