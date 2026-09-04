# LLM Theory Lab

> 一套中文大模型机制课程、透明实验室与可审计复现路线图。核心主题包括权重、激活、Attention、表征、推理、自回归反馈、因果可解释性与安全路由。

[![CI](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml)
[![Documentation](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml)
[![CodeQL](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 当前成熟度

本仓库已经是可安装、可测试、可构建文档、可生成证据 bundle 的研究型课程仓库；它还不是“Anthropic 全部实验已经复现”的成品。

截至 `2026-09-04`，机器可读复现地图覆盖 Transformer Circuits 目录中的 **56/56** 条公开来源：

| 状态 | 数量 | 准确含义 |
|---|---:|---|
| `implemented-complete` | 0 | 尚无来源被声明为完整复现 |
| `implemented-partial` | 20 | 至少有一个相关协议，但没有覆盖该来源的全部主要结果 |
| `planned` | 28 | 已进入路线图，尚无通过验证的对应协议 |
| `reference-only` | 8 | 教学、方法论、工具、基础设施或历史材料，不伪造“实验通过” |

当前可执行核心是 C01–C12 透明实验；M01–M03 是开放模型原型，默认不在 CI 下载模型。对于依赖 Claude 私有权重、未公开激活、特征字典、训练数据或替代模型资产的工作，目标是做清楚标注的开放模型类比，而不是伪称原始数值复现。

查看完整状态、阻塞项和下一步：

```bash
llm-theory-lab reproduction-map --summary-only
llm-theory-lab reproduction-map --status planned --priority P0
llm-theory-lab reproduction-map --mode open-model-analogue --json
```

人类可读矩阵见[公开结果复现地图](docs/reference/reproduction-map.md)，规范数据见 [`reproductions/transformer_circuits_v1.json`](reproductions/transformer_circuits_v1.json)。

## 为什么这个仓库存在

它不采用以下研究捷径：

- 把论文摘要堆成目录；
- 只看几个输出就解释内部机制；
- 用同一个大模型生成结果并给自己打分；
- 把 Attention 热图、probe 准确率或 steering 成功直接写成因果结论；
- 把透明 toy 或开放模型方向性结果冒充 Claude 原实验复现。

仓库把工作拆成五层：

```text
课程：按因果依赖建立心智模型
实验：把命题变成可运行的反例、对照与干预
练习：手算、构造反例并设计研究
证据：保存 claim、来源、运行状态、哈希和结论边界
复现地图：逐条说明 56 个来源做到哪里、缺什么、下一步是什么
```

## 核心因果链

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

> **训练分布塑造权重；权重规定潜在计算；输入决定本次实际激活和路由；这些路径形成 logits；被选中的 token 写回上下文后，又改变下一步计算。**

## 快速开始

```bash
git clone https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias.git
cd impact_of_guided_questioning_on_llm_bias

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev,docs]"

llm-theory-lab roadmap
llm-theory-lab explain C01
llm-theory-lab run-toy --ids C01 C02 C04
```

完整本地门槛：

```bash
make check
```

## 学习路线

入口按顺序使用：

1. [课程导览](docs/course/index.md)：8 章，从条件系统到完整实验设计；
2. [实验手册](docs/labs/index.md)：C01–C12 一对一指导；
3. [基础练习](docs/exercises/index.md)与[进阶练习](docs/exercises/advanced.md)；
4. [统一理论](docs/reference/unified-theory.md)、[机制案例](docs/reference/case-studies.md)和[方法矩阵](docs/reference/methods-matrix.md)；
5. [来源逐条精华](docs/reference/source-digest.md)与[复现地图](docs/reference/reproduction-map.md)。

推荐闭环：

```text
阅读 → 写下预测 → 运行 → 修改一个条件 → 解释失败 → 做题 → 重写结论边界
```

## 十二个透明实验

| ID | Claim | 核心命题 | 证据上限 |
|---|---|---|---|
| C01 | H-C01 | 权重大小不等于当前贡献或分布有效性 | 透明结构演示 |
| C02 | H-C02 | 正温度下，token 对数赔率由相对 logit 决定 | 数学恒等式 |
| C03 | H-C03 | 固定权重仍可对不同 input 执行不同条件计算 | 透明结构演示 |
| C04 | H-C04 | QK 决定读取位置，OV 决定写回内容 | 透明结构演示 |
| C05 | H-C05 | 首 token 写回可以放大成长期轨迹差异 | 透明结构演示 |
| C06 | H-C06 | 稀疏 superposition 提高容量，也引入干扰 | 透明结构演示 |
| C07 | H-C07 | 信息可被 probe 解码，不代表模型自然使用它 | 逻辑反例 |
| C08 | H-C08 | Activation patching 可检验候选因果中介 | 透明结构演示 |
| C09 | H-C09 | 内容识别、策略状态和最终行为可以分离 | 无害代理演示 |
| C10 | H-C10 | 内部坐标可改变，而协调后的线性函数保持不变 | 线性代数恒等式 |
| C11 | H-C11 | 单点消融无准确率损失，不证明路径未参与计算 | 逻辑反例 |
| C12 | H-C12 | Steering 需要剂量、反向和等范数方向对照 | 方法控制演示 |

查看任何实验的主张、来源、反证条件和禁止外推：

```bash
llm-theory-lab explain C11
```

## 自验证证据 bundle

```bash
llm-theory-lab reproduce --output-dir reports/reproduction
llm-theory-lab validate-evidence reports/reproduction --bundle
```

bundle 包含：

```text
results.json             原始结果与运行环境
report.md                人类可读解释
canonical-results.json   去除时间和平台噪声的审查基线
evidence-ledger.json     claim、来源、状态、数据与结果哈希
evidence-matrix.md       从 ledger 生成的证据矩阵
manifest.json            代码 revision、来源覆盖和全部文件 SHA-256
context/                 schema、基线、56 条复现地图与来源目录快照
```

一个实验异常会写成 `error` 并保留其他结果；`fail`、`error`、`inconclusive` 和 `skipped` 不会被折叠成同一种状态。bundle 还会验证来源覆盖表本身，防止通过重写 README 抬高复现程度。

## 仓库结构

```text
.
├── docs/course/             # 8 章课程
├── docs/labs/               # C01–C12 实验手册
├── docs/exercises/          # 练习、答案与能力量表
├── docs/reference/          # 理论、案例、方法、来源与复现地图
├── docs/experiments/        # 协议、结果与证据规范
├── examples/                # 最小可运行示例
├── evidence/                # 审查过的规范化实验基线
├── reproductions/           # 56 条公开来源的机器可读覆盖地图
├── schemas/                 # evidence 与 reproduction schema
├── src/llm_theory_lab/      # 实验、CLI 和验证代码
├── tests/                   # 单元、集成与篡改检测
├── scripts/                 # 仓库、文档、来源和证据检查
└── sources/                 # Transformer Circuits 来源目录
```

## 质量边界

1. **观察不是机制。** 输出变化、Attention 热图或 probe 准确率不能单独证明因果路径。
2. **代理不是原实验。** 透明 toy 和开放模型类比必须保持各自标签。
3. **解释必须可失败。** 实验要有检查、反证条件、负对照和禁止外推。
4. **失败必须保留。** 不能为了绿色 CI 删除反例、不确定结果或执行错误。
5. **覆盖与模式分开。** “部分覆盖”与“开放模型类比”回答的是不同问题。
6. **安全研究只用无害代理。** 不收录可复用越狱载荷、危险步骤或自动攻击优化。

## 贡献、引用与许可

贡献前阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。引用具体科学结论时应优先引用[原始来源](docs/reference/transformer-circuits-index.md)；引用本仓库的软件或综合时使用 [CITATION.cff](CITATION.cff)。

代码与原创整理采用 [MIT License](LICENSE)。本仓库不是 Anthropic 或 Transformer Circuits 作者的官方项目。
