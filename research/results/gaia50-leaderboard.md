# Frozen GAIA-50 Step Exact results

Step Exact is the sole selection metric in this experiment series. All rows
below use the frozen `gaia-paper-v1` 50-case denominator.

All rows below are in the **Codex SDK method family**, specifically its historical
host-agent execution subclass. The [unified reporting policy](method-family-policy.md)
does not turn them into SDK/app-server package invocations. This shortlist is not
the full history or a single fixed-model curve.

| Version | Model / effort | Step Exact | Legality | Decision |
|---|---|---:|---|---|
| Luna v3.4 | GPT-5.6 Luna / medium | 21/50 | Passed | Frozen baseline |
| Luna v3.20 | GPT-5.6 Luna / medium | 25/50 | Passed | Superseded incumbent |
| v3.83 | GPT-5.5 / medium | **26/50** | Passed, 50/50 | **Accepted incumbent** |
| v3.89 | GPT-5.5 anchor+arbiter, GPT-5.6 Sol challenger / medium | 26/50 | Passed, 50/50 | Rejected: tie |

The accepted incumbent is v3.83 because v3.89 did not strictly exceed it.
The current research target is at least 30/50, four additional exact steps.

See the [portable v3.83 artifacts](../../artifacts/releases/gaia-v3p83/) and
the [full reproduction guide](../../REPRODUCING.md).
