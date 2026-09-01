# 14｜理论如何变成代码实验

> 理论不是“听起来合理的解释”。一个机制命题必须明确对象、作用范围、干预、指标、对照和反证条件。本章把核心理论逐条映射到 [`../code/`](../code/) 实验子项目。

# 14.1 证据阶梯

```text
L0 数学恒等式或精确程序性质
L1 透明玩具模型、结构反例、完全可知因果图
L2 开放模型观察或上下文反事实
L3 开放模型内部干预
L4 跨模板、任务、checkpoint 和模型的稳定回路证据
L5 产生新反事实预测并被独立复现的机制理论
```

“实验通过”只表示该实验预先定义的检查通过。它不自动把 L1 结果升级成 L4 或 L5。

# 14.2 C01｜权重、激活与有效性

**理论命题**

$$
c_{ij}(x)=w_{ij}a_j(x).
$$

单个连接的当前贡献依赖固定权重与源激活。权重大小、当前贡献、分布有效性和因果帮助性不是同一个量。

**代码**

```text
code/src/llm_theory_lab/experiments/weights.py
```

**实验设计**

- 构造一个很大但罕见、很弱激活的连接；
- 构造一个较小但经常激活的连接；
- 比较当前贡献与 $E[(wa)^2]$ 玩具有效性代理。

**反证条件**

在这个明确分布中，若大权重不论源激活如何都必然具有更大当前贡献和有效性，则命题失败。

**允许结论**

这是一个数学结构反例，足以否定“按绝对权重排序就是功能重要性排序”的一般推理。

**禁止结论**

不能由这个玩具代理估计真实大模型中有多少 interference weights。

# 14.3 C02｜温度与 token 赔率

**理论命题**

对 $T>0$：

$$
\log\frac{p_i}{p_j}
=
\frac{z_i-z_j}{T}.
$$

相对 logit 增加 $\Delta z$ 后，赔率乘以：

$$
e^{\Delta z/T}.
$$

**代码**

```text
code/src/llm_theory_lab/experiments/temperature.py
```

**实验设计**

- 对多个温度直接计算 softmax；
- 比较概率赔率与解析式；
- 验证 $T=1$、$\Delta z=1$ 时赔率乘数为 $e$。

**反证条件**

数值 softmax 系统性偏离解析恒等式。

**允许结论**

这是精确数学关系。

**禁止结论**

不能只凭赔率变化断言某 token 一定被采样，也不能把 API 的 `temperature=0` 代入该公式。

# 14.4 C03｜固定权重下的输入条件计算

**理论命题**

$$
h=f_\theta(x),
$$

即使 $\theta$ 不变，不同 $x$ 也会产生不同激活、路由和输出。

**代码**

```text
code/src/llm_theory_lab/experiments/conditional.py
```

**实验设计**

同一固定 ReLU 网络接收任务证据、策略证据和不确定性三种状态，检查特征模式和 top token 是否分别变化。

**反证条件**

固定权重网络对不同输入无法产生不同激活或输出。

**理论意义**

它纠正“input 要影响行为就必须改参数”的错误。

# 14.5 C04｜Attention 是条件路由，不是静态关注标签

**理论命题**

$$
\alpha_{ij}
=
\operatorname{softmax}_j
\left(\frac{q_i^\top k_j}{\sqrt d}\right),
$$

$$
o_i=\sum_j\alpha_{ij}v_jW_O.
$$

输入扰动可以通过 QK 改变读取位置，并通过 OV 改变写回内容。

**代码**

```text
code/src/llm_theory_lab/experiments/attention.py
```

**实验设计**

固定全部矩阵，只改变一个 token 在 key-relevant 方向上的表示，记录最高注意力位置和聚合输出。

**反证条件**

该 key 扰动不改变注意力分布或写回向量。

**禁止结论**

单头演示不能说明真实模型中的某个头具有唯一、全分布不变的标签。

# 14.6 C05｜首 token 与自回归轨迹

**理论命题**

$$
s_{t+1}=F_\theta(s_t,y_t).
$$

在权重固定时，不同 $y_t$ 仍可改变未来状态。

**代码**

```text
code/src/llm_theory_lab/experiments/feedback.py
```

**实验设计**

从同一初始状态出发，只强制第一个 token 为 A 或 B，后续全部 greedy，比较序列与最终状态。

**反证条件**

两条运行在首 token 不同后仍具有完全相同后续状态与序列。

**开放模型延伸**

`M02` 把两个替代前缀追加到真实 tokenizer 上下文，比较下一步完整分布。

# 14.7 C06｜Superposition 与干扰

**理论命题**

$$
h=Dx,
\qquad F>d.
$$

稀疏时，多个特征可以共享较少维度；非正交方向在共激活时会产生干扰。

**代码**

```text
code/src/llm_theory_lab/experiments/superposition.py
```

**实验设计**

- 把五个特征方向放入二维空间；
- 单特征激活时用最近方向解码；
- 两特征共激活时比较 top-2 解码准确率。

**反证条件**

