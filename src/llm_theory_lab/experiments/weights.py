"""Experiments about fixed weights, activations, and distributional effectiveness."""

from __future__ import annotations

import numpy as np

from ..repro import runtime_metadata, set_global_seed
from ..result import CheckResult, ExperimentResult, checked_result


def run_weight_activation(seed: int = 7, samples: int = 20_000) -> ExperimentResult:
    """Show that magnitude, current contribution, and effectiveness differ."""

    if samples < 100:
        raise ValueError("samples must be at least 100")
    set_global_seed(seed)
    rng = np.random.default_rng(seed)

    large_weight = 8.0
    smaller_weight = 1.2

    rare_mask = rng.random(samples) < 0.01
    rare_activation = rare_mask * rng.normal(loc=0.05, scale=0.005, size=samples)
    common_activation = rng.normal(loc=1.0, scale=0.05, size=samples)

    large_effectiveness = float(np.mean(np.square(large_weight * rare_activation)))
    small_effectiveness = float(np.mean(np.square(smaller_weight * common_activation)))

    current_source = np.array([0.0, 1.0], dtype=np.float64)
    current_weights = np.array([large_weight, smaller_weight], dtype=np.float64)
    current_contributions = current_weights * current_source

    checks = (
        CheckResult(
            name="大权重当前可以零贡献",
            passed=bool(current_contributions[0] == 0.0),
            observed=float(current_contributions[0]),
            expectation="源激活为 0 时，权重再大也应有 0 直接贡献",
        ),
        CheckResult(
            name="较小权重当前可以主导",
            passed=bool(current_contributions[1] > current_contributions[0]),
            observed=current_contributions.tolist(),
            expectation="当前贡献由 weight × activation 决定",
        ),
        CheckResult(
            name="权重大小不等于分布有效性",
            passed=bool(
                large_weight > smaller_weight and large_effectiveness < small_effectiveness
            ),
            observed={
                "large_weight": large_weight,
                "large_effectiveness": large_effectiveness,
                "smaller_weight": smaller_weight,
                "smaller_effectiveness": small_effectiveness,
            },
            expectation="罕见弱激活的大权重可比常见激活的小权重更不有效",
        ),
    )

    return checked_result(
        experiment_id="C01",
        title="权重大小、当前贡献与分布有效性",
        theory_claim="参数只规定潜在映射；一次输入中的作用还取决于源激活和下游路径。",
        evidence_level="L1-transparent-toy",
        metrics={
            "seed": seed,
            "samples": samples,
            "rare_feature_activation_rate": float(np.mean(rare_mask)),
            "current_contributions": current_contributions,
            "large_weight_effectiveness_proxy": large_effectiveness,
            "smaller_weight_effectiveness_proxy": small_effectiveness,
            "effectiveness_ratio_large_over_small": large_effectiveness / small_effectiveness,
        },
        checks=checks,
        caveats=(
            "这里的 effectiveness 是 E[(w·a)^2] 玩具代理，不是任何论文指标的逐字复现。",
            "真实 Transformer 还包含门控、归一化、注意力、抵消和冗余路径。",
        ),
        metadata=runtime_metadata(),
    )
