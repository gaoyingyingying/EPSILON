# ring_small_lt_slow_truck_block

- 基础地图：`ring_small_v1.0`
- 长尾类型：弯道慢速长车遮挡 / 队列压缩
- 风险机理：低速长车在弯道前方造成遮挡与队列压缩，主车需要判断跟驰、等待或换道绕行的长期代价。
- 验证重点：验证提前减速和换道时机，重点观察 unsafe_ratio 与 LCC 的同步变化。
- 推荐周车期望速度：`8.0` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`4`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground ring_small_lt_slow_truck_block \
  --duration 120 \
  --ai-desired-vel 8.0 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 4
```
