# Maintainer Guide｜维护者指南

## 推荐仓库设置

在 GitHub Settings 中建议启用：

- 默认分支 `main`；
- Pull Request 后合并；
- squash merge；
- 合并后自动删除分支；
- Dependabot alerts 和 security updates；
- Secret scanning；
- 私密漏洞报告；
- 分支规则要求 CI 和 CodeQL 成功；
- 阻止 force push 和删除 `main`。

建议必需检查：

```text
quality
tests (3.10)
tests (3.12)
tests (3.14)
codeql
```

实际检查名称应以 GitHub Actions 页面为准。

## Issue 分类

- `bug`：实现缺陷；
- `theory`：理论、证据或来源问题；
- `experiment`：实验提案；
- `documentation`：文档；
- `security`：仅用于不含敏感细节的跟踪，漏洞本体必须私密。

## 依赖维护

Dependabot 每周检查 Python 和 GitHub Actions。合并依赖更新前：

1. 阅读上游变更；
2. 确认 Python 支持范围；
3. 运行完整 CI；
4. 检查实验数值变化是否来自依赖而非理论；
5. 在必要时更新 `CHANGELOG.md`。

## 科学完整性

不删除“不支持”“不确定”或失败结果来制造一致叙事。若修改实验阈值，应在代码和文档中解释原因，并避免查看结果后无记录地调整。

## 发布

发布前按 [`RELEASING.md`](RELEASING.md) 完成版本、变更日志、引用文件、测试和构建检查。
