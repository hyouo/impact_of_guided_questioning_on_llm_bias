# Releasing｜发布流程

## 版本规则

项目使用语义化版本。版本必须在下列位置保持一致：

```text
pyproject.toml
CITATION.cff
CHANGELOG.md
Git tag
GitHub Release
```

包运行时版本由 `importlib.metadata` 读取，避免在源码中重复维护。Evidence ledger schema 独立版本化；破坏性 schema 变化不能仅靠提高包版本替代迁移说明。

## 发布前清单

1. 从最新 `main` 创建发布分支；
2. 更新 `pyproject.toml` 与 `CITATION.cff`；
3. 将 `CHANGELOG.md` 的 Unreleased 内容移入新版本；
4. 检查 README、文档路径和安装命令；
5. 审查 `claim_id`、`claim_revision`、来源映射和复现类型；
6. 运行完整门槛：

```bash
make clean
make check
```

7. 打开 `reports/reproduction/`，人工审查 canonical result、ledger、matrix 和 manifest；
8. 若结果有变化，记录原因并同步两份审查基线：

```text
evidence/baseline-v1/Cxx.json
src/llm_theory_lab/data/baseline-v1/Cxx.json
```

9. 通过 Pull Request 合并到 `main`；
10. 确认 `main` 上的 CI、Documentation 与 CodeQL 成功。

## 创建版本标签

建议创建签名标签：

```bash
git switch main
git pull --ff-only
git tag -s vX.Y.Z -m "LLM Theory Lab vX.Y.Z"
git push origin vX.Y.Z
```

标签推送后，`.github/workflows/release.yml` 会自动：

1. 检查 tag 与 package version 一致；
2. 构建 wheel 和 source distribution；
3. 执行 `twine check`；
4. 从 tag 对应 commit 重新运行全部 CPU-safe 实验；
5. 校验 evidence ledger、审查基线和 bundle 内全部 SHA-256；
6. 创建包含来源快照、schema、canonical results、ledger、matrix 与 manifest 的 evidence 压缩包；
7. 生成 `SHA256SUMS.txt`；
8. 保存 GitHub Actions artifact；
9. 创建 GitHub Release，并附加构建产物；
10. 在重跑时更新已有 Release 的附件，而不是创建重复版本。

`workflow_dispatch` 只构建和保存 artifact；只有符合 `v*.*.*` 的标签会发布 GitHub Release。

## 发布后验证

确认：

- GitHub Release 指向正确 tag 和 commit；
- wheel 与 sdist 文件名包含正确版本；
- evidence 压缩包中的 `manifest.json` 记录该 tag commit；
- evidence 压缩包同时包含 `context/`、`canonical-results.json` 和 `evidence-ledger.json`；
- `SHA256SUMS.txt` 与全部附件一致；
- 从全新虚拟环境安装 wheel 后，以下命令可运行：

```bash
llm-theory-lab list
llm-theory-lab run-toy --ids C01 C02
llm-theory-lab reproduce --ids C01 C02 --output-dir /tmp/llm-theory-smoke
llm-theory-lab validate-evidence /tmp/llm-theory-smoke --bundle --allow-partial
```

- `CHANGELOG.md` 的版本链接有效；
- `CITATION.cff` 显示正确版本和发布日期；
- Release 不包含模型权重、私有数据、凭据或真实攻击载荷。

## PyPI

当前工作流不会自动发布到 PyPI。未来启用时应使用 PyPI Trusted Publishing 和 GitHub environment protection，不在仓库 Secrets 中长期保存 API token。发布到 PyPI 前还应从实际 wheel 安装并完成上面的仓库外 evidence smoke test。

## 回滚

不要重写已经公开的 tag。发现发布问题时：

1. 在 GitHub Release 中明确标注受影响范围；
2. 保留出错或不确定的 ledger 记录；
3. 修复问题并发布补丁版本；
4. 在 `CHANGELOG.md` 中记录修复与迁移建议；
5. 只有构建附件损坏、而代码 tag 正确时，才使用发布工作流的幂等上传覆盖附件。
