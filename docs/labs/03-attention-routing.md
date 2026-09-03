# 实验 3｜把 QK 路由与 OV 写回分开

## 问题

只改变一个 token 的表示，为什么能同时改变读取位置和写回内容？

## 先做预测

实验固定 $W_Q,W_K,W_V$，只把位置 0 在 key-relevant 方向上的值从 0 改为 3。预测哪个位置会成为最高 Attention、聚合输出向量会不会变化，以及如果只改 value、不改 key 会发生什么。

## 运行

```bash
llm-theory-lab explain C04
llm-theory-lab run-toy --ids C04 --output-dir reports/lab03
python examples/03_attention_routing.py
```

## 要检查的量

- `baseline_scores` 与 `perturbed_scores`；
- `baseline_attention` 与 `perturbed_attention`；
- `baseline_output` 与 `perturbed_output`；
- `output_l2_shift`。

## 两个关键反事实

1. **只改 key 相关维度，不改 value 相关维度**：测试路由改变如何重分配原有内容。
2. **只改 value 相关维度，不改 key 相关维度**：Attention pattern 可保持不变，但写回内容改变。

这两个反事实直接说明：Attention 热图相同，不等于头的功能输出相同。

## 结论边界

该实验只有一个低维头和一个查询位置。它证明 QK 与 OV 在数学上是不同对象，不证明真实模型中某个具体头的语义标签。
