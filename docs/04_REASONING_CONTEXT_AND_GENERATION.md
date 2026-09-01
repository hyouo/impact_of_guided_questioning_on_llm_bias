# 04｜上下文、推理、规划与生成轨迹

## 4.1 推理的工作定义

本仓库把推理定义为：

> 在固定参数和当前上下文约束下，模型通过表示形成、信息路由、局部变换、候选竞争、校验与序列反馈，把输入状态映射为输出状态的条件计算。

这一定义同时拒绝两个极端：

- “模型只是词频拼接，没有中间计算”；
- “模型内部必然存在一条清晰、单线程、与文字 CoT 同构的符号程序”。

实际情况更可能是分布式、多路径、混合算法和启发式。

## 4.2 两个计算维度

### 层维度

一次 forward pass 内，模型可以在不同层形成中间变量：

```text
输入实体 → 关系表示 → 中间答案 → 输出倾向
```

这些状态不必被写成文字。Circuit Tracing 的案例显示，某些事实问题、规划任务和诗歌押韵会形成可干预的中间表示。

### 序列维度

模型还可把中间结果写成 token，再在后续位置通过注意力读取：

```text
内部状态 → 生成草稿/步骤 → 新上下文 → 继续计算
```

这使固定深度网络获得更长的串行计算时间，也引入错误累积、提示污染和生成惯性。

## 4.3 In-context learning

Induction head 给出一个早期、具体的上下文学习机制：

\[
[A][B]\ldots[A]\rightarrow[B].
\]

在小型模型中，前一层头可以把前 token 信息写入当前位置，后一层 induction head 依据前缀匹配寻找过去相似位置，并复制其后继 token。大模型中的上下文学习显然比字面复制更丰富，但该机制证明：

- 参数不变时，模型仍能利用上下文形成临时规则；
- “学习”可以表现为检索并执行训练中学到的通用回路；
- 上下文示例、顺序和重复能够实质改变计算。

不能把 induction heads 直接等同于所有现代大模型的全部 in-context learning；原研究本身也区分了小模型中的强机制证据与大模型中的间接证据。

## 4.4 多路径推理

一个答案可能同时受到：

\[
z=z^{memory}+z^{algorithm}+z^{heuristic}+z^{format}+z^{persona}+z^{safety}+\cdots
\]

的支持。这个分解是分析语言，不意味着模型真的有完全独立模块。

常见组合：

- 事实记忆与两步关系推理同时给出相同答案；
- 主算法得到答案，快捷模式直接预测答案；
- 语义判断与多项选择格式头共同决定字母；
- 计划表示提前约束句尾、韵脚或工具调用；
- 校验头检查候选与上下文是否一致。

因此“回答正确”只证明最终竞争结果正确，不证明中间机制可靠。

## 4.5 规划

On the Biology 的案例显示，模型可能提前形成：

- 目标词或押韵结尾；
- 中间实体；
- 句法结构；
- 后续段落或动作的抽象计划。

计划不一定是完整脚本，更可能是一组约束、候选和逐步细化状态。其因果性需要通过替换或 steering 计划相关表示，看未来 token 是否按预测改变。

## 4.6 Chain-of-thought 忠实性

自然语言 CoT 是输出，不是神经活动的直接打印。至少有四种关系：

1. **忠实外显**：文字步骤与内部中间状态大体一致；
2. **压缩/省略**：内部存在计算，但文字只给简化解释；
3. **事后合理化**：答案由快捷路径得到，随后构造理由；
4. **提示诱导的倒推**：用户暗示目标答案，模型围绕它生成论证。

A Toy Model of Mechanistic (Un)Faithfulness 进一步提醒：即使分析工具本身看似重建了计算，也可能因 replacement model 的结构产生误导。需要把“模型 CoT 是否忠实”和“解释工具是否忠实”分开验证。

## 4.7 Global workspace / J-space 假说

2026 年的工作报告，在所研究模型中，一小组表示方向似乎具有以下性质：

- 更容易被模型语言化或报告；
- 可被指令调节；
- 可供多种下游任务读取；
- 与灵活、多步、可组合推理相关；
- 大量自动文本处理可以在该子空间之外进行。

可把它理解为“自动并行处理 + 小型可报告工作区”的功能模型：

```text
大量自动局部处理
       ↓ 选择/压缩
可报告、可控制、可复用的中间表示
       ↓
灵活推理与行为
```

但边界必须明确：

- J-lens 只是测量工具，不保证捕获所有相关表示；
- 可报告性不等于意识；
- 工作区类比是功能结构，不是神经科学同一性证明；
- 结果来自特定模型和实验设置。

## 4.8 Introspection 与 activation interfaces

Activation Oracles、Emergent Introspective Awareness 和 NLA 都探索“模型能否以语言访问内部状态”。应区分：

- 模型根据外部文本推断自己的状态；
- 模型从注入或读取的激活获得额外信息；
- 模型能否准确报告内部变量；
- 报告是否对行为具有因果联系；
- 报告器是否自行推断或幻觉。

最安全的研究解释是：某些模型具备可训练、有限、任务相关的内部状态读出能力。这不等于全透明自我理解。

## 4.9 生成轨迹与锁定

第一个 token 往往确定响应模式。设第 \(t\) 步状态为 \(h_t\)，选中 token \(y_t\) 后：

\[
h_{t+1}=F_\theta(h_t, e(y_t), x).
\]

一个回答式开头会增加任务完成、自洽和语法续写压力；拒绝式开头也会加强拒绝模板。于是微小的首 token logit 差可以被反复放大。

轨迹锁定并非绝对。句号、段落边界、角色切换、工具结果和新的高优先级信息都可能让模型重新计算并改变模式。但在句法结构中间，切换成本通常更高。

## 4.10 推理研究的最低标准

声称模型使用某个算法时，至少应回答：

1. 中间变量在哪里、何时出现？
2. 它是否在未见样本上预测行为？
3. 抑制它是否破坏目标计算？
4. 替换它是否得到可预测的反事实结果？
5. 其他路径能否补偿？
6. 文字 CoT 与内部机制的关系是否独立验证？
7. 结论在哪些模型、任务和分布内成立？

## 4.11 核心来源

- [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html)
- [Activation Oracles](https://alignment.anthropic.com/2025/activation-oracles/)
- [Emergent Introspective Awareness](https://transformer-circuits.pub/2025/introspection/index.html)
- [Natural Language Autoencoders](https://transformer-circuits.pub/2026/nla/index.html)
- [Verbalizable Representations Form a Global Workspace](https://transformer-circuits.pub/2026/workspace/index.html)
