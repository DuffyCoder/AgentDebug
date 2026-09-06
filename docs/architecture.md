# Architecture

AgentDebug has one supported diagnosis method: an anchored diagnosis, a single
later challenger, and conservative arbitration. Model configuration is fixed
to GPT-5.5 with medium reasoning effort.

```text
Processed AgentErrorBench GAIA trajectories
                   |
       Gold-free manifest + ordered cohort
                   |
           Input / identity checks
                   |
     Chronological ledger -> frozen anchor
                   |
       At most one later causal challenger
                   |
       Default-keep, exact-copy arbitration
                   |
        Schema / taxonomy / evidence audit
                   |
            Frozen predictions
                   |
     Separate scoring process with labels
```

## Diagnosis stages

1. **Anchor:** inspect the timeline chronologically, checking memory/reflection
   state fidelity, hard constraints and execution conditions, then strategy
   repetition or abandonment. Freeze the earliest admissible step before
   choosing its module, error type and literal evidence.
2. **Challenger:** seek at most one strictly later, independently causal error.
   Repairing the anchor must not already remove the later failure. Uncertainty
   or lack of a qualifying challenge retains the anchor.
3. **Arbiter:** independently review the challenge. Keep the anchor by default;
   otherwise select the challenger's prediction verbatim. No third prediction,
   blended answer, or semantic rewrite is permitted.

Each stage uses a fresh session. `agentdebug.method` calls the selected protocol
in `agentdebug.diagnostics.protocol`; public commands do not choose among methods.
Thirteen original components were extracted with declared module-token changes,
including executable paths in prompts. Source mapping and prompt/validator
parity tests guard this relocation; it is not a byte-identical prompt claim.
Three sessions are not three raw LLM API calls: each session may use multiple
model turns and validation tools. Failed stages have at most two attempts.

## Components

| Module | Responsibility |
|---|---|
| `agentdebug.method` | The supported method, fixed configuration, execution and strict validation |
| `agentdebug.cli` | Shared public CLI and compatibility command names |
| `agentdebug.trace` | General trace ingestion and structural checks |
| `agentdebug.benchmark` | Processed-trajectory adapters, input identities and score accounting |

General OpenClaw/Moltbot normalization is still available, but is not evidence
that the diagnosis method has been validated on those formats. Public diagnosis
currently requires processed GAIA manifests; there is no alternative fallback.

## Trust and reproducibility boundaries

Only label-free manifests, cohort membership and permitted prior-stage artifacts
are inputs to diagnosis. Source and stage hashes are checked; an altered anchor
fails the run. A failed case prevents publication of a partial successful batch.

The standalone adapter uses Codex CLI with fresh ephemeral sessions,
workspace-write sandboxing and web search disabled. It does not provide
filesystem read isolation: run with a separate container/account for sensitive
or held-out data. Prompt restrictions and hash checks are not an anti-cheating
security boundary. Review account configuration and permissions before execution.

The standalone adapter is new orchestration around the frozen method. The
saved score was measured with host-orchestrated Codex sessions, not re-measured
with this adapter. See [evaluation](results/README.md) and
[reproduction](../REPRODUCING.md).

Protocol identities remain in audit metadata for reproducibility, not in the
public method name. The active package imports neither repository scripts nor
research tools. Retired implementations, runners and tests exist only in a
restorable source snapshot, not the wheel. See the
[research archive](../research/README.md).
