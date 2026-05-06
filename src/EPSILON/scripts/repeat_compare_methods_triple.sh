#!/usr/bin/env bash
set -euo pipefail

PLAYGROUND="highway_v1.0"
DURATION=120
RUNS=5
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""
SLEEP_BETWEEN=3
START_INDEX=1
AI_DESIRED_VEL=10.0
AI_AUTONOMOUS_LEVEL=2
AI_AGGRESSIVENESS_LEVEL=4
EUDM_AI_CONFIG=""
EUDM_BASE_CONFIG=""

usage() {
  cat <<USAGE
Usage: $0 [--playground NAME] [--duration SEC] [--runs N] [--workspace PATH] [--out-root PATH] [--sleep-between SEC] [--start-index N] [--ai-desired-vel MPS] [--ai-autonomous-level N] [--ai-aggressiveness-level N] [--eudm-ai-config PATH] [--eudm-base-config PATH]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --playground)
      PLAYGROUND="$2"; shift 2 ;;
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
    --start-index)
      START_INDEX="$2"; shift 2 ;;
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
  OUT_ROOT="$WORKSPACE/results/repeat3_${PLAYGROUND}_runs${RUNS}_dur${DURATION}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

if [[ -z "$EUDM_AI_CONFIG" ]]; then
  EUDM_AI_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config.pb.txt"
fi
if [[ -z "$EUDM_BASE_CONFIG" ]]; then
  EUDM_BASE_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config_baseline.pb.txt"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
END_INDEX=$((START_INDEX + RUNS - 1))

for ((i = START_INDEX; i <= END_INDEX; i++)); do
  RUN_DIR="$OUT_ROOT/run_$(printf "%02d" "$i")"
  echo "[INFO] Starting run $i/$END_INDEX -> $RUN_DIR"
  "$SCRIPT_DIR/compare_methods_triple.sh" \
    --playground "$PLAYGROUND" \
    --duration "$DURATION" \
    --workspace "$WORKSPACE" \
    --out-root "$RUN_DIR" \
    --ai-desired-vel "$AI_DESIRED_VEL" \
    --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" \
    --ai-aggressiveness-level "$AI_AGGRESSIVENESS_LEVEL" \
    --eudm-ai-config "$EUDM_AI_CONFIG" \
    --eudm-base-config "$EUDM_BASE_CONFIG"
  if [[ "$i" -lt "$END_INDEX" ]]; then
    sleep "$SLEEP_BETWEEN"
  fi
done

python3 "$SCRIPT_DIR/aggregate_compare_runs_triple.py" --root "$OUT_ROOT"
echo "[INFO] Repeated triple-method comparison completed under: $OUT_ROOT"
