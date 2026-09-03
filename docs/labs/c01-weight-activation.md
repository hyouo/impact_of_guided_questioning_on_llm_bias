# C01｜权重、激活与分布有效性

## 问题

一个连接的权重绝对值很大，是否意味着它对当前输出或真实数据分布最重要？

## 运行

```bash
llm-theory-lab explain C01
llm-theory-lab run-toy --ids C01
python examples/02_weight_vs_activation.py
```

## 运行前预测

先写下：

1. 当源激活为 0 时，大权重的直接贡献是多少；
2. “大但只在 1% 样本中弱激活”和“小但几乎总激活”谁的有效性代理更高；
3. 哪些真实 Transformer 机制没有被这个 toy 覆盖。

## 读结果

重点看：

- `current_contributions`：当前输入中的 $w\times a$；
- `rare_feature_activation_rate`：大权重源特征实际出现频率；
- 两个 `effectiveness_proxy`：数据分布上 $E[(wa)^2]$ 的比较；
- `effectiveness_ratio_large_over_small`：只按权重排序为何会误导。

直接贡献是：

$$
c=w\,a.
$$

但分布有效性仍不等于最终因果帮助性，因为下游还可能门控、抵消或替代。

## 改动实验

打开 `src/llm_theory_lab/experiments/weights.py`，依次尝试：

- 把罕见特征激活率从 1% 调到 20%；
- 把其激活幅度从 0.05 调到 0.5；
- 保持权重不变，只改变输入分布；
- 找到有效性排序发生翻转的临界区域。

记录：是权重改变了，还是输入分布改变了？

## 结论边界

**支持：** 权重大小不足以决定当前贡献或分布有效性。  
**不支持：** 真实模型中大权重通常都无效，或这个代理等于 interference-weights 论文中的完整 helpfulness 指标。

## 延伸阅读

- [第 2 章](../course/02-weights-activations-and-logits.md)
- [Characterizing interference weights](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html)
