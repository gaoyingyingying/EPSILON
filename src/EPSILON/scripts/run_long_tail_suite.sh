#!/usr/bin/env bash
set -euo pipefail

DURATION=120
RUNS=3
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""
SLEEP_BETWEEN=3

usage() {
  cat <<USAGE
Usage: $0 [--duration SEC] [--runs N] [--workspace PATH] [--out-root PATH] [--sleep-between SEC]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --duration)
      DURATION="$2"; shift 2 ;;
    --runs)
      RUNS="$2"; shift 2 ;;
    --workspace)
      WORKSPACE="$2"; shift 2 ;;
    --out-root)
      OUT_ROOT="$2"; shift 2 ;;
    --sleep-between)
      SLEEP_BETWEEN="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$WORKSPACE/src/EPSILON/core/playgrounds/long_tail_manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  "$SCRIPT_DIR/generate_long_tail_playgrounds.py"
fi

if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="$WORKSPACE/results/long_tail_suite_runs${RUNS}_dur${DURATION}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

mapfile -t SCENARIOS < <(python3 - "$MANIFEST" <<'PY'
import json
import sys

data = json.loads(open(sys.argv[1], encoding="utf-8").read())
for item in data["scenarios"]:
    print(
        "{name}\t{vel}\t{auto}\t{agg}".format(
            name=item["name"],
            vel=item["ai_desired_vel"],
            auto=item["ai_autonomous_level"],
            agg=item["ai_aggressiveness_level"],
        )
    )
PY
)

MAP_ROOT_ARGS=()
for row in "${SCENARIOS[@]}"; do
  IFS=$'\t' read -r PLAYGROUND AI_DESIRED_VEL AI_AUTONOMOUS_LEVEL AI_AGGRESSIVENESS_LEVEL <<<"$row"
  RESULT_ROOT="$OUT_ROOT/$PLAYGROUND"
  echo "[INFO] Long-tail scenario: $PLAYGROUND -> $RESULT_ROOT"
  "$SCRIPT_DIR/repeat_compare_methods.sh" \
    --playground "$PLAYGROUND" \
    --duration "$DURATION" \
    --runs "$RUNS" \
    --workspace "$WORKSPACE" \
    --out-root "$RESULT_ROOT" \
    --sleep-between "$SLEEP_BETWEEN" \
    --ai-desired-vel "$AI_DESIRED_VEL" \
    --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" \
    --ai-aggressiveness-level "$AI_AGGRESSIVENESS_LEVEL"
  MAP_ROOT_ARGS+=(--map-root "$PLAYGROUND" "$RESULT_ROOT")
done

python3 "$SCRIPT_DIR/aggregate_multi_map_tables.py" \
  --output-dir "$OUT_ROOT/summary" \
  "${MAP_ROOT_ARGS[@]}"

echo "[INFO] Long-tail suite completed under: $OUT_ROOT"
