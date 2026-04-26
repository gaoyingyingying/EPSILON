#!/usr/bin/env bash
set -euo pipefail

METHOD="eudm"
PLAYGROUND="highway_v1.0"
DURATION=60
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_DIR=""
EGO_ID=0

usage() {
  cat <<USAGE
Usage: $0 [--method eudm|mpdm] [--playground NAME] [--duration SEC] [--workspace PATH] [--out-dir PATH] [--ego-id ID]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --method)
      METHOD="$2"; shift 2 ;;
    --playground)
      PLAYGROUND="$2"; shift 2 ;;
    --duration)
      DURATION="$2"; shift 2 ;;
    --workspace)
      WORKSPACE="$2"; shift 2 ;;
    --out-dir)
      OUT_DIR="$2"; shift 2 ;;
    --ego-id)
      EGO_ID="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ "$METHOD" != "eudm" && "$METHOD" != "mpdm" ]]; then
  echo "--method must be eudm or mpdm" >&2
  exit 1
fi

source /opt/ros/noetic/setup.bash
source "$WORKSPACE/devel/setup.bash"

if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$WORKSPACE/results/${METHOD}_${PLAYGROUND}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_DIR/glog"

export GLOG_log_dir="$OUT_DIR/glog"
export ROS_LOG_DIR="$OUT_DIR/ros"
mkdir -p "$ROS_LOG_DIR"

LAUNCH_FILE="repro_stack_${METHOD}.launch"
LAUNCH_LOG="$OUT_DIR/launch.log"
HZ_LOG="$OUT_DIR/hz_arena_info_dynamic.txt"
METRIC_JSON="$OUT_DIR/metrics.json"

cleanup() {
  set +e
  if [[ -n "${LAUNCH_PID:-}" ]]; then
    kill -INT "$LAUNCH_PID" >/dev/null 2>&1 || true
    sleep 2
    kill -TERM "$LAUNCH_PID" >/dev/null 2>&1 || true
  fi
  pkill -f "roslaunch planning_integrated ${LAUNCH_FILE}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

roslaunch planning_integrated "$LAUNCH_FILE" playground:="$PLAYGROUND" >"$LAUNCH_LOG" 2>&1 &
LAUNCH_PID=$!

sleep 8

echo "[INFO] Stack started. Collecting metrics for ${DURATION}s ..."
timeout "${DURATION}s" python3 "$(dirname "$0")/eval_metrics.py" \
  --ego-id "$EGO_ID" \
  --duration "$DURATION" \
  --output "$METRIC_JSON" || true

echo "[INFO] Sampling arena_info_dynamic topic rate ..."
timeout 15s rostopic hz /arena_info_dynamic -w 100 >"$HZ_LOG" 2>&1 || true

echo "[INFO] Finished. Output directory: $OUT_DIR"
