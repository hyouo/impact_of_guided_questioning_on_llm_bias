# 实验 2｜权重大小为什么不等于功能重要性

## 问题

一个绝对值很大的权重，是否必然比小权重重要？

## 先做预测

比较：权重 8，只在约 1% 样本中以约 0.05 激活；权重 1.2，在多数样本中以约 1.0 激活。预测当前贡献和玩具有效性 $E[(wa)^2]$ 谁更大。

## 运行

```bash
llm-theory-lab explain C01
llm-theory-lab run-toy --ids C01 --output-dir reports/lab02
python examples/02_weight_vs_activation.py
```

## 要检查的量

- `current_contributions`；
- `rare_feature_activation_rate`；
- 两条连接的 effectiveness proxy；
- `effectiveness_ratio_large_over_small`。

## 修改实验

改变稀有特征激活率和激活幅度，找出大权重从“几乎无效”变成“主导”的边界。尝试回答：

$$
E[(w_1a_1)^2]=E[(w_2a_2)^2]
$$

在什么条件下成立？

## 结论边界

这是一个足以推翻“按权重绝对值直接读取功能”的反例。它不是 interference weights 指标的完整复现，也没有包含下游抵消、冗余和损失方向。
