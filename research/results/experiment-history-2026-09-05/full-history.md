# AgentDebug 全量实验结果档案

档案截止：2026-09-05；2026-09-06 更新方法族分类。范围：已审阅的冻结档案；后续产物单列待审阅。原实验文件未修改，未调用模型重跑。

发现 222 份 metrics，展开为 227 个运行×方法结果；另有 64 个带计划/执行记录但无正式 metrics 的目录。

## 口径与可复核性

- 对外方法族统一为 LLM API / Codex SDK；后者包含宿主 Codex agent/subagent。method_family 是报告分类，execution_backend 与 transport 保留实际执行来源，不把宿主运行改写为 SDK 包调用。见 [统一口径](../method-family-policy.md)。
- 每一次运行、每一种方法独立列出；dry3、dry5、hard8、structural10、mixed30、GAIA30、GAIA50、全200以及rest150均保留。不同cohort不能连成一条准确率曲线。
- 早期API评分允许失败/非法输出按零分保留在固定分母；这类评分有效，但不等于全量输出合法。后期fail-closed流程需完整审计通过才允许评分。
- `complete_scored`：全量成功且有评分；`scored_failures_zero`：完整分母计分且包含失败；`historical_prior_prediction`、`audit_invalid`、`audit_qualified`、`mutated_diagnostic`单列，不进入合规趋势图。状态是档案证据分类，不代表重跑全部历史validator。
- `composed_report`：组合旧GAIA50和新rest150的汇总，不当成新增200次推理。
- 时间统一转北京时间；多数Codex报告的started_at是冻结后评分开始时间，不能当作推理开始时间。无法确认的日期明确留空，不以文件mtime猜测。
- All Correct逐行保留原分母；mixed30常为25，不能写成30。GAIA50保留全部50条发布标签，包括一个源轨迹映射异常实例。
- 配置优先取实际运行目录的plan/run-result，再用metrics补充；provider保留为 provenance，不按provider筛选。未知值留空。
- API报告duration可能包含推理，Codex imported-prediction评分duration通常只是评分耗时。本档案不混用它们绘制成本曲线。
- 每行metrics中的三项正确数均与可用per_example.csv重算比对；原始配置来源、数据指纹与逐例文件hash保存在JSON/CSV中。
- output/ 原始文件不随代码发布；下列路径是本地证据定位符。公开逐例计分账本和离线核验入口见 ../README.md。${REPO_ROOT} 表示克隆后的仓库根目录。

状态统计：`{"scored_failures_zero": 43, "complete_scored": 171, "historical_prior_prediction": 6, "audit_qualified": 1, "audit_invalid": 4, "composed_report": 1, "mutated_diagnostic": 1}`

## 全部已记录结果（按数据范围分组）

