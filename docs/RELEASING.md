# Releasing｜发布流程

## 版本规则

项目使用语义化版本。以下位置必须一致：

```text
pyproject.toml
CITATION.cff
CHANGELOG.md
Git tag
GitHub Release
```

Evidence ledger 和 reproduction registry 各自独立版本化。破坏性 schema 变化必须有新版本和迁移说明，不能只提高包版本。

## 发布前清单

1. 从最新 `main` 创建发布分支；
2. 更新包版本、引用信息和 changelog；
3. 审查 claim ID/revision、来源映射和实验边界；
4. 审查 56 条复现地图中的覆盖程度、模式、阻塞项和下一步；
5. 运行：

```bash
make clean
make check
```

6. 打开 `reports/reproduction/`，人工检查 canonical results、ledger、coverage summary 和 manifest；
7. 若结果变化，记录原因并同步两份审查基线；
8. 若复现地图变化，运行 `python scripts/validate_reproduction_map.py --write-docs` 并审查生成 diff；
9. 通过 PR 合并；
10. 确认 main 上 CI、Documentation 和 CodeQL 全部成功。

## 创建版本标签

```bash
git switch main
git pull --ff-only
git tag -s vX.Y.Z -m "LLM Theory Lab vX.Y.Z"
git push origin vX.Y.Z
```

Release workflow 会：

1. 检查 tag 与 package version；
2. 构建 wheel 和 sdist，并执行 `twine check`；
3. 从 tag commit 重跑全部 CPU-safe 实验；
4. 校验审查基线、evidence ledger、56 条复现地图和全部 SHA-256；
5. 创建 evidence 压缩包；
6. 生成 `SHA256SUMS.txt`；
7. 保存 Actions artifact；
8. 创建或幂等更新 GitHub Release 附件。

## 发布后验证

确认：

- Release 指向正确 tag 和 commit；
- wheel、sdist 和 evidence 压缩包版本正确；
- bundle 的 `manifest.json` 记录 tag commit；
- `context/` 包含来源目录、复现地图、两个 schema 和审查基线；
- manifest 的 `source_coverage.total_sources` 为 56；
- `SHA256SUMS.txt` 与全部附件一致；
- 从全新虚拟环境安装 wheel 后运行：

```bash
llm-theory-lab list
llm-theory-lab reproduction-map --summary-only
llm-theory-lab validate-reproduction-map
llm-theory-lab run-toy --ids C01 C02
llm-theory-lab reproduce --ids C01 C02 --output-dir /tmp/llm-theory-smoke
llm-theory-lab validate-evidence /tmp/llm-theory-smoke --bundle --allow-partial
```

- changelog 和 citation 版本正确；
- Release 不包含专有权重、私有数据、凭据或真实攻击载荷。

## PyPI

当前不自动发布 PyPI。启用时应使用 Trusted Publishing 和受保护 environment，不保存长期 API token。上传前必须从实际 wheel 完成仓库外的 reproduction-map 与 evidence smoke test。

## 回滚

不要重写公开 tag。发现问题时：

1. 在 Release 明确影响范围；
2. 保留错误、不确定和失败记录；
3. 发布补丁版本；
4. 在 changelog 记录修复与迁移；
5. 只有附件损坏但代码 tag 正确时，才幂等替换附件。
