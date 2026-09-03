# Examples

这些脚本不是另一套实验框架，而是课程中的最小变量观察入口。先在仓库根目录安装：

```bash
python -m pip install -e .
```

然后运行：

```bash
python examples/01_softmax_temperature.py
python examples/02_weight_vs_activation.py
python examples/03_attention_routing.py
python examples/04_probe_vs_causality.py
python examples/05_autoregressive_feedback.py
python examples/06_basis_invariance.py
python examples/07_redundant_paths.py
python examples/08_steering_controls.py
```

| 文件 | 对应内容 |
|---|---|
| `01_softmax_temperature.py` | C02：温度与赔率恒等式 |
| `02_weight_vs_activation.py` | C01：权重排序与当前贡献排序 |
| `03_attention_routing.py` | C04：QK score、Attention 与 OV 输出 |
| `04_probe_vs_causality.py` | C07：高可解码性但零因果使用 |
| `05_autoregressive_feedback.py` | C05：只改变首 token 后的轨迹分叉 |
| `06_basis_invariance.py` | C10：内部坐标改变而函数保持不变 |
| `07_redundant_paths.py` | C11：准确率不变但 margin 已改变 |
| `08_steering_controls.py` | C12：剂量、反向、随机与正交方向对照 |

脚本只打印关键变量。完整检查、证据等级和限制请使用 `llm-theory-lab run-toy` 生成报告。
