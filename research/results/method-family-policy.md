# 统一结果口径：LLM API 与 Codex SDK 方法族

生效日期：2026-09-06。适用于本仓库的 README、结果表、图像、复现说明和 RSI 提案。

本项目对外采用两个**方法族**：

| `method_family` | 包含的实际执行方式 | `execution_backend` / 原 `transport` |
|---|---|---|
| LLM API | 直接 Chat Completions / Responses 请求及我们自己编排的诊断流程 | LLM API / Responses API |
| Codex SDK | SDK/app-server 执行，以及历史宿主 Codex agent/subagent 编排 | 两种后端分开保留 |

“Codex SDK”在此是项目定义的 umbrella method family，不是对每一次运行所用客户端包的断言。
[OpenAI 官方文档](https://learn.chatgpt.com/docs/codex-sdk)将 SDK 定义为程序化控制 Codex agents；
这支持把相关方法放在同一研究家族，不证明宿主历史运行调用过 SDK 包，也不证明两种环境等价。

所有结果展示应使用“Codex SDK 方法族”，首次出现时注明包含宿主 agent/subagent。
需要更精确时写“Codex SDK 方法族 · 宿主子 agent”或“Codex SDK 方法族 · app-server 0.147.0”。
`transport`、运行目录、实验 ID、历史协议名称与冻结日志不改名；`execution_backend`
保留实际执行事实。原文中的 Codex agent/subagent 应理解为这个家族内的执行子类，
不是第三个互斥方法族。冻结的历史实验正文按当时用语保留，以免破坏证据绑定。

## 这次统一不改变什么

- 不创造新实验，不增加有效运行总数，不修改预测、指标、分母、时间、模型或审计结论。
- 不把 API 客户端库、OpenAI Agents SDK 或外层负责修改代码的 Codex 自动归入内层 Codex 方法族。
- 不把 Luna、Sol、混合模型或 xhigh 运行说成 GPT-5.5/medium。
- 不把阶段重放说成 fresh 运行；不把组合报告、无评分目录或审计无效运行计入有效实验。
- 不因同属一个方法族而合并不同后端、版本、案例集合、输出合同或预算的固定配置曲线。
- 不把可见集观察值当成统计显著提升、外部 SOTA 或 RSI 隐藏集校准值。

有效记录要求 `csv_verified=true`、`eligible=true` 且状态为 `complete_scored`
或 `scored_failures_zero`。后者保留失败案例并按零分计入完整分母。记录数以运行×方法计算；
实验次数另按 `run_dir` 去重。阶段重放可以是有效计分，但必须单列其非 fresh 身份。

最新汇总与每个精确案例集的两类计数见 [方法族实验次数](method-family-counts.md)。
本次计数基于 2026-09-05 的已审阅 227 条档案；后续新产物只进入
[待审阅增量清单](experiment-history-2026-09-05/post-archive-inventory.json)，不自动增加有效计数。
实现入口为 `scripts/reproduction/result_taxonomy.py`；单元测试禁止将分类扩展误写成新推理。

## 关键结果的统一说法

v3.83 是 Codex SDK 方法族中历史接受的 GAIA-50 Step 最优版本：GPT-5.5/medium，
26/50；实际由宿主子 agent 执行。v3.107 是同一方法族的 app-server 移植，23/50；
Official SDK v3 是官方拓扑的 app-server 对照，19/50。
后两者不是前者的重复测量，也不能按分数大小改写真实时间顺序。

该规则使已有宿主实验成为 SDK 方法族的完整历史证据，而不替代未来统一运行时下的复现。
