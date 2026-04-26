# 2003.02746 复现方案（EUDM Guided Branching）

## 1. 目标与范围

本文档用于在当前仓库中复现论文 **Efficient Uncertainty-aware Decision-making for Automated Driving Using Guided Branching**（arXiv:2003.02746v1, 2020-03-05）核心实验流程。

已覆盖：
- EUDM 与 MPDM 的统一场景对比运行。
- 一键启动完整栈（规划器 + AI 交通体 + 物理仿真器）。
- 自动采集核心指标并输出对比结果。

说明：
- 论文中展示了 `Double Merge` 与 `Ring` 基准。当前仓库提供 `highway_v1.0 / highway_lite / ring_small_v1.0 / ring_tiny_v1.0` playground。可在 `highway` 和 `ring` 家族地图上完成同类复现实验。

## 2. 论文关键参数映射

论文关键设置（v1 文字描述）：
- 决策频率目标：20 Hz。
- 规划时域：最长约 8 s。
- 安全/舒适度指标：unsafe frame ratio、平均速度、UD 与 LCC（阈值 1.6 m/s^2、0.12 (s*m)^-1）。

仓库映射：
- EUDM 入口：`planning_integrated/test_ssc_with_eudm`。
- MPDM 入口：`planning_integrated/test_ssc_with_mpdm`。
- EUDM 配置：`util/eudm_planner/config/eudm_config.pb.txt`。
- 指标自动计算：`scripts/eval_metrics.py`（UD/LCC 与论文同阈值默认）。

## 3. 环境准备

依赖（Ubuntu + ROS Noetic）：

```bash
sudo apt-get update
sudo apt-get install -y libgoogle-glog-dev libdw-dev libopenblas-dev gfortran
pip3 install empy pygame
```

构建：

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/build_workspace.sh /home/ying/epsilon-reproduction
```

## 4. 一键运行单方法

EUDM：

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/run_stack.sh --method eudm --playground highway_v1.0 --duration 60
```

MPDM：

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/run_stack.sh --method mpdm --playground highway_v1.0 --duration 60
```

输出目录默认在：

```text
/home/ying/epsilon-reproduction/results/<method>_<playground>_<timestamp>/
```

关键输出：
- `metrics.json`：unsafe_ratio、average_velocity_mps、ud_per_km、lcc_per_km。
- `hz_arena_info_dynamic.txt`：仿真主动态话题频率（通常接近 100Hz，决策节点内部保持 20Hz）。
- `launch.log`：完整运行日志。

## 5. 一键对比 EUDM vs MPDM

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/compare_methods.sh --playground highway_v1.0 --duration 60
```

输出：
- `.../compare_<playground>_<timestamp>/eudm/metrics.json`
- `.../compare_<playground>_<timestamp>/mpdm/metrics.json`
- `.../compare_<playground>_<timestamp>/summary.csv`

`summary.csv` 字段：
- `unsafe_ratio`
- `average_velocity_mps`
- `ud_per_km`
- `lcc_per_km`
- `distance_m`
- `frames`

## 6. 统一参数修正（已完成）

为保证复现一致性，新增了统一入口 launch：
- `app/planning_integrated/launch/repro_stack_eudm.launch`
- `app/planning_integrated/launch/repro_stack_mpdm.launch`

这两个入口会对 `planner / ai_agent / simulator` 使用同一个 `playground` 参数，避免原始默认值不一致造成实验偏差。

## 7. 已验证状态

在当前机器上已完成：
- `catkin_make` 全量通过。
- 无界面联调启动通过（planner + agents + simulator 正常发布话题）。
- `/arena_info_dynamic` 实测频率稳定在约 100Hz 量级。

## 8. 可选扩展

- 切换到 `ring_small_v1.0` 或 `ring_tiny_v1.0` 复现 ring 类场景。
- 增加多次重复（不同随机种子）并统计均值/方差。
- 若你需要严格对齐论文表格格式（Table I），可在 `summary.csv` 基础上扩展批量脚本汇总多个回合结果。
