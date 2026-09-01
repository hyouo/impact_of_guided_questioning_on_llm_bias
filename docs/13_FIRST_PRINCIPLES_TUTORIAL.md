# 13｜从第一性原理理解大模型：权重、输入、推理与生成

> 本章是整个仓库的“清晰版本”。先不假设读者懂 circuits、SAE 或 attribution graph，而是从一次语言模型调用到底发生什么开始。每个术语只承担一种含义；每个结论都注明它属于训练、单次前向传播还是连续生成。

# 13.1 最小定义：语言模型在做什么

给定已经出现的 token 序列 $x_{1:t}$，自回归语言模型计算下一个 token 的条件分布：

$$
p_\theta(x_{t+1}\mid x_{1:t}).
$$

这里：

- $x_{1:t}$ 是当前上下文中的离散 token；
- $\theta$ 是训练得到的全部参数；
- 输出不是一句完整答案，而是词表中每个候选 token 的分数和概率；
- 选出一个 token 后，它被追加到上下文，再重复同一过程。

因此，一段回答不是一次性“想完再打印”，而是：

```text
读入上下文
→ 计算下一 token 分布
→ 选择一个 token
→ 把它写回上下文
→ 再计算下一 token 分布
→ ……
```

这一步已经解释了为什么首 token、格式前缀和模型自己的早期输出会如此重要：它们立即变成后续计算的输入。

# 13.2 五种对象必须分开

| 对象 | 是什么 | 推理时是否变化 | 常见误解 |
|---|---|---:|---|
| 参数/权重 | 训练后保存在矩阵中的连接规则 | 通常不变 | “某个 token 激活了一个权重” |
| 激活 | 当前输入经过网络时产生的数值状态 | 每次输入都变 | “激活高就一定决定输出” |
| 特征 | 对一类可重复语义或计算变量的分析性描述 | 是否激活随输入变 | “特征必然等于一个神经元” |
| 回路 | 多个表示和模块之间形成的计算路径 | 实际参与路径随输入变 | “模型只有一条固定程序” |
| logits/概率 | 当前状态对候选 token 的输出偏好 | 每一步都变 | “概率就是模型的真诚信念” |

最重要的纠正是：

> **被输入改变的是激活和实际计算路径，不是标准推理中的参数数值。**

混合专家模型可以说“专家被路由选中”，但专家内部权重仍不是被 token 临时改写。

# 13.3 三个时间尺度

## 13.3.1 训练时间尺度

训练目标可简化为：

$$
\mathcal L(\theta)
=
\mathbb E_{s\sim D}
\left[-\sum_t \log p_\theta(s_t\mid s_{<t})\right].
$$

训练数据分布 $D$ 通过大量梯度更新塑造参数 $\theta$。因此下列因素会长期进入权重：

- 哪些语言、实体、事实和文体更常见；
- 哪些 token 经常共同出现；
- 数据怎样清洗和混合；
- 哪些任务获得更高损失权重；
- 后训练偏好、角色和安全样本如何构造；
- 哪些罕见组合从未被充分约束。

这时说“token 分布影响参数”是正确的，因为我们讨论的是训练数据的统计分布。

## 13.3.2 单次前向传播时间尺度

模型收到一个确定上下文后，参数通常固定。输入改变：

- token embedding；
- 位置和角色表示；
- residual stream；
- MLP 与潜在特征激活；
- query、key、value；
- attention 路由；
- 最终 logits。

因果顺序是：

```text
input tokens
→ activations / routing
→ logits
→ probability distribution
```

不是“概率分布先激活参数”。

## 13.3.3 自回归时间尺度

从概率分布选出的 token 被写回上下文：

$$
y_t\sim p_\theta(\cdot\mid x,y_{<t}),
$$

$$
p_{t+1}
=
p_\theta(\cdot\mid x,y_{<t},y_t).
$$

于是输出又成为输入，形成反馈闭环。这个时间尺度解释了轨迹依赖。

# 13.4 一次 forward pass 的逐步过程

## 13.4.1 Tokenization

模型不直接读取字符、词义或自然语言句子，而是读取 tokenizer 输出的 token IDs：

```text
字符串 → tokenizer → token IDs
```

