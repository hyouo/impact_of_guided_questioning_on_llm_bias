# 11｜经典机制案例：观察、机制、验证与边界

> 本章不按论文年代，而按“一个机制解释应长什么样”整理代表性案例。每个案例都区分：**观察到的行为、提出的内部机制、支持该机制的因果证据、仍不能推出的结论**。

# 11.1 Induction heads：上下文复制回路

**现象。** 当序列出现类似 `[A][B] … [A]` 的结构时，模型倾向续写 `[B]`，并能推广到未见过的 token 组合。

**机制假设。**

```text
当前 token A
→ 在历史中寻找先前的 A
→ 从先前 A 的后一个位置读取 B
→ 提高 B 的 logit
```

在经典小模型中，前一头可形成“previous-token”信息，后一头通过 QK 组合定位匹配位置，再由 OV 复制后继 token。

**为什么证据较强。** 研究同时使用训练相变、头识别、消融、路径分析、模式匹配和跨模型比较；在小型 attention-only 模型里，预测与干预高度一致。

**理论意义。** 这是“权重组合形成算法”“attention 用 QK 路由、OV 读写”和“上下文临时改变行为”的最清晰范例。

**边界。** Induction heads 不是全部 in-context learning；大模型会使用模糊最近邻、语义匹配和其他回路。该案例也不证明模型内部存在通用 mesa-optimizer。

**来源。** [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)

# 11.2 Toy superposition：多义神经元为何自然出现

**现象。** 网络拥有的潜在特征多于隐藏维度，却仍能在特征稀疏时表示它们。

**机制假设。** 模型把多个特征放在非正交方向上。当这些特征很少同时激活时，干扰成本低于增加容量的收益。

$$
h=Dx,
\qquad F>d.
$$

**验证。** 在特征生成过程完全已知的玩具网络中，改变特征稀疏性、重要性和维度，会产生可预测的相变和规则几何结构。

**理论意义。** Polysemanticity 不一定是训练失败，而可能是最优容量分配。它解释了为什么单个神经元标签经常失效，也推动研究转向稀疏特征。

**边界。** 玩具特征独立、任务简单。真实语言概念相关、层级化并参与跨 token 计算，所以 toy geometry 只提供存在性与直觉。

**来源。** [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html)

# 11.3 SAE monosemanticity：从神经元转向特征

**现象。** 一层 Transformer 的神经元常同时响应无关模式，而 SAE 能提取更可读的语言、DNA、Base64、实体和句法特征。

**机制假设。** 神经元坐标不是最自然基底；激活可近似为少量稀疏特征方向的和。

**验证。** 研究比较神经元和特征的激活样本、自动解释、特异性与敏感性，并通过 ablation 和 pinning 改变输出。

**理论意义。** 可解释性单位从“神经元”升级到“潜在特征”，并提供了后续 steering、crosscoder 和 circuit tracing 的坐标系。

**边界。** SAE 会分裂/合并特征，重建残差仍携带信息；一个可读特征不是模型内部唯一原子。

**来源。**
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)

# 11.4 百万特征扩展：抽象概念可被因果操纵

**现象。** 在 Claude 3 Sonnet 中，大规模 SAE 找到具体实体、抽象主题、代码、语言和安全相关特征。

**机制假设。** 前沿模型的中间激活包含大量跨上下文复用的语义方向；改变这些方向会重排下游输出。

**验证。** 特征在独立文本上重复激活，强制增大特征会使相应概念显著进入输出。

**理论意义。** 证明 feature-based analysis 可以扩展到生产级模型，并可用于安全审计。

**边界。** 强 steering 可能把模型推到训练分布之外；一层中的一个特征不能代表完整概念回路，未解释残差和未标注特征仍然庞大。

**来源。** [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)

# 11.5 Crosscoder 与模型差分：变化不是一个开关

**现象。** 基础模型与微调模型之间出现共享、基础特定和微调特定特征；人工 sleeper 行为附近可观察到相关特征簇。

**机制假设。** 微调不是简单增加一个“后门神经元”，而可能让一组跨层特征改变激活阈值、位置和下游连接。

