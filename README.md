# LLM Theory Lab｜大模型理论与机制可解释性实验仓库

[![CI](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml)
[![CodeQL](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **研究快照：2026-09-01；仓库规范版本：0.2.0。**  
> 本项目把 [Transformer Circuits Thread](https://transformer-circuits.pub/) 的主要成果整理成中文理论，并用透明玩具模型与可选开放模型实验检验其中可操作化的命题。

## 核心命题

```text
训练数据、目标和优化器
          ↓
      固定参数 θ
          ↓
字符串 → tokenizer → token / position / role 表示
          ↓
动态激活、特征、attention 路由和局部计算图
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

这要求始终区分：

- **参数**：训练后保存的连接规则，标准推理时通常不变；
- **激活**：当前输入产生的动态数值状态；
- **特征**：对可重复语义或计算变量的分析性描述；
- **回路**：多个表示和模块组成的条件计算路径；
- **logits 与概率**：当前上下文下对候选 token 的预测偏好；
- **生成轨迹**：输出 token 反复写回后形成的动态过程。

## 项目目标

本仓库同时承担三项工作：

1. **理论整理**：把权重、激活、superposition、attention、推理、安全和因果验证放入同一框架。
2. **来源审计**：对 Transformer Circuits 时间线中的 56 条来源建立机器可读目录和逐条精华。
3. **理论检验**：把可操作化命题写成有对照、指标、反证条件和结论边界的实验。

本项目不宣称已经获得前沿模型的完整“源代码”，也不把一次 probe、单个 attribution graph 或单次输出当作普遍机制证明。

## 快速开始

### 1. 安装开发环境

```bash
git clone https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias.git
cd impact_of_guided_questioning_on_llm_bias

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. 查看并运行透明实验

```bash
llm-theory-lab list
llm-theory-lab run-toy
pytest
```

默认报告写入：

```text
reports/toy/results.json
reports/toy/report.md
```

只运行指定实验：

```bash
llm-theory-lab run-toy --ids C01 C04 C07
```

### 3. 运行完整质量检查

```bash
make check
```

它会执行代码格式、静态检查、理论来源校验、单元测试、文档构建和包构建。

### 4. 可选开放模型实验

```bash
pip install -e ".[models]"

llm-theory-lab hf-tokenization
llm-theory-lab hf-prefix
llm-theory-lab hf-patch
```

开放模型实验需要下载或提供模型权重。它们默认属于观察性或局部干预证据，不能仅凭一次运行推广到所有模型。

## 已实现的实验

| ID | 理论命题 | 证据性质 |
|---|---|---|
| C01 | 权重大小不等于当前贡献或分布有效性 | 透明结构反例 |
| C02 | 正温度下，token 对数赔率由相对 logit 决定 | 数学恒等式 |
| C03 | 固定权重可对不同输入执行不同条件计算 | 透明玩具模型 |
| C04 | Attention 的 QK 路由与 OV 写回是不同问题 | 透明单头实验 |
| C05 | 首 token 写回可放大为长期轨迹分叉 | 自回归反馈模型 |
| C06 | 稀疏 superposition 能压缩特征，但会产生干扰 | 几何玩具模型 |
| C07 | 信息可被 probe 解码，不代表模型实际使用它 | 因果反例 |
| C08 | Activation patching 可检验候选中间状态 | 反事实干预 |
| C09 | 内容识别、策略状态和最终行为可以分离 | 无害安全代理 |
| M01 | Prompt 格式与 tokenization 会改变内部状态和输出分布 | 开放模型观察 |
| M02 | 不同前缀写回后，下一步条件分布会分叉 | 上下文反事实 |
| M03 | 逐层 patch 可定位传递目标 logit 效应的状态 | 局部内部干预 |

每个实验的允许结论、禁止外推和反证条件见
[`docs/14_THEORY_TO_CODE_LAB.md`](docs/14_THEORY_TO_CODE_LAB.md)。

## 文档入口

推荐阅读顺序：

```text
第一性原理教程
  → 统一理论综合
  → 经典机制案例
  → 方法与解释矩阵
  → 理论—实验映射
  → 全部来源逐条精华
```

| 文档 | 内容 |
|---|---|
| [`docs/13_FIRST_PRINCIPLES_TUTORIAL.md`](docs/13_FIRST_PRINCIPLES_TUTORIAL.md) | 从 tokenization 到生成反馈的清晰教程 |
| [`docs/09_UNIFIED_SYNTHESIS.md`](docs/09_UNIFIED_SYNTHESIS.md) | 从训练分布到行为的统一理论 |
| [`docs/11_CANONICAL_CASE_STUDIES.md`](docs/11_CANONICAL_CASE_STUDIES.md) | induction、推理、规划、幻觉、安全和 persona 案例 |
| [`docs/12_METHODS_AND_INTERPRETATION_MATRIX.md`](docs/12_METHODS_AND_INTERPRETATION_MATRIX.md) | 每种工具能够与不能证明什么 |
| [`docs/14_THEORY_TO_CODE_LAB.md`](docs/14_THEORY_TO_CODE_LAB.md) | 理论命题到代码实验的映射 |
| [`docs/10_SOURCE_BY_SOURCE_DIGEST.md`](docs/10_SOURCE_BY_SOURCE_DIGEST.md) | 56 条来源的逐条精华 |
| [`docs/TRANSFORMER_CIRCUITS_INDEX.md`](docs/TRANSFORMER_CIRCUITS_INDEX.md) | 原始研究时间线索引 |
| [`docs/experiments/EXPERIMENT_PROTOCOL.md`](docs/experiments/EXPERIMENT_PROTOCOL.md) | 实验设计协议 |
| [`docs/experiments/RESULT_SCHEMA.md`](docs/experiments/RESULT_SCHEMA.md) | 结果文件格式 |

本地构建文档：

```bash
pip install -e ".[docs]"
mkdocs serve
```

## 标准目录结构

```text
.
├── .github/                 # CI、CodeQL、Dependabot、Issue/PR 模板
├── docs/                    # 理论、来源、实验协议与维护文档
├── examples/                # 最小可运行示例
├── scripts/                 # 仓库和文档一致性校验
├── sources/                 # 机器可读来源目录
├── src/llm_theory_lab/      # Python 包
├── tests/                   # 单元与集成测试
├── pyproject.toml           # 包元数据和工具配置
├── mkdocs.yml               # 文档站配置
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

## 研究与贡献原则

所有机制主张都应包含：

```text
Claim
Scope
Evidence level
Alternative explanations
Intervention and controls
Falsifier
Allowed conclusion
Forbidden inference
```

安全研究只接受无害代理、检测、审计和防御性分析；不要提交真实危险操作步骤、可直接复用的越狱载荷或自动攻击优化。

贡献前请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。安全问题请遵循
[`SECURITY.md`](SECURITY.md)，一般使用问题见 [`SUPPORT.md`](SUPPORT.md)。

## 引用

引用本仓库的综合或代码时，请使用 [`CITATION.cff`](CITATION.cff)。引用具体科学结论时，应优先引用
[`docs/TRANSFORMER_CIRCUITS_INDEX.md`](docs/TRANSFORMER_CIRCUITS_INDEX.md) 中对应的原始研究。

## 许可证与归属

本仓库代码与原创整理采用 [MIT License](LICENSE)。Transformer Circuits 原始论文、网页、图表与交互内容的版权归各自作者和发布方所有；本仓库不是 Anthropic 或原作者的官方项目。详见 [`NOTICE.md`](NOTICE.md)。
