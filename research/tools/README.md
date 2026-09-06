# Research tools

Run from the repository root with `python -m research.tools.<module>`.
These tools are not included in the installed framework.

| Tool | Purpose |
|---|---|
| `archive_runner test` | Restore a temporary source tree and run the frozen research tests |
| `archive_runner test-all --workspace PATH` | Run all original tests in an explicit, verified restored tree |
| `extract_protocol` | Verify the 13 selected components against declared module-path substitutions |
| `research_release verify` | Check relocated results against unchanged original accounting/source bindings |
| `rsi.build_proposal_bundle build --no-plots` | Refresh the current allowlisted reviewer packet, without inference |
| `rsi.check_readiness` | Report unresolved formal-task gates |
| `rsi.audit_split` | Author-side split identity audit; no hidden IDs in public summaries |
| `reconstruct_history`, `plot_fixed_config_history`, `plot_llm_api_history` | Historical reconstruction utilities; exact local inputs required |

The dated record set is frozen. Reconstruction/plotting tools are retained for
inspection and use in a disposable workspace, not for silently overwriting
reviewed evidence. Original versions and their input contracts are available in
the [source snapshot](../archive/README.md).

Current candidate improvements belong in `research/iterations/`, with explicit
source, input, backend, budget and result identities. [Research entry](../README.md)
