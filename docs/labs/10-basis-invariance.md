# C10｜可逆基底变换与函数不变性

## 问题

内部坐标发生明显变化时，模型的输入—输出函数能否保持完全相同？这对“一个神经元就是一个概念”意味着什么？

## 先做预测

对行向量表示 $h$、可逆矩阵 $R$ 和下游映射 $W$，考虑：

$$
h'=hR,
\qquad
W'=R^{-1}W.
$$

先证明：

$$
h'W'=hW.
$$

再预测只改变 $h$ 而不补偿 $W$ 时的结果。

## 运行

```bash
llm-theory-lab explain C10
llm-theory-lab run-toy --ids C10 --output-dir reports/c10
python examples/06_basis_invariance.py
```

## 要检查的量

- `max_output_error_after_compensated_change`；
- `mean_hidden_coordinate_shift`；
- `mean_output_error_without_compensation`；
- `basis_condition_number`。

关键对照是：协调变换应保持函数，只变表示、不变下游映射应改变函数。

## 改动实验

打开 `basis_invariance.py`：

- 改成正交旋转；
- 改变条件数，观察数值误差；
- 加入逐坐标 ReLU，检查任意旋转为何不再等价；
- 比较不同基底下的稀疏性；
- 讨论优化器和架构为何可能形成 privileged basis。

## 结论边界

**支持：** 在线性子图中，内部坐标不是由输入—输出函数自动唯一确定。  
**不支持：** 所有基底都同样可解释，或真实 Transformer 的神经元完全任意、永远没有功能意义。
