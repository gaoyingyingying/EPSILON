# ring_small_lt_dense_weave

- 基础地图：`ring_small_v1.0`
- 长尾类型：环路密集交织 / 连续换道诱发风险
- 风险机理：环路局部密度升高，多车速度差较小但空间余量不足，容易出现反复换道和舒适性劣化。
- 验证重点：验证方法是否能减少无收益换道，在安全、效率、LCC 之间形成稳定折中。
- 推荐周车期望速度：`9.0` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`5`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground ring_small_lt_dense_weave \
  --duration 120 \
  --ai-desired-vel 9.0 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5
```
