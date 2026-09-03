# 第 6 章｜从相关、可解码到因果机制

## 学完你应该能

- 区分相关、可解码、必要、充分、可操纵和机制忠实；
- 解释 probe、ablation、steering 与 activation patching 各自能证明什么；
- 识别冗余路径和指标饱和造成的消融假阴性；
- 为机制主张设计正对照、负对照和反证条件；
- 识别“输出忠实但机制不忠实”的替代模型。

## 核心模型

机制主张不只是：

> 激活 $h$ 与标签 $y$ 相关。

更强的主张是：内部变量 $m$ 在输入 $x$ 到输出 $o$ 的因果链中承担特定作用。我们比较：

$$
o(x),
\qquad
o(x\mid do(m\leftarrow m')).
$$

即尽量保持其他条件不变，只替换候选中介，观察输出是否按预测改变。

## 逐步理解

### 1. 激活相关只能生成假设

某神经元在一类文本上高激活，最多说明它与这组数据相关。它也可能响应标点、语言、长度、数据来源或共现格式。

### 2. Probe 证明“信息可读”，不是“模型在用”

高容量 probe 可能自行计算标签；即使线性 probe 准确，原模型输出头也可能完全不读取那一维。

```text
可解码信息存在
≠ 自然运行中被使用
≠ 对行为必要
≠ 对行为充分
```

### 3. Ablation 检验必要性，但零结果不简单

消融后行为下降，说明对象在该干预下有因果作用。零效应却可能来自：

- 路径确实未使用；
- 存在冗余或备份路径；
- 指标已经饱和，连续 margin 变化未反映到 accuracy；
- 干预位置或粒度错误；
- 消融制造分布外状态；
- 其他模块发生补偿。

因此需要连续指标、联合消融、条件化样本和合理正对照。

### 4. Steering 检验可操纵性

沿方向 $v$ 加入 $\alpha v$ 后行为变化，说明该方向能影响系统。更可信的特异性证据需要：

- 剂量响应；
- 方向反转产生反号效应；
- 等范数随机方向；
- 正交方向；
- 错误层与错误位置；
- 目标行为之外的副作用测量。

即使全部通过，也主要增强可操纵性证据，不自动证明该方向自然、唯一或必要。

### 5. Activation patching 检验候选中介

```text
clean 输入 → 保存 m_clean
corrupted 输入 → 错误输出
corrupted 运行中令 m ← m_clean
→ 观察目标输出是否恢复
```

恢复说明状态对传递 clean 信息具有因果充分性证据。它不证明状态是唯一机制，也不保证 patch 后状态完全自然。

### 6. 替代模型可能行为忠实、机制不忠实

SAE、transcoder 或其他 replacement model 即使重建误差低、输出近似好，也可能通过不同路径实现同一函数。需要比较原模型与替代模型对相同反事实干预的响应。

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
llm-theory-lab run-toy --ids C07 C08 C11 C12
python examples/04_probe_vs_causality.py
python examples/07_redundant_paths.py
python examples/08_steering_controls.py
```

- C07：probe 很准但未使用变量的消融效应为零；
- C08：候选中介 patch 与无关维度 patch 的恢复差异；
- C11：单路径消融不改变 accuracy，却改变 margin，联合消融才暴露冗余；
- C12：目标 steering 方向必须超过随机/正交控制，并呈剂量和符号响应。

## 常见误区

**“Probe 很准，所以模型依赖这个概念。”** 缺少干预证据。

**“消融没效果，所以模块没用。”** 可能有冗余、指标饱和或错误干预。

**“Steering 成功，所以找到了真实特征。”** 主要证明可操纵性，必须与控制方向比较。

**“Patching 恢复，所以找到了唯一中介。”** 恢复接近充分性，不自动证明必要或唯一。

**“Attribution graph 很完整，所以就是源代码。”** 图依赖替代模型、剪枝、误差节点和 prompt 条件。

## 自测

1. 给出“相关但不因果”和“因果但不必要”的各一个例子。
2. 为什么 accuracy 不变时仍要检查 logit margin？
3. Patching 恢复答案后，为什么不能宣称找到唯一中介？
4. 怎样用随机方向、反向和剂量对照检验 steering？
5. 机制忠实与输出忠实有什么不同？

## 来源

- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html)
- [Natural Language Autoencoders](https://transformer-circuits.pub/2026/nla/index.html)
