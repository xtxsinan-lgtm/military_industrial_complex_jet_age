# 设计细化总计划 & 进度

> 目标：在写正式代码前，把 MVP（美国 1945–1960）细化到**最低端 AI agent 也能照做**的任务单级，并用 Python 参考实现 + 模拟验证可玩性。

## 已锁定决策
- **D1–D5（基础架构与范围）**：
  - Godot 4 + C#：纯 C# 模拟内核（`MIC.Core`，零 Godot 依赖，可 `dotnet test`）+ Godot UI 层（`MIC.Game`）
  - MVP（美国 1945–1960）细化到任务单级，后续阶段（1960–2030、战争、外销、法/苏/多国模式）细化到系统级
  - 5 种验证方法全部采用：物理校准、设计空间帕累托/漏洞搜索、蒙特卡洛机器人玩家平衡、文字版纸面原型、笨 agent 测试
  - 全部使用真实历史名称，但名称统一抽离在 `sim/data/names/*.json` 数据文件中
- **D6–D10（第 1 波后锁定的口味决策 A1–A5）**：
  - **D6（采购模式 A1）**：游戏默认将**所有主战项目统一为两阶段 `flyoff`（真机同台竞飞）**以最大化戏剧张力；代码保留 `paper_award` / `sole_source` 作为战役设置开关（“严格史实库克-克雷吉模式”）。
  - **D7（科技与缺陷迷雾 A2）**：1945–1960 科技树从开局全貌可见（标注历史年份与超前惩罚）；时代未知缺陷在 `known_from_year` 之前显示为笼统的 **“未知高速领域风险”**，首次遭遇后永久解锁具体名称（配开局“历史后见之明”开关）。
  - **D8（1960 之后延续 A3）**：`1960-12-31` 锁定正式战役评分与历史结局报告后，允许点击 **“继续沙盒模式”**（由动态 RFP 生成器持续生成后续竞标）。
  - **D9（试飞员与航发厂点名 A4）**：试飞员采用符合 1950 年代风格的**虚构姓名库**（避免试飞坠机写死真实历史人物）；委托外部定制发动机时**显式点名真实航发巨头**（`Pratt & Whitney`、`General Electric`、`Allison`、`Curtiss-Wright`、`Westinghouse`）并附带厂牌特长修正。
  - **D10（截标前竞争对手情报 A5）**：截标前通过**航空媒体传闻/情报**显示竞争对手大致性能与报价区间（带大误差棒）；定标后在 **Source Selection Debrief（评标复盘报告）** 中公开五维完整得分明细。

脊柱文档：[00_conventions.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/00_conventions.md)（v1.2，已写入 D1–D10）

---

## 第 1 波（✅ 100% 完成，已提交 Commit `c1425be`，67 项 pytest 全通）

| 模块 | 规格文档 | Python 参考实现 & 数据 | 验证报告 & 核心指标 | 状态 |
|---|---|---|---|---|
| **01 气动与性能** | [01_aero_physics.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/01_aero_physics.md) | `sim/mic/aero/`, `sim/mic/perf/`, 14 架史实校准机 `sim/data/aircraft_hist/*.json` | [aero_calibration.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/aero_calibration.md)：14 架史实机总体平均误差 **6.52%**；成功复现 `YF-102`（M 1.03 卡音障）→ `F-102A`（面积律修形后 M 1.35）的物理跃迁；2000 组随机极端设计 **0 NaN** | ✅ 完成 |
| **02 发动机与研发** | [02_engines.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/02_engines.md) | `sim/mic/engine/`, 12 台史实发动机 `sim/data/engines_hist/*.json` | [engine_calibration.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/engine_calibration.md)：12 台美苏发动机平均误差 **2.43%**（最大 **7.34%**）；[engine_rnd.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/engine_rnd.md) 验证目录采购 / 定制立项 / 自建发动机部门三层风险收益 | ✅ 完成 |
| **03 科技树 + 10 史实内容** | [03_tech_effect_keys.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/03_tech_effect_keys.md), [03_tech_tree.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/03_tech_tree.md), [10_content.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/10_content.md) | `sim/mic/tech/`, `sim/data/tech/*.json`, `sim/data/companies/*.json`, `sim/data/names/*.json` | 87 个标准效果键、7 大分支科技树、12 款雷达 / 7 款机炮 / 7 款导弹组件库、13 家主机厂 + 5 家航发厂 + 29 位总师、1962 前美空海军编号生成器 | ✅ 完成 |
| **04 公司经济** | [04_economy.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/04_economy.md) | `sim/mic/econ/`, `sim/data/economy/*.json` | [econ_cost_calibration.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/econ_cost_calibration.md)：12 架史实机出厂价误差 **7.75%**、研发费误差 **10.28%**；[econ_cashflow.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/econ_cashflow.md)：2400 场战役蒙特卡洛证明无单一必胜策略 | ✅ 完成 |
| **05 竞标与项目库** | [05_procurement.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/05_procurement.md) | `sim/mic/procurement/`, 16 个史实项目 + 苏联威胁库 `sim/data/programs/*.json` | [procurement_replay.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/procurement_replay.md)：16 个史实项目赢家 **16/16 (100%) 命中**；新厂商击败在位巨头需 **+7.7% 性能优势**（配合降价与风洞证明则降至 **+5.5%**） | ✅ 完成 |
| **06 试飞与不确定性** | [06_testing_uncertainty.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/06_testing_uncertainty.md) | `sim/mic/testing/`, 34 种隐藏缺陷库 `sim/data/testing/*.json` | [testing_value.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/testing_value.md)：2400 场研发模拟证明低新颖度适合轻度测试（S3 最优），跨音速/超音速高新颖度必须做开槽风洞与完整试飞（S4 最优），服役期修缺陷成本为风洞期的 **48 倍** | ✅ 完成 |
| **09 核心循环与架构** | [09_core_loop.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/09_core_loop.md) | `sim/mic/rng.py`, `sim/mic/calendar.py`, `sim/mic/campaign/` | Python 与 C# 位级完全一致的 `PCG32` + `FNV-1a` 独立随机流、三阶段日/月/财年结算顺序、26 个标准玩家/AI 动作指令、存档与确定性回放校验 | ✅ 完成 |

