# 第 8 章｜综合项目：把一个直觉变成可证伪实验

## 学完你应该能

- 把模糊的大模型说法改写为明确机制命题；
- 指定对象、范围、干预、指标、对照和反证条件；
- 为结果设置正确证据等级；
- 写出一份别人可以复现、也可以推翻的实验报告。

## 核心模型

一个合格的机制项目至少包含：

```text
Claim      你究竟声称什么？
Object     参数、激活、特征、头、路径、logit 还是行为？
Scope      哪个模型、任务、输入分布和位置？
Prediction 干预后哪个量应朝哪个方向变化？
Controls   正对照和负对照是什么？
Falsifier  什么结果会削弱或推翻命题？
Boundary   即使成功，也不能推出什么？
```

## 逐步理解

### 1. 从坏问题开始

坏问题：

> 换行为什么会让模型行为改变？

它同时混合 tokenizer、位置、语义、Attention、策略和行为，也预设了原因。

改写为可检验问题：

> 对固定模型和成对输入，仅增加一个换行时，tokenization、最终位置隐藏状态、指定层 Attention 和目标 logit difference 分别怎样变化？在控制序列长度和语义改写后，哪些效应仍存在？

### 2. 分解假设

可以拆成：

- H1：换行改变 token 序列；
- H2：token 差异导致某层状态改变；
- H3：该状态对目标 logit 具有因果作用；
- H4：效应跨模板和模型稳定；
- H5：行为变化由同一中介解释。

H1 是观测，H3 需要 patching，H4 需要复现，H5 需要中介与替代解释比较。不要一次实验就跳到 H5。

### 3. 设计对照

至少考虑：

- **正对照**：已知应产生效应的干预；
- **随机对照**：等范数随机方向或随机位置；
- **错误层/位置**：检验空间特异性；
- **表面形式对照**：同长度但不同语义；
- **语义对照**：同语义但不同 tokenization；
- **反向干预**：clean→corrupted 与 corrupted→clean；
- **剂量响应**：干预强度是否呈预期变化；
- **跨模板复现**：避免单个 prompt 故事。

### 4. 预先写指标

不要在看完结果后选择最漂亮的图。提前写下目标 token 或 logit difference、层/位置/头、距离或恢复指标、样本数与 seed、聚合方式和置信区间、多重比较修正，以及成功、失败与不确定阈值。

### 5. 诚实报告不确定结果

实验状态至少区分：

```text
pass / supported
fail / falsified
inconclusive
skipped
error
```

缺依赖不是理论失败；代码崩溃不是理论被证伪；一次通过也不是普遍定律。

## 动手验证

选择一个方向：输入格式、前缀反馈、probe 反例、Attention 路由或安全代理。先复制实验模板：

```text
题目：
精确命题：
对象与范围：
基线：
干预：
保持不变的量：
正对照：
负对照：
主要指标：
反证条件：
最大允许结论：
禁止外推：
```

再运行最接近的现有实验作为基线：

```bash
llm-theory-lab list
llm-theory-lab explain C08
llm-theory-lab run-toy --ids C08
```

## 常见误区

**“数据越多就越因果。”** 大样本相关仍然是相关。

**“显著性就是重要性。”** 统计显著不等于效应大、机制唯一或跨分布稳定。

**“失败样本可以删掉，因为它们不符合机制。”** 失败样本往往决定机制范围。

**“可视化足够直观，不需要反证条件。”** 越直观的故事越需要负对照。

## 自测

1. 把“模型有一个拒绝方向”改写成三个强度不同的可检验命题。
2. 为什么跨模板成功仍不等于跨模型机制相同？
3. 一个 patching 热图出现高峰，至少需要哪些负对照？
4. 你会怎样区分“不确定结果”和“理论被反驳”？

## 来源

- [Reflections on Qualitative Research](https://transformer-circuits.pub/2024/qualitative-essay/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html)
- [Automated Auditing](https://alignment.anthropic.com/2025/automated-auditing/)
