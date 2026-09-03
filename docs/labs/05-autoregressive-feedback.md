# C05｜首 token 与自回归轨迹

## 问题

在初始状态和全部权重相同的条件下，只改变第一个 token，后续状态与输出为什么可能持续分叉？

## 先做预测

分别强制首 token 为 A 和 B。预测第二步 logits、后续序列和最终状态距离。再写出一种会让两条轨迹重新收敛的反馈矩阵。

## 运行

```bash
llm-theory-lab explain C05
llm-theory-lab run-toy --ids C05 --output-dir reports/c05
python examples/05_autoregressive_feedback.py
```

## 要检查的量

- `trajectory_forced_A` 与 `trajectory_forced_B`；
- `final_state_A` 与 `final_state_B`；
- `final_state_distance`。

完整链条是：

```text
选中 token
→ token 对应状态反馈
→ 下一步 logits 改变
→ 新 token 更可能延续当前模式
```

## 改动实验

打开 `src/llm_theory_lab/experiments/feedback.py`：

- 把反馈缩小到接近 0；
- 让 A 的反馈提高 B，构造交替轨迹；
- 添加把状态拉回原点的负反馈；
- 比较 2、6、20 步后的距离。

区分“首步差异存在”和“系统会放大首步差异”两个命题。

## 结论边界

**支持：** token 回填能在固定权重系统中产生路径依赖。  
**不支持：** 任意真实 prompt 的首 token 都会无限放大，或自然语言模型采用与 toy 相同的反馈矩阵。
