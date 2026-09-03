# Development Guide｜开发指南

## 环境

支持 Python 3.10 及以上版本。推荐在虚拟环境中开发：

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,docs]"
pre-commit install
```

## 日常循环

小改动先运行最相关的检查，提交前再运行完整门槛：

```bash
make format
make test
make learning
make check
```

常见局部命令：

```bash
pytest tests/test_registry.py -q
llm-theory-lab explain C04
llm-theory-lab run-toy --ids C04 --output-dir reports/dev-c04
python scripts/check_learning_path.py
python -m mkdocs build --strict
```

## 内容开发顺序

修改一个机制主题时，按以下顺序判断：

```text
现有课程章节是否已经容纳该概念？
→ 需要新的解释、反例还是实验？
→ 注册表是否要改变？
→ 实验报告是否能显示反证条件与禁止外推？
→ 是否需要练习题检查真正理解？
→ 原始来源和证据等级是否清楚？
```

不要为每个新想法创建新的顶层 Markdown。课程解释核心概念，实验手册解释操作化，练习检查迁移能力，长篇材料进入 `docs/reference/`。

## 代码规范

- Ruff 负责 import 排序、lint 和格式化；
- 公共函数应有类型提示和简明 docstring；
- 错误信息应说明预期值与实际值；
- 核心实验不得依赖网络；
- 可选模型依赖必须延迟导入，并提供明确安装提示；
- 结果必须通过 `ExperimentResult` 或兼容结构输出；
- 实验的课程位置、直觉、反证条件和禁止外推应登记在 `registry.py`。

## 测试策略

测试分为：

1. 数学恒等式与输入校验；
2. 实验注册表和 CLI；
3. 报告序列化及学习上下文；
4. C01–C09 的预注册检查；
5. 课程—实验—练习—示例契约；
6. 包构建和文档严格构建。

开放模型下载不进入默认 CI。新增模型适配时，至少提供无网络单元测试或可注入的假对象，并把网络、模型 revision 和 `trust_remote_code` 决策显式记录。

## 调试 CI

本地先运行：

```bash
make lint
make theory
make learning
pytest
llm-theory-lab roadmap
llm-theory-lab explain C07
python -m mkdocs build --strict
python -m build
python -m twine check dist/*
```

CI 失败时修复根因，不要通过删除失败案例、放宽科学阈值、跳过学习路径检查或静默忽略异常来获得绿色状态。若预注册检查因理论或实现更新而改变，应在 PR 和 `CHANGELOG.md` 中说明原因。
