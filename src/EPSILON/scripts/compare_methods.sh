#!/usr/bin/env bash
set -euo pipefail

PLAYGROUND="highway_v1.0"
DURATION=60
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""

usage() {
  cat <<USAGE
Usage: $0 [--playground NAME] [--duration SEC] [--workspace PATH] [--out-root PATH]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --playground)
      PLAYGROUND="$2"; shift 2 ;;
    --duration)
      DURATION="$2"; shift 2 ;;
    --workspace)
      WORKSPACE="$2"; shift 2 ;;
    --out-root)
      OUT_ROOT="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="$WORKSPACE/results/compare_${PLAYGROUND}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/run_stack.sh" --method eudm --playground "$PLAYGROUND" --duration "$DURATION" --workspace "$WORKSPACE" --out-dir "$OUT_ROOT/eudm"
"$SCRIPT_DIR/run_stack.sh" --method mpdm --playground "$PLAYGROUND" --duration "$DURATION" --workspace "$WORKSPACE" --out-dir "$OUT_ROOT/mpdm"

python3 - <<PY
import json
from pathlib import Path

root = Path(r"$OUT_ROOT")
e = json.loads((root / "eudm" / "metrics.json").read_text())
m = json.loads((root / "mpdm" / "metrics.json").read_text())

rows = [
    ("unsafe_ratio", e["unsafe_ratio"], m["unsafe_ratio"]),
    ("average_velocity_mps", e["average_velocity_mps"], m["average_velocity_mps"]),
    ("ud_per_km", e["ud_per_km"], m["ud_per_km"]),
    ("lcc_per_km", e["lcc_per_km"], m["lcc_per_km"]),
    ("distance_m", e["distance_m"], m["distance_m"]),
    ("frames", e["frames"], m["frames"]),
]

report = root / "summary.csv"
with report.open("w", encoding="utf-8") as f:
    f.write("metric,eudm,mpdm\n")
    for k, ev, mv in rows:
        f.write(f"{k},{ev},{mv}\n")
print(report)
PY

echo "[INFO] Comparison completed under: $OUT_ROOT"