空格、换行、Unicode、大小写、标点、代码块和角色标签可能改变：

- token 边界；
- token 数量；
- 每个位置的 embedding；
- 最后一个位置；
- attention 可读取的结构。

所以两个“人看起来意思一样”的字符串，可能不是同一个模型输入。

## 13.4.2 Embedding 与 residual stream

每个 token 被映射为向量，再加上位置或旋转位置信息。各层通过 residual stream 读取并写入状态：

$$
h^{(\ell+1)}
=
h^{(\ell)}
+
\Delta h^{(\ell)}_{\text{attn}}
+
\Delta h^{(\ell)}_{\text{MLP}}.
$$

Residual stream 可以理解为共享通信空间，但不要把它想成一列人类可读变量。多个特征、方向和子空间可能重叠存在。

## 13.4.3 Attention：决定从哪里读、读到后写什么

对一个 attention head：

$$
q_i=h_iW_Q,
\qquad
k_j=h_jW_K,
\qquad
v_j=h_jW_V.
$$

位置 $i$ 对位置 $j$ 的分数近似是：

$$
s_{ij}=\frac{q_i^\top k_j}{\sqrt{d_k}}.
$$

经过 mask 和 softmax：

$$
\alpha_{ij}=\operatorname{softmax}_j(s_{ij}).
$$

然后聚合 value：

$$
o_i=\sum_j \alpha_{ij}v_jW_O.
$$

因此 attention 必须拆成两个问题：

- **QK：为什么读这个位置？**
- **OV：读到后向 residual stream 写了什么？**

只看热力图只能看到当前读取权重，不能单独解释读取原因、写回内容或因果必要性。

## 13.4.4 MLP：条件特征变换

简化的 MLP 可写为：

$$
\operatorname{MLP}(h)
=
W_{out}\,\phi(W_{in}h+b_{in})+b_{out}.
$$

中间非线性使某些方向表现出门控或阈值效应：输入的小变化可能让一个潜在特征从接近零跃迁到明显激活，再通过下游连接影响其他状态。

这不是说真实概念都由单个 MLP 神经元承担。Superposition 意味着一个神经元可以参与多个特征，一个特征也可以分布在多个坐标。

## 13.4.5 Unembedding、logits 与概率

最终位置状态通过 unembedding 得到 logits：

$$
z=W_Uh^{(L)}.
$$

在正温度 $T>0$ 下：

$$
p_i
=
\frac{e^{z_i/T}}
     {\sum_j e^{z_j/T}}.
$$

两个 token 的对数赔率是：

$$
\log\frac{p_i}{p_j}
=
\frac{z_i-z_j}{T}.
$$

若 token $i$ 相对 token $j$ 的 logit 增加 $\Delta z$，赔率乘数是：

$$
\exp\left(\frac{\Delta z}{T}\right).
$$

当 $T=1$ 且 $\Delta z=1$，赔率乘以 $e\approx2.718$。较低正温度会放大相对 logit 差，较高温度会压平差异。

数学上不能把 $T=0$ 直接代入 softmax。API 中的 `temperature=0` 通常表示 greedy/argmax 约定。

# 13.5 权重到底怎样影响计算

最简单线性层：

$$
y=Wx+b.
$$

第 $j$ 个源激活通过连接 $w_{ij}$ 对第 $i$ 个目标分量的直接贡献为：

$$
c_{ij}=w_{ij}x_j.
$$

因此大权重不等于大当前作用：

- 若 $x_j=0$，直接贡献就是 0；
- 若源特征很少激活，它在真实数据分布上可能很少生效；
- 若下游路径不读取该目标，当前贡献不会到达输出；
- 若其他路径抵消，净效果可以很小；
- 若存在冗余，消融一条路径后行为可能保持不变。

应依次区分四层问题：

```text
Magnitude：连接数值多大？
Contribution：这个输入下直接贡献多大？
Effectiveness：在数据分布上经常真正生效吗？
Helpfulness / causal effect：它对损失或行为究竟有益、无益还是有害？
```

Transformer Circuits 的 interference weights 工作尤其提醒：即使转到较可解释的特征基底，仍可能出现数值很大但缺乏实际作用的虚拟连接。

# 13.6 Input 为什么影响很大

