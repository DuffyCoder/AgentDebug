# AgentDebug

Evidence-grounded failure diagnosis for agent execution traces.

AgentDebug locates critical failures in processed AgentErrorBench GAIA traces
using an anchored diagnosis, one later challenger, and conservative arbitration.
It uses one fixed configuration: GPT-5.5 with medium reasoning effort.
General trace normalization, integrity checks and explicit scoring tools are
also included.

This is an independently maintained refactor of
[ulab-uiuc/AgentDebug](https://github.com/ulab-uiuc/AgentDebug), not the upstream
official release. The current Python API is not compatible with the original
detector API.

[Getting started](docs/getting-started.md) · [Documentation](docs/README.md) ·
[Reproduction](REPRODUCING.md) · [Contributing](CONTRIBUTING.md)

## What it provides

- **Trace normalization:** retain source events, tool-call relationships, and
  evidence references in a Canonical Trace.
- **Integrity checks:** detect broken references, missing tool results, and
  ambiguous execution branches before diagnosis.
- **One diagnosis method:** a frozen chronological anchor, one causal challenger,
  and an exact-copy arbiter produce evidence-validated predictions.
- **Evaluation tools:** prepare benchmark inputs, validate predictions, and
  compute explicit, fixed-denominator metrics.

## Quick start

Python 3.10+ is required; Python 3.11 is the reference environment. Run from a
source checkout:

```bash
python -m pip install -e .

agentdebug ingest \
  --session examples/moltbot_failure_session.jsonl \
  --task examples/email_triage_task.yaml \
  --output output/example.canonical.json

agentdebug validate \
  --session examples/moltbot_failure_session.jsonl \
  --task examples/email_triage_task.yaml \
  --output output/example.integrity.json \
  --strict
```

These commands run locally without model calls or benchmark downloads. The
included example is synthetic. To diagnose prepared GAIA inputs, follow
[the configuration guide](docs/getting-started.md#configure-a-judge).
Review sensitive trace contents before sending them to a provider.

The saved AgentDebug observation is **26/50 Step Exact**, **16/50 Step + Module**,
and **13/50 All Correct** on the exposed 50-case development cohort. It is not
an unseen-test score or a fresh measurement of the standalone execution adapter.
See [evaluation](docs/results/README.md) for execution provenance and limitations.

## Documentation

| Topic | Guide |
|---|---|
| Installation and a complete first run | [Getting started](docs/getting-started.md) |
| Pipeline, components, and extension points | [Architecture](docs/architecture.md) |
| Commands, inputs, and exit codes | [CLI reference](docs/reference/cli.md) |
| Selected benchmark results and limitations | [Evaluation](docs/results/README.md) |
| Artifact verification and fresh inference | [Reproduction](REPRODUCING.md) |
| Development and tests | [Contributing](CONTRIBUTING.md) |

## Development

```bash
uv sync --frozen --extra dev
make check
```

The default checks use synthetic fixtures and repository-contained artifacts.
They do not call model services or require private datasets. See the
[testing guide](docs/development.md) for test boundaries and optional checks.

```text
agentdebug/   Trace processing, diagnosis, and benchmark adapters
examples/     Small synthetic inputs
configs/      Selected release layout
tests/        Unit and regression tests
scripts/      Reproduction and maintenance tools
docs/         User and developer documentation
artifacts/    Selected evaluation evidence
research/     Separate research tools, results, and restorable source archive
```

## Attribution and license

Based on [AgentDebug](https://github.com/ulab-uiuc/AgentDebug) and its
[paper](https://arxiv.org/abs/2509.25370). Code is licensed under [MIT](LICENSE).
AgentErrorBench is distributed separately; datasets and quoted evidence do not
automatically inherit the code license. See [data provenance](docs/data-provenance.md).

[Security](SECURITY.md) · [Publication checklist](PUBLISHING.md) ·
[Research archive](research/README.md)
