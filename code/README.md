# LLM Theory Lab｜大模型理论实验代码库

这是理论仓库中的**独立可安装子项目**。它不再让另一个大模型给输出打一个主观分数，而是把理论命题改写成：

```text
明确对象
→ 可操作化命题
→ 对照与干预
→ 可计算指标
→ 预先写出的反证条件
→ 有边界的结论
```

代码分为两层：

- **C01–C09：透明玩具实验。** 权重和计算全部可见，用来验证数学恒等式、结构可能性和方法反例；CI 每次提交都运行。
- **M01–M03：开放模型实验。** 下载 Hugging Face causal LM，观察 tokenization、隐藏状态、attention、前缀反馈，并进行 GPT-2 风格逐层 activation patching；由于需要模型下载，不在 CI 中自动运行。

它们的角色不同：玩具实验适合回答“这种机制在数学上能否发生”；开放模型实验适合回答“选定模型和输入上是否出现相似现象”。两者都不能单独建立适用于所有大模型的普遍定律。

## 1. 安装

### 只运行透明实验

```bash
cd code
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 运行开放模型实验

```bash
pip install -e ".[all]"
```

模型实验会从模型托管服务下载权重。请记录实际模型 revision、tokenizer、依赖版本、设备和输出报告。即使随机种子相同，PyTorch 也不保证跨版本、设备和平台完全逐位复现。

## 2. 快速运行

列出理论命题：

```bash
llm-theory-lab list
```

运行全部透明实验：

```bash
llm-theory-lab run-toy
```

只运行选定实验：

```bash
llm-theory-lab run-toy --ids C01 C04 C07
```

输出会写入：

```text
reports/toy/results.json
reports/toy/report.md
```

运行测试：

```bash
pytest
```

## 3. 理论—实验对应表

| ID | 理论命题 | 操作化方法 | 主要结论边界 |
|---|---|---|---|
| C01 | 权重大小不等于当前贡献或有效性 | 比较大而罕见的连接与小而常见的连接 | 玩具 effectiveness 代理，不等于真实论文指标 |
| C02 | token 对数赔率由 logit 差和正温度决定 | 数值验证 softmax 恒等式与赔率乘数 | 不直接预测哪个 token 一定被采样 |
| C03 | 固定权重可执行输入条件计算 | 同一 ReLU 网络输入三种状态 | 不说明真实模型只有少数可分离特征 |
| C04 | input 可改变 QK 路由和 OV 写回 | 固定单头 attention，扰动一个 token | 单头低维演示，非全模型 attention 解释 |
| C05 | 首 token 可通过反馈放大成轨迹差异 | 强制两个首 token，比较后续状态 | 人工反馈矩阵，只证明结构可能性 |
| C06 | 稀疏 superposition 能压缩特征但有干扰 | 五个方向放入二维空间 | 人工几何，不是学习出的 SAE 字典 |
| C07 | probe 可解码不等于模型使用 | 构造高 probe 准确率、零输出效应变量 | 反例用于推翻错误推理，不估计真实 probe 质量 |
| C08 | activation patching 可检验候选中介 | clean 状态 patch 到 corrupted 运行 | 恢复说明足够性，不证明唯一性 |
| C09 | 识别、策略状态和行为可以分离 | 无害访问控制代理与策略状态 patch | 结构反例，不声称真实安全坐标相同 |
| M01 | 格式和 tokenization 可改变内部与输出 | 比较两段 prompt 的 token、层表示、attention、next-token 分布 | 观察性；多个因素同时改变 |
| M02 | 已选前缀会改变下一步条件分布 | 把两个替代前缀写入上下文 | 不说明两个前缀自然产生概率相同 |
| M03 | 某层状态可传递目标 logit 效应 | GPT-2 风格逐层最终位置 patch scan | 粒度粗；正效应不证明唯一机制 |

更完整的假设、反证条件和解释规则见 [`docs/EXPERIMENT_PROTOCOL.md`](docs/EXPERIMENT_PROTOCOL.md)。

## 4. 开放模型实验

### M01｜格式与 tokenization 敏感性

```bash
llm-theory-lab hf-tokenization \
  --model openai-community/gpt2 \
  --prompt-a "A careful answer begins with" \
  --prompt-b $'A careful answer begins with\n'
