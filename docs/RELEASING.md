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

包运行时版本由 `importlib.metadata` 读取，避免在源码中重复维护。

## 发布前清单

1. 从最新 `main` 创建发布分支；
2. 更新 `pyproject.toml` 与 `CITATION.cff`；
3. 将 `CHANGELOG.md` 的 Unreleased 内容移入新版本；
4. 检查 README、文档路径和安装命令；
5. 运行完整门槛：

```bash
make clean
make check
```

6. 通过 Pull Request 合并到 `main`；
7. 确认 `main` 上的 CI 与 CodeQL 成功。

## 创建版本标签

建议创建签名标签：

```bash
git switch main
git pull --ff-only
git tag -s vX.Y.Z -m "LLM Theory Lab vX.Y.Z"
git push origin vX.Y.Z
```

标签推送后，`.github/workflows/release.yml` 会自动：

1. 构建 wheel 和 source distribution；
2. 执行 `twine check`；
3. 生成 `SHA256SUMS.txt`；
4. 保存 GitHub Actions artifact；
5. 创建 GitHub Release，并附加构建产物；
6. 在重跑时更新已有 Release 的附件，而不是创建重复版本。

`workflow_dispatch` 只构建和保存 artifact；只有符合 `v*.*.*` 的标签会发布 GitHub Release。

## 发布后验证

确认：

- GitHub Release 指向正确 tag 和 commit；
- wheel 与 sdist 文件名包含正确版本；
- `SHA256SUMS.txt` 与附件一致；
- 从全新虚拟环境安装 wheel 后，`llm-theory-lab list` 和 `llm-theory-lab run-toy` 可运行；
- `CHANGELOG.md` 的版本链接有效；
- `CITATION.cff` 显示正确版本和发布日期。

## PyPI

当前工作流不会自动发布到 PyPI。未来启用时应使用 PyPI Trusted Publishing 和 GitHub environment protection，不在仓库 Secrets 中长期保存 API token。

## 回滚

不要重写已经公开的 tag。发现发布问题时：

1. 在 GitHub Release 中明确标注受影响范围；
2. 修复问题并发布补丁版本；
3. 在 `CHANGELOG.md` 中记录修复与迁移建议；
4. 只有构建附件损坏、而代码 tag 正确时，才使用发布工作流的幂等上传覆盖附件。