Input 同时承担多种功能：

```text
事实数据
任务说明
角色与权限线索
示例
格式
外部文档
工具返回
模型之前的输出
```

模型通过同一套 token 表示去推断“这段内容是什么、应该怎样处理”。因此 input 可以在多个层面改变计算。

## 13.6.1 改变底层表示

不同 tokenization 直接产生不同 embedding 和位置结构。

## 13.6.2 改变语义特征

词义、实体、关系、危险性、确定性、语言和任务类型会在不同层形成可解码或可干预表示。

## 13.6.3 改变角色和控制状态

系统、用户、引用文本和工具内容需要被区分。模型的角色判断是学习得到的机制，不是硬件级权限隔离。

## 13.6.4 改变 attention 路由

一个 token 的变化可以同时改变 query、key 和 value。Softmax 还会让所有可读位置相互竞争，所以局部变化可以重新分配整条读取路径。

## 13.6.5 跨越非线性阈值

若某特征接近门槛，小扰动可能让它从不活跃转为活跃，引发下游级联。

## 13.6.6 改变生成轨迹

input 决定初始输出分布；首 token 再决定下一步 input。小的首步差异由此变成长期路径差异。

# 13.7 大模型的“推理”应怎样理解

最稳妥的定义是：

> 推理是模型在当前上下文下，通过多层表示变换、注意力读取、潜在特征组合和自回归外部状态形成答案的条件计算过程。

它不必是一条单线程符号程序。

## 13.7.1 层维度推理

一次 forward pass 内，前层形成中间实体、候选答案或局部计算，后层继续组合。两跳事实问题中可以出现内部中间实体，而无需把中间步骤写成文本。

## 13.7.2 序列维度推理

模型可以把中间结果写成 token，后续位置再读取。Chain-of-thought 因而可能增加串行计算深度。

## 13.7.3 多路径推理

同一答案可同时获得：

- 事实记忆路径；
- 近似启发式；
- 上下文模式匹配；
- 显式中间计算；
- 格式和语言约束；
- 校验或拒绝路径。

最终 logit 是这些贡献的合成。答案正确并不证明模型使用了理想算法。

## 13.7.4 Chain-of-thought 的地位

外显 CoT 是模型生成的文本，不是内部计算图的直接打印。它可以：

- 反映真实中间计算；
- 只报告部分计算；
- 在答案已经形成后事后合理化；
- 受用户暗示影响而构造解释。

因此 CoT 是证据来源之一，不是最终机制证据。

# 13.8 表征：神经元、特征、子空间与流形

## 13.8.1 为什么不能只看神经元

若模型需要表示的稀疏特征数 $F$ 大于维度 $d$，可以将多个特征放在非正交方向上：

$$
h=Dx,
\qquad F>d.
$$

当特征很少同时激活，容量收益可能超过干扰成本。这就是 superposition 的核心直觉。

## 13.8.2 SAE 在做什么

Sparse autoencoder 试图找到稀疏特征 $f_i(x)$ 和方向 $d_i$：

$$
x\approx b+\sum_i f_i(x)d_i.
$$

它可以得到比神经元更可读的分析单位，但仍有：

- 重建误差；
- feature splitting/merging；
- 字典大小依赖；
- 基底不唯一；
- 标签覆盖不完整。

所以 SAE 特征是有用接口，不是已经证明的唯一“模型原子”。

## 13.8.3 连续几何

某些变量可能不是一组完全独立离散特征，而是位于低维流形上。离散特征视角和连续几何视角可以同时正确：前者像局部坐标，后者描述整体结构。

# 13.9 安全、越狱与 prompt injection 的清晰分解

为避免把所有安全失败归因于一个“拒绝神经元”，至少分成五步：

```text
1. 识别输入整体含义
2. 形成危险性、角色和权限表示
3. 形成拒绝或安全重定向策略状态
4. 策略状态影响输出 token 竞争
5. 生成前缀通过反馈维持或改变轨迹
```

任何接口都可能失配。

## 13.9.1 语义组合延迟

模型可能分别处理局部片段，却没有在输出前及时形成整体危险概念。此时任务完成路径已经先开始生成。

## 13.9.2 识别与行为分离

