# EPSILON 实验汇报整理（10轮×4地图，AI p6）

## 1. 实验范围与口径
- 日期：2026-04-27 ~ 2026-04-28
- 地图：`highway_v1.0`、`highway_lite`、`ring_small_v1.0`、`ring_tiny_v1.0`
- 方法：`EUDM(主动推理 p6)`、`MPDM`
- 运行口径：每图每方法 `10` 轮（每轮 `120s`），统计为 `mean +- std`
- 执行约束：按要求在地图之间暂停 `5` 分钟后再启动下一张图

## 2. 结果总表（Table1风格，mean +- std）
| Map | Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---:|---:|---:|---:|---:|
| highway_v1.0 | EUDM | 0.034277 +- 0.001764 | 13.683225 +- 0.189017 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| highway_v1.0 | MPDM | 0.024091 +- 0.001114 | 16.444834 +- 0.128674 | 0.914303 +- 0.201756 | 0.000000 +- 0.000000 |
| highway_lite | EUDM | 0.089556 +- 0.025326 | 13.126155 +- 0.526484 | 0.000000 +- 0.000000 | 0.448701 +- 0.706626 |
| highway_lite | MPDM | 0.043543 +- 0.005921 | 15.597559 +- 0.085034 | 1.499471 +- 0.317347 | 1.446561 +- 0.342726 |
| ring_small_v1.0 | EUDM | 0.046206 +- 0.021177 | 10.130104 +- 0.205447 | 0.000000 +- 0.000000 | 10.141379 +- 6.040587 |
| ring_small_v1.0 | MPDM | 0.054157 +- 0.005063 | 10.543777 +- 0.036159 | 0.871504 +- 0.425818 | 1.109554 +- 0.633361 |
| ring_tiny_v1.0 | EUDM | 0.288468 +- 0.286843 | 5.461352 +- 0.466867 | 0.000000 +- 0.000000 | 26.741106 +- 29.885418 |
| ring_tiny_v1.0 | MPDM | 0.014107 +- 0.000261 | 0.640875 +- 0.011692 | 12.912131 +- 0.225600 | 106.204909 +- 24.316477 |

## 3. 结果解读（简要）
- `highway_v1.0`：EUDM 在安全/效率上均显著优于旧基线（相对 2026-04-25 版本），且舒适性指标稳定。
- `highway_lite`：EUDM 相对旧基线继续保持 `unsafe_ratio` 和 `average_velocity_mps` 同时改善。
- `ring_small_v1.0`：EUDM 在安全和效率上具竞争力，但 `LCC` 波动增大。
- `ring_tiny_v1.0`：EUDM 出现高方差（`unsafe_ratio` 与 `LCC` 波动大），说明该图仍是当前参数的鲁棒性短板。

## 4. 数据索引
- 多地图总表 CSV：`/home/ying/epsilon-reproduction/results/multi_map_runs10_dur120_20260427_ai_p6/multi_map_table1_std.csv`
- 多地图总表 Markdown：`/home/ying/epsilon-reproduction/results/multi_map_runs10_dur120_20260427_ai_p6/multi_map_table1_std.md`
- 各地图结果根目录：
  - `/home/ying/epsilon-reproduction/results/repeat_highway_v1.0_runs10_dur120_20260427_ai_p6`
  - `/home/ying/epsilon-reproduction/results/repeat_highway_lite_runs10_dur120_20260427_ai_p6`
  - `/home/ying/epsilon-reproduction/results/repeat_ring_small_v1.0_runs10_dur120_20260427_ai_p6`
  - `/home/ying/epsilon-reproduction/results/repeat_ring_tiny_v1.0_runs10_dur120_20260427_ai_p6`
