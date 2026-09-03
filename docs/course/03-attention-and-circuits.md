# 第 3 章｜Attention、QK、OV 与回路

## 学完你应该能

- 解释 Attention 不是“重要性热图”；
- 分别说明 QK circuit 和 OV circuit 回答什么问题；
- 理解 residual stream 为什么像共享通信总线；
- 用路径组合而不是单个头标签解释一个简单回路。

## 核心模型

对查询位置 $i$ 和可读取位置 $j$：

$$
q_i=h_iW_Q,
\qquad
k_j=h_jW_K,
\qquad
v_j=h_jW_V.
$$

Attention 分数和权重是：

$$
s_{ij}=\frac{q_i^\top k_j}{\sqrt{d_k}},
\qquad
\alpha_{ij}=\operatorname{softmax}_j(s_{ij}).
$$

头的输出是：

$$
o_i=\sum_j\alpha_{ij}v_jW_O.
$$

因此一个头至少包含两个不同问题：

```text
QK：为什么读取这个位置？
OV：读取后写回什么方向？
```

## 逐步理解

### 1. Attention 权重高不代表因果重要

某位置的 $\alpha_{ij}$ 很高，只说明该头在当前输入中大量聚合该位置的 value。它没有告诉你：

- 这个位置为什么得到高分；
- value 中有什么信息；
- $W_O$ 把信息写到哪里；
- 其他头是否写入相反方向；
- 下游是否读取这次更新；
- 消融后行为是否真的变化。

### 2. Softmax 使所有位置相互竞争

提高一个位置的分数会改变分母，因此其他位置的注意力权重也会下降。Attention 不是独立的边开关，而是相对竞争。

### 3. Residual stream 让回路跨层组合

Transformer 每层近似执行：

$$
h^{(\ell+1)}
=
h^{(\ell)}
+
\operatorname{Attn}_\ell(h^{(\ell)})
+
\operatorname{MLP}_\ell(h^{(\ell)}).
$$

每个模块都从同一 residual stream 读取并写回。早层头写入的方向，可以改变后层头的 query、key 或 value，于是算法存在于多个矩阵和层的组合中。

### 4. Induction head 的最小图景

序列出现：

```text
... A B ... A
```

模型倾向续写 B。一个典型机制是：

```text
早层建立“前一个 token”信息
→ 后层 query 在历史中寻找匹配的 A
→ 读取先前 A 后面的 B
→ OV 路径提高 B 的 logit
```

这不是说所有 in-context learning 都由 induction heads 完成，而是展示“头与头的组合可以形成算法”。

### 5. 回路是条件化的

同一组 $W_Q,W_K,W_V,W_O$ 对不同输入产生不同 $q,k,v$，因此实际读取位置和写回内容随上下文变化。权重定义潜在网络，输入选择本次活跃路径。

## 动手验证

```bash
llm-theory-lab explain C04
llm-theory-lab run-toy --ids C04
python examples/03_attention_routing.py
```

实验只改变一个 token 在 key-relevant 方向上的表示，同时保持所有矩阵固定。你应检查：

1. 最高 Attention 位置是否改变；
2. 聚合输出向量是否也改变；
3. 为什么这仍不能证明真实模型中的某个头具有同一功能。

## 常见误区

**“Attention is explanation。”** Attention pattern 是计算中的一个中间量，不是完整因果解释。

**“这个头是姓名头，所以它只处理姓名。”** 真实头通常高秩、上下文相关，在不同数据子分布上可表现出多个模式。

**“QK 找到信息，就等于模型使用了信息。”** 还要检查 OV 写回和下游路径。

**“消融一个头没效果，说明它没用。”** 可能存在冗余、备份路径或消融产生分布外状态。

## 自测

1. 两个输入有相同 Attention 权重，但 value 不同，输出是否相同？
2. 两个头有相同 QK pattern，但 OV 不同，功能是否相同？
3. 为什么只看最高 Attention 位置无法解释 token logit？
4. 给出一个检验“某头写入的信息被下游使用”的因果实验。

## 来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [Progress on Attention](https://transformer-circuits.pub/2025/attention-update/index.html)
- [Tracing Attention Computation Through Feature Interactions](https://transformer-circuits.pub/2025/attention-qk/index.html)
- [HeadVis](https://transformer-circuits.pub/2026/headvis/index.html)
