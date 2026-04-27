# Git Upload Note (2026-04-28)

## 1. Scope of This Upload

This upload contains:

1. Active-inference decision extension in EUDM code.
2. Stability fixes for the "over-conservative stop" issue.
3. Full experiment outputs for the `10 x 120s` benchmark runs on all 4 maps.
4. Consolidated reports and cross-map table for thesis use.

This upload excludes build artifacts in `build/` and `devel/`.

## 2. Code Changes

### 2.1 Active-Inference Decision Module

Updated files:

- `src/EPSILON/util/eudm_planner/proto/eudm_config.proto`
- `src/EPSILON/util/eudm_planner/config/eudm_config.pb.txt`
- `src/EPSILON/util/eudm_planner/inc/eudm_planner/eudm_planner.h`
- `src/EPSILON/util/eudm_planner/src/eudm_planner/eudm_planner.cc`

Main changes:

- Added active-inference configuration block under `cost.active_inference`.
- Added belief update and entropy-related fields/functions in planner.
- Added active-inference cost terms:
  - risk
  - uncertainty
  - efficiency
  - comfort
- Enabled weighted integration into existing EUDM cost pipeline with minimal architecture change.

### 2.2 Runtime Stability Fixes (No-Motion / Stop Issue)

Updated files:

- `src/EPSILON/core/phy_simulator/launch/phy_simulator_planning.launch`
- `src/EPSILON/util/eudm_planner/src/eudm_planner/eudm_server_ros.cc`
- `src/EPSILON/app/planning_integrated/src/test_ssc_with_eudm.cc`

Main changes:

- `joy` launch made optional (`use_joy=false` by default) to avoid startup failure when joy package/device is unavailable.
- Added behavior fallback path in EUDM ROS server when planner run fails.
- Added staged init logs in `test_ssc_with_eudm` for debugging startup pipeline.

## 3. Experiment Runs Included

### 3.1 Verification / Debug Runs

- `results/verify_active_inference_20260427_110115/`

Contains:

- stop-issue diagnosis runs
- incremental tuning trials
- intermediate summaries

### 3.2 Main Benchmark Runs (`10 x 120s`)

- `results/repeat_highway_v1.0_runs10_dur120_20260427_ai_p6/`
- `results/repeat_highway_lite_runs10_dur120_20260427_ai_p6/`
- `results/repeat_ring_small_v1.0_runs10_dur120_20260427_ai_p6/`
- `results/repeat_ring_tiny_v1.0_runs10_dur120_20260427_ai_p6/`

Each directory includes:

- per-run `metrics.json`
- per-run `summary.csv`
- `aggregate_stats.json`
- `aggregate_summary.csv`
- `table1_style_std.csv`
- `table1_style_variance.csv`

### 3.3 New Multi-Map Consolidation

- `results/multi_map_runs10_dur120_20260427_ai_p6/multi_map_table1_std.csv`
- `results/multi_map_runs10_dur120_20260427_ai_p6/multi_map_table1_std.md`

## 4. Report Files

- Updated legacy report with incremental section:
  - `results/REPORT_runs10_all_maps_20260425.md`
- New full report for AI p6 benchmark:
  - `results/REPORT_runs10_all_maps_20260427_ai_p6.md`

## 5. Current Parameter Baseline (AI p6)

File:

- `src/EPSILON/util/eudm_planner/config/eudm_config.pb.txt`

`active_inference` core weights:

- `enable: true`
- `risk_unit_cost: 0.3`
- `uncertainty_unit_cost: 0.1`
- `efficiency_unit_cost: 0.6`
- `comfort_unit_cost: 0.1`
- `ttc_threshold: 2.4`
- `min_longitudinal_distance: 9.5`
- `min_lateral_distance: 2.3`
- `belief_smoothing: 0.65`
- `belief_entropy_weight: 0.5`

## 6. Reproduction Commands

Single map repeated benchmark:

```bash
./src/EPSILON/scripts/repeat_compare_methods.sh \
  --playground highway_lite \
  --duration 120 \
  --runs 10 \
  --workspace /home/ying/epsilon-reproduction \
  --out-root /home/ying/epsilon-reproduction/results/repeat_highway_lite_runs10_dur120_20260427_ai_p6
```

Aggregate multi-map table:

```bash
python3 src/EPSILON/scripts/aggregate_multi_map_tables.py \
  --output-dir /home/ying/epsilon-reproduction/results/multi_map_runs10_dur120_20260427_ai_p6 \
  --map-root highway_v1.0 /home/ying/epsilon-reproduction/results/repeat_highway_v1.0_runs10_dur120_20260427_ai_p6 \
  --map-root highway_lite /home/ying/epsilon-reproduction/results/repeat_highway_lite_runs10_dur120_20260427_ai_p6 \
  --map-root ring_small_v1.0 /home/ying/epsilon-reproduction/results/repeat_ring_small_v1.0_runs10_dur120_20260427_ai_p6 \
  --map-root ring_tiny_v1.0 /home/ying/epsilon-reproduction/results/repeat_ring_tiny_v1.0_runs10_dur120_20260427_ai_p6
```

## 7. Notes

- Ring-tiny remains high-variance for EUDM with current p6 tuning.
- The current upload is intended as thesis experiment milestone snapshot.
