# 大模型理论：从权重、输入到回路、推理与安全

> **研究快照：2026-09-01**  
> 本仓库把 [Transformer Circuits Thread](https://transformer-circuits.pub/) 官网时间线中的 56 条来源，整理成一套中文、可检验、有证据边界的大模型理论，并配套独立的 [`code/`](code/) 实验子项目。

旧的“引导式提问偏见打分”、Gemini 自评、旧 prompts 和旧实验代码已经从当前分支移除。旧方法只能看到输出相关性，不能回答模型内部究竟发生了什么；当前仓库采用：

```text
清晰理论
→ 明确命题
→ 透明玩具实验
→ 开放模型观测与内部干预
→ 正负对照
→ 证据分级与反证条件
```

# 先读这一句话

> **训练数据分布塑造权重；权重规定模型可能怎样计算；输入决定本次实际激活哪些表示和路径；这些路径共同形成 logits；解码选出的 token 写回上下文后，又改变下一步计算。**

完整因果链：

```text
训练数据、损失与优化器
          │
          ▼
      固定参数 θ
          │
字符串 → tokenizer → token / position / role 表示
          │
          ▼
动态激活、特征、attention 路由和局部计算图
          │
          ▼
        logits
          │
  softmax / decoding
          │
          ▼
      输出 token
          │
          └────写回上下文────> 下一步激活与新分布
```

# 必须分开的概念

| 概念 | 含义 | 标准推理时是否改变 |
|---|---|---:|
| 参数/权重 | 训练后保存的连接规则 | 通常不改变 |
| 激活 | 当前 input 经过模型时的动态数值状态 | 改变 |
| 特征 | 对可重复语义或计算变量的分析描述 | 是否激活随输入改变 |
| 回路 | 多个模块和表示之间的计算路径 | 实际参与路径随输入改变 |
| logits | 每个候选 token 的未归一化分数 | 每一步改变 |
| token 概率 | logits 经温度和 softmax 后的条件分布 | 每一步改变 |
| 生成轨迹 | 已选 token 反复写回形成的路径 | 持续演化 |

所以更准确的说法不是“某个 token 激活了某个参数”，而是：

> 某个 token 改变了当前表示和源激活，使固定参数所定义的某些连接、特征和回路在这次前向传播中产生了不同贡献。

# 最清晰的阅读入口

第一次系统理解时，按这个顺序：

```text
13 第一性原理教程
  → 14 理论如何变成代码实验
  → 09 统一综合
  → 11 经典机制案例
  → 12 方法与解释矩阵
  → 10 全部来源逐条精华
```

| 路径 | 内容 |
|---|---|
| [`docs/13_FIRST_PRINCIPLES_TUTORIAL.md`](docs/13_FIRST_PRINCIPLES_TUTORIAL.md) | 从 tokenization、forward pass、QK/OV、MLP、logits、推理和安全开始的清晰教程 |
| [`docs/14_THEORY_TO_CODE_LAB.md`](docs/14_THEORY_TO_CODE_LAB.md) | 每条理论命题对应的实验、指标、对照、反证条件和代码路径 |
| [`code/README.md`](code/README.md) | 独立实验代码库的安装、运行和解释规范 |
| [`docs/09_UNIFIED_SYNTHESIS.md`](docs/09_UNIFIED_SYNTHESIS.md) | 把整个 Transformer Circuits thread 融成统一理论 |
| [`docs/10_SOURCE_BY_SOURCE_DIGEST.md`](docs/10_SOURCE_BY_SOURCE_DIGEST.md) | 官网 56 条来源逐条整理：问题、方法、发现、位置与边界 |
| [`docs/11_CANONICAL_CASE_STUDIES.md`](docs/11_CANONICAL_CASE_STUDIES.md) | induction、两跳推理、规划、幻觉、越狱、persona、流形等机制案例 |
| [`docs/12_METHODS_AND_INTERPRETATION_MATRIX.md`](docs/12_METHODS_AND_INTERPRETATION_MATRIX.md) | 权重、probe、SAE、CLT、patching、QK attribution、NLA 等方法能证明什么 |

# 基础专题章节

| 路径 | 内容 |
|---|---|
| [`docs/00_THEORY_MAP.md`](docs/00_THEORY_MAP.md) | 全局理论图和分析层级 |
| [`docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md`](docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md) | 权重、激活、token、logits、温度和三种时间尺度 |
| [`docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md`](docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md) | 特征、superposition、SAE、crosscoder、流形和干扰权重 |
| [`docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md`](docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md) | residual stream、QK/OV、路径组合和归因图 |
| [`docs/04_REASONING_CONTEXT_AND_GENERATION.md`](docs/04_REASONING_CONTEXT_AND_GENERATION.md) | ICL、推理、规划、CoT 忠实性、序列反馈和 J-space |
| [`docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md`](docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md) | 安全识别、拒绝、越狱、过度拒绝、角色和权限 |
| [`docs/06_METHODS_AND_CAUSAL_VALIDATION.md`](docs/06_METHODS_AND_CAUSAL_VALIDATION.md) | 从观察、probe 到 ablation、steering 和 patching |
| [`docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md`](docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md) | E0–E5 证据等级和不可越界的主张 |
| [`docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md`](docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md) | 开放问题与研究路线 |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | 中英文术语表 |

# 理论的最小数学骨架

## 1. 固定权重与动态激活

线性层：

$$
y=Wx+b.
$$

一条连接的当前直接贡献：

$$
c_{ij}(x)=w_{ij}x_j.
$$

所以必须区分：

```text
权重大小
→ 当前贡献
→ 数据分布上的有效性
→ 对行为或损失的因果帮助性
```

大权重在源激活为零时贡献仍为零；大贡献也可能被后层抵消或由冗余路径替代。

## 2. Attention 的两个问题

$$
s_{ij}=\frac{q_i^\top k_j}{\sqrt{d_k}},
\qquad
\alpha_{ij}=\operatorname{softmax}_j(s_{ij}),
$$

$$
o_i=\sum_j\alpha_{ij}v_jW_O.
$$

- QK 决定为什么读取某个位置；
- OV 决定读取后写入什么；
- attention heatmap 不能单独解释完整机制。

## 3. Token 概率与温度

对正温度 $T>0$：

$$
p_i=\frac{e^{z_i/T}}{\sum_j e^{z_j/T}},
$$

$$
\log\frac{p_i}{p_j}=\frac{z_i-z_j}{T}.
$$

相对 logit 增加 $\Delta z$，赔率乘以：

$$
e^{\Delta z/T}.
$$

数学上不能把 $T=0$ 代入 softmax；许多 API 用 `temperature=0` 表示 greedy/argmax。

## 4. 自回归反馈

$$
y_t\sim p_\theta(\cdot\mid x,y_{<t}),
$$

$$
p_{t+1}=p_\theta(\cdot\mid x,y_{<t},y_t).
$$

首 token 不是结果末端，而是下一轮强输入。回答式、拒绝式、代码式或列表式开头会改变后续语法、自洽性和任务完成路径。

# 怎样理解大模型推理

推理不是一条必然可读的隐藏独白，而是当前上下文下的条件计算：

```text
层内形成中间表示
+ attention 从历史位置读取
+ 多条记忆、启发式和算法路径并行贡献
+ 必要时把中间结果写成 token 继续计算
```

因此：

- 一次 forward pass 内可以有隐式中间步骤；
- chain-of-thought 可以扩展序列维度的计算，但不保证忠实；
- 相同答案可能由不同机制支持；
- 正确输出不证明模型采用了理想算法；
- probe 能读出信息不证明模型实际使用它。

# 怎样理解越狱和 prompt injection

至少把安全链条分成：

```text
整体语义识别
→ 危险性、角色和权限表示
→ 拒绝或安全重定向策略状态
→ 输出 token 竞争
→ 生成前缀反馈
```

越狱并不必然意味着“安全知识消失”或“参数被修改”。可能发生的是：

- 整体危险语义形成太晚；
- 角色或权限被错误判断；
- 危险性可被解码，但没有形成拒绝状态；
- 拒绝状态存在，但没有被下游读取；
- 任务完成、语法或 persona 路径先赢得首 token；
- 已生成前缀通过自回归反馈维持当前轨迹。

同一框架也解释过度拒绝：粗糙危险特征或策略路径过强，压过精细无害语义。

仓库的安全实验只使用无害访问控制代理，不内置真实越狱载荷或绕过搜索。

# 独立实验代码库

[`code/`](code/) 是可单独安装的 Python 项目：

```bash
cd code
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

llm-theory-lab list
llm-theory-lab run-toy
pytest
```

透明实验：

```text
C01 权重 × 激活与分布有效性
C02 温度与赔率恒等式
C03 固定权重下的输入条件计算
C04 QK 路由与 OV 写回
C05 首 token 反馈和轨迹分叉
C06 sparse superposition 与干扰
C07 probe 可解码但不被使用的反例
C08 activation patching
C09 识别—策略—行为分离的无害代理
```

安装开放模型依赖：

```bash
pip install -e ".[all]"
llm-theory-lab hf-tokenization
llm-theory-lab hf-prefix
llm-theory-lab hf-patch
```

开放模型实验默认标记为 `observational`，避免把一次运行冒充普遍定律。每次运行会输出完整 JSON 和 Markdown 报告，而不是一个不可审计总分。

# 来源覆盖与自动校验

| 路径 | 内容 |
|---|---|
| [`docs/TRANSFORMER_CIRCUITS_INDEX.md`](docs/TRANSFORMER_CIRCUITS_INDEX.md) | 官网时间线和快速索引 |
| [`sources/transformer_circuits_catalog.csv`](sources/transformer_circuits_catalog.csv) | 56 条机器可读来源目录 |
| [`scripts/validate_catalog.py`](scripts/validate_catalog.py) | 检查目录完整性 |
| [`scripts/validate_source_digest.py`](scripts/validate_source_digest.py) | 检查逐条精华没有漏掉来源 |
| [`scripts/normalize_markdown_math.py`](scripts/normalize_markdown_math.py) | 检查 GitHub 数学公式格式 |

CI 分成两个独立任务：

```text
Theory checks：公式、来源目录、逐条精华覆盖
Code lab：安装 code 子项目、运行全部测试和 C01–C09
```

# 研究边界

本仓库建立的是当前证据支持下的工作理论，不是宣称已经读出了完整大模型源代码。尤其要保留：

- SAE、crosscoder、transcoder、CLT 和 NLA 都是近似分析接口；
- attribution graph 可能遗漏误差节点、非线性和替代路径；
- 月度研究更新与完整论文的证据强度不同；
- 小模型、单层模型或单一 Claude/GPT checkpoint 的结果不能无条件外推；
- 能语言化或报告内部状态不等于意识；
- 情绪概念能因果影响行为不等于存在主观感受；
- 一个实验的 `pass` 只表示预注册检查通过，不表示理论已跨模型成立。

引用科学结论时，请优先引用原始 Transformer Circuits 页面；引用本仓库时，应说明引用的是中文综合、代码实现或实验框架。
