# CLI reference

`agentdebug` is the public command. `agentdebug-trace`,
`agentdebug-benchmark` and `agentdebug-agent-judge` are compatibility executable
names for the same parser and method. `python -m agentdebug.cli` also works.

## Commands

| Command | Input / purpose | Model access |
|---|---|---|
| `ingest` | Normalize session/runtime/evaluation sources | None |
| `validate` | Check source integrity | None |
| `analyze` (alias `run`) | Prepare or execute diagnosis on gold-free processed GAIA manifests | Only with `--execute` |
| `validate-predictions` | Validate predictions and all required stage sidecars | None |

## Diagnosis options

| Option | Requirement or default |
|---|---|
| `--prediction-manifest PATH` | Required, hash-locked label-free inputs |
| `--cohort-manifest PATH` | Required, matching ordered processed GAIA cohort |
| `--output-dir PATH` | Required for `analyze`; must not exist |
| `--execute` | Opt-in to model sessions; absent means preparation only |
| `--codex-binary PATH` | `codex` |
| `--stage-timeout SECONDS` | `1800`, positive and finite |
| `--max-workers N` | `4`, range 1–4 |
| `--max-attempts N` | `2`, range 1–2 per stage |
| `--predictions PATH` | Required for `validate-predictions` |

The model is fixed to GPT-5.5 with medium reasoning effort. There is no
`--method`, `--protocol`, `--judge-provider`, or `--judge-model` option.
All diagnosis calls use the same anchor–challenger–arbiter method.

## Trace utility options

`ingest` and `validate` accept `--session`, `--runtime-trace`, `--eval-trace`,
supplementary `--manifest` and `--task`, plus `--output` and `--strict`.
At least one session, runtime or evaluation source is required.
Without `--output`, the destination is beside the first source. Existing trace
utility outputs may be replaced, so choose a new path to preserve prior results.

These utilities do not invoke a diagnosis method or imply cross-format accuracy.
`analyze --session ...` is no longer supported; supply prepared GAIA inputs.

## Exit codes and artifacts

`0` means completion. `2` means an argument/input error, a strict integrity
failure, or a failed diagnosis. Unexpected exceptions can exit nonzero as well.
No partial successful score is emitted when a required stage fails.

A completed diagnosis contains `run.json`, `predictions.json`, frozen stage
artifacts, `prediction-audit.json`, `artifact-hashes.json`, and
`provenance.json`. Failed attempts remain under the case directory.

## Reproduction and scoring

Source-checkout release operations use `python -m scripts.reproduction.release`
with `verify`, `prepare`, `rescore`, or `score`. These are bookkeeping and
data operations for the same method, not additional diagnostic algorithms.
See [Reproduction](../../REPRODUCING.md) for complete commands.
