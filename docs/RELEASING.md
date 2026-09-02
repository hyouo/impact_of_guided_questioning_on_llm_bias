# Releasing｜发布流程

## 版本规则

使用语义化版本。版本必须在下列位置一致：

```text
pyproject.toml
CITATION.cff
CHANGELOG.md
Git tag
GitHub Release
```

包运行时版本由 `importlib.metadata` 读取，避免在源码中重复维护。

## 发布清单

1. 从最新 `main` 创建发布分支；
2. 更新 `pyproject.toml` 与 `CITATION.cff`；
3. 将 `CHANGELOG.md` 的 Unreleased 内容移入新版本；
4. 运行：

```bash
make clean
make check
```

5. 合并发布 PR；
6. 创建签名或受保护的标签：

```bash
git tag -s vX.Y.Z -m "LLM Theory Lab vX.Y.Z"
git push origin vX.Y.Z
```

7. 确认 `release.yml` 成功构建 wheel 和 sdist；
8. 从 CI artifact 检查包内容；
9. 创建 GitHub Release，并复制对应变更日志；
10. 若未来发布到 PyPI，使用 Trusted Publishing，不在仓库中保存长期 API token。

## 回滚

发现发布问题时不要重写已经公开的 tag。发布补丁版本，并在 GitHub Release 和 `CHANGELOG.md` 中明确说明受影响版本。
