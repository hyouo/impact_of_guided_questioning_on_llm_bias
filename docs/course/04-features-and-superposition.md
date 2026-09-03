# 第 4 章｜特征、Superposition 与可解释基底

## 学完你应该能

- 区分神经元、特征、方向、子空间和流形；
- 解释为什么特征数可以超过表示维度；
- 说明 superposition 带来的容量收益和干扰成本；
- 正确理解 SAE、transcoder 和 crosscoder 的价值与限制。

## 核心模型

假设模型需要表示 $F$ 个稀疏特征，但 residual stream 只有 $d$ 个维度，且 $F>d$。可以写成：

$$
h=Dx,
$$

其中 $x\in\mathbb R^F$ 是稀疏特征激活，$D\in\mathbb R^{d\times F}$ 是特征方向。因为 $F>d$，这些方向不可能全部正交。

如果特征很少同时出现，模型可以接受少量干扰，换取更多表示容量。这就是 superposition 的核心直觉。

## 逐步理解

### 1. 神经元只是坐标，不一定是概念

单个神经元是当前基底中的一个轴。一个语义变量可能分散在多个轴上；一个轴也可能同时参与多个不相关模式。把最高激活样本贴上标签，只能得到一个假设。

### 2. Composition 与 superposition 不同

- **Composition**：多个有意义成分组合成复杂概念；
- **Superposition**：多个原本独立的稀疏特征因容量有限共享维度。

“法国科学家”可由国家与职业成分组合；这些成分各自又可能与其他稀疏特征发生 superposition。

### 3. 干扰取决于共激活

两个方向不正交并不必然造成严重错误。如果它们几乎从不同时激活，干扰很少暴露。真正危险的是罕见分布变化让原本分离的特征异常共激活。

这给 prompt 敏感性提供了一个重要视角：异常格式或组合可能把训练中很少共同出现的特征带到同一状态区域。

### 4. SAE 在做什么

稀疏自编码器尝试找到过完备字典：

$$
h\approx b+\sum_k f_k(h)d_k,
$$

并让大多数 $f_k(h)=0$。它常能得到比神经元更可读的方向，但必须记住：

- 字典不是唯一的；
- 宽度和稀疏惩罚会导致 feature splitting 或 merging；
- 重建残差可能仍携带重要计算；
- 最高激活样本容易高精度、低召回；
- 可解释方向不一定是模型自然使用的因果变量。

### 5. 从表示走向计算

- **SAE** 主要重建某层激活；
- **Transcoder** 近似模块输入到输出的变换；
- **Cross-layer transcoder** 尝试跨层追踪特征计算；
- **Crosscoder** 在多层或多模型间建立共同坐标；
- **流形视角** 用连续低维几何描述一族局部特征。

这些方法是研究接口，不是发现了模型内部唯一合法的“源代码语言”。

## 动手验证

```bash
llm-theory-lab explain C06
llm-theory-lab run-toy --ids C06
```

C06 把五个特征方向放进二维空间，比较单特征激活和共激活时的重建干扰。运行后回答：

- 为什么单个特征仍可能被辨认？
- 为什么共激活误差更大？
- 这个二维人工几何与真实 SAE 有哪些根本差异？

## 常见误区

**“一个 SAE 特征就是模型中的一个概念神经元。”** SAE 是重参数化接口，结果依赖训练目标和字典大小。

**“方向非正交就是模型坏了。”** 对稀疏特征而言，非正交可能是高效容量分配。

**“找到可解释基底后模型就会变成很小的稀疏程序。”** 特征间虚拟连接仍可发生叠加与干扰，真实计算也可能需要大量路径。

**“连续流形与离散特征互相排斥。”** 离散特征可以是连续流形的局部坐标，两种视角可能同时正确。

## 自测

1. 为什么 $F>d$ 时特征方向必然存在非零内积？
2. 两个高度相似但从不共现的特征，是否一定造成大行为误差？
3. SAE reconstruction error 小，是否足以证明机制忠实？
4. 你会怎样检验某个 SAE 特征在自然运行中真的控制输出？

## 来源

- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)
- [Distributed Representations: Composition & Superposition](https://transformer-circuits.pub/2023/superposition-composition/index.html)
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
- [Sparse Crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html)
- [When Models Manipulate Manifolds](https://transformer-circuits.pub/2025/linebreaks/index.html)
