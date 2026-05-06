# 实验二长尾风险场景说明

本文在既有 4 张测试地图基础上新增 8 个长尾 playground。场景生成方式保持地图拓扑、障碍物与原始 agent 配置不变，仅调整车辆初始分布、初速度与少量车辆参数，因此可直接复用现有 EUDM-主动推理与 MPDM 对照脚本。

## 场景清单

| Playground | 基础地图 | 长尾类型 | 验证重点 |
|---|---|---|---|
| `highway_lite_lt_close_cut_in` | `highway_lite` | 近距离强制切入 / 相邻车道低概率横向冲突 | 提前识别未来横向占用风险，避免近距离被动急刹或危险换道。 |
| `highway_lite_lt_stalled_lead` | `highway_lite` | 前方慢车/疑似故障车 / 低速障碍队尾 | 在前方低速长车出现时，验证提前减速与绕行决策是否稳定。 |
| `highway_v1.0_lt_fast_rear_approach` | `highway_v1.0` | 后方高速逼近 / 换道盲区风险 | 将后向高速目标纳入未来风险，避免切入快速后车前方。 |
| `highway_v1.0_lt_merge_squeeze` | `highway_v1.0` | 合流夹挤 / 主路与匝道车辆争抢间隙 | 在未来汇合点风险出现前主动让行或调整速度。 |
| `ring_small_lt_dense_weave` | `ring_small_v1.0` | 环路密集交织 / 连续换道诱发风险 | 降低无收益换道，观察安全、效率与 LCC 的折中。 |
| `ring_small_lt_slow_truck_block` | `ring_small_v1.0` | 弯道慢速长车遮挡 / 队列压缩 | 判断跟驰、等待或绕行的长期代价，避免舒适性劣化。 |
| `ring_tiny_lt_low_friction_cluster` | `ring_tiny_v1.0` | 小环高密度低附着 / 操控裕度不足 | 检验高难低裕度场景中的鲁棒性与方差控制。 |
| `ring_tiny_lt_conflict_release` | `ring_tiny_v1.0` | 拥堵释放 / 短暂通行窗口 | 判断抢行收益是否值得承担未来冲突，避免 unsafe_ratio 尖峰。 |

## 生成与运行

生成场景：

```bash
./src/EPSILON/scripts/generate_long_tail_playgrounds.py --force
```

单场景对比：

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground highway_lite_lt_close_cut_in \
  --duration 120 \
  --ai-desired-vel 11.5 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5
```

完整长尾套件：

```bash
./src/EPSILON/scripts/run_long_tail_suite.sh --runs 10 --duration 120
```

第一张图（`highway_v1.0`）三方法验证：

```bash
./src/EPSILON/scripts/run_first_map_long_tail_validation.sh \
  --base-map highway_v1.0 \
  --runs 10 \
  --duration 120
```

该命令会自动输出：

- `EUDM主动推理 vs 原EUDM vs MPDM` 的分场景统计结果
- 第一张图整图汇总（跨长尾场景等权）
- Markdown 报告：`REPORT_first_map_long_tail_highway_v1.0.md`

每个生成的 playground 内含 `SCENARIO.md` 与 `long_tail_manifest.json`，用于记录该场景的长尾类型、风险机理、验证重点和推荐周车参数。
