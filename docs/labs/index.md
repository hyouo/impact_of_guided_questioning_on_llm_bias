# 实验手册｜不要只看 `pass`

实验的目标不是让 CI 变绿，而是训练你把理论命题拆成可观测量、对照和结论边界。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

检查环境：

```bash
llm-theory-lab list
pytest
```

## 五个实验

| 实验 | 学会什么 | 对应代码 |
|---|---|---|
| [1. Softmax 与赔率](01-softmax-and-odds.md) | 从 logits 推导 token 相对概率 | C02 |
| [2. 权重与激活](02-weight-vs-activation.md) | 区分 magnitude、contribution、effectiveness | C01 |
| [3. Attention 路由](03-attention-routing.md) | 分开观察 QK 和 OV | C04 |
| [4. Probe 与因果](04-probe-vs-causality.md) | 构造“可解码但未被使用”的反例 | C07、C08 |
| [5. 反馈与安全路由](05-feedback-and-safety.md) | 分析首 token 反馈和识别—策略分离 | C05、C09 |

## 统一实验流程

每次都按这个顺序：

1. 先写下你预测哪个指标会怎样变化；
2. 运行 `llm-theory-lab explain Cxx`，核对反证条件；
3. 运行实验并打开 Markdown 报告；
4. 修改一个参数，预测新结果；
5. 记录失败、反常或不确定结果；
6. 写出“本实验最多能说明什么”。

## 输出文件

```bash
llm-theory-lab run-toy --output-dir reports/my-run
```

会产生：

```text
reports/my-run/results.json   # 机器可读原始结果
reports/my-run/report.md      # 人类可读报告
```

`results.json` 应作为分析来源，`report.md` 是确定性渲染。不要手工改报告来改变结论。

## 实验解释规则

- `C01–C09` 是透明玩具实验，证据级别主要是 L0/L1；
- 玩具实验通过，证明的是数学关系、结构可能性或逻辑反例；
- 开放模型实验需要额外依赖，默认是观察性或局部干预；
- 单次运行不能支持“所有大模型”结论；
- 任何 safety 结论都只使用无害代理。
