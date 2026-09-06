"""Replot direct LLM API history without modifying original results or calling models.

uv run --no-project --with matplotlib python -m research.tools.plot_llm_api_history
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/results/experiment-history-2026-09-05/all-results.json"
DEST = ROOT / "research/results/llm-api-history-2026-09-06"
METRICS = ("step_exact", "step_module_exact", "all_correct")
SERIES = (("Step Exact", "#2563eb", "o"), ("Step+Module", "#16845b", "s"),
          ("All Correct", "#d97706", "^"))
UNKNOWN = "not_recorded"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def metadata(rows, refresh=False):
    """Capture allowlisted historical settings, not response bodies or credentials."""
    target = DEST / "api-runtime-evidence.json"
    if target.exists() and not refresh:
        return json.loads(target.read_text())
    result = {}
    for row in rows:
        path = ROOT / row["metrics_path"]
        assert digest(path) == row["metrics_sha256"], row["id"]
        raw = json.loads(path.read_text()).get("run", {})
        sources = {"metrics": {"path": row["metrics_path"], "sha256": digest(path)}}
        blobs = {}
        for name in ("preregistration.json", "predict-run.json"):
            p = ROOT / row["run_dir"] / name
            if p.exists():
                blobs[name] = json.loads(p.read_text())
                sources[name] = {"path": str(p.relative_to(ROOT)), "sha256": digest(p)}
        prereg = blobs.get("preregistration.json", {})
        predict = blobs.get("predict-run.json", {})
        cfg = prereg.get("provider_config") or predict.get("provider_config") or {}
        run = {k: raw[k] for k in (
            "upstream_mode", "transport_policy_version", "retry_backoff", "retry_failures",
            "production_two_stage_pipeline_version", "logical_completion_budget_used",
            "logical_completions_used", "cumulative_logical_completions_before",
            "cumulative_logical_completions_after", "max_logical_completions",
            "judge_view_version", "evidence_validation_version") if k in raw}
        provider = {k: cfg[k] for k in (
            "thinking_mode", "request_body_mode", "reasoning_effort", "retry_backoff",
            "max_retries", "max_output_tokens", "temperature", "timeout") if k in cfg}
        mode = raw.get("upstream_mode", UNKNOWN)
        if "v30_source_sha256s" in prereg:
            mode = "frozen_v30_incumbent"
        elif mode == UNKNOWN and "frozen-v13" in raw.get("production_two_stage_pipeline_version", ""):
            mode = "frozen_v13_tuning"
        result[row["id"]] = {
            "sources": sources, "run": run, "provider_settings": provider,
            "upstream_evidence": mode,
            "live_stages": prereg.get("execution", {}).get("live_stages", UNKNOWN),
            "same_case_frozen_upstream_proven": mode.startswith("frozen_"),
        }
    save_json(target, result)
    return result


def signature(row, meta, detailed=False):
    """Outer request settings; method topology and call count remain research variables."""
    config = {k: row[k] for k in (
        "dataset_sha256", "case_set_sha256", "transport", "model", "reasoning_effort",
        "temperature", "max_output_tokens", "timeout_seconds", "workers",
        "legacy_max_retries", "max_http_attempts", "stage_models")}
    config["metric_denominators"] = [row[k + "_denominator"] for k in METRICS]
    for key in ("thinking_mode", "request_body_mode"):
        config[key] = meta["provider_settings"].get(key, UNKNOWN)
    config["retry_backoff"] = meta["provider_settings"].get("retry_backoff", meta["run"].get("retry_backoff", UNKNOWN))
    if detailed:
        config.update(
            transport_policy_version=meta["run"].get("transport_policy_version", UNKNOWN),
            upstream_evidence=meta["upstream_evidence"], live_stages=meta["live_stages"],
            method=row["method"],
        )
    return config


def config_id(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:10]


def short_label(row):
    manual = {"R015": "Baseline", "R019": "E1-v7", "R031": "E6-v2", "R047": "E9-v13",
              "R097": "v52-R", "R101": "v31-R", "R150": "Official v1", "R154": "Strict v8.2"}
    name = row["name"]
    if row["id"] in manual:
        label = manual[row["id"]]
    else:
        found = re.search(r"e9-(v\d+)", name)
        label = found.group(1) if found else row["id"]
    if row["api_metadata"]["same_case_frozen_upstream_proven"]:
        label += "*"
    return label


def series(rows):
    gpt_full = [r for r in rows if r["model"] == "gpt-4.1" and r["group"] == "Mixed-30 / tuning-v1"]
    deep_full = [r for r in rows if r["model"] == "deepseek-v4-flash" and r["group"] == "Mixed-30 / tuning-v1"]
    gpt_dry = [r for r in rows if r["model"] == "gpt-4.1" and r["case_set_sha256"].startswith("b9b30e84")]
    deep_dry = [r for r in rows if r["model"] == "deepseek-v4-flash" and r["n"] == 3
                and r["api_config"]["request_body_mode"] == "default" and r["workers"] == 1
                and r["legacy_max_retries"] == 5]
    selected = {"gpt41_tuning30": gpt_full, "deepseek_flash_tuning30": deep_full,
                "gpt41_e9_dry3": gpt_dry, "deepseek_flash_default_dry3": deep_dry}
    assert [len(v) for v in selected.values()] == [4, 14, 14, 39]
    for name, values in selected.items():
        assert len({r["api_config_id"] for r in values}) == 1, name
        assert all(r["eligible"] and r["recorded_at"] and r["csv_verified"] for r in values), name
    assert [r["step_exact"] for r in gpt_full] == [1, 8, 5, 6]
    assert [r["step_exact"] for r in deep_full] == [6, 10, 9, 9, 10, 7, 9, 9, 9, 7, 9, 10, 10, 12]
    return selected


def panel(ax, failures_ax, rows, *, connect=True, prior_best=0, ylim=None):
    xs = list(range(len(rows)))
    for key, (name, color, marker) in zip(METRICS, SERIES):
        ys = [r[key + "_pct"] if r["eligible"] else math.nan for r in rows]
        ax.plot(xs, ys, color=color, marker=marker, markersize=4.5,
                linestyle="-" if connect else "none", linewidth=1.6, label=name)
    bests = []
    for r in rows:
        if r["eligible"]:
            prior_best = max(prior_best, r["step_exact_pct"])
        bests.append(prior_best)
    if connect:
        ax.step(xs, bests, where="post", color="#475569", linestyle="--", linewidth=1.0, label="Best Step in this series")
    for x, r in zip(xs, rows):
        if r["eligible"]:
            label = f"{r['step_exact']}/{r['n']}"
            ax.annotate(label, (x, r["step_exact_pct"]), xytext=(0, 8), textcoords="offset points",
                        ha="center", fontsize=10, color="#1e40af")
        else:
            ax.scatter([x] * 3, [r[k + "_pct"] for k in METRICS], color="#777777", marker="x")
    observed = [r[k + "_pct"] for r in rows for k in METRICS]
    upper = ylim if ylim is not None else min(115, math.ceil((max(observed) + 15) / 10) * 10)
    if all(r["n"] == 3 for r in rows):
        upper = 110
        ax.set_yticks([0, 100 / 3, 200 / 3, 100], ["0", "33.3", "66.7", "100"])
    elif 40 <= upper <= 65:
        ax.set_yticks([0, 20, 40, 60] if upper >= 60 else [0, 10, 20, 30, 40])
    ax.set_ylim(-2, upper)
    ax.set_ylabel("Exact accuracy (%)")
    ax.grid(axis="y", alpha=0.2)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.tick_params(axis="x", labelbottom=False)
    failures = [r["failed_outputs"] for r in rows]
    failures_ax.bar(xs, failures, color="#b94a48", width=0.45)
    failures_ax.set_ylim(0, max(max(failures) * 1.4, 1.4))
    failures_ax.set_yticks([])
    failures_ax.set_ylabel("Failed\noutputs", fontsize=9, rotation=0, ha="right", va="center")
    for x, count in zip(xs, failures):
        failures_ax.text(x, count + 0.03, str(count), ha="center", va="bottom", fontsize=9, color="#9f2929")
    failures_ax.set_xticks(xs, [short_label(r) for r in rows], rotation=90 if len(rows) > 7 else 0, fontsize=10)
    failures_ax.set_xlim(ax.get_xlim())
    failures_ax.set_xlabel("Recorded evaluation order; R = recovered result; * = frozen upstream evidence")
    return prior_best


def figure(plt, groups, title, subtitle, footer, filename, max_points=20):
    chunks = [(name, values[i:i + max_points], i) for name, values in groups for i in range(0, len(values), max_points)]
    height = 3.75 * len(chunks) + 1.5
    fig = plt.figure(figsize=(10, height))
    # Explicit physical margins keep nested failure strips close to their plot
    # without tight_layout colliding with the figure-level title/legend/footer.
    grid = fig.add_gridspec(len(chunks), 1, hspace=0.5, left=0.10, right=0.985,
                            top=1 - 1.6 / height, bottom=1.5 / height)
    best = {}
    common_ylim = min(115, math.ceil((max(r[k + "_pct"] for _, rs in groups for r in rs for k in METRICS) + 15) / 10) * 10)
    main_axes = []
    for n, (name, values, start) in enumerate(chunks):
        pair = grid[n].subgridspec(2, 1, height_ratios=[4.3, 0.8], hspace=0.12)
        ax = fig.add_subplot(pair[0])
        fail = fig.add_subplot(pair[1], sharex=ax)
        best[name] = panel(ax, fail, values, prior_best=best.get(name, 0), ylim=common_ylim)
        ax.set_title(name + (f" | continued, observations {start + 1}-{start + len(values)}" if start else ""), loc="left", fontsize=12)
        main_axes.append(ax)
    fig.suptitle(title, fontsize=16, y=1 - 0.1 / height)
    fig.text(0.5, 1 - 0.54 / height, subtitle, ha="center", fontsize=10)
    handles, labels = main_axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=4, frameon=False, fontsize=10, loc="upper center", bbox_to_anchor=(0.5, 1 - 0.78 / height))
    fig.text(0.5, 0.02, footer, ha="center", va="bottom", fontsize=9)
    for extension in ("png", "pdf"):
        fig.savefig(DEST / f"{filename}.{extension}", dpi=170)
    plt.close(fig)


def plots(rows, selected):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": "white", "axes.facecolor": "white"})
    envelope = "T=0 | max_output_tokens=8192 | timeout=600 s | workers=1 | max_retries=5 | retry_backoff=2 s"
    figure(plt, [("GPT-4.1 | 4 scored versions", selected["gpt41_tuning30"]),
                 ("DeepSeek-v4-flash | 14 scored versions | request_body=default", selected["deepseek_flash_tuning30"])],
           "Direct LLM API: tuning30 iteration history", envelope,
           "Same mixed-environment 30 cases; Step / Step+Module denominators=30, All denominator=25.\nActive API model/settings are fixed per panel; pipeline, inherited predictions and call counts may change.",
           "01-api-tuning30-by-model")
    figure(plt, [("GPT-4.1 | E9 v1-v14 | same 3-case set", selected["gpt41_e9_dry3"])],
           "Direct LLM API: GPT-4.1 E9 dry3 iterations", envelope,
           "One case changes accuracy by 33.3 percentage points. This is a development screen, not GAIA-50.\nAll metric denominators=3. Failed outputs remain in the denominator; frozen upstream is marked *.",
           "02-gpt41-api-e9-dry3")
    figure(plt, [("DeepSeek-v4-flash / default body | same 3-case set", selected["deepseek_flash_default_dry3"])],
           "Direct LLM API: DeepSeek dry3 iterations", envelope,
           "39 matching request-setting records; v15/v16 (thinking disabled), v19/v20 (Pro) and v55 (unknown budget) excluded.\nAll denominators=3. Most runs reuse upstream evidence; this is not an end-to-end fresh single-model series.",
           "03-deepseek-api-default-dry3", max_points=20)

    by_id = {r["id"]: r for r in rows}
    fig = plt.figure(figsize=(10, 10))
    grid = fig.add_gridspec(6, 1, height_ratios=[4, 0.8] * 3)
    specs = [(["R005", "R006"], "First full-release reproduction: GPT-4o / 200 cases / T=0 / timeout=300 s"),
             (["R013", "R014"], "Gemini-3.1-pro-preview / 200 cases / T=0 / timeout=600 s / cap=8192"),
             (["R150", "R154"], "GPT-4.1 / GAIA-50 / T=0 / workers=4 | timeouts differ: 180 vs 240 s")]
    for i, (ids, title) in enumerate(specs):
        rs = [by_id[k] for k in ids]
        ax, fail = fig.add_subplot(grid[i * 2]), fig.add_subplot(grid[i * 2 + 1])
        panel(ax, fail, rs, connect=False)
        ax.set_title(title, loc="left", fontsize=11)
        if i < 2:
            fail.set_xticks([0, 1], [f"direct ({ids[0]})", f"two_stage ({ids[1]})"])
        fail.set_xlabel("Independent comparisons, not a connected optimization trajectory")
    fig.suptitle("API reference runs kept outside the tuning curves", fontsize=15, y=0.99)
    fig.text(0.5, 0.018, "Full-release All Correct denominator=170, not 200. GAIA-50 All denominator=50.\nGPT-4o two_stage had 185/200 failed outputs; low scores here also reflect execution failures.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0.015, 0.075, 0.99, 0.97), h_pad=1.25)
    for extension in ("png", "pdf"):
        fig.savefig(DEST / f"04-api-reference-runs.{extension}", dpi=170)
    plt.close(fig)

    grouped = defaultdict(list)
    for r in rows:
        grouped[r["detailed_config_id"]].append(r)
    with PdfPages(DEST / "05-all-api-config-groups.pdf") as pdf:
        for identity, values in grouped.items():
            best = 0
            for start in range(0, len(values), 18):
                part = values[start:start + 18]
                fig, (ax, fail) = plt.subplots(2, 1, figsize=(11, 6), gridspec_kw={"height_ratios": [4.3, 0.8]})
                best = panel(ax, fail, part, connect=len(part) > 1 and all(r["recorded_at"] for r in part), prior_best=best)
                c = part[0]["api_config"]
                ax.set_title(f"{identity} | {part[0]['model']} | {part[0]['group']} | cases={part[0]['case_set_sha256'][:8]}\n"
                             f"T={c['temperature']}; cap={c['max_output_tokens']}; timeout={c['timeout_seconds']}; "
                             f"workers={c['workers']}; retries={c['legacy_max_retries']}\n"
                             f"Step/Module/All denominators={c['metric_denominators']}; unknown values are not proof of equality", fontsize=10)
                ax.legend(ncol=4, frameon=False, fontsize=9, loc="upper right")
                fail.set_xticks(range(len(part)), [short_label(r) + "\n" + r["id"] for r in part], rotation=90 if len(part) > 6 else 0, fontsize=9)
                fig.text(0.5, 0.018, "All API records retained. Unknown-time groups are unconnected; audit-invalid points are gray crosses.\nExact runtime policy, upstream identity and live-stage grouping are recorded in api-records.json.", ha="center", fontsize=9)
                fig.tight_layout(rect=(0.015, 0.08, 0.99, 0.98), h_pad=1.3)
                pdf.savefig(fig)
                plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--refresh-metadata", action="store_true")
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    rows = [r for r in json.loads(SOURCE.read_text()) if r["transport"] in ("LLM API", "Responses API")]
    evidence = metadata(rows, args.refresh_metadata)
    for r in rows:
        r["api_metadata"] = evidence[r["id"]]
        r["api_config"] = signature(r, r["api_metadata"])
        r["detailed_config"] = signature(r, r["api_metadata"], detailed=True)
        r["api_config_id"] = config_id(r["api_config"])
        r["detailed_config_id"] = config_id(r["detailed_config"])
    selected = series(rows)
    fields = ["id", "name", "recorded_at", "group", "n", "method_family", "execution_backend", "transport", "model", "method",
              "step_exact", "step_module_exact", "all_correct", "step_exact_denominator",
              "step_module_exact_denominator", "all_correct_denominator", "failed_outputs",
              "eligible", "status", "run_kind", "case_set_sha256", "metrics_path",
              "api_config_id", "detailed_config_id", "api_config", "detailed_config", "api_metadata"]
    save_json(DEST / "api-records.json", [{k: r[k] for k in fields} for r in rows])
    with (DEST / "api-records.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: json.dumps(r[k], ensure_ascii=False, sort_keys=True) if isinstance(r[k], (dict, list)) else r[k] for k in fields})
    summary = {
        "source_sha256": digest(SOURCE), "api_record_count": len(rows),
        "eligible_count": sum(r["eligible"] for r in rows),
        "unknown_time_count": sum(not r["recorded_at"] for r in rows),
        "model_counts": dict(Counter(r["model"] for r in rows)),
        "api_setting_groups": len({r["api_config_id"] for r in rows}),
        "detailed_groups": len({r["detailed_config_id"] for r in rows}),
        "main_series": {name: [r["id"] for r in values] for name, values in selected.items()},
        "proven_frozen_upstream_count": sum(r["api_metadata"]["same_case_frozen_upstream_proven"] for r in rows),
        "provider_used_to_filter": False, "new_model_calls": False,
        "scope": "archived direct API runs; fixed active-model request envelope, not fixed full-pipeline cost or proof of all-stage fresh inference",
    }
    assert len(rows) == 116 and summary["eligible_count"] == 115
    save_json(DEST / "verification-summary.json", summary)
    if not args.no_plots:
        plots(rows, selected)
    save_json(DEST / "figure-manifest.json", {
        "source_sha256": digest(SOURCE), "script_sha256": digest(Path(__file__)),
        "files": {p.name: digest(p) for p in sorted(DEST.iterdir())
                  if p.is_file() and p.name not in ("README.md", "figure-manifest.json")},
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