---

## 第 2 波：AI、UI/UX 规格与全战役平衡 / 设计空间验证（✅ 100% 完成）

| 模块 / 验证 | 规格文档 / 验证报告 | Python 参考实现 & 数据 | 核心指标 & 结论 | 状态 |
|---|---|---|---|---|
| **07 竞争对手 AI 与情报** | [07_competitor_ai.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/07_competitor_ai.md) | `sim/mic/ai/`, `sim/data/tuning/ai.json`, `sim/golden/ai_*.json` | 12 家非玩家美国主机厂月度演化与历史退场、AI 参数化飞机设计合成器、两阶段竞飞试飞策略、截标前航空媒体传闻（**D10**）及 5 大航发厂点名定制报价（**D9**）；`test_ai.py` **7/7 全通** | ✅ 完成 |
| **08 逐屏 UI/UX 规格** | [08_ui_ux.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/08_ui_ux.md)（94 KB，1020 行） | 绑定 `09_core_loop.md` 全部 26 个指令与 `Units` 单位换算 | 1950s 蓝图与黄铜视觉主题、全局顶栏、`EstimateBadge` 误差棒控件、全部 9 大界面（含三视图、翼型压力分布、**Sears–Haack 面积律截面积分布图 $A(x)$**、**Boyd $P_s$ 包线热力图**、试飞未知风险卡 **D7**、真机竞飞看板 **D6**、截标前传闻与评标复盘弹窗 **D10**、1960 结局与沙盒延续弹窗 **D8**） | ✅ 完成 |
| **验证 #2：设计空间帕累托与漏洞审计** | [design_space_pareto.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/design_space_pareto.md) | [design_space_search.py](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/validation/design_space_search.py), `design_space_results.json` | 跨 1946 / 1951 / 1954 三个时代采样优化 **2,070 架**飞机（`6.1 ms/架`），生成 63–119 个非支配解构成的 4 维帕累托前沿；**12 种极端角落作弊构型（`C01`–`C12`）100% 被物理/结构/科技上限/门槛拦截** | ✅ 完成 |
| **验证 #3：全战役机器人蒙特卡洛平衡** | [campaign_bot_balance.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/campaign_bot_balance.md) | [integrated.py](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/campaign/integrated.py), [bots.py](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/mic/campaign/bots.py), [campaign_balance_mc.py](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/sim/validation/campaign_balance_mc.py) | 400 场 1945–1960 完整战役模拟证明：在两阶段真机竞飞（**D6**）下，`SpeedDemonSkipTestBot`（跳试飞快冲型）因原型机坠毁（2.58 次/局）与未修缺陷被大幅淘汰（仅赢 0.76 单，破产率 48%）；`ConservativeGoldPlaterBot` 因 +25% 溢价丢标（仅赢 0.50 单）；`BalancedPrimeBot`（赢 3.40 单，净值 \$43.4M）与 `TechPioneerBot`（赢 3.24 单，净值 \$68.5M）表现最优；年均关键决策 **9.4–10.4 次/年** | ✅ 完成 |
| **验证 #4：交互式网页验证原型 (GitHub Pages)** | 线上地址：`https://xtxsinan-lgtm.github.io/military_industrial_complex_jet_age/` | `web/index.html`, `web/app.js`, `web/sim_kernel.js`, `web/canvas_plots.js`, `web/data_bundle.js` | 打包全部 14 架史实飞机、12 款发动机、16 个竞标项目与 Python Oracle 基准数据；支持 4 大经典剧本一键切换、实时拖动气动参数滑块、**4 大实时工程蓝图画布（正交三视图、Sears–Haack 面积律截面积分布图 $A(x)$、Boyd 能量包线 $P_s$、跨音速波阻曲线 $C_{D0}(M)$）**、风洞/4 阶段试飞排雷（含 **D7 未知高速风险** 与 **D9 试飞员名册**）、航发五巨头点名定制（**D9**）、截标前传闻与真机竞飞复盘（**D6 & D10**） | ✅ 已上线 |

