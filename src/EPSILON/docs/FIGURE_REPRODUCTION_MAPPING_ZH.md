# 论文各图获取对照表（2003.02746v1）

本文档对应论文：

- Lu Zhang, Wenchao Ding, Jing Chen, Shaojie Shen, "Efficient Uncertainty-aware Decision-making for Automated Driving Using Guided Branching", arXiv:2003.02746v1, 2020-03-05.

本文目标是为毕业论文写作提供一份可直接引用的“图表复现说明”。每一项均说明：

- 是否可以直接复现
- 推荐获取方式
- 对应命令
- 对应输出文件或产物
- 建议在论文中如何表述

---

## 总体结论

按复现难度可分为三类：

1. 可直接复现：
   - Fig. 6
   - Table I

2. 可近似复现：
   - Fig. 3
   - Fig. 5

3. 不可由仓库直接导出，只能重绘：
   - Fig. 1
   - Fig. 2
   - Fig. 4

原因如下：

- Fig. 1 / Fig. 2 / Fig. 4 属于论文方法示意图，不是系统运行时自动生成的图。
- Fig. 5 使用了真实车载感知数据的 open-loop 测试，当前开源仓库未包含该原始数据。
- Fig. 3 / Fig. 6 属于行为对比和场景可视化，能够用 RViz 截图得到功能上等价的图。
- Table I 可由当前仓库批量实验脚本直接生成。

---

## 统一实验准备

所有可视化类图和表格类结果，建议先统一准备环境：

```bash
cd /home/ying/epsilon-reproduction
source /opt/ros/noetic/setup.bash
source devel/setup.bash
```

