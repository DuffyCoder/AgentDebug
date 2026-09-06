# Sources, provenance and rights review

Checked 2026-09-06. Links are author/reviewer references; do not include this
document or stronger reference solutions in the participant image.

| Source | What it establishes | What it does not establish |
|---|---|---|
| [RSI contribution process](https://rsi-exam.ai/contribute.html) | Proposal review precedes authoring-kit construction | Acceptance of our task or model-service design |
| [Task guidelines](https://rsi-exam.ai/guidelines.html) | Runnable starter/reference, automatic metric, sealed same-distribution grading, honest anchors and difficulty review | That historical development curves prove twelve-hour non-saturation |
| [Public task collection](https://huggingface.co/datasets/RSI-Exam/RSI-Exam) | Examples and separate participant/verifier layout | Permission to relabel known cases as hidden |
| [LoCoMo instruction](https://huggingface.co/datasets/RSI-Exam/RSI-Exam/raw/main/locomo_longterm_memory/instruction.md) | A public task uses a model-pinning llm_call proxy | Permission for GPT-5.5/Codex authentication or our proposed interface |
| [DiscoveryWorld task configuration](https://huggingface.co/datasets/RSI-Exam/RSI-Exam/raw/main/discoveryworld_agent_harness_low2/task.toml) | Explicit model-host allowlists for agent/verifier | Unrestricted network access for our task |
| [Codex SDK documentation](https://learn.chatgpt.com/docs/codex-sdk) | SDK programmatically controls Codex agents; Python SDK controls app-server | Identical behavior across host and SDK, or SDK-package use in old host runs |
| [AgentDebug paper](https://arxiv.org/abs/2509.25370) | Diagnostic task, taxonomy and original research | Reproduction of its numbers in our setting |
| [Official repository](https://github.com/ulab-uiuc/AgentDebug) | Detector implementation and AgentErrorBench download link | That our research changes are published there |
| [Repository MIT licence](https://github.com/ulab-uiuc/AgentDebug/blob/main/LICENSE) | Code licensing statement | A verified grant covering all externally hosted trajectory data |
| [AgentErrorBench download](https://drive.google.com/drive/folders/1bQe6dQA85pktT63YnKIKJDTVaH3O3Vpu) | Officially linked processed/annotated release | Independently verified redistribution rights for all data and embedded content |

The two public task files above were read from their raw Hugging Face URLs;
the HTML blob-view pages were unavailable during this check. Their examples
are precedents to discuss, not a workaround for the supplied form's no-network rule.

## Exact local provenance

Local source: AgentErrorBench/Original_Failure_Trajectory/GAIA and its associated
Label/gaia_labels.json; 50 failures. Full release: GAIA 50, ALFWorld 100,
WebShop 50. We optimize diagnosis over recorded observations, not new web
browsing or answering the original GAIA questions.

Full local dataset semantic SHA-256:
fa78de42eb1de06e3566555bd8c68f09deaa6930f2b07ac8937ded858cc6ac11.
Historical GAIA-50 case-set SHA-256:
ffd8b7d9ea5f75db522a3ab8ecf24cb449d716690c0cac10517503025de4ded4.
Official detector reference commit:
7740fe3a5c4822b2143cbde78ecfffeace0bb166.

Hashes identify the locally used material; they are not licences, independent
proof of experimental conduct, or proof of unexposed hidden data.

## Permission status

The contributor confirmed on 2026-09-06 that data and evidence-excerpt
distribution permissions are in order for the current repository publication.
The earlier local audit did not locate an independent data-licence document;
the contributor's confirmation is recorded without inventing licence terms or
assigning the code's MIT licence to third-party content.

For the final benchmark, document the applicable terms and scope with the
organizers, especially for additional hidden trajectories and annotations not
yet obtained. Repository publication is not completed benchmark packaging.

This evidence packet excludes trajectory bodies, labels and prediction quotes.
The full reproduction bundle elsewhere in the repository contains excerpts and
is covered by the maintainer's publication confirmation. No new hidden data has
been collected or sealed, and no publication permission is inferred from a URL.
