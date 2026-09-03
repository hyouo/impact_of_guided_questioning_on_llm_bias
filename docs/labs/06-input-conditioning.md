# C03｜固定权重下的输入条件计算

## 问题

不修改参数，只改变 input，系统是否可以激活不同内部路径并翻转输出？

## 先做预测

把以下三个命题分开写出可观测量：

1. 参数矩阵保持不变；
2. 特征激活随输入改变；
3. top token 因此可能改变。

## 运行

```bash
llm-theory-lab explain C03
llm-theory-lab run-toy --ids C03 --output-dir reports/c03
```

## 要检查的量

逐个输入比较：

- 输入状态；
- ReLU 后特征激活；
- logits 与概率；
- top token。

核心关系是：

$$
h=f_\theta(x).
$$

$\theta$ 固定不等于 $h$ 固定。

## 改动实验

打开 `src/llm_theory_lab/experiments/conditional.py`：

- 在两个输入之间连续插值，找 top token 翻转点；
- 改变 bias，观察阈值怎样移动；
- 构造不同输入但相同输出；
- 构造相同输出但内部激活不同。

最后一个任务说明，单看最终文本可能漏掉机制差异。

## 结论边界

**支持：** 固定参数函数足以实现 input-dependent computation。  
**不支持：** 真实模型只有 toy 中少数可命名轴，或每个 prompt 只激活一条离散路径。
