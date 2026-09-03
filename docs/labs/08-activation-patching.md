# C08｜Activation patching 与候选中介

## 问题

把 clean 运行中的内部状态替换到 corrupted 运行后，目标输出恢复。这支持什么，又不能证明什么？

## 先做预测

先画出：

```text
clean input → mediator_clean → correct output
corrupt input → mediator_corrupt → wrong output
```

预测 patch 候选中介与 patch 无关维度后，目标 margin 各自怎样变化。

## 运行

```bash
llm-theory-lab explain C08
llm-theory-lab run-toy --ids C08 --output-dir reports/c08
```

## 要检查的量

- clean 与 corrupted baseline；
- 候选中介 patch 后的 margin；
- 无关维度 patch 的负对照；
- 相对 clean–corrupt 差异的恢复量。

恢复说明指定状态在这个反事实中能够传递 clean 信息，接近因果充分性证据。

## 改动实验

打开 `src/llm_theory_lab/experiments/patching.py`：

- 将中介拆成多个坐标分别 patch；
- 反向执行 corrupt→clean；
- 添加随机向量和错误位置对照；
- 构造单点 patch 无效、联合 patch 有效的冗余机制；
- 与 C11 的联合消融结果比较。

## 结论边界

**支持：** 指定状态在指定反事实中可以传递目标效应。  
**不支持：** 已找到唯一概念神经元、完整回路，或 patch 后状态完全处于自然数据流形上。
