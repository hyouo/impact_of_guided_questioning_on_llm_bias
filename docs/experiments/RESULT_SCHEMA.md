# 结果格式

每个实验输出一个 `ExperimentResult`。结果既保存数值，也保存怎样解释和怎样不解释这些数值：

```json
{
  "experiment_id": "C02",
  "title": "温度与赔率",
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
    "numpy": "...",
    "learning": {
      "claim_id": "H-C02",
      "claim_revision": 1,
      "reproduction_status": "transparent-proxy",
      "category": "decoding",
      "intuition": "...",
      "falsifier": "...",
      "lesson_path": "docs/course/02-weights-activations-and-logits.md",
      "lab_path": "docs/labs/01-softmax-and-odds.md",
      "does_not_show": "...",
      "source_urls": ["..."]
    }
  },
  "created_at": "..."
}
```

## 状态含义

- `pass`：透明实验的预注册检查全部通过；不表示跨模型普遍成立。
- `fail`：至少一个预注册检查失败，应保留原始结果而不是删除案例。
- `observational`：开放模型探索，没有把单次现象包装成二元定律。
- `skipped`：依赖、模型或合法运行条件不满足。
- `inconclusive`：现有样本、指标或对照不足以区分支持与反证。
- `error`：代码、下载或运行环境异常。

代码错误、下载失败、无结论和理论反证必须使用不同状态。复现运行器会按实验独立捕获异常，因此一个 `error` 不会删除其他实验已经产生的证据。

## 证据层级

- `L0-exact-identity`：数学恒等式或程序精确性质。
- `L1-*`：透明玩具模型、结构反例或完全可知因果图。
- `L2-*`：开放模型观察和上下文反事实。
- `L3-*`：开放模型内部干预。
- `L4`：跨分布稳定回路证据。
- `L5`：产生新预测并被独立复现的理论。

证据等级不是分数。一次 L1 `pass` 不能因结果整齐而升级为 L4；一次 L3 patching 也不自动证明机制唯一。

## 为什么同时写 metrics、checks、caveats 和 learning

- `metrics`：保存完整观测，不只保存最终判断；
- `checks`：表明在看结果前准备判断什么；
- `caveats`：限制具体实现和数据的解释范围；
- `learning`：把报告重新连接到 claim ID、课程、实验手册、公开来源、反证条件与禁止外推。

只保留一个总分或一排绿色状态，会重新制造不可审计问题。Markdown 报告因此会在数值表之前展示状态解释、反证条件和不能推出的结论。

## 从单次结果到证据台账

`ExperimentResult` 是单次实验对象；正式研究记录还需要版本化 claim、复现类型、模型 revision、数据/生成器哈希、代码 commit、artifact 哈希和来源映射。这些字段存入[证据台账与复现 bundle](EVIDENCE_LEDGER.md)。

```bash
llm-theory-lab reproduce --output-dir reports/reproduction
llm-theory-lab validate-evidence reports/reproduction --bundle
```

机器可读 ledger schema 位于：

```text
schemas/evidence-ledger-v1.schema.json
```
