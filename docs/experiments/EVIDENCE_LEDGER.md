# 证据台账与可复现运行

仓库的成熟标准不是“实验数量增加”，而是每条机制说法都能追溯到：

```text
公开来源
→ 明确 claim ID
→ 可执行实验 ID
→ 固定运行入口
→ 原始结果与预注册检查
→ 数据/生成器哈希
→ 代码 revision
→ 结论边界
```

证据台账把这条链保存为机器可读记录。课程文字不能绕过台账自行提高证据等级。

## 目标范围

本项目追踪 Anthropic、Transformer Circuits 及相关公开材料中能够被明确陈述和检验的结果。对每条公开 claim，仓库应把状态标为以下之一：

- `reproduced-exactly`：定义、模型、数据和指标都可公开获得，并按原协议复现；
- `reproduced-on-open-model`：在公开模型上复现了同类预测，但不是原专有模型的逐字复刻；
- `transparent-proxy`：用完全透明系统验证数学关系、结构可能性或逻辑反例；
- `partial`：只复现了论文链条的一部分；
- `blocked-public-assets`：缺少公开权重、训练数据、特征字典或内部接口；
- `not-yet-implemented`：公开材料足够，但代码尚未完成。

“覆盖所有公开理论”意味着没有静默遗漏：每条来源都进入覆盖矩阵，并且具有上述显式状态。它不意味着能够从公开信息重建 Claude 的私有权重、未发布训练数据或未公开的内部分析资产。

## 一次完整复现

```bash
python -m pip install -e ".[dev,docs]"
llm-theory-lab reproduce --output-dir reports/reproduction
llm-theory-lab validate-evidence reports/reproduction --bundle
```

`reproduce` 独立运行每个 CPU-safe 实验。某个实验异常时，运行器会写入 `error` 记录并继续运行其余实验，而不是让前面已经产生的证据消失。

输出目录包含：

```text
results.json             完整结果，含时间和运行环境
report.md                面向人工审查的解释报告
canonical-results.json   去除时间和环境噪声后的漂移基线
evidence-ledger.json     claim、来源、哈希、状态和结论边界
evidence-matrix.md       从台账生成的快速矩阵
manifest.json            文件大小、SHA-256、代码 revision 和运行环境
context/                 schema、claim-source 索引、审查基线与可选来源快照
```

## 一条记录保存什么

每条记录至少包含：

- `claim_id`、`claim_revision` 与 `experiment_id`；
- 与代码注册表完全一致的 claim 文本；
- 原始公开来源 URL；
- 模型或透明系统 revision，以及 `reproduction_status`；
- runner 路径、默认参数和由此计算的 `dataset_sha256`；
- `code_revision`；
- 完整指标作为 `effect_size`；
- 不确定性声明；
- 预注册检查、阈值/预期和观测值；
- 偏离协议的 `deviations`；
- 原始 artifact 的选择器和 SHA-256；
- 该结果明确不能支持的外推。

透明玩具实验通常不能从一次固定种子运行估计总体置信区间。因此台账不会伪造误差条，而是把不确定性写成 `not-estimated` 并解释原因。未来引入真实数据集时，记录必须改为样本级或重复运行得到的区间。

## 状态不能混用

- `pass`：预注册检查通过；
- `fail`：预注册检查失败；
- `observational`：只做观察，不作二元判断；
- `skipped`：缺依赖、模型或合法运行条件；
- `inconclusive`：现有指标无法区分支持与反证；
- `error`：代码、下载或运行环境异常。

`error` 不是理论被反驳，`skipped` 不是零效应，`pass` 也不是跨模型定律。

## 防止结果和叙述漂移

CI 和本地 `make evidence` 每次执行：

```bash
python scripts/check_evidence_baseline.py
```

该命令会：

1. 重新运行 C01–C12；
2. 验证来源 URL 都在正式来源目录中；
3. 校验 ledger 与 bundle 内部 SHA-256；
4. 将 `canonical-results.json` 与审查过的基线比较；
5. 在结果变化时失败，而不是自动覆盖基线。

结果变化可能来自正确的 bug fix、数值依赖变化、默认参数改变或科学含义改变。维护者必须审查差异后才可以更新基线。CI 不会替维护者把“新的绿色结果”自动升级成更高证据等级。

## Schema 与迁移

机器可读 schema 位于：

```text
schemas/evidence-ledger-v1.schema.json
```

破坏性字段变化必须新增 schema 版本和迁移脚本，不能原地改变旧记录的含义。`claim_id` 不变而文字或判定规则发生实质变化时，必须提高 `claim_revision`。版本控制中的旧 ledger 和失败记录应保留；更正通过新增记录或明确迁移完成。

仓库中的 schema 与审查基线各有一份 package-data 镜像，`scripts/check_repository.py` 会逐字节比较两份副本，防止 wheel 与源码仓库的证据语义分叉。

## 发布要求

正式 tag 的 Release artifact 应至少包含：

- wheel 与 sdist；
- `SHA256SUMS.txt`；
- 来源目录快照；
- 实验注册表和 schema；
- `canonical-results.json`；
- `evidence-ledger.json`；
- `manifest.json`。

发布产物不得包含专有模型权重、私有数据、凭证、真实攻击载荷或未经授权的数据集。
