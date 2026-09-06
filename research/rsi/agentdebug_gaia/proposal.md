# RSI-Exam task proposal — copy-ready field text

Prepared 2026-09-06. Author/reviewer material, not agent-visible instructions.
This is a proposal for review, not a completed benchmark. Replace the code-link
placeholder before submitting; do not answer “yes” to unresolved data rights.

Suggested task title: Improving causal failure localization in agent trajectories.
Suggested domain: AI Models & Agents / agent diagnosis and harness optimization.

Reporting convention: “Codex SDK method family” includes both SDK/app-server
execution and historical host-orchestrated Codex agents/subagents. This is a
project-level research grouping, not a claim that every run invoked an SDK
package. Every attached result preserves its actual execution backend.

## 2.3 Task description

The agent inherits an AgentDebug-style diagnostic pipeline for recorded failed
agent trajectories: it detects local errors and selects the critical failure
step. The inputs are AgentErrorBench's processed and annotated GAIA trajectories,
not raw GAIA question-answering tasks. The method is weak at distinguishing
recoverable mistakes and downstream symptoms from the earliest causally
consequential error.

Improve evidence organization, temporal and causal analysis, candidate
generation, and final selection. The base model stays fixed at GPT-5.5 with
medium reasoning effort; the agent improves method code, not model weights.
The objective is to maximize exact critical-step localization accuracy.

Our proposed starter is the locally runnable official-topology method, measured
at 19/50. A stronger app-server implementation reached 23/50; the best accepted
method in the Codex SDK family reached 26/50 using host-orchestrated agents.
These are historical visible-set observations. We will adapt and recalibrate
the starter and reference under one approved runtime and budget.

The submission is method code, re-executed on unseen trajectories. We request
review of the fixed-model service and new hidden-data plan before construction.

## 2.4 Metric

Step Exact accuracy; fraction in [0, 1]; higher is better.

Accuracy = number of valid diagnoses with the correct critical step / total
number of cases in the fixed evaluation suite.

A valid diagnosis must name an existing source step, an allowed module/error
type pair, and a literal evidence quote in that step's trusted module-owner
projection. Module/type correctness is not a second objective; their schema
and evidence consistency are legality gates. Missing, failed, or invalid case
outputs score zero, with every case retained in the denominator. Duplicate or
unknown case identifiers invalidate the submission.

The trusted grader, outside candidate code, checks validity and computes the
metric automatically. Step+Module and All Correct remain diagnostics.
The starter/reference must be checked under the same final validation contract.
Official RSI score normalization will be calibrated separately; submitting the
untouched starter must yield normalized score zero.

## 2.5 Visible and hidden data

Visible: 50 failed GAIA trajectories and associated critical-error annotations
from the official AgentErrorBench processed release. The released full corpus
also contains 100 ALFWorld and 50 WebShop trajectories, but those environments
are outside this proposed task. All historical GAIA-50 cases have been exposed
during development; we will disclose this and use them as visible feedback,
not as evidence of held-out generalization.

Hidden: not yet assembled; currently 0 independently sealed cases, final size
to be agreed. Our proposed source is additional, permission-cleared GAIA
failure trajectories collected and annotated using the same task definition
and comparable rollout/annotation process, with independent review. We need
to confirm that this data can actually be obtained.

Split by underlying source task, not merely trajectory ID or rollout-model
prefix. Screen against all visible cases and historical/public reports for
exact and near duplicates. Hidden inputs and labels never enter the agent
image; the submitted method is executed once for final grading in an isolated
environment. Repartitioning the already-exposed 50, or using WebShop/ALFWorld
as an undisclosed distribution shift, is not our hidden-data plan.

## 2.6 Source

- AgentDebug / AgentErrorBench paper:
  https://arxiv.org/abs/2509.25370
- Official implementation:
  https://github.com/ulab-uiuc/AgentDebug
  Local official-topology reference commit:
  7740fe3a5c4822b2143cbde78ecfffeace0bb166.
- AgentErrorBench download linked by the official repository:
  https://drive.google.com/drive/folders/1bQe6dQA85pktT63YnKIKJDTVaH3O3Vpu
- Our framework, versioned runners, result archive and reproduction profiles:
  use the reviewed project link in field 5.1 and the attached evidence packet.

These sources, stronger solutions and historical results are author/reviewer
material, not inputs included in the participant's container.

## 2.7 Data licence

