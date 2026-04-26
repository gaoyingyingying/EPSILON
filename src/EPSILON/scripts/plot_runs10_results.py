#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


METRICS = [
    ("unsafe_ratio", "Safety: Unsafe Ratio (lower is better)"),
    ("average_velocity_mps", "Efficiency: Average Velocity (m/s, higher is better)"),
    ("ud_per_km", "Comfort: UD per km (lower is better)"),
    ("lcc_per_km", "Comfort: LCC per km (lower is better)"),
]


def parse_aggregate_summary(csv_path: Path):
    data = {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metric = row["metric"]
            method = row["method"]
            mean = float(row["mean"])
            std = float(row["std"])
            data[(metric, method)] = (mean, std)
    return data


def plot_metric_bars(metric_key, metric_title, map_order, all_data, out_path: Path):
    x = np.arange(len(map_order))
    width = 0.36

    eudm_means = [all_data[m][(metric_key, "eudm")][0] for m in map_order]
    eudm_stds = [all_data[m][(metric_key, "eudm")][1] for m in map_order]
    mpdm_means = [all_data[m][(metric_key, "mpdm")][0] for m in map_order]
    mpdm_stds = [all_data[m][(metric_key, "mpdm")][1] for m in map_order]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(
        x - width / 2,
        eudm_means,
        width,
        yerr=eudm_stds,
        label="EUDM",
        color="#2E86AB",
        capsize=4,
    )
    ax.bar(
        x + width / 2,
        mpdm_means,
        width,
        yerr=mpdm_stds,
        label="MPDM",
        color="#F18F01",
        capsize=4,
    )

    ax.set_title(metric_title, fontsize=13, pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(map_order, rotation=0)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_safety_efficiency_scatter(map_order, all_data, out_path: Path):
    fig, ax = plt.subplots(figsize=(8, 6))

    for method, color in [("eudm", "#2E86AB"), ("mpdm", "#F18F01")]:
        xs = [all_data[m][("unsafe_ratio", method)][0] for m in map_order]
        ys = [all_data[m][("average_velocity_mps", method)][0] for m in map_order]
        xerr = [all_data[m][("unsafe_ratio", method)][1] for m in map_order]
        yerr = [all_data[m][("average_velocity_mps", method)][1] for m in map_order]

        ax.errorbar(
            xs,
            ys,
            xerr=xerr,
            yerr=yerr,
            fmt="o",
            color=color,
            capsize=3,
            label=method.upper(),
            alpha=0.9,
        )
        for i, map_name in enumerate(map_order):
            ax.annotate(
                map_name,
                (xs[i], ys[i]),
                textcoords="offset points",
                xytext=(6, 4),
                fontsize=8,
            )

    ax.set_xlabel("Unsafe Ratio (lower is better)")
    ax.set_ylabel("Average Velocity (m/s, higher is better)")
    ax.set_title("Safety-Efficiency Trade-off (mean ± std)")
    ax.grid(linestyle="--", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Plot EPSILON repeated-run results.")
    parser.add_argument("--output-dir", required=True, help="Output directory for figures")
    parser.add_argument(
        "--map-root",
        action="append",
        nargs=2,
        metavar=("MAP_NAME", "RESULT_ROOT"),
        required=True,
        help="Map name and repeated-run result root (contains aggregate_summary.csv)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    map_order = []
    all_data = {}
    for map_name, result_root in args.map_root:
        map_order.append(map_name)
        agg_csv = Path(result_root) / "aggregate_summary.csv"
        if not agg_csv.exists():
            raise FileNotFoundError(f"Missing file: {agg_csv}")
        all_data[map_name] = parse_aggregate_summary(agg_csv)

    for metric_key, metric_title in METRICS:
        out = output_dir / f"{metric_key}_bar.png"
        plot_metric_bars(metric_key, metric_title, map_order, all_data, out)
        print(out)

    scatter_out = output_dir / "safety_efficiency_tradeoff.png"
    plot_safety_efficiency_scatter(map_order, all_data, scatter_out)
    print(scatter_out)


if __name__ == "__main__":
    main()
