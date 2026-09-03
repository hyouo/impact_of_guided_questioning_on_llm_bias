# Examples

这些脚本不是另一套实验框架，而是课程中的最小代码入口。请先在仓库根目录安装：

```bash
pip install -e .
```

然后运行：

```bash
python examples/01_softmax_temperature.py
python examples/02_weight_vs_activation.py
python examples/03_attention_routing.py
python examples/04_probe_vs_causality.py
python examples/05_autoregressive_feedback.py
```

| 文件 | 对应内容 |
|---|---|
| `01_softmax_temperature.py` | C02：温度与赔率恒等式 |
| `02_weight_vs_activation.py` | C01：权重排序与当前贡献排序 |
| `03_attention_routing.py` | C04：QK score、Attention 与 OV 输出 |
| `04_probe_vs_causality.py` | C07：高可解码性但零因果使用 |
| `05_autoregressive_feedback.py` | C05：只改变首 token 后的轨迹分叉 |

脚本只打印关键变量。完整预注册检查、证据等级和限制请使用 `llm-theory-lab run-toy` 生成报告。
