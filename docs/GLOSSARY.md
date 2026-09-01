# 术语表

| 术语 | 本仓库中的含义 |
|---|---|
| Parameter / weight | 训练后存储在模型中的数值；标准推理时通常固定 |
| Activation | 给定输入下，中间单元或向量的动态数值 |
| Neuron | 某层表示中的一个坐标/标量单元，不保证单义 |
| Feature | 可重复、对计算有意义的潜在变量；可能是方向、子空间或流形坐标 |
| Residual stream | Transformer 各模块共同读写的高维状态通道 |
| Attention head | 由 QK 路由和 OV 写入共同构成的上下文相关变换 |
| QK circuit | 决定当前位置为什么读取某一位置的打分机制 |
| OV circuit | 决定读到内容后写入什么信息的变换 |
| Logit | softmax 前对候选 token 的未归一化分数 |
| Unembedding | 把最终 residual state 映射到 vocabulary logits 的线性变换 |
| Circuit | 多个表示和组件组合形成的、可解释且可验证的计算路径 |
| Virtual weight | 在特征/组件基底中展开后的有效连接，通常是原矩阵乘积 |
| Superposition | 多个特征共享少量维度以增加容量的表示策略 |
| Polysemanticity | 一个神经元或方向在不同上下文参与多个不相关特征 |
| Composition | 多个相对独立表示组合成复杂表示/计算 |
| Privileged basis | 实际训练中某些坐标比任意旋转后的坐标更具统计特殊性 |
| SAE | 用稀疏隐变量重建激活的稀疏自编码器 |
| Transcoder | 用稀疏特征近似一个模块输入到输出的变换 |
| Crosscoder | 跨多个层或模型联合编码/重建的字典模型 |
| Feature splitting | 更大字典把一个粗特征拆成多个更细特征 |
| Feature manifold | 低内在维连续变量在高维激活空间形成的曲线/曲面 |
| Interference weight | 因权重/表示叠加出现、无帮助或有害的虚拟连接 |
| Attribution | 对某输入和目标输出分配局部贡献的分析 |
| Attribution graph | 用特征节点和贡献边近似特定 prompt 计算的图 |
| Probe | 从激活预测标签的辅助模型，主要证明信息可解码 |
| Ablation | 移除或替换组件/激活以测试必要性 |
| Steering | 沿候选方向改变激活以测试方向性影响 |
| Activation patching | 把一个运行的内部状态替换进另一个运行，测试因果恢复 |
| In-context learning | 参数不更新时，模型依据上下文改变行为或形成临时规则 |
| Induction head | 基于前缀匹配读取先前后继 token 的 attention 机制 |
| Chain-of-thought | 模型生成的中间推理文本，不自动等于内部机制 |
| J-space | global-workspace 研究中更可报告、控制和推理的表示子空间 |
| NLA | 通过自然语言瓶颈 verbalize 并重建激活的自动编码方法 |
| Jailbreak | 使模型绕过预期安全行为的输入或交互现象 |
| Prompt injection | 不可信文本被错误当作高权限指令的控制/数据混淆 |
| Over-refusal | 无害输入因表面或路由失配被错误拒绝 |
| Trajectory bias | 已生成 token 通过上下文反馈放大后续行为倾向 |
