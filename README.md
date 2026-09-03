# LLM Theory Lab｜大模型理论与机制可解释性课程

[![CI](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml)
[![Documentation](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml)
[![CodeQL](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **课程与实验版本：0.3.0；研究快照：2026-09-01。**  
> 这个仓库把 Transformer Circuits 的研究线索整理成一条可学习、可运行、可反驳的路径。目标不是收集术语，而是训练一种分析能力：分清对象，写对因果方向，设计对照，再限制结论。

## 你会学到什么

完成核心课程后，你应该能够：

- 区分训练权重、当前激活、潜在特征、回路、logits 与生成轨迹；
- 解释 input 如何在**不修改参数**的情况下改变本次实际计算；
- 分别分析 Attention 的 QK 路由与 OV 写回；
- 理解 superposition、SAE、transcoder 和 attribution graph 的价值与边界；
- 区分“信息可解码”“模型自然使用”“因果必要”和“因果充分”；
- 用识别—权限—策略—输出—反馈链分析拒绝、过度拒绝和 prompt injection；
- 把一个机制直觉改写成有正负对照、反证条件和证据等级的实验。

## 核心因果链

```text
训练数据、目标和优化器
          ↓
      固定参数 θ
          ↓
字符串 → tokenizer → token / position / role / source 表示
          ↓
动态激活、特征、Attention 路由和局部计算图
          ↓
        logits
          ↓
  softmax / decoding
          ↓
      输出 token
          ↓
          └────写回上下文────> 下一步激活与新分布
```

一句话概括：

> **训练分布塑造权重；权重规定模型可能怎样计算；输入决定本次实际激活哪些表示和路径；这些路径形成 logits；被选中的 token 写回上下文后，又改变下一步计算。**

## 30 分钟开始

先读[课程导览](docs/course/index.md)，再完成第 1、2 章，并运行三个实验：

```bash
git clone https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias.git
cd impact_of_guided_questioning_on_llm_bias

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,docs]"

llm-theory-lab course
llm-theory-lab explain C01
llm-theory-lab run-toy --ids C01 C02 C03
```

报告写入：

```text
reports/toy/results.json
reports/toy/report.md
```

不要只看 `pass`。打开报告，逐项回答：观测量是什么、保持了什么不变、哪条替代解释仍然存在、结论最多能说到哪里。

## 完整课程

| 模块 | 核心问题 | 透明实验 |
|---|---|---|
| [M01 模型是条件系统](docs/course/01-model-as-conditional-system.md) | 训练、单次 forward 和连续生成分别发生什么？ | C03 |
| [M02 权重、激活与 logits](docs/course/02-weights-activations-and-logits.md) | input 怎样通过固定参数改变 token 竞争？ | C01、C02 |
| [M03 Attention 与回路](docs/course/03-attention-and-circuits.md) | 为什么 Attention heatmap 不是完整解释？ | C04 |
| [M04 特征与 superposition](docs/course/04-features-and-superposition.md) | 为什么一个神经元通常不是一个概念？ | C06 |
| [M05 推理与反馈](docs/course/05-reasoning-and-feedback.md) | 中间状态和首 token 如何塑造轨迹？ | C05 |
| [M06 因果可解释性](docs/course/06-causal-interpretability.md) | 怎样从相关升级到机制证据？ | C07、C08 |
| [M07 安全路由](docs/course/07-safety-routing.md) | 怎样理解识别、权限、策略和最终行为的分离？ | C09 |
| [M08 综合项目](docs/course/08-capstone.md) | 怎样设计一个不会自欺的机制实验？ | 自选 |

课程配有[实验手册](docs/labs/index.md)、[练习册](docs/exercises/index.md)和[答案与解析](docs/exercises/solutions.md)。

## 已实现的实验

| ID | 检验的命题 | 证据性质 |
|---|---|---|
| C01 | 权重大小不等于当前贡献或分布有效性 | 透明结构反例 |
| C02 | 正温度下，token 对数赔率由相对 logit 决定 | 数学恒等式 |
| C03 | 固定权重可对不同 input 执行不同条件计算 | 透明玩具模型 |
| C04 | Attention 的 QK 路由与 OV 写回是不同问题 | 透明单头实验 |
| C05 | 首 token 写回可放大为长期轨迹分叉 | 自回归反馈模型 |
| C06 | 稀疏 superposition 能压缩特征，但会产生干扰 | 几何玩具模型 |
| C07 | 信息可被 probe 解码，不代表模型自然使用它 | 因果反例 |
| C08 | Activation patching 可检验候选中间状态 | 反事实干预 |
| C09 | 内容识别、策略状态和最终行为可以分离 | 无害安全代理 |

每个实验都配有运行前预测、关键指标、代码改动任务、反证条件和禁止外推。入口见[实验手册](docs/labs/index.md)。

## 三层内容，不再混成一堆

```text
docs/course/       主课程：按依赖顺序学习
docs/labs/         实验手册：预测、运行、解释、改动
docs/exercises/    练习与答案：检验是否真正理解

docs/00–14...      深度专题：需要时深入
sources/            Transformer Circuits 机器可读来源目录
src/                可安装 Python 包和实验实现
```

初学者不需要从 56 条来源逐篇开始。先完成课程和实验，再进入[统一理论综合](docs/09_UNIFIED_SYNTHESIS.md)、[经典案例](docs/11_CANONICAL_CASE_STUDIES.md)和[逐条来源精华](docs/10_SOURCE_BY_SOURCE_DIGEST.md)。

## 证据等级

```text
L0  数学恒等式
L1  完全透明的 toy 或结构反例
L2  开放模型中的受控观察
L3  开放模型内部干预
L4  跨模板、任务和模型的稳定复现
L5  能产生新反事实预测并被独立复现的机制理论
```

`pass` 只表示本次预注册检查通过，不表示“所有大模型都已证明”。同样，缺依赖、代码错误和实验被反驳必须分别记录，不能混为一谈。

## 质量检查

```bash
make check
```

它会运行：

- Ruff lint 与格式检查；
- 理论来源、课程映射和内部链接校验；
- pytest 与覆盖率；
- MkDocs strict 构建；
- wheel/sdist 构建与 Twine 检查；
- C01–C09 透明实验。

本地课程网站：

```bash
mkdocs serve
```

## 研究边界

本仓库不是 Anthropic 或 Transformer Circuits 作者的官方项目，也不声称恢复了前沿模型的完整源代码。SAE、probe、steering、patching、transcoder 和 attribution graph 都是有限分析接口；具体科学结论应优先引用原始研究。

安全研究只接受无害代理、检测、审计和防御性分析，不收录可直接复用的危险载荷或自动攻击优化。

贡献见 [CONTRIBUTING.md](CONTRIBUTING.md)，安全报告见 [SECURITY.md](SECURITY.md)，引用见 [CITATION.cff](CITATION.cff)。
