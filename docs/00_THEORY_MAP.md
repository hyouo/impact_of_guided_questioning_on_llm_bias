# 00｜大模型理论总图

## 0.1 研究对象

大语言模型可以被理解为一个由参数化函数、上下文状态和自回归反馈共同构成的条件动力系统：

$$
p_\theta(y_t\mid x_{1:n},y_{<t})
=\operatorname{softmax}(z_t),
\qquad z_t=W_Uh_t^{(L)}.
$$

这里有四个不能混淆的层次：

1. **训练层**：数据分布、损失函数和优化器塑造参数 $\theta$。
2. **表示层**：当前输入在残差流中形成神经元激活、特征方向、几何结构和位置绑定。
3. **计算层**：注意力、MLP 与其他模块把表示读出、组合、路由和写回。
4. **行为层**：最终状态被投影为 logits，解码出 token，并通过回填形成后续轨迹。

再向外一层，还有系统提示、工具、记忆、权限、环境反馈和用户交互构成的**代理层**。prompt injection 和 agent 安全主要发生在这一层与模型层的接口处。

## 0.2 统一因果图

```text
训练语料 / 后训练数据 / 损失权重 / 优化器
                     │
                     ▼
                  参数 θ
                     │
输入字符串 ─> tokenizer ─> token / position / role 表示
                     │
                     ▼
       残差流中的条件激活与临时状态
          │             │             │
          ▼             ▼             ▼
      MLP 特征      Attention QK    Attention OV
          │             │             │
          └─────────────┴─────────────┘
                        │
                        ▼
              prompt-specific 计算图
                        │
                        ▼
                 logits / 概率分布
                        │
           greedy / sampling / search / constraints
                        │
                        ▼
                    输出 token
                        │
                        └────写回上下文────> 下一轮计算
```

这个图给出本仓库的总命题：

> 模型不是“从数据库中取一句话”，也不是“执行一条固定隐藏程序”；它在固定参数提供的潜在计算网络中，依据当前上下文形成一张条件化、分布式、可能多路径并行的实际计算图。

## 0.3 五条理论主线

### 主线 A：从参数到实际作用

参数是全局、静态的连接规则；激活是输入条件下的动态状态。线性层中一条连接的直接贡献是：

$$
c_{ij}(x)=w_{ij}x_j.
$$

但这仍不是最终因果重要性。要继续考虑：

- 目标单元是否通过非线性门控；
- 后续路径是否把信息传到输出；
- 是否存在抵消或冗余；
- 连接在真实数据分布上是否经常生效；
- 移除它是否真正改变损失或行为。

因此必须区分：**magnitude → contribution → effectiveness → helpfulness/causal effect**。

### 主线 B：从神经元到特征和几何

神经元坐标不一定对应人类可命名变量。superposition 允许多个稀疏特征共享有限维度，于是出现 polysemanticity。机制研究尝试寻找更合适的描述基底：

- 稀疏自编码器：在单层激活中找稀疏方向；
- transcoder：用稀疏中间变量近似层间变换；
- crosscoder：跨层或跨模型寻找共享特征；
- feature manifold：用低内在维的连续几何解释一族离散特征；
- NLA：通过自然语言瓶颈近似表达激活信息。

这些都是分析接口，不是已经证明唯一存在的“模型原子”。

### 主线 C：从注意力到条件计算

Attention 不是泛泛的“模型关注哪里”。它包含两类不同问题：

- **QK circuit**：为什么当前位置要读取那个位置？
- **OV circuit**：读到内容后，向残差流写入什么？

注意力模式本身由输入决定，因此同一组权重可以在不同上下文执行不同路由。解释 attention 不能只看热力图，还需解释 QK 特征交互和 OV 输出效应。

### 主线 D：从内部状态到推理

推理可以发生在：

- 层维度：一次 forward pass 的连续变换；
- 序列维度：把中间结果写成 token，再在后续步骤读取；
- 多路径维度：事实记忆、启发式、任务格式、规划和校验并行贡献。

外显 chain-of-thought 是模型输出的一部分，不是内部因果图的透明转录。它可能忠实、压缩、遗漏，也可能事后合理化。

### 主线 E：从安全识别到安全行为

安全机制至少可拆成：

```text
输入语义识别
  → 危险/权限/角色表征
  → 拒绝或安全重定向状态
  → 输出 token 竞争
  → 自回归延续
```

越狱或 prompt injection 可能攻击链条中的不同接口：整体语义组合延迟、角色判断错误、安全路径未被读取、任务/语法路径先赢得首 token、输出前缀形成持续反馈等。不能把所有现象归结为“一个安全神经元被关闭”。

## 0.4 三种解释尺度

### 局部解释

回答：为什么这个模型对这个 prompt 产生这个 token？

常用工具：logit attribution、activation patching、attribution graph、特征干预。优点是条件明确；缺点是可能只适用于一个例子。

### 中尺度解释

回答：某个特征家族、头或回路在一类任务上的稳定功能是什么？

需要跨样本、跨模板、反事实输入、消融和分布测试。HeadVis 的核心提醒是：一个头在窄数据集上的行为不一定代表它在全分布上的功能。

### 全局解释

回答：能否像读程序一样理解整个模型的权重和回路？

这是机制可解释性的长期目标，但 superposition、干扰权重、替代路径、基底不唯一和模型规模都构成障碍。2026 年的 interference weights 工作表明，即使得到更可解释的虚拟权重，原始权重大小仍不能直接告诉我们功能重要性。

## 0.5 当前最稳健的综合结论

1. 标准推理中参数通常固定，输入改变激活和路由。
2. 模型内部存在可解码、部分可干预的中间表示。
3. 相同输出可以由多个机制共同支持，正确答案不证明算法正确。
4. 特征通常比单个神经元更适合作为语义分析单位，但特征分解不是唯一真相。
5. 注意力头是高秩、上下文相关的组合变换，不能只用一个标签概括。
6. 局部 attribution graph 能提出和验证机制，但不是模型完整源代码。
7. 生成 token 会改变未来状态，因此首 token 和格式前缀具有路径依赖。
8. 安全判断与安全行为可以分离；安全信号存在不保证它控制最终输出。
9. 2025–2026 年的 global workspace、NLA、introspection 和 emotion concepts 提供了新接口与现象，但不证明意识或主观体验。
10. 理论进步取决于把“可读故事”升级为“可反驳、可干预、跨分布复现的模型”。

## 0.6 核心来源

- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)
- [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [Verbalizable Representations Form a Global Workspace](https://transformer-circuits.pub/2026/workspace/index.html)
- [Characterizing Interference Weights](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