“内部可以解码出危险性”不等于“拒绝状态已经形成”，更不等于“拒绝 token 赢得输出”。识别、策略和行为是不同变量。

## 13.9.3 角色或权限判断错误

Prompt injection 主要利用指令和数据共同进入模型上下文。角色标签提供线索，但模型仍在学习式地判断谁应被服从，而不是依赖形式化访问控制。

## 13.9.4 路由和竞争失配

拒绝、任务完成、角色扮演、语法一致性和事实回答可以同时向 logits 贡献。安全路径可能存在，但在关键步骤没有赢。

## 13.9.5 自回归惯性

一旦生成回答式、代码式或列表式前缀，它会成为后续强输入。语法、自洽和任务完成倾向可能继续强化当前轨迹。

这个框架同样解释过度拒绝：表面危险特征或粗糙策略路径过强，压过了精细无害语义判断。

# 13.10 “token 分布偏置”四种含义

| 偏置类型 | 发生位置 | 改变什么 |
|---|---|---|
| 训练分布偏置 | 训练 | 长期权重和先验 |
| 上下文条件偏置 | 单次推理 | 当前激活、路由和 logits |
| 解码偏置 | token 选择 | 从给定 logits 选哪个 token |
| 轨迹偏置 | 连续生成 | 已选 token 改变未来状态 |

不要把它们混成一个概念。Temperature 不会删除训练偏置；prompt 不会在普通推理中重写参数；输出分布是当前激活的结果，只有选中 token 回填后才影响下一步激活。

# 13.11 当前研究能说到什么程度

比较稳健的结论：

1. 标准推理中参数通常固定，input 改变激活和条件路由。
2. 模型内部存在可解码、部分可干预的中间表示。
3. Attention 需要同时解释 QK 路由和 OV 写回。
4. 多义神经元与 superposition 使“一个神经元一个概念”不可靠。
5. SAE、transcoder、crosscoder、NLA 是近似解释接口。
6. 局部 attribution graph 能产生可检验机制假设，但不是全模型源代码。
7. 推理可以在层维度、序列维度和多路径维度发生。
8. CoT 不保证机制忠实。
9. 识别、安全策略和最终行为可以分离。
10. 权重绝对值不是功能重要性的充分指标。

目前不能合理宣称：

- 已经获得所有前沿模型的完整程序；
- 存在唯一正确的全局特征字典；
- 每个行为都由一个方向或一个头决定；
- 模型报告内部状态就证明它有意识；
- 一个小模型或单 prompt 的结果能无条件推广到所有模型。

# 13.12 遇到一个模型现象时怎样提问

按顺序问：

1. 字符串被 tokenizer 分成了什么？
2. 研究的是训练效应、单步激活还是生成轨迹？
3. 观察到了信息存在，还是证明模型使用了信息？
4. 哪些注意力位置和写回方向发生变化？
5. 哪些输出路径在 logit 空间竞争？
6. 首 token 是否构造了新的强上下文？
7. 有什么正对照、负对照和反事实 patch？
8. 解释是否跨模板、跨样本和跨模型复现？
9. 结果最多支持哪个证据层级？
10. 什么结果会推翻当前解释？

# 13.13 对应代码

本章中的核心命题已经在独立子项目 [`../code/`](../code/) 中操作化：

```text
C01 权重 × 激活与分布有效性
C02 温度与赔率恒等式
C03 固定权重下的输入条件计算
C04 QK 路由与 OV 写回
C05 首 token 反馈和轨迹分叉
C06 sparse superposition 与干扰
C07 probe 可解码但不被使用的反例
C08 activation patching
C09 识别—策略—行为分离的无害代理
M01–M03 开放模型观测与局部干预
```

下一章给出逐条理论—实验—反证条件映射。

# 13.14 主要来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [Tracing Attention Computation Through Feature Interactions](https://transformer-circuits.pub/2025/attention-qk/index.html)
- [When Models Manipulate Manifolds](https://transformer-circuits.pub/2025/linebreaks/index.html)
- [Natural Language Autoencoders](https://transformer-circuits.pub/2026/nla/index.html)
- [Verbalizable Representations Form a Global Workspace](https://transformer-circuits.pub/2026/workspace/index.html)
- [Characterizing Interference Weights](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
