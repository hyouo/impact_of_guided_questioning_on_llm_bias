# 贡献指南

本仓库接受理论修订、来源补充、术语澄清、反例、玩具模型与可复现实验。

提交内容应满足：

1. 把事实、作者解释、仓库综合和个人假设分开；
2. 机制主张附原始来源，并在必要时注明模型、任务和版本；
3. 不用单个 probe、单次输出或一张归因图宣称完整机制；
4. 新实验包含对照、随机种子、失败案例和反证条件；
5. 安全研究不提交可直接复用的越狱载荷、真实秘密或危险步骤；
6. 修改 `sources/transformer_circuits_catalog.csv` 后运行：

```bash
python scripts/validate_catalog.py
pytest
```

文献状态建议使用：`paper`、`research_update`、`tool`、`cross_post`、`infrastructure`、`predecessor`。
