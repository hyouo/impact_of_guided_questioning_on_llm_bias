# 大模型理论：从权重、激活到回路、推理与安全

> **研究快照：2026-09-01**  
> 本仓库是对 [Transformer Circuits Thread](https://transformer-circuits.pub/) 的中文、理论化、可检验综合。它不是网页镜像或逐句翻译，而是把官网时间线中的 **56 条来源**全部放进同一套因果框架，并明确区分论文、研究更新、工具、观点和基础设施。

旧的“引导式提问偏见打分”研究、Gemini 自评、旧 prompts 和旧实验代码已经从当前分支移除。原方法只能观察输出相关性，无法说明内部机制；现在的仓库以 **理论综合、逐条来源精华、经典案例、方法边界、因果验证和无害玩具实验**为中心。

## 一句话理论

```text
训练数据分布 ──梯度统计──> 固定权重 θ
                                  │
输入 token、位置、角色和历史 ─────┼──> 动态激活与注意力路由
                                  │                 │
                                  └────────────────> logits → token 分布
                                                                  │
                                                        选中 token 并写回
                                                                  │
                                                                  └→ 下一步激活
```

> **权重规定模型可能怎样计算；输入决定这一次实际激活哪些表示和路径；解码决定哪种输出倾向暂时胜出；生成出的 token 又成为下一轮输入。**

由此必须始终区分：

- 参数、激活、特征、方向、子空间、流形、注意力头和行为；
- 权重大小、当前贡献、分布有效性和因果帮助性；
- 训练分布偏置、上下文条件偏置、解码偏置与自回归轨迹偏置；
- 可解码信息、模型自然使用的信息和经干预验证的机制；
- 有害性识别、拒绝策略、角色/权限判断与最终输出；
- 可读解释、替代模型拟合与原模型真实机制。

# 仓库阅读入口

## 深度综合

| 路径 | 作用 |
|---|---|
| [`docs/09_UNIFIED_SYNTHESIS.md`](docs/09_UNIFIED_SYNTHESIS.md) | 把全部 thread 融成一套从训练分布到行为的统一理论；建议首先精读 |
| [`docs/10_SOURCE_BY_SOURCE_DIGEST.md`](docs/10_SOURCE_BY_SOURCE_DIGEST.md) | 官网 56 条来源逐条整理：问题、方法、核心发现、理论位置、证据边界 |
| [`docs/11_CANONICAL_CASE_STUDIES.md`](docs/11_CANONICAL_CASE_STUDIES.md) | Induction、两跳推理、规划、幻觉、越狱、persona、流形等经典机制案例 |
| [`docs/12_METHODS_AND_INTERPRETATION_MATRIX.md`](docs/12_METHODS_AND_INTERPRETATION_MATRIX.md) | 权重、probe、SAE、CLT、patching、QK attribution、NLA 等方法能与不能证明什么 |

## 基础章节

| 路径 | 内容 |
|---|---|
| [`docs/00_THEORY_MAP.md`](docs/00_THEORY_MAP.md) | 全局理论图、分析层级与核心主线 |
| [`docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md`](docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md) | 权重、激活、token、logits、温度与三种时间尺度 |
| [`docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md`](docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md) | 特征、superposition、SAE、crosscoder、流形与干扰权重 |
| [`docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md`](docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md) | residual stream、QK/OV、路径组合、归因图 |
| [`docs/04_REASONING_CONTEXT_AND_GENERATION.md`](docs/04_REASONING_CONTEXT_AND_GENERATION.md) | ICL、推理、规划、CoT 忠实性、序列反馈与 J-space |
| [`docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md`](docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md) | 安全识别、拒绝、越狱、过度拒绝、角色混淆和系统边界 |
| [`docs/06_METHODS_AND_CAUSAL_VALIDATION.md`](docs/06_METHODS_AND_CAUSAL_VALIDATION.md) | 从观察、probe 到 ablation、steering、patching 与跨分布复现 |
| [`docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md`](docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md) | E0–E5 证据等级、成熟结论和不可越界主张 |
| [`docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md`](docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md) | 开放问题和可执行研究路线 |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | 中英文术语表 |

## 来源与机器校验

| 路径 | 内容 |
|---|---|
| [`docs/TRANSFORMER_CIRCUITS_INDEX.md`](docs/TRANSFORMER_CIRCUITS_INDEX.md) | 官网完整时间线与快速索引 |
| [`sources/transformer_circuits_catalog.csv`](sources/transformer_circuits_catalog.csv) | 56 条机器可读来源目录 |
| [`scripts/validate_source_digest.py`](scripts/validate_source_digest.py) | 保证逐条精华没有漏掉目录中的标题或网址 |
| [`scripts/normalize_markdown_math.py`](scripts/normalize_markdown_math.py) | 检查 GitHub 数学公式分隔符 |
| [`src/llm_theory/`](src/llm_theory/) | 固定权重、条件激活、logit 赔率与轨迹反馈的无害玩具模型 |

# 建议阅读顺序

第一次系统学习：

```text
09 统一综合
  → 01 参数、激活和 token
  → 02 表征、叠加和几何
  → 03 Attention 与回路
  → 04 推理和生成
  → 05 安全失配
  → 11 经典机制案例
  → 12 方法与解释矩阵
  → 10 逐条来源精华
```

按原始研究发展史阅读：

```text
Mathematical Framework
  → Induction Heads
  → Toy Models of Superposition
  → Towards Monosemanticity
  → Scaling Monosemanticity
  → Crosscoders / Model Diffing
  → Circuit Tracing / Biology
  → QK Attribution / Manifolds / MOLT
  → NLA / Introspection / Global Workspace
  → Interference Weights
```

# “全部整理”的覆盖标准

本仓库所说的“覆盖 Transformer Circuits 全部精华”具体意味着：

1. 官网首页截至快照日期可见的 56 条来源全部进入机器目录；
2. 每条来源在逐条精华中都有独立条目；
3. 每条都写明研究问题、方法、核心发现、理论位置和证据边界；
4. 正式论文、研究更新、工具和愿景使用不同证据标签；
5. 重要结论被重新组织进统一理论，而不是只保留时间线摘要；
6. 关键机制被转写为观察—机制—干预—边界的案例；
7. 每种分析工具明确写出“能证明什么”和“不能证明什么”；
8. CI 自动检查目录完整性、逐条覆盖和 Markdown 数学格式。

“覆盖”不意味着复制全文，也不意味着这些研究已经形成封闭、获得共识的最终大模型定律。原始页面中的交互图、方法细节和实验附录仍应直接阅读和引用。

# 可运行的无害玩具实验

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python scripts/normalize_markdown_math.py --check
python scripts/validate_catalog.py
python scripts/validate_source_digest.py
python scripts/run_toy_lab.py
pytest
```

玩具实验演示：

1. 参数固定时，不同输入仍选择不同特征和路径；
2. 当前贡献取决于“权重 × 源激活”；
3. 相对 logit 的小变化会指数级改变 token 赔率；
4. 首 token 写回后会产生分叉的自回归轨迹；
5. 大而罕见的连接可能比小而常用的连接更不有效。

玩具模型只用于澄清数学概念，不声称重现真实前沿模型。

# 研究原则

1. **先定义对象，再讨论机制。**
2. **可解码不等于被使用。**
3. **相关性不等于因果性。**
4. **输出等价不等于机制等价。**
5. **单个 prompt 的图不冒充全局理论。**
6. **特征标签必须接受分布和反例检验。**
7. **安全研究只使用无害代理，不提供可复用攻击载荷。**
8. **把失败案例和不确定性写进结论。**
9. **科学结论优先引用原始研究页面。**

# 范围与边界

当前最合理的综合立场是：

- SAE、crosscoder、transcoder、CLT、MOLT、NLA 和 J-space 都是分析接口或近似模型，不是唯一正确坐标；
- attribution graph 可以提出并部分验证局部机制，但可能遗漏误差、QK 动态、替代路径和非线性；
- 小模型、单层模型和特定 Claude 版本上的结果不能无条件推广；
- 内部存在情绪、角色或危险概念不意味着主观体验或人格；
- 功能性内省和 global-workspace 类比不构成意识证明；
- prompt injection 最终仍需要外部权限隔离和系统安全，而非只靠提示词或可解释性。

# 版权与归属

本仓库的中文综合、结构和代码采用 MIT License。原始论文、研究更新、工具和交互图版权归各自作者及发布方所有。引用科学结论时，请优先打开逐条精华或索引中的原始页面。
