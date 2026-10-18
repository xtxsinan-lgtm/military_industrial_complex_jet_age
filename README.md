# Military-Industrial Complex: Jet Age (《军工复合体：喷气时代》)

一款冷战早期（1945–1960）美国喷气式战斗机主机厂经营、气动总体设计、风洞/试飞排雷与五角大楼竞标模拟游戏。

🌐 **在线交互验证原型 (GitHub Pages)**：  
👉 **[https://xtxsinan-lgtm.github.io/military_industrial_complex_jet_age/](https://xtxsinan-lgtm.github.io/military_industrial_complex_jet_age/)**

---

## 1. 核心规格文档体系 (`docs/spec/`)

| 编号 | 规格文档 | 说明 |
| :--- | :--- | :--- |
| **00** | [`docs/spec/00_conventions.md`](docs/spec/00_conventions.md) | 跨模块统一契约、单位制（内部 SI / 显示美制）、确定性随机数与已锁定决策 **D1–D10** |
| **01** | [`docs/spec/01_aero_physics.md`](docs/spec/01_aero_physics.md) | ISA 1976 大气、CST/NACA 翼型、修正 Weissinger VLM、64 站 Sears–Haack 面积律波阻 $A(x)$、Boyd $P_s$ 包线与性能评估 |
| **02** | [`docs/spec/02_engines.md`](docs/spec/02_engines.md) | 1D 变比热布雷顿热力循环、非设计点推进表、航发定径与自研/委托研发 |
| **03** | [`docs/spec/03_tech_tree.md`](docs/spec/03_tech_tree.md) & [`03_tech_effect_keys.md`](docs/spec/03_tech_effect_keys.md) | 1945–1960 科技树（82 节点、87 个标准效果键）、布鲁克斯定律、超前研发惩罚与 NACA 扩散 |
| **04** | [`docs/spec/04_economy.md`](docs/spec/04_economy.md) | 修正 DAPCA-IV 研发/出厂成本、Wright 82% 学习曲线、CPFF/FPIF/FFP 合同结算与破产重整 |
| **05** | [`docs/spec/05_procurement.md`](docs/spec/05_procurement.md) | 16 个史实美军招标项目、两阶段真机同台竞飞（**D6**）、评标打分与定标复盘报告（**D10**） |
| **06** | [`docs/spec/06_testing_uncertainty.md`](docs/spec/06_testing_uncertainty.md) | 贝叶斯 `Estimate (±1σ)` 收敛、开槽跨音速风洞、爱德华兹 4 阶段试飞、34 种隐藏缺陷与时代迷雾（**D7 & D9**） |
| **07** | [`docs/spec/07_competitor_ai.md`](docs/spec/07_competitor_ai.md) | 12 家美国竞争对手 AI 演化、参数化飞机合成器、截标前媒体传闻（**D10**）与 5 大航发巨头点名定制（**D9**） |
| **08** | [`docs/spec/08_ui_ux.md`](docs/spec/08_ui_ux.md) | Godot 4 逐屏 UI/UX 规格（Screens 0–8 节点树、4 大气动工程画布、`EstimateBadge` 与 26 指令绑定） |
| **09** | [`docs/spec/09_core_loop.md`](docs/spec/09_core_loop.md) | 位级一致 `PCG32` + `FNV-1a` 随机流、三阶段日历结算、26 个标准动作指令、存档与 1960 沙盒延续（**D8**） |
| **10** | [`docs/spec/10_content.md`](docs/spec/10_content.md) | 13 家主机厂、5 家航发厂、29 位总师、武器雷达组件库与 1962 前美空海军编号规则 |
| **21–23** | [`21_war_system.md`](docs/spec/21_war_system.md), [`22_export_geopolitics.md`](docs/spec/22_export_geopolitics.md), [`23_nations_and_eras_1960_2030.md`](docs/spec/23_nations_and_eras_1960_2030.md) | 后续阶段系统级规格：局部战争双层空战反馈、军贸外销与猴版减配、法/苏/多国制度原型与 1960–2030 跨代扩展 |

---

## 2. 五大可玩性与数值校准验证报告 (`docs/validation/`)

1. **验证 #1（史实物理与经济校准）**：
   - [`docs/validation/aero_calibration.md`](docs/validation/aero_calibration.md)：14 架史实名机 98 项指标总体平均误差 **6.52%**，精确复现 `YF-102`（M 1.03 卡音障）到 `F-102A`（面积律蜂腰修形后 M 1.35）的跃迁。
   - [`docs/validation/engine_calibration.md`](docs/validation/engine_calibration.md) & [`engine_rnd.md`](docs/validation/engine_rnd.md)：12 台史实航发平均误差 **2.43%**（最大 **7.34%**）。
   - [`docs/validation/econ_cost_calibration.md`](docs/validation/econ_cost_calibration.md) & [`econ_cashflow.md`](docs/validation/econ_cashflow.md)：12 架战机出厂价平均误差 **7.75%**，2,400 场现金流蒙特卡洛验证。
   - [`docs/validation/procurement_replay.md`](docs/validation/procurement_replay.md)：16 个史实美军招标项目历史赢家 **16/16 (100%) 命中**。
   - [`docs/validation/testing_value.md`](docs/validation/testing_value.md)：2,400 场试飞模拟验证跨音速高新颖度构型必须做开槽风洞与完整试飞（服役期改缺陷成本为风洞期的 48 倍）。
2. **验证 #2（12 维设计空间帕累托前沿与极端角落漏洞审计）**：
   - [`docs/validation/design_space_pareto.md`](docs/validation/design_space_pareto.md)：跨 3 个时代评估 2,070 架设计（`6.1 ms/架`），**12/12 (100%) 极端角落作弊构型被物理/科技上限/门槛拦截**。
3. **验证 #3（1945–1960 全模块集成战役 4 机器人蒙特卡洛平衡）**：
   - [`docs/validation/campaign_bot_balance.md`](docs/validation/campaign_bot_balance.md)：400 场完整战役验证两阶段真机竞飞（**D6**）有效淘汰“吹牛跳试飞党”，年均关键决策 **9.4–10.4 次/年**。
4. **验证 #4（交互式网页原型 & 命令行纸面原型）**：
   - 网页版：[`web/`](web/)（已部署至 [GitHub Pages](https://xtxsinan-lgtm.github.io/military_industrial_complex_jet_age/)）
   - 命令行版：[`sim/validation/paper_prototype_cli.py`](sim/validation/paper_prototype_cli.py)
5. **验证 #5（`flash_lite` 净室“笨 Agent 测试”）**：
   - [`docs/validation/dumb_agent_test.md`](docs/validation/dumb_agent_test.md)：使用最低端 `flash_lite` 模型在禁止读取 `sim/mic/` 的净室条件下独立执行 `T01`，**0 提问一次通过 100% 黄金测试向量**。

---

## 3. Godot 4 + C# (.NET 8) 任务单级实施计划 (`docs/workplan/`)

- [`docs/workplan/00_master_roadmap.md`](docs/workplan/00_master_roadmap.md) — 解决方案架构、30 张任务单依赖 DAG 与黄金向量绑定矩阵
- [`docs/workplan/T01_T05_foundation_and_aero.md`](docs/workplan/T01_T05_foundation_and_aero.md) — 基础随机数/日历、共享契约、ISA 大气、翼型、VLM 与面积律波阻、性能评估
- [`docs/workplan/T06_T10_engines_and_tech.md`](docs/workplan/T06_T10_engines_and_tech.md) — 航发热力循环、航发研发、科技树 DAG、超前惩罚、美军编号生成器
- [`docs/workplan/T11_T16_econ_procurement_testing.md`](docs/workplan/T11_T16_econ_procurement_testing.md) — 成本与学习曲线、合同结算、招标评分、两阶段真机竞飞、隐藏缺陷与 4 阶段试飞
- [`docs/workplan/T17_T22_ai_and_core_loop.md`](docs/workplan/T17_T22_ai_and_core_loop.md) — 竞争对手 AI、飞机合成器、截标前传闻、航发厂报价、26 指令主循环与存档
- [`docs/workplan/T23_T30_godot_ui_screens.md`](docs/workplan/T23_T30_godot_ui_screens.md) — Godot 4 全局外壳、`EstimateBadge`、Screens 0–8 节点树与 4 大 2D 工程矢量画布

---

## 4. 运行 Python 参考实现 (Oracle) 与测试套件

```bash
.venv/bin/python -m pytest sim/tests/ -v
```
当前全库 **77 / 77 项测试全部通过**，生成的 19 组黄金测试向量位于 [`sim/golden/`](sim/golden/)。
