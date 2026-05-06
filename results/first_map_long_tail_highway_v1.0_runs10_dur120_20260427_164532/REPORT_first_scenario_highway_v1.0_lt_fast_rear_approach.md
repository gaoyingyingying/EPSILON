# 第一场景结果整理（10轮 × 120s）

## 场景信息

- 场景：`highway_v1.0_lt_fast_rear_approach`
- 基础地图：`highway_v1.0`
- 长尾类型：后方高速逼近 / 换道盲区风险
- 风险机理：主车附近存在快速接近的后车，当前最优换道可能在短时窗内触发后向冲突
- 验证重点：是否能将后向高速目标纳入未来风险代价并提前规避
- 周车参数：`desired_vel=13.5`，`autonomous_level=2`，`aggressiveness=5`

## 三方法聚合结果（均值 ± 标准差）

| Method | Safety (unsafe ratio, ↓) | Efficiency (Ave. Vel m/s, ↑) | Comfort UD (/km, ↓) | Comfort LCC (/km, ↓) |
|---|---:|---:|---:|---:|
| EUDM_AI | 0.044605 +- 0.031570 | 13.544409 +- 0.359804 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| EUDM_BASE | 0.175681 +- 0.275589 | 13.045018 +- 0.100260 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |
| MPDM | 0.139951 +- 0.294330 | 13.291736 +- 1.078802 | 0.000000 +- 0.000000 | 0.000000 +- 0.000000 |

## 逐轮表现摘要（unsafe_ratio）

| Run | EUDM_AI | EUDM_BASE | MPDM |
|---|---:|---:|---:|
| run_01 | 0.060008 | 0.435855 | 0.000000 |
| run_02 | 0.030255 | 0.000000 | 0.000000 |
| run_03 | 0.037436 | 0.000000 | 0.000000 |
| run_04 | 0.001170 | 0.000000 | 0.000000 |
| run_05 | 0.117259 | 0.607071 | 0.930804 |
| run_06 | 0.029417 | 0.000000 | 0.000000 |
| run_07 | 0.040970 | 0.000000 | 0.000000 |
| run_08 | 0.080047 | 0.000000 | 0.027079 |
| run_09 | 0.021737 | 0.713880 | 0.000000 |
| run_10 | 0.027750 | 0.000000 | 0.441631 |

## 当前结论（第一场景）

- 就该场景 10 轮统计看，`EUDM_AI` 的安全指标均值最低且方差显著低于 `EUDM_BASE` 与 `MPDM`。
- `EUDM_BASE` 在个别轮次出现明显高风险尖峰（如 run_05、run_09），稳定性不足。
- `MPDM` 在效率上有竞争力，但安全方差较大，存在高风险轮次（如 run_05、run_10）。

## 数据文件

- 聚合总表：`/home/ying/epsilon-reproduction/results/first_map_long_tail_highway_v1.0_runs10_dur120_20260427_164532/highway_v1.0_lt_fast_rear_approach/table1_style_std.csv`
- 聚合明细：`/home/ying/epsilon-reproduction/results/first_map_long_tail_highway_v1.0_runs10_dur120_20260427_164532/highway_v1.0_lt_fast_rear_approach/aggregate_summary.csv`
- 各轮原始对比：`run_01` ~ `run_10` 下 `summary.csv`