The contributor confirmed on 2026-09-06 that data and evidence-excerpt
distribution permissions are in order for the current repository publication.
This is a contributor declaration; it does not assign the repository's MIT
code licence to third-party data or identify a new data-licence text.

Before distributing the final benchmark dataset, supply the applicable terms
and scope to the organizers, including any additional hidden instances that
have not yet been obtained. The current reviewer packet does not redistribute
raw trajectories, labels, model transcripts, or evidence quotations. Formal
benchmark packaging remains separate from this repository publication.

## 3.1 Anchors

Measured historical visible-set baseline candidate: 0.38 (19/50),
Official SDK v3, GPT-5.5 / medium.

External SOTA: none established for this exact setting.

Upper bound: 1.0, the mathematical upper bound of an accuracy fraction.
This is not a claim that every historical annotation is attainable or correct.

Additional measured local reference candidates:
- 0.46 (23/50): v3.107, SDK/app-server 0.147.0.
- 0.52 (26/50): v3.83, Codex SDK method family, host-agent execution.

All three use the same historical visible GAIA-50 membership. They are not a
chronological 19-to-23-to-26 improvement sequence, not a matched-backend
comparison, and not externally established SOTA. The 0.52 has not been
reproduced after an app-server port. One known source-step mapping anomaly
remains in the historical full-denominator reporting.

Final sealed-task baseline and reference anchors: none; not calibrated yet.
We will measure the shipped starter/reference on the final runtime and data.
The historical 0.38 is a raw accuracy, not a normalized RSI score.

## 3.2 Can you reproduce the SOTA number yourself?

No external SOTA reproduction is claimed.

We have executed the local candidate methods and retained their outputs,
configuration records and independently recomputable score accounting.
We did not obtain the paper's reported accuracy in our local official-repository
reproduction: our GPT-4.1 API GAIA-50 result was 14/50 (0.28). We disclose that
gap rather than use the paper number as an anchor; the result is not evidence
that the paper's original setting was reproduced exactly.

The local 0.38 / 0.46 / 0.52 observations are verifiable from saved artifacts.
New inference may vary. The final standardized runtime, hidden-set
calibration, and repeated-run stability checks remain to be completed.

## 3.3 Why won't this saturate?

We expect substantial room because local-error detection is not sufficient
for critical-error localization: an agent may recover from an early mistake,
while a later symptom looks more salient than the causal boundary. Improving
candidate coverage alone has not reliably improved the final selection.

The cleanest fixed-configuration GPT-5.5/medium historical series retained
three fresh sessions per case, four concurrent cases and at most two semantic
attempts per stage. Four evaluated versions scored 26, 24, 18 and 22 out of 50.
The three follow-up mechanisms—typed-boundary challenges, evidence-lifecycle
challenges and sparse influence-graph challenges—did not exceed the starting
incumbent. The broader Codex family also contains extensive Luna experiments
with early gains followed by regressions and plateaus; they are supplementary
evidence, not GPT-5.5 experiments.

This supports a research bottleneck, not a guarantee against saturation.
The historical maximum is 0.52 on an exposed set, well below the mathematical
bound, but the remaining errors may include annotation issues. We will run a
new fixed-model scratch optimization probe and audit labels/shortcuts before
claiming that the finished task remains hard after twelve hours.

## 3.4 Evidence of difficulty

The archive contains 227 scored run-by-method records. After excluding
audit-invalid/qualified records, historical-prior-output cases, a
mutated-validator diagnostic and a composed report, 214 valid score records
remain, representing 209 distinct run directories.

Under our disclosed grouping, the Codex SDK method family has 99 valid runs:
97 host-agent runs and 2 SDK/app-server runs, across multiple models and
datasets. Of these, 67 are GAIA-50 runs; 3 reuse an earlier stage, leaving 64
recorded fresh full-pipeline GAIA-50 runs.

For the proposed fixed model, there are 9 all-stage GPT-5.5 fresh GAIA-50 runs
across reasoning efforts; 7 use medium. Only 4 share the stricter recorded
three-stage host configuration described in 3.3. The attachment lists all
7 medium runs, their three scores, actual backends and differing configurations,
plus a CSV of all 99 family runs. These totals are not counts of independent
research ideas or one continuous twelve-hour rollout.

The historical workflow alternated hypotheses, code changes, complete
evaluations, post-score analysis and acceptance/rejection under Step Exact.
It involved human/agent interaction over weeks. No newly executed scratch
probe is claimed in this proposal.

