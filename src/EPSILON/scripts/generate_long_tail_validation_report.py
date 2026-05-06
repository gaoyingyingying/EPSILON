#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


METHODS = ("eudm_ai", "eudm_base", "mpdm")
DISPLAY = {"eudm_ai": "EUDM主动推理", "eudm_base": "原EUDM", "mpdm": "MPDM"}
METRIC_LABELS = {
    "unsafe_ratio": "Safety (unsafe ratio, ↓)",
    "average_velocity_mps": "Efficiency (Ave. Vel m/s, ↑)",
    "ud_per_km": "Comfort UD (/km, ↓)",
    "lcc_per_km": "Comfort LCC (/km, ↓)",
}


def fmt(v):
    return f"{v:.6f}"


def fmt_pm(mean, std):
    return f"{mean:.6f} +- {std:.6f}"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Generate long-tail validation report")
    parser.add_argument("--suite-root", required=True, help="Suite result root")
    parser.add_argument("--manifest", required=True, help="Long-tail manifest json")
    parser.add_argument("--base-map", required=True, help="Base map name to summarize")
    parser.add_argument("--output-md", required=True, help="Output markdown report path")
    args = parser.parse_args()

    suite_root = Path(args.suite_root)
    manifest = load_json(Path(args.manifest))
    scenarios = [s for s in manifest["scenarios"] if s["base"] == args.base_map]
    if not scenarios:
        raise RuntimeError(f"No scenarios found for base map: {args.base_map}")

    scenario_rows = []
    for s in scenarios:
        root = suite_root / s["name"]
        agg_path = root / "aggregate_stats.json"
        if not agg_path.exists():
            raise FileNotFoundError(f"Missing aggregated stats: {agg_path}")
        agg = load_json(agg_path)
        scenario_rows.append((s, root, agg))

    # Overall map-level summary: arithmetic mean over scenario means
    overall = {m: {k: 0.0 for k in METRIC_LABELS} for m in METHODS}
    for _, _, agg in scenario_rows:
        for metric in METRIC_LABELS:
            for method in METHODS:
                overall[method][metric] += agg["metrics"][metric][method]["mean"]
    n = float(len(scenario_rows))
    for method in METHODS:
        for metric in METRIC_LABELS:
            overall[method][metric] /= n

    overall_csv = suite_root / f"{args.base_map}_overall_mean_by_scenarios.csv"
    with overall_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Method"] + list(METRIC_LABELS.values()))
        for method in METHODS:
            writer.writerow([DISPLAY[method]] + [fmt(overall[method][k]) for k in METRIC_LABELS])

    lines = []
    lines.append(f"# 第一张图（{args.base_map}）长尾验证报告：EUDM主动推理 vs 原EUDM vs MPDM")
    lines.append("")
    lines.append("## 1. 验证范围与口径")
    lines.append("")
    lines.append(f"- 基础地图：`{args.base_map}`")
    lines.append(f"- 长尾场景数：`{len(scenario_rows)}`")
    lines.append(f"- 指标口径：`unsafe_ratio`、`average_velocity_mps`、`ud_per_km`、`lcc_per_km`")
    lines.append("- 方法对照：`EUDM主动推理`、`原EUDM`、`MPDM`")
    lines.append("- 说明：整图汇总采用“对各长尾场景均值再平均”的方式，强调跨场景稳健性。")
    lines.append("")
    lines.append("## 2. 整图汇总（按场景等权平均）")
    lines.append("")
    lines.append("| Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |")
    lines.append("|---|---:|---:|---:|---:|")
    for method in METHODS:
        lines.append(
            f"| {DISPLAY[method]} | {fmt(overall[method]['unsafe_ratio'])} | "
            f"{fmt(overall[method]['average_velocity_mps'])} | "
            f"{fmt(overall[method]['ud_per_km'])} | "
            f"{fmt(overall[method]['lcc_per_km'])} |"
        )
    lines.append("")
    lines.append(f"- 结构化汇总 CSV：`{overall_csv}`")
    lines.append("")
    lines.append("## 3. 分长尾场景结果与说明")
    lines.append("")

    for idx, (s, root, agg) in enumerate(scenario_rows, start=1):
        lines.append(f"### 3.{idx} `{s['name']}`")
        lines.append("")
        lines.append(f"- 长尾类型：{s['type']}")
        lines.append(f"- 风险机理：{s['risk']}")
        lines.append(f"- 验证重点：{s['verify']}")
        lines.append(
            f"- 周车参数：`desired_vel={s['ai_desired_vel']}`，`autonomous_level={s['ai_autonomous_level']}`，`aggressiveness={s['ai_aggressiveness_level']}`"
        )
        lines.append("")
        lines.append("| Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |")
        lines.append("|---|---:|---:|---:|---:|")
        for method in METHODS:
            lines.append(
                f"| {DISPLAY[method]} | "
                f"{fmt_pm(agg['metrics']['unsafe_ratio'][method]['mean'], agg['metrics']['unsafe_ratio'][method]['std'])} | "
                f"{fmt_pm(agg['metrics']['average_velocity_mps'][method]['mean'], agg['metrics']['average_velocity_mps'][method]['std'])} | "
                f"{fmt_pm(agg['metrics']['ud_per_km'][method]['mean'], agg['metrics']['ud_per_km'][method]['std'])} | "
                f"{fmt_pm(agg['metrics']['lcc_per_km'][method]['mean'], agg['metrics']['lcc_per_km'][method]['std'])} |"
            )
        lines.append("")
        lines.append(f"- 该场景结果目录：`{root}`")
        lines.append("")

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output_md)
    print(overall_csv)


if __name__ == "__main__":
    main()
