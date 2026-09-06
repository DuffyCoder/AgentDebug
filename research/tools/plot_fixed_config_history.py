"""Plot recorded-configuration-matched GAIA histories; never rerun inference.

uv run --no-project --with matplotlib python -m research.tools.plot_fixed_config_history
The existing 2026-09-05 archive and original output/ artifacts are read-only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "research/results/experiment-history-2026-09-05/all-results.json"
DEST = ROOT / "research/results/fixed-config-history-2026-09-06"
METRICS = ("step_exact", "step_module_exact", "all_correct")
SERIES = (("Step Exact", "#2563eb", "o"), ("Step+Module", "#16845b", "s"),
          ("All Correct", "#d97706", "^"))
UNKNOWN = "not_recorded"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_supplement(rows, refresh=False):
    """Persist only allowlisted runtime facts, without prompts, credentials or labels."""
    path = DEST / "sdk-runtime-evidence.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    by_id = {r["id"]: r for r in rows}
    a = ROOT / by_id["R216"]["run_dir"] / "transport-preflight.json"
    b = ROOT / by_id["R219"]["run_dir"] / "experiment-plan.json"
    pa, pb = json.loads(a.read_text()), json.loads(b.read_text())
    result = {
        "R216": {
            "source": str(a.relative_to(ROOT)), "source_sha256": sha(a),
            "sdk_version": pa["provenance"]["sdk_version"],
            "transport_retry_policy": pa["transport_retry_policy"],
            "semantic_attempts": 2, "semantic_attempt_unit": "stage",
            "output_contract": "v3.83 strict owner/taxonomy/evidence validation",
        },
        "R219": {
            "source": str(b.relative_to(ROOT)), "source_sha256": sha(b),
            "sdk_version": pb["sdk_version"],
            "bundled_cli_version": pb["bundled_cli_version"],
            "outer_semantic_retries": pb["outer_semantic_retries"],
            "max_same_prompt_transport_attempts": pb["max_same_prompt_transport_attempts"],
            "provider_internal_retry_budget_observable": pb["provider_internal_retry_budget_observable"],
            "semantic_attempts": 1 + pb["outer_semantic_retries"],
            "semantic_attempt_unit": "call",
            "output_contract": "native taxonomy + others virtual-owner bridge",
        },
    }
    assert result["R216"]["sdk_version"] == result["R219"]["sdk_version"] == "0.147.0"
    dump(path, result)
    return result


def model_signature(row):
    # Naming roles differently is an architecture change, not a model change.
    stages = row["stage_models"]
    if not stages:
        return [[row["model"], row["reasoning_effort"]]]
    pairs = set()
    for value in stages.values():
        if isinstance(value, dict):
            pairs.add((value.get("model", UNKNOWN), value.get("reasoning_effort", UNKNOWN)))
        else:
            pairs.add((str(value), UNKNOWN))
    return [list(p) for p in sorted(pairs, key=str)]


def configuration(row, supplement):
    sources = row["config_sources"]
    plan = sources.get("tuning-plan.json") or sources.get("experiment-plan.json") or {}
    topo = plan.get("session_topology", {})
    sdk = supplement.get(row["id"], {})
    if "max_attempts_per_stage" in topo:
        unit, attempts = "stage", topo["max_attempts_per_stage"]
    elif "max_attempts_per_case" in topo:
        unit, attempts = "case", topo["max_attempts_per_case"]
    else:
        unit, attempts = sdk.get("semantic_attempt_unit", UNKNOWN), sdk.get("semantic_attempts", UNKNOWN)
    if topo.get("fresh_ephemeral_session_per_case"):
        sessions = 1
    elif isinstance(topo.get("serial_stages_per_case"), list):
        sessions = len(topo["serial_stages_per_case"])
    else:
        sessions = UNKNOWN  # Do not infer a fixed budget from missing metadata.
    if "SDK" in row["transport"]:
        transport_budget = {k: sdk[k] for k in (
            "transport_retry_policy", "max_same_prompt_transport_attempts",
            "provider_internal_retry_budget_observable") if k in sdk}
    elif row["transport"] == "Codex agent/subagent":
        # Imported-prediction scoring.max_retries is NOT the agent inference budget.
        transport_budget = UNKNOWN
    else:
        transport_budget = {"max_http_attempts": row["max_http_attempts"],
                            "legacy_max_retries": row["legacy_max_retries"]}
    return {
        "dataset_sha256": row["dataset_sha256"],
        "case_set_sha256": row["case_set_sha256"],
        "metric_denominators": [row[k + "_denominator"] for k in METRICS],
        "transport": row["transport"],
        "sdk_or_host_version": sdk.get("sdk_version", UNKNOWN),
        "models_and_efforts": model_signature(row),
        "temperature": row["temperature"], "max_output_tokens": row["max_output_tokens"],
        "timeout_seconds": row["timeout_seconds"], "workers": row["workers"],
        "semantic_attempt_unit": unit, "max_semantic_attempts": attempts,
        "transport_retry_budget": transport_budget,
        "planned_fresh_sessions_per_case": sessions,
        "one_trajectory_per_session": topo.get("trajectories_per_session", UNKNOWN),
        "cross_case_state_visible": topo.get("cross_case_state_visible", UNKNOWN),
        "fresh_end_to_end": row["fresh_end_to_end"],
    }


def config_id(config):
    return "C-" + hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:10]


def version(row):
    if row["id"] == "R219":
        return "Official SDK v3"
    return re.search(r"v\d+(?:\.\d+)*", row["name"]).group() if re.search(r"v\d+", row["name"]) else row["id"]


def select(rows, *, model, group, sessions=None, attempt_unit=None):
    return [r for r in rows if r["eligible"] and r["fresh_end_to_end"]
            and r["group"] == group
            and r["fixed_config"]["models_and_efforts"] == [[model, "medium"]]
            and r["transport"] == "Codex agent/subagent"
            and r["fixed_config"]["max_semantic_attempts"] == 2
            and (sessions is None or r["fixed_config"]["planned_fresh_sessions_per_case"] == sessions)
            and (attempt_unit is None or r["fixed_config"]["semantic_attempt_unit"] == attempt_unit)]


def validate(rows):
    luna = select(rows, model="gpt-5.6-luna", group="GAIA-50", sessions=3, attempt_unit="stage")
    gpt = select(rows, model="gpt-5.5", group="GAIA-50", sessions=3, attempt_unit="stage")
    early = select(rows, model="gpt-5.6-luna", group="GAIA-smoke-30", sessions=1, attempt_unit="case")
    broader = select(rows, model="gpt-5.6-luna", group="GAIA-50", attempt_unit="stage")
    assert [len(x) for x in (luna, gpt, early, broader)] == [31, 4, 13, 47]
    for values in (luna, gpt, early):
        assert len({r["fixed_config_id"] for r in values}) == 1
        assert all(r["csv_verified"] and r["recorded_at"] and not r["failed_outputs"] for r in values)
    assert [r["id"] for r in gpt] == ["R208", "R211", "R212", "R213"]
    assert [r["step_exact"] for r in gpt] == [26, 24, 18, 22]
    assert not {"R199", "R200", "R201", "R202"} & {r["id"] for r in broader}
    assert next(r for r in rows if r["id"] == "R216")["fixed_config_id"] != next(r for r in rows if r["id"] == "R219")["fixed_config_id"]
    assert next(r for r in rows if r["id"] == "R150")["fixed_config_id"] != next(r for r in rows if r["id"] == "R154")["fixed_config_id"]
    return luna, gpt, early, broader


def plot_line(ax, rows, *, prior_best=0, show_ids=False):
    x = list(range(len(rows)))
    for key, (label, color, marker) in zip(METRICS, SERIES):
        y = [r[key] for r in rows]
        ax.plot(x, y, color=color, marker=marker, markersize=4.5, linewidth=1.6, label=label)
    best = []
    for r in rows:
        prior_best = max(prior_best, r["step_exact"])
        best.append(prior_best)
    ax.step(x, best, where="post", color="#475569", linestyle="--", linewidth=1.1, label="Best Step so far")
    for i, row in enumerate(rows):
        ax.annotate(str(row["step_exact"]), (i, row["step_exact"]), xytext=(0, 7),
                    textcoords="offset points", ha="center", fontsize=10, color="#1e40af")
    labels = [version(r) + ("\n" + r["id"] if show_ids else "") for r in rows]
    ax.set_xticks(x, labels, rotation=90 if len(rows) > 8 else 0, fontsize=10)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(0, math.ceil((max(max(r[k] for k in METRICS) for r in rows) + 4) / 5) * 5)
    ax.set_ylabel(f"Correct cases / {rows[0]['n']}")
    ax.set_xlabel("Version in recorded evaluation order (not parent-child ancestry)")
    ax.grid(axis="y", alpha=0.2)
    return prior_best


def line_figure(plt, rows, name, title, subtitle, footer, per_panel=18):
    panels = math.ceil(len(rows) / per_panel)
    height = 3.6 * panels + 1.5
    fig, axes = plt.subplots(panels, 1, figsize=(10, height), squeeze=False)
    best = 0
    common_upper = math.ceil((max(max(r[k] for k in METRICS) for r in rows) + 4) / 5) * 5
    for i, ax in enumerate(axes[:, 0]):
        subset = rows[i * per_panel:(i + 1) * per_panel]
        best = plot_line(ax, subset, prior_best=best)
        ax.set_ylim(0, common_upper)
        if panels > 1:
            ax.set_title(f"{i * per_panel + 1}-{i * per_panel + len(subset)} of {len(rows)} observations", loc="left", fontsize=11)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    # Reserve title/legend space in physical inches, including single-panel figures.
    fig.suptitle(title, fontsize=16, y=1 - 0.1 / height)
    fig.text(0.5, 1 - 0.56 / height, subtitle, ha="center", fontsize=10)
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1 - 0.82 / height), ncol=4, frameon=False, fontsize=10)
    fig.text(0.5, 0.015, footer, ha="center", va="bottom", fontsize=9)
    fig.tight_layout(rect=(0.015, 0.55 / height, 0.99, 1 - 1.25 / height), h_pad=2.1)
    for ext in ("png", "pdf"):
        fig.savefig(DEST / f"{name}.{ext}", dpi=170)
    plt.close(fig)


def draw_singletons(ax, rows, labels):
    for j, (key, (label, color, marker)) in enumerate(zip(METRICS, SERIES)):
        xs = [i + (j - 1) * 0.14 for i in range(len(rows))]
        ys = [r[key] for r in rows]
        ax.scatter(xs, ys, color=color, marker=marker, s=65, label=label)
        for x, y in zip(xs, ys):
            ax.annotate(str(y), (x, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=11)
    ax.set_xticks(range(len(rows)), labels, fontsize=10)
    ax.set_xlim(-0.5, len(rows) - 0.5)
    ax.set_ylim(0, 30)
    ax.set_ylabel("Correct cases / 50")
    ax.grid(axis="y", alpha=0.2)


def plots(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": "white", "axes.facecolor": "white"})
    luna, gpt, early, broader = validate(rows)
    fixed = "medium | workers=4 | 3 fresh sessions/case | max 2 attempts/stage | identical GAIA-50"
    line_figure(plt, luna, "01-luna-gaia50-fixed-three-stage",
                "Luna / Codex SDK family: fixed three-stage history", fixed,
                "Execution: host-orchestrated Codex agents, not SDK package calls; host/backend snapshots unrecorded.\n31 scored versions. Unscored, replayed and audit-rejected runs are not interpolated or counted as zero.", per_panel=16)
    line_figure(plt, gpt, "02-gpt55-gaia50-fixed-three-stage",
                "GPT-5.5 / Codex SDK family: fixed three-stage history", fixed,
                "Execution: host-orchestrated Codex agents. 4 scored versions; no SDK package invocation claim.\nv3.85 (high), v3.89 (mixed), v3.102 (3 attempts), and app-server runs are different configurations.")
    line_figure(plt, early, "03-luna-gaia30-fixed-case-session",
                "Luna / Codex SDK family: GAIA-smoke30 history",
                "medium | workers=4 | 1 fresh session/case | max 2 attempts/case | identical 30 cases",
                "Execution: host-orchestrated Codex agents. 13 scored versions.\nGAIA-50 is a different cohort; v3.12 uses 3 sessions and is a separate group.")
    line_figure(plt, broader, "05-luna-gaia50-runtime-only",
                "Luna / medium / Codex SDK family / GAIA-50",
                "workers=4 | max 2 attempts/stage | stage count varies: NOT a fixed total-call-budget curve",
                "Execution: host-orchestrated Codex agents. All 47 eligible fresh per-stage runs.\nThe per-case v3.4 baseline is separate; audit-rejected v3.61/v3.62/v3.64/v3.65 remain in the inventory.", per_panel=24)
    by_id = {r["id"]: r for r in rows}
    fig, axes = plt.subplots(2, 1, figsize=(10, 8.5))
    draw_singletons(axes[0], [by_id["R216"], by_id["R219"]],
                    ["v3.107 (R216)\n2026-08-31\n2 semantic attempts/stage",
                     "Official SDK v3 (R219)\n2026-09-03\n1 semantic attempt/call"])
    axes[0].set_title("Codex SDK family: app-server 0.147.0 / GPT-5.5 medium / workers=4", loc="left", fontsize=12)
    axes[0].set_xlabel("Different retry + output contracts and method branches: no connecting line")
    axes[0].legend(ncol=3, frameon=False, fontsize=10, loc="upper right")
    draw_singletons(axes[1], [by_id["R150"], by_id["R154"]],
                    ["Official topology v1 (R150)\ntimeout=180 s", "Strict v8.2 (R154)\ntimeout=240 s"])
    axes[1].set_title("GPT-4.1 / API / temperature=0 / workers=4", loc="left", fontsize=13)
    axes[1].set_xlabel("Different timeouts/contracts: same model alone does not establish fixed configuration")
    fig.suptitle("Same model, but insufficient matched-config iteration evidence", fontsize=15, y=0.99)
    fig.text(0.5, 0.012, "App-server v1, v2 and v3.104 have no archived formal score; missing results are NOT zero.\nThe Codex SDK family also includes host-agent runs in Figures 1-3. These points are not a learning curve.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0.02, 0.08, 0.99, 0.96), h_pad=2.5)
    for ext in ("png", "pdf"):
        fig.savefig(DEST / f"04-sdk-and-api-unmatched-comparisons.{ext}", dpi=170)
    plt.close(fig)

    groups = defaultdict(list)
    for r in rows:
        groups[r["fixed_config_id"]].append(r)
    # Exhaustive appendix: every GAIA-50 and GAIA-smoke30 record appears exactly once.
    with PdfPages(DEST / "06-all-gaia-config-groups.pdf") as pdf:
        for ident, values in groups.items():
            for start in range(0, len(values), 18):
                part = values[start:start + 18]
                fig, ax = plt.subplots(figsize=(11, 5.5))
                usable = [r for r in part if r["eligible"] and r["fresh_end_to_end"] and r["recorded_at"]]
                xs = {r["id"]: i for i, r in enumerate(part)}
                for key, (label, color, marker) in zip(METRICS, SERIES):
                    ax.plot([xs[r["id"]] for r in usable], [r[key] for r in usable], color=color,
                            marker=marker, label=label, linewidth=1.4)
                for r in part:
                    if r not in usable:
                        ax.scatter([xs[r["id"]]] * 3, [r[k] for k in METRICS], marker="x", color="#777777")
                ax.set_xticks(range(len(part)), [version(r) + "\n" + r["id"] for r in part], rotation=90 if len(part) > 6 else 0, fontsize=9)
                ax.set_xlim(-0.6, len(part) - 0.4)
                ax.set_ylim(0, 35)
                ax.set_ylabel(f"Correct cases / {part[0]['n']}")
                ax.set_xlabel("Recorded evaluation order; gray crosses are ineligible/replayed/unordered")
                c = part[0]["fixed_config"]
                ax.set_title(f"{ident} | {part[0]['group']} | {part[0]['method_family']} family | {part[0]['transport']}\n"
                             f"models/efforts={c['models_and_efforts']}\n"
                             f"sessions/case={c['planned_fresh_sessions_per_case']}; "
                             f"attempts/{c['semantic_attempt_unit']}={c['max_semantic_attempts']}; workers={c['workers']}", fontsize=10)
                ax.grid(axis="y", alpha=0.2)
                ax.legend(ncol=3, frameon=False, loc="upper right", fontsize=9)
                fig.text(0.5, 0.018, "Exact group key and all omitted/unknown fields: fixed-config-records.json.\nUnknown runtime/backend metadata is not proof of identical execution environments.", ha="center", fontsize=9)
                fig.tight_layout(rect=(0.01, 0.08, 0.99, 0.99))
                pdf.savefig(fig)
                plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--refresh-sdk-evidence", action="store_true")
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    all_rows = json.loads(HISTORY.read_text())
    rows = [r for r in all_rows if r["group"] in ("GAIA-50", "GAIA-smoke-30")]
    supplement = read_supplement(rows, args.refresh_sdk_evidence)
    for r in rows:
        r["fixed_config"] = configuration(r, supplement)
        r["fixed_config_id"] = config_id(r["fixed_config"])
    luna, gpt, early, broader = validate(rows)
    fields = ["id", "name", "group", "recorded_at", "method_family", "execution_backend", "transport", "model", "reasoning_effort",
              "fixed_config_id", "step_exact", "step_module_exact", "all_correct", "n", "failed_outputs",
              "status", "eligible", "fresh_end_to_end", "semantic_parent", "mechanism", "metrics_path"]
    reduced = [{k: r[k] for k in fields + ["fixed_config"]} for r in rows]
    dump(DEST / "fixed-config-records.json", reduced)
    with (DEST / "fixed-config-records.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields + ["fixed_config"])
        writer.writeheader()
        for r in reduced:
            writer.writerow(r | {"fixed_config": json.dumps(r["fixed_config"], ensure_ascii=False, sort_keys=True)})
    groups = defaultdict(list)
    for r in rows:
        groups[r["fixed_config_id"]].append(r["id"])
    summary = {
        "source_archive": str(HISTORY.relative_to(ROOT)), "source_archive_sha256": sha(HISTORY),
        "scope": ["GAIA-50", "GAIA-smoke-30"], "record_count": len(rows),
        "group_count": len(groups), "groups": dict(groups),
        "main_series": {name: [r["id"] for r in values] for name, values in (
            ("luna_gaia50_three_stage", luna), ("gpt55_gaia50_three_stage", gpt),
            ("luna_gaia30_case_session", early), ("luna_gaia50_variable_stage_count", broader))},
        "provider_ignored_for_grouping": True,
        "null_or_missing_means": "not independently established; not proof that defaults/backends matched",
        "new_model_inference": False,
        "interpretation": "recorded-config matched observations, not causal estimates, constant-token-budget trials, or a parent-child genealogy",
    }
    dump(DEST / "verification-summary.json", summary)
    if not args.no_plots:
        plots(rows)
    dump(DEST / "figure-manifest.json", {
        "source_archive_sha256": sha(HISTORY), "plot_script_sha256": sha(Path(__file__)),
        "files": {p.name: sha(p) for p in sorted(DEST.iterdir())
                  if p.is_file() and p.name not in ("figure-manifest.json", "README.md")},
    })
    print(json.dumps({"records": len(rows), "groups": len(groups),
                      "main_series_lengths": [len(x) for x in (luna, gpt, early, broader)],
                      "source_archive_unchanged": sha(HISTORY) == summary["source_archive_sha256"],
                      "new_model_inference": False}, indent=2))


if __name__ == "__main__":
    main()
