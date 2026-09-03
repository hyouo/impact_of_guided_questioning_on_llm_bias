# 实验 4｜可解码信息不等于模型使用

## 问题

一个变量能被线性 probe 以接近 100% 准确率读出，是否说明模型依赖它？

## 先做预测

模型隐藏状态有两维：第 0 维真正进入输出头；第 1 维编码另一个高度可解码变量，但输出头权重为 0。预测消融两维后的输出变化。

## 运行

```bash
llm-theory-lab explain C07
llm-theory-lab explain C08
llm-theory-lab run-toy --ids C07 C08 --output-dir reports/lab04
python examples/04_probe_vs_causality.py
```

## 要检查的量

C07：

- `probe_accuracy_unused_variable`；
- `mean_output_change_after_unused_ablation`；
- `mean_output_change_after_causal_ablation`。

C08：

- corrupted baseline；
- patch 候选中介后的恢复；
- patch 无关维度的负对照。

## 解释任务

分别用一句话说明 probe、ablation 和 patching 给出的证据，以及三者仍不能证明的内容。

## 结论边界

C07 是逻辑反例：它证明“可解码 ⇒ 被使用”不是一般定理。C08 的恢复说明候选状态能传递因果信息，但不证明它是唯一、最自然或完整的中介。
