# 06｜机制研究方法与因果验证

## 6.1 从现象到机制的阶梯

```text
行为差异
  → 内部相关量
  → 可泛化表征
  → 定向干预
  → 反事实修补
  → 回路组合
  → 跨任务 / 跨模型 / 跨训练阶段复现
```

每上升一级，允许的主张更强；但前一级不能被后一级术语伪装。

## 6.2 行为实验

回答：输入变化是否导致输出分布或行为变化？

最低设计：

- 成对或因子化 prompt；
- 固定模型、system prompt、工具和解码参数；
- 多 seed 或完整 logprob；
- 随机化条件顺序；
- 记录失败和无效结果；
- 预注册主要指标与排除规则。

行为实验可以支持“输入改变行为”，不能单独支持“某特征或权重造成行为”。

## 6.3 Feature visualization

对候选神经元或特征收集高激活样本、激活谱不同区间、负样本和人工构造对照。只看 top-k 容易产生确认偏差：

- 高频 token 可能污染样本；
- 同一表面模式可能覆盖多个语义；
- 低激活区域可能暴露 polysemanticity；
- 狭窄数据集可能让特征看起来比实际更专一。

应同时报告 specificity、sensitivity、激活分布和跨数据集稳定性。

## 6.4 Probe

Probe 训练映射：

\[
\hat y=g(h^{(\ell)}).
\]

它证明表示中含有可解码信息。常见风险：

- 高容量 probe 自己学习任务；
- 标签与表面特征混杂；
- 线性可解码不代表模型下游使用该方向；
- 多个相关变量难以区分；
- 训练/测试分布过近。

改进：低容量 probe、控制任务、选择性指标、跨模板测试、随机标签、层间比较和后续因果干预。

## 6.5 Logit lens 与 attribution

把中间表示投影到 vocabulary，可观察其直接输出倾向：

\[
z^{(\ell)}=W_Uh^{(\ell)}.
\]

但中间层表示未必为最终 unembedding 坐标准备；LayerNorm、后续层和校正回路可改变含义。Logit attribution 能分解某路径对目标 logit 的直接贡献，但不能自动证明该路径必要。

## 6.6 Activation patching

构造 clean 与 corrupted 输入：

1. clean 输入产生正确行为和激活 \(h_c\)；
2. corrupted 输入破坏行为，产生 \(h_b\)；
3. 把某层/位置/组件的 \(h_c\) patch 到 corrupted run；
4. 测量目标行为恢复程度。

Patching 可定位承载因果信息的位置，但仍需注意：

- patch 可能离开自然激活流形；
- 组件间有非线性交互；
- 大范围 patch 难以确定最小机制；
- 恢复信息不一定等于恢复模型原算法。

## 6.7 Ablation 与 steering

### Ablation

把候选单元置零、均值替换或投影移除，测试必要性。

### Steering

沿方向增加或减少激活，测试方向性预测和部分充分性。

良好对照包括：

- 随机同范数方向；
- 相邻层与错误位置；
- 语义相近但行为无关的特征；
- 多种强度曲线；
- 流畅度、困惑度和副作用；
- 对新 prompt 的泛化。

强 steering 可能把模型推到分布外，因此“能操控”不等于“自然运行时主要使用”。

## 6.8 Causal scrubbing / interchange intervention

先提出抽象计算图，再测试模型组件是否满足图中的变量交换关系。若抽象变量在两个输入间可互换，替换对应内部状态应产生模型预测的反事实输出。

这种方法比单纯看相关性更接近验证“模型实现了哪个算法”，但抽象图选择本身仍由研究者提出。

## 6.9 SAE、transcoder、crosscoder 的评估

至少同时评估：

- reconstruction error / explained variance；
- 稀疏度与 dead features；
- 特征可解释性；
- 跨 seed 稳定性；
- feature splitting 与 absorption；
- 下游因果效应；
- error term 对目标行为的贡献；
- 在不同数据分布上的覆盖。

只优化重建 + 稀疏，不保证得到最适合机制解释的变量。

## 6.10 Attribution graph 验证模板

```markdown
### 目标
- prompt：
- 目标 token / logit difference：
- 模型版本：

### 候选机制
- 上游特征：
- 中间变量：
- attention 路由：
- 下游输出特征：

### 预测
- 抑制 A 应降低 B：
- 激活 C 应把输出从 X 改为 Y：
- clean→corrupt patch 应恢复：

### 对照
- 随机特征：
- 错误位置：
- 相同范数方向：
- 长度/格式匹配 prompt：

### 结果
- 行为效应：
- 中间节点效应：
- 副作用：
- 失败案例：
- 可支持的最强主张：
```

## 6.11 全分布与窄任务

一个组件在特定数据集上的功能标签可能只是其行为切片。HeadVis 提醒应把“task-specific role”升级为“distributional characterization”：

- 在自然语料中找高作用样本；
- 聚类不同注意/输出模式；
- 检查一个头是否复用同一低秩变换完成多类任务；
- 区分共享机制与偶然共激活；
- 测试能否用少数原则预测未见行为。

## 6.12 模型 diffing

比较训练阶段或微调前后的模型时，不应只比较参数差：

- 参数对称性会使直接差异难解释；
- 同一特征可能旋转；
- 新行为可能来自旧特征的新组合；
- 训练数据和模型表示变化需要分离。

Crosscoder 与 stage-wise model diffing 尝试建立共享特征坐标，并分别引入数据与模型变化。但它们仍处于方法发展阶段，需要跨模型复现和强对照。

## 6.13 定性研究的作用

机制可解释性仍处于前范式阶段。交互可视化、案例研究和“结构信号”可以发现新对象，但应避免两个错误：

- 认为只有汇总统计才是科学；
- 认为一个漂亮案例无需反事实验证。

合理流程是：定性发现结构 → 形成精确假设 → 扩展数据 → 因果干预 → 定量复现。

## 6.14 核心来源

- [Reflections on Qualitative Research](https://transformer-circuits.pub/2024/qualitative-essay/index.html)
- [Towards Monosemanticity](https://transformer-circuits.pub/2023/monosemantic-features/index.html)
- [Scaling Monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
- [Circuit Tracing](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
- [HeadVis](https://transformer-circuits.pub/2026/headvis/index.html)
- [Sparse Crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html)
- [Stage-Wise Model Diffing](https://transformer-circuits.pub/2024/model-diffing/index.html)
