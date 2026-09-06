# AgentDebug 使用与接口

公开版本只有一种诊断方法，统一称为 **AgentDebug**。固定 GPT-5.5、medium
推理强度，使用“时间顺序锚点 → 单一后续挑战 → 保守仲裁”。CLI、Python API
和复现说明均对应同一组冻结提示词及校验器。

## 输入边界

诊断输入是 AgentErrorBench 处理后的 GAIA 轨迹生成的 gold-free prediction
manifest，以及匹配的有序 cohort。它不直接接受原始 GAIA 问答数据、答案标签，
也不把通用 OpenClaw 轨迹诊断当作已经验证的能力。

`CanonicalTrace`、来源文件导入与完整性检查仍保留为独立的数据工具。
这些工具没有第二套语义诊断器作为默认或回退路径。

## 诊断流程

1. 按时间顺序检查 Memory/Reflection 状态忠实性、硬约束与执行条件、策略重复与
   终止放弃，记录候选账本；冻结最早符合条件的步骤，然后确定模块、类型和证据。
2. 独立会话最多提出一个更晚的因果挑战；必须证明修复锚点仍无法消除该后续错误。
   没有合格挑战或证据不确定时保留锚点。
3. 仲裁默认保留锚点，仅在挑战成立时选择挑战者。最终预测必须逐字段复制其中一个，
   不允许新造第三个预测、混合输出或改写语义。

每例三个新会话，不是三次裸 API 调用。合法性检查覆盖顺序、步骤冻结、taxonomy、
字面证据、输入身份和最终精确复制；它们不等于证明模型的因果判断正确。

## Python API

```python
from agentdebug import analyze

plan = analyze(
    prediction_manifest="output/gaia-inputs/prediction-manifest.json",
    cohort_manifest="benchmarks/cohorts/gaia-paper-v1.json",
    output_dir="output/python-plan",
)
assert plan["status"] == "prepared"  # 不调用模型

result = analyze(
    prediction_manifest="output/gaia-inputs/prediction-manifest.json",
    cohort_manifest="benchmarks/cohorts/gaia-paper-v1.json",
    output_dir="output/python-live",  # 必须是新目录
    execute=True,                    # 明确授权启动模型会话
)
```

`agentdebug.diagnostics.analyze` 和 `agentdebug.method.analyze` 指向同一方法。
旧的 `analyze(trace, judge=...)` 调用契约已退役，不会静默调用旧算法。

单独检查完整预测包：

```python
from agentdebug.method import validate_predictions

audit = validate_predictions(
    prediction_manifest="output/gaia-inputs/prediction-manifest.json",
    cohort_manifest="benchmarks/cohorts/gaia-paper-v1.json",
    predictions="output/python-live/predictions.json",
)
```

需要保留预测旁的锚点、账本、checkpoint、challenger、arbiter 等伴随文件；
只有最终预测文件不足以完成验证。

## 执行与测试接口

`agentdebug.method.StageRequest` 给执行器提供阶段名称、新工作目录、冻结任务文本
和产物路径。`CodexExecutor` 是默认独立 CLI 适配器。单元测试可传入
`executor(request)` 写出模拟产物；父进程仍运行真实冻结校验器。
自定义执行器必须遵守固定模型、每阶段独立会话和数据边界，不能把它的结果冒充为
已测后端的结果。

默认最多并发四例、每阶段两次尝试；失败尝试保存在独立目录中。输入或锚点被修改
会导致运行失败，不允许在被修改的输入上继续重试。任一案例失败时不会发布部分
成功的总分。

## 结果与安全

公开观察是 50 条已暴露开发轨迹上的 Step 26/50、Step+Module 16/50、
All Correct 13/50，来自历史 host 编排执行。当前独立执行适配器没有新的准确率
测量；模型版本和运行条件变化可能影响复跑结果。

`run.json` 使用中性方法名称；完整实现身份保留在 `provenance.json` 和审计产物。
统一公开名称不会改写既有实验记录。

模型进程仍可读取沙箱允许的宿主文件。gold-free 输入与提示词禁令不等于 OS 级
隐藏数据隔离；正式隔离环境需要单独部署。敏感轨迹必须先做隐私审查。

参考：[快速开始](getting-started.md)、[命令参考](reference/cli.md)、
[复现指南](../REPRODUCING.md)、[研究档案](../research/README.md)。
