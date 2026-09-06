# 提交人使用指南

这份材料可以用于 **task proposal 评审**，不能标记为已完成的 RSI 任务。
尚未向 Airtable 提交；源码发布地址为
[DuffyCoder/AgentDebug](https://github.com/DuffyCoder/AgentDebug)。公开源码不等于提交或验收任务。

## 填写顺序

1. 个人姓名、联系方式、机构等身份字段由提交人填写，不从机器账户名推断。
2. 标题建议：Improving causal failure localization in agent trajectories。
3. 将 [proposal.md](proposal.md) 中相应标题下的英文复制到 2.3–5.2 字段。
   开头的作者备注和 reporting convention 可放附件，不必单独寻找表单字段。
4. 5.1 已填写本项目仓库地址；提交时附上实际审阅的 commit。上游仓库不包含本地工作，
   不能把它当成我们的发布地址。当前 ZIP 只有评审材料，不能替代完整代码。
5. 5.2 上传 [附件 ZIP](attachments/agentdebug-rsi-proposal-evidence.zip)。若只能少量上传，
   优先选择实验说明、固定模型曲线和指标/隔离说明；详情见 [附件清单](attachments/README.md)。
6. 仓库数据及摘录的分发权限已由维护者确认。正式 benchmark 的授权条款归档、
   新隐藏数据与 model access 仍需按实际证据填写；不能据此把任务标记为已完成。

## 这次任务形态的选择

- 数据限定为 AgentErrorBench 处理后的 GAIA 失败轨迹，优化错误定位，不做 GAIA 问答。
- 内层固定 GPT-5.5/medium；外层优化 agent 的模型和调用方式不属于被评测方法的固定模型。
- 对外使用 Codex SDK **方法族**，包括宿主子 agent 与 SDK/app-server；附件保留实际后端。
- starter 候选为 Official SDK v3，历史可见集 19/50。
- 最优历史方法候选为 v3.83，26/50（宿主后端）；已执行的 app-server 较强候选为
  v3.107，23/50。迁移到统一服务和合法性合同后必须重新测量，不能保证保留原分数。
- 不将 99 次混合模型/数据集运行宣称为 99 次固定 GPT-5.5 实验，不将 19→23→26
  说成真实时间序列。7 次 GPT-5.5/medium fresh GAIA-50 运行已全部列入附件。

## 表单中的“none”和数字

3.1 提供实测可见集 baseline 候选 0.38，明确 sealed baseline/reference 仍为 none。
外部 SOTA 为 none；0.52 是本地观察最好值，不是官方 SOTA。
1.0 是准确率的数学上界，不是标签必然可达的经验结论。归一化参数等待正式 kit 校准。

3.2 如表单只允许 Yes/No，外部 SOTA 的回答选 **No**，在补充文字中说明本地候选已运行、
官方论文分数未复现。不能因为拥有本地 0.52 就回答已复现论文 SOTA。

4.1 选择 CPU 类别仅适用于“任务容器 + 经批准的外部固定模型服务”；不表示 GPT-5.5
可以在无网络 CPU 上推理。若选项不允许解释，先询问主办方，不选虚构 GPU 型号。
4.2 本设计无容器内 GPU；4.3 CPU/RAM 未实测，不拿并发数冒充硬件要求。

## 向主办方确认的三个问题

1. 是否允许由可信、凭据隔离的固定 GPT-5.5/medium 服务支撑该任务？最终接口是否可以
   包含受限的多轮阶段执行，还是只能是普通 llm_call？公开 allowlist/proxy 先例不是本任务许可。
2. 能否先按提案评审，再协调新增、同分布、独立封存的 GAIA 失败轨迹？当前隐藏集为零，
   已见 50 条不能重新切分后宣称未见。新增数据的许可范围与采集/标注资源仍待确认。
3. 是否接受以本地可重算的 starter/reference 候选进入构建，再按正式运行时重做校准？
   官方论文结果没有在本地复现，附录对此明确披露。

## 本地核验

```bash
make verify
make test-public
make research-check
make -f research/Makefile rsi-ready
```

前三项分别核验公开入口、框架测试、研究结果与准备材料；最后一项目前应失败，因为 8 个构建就绪条件仍开放。
这个预期失败不影响提出诚实的任务建议，但阻止把草稿包装成已通过验收的任务。
