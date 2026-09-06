# AgentErrorBench evaluation report

## Run identity

- Dataset path: `${REPO_ROOT}/data/AgentErrorBench`
- Dataset version: `official-google-drive-unversioned-fa78de42eb1d`
- Dataset manifest SHA-256: `fa78de42eb1de06e3566555bd8c68f09deaa6930f2b07ac8937ded858cc6ac11`
- Cohort: `gaia-paper-v1`
- Cohort manifest: `${REPO_ROOT}/benchmarks/cohorts/gaia-paper-v1.json`
- Cohort SHA-256: `193dea48f9f9cd672215a8bdf4c82ab771836cb3fffe8768468facd5c6870240`
- Run started: `2026-08-28T15:54:07.402052+00:00`
- Run finished: `2026-08-28T15:54:25.803215+00:00`
- Duration seconds: `18.401163`
- Provider: `codex-subagent`
- Endpoint: `orchestrator`
- Model: `gpt-5.5`
- Temperature: `None`
- Max output tokens: `None`
- Timeout seconds: `None`
- Max retries: `1`
- Workers: `4`
- Execution order: `cohort`
- Prompt versions: `{"agent_judge": "agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium"}`
- Production two-stage pipeline: `agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`
- Evidence validation version: `agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`
- Transport policy: `codex-orchestrator-subagent`
- Preregistration: `null`
- Released labels: **200**
- Source trajectories found: **200**
- Canonical adaptations completed: **200**
- Gold-mappable judge inputs: **199**
- LLM-evaluated trajectories: **50**
- Metric cohort trajectories: **50**
- Prediction records: **50**

This run evaluates the available AgentErrorBench release cohort. The release has no official train/dev/test field, so these results are not described as held-out test results. No gold reasoning or label is sent to either judge.

## Overall exact metrics

| Method | N | Step Exact | Step+Module | All Correct | Failed outputs |
|---|---:|---:|---:|---:|---:|
| agent_judge | 50 | 52.00% (26/50) | 32.00% (16/50) | 26.00% (13/50) | 0 |

Failed calls, malformed JSON, illegal taxonomy values, evidence validation failures, and unmapped event IDs remain in every eligible denominator and receive no credit. All Correct excludes only rows whose released `failure_type` is empty; those rows remain in Step and Step+Module.

## Environment breakdown

### alfworld

| Method | N | Step Exact | Step+Module | All Correct | Failed outputs |
|---|---:|---:|---:|---:|---:|
| agent_judge | 0 | N/A (0/0) | N/A (0/0) | N/A (0/0) | 0 |

### gaia

| Method | N | Step Exact | Step+Module | All Correct | Failed outputs |
|---|---:|---:|---:|---:|---:|
| agent_judge | 50 | 52.00% (26/50) | 32.00% (16/50) | 26.00% (13/50) | 0 |

### webshop

| Method | N | Step Exact | Step+Module | All Correct | Failed outputs |
|---|---:|---:|---:|---:|---:|
| agent_judge | 0 | N/A (0/0) | N/A (0/0) | N/A (0/0) | 0 |

## Error-type breakdown

### agent_judge

| Gold error type | N | Step Exact | Step+Module | All Correct |
|---|---:|---:|---:|---:|
| `constraint_ignorance` | 4 | 100.00% | 100.00% | 100.00% |
| `hallucination` | 1 | 0.00% | 0.00% | 0.00% |
| `impossible_action` | 4 | 50.00% | 50.00% | 50.00% |
| `inefficient_plan` | 18 | 33.33% | 33.33% | 16.67% |
| `llm_limit` | 1 | 100.00% | 0.00% | 0.00% |
| `misalignment` | 3 | 33.33% | 0.00% | 0.00% |
| `outcome_misinterpretation` | 5 | 60.00% | 40.00% | 40.00% |
| `over_simplification` | 4 | 0.00% | 0.00% | 0.00% |
| `parameter_error` | 3 | 100.00% | 33.33% | 33.33% |
| `progress_misjudge` | 4 | 75.00% | 0.00% | 0.00% |
| `tool_execution_error` | 3 | 100.00% | 33.33% | 33.33% |

## Direct Prompting vs two-stage

Both methods were not present, so no paired comparison is available.

## Intermediate local-candidate metrics

**Not computable.** The release supplies only one final critical annotation rather than exhaustive local-candidate labels. The inspected release has exactly one step_annotations record per trajectory, and it is the same critical_failure_step. It does not provide exhaustive positive/negative multi-label truth for every step, so Phase 1 precision/recall/F1 is not computable.

## Provider transport telemetry

The configured judge does not expose provider transport telemetry.

## Production integrity

