#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


METRICS = ("unsafe_ratio", "average_velocity_mps", "ud_per_km", "lcc_per_km")
METHODS = ("eudm_ai", "eudm_base", "mpdm")
METHOD_LABELS = {
    "eudm_ai": "主动推理决策",
    "eudm_base": "原始EUDM",
    "mpdm": "MPDM基线",
}
SCENARIO_LABELS = {
    "highway_v1.0_lt_fast_rear_approach": "后方高速逼近",
    "highway_v1.0_lt_merge_squeeze": "合流夹挤",
}
METHOD_PLOT_LABELS = {
    "eudm_ai": "Active inference",
    "eudm_base": "EUDM baseline",
    "mpdm": "MPDM",
}
SCENARIO_PLOT_LABELS = {
    "highway_v1.0_lt_fast_rear_approach": "Fast rear approach",
    "highway_v1.0_lt_merge_squeeze": "Merge squeeze",
}


def load_stats(result_dir: Path):
    path = result_dir / "aggregate_stats.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing aggregate stats: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def stat(stats, metric, method, field="mean"):
    return stats["metrics"][metric][method][field]


def fmt_pm(stats, metric, method):
    mean = stat(stats, metric, method, "mean")
    std = stat(stats, metric, method, "std")
    return f"{mean:.6f} +- {std:.6f}"


def collect_rows(root: Path):
    rows = []
    for scenario_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        scenario = scenario_dir.name
        for agg_dir in sorted(p for p in scenario_dir.iterdir() if p.is_dir() and p.name.startswith("agg_")):
            aggr = agg_dir.name.replace("agg_", "")
            if not aggr.isdigit() or not (agg_dir / "aggregate_stats.json").exists():
                continue
            stats = load_stats(agg_dir)
            for method in METHODS:
                rows.append(
                    {
                        "scenario": scenario,
                        "scenario_label": SCENARIO_LABELS.get(scenario, scenario),
                        "aggressiveness": int(aggr),
                        "method": method,
                        "method_label": METHOD_LABELS[method],
                        "runs": stats["runs"],
                        "unsafe_ratio": stat(stats, "unsafe_ratio", method),
                        "unsafe_ratio_pm": fmt_pm(stats, "unsafe_ratio", method),
                        "average_velocity_mps": stat(stats, "average_velocity_mps", method),
                        "average_velocity_mps_pm": fmt_pm(stats, "average_velocity_mps", method),
                        "ud_per_km": stat(stats, "ud_per_km", method),
                        "ud_per_km_pm": fmt_pm(stats, "ud_per_km", method),
                        "lcc_per_km": stat(stats, "lcc_per_km", method),
                        "lcc_per_km_pm": fmt_pm(stats, "lcc_per_km", method),
                    }
                )
    return rows


def write_csv(rows, out_dir: Path):
    raw_path = out_dir / "table_iv_style_main.csv"
    with raw_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "scenario",
                "scenario_label",
                "aggressiveness",
                "method",
                "method_label",
                "runs",
                "unsafe_ratio",
                "average_velocity_mps",
                "ud_per_km",
                "lcc_per_km",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    paper_path = out_dir / "table_iv_style_main_pm.csv"
    with paper_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Scenario",
                "Aggressiveness",
                "Method",
                "Runs",
                "Safety unsafe ratio ↓",
                "Efficiency avg vel m/s ↑",
                "Comfort UD/km ↓",
                "Comfort LCC/km ↓",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["scenario_label"],
                    row["aggressiveness"],
                    row["method_label"],
                    row["runs"],
                    row["unsafe_ratio_pm"],
                    row["average_velocity_mps_pm"],
                    row["ud_per_km_pm"],
                    row["lcc_per_km_pm"],
                ]
            )
    return raw_path, paper_path


def write_markdown(rows, out_dir: Path):
    md_path = out_dir / "REPORT_decision_model_table_iv.md"
    lines = [
        "# 主动推理决策小规模复现实验",
        "",
        "## 实验设置",
        "",
        "- 场景：`highway_v1.0_lt_fast_rear_approach`、`highway_v1.0_lt_merge_squeeze`",
        "- 方法：`主动推理决策`、`原始EUDM`、`MPDM基线`",
        "- 参数：`aggressiveness=3/5/7`",
        "- 每组：`5 runs × 120s`",
        "- 指标参考 EPSILON 原论文 Table IV：安全与效率为主，补充舒适性指标。",
        "",
        "## Table-IV 风格主表",
        "",
        "| Scenario | Aggressiveness | Method | Runs | Safety unsafe ratio ↓ | Efficiency avg vel m/s ↑ | UD/km ↓ | LCC/km ↓ |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {scenario} | {aggr} | {method} | {runs} | {unsafe} | {vel} | {ud} | {lcc} |".format(
                scenario=row["scenario_label"],
                aggr=row["aggressiveness"],
                method=row["method_label"],
                runs=row["runs"],
                unsafe=row["unsafe_ratio_pm"],
                vel=row["average_velocity_mps_pm"],
                ud=row["ud_per_km_pm"],
                lcc=row["lcc_per_km_pm"],
            )
        )
    lines.extend(
        [
            "",
            "## 输出文件",
            "",
            "- `table_iv_style_main.csv`：机器可读主表",
            "- `table_iv_style_main_pm.csv`：论文表格口径",
            "- `safety_efficiency_by_aggressiveness.png`：安全-效率折线图",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def plot_safety_efficiency(rows, out_dir: Path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"eudm_ai": "#1b9e77", "eudm_base": "#d95f02", "mpdm": "#4b5cc4"}
    markers = {"eudm_ai": "o", "eudm_base": "s", "mpdm": "^"}
    scenarios = sorted({row["scenario"] for row in rows})

    fig, axes = plt.subplots(1, len(scenarios), figsize=(6 * len(scenarios), 4.8), squeeze=False)
    for ax, scenario in zip(axes[0], scenarios):
        sub = [row for row in rows if row["scenario"] == scenario]
        for method in METHODS:
            pts = sorted((row for row in sub if row["method"] == method), key=lambda r: r["aggressiveness"])
            xs = [row["unsafe_ratio"] for row in pts]
            ys = [row["average_velocity_mps"] for row in pts]
            labels = [str(row["aggressiveness"]) for row in pts]
            ax.plot(xs, ys, marker=markers[method], color=colors[method], label=METHOD_PLOT_LABELS[method], linewidth=2)
            for x, y, label in zip(xs, ys, labels):
                ax.annotate(label, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)
        ax.set_title(SCENARIO_PLOT_LABELS.get(scenario, scenario))
        ax.set_xlabel("Unsafe ratio (lower is better)")
        ax.set_ylabel("Average velocity m/s (higher is better)")
        ax.grid(True, alpha=0.3)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(METHODS))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out_path = out_dir / "safety_efficiency_by_aggressiveness.png"
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Summarize the decision-model Table-IV style experiment.")
    parser.add_argument("--root", required=True, help="Experiment root containing scenario/agg_* result directories")
    args = parser.parse_args()

    root = Path(args.root)
    rows = collect_rows(root)
    if not rows:
        raise RuntimeError(f"No summarized rows found under {root}")
    rows.sort(key=lambda r: (r["scenario"], r["aggressiveness"], METHODS.index(r["method"])))

    raw_csv, pm_csv = write_csv(rows, root)
    md = write_markdown(rows, root)
    plot = plot_safety_efficiency(rows, root)
    print(raw_csv)
    print(pm_csv)
    print(md)
    print(plot)


if __name__ == "__main__":
    main()
