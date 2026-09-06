# Reproducing AgentDebug

This repository exposes one diagnosis method, AgentDebug, using GPT-5.5 with
medium reasoning effort. Its saved observation on 50 processed AgentErrorBench
GAIA trajectories is Step Exact **26/50**, Step + Module **16/50**, and All
Correct **13/50**. See [evaluation](docs/results/README.md) for limitations.

Artifact verification, rescoring saved predictions, and fresh inference are
different operations. Passing one does not claim that another has run.

## Install

Python 3.11 is the reference environment (package minimum: Python 3.10).

```bash
uv sync --frozen --extra dev
```

All release-management commands below run from a source checkout. Live inference
additionally needs an authenticated Codex CLI with access to GPT-5.5.
No model calls are made by preparation, verification, or scoring.

## Verify the saved release

```bash
uv run python -m scripts.reproduction.release verify
```

Expected output includes `verified_artifact_count: 16`, `step_exact: "26/50"`,
`accuracy: 0.52`, and `legal_full_run: true`. This checks the frozen evidence,
original implementation hashes, declared current module-path relocation, complete
50-case prediction set, and recorded legality. Original source hashes resolve
inside the verified source snapshot; they are not re-signed for the active
package. `make verify` additionally checks layout, documentation and hygiene.

Exact archived identities remain in audit metadata; no experimental version
selector is required to use or verify the public method.

## Obtain the processed data

Obtain the AgentErrorBench release from the sources in
[data provenance](docs/data-provenance.md), respecting its access and
redistribution terms:

```text
data/AgentErrorBench/
├── Label/
└── Original_Failure_Trajectory/
    └── GAIA/
```

The complete expected dataset identity is
`fa78de42eb1de06e3566555bd8c68f09deaa6930f2b07ac8937ded858cc6ac11`.
Raw data is not included in the package.

## Prepare gold-free inputs

```bash
uv run python -m scripts.reproduction.release prepare \
  --source-root data/AgentErrorBench/Original_Failure_Trajectory/GAIA \
  --cohort benchmarks/cohorts/gaia-paper-v1.json \
  --output-dir output/gaia-inputs
```

This reads released trajectories, not labels. The generated manifest contains
complete JudgeViews and is approximately 93 MiB. Use a new output directory.

Verify data and manifest identity:

```bash
uv run python -m scripts.reproduction.release verify \
  --dataset data/AgentErrorBench \
  --cohort benchmarks/cohorts/gaia-paper-v1.json \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json
```

## Rescore the published predictions

```bash
uv run python -m scripts.reproduction.release rescore \
  --dataset data/AgentErrorBench \
  --cohort benchmarks/cohorts/gaia-paper-v1.json \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --output-dir output/release-rescore
```

This validates the saved predictions before reading labels and checks that
Step Exact remains 26/50. It does not launch model inference.

## Run fresh inference

First prepare without using a model:

```bash
uv run agentdebug analyze \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --cohort-manifest benchmarks/cohorts/gaia-paper-v1.json \
  --output-dir output/agentdebug-plan
```

Then explicitly start a new run:

```bash
uv run agentdebug analyze \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --cohort-manifest benchmarks/cohorts/gaia-paper-v1.json \
  --output-dir output/agentdebug-live --execute
```

A complete 50-case run requires 150 fresh stage sessions before retries.
The default allows four concurrent cases and at most two attempts per stage.
Every invocation requires a new output directory. A failed required stage
fails the batch; no partial successful score is published.

Validate and score a successful new run separately:

```bash
uv run agentdebug validate-predictions \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --cohort-manifest benchmarks/cohorts/gaia-paper-v1.json \
  --predictions output/agentdebug-live/predictions.json

uv run python -m scripts.reproduction.release score \
  --dataset data/AgentErrorBench \
  --cohort benchmarks/cohorts/gaia-paper-v1.json \
  --prediction-manifest output/gaia-inputs/prediction-manifest.json \
  --run-dir output/agentdebug-live --output-dir output/agentdebug-score
```

## Interpretation and isolation

The saved result was measured with host-orchestrated Codex sessions. The
public standalone CLI adapter uses the selected diagnostic rules and validators.
Executable module paths in generated prompts were relocated; exact source
mapping and whole-stage prompt comparisons check this limited change. The adapter
does not inherit the saved measured accuracy. Fresh hosted-model output can
vary, and the new adapter has not been assigned a fresh accuracy result.

GAIA-50 is exposed development material, not a hidden test. The public adapter
is not an OS-level read-isolation boundary: run in a separate container or
account without hidden labels, old outputs or sensitive files when that
isolation matters. Review [security](SECURITY.md) and
[data rights](docs/data-provenance.md) before execution or redistribution.

Exact original runners, hashes, historical configurations and backend-specific
provenance are accessible through the [research archive](research/README.md).
