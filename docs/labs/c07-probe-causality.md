# C07｜Probe 可解码不等于模型自然使用

## 问题

如果一个变量能被线性 probe 以接近 100% 的准确率读出，是否说明原模型依赖这个变量生成输出？

## 运行

```bash
llm-theory-lab explain C07
llm-theory-lab run-toy --ids C07
python examples/04_probe_vs_causality.py
```

## 运行前预测

隐藏状态有两个维度：一个被输出头读取，一个只携带可解码标签。预测：

- probe 对未使用维度的准确率；
- 消融未使用维度后的输出变化；
- 消融真正因果维度后的输出变化。

## 读结果

重点比较：

- `probe_accuracy_unused_variable`；
- `mean_output_change_after_unused_ablation`；
- `mean_output_change_after_causal_ablation`。

如果 probe 很准，但第一种消融效应为零，而第二种很大，就得到一个直接反例：

```text
信息存在并可被外部读出
≠ 原模型输出路径使用了它
```

## 改动实验

打开 `probe_causality.py`：

- 让两个隐藏维度相关；
- 让输出头以很小权重读取“未使用”维度；
- 增加 probe 容量并降低样本数；
- 构造训练集上高准确、分布外失效的 probe；
- 比较 probe 预测与 activation patching 的证据差异。

## 结论边界

**支持：** 高 probe 准确率本身不能证明自然因果使用。  
**不支持：** 所有 probe 都无价值；probe 仍可用于定位候选信息和生成干预假设。

## 延伸阅读

- [第 6 章](../course/06-causal-interpretability.md)
- [方法与解释矩阵](../12_METHODS_AND_INTERPRETATION_MATRIX.md)
