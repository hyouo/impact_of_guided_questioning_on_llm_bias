# C11｜冗余路径、消融与指标饱和

## 问题

消融一条路径后准确率完全不变，是否能证明这条路径没有参与计算？

## 先做预测

两个路径 A、B 都携带同一个二分类信号。基线 margin 为 $A+B$。预测：

- 单独移除 A 或 B 后的准确率；
- 单独移除后的连续 margin；
- 同时移除 A 和 B 后的准确率。

## 运行

```bash
llm-theory-lab explain C11
llm-theory-lab run-toy --ids C11 --output-dir reports/c11
python examples/07_redundant_paths.py
```

## 要检查的量

- `baseline_accuracy`；
- 两个单路径消融准确率；
- `accuracy_after_joint_ablation`；
- 两个单路径消融后的 mean margin change；
- 基线与单路径的平均绝对 margin。

离散准确率可能已经饱和，看不见连续置信 margin 的变化。联合消融才暴露两条路径的冗余关系。

## 改动实验

打开 `redundancy.py`：

- 给两条路径加入不同噪声；
- 让它们只在部分样本上冗余；
- 比较 accuracy、cross-entropy、calibration 和 margin；
- 构造三条备份路径；
- 模拟消融后补偿，而不是静态冗余。

## 结论边界

**支持：** 单点消融在粗粒度指标上无效，不足以证明路径未参与计算。  
**不支持：** 所有零消融结果都由冗余造成；干预位置错误、指标不敏感和分布外效应也是替代解释。
