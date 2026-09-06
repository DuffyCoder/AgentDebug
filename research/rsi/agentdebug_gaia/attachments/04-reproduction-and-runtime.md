# Reproduction and runtime evidence

## Candidate methods

| Role | Profile / history ID | Historical Step | Actual execution |
|---|---|---:|---|
| Starter source | official-sdk-v3 / R219 | 19/50 | Python SDK/app-server 0.147.0 |
| Executed stronger app-server source | sdk-v3p107 / R216 | 23/50 | Python SDK/app-server 0.147.0 |
| Best accepted family source | best-historical-v3p83 / R208 | 26/50 | Host-orchestrated Codex agents |
| Earlier paper-reproduction disclosure | official-gpt41 / R150 | 14/50 | GPT-4.1 direct API |

The first three use nominal GPT-5.5/medium. Their backends, output contracts
and budgets differ. v3.107 predates Official SDK v3. No controlled 19-to-26
gain or 0.52 app-server rerun is claimed. A model alias is not evidence of an
identical backend snapshot. The last row is not a fixed-GPT-5.5 comparator.

The full repository retains original runner/module identifiers in
research/configs/reproduction-profiles.json and exact provenance in
research/results/accounting/reproduction-index.json. Its REPRODUCING.md and
research/notes/sdk-comparison.md distinguish four levels of evidence:
saved-score accounting, artifact integrity, gold rescoring, and fresh inference.
Versioned runner paths resolve inside the verified pre-cleanup source snapshot,
not the active package. Follow research/archive/README.md to restore them.
The supported current method is standalone; its new source layout does not
supply a new measured score or a completed RSI runtime.

Without credentials or raw data, a complete reviewed checkout supports:

```bash
uv sync --frozen --extra dev
make verify
make test-public
make research-check
```

The small proposal ZIP is not a full checkout. It includes pointers/profiles
and metric/split prototypes, not all runner dependencies or stronger methods.
Model inference additionally requires authorized AgentErrorBench data, the
specified reference sources/dependencies and working model access. Execution
is explicit through documented --execute flags and fresh output directories.
Nothing in this submission-preparation pass calls a paid model.

## Runtime measurement actually available

Official SDK v3: 8,398.8245 wall-clock seconds for its recorded full workflow
(about 2.33 hours), 3,252 successful model calls (3,202 local-analysis calls and
50 selection calls), 52,224,583 total tokens. v3.107: 150 successful stages,
55,954,260 total tokens. A stage can contain multiple model/tool interactions
and recovery attempts; call counts and stage counts are not interchangeable.
Token totals are historical reported usage, not a price estimate. Score-import
duration is not inference duration.

SDK/app-server and its CLI dependency are pinned to 0.147.0 in the additive
research/requirements-transports.txt file. Host runtime versions were not uniformly recorded.
The current standalone CLI adapter is a reproduction path, not proof that the
historical host used that CLI version. Retain actual configuration and missing
metadata in any repeated run.

## Final-runtime work still required

Request an approved credential-isolated GPT-5.5/medium service; a no-network
container cannot simply run the existing remote-model code. Freeze service
version, model identity/alias disclosure, instructions, session lifecycle,
tool surface, read/write boundaries and per-case/full-run call/token/time caps.
Distinguish transport retries from semantic retries. Both consume real resources;
neither may silently become unbounded inference.

A simple llm_call interface may require explicit adaptation of the historical
filesystem-agent protocols. If a bounded stage-execution interface is required,
obtain approval and test both methods there. Do not claim a score transfers
across that change without measurement. Re-run starter/reference, then a scratch
optimization probe; demonstrate at least two full visible evaluations in twelve
hours. CPU/RAM requirements and final cost/latency are still unmeasured.
