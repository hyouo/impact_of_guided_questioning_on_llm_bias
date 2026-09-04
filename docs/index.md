# LLM Theory Lab

这是一门“边学边验证”的大模型机制课程，也是一张诚实记录公开复现进度的工程地图。它不要求你先懂稀疏自编码器，也不要求你相信漂亮的内部可视化。

<div class="grid cards" markdown>

-   :material-school: **学习课程**

    ---

    按因果顺序理解 token、权重、激活、Attention、推理和安全。

    [进入课程](course/index.md)

-   :material-flask: **运行十二个实验**

    ---

    用透明数值系统检验核心命题，并学习怎样解释失败和反例。

    [进入实验手册](labs/index.md)

-   :material-pencil: **练习与评估**

    ---

    手算公式、构造反例、设计对照，并检查自己的证据边界。

    [基础练习](exercises/index.md) · [进阶练习](exercises/advanced.md)

-   :material-map-check: **检查复现进度**

    ---

    查看 56 条公开来源哪些只有代理、哪些可在开放模型上类比、哪些仍被资产阻塞。

    [进入复现地图](reference/reproduction-map.md)

-   :material-bookshelf: **查研究资料**

    ---

    阅读统一理论、案例、方法边界和 Transformer Circuits 来源摘要。

    [进入深度参考](reference/unified-theory.md)

</div>

## 当前成熟度

截至 `2026-09-04`：

```text
56 条公开来源全部进入覆盖地图
0 条声明为完整复现
20 条部分覆盖
28 条已规划但尚无验证协议
8 条作为教学、方法、工具或历史参考
```

“部分覆盖”不代表原论文完整复现。当前 C01–C12 是透明数学/结构实验；开放模型 M01–M03 仍是原型。涉及 Claude 私有权重或未公开中间资产的结果，只能做明确标注的开放模型类比。

## 最小心智模型

```text
训练分布 → 权重
输入 + 固定权重 → 激活、路由和局部计算图
局部计算图 → logits → token 分布
token 被选中并写回 → 下一步状态
```

## 五分钟验证环境

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e .

llm-theory-lab roadmap
llm-theory-lab run-toy --ids C01 C02
llm-theory-lab reproduction-map --summary-only
```

看到 `pass` 只表示预注册数值检查成立；它不是“所有大模型都被证明如此”。

## 推荐学习循环

```text
课程章节
→ 写下自己的预测
→ 运行透明实验
→ 修改一个条件
→ 做对应练习
→ 对照答案解析
→ 重写结论和边界
```

## 学完后你应该能

- 用三个时间尺度解释训练分布、输入和生成 token 各自影响什么；
- 从 $c=w\cdot a$ 理解权重大小为什么不等于当前作用；
- 推导 softmax 下的 token 相对赔率；
- 区分 Attention 的 QK 路由和 OV 写回；
- 解释 superposition、特征、SAE 与基底不唯一；
- 区分相关、可解码、必要、充分和可操纵性；
- 识别冗余路径和指标饱和造成的消融假阴性；
- 用“识别—策略—输出—反馈”分析安全失配；
- 为一个机制主张写出对照、干预、指标和反证条件；
- 判断一个结果是精确复现、开放模型类比、透明代理还是仍未实现。

开始：[课程导览](course/index.md) · [实验手册](labs/index.md) · [练习册](exercises/index.md) · [复现地图](reference/reproduction-map.md)
