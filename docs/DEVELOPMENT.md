# Development Guide｜开发指南

## 环境

支持 Python 3.10 及以上版本。推荐在虚拟环境中开发：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev,docs]"
pre-commit install
```

## 日常循环

```bash
make format
make test
make check
```

运行单个测试：

```bash
pytest tests/test_registry.py -q
```

运行单个实验：

```bash
llm-theory-lab run-toy --ids C04
```

## 代码规范

- Ruff 负责 import 排序、lint 和格式化；
- 公共函数应有类型提示和简明 docstring；
- 错误信息应说明预期值与实际值；
- 核心实验不得依赖网络；
- 可选模型依赖必须延迟导入，并提供明确安装提示；
- 结果必须通过 `ExperimentResult` 或兼容结构输出。

## 测试策略

测试分为：

1. 数学恒等式与输入校验；
2. 实验注册表和 CLI；
3. 报告序列化；
4. C01–C09 的预注册检查；
5. 包构建和文档严格构建。

开放模型下载不进入默认 CI。新增模型适配时，至少提供无网络单元测试或可注入的假对象。

## 调试 CI

本地先运行：

```bash
make lint
make theory
pytest
mkdocs build --strict
python -m build
python -m twine check dist/*
```

CI 失败时应修复根因，不要通过删除失败案例、放宽科学阈值或静默忽略异常来获得绿色状态。
