# Data provenance and redistribution

Source review recorded on 2026-09-05; maintainer publication confirmation recorded
on 2026-09-06. Source identity, distribution permission and privacy review are
separate concerns.

| Material | Source and release boundary |
|---|---|
| Upstream code | [ulab-uiuc/AgentDebug](https://github.com/ulab-uiuc/AgentDebug), with its MIT license and attribution retained |
| AgentErrorBench | [Download directory linked by the upstream project](https://drive.google.com/drive/folders/1bQe6dQA85pktT63YnKIKJDTVaH3O3Vpu?usp=drive_link); obtained separately, not bundled with the Python package |
| GAIA-50 evaluation | Processed failure trajectories in `Original_Failure_Trajectory/GAIA` and labels in `Label/gaia_labels.json` |
| Derived score metadata | Recorded evaluation decisions and source hashes, not independently relabeled ground truth |
| Prediction and audit excerpts | Data-derived content; the maintainer confirmed distribution permission for the current repository publication on 2026-09-06 |
| Examples | Small synthetic fixtures; no benchmark credentials or raw corpus |

The benchmark measures failure localization in AgentErrorBench's processed
trajectories. It does not measure success on the original GAIA question-answering
task. A similarly named mirror is not evidence of identical data or licensing.

## Reproduction identity

The recorded complete AgentErrorBench semantic identity is:

```text
fa78de42eb1de06e3566555bd8c68f09deaa6930f2b07ac8937ded858cc6ac11
```

The GAIA cohort semantic identity is:

```text
193dea48f9f9cd672215a8bdf4c82ab771836cb3fffe8768468facd5c6870240
```

File hashes, case-set hashes, and semantic identities are distinct. See
[the reproduction guide](../REPRODUCING.md) for
the expected files and [REPRODUCING.md](../REPRODUCING.md) for verification.

## Permission and privacy

On 2026-09-06, the maintainer explicitly confirmed that distribution permissions
for the data and evidence excerpts were in order and authorized publication of
this repository, including its curated evidence and source archive. This is a
record of the maintainer's confirmation, not a newly issued third-party license.

The earlier local review did not locate a separate data-license document. The
code remains MIT-licensed; that code license is not automatically assigned to
externally hosted trajectories, labels or third-party content. Raw datasets,
local model transcripts and credentials are still excluded from this release.
Downstream users must respect the applicable source terms for their own use.

Keep downloaded data in ignored `data/` and raw runs in ignored `output/`.
Sanitizing paths or passing a secret-pattern scan is not a content-license or
privacy clearance. Review new or changed evidence separately before subsequent
publication; the current confirmation is not a blanket grant for future data.

Reported GAIA-50 scores concern exposed development material, not an unseen
evaluation. Moving or renaming files does not change prior exposure. Additional
research and split-design notes are available through the
[research archive](../research/README.md).