```

报告内容包括：

- 两个字符串对应的 token IDs 和 token 文本；
- 下一 token 分布的 Jensen–Shannon divergence；
- 最终位置隐藏状态逐层 cosine similarity；
- 每层最后 query 的 attention 差异；
- 两边的 top-k next tokens。

解释时不能把全部差异归因于一个“语义特征”，因为换行也改变序列长度、最后位置和 tokenization。

### M02｜前缀反馈

```bash
llm-theory-lab hf-prefix \
  --model openai-community/gpt2 \
  --prompt "The response begins:" \
  --prefix-a " Yes" \
  --prefix-b " No"
```

它直接测试：在权重不变时，把不同前缀写入上下文，下一步条件分布是否分叉。长期轨迹还需继续多步生成，并对多个 seed、模板和候选前缀复现。

### M03｜逐层 activation patching

```bash
llm-theory-lab hf-patch \
  --model openai-community/gpt2 \
  --clean "The capital of France is" \
  --corrupted "The capital of Italy is" \
  --target-token " Paris"
```

要求：

- clean 与 corrupted prompt 的 token tensor 形状相同；
- target token 必须恰好是一个 tokenizer token；
- 模型必须提供 GPT-2 风格的 `model.transformer.h` block 列表。

程序把 clean 运行中每一层最终位置的 block 输出，逐层 patch 到 corrupted 运行，然后测量目标 token logit 的变化。结果是局部因果证据，但 patch 整个 residual 向量会同时替换很多变量，所以不能据此宣称找到了单一概念神经元。

## 5. 实验分级

```text
L0  数学恒等式或精确程序性质
L1  完全透明的玩具模型、结构反例、可穷举因果关系
L2  开放模型中的观察或受控上下文反事实
L3  开放模型中的局部内部干预
L4  跨模板、跨任务、跨模型、带负对照的稳定回路证据
L5  能产生新反事实预测并被独立复现的机制理论
```

代码里的 `status=pass` 只表示该实验的**预注册检查**通过，不表示该理论已经在所有大模型中得到证明。开放模型实验默认使用 `observational`，避免把一次运行包装成普遍结论。

## 6. 正确的实验记录

一次可审计实验至少保存：

```text
理论 claim ID
模型名称与 revision
tokenizer 与聊天模板
完整输入与 token IDs
随机种子和解码参数
层、位置、头、特征或 patch 对象
基线、干预和负对照
指标定义与统计聚合
失败样本
软件版本、设备和日期
允许的结论与禁止的外推
```

不要只保存最终生成文本。机制问题需要隐藏状态、attention、logits、干预位置和对照条件。

## 7. 安全边界

C09 使用的是无害的访问控制代理。仓库不内置真实越狱载荷、危险操作提示或绕过安全系统的自动搜索。安全机制研究应测试：识别、权限、策略路由、拒绝状态和输出之间是否解耦，而不是优化可复用攻击字符串。

## 8. 目录

```text
code/
├── pyproject.toml
├── README.md
├── docs/
│   ├── EXPERIMENT_PROTOCOL.md
│   └── RESULT_SCHEMA.md
├── scripts/
│   └── run_toy_suite.py
├── src/llm_theory_lab/
│   ├── cli.py
│   ├── math_utils.py
│   ├── registry.py
│   ├── repro.py
│   ├── result.py
│   └── experiments/
│       ├── attention.py
│       ├── conditional.py
│       ├── feedback.py
│       ├── hf_models.py
│       ├── patching.py
│       ├── probe_causality.py
│       ├── safety_routing.py
│       ├── superposition.py
│       ├── temperature.py
│       └── weights.py
└── tests/
```
