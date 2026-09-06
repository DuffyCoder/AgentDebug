"""Reconstruct the local experiment archive without rerunning any model.

Outputs are derived tables and figures; original experiment artifacts are read-only.
Run only in a disposable source tree: python -m research.tools.reconstruct_history
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))
from research.tools.result_taxonomy import classification

DEST = ROOT / "research/results/experiment-history-2026-09-05"
ARCHIVE_THROUGH = "2026-09-05"
METRIC_NAMES = ("step_exact", "step_module_exact", "all_correct")
CONFIG_KEYS = {
    "experiment", "agent_judge_version", "protocol", "semantic_protocol", "semantic_parent",
    "direct_semantic_parent", "semantic_topology", "topology", "single_major_change",
    "sole_mechanism_change", "phase1_topology", "phase2_topology", "model", "models",
    "model_by_stage", "stage_models", "model_by_role", "reasoning_effort", "temperature",
    "provider", "endpoint", "transport", "transport_policy_version", "session_topology",
    "execution", "execution_topology", "max_workers", "max_concurrency", "workers",
    "max_attempts", "max_attempts_per_case", "max_attempts_per_stage", "max_retries",
    "max_http_attempts", "max_http_attempts_per_fresh_call", "max_semantic_attempts_per_stage",
    "max_phase2_semantic_attempts", "max_output_tokens", "timeout", "timeout_seconds",
    "prompt_versions", "selection", "sdk_version", "bundled_cli_version", "case_count",
    "scope", "gold_free_inference", "incumbent_or_prior_predictions_visible",
    "prior_predictions_visible", "acceptance", "goal_completion", "selection_metric",
    "official_repository_commit", "calls_per_case_before_retry", "model_calls_per_case_before_semantic_repair",
    "calls_per_case_before_semantic_repair", "experiment_role", "expected_phase1_call_count",
    "expected_phase2_call_count", "retry_policy", "transport_retry_policy",
    "topology_description", "serial_stages_per_case", "planned_session_count", "provider_config",
    "judge", "llm", "model_config", "stage_model_config", "pipeline_version", "prompt_protocol_version",
}


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def small_config(obj):
    if not isinstance(obj, dict):
        return {}
    return {k: v for k, v in obj.items() if k in CONFIG_KEYS}


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from flatten(v, f"{prefix}.{i}")
    else:
        yield prefix, obj


def first(configs, *keys):
    for c in configs:
        for k in keys:
            if k in c and c[k] is not None:
                return c[k]
    return None


def short_name(root, method):
    s = root.name.removeprefix("agenterrorbench-")
    if "agent-judge-" in s:
        s = s.split("agent-judge-", 1)[1]
    else:
        s = re.sub(r"^(?:deepseek-v4-(?:flash|pro)|gpt-4[.](?:1|o)|gemini-3.1)-", "", s)
    s = re.sub(r"-case\d+$", "", s)
    s = re.sub(r"v(\d+)p(\d+)(?:p(\d+))?", lambda m: "v" + ".".join(x for x in m.groups() if x), s)
    return s + (" / " + method if method in ("direct", "two_stage") else "")


def clock_text(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    except (ValueError, AttributeError):
        return ""


def classify(row, plan, result, audit):
    """Separate mathematical scoring validity from experimental eligibility."""
    name = row["run_dir"]
    notes = []
    status = "complete_scored" if row["failed_outputs"] == 0 else "scored_failures_zero"
    eligible = True
    if row["n"] <= 10:
        notes.append("小样本/诊断；不代表完整GAIA-50")
    m = re.search(r"tuning-v1-agent-judge-luna-v(\d+)-case30", name)
    if m and int(m.group(1)) in (7, 8, 9, 10, 11, 12):
        status, eligible = "historical_prior_prediction", False
        notes.append("读取同case历史预测；不满足后续统一fresh/no-prior边界")
    if "luna-v12-standalone" in name:
        status, eligible = "audit_qualified", False
        notes.append("输出计分有效；独立审计发现allowlist及写入边界缺口")
    independent = ROOT / name / "analysis/inference-access-write-audit.json"
    if independent.exists() and read_json(independent).get("independent_access_write_audit_passed") is False:
        status, eligible = "audit_invalid", False
        notes.append("50条曾评分，但独立访问/写拓扑审计失败："+str(independent.relative_to(ROOT)))
    if "agent-judge-boundary-v5-case8" in name:
        status, eligible = "mutated_diagnostic", False
        notes.append("运行中修改validator，仅开发诊断")
    if "/scored/agenterrorbench200/" in row["metrics_path"]:
        status = "composed_report"
        notes.append("旧GAIA50+新rest150的组合报告，不是新增200条独立推理")
    if any(str(k).startswith("inherited-") for k in row.get("stage_models", {})):
        notes.append("继承历史冻结中间结果的阶段重放；不能视作全流程fresh推理")
        row["fresh_end_to_end"] = False
    else:
        row["fresh_end_to_end"] = eligible and status != "composed_report"
    if not row["csv_verified"] and row["csv_verified"] is not None:
        status, eligible = "score_mismatch", False
        notes.append("逐例重算与metrics不一致，须查证")
    # Structural validity is checked separately from benchmark accuracy.
    if audit.get("forbidden_read_occurred") is True:
        status, eligible = "audit_invalid", False
        notes.append("prediction audit报告越界读取")
    if row["failed_outputs"]:
        notes.append("失败输出保留在完整计分分母并按零分计；不是删掉失败后的成功子集")
    if result.get("status") in ("failed", "failed_before_freeze"):
        status, eligible = "audit_invalid", False
        notes.append("run-result失败，与评分文件存在性分开记录")
    row.update(status=status, eligible=eligible, notes="；".join(notes))


def extract(metrics_path):
    data = read_json(metrics_path)
    run = data.get("run", {})
    root = ROOT / Path(*metrics_path.relative_to(ROOT).parts[:2])
    sources = {f: read_json(root / f) for f in ("experiment-plan.json", "tuning-plan.json", "run-result.json", "prediction-audit.json", "preregistration.json", "predict-run.json", "repair-predict-run.json")}
    result, audit = sources["run-result.json"], sources["prediction-audit.json"]
    plan = sources["experiment-plan.json"] or sources["tuning-plan.json"] or sources["preregistration.json"]
    configs = [plan, result.get("plan", {}), result, run, sources["predict-run.json"], sources["repair-predict-run.json"]]
    configs += [v for c in configs for k,v in c.items() if k in ("provider_config","judge","llm","model_config") and isinstance(v,dict)]
    topo = first(configs, "session_topology", "execution_topology", "execution") or {}
    if isinstance(topo, dict):
        configs.insert(0, topo)
    configs = [c for c in configs if isinstance(c, dict)]
    methods = data.get("metrics", {}).get("by_method", {})
    custom = not bool(methods)
    if custom:
        if "step_exact" in data:
            current = data
        else:
            current_key = next(k for k in data if isinstance(data[k], dict) and "step_exact" in data[k] and "same_cases" not in k)
            current = data[current_key]
        n = data["case_count"]
        overall = {"trajectory_count": n, "failed_prediction_count": 0}
        for key in METRIC_NAMES:
            overall[key] = {"correct": current[key], "denominator": data.get("all_correct_denominator", n) if key == "all_correct" else n}
        methods = {"agent_judge": {"overall": overall}}
    csv_path = metrics_path.with_name("per_example.csv")
    if not csv_path.exists() and metrics_path.with_name("per-example.csv").exists():
        csv_path = metrics_path.with_name("per-example.csv")
    csv_rows = list(csv.DictReader(csv_path.open())) if csv_path.exists() else []
    output = []
    for method, info in methods.items():
        overall = info["overall"]
        selection = run.get("selection", {})
        row = dict(run_dir=str(root.relative_to(ROOT)), metrics_path=str(metrics_path.relative_to(ROOT)),
                   metrics_sha256=digest(metrics_path), name=short_name(root, method), method=method,
                   n=overall["step_exact"]["denominator"], failed_outputs=overall.get("failed_prediction_count", 0),
                   model=first(configs, "model") or data.get("model", "unknown"),
                   reasoning_effort=first(configs, "reasoning_effort"), temperature=first(configs, "temperature"),
                   stage_models=first(configs, "stage_models", "model_by_stage", "model_by_role") or {},
                   provider=first(configs, "provider"), endpoint=first(configs, "endpoint"),
                   workers=first(configs, "max_workers", "max_concurrency", "workers"),
                   max_output_tokens=first(configs, "max_output_tokens"),
                   max_semantic_attempts=first(configs, "max_attempts_per_stage", "max_semantic_attempts_per_stage", "max_attempts_per_case", "max_attempts"),
                   max_http_attempts=first(configs, "max_http_attempts", "max_http_attempts_per_fresh_call"),
                   legacy_max_retries=run.get("max_retries"),
                   timeout_seconds=first(configs, "timeout_seconds", "timeout"),
                   protocol=first(configs, "agent_judge_version", "protocol") or run.get("prompt_versions", {}).get(method, "unknown"),
                   semantic_parent=first(configs, "semantic_parent", "direct_semantic_parent"),
                   mechanism=first(configs, "single_major_change", "sole_mechanism_change", "semantic_topology", "topology", "topology_description") or "",
                   cohort=selection.get("cohort_name") or selection.get("cohort") or first(configs, "cohort") or data.get("scope", "selection-specific"),
                   cohort_sha256=selection.get("cohort_sha256", ""), dataset_sha256=data.get("dataset", {}).get("dataset_sha256", ""),
                   recorded_at=clock_text(run.get("started_at")), date_source="metrics.run.started_at (API run / imported-prediction scoring start)",
                   scoring_or_api_seconds=run.get("duration_seconds"), csv_verified=None,
                   config_sources={k:small_config(v) for k,v in sources.items() if v},
                   scoring_config=small_config(run), environment_metrics={})
        transport = first(configs, "transport") or run.get("transport_policy_version", "")
        if "sdk" in root.name:
            row["transport"] = "Codex SDK/app-server"
        elif "codex" in str(transport).lower() or run.get("endpoint") == "orchestrator" or "codex_agent"==method:
            row["transport"] = "Codex agent/subagent"
        else:
            row["transport"] = "Responses API" if "responses" in str(row["endpoint"]) else "LLM API"
        row.update(classification(row["transport"]))
        for key in METRIC_NAMES:
            row[key] = overall[key]["correct"]
            row[key + "_denominator"] = overall[key]["denominator"]
            row[key + "_pct"] = 100 * row[key] / row[key + "_denominator"] if row[key + "_denominator"] else None
        if csv_rows:
            selected = [r for r in csv_rows if r.get("method", method) == method]
            row["csv_verified"] = len(selected) == row["n"] and all(sum(r.get(k, "").lower() == "true" for r in selected) == row[k] for k in METRIC_NAMES)
            all_den = sum(r.get('all_correct','').lower() in ('true','false') for r in selected)
            row["csv_verified"] = row["csv_verified"] and all_den == row['all_correct_denominator']
            row["case_set_sha256"] = hashlib.sha256("\n".join(sorted(r["trajectory_id"] for r in selected)).encode()).hexdigest()
            row["per_example_sha256"] = digest(csv_path)
            row["case_count_csv"] = len(selected)
            for item in selected:
                item.setdefault("environment", "gaia" if "gaia" in root.name else "unknown")
            row["environment_counts"] = dict(Counter(r["environment"] for r in selected))
            # Exact fractions remain in the archive for comparisons on a fixed environment.
            for env in row["environment_counts"]:
                subset = [r for r in selected if r["environment"] == env]
                row["environment_metrics"][env] = {k:sum(r.get(k, "").lower() == "true" for r in subset) for k in METRIC_NAMES} | {"n":len(subset)}
        else:
            row["case_set_sha256"] = ""
            row["environment_counts"] = {"gaia":row["n"]} if "gaia" in root.name else {}
        if not row["recorded_at"]:
            times = [(k,v) for k,v in flatten(sources) if isinstance(v,str) and re.search(r"(started|finished|created|frozen|timestamp|completed)(_at|_utc)?$", k) and clock_text(v)]
            if times:
                key,val=sorted(times,key=lambda x:x[1])[0]
                row["recorded_at"], row["date_source"] = clock_text(val), key
        if row['cohort']=='selection-specific' and row['case_set_sha256']=='':
            row['notes']='无cohort身份；不可直接跨运行比较'
        if 'terra-smoke-v1-experiment-b-v1' in root.name:
            row['cohort']='smoke-v1'
        if not row["mechanism"]:
            row["mechanism"] = " / ".join(str(first(configs,k)) for k in ("phase1_topology", "phase2_topology") if first(configs,k)) or row["protocol"]
        if row["n"] == 50 and row["environment_counts"] == {"gaia":50}:
            row["group"] = "GAIA-50"
        elif row["n"] == 30 and row["environment_counts"] == {"gaia":30}:
            row["group"] = "GAIA-smoke-30"
        elif row["n"] == 30:
            row["group"] = "Mixed-30 / " + str(row["cohort"])
        elif row["n"] in (150,200):
            row["group"] = "Full / " + str(row["n"])
        else:
            row["group"] = "Small diagnostics / " + str(row["n"])
        row["evidence_files"] = [str(p.relative_to(ROOT)) for p in [metrics_path,csv_path,metrics_path.with_name("report.md"),root/'analysis/inference-access-write-audit.json',*[root/f for f in sources]] if p.exists()]
        classify(row, plan, result, audit)
        row['run_kind'] = 'scored_run'
        if any(str(k).startswith('inherited-') for k in row['stage_models']):
            row['run_kind'] = 'stage_replay'
        elif 'strict-revalidation' in root.name:
            row['run_kind'] = 'revalidation'
        elif '-e5d-' in root.name:
            row['run_kind'] = 'evidence_only_repair'
        elif any(s in root.name for s in ('-recovered-', '-recovery-')):
            row['run_kind'] = 'recovered_run'
        elif row['status']=='composed_report':
            row['run_kind'] = 'composed_report'
        output.append(row)
    return output


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fields);writer.writeheader()
        for r in rows:
            writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})


def inventory_unscored(all_paths, scored_roots):
    grouped=defaultdict(list)
    for p in all_paths:
        if len(p.parts)>=3 and p.parts[0]=="output" and p.parts[1].startswith("agenterrorbench-"):
            grouped[str(Path(*p.parts[:2]))].append(p)
    result=[]
    for name,files in sorted(grouped.items()):
        if name in scored_roots: continue
        root=ROOT/name
        evidence=[p for p in files if p.name in ("run-result.json","execution-summary.json","experiment-plan.json","tuning-plan.json") and len(p.parts)==3]
        if not evidence:continue
        run=read_json(root/"run-result.json")
        preds=root/"predictions.json"
        if not preds.exists(): count=None
        else:
            d=read_json(preds);count=len(d) if isinstance(d,list) else len(d.get("predictions",[]))
        result.append(dict(run_dir=name,status=run.get("status","no_frozen_score"),merged_prediction_count=count,evidence=[str(p) for p in evidence],reason="未找到本轮正式metrics；不补算、不把部分输出当正式结果"))
    return result


def md_escape(x):
    return str(x if x is not None else "—").replace("|","/").replace("\n"," ")


def link(path,label):
    # Raw runs are deliberately not distributed. A relative-looking hyperlink
    # would still be broken for a fresh clone, so keep a resolvable local path
    # as provenance, not as a claimed repository-contained attachment.
    return f"{label}: `{path}`"


def portable(value):
    """Sanitize derived exports only; never rewrite the frozen source runs."""
    if isinstance(value, dict):
        return {k: portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    if isinstance(value, str):
        return value.replace(str(ROOT.resolve()), "${REPO_ROOT}")
    return value


def render_report(rows, unscored):
    counts=Counter(r["status"] for r in rows)
    lines=["# AgentDebug 全量实验结果档案", "", "档案截止：2026-09-05；2026-09-06 更新方法族分类。范围：已审阅的冻结档案；后续产物单列待审阅。原实验文件未修改，未调用模型重跑。", "",
           f"发现 {len(set(r['metrics_path'] for r in rows))} 份 metrics，展开为 {len(rows)} 个运行×方法结果；另有 {len(unscored)} 个带计划/执行记录但无正式 metrics 的目录。", "",
           "## 口径与可复核性", "",
           "- 对外方法族统一为 LLM API / Codex SDK；后者包含宿主 Codex agent/subagent。method_family 是报告分类，execution_backend 与 transport 保留实际执行来源，不把宿主运行改写为 SDK 包调用。见 [统一口径](../method-family-policy.md)。",
           "- 每一次运行、每一种方法独立列出；dry3、dry5、hard8、structural10、mixed30、GAIA30、GAIA50、全200以及rest150均保留。不同cohort不能连成一条准确率曲线。",
           "- 早期API评分允许失败/非法输出按零分保留在固定分母；这类评分有效，但不等于全量输出合法。后期fail-closed流程需完整审计通过才允许评分。",
           "- `complete_scored`：全量成功且有评分；`scored_failures_zero`：完整分母计分且包含失败；`historical_prior_prediction`、`audit_invalid`、`audit_qualified`、`mutated_diagnostic`单列，不进入合规趋势图。状态是档案证据分类，不代表重跑全部历史validator。",
           "- `composed_report`：组合旧GAIA50和新rest150的汇总，不当成新增200次推理。",
           "- 时间统一转北京时间；多数Codex报告的started_at是冻结后评分开始时间，不能当作推理开始时间。无法确认的日期明确留空，不以文件mtime猜测。",
           "- All Correct逐行保留原分母；mixed30常为25，不能写成30。GAIA50保留全部50条发布标签，包括一个源轨迹映射异常实例。",
           "- 配置优先取实际运行目录的plan/run-result，再用metrics补充；provider保留为 provenance，不按provider筛选。未知值留空。",
           "- API报告duration可能包含推理，Codex imported-prediction评分duration通常只是评分耗时。本档案不混用它们绘制成本曲线。",
           "- 每行metrics中的三项正确数均与可用per_example.csv重算比对；原始配置来源、数据指纹与逐例文件hash保存在JSON/CSV中。",
           "- output/ 原始文件不随代码发布；下列路径是本地证据定位符。公开逐例计分账本和离线核验入口见 ../README.md。${REPO_ROOT} 表示克隆后的仓库根目录。",
           "", "状态统计：`"+json.dumps(counts,ensure_ascii=False)+"`", "",
           "## 全部已记录结果（按数据范围分组）", ""]
    for group in dict.fromkeys(r["group"] for r in rows):
        lines += ["### "+group,"", "| ID | 记录时间（北京） | 版本 / 方法 | 方法族 | 模型；effort / T | Step | Step+Module | All | 失败 | 状态 | 配置 / 原报告 |", "|---|---|---|---|---|---:|---:|---:|---:|---|---|"]
        for r in rows:
            if r["group"] != group:continue
            fractions=[f"{r[k]}/{r[k+'_denominator']}" for k in METRIC_NAMES]
            model=f"{r['model']}；{r['reasoning_effort'] or '—'} / {r['temperature'] if r['temperature'] is not None else '—'}"
            model_set={v.get('model') for v in r['stage_models'].values() if isinstance(v,dict)}
            if len(model_set)>1:
                model=' + '.join(sorted(model_set))+'（分阶段，见配置）'
            lines.append("| "+" | ".join(map(md_escape,[r['id'],r['recorded_at'][:16].replace('T',' ') or '未知',r['name'],r['method_family'],model,*fractions,r['failed_outputs'],r['status']]))+f" | [配置](#{r['id'].lower()}) / "+link(r['metrics_path'],'metrics')+" |")
        lines.append("")
    lines += ["## 每次运行的配置与证据", ""]
    for r in rows:
        lines += ["### "+r['id'], "", f"{r['name']}", "",
                  f"- 数据：{r['cohort']}；N={r['n']}；环境={json.dumps(r['environment_counts'],ensure_ascii=False)}。",
                  f"- 方法族：{r['method_family']}；实际执行后端：{r['execution_backend']}；原 transport={r['transport']}。",
                  f"- 模型：{r['model']}；reasoning effort={r['reasoning_effort']}；temperature={r['temperature']}。",
                  f"- 分阶段模型/effort：{json.dumps(r['stage_models'],ensure_ascii=False) if r['stage_models'] else '无单独记录；见统一配置'}。",
                  f"- 并发={r['workers']}；每阶段/实例语义尝试上限={r['max_semantic_attempts']}；HTTP尝试上限={r['max_http_attempts']}；legacy max_retries={r['legacy_max_retries']}；max_output_tokens={r['max_output_tokens']}；timeout={r['timeout_seconds']}。",
                  f"- 协议：`{r['protocol']}`。",
                  f"- 父版本：`{r['semantic_parent']}`。主要机制/拓扑：{r['mechanism']}。",
                  f"- 计分："+"；".join(f"{k}={r[k]}/{r[k+'_denominator']}" for k in METRIC_NAMES)+f"；失败={r['failed_outputs']}；逐例重算={r['csv_verified']}。",
                  f"- 状态：{r['status']}。{r['notes']}",
                  f"- 运行类型：{r['run_kind']}；不是所有表格行都代表一次独立全流程模型运行。",
                  "- 来源："+" · ".join(link(p,Path(p).name) for p in r['evidence_files']), ""]
    lines += ["## 无正式分数的目录（完整性清单）", "", "目录存在不等于新增实验：本清单可能包括准备目录、拼写错误目录或中断执行。仅显示有计划/执行摘要的目录，绝不补造分数。", "", "| 目录 | 状态 | merged预测数 |", "|---|---|---:|"]
    for u in unscored:
        lines.append(f"| {link(u['run_dir'],Path(u['run_dir']).name)} | {md_escape(u['status'])} | {md_escape(u['merged_prediction_count'])} |")
    (DEST/"full-history.md").write_text("\n".join(lines)+"\n")
    chronological=["# 逐次实验结果与配置总表", "", "按可确认的结果记录时间排序；日期未知的记录在末尾。ID与完整档案、CSV和图像一致。这里包含全部已保存评分，不省略被拒绝或失败计零的记录；请同时阅读状态列。", "",
                   "模型混合运行用分阶段配置表示；T/effort、并发和重试的原始记录见每行配置链接。All的原始分母逐行保留。", "",
                   "方法族使用 [统一报告口径](../method-family-policy.md)：Codex SDK 包含宿主子 agent；实际执行层仍分列。", "",
                   "| ID | 时间（北京） | 数据范围 | 版本/机制标识 | 模型 | T / effort | 方法族 | 实际执行层 | 并发 | Step | Step+Module | All | 失败 | 状态 | 配置 |",
                   "|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|"]
    for r in rows:
        model_set={v.get('model') for v in r['stage_models'].values() if isinstance(v,dict) and v.get('model')}
        model=' + '.join(sorted(model_set)) if len(model_set)>1 else r['model']
        columns=[r['id'],r['recorded_at'][:16].replace('T',' ') or '未知',r['group'],r['name'],model,
                 f"{r['temperature'] if r['temperature'] is not None else '—'} / {r['reasoning_effort'] or '—'}"+('（分阶段）' if len(model_set)>1 else ''),r['method_family'],r['execution_backend'],r['workers'],
                 *[f"{r[k]}/{r[k+'_denominator']}" for k in METRIC_NAMES],r['failed_outputs'],r['status']]
        chronological.append('| '+' | '.join(map(md_escape,columns))+f" | [配置与证据](full-history.md#{r['id'].lower()}) |")
    (DEST/'chronological-table.md').write_text('\n'.join(chronological)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--no-plots",action="store_true");args=parser.parse_args()
    all_paths=[Path(p) for p in subprocess.check_output(["rg","--files","--no-ignore","output"],cwd=ROOT,text=True).splitlines()]
    metric_paths=sorted(ROOT/p for p in all_paths if p.name=="metrics.json" and len(p.parts)<=6)
    if not metric_paths:
        raise RuntimeError("No private metrics found; use research_release verify for a public clone")
    discovered=portable([r for p in metric_paths for r in extract(p)])
    # This is a dated, already reviewed publication snapshot. Later runs need
    # their own review; do not silently shift stable R IDs or count new scores
    # merely because another task produced output while this report rebuilt.
    later = [r for r in discovered if r['recorded_at'] and r['recorded_at'][:10] > ARCHIVE_THROUGH]
    rows = [r for r in discovered if r not in later]
    rows.sort(key=lambda r:(r['recorded_at'] or '9999',r['run_dir'],r['method']))
    for i,r in enumerate(rows,1):r['id']=f"R{i:03d}"
    unscored=inventory_unscored(all_paths,{r['run_dir'] for r in discovered})
    # A public clone or partial local archive must not overwrite the complete
    # published ledger with an empty/truncated reconstruction.
    previous = read_json(DEST / "all-results.json")
    missing = {r['metrics_path'] for r in previous
               if not r['recorded_at'] or r['recorded_at'][:10] <= ARCHIVE_THROUGH} - {r['metrics_path'] for r in rows}
    if missing:
        raise RuntimeError(f"Private archive is incomplete: {len(missing)} previously recorded metric files missing")
    assert all(r['csv_verified'] is True for r in rows), 'A recorded score failed independent per-example verification'
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/"all-results.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n")
    write_csv(DEST/"all-results.csv",rows)
    write_csv(DEST/"eligible-results.csv",[r for r in rows if r['eligible'] and r['status']!='composed_report'])
    write_csv(DEST/"complete-valid-results.csv",[r for r in rows if r['eligible'] and r['status']=='complete_scored'])
    write_csv(DEST/"unscored-inventory.csv",unscored)
    (DEST/'post-archive-inventory.json').write_text(json.dumps({
        "archive_through": ARCHIVE_THROUGH,
        "status": "outside_reviewed_snapshot_not_counted_as_valid_experiments",
        "records": [{k: r[k] for k in ('run_dir', 'metrics_path', 'metrics_sha256', 'recorded_at', 'n')}
                    for r in later],
        "note": "New records require execution/provenance/recovery review; this list makes no validity or freshness claim."
    },ensure_ascii=False,indent=2)+'\n')
    render_report(rows,unscored)
    summary={"metric_files":len({r['metrics_path'] for r in rows}),"rows":len(rows),"statuses":Counter(r['status'] for r in rows),"groups":Counter(r['group'] for r in rows),"csv_verification":Counter(str(r['csv_verified']) for r in rows),"unknown_dates":[r['id']+': '+r['name'] for r in rows if not r['recorded_at']],"unscored_directories":len(unscored),"archive_through":ARCHIVE_THROUGH,"post_archive_records_pending_review":len(later)}
    (DEST/'verification-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    assert all(r['csv_verified'] is True for r in rows), 'A recorded score failed independent per-example verification'
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if not args.no_plots:
        plot(rows)


def plot(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,"axes.spines.right":False,"figure.facecolor":"#f8fafc","axes.facecolor":"#f8fafc","savefig.facecolor":"#f8fafc"})
    palettes={"step_exact":"#2563eb","step_module_exact":"#0d9488","all_correct":"#d97706"}
    display={"step_exact":"Step Exact","step_module_exact":"Step + Module","all_correct":"All Correct"}
    panels=[("Initial full-release reproductions (200)",[r for r in rows if r['group']=='Full / 200' and r['status']!='composed_report']),
            ("Mixed tuning-v1 (30)",[r for r in rows if r['group']=='Mixed-30 / tuning-v1' and r['eligible']]),
            ("GAIA-smoke-30",[r for r in rows if r['group']=='GAIA-smoke-30' and r['eligible']]),
            ("GAIA-50",[r for r in rows if r['group']=='GAIA-50' and r['eligible']])]
    fig,axes=plt.subplots(4,1,figsize=(19,19),gridspec_kw={"height_ratios":[.8,1.2,1,1.4]},layout="constrained")
    for ax,(title,group) in zip(axes,panels):
        x=np.arange(len(group))
        for key in METRIC_NAMES:
            ax.plot(x,[r[key+'_pct'] for r in group],marker='o',markersize=4,lw=1.1,color=palettes[key],label=display[key])
        best=np.maximum.accumulate([r['step_exact_pct'] for r in group])
        ax.step(x,best,where='post',color='#1e293b',lw=1.6,ls='--',label='Observed best Step (not a causal lineage)')
        labels=[r['id'] for r in group]
        if title.startswith('Initial'):
            labels=[r['id']+' '+r['model']+' / '+r['method'] for r in group]
        ax.set_xticks(x,labels,rotation=90 if len(group)>8 else 0,fontsize=8)
        ax.set_title(f"{title}  |  {len(group)} scored run-method records",loc='left',fontweight='bold',pad=12)
        ax.set_ylabel('Exact accuracy (%)');ax.set_ylim(-2,70);ax.grid(axis='y',alpha=.18)
        for j,r in enumerate(group):
            if r['failed_outputs']:
                ax.scatter(j,r['step_exact_pct'],marker='x',color='#dc2626',s=40,zorder=5)
        if ax is axes[0]:ax.legend(loc='upper left',ncol=4,fontsize=9)
    fig.suptitle('AgentDebug: complete result history on the four principal evaluation scopes',fontsize=19,fontweight='bold')
    axes[-1].set_xlabel('Archive ID in result-recording order; IDs resolve to full configuration in full-history.md\nRed x: failed outputs retained as zero. Cross-model points are descriptive, not isolated architecture effects.')
    fig.savefig(DEST/'01-all-cohort-trajectories.png',dpi=160);fig.savefig(DEST/'01-all-cohort-trajectories.pdf');plt.close(fig)
    # Full GAIA matrix: each row retains its own label, configuration, and all three metrics.
    gaia=panels[-1][1]
    fig,ax=plt.subplots(figsize=(13,max(10,len(gaia)*.29)),layout='constrained')
    matrix=np.array([[r[k+'_pct'] for k in METRIC_NAMES] for r in gaia])
    ax.imshow(matrix,cmap='YlGnBu',vmin=0,vmax=60,aspect='auto')
    labels=[]
    for r in gaia:
        name=r['name'].replace('luna-gaia-','').replace('gaia-','').replace('clean-v3.20-','').replace('clean-v3p20-','')
        stage_models={v.get('model') for v in r['stage_models'].values() if isinstance(v,dict) and v.get('model')}
        model_label='+'.join(sorted(m.replace('gpt-','') for m in stage_models)) if len(stage_models)>1 else r['model'].replace('gpt-','')
        if r['run_kind']=='stage_replay':model_label+='; replay'
        labels.append(f"{r['id']}  {name[:60]}  [{model_label}]")
    ax.set_yticks(range(len(gaia)),labels,fontsize=8)
    ax.set_xticks(range(3),['Step','Step + Module','All']);ax.xaxis.tick_top()
    for i,r in enumerate(gaia):
        for j,key in enumerate(METRIC_NAMES):
            ax.text(j,i,f"{r[key]}/{r[key+'_denominator']}",ha='center',va='center',fontsize=8,color='white' if matrix[i,j]>35 else '#0f172a')
    ax.set_title('Every eligible GAIA-50 result (original fractions)',loc='left',pad=35,fontweight='bold')
    fig.savefig(DEST/'02-gaia50-every-version.png',dpi=170);fig.savefig(DEST/'02-gaia50-every-version.pdf');plt.close(fig)
    # Small gates use different selected cases; deliberately draw points, not a learning curve.
    diagnostic_panels=[('Single-case engineering probes',[r for r in rows if r['n']==1 and r['eligible']]),
                       ('Dry-3 screens (subset identity must be checked in the CSV)',[r for r in rows if r['n']==3 and r['eligible']]),
                       ('Dry-5 / gate-9 / GAIA hard-8 / structural-10',[r for r in rows if r['n'] in (5,8,9,10) and r['eligible']]),
                       ('Smoke-30 and rest150 reporting',[r for r in rows if (r['group']=='Mixed-30 / smoke-v1' or r['n']==150) and r['eligible']])]
    fig,axes=plt.subplots(4,1,figsize=(19,17),layout='constrained')
    for ax,(title,group) in zip(axes,diagnostic_panels):
        x=np.arange(len(group))
        for j,key in enumerate(METRIC_NAMES):
            ax.scatter(x+(j-1)*.17,[r[key+'_pct'] for r in group],color=palettes[key],s=30,marker=['o','s','^'][j],label=display[key])
        ax.set_xticks(x,[r['id']+f" (N={r['n']})" if len(group)<20 else r['id'] for r in group],rotation=90 if len(group)>12 else 0,fontsize=8)
        ax.set_title(title,loc='left',fontweight='bold');ax.set_ylim(-4,110);ax.set_ylabel('Exact accuracy (%)');ax.grid(axis='y',alpha=.18)
        if ax is axes[0]:ax.legend(ncol=3,loc='upper left')
    fig.suptitle('Remaining scored records: small screens and separate reporting cohorts',fontsize=18,fontweight='bold')
    axes[-1].set_xlabel('Each ID is a separate record. Different selected cases / denominators: do not read this as a common learning curve.\nDates unavailable for several diagnostic records; see archive rather than inferring chronology from file times.')
    fig.savefig(DEST/'03-diagnostics-and-other-scopes.png',dpi=160);fig.savefig(DEST/'03-diagnostics-and-other-scopes.pdf');plt.close(fig)
    # These are post-score candidate coverage measurements, never achievable model scores.
    stages=['Local inventory + anchor','Compressed candidates + anchor','Final prediction']
    fig,axes=plt.subplots(1,2,figsize=(14,5.5),layout='constrained')
    for ax,version,values in [(axes[0],'Luna v3.54',[36,24,18]),(axes[1],'Luna v3.56',[41,22,22])]:
        bars=ax.bar(range(3),values,color=['#93c5fd','#60a5fa','#2563eb'],width=.62)
        ax.set_xticks(range(3),stages,fontsize=9);ax.set_ylim(0,50);ax.set_ylabel('Cases / 50')
        ax.set_title(version,loc='left',fontweight='bold');ax.grid(axis='y',alpha=.15)
        ax.bar_label(bars,labels=[f'{v}/50' for v in values],padding=4)
        ax.axhline(30,ls='--',color='#64748b',lw=1)
    fig.suptitle('Candidate coverage can grow while usable diagnostic accuracy stalls',fontsize=17,fontweight='bold')
    fig.supxlabel('First two bars: post-score oracle coverage, not an agent score. Source: v3.20/v3.39 comparison report, v3.54/v3.56 section.',fontsize=9)
    fig.savefig(DEST/'04-candidate-selection-bottleneck.png',dpi=170);fig.savefig(DEST/'04-candidate-selection-bottleneck.pdf');plt.close(fig)


if __name__ == "__main__":
    main()
