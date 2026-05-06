# ring_tiny_lt_conflict_release

- 基础地图：`ring_tiny_v1.0`
- 长尾类型：拥堵释放 / 低速密集车辆突然形成通行窗口
- 风险机理：多车低速密集排布下，局部间隙短暂出现，系统需要判断抢行收益是否值得承担未来冲突。
- 验证重点：验证方法是否选择保守但稳定的释放策略，避免在短窗口中产生高 LCC 或 unsafe_ratio 尖峰。
- 推荐周车期望速度：`6.5` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`5`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground ring_tiny_lt_conflict_release \
  --duration 120 \
  --ai-desired-vel 6.5 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5
```
