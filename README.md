# LLM Theory Lab

> 用一条清晰的学习路径理解大模型的权重、激活、Attention、表征、推理、自回归反馈与安全路由；再用透明实验和可审计证据台账检验你是否真的理解了。

[![CI](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml)
[![Documentation](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml)
[![CodeQL](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

本仓库不是论文堆、链接收藏夹，也不是“观察几段输出就解释内部机制”的 prompt 项目。它把 [Transformer Circuits](https://transformer-circuits.pub/) 的公开研究线索组织成五层：

```text
课程：按依赖顺序建立正确心智模型
实验：把命题变成可运行的对照、反例和干预
练习：手算、构造反例并设计实验
证据：保存 claim、来源、运行状态、哈希和结论边界
参考：需要研究细节时再进入深度材料和原始来源
```

## 先记住这条因果链

```text
训练数据、目标和优化器
          ↓
      固定参数 θ
          ↓
输入 token、位置、角色和历史
          ↓
动态激活、特征与 Attention 路由
          ↓
        logits
          ↓
  softmax / decoding
          ↓
      输出 token
          ↓
          └──写回上下文──> 下一步激活与新分布
```

> **训练分布塑造权重；权重规定模型可能怎样计算；输入决定本次实际激活哪些表示和路径；这些路径共同形成 logits；选出的 token 写回上下文后，又改变下一步计算。**

## 三种使用方式

### 1 小时：建立最小正确模型

读[课程导览](docs/course/index.md)，完成第 1–3 章，再运行：

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e .

llm-theory-lab explain C01
llm-theory-lab run-toy --ids C01 C02 C04
```

你应该能解释：参数和激活为什么不是同一件事、相对 logit 怎样决定赔率、QK 与 OV 分别做什么。

### 1 天：完成核心课程和十二个实验

```bash
python -m pip install -e ".[dev]"
llm-theory-lab roadmap
llm-theory-lab run-toy
pytest
```

按[课程主线](docs/course/index.md)学习 8 章，完成[十二个独立实验手册](docs/labs/index.md)，再用[练习册](docs/exercises/index.md)和[进阶练习](docs/exercises/advanced.md)检查自己能否独立推导和设计对照。

推荐循环：

```text
阅读 → 写预测 → 运行 → 修改条件 → 解释失败 → 做题 → 重写结论边界
```

### 研究使用：从观察升级到因果证据

先读：

- [统一理论综合](docs/reference/unified-theory.md)
- [机制案例](docs/reference/case-studies.md)
- [方法与解释矩阵](docs/reference/methods-matrix.md)
- [来源逐条精华](docs/reference/source-digest.md)
- [证据台账与复现规范](docs/experiments/EVIDENCE_LEDGER.md)

开放模型实验是可选依赖：

```bash
python -m pip install -e ".[models]"
llm-theory-lab hf-tokenization --help
llm-theory-lab hf-prefix --help
llm-theory-lab hf-patch --help
```

## 一键复现与证据校验

完整 CPU-safe 复现入口不是单纯运行一组测试，而是生成自验证 bundle：

```bash
python -m pip install -e ".[dev,docs]"
llm-theory-lab reproduce --output-dir reports/reproduction
llm-theory-lab validate-evidence reports/reproduction --bundle
```

bundle 同时包含：

```text
results.json             原始结果与运行环境
report.md                人类可读解释
canonical-results.json   去除时间/平台噪声后的漂移基线
evidence-ledger.json     claim、来源、状态、数据与结果哈希
evidence-matrix.md       证据矩阵
manifest.json            代码 revision 和全部文件 SHA-256
context/                 schema、审查基线与来源快照
```

每个 C01–C12 都有稳定的 `H-Cxx@revision`、复现类型和原始来源映射。一个实验异常会被记录为 `error`，其余实验继续运行；`error`、`inconclusive`、`skipped` 与理论上的 `fail` 不再混为一谈。bundle 会携带打包后的 schema 和审查基线，因此从 wheel 安装后也能在仓库外校验。

当前目标是覆盖 Anthropic 与 Transformer Circuits 的**全部公开、可明确检验的机制 claim**，并为无法逐字复现的项目标注公开资产缺口。公开代码不能凭空恢复 Claude 的私有权重、未发布训练数据或未公开内部接口，因此这类项目必须记录为 `blocked-public-assets`，而不是伪装成已经复现。

## 课程地图

| 章 | 你要解决的问题 | 对应实验 |
|---|---|---|
| 1 | 一次语言模型调用到底发生了什么？ | C03 |
| 2 | 权重、激活、logits 和温度怎样连接？ | C01、C02 |
| 3 | Attention 为什么必须拆成 QK 与 OV？ | C04 |
| 4 | 为什么一个神经元通常不是一个概念？ | C06、C10 |
| 5 | 模型怎样形成中间状态，首 token 为什么重要？ | C05 |
| 6 | 怎样区分相关、可解码、必要、充分与可操纵？ | C07、C08、C11、C12 |
| 7 | 怎样理解拒绝、过度拒绝和权限混淆？ | C09 |
| 8 | 怎样设计一个不会自欺的机制实验？ | 综合项目 |

## 十二个透明实验

C01–C12 在 CI 中运行，关键权重、激活和中间状态全部可见。它们用于验证数学关系、证明结构可能性或构造方法反例，不冒充前沿模型的完整机制。

| ID | Claim | 核心命题 |
|---|---|---|
| C01 | H-C01 | 权重大小不等于当前贡献或分布有效性 |
| C02 | H-C02 | 正温度下，token 对数赔率由相对 logit 决定 |
| C03 | H-C03 | 固定权重仍可对不同 input 执行不同条件计算 |
| C04 | H-C04 | QK 决定读取位置，OV 决定写回内容 |
| C05 | H-C05 | 首 token 写回可以放大成长期轨迹差异 |
| C06 | H-C06 | 稀疏 superposition 提高容量，也引入干扰 |
| C07 | H-C07 | 信息可被 probe 解码，不代表模型自然使用它 |
| C08 | H-C08 | Activation patching 可检验候选因果中介 |
| C09 | H-C09 | 内容识别、策略状态和最终行为可以分离 |
| C10 | H-C10 | 内部坐标可改变，而协调后的线性函数保持不变 |
| C11 | H-C11 | 单点消融无准确率损失，不证明路径未参与计算 |
| C12 | H-C12 | Steering 需要剂量、反向和等范数方向对照 |

查看某个实验真正能与不能证明什么及其来源：

```bash
llm-theory-lab explain C11
```

## 练习与能力评估

[基础练习册](docs/exercises/index.md)覆盖完整课程；[进阶方法练习](docs/exercises/advanced.md)专门训练：

- 基底变换的精确推导与 privileged basis 边界；
- accuracy 饱和、冗余路径和联合消融；
- steering 的随机方向、正交方向、反向干预和剂量响应；
- 如何把“实验成功”降格为证据范围内的准确表述。

先独立作答，再查看[基础答案](docs/exercises/solutions.md)和[进阶答案](docs/exercises/advanced-solutions.md)。完成标准不是记住名词，而是能为机制说法补上对象、范围、对照、反证条件和禁止外推。

## 仓库结构

```text
.
├── docs/course/             # 从零开始的 8 章课程
├── docs/labs/               # C01–C12 一对一实验手册
├── docs/exercises/          # 基础与进阶练习、答案和能力量表
├── docs/reference/          # 深度综合、案例、方法和来源
├── docs/experiments/        # 协议、结果结构和证据台账规范
├── examples/                # 可直接运行的最小示例
├── evidence/                # 审查过的规范化结果基线
├── schemas/                 # 机器可读 ledger schema
├── src/llm_theory_lab/      # 实验包、证据工具与 CLI
├── tests/                   # 单元、集成和篡改检测测试
├── scripts/                 # 内容、来源、链接和证据一致性检查
├── sources/                 # 机器可读来源目录
├── pyproject.toml
└── mkdocs.yml
```

## 质量边界

本仓库坚持五条规则：

1. **观察不是机制。** 输出变化、Attention 热图或 probe 准确率都不能单独证明因果路径。
2. **玩具结果不是普遍定律。** C01–C12 说明一种机制可以发生或一种推理不成立，不估计所有大模型中的效应大小。
3. **解释必须可失败。** 每个实验都有检查项、反证条件和禁止外推。
4. **失败必须保留。** `fail`、`error`、`skipped` 和 `inconclusive` 进入证据记录，不能只发布绿色结果。
5. **安全研究只用无害代理。** 不收录可直接复用的越狱载荷、危险步骤或自动攻击优化。

完整质量检查：

```bash
python -m pip install -e ".[dev,docs]"
make check
```

## 贡献、引用与许可

贡献前阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。安全问题按 [SECURITY.md](SECURITY.md) 私下报告。引用具体科学结论时，应优先引用[原始研究索引](docs/reference/transformer-circuits-index.md)中的来源；引用本仓库的整理或软件时使用 [CITATION.cff](CITATION.cff)。

代码与原创整理采用 [MIT License](LICENSE)。本仓库不是 Anthropic 或 Transformer Circuits 作者的官方项目。
