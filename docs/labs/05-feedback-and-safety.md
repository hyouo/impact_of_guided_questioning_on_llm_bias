# 实验 5｜首 token 反馈与安全路由分离

## 问题

为什么模型已经识别出某种内容，最终行为仍可能不同？为什么首 token 会进一步放大差异？

## 先做预测

C05 保持权重和初始状态相同，只强制首 token 为 A 或 B。预测六步后的序列和最终状态距离。

C09 使用无害权限代理，分别表示内容识别、策略状态和动作倾向。预测只 patch 策略状态是否能翻转动作。

## 运行

```bash
llm-theory-lab explain C05
llm-theory-lab explain C09
llm-theory-lab run-toy --ids C05 C09 --output-dir reports/lab05
python examples/05_autoregressive_feedback.py
```

## 要检查的量

- 两条强制首 token 轨迹；
- 最终状态 L2 距离；
- 内容识别信号是否保持不变；
- 策略 patch 前后的 top action；
- 为什么动作翻转不要求修改参数。

## 扩展实验

尝试构造三种反馈矩阵：正反馈、回到共同稳定点的负反馈，以及 A/B 交替的交叉反馈。然后讨论自然语言中的回答式前缀、拒绝式前缀和列表结构分别更像哪一种。

## 结论边界

实验说明识别、策略和行为在结构上可以分离，且 token 反馈可以放大首步差异。它不提供真实越狱载荷，也不证明所有安全失败由同一坐标或单一路径造成。
