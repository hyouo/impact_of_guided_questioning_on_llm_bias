# 14｜理论如何变成代码实验

> 理论不是“听起来合理的解释”。机制命题必须明确对象、范围、干预、指标、对照、反证条件和结论边界。本章把核心理论映射到标准根目录中的 [`src/llm_theory_lab/`](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/tree/main/src/llm_theory_lab) 与 [`tests/`](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/tree/main/tests)。

## 14.1 证据阶梯

```text
L0 数学恒等式或精确程序性质
L1 透明玩具模型、结构反例、完全可知因果图
L2 开放模型观察或上下文反事实
L3 开放模型内部干预
L4 跨模板、任务、checkpoint 和模型的稳定回路证据
L5 产生新反事实预测并被独立复现的机制理论
```

实验 `pass` 只表示预先定义的检查通过，不会自动把 L1 结果升级为 L4 或 L5。

## 14.2 实验总览

| ID | 核心命题 | 代码 | 主要边界 |
|---|---|---|---|
| C01 | 权重大小不等于当前贡献或有效性 | `experiments/weights.py` | 玩具分布，不估计真实模型比例 |
| C02 | 正温度下 log-odds 由相对 logit 决定 | `experiments/temperature.py` | 不保证某 token 一定被采样 |
| C03 | 固定权重可执行输入条件计算 | `experiments/conditional.py` | 不说明真实模型只有少数特征 |
| C04 | QK 路由和 OV 写回是不同对象 | `experiments/attention.py` | 低维单头演示 |
| C05 | 首 token 可造成轨迹分叉 | `experiments/feedback.py` | 人工反馈模型 |
| C06 | Superposition 可压缩但会干扰 | `experiments/superposition.py` | 人工几何 |
| C07 | Probe 可解码不等于因果使用 | `experiments/probe_causality.py` | 结构反例 |
| C08 | Patching 可测试候选中介 | `experiments/patching.py` | 足够性不等于唯一性 |
| C09 | 识别、策略状态和行为可分离 | `experiments/safety_routing.py` | 无害安全代理 |
| M01 | Prompt 格式影响 token、状态和分布 | `experiments/hf_models.py` | 观察性，因素可能混杂 |
| M02 | 替代前缀改变下一步条件分布 | `experiments/hf_models.py` | 不比较前缀自然概率 |
| M03 | 逐层 patch 传递目标 logit 效应 | `experiments/hf_models.py` | 粒度粗、架构有限 |

下文中的代码路径均相对于 `src/llm_theory_lab/`。

## 14.3 C01｜权重、激活与有效性

一条连接的当前贡献为：

$$
c_{ij}(x)=w_{ij}a_j(x).
$$

实验构造“大但罕见”和“小但常见”的连接，比较当前贡献与透明的分布有效性代理。

**反证条件：** 在已明确的输入分布中，绝对权重无论源激活如何都必然给出相同的重要性排序。

**允许结论：** 权重绝对值不是功能重要性的充分指标。

**禁止结论：** 不能由玩具代理估计真实模型中 interference weights 的比例。

## 14.4 C02｜温度与 token 赔率

对 $T>0$：

$$
\log\frac{p_i}{p_j}=\frac{z_i-z_j}{T}.
$$

相对 logit 增加 $\Delta z$ 后，赔率乘以：

$$
e^{\Delta z/T}.
$$

实验直接比较解析式和数值 softmax。

**边界：** API 中的 `temperature=0` 通常代表 greedy/argmax 约定，不应代入上述公式。

## 14.5 C03｜固定权重下的条件计算

$$
h=f_\theta(x).
$$

保持 $\theta$ 不变，对任务证据、安全证据和不确定性输入进行对照，检查激活模式与 top token 是否改变。

**允许结论：** input 无需修改参数也能改变实际计算路径。

## 14.6 C04｜Attention 的 QK 与 OV

$$
\alpha_{ij}
=
\operatorname{softmax}_j
\left(
\frac{q_i^\top k_j}{\sqrt d}
\right),
\qquad
o_i=\sum_j\alpha_{ij}v_jW_O.
$$

