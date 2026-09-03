# 第 1 章｜把语言模型看成条件动力系统

## 学完你应该能

- 区分训练、单次前向传播和连续生成三个时间尺度；
- 准确说明 input、参数、激活、logits 和输出 token 的因果顺序；
- 解释为什么模型既不是静态数据库，也不是每次都在修改权重；
- 读懂后续章节使用的统一记号。

## 核心模型

给定已有 token 序列 $x_{1:t}$，自回归语言模型计算：

$$
p_\theta(x_{t+1}\mid x_{1:t}).
$$

这里的 $\theta$ 是训练得到的参数。模型不是一次性生成完整答案，而是反复执行：

```text
上下文 → 下一 token 分布 → 选 token → 写回上下文 → 重复
```

把一次运行写成状态更新：

$$
h_t=f_\theta(x_{1:t}),
\qquad
z_t=W_Uh_t,
\qquad
x_{t+1}\sim\operatorname{softmax}(z_t/T).
$$

$h_t$ 是当前动态状态，$z_t$ 是词表 logits，$T>0$ 是数学 softmax 的温度。

## 逐步理解

### 1. 训练时间尺度：数据改变参数

预训练目标可简化为：

$$
\mathcal L(\theta)
=
\mathbb E_{s\sim D}
\left[-\sum_t\log p_\theta(s_t\mid s_{<t})\right].
$$

数据分布 $D$ 决定哪些模式频繁进入梯度，优化器长期更新 $\theta$。语言比例、事实频率、文体、安全样本和损失权重都能形成参数先验。

### 2. 单次前向传播：输入改变激活

模型收到一个确定 prompt 后，参数通常固定。变化的是：

- token 与位置表示；
- residual stream；
- MLP 与潜在特征激活；
- query、key、value；
- Attention 路由；
- 最终 logits。

正确方向是：

```text
input → activations / routing → logits → probabilities
```

不是“概率分布先激活参数”。

### 3. 连续生成：输出又成为输入

第一个输出 token 被追加到上下文，因此：

$$
p_{t+1}
=
p_\theta(\cdot\mid x_{1:t},x_{t+1}).
$$

这使模型成为一个有路径依赖的动力系统。两个首 token 即使差异很小，也可能把后续计算带到不同区域。

## 一个具体例子

假设系统当前有两个内部状态维度：“回答倾向”和“拒绝倾向”。固定权重把它们映射到 `ANSWER` 与 `REFUSE` 两个 token。prompt A 让回答维度更高，prompt B 让拒绝维度更高。权重完全没变，但 top token 可以翻转。

若第一步强制输出 `ANSWER`，这个 token 又会强化“继续回答”的上下文；若强制输出 `REFUSE`，后续更容易延续拒绝句式。模型行为的巨大差异不要求参数变化。

## 动手验证

```bash
llm-theory-lab explain C03
llm-theory-lab run-toy --ids C03 C05
```

重点观察：

- C03 中固定矩阵是否对不同输入产生不同特征与 top token；
- C05 中只改变第一个 token 后，最终状态距离是否持续增大。

不要只看 `pass`。打开 `reports/toy/report.md`，逐项解释观测量为什么支持命题。

## 常见误区

**“模型把答案存在参数里，所以 input 只是检索键。”** 参数同时编码表示、路由、变换和生成先验；许多结果来自上下文条件计算，不是精确数据库查找。

**“prompt 改变模型，说明 prompt 修改了权重。”** 标准推理通常只改变激活。只有微调、在线学习、显式参数更新或某些外部记忆机制才会改变持久参数。

**“一次 forward pass 就等于完整回答。”** 一次 forward pass 通常只产生下一 token 分布。完整回答是多次前向传播构成的轨迹。

## 自测

1. 为什么训练 token 分布能影响参数，而单次 prompt 通常不能？
2. 如果 temperature 改变，当前隐藏状态是否一定改变？下一步隐藏状态呢？
3. “模型内部已经知道答案”这句话至少混淆了哪些不同对象？
4. 给出一个不修改权重、却能让后续轨迹分叉的干预。

## 来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
