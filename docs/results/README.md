# Evaluation

AgentDebug diagnoses the critical failure in 50 processed GAIA trajectories
from AgentErrorBench. This is not GAIA question-answering accuracy.

## Published observation

| Method | Model | Step Exact | Step + Module | All Correct |
|---|---|---:|---:|---:|---:|
| AgentDebug | GPT-5.5 / medium | 26/50 (52%) | 16/50 (32%) | 13/50 (26%) |

Step Exact is the selection metric. “Best” here means the selected historical
result on this exposed 50-case development cohort, not best on every metric,
an official paper reproduction, or performance on unseen data.

The observation used host-orchestrated Codex sessions. In this project's
reporting taxonomy these belong to the Codex SDK method family; they were not
calls through the standalone SDK package. The public CLI reuses the frozen
diagnostic protocol with a standalone execution adapter. Its fresh accuracy
has not been measured; 26/50 must not be reported as its fresh result.

## Metrics

- **Step Exact:** predicted critical step equals the reference step.
- **Step + Module:** both step and responsible module match.
- **All Correct:** step, module and error type match under the recorded label policy.

Higher is better. All three denominators are 50. The published bundle has
complete legal predictions. Failed new runs are not partial successful
evaluations; do not silently drop cases or transfer this score to another
model, cohort or execution backend.

## Verification

[Reproduction](../../REPRODUCING.md) separates artifact verification, licensed
gold rescoring and fresh inference. Deterministic verification of saved evidence
is not a new model run. Data and excerpt rights are discussed in
[data provenance](../data-provenance.md).

Historical comparisons, exact implementation identities and full provenance are
retained only through the [research archive](../../research/README.md).