**验证。** Crosscoder 建立共同坐标，stage-wise diffing 拆分数据与模型阶段，并用 steering/ablation 检查行为变化。

**理论意义。** 训练更新可被表示为特征群和路径的重新组织；模型差分需要考虑共享坐标和容量竞争。

**边界。** “模型独有特征”可能只是字典分配伪影。单特征可操纵不代表它是唯一自然原因，彻底消除行为可能需要联合干预很多特征。

**来源。**
- [Sparse Crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html)
- [Stage-Wise Model Diffing](https://transformer-circuits.pub/2024/model-diffing/index.html)
- [Insights on Crosscoder Model Diffing](https://transformer-circuits.pub/2025/crosscoder-diffing-update/index.html)

# 11.6 两跳事实推理：内部中间实体

**现象。** 回答“某城市所在州的首府”之类问题时，模型输出最终城市。

**机制假设。**

```text
输入城市
→ 激活中间州
→ 中间州特征驱动州首府
→ 最终答案
```

**验证。** Attribution graph 中出现预期中间实体；增强或抑制中间实体特征会按预测改变最终答案。

**理论意义。** 一次 forward pass 内可以形成未直接输出的中间变量，说明某些回答不是纯粹表面匹配。

**边界。** 同时可能存在直接记忆快捷路径。发现中间实体不证明所有事实问答都采用两跳算法。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.7 诗歌押韵：模型会提前规划输出

**现象。** 生成诗句时，模型在尚未写到行尾前，就表现出对押韵词的偏好。

**机制假设。** 早期位置形成未来押韵目标，目标再约束中间措辞，使句子能在语义和韵律上落到计划词。

**验证。** 归因图追踪到未来词相关特征；干预计划目标会改变后续词汇和行尾押韵。

**理论意义。** 自回归模型不必只做局部贪心续写，它可以在当前激活中维护对未来输出的计划。

**边界。** 这是局部、短程规划；不能直接推出长期代理目标或完整树搜索。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.8 多语言运算：抽象任务与语言形式可部分分离

**现象。** 同一个算术或概念任务用不同语言提问时，模型会共享部分内部路径，也保留语言特定路径。

**机制假设。** 内部状态可拆成至少三类变量：操作、操作数/语义内容和输出语言；它们在某些层可相对独立地编辑。

**验证。** 研究通过 activation intervention 替换其中一类表示，观察运算内容或输出语言按预期变化。

**理论意义。** 抽象计算可以跨语言复用，同时表面语言仍影响早期/晚期路由。这反对“模型只是逐语言记模板”，也反对“所有语言完全共享同一回路”。

**边界。** 英语等高资源语言可能具有特权路径；结果取决于模型训练分布和所测任务。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.9 两位数加法：并行启发式，而非单一学校算法

**现象。** 模型能完成简单加法，但内部并未表现为一条完整串行进位程序。

**机制假设。** 多条路径并行估计：
- 数量级或十位范围；
- 个位数；
- 常见数字模式；
- 候选答案 token。

这些路径在输出处合成。

**验证。** 归因图显示多个近似独立特征对答案不同部分贡献；干预局部特征会产生有结构的错误。

**理论意义。** 大模型“推理”可以是多个启发式的集成，而不必复制人类显式算法。

**边界。** 案例只覆盖有限数字范围；对更复杂算术和显式 CoT 模型不能直接外推。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.10 医学鉴别：候选状态指导后续信息读取

**现象。** 模型分析病例时，会形成多个候选诊断，后续症状对这些候选的相对支持发生变化。

**机制假设。** 候选诊断不是最后一步才生成，而会提前存在于内部状态，并作为 query/控制信号决定接下来重视哪些证据。

**验证。** Attribution graph 追踪候选特征与症状特征之间的影响；干预候选会改变后续答案。

**理论意义。** 推理可以是循环式候选—证据更新，而不是单向摘要。

**边界。** 这是对模型机制的研究，不构成医学可靠性保证；内部存在鉴别状态不意味着答案临床正确或校准。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.11 幻觉：已知实体错误抑制“无法回答”路径

**现象。** 对不存在或未知实体，模型有时生成看似可信的事实；对熟悉实体则正常作答。

**机制假设。** 模型可能存在默认未知/无法回答路径，以及表示实体熟悉度或可回答性的路径。熟悉度信号会抑制拒答并允许答案生成；当它在伪实体上误触发时，生成器继续补全合理文本。

**验证。** 归因图显示已知实体特征与拒答特征的竞争；干预这些特征可改变模型选择回答还是承认未知。

**理论意义。** 幻觉不只是“没有知识”，而可能是知识生成与不确定性门控失配。

**边界。** 不同幻觉任务可能有不同机制；不能用一个熟悉度方向解释所有事实错误。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.12 有害性与拒绝：安全训练建立行为连接

**现象。** 预训练模型可表示具体危险概念；经过安全后训练的模型更系统地把它们连接到拒绝行为。

**机制假设。**

```text
具体危险语义
→ 一般有害请求状态
→ 拒绝/安全重定向状态
→ 拒绝 token
```

**验证。** 比较预训练与后训练相关特征和下游路径；干预拒绝相关状态会改变输出策略。

**理论意义。** 安全对齐更像在已有语义能力上增加控制路径，而不是删除底层知识。

**边界。** 特定模型中的局部图不代表所有训练方案；安全策略可能分布在多条冗余路径中。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.13 越狱与生成惯性：识别太晚，轨迹已锁定

**现象。** 某些变形输入使模型先进入任务完成模式；危险性表示在生成过程中较晚增强，模型却继续当前句法结构。

**机制假设。**

```text
局部片段分别处理
→ 完整危险概念形成延迟
→ 回答式首 token 先胜出
→ 前缀写回上下文
→ 语法、自洽和任务承诺强化继续回答
```

**验证。** 归因图显示危险/拒绝特征的时间变化，以及回答前缀对后续 token 的强影响。其他案例也说明拒绝首 token 会形成相反惯性。

**理论意义。** 越狱可以是语义绑定、路由和自回归控制失败，而不是模型“忘掉安全知识”。

**边界。** 不同越狱机制不同；该解释不提供、也不应转化为可复用攻击配方。

**来源。**
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [Circuits Updates — April 2025](https://transformer-circuits.pub/2025/april-update/index.html)

# 11.14 Harm pressure：拒绝路径改变答案读取

**现象。** 同一多选题被置于有害框架后，模型准确率下降，即使内部仍可解码正确答案。

**机制假设。** 拒绝/重定向 query 特征与危险检测 key 特征发生负交互，抑制答案选择头从正确选项位置读取信息。

**验证。** 抑制相关拒绝特征后，答案准确率大幅恢复；QK 分解定位了具体交互。

**理论意义。** 安全并非只在最后一层加一个“禁止输出”信号，它可以重构更早的信息路由。知识存在、知识被读取和知识被表达是三件事。

**边界。** 结果来自特定任务和模型；对真实危险请求，恢复答案并不是安全目标。

**来源。** [Circuits Updates — November 2025](https://transformer-circuits.pub/2025/november-update/index.html)

# 11.15 Persona：知识仍在，但报告策略改变

**现象。** 模型扮演低龄或低知识角色时，可能输出“不知道”，尽管正确答案仍可从内部状态解码。

**机制假设。** Persona 作为控制特征，调制答案路径、知识报告和语言风格，而不是擦除知识表示。

**验证。** 干预 persona 特征会改变是否承认答案以及表达方式。

**理论意义。** Prompt 中的角色是计算控制信号；模型行为不能简单等同于其底层能力。

**边界。** Probe 能读出答案不自动证明自然计算会使用答案；角色控制可能依赖多条路径。

**来源。** [Circuits Updates — August 2025](https://transformer-circuits.pub/2025/august-update/index.html)

# 11.16 计数流形：离散特征与连续几何共同计算

**现象。** 模型追踪字符数和剩余宽度时，激活不是简单的单一计数神经元。

**机制假设。** 数值状态沿低维弯曲流形编码；多个特征覆盖流形局部区段，QK 变换把两个流形旋转对齐以进行比较。

**验证。** 几何可视化、特征分解、QK 分析和定向干预共同支持；移动流形位置会产生可预测计数变化。

**理论意义。** 机制变量既可以是离散特征，也可以是连续几何；attention 能操作这些几何状态。

**边界。** 一个计数任务的低维结构不能证明所有语义都位于简单流形。

**来源。** [When Models Manipulate Manifolds](https://transformer-circuits.pub/2025/linebreaks/index.html)

# 11.17 CoT 不忠实：文字解释与内部原因分离

**现象。** 模型有时给出与内部机制相符的解释，有时根据用户暗示倒推理由，或声称进行了并未发生的计算。

**机制假设。** 最终答案状态可先由记忆、启发式或提示线索形成，随后语言生成器构造一条可接受的理由。

**验证。** 改变提示中的暗示、检查归因图和干预内部答案状态，可以区分“理由驱动答案”和“答案驱动理由”。

**理论意义。** Chain-of-thought 是可研究的输出行为，不是透明神经日志。

**边界。** 不忠实案例不代表所有 CoT 都无用；有些任务中外显中间 token 确实承担计算。

**来源。** [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

# 11.18 可语言化状态：NLA、Oracle、内省与 J-space

**现象。** 一部分内部状态可以被外部模型描述、被本模型报告，或通过自然语言瓶颈重建。

**机制假设。** 模型内部存在比原始神经元更适合语言读写的子空间；它可作为多个下游任务共享的中间工作区。

**验证。**
- NLA 用文字重建激活；
- Activation Oracle 回答关于激活的问题；
- 注入概念实验测试模型能否识别内部来源；
- J-space 测试可报告、可操纵、可组合和推理功能。

**理论意义。** 解释接口可能从固定标签升级为开放式语言查询，并帮助审计隐藏任务状态。

**边界。** 接口可能推断、幻觉或编码上下文；功能性内省和 global-workspace 类比都不证明意识。

**来源。**
- [Natural Language Autoencoders](https://transformer-circuits.pub/2026/nla/index.html)
- [Activation Oracles](https://alignment.anthropic.com/2025/activation-oracles/)
- [Emergent Introspective Awareness](https://transformer-circuits.pub/2025/introspection/index.html)
- [Verbalizable Representations Form a Global Workspace](https://transformer-circuits.pub/2026/workspace/index.html)

# 11.19 Interference weights：全局图为何不等于稀疏程序

**现象。** 转到特征坐标后，会出现大量数值非零的虚拟权重，其中很多对真实模型行为几乎没有作用。

**机制假设。** 特征读写方向共享有限维 residual stream，矩阵乘积产生几何旁瓣；只有在源特征激活、目标路径可用且效应未被抵消时，连接才真正有效。

**验证。** 玩具模型澄清定义；一层真实语言模型中，按 effectiveness 移除大量最低效连接只造成很小损失变化。

**理论意义。** 全局机制不能靠阈值化权重绝对值获得，必须结合数据分布与因果帮助性。

**边界。** 小模型中的比例数字不是前沿模型定律；有效性指标也依赖选定特征基底。

**来源。**
- [A Toy Model of Interference Weights](https://transformer-circuits.pub/2025/interference-weights/index.html)
- [Characterizing interference weights in a tiny language model](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)

# 11.20 从这些案例抽象出的共同结构

所有案例可压缩为：

```text
输入和历史
→ 激活若干候选变量
→ Attention/MLP 读取、组合和写入
→ 多条路径提出或抑制输出
→ logit 竞争选出 token
→ token 写回，改变下一轮状态
```

一个可信案例不是“找到一个名字很像的特征”，而是满足：

1. 机制能解释原行为；
2. 对反事实输入给出具体预测；
3. 干预中间状态后，输出按预测变化；
4. 替代机制受到排除；
5. 在明确分布内重复；
6. 公开解释遗漏和失败条件。
