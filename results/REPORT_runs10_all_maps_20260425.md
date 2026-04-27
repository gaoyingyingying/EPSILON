# EPSILON 实验汇报整理（10轮×4地图）

## 1. 实验范围与口径
- 时间口径：本次整理基于 2026-04-24 与 2026-04-25 完成的数据。
- 地图：`highway_v1.0`、`highway_lite`、`ring_small_v1.0`、`ring_tiny_v1.0`。
- 方法：`EUDM`、`MPDM`。
- 运行口径：每图每方法 10 轮（每轮 120s），统计采用 `mean +- std`。
- 指标：
  - Safety：`unsafe_ratio`（越低越好）
  - Efficiency：`average_velocity_mps`（越高越好）
  - Comfort：`ud_per_km`、`lcc_per_km`（越低越好）

## 2. 结果总表（Table1风格，mean +- std）
| Map | Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---|---:|---:|---:|---:|
| highway_v1.0 | EUDM | 0.067674 +- 0.006860 | 12.170984 +- 0.144002 | 0.137166 +- 0.274340 | 0.206287 +- 0.315120 |
| highway_v1.0 | MPDM | 0.027462 +- 0.001046 | 15.593811 +- 0.060383 | 1.243746 +- 0.487286 | 0.323442 +- 0.356885 |
| highway_lite | EUDM | 0.099219 +- 0.012897 | 12.908948 +- 0.469887 | 0.000000 +- 0.000000 | 7.125091 +- 2.461631 |
| highway_lite | MPDM | 0.055699 +- 0.014085 | 15.547761 +- 0.164398 | 1.020085 +- 0.441422 | 1.507270 +- 0.327822 |
| ring_small_v1.0 | EUDM | 0.046309 +- 0.013824 | 5.918145 +- 2.617407 | 1.755565 +- 0.776603 | 0.000000 +- 0.000000 |
| ring_small_v1.0 | MPDM | 0.054145 +- 0.005710 | 10.565013 +- 0.046776 | 0.790693 +- 0.353692 | 1.185828 +- 0.393598 |
| ring_tiny_v1.0 | EUDM | 0.056467 +- 0.001932 | 1.716692 +- 0.011937 | 4.405971 +- 1.468700 | 247.612128 +- 28.838190 |
| ring_tiny_v1.0 | MPDM | 0.014213 +- 0.000264 | 0.648835 +- 0.005413 | 12.745759 +- 0.101073 | 109.652933 +- 9.007245 |

## 3. 分地图核心结论（用于汇报一句话）
- highway_v1.0：MPDM 在安全与效率显著领先；EUDM 在舒适性（UD/LCC）更优。
- highway_lite：MPDM 在安全、效率和 LCC 明显更好；EUDM 仅在 UD 指标为 0（优于 MPDM）。
- ring_small_v1.0：EUDM 安全略好且 LCC=0；MPDM 在效率和 UD 更优，且速度稳定性明显更强。
- ring_tiny_v1.0：MPDM 安全和 LCC 更优；EUDM 在效率与 UD 更优，且两方法在该图都表现为“低速保守”工况。

## 4. 跨图总体观察（汇报重点）
- 没有单一方法在全部地图和全部指标上同时最优，存在明确 trade-off。
- MPDM 倾向于更高效率（特别在 highway/ring_small），并在多数地图的 unsafe_ratio 更低。
- EUDM 在部分舒适指标（尤其 UD）更有优势，但在某些地图（如 ring_small）速度方差较大。
- ring_tiny_v1.0 是明显“困难工况”：两方法速度都较低，且 LCC 指标绝对值远高于其他地图。

## 5. 数据质量与完整性
- 4 张地图均完成 10 轮统计。
- `ring_tiny_v1.0` 在执行中曾出现一次中断，已补齐 `run_01/mpdm` 并重新聚合，当前统计完整。
- 各结果目录均包含：`aggregate_stats.json`、`aggregate_summary.csv`、`table1_style_std.csv`。

## 6. 汇报建议结构（可直接做PPT）
- 第1页：实验设置（地图、方法、轮次、指标定义）。
- 第2页：总表（4图×2方法，mean+-std）。
- 第3页：highway 两图对比（强调 MPDM 的安全/效率优势与舒适性 trade-off）。
- 第4页：ring 两图对比（强调场景难度提升下的策略差异）。
- 第5页：总结与下一步（按目标偏好选方法，或做混合策略/参数自适应）。

## 7. 数据索引
- 多地图总表：`/home/ying/epsilon-reproduction/results/multi_map_runs10_dur120_20260425/multi_map_table1_std.csv`
- 多地图 Markdown：`/home/ying/epsilon-reproduction/results/multi_map_runs10_dur120_20260425/multi_map_table1_std.md`
- 各地图结果根目录：
  - `/home/ying/epsilon-reproduction/results/repeat_highway_v1.0_runs10_dur120_20260424`
  - `/home/ying/epsilon-reproduction/results/repeat_highway_lite_runs10_dur120_20260425`
  - `/home/ying/epsilon-reproduction/results/repeat_ring_small_v1.0_runs10_dur120_20260425`
  - `/home/ying/epsilon-reproduction/results/repeat_ring_tiny_v1.0_runs10_dur120_20260425`

## 8. 更新：主动推理调参复验（2026-04-27）

### 8.1 复验口径
- 地图：`highway_lite`
- 方法：`EUDM(主动推理 p6 参数)`、`MPDM`
- 运行口径：`10×120s`（与原报告一致）
- 结果目录：`/home/ying/epsilon-reproduction/results/repeat_highway_lite_runs10_dur120_20260427_ai_p6`

### 8.2 新结果（mean +- std）
| Map | Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---|---:|---:|---:|---:|
| highway_lite | EUDM (AI p6) | 0.089556 +- 0.025326 | 13.126155 +- 0.526484 | 0.000000 +- 0.000000 | 0.448701 +- 0.706626 |
| highway_lite | MPDM | 0.043543 +- 0.005921 | 15.597559 +- 0.085034 | 1.499471 +- 0.317347 | 1.446561 +- 0.342726 |

### 8.3 相对原 `highway_lite` EUDM 基线（2026-04-25）的变化
- 安全性：`unsafe_ratio` 从 `0.099219` 降到 `0.089556`（改善）。
- 效率：`average_velocity_mps` 从 `12.908948` 升到 `13.126155`（改善）。
- 舒适性：
  - `ud_per_km` 维持 `0.0`；
  - `lcc_per_km` 从 `7.125091` 降到 `0.448701`（显著改善）。

### 8.4 说明
- 该更新仅替换了 `highway_lite` 场景下的 EUDM 参数结果，其他三张地图仍沿用 2026-04-25 的基线统计。
- 如需将“主动推理 p6”固化为整篇论文统一口径，建议继续对 `highway_v1.0`、`ring_small_v1.0`、`ring_tiny_v1.0` 按同样 `10×120s` 跑完并重做多地图总表。
