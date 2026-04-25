#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def load_table(table_path: Path):
    rows = []
    with table_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Aggregate multiple map table1_style_std.csv files")
    parser.add_argument("--output-dir", required=True, help="Directory to write merged tables into")
    parser.add_argument(
        "--map-root",
        action="append",
        nargs=2,
        metavar=("MAP_NAME", "RESULT_ROOT"),
        required=True,
        help="Map name and repeated-run result root",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    merged_rows = []
    for map_name, result_root in args.map_root:
        root = Path(result_root)
        table_path = root / "table1_style_std.csv"
        if not table_path.exists():
            raise FileNotFoundError(f"Missing table file: {table_path}")
        rows = load_table(table_path)
        for row in rows:
            merged_rows.append(
                {
                    "Map": map_name,
                    "Method": row["Method"],
                    "Safety (unsafe ratio, ↓)": row["Safety (unsafe ratio, ↓)"],
                    "Efficiency (Ave. Vel m/s, ↑)": row["Efficiency (Ave. Vel m/s, ↑)"],
                    "Comfort UD (/km, ↓)": row["Comfort UD (/km, ↓)"],
                    "Comfort LCC (/km, ↓)": row["Comfort LCC (/km, ↓)"],
                    "Result Root": str(root),
                }
            )

    csv_path = output_dir / "multi_map_table1_std.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Map",
                "Method",
                "Safety (unsafe ratio, ↓)",
                "Efficiency (Ave. Vel m/s, ↑)",
                "Comfort UD (/km, ↓)",
                "Comfort LCC (/km, ↓)",
                "Result Root",
            ],
        )
        writer.writeheader()
        writer.writerows(merged_rows)

    markdown_path = output_dir / "multi_map_table1_std.md"
    with markdown_path.open("w", encoding="utf-8") as f:
        f.write("| Map | Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for row in merged_rows:
            f.write(
                f"| {row['Map']} | {row['Method']} | "
                f"{row['Safety (unsafe ratio, ↓)']} | "
                f"{row['Efficiency (Ave. Vel m/s, ↑)']} | "
                f"{row['Comfort UD (/km, ↓)']} | "
                f"{row['Comfort LCC (/km, ↓)']} |\n"
            )

    print(csv_path)
    print(markdown_path)


if __name__ == "__main__":
    main()
