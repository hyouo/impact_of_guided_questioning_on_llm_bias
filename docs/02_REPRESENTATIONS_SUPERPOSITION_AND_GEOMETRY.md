# 02｜表征、叠加、可解释基底与几何

## 2.1 什么是“特征”

在机制可解释性中，feature 通常指一个可重复出现、对计算有意义的潜在变量。它可能表示：

- 输入属性：语言、实体、危险主题、位置或文体；
- 中间结果：答案候选、字符计数、语义关系；
- 控制状态：当前 persona、任务类型、拒绝倾向；
- 输出动作：某类词、格式或多 token 行为的倾向。

“特征”不必等于一个神经元。一个特征可能分布在多维上，一个神经元也可能参与多个特征。

## 2.2 Superposition

若模型需要表示的稀疏特征数 $F$ 大于可用维度 $d$，它可以让多个特征共享同一低维空间：

$$
h=Dx,
$$

其中 $x\in\mathbb R^F$ 是稀疏特征活动，$D\in\mathbb R^{d\times F}$ 是特征方向集合，且 $F>d$。这种过完备表示带来容量优势，也带来干扰：不同特征方向不再完全正交。

Toy Models of Superposition 在具有已知生成过程的简单网络中展示了：

- 单义和多义神经元都可以自然形成；
- 是否进入叠加可表现为相变；
- 特征会形成多边形、多面体等几何结构；
- 某些计算可以在叠加中进行；
- 玩具模型结果不能无条件外推到真实大模型。

## 2.3 Composition 与 superposition

“分布式表示”至少包含两种不同现象：

- **composition**：多个方向分别表示组成部分，组合后构成复杂概念；
- **superposition**：多个本应独立的特征因容量限制共享维度并相互干扰。

它们可同时存在。把所有分布式表示都称为 superposition，会失去对“有意义组合”和“容量压缩干扰”的区分。

## 2.4 可解释基底不是自动给定的

Residual stream 在理想化数学上常可做基底旋转而不改变函数，因此单个坐标未必有特殊语义。但实际训练可能产生 privileged basis，例如优化器的逐维归一化使部分坐标获得统计特殊性。

这带来两个结论：

1. 不能假设神经元坐标天然就是正确变量；
2. 也不能简单宣称残差流完全没有特殊坐标。

机制解释应由预测和干预来评判，而不是只由坐标的直观性评判。

## 2.5 Sparse Autoencoder

SAE 试图近似：

$$
x\approx b+\sum_i f_i(x)d_i,
$$

其中大多数 $f_i(x)=0$，$d_i$ 是 decoder 方向。典型目标包含重建误差和稀疏惩罚：

$$
\mathcal L=\|x-\hat x\|_2^2+\lambda\|f(x)\|_1.
$$

SAE 的价值：

- 从多义神经元中提取更可解释的方向；
- 给 attribution、steering 和 feature visualization 提供单位；
- 在大规模模型中发现抽象、安全相关和跨语言特征。

SAE 的限制：

- reconstruction error 会形成未解释的“暗物质”；
- dictionary size 与正则化会造成 feature splitting 或合并；
- 特征标签可能只覆盖其激活分布的一部分；
- 不同随机种子和架构可得到不同分解；
- 高可解释性不等于全部模型计算都被覆盖。

## 2.6 Transcoder 与 crosscoder

### Transcoder

用稀疏特征近似某个模块从输入激活到输出激活的变换。它比只重建同层激活的 SAE 更贴近“计算发生了什么”，因此适合构建 feature-to-feature attribution graph。

### Crosscoder

同时读取或重建多个层，甚至多个模型。它可用于：

- 找跨层持续存在的特征；
- 减少每层重复特征导致的复杂度；
- 比较预训练与微调模型；
- 追踪特征如何因数据或模型变化而旋转。

但 crosscoder 的因果描述仍是分析层的重参数化，未必等同于底层网络实际执行顺序。

## 2.7 离散特征与连续流形

2025 年的 line-breaking 研究发现，字符计数等标量并非简单存成单一数值，也不必为每个整数分配完全正交方向。模型可以把标量编码在低内在维、带曲率的流形上：

- 一组离散 SAE/crosscoder 特征像局部坐标，分段覆盖流形；
- 全局几何视角把这些特征看成连续曲线；
- attention 的 QK 变换可旋转、对齐或“扭转”两个计数流形；
- 多个头共同构造足够复杂的几何。

这说明 feature view 与 geometry view 可能是同一对象的两种尺度。只保留离散特征会支付“复杂度税”；只看低维几何又可能漏掉无法简单参数化的语义结构。

## 2.8 权重叠加与干扰权重

即使找到了理想特征基底，特征仍通过低维 residual stream 读写。特征间的虚拟权重可写成矩阵乘积，例如：

$$
W_{virtual}=D_{target}^{\top}WD_{source}.
$$

由于低维压缩，这些虚拟连接也会发生叠加，产生看起来很大却在数据分布上不工作的连接，即 interference weights。

应区分：

- **raw magnitude**：虚拟权重本身多大；
- **coactivation**：源和目标是否在同一数据上共同相关；
- **effectiveness**：连接实际改变输出的程度；
- **helpfulness**：这种改变是降低还是提高损失。

2026 年的一层 transformer 研究报告：按有效性排序，去掉最低的 70% 虚拟权重只带来约 0.01 nats 的损失增加；但剩下的有帮助权重数量仍很大。这既显示大量无效连接的存在，也显示“找到正确基底后模型立刻变成稀疏程序”仍未实现。

## 2.9 自然语言作为激活接口

Natural Language Autoencoder 使用两部分：

- activation verbalizer：激活 → 文字描述；
- activation reconstructor：文字描述 → 重建激活。

它以重建为训练目标，不依赖人工概念标签，并能产生可读解释和编辑方向。但 verbalizer 本身是高容量模型，可能进行额外推断、重复上下文、混入幻觉或形成不透明编码；因此 NLA 输出应被当作**假设生成接口**，再用独立方法验证。

## 2.10 当前理论立场

最稳妥的说法不是“模型由一组确定的语义特征组成”，而是：

> 多类证据支持模型激活中存在具有可重复语义和因果作用的方向、子空间及流形；不同工具对这些结构给出不同近似分解，研究目标是寻找在重建、简洁、稳定和因果预测之间更好的坐标系。

## 2.11 核心来源

- [Distributed Representations: Composition & Superposition](https://transformer-circuits.pub/2023/superposition-composition/index.html)
- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)
- [Privileged Bases in the Transformer Residual Stream](https://transformer-circuits.pub/2023/privileged-basis/index.html)
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
- [Sparse Crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html)
- [When Models Manipulate Manifolds](https://transformer-circuits.pub/2025/linebreaks/index.html)
- [Natural Language Autoencoders](https://transformer-circuits.pub/2026/nla/index.html)
- [Characterizing Interference Weights](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
