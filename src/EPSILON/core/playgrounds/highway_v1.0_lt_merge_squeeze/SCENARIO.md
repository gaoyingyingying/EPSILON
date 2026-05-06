# highway_v1.0_lt_merge_squeeze

- 基础地图：`highway_v1.0`
- 长尾类型：合流夹挤 / 主路与匝道车辆同时争抢间隙
- 风险机理：主车、前车与侧前方车辆构成三车夹挤，风险在当前帧不一定最大，但未来汇合点冲突显著。
- 验证重点：验证主动推理是否能提前牺牲少量效率换取合流间隙，降低横纵向复合冲突。
- 推荐周车期望速度：`12.0` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`5`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground highway_v1.0_lt_merge_squeeze \
  --duration 120 \
  --ai-desired-vel 12.0 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5
```
