# C02｜Softmax、温度与 token 赔率

## 问题

为什么两个 token 的相对赔率只由 logit 差和正温度决定？小 logit 改变何时会产生明显行为差异？

## 运行

```bash
llm-theory-lab explain C02
llm-theory-lab run-toy --ids C02
python examples/01_softmax_temperature.py
```

## 运行前预测

对 $T=0.5,1,2$ 分别预测：

- 相同 logit 差对应的 log-odds 大小；
- token $i$ 的 logit 增加 1 后，赔率乘数；
- 哪些量不依赖第三个 token，哪些量会受整个词表影响。

## 读结果

实验检查：

$$
\log\frac{p_i}{p_j}=\frac{z_i-z_j}{T}
$$

以及：

$$
\frac{(p_i/p_j)_{\text{after}}}{(p_i/p_j)_{\text{before}}}
=e^{\Delta z/T}.
$$

重点看 `identity_absolute_errors` 和 `odds_multiplier_after_plus_one_logit_at_T1`。前者应接近数值精度，后者应接近 $e$。

## 改动实验

打开 `temperature.py`：

- 加入第四个非常高的 logit，检查 $p_i/p_j$ 与各自绝对概率；
- 将 $\Delta z$ 改为 0.1、0.5、2；
- 对多个温度画出赔率乘数；
- 尝试给 `softmax` 传入 $T=0$，解释为什么应拒绝。

## 结论边界

**支持：** 正温度 softmax 下的赔率恒等式。  
**不支持：** logit 增加就一定采样该 token；解码还受其余词表、top-k、top-p、greedy 和约束影响。

## 延伸阅读

- [第 2 章](../course/02-weights-activations-and-logits.md)
- [参数、激活与 token 深度专题](../01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md)
