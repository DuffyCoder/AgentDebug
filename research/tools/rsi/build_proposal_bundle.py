"""Build a data-free reviewer packet and unified method-family accounting.

Reads public derived records, never output/, data/, credentials or model APIs.
Only an explicit file allowlist enters the ZIP; this is not an agent image.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from research.tools.result_taxonomy import (
    API_FAMILY, CODEX_FAMILY, POLICY_VERSION, classification, is_fixed_model,
    valid_record,
)

ROOT = Path(__file__).resolve().parents[3]
HISTORY = Path("research/results/experiment-history-2026-09-05/all-results.json")
FIXED = Path("research/results/fixed-config-history-2026-09-06/fixed-config-records.json")
TASK = Path("research/rsi/agentdebug_gaia")
ATTACH = TASK / "attachments"
COUNTS = Path("research/results/method-family-counts.json")
MANIFEST = ATTACH / "bundle-manifest.json"
ZIP_PATH = ATTACH / "agentdebug-rsi-proposal-evidence.zip"
CORE_IDS = ("R208", "R211", "R212", "R213")
FIELDS = (
    "id", "name", "recorded_at", "method_family", "execution_backend",
    "transport", "model", "reasoning_effort", "stage_models", "group", "n",
    "temperature", "workers", "max_semantic_attempts", "max_http_attempts",
    "legacy_max_retries", "max_output_tokens", "timeout_seconds", "protocol",
    "dataset_sha256", "case_set_sha256", "environment_counts", "run_dir",
    "status", "eligible", "run_kind", "fresh_end_to_end", "failed_outputs", "csv_verified",
    "step_exact", "step_exact_denominator", "step_module_exact",
    "step_module_exact_denominator", "all_correct", "all_correct_denominator",
    "semantic_parent", "metrics_path", "metrics_sha256", "per_example_sha256",
)
STATIC_FILES = (
    "LICENSE", "REPRODUCING.md", "research/requirements-transports.txt",
    "research/configs/reproduction-profiles.json",
    "research/configs/transport-contract.json",
    "research/notes/sdk-comparison.md", "research/results/method-family-policy.md",
    "research/results/fixed-config-history-2026-09-06/01-luna-gaia50-fixed-three-stage.png",
    "research/results/fixed-config-history-2026-09-06/01-luna-gaia50-fixed-three-stage.pdf",
    "research/results/method-family-counts.md", "research/results/method-family-counts.csv",
    str(COUNTS), str(TASK / "proposal.md"), str(TASK / "instruction.md"),
    str(TASK / "submission-guide.zh-CN.md"), str(TASK / "design.md"),
    str(TASK / "readiness.json"), str(ATTACH / "README.md"),
    str(ATTACH / "01-experiment-evidence.md"), str(ATTACH / "02-fixed-gpt55-iterations.png"),
    str(ATTACH / "02-fixed-gpt55-iterations.pdf"), str(ATTACH / "03-metric-and-seal.md"),
    str(ATTACH / "04-reproduction-and-runtime.md"), str(ATTACH / "05-sources-and-licensing.md"),
    str(ATTACH / "experiment-evidence.json"), str(ATTACH / "codex-sdk-family-runs.csv"),
    "research/tools/rsi/contracts.py", "research/tools/rsi/check_readiness.py",
    "research/tests/test_authoring_contracts.py",
    "research/tools/result_taxonomy.py",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(row[k], ensure_ascii=False, sort_keys=True)
                             if isinstance(row[k], (dict, list)) else row[k] for k in fields})


def count(rows: list[dict]) -> dict:
    return {"runs": len({r["run_dir"] for r in rows}), "records": len(rows)}


def summarize(rows: list[dict]) -> dict:
    for row in rows:
        if any(row.get(k) != v for k, v in classification(row["transport"]).items()):
            raise ValueError(f"Reporting classification missing or inconsistent: {row['id']}")
    valid = [r for r in rows if valid_record(r)]
    families = {family: count([r for r in valid if r["method_family"] == family])
                for family in (API_FAMILY, CODEX_FAMILY)}
    codex = [r for r in valid if r["method_family"] == CODEX_FAMILY]
    gaia = [r for r in codex if r["group"] == "GAIA-50"]
    fresh = [r for r in gaia if r["fresh_end_to_end"]]
    gpt = [r for r in fresh if is_fixed_model(r, "gpt-5.5")]
    medium = [r for r in gpt if is_fixed_model(r, "gpt-5.5", "medium")]
    cohorts = defaultdict(list)
    for row in valid:
        cohorts[(row["dataset_sha256"], row["case_set_sha256"])].append(row)
    grouped = []
    for (dataset, identity), values in cohorts.items():
        if not identity or len({r["n"] for r in values}) != 1:
            raise ValueError("Cannot identify a unique fixed case set")
        api = [r for r in values if r["method_family"] == API_FAMILY]
        family = [r for r in values if r["method_family"] == CODEX_FAMILY]
        app = [r for r in family if r["execution_backend"] == "Codex SDK/app-server"]
        host = [r for r in family if r["execution_backend"] != "Codex SDK/app-server"]
        grouped.append({
            "group": " / ".join(sorted({r["group"] for r in values})), "n": values[0]["n"],
            "dataset_sha256": dataset, "case_set_sha256": identity,
            "llm_api_runs": count(api)["runs"], "llm_api_records": len(api),
            "codex_sdk_family_runs": count(family)["runs"], "codex_sdk_family_records": len(family),
            "codex_app_server_runs": count(app)["runs"], "codex_host_agent_runs": count(host)["runs"],
        })
    grouped.sort(key=lambda r: (-r["n"], r["group"], r["case_set_sha256"]))
    return {
        "schema_version": "agentdebug.method-family-counts.v1", "reporting_policy": POLICY_VERSION,
        "validity_rule": "csv_verified && eligible && status in {complete_scored, scored_failures_zero}",
        "count_unit": "runs deduplicated by run_dir; records are run-by-method scores",
        "total_archive_records": len(rows), "valid": count(valid), "families": families,
        "actual_codex_backends": {key: count([r for r in codex if r["execution_backend"] == key])
                                  for key in sorted({r["execution_backend"] for r in codex})},
        "cohorts": grouped,
        "distinct_case_sets": len({r["case_set_sha256"] for r in valid}),
        "gaia50_codex_family": {"valid": count(gaia), "recorded_fresh": count(fresh),
                                "stage_replay_ids": [r["id"] for r in gaia if r["run_kind"] == "stage_replay"]},
        "gpt55_gaia50_all_stage_fresh_ids": [r["id"] for r in gpt],
        "gpt55_medium_gaia50_all_stage_fresh_ids": [r["id"] for r in medium],
        "matched_host_three_stage_ids": list(CORE_IDS),
        "status_counts_all_records": dict(Counter(r["status"] for r in rows)),
        "new_inference_performed": False,
        "caveats": ["Valid score accounting does not prove fresh or independent inference.",
                    "API fresh_end_to_end is not a reliable frozen-upstream audit.",
                    "Method-family grouping does not imply matched backends, models or budgets.",
                    "All historical GAIA-50 cases are exposed; no hidden-set result is claimed."],
    }


def render_counts(summary: dict) -> str:
    api, sdk = (summary["families"][f] for f in (API_FAMILY, CODEX_FAMILY))
    lines = ["# 按统一方法族统计有效实验", "",
             "由公开结果档案自动生成；口径见 [方法族政策](method-family-policy.md)。没有新增模型推理。", "",
             f"总计 {summary['valid']['runs']} 次有效运行 / {summary['valid']['records']} 条运行×方法记录。",
             f"LLM API：{api['runs']} 次 / {api['records']} 条；Codex SDK 方法族：{sdk['runs']} 次 / {sdk['records']} 条。", "",
             "每行使用数据身份与精确案例集合指纹，而不是仅按样本数合并。API 单个运行可能同时评测 direct / two_stage。",
             f"共 {summary['distinct_case_sets']} 个案例集合，按已记录数据身份分为 {len(summary['cohorts'])} 层；未知身份不默认相同。",
             "宿主子 agent 已归入 SDK 方法族，后两列仅解释实际执行来源，不是额外实验。", "",
             "| 数据范围 | N | 数据身份前8位 | 案例集指纹前8位 | LLM API 次数 | SDK 方法族次数 | 其中 app-server | 其中宿主子 agent |",
             "|---|---:|---|---|---:|---:|---:|---:|"]
    for r in summary["cohorts"]:
        lines.append(f"| {r['group']} | {r['n']} | {r['dataset_sha256'][:8] or '未记录'} | {r['case_set_sha256'][:8]} | {r['llm_api_runs']} | "
                     f"{r['codex_sdk_family_runs']} | {r['codex_app_server_runs']} | {r['codex_host_agent_runs']} |")
    g = summary["gaia50_codex_family"]
    lines += ["", "## 对固定模型 RSI 证据的限制", "",
              f"SDK 方法族 GAIA-50 有 {g['valid']['runs']} 次有效运行，其中 {len(g['stage_replay_ids'])} 次阶段重放；"
              f"{g['recorded_fresh']['runs']} 次记录为 fresh。",
              f"所有阶段均为 GPT-5.5 的 fresh GAIA-50 运行有 {len(summary['gpt55_gaia50_all_stage_fresh_ids'])} 次；"
              f"再固定 medium 后有 {len(summary['gpt55_medium_gaia50_all_stage_fresh_ids'])} 次。",
              "其中只有 R208/R211/R212/R213 属于同一已记录三阶段宿主配置。未知宿主版本并未因此补齐。", "",
              "有效计分允许失败按零计入完整分母；有效不等于每条输出合法、不等于独立研究思路、",
              "也不等于所有阶段都重新推理。API 历史存在冻结上游复用，不能由通用 fresh 标记推出全部 fresh。",
              "组合报告、审计否决/保留、历史先验输出与修改 validator 的诊断不计入上述有效总数。", "",
              "[JSON](method-family-counts.json) / [CSV](method-family-counts.csv) 保留完整指纹和记录数。",
              "[研究档案](../../research/README.md) 统一收录 RSI 附件、固定模型证据与全部家族运行。", ""]
    return "\n".join(lines)


def render_evidence(summary: dict, records: list[dict]) -> str:
    primary = set(summary["gpt55_medium_gaia50_all_stage_fresh_ids"])
    lines = ["# Experimental evidence — Codex SDK method family", "",
             "This project groups SDK/app-server and host-orchestrated Codex agents in one method family. "
             "Actual backends remain explicit; host runs are not relabeled as SDK-package invocations.", "",
             f"The archive has {summary['valid']['records']} valid score records from {summary['valid']['runs']} run directories. "
             f"The Codex SDK family accounts for {summary['families'][CODEX_FAMILY]['runs']} runs "
             "(97 host-agent, 2 app-server). These span models, cohorts and replay modes.", "",
             "## All fresh GAIA-50 runs with every stage fixed to GPT-5.5 / medium", "",
             "| ID | Version | Actual backend | Step | Step+Module | All | Recorded configuration |",
             "|---|---|---|---:|---:|---:|---|"]
    for r in records:
        if r["id"] not in primary:
            continue
        version = {"R208": "v3.83", "R211": "v3.86", "R212": "v3.87", "R213": "v3.88",
                   "R215": "v3.102", "R216": "v3.107", "R219": "Official SDK v3"}[r["id"]]
        setting = ("3 stages; max 2 semantic attempts/stage" if r["id"] in CORE_IDS else
                   {"R215": "2 stages; max 3 attempts/stage", "R216": "app-server 0.147.0; 3 stages; bounded retries",
                    "R219": "app-server 0.147.0; official topology; 1 semantic attempt/call"}[r["id"]])
        scores = " | ".join(f"{r[k]}/{r[k + '_denominator']}" for k in ("step_exact", "step_module_exact", "all_correct"))
        lines.append(f"| {r['id']} | {version} | {r['execution_backend']} | {scores} | {setting} |")
    lines += ["", "![Fixed-model evidence](02-fixed-gpt55-iterations.png)", "",
              "The four connected observations share the recorded host configuration: workers=4, three fresh "
              "sessions/case, at most two semantic attempts/stage, same 50-case membership. They do not have "
              "proven identical host/backend snapshots or realized token costs. Other valid medium runs "
              "are shown as separate points. Missing formal results are never zero-filled.", "",
              "## What the iteration process actually did", "",
              "A candidate starts from a frozen incumbent, proposes a mechanism, changes code/prompts, "
              "checks output contracts, executes a full evaluation, freezes predictions, and then inspects "
              "scores/errors. Step Exact determines acceptance; rejected experiments remain in the archive. "
              "Many candidates branch from the same incumbent rather than inherit the preceding rejected version.", "",
              "In the matched GPT-5.5 series, v3.86 tested bounded typed-boundary challenges, v3.87 tested "
              "evidence-lifecycle challenges, and v3.88 tested sparse influence-graph challenges. Their Step "
              "scores of 24/50, 18/50 and 22/50 did not exceed v3.83's 26/50. v3.107 tested an app-server "
              "execution path and bounded transport retries. This is evidence of non-monotonic method search, "
              "not proof of a transport effect or of statistical significance.", "",
              "Luna provides supplementary, separately fixed-model evidence: the stricter 31-version "
              "three-stage series improved from 20/50 to 24/50 to 25/50, then 23 further scored versions "
              "did not exceed 25/50. It belongs to the same method family but is not GPT-5.5 evidence. "
              "The supplementary 31-version Luna figure is included under research/results/fixed-config-history-2026-09-06/ "
              "in the packet. It is explicitly a different-model curve; do not pool it with GPT-5.5.", "",
              "## Audit and interpretation limits", "",
              "All 50 cases were exposed during development. There is no sealed generalization result, "
              "single twelve-hour scratch rollout, or demonstrated non-saturation guarantee. A known "
              "source-step mapping anomaly remains in historical full-denominator results. The best "
              "observed local number is not external SOTA and has not been reproduced after a standardized "
              "app-server port. v3.107 ran before Official SDK v3, so 19→23→26 is not historical chronology.", "",
              "The CSV contains every valid Codex-family run, including explicitly marked stage replay; "
              "it does not claim they are independent full-pipeline iterations. The JSON provides the "
              "complete counting rule, source archive SHA-256 and per-record provenance. Ineligible or "
              "unscored versions remain in the full research archive, not this valid-run attachment.", ""]
    return "\n".join(lines)


def plot_evidence(root: Path, records: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    by_id = {r["id"]: r for r in records}
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.5))
    series = (("step_exact", "Step Exact", "#2563eb", "o"),
              ("step_module_exact", "Step+Module", "#16845b", "s"),
              ("all_correct", "All Correct", "#d97706", "^"))
    groups = (CORE_IDS, ("R215", "R216", "R219"))
    labels = (("v3.83\nR208", "v3.86\nR211", "v3.87\nR212", "v3.88\nR213"),
              ("v3.102 / host\n2 stages, 3 attempts", "v3.107 / app-server\n3 stages, bounded retries",
               "Official SDK v3 / app-server\nofficial topology"))
    for i, (ax, ids) in enumerate(zip(axes, groups)):
        for j, (key, label, color, marker) in enumerate(series):
            x = [k + ((j - 1) * 0.12 if i else 0) for k in range(len(ids))]
            y = [by_id[ident][key] for ident in ids]
            ax.plot(x, y, label=label, color=color, marker=marker,
                    linestyle="-" if i == 0 else "none", linewidth=1.5, markersize=6)
            if key == "step_exact":
                for xx, yy in zip(x, y):
                    ax.annotate(str(yy), (xx, yy), xytext=(0, 8), textcoords="offset points", ha="center")
        ax.set_xticks(range(len(ids)), labels[i], fontsize=10)
        ax.set_xlim(-0.5, len(ids) - 0.5)
        ax.set_ylim(0, 32)
        ax.set_ylabel("Correct cases / 50")
        ax.grid(axis="y", alpha=0.2)
        ax.spines[["right", "top"]].set_visible(False)
    axes[0].set_title("Matched recorded host configuration: 3 fresh sessions/case, max 2 attempts/stage", fontsize=11, loc="left")
    axes[0].legend(ncol=3, frameon=False, loc="lower left")
    axes[1].set_title("Other valid medium runs: different budgets/backends/contracts; no connecting line", fontsize=11, loc="left")
    fig.suptitle("Codex SDK method family | GPT-5.5 / medium | GAIA-50", fontsize=15, y=0.98)
    fig.text(0.5, 0.055, "Family includes host agents AND SDK/app-server; actual execution is labeled.\n"
             "All seven fresh medium runs shown. Exposed development data; not hidden anchors or causal effects.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0.01, 0.1, 0.99, 0.94), h_pad=2.2)
    for ext in ("png", "pdf"):
        fig.savefig(root / ATTACH / f"02-fixed-gpt55-iterations.{ext}", dpi=170)
    plt.close(fig)


def build(root: Path = ROOT, *, no_plots: bool = False) -> dict:
    rows = load(root / HISTORY)
    summary = summarize(rows)
    summary.update(source_archive=str(HISTORY), source_archive_sha256=sha(root / HISTORY))
    write_json(root / COUNTS, summary)
    (root / COUNTS.with_suffix(".md")).write_text(render_counts(summary), encoding="utf-8")
    write_csv(root / COUNTS.with_suffix(".csv"), summary["cohorts"], summary["cohorts"][0].keys())
    fixed = {r["id"]: r for r in load(root / FIXED)}
    if len({fixed[i]["fixed_config_id"] for i in CORE_IDS}) != 1:
        raise ValueError("Core evidence is not one recorded configuration")
    if any(i not in summary["gpt55_medium_gaia50_all_stage_fresh_ids"] for i in CORE_IDS):
        raise ValueError("Core evidence does not meet fixed-model/fresh requirements")
    records = [{k: r[k] for k in FIELDS} for r in rows
               if valid_record(r) and r["method_family"] == CODEX_FAMILY]
    evidence = {"schema_version": "agentdebug.rsi-proposal-evidence.v1", "summary": summary,
                "records": records, "fixed_configurations": {
                    i: fixed[i]["fixed_config"] for i in summary["gpt55_medium_gaia50_all_stage_fresh_ids"]},
                "contains_raw_trajectories_or_labels": False, "sealed_anchors_calibrated": False}
    write_json(root / ATTACH / "experiment-evidence.json", evidence)
    write_csv(root / ATTACH / "codex-sdk-family-runs.csv", records, FIELDS)
    (root / ATTACH / "01-experiment-evidence.md").write_text(render_evidence(summary, records), encoding="utf-8")
    if not no_plots:
        plot_evidence(root, records)
    files = {}
    for name in STATIC_FILES:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or unsafe bundle file: {name}")
        files[name] = sha(path)
    manifest = {"schema_version": "agentdebug.rsi-proposal-bundle.v1", "prepared_date": "2026-09-06",
                "audience": "authors/reviewers only; never participant image",
                "source_archive_sha256": sha(root / HISTORY), "files": files,
                "contains_full_research_code": False, "contains_raw_data_or_model_outputs": False,
                "new_model_inference": False, "submitted_to_airtable": False,
                "sealed_task_ready": False}
    write_json(root / MANIFEST, manifest)
    with ZipFile(root / ZIP_PATH, "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted([*files, str(MANIFEST)]):
            info = ZipInfo(name, date_time=(2026, 9, 6, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root / name).read_bytes())
    return check(root)


def check(root: Path = ROOT) -> dict:
    manifest = load(root / MANIFEST)
    if set(manifest["files"]) != set(STATIC_FILES):
        raise ValueError("Bundle file allowlist changed")
    if sha(root / HISTORY) != manifest["source_archive_sha256"]:
        raise ValueError("Bundle source archive changed; rebuild evidence")
    evidence = load(root / ATTACH / "experiment-evidence.json")
    rows = load(root / HISTORY)
    summary = summarize(rows)
    if any(evidence["summary"].get(k) != v for k, v in summary.items()):
        raise ValueError("Evidence counts do not match the source")
    expected_records = [{k: r[k] for k in FIELDS} for r in rows
                        if valid_record(r) and r["method_family"] == CODEX_FAMILY]
    if evidence["records"] != expected_records:
        raise ValueError("Evidence records do not match the source")
    if load(root / COUNTS) != evidence["summary"]:
        raise ValueError("Count report does not match evidence")
    fixed = {r["id"]: r for r in load(root / FIXED)}
    if evidence["fixed_configurations"] != {
        i: fixed[i]["fixed_config"] for i in summary["gpt55_medium_gaia50_all_stage_fresh_ids"]
    }:
        raise ValueError("Fixed configuration evidence changed")
    with ZipFile(root / ZIP_PATH) as archive:
        expected = {*STATIC_FILES, str(MANIFEST)}
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != expected:
            raise ValueError("ZIP contains missing, duplicate or unexpected files")
        for name in sorted(expected):
            path = root / name
            if Path(name).is_absolute() or not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
                raise ValueError("Unsafe bundle member")
            if name != str(MANIFEST) and sha(path) != manifest["files"][name]:
                raise ValueError(f"Bundle source file changed: {name}")
            if archive.read(name) != path.read_bytes():
                raise ValueError(f"ZIP differs from reviewed file: {name}")
    return {"verified_bundle_files": len(STATIC_FILES) + 1,
            "valid_runs": summary["valid"]["runs"], "families": summary["families"],
            "gpt55_medium_gaia50_fresh_runs": len(summary["gpt55_medium_gaia50_all_stage_fresh_ids"]),
            "bundle_sha256": sha(root / ZIP_PATH), "new_inference": False,
            "submitted": False, "sealed_task_ready": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    result = build(no_plots=args.no_plots) if args.action == "build" else check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
