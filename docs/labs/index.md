# 实验手册｜从“看结果”到“解释结果”

这里的实验不是九个演示动画。每个实验都要求你完成同一套动作：

```text
先写预测
→ 运行基线
→ 找出真正保持不变的量
→ 解释关键指标
→ 修改一个变量
→ 检查反例
→ 写出最大允许结论
```

## 实验地图

| ID | 核心对象 | 要推翻的错误直觉 | 课程 |
|---|---|---|---|
| [C01](c01-weight-activation.md) | 权重、激活、有效性 | 权重越大就越重要 | 第 2 章 |
| [C02](c02-softmax-odds.md) | logits、温度、赔率 | 单个概率可以脱离其他 token 理解 | 第 2 章 |
| [C03](c03-input-conditioning.md) | 固定权重、条件激活 | input 影响行为就必须修改参数 | 第 1 章 |
| [C04](c04-attention-routing.md) | QK、OV、softmax | Attention 热图就是完整解释 | 第 3 章 |
| [C05](c05-autoregressive-feedback.md) | token 回填、轨迹 | 首 token 只是表面措辞 | 第 5 章 |
| [C06](c06-superposition.md) | 稀疏特征、非正交干扰 | 一个神经元天然等于一个概念 | 第 4 章 |
| [C07](c07-probe-causality.md) | probe、消融 | 可解码就等于模型在使用 | 第 6 章 |
| [C08](c08-activation-patching.md) | 反事实中间状态 | patch 恢复就找到了唯一机制 | 第 6 章 |
| [C09](c09-safety-routing.md) | 识别、策略、输出 | 识别到风险就必然拒绝 | 第 7 章 |

## 通用运行方式

```bash
llm-theory-lab list
llm-theory-lab explain C04
llm-theory-lab run-toy --ids C04
```

全部运行：

```bash
llm-theory-lab run-toy
```

报告位置：

```text
reports/toy/results.json
reports/toy/report.md
```

## 每次必须记录

```text
实验 ID 与代码版本
运行命令
随机种子和样本数
保持不变的量
实际干预
主要指标
正对照与负对照
失败检查
允许结论
禁止外推
```

## 如何读 `pass`

`pass` 只表示当前代码中预先写好的检查成立。它不表示：

- 真实大模型必然使用同一坐标；
- 效应在其他输入分布上同样大；
- 候选机制是唯一机制；
- toy 的参数比例可以外推到前沿模型；
- 一次运行已经构成论文级证据。

真正的学习发生在你能解释“为什么这个检查合理、哪种修改会让它失败、失败后理论是否真的被反驳”。
