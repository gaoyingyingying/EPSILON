#!/usr/bin/env bash
set -euo pipefail

BASE_MAP="highway_v1.0"
DURATION=120
RUNS=10
WORKSPACE="/home/ying/epsilon-reproduction"
OUT_ROOT=""
SLEEP_BETWEEN=3
EUDM_AI_CONFIG=""
EUDM_BASE_CONFIG=""

usage() {
  cat <<USAGE
Usage: $0 [--base-map NAME] [--duration SEC] [--runs N] [--workspace PATH] [--out-root PATH] [--sleep-between SEC] [--eudm-ai-config PATH] [--eudm-base-config PATH]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-map)
      BASE_MAP="$2"; shift 2 ;;
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
MANIFEST="$WORKSPACE/src/EPSILON/core/playgrounds/long_tail_manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  "$SCRIPT_DIR/generate_long_tail_playgrounds.py"
fi

if [[ -z "$OUT_ROOT" ]]; then
  OUT_ROOT="$WORKSPACE/results/first_map_long_tail_${BASE_MAP}_runs${RUNS}_dur${DURATION}_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT_ROOT"

if [[ -z "$EUDM_AI_CONFIG" ]]; then
  EUDM_AI_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config.pb.txt"
fi
if [[ -z "$EUDM_BASE_CONFIG" ]]; then
  EUDM_BASE_CONFIG="$WORKSPACE/src/EPSILON/util/eudm_planner/config/eudm_config_baseline.pb.txt"
fi

mapfile -t SCENARIOS < <(python3 - "$MANIFEST" "$BASE_MAP" <<'PY'
import json
import sys
manifest = json.loads(open(sys.argv[1], encoding="utf-8").read())
base_map = sys.argv[2]
for item in manifest["scenarios"]:
    if item["base"] != base_map:
        continue
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

if [[ ${#SCENARIOS[@]} -eq 0 ]]; then
  echo "[ERROR] No long-tail scenarios found for base map: $BASE_MAP" >&2
  exit 1
fi

for row in "${SCENARIOS[@]}"; do
  IFS=$'\t' read -r PLAYGROUND AI_DESIRED_VEL AI_AUTONOMOUS_LEVEL AI_AGGRESSIVENESS_LEVEL <<<"$row"
  RESULT_ROOT="$OUT_ROOT/$PLAYGROUND"
  echo "[INFO] Scenario: $PLAYGROUND -> $RESULT_ROOT"
  "$SCRIPT_DIR/repeat_compare_methods_triple.sh" \
    --playground "$PLAYGROUND" \
    --duration "$DURATION" \
    --runs "$RUNS" \
    --workspace "$WORKSPACE" \
    --out-root "$RESULT_ROOT" \
    --sleep-between "$SLEEP_BETWEEN" \
    --ai-desired-vel "$AI_DESIRED_VEL" \
    --ai-autonomous-level "$AI_AUTONOMOUS_LEVEL" \
    --ai-aggressiveness-level "$AI_AGGRESSIVENESS_LEVEL" \
    --eudm-ai-config "$EUDM_AI_CONFIG" \
    --eudm-base-config "$EUDM_BASE_CONFIG"
done

REPORT_MD="$OUT_ROOT/REPORT_first_map_long_tail_${BASE_MAP}.md"
python3 "$SCRIPT_DIR/generate_long_tail_validation_report.py" \
  --suite-root "$OUT_ROOT" \
  --manifest "$MANIFEST" \
  --base-map "$BASE_MAP" \
  --output-md "$REPORT_MD"

echo "[INFO] First-map long-tail validation completed."
echo "[INFO] Report: $REPORT_MD"
