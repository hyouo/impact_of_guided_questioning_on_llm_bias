# 可运行示例

这些脚本不是第二套实验框架，而是课程中的“最小可读入口”。每个示例直接调用 `src/llm_theory_lab/experiments/` 中的正式实验函数。

先安装项目：

```bash
python -m pip install -e .
```

## 运行顺序

| 示例 | 先回答的问题 | 课程与实验 |
|---|---|---|
| `01_softmax_temperature.py` | 温度减半后，相同 logit 差的赔率怎样变化？ | 第 2 章 / C02 |
| `02_weight_vs_activation.py` | 最大权重是否一定有最大当前贡献？ | 第 2 章 / C01 |
| `03_attention_routing.py` | 只改一个 token 表示，会改读取位置还是写回内容？ | 第 3 章 / C04 |
| `04_probe_vs_causality.py` | probe 接近满分时，消融变量一定改变输出吗？ | 第 6 章 / C07 |
| `05_autoregressive_feedback.py` | 只强制首 token，后续状态会不会持续分叉？ | 第 5 章 / C05 |

按顺序运行：

```bash
python examples/01_softmax_temperature.py
python examples/02_weight_vs_activation.py
python examples/03_attention_routing.py
python examples/04_probe_vs_causality.py
python examples/05_autoregressive_feedback.py
```

## 正确使用方法

每个脚本运行前，先写下：

```text
我的预测：
主要观测量：
什么结果会让我改变看法：
即使结果符合预测，也不能推出什么：
```

运行后不要只看 `pass`。至少检查：

1. 哪个具体数值支持了预测；
2. 正对照是否真的有效；
3. 是否存在更简单的替代解释；
4. 结果属于数学恒等式、结构反例，还是经验观察；
5. 把哪一个条件改掉最可能使结果失败。

完整报告会同时保存原始指标、反证条件、课程位置和禁止外推：

```bash
llm-theory-lab run-toy --output-dir reports/toy
```

随后做[练习册](../docs/exercises/index.md)中的对应题组，把“看懂输出”升级为“能独立推导和设计对照”。
