# 按统一方法族统计有效实验

由公开结果档案自动生成；口径见 [方法族政策](method-family-policy.md)。没有新增模型推理。

总计 209 次有效运行 / 214 条运行×方法记录。
LLM API：110 次 / 115 条；Codex SDK 方法族：99 次 / 99 条。

每行使用数据身份与精确案例集合指纹，而不是仅按样本数合并。API 单个运行可能同时评测 direct / two_stage。
共 16 个案例集合，按已记录数据身份分为 17 层；未知身份不默认相同。
宿主子 agent 已归入 SDK 方法族，后两列仅解释实际执行来源，不是额外实验。

| 数据范围 | N | 数据身份前8位 | 案例集指纹前8位 | LLM API 次数 | SDK 方法族次数 | 其中 app-server | 其中宿主子 agent |
|---|---:|---|---|---:|---:|---:|---:|
| Full / 200 | 200 | fa78de42 | 84d2ecd2 | 2 | 0 | 0 | 0 |
| Full / 150 | 150 | fa78de42 | 92070149 | 0 | 1 | 0 | 1 |
| GAIA-50 | 50 | fa78de42 | ffd8b7d9 | 2 | 67 | 2 | 65 |
| GAIA-smoke-30 | 30 | fa78de42 | 500a41b7 | 0 | 14 | 0 | 14 |
| Mixed-30 / smoke-v1 | 30 | fa78de42 | a54247a7 | 2 | 0 | 0 | 0 |
| Mixed-30 / smoke-v1 | 30 | 未记录 | a54247a7 | 0 | 1 | 0 | 1 |
| Mixed-30 / tuning-v1 | 30 | fa78de42 | 0defb39f | 18 | 15 | 0 | 15 |
| Small diagnostics / 10 | 10 | 未记录 | 28a3480e | 1 | 0 | 0 | 0 |
| Small diagnostics / 9 | 9 | fa78de42 | ba7f8e60 | 0 | 1 | 0 | 1 |
| Small diagnostics / 8 | 8 | 未记录 | 70d15690 | 5 | 0 | 0 | 0 |
| Small diagnostics / 5 | 5 | fa78de42 | 01c397cc | 2 | 0 | 0 | 0 |
| Small diagnostics / 3 | 3 | fa78de42 | 8068c52e | 12 | 0 | 0 | 0 |
| Small diagnostics / 3 | 3 | fa78de42 | b9b30e84 | 58 | 0 | 0 | 0 |
| Small diagnostics / 1 | 1 | fa78de42 | 6c4b4bf6 | 1 | 0 | 0 | 0 |
| Small diagnostics / 1 | 1 | fa78de42 | 6ea4a9b3 | 1 | 0 | 0 | 0 |
| Small diagnostics / 1 | 1 | fa78de42 | 7380b457 | 3 | 0 | 0 | 0 |
| Small diagnostics / 1 | 1 | fa78de42 | dc8189fa | 3 | 0 | 0 | 0 |

## 对固定模型 RSI 证据的限制

SDK 方法族 GAIA-50 有 67 次有效运行，其中 3 次阶段重放；64 次记录为 fresh。
所有阶段均为 GPT-5.5 的 fresh GAIA-50 运行有 9 次；再固定 medium 后有 7 次。
其中只有 R208/R211/R212/R213 属于同一已记录三阶段宿主配置。未知宿主版本并未因此补齐。

有效计分允许失败按零计入完整分母；有效不等于每条输出合法、不等于独立研究思路、
也不等于所有阶段都重新推理。API 历史存在冻结上游复用，不能由通用 fresh 标记推出全部 fresh。
组合报告、审计否决/保留、历史先验输出与修改 validator 的诊断不计入上述有效总数。

[JSON](method-family-counts.json) / [CSV](method-family-counts.csv) 保留完整指纹和记录数。
[研究档案](../../research/README.md) 统一收录 RSI 附件、固定模型证据与全部家族运行。
