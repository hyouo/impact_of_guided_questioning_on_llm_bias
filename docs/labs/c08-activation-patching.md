# C08｜Activation patching 与候选中介

## 问题

把 clean 运行中的内部状态替换到 corrupted 运行后，目标输出恢复了。这究竟支持什么，又不能证明什么？

## 运行

```bash
llm-theory-lab explain C08
llm-theory-lab run-toy --ids C08
```

## 运行前预测

先画出：

```text
clean input → mediator_clean → correct output
corrupt input → mediator_corrupt → wrong output
```

再预测：

- patch 候选中介后的目标 margin；
- patch 无关维度后的 margin；
- clean 与 corrupt 基线；
- 什么结果会削弱“该状态传递关键信息”的命题。

## 读结果

重点看：

- clean、corrupt 与 patched margin；
- 候选中介 patch 的恢复量；
- 无关维度 patch 的负对照；
- 恢复率是否被 clean–corrupt 差异归一化。

恢复说明 patch 的状态对传递 clean 信息具有因果充分性证据。它不自动说明该状态在所有自然输入中必要，也不说明它是唯一中介。

## 改动实验

打开 `patching.py`：

- 将候选中介拆成多个坐标分别 patch；
- 同时 patch 两个冗余路径；
- 反向执行 corrupt→clean；
- 添加随机向量和错误位置对照；
- 构造“单点 patch 无效、联合 patch 有效”的冗余机制。

## 结论边界

**支持：** 指定内部状态在指定反事实中可以传递目标效应。  
**不支持：** 已找到唯一概念神经元、完整回路，或 patch 后状态完全处于自然数据流形上。

## 延伸阅读

- [第 6 章](../course/06-causal-interpretability.md)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
