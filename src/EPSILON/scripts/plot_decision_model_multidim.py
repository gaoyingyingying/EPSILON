#!/usr/bin/env python3
import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METHODS = ("eudm_ai", "eudm_base", "mpdm")
METHOD_LABELS = {
    "eudm_ai": "Active inference",
    "eudm_base": "EUDM baseline",
    "mpdm": "MPDM",
}
METHOD_COLORS = {
    "eudm_ai": "#1b9e77",
    "eudm_base": "#d95f02",
    "mpdm": "#4b5cc4",
}
SCENARIO_LABELS = {
    "highway_v1.0_lt_fast_rear_approach": "Fast rear",
    "highway_v1.0_lt_merge_squeeze": "Merge squeeze",
}
METRIC_LABELS = {
    "unsafe_ratio": "Unsafe ratio",
    "average_velocity_mps": "Average velocity (m/s)",
    "ud_per_km": "UD per km",
    "lcc_per_km": "LCC per km",
}


def load_rows(csv_path: Path):
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["aggressiveness"] = int(row["aggressiveness"])
        for key in ("unsafe_ratio", "average_velocity_mps", "ud_per_km", "lcc_per_km"):
            row[key] = float(row[key])
    return rows


def sorted_groups(rows):
    groups = sorted({(row["scenario"], row["aggressiveness"]) for row in rows})
    return groups


def get_value(rows, scenario, aggr, method, metric):
    for row in rows:
        if row["scenario"] == scenario and row["aggressiveness"] == aggr and row["method"] == method:
            return row[metric]
    raise KeyError((scenario, aggr, method, metric))


def save_fig(fig, out_path: Path):
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    return out_path


def plot_grouped_metric(rows, metric, out_path):
    groups = sorted_groups(rows)
    x = np.arange(len(groups))
    width = 0.24
    fig, ax = plt.subplots(figsize=(12, 5.2))
    for idx, method in enumerate(METHODS):
        values = [get_value(rows, scenario, aggr, method, metric) for scenario, aggr in groups]
        ax.bar(
            x + (idx - 1) * width,
            values,
            width=width,
            color=METHOD_COLORS[method],
            label=METHOD_LABELS[method],
        )
    labels = [f"{SCENARIO_LABELS.get(s, s)}\nA={a}" for s, a in groups]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(METRIC_LABELS[metric])
    ax.set_title(f"{METRIC_LABELS[metric]} by scenario and aggressiveness")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    return save_fig(fig, out_path)


def plot_comfort(rows, out_path):
    groups = sorted_groups(rows)
    x = np.arange(len(groups))
    width = 0.24
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for ax, metric in zip(axes, ("ud_per_km", "lcc_per_km")):
        for idx, method in enumerate(METHODS):
            values = [get_value(rows, scenario, aggr, method, metric) for scenario, aggr in groups]
            ax.bar(
                x + (idx - 1) * width,
                values,
                width=width,
                color=METHOD_COLORS[method],
                label=METHOD_LABELS[method],
            )
        ax.set_ylabel(METRIC_LABELS[metric])
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_title("Comfort and behavior stability")
    labels = [f"{SCENARIO_LABELS.get(s, s)}\nA={a}" for s, a in groups]
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(labels)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=3, loc="lower center")
    fig.subplots_adjust(bottom=0.18)
    return save_fig(fig, out_path)


def plot_heatmap(rows, metric, out_path, cmap):
    groups = sorted_groups(rows)
    data = np.array(
        [[get_value(rows, scenario, aggr, method, metric) for scenario, aggr in groups] for method in METHODS]
    )
    fig, ax = plt.subplots(figsize=(12, 3.8))
    im = ax.imshow(data, aspect="auto", cmap=cmap)
    ax.set_yticks(np.arange(len(METHODS)))
    ax.set_yticklabels([METHOD_LABELS[m] for m in METHODS])
    ax.set_xticks(np.arange(len(groups)))
    ax.set_xticklabels([f"{SCENARIO_LABELS.get(s, s)}\nA={a}" for s, a in groups])
    ax.set_title(f"{METRIC_LABELS[metric]} heatmap")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.3f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    return save_fig(fig, out_path)


