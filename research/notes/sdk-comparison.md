# GPT-5.5 Codex SDK 方法族对照复现

这是固定模型的横向方法比较，不是跨 provider 排名，也不是已完成的 RSI 隐藏集评估。
按照 [统一口径](../results/method-family-policy.md)，三项都属于 Codex SDK 方法族，
但其实际执行后端不同。方法族共有多少有效历史实验见 [分类计数](../results/method-family-counts.md)。

| Profile | 历史记录 | Step / Step+Module / All | 解释 |
|---|---|---|---|
| `official-sdk-v3` | R219，2026-09-03 | 19 / 9 / 6，分母均 50 | 官方拓扑 + native taxonomy/others owner bridge |
| `sdk-v3p107` | R216，2026-08-31 | 23 / 18 / 13，分母均 50 | v3.83 三阶段语义的 SDK bounded-retry 移植 |
| `best-historical-v3p83` | R208 | 26 / 16 / 13，分母均 50 | SDK 方法族 · 宿主子 agent；不是上述 app-server 运行 |

四个复现入口、原配置和源证据定位符见
[reproduction-index.json](../results/accounting/reproduction-index.json)。
两个 app-server 运行均固定 `gpt-5.5`、`medium`、`openai-codex==0.147.0`。
v3.83 的原宿主版本未记录；现有 CLI 复现适配器不构成历史 SDK 包调用的证明。
Provider 不用于筛掉任何历史结果，但认证、端点、上下文和 transport 配置仍是复现所需信息。
不得把模型别名解释成已有精确 backend snapshot 证明。

## 1. 无模型费用的结果核验

```bash
uv sync --frozen --extra dev
uv run python -m research.tools.research_release verify
```

该步骤复核已保存逐例计分的汇总，不重新执行 SDK、不下载原始轨迹。
SDK 版本的完整预测与逐阶段原始日志仍在本地 `output/`，没有在这次整理中复制其正文。

## 2. 准备同一套输入与可选 SDK 依赖

以下第 2、3 节是历史方法的复现说明，必须先按
[归档恢复指南](../archive/README.md) 恢复源码，在恢复目录中建立独立环境后执行。
这里的原始脚本名、依赖文件名和配置只在恢复后的树中存在；它们不是当前框架的入口。

依照 [主复现指南](../../REPRODUCING.md) 获取经过授权的 AgentErrorBench，重建并验证
`gaia-paper-v1` 的 50 个完整 gold-free JudgeView。

```bash
uv pip install -r requirements-v3p83-transports.txt
```

SDK 依赖独立于历史 `uv.lock`，以保持 v3.83 已冻结的 lock 哈希。
这不是 `uv sync --frozen` 已包含 SDK 的声明。再次运行同步可能移除这些可选包，应按上述顺序安装。

Official SDK v3 还需要未改动的上游 detector：

```bash
git clone https://github.com/ulab-uiuc/AgentDebug.git data/upstream-agentdebug
git -C data/upstream-agentdebug switch --detach 7740fe3a5c4822b2143cbde78ecfffeace0bb166
```

这只用于新建的上游参考副本；不要对当前研究仓库执行该切换。
已存在的目录应先核验身份，不覆盖。运行器会检查上游源码哈希。

## 3. 准备新的运行目录，不覆盖历史结果

下面不带 `--execute`，只生成计划/准备输入，不调用模型。上游路径显式给出，避免历史脚本的临时目录默认值。

```bash
source .venv/bin/activate
python -m scripts.run_agent_judge_gaia_official_repo_gpt55_codex_sdk_v3_paper50 \
  --official-repo data/upstream-agentdebug \
  --run-dir output/reproduction-official-sdk-v3 \
  --max-concurrency 4

python -m scripts.run_agent_judge_gaia_v3_107_v3p83_codex_sdk_bounded_retry_gpt55_medium_paper50 \
  --run-dir output/reproduction-sdk-v3p107 \
  --case-input-root output/reproduction-sdk-v3p107-inputs \
  --max-workers 4 --max-attempts 2
```

在已激活项目 `.venv` 中执行 `python`（例如先 `source .venv/bin/activate`），防止再次同步移除 SDK。
需要新推理时，确认账户可用、额度和输入后，在相同命令追加 `--execute`。
Official SDK 使用自己的 Codex 认证源，v3.107 历史配置读取 `SOPHNET_API_KEY`。
不要把密钥写入配置文件、报告、共享日志或提交；也不要为隐藏 provider 差异悄悄改动冻结 runner。

本次整理验证了配置、代码导入、测试和冻结计分，没有用付费模型重新跑这两次实验。
真正的新推理输出可能受服务变动和随机性影响；保留独立 run ID 和全部尝试记录。

## 4. 比较时锁定什么

锁定完整案例集合、模型与 effort、gold-free 输入、taxonomy/owner 投影、语义重试和
transport 重试上限；运行完后先验证与冻结预测，再打开标签。所有失败保留在完整分母，
不得拼接别的运行来补成一次 fresh 成绩。

Official SDK v3 的 native taxonomy bridge 与 v3.107 的严格协议并不完全相同。
因此这两个本地数字是候选方法证据，最终 RSI 对照还要在统一可信输出合同下重新标定。
API、SDK、模型 alias 和 backend 不是可以互换的标签。

历史 Official SDK v3：3,252 次成功调用（3,202 Phase 1 + 50 Phase 2），
记录的总流程 wall time 为 8,398.8245 秒，约 2.33 小时；总 tokens 为 52,224,583。
v3.107：150 个成功阶段，总 tokens 为 55,954,260。少调用不等于更少 tokens；
这里不由调用数推算价格，也不把 imported-prediction 的评分耗时当成模型耗时。
目标容器的 CPU、RAM、服务限流和 12 小时实验轮数仍需实测。
