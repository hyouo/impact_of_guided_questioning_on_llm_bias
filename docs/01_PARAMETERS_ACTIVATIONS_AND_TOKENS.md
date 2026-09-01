# 01｜参数、激活、token 与概率分布

## 1.1 首要纠正：参数一般不会“被激活”

一次标准推理中，模型参数 \(\theta\) 通常保持不变。输入改变的是：

- token embedding 与位置表示；
- residual stream 中的向量；
- MLP 神经元或稀疏特征的激活；
- attention 的 query、key、value 和模式；
- 中间几何状态；
- logits 与下一个 token 的条件分布。

在混合专家模型中，可以说“某些专家被路由选中”，但这仍不是权重数值被打开或修改。

最简单的线性层为：

\[
y=Wx+b.
\]

第 \(j\) 个输入维度通过第 \(i,j\) 个连接对输出 \(i\) 的直接贡献为：

\[
c_{ij}=w_{ij}x_j.
\]

因此：

- 大权重若源激活接近零，当前几乎不起作用；
- 中等权重若源激活很强，当前贡献可能很大；
- 大直接贡献也可能在后续被门控、归一化或抵消；
- 只有干预后观察行为或损失变化，才接近因果重要性。

## 1.2 三个时间尺度

### 训练时间尺度

\[
\mathcal L(\theta)
=\mathbb E_{s\sim D_{train}}
\left[-\sum_t\log p_\theta(s_t\mid s_{<t})\right].
\]

训练 token 分布通过梯度累计改变参数。数据频率、共现结构、语言比例、任务混合、安全后训练样本和损失权重都会形成长期先验。

这时“token 分布影响参数”是正确说法。

### 单次前向传播时间尺度

给定 token 序列：

\[
h_i^{(0)}=E(x_i)+P_i,
\]

每层近似执行：

\[
h^{(\ell+1)}=h^{(\ell)}+
\operatorname{Attn}_\ell(h^{(\ell)})+
\operatorname{MLP}_\ell(h^{(\ell)}).
\]

输入与固定权重共同决定当前激活。这里的因果顺序是：

```text
input → activations / attention → logits → token distribution
```

不是“token 概率分布先激活参数”。

### 自回归时间尺度

\[
y_t\sim p_\theta(\cdot\mid x,y_{<t}),
\qquad
p_{t+1}=p_\theta(\cdot\mid x,y_{<t},y_t).
\]

当前分布选出的 token 被写回上下文，才成为下一步激活的原因。于是完整闭环是：

```text
输入 → 激活 → 分布 → 选中 token → 新输入 → 新激活
```

## 1.3 Tokenization 为什么重要

模型接收的不是字符或“语义本身”，而是 tokenizer 产生的离散序列。下列变化可能改变 token 边界、长度和 embedding 组合：

- 空格和换行；
- 标点、大小写和 Unicode；
- 拼写拆分或编码；
- 角色标签和消息模板；
- 代码块、引号和 XML/JSON 结构；
- 多语言混合。

因此一个 prompt 实验若不记录 tokenizer 输出，就不能确定观察到的是语义干预、表面形式、位置效应还是三者混合。

## 1.4 Logits、softmax 与赔率

最终状态通过 unembedding 得到 logits：

\[
z=W_Uh^{(L)}.
\]

温度为 \(T\) 时：

\[
p_i=\frac{e^{z_i/T}}{\sum_j e^{z_j/T}}.
\]

两个 token 的赔率只取决于相对 logit：

\[
\log\frac{p_i}{p_j}=\frac{z_i-z_j}{T}.
\]

当 \(T=1\) 时，相对 logit 增加 1 会把赔率乘以 \(e\approx2.718\)。所以隐藏状态中的小方向变化，可能翻转首 token；首 token 再通过反馈产生大规模轨迹差异。

## 1.5 四类“token 分布偏置”

### 训练分布偏置

数据中高频模式被更频繁地优化，形成长期参数先验。它可表现为事实频率、文化刻板关联、文体偏好、默认角色和常见任务启发式。

### 上下文条件偏置

prompt 中的例子、顺序、角色、用户立场和格式改变当前条件分布，但不修改参数。这是 in-context learning、few-shot learning、persona 和许多 jailbreak/prompt injection 现象的共同入口。

### 解码偏置

temperature、top-p、top-k、beam search、logit bias 和 seed 决定如何从已经计算出的 logits 选 token。当前步隐藏状态通常已固定，但所选 token 会改变以后所有步骤。

### 轨迹偏置

生成的开头会构造新的局部先验。比如回答式、拒绝式、代码式或列表式前缀会使后续语法、自洽性和任务完成路径变得更自然。

## 1.6 “权重影响”应怎样测量

建议使用四层问题：

| 层次 | 问题 | 典型测量 |
|---|---|---|
| 结构 | 连接有多大？ | 参数/虚拟权重数值 |
| 当前贡献 | 当前输入下贡献多少？ | 激活 × 有效权重、logit attribution |
| 分布有效性 | 在真实数据上经常影响输出吗？ | 平均平方效应、Fisher 类指标、共激活 |
| 因果帮助性 | 移除它会让损失或行为怎样变化？ | ablation、loss delta、patching |

2026 年的 tiny-transformer 研究把虚拟权重的 **effectiveness** 与 **helpfulness** 分开，并发现有益、无益和有害权重可以跨越整个权重大小范围。这支持“不能按绝对值直接读取程序”的结论，但该实验来自一层小模型，不能直接外推成前沿模型定律。

## 1.7 常见错误

- “这个 token 激活了某个权重。”  
  更准确：这个 token 改变表示，使经过该权重的源激活和实际贡献发生变化。

- “概率高说明模型相信它是真的。”  
  概率是当前上下文下的预测偏好，混合了事实、风格、任务、角色和语法等多种因素。

- “低温度消除了偏置。”  
  低温度只减少采样随机性，不能删除参数先验或上下文诱导。

- “第一个 token 不重要。”  
  在自回归模型中，第一个 token 是下一步的强输入，常常决定响应模式。

## 1.8 核心来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [Characterizing interference weights in a tiny language model](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
- [Circuits Updates — April 2025](https://transformer-circuits.pub/2025/april-update/index.html)
