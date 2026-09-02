# Repository Architecture｜仓库架构

## 设计目标

仓库采用标准 Python `src` 布局，并让理论、来源、代码和验证保持可追溯关系。

```text
docs/                 理论、来源综合、研究边界与维护文档
sources/              机器可读的外部来源目录
src/llm_theory_lab/   实验框架、数学工具和模型接口
tests/                单元与集成测试
examples/             最小运行示例
scripts/              仓库、来源和 Markdown 一致性检查
.github/              CI、安全扫描、依赖更新和贡献模板
```

## 代码层

`llm_theory_lab` 分为：

- `registry.py`：实验 ID、理论主张、类别和反证条件的单一入口；
- `result.py`：结构化检查、实验结果和 Markdown/JSON 报告；
- `math_utils.py`：数值稳定的数学工具；
- `repro.py`：运行环境和复现元数据；
- `experiments/`：每个可独立运行的理论实验；
- `cli.py`：稳定的命令行接口。

## 理论—代码契约

每个实验应回答：

```text
它检验哪条理论？
操纵了什么？
保持了什么不变？
正负对照是什么？
指标和阈值是什么？
什么结果会反驳它？
最多允许得出什么结论？
```

`registry.py` 是代码侧入口，`docs/14_THEORY_TO_CODE_LAB.md` 是文字侧入口。修改一侧时应同步更新另一侧。

## 依赖边界

核心包只依赖 NumPy。PyTorch、Transformers 和 Safetensors 位于 `models` 可选依赖，避免透明实验被大型框架绑死。文档和开发工具也分别使用可选依赖。

## 生成产物

下列内容不进入 Git：

```text
reports/
runs/
model_cache/
build/
dist/
site/
coverage.xml
```

正式结果若需要长期保存，应包含版本、commit、种子、模型 revision、token IDs、指标定义和结论边界，并单独进行审查。
