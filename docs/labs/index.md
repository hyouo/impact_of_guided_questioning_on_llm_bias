# 实验手册｜十二个命题，十二个独立实验

实验的目标不是让 CI 变绿，而是训练你把理论命题拆成可观测量、干预、对照、反证条件和结论边界。

## 安装与运行

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"

llm-theory-lab list
llm-theory-lab explain C01
llm-theory-lab run-toy --ids C01
```

运行全部透明实验：

```bash
llm-theory-lab run-toy --output-dir reports/all-transparent
```

结果包含机器可读的 `results.json` 和人类可读的 `report.md`。

## 实验地图

| ID | 独立实验 | 主要学习目标 | 课程 |
|---|---|---|---|
| C01 | [权重与激活](02-weight-vs-activation.md) | 区分 magnitude、contribution 与 effectiveness | 第 2 章 |
| C02 | [Softmax 与赔率](01-softmax-and-odds.md) | 从 logit difference 推导相对概率 | 第 2 章 |
| C03 | [输入条件计算](06-input-conditioning.md) | 理解固定权重下的 input-dependent computation | 第 1 章 |
| C04 | [Attention 路由](03-attention-routing.md) | 分开观察 QK 与 OV | 第 3 章 |
| C05 | [自回归反馈](05-autoregressive-feedback.md) | 观察首 token 如何改变未来轨迹 | 第 5 章 |
| C06 | [Superposition](07-superposition.md) | 观察过完备表示与共激活干扰 | 第 4 章 |
| C07 | [Probe 与因果使用](04-probe-vs-causality.md) | 构造“可解码但未被使用”的反例 | 第 6 章 |
| C08 | [Activation patching](08-activation-patching.md) | 检验候选中间状态是否传递因果效应 | 第 6 章 |
| C09 | [安全路由代理](09-safety-routing.md) | 区分识别、策略与最终行为 | 第 7 章 |
| C10 | [基底不变性](10-basis-invariance.md) | 理解内部坐标不自动唯一 | 第 4 章 |
| C11 | [冗余路径](11-redundant-paths.md) | 理解零消融效应与指标饱和 | 第 6 章 |
| C12 | [Steering 对照](12-steering-controls.md) | 用剂量、反向和随机方向检验特异性 | 第 6 章 |

## 统一实验流程

每个实验都按以下顺序完成：

1. 在看结果前写下方向性预测；
2. 用 `explain` 核对命题、反证条件和禁止外推；
3. 运行实验并检查原始指标；
4. 修改一个条件，重新预测；
5. 记录失败、反常或不确定结果；
6. 写出本实验的最大允许结论。

## 如何理解 `pass`

`pass` 只表示当前代码中的预注册数值检查成立。它不表示：

- 真实大模型使用相同坐标或参数比例；
- 候选机制是唯一机制；
- 效应跨输入、任务、模型和 checkpoint 稳定；
- toy 结果已经达到论文级证据；
- 安全代理测量了真实越狱成功率。

透明实验的价值主要有三种：验证精确恒等式、证明某种结构可以发生、以及构造反例推翻错误的一般推理。