$F>d$ 时单特征完全不可识别，或者共激活永远不增加混淆。

**禁止结论**

人工正五边形不证明真实 LLM 恰好使用相同几何。

# 14.8 C07｜Probe 不等于因果使用

**理论命题**

存在一个表示 $h$，变量 $u$ 可由 probe 从 $h$ 解码，但模型输出 $g(h)$ 完全不依赖 $u$。

**代码**

```text
code/src/llm_theory_lab/experiments/probe_causality.py
```

**实验设计**

- 隐藏状态包含一个真正影响输出的变量和一个未被输出头读取的变量；
- 线性 probe 高准确率解码未使用变量；
- 消融它后输出不变；
- 消融真正因果变量作为正对照。

**反证条件**

任何可被高准确率 probe 解码的变量，消融后都必然改变输出。

**意义**

这是方法论中的关键反例：信息存在、相关性、被使用和因果必要性必须分开。

# 14.9 C08｜Activation patching

**理论命题**

若中间状态 $m$ 是 clean 与 corrupted 输出差异的候选中介，则将 $m_{clean}$ 替换到 corrupted 运行可能恢复目标指标。

恢复比例：

$$
R=
\frac{M_{patched}-M_{corrupted}}
     {M_{clean}-M_{corrupted}}.
$$

**代码**

```text
code/src/llm_theory_lab/experiments/patching.py
```

**实验设计**

- patch 真正因果维度；
- patch 同规模无关维度作为负对照；
- 比较恢复比例。

**反证条件**

候选中介与无关维度的 patch 效应相同。

**开放模型延伸**

`M03` 对 GPT-2 风格模型逐层 patch 最终位置 residual block 输出，扫描目标 token logit 改变。

**边界**

成功 patch 主要说明状态足以传递效应；不自动证明唯一性、自然性或完整机制。

# 14.10 C09｜识别、策略与行为分离

**理论命题**

安全或策略链条至少可以分成：

```text
识别表示
→ 策略状态
→ 输出动作
```

前一变量存在不逻辑蕴含后一变量一定形成或获胜。

**代码**

```text
code/src/llm_theory_lab/experiments/safety_routing.py
```

**实验设计**

使用无害的“受限资源访问”代理：

- restricted-category 检测维度为高；
- 输出头不直接读取该检测维度；
- completion state 使 PROCEED 获胜；
- patch decline-policy state 后动作翻转为 DECLINE。

**反证条件**

检测维度存在时必然直接决定输出动作，策略中介没有独立作用。

**安全边界**

实验不含真实越狱载荷，也不搜索绕过字符串。它只检验机制分层。

# 14.11 M01｜开放模型 tokenization 与格式敏感性

**代码**

```text
code/src/llm_theory_lab/experiments/hf_models.py
```

**记录内容**

- token IDs 与 token 文本；
- next-token Jensen–Shannon divergence；
- 最终位置隐藏状态逐层 cosine similarity；
- 最后 query 的 attention 差异；
- top-k token。

**正确解释**

格式变化与分布变化共现。

**错误解释**

“已经证明某个换行特征是唯一因果机制。”

进一步需要长度匹配对照、位置匹配、patching 和跨 prompt 复现。

# 14.12 M02｜开放模型前缀反馈

**操作**

把两个替代前缀分别写入相同 base prompt，比较下一 token 完整分布。

**允许结论**

在该模型和上下文中，已写入前缀改变了下一步条件分布。

**禁止结论**

不能说明两个前缀在自然生成中的首步概率相同，也不能由一步 JS divergence 推断全部长期语义后果。

# 14.13 M03｜开放模型逐层 patch scan

**操作**

- clean prompt 产生目标 token；
- corrupted prompt 改变事实条件；
- 对每个 GPT-2 block，把 clean 最终位置 residual 输出 patch 到 corrupted 运行；
- 测量目标 token logit 改善。

**需要的对照**

1. clean/corrupted 对调；
2. 随机等范数向量；
3. 非最终位置；
4. 无关目标 token；
5. 多组事实和模板；
6. patch 单头、MLP 或特征，而不只是整条 residual。

# 14.14 从当前代码到真正研究项目

当前实验代码已经建立正确的研究骨架，但要升级为严谨论文，需要按以下顺序扩展：

```text
透明 C 系列验证概念
→ M 系列确认开放模型中存在相似现象
→ 建立成百上千个匹配样本
→ 自动保存 token、激活、logits 和环境元数据
→ 增加多层/多头/多特征干预
→ 加随机与语义负对照
→ 跨 checkpoint、模型家族和语言复现
→ 预测未见反事实
→ 独立代码实现复现
```

# 14.15 运行

```bash
cd code
pip install -e ".[dev]"
llm-theory-lab list
llm-theory-lab run-toy
pytest
```

开放模型：

```bash
pip install -e ".[all]"
llm-theory-lab hf-tokenization
llm-theory-lab hf-prefix
llm-theory-lab hf-patch
```

所有实验都输出 JSON 和 Markdown 报告，而不是只打印一个不可审计总分。
