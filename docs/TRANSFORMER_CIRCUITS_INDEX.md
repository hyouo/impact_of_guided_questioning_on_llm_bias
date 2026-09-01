# Transformer Circuits 完整索引

> 快照日期：2026-09-01。目录以 Transformer Circuits 首页可见时间线为边界，共 **56** 条：55 个站内/交叉发布/工具条目，加 1 个 Distill Circuits 前史。

本页不是原文摘要的替代品。`role` 列只说明该条目在本仓库理论中的位置；科学引用应打开原始页面。月度更新和部分短文明确属于初步研究，不能与长篇论文等权使用。

## 状态标签

| 标签 | 含义 |
|---|---|
| 研究论文 | 相对完整的研究页面；仍应核对方法和局限 |
| 研究更新 | 类似实验室阶段报告，结论通常更初步 |
| 工具/论文 | 主要贡献是分析界面或工具，同时包含案例 |
| 交叉发布 | 发布在 Anthropic Alignment 等其他站点 |
| 观点/方法论 | 研究战略、概念或科学方法讨论 |
| 基础设施/教学/前史 | 工具、练习、视频和历史来源 |

## 2026

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2026-08-21 | [Characterizing interference weights in a tiny language model](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html) | 研究论文 | 区分虚拟权重大小、有效性与帮助性；展示真实 transformer 中的干扰权重。 |
| 2026-07 | [Verbalizable Representations Form a Global Workspace in Language Models](https://transformer-circuits.pub/2026/workspace/index.html) | 研究论文 | 提出更可报告、可控制、可复用的 J-space/global-workspace 功能结构。 |
| 2026-06 | [Circuits Updates — June 2026](https://transformer-circuits.pub/2026/june-update/index.html) | 研究更新 | turn-averaged sparse autoencoders；探索跨 token 聚合的表示分解。 |
| 2026-05 | [Circuits Updates — May 2026](https://transformer-circuits.pub/2026/may-update/index.html) | 研究更新 | 用下游连接理解特征，并研究哪些特征更可能有效 steering。 |
| 2026-05-07 | [Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations](https://transformer-circuits.pub/2026/nla/index.html) | 研究论文 | 用 verbalizer/reconstructor 与自然语言瓶颈重建激活，作为假设生成和审计接口。 |
| 2026-05-04 | [HeadVis: An Interactive Tool For Investigating Attention Heads](https://transformer-circuits.pub/2026/headvis/index.html) | 工具/论文 | 在全数据分布上可视化高秩、上下文相关的注意力头行为。 |
| 2026-04-02 | [Emotion Concepts and their Function in a Large Language Model](https://transformer-circuits.pub/2026/emotions/index.html) | 研究论文 | 提取情绪概念表示并验证其行为因果效应；不等同于主观体验。 |

## 2025

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2025-12 | [Circuits Cross-Post — Activation Oracles](https://alignment.anthropic.com/2025/activation-oracles/) | 交叉发布 | 训练模型用自然语言回答有关自身激活的问题，探索有限内部状态读出。 |
| 2025-11 | [Circuits Updates — November 2025](https://transformer-circuits.pub/2025/november-update/index.html) | 研究更新 | 研究 harm pressure 如何通过注意力路由影响回答与安全行为。 |
| 2025-10 | [Emergent Introspective Awareness in Large Language Models](https://transformer-circuits.pub/2025/introspection/index.html) | 研究论文 | 测试模型对注入内部状态的识别和报告能力，并讨论严格边界。 |
| 2025-10 | [Circuits Updates — October 2025](https://transformer-circuits.pub/2025/october-update/index.html) | 研究更新 | 跨文本视觉形式的特征与 dictionary 初始化方法。 |
| 2025-10 | [When Models Manipulate Manifolds: The Geometry of a Counting Task](https://transformer-circuits.pub/2025/linebreaks/index.html) | 研究论文 | 以换行计数展示离散特征、连续流形、QK 扭转和分布式计算的统一。 |
| 2025-09 | [Circuits Updates — September 2025](https://transformer-circuits.pub/2025/september-update/index.html) | 研究更新 | 探索特征与 in-context learning 的关系。 |
| 2025-08 | [Circuits Updates — August 2025](https://transformer-circuits.pub/2025/august-update/index.html) | 研究更新 | 研究 persona 如何调制知识报告、风格和行为。 |
| 2025-07 | [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html) | 研究更新 | 说明 replacement model/transcoder 解释可能产生机制不忠实。 |
| 2025-07 | [Tracing Attention Computation Through Feature Interactions](https://transformer-circuits.pub/2025/attention-qk/index.html) | 研究论文 | 把 QK 注意力分数展开为 query/key 特征交互并接入归因图。 |
| 2025-07 | [A Toy Model of Interference Weights](https://transformer-circuits.pub/2025/interference-weights/index.html) | 研究更新 | 用玩具模型澄清权重叠加与干扰权重的多种定义。 |
| 2025-07 | [Sparse mixtures of linear transforms](https://transformer-circuits.pub/2025/bulk-update/index.html) | 研究更新 | 把“何时激活”和“激活时执行什么变换”共同建模为稀疏线性变换混合。 |
| 2025-07 | [Circuits Updates — July 2025](https://transformer-circuits.pub/2025/july-update/index.html) | 研究更新 | 回顾数学框架、虚拟权重和可解释性在生物学等方向的应用。 |
| 2025-07 | [Automated Auditing](https://alignment.anthropic.com/2025/automated-auditing/) | 交叉发布 | 探索使用代理和可解释性工具进行自动化对齐审计。 |
| 2025-04 | [Circuits Updates — April 2025](https://transformer-circuits.pub/2025/april-update/index.html) | 研究更新 | 失败越狱、密集特征和机制可解释性研究实践；包含重要失败案例。 |
| 2025-04 | [Progress on Attention](https://transformer-circuits.pub/2025/attention-update/index.html) | 研究更新 | 总结注意力解释的困难及 QK/OV 分析进展。 |
| 2025-03 | [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) | 研究论文 | 用归因图研究多步推理、规划、幻觉、拒绝、越狱和 CoT 忠实性。 |
| 2025-03 | [Circuit Tracing: Revealing Computational Graphs in Language Models](https://transformer-circuits.pub/2025/attribution-graphs/methods.html) | 研究论文 | 提出 cross-layer transcoder 与 prompt-specific attribution graph 方法。 |
| 2025-02 | [Insights on Crosscoder Model Diffing](https://transformer-circuits.pub/2025/crosscoder-diffing-update/index.html) | 研究更新 | 用 crosscoder 比较模型表示与微调差异的初步结果。 |
| 2025-01 | [Circuits Updates — January 2025](https://transformer-circuits.pub/2025/january-update/index.html) | 研究更新 | dictionary learning 的优化与训练技术。 |

## 2024

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2024-12 | [Stage-Wise Model Diffing](https://transformer-circuits.pub/2024/model-diffing/index.html) | 研究更新 | 通过分阶段引入数据与模型变化，隔离微调特征变化。 |
| 2024-10 | [Sparse Crosscoders for Cross-Layer Features and Model Diffing](https://transformer-circuits.pub/2024/crosscoders/index.html) | 研究更新 | 跨层/跨模型联合特征分解，减少层间重复并建立共享坐标。 |
| 2024-10 | [Using Dictionary Learning Features as Classifiers](https://transformer-circuits.pub/2024/features-as-classifiers/index.html) | 研究更新 | 比较字典特征与原始激活的有害性分类能力。 |
| 2024-09 | [Circuits Updates — September 2024](https://transformer-circuits.pub/2024/september-update/index.html) | 研究更新 | successor heads、SAE 数据过采样等初步研究。 |
| 2024-08 | [Circuits Updates — August 2024](https://transformer-circuits.pub/2024/august-update/index.html) | 研究更新 | 可解释性评估与自我解释复现。 |
| 2024-07 | [Circuits Updates — July 2024](https://transformer-circuits.pub/2024/july-update/index.html) | 研究更新 | 总结可解释性的五个障碍、线性表示、暗物质和特征敏感性。 |
| 2024-06 | [Circuits Updates — June 2024](https://transformer-circuits.pub/2024/june-update/index.html) | 研究更新 | TopK 与 gated SAE 等训练方法。 |
| 2024-05 | [Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) | 研究论文 | 把 SAE 扩展到生产级模型，研究抽象特征、因果 steering 与安全相关表示。 |
| 2024-04 | [Circuits Updates — April 2024](https://transformer-circuits.pub/2024/april-update/index.html) | 研究更新 | SAE 训练、特征评估和相关实验更新。 |
| 2024-03 | [Circuits Updates — March 2024](https://transformer-circuits.pub/2024/march-update/index.html) | 研究更新 | 机制可解释性与字典学习的短期研究结果。 |
| 2024-03 | [Reflections on Qualitative Research](https://transformer-circuits.pub/2024/qualitative-essay/index.html) | 观点/方法论 | 讨论前范式领域中定性发现、可视化与“结构信号”的科学角色。 |
| 2024-02 | [Circuits Updates — February 2024](https://transformer-circuits.pub/2024/feb-update/index.html) | 研究更新 | 可解释性团队的阶段性研究记录。 |
| 2024-01 | [Circuits Updates — January 2024](https://transformer-circuits.pub/2024/jan-update/index.html) | 研究更新 | 特征分解、训练和分析的阶段性研究记录。 |

## 2023

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2023-10 | [Towards Monosemanticity: Decomposing Language Models With Dictionary Learning](https://transformer-circuits.pub/2023/monosemantic-features/index.html) | 研究论文 | 用 SAE 从一层 transformer 中提取比神经元更可解释的稀疏特征。 |
| 2023-07 | [Circuits Updates — July 2023](https://transformer-circuits.pub/2023/july-update/index.html) | 研究更新 | 有限数据区间、安全相关特征和 skip-trigram 回路。 |
| 2023-05 | [Circuits Updates — May 2023](https://transformer-circuits.pub/2023/may-update/index.html) | 研究更新 | dictionary learning、特征定义、权重/头叠加等早期思考。 |
| 2023-05 | [Interpretability Dreams](https://transformer-circuits.pub/2023/interpretability-dreams/index.html) | 观点/方法论 | 描述机制可解释性的长期目标、潜在安全用途和研究路线。 |
| 2023-05 | [Distributed Representations: Composition & Superposition](https://transformer-circuits.pub/2023/superposition-composition/index.html) | 观点/方法论 | 区分有意义的组合表示与容量压缩产生的叠加。 |
| 2023-03 | [Privileged Bases in the Transformer Residual Stream](https://transformer-circuits.pub/2023/privileged-basis/index.html) | 研究论文 | 研究残差流坐标为何在实际训练中可能并非完全旋转对称。 |
| 2023-01 | [Superposition, Memorization, and Double Descent](https://transformer-circuits.pub/2023/toy-double-descent/index.html) | 研究论文 | 连接有限数据、记忆、泛化、叠加与 double descent。 |

## 2022

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2022-09 | [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html) | 研究论文 | 在可控玩具网络中建立 superposition、polysemanticity、相变与几何的基础。 |
| 2022-06 | [Softmax Linear Units](https://transformer-circuits.pub/2022/solu/index.html) | 研究论文 | 研究替代激活函数能否提高神经元表面可解释性。 |
| 2022-06 | [Mechanistic Interpretability, Variables, and the Importance of Interpretable Bases](https://transformer-circuits.pub/2022/mech-interp-essay/index.html) | 观点/方法论 | 讨论变量、基底与机制解释单位的概念基础。 |
| 2022-03 | [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html) | 研究论文 | 研究 induction heads、训练相变与 in-context learning 的机制联系。 |

## 2021

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2021-12 | [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html) | 研究论文 | 建立 residual stream、QK/OV、路径展开、虚拟权重与小模型逆向工程框架。 |
| 2021-12 | [Transformer Circuit Exercises](https://transformer-circuits.pub/2021/exercises/index.html) | 练习 | 通过参数级算法练习建立机制推理能力。 |
| 2021-12 | [Transformer Circuit Videos](https://transformer-circuits.pub/2021/videos/index.html) | 教学资源 | 早期非正式讲解与研究思路。 |
| 2021-12 | [PySvelte](https://github.com/anthropics/PySvelte) | 基础设施 | 连接 Python 与交互式网页可视化的基础设施。 |
| 2021-12 | [Garcon](https://transformer-circuits.pub/2021/garcon/index.html) | 基础设施 | 面向大模型可解释性实验的数据与计算工具。 |

## 2020

| 时间 | 条目 | 状态 | 在统一理论中的作用 |
|---|---|---|---|
| 2020-03/2021-04 | [Original Distill Circuits Thread](https://distill.pub/2020/circuits/) | 前史 | Transformer Circuits 的视觉化、逆向工程与 circuits 研究前史。 |

## 主题阅读映射

| 想理解的问题 | 优先阅读 |
|---|---|
| 权重、路径、QK/OV | Mathematical Framework → Attention-QK → Interference Weights |
| 输入如何形成临时规则 | Induction Heads → September 2025 ICL update → Global Workspace |
| 神经元为何多义 | Toy Models → Composition & Superposition → Towards/Scaling Monosemanticity |
| 特征如何跨层/跨模型 | Sparse Crosscoders → Crosscoder Diffing → Stage-Wise Model Diffing |
| 如何解释单个回答 | Circuit Tracing → Biology → Attention Feature Interactions |
| 离散特征与连续几何 | Linebreaks / Counting Manifolds |
| 模型能否报告内部状态 | Activation Oracles → Introspection → NLA → Global Workspace |
| 越狱与安全行为 | Scaling safety features → Biology jailbreak → April/November updates |
| 工具局限和科学方法 | Qualitative Research → Mechanistic Unfaithfulness → HeadVis |

## 机器可读版本

完整字段见 [`sources/transformer_circuits_catalog.csv`](../sources/transformer_circuits_catalog.csv)。CI 会检查条目数量、链接唯一性、状态枚举和首页关键条目。
