# 贡献指南

项目同时包含课程、实验、练习、研究参考、证据台账和逐来源复现地图。贡献必须让：

```text
主张 → 来源 → 复现模式 → 代码 → 结果 → 学习目标 → 结论边界
```

保持一致。

## 开发环境

```bash
git clone https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias.git
cd impact_of_guided_questioning_on_llm_bias

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,docs]"
pre-commit install
```

常用命令：

```bash
make format            # 自动格式化
make lint              # 静态检查
make test              # 单元测试
make learning          # 课程—实验—练习契约
make reproduction-map  # 56 条公开来源覆盖契约
make evidence          # 重跑、校验证据并比较审查基线
make docs              # 严格构建文档
make check             # 完整本地质量门槛
```

## 内容放在哪里

不要在 `docs/` 根目录创建第二条学习入口。

| 内容 | 正确位置 | 必须同步 |
|---|---|---|
| 核心心智模型 | 现有 `docs/course/` 章节 | 学习目标、自测、来源和边界 |
| 可运行教学实验 | `src/llm_theory_lab/experiments/` 与 `docs/labs/` | 注册表、测试、练习和 evidence baseline |
| 课后题 | `docs/exercises/` | 答案、解析和课程映射 |
| 深度综合、案例、术语 | `docs/reference/` | 原始来源和证据状态 |
| 运行证据 | `evidence/`、`schemas/evidence-*` | package-data 镜像和漂移理由 |
| 逐来源复现状态 | `reproductions/`、`schemas/reproduction-*` | 生成文档、package-data 镜像和验证测试 |
| 项目维护信息 | 现有项目文档 | 不进入课程主线 |

## 理论贡献

至少说明：

```text
Claim ID / revision
精确主张与分析对象
适用模型、任务、输入和位置
原始来源与证据等级
当前复现模式
至少一个替代解释
反证条件
禁止外推
学习者应获得的能力
```

请区分原论文结果、作者解释、仓库综合和个人假设。月度研究更新、玩具模型和正式论文不能等权引用。已有 claim 的文字、范围、指标或判定规则实质改变时必须提高 `claim_revision`。

## 实验贡献

新实验至少包含：

```text
Intervention       改变什么
Invariants         保持什么不变
Positive control   什么条件应出现效应
Negative control   什么条件不应出现效应
Metric             看结果前定义的指标
Seeds / samples    随机性与样本规模
Failure cases      失败和不确定结果
Conclusion boundary 最多支持什么
```

还必须：

- 固定或保存模型 revision、tokenizer、模板、数据、依赖、seed 和设备；
- 为错误输入、正常路径和关键边界添加测试；
- 在 `registry.py` 连接 claim、来源、课程、手册、反证条件和禁止外推；
- 在 evidence ledger 中保留 `fail`、`error`、`inconclusive` 和 `skipped`；
- 不把 `pass` 写成所有模型上的定律。

## 复现地图状态升级

机器可读入口：

```text
reproductions/transformer_circuits_v1.json
```

覆盖程度和复现模式必须分开。一个开放模型类比可以是“部分覆盖”，但不能因此变成“原始实验精确复现”。

状态升级 PR 必须提供：

1. 固定模型或架构 revision；
2. 固定数据集/生成器与哈希；
3. 原始公开协议、代码和许可证审计；
4. 本实现相对原协议的逐项偏离；
5. 预注册指标、容差、正负对照和反证条件；
6. 原始结果、canonical result、ledger 与 manifest；
7. 多 seed 或样本级不确定性；
8. 仍未覆盖的结果清单；
9. 对应 `coverage_status`、`current_modes`、`blockers` 和 `next_step` 更新。

从 `open-model-analogue` 升级为 `exact-reproduction`，必须证明模型、数据、指标和协议公开等价。方向一致、输出相似或图形相似都不够。

修改 registry 后运行：

```bash
python scripts/validate_reproduction_map.py --write-docs
python scripts/validate_reproduction_map.py
```

不要手工编辑生成的 `docs/reference/reproduction-map.md`。

## Evidence ledger 与基线

```bash
llm-theory-lab reproduce --output-dir reports/reproduction
llm-theory-lab validate-evidence reports/reproduction --bundle
python scripts/check_evidence_baseline.py
```

规则：

1. `results.json`、ledger、matrix 和 manifest 是生成产物；
2. `evidence/baseline-v1/Cxx.json` 只在理解差异后更新；
3. 更新基线必须同步 package-data 镜像；
4. PR 要说明变化来自 bug fix、默认参数、依赖数值、实验设计还是理论语义；
5. schema 破坏性变化必须新增版本和迁移说明；
6. 公开资产不足时使用明确 blocker，不得把透明代理写成 Claude 原实验复现。

## 文档与来源

```bash
python scripts/validate_catalog.py
python scripts/validate_source_digest.py
python scripts/validate_reproduction_map.py
python scripts/check_learning_path.py
python scripts/check_markdown_links.py
python scripts/check_evidence_baseline.py
```

数学公式使用 `$...$` 与 `$$...$$`。使用准确转述并链接原始来源，不复制大段受版权保护内容。

## 安全边界

允许：无害代理、拒绝/权限路由分析、检测、审计、缓解和防御性实验。

不接受：真实危险操作步骤、可直接复用越狱载荷、秘密提取、凭据、自动攻击优化或绕过生产系统的代码。

## Pull Request 检查表

- [ ] `make check` 通过；
- [ ] 新行为有测试，解析器有畸形和篡改测试；
- [ ] 文档、claim、来源、协议和代码路径一致；
- [ ] 新主张有范围、反证条件与禁止外推；
- [ ] 课程改动有学习目标、自测或练习；
- [ ] 没有创建重复入口或文档孤岛；
- [ ] 失败案例和限制没有被删除；
- [ ] 复现状态升级有完整审计材料；
- [ ] 基线变化有人工审查理由并同步 package-data；
- [ ] `CHANGELOG.md` 已更新；
- [ ] 不包含秘密、模型权重、缓存或大型生成文件。

维护和发布规则见 [`GOVERNANCE.md`](GOVERNANCE.md) 与 [`docs/RELEASING.md`](docs/RELEASING.md)。
