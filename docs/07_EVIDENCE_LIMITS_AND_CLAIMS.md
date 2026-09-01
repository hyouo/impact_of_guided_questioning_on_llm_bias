# 07｜证据等级、已知边界与主张登记

## 7.1 E0–E5 证据等级

| 等级 | 证据 | 可以支持 | 不能单独支持 |
|---|---|---|---|
| E0 | 直觉、类比、单案例 | 提出机制假设 | 普遍规律或因果结论 |
| E1 | 多样本黑盒行为 | 输入与输出存在稳定效应 | 指定内部特征、头或权重 |
| E2 | probe、decoder、相关归因 | 表示中存在可解码信息 | 信息被模型自然使用 |
| E3 | feature/head ablation 或 steering | 候选变量影响行为 | 完整机制、唯一性、自然必要性 |
| E4 | patching、反事实交换、强对照、跨模板复现 | 有边界的局部回路获得强支持 | 全模型全局解释 |
| E5 | 从数据/训练到表征/回路再到行为的可预测理论，跨模型验证 | 限定范围内的机制预测 | 无条件外推到所有架构与分布 |

## 7.2 本仓库采用的主张格式

每个机制结论应包含：

```text
对象：哪个模型/层/组件？
范围：哪些 prompt、任务、语言和数据分布？
证据：行为、probe、归因、干预、patching 中哪些？
反事实：改变候选变量后发生什么？
替代解释：还有哪些路径可能产生结果？
不确定性：工具误差、样本偏差和外推边界是什么？
```

## 7.3 可以较有信心接受的结论

### 标准推理不修改大多数模型参数

输入通过固定权重改变激活、注意力和 logits。特殊系统可有在线学习、缓存更新或外部记忆，但应另行说明。

### 输入会选择不同条件计算

同一模型对不同上下文形成不同特征活动和 attention pattern；这是 Transformer 定义和大量干预实验共同支持的基础事实。

### 神经元通常不是唯一语义原子

superposition、polysemanticity 与 dictionary learning 结果支持使用特征方向作为补充单位，但不存在已证明唯一、完备的特征词典。

### 中间表示可以有因果作用

多个研究通过 steering、ablation 和 patching 改变模型行为，说明至少部分可识别表示不是纯观察相关量。

### 推理可由多条路径并行支持

具体案例显示记忆、算法、格式、规划和校验可以并行；不能从输出正确性反推唯一算法。

### 自回归输出形成反馈

所选 token 进入下一步上下文，首 token 和结构性前缀可显著改变后续生成。

## 7.4 只在限定范围内成立的结论

### Induction heads 与 in-context learning

小型 attention-only 模型中有较强机制证据；对大模型“多数 ICL 都由 induction heads 实现”的说法证据更间接，不能作为已完成的统一理论。

### SAE 特征的单义性

许多特征比神经元更易解释，并可有因果效应；但 feature splitting、coverage gap、误差项与多义性仍存在。

### Attribution graph 的解释力

它能揭示并验证局部机制，也会失败或遗漏。工具产生的图不是自动真相。

### 低维拒绝方向

在某些模型中可以强烈调制拒绝；不代表风险识别、安全策略和所有模型都由唯一方向实现。

### Global workspace / J-space

所研究模型中存在更可报告、可控制和可复用的表示子空间；这是一种功能结构证据，不是意识结论。

### Emotion concepts

特定模型中提取的情绪概念方向能预测并因果影响行为；研究明确不等同于模型具有主观情绪体验。

### Interference weights

玩具模型和一层 transformer 中得到实证；规模化到前沿多层模型仍是开放问题。

## 7.5 不应接受的过强表述

| 过强表述 | 更准确的改写 |
|---|---|
| 某 token 激活了某个参数 | 该 token 改变源表示，使通过固定参数的贡献发生变化 |
| 大权重就是重要回路 | 需测当前激活、有效性、损失作用和干预效应 |
| attention 权重大就是模型依赖它 | 需同时看 QK 原因、OV 内容、下游传播和消融 |
| probe 解码出危险性，所以模型用它拒绝 | 只证明危险信息可解码；还需行为干预 |
| CoT 就是模型真实思维 | CoT 是可能忠实也可能合理化的输出通道 |
| 一个成功越狱证明安全特征消失 | 可能是识别延迟、路由、竞争或轨迹问题 |
| SAE 找到了模型真正的全部概念 | SAE 是带重建误差和超参数依赖的近似分解 |
| 模型会描述激活，所以有自我意识 | 可报告内部信息不等于主观意识 |
| 一个 Claude 案例就是所有 LLM 定律 | 结论需限定模型、版本、任务和方法 |

## 7.6 研究更新与正式论文

Transformer Circuits 时间线混合了：

- 长篇研究论文；
- 月度/短期 research update；
- 工具和基础设施；
- 跨站发布；
- 观点性文章；
- 玩具模型与练习。

月度更新多次明确要求按“实验室会议中的初步想法”理解。仓库目录通过 `status` 字段保留这种差异，避免把所有条目等权引用。

## 7.7 方法特有的误差

### Feature visualization

top examples 可能窄化含义；人工标签可能遗漏低激活语义。

### Probe

可解码不等于被使用；高容量 probe 可学习标签。

### Steering

强干预可能离开自然分布，并引发副作用。

### Ablation

置零可能是不自然状态；冗余路径可掩盖必要性。

### Patching

恢复结果可表明信息位置，但不一定恢复原始算法。

### Attribution

局部线性化、冻结 attention、误差节点和 replacement model 都会产生遗漏。

### NLA / activation oracle

语言化模型可能额外推断、幻觉、压缩或使用隐蔽编码。

### 模型行为 API

服务端版本、外部安全过滤、采样和系统模板可能造成不可见变化。

## 7.8 仓库主张登记

| 主张 | 当前等级 | 依据 | 下一步 |
|---|---:|---|---|
| 固定权重下不同输入产生不同激活与路径 | E4/基础架构事实 | Transformer 方程、干预研究 | 扩展到具体模型图谱 |
| 权重大小不等于功能重要性 | E4（小模型范围） | interference-weight 实验 | 多层/前沿模型复现 |
| token 概率变化可通过回填放大为轨迹差异 | E4/架构事实 | 自回归定义、前缀干预 | 大规模量化边界 |
| 推理是多路径条件计算 | E3–E4（案例范围） | Circuit Tracing / attention 案例 | 跨任务自动发现 |
| 有害性识别、拒绝状态和行为可分离 | E2–E4（模型相关） | 安全特征与局部回路案例 | 统一跨模型实验 |
| prompt injection 是数据/控制和权限分离问题 | E1–E3 | agent 行为与角色表征研究 | 外部强制权限基准 |
| 存在唯一、完整、普适的大模型特征基底 | 未支持 | 当前方法不唯一 | 理论与可识别性研究 |
| 当前方法可完整解释前沿模型 | 未支持 | 覆盖、误差和规模限制 | 自动化、分层与全局回路 |

## 7.9 核心来源

- [Reflections on Qualitative Research](https://transformer-circuits.pub/2024/qualitative-essay/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html)
- [Characterizing Interference Weights](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