### Small diagnostics / 1

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R001 | 2026-07-23 22:57 | gpt-4o-smoke / direct | LLM API | gpt-4o；— / 0.0 | 0/1 | 0/1 | 0/1 | 1 | scored_failures_zero | [配置](#r001) / metrics: `output/agenterrorbench-gpt-4o-smoke/metrics.json` |
| R002 | 2026-07-23 22:57 | gpt-4o-smoke / two_stage | LLM API | gpt-4o；— / 0.0 | 1/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r002) / metrics: `output/agenterrorbench-gpt-4o-smoke/metrics.json` |
| R003 | 2026-07-23 23:09 | gpt-4o-smoke-v2 / direct | LLM API | gpt-4o；— / 0.0 | 0/1 | 0/1 | 0/1 | 1 | scored_failures_zero | [配置](#r003) / metrics: `output/agenterrorbench-gpt-4o-smoke-v2/metrics.json` |
| R004 | 2026-07-23 23:09 | gpt-4o-smoke-v2 / two_stage | LLM API | gpt-4o；— / 0.0 | 0/1 | 0/1 | 0/1 | 1 | scored_failures_zero | [配置](#r004) / metrics: `output/agenterrorbench-gpt-4o-smoke-v2/metrics.json` |
| R007 | 2026-07-24 00:07 | smoke / direct | LLM API | gemini-3.1-pro-preview；— / 0.0 | 0/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r007) / metrics: `output/agenterrorbench-gemini-3.1-smoke/metrics.json` |
| R008 | 2026-07-24 00:07 | smoke / two_stage | LLM API | gemini-3.1-pro-preview；— / 0.0 | 0/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r008) / metrics: `output/agenterrorbench-gemini-3.1-smoke/metrics.json` |
| R009 | 2026-07-24 00:11 | largest-smoke / direct | LLM API | gemini-3.1-pro-preview；— / 0.0 | 0/1 | 0/1 | 0/1 | 1 | scored_failures_zero | [配置](#r009) / metrics: `output/agenterrorbench-gemini-3.1-largest-smoke/metrics.json` |
| R010 | 2026-07-24 00:30 | largest-smoke-v3 / direct | LLM API | gemini-3.1-pro-preview；— / 0.0 | 0/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r010) / metrics: `output/agenterrorbench-gemini-3.1-largest-smoke-v3/metrics.json` |
| R011 | 2026-07-24 00:32 | largest-two-stage-smoke-v3 / two_stage | LLM API | gemini-3.1-pro-preview；— / 0.0 | 0/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r011) / metrics: `output/agenterrorbench-gemini-3.1-largest-two-stage-smoke-v3/metrics.json` |
| R012 | 2026-07-24 00:48 | max-output-smoke / direct | LLM API | gemini-3.1-pro-preview；— / 0.0 | 1/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r012) / metrics: `output/agenterrorbench-gemini-3.1-max-output-smoke/metrics.json` |
| R018 | 2026-07-24 14:05 | tuning-v1-e1b-web-format / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/1 | 0/1 | 0/1 | 0 | complete_scored | [配置](#r018) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e1b-web-format/metrics.json` |

### Full / 200

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R005 | 2026-07-23 23:12 | gpt-4o-v2 / direct | LLM API | gpt-4o；— / 0.0 | 2/200 | 0/200 | 0/170 | 177 | scored_failures_zero | [配置](#r005) / metrics: `output/agenterrorbench-gpt-4o-v2/metrics.json` |
| R006 | 2026-07-23 23:12 | gpt-4o-v2 / two_stage | LLM API | gpt-4o；— / 0.0 | 3/200 | 0/200 | 0/170 | 185 | scored_failures_zero | [配置](#r006) / metrics: `output/agenterrorbench-gpt-4o-v2/metrics.json` |
| R013 | 2026-07-24 00:49 | pro-preview / direct | LLM API | gemini-3.1-pro-preview；— / 0.0 | 41/200 | 14/200 | 9/170 | 42 | scored_failures_zero | [配置](#r013) / metrics: `output/agenterrorbench-gemini-3.1-pro-preview/metrics.json` |
| R014 | 2026-07-24 00:49 | pro-preview / two_stage | LLM API | gemini-3.1-pro-preview；— / 0.0 | 36/200 | 12/200 | 6/170 | 67 | scored_failures_zero | [配置](#r014) / metrics: `output/agenterrorbench-gemini-3.1-pro-preview/metrics.json` |
| R217 | 2026-09-01 20:56 | gaia-v3.83-clean-v3.20-model-only-gpt55-medium | Codex SDK | gpt-5.5；medium / — | 59/200 | 24/200 | 16/170 | 0 | composed_report | [配置](#r217) / metrics: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/agenterrorbench200/metrics.json` |

### Mixed-30 / tuning-v1

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R015 | 2026-07-24 12:59 | tuning-v1-baseline / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/30 | 0/30 | 0/25 | 10 | scored_failures_zero | [配置](#r015) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-baseline/metrics.json` |
| R019 | 2026-07-24 14:07 | tuning-v1-e1-v7 / two_stage | LLM API | gpt-4.1；— / 0.0 | 8/30 | 4/30 | 3/25 | 1 | scored_failures_zero | [配置](#r019) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-v7/metrics.json` |
| R031 | 2026-07-27 20:37 | tuning-v1-e6-v2-production-full30 / two_stage | LLM API | gpt-4.1；— / 0.0 | 5/30 | 3/30 | 3/25 | 4 | scored_failures_zero | [配置](#r031) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e6-v2-production-full30/metrics.json` |
| R047 | 2026-07-30 14:38 | tuning-v1-e9-v13-atomic-taxonomy-pair-full30 / two_stage | LLM API | gpt-4.1；— / 0.0 | 6/30 | 3/30 | 3/25 | 1 | scored_failures_zero | [配置](#r047) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-full30/metrics.json` |
| R059 | 2026-08-12 01:01 | tuning-v1-e9-v24-final-content-critic-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 6/30 | 4/30 | 4/25 | 10 | scored_failures_zero | [配置](#r059) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-full30/metrics.json` |
| R061 | 2026-08-12 01:51 | tuning-v1-e9-v25-local-error-critic-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 10/30 | 3/30 | 3/25 | 2 | scored_failures_zero | [配置](#r061) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-full30/metrics.json` |
| R064 | 2026-08-12 02:47 | tuning-v1-e9-v27-critical-event-critic-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 9/30 | 3/30 | 3/25 | 3 | scored_failures_zero | [配置](#r064) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-full30/metrics.json` |
| R067 | 2026-08-12 03:45 | tuning-v1-e9-v29-terminal-guard-critic-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 9/30 | 3/30 | 3/25 | 1 | scored_failures_zero | [配置](#r067) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-full30/metrics.json` |
| R069 | 2026-08-12 04:19 | tuning-v1-e9-v30-first-defect-critic-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 10/30 | 5/30 | 4/25 | 1 | scored_failures_zero | [配置](#r069) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-full30/metrics.json` |
| R075 | 2026-08-12 16:35 | tuning-v1-e9-v35-symmetric-brace-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 7/30 | 4/30 | 4/25 | 0 | complete_scored | [配置](#r075) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-full30/metrics.json` |
| R079 | 2026-08-12 18:20 | tuning-v1-e9-v38-first-defect-terminal-guard-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 9/30 | 4/30 | 3/25 | 0 | complete_scored | [配置](#r079) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-full30/metrics.json` |
| R082 | 2026-08-12 19:43 | tuning-v1-e9-v40-causal-ledger-length-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 9/30 | 4/30 | 4/25 | 1 | scored_failures_zero | [配置](#r082) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-full30/metrics.json` |
| R089 | 2026-08-13 01:10 | tuning-v1-e9-v46-persistent-information-root-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 9/30 | 3/30 | 3/25 | 0 | complete_scored | [配置](#r089) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-full30/metrics.json` |
| R095 | 2026-08-13 05:30 | tuning-v1-e9-v51-whitespace-brace-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 7/30 | 3/30 | 3/25 | 0 | complete_scored | [配置](#r095) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-full30/metrics.json` |
| R097 | 2026-08-13 12:33 | tuning-v1-e9-v52-module-census-recovery-v2-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 9/30 | 5/30 | 4/25 | 0 | complete_scored | [配置](#r097) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-recovery-v2-full30/metrics.json` |
| R101 | 2026-08-13 14:33 | tuning-v1-e9-v31-pairwise-candidate-recovered-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 10/30 | 4/30 | 4/25 | 1 | scored_failures_zero | [配置](#r101) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-recovered-full30/metrics.json` |
| R104 | 2026-08-13 14:55 | tuning-v1-e9-v57-v30-earlier-only-review-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 10/30 | 4/30 | 3/25 | 4 | scored_failures_zero | [配置](#r104) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-full30/metrics.json` |
| R106 | 2026-08-13 15:19 | tuning-v1-e9-v58-v30-incumbent-copy-review-full30 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 12/30 | 5/30 | 4/25 | 0 | complete_scored | [配置](#r106) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-full30/metrics.json` |
| R108 | 2026-08-13 19:08 | v1 | Codex SDK | gpt-5.6-terra；medium / — | 5/30 | 1/30 | 0/25 | 0 | complete_scored | [配置](#r108) / metrics: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-agent-judge-v1/scored/metrics.json` |
| R110 | 2026-08-13 21:43 | luna-v1 | Codex SDK | gpt-5.6-luna；medium / — | 5/30 | 1/30 | 1/25 | 0 | complete_scored | [配置](#r110) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1-case30/scored/metrics.json` |
| R111 | 2026-08-13 22:38 | luna-v2 | Codex SDK | gpt-5.6-luna；medium / — | 6/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r111) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v2-case30/scored/metrics.json` |
| R112 | 2026-08-13 22:55 | luna-v3 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 3/30 | 2/25 | 0 | complete_scored | [配置](#r112) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-case30/scored/metrics.json` |
| R113 | 2026-08-13 23:15 | luna-v4 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 3/30 | 2/25 | 0 | complete_scored | [配置](#r113) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v4-case30/scored/metrics.json` |
| R114 | 2026-08-13 23:34 | luna-v5 | Codex SDK | gpt-5.6-luna；medium / — | 6/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r114) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v5-case30/scored/metrics.json` |
| R115 | 2026-08-13 23:56 | luna-v6 | Codex SDK | gpt-5.6-luna；medium / — | 7/30 | 2/30 | 2/25 | 0 | complete_scored | [配置](#r115) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v6-case30/scored/metrics.json` |
| R116 | 2026-08-14 00:14 | luna-v7 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 3/30 | 2/25 | 0 | historical_prior_prediction | [配置](#r116) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v7-case30/scored/metrics.json` |
| R117 | 2026-08-14 00:28 | luna-v8 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 3/30 | 2/25 | 0 | historical_prior_prediction | [配置](#r117) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v8-case30/scored/metrics.json` |
| R118 | 2026-08-14 00:47 | luna-v9 | Codex SDK | gpt-5.6-luna；medium / — | 7/30 | 4/30 | 2/25 | 0 | historical_prior_prediction | [配置](#r118) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v9-case30/scored/metrics.json` |
| R119 | 2026-08-14 01:03 | luna-v10 | Codex SDK | gpt-5.6-luna；medium / — | 5/30 | 2/30 | 2/25 | 0 | historical_prior_prediction | [配置](#r119) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v10-case30/scored/metrics.json` |
| R120 | 2026-08-14 01:22 | luna-v11 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 3/30 | 2/25 | 0 | historical_prior_prediction | [配置](#r120) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v11-case30/scored/metrics.json` |
| R121 | 2026-08-14 01:41 | luna-v12 | Codex SDK | gpt-5.6-luna；medium / — | 13/30 | 6/30 | 5/25 | 0 | historical_prior_prediction | [配置](#r121) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-case30/scored/metrics.json` |
| R122 | 2026-08-14 12:14 | luna-v3-serial-v2 | Codex SDK | gpt-5.6-luna；medium / — | 7/30 | 3/30 | 2/25 | 0 | complete_scored | [配置](#r122) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/scored/metrics.json` |
| R123 | 2026-08-14 12:34 | luna-v12-standalone-v1 | Codex SDK | gpt-5.6-luna；medium / — | 7/30 | 3/30 | 2/25 | 0 | audit_qualified | [配置](#r123) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/scored/metrics.json` |
| R124 | 2026-08-14 13:23 | luna-clean-debate-v1 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 3/30 | 2/25 | 0 | complete_scored | [配置](#r124) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/scored/metrics.json` |
| R125 | 2026-08-14 14:21 | luna-clean-debate-v2 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r125) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/scored/metrics.json` |
| R126 | 2026-08-14 15:37 | luna-clean-debate-v3 | Codex SDK | gpt-5.6-luna；medium / — | 6/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r126) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/scored/metrics.json` |
| R127 | 2026-08-14 18:11 | luna-clean-debate-v4-rerun1 | Codex SDK | gpt-5.6-luna；medium / — | 8/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r127) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/scored/metrics.json` |
| R151 | 2026-08-20 21:07 | luna-v14-unified-v1 | Codex SDK | gpt-5.6-luna；medium / — | 9/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r151) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/scored/metrics.json` |
| R152 | 2026-08-20 22:51 | luna-v15-unified-v2 | Codex SDK | gpt-5.6-luna；medium / — | 7/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r152) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/scored/metrics.json` |
| R153 | 2026-08-21 00:01 | luna-v16-unified-v1 | Codex SDK | gpt-5.6-luna；medium / — | 6/30 | 2/30 | 1/25 | 0 | complete_scored | [配置](#r153) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/scored/metrics.json` |

### Mixed-30 / smoke-v1

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R016 | 2026-07-24 13:15 | smoke-v1-baseline / two_stage | LLM API | gpt-4.1；— / 0.0 | 4/30 | 2/30 | 1/27 | 9 | scored_failures_zero | [配置](#r016) / metrics: `output/agenterrorbench-gpt-4.1-smoke-v1-baseline/metrics.json` |
| R107 | 2026-08-13 17:17 | smoke-v1-e9-v58-fresh-v30-review / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 8/30 | 3/30 | 3/27 | 3 | scored_failures_zero | [配置](#r107) / metrics: `output/agenterrorbench-deepseek-v4-flash-smoke-v1-e9-v58-fresh-v30-review/metrics.json` |
| R220 | 未知 | codex-gpt-5.6-terra-smoke-v1-experiment-b-v1 | Codex SDK | gpt-5.6-terra；medium / — | 7/30 | 3/30 | 2/27 | 0 | complete_scored | [配置](#r220) / metrics: `output/agenterrorbench-codex-gpt-5.6-terra-smoke-v1-experiment-b-v1/metrics.json` |

### Small diagnostics / 3

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R017 | 2026-07-24 14:03 | tuning-v1-e1-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r017) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-dry3/metrics.json` |
| R020 | 2026-07-24 14:33 | tuning-v1-e2-matrix-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 1 | scored_failures_zero | [配置](#r020) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-matrix-dry3/metrics.json` |
| R021 | 2026-07-24 14:38 | tuning-v1-e2-v9-schema-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r021) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v9-schema-dry3/metrics.json` |
| R022 | 2026-07-24 14:44 | tuning-v1-e2-v10-validity-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r022) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v10-validity-dry3/metrics.json` |
| R023 | 2026-07-24 15:02 | tuning-v1-m3-v1-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r023) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-m3-v1-dry3/metrics.json` |
| R024 | 2026-07-24 15:16 | tuning-v1-e4-v1-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r024) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e4-v1-dry3/metrics.json` |
| R025 | 2026-07-27 17:03 | tuning-v1-e5a-replay-critic-dry3 | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r025) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e5a-replay-critic-dry3/metrics.json` |
| R026 | 2026-07-27 17:15 | tuning-v1-e5b-explicit-audit-dry3 | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r026) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e5b-explicit-audit-dry3/metrics.json` |
| R027 | 2026-07-27 17:45 | tuning-v1-e5c-handoff-dry3 | LLM API | gpt-4.1；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r027) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-handoff-dry3/metrics.json` |
| R028 | 2026-07-27 18:28 | tuning-v1-e5c-strict-revalidation-dry3 | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 1 | scored_failures_zero | [配置](#r028) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-strict-revalidation-dry3/metrics.json` |
| R029 | 2026-07-27 19:07 | tuning-v1-e5d-evidence-repair-dry3 | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 1 | scored_failures_zero | [配置](#r029) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-evidence-repair-dry3/metrics.json` |
| R030 | 2026-07-27 19:18 | tuning-v1-e5d-v2-json-fallback-dry3 | LLM API | gpt-4.1；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r030) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-v2-json-fallback-dry3/metrics.json` |
| R034 | 2026-07-28 00:15 | tuning-v1-e9-v1-batched-causal-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r034) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v1-batched-causal-dry3/metrics.json` |
| R035 | 2026-07-28 00:37 | tuning-v1-e9-v2-batched-module-audit-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r035) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v2-batched-module-audit-dry3/metrics.json` |
| R036 | 2026-07-28 00:51 | tuning-v1-e9-v3-candidate-review-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r036) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v3-candidate-review-dry3/metrics.json` |
| R037 | 2026-07-28 01:27 | tuning-v1-e9-v4-chronology-first-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 2 | scored_failures_zero | [配置](#r037) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v4-chronology-first-dry3/metrics.json` |
| R038 | 2026-07-28 01:56 | tuning-v1-e9-v5-owner-maturity-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 1 | scored_failures_zero | [配置](#r038) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v5-owner-maturity-dry3/metrics.json` |
| R039 | 2026-07-28 02:37 | tuning-v1-e9-v6-atomic-boundary-cycle-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 2 | scored_failures_zero | [配置](#r039) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v6-atomic-boundary-cycle-dry3/metrics.json` |
| R040 | 2026-07-30 11:29 | tuning-v1-e9-v7-flat-arbiter-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 2 | scored_failures_zero | [配置](#r040) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v7-flat-arbiter-dry3/metrics.json` |
| R041 | 2026-07-30 11:54 | tuning-v1-e9-v8-tail-recency-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r041) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v8-tail-recency-dry3/metrics.json` |
| R042 | 2026-07-30 12:13 | tuning-v1-e9-v9-literal-constraint-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r042) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v9-literal-constraint-dry3/metrics.json` |
| R043 | 2026-07-30 12:33 | tuning-v1-e9-v10-ordered-root-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 1 | scored_failures_zero | [配置](#r043) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v10-ordered-root-dry3/metrics.json` |
| R044 | 2026-07-30 12:59 | tuning-v1-e9-v11-visible-audit-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 2 | scored_failures_zero | [配置](#r044) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v11-visible-audit-dry3/metrics.json` |
| R045 | 2026-07-30 13:46 | tuning-v1-e9-v12-semantic-candidates-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r045) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v12-semantic-candidates-dry3/metrics.json` |
| R046 | 2026-07-30 14:22 | tuning-v1-e9-v13-atomic-taxonomy-pair-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r046) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-dry3/metrics.json` |
| R048 | 2026-08-11 19:27 | tuning-v1-e9-v14-prior-late-balanced-critic-dry3 / two_stage | LLM API | gpt-4.1；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r048) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v14-prior-late-balanced-critic-dry3/metrics.json` |
| R049 | 2026-08-11 21:17 | tuning-v1-e9-v15-prior-late-balanced-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r049) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v15-prior-late-balanced-critic-dry3/metrics.json` |
| R050 | 2026-08-11 21:30 | tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r050) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3/metrics.json` |
| R051 | 2026-08-11 21:46 | tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 1 | scored_failures_zero | [配置](#r051) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3/metrics.json` |
| R052 | 2026-08-11 22:11 | tuning-v1-e9-v18-conservative-prior-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r052) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v18-conservative-prior-critic-dry3/metrics.json` |
| R053 | 2026-08-11 22:27 | tuning-v1-e9-v19-task-closing-prior-critic-dry3 / two_stage | LLM API | deepseek-v4-pro；— / 0.0 | 1/3 | 1/3 | 1/3 | 1 | scored_failures_zero | [配置](#r053) / metrics: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v19-task-closing-prior-critic-dry3/metrics.json` |
| R054 | 2026-08-11 22:41 | tuning-v1-e9-v20-minimal-final-prior-critic-dry3 / two_stage | LLM API | deepseek-v4-pro；— / 0.0 | 1/3 | 1/3 | 1/3 | 1 | scored_failures_zero | [配置](#r054) / metrics: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v20-minimal-final-prior-critic-dry3/metrics.json` |
| R055 | 2026-08-11 22:59 | tuning-v1-e9-v21-format-safe-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r055) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v21-format-safe-critic-dry3/metrics.json` |
| R056 | 2026-08-11 23:12 | tuning-v1-e9-v22-recovery-checkpoint-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r056) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v22-recovery-checkpoint-critic-dry3/metrics.json` |
| R057 | 2026-08-11 23:23 | tuning-v1-e9-v23-novelty-recovery-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 3 | scored_failures_zero | [配置](#r057) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v23-novelty-recovery-critic-dry3/metrics.json` |
| R058 | 2026-08-11 23:33 | tuning-v1-e9-v24-final-content-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r058) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-dry3/metrics.json` |
| R060 | 2026-08-12 01:21 | tuning-v1-e9-v25-local-error-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r060) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-dry3/metrics.json` |
| R062 | 2026-08-12 02:05 | tuning-v1-e9-v26-upstream-owner-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r062) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v26-upstream-owner-critic-dry3/metrics.json` |
| R063 | 2026-08-12 02:18 | tuning-v1-e9-v27-critical-event-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r063) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-dry3/metrics.json` |
| R065 | 2026-08-12 03:01 | tuning-v1-e9-v28-flat-review-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r065) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v28-flat-review-critic-dry3/metrics.json` |
| R066 | 2026-08-12 03:12 | tuning-v1-e9-v29-terminal-guard-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r066) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-dry3/metrics.json` |
| R068 | 2026-08-12 03:56 | tuning-v1-e9-v30-first-defect-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r068) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-dry3/metrics.json` |
| R070 | 2026-08-12 04:34 | tuning-v1-e9-v31-pairwise-candidate-critic-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r070) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-critic-dry3/metrics.json` |
| R071 | 2026-08-12 14:14 | tuning-v1-e9-v32-candidate-selector-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r071) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v32-candidate-selector-dry3/metrics.json` |
| R072 | 2026-08-12 14:32 | tuning-v1-e9-v33-maturity-calibrated-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r072) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v33-maturity-calibrated-dry3/metrics.json` |
| R073 | 2026-08-12 14:48 | tuning-v1-e9-v34-capability-query-epoch-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r073) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v34-capability-query-epoch-dry3/metrics.json` |
| R074 | 2026-08-12 15:38 | tuning-v1-e9-v35-symmetric-brace-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r074) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-dry3/metrics.json` |
| R076 | 2026-08-12 17:01 | tuning-v1-e9-v36-original-causal-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r076) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v36-original-causal-dry3/metrics.json` |
| R077 | 2026-08-12 17:19 | tuning-v1-e9-v37-incumbent-preserving-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r077) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v37-incumbent-preserving-dry3/metrics.json` |
| R078 | 2026-08-12 17:37 | tuning-v1-e9-v38-first-defect-terminal-guard-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r078) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-dry3/metrics.json` |
| R080 | 2026-08-12 18:39 | tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 1 | scored_failures_zero | [配置](#r080) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3/metrics.json` |
| R081 | 2026-08-12 18:55 | tuning-v1-e9-v40-causal-ledger-length-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r081) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-dry3/metrics.json` |
| R083 | 2026-08-12 20:10 | tuning-v1-e9-v41-symmetric-module-census-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r083) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v41-symmetric-module-census-dry3/metrics.json` |
| R084 | 2026-08-12 22:00 | tuning-v1-e9-v42-chronological-module-census-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r084) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v42-chronological-module-census-dry3/metrics.json` |
| R085 | 2026-08-12 22:34 | tuning-v1-e9-v43-symmetric-causal-lanes-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r085) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v43-symmetric-causal-lanes-dry3/metrics.json` |
| R086 | 2026-08-12 22:49 | tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 0/3 | 0 | complete_scored | [配置](#r086) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3/metrics.json` |
| R087 | 2026-08-12 23:33 | tuning-v1-e9-v45-categorical-boundary-action-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r087) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v45-categorical-boundary-action-dry3/metrics.json` |
| R088 | 2026-08-12 23:49 | tuning-v1-e9-v46-persistent-information-root-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r088) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-dry3/metrics.json` |
| R090 | 2026-08-13 01:34 | tuning-v1-e9-v47-five-lane-handoff-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r090) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v47-five-lane-handoff-dry3/metrics.json` |
| R091 | 2026-08-13 01:58 | tuning-v1-e9-v48-scout-broadened-handoff-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r091) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v48-scout-broadened-handoff-dry3/metrics.json` |
| R092 | 2026-08-13 02:18 | tuning-v1-e9-v49-cross-module-consistency-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r092) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v49-cross-module-consistency-dry3/metrics.json` |
| R093 | 2026-08-13 03:33 | tuning-v1-e9-v50-selector-capacity-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r093) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v50-selector-capacity-dry3/metrics.json` |
| R094 | 2026-08-13 04:09 | tuning-v1-e9-v51-whitespace-brace-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r094) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-dry3/metrics.json` |
| R096 | 2026-08-13 05:55 | tuning-v1-e9-v52-module-census-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r096) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-dry3/metrics.json` |
| R098 | 2026-08-13 13:28 | tuning-v1-e9-v53-dual-timescale-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r098) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v53-dual-timescale-dry3/metrics.json` |
| R099 | 2026-08-13 13:52 | tuning-v1-e9-v54-contradiction-first-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r099) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v54-contradiction-first-dry3/metrics.json` |
| R100 | 2026-08-13 14:12 | tuning-v1-e9-v55-one-stage-global-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 0/3 | 0/3 | 0/3 | 0 | complete_scored | [配置](#r100) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v55-one-stage-global-dry3/metrics.json` |
| R102 | 2026-08-13 14:47 | tuning-v1-e9-v56-v30-incumbent-review-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 1/3 | 1/3 | 1/3 | 0 | complete_scored | [配置](#r102) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v56-v30-incumbent-review-dry3/metrics.json` |
| R103 | 2026-08-13 14:52 | tuning-v1-e9-v57-v30-earlier-only-review-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r103) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-dry3/metrics.json` |
| R105 | 2026-08-13 15:18 | tuning-v1-e9-v58-v30-incumbent-copy-review-dry3 / two_stage | LLM API | deepseek-v4-flash；— / 0.0 | 2/3 | 2/3 | 2/3 | 0 | complete_scored | [配置](#r105) / metrics: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-dry3/metrics.json` |

### Small diagnostics / 5

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R032 | 2026-07-27 21:20 | tuning-v1-e7-v3-global-critic-dry5 / two_stage | LLM API | gpt-4.1；— / 0.0 | 2/5 | 0/5 | 0/5 | 0 | complete_scored | [配置](#r032) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e7-v3-global-critic-dry5/metrics.json` |
| R033 | 2026-07-27 23:18 | tuning-v1-e8-v3-fresh-semantic-dry5 / two_stage | LLM API | gpt-4.1；— / 0.0 | 1/5 | 1/5 | 1/5 | 1 | scored_failures_zero | [配置](#r033) / metrics: `output/agenterrorbench-gpt-4.1-tuning-v1-e8-v3-fresh-semantic-dry5/metrics.json` |

### Small diagnostics / 9

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R109 | 2026-08-13 19:52 | v2_2 | Codex SDK | gpt-5.6-terra；medium / — | 1/9 | 0/9 | 0/7 | 0 | complete_scored | [配置](#r109) / metrics: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-gate3x3-agent-judge-v2_2/scored/metrics.json` |

### GAIA-smoke-30

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R128 | 2026-08-15 00:04 | luna-gaia-v1 | Codex SDK | gpt-5.6-luna；medium / — | 10/30 | 9/30 | 5/30 | 0 | complete_scored | [配置](#r128) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/scored/metrics.json` |
| R129 | 2026-08-15 00:50 | luna-gaia-v2.1 | Codex SDK | gpt-5.6-luna；medium / — | 9/30 | 7/30 | 5/30 | 0 | complete_scored | [配置](#r129) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/scored/metrics.json` |
| R130 | 2026-08-15 01:15 | luna-gaia-v3 | Codex SDK | gpt-5.6-luna；medium / — | 11/30 | 8/30 | 6/30 | 0 | complete_scored | [配置](#r130) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/scored/metrics.json` |
| R131 | 2026-08-15 01:37 | luna-gaia-v3.1 | Codex SDK | gpt-5.6-luna；medium / — | 14/30 | 11/30 | 9/30 | 0 | complete_scored | [配置](#r131) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/scored/metrics.json` |
| R132 | 2026-08-15 01:55 | luna-gaia-v3.2 | Codex SDK | gpt-5.6-luna；medium / — | 12/30 | 9/30 | 7/30 | 0 | complete_scored | [配置](#r132) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/scored/metrics.json` |
| R133 | 2026-08-15 02:13 | luna-gaia-v3.3 | Codex SDK | gpt-5.6-luna；medium / — | 12/30 | 10/30 | 6/30 | 0 | complete_scored | [配置](#r133) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/scored/metrics.json` |
| R134 | 2026-08-15 02:43 | luna-gaia-v3.4 | Codex SDK | gpt-5.6-luna；medium / — | 16/30 | 10/30 | 7/30 | 0 | complete_scored | [配置](#r134) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/scored/metrics.json` |
| R135 | 2026-08-15 03:37 | luna-gaia-v3.5.1 | Codex SDK | gpt-5.6-luna；medium / — | 15/30 | 9/30 | 6/30 | 0 | complete_scored | [配置](#r135) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/scored/metrics.json` |
| R136 | 2026-08-15 04:02 | luna-gaia-v3.6 | Codex SDK | gpt-5.6-luna；medium / — | 15/30 | 13/30 | 10/30 | 0 | complete_scored | [配置](#r136) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/scored/metrics.json` |
| R137 | 2026-08-15 11:37 | luna-gaia-v3.7.1 | Codex SDK | gpt-5.6-luna；medium / — | 13/30 | 11/30 | 8/30 | 0 | complete_scored | [配置](#r137) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/scored/metrics.json` |
| R138 | 2026-08-15 12:13 | luna-gaia-v3.8 | Codex SDK | gpt-5.6-luna；medium / — | 15/30 | 12/30 | 9/30 | 0 | complete_scored | [配置](#r138) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/scored/metrics.json` |
| R139 | 2026-08-15 12:44 | luna-gaia-v3.9 | Codex SDK | gpt-5.6-luna；medium / — | 14/30 | 10/30 | 7/30 | 0 | complete_scored | [配置](#r139) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/scored/metrics.json` |
| R140 | 2026-08-15 13:04 | luna-gaia-v3.10 | Codex SDK | gpt-5.6-luna；medium / — | 14/30 | 10/30 | 8/30 | 0 | complete_scored | [配置](#r140) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/scored/metrics.json` |
| R155 | 2026-08-22 17:31 | luna-gaia-v3.12-global | Codex SDK | gpt-5.6-luna；medium / — | 9/30 | 6/30 | 4/30 | 0 | complete_scored | [配置](#r155) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/scored/metrics.json` |

### GAIA-50

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R141 | 2026-08-15 14:30 | luna-gaia-v3.4 | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 13/50 | 10/50 | 0 | complete_scored | [配置](#r141) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/scored/metrics.json` |
| R142 | 2026-08-15 16:30 | v2.4-global-census | Codex SDK | gpt-5.6-terra；medium / — | 11/50 | 6/50 | 4/50 | 0 | complete_scored | [配置](#r142) / metrics: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/scored/metrics.json` |
| R143 | 2026-08-15 18:17 | two-stage-v1 | Codex SDK | gpt-5.6-sol；high / — | 15/50 | 5/50 | 2/50 | 0 | complete_scored | [配置](#r143) / metrics: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/scored/metrics.json` |
| R144 | 2026-08-16 02:26 | serial-v2 | Codex SDK | gpt-5.6-luna + gpt-5.6-sol（分阶段，见配置） | 15/50 | 9/50 | 5/50 | 0 | complete_scored | [配置](#r144) / metrics: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/scored/metrics.json` |
| R145 | 2026-08-16 05:56 | forced-census-v1 | Codex SDK | gpt-5.6-sol；high / — | 13/50 | 6/50 | 5/50 | 0 | complete_scored | [配置](#r145) / metrics: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/scored/metrics.json` |
| R146 | 2026-08-16 07:13 | causal-serial-v1 | Codex SDK | gpt-5.6-luna + gpt-5.6-sol（分阶段，见配置） | 16/50 | 8/50 | 6/50 | 0 | complete_scored | [配置](#r146) / metrics: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/scored/metrics.json` |
| R147 | 2026-08-16 08:00 | official-phase2-v1 | Codex SDK | gpt-5.5 + gpt-5.6-sol（分阶段，见配置） | 16/50 | 4/50 | 4/50 | 0 | complete_scored | [配置](#r147) / metrics: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/scored/metrics.json` |
| R148 | 2026-08-16 09:37 | raw-causal-serial-v1 | Codex SDK | gpt-5.5；xhigh / — | 17/50 | 8/50 | 4/50 | 0 | complete_scored | [配置](#r148) / metrics: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/scored/metrics.json` |
| R149 | 2026-08-16 11:44 | faithful-local-v1 | Codex SDK | gpt-5.5 + gpt-5.6-luna（分阶段，见配置） | 16/50 | 9/50 | 7/50 | 0 | complete_scored | [配置](#r149) / metrics: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/scored/metrics.json` |
| R150 | 2026-08-19 17:44 | official-repo-topology-v1 | LLM API | gpt-4.1；not_applicable / 0.0 | 14/50 | 9/50 | 5/50 | 0 | complete_scored | [配置](#r150) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/scored/metrics.json` |
| R154 | 2026-08-21 17:44 | strict-v8.2-paper50-v1 | LLM API | gpt-4.1；not_applicable / 0.0 | 13/50 | 3/50 | 2/50 | 0 | complete_scored | [配置](#r154) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/scored/metrics.json` |
| R156 | 2026-08-22 20:05 | luna-gaia-v3.13-conservative-challenger | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r156) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/scored/metrics.json` |
| R157 | 2026-08-22 21:42 | luna-gaia-v3.14-earliest-causal-challenger | Codex SDK | gpt-5.6-luna；medium / — | 24/50 | 13/50 | 8/50 | 0 | complete_scored | [配置](#r157) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/scored/metrics.json` |
| R158 | 2026-08-23 01:42 | luna-gaia-v3.15-packet-handoff-closure | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r158) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/scored/metrics.json` |
| R159 | 2026-08-23 03:11 | luna-gaia-v3.16-bounded-bidirectional-challenger | Codex SDK | gpt-5.6-luna；medium / — | 24/50 | 16/50 | 11/50 | 0 | complete_scored | [配置](#r159) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/scored/metrics.json` |
| R160 | 2026-08-23 04:47 | luna-gaia-v3.17-mandatory-earlier-scan | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 12/50 | 11/50 | 0 | complete_scored | [配置](#r160) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/scored/metrics.json` |
| R161 | 2026-08-23 06:27 | luna-gaia-v3.18-probe-contribution-veto | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 14/50 | 9/50 | 0 | complete_scored | [配置](#r161) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/scored/metrics.json` |
| R162 | 2026-08-23 08:02 | luna-gaia-v3.19-hard-disqualifier-precedence | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 13/50 | 8/50 | 0 | complete_scored | [配置](#r162) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/scored/metrics.json` |
| R163 | 2026-08-23 09:30 | luna-gaia-v3.20-packet-state-closure | Codex SDK | gpt-5.6-luna；medium / — | 25/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r163) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/scored/metrics.json` |
| R164 | 2026-08-23 11:00 | luna-gaia-v3.21-typed-state-claim-entailment | Codex SDK | gpt-5.6-luna；medium / — | 16/50 | 11/50 | 8/50 | 0 | complete_scored | [配置](#r164) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/scored/metrics.json` |
| R165 | 2026-08-23 12:36 | luna-gaia-v3.22-isolated-bidirectional-state-challenger | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 12/50 | 6/50 | 0 | complete_scored | [配置](#r165) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/scored/metrics.json` |
| R166 | 2026-08-23 14:15 | luna-gaia-v3.23-mandatory-state-scan-before-veto | Codex SDK | gpt-5.6-luna；medium / — | 18/50 | 12/50 | 7/50 | 0 | complete_scored | [配置](#r166) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/scored/metrics.json` |
| R167 | 2026-08-23 16:11 | luna-gaia-v3.24-isolated-state-evidence-ledger | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 10/50 | 7/50 | 0 | complete_scored | [配置](#r167) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/scored/metrics.json` |
| R168 | 2026-08-23 18:16 | luna-gaia-v3.25-predecessor-feedback-aligned-state-ledger | Codex SDK | gpt-5.6-luna；medium / — | 18/50 | 12/50 | 9/50 | 0 | complete_scored | [配置](#r168) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/scored/metrics.json` |
| R169 | 2026-08-23 20:32 | luna-gaia-v3.26-same-step-consumer-witnessed-state-ledger | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 11/50 | 7/50 | 0 | complete_scored | [配置](#r169) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/scored/metrics.json` |
| R170 | 2026-08-23 23:15 | luna-gaia-v3.27-prior-feedback-matured-capability-admission | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 12/50 | 9/50 | 0 | complete_scored | [配置](#r170) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/scored/metrics.json` |
| R171 | 2026-08-24 00:48 | luna-gaia-v3.28-clean-v3.20-prior-feedback-matured-capability-admission | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 13/50 | 11/50 | 0 | complete_scored | [配置](#r171) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/scored/metrics.json` |
| R172 | 2026-08-24 02:23 | luna-gaia-v3.29-clean-v3.20-acquisition-anchor-zero-contribution-challenger | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 14/50 | 8/50 | 0 | complete_scored | [配置](#r172) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/scored/metrics.json` |
| R173 | 2026-08-24 03:44 | luna-gaia-v3.30-clean-v3.20-bounded-bidirectional-challenger | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r173) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/scored/metrics.json` |
| R174 | 2026-08-24 06:11 | luna-gaia-v3.31-clean-v3.20-dual-anchor-disagreement-adjudication | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 13/50 | 10/50 | 0 | complete_scored | [配置](#r174) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/scored/metrics.json` |
| R175 | 2026-08-24 07:50 | luna-gaia-v3.32-clean-v3.20-complete-step-census-challenger | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 13/50 | 11/50 | 0 | complete_scored | [配置](#r175) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/scored/metrics.json` |
| R176 | 2026-08-24 09:55 | luna-gaia-v3.33-clean-v3.20-anchor-blind-complete-step-census-freeze | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 16/50 | 12/50 | 0 | complete_scored | [配置](#r176) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/scored/metrics.json` |
| R177 | 2026-08-24 11:38 | luna-gaia-v3.34-clean-v3.20-observable-impact-bidirectional-challenger | Codex SDK | gpt-5.6-luna；medium / — | 23/50 | 14/50 | 10/50 | 0 | complete_scored | [配置](#r177) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/scored/metrics.json` |
| R178 | 2026-08-24 13:16 | luna-gaia-v3.35-clean-v3.20-veto-closed-observable-impact-challenger | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 13/50 | 8/50 | 0 | complete_scored | [配置](#r178) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/scored/metrics.json` |
| R179 | 2026-08-24 14:51 | luna-gaia-v3.36-clean-v3.20-task-predicate-maturity-closure | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 13/50 | 10/50 | 0 | complete_scored | [配置](#r179) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/scored/metrics.json` |
| R180 | 2026-08-24 16:43 | luna-gaia-v3.37-clean-v3.20-factorized-anchor-blind-specialist-panel | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r180) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/scored/metrics.json` |
| R181 | 2026-08-24 18:13 | luna-gaia-v3.38-clean-v3.20-typed-boundary-calibration | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 14/50 | 11/50 | 0 | complete_scored | [配置](#r181) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/scored/metrics.json` |
| R182 | 2026-08-24 19:56 | luna-gaia-v3.39-clean-v3.20-bounded-typed-boundary-challenger | Codex SDK | gpt-5.6-luna；medium / — | 25/50 | 14/50 | 9/50 | 0 | complete_scored | [配置](#r182) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/scored/metrics.json` |
| R183 | 2026-08-24 21:50 | luna-gaia-v3.40-clean-v3.20-complete-typed-boundary-census-challenger | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r183) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/scored/metrics.json` |
| R184 | 2026-08-24 23:37 | luna-gaia-v3.41-clean-v3.20-owner-factored-boundary-census-challenger | Codex SDK | gpt-5.6-luna；medium / — | 23/50 | 13/50 | 10/50 | 0 | complete_scored | [配置](#r184) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/scored/metrics.json` |
| R185 | 2026-08-25 01:37 | luna-gaia-v3.42-clean-v3.20-anchor-blind-three-specialist-tournament | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 14/50 | 9/50 | 0 | complete_scored | [配置](#r185) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/scored/metrics.json` |
| R186 | 2026-08-25 03:25 | luna-gaia-v3.43-clean-v3.20-direction-factorized-anchor-aware-challenger-tournament | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 14/50 | 9/50 | 0 | complete_scored | [配置](#r186) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/scored/metrics.json` |
| R187 | 2026-08-25 06:53 | luna-gaia-v3.44-clean-v3.20-provenance-blind-independent-boundary-ballot-tournament | Codex SDK | gpt-5.6-luna；medium / — | 13/50 | 9/50 | 5/50 | 0 | complete_scored | [配置](#r187) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/scored/metrics.json` |
| R188 | 2026-08-25 15:28 | luna-gaia-v3.47-clean-v3.20-relative-io-module-complete-local-error-profile-causal-promotion | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 13/50 | 8/50 | 0 | complete_scored | [配置](#r188) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/scored/metrics.json` |
| R189 | 2026-08-25 18:37 | luna-gaia-v3.48-clean-v3.20-profile-critical-compression-anchor-duel | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 14/50 | 10/50 | 0 | complete_scored | [配置](#r189) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/scored/metrics.json` |
| R190 | 2026-08-25 20:45 | luna-gaia-v3.49-clean-v3.20-anchor-blind-global-causal-proposal-duel | Codex SDK | gpt-5.6-luna；medium / — | 25/50 | 16/50 | 10/50 | 0 | complete_scored | [配置](#r190) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/scored/metrics.json` |
| R191 | 2026-08-26 01:34 | luna-gaia-v3.50-clean-v3.20-factorized-local-inventory-global-proposal-duel | Codex SDK | gpt-5.6-luna；medium / — | 15/50 | 10/50 | 8/50 | 0 | complete_scored | [配置](#r191) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/scored/metrics.json` |
| R192 | 2026-08-26 05:12 | luna-gaia-v3.51-clean-v3.20-replicated-global-causal-proposal-panel | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r192) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/scored/metrics.json` |
| R193 | 2026-08-26 09:06 | luna-gaia-v3.52-clean-v3.20-module-factorized-local-census-proposal-panel | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 14/50 | 10/50 | 0 | complete_scored | [配置](#r193) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/scored/metrics.json` |
| R194 | 2026-08-26 16:44 | luna-gaia-v3.54-clean-v3.20-step-isolated-paper-local-promotion-safe-system-evidence | Codex SDK | gpt-5.6-luna；medium / — | 18/50 | 9/50 | 7/50 | 0 | complete_scored | [配置](#r194) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/scored/metrics.json` |
| R195 | 2026-08-26 23:08 | luna-gaia-v3.56-clean-v3.20-step-isolated-class-stratified-anchor-selector-enumerated-contract | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 14/50 | 11/50 | 0 | complete_scored | [配置](#r195) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/scored/metrics.json` |
| R196 | 2026-08-27 05:13 | luna-gaia-v3.57-clean-v3.20-step-isolated-earliest-module-reservoir-anchor-selector | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 11/50 | 7/50 | 0 | complete_scored | [配置](#r196) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/scored/metrics.json` |
| R197 | 2026-08-27 17:06 | luna-gaia-v3.59-clean-v3.20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly | Codex SDK | gpt-5.6-luna；medium / — | 18/50 | 12/50 | 8/50 | 0 | complete_scored | [配置](#r197) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/scored/metrics.json` |
| R198 | 2026-08-27 18:35 | luna-gaia-v3.60-clean-v3.20-retrospective-prefix-ledger-closure | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 13/50 | 9/50 | 0 | complete_scored | [配置](#r198) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/scored/metrics.json` |
| R199 | 2026-08-27 20:35 | luna-gaia-v3.61-clean-v3.20-decision-time-evidence-maturity-census-challenger | Codex SDK | gpt-5.6-luna；medium / — | 20/50 | 13/50 | 10/50 | 0 | audit_invalid | [配置](#r199) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/scored/metrics.json` |
| R200 | 2026-08-28 03:02 | luna-gaia-v3.62-clean-v3.20-full-local-step-pairwise-reducer | Codex SDK | gpt-5.6-luna；medium / — | 18/50 | 11/50 | 8/50 | 0 | audit_invalid | [配置](#r200) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/scored/metrics.json` |
| R201 | 2026-08-28 06:46 | luna-gaia-v3.64-clean-v3.20-heterogeneous-critical-boundary-panel | Codex SDK | gpt-5.6-luna；medium / — | 18/50 | 10/50 | 9/50 | 0 | audit_invalid | [配置](#r201) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/scored/metrics.json` |
| R202 | 2026-08-28 09:01 | luna-gaia-v3.65-clean-v3.20-outcome-conditioned-global-boundary-proposal-duel | Codex SDK | gpt-5.6-luna；medium / — | 19/50 | 12/50 | 8/50 | 0 | audit_invalid | [配置](#r202) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/scored/metrics.json` |
| R203 | 2026-08-28 13:01 | luna-gaia-v3.74-clean-v3.20-exact-predicate-acquisition-boundary-reducer-owner-materialized | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 12/50 | 8/50 | 0 | complete_scored | [配置](#r203) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/scored/metrics.json` |
| R204 | 2026-08-28 14:05 | luna-gaia-v3.76-clean-v3.20-sparse-ledger-global-boundary-selector-runtime-repair | Codex SDK | gpt-5.6-luna；medium / — | 21/50 | 14/50 | 10/50 | 0 | complete_scored | [配置](#r204) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/scored/metrics.json` |
| R205 | 2026-08-28 15:19 | luna-gaia-v3.78-clean-v3.20-factorized-sparse-ledger-pairwise-selector-contract-repair | Codex SDK | gpt-5.6-luna；medium / — | 22/50 | 10/50 | 5/50 | 0 | complete_scored | [配置](#r205) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/scored/metrics.json` |
| R206 | 2026-08-28 16:17 | luna-gaia-v3.80-clean-v3.20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair | Codex SDK | gpt-5.6-luna；medium / — | 17/50 | 8/50 | 5/50 | 0 | complete_scored | [配置](#r206) / metrics: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/scored/metrics.json` |
| R207 | 2026-08-28 22:35 | gaia-v3.82-clean-v3.20-model-only-terra-medium | Codex SDK | gpt-5.6-terra；medium / — | 22/50 | 13/50 | 10/50 | 0 | complete_scored | [配置](#r207) / metrics: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/scored/metrics.json` |
| R208 | 2026-08-28 23:54 | gaia-v3.83-clean-v3.20-model-only-gpt55-medium | Codex SDK | gpt-5.5；medium / — | 26/50 | 16/50 | 13/50 | 0 | complete_scored | [配置](#r208) / metrics: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/scored/metrics.json` |
| R209 | 2026-08-29 01:10 | gaia-v3.84-model-only-gpt54-medium | Codex SDK | gpt-5.4；medium / — | 23/50 | 13/50 | 10/50 | 0 | complete_scored | [配置](#r209) / metrics: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/scored/metrics.json` |
| R210 | 2026-08-29 03:22 | gaia-v3.85-gpt55-high-effort-only | Codex SDK | gpt-5.5；high / — | 23/50 | 15/50 | 12/50 | 0 | complete_scored | [配置](#r210) / metrics: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/scored/metrics.json` |
| R211 | 2026-08-29 04:49 | gaia-v3.86-gpt55-bounded-typed-boundary-challenger | Codex SDK | gpt-5.5；medium / — | 24/50 | 15/50 | 11/50 | 0 | complete_scored | [配置](#r211) / metrics: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/scored/metrics.json` |
| R212 | 2026-08-29 13:04 | gaia-v3.87-gpt55-evidence-lifecycle-challenger | Codex SDK | gpt-5.5；medium / — | 18/50 | 12/50 | 11/50 | 0 | complete_scored | [配置](#r212) / metrics: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/scored/metrics.json` |
| R213 | 2026-08-29 14:35 | gaia-v3.88-gpt55-sparse-influence-graph-challenger | Codex SDK | gpt-5.5；medium / — | 22/50 | 14/50 | 10/50 | 0 | complete_scored | [配置](#r213) / metrics: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/scored/metrics.json` |
| R214 | 2026-08-29 16:03 | gaia-v3.89-gpt55-sol-heterogeneous-challenger | Codex SDK | gpt-5.5 + gpt-5.6-sol（分阶段，见配置） | 26/50 | 15/50 | 12/50 | 0 | complete_scored | [配置](#r214) / metrics: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/scored/metrics.json` |
| R215 | 2026-08-30 18:25 | gaia-v3.102-gpt55-three-attempt-access-validated-tournament | Codex SDK | gpt-5.5；medium / — | 21/50 | 13/50 | 8/50 | 0 | complete_scored | [配置](#r215) / metrics: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/scored/metrics.json` |
| R216 | 2026-08-31 22:26 | gaia-v3.107-v3.83-codex-sdk-bounded-retry | Codex SDK | gpt-5.5；medium / — | 23/50 | 18/50 | 13/50 | 0 | complete_scored | [配置](#r216) / metrics: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/scored/metrics.json` |
| R219 | 2026-09-03 04:00 | official-repo-topology-sdk-v3-native-taxonomy-bridge | Codex SDK | gpt-5.5；medium / — | 19/50 | 9/50 | 6/50 | 0 | complete_scored | [配置](#r219) / metrics: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/scored/metrics.json` |

### Full / 150

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R218 | 2026-09-01 20:56 | gaia-v3.83-clean-v3.20-model-only-gpt55-medium | Codex SDK | gpt-5.5；medium / — | 33/150 | 8/150 | 3/120 | 0 | complete_scored | [配置](#r218) / metrics: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/rest150/metrics.json` |

### Small diagnostics / 8

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R221 | 未知 | candidate-v3 | LLM API | gpt-4.1；— / 0.0 | 2/8 | 1/8 | 1/8 | 0 | complete_scored | [配置](#r221) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v1-agent-judge-candidate-v3-case8/scored/metrics.json` |
| R222 | 未知 | serial-v4 | LLM API | gpt-4.1；— / 0.0 | 3/8 | 2/8 | 1/8 | 0 | complete_scored | [配置](#r222) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v2-agent-judge-serial-v4-case8/scored/metrics.json` |
| R223 | 未知 | boundary-v5 | LLM API | gpt-4.1；— / 0.0 | 2/8 | 2/8 | 1/8 | 0 | mutated_diagnostic | [配置](#r223) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v3-agent-judge-boundary-v5-case8/scored/metrics.json` |
| R224 | 未知 | strict-v8 | LLM API | gpt-4.1；— / 0.0 | 3/8 | 2/8 | 2/8 | 0 | complete_scored | [配置](#r224) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v6-agent-judge-strict-v8-case8/scored/metrics.json` |
| R225 | 未知 | atom-v12 | LLM API | gpt-4.1；not_applicable / 0.0 | 3/8 | 1/8 | 1/8 | 0 | complete_scored | [配置](#r225) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v12-case8/scored/metrics.json` |
| R226 | 未知 | atom-v13-backtrace | LLM API | gpt-4.1；not_applicable / 0.0 | 3/8 | 1/8 | 1/8 | 0 | complete_scored | [配置](#r226) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v13-backtrace-case8/scored/metrics.json` |

### Small diagnostics / 10

| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |
|---|---|---|---|---|---:|---:|---:|---:|---|---|
| R227 | 未知 | official-repo-canonical-v2 | LLM API | gpt-4.1；— / 0.0 | 9/10 | 3/10 | 1/10 | 0 | complete_scored | [配置](#r227) / metrics: `output/agenterrorbench-sophnet-gpt-4.1-gaia-structural-gate-v1-agent-judge-official-repo-canonical-v2-case10/scored/metrics.json` |

## 每次运行的配置与证据

### R001

gpt-4o-smoke / direct

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4o；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=300.0。
- 协议：`agenterrorbench-direct-v1`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v1。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4o-smoke/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4o-smoke/per_example.csv` · report.md: `output/agenterrorbench-gpt-4o-smoke/report.md`

### R002

gpt-4o-smoke / two_stage

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4o；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=300.0。
- 协议：`agentdebug-two-stage-v1`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v1。
- 计分：step_exact=1/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4o-smoke/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4o-smoke/per_example.csv` · report.md: `output/agenterrorbench-gpt-4o-smoke/report.md`

### R003

gpt-4o-smoke-v2 / direct

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4o；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=300.0。
- 协议：`agenterrorbench-direct-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v2-lossless-string-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4o-smoke-v2/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4o-smoke-v2/per_example.csv` · report.md: `output/agenterrorbench-gpt-4o-smoke-v2/report.md`

### R004

gpt-4o-smoke-v2 / two_stage

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4o；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=300.0。
- 协议：`agentdebug-two-stage-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v2-lossless-string-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4o-smoke-v2/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4o-smoke-v2/per_example.csv` · report.md: `output/agenterrorbench-gpt-4o-smoke-v2/report.md`

### R005

gpt-4o-v2 / direct

- 数据：complete_available_release；N=200；环境={"alfworld": 100, "webshop": 50, "gaia": 50}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4o；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=300.0。
- 协议：`agenterrorbench-direct-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v2-lossless-string-table。
- 计分：step_exact=2/200；step_module_exact=0/200；all_correct=0/170；失败=177；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4o-v2/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4o-v2/per_example.csv` · report.md: `output/agenterrorbench-gpt-4o-v2/report.md`

### R006

gpt-4o-v2 / two_stage

- 数据：complete_available_release；N=200；环境={"alfworld": 100, "webshop": 50, "gaia": 50}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4o；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=300.0。
- 协议：`agentdebug-two-stage-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v2-lossless-string-table。
- 计分：step_exact=3/200；step_module_exact=0/200；all_correct=0/170；失败=185；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4o-v2/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4o-v2/per_example.csv` · report.md: `output/agenterrorbench-gpt-4o-v2/report.md`

### R007

smoke / direct

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=600.0。
- 协议：`agenterrorbench-direct-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v2-lossless-string-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-smoke/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-smoke/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-smoke/report.md`

### R008

smoke / two_stage

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=600.0。
- 协议：`agentdebug-two-stage-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v2-lossless-string-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-smoke/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-smoke/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-smoke/report.md`

### R009

largest-smoke / direct

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=600.0。
- 协议：`agenterrorbench-direct-v2-lossless-string-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v2-lossless-string-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-largest-smoke/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-largest-smoke/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-largest-smoke/report.md`

### R010

largest-smoke-v3 / direct

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=600.0。
- 协议：`agenterrorbench-direct-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v3-lossless-chunk-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-largest-smoke-v3/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-largest-smoke-v3/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-largest-smoke-v3/report.md`

### R011

largest-two-stage-smoke-v3 / two_stage

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=None；timeout=600.0。
- 协议：`agentdebug-two-stage-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v3-lossless-chunk-table。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-largest-two-stage-smoke-v3/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-largest-two-stage-smoke-v3/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-largest-two-stage-smoke-v3/report.md`

### R012

max-output-smoke / direct

- 数据：explicit_subset；N=1；环境={"gaia": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agenterrorbench-direct-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v3-lossless-chunk-table。
- 计分：step_exact=1/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-max-output-smoke/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-max-output-smoke/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-max-output-smoke/report.md`

### R013

pro-preview / direct

- 数据：complete_available_release；N=200；环境={"alfworld": 100, "webshop": 50, "gaia": 50}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agenterrorbench-direct-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agenterrorbench-direct-v3-lossless-chunk-table。
- 计分：step_exact=41/200；step_module_exact=14/200；all_correct=9/170；失败=42；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-pro-preview/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-pro-preview/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-pro-preview/report.md`

### R014

pro-preview / two_stage

- 数据：complete_available_release；N=200；环境={"alfworld": 100, "webshop": 50, "gaia": 50}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gemini-3.1-pro-preview；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v3-lossless-chunk-table。
- 计分：step_exact=36/200；step_module_exact=12/200；all_correct=6/170；失败=67；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gemini-3.1-pro-preview/metrics.json` · per_example.csv: `output/agenterrorbench-gemini-3.1-pro-preview/per_example.csv` · report.md: `output/agenterrorbench-gemini-3.1-pro-preview/report.md`

### R015

tuning-v1-baseline / two_stage

- 数据：tuning-v1；N=30；环境={"gaia": 10, "webshop": 10, "alfworld": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v3-lossless-chunk-table。
- 计分：step_exact=1/30；step_module_exact=0/30；all_correct=0/25；失败=10；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-baseline/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-baseline/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-baseline/report.md`

### R016

smoke-v1-baseline / two_stage

- 数据：smoke-v1；N=30；环境={"gaia": 10, "webshop": 10, "alfworld": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v3-lossless-chunk-table`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v3-lossless-chunk-table。
- 计分：step_exact=4/30；step_module_exact=2/30；all_correct=1/27；失败=9；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-smoke-v1-baseline/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-smoke-v1-baseline/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-smoke-v1-baseline/report.md`

### R017

tuning-v1-e1-dry3 / two_stage

- 数据：explicit_subset；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v5-canonical-judge-view-v2-aeb-incremental-batched-specialists`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v5-canonical-judge-view-v2-aeb-incremental-batched-specialists。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-dry3/report.md`

### R018

tuning-v1-e1b-web-format / two_stage

- 数据：explicit_subset；N=1；环境={"webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v6-canonical-judge-view-v2-aeb-incremental-numeric-step`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v6-canonical-judge-view-v2-aeb-incremental-numeric-step。
- 计分：step_exact=0/1；step_module_exact=0/1；all_correct=0/1；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e1b-web-format/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e1b-web-format/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e1b-web-format/report.md`

### R019

tuning-v1-e1-v7 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v7-canonical-judge-view-v2-aeb-incremental-flow-attribution`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v7-canonical-judge-view-v2-aeb-incremental-flow-attribution。
- 计分：step_exact=8/30；step_module_exact=4/30；all_correct=3/25；失败=1；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-v7/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-v7/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e1-v7/report.md`

### R020

tuning-v1-e2-matrix-dry3 / two_stage

- 数据：explicit_subset；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v8-canonical-judge-view-v3-aeb-incremental-execution-facts-verdict-matrix`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v8-canonical-judge-view-v3-aeb-incremental-execution-facts-verdict-matrix。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-matrix-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-matrix-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-matrix-dry3/report.md`

### R021

tuning-v1-e2-v9-schema-dry3 / two_stage

- 数据：explicit_subset；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v9-canonical-judge-view-v3-aeb-incremental-execution-facts-verdict-matrix-schema-example`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v9-canonical-judge-view-v3-aeb-incremental-execution-facts-verdict-matrix-schema-example。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v9-schema-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v9-schema-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v9-schema-dry3/report.md`

### R022

tuning-v1-e2-v10-validity-dry3 / two_stage

- 数据：explicit_subset；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-two-stage-v10-canonical-judge-view-v3-aeb-incremental-execution-facts-local-validity-veto`。
- 父版本：`None`。主要机制/拓扑：agentdebug-two-stage-v10-canonical-judge-view-v3-aeb-incremental-execution-facts-local-validity-veto。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v10-validity-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v10-validity-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e2-v10-validity-dry3/report.md`

### R023

tuning-v1-m3-v1-dry3 / two_stage

- 数据：explicit_subset；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-m3-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-independent-adjudication`。
- 父版本：`None`。主要机制/拓扑：agentdebug-m3-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-independent-adjudication。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-m3-v1-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-m3-v1-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-m3-v1-dry3/report.md`

### R024

tuning-v1-e4-v1-dry3 / two_stage

- 数据：explicit_subset；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e4-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-module-specialists`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e4-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-module-specialists。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e4-v1-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e4-v1-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e4-v1-dry3/report.md`

### R025

tuning-v1-e5a-replay-critic-dry3

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e5-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-module-specialists-adversarial-critic`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e5-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-module-specialists-adversarial-critic。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5a-replay-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e5a-replay-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e5a-replay-critic-dry3/report.md` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5a-replay-critic-dry3/predict-run.json`

### R026

tuning-v1-e5b-explicit-audit-dry3

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e5b-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-explicit-adversarial-audit`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e5b-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-explicit-adversarial-audit。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5b-explicit-audit-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e5b-explicit-audit-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e5b-explicit-audit-dry3/report.md` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5b-explicit-audit-dry3/predict-run.json`

### R027

tuning-v1-e5c-handoff-dry3

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e5c-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-cross-boundary-ledger-independent-selector`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e5c-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-cross-boundary-ledger-independent-selector。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-handoff-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-handoff-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-handoff-dry3/report.md` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-handoff-dry3/predict-run.json`

### R028

tuning-v1-e5c-strict-revalidation-dry3

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e5c-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-cross-boundary-ledger-independent-selector`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e5c-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-cross-boundary-ledger-independent-selector。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：revalidation；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-strict-revalidation-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-strict-revalidation-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-strict-revalidation-dry3/report.md` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5c-strict-revalidation-dry3/predict-run.json`

### R029

tuning-v1-e5d-evidence-repair-dry3

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-evidence-repair-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-frozen-semantics-exact-source-substring`。
- 父版本：`None`。主要机制/拓扑：agentdebug-evidence-repair-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-frozen-semantics-exact-source-substring。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：evidence_only_repair；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-evidence-repair-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-evidence-repair-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-evidence-repair-dry3/report.md` · repair-predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-evidence-repair-dry3/repair-predict-run.json`

### R030

tuning-v1-e5d-v2-json-fallback-dry3

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-evidence-repair-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-frozen-semantics-exact-source-substring`。
- 父版本：`None`。主要机制/拓扑：agentdebug-evidence-repair-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-frozen-semantics-exact-source-substring。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：evidence_only_repair；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-v2-json-fallback-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-v2-json-fallback-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-v2-json-fallback-dry3/report.md` · repair-predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e5d-v2-json-fallback-dry3/repair-predict-run.json`

### R031

tuning-v1-e6-v2-production-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e5c-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-cross-boundary-ledger-independent-selector+conditional-agentdebug-evidence-repair-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-frozen-semantics-exact-source-substring`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e5c-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-cross-boundary-ledger-independent-selector+conditional-agentdebug-evidence-repair-v1-canonical-judge-view-v3-aeb-incremental-execution-facts-frozen-semantics-exact-source-substring。
- 计分：step_exact=5/30；step_module_exact=3/30；all_correct=3/25；失败=4；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e6-v2-production-full30/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e6-v2-production-full30/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e6-v2-production-full30/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e6-v2-production-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e6-v2-production-full30/predict-run.json`

### R032

tuning-v1-e7-v3-global-critic-dry5 / two_stage

- 数据：tuning-v1；N=5；环境={"alfworld": 1, "gaia": 2, "webshop": 2}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e7-v3-canonical-judge-view-v3-aeb-incremental-execution-facts-official-module-scan-fallible-prior-five-causal-tests-json-schema`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e7-v3-canonical-judge-view-v3-aeb-incremental-execution-facts-official-module-scan-fallible-prior-five-causal-tests-json-schema。
- 计分：step_exact=2/5；step_module_exact=0/5；all_correct=0/5；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e7-v3-global-critic-dry5/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e7-v3-global-critic-dry5/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e7-v3-global-critic-dry5/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e7-v3-global-critic-dry5/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e7-v3-global-critic-dry5/predict-run.json`

### R033

tuning-v1-e8-v3-fresh-semantic-dry5 / two_stage

- 数据：tuning-v1；N=5；环境={"alfworld": 1, "gaia": 2, "webshop": 2}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`agentdebug-e8-v2-canonical-judge-view-v3-aeb-incremental-execution-facts-anonymous-trace-joint-maturity-ownership-five-field-json`。
- 父版本：`None`。主要机制/拓扑：agentdebug-e8-v2-canonical-judge-view-v3-aeb-incremental-execution-facts-anonymous-trace-joint-maturity-ownership-five-field-json。
- 计分：step_exact=1/5；step_module_exact=1/5；all_correct=1/5；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e8-v3-fresh-semantic-dry5/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e8-v3-fresh-semantic-dry5/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e8-v3-fresh-semantic-dry5/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e8-v3-fresh-semantic-dry5/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e8-v3-fresh-semantic-dry5/predict-run.json`

### R034

tuning-v1-e9-v1-batched-causal-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v1-three-anonymous-complete-timelines-two-candidates', 'arbiter': 'agentdebug-e9-arbiter-v1-independent-joint-root-evidence-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v1-three-anonymous-complete-timelines-two-candidates', 'arbiter': 'agentdebug-e9-arbiter-v1-independent-joint-root-evidence-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v1-batched-causal-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v1-batched-causal-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v1-batched-causal-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v1-batched-causal-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v1-batched-causal-dry3/predict-run.json`

### R035

tuning-v1-e9-v2-batched-module-audit-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v2-five-module-nullable-chronology-falsification', 'arbiter': 'agentdebug-e9-arbiter-v2-module-audit-chronology-falsification-evidence'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v2-five-module-nullable-chronology-falsification', 'arbiter': 'agentdebug-e9-arbiter-v2-module-audit-chronology-falsification-evidence'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v2-batched-module-audit-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v2-batched-module-audit-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v2-batched-module-audit-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v2-batched-module-audit-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v2-batched-module-audit-dry3/predict-run.json`

### R036

tuning-v1-e9-v3-candidate-review-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v3-five-module-nullable-chronology-falsification', 'arbiter': 'agentdebug-e9-arbiter-v3-structured-candidate-reviews-evidence'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v3-five-module-nullable-chronology-falsification', 'arbiter': 'agentdebug-e9-arbiter-v3-structured-candidate-reviews-evidence'}。
- 计分：step_exact=1/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v3-candidate-review-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v3-candidate-review-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v3-candidate-review-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v3-candidate-review-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v3-candidate-review-dry3/predict-run.json`

### R037

tuning-v1-e9-v4-chronology-first-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v4-label-free-chronology-cartographer', 'arbiter': 'agentdebug-e9-arbiter-v4-chronology-ownership-boundary-proof'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v4-label-free-chronology-cartographer', 'arbiter': 'agentdebug-e9-arbiter-v4-chronology-ownership-boundary-proof'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=2；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v4-chronology-first-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v4-chronology-first-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v4-chronology-first-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v4-chronology-first-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v4-chronology-first-dry3/predict-run.json`

### R038

tuning-v1-e9-v5-owner-maturity-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v5-label-free-coverage-cartographer', 'arbiter': 'agentdebug-e9-arbiter-v5-local-ownership-maturity-boundary'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v5-label-free-coverage-cartographer', 'arbiter': 'agentdebug-e9-arbiter-v5-local-ownership-maturity-boundary'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v5-owner-maturity-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v5-owner-maturity-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v5-owner-maturity-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v5-owner-maturity-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v5-owner-maturity-dry3/predict-run.json`

### R039

tuning-v1-e9-v6-atomic-boundary-cycle-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v6-time-cutoff-maturity-boundary-fork'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v6-time-cutoff-maturity-boundary-fork'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=2；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v6-atomic-boundary-cycle-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v6-atomic-boundary-cycle-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v6-atomic-boundary-cycle-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v6-atomic-boundary-cycle-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v6-atomic-boundary-cycle-dry3/predict-run.json`

### R040

tuning-v1-e9-v7-flat-arbiter-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v7-flat-semantic-root'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v7-flat-semantic-root'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=2；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v7-flat-arbiter-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v7-flat-arbiter-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v7-flat-arbiter-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v7-flat-arbiter-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v7-flat-arbiter-dry3/predict-run.json`

### R041

tuning-v1-e9-v8-tail-recency-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v8-tail-recency-causal-audit'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v8-tail-recency-causal-audit'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v8-tail-recency-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v8-tail-recency-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v8-tail-recency-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v8-tail-recency-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v8-tail-recency-dry3/predict-run.json`

### R042

tuning-v1-e9-v9-literal-constraint-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v9-literal-constraint-coverage-audit'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v9-literal-constraint-coverage-audit'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v9-literal-constraint-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v9-literal-constraint-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v9-literal-constraint-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v9-literal-constraint-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v9-literal-constraint-dry3/predict-run.json`

### R043

tuning-v1-e9-v10-ordered-root-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v10-ordered-root-eligibility-audit'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v10-ordered-root-eligibility-audit'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v10-ordered-root-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v10-ordered-root-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v10-ordered-root-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v10-ordered-root-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v10-ordered-root-dry3/predict-run.json`

### R044

tuning-v1-e9-v11-visible-audit-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v11-visible-audit-certificate'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v6-label-free-course-checkpoints', 'arbiter': 'agentdebug-e9-arbiter-v11-visible-audit-certificate'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=2；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v11-visible-audit-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v11-visible-audit-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v11-visible-audit-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v11-visible-audit-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v11-visible-audit-dry3/predict-run.json`

### R045

tuning-v1-e9-v12-semantic-candidates-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v8-unranked-semantic-candidates-capability-history', 'arbiter': 'agentdebug-e9-arbiter-v12-independent-review-capability-history'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v8-unranked-semantic-candidates-capability-history', 'arbiter': 'agentdebug-e9-arbiter-v12-independent-review-capability-history'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v12-semantic-candidates-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v12-semantic-candidates-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v12-semantic-candidates-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v12-semantic-candidates-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v12-semantic-candidates-dry3/predict-run.json`

### R046

tuning-v1-e9-v13-atomic-taxonomy-pair-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v13-atomic-taxonomy-pair', 'arbiter': 'agentdebug-e9-arbiter-v12-independent-review-capability-history'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v13-atomic-taxonomy-pair', 'arbiter': 'agentdebug-e9-arbiter-v12-independent-review-capability-history'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-dry3/predict-run.json`

### R047

tuning-v1-e9-v13-atomic-taxonomy-pair-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'scout': 'agentdebug-e9-scout-v13-atomic-taxonomy-pair', 'arbiter': 'agentdebug-e9-arbiter-v12-independent-review-capability-history'}`。
- 父版本：`None`。主要机制/拓扑：{'scout': 'agentdebug-e9-scout-v13-atomic-taxonomy-pair', 'arbiter': 'agentdebug-e9-arbiter-v12-independent-review-capability-history'}。
- 计分：step_exact=6/30；step_module_exact=3/30；all_correct=3/25；失败=1；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-full30/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-full30/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-full30/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v13-atomic-taxonomy-pair-full30/predict-run.json`

### R048

tuning-v1-e9-v14-prior-late-balanced-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v14-prior-late-balanced-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v14-prior-late-balanced-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v14-prior-late-balanced-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v14-prior-late-balanced-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-gpt-4.1-tuning-v1-e9-v14-prior-late-balanced-critic-dry3/predict-run.json`

### R049

tuning-v1-e9-v15-prior-late-balanced-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v15-prior-late-balanced-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v15-prior-late-balanced-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v15-prior-late-balanced-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v15-prior-late-balanced-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v15-prior-late-balanced-critic-dry3/predict-run.json`

### R050

tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v16-retry1-prior-late-balanced-critic-dry3/predict-run.json`

### R051

tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v14-progress-aware-ownership-falsification-atomic-pair'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v17-default-prior-late-balanced-critic-dry3/predict-run.json`

### R052

tuning-v1-e9-v18-conservative-prior-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v18-incumbent-review-search-episode-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v18-incumbent-review-search-episode-atomic-pair'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v18-conservative-prior-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v18-conservative-prior-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v18-conservative-prior-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v18-conservative-prior-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v18-conservative-prior-critic-dry3/predict-run.json`

### R053

tuning-v1-e9-v19-task-closing-prior-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-pro；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v19-task-closing-recovery-search-episode-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v19-task-closing-recovery-search-episode-atomic-pair'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v19-task-closing-prior-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v19-task-closing-prior-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v19-task-closing-prior-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v19-task-closing-prior-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v19-task-closing-prior-critic-dry3/predict-run.json`

### R054

tuning-v1-e9-v20-minimal-final-prior-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-pro；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v20-minimal-final-task-progress-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v20-minimal-final-task-progress-atomic-pair'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v20-minimal-final-prior-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v20-minimal-final-prior-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v20-minimal-final-prior-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v20-minimal-final-prior-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-pro-tuning-v1-e9-v20-minimal-final-prior-critic-dry3/predict-run.json`

### R055

tuning-v1-e9-v21-format-safe-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v21-source-id-single-brace-repair-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v21-source-id-single-brace-repair-atomic-pair'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v21-format-safe-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v21-format-safe-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v21-format-safe-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v21-format-safe-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v21-format-safe-critic-dry3/predict-run.json`

### R056

tuning-v1-e9-v22-recovery-checkpoint-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v22-recovery-checkpoint-source-id-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v22-recovery-checkpoint-source-id-atomic-pair'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：recovered_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v22-recovery-checkpoint-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v22-recovery-checkpoint-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v22-recovery-checkpoint-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v22-recovery-checkpoint-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v22-recovery-checkpoint-critic-dry3/predict-run.json`

### R057

tuning-v1-e9-v23-novelty-recovery-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v23-novelty-calibrated-recovery-source-id-atomic-pair'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v23-novelty-calibrated-recovery-source-id-atomic-pair'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=3；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：recovered_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v23-novelty-recovery-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v23-novelty-recovery-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v23-novelty-recovery-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v23-novelty-recovery-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v23-novelty-recovery-critic-dry3/predict-run.json`

### R058

tuning-v1-e9-v24-final-content-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v24-final-content-novelty-recovery-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v24-final-content-novelty-recovery-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-dry3/predict-run.json`

### R059

tuning-v1-e9-v24-final-content-critic-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v24-final-content-novelty-recovery-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v24-final-content-novelty-recovery-source-id'}。
- 计分：step_exact=6/30；step_module_exact=4/30；all_correct=4/25；失败=10；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v24-final-content-critic-full30/predict-run.json`

### R060

tuning-v1-e9-v25-local-error-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v25-official-local-error-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v25-official-local-error-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-dry3/predict-run.json`

### R061

tuning-v1-e9-v25-local-error-critic-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v25-official-local-error-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v25-official-local-error-source-id'}。
- 计分：step_exact=10/30；step_module_exact=3/30；all_correct=3/25；失败=2；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v25-local-error-critic-full30/predict-run.json`

### R062

tuning-v1-e9-v26-upstream-owner-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v26-upstream-owner-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v26-upstream-owner-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v26-upstream-owner-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v26-upstream-owner-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v26-upstream-owner-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v26-upstream-owner-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v26-upstream-owner-critic-dry3/predict-run.json`

### R063

tuning-v1-e9-v27-critical-event-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v27-critical-event-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v27-critical-event-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-dry3/predict-run.json`

### R064

tuning-v1-e9-v27-critical-event-critic-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v27-critical-event-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v27-critical-event-source-id'}。
- 计分：step_exact=9/30；step_module_exact=3/30；all_correct=3/25；失败=3；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v27-critical-event-critic-full30/predict-run.json`

### R065

tuning-v1-e9-v28-flat-review-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v28-flat-review-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v28-flat-review-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v28-flat-review-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v28-flat-review-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v28-flat-review-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v28-flat-review-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v28-flat-review-critic-dry3/predict-run.json`

### R066

tuning-v1-e9-v29-terminal-guard-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v29-terminal-guard-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v29-terminal-guard-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-dry3/predict-run.json`

### R067

tuning-v1-e9-v29-terminal-guard-critic-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v29-terminal-guard-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v29-terminal-guard-source-id'}。
- 计分：step_exact=9/30；step_module_exact=3/30；all_correct=3/25；失败=1；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v29-terminal-guard-critic-full30/predict-run.json`

### R068

tuning-v1-e9-v30-first-defect-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v30-first-defect-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v30-first-defect-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-dry3/predict-run.json`

### R069

tuning-v1-e9-v30-first-defect-critic-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v30-first-defect-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v30-first-defect-source-id'}。
- 计分：step_exact=10/30；step_module_exact=5/30；all_correct=4/25；失败=1；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v30-first-defect-critic-full30/predict-run.json`

### R070

tuning-v1-e9-v31-pairwise-candidate-critic-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-critic-v31-pairwise-candidate-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-critic-v31-pairwise-candidate-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-critic-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-critic-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-critic-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-critic-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-critic-dry3/predict-run.json`

### R071

tuning-v1-e9-v32-candidate-selector-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v32-pairwise-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v32-pairwise-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v32-candidate-selector-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v32-candidate-selector-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v32-candidate-selector-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v32-candidate-selector-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v32-candidate-selector-dry3/predict-run.json`

### R072

tuning-v1-e9-v33-maturity-calibrated-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v33-maturity-calibrated-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v33-maturity-calibrated-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v33-maturity-calibrated-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v33-maturity-calibrated-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v33-maturity-calibrated-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v33-maturity-calibrated-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v33-maturity-calibrated-dry3/predict-run.json`

### R073

tuning-v1-e9-v34-capability-query-epoch-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v34-capability-query-epoch-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v34-capability-query-epoch-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v34-capability-query-epoch-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v34-capability-query-epoch-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v34-capability-query-epoch-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v34-capability-query-epoch-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v34-capability-query-epoch-dry3/predict-run.json`

### R074

tuning-v1-e9-v35-symmetric-brace-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v35-capability-query-epoch-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v35-capability-query-epoch-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-dry3/predict-run.json`

### R075

tuning-v1-e9-v35-symmetric-brace-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v35-capability-query-epoch-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v35-capability-query-epoch-source-id'}。
- 计分：step_exact=7/30；step_module_exact=4/30；all_correct=4/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v35-symmetric-brace-full30/predict-run.json`

### R076

tuning-v1-e9-v36-original-causal-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v36-original-phase2-causal-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v36-original-phase2-causal-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v36-original-causal-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v36-original-causal-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v36-original-causal-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v36-original-causal-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v36-original-causal-dry3/predict-run.json`

### R077

tuning-v1-e9-v37-incumbent-preserving-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v37-incumbent-preserving-causal-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v37-incumbent-preserving-causal-source-id'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v37-incumbent-preserving-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v37-incumbent-preserving-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v37-incumbent-preserving-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v37-incumbent-preserving-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v37-incumbent-preserving-dry3/predict-run.json`

### R078

tuning-v1-e9-v38-first-defect-terminal-guard-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v38-first-defect-terminal-guard-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v38-first-defect-terminal-guard-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-dry3/predict-run.json`

### R079

tuning-v1-e9-v38-first-defect-terminal-guard-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v38-first-defect-terminal-guard-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v38-first-defect-terminal-guard-source-id'}。
- 计分：step_exact=9/30；step_module_exact=4/30；all_correct=3/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v38-first-defect-terminal-guard-full30/predict-run.json`

### R080

tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v39-multi-hypothesis-causal-ledger-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v39-multi-hypothesis-causal-ledger-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=1；逐例重算=True。
- 状态：scored_failures_zero。小样本/诊断；不代表完整GAIA-50；失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v39-multi-hypothesis-causal-ledger-dry3/predict-run.json`

### R081

tuning-v1-e9-v40-causal-ledger-length-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v40-multi-hypothesis-causal-ledger-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v40-multi-hypothesis-causal-ledger-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-dry3/predict-run.json`

### R082

tuning-v1-e9-v40-causal-ledger-length-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v40-multi-hypothesis-causal-ledger-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v40-multi-hypothesis-causal-ledger-source-id'}。
- 计分：step_exact=9/30；step_module_exact=4/30；all_correct=4/25；失败=1；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v40-causal-ledger-length-full30/predict-run.json`

### R083

tuning-v1-e9-v41-symmetric-module-census-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v41-symmetric-module-census-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v41-symmetric-module-census-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v41-symmetric-module-census-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v41-symmetric-module-census-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v41-symmetric-module-census-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v41-symmetric-module-census-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v41-symmetric-module-census-dry3/predict-run.json`

### R084

tuning-v1-e9-v42-chronological-module-census-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v42-chronological-module-census-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v42-chronological-module-census-source-id'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v42-chronological-module-census-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v42-chronological-module-census-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v42-chronological-module-census-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v42-chronological-module-census-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v42-chronological-module-census-dry3/predict-run.json`

### R085

tuning-v1-e9-v43-symmetric-causal-lanes-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v43-symmetric-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v43-symmetric-causal-lanes-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v43-symmetric-causal-lanes-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v43-symmetric-causal-lanes-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v43-symmetric-causal-lanes-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v43-symmetric-causal-lanes-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v43-symmetric-causal-lanes-dry3/predict-run.json`

### R086

tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v44-failure-preventing-causal-lanes-dry3/predict-run.json`

### R087

tuning-v1-e9-v45-categorical-boundary-action-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v45-categorical-boundary-action-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v45-categorical-boundary-action-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v45-categorical-boundary-action-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v45-categorical-boundary-action-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v45-categorical-boundary-action-dry3/predict-run.json`

### R088

tuning-v1-e9-v46-persistent-information-root-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-dry3/predict-run.json`

### R089

tuning-v1-e9-v46-persistent-information-root-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v44-failure-preventing-causal-lanes-source-id'}。
- 计分：step_exact=9/30；step_module_exact=3/30；all_correct=3/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v46-persistent-information-root-full30/predict-run.json`

### R090

tuning-v1-e9-v47-five-lane-handoff-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v47-five-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v47-five-causal-lanes-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v47-five-lane-handoff-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v47-five-lane-handoff-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v47-five-lane-handoff-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v47-five-lane-handoff-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v47-five-lane-handoff-dry3/predict-run.json`

### R091

tuning-v1-e9-v48-scout-broadened-handoff-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v48-five-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v48-five-causal-lanes-source-id'}。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v48-scout-broadened-handoff-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v48-scout-broadened-handoff-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v48-scout-broadened-handoff-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v48-scout-broadened-handoff-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v48-scout-broadened-handoff-dry3/predict-run.json`

### R092

tuning-v1-e9-v49-cross-module-consistency-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v49-cross-module-consistency-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v49-cross-module-consistency-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v49-cross-module-consistency-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v49-cross-module-consistency-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v49-cross-module-consistency-dry3/predict-run.json`

### R093

tuning-v1-e9-v50-selector-capacity-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v50-selector-capacity-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v50-selector-capacity-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v50-selector-capacity-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v50-selector-capacity-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v50-selector-capacity-dry3/predict-run.json`

### R094

tuning-v1-e9-v51-whitespace-brace-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-dry3/predict-run.json`

### R095

tuning-v1-e9-v51-whitespace-brace-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v49-six-causal-lanes-source-id'}。
- 计分：step_exact=7/30；step_module_exact=3/30；all_correct=3/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v51-whitespace-brace-full30/predict-run.json`

### R096

tuning-v1-e9-v52-module-census-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v52-module-local-census-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v52-module-local-census-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-dry3/predict-run.json`

### R097

tuning-v1-e9-v52-module-census-recovery-v2-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=9/30；step_module_exact=5/30；all_correct=4/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：recovered_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-recovery-v2-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-recovery-v2-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-recovery-v2-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-recovery-v2-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v52-module-census-recovery-v2-full30/predict-run.json`

### R098

tuning-v1-e9-v53-dual-timescale-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v53-dual-timescale-planning-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v53-dual-timescale-planning-source-id'}。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v53-dual-timescale-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v53-dual-timescale-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v53-dual-timescale-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v53-dual-timescale-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v53-dual-timescale-dry3/predict-run.json`

### R099

tuning-v1-e9-v54-contradiction-first-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`{'critic': 'agentdebug-e9-candidate-v54-contradiction-first-planning-source-id'}`。
- 父版本：`None`。主要机制/拓扑：{'critic': 'agentdebug-e9-candidate-v54-contradiction-first-planning-source-id'}。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v54-contradiction-first-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v54-contradiction-first-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v54-contradiction-first-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v54-contradiction-first-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v54-contradiction-first-dry3/predict-run.json`

### R100

tuning-v1-e9-v55-one-stage-global-dry3 / two_stage

- 数据：selection-specific；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：one_stage_global。
- 计分：step_exact=0/3；step_module_exact=0/3；all_correct=0/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v55-one-stage-global-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v55-one-stage-global-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v55-one-stage-global-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v55-one-stage-global-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v55-one-stage-global-dry3/predict-run.json`

### R101

tuning-v1-e9-v31-pairwise-candidate-recovered-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=10/30；step_module_exact=4/30；all_correct=4/25；失败=1；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：recovered_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-recovered-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-recovered-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-recovered-full30/report.md` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v31-pairwise-candidate-recovered-full30/predict-run.json`

### R102

tuning-v1-e9-v56-v30-incumbent-review-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=1/3；step_module_exact=1/3；all_correct=1/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v56-v30-incumbent-review-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v56-v30-incumbent-review-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v56-v30-incumbent-review-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v56-v30-incumbent-review-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v56-v30-incumbent-review-dry3/predict-run.json`

### R103

tuning-v1-e9-v57-v30-earlier-only-review-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-dry3/predict-run.json`

### R104

tuning-v1-e9-v57-v30-earlier-only-review-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=10/30；step_module_exact=4/30；all_correct=3/25；失败=4；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v57-v30-earlier-only-review-full30/predict-run.json`

### R105

tuning-v1-e9-v58-v30-incumbent-copy-review-dry3 / two_stage

- 数据：tuning-v1；N=3；环境={"alfworld": 1, "gaia": 1, "webshop": 1}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=2/3；step_module_exact=2/3；all_correct=2/3；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-dry3/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-dry3/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-dry3/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-dry3/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-dry3/predict-run.json`

### R106

tuning-v1-e9-v58-v30-incumbent-copy-review-full30 / two_stage

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=12/30；step_module_exact=5/30；all_correct=4/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-full30/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-full30/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-full30/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-full30/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-tuning-v1-e9-v58-v30-incumbent-copy-review-full30/predict-run.json`

### R107

smoke-v1-e9-v58-fresh-v30-review / two_stage

- 数据：smoke-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：deepseek-v4-flash；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=5；max_output_tokens=8192；timeout=600.0。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=3/27；失败=3；逐例重算=True。
- 状态：scored_failures_zero。失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-deepseek-v4-flash-smoke-v1-e9-v58-fresh-v30-review/metrics.json` · per_example.csv: `output/agenterrorbench-deepseek-v4-flash-smoke-v1-e9-v58-fresh-v30-review/per_example.csv` · report.md: `output/agenterrorbench-deepseek-v4-flash-smoke-v1-e9-v58-fresh-v30-review/report.md` · preregistration.json: `output/agenterrorbench-deepseek-v4-flash-smoke-v1-e9-v58-fresh-v30-review/preregistration.json` · predict-run.json: `output/agenterrorbench-deepseek-v4-flash-smoke-v1-e9-v58-fresh-v30-review/predict-run.json`

### R108

v1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-terra；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.v1`。
- 父版本：`None`。主要机制/拓扑：three_stage_five_step_agent_judge。
- 计分：step_exact=5/30；step_module_exact=1/30；all_correct=0/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-agent-judge-v1/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-agent-judge-v1/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-agent-judge-v1/scored/report.md` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-agent-judge-v1/prediction-audit.json` · preregistration.json: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-agent-judge-v1/preregistration.json`

### R109

v2_2

- 数据：tuning-v1；N=9；环境={"alfworld": 3, "gaia": 3, "webshop": 3}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-terra；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=1；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.v2.2`。
- 父版本：`None`。主要机制/拓扑：step_owner_type_with_first_false_proposition_and_validation_loop。
- 计分：step_exact=1/9；step_module_exact=0/9；all_correct=0/7；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-gate3x3-agent-judge-v2_2/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-gate3x3-agent-judge-v2_2/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-gate3x3-agent-judge-v2_2/scored/report.md` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-gate3x3-agent-judge-v2_2/prediction-audit.json` · preregistration.json: `output/agenterrorbench-codex-gpt-5.6-terra-tuning-v1-gate3x3-agent-judge-v2_2/preregistration.json`

### R110

luna-v1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v1`。
- 父版本：`None`。主要机制/拓扑：complete_local_pair_census_global_critical_root_definition_guarded_luna。
- 计分：step_exact=5/30；step_module_exact=1/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1-case30/prediction-audit.json`

### R111

luna-v2

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v2`。
- 父版本：`None`。主要机制/拓扑：upstream_introduction_ledger_same_step_handoff_luna。
- 计分：step_exact=6/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v2-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v2-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v2-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v2-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v2-case30/prediction-audit.json`

### R112

luna-v3

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v3`。
- 父版本：`None`。主要机制/拓扑：chronological_first_mature_breakpoint_then_owner_then_type_luna。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-case30/prediction-audit.json`

### R113

luna-v4

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v4`。
- 父版本：`None`。主要机制/拓扑：chronological_breakpoint_same_defect_backtrace_then_owner_luna。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v4-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v4-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v4-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v4-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v4-case30/prediction-audit.json`

### R114

luna-v5

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v5`。
- 父版本：`None`。主要机制/拓扑：module_lane_recall_categorical_first_mature_arbitration_luna。
- 计分：step_exact=6/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v5-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v5-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v5-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v5-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v5-case30/prediction-audit.json`

### R115

luna-v6

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v6`。
- 父版本：`None`。主要机制/拓扑：v3_draft_conservative_execution_recovery_probe_handoff_correction_luna。
- 计分：step_exact=7/30；step_module_exact=2/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v6-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v6-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v6-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v6-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v6-case30/prediction-audit.json`

### R116

luna-v7

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v7`。
- 父版本：`None`。主要机制/拓扑：same_case_luna_v3_incumbent_strictly_earlier_conservative_review。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：historical_prior_prediction。读取同case历史预测；不满足后续统一fresh/no-prior边界
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v7-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v7-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v7-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v7-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v7-case30/prediction-audit.json`

### R117

luna-v8

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v8`。
- 父版本：`None`。主要机制/拓扑：same_case_v3_incumbent_earliest_independent_challenger_review。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：historical_prior_prediction。读取同case历史预测；不满足后续统一fresh/no-prior边界
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v8-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v8-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v8-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v8-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v8-case30/prediction-audit.json`

### R118

luna-v9

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v9`。
- 父版本：`None`。主要机制/拓扑：blind_same_case_v3_v4_dual_proposal_boundary_arbitration。
- 计分：step_exact=7/30；step_module_exact=4/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：historical_prior_prediction。读取同case历史预测；不满足后续统一fresh/no-prior边界
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v9-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v9-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v9-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v9-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v9-case30/prediction-audit.json`

### R119

luna-v10

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v10`。
- 父版本：`None`。主要机制/拓扑：single_v3_incumbent_confirmation_wrapper_recovery_hard_veto_review。
- 计分：step_exact=5/30；step_module_exact=2/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：historical_prior_prediction。读取同case历史预测；不满足后续统一fresh/no-prior边界
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v10-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v10-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v10-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v10-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v10-case30/prediction-audit.json`

### R120

luna-v11

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v11`。
- 父版本：`None`。主要机制/拓扑：v3_incumbent_planning_inefficient_sink_isolated_relocation。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：historical_prior_prediction。读取同case历史预测；不满足后续统一fresh/no-prior边界
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v11-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v11-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v11-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v11-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v11-case30/prediction-audit.json`

### R121

luna-v12

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`luna-v12`。
- 父版本：`None`。主要机制/拓扑：v3_sink_forced_single_local_failure_boundary_replacement。
- 计分：step_exact=13/30；step_module_exact=6/30；all_correct=5/25；失败=0；逐例重算=True。
- 状态：historical_prior_prediction。读取同case历史预测；不满足后续统一fresh/no-prior边界
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-case30/tuning-plan.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-case30/prediction-audit.json`

### R122

luna-v3-serial-v2

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-v3-serial-v2`。
- 父版本：`None`。主要机制/拓扑：three_fresh_serial_agents_with_deterministic_type_evidence_sources。
- 计分：step_exact=7/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v2-case30/prediction-audit.json`

### R123

luna-v12-standalone-v1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-v12-standalone-v1`。
- 父版本：`None`。主要机制/拓扑：proposal_free_all_module_single_local_failure_competition_luna。
- 计分：step_exact=7/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：audit_qualified。输出计分有效；独立审计发现allowlist及写入边界缺口
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v12-standalone-v1-case30/prediction-audit.json`

### R124

luna-clean-debate-v1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-clean-debate-v1`。
- 父版本：`None`。主要机制/拓扑：three fresh same-case sessions; anonymous current-run proposals; no historical prediction or label-pair routing。
- 计分：step_exact=8/30；step_module_exact=3/30；all_correct=2/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v1-case30/prediction-audit.json`

### R125

luna-clean-debate-v2

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-clean-debate-v2`。
- 父版本：`None`。主要机制/拓扑：three fresh same-case sessions; two current-run candidates followed by an exact-choice structured causal tournament; no historical prediction or label-pair routing。
- 计分：step_exact=8/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v2-case30/prediction-audit.json`

### R126

luna-clean-debate-v3

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-clean-debate-v3`。
- 父版本：`None`。主要机制/拓扑：four fresh same-case sessions; three current-run distinct-step candidates followed by an exact-choice causal panel; no historical prediction, environment routing, or label-pair routing。
- 计分：step_exact=6/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v3-case30/prediction-audit.json`

### R127

luna-clean-debate-v4-rerun1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-clean-debate-v4`。
- 父版本：`None`。主要机制/拓扑：two fresh clean-v1 different-step candidates followed by a fresh uniform chronological root-precedence exact-copy arbiter; no historical prediction or label-pair routing。
- 计分：step_exact=8/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-rerun1-case30/prediction-audit.json`

### R128

luna-gaia-v1

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v1`。
- 父版本：`None`。主要机制/拓扑：v3_chronological_breakpoint_with_nested_owner_evidence_fragments。
- 计分：step_exact=10/30；step_module_exact=9/30；all_correct=5/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v1-case30/prediction-audit.json`

### R129

luna-gaia-v2.1

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v2.1`。
- 父版本：`None`。主要机制/拓扑：recovery_aware_causal_state_ledger_with_short_execution_aliases。
- 计分：step_exact=9/30；step_module_exact=7/30；all_correct=5/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2p1-case30/prediction-audit.json`

### R130

luna-gaia-v3

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_immutable_step_checkpoint。
- 计分：step_exact=11/30；step_module_exact=8/30；all_correct=6/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3-case30/prediction-audit.json`

### R131

luna-gaia-v3.1

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.1`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_step_checkpoint_and_external_exception_packet_fence。
- 计分：step_exact=14/30；step_module_exact=11/30；all_correct=9/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p1-case30/prediction-audit.json`

### R132

luna-gaia-v3.2

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.2`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_step_checkpoint_packet_fence_and_capability_admission_gate。
- 计分：step_exact=12/30；step_module_exact=9/30；all_correct=7/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p2-case30/prediction-audit.json`

### R133

luna-gaia-v3.3

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.3`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_step_checkpoint_packet_fence_and_strategy_identity_gate。
- 计分：step_exact=12/30；step_module_exact=10/30；all_correct=6/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p3-case30/prediction-audit.json`

### R134

luna-gaia-v3.4

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.4`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_validated_step_candidate_ledger_step_checkpoint_and_external_exception_packet_fence。
- 计分：step_exact=16/30；step_module_exact=10/30；all_correct=7/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p4-case30/prediction-audit.json`

### R135

luna-gaia-v3.5.1

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.5.1`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_validated_step_only_candidate_ledger_checkpoint_packet_fence_and_positive_immediate_subgoal_capability。
- 计分：step_exact=15/30；step_module_exact=9/30；all_correct=6/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5p1-case30/prediction-audit.json`

### R136

luna-gaia-v3.6

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.6`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_step_only_candidate_ledger_checkpoint_packet_fence_positive_capability_and_action_materiality。
- 计分：step_exact=15/30；step_module_exact=13/30；all_correct=10/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p6-case30/prediction-audit.json`

### R137

luna-gaia-v3.7.1

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.7.1`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_precommit_step_ledger_checkpoint_packet_fence_positive_capability_action_materiality_and_orthogonal_same_route_strategy_state。
- 计分：step_exact=13/30；step_module_exact=11/30；all_correct=8/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7p1-case30/prediction-audit.json`

### R138

luna-gaia-v3.8

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.8`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_precommit_step_ledger_checkpoint_packet_fence_positive_capability_action_materiality_and_structured_lane_a_claim_support。
- 计分：step_exact=15/30；step_module_exact=12/30；all_correct=9/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p8-case30/prediction-audit.json`

### R139

luna-gaia-v3.9

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.9`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_validated_step_candidate_ledger_checkpoint_packet_fence_and_static_document_capability_outcome_separation。
- 计分：step_exact=14/30；step_module_exact=10/30；all_correct=7/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p9-case30/prediction-audit.json`

### R140

luna-gaia-v3.10

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.10`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_validated_step_candidate_ledger_checkpoint_packet_fence_literal_pdf_capability_outcome_rule_and_shell_safe_compact_validation。
- 计分：step_exact=14/30；step_module_exact=10/30；all_correct=8/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p10-case30/prediction-audit.json`

### R141

luna-gaia-v3.4

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.4`。
- 父版本：`None`。主要机制/拓扑：lane_ordered_chronology_with_validated_step_candidate_ledger_step_checkpoint_and_external_exception_packet_fence。
- 计分：step_exact=21/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p4-case50/prediction-audit.json`

### R142

v2.4-global-census

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-terra；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.v2.4`。
- 父版本：`None`。主要机制/拓扑：complete_local_pair_census_global_critical_root_new_defect_owner。
- 计分：step_exact=11/50；step_module_exact=6/50；all_correct=4/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-v2p4-global-census-case50/prediction-audit.json`

### R143

two-stage-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-sol；reasoning effort=high；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.sol-gaia-two-stage-v1`。
- 父版本：`None`。主要机制/拓扑：one fresh high-recall unranked candidate-proposer followed by one fresh closed-set causal root arbiter; frozen same-case proposal carry-forward。
- 计分：step_exact=15/50；step_module_exact=5/50；all_correct=2/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-two-stage-v1-case50/prediction-audit.json`

### R144

serial-v2

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：{"inherited-candidate-proposer": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "inherited-step": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}, "module": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}, "error-type": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.sol-luna-gaia-serial-v2`。
- 父版本：`None`。主要机制/拓扑：reuse the complete frozen gold-free Sol candidate and Luna Step lineage from invalid serial-v1; replay fresh Luna-medium Module and Type sessions for every case with deterministic validator-owned evidence sources。
- 计分：step_exact=15/50；step_module_exact=9/50；all_correct=5/50；失败=0；逐例重算=True。
- 状态：complete_scored。继承历史冻结中间结果的阶段重放；不能视作全流程fresh推理
- 运行类型：stage_replay；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-sol-luna-gaia-paper-v2-agent-judge-serial-v2-case50/prediction-audit.json`

### R145

forced-census-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-sol；reasoning effort=high；temperature=None。
- 分阶段模型/effort：{"forced-census-memory": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "forced-census-reflection": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "forced-census-planning": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "forced-census-action": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "forced-census-system": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "global-root-arbiter": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.sol-gaia-forced-census-v1`。
- 父版本：`None`。主要机制/拓扑：five fresh isolated module specialists each forced to review every step, deterministic extraction and merge of all error hypotheses, then one fresh Sol-high global joint step/module/type root arbiter。
- 计分：step_exact=13/50；step_module_exact=6/50；all_correct=5/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-sol-high-gaia-paper-v1-agent-judge-forced-census-v1-case50/prediction-audit.json`

### R146

causal-serial-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：{"inherited-forced-census": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "step": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}, "module": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "error-type": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-causal-serial-v1`。
- 父版本：`None`。主要机制/拓扑：reuse only frozen gold-free forced-census hypotheses through a deterministic label-hidden all-step dossier; fresh Luna-medium Step, fresh Sol-high Module, then fresh Sol-high Type for every case。
- 计分：step_exact=16/50；step_module_exact=8/50；all_correct=6/50；失败=0；逐例重算=True。
- 状态：complete_scored。继承历史冻结中间结果的阶段重放；不能视作全流程fresh推理
- 运行类型：stage_replay；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-luna-sol-gaia-paper-v2-agent-judge-causal-serial-v1-case50/prediction-audit.json`

### R147

official-phase2-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=xhigh；temperature=None。
- 分阶段模型/effort：{"inherited-phase1-census": {"model": "gpt-5.6-sol", "reasoning_effort": "high"}, "joint-phase2": {"model": "gpt-5.5", "reasoning_effort": "xhigh"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-official-phase2-v1`。
- 父版本：`None`。主要机制/拓扑：reuse only five frozen gold-free all-step Phase1 module censuses through an exact official-format projection; one fresh gpt-5.5/xhigh joint Phase2 judge per case may select any step/module/type。
- 计分：step_exact=16/50；step_module_exact=4/50；all_correct=4/50；失败=0；逐例重算=True。
- 状态：complete_scored。继承历史冻结中间结果的阶段重放；不能视作全流程fresh推理
- 运行类型：stage_replay；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v3-agent-judge-official-phase2-v1-case50/prediction-audit.json`

### R148

raw-causal-serial-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=xhigh；temperature=None。
- 分阶段模型/effort：{"step": {"model": "gpt-5.5", "reasoning_effort": "xhigh"}, "module": {"model": "gpt-5.5", "reasoning_effort": "xhigh"}, "error-type": {"model": "gpt-5.5", "reasoning_effort": "xhigh"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-raw-causal-serial-v1`。
- 父版本：`None`。主要机制/拓扑：fresh label-free complete-raw-trajectory Step, then fresh selected-step information-flow Module, then fresh late-bound Type; all gpt-5.5/xhigh。
- 计分：step_exact=17/50；step_module_exact=8/50；all_correct=4/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-xhigh-gaia-paper-v4-agent-judge-raw-causal-serial-v1-case50/prediction-audit.json`

### R149

faithful-local-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=xhigh；temperature=None。
- 分阶段模型/effort：{"phase1": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}, "phase2": {"model": "gpt-5.5", "reasoning_effort": "xhigh"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-faithful-local-v1`。
- 父版本：`None`。主要机制/拓扑：four fresh official-local temporally bounded Phase1 module reviewers, positive-only deterministic merge, then fresh unrestricted joint Phase2。
- 计分：step_exact=16/50；step_module_exact=9/50；all_correct=7/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-luna-gpt5.5-gaia-paper-v5-agent-judge-faithful-local-v1-case50/prediction-audit.json`

### R150

official-repo-topology-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=not_applicable；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=None；HTTP尝试上限=3；legacy max_retries=3；max_output_tokens=None；timeout=180.0。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-v1`。
- 父版本：`None`。主要机制/拓扑：official_repository_independent_step_module_phase1_calls_then_positive_only_full_trajectory_joint_phase2。
- 计分：step_exact=14/50；step_module_exact=9/50；all_correct=5/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/scored/report.md` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v6-agent-judge-official-repo-topology-v1-case50/prediction-audit.json`

### R151

luna-v14-unified-v1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-v14-unified-v1`。
- 父版本：`None`。主要机制/拓扑：proposal_free_one_session_dual_owner_bound_evidence_atom_locators_then_uniform_arbitration_and_atom_locked_taxonomy。
- 计分：step_exact=9/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v14-unified-v1-case30/prediction-audit.json`

### R152

luna-v15-unified-v2

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-v15-unified-v2`。
- 父版本：`None`。主要机制/拓扑：proposal_free_one_session_three_step_only_locators_plus_derived_predecessor_neutral_arbitration_then_same_step_owner_atom_and_type。
- 计分：step_exact=7/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v2-case30/prediction-audit.json`

### R153

luna-v16-unified-v1

- 数据：tuning-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-v16-unified-v1`。
- 父版本：`None`。主要机制/拓扑：proposal_free_one_session_three_owner_bound_evidence_witnesses_plus_parent_strategy_predecessor_lane_blind_uniform_arbitration_then_same_step_owner_atom_and_type。
- 计分：step_exact=6/30；step_module_exact=2/30；all_correct=1/25；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v16-unified-v1-case30/prediction-audit.json`

### R154

strict-v8.2-paper50-v1

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=not_applicable；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=None；HTTP尝试上限=3；legacy max_retries=3；max_output_tokens=None；timeout=240.0。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-strict-v8.2`。
- 父版本：`None`。主要机制/拓扑：three-top2-specialists-top3-coverage-assessor-selector-module-type。
- 计分：step_exact=13/50；step_module_exact=3/50；all_correct=2/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/scored/report.md` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p2-paper50-v1-case50/prediction-audit.json`

### R155

luna-gaia-v3.12-global

- 数据：gaia-smoke-v1；N=30；环境={"gaia": 30}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：{"candidate_census": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}, "global_selection": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}, "same_step_owner_type_binding": {"model": "gpt-5.6-luna", "reasoning_effort": "medium"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.12-global`。
- 父版本：`None`。主要机制/拓扑：three fresh Luna sessions: exhaustive full-trajectory step×module census, global root selection, then frozen-step owner/type/evidence binding。
- 计分：step_exact=9/30；step_module_exact=6/30；all_correct=4/30；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p12-global-case30/prediction-audit.json`

### R156

luna-gaia-v3.13-conservative-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.13-conservative-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.4`。主要机制/拓扑：one later challenger with default-keep arbiter。
- 计分：step_exact=20/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p13-conservative-challenger-case50/prediction-audit.json`

### R157

luna-gaia-v3.14-earliest-causal-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.13-conservative-challenger`。主要机制/拓扑：earliest path-intervention-causal ordering for the sole later challenger。
- 计分：step_exact=24/50；step_module_exact=13/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p14-earliest-causal-challenger-case50/prediction-audit.json`

### R158

luna-gaia-v3.15-packet-handoff-closure

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.15-packet-handoff-closure`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger`。主要机制/拓扑：task-material result-to-state and target-to-action packet-handoff closure in the anchor。
- 计分：step_exact=20/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p15-packet-handoff-closure-case50/prediction-audit.json`

### R159

luna-gaia-v3.16-bounded-bidirectional-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.16-bounded-bidirectional-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger`。主要机制/拓扑：one bounded earlier-first bidirectional challenger over the unchanged anchor。
- 计分：step_exact=24/50；step_module_exact=16/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p16-bounded-bidirectional-challenger-case50/prediction-audit.json`

### R160

luna-gaia-v3.17-mandatory-earlier-scan

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.17-mandatory-earlier-scan`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger`。主要机制/拓扑：validator-enforced ordered earlier-scan ledger before the one challenger。
- 计分：step_exact=19/50；step_module_exact=12/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p17-mandatory-earlier-scan-case50/prediction-audit.json`

### R161

luna-gaia-v3.18-probe-contribution-veto

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.18-probe-contribution-veto`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger`。主要机制/拓扑：validator-audited probe-contribution veto in anchor candidate admission。
- 计分：step_exact=22/50；step_module_exact=14/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p18-probe-contribution-veto-case50/prediction-audit.json`

### R162

luna-gaia-v3.19-hard-disqualifier-precedence

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.19-hard-disqualifier-precedence`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.18-probe-contribution-veto`。主要机制/拓扑：literal hard-disqualifier precedence over the probe-contribution veto。
- 计分：step_exact=20/50；step_module_exact=13/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p19-hard-disqualifier-precedence-case50/prediction-audit.json`

### R163

luna-gaia-v3.20-packet-state-closure

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.14-earliest-causal-challenger`。主要机制/拓扑：validator-audited observation-to-Memory/Reflection packet-state closure。
- 计分：step_exact=25/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p20-packet-state-closure-case50/prediction-audit.json`

### R164

luna-gaia-v3.21-typed-state-claim-entailment

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.21-typed-state-claim-entailment`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：typed Memory/Reflection claim-kind and entailment-relation closure。
- 计分：step_exact=16/50；step_module_exact=11/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p21-typed-state-claim-entailment-case50/prediction-audit.json`

### R165

luna-gaia-v3.22-isolated-bidirectional-state-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.22-isolated-bidirectional-state-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one isolated state-only bidirectional challenger over the v3.20 anchor。
- 计分：step_exact=22/50；step_module_exact=12/50；all_correct=6/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p22-isolated-bidirectional-state-challenger-case50/prediction-audit.json`

### R166

luna-gaia-v3.23-mandatory-state-scan-before-veto

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.23-mandatory-state-scan-before-veto`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.22-isolated-bidirectional-state-challenger`。主要机制/拓扑：mandatory complete state scan and candidate freeze before anchor veto。
- 计分：step_exact=18/50；step_module_exact=12/50；all_correct=7/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p23-mandatory-state-scan-before-veto-case50/prediction-audit.json`

### R167

luna-gaia-v3.24-isolated-state-evidence-ledger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia-v3.24-isolated-state-evidence-ledger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.23-mandatory-state-scan-before-veto`。主要机制/拓扑：validator-complete local evidence row for every state Step and earliest-candidate derivation。
- 计分：step_exact=20/50；step_module_exact=10/50；all_correct=7/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p24-isolated-state-evidence-ledger-case50/prediction-audit.json`

### R168

luna-gaia-v3.25-predecessor-feedback-aligned-state-ledger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.25-predecessor-feedback-aligned-state-ledger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia.v3.24-isolated-state-evidence-ledger`。主要机制/拓扑：mechanical predecessor-feedback binding for every state evidence row。
- 计分：step_exact=18/50；step_module_exact=12/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p25-predecessor-feedback-aligned-state-ledger-case50/prediction-audit.json`

### R169

luna-gaia-v3.26-same-step-consumer-witnessed-state-ledger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.26-same-step-consumer-witnessed-state-ledger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia.v3.25-predecessor-feedback-aligned-state-ledger`。主要机制/拓扑：literal same-Step later-module Planning/Action consumer witness for state candidates。
- 计分：step_exact=19/50；step_module_exact=11/50；all_correct=7/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p26-same-step-consumer-witnessed-state-ledger-case50/prediction-audit.json`

### R170

luna-gaia-v3.27-prior-feedback-matured-capability-admission

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.27-prior-feedback-matured-capability-admission`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia.v3.26-same-step-consumer-witnessed-state-ledger`。主要机制/拓扑：prior-feedback maturity gate before interface/corpus Lane-B admission。
- 计分：step_exact=21/50；step_module_exact=12/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p27-prior-feedback-matured-capability-admission-case50/prediction-audit.json`

### R171

luna-gaia-v3.28-clean-v3.20-prior-feedback-matured-capability-admission

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.28-clean-v3.20-prior-feedback-matured-capability-admission`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：prior-feedback maturity gate before interface/corpus Lane-B admission。
- 计分：step_exact=19/50；step_module_exact=13/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p28-clean-v3p20-prior-feedback-matured-capability-admission-case50/prediction-audit.json`

### R172

luna-gaia-v3.29-clean-v3.20-acquisition-anchor-zero-contribution-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.29-clean-v3.20-acquisition-anchor-zero-contribution-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：literal zero-contribution gate for acquisition-anchor challenger classification。
- 计分：step_exact=20/50；step_module_exact=14/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p29-clean-v3p20-acquisition-anchor-zero-contribution-challenger-case50/prediction-audit.json`

### R173

luna-gaia-v3.30-clean-v3.20-bounded-bidirectional-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.30-clean-v3.20-bounded-bidirectional-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one bounded earlier-first bidirectional challenger。
- 计分：step_exact=20/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p30-clean-v3p20-bounded-bidirectional-challenger-case50/prediction-audit.json`

### R174

luna-gaia-v3.31-clean-v3.20-dual-anchor-disagreement-adjudication

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.31-clean-v3.20-dual-anchor-disagreement-adjudication`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：two independent v3.20 anchors with disagreement-only adjudication。
- 计分：step_exact=21/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p31-clean-v3p20-dual-anchor-disagreement-adjudication-case50/prediction-audit.json`

### R175

luna-gaia-v3.32-clean-v3.20-complete-step-census-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.32-clean-v3.20-complete-step-census-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one validator-complete Step census before challenger anchor classification。
- 计分：step_exact=21/50；step_module_exact=13/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p32-clean-v3p20-complete-step-census-challenger-case50/prediction-audit.json`

### R176

luna-gaia-v3.33-clean-v3.20-anchor-blind-complete-step-census-freeze

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.33-clean-v3.20-anchor-blind-complete-step-census-freeze`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：anchor-blind complete-Step candidate freeze before separate anchor comparison。
- 计分：step_exact=22/50；step_module_exact=16/50；all_correct=12/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p33-clean-v3p20-anchor-blind-complete-step-census-freeze-case50/prediction-audit.json`

### R177

luna-gaia-v3.34-clean-v3.20-observable-impact-bidirectional-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.34-clean-v3.20-observable-impact-bidirectional-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one observable-impact evidence-stratified bidirectional challenger。
- 计分：step_exact=23/50；step_module_exact=14/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p34-clean-v3p20-observable-impact-bidirectional-challenger-case50/prediction-audit.json`

### R178

luna-gaia-v3.35-clean-v3.20-veto-closed-observable-impact-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.35-clean-v3.20-veto-closed-observable-impact-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one veto-closed observable-impact challenger。
- 计分：step_exact=22/50；step_module_exact=13/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p35-clean-v3p20-veto-closed-observable-impact-challenger-case50/prediction-audit.json`

### R179

luna-gaia-v3.36-clean-v3.20-task-predicate-maturity-closure

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.36-clean-v3.20-task-predicate-maturity-closure`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one task-predicate maturity-closure challenger。
- 计分：step_exact=22/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p36-clean-v3p20-task-predicate-maturity-closure-case50/prediction-audit.json`

### R180

luna-gaia-v3.37-clean-v3.20-factorized-anchor-blind-specialist-panel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.37-clean-v3.20-factorized-anchor-blind-specialist-panel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one factorized anchor-blind two-specialist recall panel。
- 计分：step_exact=22/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p37-clean-v3p20-factorized-anchor-blind-specialist-panel-case50/prediction-audit.json`

### R181

luna-gaia-v3.38-clean-v3.20-typed-boundary-calibration

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.38-clean-v3.20-typed-boundary-calibration`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：typed critical-boundary calibration before the v3.20 Step freeze。
- 计分：step_exact=20/50；step_module_exact=14/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p38-clean-v3p20-typed-boundary-calibration-case50/prediction-audit.json`

### R182

luna-gaia-v3.39-clean-v3.20-bounded-typed-boundary-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.39-clean-v3.20-bounded-typed-boundary-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one bounded typed-boundary later challenger。
- 计分：step_exact=25/50；step_module_exact=14/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p39-clean-v3p20-bounded-typed-boundary-challenger-case50/prediction-audit.json`

### R183

luna-gaia-v3.40-clean-v3.20-complete-typed-boundary-census-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.40-clean-v3.20-complete-typed-boundary-census-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one complete typed-boundary census challenger/adjudication contract。
- 计分：step_exact=22/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p40-clean-v3p20-complete-typed-boundary-census-challenger-case50/prediction-audit.json`

### R184

luna-gaia-v3.41-clean-v3.20-owner-factored-boundary-census-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.41-clean-v3.20-owner-factored-boundary-census-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one owner-factored boundary census challenger/adjudication contract。
- 计分：step_exact=23/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p41-clean-v3p20-owner-factored-boundary-census-challenger-case50/prediction-audit.json`

### R185

luna-gaia-v3.42-clean-v3.20-anchor-blind-three-specialist-tournament

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.42-clean-v3.20-anchor-blind-three-specialist-tournament`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one anchor-blind three-specialist exact-copy tournament。
- 计分：step_exact=22/50；step_module_exact=14/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p42-clean-v3p20-anchor-blind-three-specialist-tournament-case50/prediction-audit.json`

### R186

luna-gaia-v3.43-clean-v3.20-direction-factorized-anchor-aware-challenger-tournament

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.43-clean-v3.20-direction-factorized-anchor-aware-challenger-tournament`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one direction-factorized anchor-aware exact-copy tournament。
- 计分：step_exact=21/50；step_module_exact=14/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p43-clean-v3p20-direction-factorized-anchor-aware-challenger-tournament-case50/prediction-audit.json`

### R187

luna-gaia-v3.44-clean-v3.20-provenance-blind-independent-boundary-ballot-tournament

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.44-clean-v3.20-provenance-blind-independent-boundary-ballot-tournament`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one provenance-blind independent-boundary ballot tournament。
- 计分：step_exact=13/50；step_module_exact=9/50；all_correct=5/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p44-clean-v3p20-provenance-blind-independent-boundary-ballot-tournament-case50/prediction-audit.json`

### R188

luna-gaia-v3.47-clean-v3.20-relative-io-module-complete-local-error-profile-causal-promotion

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.47-clean-v3.20-relative-io-module-complete-local-error-profile-causal-promotion`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one module-complete local-error profile with causal promotion。
- 计分：step_exact=19/50；step_module_exact=13/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p47-clean-v3p20-relative-io-module-complete-local-error-profile-causal-promotion-case50/prediction-audit.json`

### R189

luna-gaia-v3.48-clean-v3.20-profile-critical-compression-anchor-duel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.48-clean-v3.20-profile-critical-compression-anchor-duel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one module-complete profile critical-compression anchor duel。
- 计分：step_exact=19/50；step_module_exact=14/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p48-clean-v3p20-profile-critical-compression-anchor-duel-case50/prediction-audit.json`

### R190

luna-gaia-v3.49-clean-v3.20-anchor-blind-global-causal-proposal-duel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.49-clean-v3.20-anchor-blind-global-causal-proposal-duel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one anchor-blind global causal proposal duel。
- 计分：step_exact=25/50；step_module_exact=16/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p49-clean-v3p20-anchor-blind-global-causal-proposal-duel-case50/prediction-audit.json`

### R191

luna-gaia-v3.50-clean-v3.20-factorized-local-inventory-global-proposal-duel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.50-clean-v3.20-factorized-local-inventory-global-proposal-duel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one factorized local-inventory global proposal duel。
- 计分：step_exact=15/50；step_module_exact=10/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p50-clean-v3p20-factorized-local-inventory-global-proposal-duel-case50/prediction-audit.json`

### R192

luna-gaia-v3.51-clean-v3.20-replicated-global-causal-proposal-panel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.51-clean-v3.20-replicated-global-causal-proposal-panel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one replicated global causal proposal panel。
- 计分：step_exact=19/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p51-clean-v3p20-replicated-global-causal-proposal-panel-case50/prediction-audit.json`

### R193

luna-gaia-v3.52-clean-v3.20-module-factorized-local-census-proposal-panel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.52-clean-v3.20-module-factorized-local-census-proposal-panel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one module-factorized local-census proposal panel。
- 计分：step_exact=19/50；step_module_exact=14/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p52-clean-v3p20-module-factorized-local-census-proposal-panel-case50/prediction-audit.json`

### R194

luna-gaia-v3.54-clean-v3.20-step-isolated-paper-local-promotion-safe-system-evidence

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.54-clean-v3.20-step-isolated-paper-local-promotion-safe-system-evidence`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one step-isolated paper-local evidence matrix feeding one anchor-blind global challenger。
- 计分：step_exact=18/50；step_module_exact=9/50；all_correct=7/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p54-clean-v3p20-step-isolated-paper-local-promotion-safe-system-evidence-case50/prediction-audit.json`

### R195

luna-gaia-v3.56-clean-v3.20-step-isolated-class-stratified-anchor-selector-enumerated-contract

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.56-clean-v3.20-step-isolated-class-stratified-anchor-selector-enumerated-contract`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one step-isolated local evidence matrix feeding one anchor-aware class-stratified final selector with a fully enumerated contract。
- 计分：step_exact=22/50；step_module_exact=14/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p56-clean-v3p20-step-isolated-class-stratified-anchor-selector-enumerated-contract-case50/prediction-audit.json`

### R196

luna-gaia-v3.57-clean-v3.20-step-isolated-earliest-module-reservoir-anchor-selector

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.57-clean-v3.20-step-isolated-earliest-module-reservoir-anchor-selector`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one step-isolated local taxonomy matrix feeding a deterministic earliest-positive-per-module reservoir and one anchor-aware selector。
- 计分：step_exact=20/50；step_module_exact=11/50；all_correct=7/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p57-clean-v3p20-step-isolated-earliest-module-reservoir-anchor-selector-case50/prediction-audit.json`

### R197

luna-gaia-v3.59-clean-v3.20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.59-clean-v3.20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one clean-v3.20 step-isolated observed-continuation pairwise mechanism whose immutable bindings and reducer output are deterministically assembled from semantic-only assessments。
- 计分：step_exact=18/50；step_module_exact=12/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p59-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-deterministic-assembly-case50/prediction-audit.json`

### R198

luna-gaia-v3.60-clean-v3.20-retrospective-prefix-ledger-closure

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.60-clean-v3.20-retrospective-prefix-ledger-closure`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：retrospective closure over every pre-anchor row in the unchanged v3.20 sparse ledger, followed by deterministic earliest-qualifying reduction。
- 计分：step_exact=21/50；step_module_exact=13/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p60-clean-v3p20-retrospective-prefix-ledger-closure-case50/prediction-audit.json`

### R199

luna-gaia-v3.61-clean-v3.20-decision-time-evidence-maturity-census-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.61-clean-v3.20-decision-time-evidence-maturity-census-challenger`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one complete decision-time evidence-maturity census challenger。
- 计分：step_exact=20/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：audit_invalid。50条曾评分，但独立访问/写拓扑审计失败：output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/analysis/inference-access-write-audit.json
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p61-clean-v3p20-decision-time-evidence-maturity-census-challenger-case50/prediction-audit.json`

### R200

luna-gaia-v3.62-clean-v3.20-full-local-step-pairwise-reducer

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.62-clean-v3.20-full-local-step-pairwise-reducer`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one complete Step-isolated local matrix retained through a full anchor-versus-positive-Step pair table and deterministic earliest-winner reducer。
- 计分：step_exact=18/50；step_module_exact=11/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：audit_invalid。50条曾评分，但独立访问/写拓扑审计失败：output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/analysis/inference-access-write-audit.json
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p62-clean-v3p20-full-local-step-pairwise-reducer-case50/prediction-audit.json`

### R201

luna-gaia-v3.64-clean-v3.20-heterogeneous-critical-boundary-panel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.64-clean-v3.20-heterogeneous-critical-boundary-panel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one heterogeneous complete-boundary panel。
- 计分：step_exact=18/50；step_module_exact=10/50；all_correct=9/50；失败=0；逐例重算=True。
- 状态：audit_invalid。50条曾评分，但独立访问/写拓扑审计失败：output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/analysis/inference-access-write-audit.json
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p64-clean-v3p20-heterogeneous-critical-boundary-panel-case50/prediction-audit.json`

### R202

luna-gaia-v3.65-clean-v3.20-outcome-conditioned-global-boundary-proposal-duel

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.65-clean-v3.20-outcome-conditioned-global-boundary-proposal-duel`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one outcome-conditioned global boundary proposal duel。
- 计分：step_exact=19/50；step_module_exact=12/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：audit_invalid。50条曾评分，但独立访问/写拓扑审计失败：output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/analysis/inference-access-write-audit.json
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p65-clean-v3p20-outcome-conditioned-global-boundary-proposal-duel-case50/prediction-audit.json`

### R203

luna-gaia-v3.74-clean-v3.20-exact-predicate-acquisition-boundary-reducer-owner-materialized

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.74-clean-v3.20-exact-predicate-acquisition-boundary-reducer-owner-materialized`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one exact-predicate acquisition boundary reducer。
- 计分：step_exact=21/50；step_module_exact=12/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p74-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-materialized-case50/prediction-audit.json`

### R204

luna-gaia-v3.76-clean-v3.20-sparse-ledger-global-boundary-selector-runtime-repair

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.76-clean-v3.20-sparse-ledger-global-boundary-selector-runtime-repair`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：one sparse-ledger global critical-boundary selector。
- 计分：step_exact=21/50；step_module_exact=14/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p76-clean-v3p20-sparse-ledger-global-boundary-selector-runtime-repair-case50/prediction-audit.json`

### R205

luna-gaia-v3.78-clean-v3.20-factorized-sparse-ledger-pairwise-selector-contract-repair

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.78-clean-v3.20-factorized-sparse-ledger-pairwise-selector-contract-repair`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：factorize native sparse-ledger local facts from pairwise global selection。
- 计分：step_exact=22/50；step_module_exact=10/50；all_correct=5/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p78-clean-v3p20-factorized-sparse-ledger-pairwise-selector-contract-repair-case50/prediction-audit.json`

### R206

luna-gaia-v3.80-clean-v3.20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-luna；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.luna-gaia.v3.80-clean-v3.20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：outcome-conditioned exact-predicate handoff tournament over the native v3.20 ledger。
- 计分：step_exact=17/50；step_module_exact=8/50；all_correct=5/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p80-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-taxonomy-repair-case50/prediction-audit.json`

### R207

gaia-v3.82-clean-v3.20-model-only-terra-medium

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-terra；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.82-clean-v3.20-model-only-terra-medium`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：model only: gpt-5.6-luna to gpt-5.6-terra。
- 计分：step_exact=22/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-terra-gaia-paper-v1-agent-judge-gaia-v3p82-clean-v3p20-model-only-terra-medium-case50/prediction-audit.json`

### R208

gaia-v3.83-clean-v3.20-model-only-gpt55-medium

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。
- 父版本：`agentdebug.codex-agent-judge.luna-gaia-v3.20-packet-state-closure`。主要机制/拓扑：model only: gpt-5.6-luna to gpt-5.5。
- 计分：step_exact=26/50；step_module_exact=16/50；all_correct=13/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case50/prediction-audit.json`

### R209

gaia-v3.84-model-only-gpt54-medium

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.4；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.84-model-only-gpt54-medium`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：model only: gpt-5.5 to gpt-5.4。
- 计分：step_exact=23/50；step_module_exact=13/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.4-gaia-paper-v1-agent-judge-gaia-v3p84-model-only-gpt54-medium-case50/prediction-audit.json`

### R210

gaia-v3.85-gpt55-high-effort-only

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=high；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.85-gpt55-high-effort-only`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：reasoning effort only: medium to high。
- 计分：step_exact=23/50；step_module_exact=15/50；all_correct=12/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p85-gpt55-high-effort-only-case50/prediction-audit.json`

### R211

gaia-v3.86-gpt55-bounded-typed-boundary-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.86-gpt55-bounded-typed-boundary-challenger`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：one bounded typed-boundary later challenger。
- 计分：step_exact=24/50；step_module_exact=15/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p86-gpt55-bounded-typed-boundary-challenger-case50/prediction-audit.json`

### R212

gaia-v3.87-gpt55-evidence-lifecycle-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.87-gpt55-evidence-lifecycle-challenger`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：one evidence-grounded bidirectional error-lifecycle challenger。
- 计分：step_exact=18/50；step_module_exact=12/50；all_correct=11/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p87-gpt55-evidence-lifecycle-challenger-case50/prediction-audit.json`

### R213

gaia-v3.88-gpt55-sparse-influence-graph-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.88-gpt55-sparse-influence-graph-challenger`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：one sparse producer-consumer influence-graph challenger。
- 计分：step_exact=22/50；step_module_exact=14/50；all_correct=10/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p88-gpt55-sparse-influence-graph-challenger-case50/prediction-audit.json`

### R214

gaia-v3.89-gpt55-sol-heterogeneous-challenger

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：{"unchanged-v3p83-packet-state-anchor": {"model": "gpt-5.5", "reasoning_effort": "medium"}, "sol-v3p83-earliest-causal-challenger": {"model": "gpt-5.6-sol", "reasoning_effort": "medium"}, "unchanged-v3p83-default-keep-arbiter": {"model": "gpt-5.5", "reasoning_effort": "medium"}}。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.89-gpt55-sol-heterogeneous-challenger`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：challenger executor only: gpt-5.5 to gpt-5.6-sol。
- 计分：step_exact=26/50；step_module_exact=15/50；all_correct=12/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-heterogeneous-gaia-paper-v1-agent-judge-gaia-v3p89-gpt55-sol-heterogeneous-challenger-case50/prediction-audit.json`

### R215

gaia-v3.102-gpt55-three-attempt-access-validated-tournament

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=3；HTTP尝试上限=None；legacy max_retries=2；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.102-gpt55-three-attempt-access-validated-predicate-handoff-tournament`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：replace accepted v3.83 challenger/arbiter with one outcome-conditioned predicate-handoff tournament over every native v3.83 ledger Step。
- 计分：step_exact=21/50；step_module_exact=13/50；all_correct=8/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/scored/report.md` · inference-access-write-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/analysis/inference-access-write-audit.json` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p102-gpt55-three-attempt-access-validated-tournament-case50/prediction-audit.json`

### R216

gaia-v3.107-v3.83-codex-sdk-bounded-retry

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：Codex SDK/app-server；原 transport=Codex SDK/app-server。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：transport reliability only: within each fresh v3.83 SDK semantic attempt, bound provider request retries at 2 and SSE interruption retries at 2。
- 计分：step_exact=23/50；step_module_exact=18/50；all_correct=13/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/scored/report.md` · tuning-plan.json: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/tuning-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case50/prediction-audit.json`

### R217

gaia-v3.83-clean-v3.20-model-only-gpt55-medium

- 数据：agenterrorbench-release-200-composed-v1；N=200；环境={"alfworld": 100, "gaia": 50, "webshop": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：evaluation scope only: apply the frozen v3.83 protocol to all 150 released ALFWorld and WebShop cases。
- 计分：step_exact=59/200；step_module_exact=24/200；all_correct=16/170；失败=0；逐例重算=True。
- 状态：composed_report。旧GAIA50+新rest150的组合报告，不是新增200条独立推理
- 运行类型：composed_report；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/agenterrorbench200/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/agenterrorbench200/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/agenterrorbench200/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/prediction-audit.json`

### R218

gaia-v3.83-clean-v3.20-model-only-gpt55-medium

- 数据：agenterrorbench-paper-rest150-v1；N=150；环境={"alfworld": 100, "webshop": 50}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=None；legacy max_retries=1；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。
- 父版本：`agentdebug.codex-agent-judge.gaia-v3.83-clean-v3.20-model-only-gpt55-medium`。主要机制/拓扑：evaluation scope only: apply the frozen v3.83 protocol to all 150 released ALFWorld and WebShop cases。
- 计分：step_exact=33/150；step_module_exact=8/150；all_correct=3/120；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/rest150/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/rest150/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/scored/rest150/report.md` · tuning-plan.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/tuning-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-rest150-agent-judge-gaia-v3p83-clean-v3p20-model-only-gpt55-medium-case150/prediction-audit.json`

### R219

official-repo-topology-sdk-v3-native-taxonomy-bridge

- 数据：gaia-paper-v1；N=50；环境={"gaia": 50}。
- 方法族：Codex SDK；实际执行后端：Codex SDK/app-server；原 transport=Codex SDK/app-server。
- 模型：gpt-5.5；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=2；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.codex-agent-judge.gaia-official-repo-gpt55-codex-sdk-v3`。
- 父版本：`agentdebug.codex-agent-judge.gaia-official-repo-gpt55-codex-sdk-v1`。主要机制/拓扑：public_native_taxonomy_and_others_owner_bridge。
- 计分：step_exact=19/50；step_module_exact=9/50；all_correct=6/50；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/scored/metrics.json` · per_example.csv: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/scored/per_example.csv` · report.md: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/scored/report.md` · experiment-plan.json: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/experiment-plan.json` · run-result.json: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/run-result.json` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case50/prediction-audit.json`

### R220

codex-gpt-5.6-terra-smoke-v1-experiment-b-v1

- 数据：smoke-v1；N=30；环境={"alfworld": 10, "gaia": 10, "webshop": 10}。
- 方法族：Codex SDK；实际执行后端：host-orchestrated Codex agent/subagent；原 transport=Codex agent/subagent。
- 模型：gpt-5.6-terra；reasoning effort=medium；temperature=None。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`unknown`。
- 父版本：`None`。主要机制/拓扑：unknown。
- 计分：step_exact=7/30；step_module_exact=3/30；all_correct=2/27；失败=0；逐例重算=True。
- 状态：complete_scored。
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-codex-gpt-5.6-terra-smoke-v1-experiment-b-v1/metrics.json` · per-example.csv: `output/agenterrorbench-codex-gpt-5.6-terra-smoke-v1-experiment-b-v1/per-example.csv` · prediction-audit.json: `output/agenterrorbench-codex-gpt-5.6-terra-smoke-v1-experiment-b-v1/prediction-audit.json` · preregistration.json: `output/agenterrorbench-codex-gpt-5.6-terra-smoke-v1-experiment-b-v1/preregistration.json`

### R221

candidate-v3

- 数据：prior Step Exact error diagnostic subset; not GAIA-50 accuracy；N=8；环境={"gaia": 8}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-candidate-v3`。
- 父版本：`None`。主要机制/拓扑：agentdebug.llm-judge.gaia-official-repo-gpt4.1-candidate-v3。
- 计分：step_exact=2/8；step_module_exact=1/8；all_correct=1/8；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v1-agent-judge-candidate-v3-case8/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v1-agent-judge-candidate-v3-case8/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v1-agent-judge-candidate-v3-case8/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v1-agent-judge-candidate-v3-case8/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v1-agent-judge-candidate-v3-case8/prediction-audit.json`

### R222

serial-v4

- 数据：same prior Step Exact error diagnostic subset; not GAIA-50 accuracy；N=8；环境={"gaia": 8}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-serial-v4`。
- 父版本：`None`。主要机制/拓扑：fresh-step-locator-then-fresh-module-judge-then-fresh-error-type-judge。
- 计分：step_exact=3/8；step_module_exact=2/8；all_correct=1/8；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v2-agent-judge-serial-v4-case8/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v2-agent-judge-serial-v4-case8/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v2-agent-judge-serial-v4-case8/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v2-agent-judge-serial-v4-case8/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v2-agent-judge-serial-v4-case8/prediction-audit.json`

### R223

boundary-v5

- 数据：same prior Step Exact error diagnostic subset; not GAIA-50 accuracy；N=8；环境={"gaia": 8}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-boundary-v5`。
- 父版本：`None`。主要机制/拓扑：top3-step-proposer-then-boundary-reviewer-then-module-then-type。
- 计分：step_exact=2/8；step_module_exact=2/8；all_correct=1/8；失败=0；逐例重算=True。
- 状态：mutated_diagnostic。小样本/诊断；不代表完整GAIA-50；运行中修改validator，仅开发诊断
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v3-agent-judge-boundary-v5-case8/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v3-agent-judge-boundary-v5-case8/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v3-agent-judge-boundary-v5-case8/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v3-agent-judge-boundary-v5-case8/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v3-agent-judge-boundary-v5-case8/prediction-audit.json`

### R224

strict-v8

- 数据：same prior Step Exact error diagnostic subset; not GAIA-50 accuracy；N=8；环境={"gaia": 8}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=1；legacy max_retries=None；max_output_tokens=None；timeout=180.0。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-strict-v8`。
- 父版本：`None`。主要机制/拓扑：three-top2-specialists-top3-coverage-assessor-selector-module-type。
- 计分：step_exact=3/8；step_module_exact=2/8；all_correct=2/8；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v6-agent-judge-strict-v8-case8/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v6-agent-judge-strict-v8-case8/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v6-agent-judge-strict-v8-case8/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v6-agent-judge-strict-v8-case8/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v6-agent-judge-strict-v8-case8/prediction-audit.json`

### R225

atom-v12

- 数据：historically selected GAIA hard-8 diagnostic/tuning subset; not GAIA-50 accuracy and not unknown-data generalization；N=8；环境={"gaia": 8}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=not_applicable；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=1；legacy max_retries=None；max_output_tokens=None；timeout=180.0。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-atom-v12`。
- 父版本：`None`。主要机制/拓扑：three serialized semantic freezes per case: boundary atom/predicate, module owner on frozen boundary, then error type on frozen boundary and owner; each non-deterministic stage uses one fresh stateless Chat Completion whose model-visible request contains only the protocol task (never the local JSON Schema), and prediction is mechanically derived。
- 计分：step_exact=3/8；step_module_exact=1/8；all_correct=1/8；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v12-case8/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v12-case8/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v12-case8/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v12-case8/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v12-case8/prediction-audit.json`

### R226

atom-v13-backtrace

- 数据：historically selected GAIA hard-8 diagnostic/tuning subset; not GAIA-50 accuracy and not unknown-data generalization；N=8；环境={"gaia": 8}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=not_applicable；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=4；每阶段/实例语义尝试上限=2；HTTP尝试上限=1；legacy max_retries=None；max_output_tokens=None；timeout=180.0。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-atom-v13-backtrace`。
- 父版本：`None`。主要机制/拓扑：four serialized semantic freezes per case: locator chooses a local atom, backtrace chooses the earliest sufficient root from the frozen radius-bounded pool, module chooses an owner on that frozen root, and type chooses a taxonomy label on the frozen root and owner; each non-deterministic stage uses one fresh stateless Chat Completion whose model-visible request contains only the protocol task (never the local JSON Schema), and prediction is mechanically derived。
- 计分：step_exact=3/8；step_module_exact=1/8；all_correct=1/8；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v13-backtrace-case8/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v13-backtrace-case8/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v13-backtrace-case8/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v13-backtrace-case8/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v13-backtrace-case8/prediction-audit.json`

### R227

official-repo-canonical-v2

- 数据：gold-informed structural diagnostic subset; not GAIA-50 accuracy；N=10；环境={"gaia": 10}。
- 方法族：LLM API；实际执行后端：LLM API；原 transport=LLM API。
- 模型：gpt-4.1；reasoning effort=None；temperature=0.0。
- 分阶段模型/effort：无单独记录；见统一配置。
- 并发=None；每阶段/实例语义尝试上限=None；HTTP尝试上限=None；legacy max_retries=None；max_output_tokens=None；timeout=None。
- 协议：`agentdebug.llm-judge.gaia-official-repo-gpt4.1-canonical-v2`。
- 父版本：`None`。主要机制/拓扑：agentdebug.llm-judge.gaia-official-repo-gpt4.1-canonical-v2。
- 计分：step_exact=9/10；step_module_exact=3/10；all_correct=1/10；失败=0；逐例重算=True。
- 状态：complete_scored。小样本/诊断；不代表完整GAIA-50
- 运行类型：scored_run；不是所有表格行都代表一次独立全流程模型运行。
- 来源：metrics.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-structural-gate-v1-agent-judge-official-repo-canonical-v2-case10/scored/metrics.json` · per_example.csv: `output/agenterrorbench-sophnet-gpt-4.1-gaia-structural-gate-v1-agent-judge-official-repo-canonical-v2-case10/scored/per_example.csv` · experiment-plan.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-structural-gate-v1-agent-judge-official-repo-canonical-v2-case10/experiment-plan.json` · run-result.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-structural-gate-v1-agent-judge-official-repo-canonical-v2-case10/run-result.json` · prediction-audit.json: `output/agenterrorbench-sophnet-gpt-4.1-gaia-structural-gate-v1-agent-judge-official-repo-canonical-v2-case10/prediction-audit.json`

## 无正式分数的目录（完整性清单）

目录存在不等于新增实验：本清单可能包括准备目录、拼写错误目录或中断执行。仅显示有计划/执行摘要的目录，绝不补造分数。

| 目录 | 状态 | merged预测数 |
|---|---|---:|
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p100-gpt55-short-bound-access-audited-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p100-gpt55-short-bound-access-audited-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p101-gpt55-stage-local-access-validated-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p101-gpt55-stage-local-access-validated-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p103-gpt55-native-initial-probe-veto-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p103-gpt55-native-initial-probe-veto-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p90-gpt55-outcome-conditioned-predicate-handoff-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p90-gpt55-outcome-conditioned-predicate-handoff-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p91-gpt55-file-inspected-predicate-handoff-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p91-gpt55-file-inspected-predicate-handoff-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p92-gpt55-singleton-safe-file-inspected-predicate-handoff-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p92-gpt55-singleton-safe-file-inspected-predicate-handoff-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p93-gpt55-audited-no-bwrap-predicate-handoff-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p93-gpt55-audited-no-bwrap-predicate-handoff-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p94-gpt55-response-only-audited-no-bwrap-predicate-handoff-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p94-gpt55-response-only-audited-no-bwrap-predicate-handoff-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p95-gpt55-dual-stage-response-only-audited-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p95-gpt55-dual-stage-response-only-audited-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p96-gpt55-normalized-access-audited-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p96-gpt55-normalized-access-audited-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p97-gpt55-python3-bounded-access-audited-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p97-gpt55-python3-bounded-access-audited-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p98-gpt55-stage-bounded-access-audited-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p98-gpt55-stage-bounded-access-audited-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p99-gpt55-cwd-robust-access-audited-tournament-case50: `output/agenterrorbench-codex-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p99-gpt55-cwd-robust-access-audited-tournament-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v1-case50: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v1-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v2-phase2-resample-case50: `output/agenterrorbench-codex-gpt-5.5-medium-gaia-paper-v1-agent-judge-official-repo-topology-sdk-v2-phase2-resample-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.5-medium-official-v3-transport-recovery64-case64: `output/agenterrorbench-codex-gpt-5.5-medium-official-v3-transport-recovery64-case64` | no_frozen_score | 64 |
| agenterrorbench-codex-gpt-5.5-medium-rest150-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case150: `output/agenterrorbench-codex-gpt-5.5-medium-rest150-agent-judge-official-repo-topology-sdk-v3-native-taxonomy-bridge-case150` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p45-clean-v3p20-anchor-preserving-independent-typed-challenger-panel-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p45-clean-v3p20-anchor-preserving-independent-typed-challenger-panel-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p46-clean-v3p20-module-complete-local-error-profile-causal-promotion-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p46-clean-v3p20-module-complete-local-error-profile-causal-promotion-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p53-clean-v3p20-step-isolated-paper-local-global-challenger-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p53-clean-v3p20-step-isolated-paper-local-global-challenger-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p55-clean-v3p20-step-isolated-class-stratified-anchor-selector-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p55-clean-v3p20-step-isolated-class-stratified-anchor-selector-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p58-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-reducer-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p58-clean-v3p20-step-isolated-module-reservoir-pairwise-observed-continuation-reducer-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p63-clean-v3p20-heterogeneous-critical-boundary-panel-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p63-clean-v3p20-heterogeneous-critical-boundary-panel-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p66-clean-v3p20-exact-predicate-acquisition-boundary-reducer-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p66-clean-v3p20-exact-predicate-acquisition-boundary-reducer-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p67-clean-v3p20-exact-predicate-acquisition-boundary-reducer-read-only-input-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p67-clean-v3p20-exact-predicate-acquisition-boundary-reducer-read-only-input-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p68-clean-v3p20-exact-predicate-acquisition-boundary-reducer-compact-embedded-input-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p68-clean-v3p20-exact-predicate-acquisition-boundary-reducer-compact-embedded-input-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p69-clean-v3p20-exact-predicate-acquisition-boundary-reducer-runtime-integrated-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p69-clean-v3p20-exact-predicate-acquisition-boundary-reducer-runtime-integrated-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p70-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-explicit-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p70-clean-v3p20-exact-predicate-acquisition-boundary-reducer-owner-explicit-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p71-clean-v3p20-exact-predicate-acquisition-boundary-reducer-evidence-materialized-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p71-clean-v3p20-exact-predicate-acquisition-boundary-reducer-evidence-materialized-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p72-clean-v3p20-exact-predicate-acquisition-boundary-reducer-binding-materialized-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p72-clean-v3p20-exact-predicate-acquisition-boundary-reducer-binding-materialized-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p73-clean-v3p20-exact-predicate-acquisition-boundary-reducer-auditor-corrected-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p73-clean-v3p20-exact-predicate-acquisition-boundary-reducer-auditor-corrected-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p75-clean-v3p20-sparse-ledger-global-boundary-selector-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p75-clean-v3p20-sparse-ledger-global-boundary-selector-case50` | no_frozen_score | 50 |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p77-clean-v3p20-factorized-sparse-ledger-pairwise-selector-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p77-clean-v3p20-factorized-sparse-ledger-pairwise-selector-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p79-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-case50: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-paper-v1-agent-judge-luna-gaia-v3p79-clean-v3p20-outcome-conditioned-predicate-handoff-tournament-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2-case30: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v2-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5-case30: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p5-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7-case30: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-gaia-v3p7-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-v3-baseline-case30: `output/agenterrorbench-codex-gpt-5.6-luna-gaia-smoke-v1-agent-judge-luna-v3-baseline-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-case30: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-clean-debate-v4-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v1` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v13-unified-v1-case30: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v13-unified-v1-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v1-case30: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v15-unified-v1-case30` | no_frozen_score | 30 |
| agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v1-case30: `output/agenterrorbench-codex-gpt-5.6-luna-tuning-v1-agent-judge-luna-v3-serial-v1-case30` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-sol-gaia-paper-v1-agent-judge-gaia-v3p81-clean-v3p20-model-only-sol-medium-case50: `output/agenterrorbench-codex-gpt-5.6-sol-gaia-paper-v1-agent-judge-gaia-v3p81-clean-v3p20-model-only-sol-medium-case50` | no_frozen_score | — |
| agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-specialist-critic-v1-case50: `output/agenterrorbench-codex-gpt-5.6-sol-high-gaia-paper-v1-agent-judge-specialist-critic-v1-case50` | invalid-exhausted-retries-not-scored | — |
| agenterrorbench-codex-sol-luna-gaia-paper-v1-agent-judge-serial-v1-case50: `output/agenterrorbench-codex-sol-luna-gaia-paper-v1-agent-judge-serial-v1-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8-paper50-v1-case50: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8-paper50-v1-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p1-paper50-v1-case50: `output/agenterrorbench-sophnet-gpt-4.1-gaia-paper-v1-agent-judge-strict-v8p1-paper50-v1-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v4-agent-judge-multiscout-v6-case8: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v4-agent-judge-multiscout-v6-case8` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v5-agent-judge-coverage-v7-case8: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v5-agent-judge-coverage-v7-case8` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v7-agent-judge-causal-v9-case8: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v7-agent-judge-causal-v9-case8` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v8-agent-judge-causal-v10-case8: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v8-agent-judge-causal-v10-case8` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v11-case8: `output/agenterrorbench-sophnet-gpt-4.1-gaia-step-error-gate-v9-agent-judge-atom-v11-case8` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p104-v3p83-codex-sdk-transport-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p104-v3p83-codex-sdk-transport-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p106-v3p83-responses-api-transport-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p106-v3p83-responses-api-transport-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p108-v3p83-responses-validator-closure-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p108-v3p83-responses-validator-closure-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p109-v3p83-responses-expanded-validator-closure-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p109-v3p83-responses-expanded-validator-closure-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p110-v3p83-responses-decision-locked-exact-copy-closure-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p110-v3p83-responses-decision-locked-exact-copy-closure-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p111-v3p83-responses-locked-stage-legality-closure-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p111-v3p83-responses-locked-stage-legality-closure-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50-replicate-02: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50-replicate-02` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50-superseded-dual-reachability-hardening: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50-superseded-dual-reachability-hardening` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50-superseded-verifier-hardening: `output/agenterrorbench-sophnet-gpt-5.5-gaia-paper-v1-agent-judge-gaia-v3p112-v3p83-responses-validated-semantic-core-closure-case50-superseded-verifier-hardening` | no_frozen_score | — |
| agenterrorbench-sophnet-gpt-5.5-rest150-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case150: `output/agenterrorbench-sophnet-gpt-5.5-rest150-agent-judge-gaia-v3p107-v3p83-codex-sdk-bounded-retry-case150` | no_frozen_score | — |
