# C05｜首 token 与自回归轨迹

## 问题

在初始状态和全部权重相同的条件下，只改变第一个 token，后续状态与输出为什么会持续分叉？

## 运行

```bash
llm-theory-lab explain C05
llm-theory-lab run-toy --ids C05
python examples/05_autoregressive_feedback.py
```

## 运行前预测

写出两条轨迹：强制首 token 为 A 和为 B。预测：

- 第二步 logits 如何改变；
- 后续是否会强化同一模式；
- 最终状态距离随步数如何变化；
- 哪种反馈矩阵会让两条轨迹重新收敛。

## 读结果

重点看：

- `trajectory_forced_A` 与 `trajectory_forced_B`；
- `final_state_A` 与 `final_state_B`；
- `final_state_distance`。

完整因果链是：

```text
选中 token
→ token 对应反馈写入状态
→ 下一步 logits 改变
→ 新 token 更可能延续当前模式
```

## 改动实验

打开 `feedback.py`：

- 将反馈缩小到接近 0；
- 让 A 的反馈提高 B，构造交替轨迹；
- 添加会把状态拉回原点的负反馈；
- 比较 2、6、20 步的最终距离。

区分“首步差异存在”和“系统会放大首步差异”两个命题。

## 结论边界

**支持：** token 回填能在固定权重系统中产生路径依赖。  
**不支持：** 任意真实 prompt 的首 token 都会无限放大，或自然语言模型使用与 toy 完全相同的反馈矩阵。

## 延伸阅读

- [第 5 章](../course/05-reasoning-and-feedback.md)
- [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
