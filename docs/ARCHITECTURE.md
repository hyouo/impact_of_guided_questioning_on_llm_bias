# Repository Architecture｜仓库架构

## 设计目标

仓库不是把“理论、代码和链接”放进同一个目录就结束，而是维持一条可审计的学习与研究链：

```text
课程解释一个机制对象
→ 实验把命题操作化
→ 练习检查能否独立推导和设计对照
→ 参考层保留来源、案例和方法边界
→ CI 验证这些入口没有再次分叉
```

## 内容分层

```text
docs/course/            8 章主课程；初学者的唯一连续入口
docs/labs/              与 C01–C09 对应的指导式实验
docs/exercises/         推导、反例、研究设计、答案和能力量表
docs/reference/         深度综合、案例、方法、术语和来源目录
docs/experiments/       实验设计协议与结果格式
sources/                机器可读的 Transformer Circuits 来源目录
examples/               最小可运行脚本
src/llm_theory_lab/     实验包、注册表、报告和 CLI
tests/                  单元与集成测试
scripts/                来源、链接、仓库结构和学习路径检查
.github/                CI、文档部署、安全扫描和贡献模板
```

`course/` 解释“应该怎样理解”；`labs/` 解释“怎样亲手验证”；`exercises/` 检查“能否脱离提示独立分析”；`reference/` 回答“原始证据和更深细节在哪里”。长篇来源摘要不再占据课程主线。

## 代码层

`llm_theory_lab` 的职责保持窄而明确：

- `registry.py`：实验 ID、课程位置、理论主张、直觉、反证条件和禁止外推的单一入口；
- `result.py`：结构化检查、实验结果和 Markdown/JSON 报告；
- `math_utils.py`：数值稳定的基础运算；
- `repro.py`：运行环境和复现元数据；
- `experiments/`：每个可独立运行的透明实验与可选模型实验；
- `cli.py`：`list`、`roadmap`、`explain`、`run-toy` 等稳定入口。

核心包只依赖 NumPy。PyTorch、Transformers 和 Safetensors 属于 `models` 可选依赖，因此数学实验不会被大型模型框架绑死。

## 理论—实验—练习契约

每个核心实验必须回答：

```text
Claim               它检验哪条明确命题？
Object               参数、激活、特征、头、路径、logit 还是行为？
Intervention         改变什么？
Invariants           保持什么不变？
Controls             正、负和随机对照是什么？
Metric               什么量决定结果？
Falsifier            什么结果会削弱命题？
Allowed conclusion   最多能得出什么？
Forbidden inference  即使通过也不能推出什么？
Course location      学习者在哪里获得所需概念？
```

代码侧单一入口是 `src/llm_theory_lab/registry.py`。文字侧入口是：

- [课程导览](course/index.md)；
- [实验导览](labs/index.md)；
- [练习册](exercises/index.md)；
- [方法与解释矩阵](reference/methods-matrix.md)。

修改实验时，必须同步更新注册表、对应课程或实验手册、测试以及必要的练习；`scripts/check_learning_path.py` 会验证这条链。

## 质量门槛

本地 `make check` 和 CI 共同检查：

1. Ruff lint 与格式；
2. 数学 Markdown 和内部链接；
3. 56 条来源目录与逐条摘要覆盖；
4. 课程、实验、练习和示例完整性；
5. Python 3.10、3.12、3.14 测试；
6. C01–C09 全部透明实验；
7. learner-facing CLI；
8. MkDocs strict 构建；
9. wheel/sdist 构建和元数据；
10. CodeQL 与文档站发布。

一次性迁移工作流、重复编号章节和嵌套 `code/` 项目被视为禁止路径，避免仓库再次回到多入口状态。

## 生成产物与证据保存

默认不提交：

```text
reports/
runs/
model_cache/
build/
dist/
site/
coverage.xml
```

需要长期保存的正式结果应经过单独审查，并至少记录：代码 commit、包版本、模型和 tokenizer revision、完整输入或数据哈希、随机种子、干预位置、指标、全部结果状态和结论边界。失败、跳过和不确定结果不能被成功运行覆盖。
