# 第 2 章｜权重、激活、logits 与 token 赔率

## 学完你应该能

- 用 $w\times a$ 解释一条连接在当前输入下的直接贡献；
- 区分权重大小、当前贡献、分布有效性和因果帮助性；
- 推导两个 token 的相对赔率；
- 解释为什么小的隐藏状态变化可能翻转首 token，却不必夸大为“模型被一个神经元控制”。

## 核心模型

最简单的线性层是：

$$
y=Wx+b.
$$

连接 $w_{ij}$ 对输出 $y_i$ 的当前直接贡献为：

$$
c_{ij}(x)=w_{ij}x_j.
$$

最终状态经 unembedding 得到 logits：

$$
z=W_Uh.
$$

温度为 $T>0$ 时：

$$
p_i=\frac{e^{z_i/T}}{\sum_j e^{z_j/T}}.
$$

两个 token 的相对赔率满足：

$$
\log\frac{p_i}{p_j}=\frac{z_i-z_j}{T}.
$$

## 逐步理解

### 1. 大权重不等于大当前作用

设两个连接权重分别为 $100$ 和 $2$，源激活分别为 $0$ 和 $3$：

$$
100\times0=0,
\qquad
2\times3=6.
$$

只按绝对权重排序，会把当前真正工作的连接排错。

### 2. 当前贡献不等于最终因果重要性

即使某条路径直接贡献很大，它也可能：

- 被 ReLU 或其他门控截断；
- 被 LayerNorm 改变尺度；
- 被后续路径抵消；
- 只在极少输入中激活；
- 被冗余路径替代；
- 对当前 logit 有贡献，却提高整体损失。

因此研究时至少要区分：

| 层次 | 问题 |
|---|---|
| magnitude | 固定连接有多大？ |
| contribution | 这个输入下贡献多少？ |
| effectiveness | 在数据分布上多久、以多大幅度生效？ |
| helpfulness | 干预后损失或目标行为变好还是变坏？ |

### 3. Logit 差而不是单个 logit 决定赔率

设 token A 与 B 的 logit 差为 $1$。当 $T=1$：

$$
\frac{p_A}{p_B}=e^1\approx2.718.
$$

若 A 相对 B 再增加 $\Delta z$，赔率乘数为：

$$
e^{\Delta z/T}.
$$

低温放大相同 logit 差，高温压缩它。但赔率翻倍不代表 A 一定被采样，因为词表里还有其他 token，解码还可能使用 top-p、top-k 或 greedy。

### 4. 隐藏方向怎样影响 token

若隐藏状态发生变化 $\Delta h$，token $i$ 的 logit 变化是：

$$
\Delta z_i=u_i^\top\Delta h,
$$

其中 $u_i$ 是 unembedding 中对应 token 的方向。真正影响 A/B 竞争的是：

$$
\Delta(z_A-z_B)=(u_A-u_B)^\top\Delta h.
$$

所以“隐藏状态变化很小”不是完整判断；关键是变化是否对准了竞争 token 的差分方向。

## 动手验证

```bash
llm-theory-lab explain C01
llm-theory-lab explain C02
llm-theory-lab run-toy --ids C01 C02
python examples/01_softmax_temperature.py
python examples/02_weight_vs_activation.py
```

C01 会比较“大而罕见”的连接与“小而常见”的连接；C02 会直接验证赔率恒等式和 $e$ 倍关系。

## 常见误区

**“最大的参数就是最重要参数。”** 忽略了源激活、数据分布和下游抵消。

**“概率就是模型对事实的信念。”** token 概率同时受到事实、语法、角色、格式、任务和当前前缀影响。

**“低温度消除了偏置。”** 低温只改变解码分布的尖锐程度，不会删除训练先验或上下文路由。

**“某方向能 steering，所以自然运行一定使用它。”** 可操纵性不等于自然因果必要性；需要随机方向、错误层和 patching 对照。

## 自测

1. 权重为 10、平均源激活为 0.01，与权重为 1、平均源激活为 1，谁更重要？还缺什么信息？
2. 当 $T=0.5$、$\Delta z=1$ 时，赔率乘数是多少？
3. 为什么 direct logit attribution 仍不等于最终机制证明？
4. 哪种实验能区分“贡献很大”和“移除后不可替代”？

## 来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [A Toy Model of Interference Weights](https://transformer-circuits.pub/2025/interference-weights/index.html)
- [Characterizing interference weights in a tiny language model](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
