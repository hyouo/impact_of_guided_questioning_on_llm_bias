# 实验 1｜Softmax、温度与 token 赔率

## 问题

为什么相对 logit 的小变化能显著改变 token 竞争？

## 先做预测

对 logits $[0.2,-0.1,1.4]$，比较 token 2 与 token 0。先计算 $\Delta z=1.4-0.2=1.2$，再分别预测 $T=0.5,1,2$ 时的 log-odds。

## 运行

```bash
llm-theory-lab explain C02
llm-theory-lab run-toy --ids C02 --output-dir reports/lab01
python examples/01_softmax_temperature.py
```

## 要检查的量

在 `reports/lab01/results.json` 中找到：

- `identity_absolute_errors`；
- `odds_multiplier_after_plus_one_logit_at_T1`；
- 三种温度下的 log-odds。

验证：

$$
\log\frac{p_i}{p_j}=\frac{z_i-z_j}{T},
\qquad
\text{multiplier}=e^{\Delta z/T}.
$$

## 修改实验

尝试：给所有 logits 同时加 100；只给 token 2 加 0.2；把温度改为 0.25；增加第四个极高 logit token。解释哪些操作改变 token 2 与 token 0 的赔率，哪些只改变它们的绝对概率。

## 结论边界

本实验精确验证 softmax 恒等式。它不能证明某个 token 一定被采样，也不能把 API 中的 `temperature=0` 当作公式里的 $T=0$。