实验固定所有矩阵，只改变一个 token 在 key-relevant 方向上的表示，分别记录注意力路由和聚合输出。

**禁止结论：** 一张热力图不能单独说明为什么读取、写入什么或该头是否必要。

## 14.7 C05｜自回归反馈

$$
y_t\sim p_\theta(\cdot\mid x,y_{<t}),
\qquad
p_{t+1}=p_\theta(\cdot\mid x,y_{<t},y_t).
$$

强制两个不同首 token 后，比较未来状态和序列。

**允许结论：** 生成 token 可以作为新输入产生路径依赖。

**禁止结论：** 人工反馈矩阵不能量化真实模型的越狱惯性。

## 14.8 C06｜Superposition

将 $F>d$ 个稀疏特征放入低维空间，比较单特征激活与共激活时的重建误差。

**允许结论：** 过完备表示在特征稀疏时可行，但非正交方向会产生干扰。

**禁止结论：** 人工方向不是训练出的 SAE 字典。

## 14.9 C07｜可解码与被使用

实验构造一个可被 probe 高准确率恢复、但输出头权重为零的变量，再与真正控制输出的变量比较消融效应。

**允许结论：** `decodable` 不蕴含 `causally used`。

## 14.10 C08｜Activation patching

从 clean 运行提取候选中间状态，替换 corrupted 运行中的对应状态，并测量目标输出恢复；无关维度作为负对照。

**允许结论：** 被替换状态对目标效应具有局部因果充分性。

**禁止结论：** 正恢复不证明该状态是唯一自然中介。

## 14.11 C09｜安全识别、策略与行为分离

使用无害访问控制任务，把类别识别、策略状态和最终动作分成独立维度，再 patch 策略状态。

**允许结论：** 检测信号存在不保证最终行为与之对齐。

**安全边界：** 不包含真实越狱载荷、危险操作或攻击搜索。

## 14.12 M01–M03｜开放模型实验

安装：

```bash
pip install -e ".[models]"
```

### M01：格式与 tokenization

```bash
llm-theory-lab hf-tokenization \
  --model openai-community/gpt2 \
  --prompt-a "A careful answer begins with" \
  --prompt-b $'A careful answer begins with\n'
```

记录 token IDs、top-k、分布差异、逐层表示和 attention。结果是观察性证据，不能把所有变化归因于单个语义特征。

### M02：前缀反馈

```bash
llm-theory-lab hf-prefix \
  --model openai-community/gpt2 \
  --prompt "The response begins:" \
  --prefix-a " Yes" \
  --prefix-b " No"
```

它测试固定权重下，把不同 token 写回上下文是否改变下一步分布。

### M03：逐层 patch

```bash
llm-theory-lab hf-patch \
  --model openai-community/gpt2 \
  --clean "The capital of France is" \
  --corrupted "The capital of Italy is" \
  --target-token " Paris"
```

程序对 GPT-2 风格 block 的最终位置 residual state 逐层 patch。整个 residual 向量包含许多变量，因此正效应不等于找到单一概念神经元。

## 14.13 标准实验报告

每次实验至少记录：

```text
理论 claim / experiment ID
代码版本和 Git commit
模型名称、revision 和 tokenizer
完整输入与 token IDs
随机种子与解码参数
层、位置、头、特征或 patch 对象
基线、正对照、负对照和干预
指标、聚合方式和不确定性
失败样本
允许结论与禁止外推
```

结果结构见 [`experiments/RESULT_SCHEMA.md`](experiments/RESULT_SCHEMA.md)，设计规范见
[`experiments/EXPERIMENT_PROTOCOL.md`](experiments/EXPERIMENT_PROTOCOL.md)。

## 14.14 运行与验证

```bash
pip install -e ".[dev]"
llm-theory-lab list
llm-theory-lab run-toy
pytest
make check
```

代码注册表位于 [`src/llm_theory_lab/registry.py`](https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/blob/main/src/llm_theory_lab/registry.py)。新增实验时必须同步更新测试、本文和变更日志。
