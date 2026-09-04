# Transformer Circuits 公开结果复现地图

> 本页由机器可读复现注册表生成。`implemented-partial` 不等于原论文完整复现；
> `open-model-analogue` 也不等于在 Claude 私有权重上复现原始数值。

快照日期：`2026-09-04`；来源总数：**56**。

## 当前覆盖

| 覆盖状态 | 数量 |
|---|---:|
| `implemented-partial` | 20 |
| `planned` | 28 |
| `reference-only` | 8 |

## 精确复现可行性审计

| 可行性 | 数量 |
|---|---:|
| `blocked-by-proprietary-or-unpublished-assets` | 21 |
| `not-applicable` | 8 |
| `public-protocol-likely-feasible` | 12 |
| `source-specific-audit-required` | 15 |

## 全部来源

| ID | 日期 | 来源 | 主题 | 当前覆盖 | 当前模式 | 协议 | 精确复现可行性 | 优先级 | 计算 |
|---|---|---|---|---|---|---|---|---|---|
| `TC-7AD561BE51` | 2026-08-21 | [Characterizing interference weights in a tiny language model](https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html) | `global_weights` | `implemented-partial` | `transparent-proxy` | `C01` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-E98DED276D` | 2026-07 | [Verbalizable Representations Form a Global Workspace in Language Models](https://transformer-circuits.pub/2026/workspace/index.html) | `reasoning` | `implemented-partial` | `open-model-analogue` | `M02` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-5693BDC281` | 2026-06 | [Circuits Updates — June 2026](https://transformer-circuits.pub/2026/june-update/index.html) | `representations` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-7BB06AA88A` | 2026-05 | [Circuits Updates — May 2026](https://transformer-circuits.pub/2026/may-update/index.html) | `circuits` | `implemented-partial` | `transparent-proxy` | `C12` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-A3D958E6C3` | 2026-05-07 | [Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations](https://transformer-circuits.pub/2026/nla/index.html) | `activation_interfaces` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-63534E7549` | 2026-05-04 | [HeadVis: An Interactive Tool For Investigating Attention Heads](https://transformer-circuits.pub/2026/headvis/index.html) | `attention` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-A6C91CD803` | 2026-04-02 | [Emotion Concepts and their Function in a Large Language Model](https://transformer-circuits.pub/2026/emotions/index.html) | `representations` | `implemented-partial` | `transparent-proxy` | `C12` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-D7B90B802E` | 2025-12 | [Circuits Cross-Post — Activation Oracles](https://alignment.anthropic.com/2025/activation-oracles/) | `activation_interfaces` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-E6C3D9B0FA` | 2025-11 | [Circuits Updates — November 2025](https://transformer-circuits.pub/2025/november-update/index.html) | `safety` | `implemented-partial` | `transparent-proxy` | `C09` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-4C2BD77EB2` | 2025-10 | [Emergent Introspective Awareness in Large Language Models](https://transformer-circuits.pub/2025/introspection/index.html) | `introspection` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P1` | `multi-gpu` |
| `TC-D2EF558D57` | 2025-10 | [Circuits Updates — October 2025](https://transformer-circuits.pub/2025/october-update/index.html) | `representations` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-E2D64806D8` | 2025-10 | [When Models Manipulate Manifolds: The Geometry of a Counting Task](https://transformer-circuits.pub/2025/linebreaks/index.html) | `geometry` | `implemented-partial` | `open-model-analogue` | `M01` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-D6C098FC6F` | 2025-09 | [Circuits Updates — September 2025](https://transformer-circuits.pub/2025/september-update/index.html) | `in_context_learning` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-0EAF9D49E4` | 2025-08 | [Circuits Updates — August 2025](https://transformer-circuits.pub/2025/august-update/index.html) | `persona` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-28A346D65A` | 2025-07 | [A Toy Model of Mechanistic (Un)Faithfulness](https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html) | `methods` | `implemented-partial` | `transparent-proxy` | `C11` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-40408D3D25` | 2025-07 | [Tracing Attention Computation Through Feature Interactions](https://transformer-circuits.pub/2025/attention-qk/index.html) | `attention` | `implemented-partial` | `transparent-proxy` | `C04` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-9A2C59E608` | 2025-07 | [A Toy Model of Interference Weights](https://transformer-circuits.pub/2025/interference-weights/index.html) | `global_weights` | `implemented-partial` | `transparent-proxy` | `C01` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-B0B1E6EF1D` | 2025-07 | [Sparse mixtures of linear transforms](https://transformer-circuits.pub/2025/bulk-update/index.html) | `circuits` | `implemented-partial` | `transparent-proxy` | `C03` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-444BC86B75` | 2025-07 | [Circuits Updates — July 2025](https://transformer-circuits.pub/2025/july-update/index.html) | `methods` | `planned` | — | — | `source-specific-audit-required` | `P2` | `cpu` |
| `TC-33E68B26C9` | 2025-07 | [Automated Auditing](https://alignment.anthropic.com/2025/automated-auditing/) | `auditing` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-3EB24C535B` | 2025-04 | [Circuits Updates — April 2025](https://transformer-circuits.pub/2025/april-update/index.html) | `safety` | `implemented-partial` | `open-model-analogue` | `M01` | `blocked-by-proprietary-or-unpublished-assets` | `P1` | `multi-gpu` |
| `TC-F189E98B43` | 2025-04 | [Progress on Attention](https://transformer-circuits.pub/2025/attention-update/index.html) | `attention` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-573987B7FD` | 2025-03 | [On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) | `case_studies` | `implemented-partial` | `transparent-proxy`, `open-model-analogue` | `C05`, `C08`, `C09`, `M02`, `M03` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-21EF8BF2A7` | 2025-03 | [Circuit Tracing: Revealing Computational Graphs in Language Models](https://transformer-circuits.pub/2025/attribution-graphs/methods.html) | `methods` | `implemented-partial` | `transparent-proxy`, `open-model-analogue` | `C07`, `C08`, `C11`, `M03` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-BC7F77D254` | 2025-02 | [Insights on Crosscoder Model Diffing](https://transformer-circuits.pub/2025/crosscoder-diffing-update/index.html) | `model_diffing` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-183FC4CAAE` | 2025-01 | [Circuits Updates — January 2025](https://transformer-circuits.pub/2025/january-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-B81E55708E` | 2024-12 | [Stage-Wise Model Diffing](https://transformer-circuits.pub/2024/model-diffing/index.html) | `model_diffing` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-3C519406E3` | 2024-10 | [Sparse Crosscoders for Cross-Layer Features and Model Diffing](https://transformer-circuits.pub/2024/crosscoders/index.html) | `representations` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-5C4D1067C8` | 2024-10 | [Using Dictionary Learning Features as Classifiers](https://transformer-circuits.pub/2024/features-as-classifiers/index.html) | `safety` | `planned` | — | — | `blocked-by-proprietary-or-unpublished-assets` | `P2` | `multi-gpu` |
| `TC-B4AFFC2E98` | 2024-09 | [Circuits Updates — September 2024](https://transformer-circuits.pub/2024/september-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-2D75B54C8B` | 2024-08 | [Circuits Updates — August 2024](https://transformer-circuits.pub/2024/august-update/index.html) | `evaluation` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-617276E404` | 2024-07 | [Circuits Updates — July 2024](https://transformer-circuits.pub/2024/july-update/index.html) | `methods` | `planned` | — | — | `source-specific-audit-required` | `P2` | `unknown` |
| `TC-C44513DB0D` | 2024-06 | [Circuits Updates — June 2024](https://transformer-circuits.pub/2024/june-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-C2E7229B82` | 2024-05 | [Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) | `representations` | `implemented-partial` | `transparent-proxy` | `C12` | `blocked-by-proprietary-or-unpublished-assets` | `P0` | `multi-gpu` |
| `TC-7CCB80EE99` | 2024-04 | [Circuits Updates — April 2024](https://transformer-circuits.pub/2024/april-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-1B65E26883` | 2024-03 | [Circuits Updates — March 2024](https://transformer-circuits.pub/2024/march-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-C2B0D2ACF2` | 2024-03 | [Reflections on Qualitative Research](https://transformer-circuits.pub/2024/qualitative-essay/index.html) | `methodology` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-EE0687E541` | 2024-02 | [Circuits Updates — February 2024](https://transformer-circuits.pub/2024/feb-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-EB3A66CE68` | 2024-01 | [Circuits Updates — January 2024](https://transformer-circuits.pub/2024/jan-update/index.html) | `dictionary_learning` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-6B96C467BA` | 2023-10 | [Towards Monosemanticity: Decomposing Language Models With Dictionary Learning](https://transformer-circuits.pub/2023/monosemantic-features/index.html) | `representations` | `planned` | — | — | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-07DCD8CF1B` | 2023-07 | [Circuits Updates — July 2023](https://transformer-circuits.pub/2023/july-update/index.html) | `safety` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-8967179AC4` | 2023-05 | [Circuits Updates — May 2023](https://transformer-circuits.pub/2023/may-update/index.html) | `representations` | `planned` | — | — | `source-specific-audit-required` | `P2` | `single-gpu` |
| `TC-40243386D6` | 2023-05 | [Interpretability Dreams](https://transformer-circuits.pub/2023/interpretability-dreams/index.html) | `strategy` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-0DE9FB5706` | 2023-05 | [Distributed Representations: Composition & Superposition](https://transformer-circuits.pub/2023/superposition-composition/index.html) | `representations` | `implemented-partial` | `transparent-proxy` | `C06` | `source-specific-audit-required` | `P0` | `cpu` |
| `TC-6B6784D3AF` | 2023-03 | [Privileged Bases in the Transformer Residual Stream](https://transformer-circuits.pub/2023/privileged-basis/index.html) | `representations` | `implemented-partial` | `transparent-proxy` | `C10` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-5B0A82B2B9` | 2023-01 | [Superposition, Memorization, and Double Descent](https://transformer-circuits.pub/2023/toy-double-descent/index.html) | `learning_dynamics` | `planned` | — | — | `public-protocol-likely-feasible` | `P1` | `cpu` |
| `TC-84B5006C95` | 2022-09 | [Toy Models of Superposition](https://transformer-circuits.pub/2022/toy_model/index.html) | `representations` | `implemented-partial` | `transparent-proxy` | `C06` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-5D225BC073` | 2022-06 | [Softmax Linear Units](https://transformer-circuits.pub/2022/solu/index.html) | `architecture` | `planned` | — | — | `public-protocol-likely-feasible` | `P1` | `cpu` |
| `TC-11FE24F0C6` | 2022-06 | [Mechanistic Interpretability, Variables, and the Importance of Interpretable Bases](https://transformer-circuits.pub/2022/mech-interp-essay/index.html) | `methodology` | `implemented-partial` | `transparent-proxy` | `C07`, `C10` | `source-specific-audit-required` | `P0` | `cpu` |
| `TC-B8B47C35CD` | 2022-03 | [In-context Learning and Induction Heads](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html) | `in_context_learning` | `implemented-partial` | `transparent-proxy` | `C05` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-06CE357D56` | 2021-12 | [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html) | `foundations` | `implemented-partial` | `transparent-proxy` | `C02`, `C03`, `C04` | `public-protocol-likely-feasible` | `P0` | `cpu` |
| `TC-044738CB83` | 2021-12 | [Transformer Circuit Exercises](https://transformer-circuits.pub/2021/exercises/index.html) | `education` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-CE72F82AC4` | 2021-12 | [Transformer Circuit Videos](https://transformer-circuits.pub/2021/videos/index.html) | `education` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-C4622F75E3` | 2021-12 | [PySvelte](https://github.com/anthropics/PySvelte) | `visualization` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-65F5920C4B` | 2021-12 | [Garcon](https://transformer-circuits.pub/2021/garcon/index.html) | `infrastructure` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |
| `TC-B0E991068B` | 2020-03/2021-04 | [Original Distill Circuits Thread](https://distill.pub/2020/circuits/) | `foundations` | `reference-only` | `reference` | — | `not-applicable` | `P3` | `none` |

## 怎样使用这张表

1. 先看 `coverage_status`：仓库是否已经有协议，以及是否只覆盖部分结果；
2. 再看 `current_modes`：当前代码是数学/透明代理，还是开放模型类比；
3. 查看 `exact_reproduction_feasibility`：原始模型、数据和中间资产是否足够公开；
4. 只有满足该来源的 `acceptance_criteria`，才能提高覆盖状态；
5. 所有状态升级都必须附带 evidence ledger、固定 revision、结果哈希与失败记录。

## 状态语义

- **`implemented-complete`**：All registered headline result families have a validated protocol at the stated mode.
- **`implemented-partial`**：At least one relevant protocol exists, but the source's result set is not fully reproduced.
- **`planned`**：The source is in scope, but no validated protocol currently covers it.
- **`reference-only`**：The item is educational, methodological, strategic, tooling, infrastructure, or historical rather than one reproducible result set.

- **`exact-reproduction`**：Original/publicly equivalent model, data, metric, and protocol are matched within declared tolerances.
- **`open-model-analogue`**：The same directional hypothesis is tested on pinned open weights; not an original numerical reproduction.
- **`transparent-proxy`**：A fully transparent toy or mathematical system tests a structural claim or invalid inference.
- **`reference`**：Integrated as curriculum, methodology, tooling, or history without an empirical reproduction claim.

## 机器可读入口

```bash
llm-theory-lab reproduction-map
llm-theory-lab reproduction-map --status planned --priority P0
llm-theory-lab reproduction-map --mode open-model-analogue --json
llm-theory-lab validate-reproduction-map
```

规范文件：

- `reproductions/transformer_circuits_v1.json`
- `schemas/reproduction-registry-v1.schema.json`
- `sources/transformer_circuits_catalog.csv`
