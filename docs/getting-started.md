# Getting started

## Install

Python 3.10+ is required; Python 3.11 is the reference environment.
From a source checkout:

```bash
python -m pip install -e .
agentdebug --help
```

For development, use `uv sync --frozen --extra dev`. With this environment,
prefix commands with `uv run` or activate `.venv`.

## Normalize and validate a trace

The included example is synthetic and needs no credentials:

```bash
agentdebug ingest \
  --session examples/moltbot_failure_session.jsonl \
  --task examples/email_triage_task.yaml \
  --output output/example.canonical.json

agentdebug validate \
  --session examples/moltbot_failure_session.jsonl \
  --task examples/email_triage_task.yaml \
  --output output/example.integrity.json --strict
```

These are local data tools, not semantic diagnosis. A valid trace may still
describe a failed task. General source ingestion does not imply that the
diagnosis method has been evaluated on every supported source format.

## Configure a judge

AgentDebug uses one fixed configuration: **GPT-5.5 / medium**, with an anchor,
one later challenger, and a conservative arbiter. No model or method selector
is exposed. The live adapter requires an authenticated Codex CLI with access
to this model; it does not fall back to another model.

See the [official non-interactive Codex documentation](https://learn.chatgpt.com/docs/non-interactive-mode)
for authentication and execution setup. Sessions can incur charges. Review
trace contents, permissions and the [security guidance](../SECURITY.md) first.

## Prepare a diagnosis

The current diagnosis input is a gold-free prediction manifest of processed
AgentErrorBench GAIA trajectories and its matching cohort. It is not raw GAIA
QA data or an arbitrary session file. Use the [reproduction guide](../REPRODUCING.md)
to obtain and prepare licensed input locally.

```bash
agentdebug analyze \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --cohort-manifest benchmarks/cohorts/gaia-paper-v1.json \
  --output-dir output/diagnosis-plan
```

Without `--execute`, the command checks and shards inputs without model calls.
Every invocation needs a new output directory.

## Execute the same method

```bash
agentdebug analyze \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --cohort-manifest benchmarks/cohorts/gaia-paper-v1.json \
  --output-dir output/diagnosis-live \
  --execute
```

There are three fresh sessions per case, with at most four cases running
concurrently and two attempts per stage. No labels are accepted by this command.
The CLI adapter is not a sealed evaluation container; do not make hidden data
accessible to the model process.

## Read the output

Inspect `run.json` first: `prepared` means no inference ran; `validated`
means every required stage and the combined prediction bundle passed the frozen
checks; `failed` records execution failure. Successful validation does not prove
the model's diagnosis correct.

Successful runs include `predictions.json`, stage artifacts and audit records.
Detailed implementation identities remain in `provenance.json`. No published
score is copied into a new run. Score separately using licensed labels.

The old executable names `agentdebug-trace`, `agentdebug-benchmark` and
`agentdebug-agent-judge` are aliases of this CLI, not different methods.
Their former model/protocol arguments are no longer supported.

Next: [architecture](architecture.md), [CLI reference](reference/cli.md), or
[Python API](framework-guide.md#python-api).
