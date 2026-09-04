# 全部来源复现目录｜不要把“相关实验”写成“原论文已复现”

本页回答一个比“仓库收录了多少论文”更严格的问题：

> 对 Transformer Circuits 时间线中的每一项公开来源，当前究竟能精确复现什么、只能做什么替代实验、缺少什么公开资产、下一步应实现什么？

仓库把这些状态分开保存，避免使用一句模糊的“已覆盖”掩盖巨大证据差异。

## 三个彼此独立的问题

### 1. 原始结果能否精确复现

`exact_feasibility` 只讨论原论文或研究更新中的原始实验：

| 值 | 含义 |
|---|---|
| `partial-public` | 方法和部分资产公开，可以重实现，但仍需核对代码、数据、checkpoint 或超参数 |
| `blocked-proprietary-assets` | 精确运行需要未公开模型、激活缓存、字典、训练分布、内部接口或评测资产 |
| `not-applicable` | 来源是观点、教育、工具、基础设施或历史材料，不对应一个单一实验结果 |

`blocked-proprietary-assets` 不表示结果错误。它只表示：

> 公开仓库不能声称已经逐字复现一个依赖私有 Claude 权重或内部激活接口的实验。

### 2. 本仓库现在实现了哪一层证据

`current_stage` 描述本仓库当前已有的工作：

| 值 | 含义 |
|---|---|
| `transparent-proxy` | 有完全透明的数学、结构或方法反例 |
| `open-model-partial` | 已有开放权重模型上的观察或局部干预，但不等同原始模型 |
| `planned` | 协议已经分类，但实现、资产或审查尚未完成 |
| `reference-synthesis` | 当前只作为概念、历史、教学或工具材料整理 |

例如，C09 能证明“识别状态与最终行为在结构上可以分离”，但不能据此声称已经复现 Claude 的拒绝回路。M04 能在开放模型上寻找 induction-style attention，但不能复现原研究中的完整训练相变和跨模型论证。

### 3. 下一步应使用哪个协议

每个来源至少映射到一个 `Pxx-*` 协议。协议不是论文标签，而是可执行研究路线：

| 协议 | 当前实现 | 作用 |
|---|---|---|
| `P01-CIRCUIT-ALGEBRA` | C02、C03、C04、C10 | residual stream、QK/OV、条件计算与基底代数 |
| `P02-SUPERPOSITION-WEIGHTS` | C01、C06、C10、C11 | superposition、干扰权重、有效性与冗余 |
| `P03-ATTENTION-OPEN-MODEL` | C04、M01、M03、M04 | 开放模型 attention、格式差异、patching 与 induction |
| `P04-AUTOREGRESSIVE-FEEDBACK` | C05、M02 | 前缀写回与条件分布分叉 |
| `P05-CAUSAL-CONTROLS` | C07、C08、C11、C12、M03 | probe、消融、steering 与 patching 的证据边界 |
| `P06-SAFETY-ROUTING-PROXY` | C09 | 无害的识别—策略—动作分离 |
| `P07-DICTIONARY-LEARNING` | 计划中 | SAE、transcoder、crosscoder |
| `P08-MODEL-DIFFING` | 计划中 | 匹配 checkpoint 与 stage-wise model diffing |
| `P09-CIRCUIT-TRACING` | 计划中 | replacement model 与 attribution graph |
| `P10-ACTIVATION-INTERFACES` | 计划中 | NLA、Activation Oracle 类接口 |
| `P11-MANIFOLD-GEOMETRY` | 计划中 | 连续流形与计数几何 |
| `P12-INTROSPECTION-WORKSPACE` | 计划中 | 注入状态、可报告表征与工作区 |
| `P13-AUDITING` | 计划中 | 自动审计与有种子缺陷的评测环境 |
| `P14-ARCHITECTURE` | 计划中 | SoLU 与匹配训练的架构比较 |
| `P15-LEARNING-DYNAMICS` | 计划中 | circuit formation、相变与 double descent |
| `P16-EDUCATION-INFRA` | 参考层 | 视频、练习、工具与研究前史 |
| `P17-PERSONA-SAFETY` | C09 支撑代理；真实实验计划中 | persona、角色、知识访问与策略路由 |

