# Data and split authoring notes

The public [data provenance guide](../docs/data-provenance.md) describes the
source and redistribution boundary. Additional conditions apply to a sealed task.

Historical GAIA-50 has been inspected and used for version selection. It cannot
become a hidden set by moving files or changing case IDs. New hidden samples must
follow the same source process, task definition, difficulty, and annotation rules.

Group splits by the underlying `source_task_id`, not just rollout model or
trajectory ID. Check near-duplicate questions, trace text, public answers, and
historical diagnosis reports. Freeze exclusion and label-repair rules before
method comparison; do not drop difficult examples after seeing scores.

For independently supplied, reviewed manifests:

```bash
uv run python -m research.tools.rsi.audit_split \
  --visible /path/to/visible-manifest.json \
  --hidden /path/outside-repository/hidden-manifest.json
```

Each row contains `trajectory_id`, `source_task_id`, and `trajectory_sha256`.
The checker rejects empty sets, duplicate IDs, exact content duplicates, and
cross-split task overlap. It cannot prove task mappings are correct or detect
all semantic near-duplicates. It emits counts rather than hidden identifiers.

Keep hidden data, labels, instance IDs, and grader credentials outside the
public repository and participant build context. Obtain recorded permission
for the processed traces, labels, third-party excerpts, and intended benchmark
distribution. The code's MIT license is not that permission.
