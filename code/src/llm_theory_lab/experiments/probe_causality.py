"""A counterexample: high probe accuracy without causal use by the model."""

from __future__ import annotations

import numpy as np

from ..repro import runtime_metadata, set_global_seed
from ..result import CheckResult, ExperimentResult, checked_result


def _fit_linear_probe(features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    design = np.column_stack([features, np.ones(features.shape[0])])
    regularizer = 1e-6 * np.eye(design.shape[1])
    regularizer[-1, -1] = 0.0
    return np.linalg.solve(design.T @ design + regularizer, design.T @ labels)


def run_probe_vs_causality(seed: int = 13, samples: int = 4_000) -> ExperimentResult:
    if samples < 100:
        raise ValueError("samples must be at least 100")
    set_global_seed(seed)
    rng = np.random.default_rng(seed)

    causal_variable = rng.choice([-1.0, 1.0], size=samples)
    decodable_but_unused = rng.choice([-1.0, 1.0], size=samples)
    hidden = np.column_stack(
        [
            causal_variable + rng.normal(0.0, 0.08, size=samples),
            decodable_but_unused + rng.normal(0.0, 0.08, size=samples),
        ]
    )

    split = int(samples * 0.7)
    probe = _fit_linear_probe(hidden[:split], decodable_but_unused[:split])
    held_out_design = np.column_stack([hidden[split:], np.ones(samples - split)])
    probe_predictions = np.where(held_out_design @ probe >= 0.0, 1.0, -1.0)
    probe_accuracy = float(np.mean(probe_predictions == decodable_but_unused[split:]))

    # The tested model's output head uses only hidden dimension 0.
    output_gap = 2.0 * hidden[:, 0]
    nuisance_ablated = hidden.copy()
    nuisance_ablated[:, 1] = 0.0
    output_gap_after_nuisance_ablation = 2.0 * nuisance_ablated[:, 0]

    causal_ablated = hidden.copy()
    causal_ablated[:, 0] = 0.0
    output_gap_after_causal_ablation = 2.0 * causal_ablated[:, 0]

    nuisance_effect = float(np.mean(np.abs(output_gap_after_nuisance_ablation - output_gap)))
    causal_effect = float(np.mean(np.abs(output_gap_after_causal_ablation - output_gap)))

    checks = (
        CheckResult(
            name="未使用变量高度可解码",
            passed=probe_accuracy > 0.98,
            observed=probe_accuracy,
            expectation="held-out probe accuracy > 0.98",
        ),
        CheckResult(
            name="消融可解码变量不改变模型输出",
            passed=nuisance_effect < 1e-12,
            observed=nuisance_effect,
            expectation="平均输出变化接近 0",
        ),
        CheckResult(
            name="正向因果对照有效",
            passed=causal_effect > 1.5,
            observed=causal_effect,
            expectation="消融真正被输出头读取的变量应显著改变输出",
        ),
    )

    return checked_result(
        experiment_id="C07",
        title="可解码信息不等于因果使用",
        theory_claim="probe 能读出一个变量，只证明表示中存在信息；不能单独证明原模型使用它生成答案。",
        evidence_level="L1-transparent-counterexample",
        metrics={
            "seed": seed,
            "samples": samples,
            "probe_accuracy_unused_variable": probe_accuracy,
            "mean_output_change_after_unused_ablation": nuisance_effect,
            "mean_output_change_after_causal_ablation": causal_effect,
            "probe_weights": probe,
        },
        checks=checks,
        caveats=(
            "这是刻意构造的反例，用于否定一种错误推理，而不是估计真实 probe 的可靠度。",
            "在真实模型中，需要 patching、ablation、mediation 等方法检验信息是否被使用。",
        ),
        metadata=runtime_metadata(),
    )
