# 第 5 章｜推理、中间状态与自回归反馈

## 学完你应该能

- 把“推理”解释为输入条件下的多路径计算，而不是神秘内心独白；
- 区分层内计算、跨 token 计算和外显 chain-of-thought；
- 解释为什么正确答案不证明模型使用了正确算法；
- 分析首 token、句法边界和已有前缀怎样改变后续轨迹。

## 核心模型

一次前向传播可在层维度形成中间状态：

$$
h^{(0)}\rightarrow h^{(1)}\rightarrow\cdots\rightarrow h^{(L)}.
$$

连续生成又把选出的 token 写回序列：

$$
y_t\sim p_\theta(\cdot\mid x,y_{<t}),
\qquad
p_{t+1}=p_\theta(\cdot\mid x,y_{<t},y_t).
$$

因此模型有两条串行计算轴：

```text
层轴：在一次 forward pass 内变换状态
序列轴：通过输出 token 把中间结果带到下一次 forward pass
```

## 逐步理解

### 1. 推理通常不是单一路径

同一个答案可能同时得到以下路径支持：

- 直接事实记忆；
- 语义相似模式；
- 局部启发式；
- 真正的中间变量计算；
- 任务格式和语法；
- 由 prompt 示例诱导的临时规则。

如果输出正确，只能说明这些贡献的合成使目标 token 获胜。要证明某条算法路径，需要中间状态预测和因果干预。

### 2. 隐式中间状态不必写成文字

两跳问题可以在中层先形成中间实体，再由后层读取并完成第二跳。押韵生成可以提前表示计划中的句末词，再让当前词选择服从这个计划。模型不必把这些状态先输出为自然语言。

### 3. Chain-of-thought 是输出，不是透明日志

外显推理文字可能：

- 与内部路径一致；
- 只报告一部分；
- 在答案已形成后进行解释；
- 受用户暗示影响，反向构造合理故事；
- 引入新的 token，实际改变后续计算。

所以 CoT 既可能是报告，也可能是工作区，还可能是事后叙事。不能只读文字就确定内部机制。

### 4. 首 token 会形成生成惯性

假设初始状态对 `ANSWER` 与 `REFUSE` 的 logits 接近。若第一步选中 `ANSWER`，后续上下文中会出现回答式语法、任务承诺和内容词；若选中 `REFUSE`，后续更容易接拒绝理由和替代建议。

```text
微小首步差异
→ 不同 token 写回
→ 不同下一步激活
→ 更偏向延续当前模式
→ 轨迹进一步分离
```

### 5. 句法边界可能改变策略切换难度

模型已经进入一个列表、代码块或句子结构后，局部语法对下一 token 有强约束。某个安全或纠错信号即使变强，也可能要等到句号、换行或新段落才更容易改变生成模式。

## 动手验证

```bash
llm-theory-lab explain C05
llm-theory-lab run-toy --ids C05
python examples/05_autoregressive_feedback.py
```

实验保持初态和全部权重不变，只强制不同首 token。观察两条序列和最终状态距离。然后修改反馈矩阵，尝试构造：会收敛回同一轨迹、会交替振荡、以及对首 token 极端敏感的系统。

## 常见误区

**“模型答对了，所以它会推理。”** 还要问它使用了什么机制、是否跨模板稳定、干预中间变量后是否按预测变化。

**“CoT 就是模型真实思维。”** CoT 是生成行为的一部分，不是未经加工的内部记录。

**“第一个 token 只是表面措辞。”** 它立即成为后续输入，常常决定响应模式。

**“轨迹差异都是采样噪声。”** 即使采用确定性 greedy，强制不同前缀也能造成条件分布分叉。

## 自测

1. 为什么输出更多 token 有时能增加模型的有效串行计算深度？
2. 如何设计实验区分“两跳计算”与“直接记忆答案”？
3. CoT 与内部机制一致时，还需要什么因果证据？
4. 为什么句法边界可能成为策略切换的关键位置？

## 来源

- [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html)
- [Verbalizable Representations Form a Global Workspace](https://transformer-circuits.pub/2026/workspace/index.html)
