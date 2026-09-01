# 03｜回路、注意力与条件计算

## 3.1 Residual stream：共享通信总线

Transformer 的每一层把信息读自并写回 residual stream：

\[
h^{(\ell+1)}=h^{(\ell)}+a^{(\ell)}+m^{(\ell)}.
\]

它不是一个单一语义向量，而是许多并行信号共享的高维工作区。不同层可以：

- 写入新特征；
- 增强或抑制已有方向；
- 复制信息到其他位置；
- 组合局部变量；
- 把中间状态转成输出倾向。

Residual connection 使许多模块的输出可以近似相加，也使 path expansion 成为可能：最终 logit 可分析为多条计算路径贡献的和，但 LayerNorm、softmax 和非线性会限制这种线性展开的精确性。

## 3.2 Attention 的两个回路

对一个 attention head：

\[
q_i=W_Qh_i,\qquad k_j=W_Kh_j,\qquad v_j=W_Vh_j.
\]

注意力分数：

\[
s_{ij}=\frac{q_i^\top k_j}{\sqrt{d_h}},
\qquad
\alpha_{ij}=\operatorname{softmax}_j(s_{ij}).
\]

输出：

\[
o_i=W_O\sum_j\alpha_{ij}v_j.
\]

机制上应拆成：

### QK circuit：选择信息源

\[
s_{ij}=h_i^\top W_Q^\top W_Kh_j.
\]

它回答“为什么当前位置从那个位置读取”。输入特征、角色、位置和语法都可能通过 query-key 交互改变路由。

### OV circuit：处理并写入信息

\[
W_OW_Vh_j.
\]

它回答“读取后向 residual stream 写了什么”。一个头可以复制、抑制、旋转、选择或转换被注意内容。

只展示 attention heatmap 只能看到 \(\alpha\)，既没有解释分数如何形成，也没有说明读到的信息对 logits 有何影响。

## 3.3 Virtual weights 与路径

在简化模型里，可把 head 的直接 token-to-token 作用写成 QK 与 OV 矩阵；多个 head 和 MLP 的路径又可组合成更长的虚拟回路。

例如 induction circuit 的理想化形式：

```text
previous-token head：把前一个 token 信息写到当前位置
          ↓
induction head：找到先前相同前缀并读取其后继 token
          ↓
OV：提高该后继 token 的 logit
```

这展示了“算法”如何由多个模块组合，而不是存放在单一神经元中。

## 3.4 条件计算图

固定参数定义所有潜在路径，prompt 决定每条路径的当前强度。对源特征 \(s\) 和目标特征 \(t\)，局部边归因可近似为：

\[
A_{s\to t}(x)=a_s(x)w_{s\to t}.
\]

于是同一虚拟连接：

- 在源特征不激活时完全无效；
- 在特定 prompt 中成为主要贡献；
- 可能在另一个上下文被其他路径抵消。

这就是“条件计算”的含义：不是改变权重，而是输入选择实际工作的子图和连续强度。

## 3.5 Attribution graph

Circuit Tracing 使用 replacement model、cross-layer transcoders 和归因方法，把一个特定输出展开为特征节点和边。

典型工作流：

1. 选择具体 prompt、目标 token 或 logit 差；
2. 用特征模型近似原模型中的中间变换；
3. 按归因追溯上游特征与位置；
4. 把相关节点聚合为更高层 supernode；
5. 提出机制故事；
6. 用抑制、增强、替换或 patching 验证预测。

归因图的价值不是“看起来像流程图”，而是能够导出可检验反事实。例如：抑制某个上游特征后，下游节点和目标 token 是否按预测变化？

## 3.6 为什么归因图不等于完整程序

- replacement model 有重建误差；
- error nodes 可能承载关键未知信息；
- 冻结 attention pattern 会忽略 QK 形成原因；
- 梯度/局部线性化可能错过强非线性；
- 图通常只覆盖一个 prompt 和一个输出；
- 多条替代路径可在干预后补偿；
- 人工 supernode 聚合会引入解释者判断。

因此图是“局部执行轨迹的近似因果模型”，不是全模型源代码。

## 3.7 解释 attention 的进一步进展

### Feature interaction attribution

2025 年的 QK attribution 把 query 和 key 激活展开为特征、偏置与误差，分析哪些特征对共同提高了某个注意力分数。这能解释“为什么注意到那里”，并与 OV/特征图结合。

### HeadVis

2026 年 HeadVis 强调：attention head 是高秩、上下文相关的计算单元。研究一个窄任务后给头贴上“选择头”“复制头”标签往往不够。需要在广泛数据分布上同时看：

- attention pattern；
- QK 与 OV 特征归因；
- 输出秩和低秩成分；
- 不同任务上的多种行为；
- 反事实干预。

### Mixtures of linear transforms

MOLT 尝试把模块理解为稀疏条件下启用的线性变换，而不只是一组标量特征。它提醒我们：计算单位可能需要同时表示“何时启用”和“启用时执行什么变换”。

## 3.8 多路径并行与校验

真实模型常同时运行：

- 主算法；
- 事实记忆快捷路径；
- 语法和格式路径；
- 候选答案选择；
- 一致性或 discordance 检查；
- 任务和 persona 控制。

简单行为也可能由大量启发式共同支持。分析时应避免“发现一条可解释路径，因此它就是唯一原因”。更强的验证要测试：

- 路径是否必要；
- 路径是否足够；
- 是否存在冗余；
- 在新样本上是否保持；
- 随机方向/随机头是否无同样效应。

## 3.9 核心来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [Progress on Attention](https://transformer-circuits.pub/2025/attention-update/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [Tracing Attention Computation Through Feature Interactions](https://transformer-circuits.pub/2025/attention-qk/index.html)
- [HeadVis](https://transformer-circuits.pub/2026/headvis/index.html)
- [Sparse mixtures of linear transforms](https://transformer-circuits.pub/2025/bulk-update/index.html)
