# Source-checkout tools

These tools are not part of the installed Python framework. Run them from the
repository root with `python -m <entry point>`.

| Directory | Responsibility | Main entry point |
|---|---|---|
| `reproduction/` | Prepare inputs, verify artifacts, rescore, score a new run | `scripts.reproduction.release` |
| `maintenance/` | Check documentation, source layout, distribution contents and publication hygiene | `make verify` |
| `maintenance/` | Generate a review-only file inventory; no Git writes | `scripts.maintenance.prepare_commit --scan-history` |

There are no top-level experiment runners. Reusable runtime code belongs in
`agentdebug/`, not in a script imported by the framework. New maintenance tools
must have a clear purpose, explicit inputs and synthetic tests. One-off research
tools and retired scripts belong in the [research archive](../research/README.md).

Common checks:

```bash
python -m scripts.maintenance.check_public_docs
python -m scripts.maintenance.check_layout
python -m scripts.maintenance.check_repository_hygiene
python -m scripts.maintenance.check_distribution dist/agentdebug-0.4.0.whl
```

Follow [Reproduction](../REPRODUCING.md) for the supported method and
[Publishing](../PUBLISHING.md) for release checks. Maintenance never implies
permission to launch live model calls.
