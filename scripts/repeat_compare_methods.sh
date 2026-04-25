#!/usr/bin/env bash
set -euo pipefail

PLAYGROUND="highway_v1.0"
DURATION=120
RUNS=5
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""
SLEEP_BETWEEN=3
START_INDEX=1

usage() {
  cat <<USAGE
Usage: $0 [--playground NAME] [--duration SEC] [--runs N] [--workspace PATH] [--out-root PATH] [--sleep-between SEC]
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
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="$WORKSPACE/results/repeat_${PLAYGROUND}_runs${RUNS}_dur${DURATION}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

END_INDEX=$((START_INDEX + RUNS - 1))

for ((i = START_INDEX; i <= END_INDEX; i++)); do
  RUN_DIR="$OUT_ROOT/run_$(printf "%02d" "$i")"
  echo "[INFO] Starting run $i/$END_INDEX -> $RUN_DIR"
  "$SCRIPT_DIR/compare_methods.sh" \
    --playground "$PLAYGROUND" \
    --duration "$DURATION" \
    --workspace "$WORKSPACE" \
    --out-root "$RUN_DIR"
  if [[ "$i" -lt "$END_INDEX" ]]; then
    sleep "$SLEEP_BETWEEN"
  fi
done

python3 "$SCRIPT_DIR/aggregate_compare_runs.py" --root "$OUT_ROOT"
echo "[INFO] Repeated comparison completed under: $OUT_ROOT"
