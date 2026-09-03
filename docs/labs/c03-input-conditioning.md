# C03｜固定权重下的输入条件计算

## 问题

不修改参数，只改变 input，模型是否可以激活不同内部路径并翻转输出？

## 运行

```bash
llm-theory-lab explain C03
llm-theory-lab run-toy --ids C03
```

## 运行前预测

区分三个命题：

1. 参数矩阵保持不变；
2. 隐藏激活会随输入改变；
3. top token 可能因此改变。

写出什么观测会分别验证这三点。

## 读结果

重点比较不同输入状态对应的：

- 特征激活向量；
- logits；
- 概率分布；
- top token。

核心不是“模型切换了人格”，而是同一函数 $f_\theta(x)$ 在不同 $x$ 上产生不同状态：

$$
h=f_\theta(x).
$$

## 改动实验

打开 `conditional.py`：

- 连续插值两个输入，找出 top token 翻转点；
- 改变 bias，观察阈值如何移动；
- 构造两个不同输入但相同输出的例子；
- 构造输出相同但内部特征不同的例子。

最后一个任务说明：只看最终文本可能漏掉机制差异。

## 结论边界

**支持：** 固定参数足以实现 input-dependent computation。  
**不支持：** 真实模型的内部状态恰好由 toy 中几条可命名轴组成。

## 延伸阅读

- [第 1 章](../course/01-model-as-conditional-system.md)
- [理论总图](../00_THEORY_MAP.md)
