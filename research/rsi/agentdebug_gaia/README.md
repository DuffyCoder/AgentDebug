# AgentDebug GAIA — RSI-Exam proposal package

状态：**提案草稿 + 本地准备工具；不是已验收的 RSI 任务**。
不要将本目录或整个研究仓库直接作为 agent 容器构建上下文。

| 文件 | 用途 | 谁能看到 |
|---|---|---|
| [proposal.md](proposal.md) | 对应 Airtable 字段的英文草稿 | 作者 / 审稿者 |
| [submission-guide.zh-CN.md](submission-guide.zh-CN.md) | 填写顺序、中文解释和未决项 | 提交人 |
| [attachments/README.md](attachments/README.md) | 必要附件、图像、机器可读证据和 ZIP | 作者 / 审稿者；不进 agent 镜像 |
| [instruction.md](instruction.md) | 任务说明草稿，无论文/SOTA/历史答案 | 未来参赛 agent；仍待运行接口确认 |
| [design.md](design.md) | 任务边界、模型接口、数据隔离与封装方案 | 作者 / 审稿者 |
| [readiness.json](readiness.json) | 8 项就绪门禁和未填的隐藏集 anchors | 作者 / CI |
| [environment/README.md](environment/README.md) | 未来 agent 镜像的最小允许内容 | 构建人员 |
| [tests/README.md](tests/README.md) | 未来可信评分镜像的要求 | 构建人员 |
| [solution/README.md](solution/README.md) | 较强参考方法的来源 | 作者 / 校准人员 |

```bash
make -f research/Makefile rsi-check  # 结构有效即可成功，同时显示所有尚未解决的条件
make -f research/Makefile rsi-ready  # 正式任务门禁；当前应以非零状态退出
```

目前可分享给主办方评估的问题是：能否以固定 GPT-5.5 的受控 SDK 推理服务承载一个
失败根因定位方法优化任务？历史 starter 候选 19/50，app-server 较强候选 23/50，SDK
方法族最优历史版本 26/50（宿主子 agent）。它们都是已暴露 GAIA-50 上的观察，不是隐藏集锚点。

需要先解决：处理后数据和摘录的分发权限、同分布且与历史开发材料隔离的隐藏实例、
受控推理服务政策。然后才移植 baseline/reference、在最终环境做校准和难度测试。
不应先凭空填写隐藏集大小、GPU 型号、SOTA 或主办方专有配置。

[官方流程](https://rsi-exam.ai/contribute.html) 允许先交提案，经审查后取得 authoring kit。
所以这里不捏造一个看似正式可用的 `task.toml` 或空 Dockerfile。
没有向 Airtable 提交，也没有上传原始数据或创建外部发布。
