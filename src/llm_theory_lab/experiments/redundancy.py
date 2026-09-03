"""Transparent counterexample for redundant paths and coarse behavior metrics."""

from __future__ import annotations

import numpy as np

from ..repro import runtime_metadata, set_global_seed
from ..result import CheckResult, ExperimentResult, checked_result


def _accuracy(margins: np.ndarray, labels: np.ndarray) -> float:
    predictions = np.where(margins >= 0.0, 1.0, -1.0)
    return float(np.mean(predictions == labels))


def run_redundant_paths(seed: int = 23, samples: int = 2_000) -> ExperimentResult:
    """Show that one path can matter to margin but not be necessary for accuracy."""

    if samples < 20 or samples % 2:
        raise ValueError("samples must be an even integer of at least 20")
    set_global_seed(seed)
    rng = np.random.default_rng(seed)

    labels = np.tile(np.array([-1.0, 1.0], dtype=np.float64), samples // 2)
    rng.shuffle(labels)

    # Two paths carry the same task signal. Either one is sufficient for the
    # current binary decision, although each contributes to the logit margin.
    path_a = labels.copy()
    path_b = labels.copy()

    baseline_margin = path_a + path_b
    ablate_a_margin = path_b
    ablate_b_margin = path_a
    ablate_both_margin = np.zeros_like(labels)

    baseline_accuracy = _accuracy(baseline_margin, labels)
    ablate_a_accuracy = _accuracy(ablate_a_margin, labels)
    ablate_b_accuracy = _accuracy(ablate_b_margin, labels)
    ablate_both_accuracy = _accuracy(ablate_both_margin, labels)

    mean_margin_change_a = float(np.mean(np.abs(baseline_margin - ablate_a_margin)))
    mean_margin_change_b = float(np.mean(np.abs(baseline_margin - ablate_b_margin)))

    checks = (
        CheckResult(
            name="单路径消融不降低当前准确率",
            passed=(
                baseline_accuracy == 1.0
                and ablate_a_accuracy == baseline_accuracy
                and ablate_b_accuracy == baseline_accuracy
            ),
            observed={
                "baseline": baseline_accuracy,
                "ablate_a": ablate_a_accuracy,
                "ablate_b": ablate_b_accuracy,
            },
            expectation="基线和两个单路径消融的分类准确率都为 1",
        ),
        CheckResult(
            name="单路径仍改变连续 margin",
            passed=mean_margin_change_a > 0.9 and mean_margin_change_b > 0.9,
            observed={
                "ablate_a": mean_margin_change_a,
                "ablate_b": mean_margin_change_b,
            },
            expectation="任一单路径消融都让平均绝对 margin 改变 > 0.9",
        ),
        CheckResult(
            name="联合消融暴露冗余",
            passed=ablate_both_accuracy == 0.5,
            observed=ablate_both_accuracy,
            expectation="平衡数据上联合消融准确率为 0.5",
        ),
    )

    return checked_result(
        experiment_id="C11",
        title="冗余路径、消融与指标饱和",
        theory_claim=(
            "单点消融在粗粒度行为指标上无效，不足以证明路径未参与计算；"
            "冗余路径可以保持决策，同时隐藏连续 margin 的因果变化。"
        ),
        evidence_level="L1-transparent-counterexample",
        metrics={
            "seed": seed,
            "samples": samples,
            "baseline_accuracy": baseline_accuracy,
            "accuracy_after_ablate_a": ablate_a_accuracy,
            "accuracy_after_ablate_b": ablate_b_accuracy,
            "accuracy_after_joint_ablation": ablate_both_accuracy,
            "mean_margin_change_after_ablate_a": mean_margin_change_a,
            "mean_margin_change_after_ablate_b": mean_margin_change_b,
            "baseline_mean_absolute_margin": float(np.mean(np.abs(baseline_margin))),
            "single_path_mean_absolute_margin": float(np.mean(np.abs(ablate_a_margin))),
        },
        checks=checks,
        caveats=(
            "这里的两条路径完全重复；真实模型中的冗余通常只在部分输入上成立。",
            "真实消融可能触发补偿、分布外状态或其他模块的非线性响应。",
            "准确率不变不等于 logits、校准、鲁棒性或生成轨迹完全不变。",
        ),
        metadata=runtime_metadata(),
    )
