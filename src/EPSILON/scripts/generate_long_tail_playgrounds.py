#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUNDS = ROOT / "core" / "playgrounds"


PARAM_PROFILES = {
    "car": {
        "width": 1.90,
        "length": 4.88,
        "wheel_base": 2.85,
        "front_suspension": 0.93,
        "rear_suspension": 1.10,
        "max_steering_angle": 45.0,
        "max_longitudinal_acc": 2.0,
        "max_lateral_acc": 2.0,
    },
    "truck": {
        "width": 2.50,
        "length": 8.80,
        "wheel_base": 5.20,
        "front_suspension": 1.20,
        "rear_suspension": 1.60,
        "max_steering_angle": 38.0,
        "max_longitudinal_acc": 1.0,
        "max_lateral_acc": 1.4,
    },
    "low_mu": {
        "width": 1.90,
        "length": 4.88,
        "wheel_base": 2.85,
        "front_suspension": 0.93,
        "rear_suspension": 1.10,
        "max_steering_angle": 45.0,
        "max_longitudinal_acc": 1.0,
        "max_lateral_acc": 1.0,
    },
}


SCENARIOS = [
    {
        "name": "highway_lite_lt_close_cut_in",
        "base": "highway_lite",
        "type": "近距离强制切入 / 相邻车道低概率横向冲突",
        "risk": "前方相邻车道车辆在很小纵向间隙内形成切入压力，主车需要提前减速或放弃激进换道。",
        "verify": "验证主动推理是否能在 unsafe_ratio 上升前识别未来横向占用风险，并保持速度损失可控。",
        "ai_desired_vel": 11.5,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 5,
        "changes": [
            {"id": 0, "state": {"velocity": 7.0}},
            {"id": 4, "state": {"x": 128.2, "y": -272.6, "angle": -1.10, "velocity": 8.0}},
            {"id": 5, "state": {"x": 126.0, "y": -267.8, "angle": -1.14, "velocity": 9.5}},
            {"id": 7, "state": {"x": 133.2, "y": -284.0, "angle": -1.11, "velocity": 6.0}},
        ],
    },
    {
        "name": "highway_lite_lt_stalled_lead",
        "base": "highway_lite",
        "type": "前方慢车/疑似故障车 / 低速障碍队尾",
        "risk": "主车路径前方出现低速长车，后续车辆仍保持较高期望速度，形成追尾与绕行权衡。",
        "verify": "验证系统能否提前降低速度并选择安全绕行，而不是在近距离才急减速。",
        "ai_desired_vel": 10.0,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 4,
        "changes": [
            {"id": 0, "state": {"velocity": 6.0}},
            {"id": 4, "subclass": "truck", "params": "truck", "state": {"x": 129.2, "y": -271.6, "angle": -1.11, "velocity": 1.0}},
            {"id": 7, "state": {"x": 132.7, "y": -281.6, "angle": -1.12, "velocity": 10.0}},
            {"id": 9, "state": {"x": 130.2, "y": -278.3, "angle": -1.13, "velocity": 9.0}},
        ],
    },
    {
        "name": "highway_v1.0_lt_fast_rear_approach",
        "base": "highway_v1.0",
        "type": "后方高速逼近 / 换道盲区风险",
        "risk": "主车附近存在快速接近的后车，单纯当前最优换道可能在未来短时窗内产生后向冲突。",
        "verify": "验证决策是否能把后向高速目标纳入未来风险代价，避免把自己切入快速后车前方。",
        "ai_desired_vel": 13.5,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 5,
        "changes": [
            {"id": 0, "state": {"velocity": 8.0}},
            {"id": 7, "state": {"x": 4.9, "y": -48.6, "angle": -0.98, "velocity": 15.0}},
            {"id": 2, "state": {"x": 22.5, "y": -69.2, "angle": -0.98, "velocity": 7.0}},
            {"id": 3, "state": {"x": 34.0, "y": -94.8, "angle": -0.99, "velocity": 6.0}},
        ],
    },
    {
        "name": "highway_v1.0_lt_merge_squeeze",
        "base": "highway_v1.0",
        "type": "合流夹挤 / 主路与匝道车辆同时争抢间隙",
        "risk": "主车、前车与侧前方车辆构成三车夹挤，风险在当前帧不一定最大，但未来汇合点冲突显著。",
        "verify": "验证主动推理是否能提前牺牲少量效率换取合流间隙，降低横纵向复合冲突。",
        "ai_desired_vel": 12.0,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 5,
        "changes": [
            {"id": 0, "state": {"velocity": 7.5}},
            {"id": 2, "state": {"x": 24.0, "y": -70.4, "angle": -0.97, "velocity": 7.0}},
            {"id": 3, "state": {"x": 30.8, "y": -82.5, "angle": -0.99, "velocity": 8.5}},
            {"id": 4, "state": {"x": 42.4, "y": -101.7, "angle": -1.00, "velocity": 9.0}},
        ],
    },
    {
        "name": "ring_small_lt_dense_weave",
        "base": "ring_small_v1.0",
        "type": "环路密集交织 / 连续换道诱发风险",
        "risk": "环路局部密度升高，多车速度差较小但空间余量不足，容易出现反复换道和舒适性劣化。",
        "verify": "验证方法是否能减少无收益换道，在安全、效率、LCC 之间形成稳定折中。",
        "ai_desired_vel": 9.0,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 5,
        "changes": [
            {"id": 0, "state": {"velocity": 6.0}},
            {"id": 2, "state": {"x": 93.0, "y": -79.9, "angle": -0.06, "velocity": 6.5}},
            {"id": 5, "state": {"x": 71.5, "y": -82.6, "angle": 0.03, "velocity": 8.5}},
            {"id": 1002, "state": {"x": 78.8, "y": -85.7, "angle": -0.02, "velocity": 7.5}},
            {"id": 1, "state": {"x": 119.0, "y": -86.4, "angle": -0.10, "velocity": 6.0}},
        ],
    },
    {
        "name": "ring_small_lt_slow_truck_block",
        "base": "ring_small_v1.0",
        "type": "弯道慢速长车遮挡 / 队列压缩",
        "risk": "低速长车在弯道前方造成遮挡与队列压缩，主车需要判断跟驰、等待或换道绕行的长期代价。",
        "verify": "验证提前减速和换道时机，重点观察 unsafe_ratio 与 LCC 的同步变化。",
        "ai_desired_vel": 8.0,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 4,
        "changes": [
            {"id": 0, "state": {"velocity": 5.5}},
            {"id": 2, "subclass": "truck", "params": "truck", "state": {"x": 96.8, "y": -79.7, "angle": -0.06, "velocity": 2.0}},
            {"id": 1, "state": {"x": 123.0, "y": -86.8, "angle": -0.11, "velocity": 3.5}},
            {"id": 5, "state": {"x": 72.8, "y": -82.5, "angle": 0.03, "velocity": 8.0}},
        ],
    },
    {
        "name": "ring_tiny_lt_low_friction_cluster",
        "base": "ring_tiny_v1.0",
        "type": "小环高密度低附着 / 操控裕度不足",
        "risk": "车辆横纵向能力被限制，环路空间又很小，激进行为会更快转化为不舒适或不安全状态。",
        "verify": "验证主动推理在高难低裕度场景中是否能降低高方差，尤其关注 unsafe_ratio 标准差。",
        "ai_desired_vel": 7.0,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 4,
        "changes": [
            {"id": 0, "params": "low_mu", "state": {"velocity": 4.0}},
            {"id": 1, "params": "low_mu", "state": {"x": 51.0, "y": 2.2, "angle": -2.38, "velocity": 5.5}},
            {"id": 5, "params": "low_mu", "state": {"x": 64.2, "y": 32.0, "angle": -1.57, "velocity": 5.0}},
            {"id": 1002, "params": "low_mu", "state": {"x": 57.2, "y": 57.5, "angle": -0.74, "velocity": 4.5}},
        ],
    },
    {
        "name": "ring_tiny_lt_conflict_release",
        "base": "ring_tiny_v1.0",
        "type": "拥堵释放 / 低速密集车辆突然形成通行窗口",
        "risk": "多车低速密集排布下，局部间隙短暂出现，系统需要判断抢行收益是否值得承担未来冲突。",
        "verify": "验证方法是否选择保守但稳定的释放策略，避免在短窗口中产生高 LCC 或 unsafe_ratio 尖峰。",
        "ai_desired_vel": 6.5,
        "ai_autonomous_level": 2,
        "ai_aggressiveness_level": 5,
        "changes": [
            {"id": 0, "state": {"velocity": 3.0}},
            {"id": 1, "state": {"x": 51.5, "y": 2.0, "angle": -2.38, "velocity": 2.0}},
            {"id": 4, "state": {"x": 28.8, "y": -18.0, "angle": -2.35, "velocity": 2.5}},
            {"id": 5, "state": {"x": 63.0, "y": 33.0, "angle": -1.57, "velocity": 4.0}},
            {"id": 1000, "state": {"x": 14.0, "y": -32.5, "angle": -2.37, "velocity": 3.0}},
        ],
    },
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def vehicle_by_id(vehicle_set):
    return {vehicle["id"]: vehicle for vehicle in vehicle_set["vehicles"]["info"]}


def apply_changes(vehicle_set, changes):
    vehicles = vehicle_by_id(vehicle_set)
    for change in changes:
        vehicle = vehicles[change["id"]]
        if "subclass" in change:
            vehicle["subclass"] = change["subclass"]
        if "params" in change:
            vehicle["params"] = dict(PARAM_PROFILES[change["params"]])
        if "state" in change:
            vehicle["init_state"].update(change["state"])


def scenario_doc(scenario):
    return f"""# {scenario['name']}

- 基础地图：`{scenario['base']}`
- 长尾类型：{scenario['type']}
- 风险机理：{scenario['risk']}
- 验证重点：{scenario['verify']}
- 推荐周车期望速度：`{scenario['ai_desired_vel']}` m/s
- 推荐周车自动驾驶等级：`{scenario['ai_autonomous_level']}`
- 推荐周车激进度：`{scenario['ai_aggressiveness_level']}`

## 运行示例

```bash
./src/EPSILON/scripts/compare_methods.sh \\
  --playground {scenario['name']} \\
  --duration 120 \\
  --ai-desired-vel {scenario['ai_desired_vel']} \\
  --ai-autonomous-level {scenario['ai_autonomous_level']} \\
  --ai-aggressiveness-level {scenario['ai_aggressiveness_level']}
```
"""


def generate(force=False):
    manifest = []
    for scenario in SCENARIOS:
        src = PLAYGROUNDS / scenario["base"]
        dst = PLAYGROUNDS / scenario["name"]
        if dst.exists():
            if not force:
                raise FileExistsError(f"{dst} already exists; rerun with --force")
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        vehicle_set_path = dst / "vehicle_set.json"
        vehicle_set = load_json(vehicle_set_path)
        apply_changes(vehicle_set, scenario["changes"])
        write_json(vehicle_set_path, vehicle_set)

        scenario_meta = {k: v for k, v in scenario.items() if k != "changes"}
        write_json(dst / "long_tail_manifest.json", scenario_meta)
        (dst / "SCENARIO.md").write_text(scenario_doc(scenario), encoding="utf-8")
        manifest.append(scenario_meta)

    write_json(PLAYGROUNDS / "long_tail_manifest.json", {"scenarios": manifest})


def main():
    parser = argparse.ArgumentParser(description="Generate long-tail playground variants.")
    parser.add_argument("--force", action="store_true", help="Overwrite generated scenario directories.")
    args = parser.parse_args()
    generate(force=args.force)
    print(f"Generated {len(SCENARIOS)} long-tail playgrounds under {PLAYGROUNDS}")


if __name__ == "__main__":
    main()
