# 第 6 章｜从相关、可解码到因果机制

## 学完你应该能

- 区分相关、可解码、必要、充分和机制忠实；
- 解释 probe、ablation、steering 和 activation patching 各自能证明什么；
- 为一个机制主张设计正对照、负对照和反证条件；
- 识别“漂亮解释但机制不忠实”的风险。

## 核心模型

机制主张不只是：

> 激活 $h$ 与标签 $y$ 相关。

更强的主张是：某个内部变量 $m$ 在输入 $x$ 到输出 $o$ 的因果链中承担特定作用。我们希望比较：

$$
o(x),
\qquad
o(x\mid do(m\leftarrow m')).
$$

即保持其他条件尽量不变，只替换候选中介状态，观察输出是否按预测改变。

## 逐步理解

### 1. 激活相关只能生成假设

看到某神经元在一类文本上高激活，最多说明它与这组数据相关。它也可能响应标点、语言、长度、数据来源或共现格式。

### 2. Probe 证明“信息可读”，不是“模型在用”

一个高容量 probe 可能自行计算标签；即使线性 probe 准确，原模型输出头也可能完全不读取那一维。

```text
可解码信息存在
≠ 自然运行中被使用
≠ 对行为必要
≠ 对行为充分
```

### 3. Ablation 检验必要性，但有副作用

把头、神经元或特征置零后行为下降，说明它在该干预下有因果作用。但还要问：消融是否制造分布外状态、是否破坏通用计算、是否有冗余路径，以及结果是否跨模板稳定。

### 4. Steering 检验可操纵性

沿方向 $v$ 加入 $\alpha v$ 后行为变化，说明该方向能影响系统。它不自动证明自然运行时模型用同一方向表达同一变量。必要对照包括等范数随机方向、错误层、错误位置、不同剂量和方向反转。

### 5. Activation patching 检验候选中介

典型设计：

```text
clean 输入 → 保存中间状态 m_clean
corrupted 输入 → 得到错误输出
corrupted 运行中把 m 替换为 m_clean
→ 观察目标输出是否恢复
```

恢复说明该状态对传递 clean 信息具有充分性证据。它不证明这个状态是唯一机制，也不证明 patch 后状态完全自然。

### 6. 替代模型可能行为忠实、机制不忠实

SAE、transcoder 或其他 replacement model 即使重建误差低、输出近似好，也可能通过不同路径实现同一函数。解释替代模型时必须验证它对反事实干预的响应是否与原模型一致。

## 证据阶梯

| 层级 | 例子 | 合理结论 |
|---|---|---|
| L0 | 数学恒等式 | 在定义条件内精确成立 |
| L1 | 完全透明玩具反例 | 证明一种机制可能或一种推理无效 |
| L2 | 开放模型观察 | 指定模型与输入上存在相关结构 |
| L3 | 开放模型内部干预 | 局部状态传递因果效应 |
| L4 | 跨模板、任务、模型复现 | 稳定机制家族证据 |
| L5 | 新反事实预测被独立复现 | 接近成熟机制理论 |

## 动手验证

```bash
llm-theory-lab explain C07
llm-theory-lab explain C08
llm-theory-lab run-toy --ids C07 C08
python examples/04_probe_vs_causality.py
```

C07 构造一个“probe 准确率接近 1、但消融后输出变化为 0”的变量；C08 比较 patch 候选中介与 patch 无关维度的恢复差异。

## 常见误区

**“Probe 很准，所以模型依赖这个概念。”** 缺少干预证据。

**“消融没效果，所以模块没用。”** 可能有冗余或干预方式不合适。

**“Steering 成功，所以找到了真实特征。”** 只证明可操纵性。

**“Attribution graph 很完整，所以就是源代码。”** 图依赖替代模型、剪枝、误差节点和 prompt 条件。

## 自测

1. 给出“相关但不因果”和“因果但不必要”的各一个例子。
2. Patching 恢复答案后，为什么还不能宣称找到唯一中介？
3. 怎样用随机方向对照检验 steering？
4. 机制忠实与输出忠实有什么不同？

## 来源

- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html)
- [Natural Language Autoencoders](https://transformer-circuits.pub/2026/nla/index.html)
