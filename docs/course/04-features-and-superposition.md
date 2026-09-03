# 第 4 章｜特征、Superposition 与可解释基底

## 学完你应该能

- 区分神经元、特征、方向、子空间和流形；
- 解释为什么特征数可以超过表示维度；
- 说明 superposition 的容量收益和干扰成本；
- 推导线性子图中的可逆基底变换；
- 正确理解 SAE、transcoder 和 crosscoder 的价值与限制。

## 核心模型

假设模型需要表示 $F$ 个稀疏特征，但 residual stream 只有 $d$ 个维度，且 $F>d$：

$$
h=Dx,
$$

其中 $x\in\mathbb R^F$ 是稀疏特征激活，$D\in\mathbb R^{d\times F}$ 是特征方向。因为 $F>d$，方向不可能全部正交。

如果特征很少同时出现，模型可以接受少量干扰，换取更多表示容量。这是 superposition 的核心直觉。

## 逐步理解

### 1. 神经元只是坐标，不自动等于概念

单个神经元是当前基底中的一个轴。一个语义变量可能分散在多个轴上；一个轴也可能参与多个无关模式。给最高激活样本贴标签，只得到一个候选解释。

### 2. Composition 与 superposition 不同

- **Composition**：多个有意义成分组合成复杂概念；
- **Superposition**：多个原本独立的稀疏特征因容量有限共享维度。

“法国科学家”可以由国家与职业成分组合；这些成分本身又可能与其他稀疏特征发生 superposition。

### 3. 干扰取决于共激活

方向不正交不必然造成严重错误。如果它们很少同时激活，干扰很少暴露。分布变化让原本分离的特征异常共激活时，问题才会明显。

### 4. 基底不唯一的精确例子

对行向量表示 $h$、可逆矩阵 $R$ 和线性下游映射 $W$：

$$
h'=hR,
\qquad
W'=R^{-1}W.
$$

于是：

$$
h'W'=hRR^{-1}W=hW.
$$

内部坐标可以明显改变，输入—输出函数却完全相同。因此“某个神经元就是某个概念”不是仅由函数自动确定的结论。

但这不等于所有基底同样好。非线性、LayerNorm、稀疏性、优化器和架构可能让某些坐标更特殊，这就是 privileged basis 问题。

### 5. SAE 在做什么

稀疏自编码器尝试找到过完备字典：

$$
h\approx b+\sum_k f_k(h)d_k,
$$

并让大多数 $f_k(h)=0$。它常得到比神经元更可读的方向，但必须保留以下限制：

- 字典不唯一；
- 宽度和稀疏惩罚会导致 splitting 或 merging；
- 重建残差可能仍携带重要计算；
- 最高激活样本容易高精度、低召回；
- 可解释方向不一定是模型自然使用的因果变量。

### 6. 从表示走向计算

- **SAE** 主要重建某层激活；
- **Transcoder** 近似模块输入到输出的变换；
- **Cross-layer transcoder** 尝试跨层追踪特征计算；
- **Crosscoder** 在多层或多模型间建立共同坐标；
- **流形视角** 用连续低维几何描述一族局部特征。

这些方法是研究接口，不是发现了模型内部唯一合法的“源代码语言”。

## 动手验证

```bash
llm-theory-lab explain C06
llm-theory-lab explain C10
llm-theory-lab run-toy --ids C06 C10
python examples/06_basis_invariance.py
```

C06 比较单特征与共激活干扰；C10 同时改变表示基底与下游映射，验证输出在数值精度内保持不变，并用“只改表示”的正对照确认补偿是必要的。

## 常见误区

**“一个 SAE 特征就是概念神经元。”** SAE 是重参数化接口，结果依赖训练目标和字典大小。

**“方向非正交就是模型坏了。”** 对稀疏特征而言，非正交可能是高效容量分配。

**“存在基底等价，所以神经元永远没意义。”** 实际网络的非线性和训练过程可能形成 privileged basis。

**“找到可解释基底后模型就变成小型稀疏程序。”** 特征间虚拟连接仍可叠加，真实计算也可能需要大量路径。

## 结论边界

C06 与 C10 都是 L0/L1 透明结果。它们证明结构可能与逻辑限制，不证明真实模型的具体特征字典、几何形状或自然基底。

## 自测

1. 为什么 $F>d$ 时特征方向不可能全部正交？
2. 两个高度相似但从不共现的特征，是否一定造成大行为误差？
3. 推导 $h'=hR, W'=R^{-1}W$ 的函数不变性。
4. 为什么这个推导不能直接跨过 ReLU？
5. 怎样检验某个 SAE 特征在自然运行中真的控制输出？

## 来源

- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)
- [Privileged Bases in the Transformer Residual Stream](https://transformer-circuits.pub/2023/privileged-basis/index.html)
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
- [Sparse Crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html)
- [When Models Manipulate Manifolds](https://transformer-circuits.pub/2025/linebreaks/index.html)