---

## 第 3 波：后续阶段（Phase 2–5）系统级规格（✅ 100% 完成）

| 模块 | 规格文档 | 核心设计内容 | 状态 |
|---|---|---|---|
| **21 局部战争与空战反馈** | [21_war_system.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/21_war_system.md)（48 KB） | 季度战区出动引擎（BVR 雷达/导弹交换 + WVR Boyd 能量机动狗斗 + 对地/SAM 防空损耗）、出动率 `SGR` 与热带/沙漠环境应力、战损复盘报告 `CombatAAR` 动态改变军方评标权重并触发战时紧急改型（ECP）与备件急单 | ✅ 完成 |
| **22 军贸外销与地缘政治** | [22_export_geopolitics.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/22_export_geopolitics.md)（35 KB） | 美/法/苏/不结盟军贸审批体制、4 级外贸改型（含猴版减配 `MonkeyModel` 与客户定制版）、许可证组装生产（`CKD`）技术外溢、洛克希德式海外行贿丑闻风险、敌机秘密评估（`Have Doughnut`）与逆向仿制 | ✅ 完成 |
| **23 多国制度原型与 1960–2030 时代扩展** | [23_nations_and_eras_1960_2030.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/spec/23_nations_and_eras_1960_2030.md)（35 KB） | 四大国家制度原型（美国五角大楼市场型、法国达索家族谱系+外贸型、苏联 OKB 设计局+GAZ 国营厂+TsAGI 气动门禁型、后发许可证追赶型与欧洲份额分配联合体）+ 1960–2030 四大跨代扩展（变后掠翼、放宽静稳定度+电传、三维 RCS 隐身+超巡+推力矢量、无人忠诚僚机+自适应变循环）及零破坏 Schema 兼容表 | ✅ 完成 |

---

## 第 4 波：C# / Godot 4 任务单拆分与“笨 Agent 净室测试”（✅ 100% 完成）

| 交付物 | 文档路径 | 内容与验证结果 | 状态 |
|---|---|---|---|
| **00 总体实施路线图** | [00_master_roadmap.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/workplan/00_master_roadmap.md) | 解决方案结构（`MIC.Core`, `MIC.Core.Tests`, `MIC.Game`）、`.csproj` 配置、30 张任务单依赖 DAG 与黄金向量容差矩阵 | ✅ 完成 |
| **T01–T05 基础与气动** | [T01_T05_foundation_and_aero.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/workplan/T01_T05_foundation_and_aero.md) | `Pcg32` / `GameCalendar`、共享数据契约、ISA 大气与 CST 翼型、VLM 与面积律波阻 $A(x)$、`PerformanceEvaluator` | ✅ 完成 |
| **T06–T10 航发与科技** | [T06_T10_engines_and_tech.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/workplan/T06_T10_engines_and_tech.md) | 布雷顿循环与性能表、航发定径与研发、87 个科技效果键与 DAG、超前惩罚与成熟度、美军机型编号生成器 | ✅ 完成 |
| **T11–T16 经济/采购/试飞** | [T11_T16_econ_procurement_testing.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/workplan/T11_T16_econ_procurement_testing.md) | DAPCA 成本与学习曲线、合同结算、五角大楼评标、两阶段真机竞飞（**D6**）与复盘（**D10**）、隐藏缺陷与 4 阶段试飞（**D7 & D9**） | ✅ 完成 |
| **T17–T22 AI 与主循环** | [T17_T22_ai_and_core_loop.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/workplan/T17_T22_ai_and_core_loop.md) | 12 家竞争对手 AI、参数化飞机合成器、截标前传闻（**D10**）、5 大航发厂报价（**D9**）、26 指令主循环与 1960 沙盒延续（**D8**） | ✅ 完成 |
| **T23–T30 Godot 4 UI 层** | [T23_T30_godot_ui_screens.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/workplan/T23_T30_godot_ui_screens.md) | `MainShell`、`Units`、`EstimateBadge`、Screens 0–8 节点树、Presenter 签名与 4 大 2D 工程矢量画布 | ✅ 完成 |
| **验证 #5：“笨 Agent 测试”** | [dumb_agent_test.md](file:///Users/xtxsinan/.gemini/antigravity/scratch/military_industrial_complex_jet_age/docs/validation/dumb_agent_test.md) | 使用最低端 `flash_lite` 模型在禁止读取 `sim/mic/` 的净室条件下独立执行 `T01`，**0 提问一次通过 100% 黄金测试向量** | ✅ 完成 |



