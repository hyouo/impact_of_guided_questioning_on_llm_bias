# 结果格式

每个实验输出一个 `ExperimentResult`：

```json
{
  "experiment_id": "C02",
  "title": "温度、softmax 与 token 赔率",
  "theory_claim": "...",
  "evidence_level": "L0-exact-identity",
  "status": "pass",
  "metrics": {},
  "checks": [
    {
      "name": "赔率恒等式",
      "passed": true,
      "observed": {},
      "expectation": "...",
      "rationale": ""
    }
  ],
  "caveats": [],
  "metadata": {
    "python": "...",
    "numpy": "..."
  },
  "created_at": "..."
}
```

## 状态含义

- `pass`：透明实验的预注册检查全部通过；不表示跨模型普遍成立。
- `fail`：至少一个预注册检查失败，应保留原始结果而不是删除案例。
- `observational`：开放模型探索，没有把单次现象包装成二元定律。
- `skipped`：依赖、模型或运行条件不满足。

## 证据层级

- `L0-exact-identity`：数学恒等式或程序精确性质。
- `L1-*`：透明玩具模型、结构反例或完全可知因果图。
- `L2-*`：开放模型观察和上下文反事实。
- `L3-*`：开放模型内部干预。
- `L4`：跨分布稳定回路证据。
- `L5`：产生新预测并被独立复现的理论。

## 为什么同时写 metrics、checks 和 caveats

`metrics` 保存完整观测；`checks` 表明在看结果前准备判断什么；`caveats` 限制结论范围。只保留一个总分，会重新制造旧研究中的不可审计问题。
