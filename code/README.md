# 目录迁移说明

从 `v0.2.0` 起，实验代码已从嵌套的 `code/` 子项目迁移到标准 Python 根目录布局：

```text
src/llm_theory_lab/
tests/
examples/
pyproject.toml
```

新的安装方式：

```bash
# 在仓库根目录运行
pip install -e ".[dev]"
llm-theory-lab run-toy
pytest
```

本目录只为旧链接保留一个版本周期，不再包含独立包配置或源码。
