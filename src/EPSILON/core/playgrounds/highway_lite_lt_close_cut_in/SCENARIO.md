# highway_lite_lt_close_cut_in

- 基础地图：`highway_lite`
- 长尾类型：近距离强制切入 / 相邻车道低概率横向冲突
- 风险机理：前方相邻车道车辆在很小纵向间隙内形成切入压力，主车需要提前减速或放弃激进换道。
- 验证重点：验证主动推理是否能在 unsafe_ratio 上升前识别未来横向占用风险，并保持速度损失可控。
- 推荐周车期望速度：`11.5` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`5`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground highway_lite_lt_close_cut_in \
  --duration 120 \
  --ai-desired-vel 11.5 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 5
```
