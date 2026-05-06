# ring_tiny_lt_low_friction_cluster

- 基础地图：`ring_tiny_v1.0`
- 长尾类型：小环高密度低附着 / 操控裕度不足
- 风险机理：车辆横纵向能力被限制，环路空间又很小，激进行为会更快转化为不舒适或不安全状态。
- 验证重点：验证主动推理在高难低裕度场景中是否能降低高方差，尤其关注 unsafe_ratio 标准差。
- 推荐周车期望速度：`7.0` m/s
- 推荐周车自动驾驶等级：`2`
- 推荐周车激进度：`4`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \
  --playground ring_tiny_lt_low_friction_cluster \
  --duration 120 \
  --ai-desired-vel 7.0 \
  --ai-autonomous-level 2 \
  --ai-aggressiveness-level 4
```
