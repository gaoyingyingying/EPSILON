# 第一张图（highway_v1.0）长尾验证报告：EUDM主动推理 vs 原EUDM vs MPDM

## 1. 验证范围与口径

- 基础地图：`highway_v1.0`
- 长尾场景数：`2`
- 指标口径：`unsafe_ratio`、`average_velocity_mps`、`ud_per_km`、`lcc_per_km`
- 方法对照：`EUDM主动推理`、`原EUDM`、`MPDM`
- 说明：整图汇总采用“对各长尾场景均值再平均”的方式，强调跨场景稳健性。

## 2. 整图汇总（按场景等权平均）

| Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---:|---:|---:|---:|
| EUDM主动推理 | 0.000000 | 10.492837 | 0.000000 | 0.000000 |
| 原EUDM | 0.000000 | 10.382802 | 0.000000 | 0.000000 |
| MPDM | 0.135770 | 14.581673 | 0.000000 | 0.000000 |

- 结构化汇总 CSV：`/home/ying/epsilon-reproduction/results/smoke_first_map_long_tail_fixed_20260427_163648/highway_v1.0_overall_mean_by_scenarios.csv`

## 3. 分长尾场景结果与说明

### 3.1 `highway_v1.0_lt_fast_rear_approach`

- 长尾类型：后方高速逼近 / 换道盲区风险
- 风险机理：主车附近存在快速接近的后车，单纯当前最优换道可能在未来短时窗内产生后向冲突。
- 验证重点：验证决策是否能把后向高速目标纳入未来风险代价，避免把自己切入快速后车前方。
- 周车参数：`desired_vel=13.5`，`autonomous_level=2`，`aggressiveness=5`

| Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---:|---:|---:|---:|
| EUDM主动推理 | 0.000000 +- 0.000000 | 9.026096 +- 0.000000 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| 原EUDM | 0.000000 +- 0.000000 | 8.935603 +- 0.000000 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| MPDM | 0.000000 +- 0.000000 | 14.018814 +- 0.000000 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |

- 该场景结果目录：`/home/ying/epsilon-reproduction/results/smoke_first_map_long_tail_fixed_20260427_163648/highway_v1.0_lt_fast_rear_approach`

### 3.2 `highway_v1.0_lt_merge_squeeze`

- 长尾类型：合流夹挤 / 主路与匝道车辆同时争抢间隙
- 风险机理：主车、前车与侧前方车辆构成三车夹挤，风险在当前帧不一定最大，但未来汇合点冲突显著。
- 验证重点：验证主动推理是否能提前牺牲少量效率换取合流间隙，降低横纵向复合冲突。
- 周车参数：`desired_vel=12.0`，`autonomous_level=2`，`aggressiveness=5`

| Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---:|---:|---:|---:|
| EUDM主动推理 | 0.000000 +- 0.000000 | 11.959578 +- 0.000000 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| 原EUDM | 0.000000 +- 0.000000 | 11.830002 +- 0.000000 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| MPDM | 0.271540 +- 0.000000 | 15.144532 +- 0.000000 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |

- 该场景结果目录：`/home/ying/epsilon-reproduction/results/smoke_first_map_long_tail_fixed_20260427_163648/highway_v1.0_lt_merge_squeeze`

