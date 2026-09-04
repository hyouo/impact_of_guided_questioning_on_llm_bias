# M04｜开放模型 induction-head 扫描

## 问题

在序列：

```text
A B C D A
```

中，后一个 `A` 是否让某些注意力头读取前一个 `A` 后面的 `B`？

这是 induction-head 假设的一个局部、可测量切片。它比“看起来像复制”更具体，但仍只是候选机制观察。

## 证据等级

```text
L2：开放模型观察
```

本实验没有把候选头消融，因此不是 L3 因果干预。

## 环境与模型 revision

安装可选依赖：

```bash
python -m pip install -e ".[models]"
```

仓库默认不联网下载。先使用已经缓存的模型，或在首次运行中显式允许下载：

```bash
llm-theory-lab hf-induction \
  --model openai-community/gpt2 \
  --revision <immutable-hub-commit> \
  --allow-download
```

审查级结果必须使用不可变 commit SHA，而不是只记录 `main` 或模型名。

## 运行前预测

先写下：

1. 你预测哪些层更可能出现较高 induction score；
2. 目标 attention 是否一定与目标 token logit margin 同方向；
3. 若最高头被消融，预测 margin 会怎样变化；
4. 哪些结果会让你放弃“这个头是主要 induction 中介”的解释。

## 运行

```bash
llm-theory-lab hf-induction \
  --model openai-community/gpt2 \
  --revision <immutable-hub-commit> \
  --samples 64 \
  --top-k 20 \
  --seed 7 \
  --output reports/m04-induction.json
```

同时会生成：

```text
reports/m04-induction.md
```

## 指标定义

对每个 layer/head 和后一个 `A` 的 query，定义：

$$
s_{\ell,h}
=
\alpha_{\ell,h}(A_{\text{later}}, B_{\text{earlier-successor}})
-
\operatorname{mean}_{j\neq B}\alpha_{\ell,h}(A_{\text{later}},j).
$$

报告包含：

- `target_attention_by_layer_head`；
- `control_attention_by_layer_head`；
- `induction_score_by_layer_head`；
- `top_heads`；
- `mean_target_logit_margin`；
- `std_target_logit_margin`；
- 前八个样本的 token ID、token 文本和 margin。

这里的 control 是同一 query 下其余 causal 位置的平均值。它控制了“这个头普遍把质量集中到少数位置”的一部分影响，但还不是完整负对照。

## 如何读结果

### 得分高

允许结论：

> 该 layer/head 在当前模型、revision、模板和样本中具有 induction-style attention pattern。

不允许结论：

> 它就是模型唯一的 induction head，或它决定了全部 in-context learning。

### 得分低

不能立即说明模型没有 induction 机制。替代解释包括：

- 当前模型通过 MLP、其他位置或多头组合实现；
- 五 token 模板太短；
- 候选词的 tokenization 不合适；
- 目标行为需要前一 token head 先写入信息；
- attention 实现没有以容易观察的单头峰值出现；
- 模型本身没有在该规模形成强 induction behaviour。

## 必做负对照

完成基础运行后，至少加入四个对照：

1. **不重复 A：** `A B C D E`；
2. **错误 successor：** 读取前一个 A 本身，而不是其后 B；
3. **相同距离对照：** 保持目标位置距离不变但改变 token 匹配；
4. **随机头基线：** 比较最高头与随机 layer/head 的分数分布。

更强版本还应加入：

- 多个序列长度；
- 多个 distractor 数量；
- 两次及多次重复；
- 不同词类与不同语言 token；
- 多个模型和多个 checkpoint；
- bootstrap 置信区间；
- 预先登记的头选择规则。

## 从观察升级到因果

下一步可实现 M05：

```text
找候选头
→ 在 corrupted/clean 序列间 patch 该头输出
→ 或对该头做 head mask / output ablation
→ 测量目标 B 的 logit difference
→ 与错误头、错误层、随机头比较
```

只有当候选头的干预在正确位置、正确方向和多个模板上按预测改变行为时，才能把结论升级为局部因果证据。

## 与原始 induction-head 工作的差异

原始研究还讨论：

- induction heads 在训练中的形成相变；
- 宏观 in-context learning 指标的变化；
- previous-token heads 与 induction heads 的组合；
- 不同模型规模与 checkpoint；
- 路径级 QK/OV 分析；
- 多种消融和行为关联。

M04 目前只复现“开放模型中是否能观察到对应 attention pattern”这一小块。结果页和复现目录必须保留这项差异。

## 失败记录

模型未缓存、依赖缺失或 attention 未返回时，不要手工把实验标为通过。记录：

```text
模型名与 revision
下载策略
Transformers 与 PyTorch 版本
设备
错误类型
错误消息
```

缺少运行条件是 `skipped/error`，不是理论反证，也不是成功复现。
