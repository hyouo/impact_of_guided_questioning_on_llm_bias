# C04｜Attention 的 QK 路由与 OV 写回

## 问题

为什么改变一个 token 的表示会同时改变“从哪里读”和“写回什么”？为什么 Attention heatmap 不是完整解释？

## 运行

```bash
llm-theory-lab explain C04
llm-theory-lab run-toy --ids C04
python examples/03_attention_routing.py
```

## 运行前预测

在所有矩阵固定时，只改变位置 0 的 key-relevant 坐标。预测：

- 哪个位置的 QK score 会变化；
- softmax 后其他位置的权重为何也会变化；
- 聚合输出是否必然变化；
- 如果 value 恰好相同，会出现什么反例。

## 读结果

依次看：

1. `baseline_scores` 与 `perturbed_scores`；
2. `baseline_attention` 与 `perturbed_attention`；
3. `baseline_output` 与 `perturbed_output`；
4. `output_l2_shift`。

不要跳过 score 直接给 heatmap 贴语义标签。QK 解释路由，value 与 $W_O$ 决定写回内容。

## 改动实验

打开 `attention.py`：

- 只改 value-relevant 坐标，保持 QK score 不变；
- 让两个位置 score 相同但 value 相反；
- 提高一个 score，验证其他权重因分母而下降；
- 添加第二个头，让两个输出互相抵消。

## 结论边界

**支持：** Attention 是输入条件下的相对路由与内容聚合。  
**不支持：** 最高 Attention 位置就是最终答案的唯一原因，或一个低维单头 toy 足以解释真实模型中的头。

## 延伸阅读

- [第 3 章](../course/03-attention-and-circuits.md)
- [Tracing Attention Computation Through Feature Interactions](https://transformer-circuits.pub/2025/attention-qk/index.html)
