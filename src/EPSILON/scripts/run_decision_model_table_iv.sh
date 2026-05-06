#!/usr/bin/env bash
set -euo pipefail

DURATION=120
RUNS=5
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""
SLEEP_BETWEEN=3
EUDM_AI_CONFIG=""
EUDM_BASE_CONFIG=""

usage() {
  cat <<USAGE
Usage: $0 [--duration SEC] [--runs N] [--workspace PATH] [--out-root PATH] [--sleep-between SEC] [--eudm-ai-config PATH] [--eudm-base-config PATH]

Runs the small Table-IV-style decision-model experiment:
  scenarios: highway_v1.0_lt_fast_rear_approach, highway_v1.0_lt_merge_squeeze
  methods: active-inference EUDM, baseline EUDM, MPDM
  aggressiveness: 3, 5, 7
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

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="$WORKSPACE/results/decision_model_table_iv_runs${RUNS}_dur${DURATION}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

if [[ -z "$EUDM_AI_CONFIG" ]]; then
  EUDM_AI_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config.pb.txt"
fi
if [[ -z "$EUDM_BASE_CONFIG" ]]; then
  EUDM_BASE_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config_baseline.pb.txt"
fi

SCENARIOS=(
  "highway_v1.0_lt_fast_rear_approach 13.5 2"
  "highway_v1.0_lt_merge_squeeze 12.0 2"
)
AGGRESSIVENESS_LEVELS=(3 5 7)

echo "[INFO] Decision-model Table-IV experiment root: $OUT_ROOT"
echo "[INFO] Active-inference config: $EUDM_AI_CONFIG"
echo "[INFO] Baseline EUDM config: $EUDM_BASE_CONFIG"

for scenario_row in "${SCENARIOS[@]}"; do
  read -r PLAYGROUND AI_DESIRED_VEL AI_AUTONOMOUS_LEVEL <<<"$scenario_row"
  for AGG in "${AGGRESSIVENESS_LEVELS[@]}"; do
    RESULT_ROOT="$OUT_ROOT/$PLAYGROUND/agg_$AGG"
    echo "[INFO] Scenario=$PLAYGROUND aggressiveness=$AGG -> $RESULT_ROOT"
    "$SCRIPT_DIR/repeat_compare_methods_triple.sh" \
      --playground "$PLAYGROUND" \
      --duration "$DURATION" \
      --runs "$RUNS" \
      --workspace "$WORKSPACE" \
      --out-root "$RESULT_ROOT" \
      --sleep-between "$SLEEP_BETWEEN" \
      --ai-desired-vel "$AI_DESIRED_VEL" \
      --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" \
      --ai-aggressiveness-level "$AGG" \
      --eudm-ai-config "$EUDM_AI_CONFIG" \
      --eudm-base-config "$EUDM_BASE_CONFIG"
  done
done

python3 "$SCRIPT_DIR/summarize_decision_model_table_iv.py" --root "$OUT_ROOT"

echo "[INFO] Decision-model Table-IV experiment completed."
echo "[INFO] Root: $OUT_ROOT"