## 运行目录

查看全部 56 项来源：

```bash
llm-theory-lab replications
```

按主题过滤：

```bash
llm-theory-lab replications --theme attention
llm-theory-lab replications --theme dictionary_learning
```

只看精确复现受阻的来源：

```bash
llm-theory-lab replications \
  --exact blocked-proprietary-assets
```

只看当前已有开放模型部分协议的来源：

```bash
llm-theory-lab replications \
  --stage open-model-partial
```

生成机器可读 JSON：

```bash
llm-theory-lab replications \
  --format json \
  --output reports/replications.json
```

生成 Markdown 矩阵：

```bash
llm-theory-lab replications \
  --format markdown \
  --output reports/replication-matrix.md
```

查询单个来源：

```bash
llm-theory-lab replication-show "induction heads"
llm-theory-lab replication-show "scaling monosemanticity"
```

稳定来源 ID 是 URL 的 SHA-256 前缀，不会因为未来向时间线中插入新论文而整体重排。

## 当前首个开放模型协议：M04

M04 使用受控序列：

```text
[A, B, C, D, A]
```

对后一个 `A`，induction-style 目标位置是前一个 `A` 后面的 `B`。协议分别记录：

1. 每层每头对目标位置的平均 attention；
2. 同一 query 下其他 causal 位置的平均 attention；
3. 二者之差；
4. 得分最高的 layer/head；
5. 最终位置对 `B` 相对 distractor 的 logit margin。

运行：

```bash
python -m pip install -e ".[models]"

llm-theory-lab hf-induction \
  --model openai-community/gpt2 \
  --revision <immutable-hub-commit> \
  --samples 64
```

默认只读取本地缓存。首次下载必须显式加入 `--allow-download`。

运行结果记录请求 revision、解析到的 Hub commit、模型类、tokenizer 类、设备、层数、头数和下载策略。

## 为什么默认禁止自动下载

一个“同名模型”会随 Hub 默认分支变化。未经记录的自动下载会使：

- 今天和明天运行到不同权重；
- tokenizer 或配置悄然改变；
- 结果无法和证据 ledger 对齐；
- 用户误以为模型名本身就是不可变 revision。

因此审查级运行应使用 immutable commit SHA，并保存结果文件和运行环境。

## M04 能支持什么

若某些头稳定表现出：

$$
\operatorname{Attention}(A_{\text{later}}\rightarrow B_{\text{earlier-successor}})
>
\operatorname{mean\ control\ attention},
$$

可以说：

> 在指定模型、revision、模板和样本中，存在 induction-style attention 候选头。

它仍不能单独证明：

- 该头对预测 `B` 因果必要；
- 模型只使用这一条路径；
- 该头实现了全部 in-context learning；
- 其他模型或语言具有相同 layer/head；
- 原论文的训练相变、宏观能力跳变和完整回路已经复现。

下一阶段至少需要：

1. 对候选头做消融或输出 patch；
2. 加入相同距离但不匹配 token 的负对照；
3. 改变序列长度和 distractor 数量；
4. 使用多个随机种子和多个模型 revision；
5. 检验 attention 得分是否预测目标 logit 的变化；
6. 对前一 token 写入路径和后续读取路径做组合干预。

## CI 契约

`python scripts/validate_replication_catalog.py` 会检查：

- 仓库来源 CSV 与 wheel 内置副本逐字节一致；
- 正好覆盖 56 个唯一 URL；
- 每个来源都有稳定 ID、主题、协议和当前状态；
- 所有 protocol ID 和 experiment ID 都存在；
- 受阻项必须写明 blocker；
- 非实证来源不能伪装成精确实验复现；
- 新增来源若没有映射，CI 立即失败。

因此“新增一个链接但不说明如何验证”不再被视为完成。

## 正确的项目目标

本仓库的长期目标应写成：

> 对全部公开机制主张建立可追踪的复现路线；能精确复现的使用原始公开资产，不能精确复现的使用匹配开放模型协议，并明确记录差异、阻塞和证据等级。

不应写成：

> 已经用开源代码复现 Anthropic 的所有内部结果。

后一句在缺少原始私有权重、激活和训练资产时不可验证，也会破坏仓库最重要的证据边界。
