# EUDM“过度保守停驶”修复验证（2026-04-27）

## 1) 修复内容（最小改动）
- `phy_simulator_planning.launch`：将 `joy_ctrl.launch` 改为可选，默认 `use_joy=false`（避免无 `joy` 包时整栈启动异常）。
- `test_ssc_with_eudm.cc`：补充初始化阶段日志（定位是否卡在 `bp/ssc/smm` 初始化）。
- `eudm_server_ros.cc`：保留规划失败兜底（沿用上一帧行为，避免“无控制即停驶”）。

## 2) 关键对比（highway_lite）

| 口径 | unsafe_ratio ↓ | average_velocity_mps ↑ | ud_per_km ↓ | lcc_per_km ↓ | 备注 |
|---|---:|---:|---:|---:|---|
| 停驶异常期（d20） | 0.183249 | 0.000000 | 0.000000 | 0.000000 | `recheck_eudm_hl_d20_nojoy` |
| 修复后快测（d20） | 0.143947 | 7.853061 | 0.000000 | 84.260309 | `recheck_eudm_hl_d20_initprobe` |
| 修复后（d60） | 0.222129 | 11.238626 | 0.000000 | 16.406273 | `recheck_eudm_hl_d60_after_fix` |
| 修复后（d120） | 0.102641 | 12.708173 | 0.000000 | 7.893419 | `recheck_eudm_hl_d120_after_fix` |
| 历史EUDM均值（10×120s） | 0.099219 | 12.908948 | 0.000000 | 7.125091 | `REPORT_runs10_all_maps_20260425.md` |

## 3) 结论
- “过度保守停驶”已从 **0速** 恢复为正常行驶。
- 与历史 10 轮均值相比，修复后 `d120` 单轮结果已接近：
  - 速度：`12.71` vs `12.91`
  - `unsafe_ratio`：`0.103` vs `0.099`
  - `lcc_per_km`：`7.89` vs `7.13`
- 当前版本已可继续做主动推理模块的正式对比与消融实验。

## 4) 结果目录
- `/home/ying/epsilon-reproduction/results/verify_active_inference_20260427_110115/recheck_eudm_hl_d20_nojoy/metrics.json`
- `/home/ying/epsilon-reproduction/results/verify_active_inference_20260427_110115/recheck_eudm_hl_d20_initprobe/metrics.json`
- `/home/ying/epsilon-reproduction/results/verify_active_inference_20260427_110115/recheck_eudm_hl_d60_after_fix/metrics.json`
- `/home/ying/epsilon-reproduction/results/verify_active_inference_20260427_110115/recheck_eudm_hl_d120_after_fix/metrics.json`

## 5) 主动推理权重调优（highway_lite）

### 当前采用的 `active_inference` 权重（p6）
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

### 关键对比（120s）
| 口径 | unsafe_ratio ↓ | average_velocity_mps ↑ | lcc_per_km ↓ | 备注 |
|---|---:|---:|---:|---|
| EUDM修复后（无AI） | 0.102641 | 12.708173 | 7.893419 | `recheck_eudm_hl_d120_after_fix` |
| AI调优 p6（run1） | 0.065853 | 12.966154 | 0.000000 | `tune_hl_d120_ai_p6` |
| AI调优 p6（run2） | 0.078923 | 13.118570 | 0.000000 | `tune_hl_d120_ai_p6_rep2` |
| 历史EUDM均值（10×120s） | 0.099219 | 12.908948 | 7.125091 | `REPORT_runs10_all_maps_20260425.md` |

### 小结
- 在两轮 120s 复验中，`p6` 同时实现了：
  - `unsafe_ratio` 下降（`0.1026 -> 0.0659/0.0789`）
  - `average_velocity_mps` 上升（`12.708 -> 12.966/13.119`）
- 该组参数可作为你后续“主动推理完整方法（Ours-full）”的默认口径。