## 3.5 Known shortcuts or traps

Potential shortcuts include source-task overlap across rollout models; labels
or answers leaking through input adapters; case-ID answer tables; reference
code/predictions or the complete research archive entering the agent image;
modifying the evaluator; dropping failed cases; stitching partial runs;
changing taxonomy or source-step mapping after observing scores; and unbounded
model calls, retries or cross-case state.

We will separately test empty, constant-step, first/last-step and memorization
controls. Their final scores have not yet been measured. A literal quote is
only an automatic legality check, not proof that the diagnosis is causally
correct. All trajectory text is treated as untrusted data, not instructions.

## 4.1 Compute tier

Proposed: CPU task container with an explicitly approved, credential-isolated
fixed-model inference service. Final tier requires organizer confirmation.
This is not a claim that GPT-5.5 inference runs locally or offline on a CPU.

## 4.2 GPU requirement

No GPU in the task container for the historical hosted-model design.
Hosted inference hardware is external and not included in that statement.
If a fully local model is required, the task/model/hardware and anchors must
be redesigned and measured; no local GPU configuration is claimed.

## 4.3 CPU and memory

Not yet profiled in the target container. Historical case concurrency was 4;
this is not a measured vCPU or RAM requirement. Final resource sizing is pending.

## 4.4 How long does one evaluation take?

Historical Official SDK v3 on GAIA-50 recorded 8,398.8245 seconds of full
workflow wall time, approximately 2.33 hours, with 3,252 successful model
calls and 52,224,583 total tokens.

The v3.107 run recorded 150 successful stages and 55,954,260 total tokens.
A successful stage is not necessarily one model request; we do not infer
evaluation duration or cost from stage count. Imported-prediction scoring
duration is not inference duration.

These observations suggest room for multiple evaluations, but do not verify
the final twelve-hour budget. We must measure at least two complete visible
evaluations under the final service, resource limits and call/token/time
caps, including failures and retries.

## 4.5 Packages needed, and any that must be banned

Historical reference: Python 3.11, PyYAML, and the repository-locked supporting
environment. The SDK service uses openai-codex==0.147.0 with the matching
openai-codex-cli-bin==0.147.0 and pinned Pydantic dependencies, listed in
research/requirements-transports.txt. The baseline needs hash-checked upstream
detector sources. Test tooling includes pytest/jsonschema; plotting packages
are author-side only. Resolve dependencies and authorized data at build time.

No package is currently identified as a one-call solution that must be banned.
Instead, exclude stronger reference implementations, answer tables, historical
predictions, raw labels, credentials and alternate model endpoints from the
participant environment. Do not install the whole research registry if it
would expose stronger methods.

The supplied form says there is no network. We explicitly request an approved
fixed-model service exception/interface; we do not assume SDK access is allowed.
Public LoCoMo and DiscoveryWorld tasks provide model-pinning/allowlist
precedents, but not approval for this task. Without an approved model channel,
the current GPT-5.5 design is not executable. Static completion caches cannot
support arbitrary newly improved prompts.

## 5.1 Link to code or data

[DuffyCoder/AgentDebug](https://github.com/DuffyCoder/AgentDebug)

This is our independently maintained repository, not the upstream official
implementation. It contains the framework, restorable historical runners,
reproducibility profiles, frozen-score verification, full result history and
this proposal. Use the submitted commit identity when sharing a reviewed snapshot.

The small evidence ZIP in 5.2 is not a replacement for the complete code
repository and contains no raw dataset.

## 5.2 Attachments

Attach agentdebug-rsi-proposal-evidence.zip, built from an explicit allowlist.

It contains:
- this field-by-field proposal and an agent-facing instruction draft;
- a method/evidence note, the fixed-GPT-5.5 iteration figure, a separately
  labeled supplementary Luna curve, and machine-readable counts/results with
  actual execution backends;
- metric, isolation and shortcut-review notes, plus tested scoring/split
  prototype code (not a production grader);
- reproduction instructions, candidate profiles and pinned SDK dependencies;
- source/licensing notes, readiness gates and a SHA-256 file manifest.

All attachments are for authors/reviewers, not the agent image. Raw trajectories,
labels, prediction quotations, model transcripts, credentials and hidden data
are deliberately excluded. See attachments/README.md for the exact inventory.
