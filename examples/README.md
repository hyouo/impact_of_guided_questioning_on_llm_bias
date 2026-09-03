# 可运行示例

这些脚本不是另一个测试框架，而是课程中的“最小可读入口”。先安装项目：

```bash
python -m pip install -e .
```

然后按顺序运行：

```bash
python examples/01_softmax_temperature.py
python examples/02_weight_vs_activation.py
python examples/03_attention_routing.py
python examples/04_probe_vs_causality.py
python examples/05_autoregressive_feedback.py
```

每个脚本都会：

1. 运行仓库中的真实实验函数；
2. 打印最重要的观测量；
3. 检查实验状态；
4. 明确写出它不能证明什么。

完整报告请使用：

```bash
llm-theory-lab run-toy --output-dir reports/toy
```
