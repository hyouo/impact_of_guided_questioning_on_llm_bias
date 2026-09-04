# 证据台账、覆盖地图与可复现运行

仓库使用两套互补的机器可读记录：

```text
复现地图：每条公开来源目前做到哪里
证据台账：某一次具体实验运行产生了什么证据
```

两者不能互相替代。来源被列入地图，不代表实验已经运行；实验通过，也不代表该来源的所有结果都被覆盖。

## 两个状态轴

### 覆盖程度

- `implemented-complete`：该来源登记的主要结果族都已有相应模式下的验证协议；
- `implemented-partial`：至少有一个相关协议，但没有覆盖完整结果集；
- `planned`：已进入路线图，尚无验证协议；
- `reference-only`：教学、方法论、工具、基础设施或历史材料，不伪造实验状态。

### 当前复现模式

- `exact-reproduction`：公开等价的模型、数据、指标和协议在声明容差内匹配；
- `open-model-analogue`：在固定开放权重上测试同类方向性预测，不冒充原始 Claude 数值；
- `transparent-proxy`：透明数学系统或 toy 检验结构命题、反例或方法边界；
- `reference`：只用于课程、方法或历史背景。

因此，一个来源可以同时是 `implemented-partial` 和 `open-model-analogue`。前者回答“覆盖多少”，后者回答“用什么模式覆盖”。

完整 56 条地图位于：

```text
reproductions/transformer_circuits_v1.json
docs/reference/reproduction-map.md
schemas/reproduction-registry-v1.schema.json
```

验证与查询：

```bash
python scripts/validate_reproduction_map.py
llm-theory-lab validate-reproduction-map
llm-theory-lab reproduction-map --status planned --priority P0
```

## 从来源到一次运行

```text
公开来源
→ 复现地图中的 source ID、可行性和目标模式
→ 稳定 claim ID / revision
→ 可执行 experiment ID
→ 固定 runner、模型/系统 revision 和数据
→ 原始结果与预注册检查
→ 数据、结果、代码和文件哈希
→ 结论边界
```

课程文字不能绕过这条链自行提高证据等级。

## 一次完整透明复现

```bash
python -m pip install -e ".[dev,docs]"
llm-theory-lab reproduce --output-dir reports/reproduction
llm-theory-lab validate-evidence reports/reproduction --bundle
```

某个实验异常时，运行器写入 `error` 并继续其余实验。输出包含：

```text
results.json             完整结果，含时间和运行环境
report.md                面向人工审查的解释报告
canonical-results.json   去除时间和环境噪声后的漂移基线
evidence-ledger.json     claim、来源、哈希、状态和结论边界
evidence-matrix.md       从台账生成的快速矩阵
manifest.json            文件大小、SHA-256、代码 revision 和来源覆盖摘要
context/                 schema、审查基线、来源目录与 56 条复现地图快照
```

`validate-evidence` 不只检查文件哈希，还会重新验证 bundle 内的来源目录和复现地图语义。即使攻击者重算 manifest，也不能把带有协议的来源静默改成 `planned`，或把透明代理改写成精确复现。

## Evidence ledger 一条记录保存什么

- `claim_id`、`claim_revision` 与 `experiment_id`；
- 与代码注册表一致的 claim 文本；
- 原始来源 URL；
- 模型或透明系统 revision，以及 `reproduction_status`；
- runner、默认参数和 `dataset_sha256`；
- `code_revision` 与 `result_sha256`；
- 完整指标、不确定性声明和预注册检查；
- 协议偏离 `deviations`；
- artifact 选择器与哈希；
- 该结果不能支持的外推。

透明固定输入通常不能估计总体置信区间，所以台账写 `not-estimated` 并说明原因，而不是制造误差条。真实数据或多随机种子实验必须记录样本级结果和区间。

## 运行状态不能混用

- `pass`：预注册检查通过；
- `fail`：预注册检查失败；
- `observational`：只做观察；
- `skipped`：缺少依赖、模型或合法运行条件；
- `inconclusive`：指标不足以区分支持与反证；
- `error`：代码、下载或环境异常。

`error` 不是理论被反驳，`skipped` 不是零效应，`pass` 也不是跨模型定律。

## 防止结果、覆盖和叙述漂移

CI 依次执行：

```bash
python scripts/validate_catalog.py
python scripts/validate_source_digest.py
python scripts/validate_reproduction_map.py
python scripts/check_evidence_baseline.py
```

它会验证：

1. 56 条来源没有静默遗漏或重复；
2. 复现地图逐条匹配来源目录且哈希一致；
3. C01–C12 的来源链接与协议映射双向一致；
4. repo 与 wheel 中的 registry/schema/catalog 字节相同；
5. C01–C12 重跑结果与审查基线一致；
6. bundle 内 ledger、map、manifest 和所有文件哈希一致；
7. 结果变化时失败，而不是自动覆盖基线。

## 提高覆盖状态的门槛

来源不能仅凭“代码能跑”升级。PR 至少要提供：

- 固定模型或架构 revision；
- 固定数据集/生成器及哈希；
- 原协议与本实现的逐项差异；
- 预注册指标、容差、正负对照和反证条件；
- 原始与规范化结果；
- evidence ledger 记录和可验证 artifact；
- 失败样本、不确定性与跨种子结果；
- 仍未覆盖的原论文结果清单。

从 `open-model-analogue` 升为 `exact-reproduction`，还必须证明模型、数据、指标和协议确实公开等价。方向一致不够。

## Schema 与迁移

```text
schemas/evidence-ledger-v1.schema.json
schemas/reproduction-registry-v1.schema.json
```

破坏性变化必须新增 schema 版本和迁移脚本。`claim_id` 不变而文字、范围、指标或判定规则实质改变时，必须提高 `claim_revision`。旧 ledger、旧地图快照和失败结果应保留。

## 发布要求

正式 Release artifact 至少包含：

- wheel、sdist 与 `SHA256SUMS.txt`；
- 来源目录、复现地图和两个 schema；
- canonical results、evidence ledger、matrix 与 manifest；
- 明确的原始资产缺口和模式标签。

发布产物不得包含专有模型权重、私有数据、凭证、真实攻击载荷或未经授权的数据集。