如需重新编译：

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/build_workspace.sh /home/ying/epsilon-reproduction
```

打开 `roscore`：

```bash
roscore
```

打开 RViz：

```bash
rviz -d /home/ying/epsilon-reproduction/src/EPSILON/core/phy_simulator/rviz/phy_simulator_planning.rviz
```

EUDM 场景启动：

```bash
roslaunch planning_integrated repro_stack_eudm.launch playground:=highway_v1.0
```

MPDM 场景启动：

```bash
roslaunch planning_integrated repro_stack_mpdm.launch playground:=highway_v1.0
```

统一 RViz 配置文件：

- [phy_simulator_planning.rviz](/home/ying/epsilon-reproduction/src/EPSILON/core/phy_simulator/rviz/phy_simulator_planning.rviz)

常用可视化 topic：

- `/vis/agent_0/ego_behavior_vis`
- `/vis/agent_0/pred_initial_intention_vis`
- `/vis/agent_0/pred_traj_openloop_vis`
- `/vis/agent_0/forward_trajs`
- `/vis/agent_0/ssc/exec_traj`

---

## Fig. 1

论文标题：

- Illustration of the proposed decision-making framework

是否可直接复现：

- 否

原因：

- 该图是作者手工绘制的概念图，用于解释“belief、DCP-Tree、CFB、closed-loop simulation、risky scenario”等概念之间的关系，不是系统运行时导出的可视化结果。

推荐获取方式：

- 根据论文描述和当前代码结构重新绘制一张“复现版框架图”。

建议参考代码模块：

- [eudm_planner.cc](/home/ying/epsilon-reproduction/src/EPSILON/util/eudm_planner/src/eudm_planner/eudm_planner.cc)
- [eudm_manager.cc](/home/ying/epsilon-reproduction/src/EPSILON/util/eudm_planner/src/eudm_planner/eudm_manager.cc)
- [test_ssc_with_eudm.cc](/home/ying/epsilon-reproduction/src/EPSILON/app/planning_integrated/src/test_ssc_with_eudm.cc)

可用于重绘的结构建议：

- 输入：semantic map / nearby agents / initial belief
- EUDM：DCP-Tree action branching
- CFB：intention branching
- Forward simulation：policy evaluation
- 输出：best policy sequence
- 下游：SSC motion planner

输出文件：

- 无仓库自动输出文件，需手工绘制为 `png/pdf/svg`

论文中建议表述：

- “Fig. 1 为方法框架示意图，原论文未提供自动生成脚本。本文依据开源实现的模块结构进行了重绘。”

---

## Fig. 2

论文标题：

- Illustration of the proposed decision-making framework (in the blue box) and its relationship with other system components

是否可直接复现：

- 否

原因：

- 这是一张系统模块关系图，展示 decision-making 与 motion planning、prediction、simulator 等模块的关系，不是程序直接导出的图。

推荐获取方式：

- 根据系统 launch 结构和代码依赖关系重绘。

建议参考文件：

- [repro_stack_eudm.launch](/home/ying/epsilon-reproduction/src/EPSILON/app/planning_integrated/launch/repro_stack_eudm.launch)
- [test_ssc_with_eudm_ros.launch](/home/ying/epsilon-reproduction/src/EPSILON/app/planning_integrated/launch/test_ssc_with_eudm_ros.launch)
- [phy_simulator_planning.launch](/home/ying/epsilon-reproduction/src/EPSILON/core/phy_simulator/launch/phy_simulator_planning.launch)
- [onlane_ai_agent.launch](/home/ying/epsilon-reproduction/src/EPSILON/util/ai_agent_planner/launch/onlane_ai_agent.launch)

推荐图中保留的模块：

- Semantic map manager
- EUDM behavior planner
- SSC planner
- Physical simulator
- AI agents
- Visualization / RViz

输出文件：

- 无仓库自动输出文件，需手工绘制为 `png/pdf/svg`

论文中建议表述：

- “Fig. 2 为系统结构图，依据开源工程中的 launch 组织关系与模块调用关系进行重绘。”

---

## Fig. 3

论文标题：

- Comparison of MPDM (left) and EUDM (right)

是否可直接复现：

- 可近似复现

原因：

- 原论文图是作者手工选取代表性时刻并排版后的对比图，但系统能输出与其语义一致的 RViz 可视化结果。

推荐获取方式：

- 分别运行 `MPDM` 和 `EUDM`。
- 在相近交通场景、相近时刻截图。
- 将两张截图并排排版为“left: MPDM, right: EUDM”。

推荐命令：

MPDM：

```bash
cd /home/ying/epsilon-reproduction
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch planning_integrated repro_stack_mpdm.launch playground:=highway_v1.0
```

EUDM：

```bash
cd /home/ying/epsilon-reproduction
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch planning_integrated repro_stack_eudm.launch playground:=highway_v1.0
```

截图时建议保留的 RViz 图层：

- `/vis/agent_0/ego_behavior_vis`
- `/vis/agent_0/forward_trajs`
- `/vis/agent_0/ssc/exec_traj`

建议输出文件：

- `fig3_mpdm.png`
- `fig3_eudm.png`
- 最终排版图：`fig3_compare.png`

论文中建议表述：

- “Fig. 3 为基于开源仿真平台复现得到的定性对比图。本文在相同地图与近似交通状态下分别运行 MPDM 与 EUDM，并在 RViz 中截取代表性时刻进行并排展示。”

---

## Fig. 4

论文标题：

- Illustration of the proposed DCP-Tree and the rebuilding process

是否可直接复现：

- 否

原因：

- 该图是树结构的概念解释图，不是系统默认输出的图形。

推荐获取方式：

- 根据论文 IV-B 小节和算法描述手工重绘。

参考内容：

- 论文文字中明确说明：每条 policy sequence 在一个 planning cycle 中最多包含一次动作切换。
- 树高度与动作集合来自论文设定：`{LK, LCL, LCR}` 加纵向动作组合。

参考代码：

- [eudm_planner.cc](/home/ying/epsilon-reproduction/src/EPSILON/util/eudm_planner/src/eudm_planner/eudm_planner.cc)

输出文件：

- 无仓库自动输出文件，需手工绘制

论文中建议表述：

- “Fig. 4 为 DCP-Tree 机制示意图，本文依据论文算法描述与代码中的策略展开逻辑进行了重绘。”

---

## Fig. 5

论文标题：

- Open-loop test using onboard sensing data

是否可直接复现：

- 原图不可直接复现
- 可做仿真近似替代图

原因：

- 原论文使用“真实车载感知数据”，仓库中未提供对应 raw data / rosbag / perception result。
- 但系统支持在仿真中显示类似的“belief / risky scenario / lane-change decision”结果。

推荐获取方式：

方案 A：论文严格表述

- 在毕业论文中明确写明“由于开源仓库未提供原始 onboard sensing data，原 Fig. 5 不可 1:1 复现”。

方案 B：给出替代图

- 使用仿真场景创建“前车插入 / aggressive merge / ego decelerate”的近似案例。
- 在 RViz 中保留以下图层：
  - `/vis/agent_0/pred_initial_intention_vis`
  - `/vis/agent_0/pred_traj_openloop_vis`
  - `/vis/agent_0/ego_behavior_vis`
  - `/vis/agent_0/forward_trajs`

推荐命令：

```bash
cd /home/ying/epsilon-reproduction
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch planning_integrated repro_stack_eudm.launch playground:=highway_v1.0
```

建议输出文件：

- `fig5_case1.png`
- `fig5_case2.png`
- `fig5_reproduced.png`

论文中建议表述：

- “原 Fig. 5 依赖真实车载感知数据，该数据未在开源仓库中发布，因此本文无法进行严格复现。本文使用开源仿真平台构造相似交互场景，给出功能等价的定性替代图。”

---

## Fig. 6

论文标题：

- Illustration of different decision-making results in a conflict zone

是否可直接复现：

- 是

原因：

- 该图本质上是交互仿真中的定性结果展示，当前仓库支持完整运行 EUDM 和可视化 forward trajectories、behavior decision、executed trajectory。

推荐获取方式：

- 运行 EUDM。
- 在冲突区、超车、让行等关键时刻暂停 RViz 截图。
- 如果要得到论文中 `(a)` 与 `(b)` 结构，建议分别收集两组案例：
  - `(a)` overtake the leading vehicle
  - `(b)` give up overtaking and yield

推荐命令：

```bash
cd /home/ying/epsilon-reproduction
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch planning_integrated repro_stack_eudm.launch playground:=highway_v1.0
```

或尝试 ring 类地图：

```bash
cd /home/ying/epsilon-reproduction
source /opt/ros/noetic/setup.bash
source devel/setup.bash
roslaunch planning_integrated repro_stack_eudm.launch playground:=ring_small_v1.0
```

建议保留的 RViz 图层：

- `/vis/agent_0/ego_behavior_vis`
- `/vis/agent_0/pred_initial_intention_vis`
- `/vis/agent_0/forward_trajs`
- `/vis/agent_0/ssc/exec_traj`
- `/vis/agent_0/surrounding_vehicle_vis`

建议输出文件：

- `fig6_a_1.png`
- `fig6_a_2.png`
- `fig6_a_3.png`
- `fig6_b_1.png`
- `fig6_b_2.png`
- `fig6_b_3.png`
- 最终排版图：`fig6_reproduced.png`

论文中建议表述：

- “Fig. 6 可由开源仿真平台直接复现。本文在相同地图下运行 EUDM，并在冲突区相关交互时刻截取 RViz 画面，整理得到超车与让行两类决策结果图。”

---

## Table I

论文标题：

- Comparison of different decision-making approaches

是否可直接复现：

- 是

原因：

- 当前工程已补充批量实验和统计脚本，可直接输出单轮和多轮聚合结果。

单轮对比命令：

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/compare_methods.sh --playground highway_v1.0 --duration 300 --workspace /home/ying/epsilon-reproduction
```

