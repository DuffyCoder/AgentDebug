# Configuration

The supported method uses GPT-5.5 / medium, three fresh stages per case,
up to four concurrent cases and two attempts per stage. Settings live in
`agentdebug.method`; public commands have no method or protocol selector.

[reproduction/release.json](reproduction/release.json) locates the selected
evidence bundle and its original source bindings. It is not a runtime registry.

Historical model/provider configurations and reproduction profiles are kept in
the [research archive](../research/README.md), outside the active configuration
directory. Do not put credentials or machine-specific paths in configuration.

See [Getting started](../docs/getting-started.md) and
[Reproduction](../REPRODUCING.md).
