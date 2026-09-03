# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 的结构，并使用语义化版本号。

## [Unreleased]

### Added

- 预留开放模型配对数据、跨模型 patching、SAE 评价与训练动力学实验。

## [0.4.0] - 2026-09-03

### Added

- C10 可逆基底变换实验，精确区分函数不变性与内部坐标不唯一。
- C11 冗余路径实验，展示 accuracy 饱和如何掩盖连续 margin 的因果变化。
- C12 steering 控制实验，加入剂量、反向、随机方向和正交方向基线。
- C01–C12 一对一实验手册，不再让多个机制共用一个实验页面。
- 基底、冗余与 steering 的进阶练习和答案。
- 三个新实验的最小可运行示例和针对性测试。

### Changed

- 第 4 章加入基底不唯一与 privileged basis 的明确边界。
- 第 6 章加入消融假阴性、连续指标、联合消融和 steering 特异性控制。
- README、课程地图、实验导航和 CLI 更新为十二个透明实验。
- 学习路径检查改为从实验注册表验证唯一手册、课程映射和练习覆盖。

### Removed

- 将 C05/C09 混在一起的旧实验页面；两者现在各有独立手册。

## [0.3.0] - 2026-09-03

### Added

- 按因果顺序组织的 8 章大模型机制课程。
- 5 个与透明实验直接对应的指导式实验手册。
- 覆盖数学推导、机制反例、实验设计与安全路由的练习册。
- 带完整推导、证据边界和自我评分量表的答案解析。
- 5 个最小可运行示例。
- CLI `roadmap`、`explain` 与实验分类入口。
- 课程、实验、练习、示例和参考层之间的一致性检查。
- 独立的严格文档构建与 GitHub Pages 发布工作流。

### Changed

- 将平铺的编号文档重组为 `course/`、`labs/`、`exercises/` 和 `reference/` 四层。
- 将 README 从文件清单改为按 1 小时、1 天和研究使用划分的学习入口。
- 为每个 C01–C09 实验补充直觉、反证条件、课程位置和禁止外推。
- 让 CI 同时验证学习路径、learner-facing CLI、严格文档构建和实验报告。
- 将包描述与引用元数据更新为课程和实验平台定位。

### Removed

- 重复的顶层理论章节和已迁移的 `code/` 占位目录。
- 一次性内容整合工作流及其他只服务迁移过程的临时入口。

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

[Unreleased]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/releases/tag/v0.2.0
[0.1.0]: https://github.com/hyouo/impact_of_guided_questioning_on_llm_bias/commits/4510c197b46a6dee52590ddb4b655cdd69b2779e
