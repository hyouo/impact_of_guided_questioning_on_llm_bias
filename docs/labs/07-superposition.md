# C06｜稀疏 Superposition 与共激活干扰

## 问题

当潜在特征数多于表示维度时，系统怎样共享容量？为什么单特征可读而共激活时出现干扰？

## 先做预测

设五个特征方向位于二维空间。判断它们能否全部正交，并预测单特征、相邻特征共同激活时的重建差异。

## 运行

```bash
llm-theory-lab explain C06
llm-theory-lab run-toy --ids C06 --output-dir reports/c06
```

## 要检查的量

- 特征方向间的非对角内积；
- `single_feature_accuracy`；
- `pair_feature_accuracy`；
- 共激活误差相对单特征误差的增量。

$F>d$ 时方向不可能全部正交。若特征稀疏、很少共现，有限干扰可能换来更大表示容量。

## 改动实验

打开 `src/llm_theory_lab/experiments/superposition.py`：

- 改变特征数和表示维度；
- 比较相邻方向与近似正交方向共激活；
- 为特征指定不同出现概率，计算期望误差；
- 找出增加一个特征何时不再划算。

## 结论边界

**支持：** 稀疏特征可以非正交共享低维空间，共激活会暴露干扰。  
**不支持：** 真实语言特征具有相同规则几何，或这个 toy 等价于训练出的 SAE 字典。
