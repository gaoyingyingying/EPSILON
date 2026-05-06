# highway_v1.0_lt_fast_rear_approach

- 基础地图：`highway_v1.0`
- 长尾类型：后方高速逼近 / 换道盲区风险
- 风险机理：主车附近存在快速接近的后车，单纯当前最优换道可能在未来短时窗内产生后向冲突。
- 验证重点：验证决策是否能把后向高速目标纳入未来风险代价，避免把自己切入快速后车前方。
- 推荐周车期望速度：`13.5` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`5`
- 可视化建议：为更稳定观察“后车逼近->主车反应”，本场景将后车 `id=7` 初始位置后移，保留高速逼近设定，拉长可观测窗口。

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground highway_v1.0_lt_fast_rear_approach \
  --duration 120 \
  --ai-desired-vel 13.5 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5
```

使用“后向风险强化”EUDM配置（推荐）：

```bash
./src/EPSILON/scripts/run_stack.sh \
  --method eudm \
  --playground highway_v1.0_lt_fast_rear_approach \
  --duration 120 \
  --workspace /home/ying/epsilon-reproduction \
  --out-dir /home/ying/epsilon-reproduction/results/rear_guard_demo \
  --ai-desired-vel 13.5 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5 \
  --eudm-bp-config /home/ying/epsilon-reproduction/src/EPSILON/util/eudm_planner/config/eudm_config_rear_guard.pb.txt
```
