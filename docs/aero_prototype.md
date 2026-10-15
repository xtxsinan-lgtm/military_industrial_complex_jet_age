# 气动原型：F-86E 验证（v0.1）

用 AeroSandbox（MIT 协议）跑通设计文档第 3 节的“2D 翼型 + 涡格法 + 经验公式”管线，并用 F-86E 的史实数据校准。

## 运行

```bash
python3 -m venv .venv && .venv/bin/pip install --only-binary=:all: -r requirements.txt
.venv/bin/python -m aero.scripts.validate_f86   # 验证 + 出图
.venv/bin/python -m aero.scripts.make_table     # 生成 L/D(高度, 马赫, 迎角) 表
```

输出在 `output/`：`f86_polars.png`、`f86_drag_rise.png`、`f86_three_view.png`、`f86_aero_table.csv`。

## 代码结构

| 文件 | 内容 |
|---|---|
| `aero/airfoils.py` | 任意厚度的 NACA 00xx 翼型（F-86 翼根 9.5%、翼尖 8.5%） |
| `aero/aircraft/f86.py` | F-86E 近似几何 + 史实参考值及出处 |
| `aero/analysis.py` | 第 1 档 AeroBuildup、第 2 档 VLM 交叉校验、极曲线摘要 |
| `aero/scripts/validate_f86.py` | 与史实数据对比 |
| `aero/scripts/make_table.py` | 离线生成气动表（1518 个点约 2.5 s） |

## 验证结果

| 指标 | 模型 | 史实 / 参考值 | 误差 |
|---|---|---|---|
| 零升阻力 CD0（35k ft, M0.6） | 0.0128 | 0.0134 | −4.6% |
| 最大升阻比 (L/D)max | 15.2 | 15.0 | +1.3% |
| 升力线斜率 CLα（M0.2），第 1 档 vs 第 2 档 VLM | 0.0714 /° | 0.0715 /° | −0.2% |
| 阻力发散马赫数 Mdd（CL = 0.2） | 0.90 | F-86 平飞极速约 M0.9，俯冲才能超声速 | 趋势正确 |

参考值出处：Loftin, *Quest for Performance*, NASA SP-468, 第 11 章。NTRS 上的文本里 Table V 无法识别，所以参考值是从正文推算的：
- 书中说 F-86E 的 CD0 与 P-80A “大致相同”，P-80A 的阻力面积为 3.2 ft²、机翼面积 238 ft²，由此得 CD0 ≈ 0.0134。
- 书中说 P-80（L/D = 17.6）领先约 17%，由此得 F-86E 的 L/D ≈ 15.0。

注意：Loftin 的 (L/D)max 本身也是由 CD0 加上假设的 e ≈ 0.8 推算出来的，不是直接测量值。

## 已知局限（后续工作）

1. **跨声速失速过于悲观、过于突然**：M0.8 时 CLmax 约 0.37，失速后升力曲线会先塌陷再回升。实际 F-86 在 M0.8 的抖振边界更高；而且 F-86E 装有前缘缝翼，模型里没有。游戏里应把这段处理成“抖振边界”，并用平滑函数代替。
2. **跨声速段的 Oswald e 没有意义**：M ≥ 0.7 时波阻随 CL 增长，极曲线不再是抛物线。拟合出的 e 只在 M ≤ 0.6 时可信。
3. **未配平**：Cm 已经输出，但没有计算平尾配平带来的阻力。
4. **几何是目测的**：机身半径、尾翼位置都是根据三视图估的；进气道内流没有建模。
5. **还没有超声速验证**：需要用 F-100 / F-104 补 DATCOM 波阻，并和史实数据对比。

## 与玩法的对应（设计文档 2.1 节）

- 内置模拟器 → 第 1 档 AeroBuildup，结果附带误差范围
- 风洞 → 第 2 档 VLM + NeuralFoil，误差范围更小
- 试飞 → “真值”模型 + 隐藏问题
