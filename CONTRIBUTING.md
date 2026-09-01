# 贡献指南

本仓库同时包含理论文档与独立实验子项目 [`code/`](code/)。任何新主张都应尽量同时提交“理论卡”和“实验卡”。

## 理论卡

```text
Claim：具体命题
Object：参数、激活、特征、头、路径、logit、token 或行为
Scope：模型、任务、输入和运行条件
Evidence：支持来源与证据等级
Alternative explanations：至少一个替代解释
Falsifier：什么结果会削弱该命题
Forbidden inference：不能从该命题推出什么
```

## 实验卡

```text
Intervention：改变什么
Invariants：保持什么不变
Positive control：应当出现效应的条件
Negative control：不应出现效应的条件
Metric：看结果前定义的指标
Seeds / samples：随机性和样本规模
Failure cases：失败样本必须保留
Conclusion boundary：该实验最多支持什么
```

## 提交要求

1. 把事实、作者解释、仓库综合和个人假设分开；
2. 机制主张附原始来源，并注明模型、任务和版本；
3. 不用单个 probe、单次输出或一张归因图宣称完整机制；
4. 不把 toy experiment 的 `pass` 写成“所有大模型已证明”；
5. 新代码包含类型提示、错误处理、正负对照和测试；
6. 开放模型实验保存 tokenizer、token IDs、revision、seed、设备和依赖版本；
7. 安全研究不提交真实越狱载荷、危险步骤或自动攻击优化；
8. 数学公式使用 GitHub 支持的 `$...$` 和 `$$...$$`。

提交前运行：

```bash
python scripts/normalize_markdown_math.py --check
python scripts/validate_catalog.py
python scripts/validate_source_digest.py

cd code
pip install -e ".[dev]"
pytest
llm-theory-lab run-toy
```

文献状态建议使用：`paper`、`research_update`、`tool`、`cross_post`、`infrastructure`、`predecessor`。