- Gold-isolated prediction: `{"prediction_audit": {"agent_judge_version": "agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium", "all_evidence_quotes_found_in_selected_step_module": true, "all_predicted_steps_in_range": true, "all_selected_predictions_exact_copies": true, "all_status_success": true, "all_taxonomy_pairs_valid": true, "arbiter_decision_counts": {"accept_challenger": 2, "keep_anchor": 48}, "case_count": 50, "cohort_order_matches": true, "earliest_later_boundary_required": true, "forbidden_read_occurred": false, "gold_free_validation": true, "input_sha256": {"cohort": "31140b667a479431abf5e0e274752cb9a486ec5f4a9d80b471b617e586b48126", "prediction_manifest": "77815b429514b136d715c5914eee912637a2e942979dd23f7d614aa33ee508cc"}, "input_sidecar_sha256": {"anchor-predictions.json": "a97474d15d0f590e9fd1a2675e725f46847f8f54692ca44c2749c5928f75316d", "anchor-step-candidates.json": "17dffbdd510e91e63a8e0bca57f85ccab4c30721479790fbe4a721dacf27a56b", "anchor-step-freezes.json": "37ef2c0b262e27ef681a53455ff500fb661d4bf87441d202fb826b686dc1d2f0", "arbiters.json": "bb94fd5d0bafec8344f0d198f24a4210c2afcb0fb873ce9788ffe969a3bfa608", "challengers.json": "7b9b085a9a0f4e02c7ffdc84ca9cd955df6fc447550a062c10556a28056fa64b"}, "manifest_order_matches": true, "model": "gpt-5.5", "model_only_swap": true, "output_sha256": {"predictions.json": "f74161b06c456461ccacdcf7c708157154e8e9810cb5dffa8ef09352698fca3d"}, "packet_state_closure": {"ledger_count": 50, "nonfaithful_state_admission_count": 14, "path": "${REPO_ROOT}/output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/anchor-step-candidates.json", "required": true, "row_count": 169, "state_counts": {"memory_reflection:dropped_necessary_fact": 4, "memory_reflection:faithful": 91, "memory_reflection:outcome_misread": 7, "memory_reflection:unsupported_fact": 3, "none:not_applicable": 64}, "valid": true}, "path_intervention_required": true, "reasoning_effort": "medium", "schema_version": "agentdebug.codex-agent-judge-audit.v1", "selection_policy": "packet_state_closure_v3_4_anchor_one_earliest_causal_later_challenger_default_keep_exact_copy_arbiter", "semantic_parent": "agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure", "unique_trajectory_ids": 50, "validation_method": "Gold-free exact JSON, cohort/manifest order, trajectory identity, step range, taxonomy pair, and selected-owner evidence checks."}, "prediction_manifest_path": "${REPO_ROOT}/output/agenterrorbench-gaia-paper-v1-prediction-input-case50/prediction-manifest.json", "prediction_process_received_gold": false, "raw_artifacts_validated_before_dataset_load": true, "unscored_predictions_path": "${REPO_ROOT}/output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/predictions.json"}`
- Provider telemetry coverage: `null`
- Evidence repair eligible / attempted / applied: **None / None / None**
- Logical-completion budget used / maximum: **None / None**

## Output and provider failures

| Method | Status counts | Failure-code counts |
|---|---|---|
| agent_judge | `{"success": 50}` | `{}` |

## Conversion and release integrity

- Missing trajectory files: **0**
- Conversion failures: **1**
- Canonical adaptations: **200/200**
- Evaluation-ready after gold mapping: **199/200**
- All Correct gold-type eligible: **170/200**
- Step mapping rule: Each assistant-role source message is one 1-based benchmark decision step. Its assistant message event is the unique critical_event_id. Messages after the previous assistant message and before this assistant message are context events for the same step. Embedded <memory>/<reflection>/<plan>/<action> text is preserved as text and is not converted into invented tool calls.

Raw release labels are preserved. Schema normalization is recorded separately:

- Preserve raw_module and raw_error_type on every GoldLabel.
- Trim surrounding whitespace and lowercase module/error-type spelling.
- Map release module alias 'plan' to taxonomy module 'planning'.
- Do not infer an error type when failure_type is empty or not a taxonomy value.
- In particular, preserve 'plan_inefficient' as raw release data and mark its All Correct gold type unscorable rather than rewriting its meaning.

Conversion failures:

- `GPT-4o_003_memory_b000_t00_e03-21a3a421`: conversion_integrity_failure

## Representative error cases

### 1. GPT-4o_001_memory_b000_t00_e00-7743eba0 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `5`, module `planning`, type `inefficient_plan`
- Prediction: step `2`, module `planning`, type `impossible_action`
- Root summary: At the first material breakpoint, the agent planned to identify a timestamp-specific racetrack by extracting static text from the YouTube page, even though the unresolved subgoal required video evidence from the two-minute mark.