多轮均值统计命令：

```bash
cd /home/ying/epsilon-reproduction/src/EPSILON
./scripts/repeat_compare_methods.sh --playground highway_v1.0 --duration 120 --runs 5 --workspace /home/ying/epsilon-reproduction
```

当前已有结果：

- [summary.csv](/home/ying/epsilon-reproduction/results/compare_highway_v1.0_20260423_110233/summary.csv)
- [aggregate_summary.csv](/home/ying/epsilon-reproduction/results/repeat_highway_v1.0_runs5_dur120_20260424_105518/aggregate_summary.csv)
- [table1_style.csv](/home/ying/epsilon-reproduction/results/repeat_highway_v1.0_runs5_dur120_20260424_105518/table1_style.csv)

当前多回合统计使用指标：

- `unsafe_ratio`
- `average_velocity_mps`
- `ud_per_km`
- `lcc_per_km`

论文中建议表述：

- “Table I 由本文在开源代码基础上完成多回合仿真实验后统计得到。由于开源 playground 与原论文 benchmark map 不完全一致，因此本文结果用于复现实验验证，而不宣称与原文数值完全一致。”

---

## 毕业论文推荐写法

如果你要写研究生毕业论文，建议把图表复现说明写成以下三类：

1. 严格复现：
   - Table I
   - Fig. 6

2. 近似复现：
   - Fig. 3
   - Fig. 5 替代图

3. 重绘说明图：
   - Fig. 1
   - Fig. 2
   - Fig. 4

推荐一句总括性表述：

- “本文针对论文中的图表分别采用了三种处理方式：对于实验结果表与仿真定性图进行直接复现；对于依赖真实车载数据但数据未公开的图进行功能等价替代；对于方法框架类示意图依据论文描述与开源实现进行重绘。”

---

## 建议的论文附录组织

建议在附录中加入一个表格，列如下：

- 编号
- 原论文图名
- 是否可直接复现
- 本文处理方式
- 对应命令
- 对应结果文件

如果需要，我可以继续把这份文档再整理成：

- 适合毕业论文正文的 LaTeX 表格版本
- 适合附录的 Markdown 表格版本
- 适合答辩 PPT 的一页总结版