def plot_tradeoff(rows, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    scenarios = sorted({row["scenario"] for row in rows})
    markers = {3: "o", 5: "s", 7: "^"}
    for ax, scenario in zip(axes, scenarios):
        for method in METHODS:
            sub = sorted(
                [row for row in rows if row["scenario"] == scenario and row["method"] == method],
                key=lambda row: row["aggressiveness"],
            )
            xs = [row["unsafe_ratio"] for row in sub]
            ys = [row["average_velocity_mps"] for row in sub]
            ax.plot(xs, ys, color=METHOD_COLORS[method], linewidth=2, label=METHOD_LABELS[method])
            for row in sub:
                ax.scatter(
                    row["unsafe_ratio"],
                    row["average_velocity_mps"],
                    color=METHOD_COLORS[method],
                    marker=markers[row["aggressiveness"]],
                    s=80,
                    edgecolor="white",
                    linewidth=0.8,
                )
                ax.annotate(
                    f"A={row['aggressiveness']}",
                    (row["unsafe_ratio"], row["average_velocity_mps"]),
                    textcoords="offset points",
                    xytext=(5, 5),
                    fontsize=8,
                )
        ax.set_title(SCENARIO_LABELS.get(scenario, scenario))
        ax.set_xlabel("Unsafe ratio (lower is better)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Average velocity (m/s, higher is better)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.subplots_adjust(bottom=0.2)
    return save_fig(fig, out_path)


def mean_by_method(rows):
    summary = {}
    for method in METHODS:
        sub = [row for row in rows if row["method"] == method]
        summary[method] = {
            key: sum(row[key] for row in sub) / len(sub)
            for key in ("unsafe_ratio", "average_velocity_mps", "ud_per_km", "lcc_per_km")
        }
    return summary


def plot_radar(rows, out_path):
    summary = mean_by_method(rows)
    unsafe_max = max(v["unsafe_ratio"] for v in summary.values()) or 1.0
    vel_max = max(v["average_velocity_mps"] for v in summary.values()) or 1.0
    ud_max = max(v["ud_per_km"] for v in summary.values()) or 1.0
    lcc_max = max(v["lcc_per_km"] for v in summary.values()) or 1.0
    labels = ("Safety", "Efficiency", "Low UD", "Low LCC")
    angles = np.linspace(0, 2 * math.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(6.5, 6))
    ax = fig.add_subplot(111, polar=True)
    for method in METHODS:
        vals = summary[method]
        scores = [
            1.0 - vals["unsafe_ratio"] / unsafe_max,
            vals["average_velocity_mps"] / vel_max,
            1.0 - vals["ud_per_km"] / ud_max,
            1.0 - vals["lcc_per_km"] / lcc_max,
        ]
        scores = [max(0.0, min(1.0, v)) for v in scores]
        scores += scores[:1]
        ax.plot(angles, scores, color=METHOD_COLORS[method], linewidth=2, label=METHOD_LABELS[method])
        ax.fill(angles, scores, color=METHOD_COLORS[method], alpha=0.12)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_title("Normalized overall profile")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    return save_fig(fig, out_path)


def plot_dashboard(rows, out_path):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    metrics = ("unsafe_ratio", "average_velocity_mps", "ud_per_km", "lcc_per_km")
    summary = mean_by_method(rows)
    for ax, metric in zip(axes.ravel(), metrics):
        values = [summary[m][metric] for m in METHODS]
        ax.bar([METHOD_LABELS[m] for m in METHODS], values, color=[METHOD_COLORS[m] for m in METHODS])
        ax.set_title(METRIC_LABELS[metric])
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(axis="x", rotation=15)
    fig.suptitle("Overall method comparison", y=1.02)
    return save_fig(fig, out_path)


def write_index(paths, out_dir: Path):
    index = out_dir / "VISUALIZATION_INDEX.md"
    rels = [path.name for path in paths]
    lines = [
        "# Decision Model Visualization Index",
        "",
        "| Figure | Focus |",
        "|---|---|",
        "| `overall_dashboard.png` | Overall mean metrics by method |",
        "| `unsafe_ratio_grouped.png` | Safety grouped by scenario and aggressiveness |",
        "| `average_velocity_grouped.png` | Efficiency grouped by scenario and aggressiveness |",
        "| `comfort_grouped.png` | UD and LCC comfort/stability metrics |",
        "| `unsafe_ratio_heatmap.png` | Safety heatmap across all experiment cells |",
        "| `average_velocity_heatmap.png` | Efficiency heatmap across all experiment cells |",
        "| `safety_efficiency_tradeoff.png` | Safety-efficiency tradeoff curves |",
        "| `overall_radar.png` | Normalized multi-objective method profile |",
        "",
        "Generated files:",
        "",
    ]
    lines.extend(f"- `{rel}`" for rel in rels)
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index


def main():
    parser = argparse.ArgumentParser(description="Plot multidimensional decision model experiment figures.")
    parser.add_argument("--csv", required=True, help="Path to table_iv_style_main.csv")
    parser.add_argument("--out-dir", required=True, help="Output directory for plots")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = load_rows(csv_path)
    paths = [
        plot_dashboard(rows, out_dir / "overall_dashboard.png"),
        plot_grouped_metric(rows, "unsafe_ratio", out_dir / "unsafe_ratio_grouped.png"),
        plot_grouped_metric(rows, "average_velocity_mps", out_dir / "average_velocity_grouped.png"),
        plot_comfort(rows, out_dir / "comfort_grouped.png"),
        plot_heatmap(rows, "unsafe_ratio", out_dir / "unsafe_ratio_heatmap.png", "YlOrRd"),
        plot_heatmap(rows, "average_velocity_mps", out_dir / "average_velocity_heatmap.png", "YlGnBu"),
        plot_tradeoff(rows, out_dir / "safety_efficiency_tradeoff.png"),
        plot_radar(rows, out_dir / "overall_radar.png"),
    ]
    index = write_index(paths, out_dir)
    for path in paths:
        print(path)
    print(index)


if __name__ == "__main__":
    main()
