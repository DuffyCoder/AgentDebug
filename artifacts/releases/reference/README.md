# Selected AgentDebug evidence bundle

This directory contains the portable, scored artifacts for the selected
AgentDebug observation. Original experiment identifiers remain in audit metadata.

- Frozen scope: `gaia-paper-v1`, all 50 released GAIA cases.
- Model configuration: GPT-5.5, medium reasoning effort.
- Primary metric: Step Exact `26/50` (`0.52`).
- Runtime result: 50 successful predictions, no failed case.
- Legality: schema, taxonomy, evidence, ordering, gold-isolation, and exact-copy
  checks passed.

The files are derived byte-for-byte from the frozen run except that absolute
repository paths were replaced with `${REPO_ROOT}`. `release-manifest.json`
records both the original frozen hash and the portable release hash for every
artifact.

The approximately 93 MiB gold-free prediction manifest is deliberately not
stored in Git. Rebuild it from the released AgentErrorBench trajectories by
following [`REPRODUCING.md`](../../../REPRODUCING.md), then verify its file and
semantic hashes before rescoring or making a fresh model run.

The directory relocation does not change artifact bytes or assign the saved
score to the current standalone execution adapter. Original source bindings
resolve in the verified snapshot; current module paths are separately mapped.
