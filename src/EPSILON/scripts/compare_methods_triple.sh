#!/usr/bin/env bash
set -euo pipefail

PLAYGROUND="highway_v1.0"
DURATION=60
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""
AI_DESIRED_VEL=10.0
AI_AUTONOMOUS_LEVEL=2
AI_AGGRESSIVENESS_LEVEL=4
EUDM_AI_CONFIG=""
EUDM_BASE_CONFIG=""

usage() {
  cat <<USAGE
Usage: $0 [--playground NAME] [--duration SEC] [--workspace PATH] [--out-root PATH] [--ai-desired-vel MPS] [--ai-autonomous-level N] [--ai-aggressiveness-level N] [--eudm-ai-config PATH] [--eudm-base-config PATH]
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
    --ai-desired-vel)
      AI_DESIRED_VEL="$2"; shift 2 ;;
    --ai-autonomous-level)
      AI_AUTONOMOUS_LEVEL="$2"; shift 2 ;;
    --ai-aggressiveness-level)
      AI_AGGRESSIVENESS_LEVEL="$2"; shift 2 ;;
    --eudm-ai-config)
      EUDM_AI_CONFIG="$2"; shift 2 ;;
    --eudm-base-config)
      EUDM_BASE_CONFIG="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="$WORKSPACE/results/compare3_${PLAYGROUND}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

if [[ -z "$EUDM_AI_CONFIG" ]]; then
  EUDM_AI_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config.pb.txt"
fi
if [[ -z "$EUDM_BASE_CONFIG" ]]; then
  EUDM_BASE_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config_baseline.pb.txt"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/run_stack.sh" --method eudm --playground "$PLAYGROUND" --duration "$DURATION" --workspace "$WORKSPACE" --out-dir "$OUT_ROOT/eudm_ai" --ai-desired-vel "$AI_DESIRED_VEL" --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" --ai-aggressiveness-level "$AI_AGGRESSIVENESS_LEVEL" --eudm-bp-config "$EUDM_AI_CONFIG"
"$SCRIPT_DIR/run_stack.sh" --method eudm --playground "$PLAYGROUND" --duration "$DURATION" --workspace "$WORKSPACE" --out-dir "$OUT_ROOT/eudm_base" --ai-desired-vel "$AI_DESIRED_VEL" --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" --ai-aggressiveness-level "$AI_AGGRESSIVENESS_LEVEL" --eudm-bp-config "$EUDM_BASE_CONFIG"
"$SCRIPT_DIR/run_stack.sh" --method mpdm --playground "$PLAYGROUND" --duration "$DURATION" --workspace "$WORKSPACE" --out-dir "$OUT_ROOT/mpdm" --ai-desired-vel "$AI_DESIRED_VEL" --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" --ai-aggressiveness-level "$AI_AGGRESSIVENESS_LEVEL"

python3 - <<PY
import json
from pathlib import Path

root = Path(r"$OUT_ROOT")
ai = json.loads((root / "eudm_ai" / "metrics.json").read_text())
base = json.loads((root / "eudm_base" / "metrics.json").read_text())
mpdm = json.loads((root / "mpdm" / "metrics.json").read_text())

rows = [
    ("unsafe_ratio", ai["unsafe_ratio"], base["unsafe_ratio"], mpdm["unsafe_ratio"]),
    ("average_velocity_mps", ai["average_velocity_mps"], base["average_velocity_mps"], mpdm["average_velocity_mps"]),
    ("ud_per_km", ai["ud_per_km"], base["ud_per_km"], mpdm["ud_per_km"]),
    ("lcc_per_km", ai["lcc_per_km"], base["lcc_per_km"], mpdm["lcc_per_km"]),
    ("distance_m", ai["distance_m"], base["distance_m"], mpdm["distance_m"]),
    ("frames", ai["frames"], base["frames"], mpdm["frames"]),
]

report = root / "summary.csv"
with report.open("w", encoding="utf-8") as f:
    f.write("metric,eudm_ai,eudm_base,mpdm\n")
    for k, a, b, m in rows:
        f.write(f"{k},{a},{b},{m}\n")
print(report)
PY

echo "[INFO] Triple-method comparison completed under: $OUT_ROOT"
