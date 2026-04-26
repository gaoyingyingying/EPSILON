#!/usr/bin/env python3
import argparse
import csv
import json
import math
from pathlib import Path


METRICS = [
    "unsafe_ratio",
    "average_velocity_mps",
    "ud_per_km",
    "lcc_per_km",
    "distance_m",
    "frames",
]


def load_run_metrics(run_root: Path):
    data = {}
    for method in ("eudm", "mpdm"):
        metrics_path = run_root / method / "metrics.json"
        if not metrics_path.exists():
            raise FileNotFoundError(f"Missing metrics file: {metrics_path}")
        data[method] = json.loads(metrics_path.read_text(encoding="utf-8"))
    return data


def calc_stats(values):
    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance)
    return {
        "count": n,
        "mean": mean,
        "variance": variance,
        "std": std,
    }


def format_mean_variance(stats):
    return f"{stats['mean']:.6f} +- {stats['variance']:.6f}"


def format_mean_std(stats):
    return f"{stats['mean']:.6f} +- {stats['std']:.6f}"


def main():
    parser = argparse.ArgumentParser(description="Aggregate repeated EUDM/MPDM runs")
    parser.add_argument("--root", required=True, help="Batch result root directory")
    args = parser.parse_args()

    root = Path(args.root)
    run_dirs = sorted(
        [p for p in root.iterdir() if p.is_dir() and p.name.startswith("run_")]
    )
    if not run_dirs:
        raise FileNotFoundError(f"No run_* directories found under {root}")

    runs = [load_run_metrics(run_dir) for run_dir in run_dirs]

    aggregate = {"runs": len(runs), "metrics": {}}
    for metric in METRICS:
        aggregate["metrics"][metric] = {}
        for method in ("eudm", "mpdm"):
            values = [run[method][metric] for run in runs]
            aggregate["metrics"][metric][method] = calc_stats(values)

    json_path = root / "aggregate_stats.json"
    json_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = root / "aggregate_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "metric",
                "method",
                "count",
                "mean",
                "variance",
                "std",
                "mean_pm_variance",
                "mean_pm_std",
            ]
        )
        for metric in METRICS:
            for method in ("eudm", "mpdm"):
                stats = aggregate["metrics"][metric][method]
                writer.writerow(
                    [
                        metric,
                        method,
                        stats["count"],
                        stats["mean"],
                        stats["variance"],
                        stats["std"],
                        format_mean_variance(stats),
                        format_mean_std(stats),
                    ]
                )

    table_var_path = root / "table1_style_variance.csv"
    table_std_path = root / "table1_style_std.csv"
    label_map = {
        "unsafe_ratio": "Safety (unsafe ratio, ↓)",
        "average_velocity_mps": "Efficiency (Ave. Vel m/s, ↑)",
        "ud_per_km": "Comfort UD (/km, ↓)",
        "lcc_per_km": "Comfort LCC (/km, ↓)",
    }
    with table_var_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method"] + list(label_map.values()))
        for method in ("eudm", "mpdm"):
            row = [method.upper()]
            for metric in label_map:
                row.append(format_mean_variance(aggregate["metrics"][metric][method]))
            writer.writerow(row)

    with table_std_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method"] + list(label_map.values()))
        for method in ("eudm", "mpdm"):
            row = [method.upper()]
            for metric in label_map:
                row.append(format_mean_std(aggregate["metrics"][metric][method]))
            writer.writerow(row)

    print(json_path)
    print(csv_path)
    print(table_var_path)
    print(table_std_path)


if __name__ == "__main__":
    main()
