# 从研究仓库到 RSI 任务：设计与未决项

## 任务形态

优化对象是**失败轨迹诊断算法/agent harness**，不是 GAIA 问题求解器，也不是改底层模型权重。
范围先固定到 AgentErrorBench 的 GAIA；历史 WebShop/ALFWorld 结果继续公开作为研究记录，
不拿来填本任务隐藏集。它们不是相同分布，也没有与 GAIA-50 可比的评分分母。

保持 GPT-5.5/medium 的 Codex SDK 方法族为首选，使用 Official SDK v3 作为可运行 starter
的来源，v3.83 作为家族内最强历史方法候选，v3.107 作为已执行的 app-server 较强参考候选。
依 [统一口径](../../results/method-family-policy.md)，v3.83 的宿主子 agent 执行也归入 SDK
方法族，但 26/50 并非 app-server 移植后实测值；统一分类不替代移植验证。
需要先统一 taxonomy/owner 合同，确认没有额外提示、工具权限和重试差异破坏可比性。
这些适配与最终 runtime 都可能改变结果，所以现有数字只作历史证据。

## 模型与网络：已核对到的例外

用户提供的表单明确写无网络，但截至 2026-09-05 的公开
[DiscoveryWorld task.toml](https://huggingface.co/datasets/RSI-Exam/RSI-Exam/blob/main/discoveryworld_agent_harness_low2/task.toml)
为 agent/verifier 设置模型域名 allowlist，
[LoCoMo instruction](https://huggingface.co/datasets/RSI-Exam/RSI-Exam/blob/main/locomo_longterm_memory/instruction.md)
要求经固定模型代理调用，参赛代码拿不到真实密钥。这说明“只能完全本地 LLM”或“禁止 SDK”
都不是可以直接推出的结论，但不等于我们的 SDK 方案已获批。

首选提交给主办方确认的方案：可信服务运行 pinned GPT-5.5/medium SDK，向可修改的方法
仅暴露 `llm_call`；服务固定 model、effort、上下文规则、工具禁用策略、预算和可用 endpoint。
这是拟议的最小接口，不是声称当前 v3.83/v3.107 原样可通过它运行。二者的文件读写、验证与
多轮执行必须在统一规则下适配；如果单轮接口损失关键能力，需主办方批准受限的阶段执行接口。
不得为保留较高历史分数而给某个方法额外工具、隐藏信息或不同预算。
真实认证不传入参赛容器。参赛代码只能修改诊断程序；不能通过请求参数改模型、增加工具，
或访问宿主文件系统。服务用 fresh session，按协议记录每次调用和重试。

[OpenAI authentication 文档](https://learn.chatgpt.com/docs/auth) 说明 Codex 可用 ChatGPT
或 API 认证，但这不构成可离线执行 GPT-5.5 的保证。本地历史 transport 代码实际访问
远端服务。若主办方不允许上述受控通道，再由项目所有者决定是否另建固定本地模型任务；
不能无提示换模型并沿用当前 anchors。固定提示的 completion cache 也不能支持任意新提示。

## 必须成立的隔离关系

```text
公开研究仓库（全部历史方法、分数和图像）
  └─ 作者人工审核的最小导出 → agent 镜像
       starter + 可见轨迹 + visible self-check + 受控模型接口
       │ 只提交方法代码
       ▼
     独立评分镜像 → 重新运行代码 → 可信合法性检查 → sealed Step Exact
       隐藏轨迹与 labels         ▲
                              可信固定模型服务（若获准）
```

不能 `COPY . /app`。整个 `output/`、历史预测、最佳版本、全部实验报告、原始 labels、
gold 标注 sidecar、`.git` 历史和开发机器身份均不进入 agent 镜像。
当前公共研究 registry 会导入全部历史协议，因此也不能直接把它的完整依赖闭包导出给
参赛 agent。正式 kit 需要独立的最小 starter 适配器/registry，其余代码只留给作者或
可信服务；否则即使没有复制 `solution/`，仍可能把较强方法一并送入 agent 镜像。
评分时也不能把隐藏 labels 与 submitted code 放在同一可读文件系统中；可信控制器只向
受限子进程发送单个 gold-free 输入，输出先冻结，再在不同权限域中评分。
同一个 Python 进程内禁用 `open()`、检查路径或做 monkeypatch 不是安全边界。

隐藏集不仅要新 trajectory ID，还必须与可见集和全部历史报告按底层任务隔离；
按源模型前缀分割不能解决同题泄漏。新的数据规模、采集许可和同分布证据尚未确定。

## 已实现的准备工具及它们没有证明什么

`scripts/rsi_exam/contracts.py` 提供固定分母 Step Exact 的可测试纯函数原型，检查 ID、
整数 step、taxonomy、literal owner evidence 和缺失/失败零分；提供 split ID/来源任务/
内容哈希重叠检查和结构性 label-field 检查。`audit_split` CLI 不输出隐藏 ID。
它们**不执行不可信代码、不提供沙箱，也尚未将现有 JudgeView 完整适配到原型投影**。
因此这些测试通过不等于旧 baseline 在正式任务中已获得同样分数。

`check_readiness --require-ready` 阻止缺证据状态被写成正式可运行任务。通过门禁需要
每项人工/自动审查的 hash-bound 公开摘要；隐藏内容本身不进入这些摘要。
官方 normalization 交给 authoring kit，并用最终 baseline/reference 重测值填充。
没有在本地擅自发明 `task.toml` 字段、运行时通道或归一化公式。

## 按依赖顺序完成

1. 用 [逐字段 proposal](proposal.md) 和 [审稿附件](attachments/README.md) 请求主办方确认
   受控 GPT-5.5 SDK 接入，以及处理后数据的可接受分发方式。
2. 获得许可并补齐未暴露、同分布的新数据；冻结 source-task 分组、近重复审核和标注规则。
3. 用正式 kit 建立两个最小镜像、可信模型服务、可修改方法接口和不可修改的 grader。
4. 在相同 runtime、数据、taxonomy、预算下跑 starter/reference；公开原始 raw 指标，
   仅用新的 sealed calibration 设置 anchors；starter 原样提交须归一化到 0。
5. 空输出、固定 step、最后一步、答案表、标签读取、跨案例状态、超预算/重试等攻击测试。
6. 实测两次以上完整 evaluation 与一次固定模型 scratch 优化探测；保存每次真实不同的
   改动、完整可见集分数与成本。达标后再过正式 automated checks 和人工审查。

总体流程参考 [任务指南](https://rsi-exam.ai/guidelines.html)。这份仓库整理完成工程准备，
不能代替数据方授权、主办方批准或真实隐藏集实验。
