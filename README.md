# 大模型理论：从权重、激活到回路、推理与安全

> **研究快照：2026-09-01**  
> 本仓库是对 [Transformer Circuits Thread](https://transformer-circuits.pub/) 的中文、理论化、可检验的综合整理。它不是网页镜像，也不复制原文；目标是把分散的研究结果组织成一套能指导阅读、建模与实验的统一框架。

仓库沿用旧项目的 GitHub 地址，但旧的“引导式提问偏见打分”研究、Gemini API 自评、旧 prompts 数据和旧实验代码已经全部移除。原方法只能观察输出相关性，却把黑盒评分过早解释成内部机制；本版本改为 **理论主线 + 证据等级 + 因果验证 + 无害玩具实验**。

## 核心命题

```text
训练数据分布 ──梯度统计──> 权重 θ
                                │
输入 token + 上下文 ────────────┼──> 激活 / 注意力路由 / 临时计算图
                                │                     │
                                └────────────────────> logits → token 分布
                                                              │
                                                     选中 token 并回填上下文
                                                              │
                                                              └──> 下一步激活与生成轨迹
```

一句话概括：

> **权重规定模型可能怎样计算；输入决定这一次实际激活哪些表示和路径；解码决定哪种输出倾向暂时胜出；生成出的 token 又成为下一轮输入。**

这套框架要求始终区分：

- 参数、激活、特征、注意力模式和输出概率；
- 权重大小、当前贡献、数据分布上的有效性和真正的因果重要性；
- 训练分布偏置、prompt 条件偏置、解码偏置与自回归轨迹偏置；
- 可解码信息、模型实际使用的信息和经干预验证的机制；
- 有害性识别、拒绝状态与最终行为。

## 仓库结构

| 路径 | 内容 |
|---|---|
| [`docs/00_THEORY_MAP.md`](docs/00_THEORY_MAP.md) | 全局理论图、层级关系与阅读入口 |
| [`docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md`](docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md) | 权重、激活、token、logits 与三种时间尺度 |
| [`docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md`](docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md) | 特征、叠加、可解释基底、SAE、流形与干扰权重 |
| [`docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md`](docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md) | residual stream、QK/OV、回路、归因图和条件计算 |
| [`docs/04_REASONING_CONTEXT_AND_GENERATION.md`](docs/04_REASONING_CONTEXT_AND_GENERATION.md) | 上下文学习、推理、规划、CoT 忠实性和生成反馈 |
| [`docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md`](docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md) | 越狱、过度拒绝、角色混淆、prompt injection 的机制框架 |
| [`docs/06_METHODS_AND_CAUSAL_VALIDATION.md`](docs/06_METHODS_AND_CAUSAL_VALIDATION.md) | 从观察、probe 到 ablation、patching 与跨分布复现 |
| [`docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md`](docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md) | E0–E5 证据等级、已知结论和不可越界的主张 |
| [`docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md`](docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md) | 开放问题和可执行研究路线 |
| [`docs/TRANSFORMER_CIRCUITS_INDEX.md`](docs/TRANSFORMER_CIRCUITS_INDEX.md) | 官网时间线上全部条目的中文索引 |
| [`sources/transformer_circuits_catalog.csv`](sources/transformer_circuits_catalog.csv) | 可机器读取的完整目录与分类 |
| [`src/llm_theory/`](src/llm_theory/) | 固定权重、条件激活、logit 赔率与轨迹反馈的玩具模型 |

## 建议阅读路径

```text
01 参数与激活
  → 02 表征、叠加与几何
  → 03 回路与注意力
  → 04 推理与生成
  → 05 安全失配
  → 06 因果验证
  → 07 证据边界
  → 08 开放问题
```

首次接触机制可解释性时，可同步阅读：

```text
Mathematical Framework
  → Induction Heads
  → Toy Models of Superposition
  → Towards / Scaling Monosemanticity
  → Circuit Tracing
  → On the Biology of a Large Language Model
  → 2025–2026 的 attention、geometry、workspace、NLA 与 interference weights
```

## 可运行的无害玩具实验

这些实验不声称重现真实前沿模型；它们只把概念变成可以检查的最小数学对象。

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python scripts/validate_catalog.py
python scripts/run_toy_lab.py
pytest
```

实验演示四件事：

1. 权重固定时，不同输入仍会选择不同特征与输出路径；
2. 单个连接的当前贡献取决于“权重 × 源激活”；
3. 相对 logit 的小变化会指数级改变 token 赔率；
4. 不同首 token 被写回上下文后，会产生分叉的自回归轨迹。

## 研究原则

1. **先定义对象，再讨论机制。** 不把参数、神经元、特征、方向、头和行为混为一谈。
2. **先做对照，再看故事。** 解释必须经消融、替换、激活修补或定向干预验证。
3. **局部解释不冒充全局理论。** 单个 prompt 的 attribution graph 是条件计算的局部近似。
4. **可解码不等于被使用。** probe 只能证明信息存在，不能自动证明它控制输出。
5. **把不确定性写进结论。** 月度更新、工具说明、玩具模型和正式论文使用不同证据标签。
6. **安全研究采用无害代理。** 仓库不收录可直接复用的越狱载荷或危险操作步骤。

## 范围与边界

本仓库覆盖 Transformer Circuits 官网截至 2026-09-01 可见的时间线条目，并把它们映射到一套统一理论。所谓“覆盖”指：建立完整索引、提取核心问题、连接概念与标注证据状态；并不意味着逐句复刻，也不意味着相关研究已经构成封闭、完备、获得共识的“大模型定律”。

尤其需要保留以下限制：

- SAE、crosscoder、transcoder 和 NLA 都是近似接口，不是模型内部唯一正确的坐标系；
- attribution graph 可能遗漏误差节点、非线性和替代路径；
- 2025–2026 年若干页面明确属于研究更新或初步结果；
- 小模型、单层模型和特定 Claude 版本上的结果不能无条件外推到所有模型；
- “能够语言化内部状态”不等于意识，“情绪概念影响行为”不等于主观体验。

## 版权与归属

理论整理与代码采用 MIT License。原始论文、交互图和研究页面的版权归各自作者及发布方所有。引用研究结论时，请优先引用 [`docs/TRANSFORMER_CIRCUITS_INDEX.md`](docs/TRANSFORMER_CIRCUITS_INDEX.md) 中对应的原始页面，而不是只引用本仓库。
