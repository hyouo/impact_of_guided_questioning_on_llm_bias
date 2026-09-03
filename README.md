# LLM Theory Lab

> 用一条清晰的学习路径理解大模型的权重、激活、Attention、表征、推理、自回归反馈与安全路由；再用透明实验检验你是否真的理解了。

[![CI](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/ci.yml)
[![Documentation](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/docs.yml)
[![CodeQL](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml/badge.svg)](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

本仓库不是论文堆、链接收藏夹，也不是“观察几段输出就解释内部机制”的 prompt 项目。它把 [Transformer Circuits](https://transformer-circuits.pub/) 的研究线索组织成四层：

```text
课程：按依赖顺序建立正确心智模型
实验：把命题变成可运行的对照、反例和干预
练习：手算、构造反例并设计实验
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

开放模型实验是可选依赖：

```bash
python -m pip install -e ".[models]"
llm-theory-lab hf-tokenization --help
llm-theory-lab hf-prefix --help
llm-theory-lab hf-patch --help
```

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

| ID | 核心命题 |
|---|---|
| C01 | 权重大小不等于当前贡献或分布有效性 |
| C02 | 正温度下，token 对数赔率由相对 logit 决定 |
| C03 | 固定权重仍可对不同 input 执行不同条件计算 |
| C04 | QK 决定读取位置，OV 决定写回内容 |
| C05 | 首 token 写回可以放大成长期轨迹差异 |
| C06 | 稀疏 superposition 提高容量，也引入干扰 |
| C07 | 信息可被 probe 解码，不代表模型自然使用它 |
| C08 | Activation patching 可检验候选因果中介 |
| C09 | 内容识别、策略状态和最终行为可以分离 |
| C10 | 内部坐标可改变，而协调后的线性函数保持不变 |
| C11 | 单点消融无准确率损失，不证明路径未参与计算 |
| C12 | Steering 需要剂量、反向和等范数方向对照 |

查看某个实验真正能与不能证明什么：

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
├── examples/                # 可直接运行的最小示例
├── src/llm_theory_lab/      # 实验包与 CLI
├── tests/                   # 单元与集成测试
├── scripts/                 # 内容、链接和来源一致性检查
├── sources/                 # 机器可读来源目录
├── pyproject.toml
└── mkdocs.yml
```

## 质量边界

本仓库坚持四条规则：

1. **观察不是机制。** 输出变化、Attention 热图或 probe 准确率都不能单独证明因果路径。
2. **玩具结果不是普遍定律。** C01–C12 说明一种机制可以发生或一种推理不成立，不估计所有大模型中的效应大小。
3. **解释必须可失败。** 每个实验都有检查项、反证条件和禁止外推。
4. **安全研究只用无害代理。** 不收录可直接复用的越狱载荷、危险步骤或自动攻击优化。

完整质量检查：

```bash
python -m pip install -e ".[dev,docs]"
make check
```

## 贡献、引用与许可

贡献前阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。安全问题按 [SECURITY.md](SECURITY.md) 私下报告。引用具体科学结论时，应优先引用[原始研究索引](docs/reference/transformer-circuits-index.md)中的来源；引用本仓库的整理或软件时使用 [CITATION.cff](CITATION.cff)。

代码与原创整理采用 [MIT License](LICENSE)。本仓库不是 Anthropic 或 Transformer Circuits 作者的官方项目。
