# C07｜可解码信息不等于模型自然使用

## 问题

一个变量能被线性 probe 以接近 100% 的准确率读出，是否说明原模型依赖它生成输出？

## 先做预测

隐藏状态有两维：第 0 维进入输出头，第 1 维编码另一个高度可解码变量，但输出权重为 0。预测：

- probe 对第 1 维标签的准确率；
- 消融第 1 维后的输出变化；
- 消融第 0 维后的输出变化。

## 运行

```bash
llm-theory-lab explain C07
llm-theory-lab run-toy --ids C07 --output-dir reports/c07
python examples/04_probe_vs_causality.py
```

## 要检查的量

- `probe_accuracy_unused_variable`；
- `mean_output_change_after_unused_ablation`；
- `mean_output_change_after_causal_ablation`。

若 probe 很准，但未使用维度的消融效应为零，而真正因果维度的消融效应很大，就得到一个结构反例：

```text
信息存在并可被外部读出
≠ 原模型自然计算时使用了它
```

## 改动实验

打开 `src/llm_theory_lab/experiments/probe_causality.py`：

- 让两个隐藏维度相关；
- 给原输出头增加很小的第 1 维权重；
- 降低样本数并提高 probe 容量；
- 构造训练集准确、分布外失效的 probe；
- 比较 probe 证据与 C08 patching 证据。

## 结论边界

**支持：** 高 probe 准确率本身不能证明模型自然使用该变量。  
**不支持：** 所有 probe 都无价值。Probe 仍适合定位候选信息、比较层和生成干预假设。
