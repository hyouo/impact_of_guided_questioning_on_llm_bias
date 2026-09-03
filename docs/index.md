# LLM Theory Lab

这里不是论文链接堆，也不是让另一个模型给输出打分的黑盒测试集。它是一条从基本数学对象走向因果机制实验的课程。

## 从这里开始

1. 阅读[课程导览](course/index.md)，先回答五个基线问题；
2. 按 M01–M07 顺序学习，每章运行对应实验；
3. 完成[练习册](exercises/index.md)，再核对[答案与解析](exercises/solutions.md)；
4. 用 M08 的模板完成一个小型机制研究项目；
5. 最后进入深度参考和原始来源。

## 你要建立的心智模型

```text
训练分布 → 参数
输入与历史 + 固定参数 → 当前激活与路由
激活与回路 → logits
解码 → token
token 写回 → 下一步状态与新轨迹
```

这条因果链要求你始终区分：

- 权重大小、当前贡献、分布有效性和因果帮助性；
- 神经元、特征、方向、子空间和流形；
- Attention 的 QK 路由与 OV 写回；
- 信息可解码、自然使用、必要性和充分性；
- 内容识别、角色/权限、策略状态和最终输出。

## 三条使用路线

### 学习路线

从[课程导览](course/index.md)进入八个模块。每章包含学习目标、核心模型、具体例子、常见误区、自测和原始来源。

### 实验路线

从[实验手册](labs/index.md)进入 C01–C09。先写预测，再运行：

```bash
llm-theory-lab course
llm-theory-lab explain C04
llm-theory-lab run-toy --ids C04
```

### 研究路线

完成课程后再读：

- [统一理论综合](09_UNIFIED_SYNTHESIS.md)
- [经典机制案例](11_CANONICAL_CASE_STUDIES.md)
- [方法与解释矩阵](12_METHODS_AND_INTERPRETATION_MATRIX.md)
- [Transformer Circuits 逐条精华](10_SOURCE_BY_SOURCE_DIGEST.md)

## 结果状态怎么读

| 状态 | 含义 |
|---|---|
| `pass` | 本次预注册数值检查成立 |
| `fail` | 至少一条检查没有达到预期 |
| `observational` | 只记录观察，不做二元机制判断 |
| `skipped` | 缺少模型、依赖或运行条件 |

透明 toy 的作用是证明结构可能、验证恒等式，或构造反例推翻错误逻辑；它不能估计真实前沿模型中的普遍效应大小。