### 2. GPT-4o_002_memory_b000_t00_e01-7ab08a46 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `3`, module `action`, type `misalignment`
- Prediction: step `4`, module `planning`, type `inefficient_plan`
- Root summary: At step 4 the agent had just recorded that the Tropicos search result was an unrelated Helodiaceae page, but it planned to inspect that page as though it might contain the Helotiales Tropicos ID.

### 3. GPT-4o_003_memory_b000_t00_e03-21a3a421 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `3`, module `planning`, type `inefficient_plan`
- Prediction: step `1`, module `planning`, type `constraint_ignorance`
- Root summary: At the only assistant step, the plan ignores the explicit instruction that the liking verb reverses English roles, so the liker should be the direct object and apples should be the subject.

### 4. GPT-4o_005_memory_b000_t00_e05-c9015705 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `1`, module `planning`, type `inefficient_plan`
- Prediction: step `3`, module `reflection`, type `outcome_misinterpretation`
- Root summary: At step 3, Reflection misread the prior Google results as successfully satisfying the required Moon Wikipedia minimum perigee source constraint by accepting a Google/Quora-derived 363,300 km value.

### 5. GPT-4o_006_memory_b000_t00_e06-71f77595 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `3`, module `memory`, type `over_simplification`
- Prediction: step `5`, module `system`, type `tool_execution_error`
- Root summary: At the first computation attempt, a well-formed comparison call to python_code_generator failed with a serialization exception instead of returning the overlap count.

### 6. GPT-4o_007_memory_b000_t00_e08-f572f2ad / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `2`, module `memory`, type `over_simplification`
- Prediction: step `4`, module `reflection`, type `outcome_misinterpretation`
- Root summary: At step 4, Reflection misinterpreted the extracted article and answer target by treating ZnO and CuO nanoparticles as the requested nano-compound, despite the same packet preserving the article title "Formation of Nano-Bio-Complex" and text about nanomaterial bio-complex formation.

### 7. GPT-4o_009_memory_b001_t00_e01-7ab08a46 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `8`, module `planning`, type `inefficient_plan`
- Prediction: step `10`, module `planning`, type `inefficient_plan`
- Root summary: At step 10 the agent recommitted to the exact same Google pdf download search already shown unhelpful at step 8 instead of using materially new evidence routes or the result snippets already exposed.

### 8. GPT-4o_010_memory_b001_t00_e02-8d639e26 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `4`, module `planning`, type `impossible_action`
- Prediction: step `2`, module `planning`, type `impossible_action`
- Root summary: At the first material breakpoint, the agent planned to use a static URL text extractor on a YouTube page as though it would expose the video's narration/transcript needed to answer a dynamic video question.

### 9. GPT-4o_011_memory_b001_t00_e03-21a3a421 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `3`, module `memory`, type `over_simplification`
- Prediction: step `7`, module `action`, type `misalignment`
- Root summary: At step 7 the agent recognized that the prior NSI PDF extraction had produced corrupted raw PDF text and planned to use a different method or tool, but the emitted action repeated the same url_text_extractor call on the same PDF URL.

### 10. GPT-4o_012_memory_b001_t00_e04-5e8c1dcf / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `5`, module `action`, type `parameter_error`
- Prediction: step `5`, module `memory`, type `over_simplification`
- Root summary: After the Project MUSE HTML extraction exposed the needed article passage and the mismatching word, the step 5 memory compressed that observation into a false state that the specific page content was still unavailable.

### 11. GPT-4o_013_memory_b001_t00_e05-c9015705 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `5`, module `action`, type `parameter_error`
- Prediction: step `5`, module `planning`, type `constraint_ignorance`
- Root summary: At the first material breakpoint, the agent planned to proceed with decimal conversion even though visible evidence only supplied values for 𒐜 and 𒐐 and did not establish 𒐚 or the correct positional grouping.

### 12. GPT-4o_014_memory_b001_t00_e06-71f77595 / agent_judge

- Environment: `gaia`
- Status: `success`
- Gold: step `7`, module `planning`, type `inefficient_plan`
- Prediction: step `3`, module `planning`, type `impossible_action`
- Root summary: At the first concrete breakpoint, after text extraction failed to expose issue details, the agent planned to use manual browser/visual GitHub inspection even though the available interface did not provide a browser or visual inspection capability.

## Limits for real OpenClaw generalization

AgentErrorBench measures agreement with its released critical-step, module, and error-type annotations. Its trajectories use benchmark environment message logs with embedded module markup; they do not exercise OpenClaw session-v3 branches, runtime dispatch records, tool-call/result joins, permissions, long-lived memory, or production connector failures. A positive benchmark result therefore validates the Canonical-Trace judge pipeline on AgentErrorBench, not generalization to real OpenClaw deployments.

The label release also provides only one critical annotation per trajectory. It cannot validate Phase 1 recall over all actual errors.
