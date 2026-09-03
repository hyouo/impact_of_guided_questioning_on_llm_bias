# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 的结构，并使用语义化版本号。

## [Unreleased]

### Added

- 预留开放权重模型的跨模板、跨模型和跨 checkpoint 复现实验。

## [0.3.0] - 2026-09-03

### Added

- 八模块主课程，建立明确的先修关系、学习目标、自测与综合项目。
- C01–C09 一对一实验手册，包含运行前预测、关键指标、修改任务和结论边界。
- 机器可读课程注册表、`course`/`explain` CLI 和课程一致性校验。
- 课程、实验、练习、深度参考三层导航。

### Changed

- README 和文档首页改为学习导向，不再要求读者从长文献目录开始。
- 将既有长篇理论保留为深度参考，由主课程按需要链接。
- 包版本、引用信息、发布说明和项目描述更新到 0.3.0。

### Fixed

- 修复 `THREAT_MODEL.md` 导航缺失和跨文档链接导致的 MkDocs strict 构建失败。
- CI 现在校验课程、实验、文档和代码之间的映射。

### Removed

- 已完成任务的一次性自修改 workflow。
- 过期的嵌套 `code/` 迁移占位目录。

## [0.2.0] - 2026-09-02

### Added

- 标准根目录 `src/` 包布局与根级 `pyproject.toml`。
- Ruff、pytest、coverage、build、twine 和 MkDocs 配置。
- CI 测试矩阵、CodeQL、发布构建和 Dependabot。
- Issue 表单、PR 模板、CODEOWNERS 和社区健康文件。
- 仓库结构、开发、发布和维护者文档。
- 内部 Markdown 链接与仓库契约自动检查。

### Changed

- 将原 `code/` 子项目迁移到标准根目录。
- 统一安装、测试、文档和实验命令。
- 更新 README、贡献指南、引用信息和实验路径。

### Removed

- 嵌套 Python 项目配置；`code/` 仅保留迁移说明。

## [0.1.0] - 2026-09-01

### Added

- Transformer Circuits 来源目录与中文理论综合。
- C01–C09 透明实验以及 M01–M03 开放模型实验入口。
- 实验协议、结果结构和基础 CI。

[Unreleased]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/releases/tag/v0.3.0
[0.2.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/releases/tag/v0.2.0
[0.1.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/commits/4510c197b46a6dee52590ddb4b655cdd69b2779e
