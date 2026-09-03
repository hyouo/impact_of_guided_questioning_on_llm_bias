# LLM Theory Lab

这是一门“边学边验证”的大模型机制课程。它不要求你先懂稀疏自编码器，也不要求你相信任何漂亮的内部可视化。

## 从哪里开始

<div class="grid cards" markdown>

-   :material-school: **学习课程**

    ---

    按因果顺序理解 token、权重、激活、Attention、推理和安全。

    [进入课程](course/index.md)

-   :material-flask: **运行实验**

    ---

    用透明数值模型检验每个核心命题，并学习怎样解释结果。

    [进入实验手册](labs/index.md)

-   :material-bookshelf: **查研究资料**

    ---

    阅读统一理论、案例、方法边界和 Transformer Circuits 来源摘要。

    [进入深度参考](reference/unified-theory.md)

</div>

## 最小心智模型

```text
训练分布 → 权重
输入 + 固定权重 → 激活、路由和局部计算图
局部计算图 → logits → token 分布
token 被选中并写回 → 下一步状态
```

这条链可以统一解释很多现象，但不会把它们粗暴归结为一个“神经元”或一个“安全参数”。

## 五分钟验证环境

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e .

llm-theory-lab roadmap
llm-theory-lab run-toy --ids C01 C02
```

看到 `pass` 只表示预先写下的数值检查成立。它不是“所有大模型都被证明如此”。

## 学完后你应该能

- 用三个时间尺度解释训练分布、输入和生成 token 各自影响什么；
- 从 $c=w\cdot a$ 理解权重大小为什么不等于当前作用；
- 推导 softmax 下的 token 相对赔率；
- 区分 Attention 的 QK 路由和 OV 写回；
- 解释 superposition、特征、SAE 与基底不唯一；
- 区分相关、可解码、必要、充分和机制忠实；
- 用“识别—策略—输出—反馈”分析安全失配；
- 为一个机制主张写出对照、干预、指标和反证条件。
