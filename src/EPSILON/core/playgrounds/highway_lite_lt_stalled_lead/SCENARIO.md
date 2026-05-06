# highway_lite_lt_stalled_lead

- 基础地图：`highway_lite`
- 长尾类型：前方慢车/疑似故障车 / 低速障碍队尾
- 风险机理：主车路径前方出现低速长车，后续车辆仍保持较高期望速度，形成追尾与绕行权衡。
- 验证重点：验证系统能否提前降低速度并选择安全绕行，而不是在近距离才急减速。
- 推荐周车期望速度：`10.0` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`4`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground highway_lite_lt_stalled_lead \
  --duration 120 \
  --ai-desired-vel 10.0 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 4
```
