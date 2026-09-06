# Artifact policy

[releases/reference/](releases/reference/) contains the selected saved predictions,
stage outputs and scoring evidence. Its recorded identities and file hashes
remain unchanged. Verify with:

```bash
python -m scripts.reproduction.release verify
```

[protocol-source-map.json](protocol-source-map.json) binds original protocol
components to current neutral module paths. Only the declared module-token
substitutions, including executable paths in prompts, are permitted.

These artifacts establish saved-evidence integrity, not fresh inference.
See [Evaluation](../docs/results/README.md) and [Reproduction](../REPRODUCING.md).

Prediction/audit files include evidence quotations derived from AgentErrorBench.
Path sanitization is not privacy review or redistribution permission. Review
[data rights](../docs/data-provenance.md) before publishing. Never expose
solution artifacts to a blind-evaluation participant.

Full historical score accounting has moved out of this directory and is
accessible through the [research archive](../research/README.md). Raw datasets,
credentials, transcripts and hidden evaluation data must remain outside Git.
