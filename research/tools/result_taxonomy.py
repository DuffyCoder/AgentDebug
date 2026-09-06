"""Publication categories, deliberately separate from as-run provenance.

"Codex SDK" is this project's umbrella method family. It includes historical
host-orchestrated Codex agents, NOT a claim that those runs used an SDK package.
Never use the family alone as a fixed-runtime or fixed-model comparison key.
"""
from __future__ import annotations

CODEX_FAMILY = "Codex SDK"
API_FAMILY = "LLM API"
POLICY_VERSION = "agentdebug.result-taxonomy.v1"
VALID_STATUSES = frozenset({"complete_scored", "scored_failures_zero"})


def classification(transport: str) -> dict[str, str]:
    if transport.startswith("Codex agent/subagent"):
        backend = "host-orchestrated Codex agent/subagent"
        family = CODEX_FAMILY
    elif transport.startswith(("Codex SDK", "Codex Python SDK")):
        backend = "Codex SDK/app-server"
        family = CODEX_FAMILY
    elif transport in {"LLM API", "Responses API"}:
        backend = transport
        family = API_FAMILY
    else:
        raise ValueError(f"Unclassified historical transport: {transport!r}")
    return {"method_family": family, "execution_backend": backend}


def valid_record(row: dict) -> bool:
    """Valid score accounting, not proof of fresh or independent inference."""
    return (row.get("csv_verified") is True and row.get("eligible") is True
            and row.get("status") in VALID_STATUSES)


def is_fixed_model(row: dict, model: str, effort: str | None = None) -> bool:
    """Inspect every recorded stage, including inherited stages and mixtures."""
    stages = row.get("stage_models") or {}
    configurations = list(stages.values()) if stages else [row]
    return bool(configurations) and all(
        isinstance(c, dict) and c.get("model") == model
        and (effort is None or c.get("reasoning_effort") == effort)
        for c in configurations
    )
