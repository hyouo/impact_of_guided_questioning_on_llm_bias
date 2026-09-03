"""Methodology experiment for steering specificity and control directions."""

from __future__ import annotations

import numpy as np

from ..repro import runtime_metadata, set_global_seed
from ..result import CheckResult, ExperimentResult, checked_result


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise ValueError("cannot normalize a zero vector")
    return vector / norm


def run_steering_controls(
    seed: int = 29,
    dimensions: int = 64,
    random_controls: int = 4_096,
) -> ExperimentResult:
    """Compare a target-aligned steering direction with equal-norm controls."""

    if dimensions < 4:
        raise ValueError("dimensions must be at least 4")
    if random_controls < 100:
        raise ValueError("random_controls must be at least 100")
    set_global_seed(seed)
    rng = np.random.default_rng(seed)

    readout_direction = _unit(rng.normal(size=dimensions))
    baseline_state = np.zeros(dimensions, dtype=np.float64)
    doses = np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=np.float64)
    target_scores = np.array(
        [float((baseline_state + dose * readout_direction) @ readout_direction) for dose in doses]
    )

    controls = rng.normal(size=(random_controls, dimensions))
    controls /= np.linalg.norm(controls, axis=1, keepdims=True)
    random_effects = controls @ readout_direction
    random_abs_q99 = float(np.quantile(np.abs(random_effects), 0.99))

    orthogonal = rng.normal(size=dimensions)
    orthogonal -= float(orthogonal @ readout_direction) * readout_direction
    orthogonal = _unit(orthogonal)
    orthogonal_effect = float(orthogonal @ readout_direction)

    target_positive_effect = float(target_scores[-1] - target_scores[2])
    target_negative_effect = float(target_scores[0] - target_scores[2])

    checks = (
        CheckResult(
            name="目标方向呈单调剂量响应",
            passed=bool(np.all(np.diff(target_scores) > 0.0)),
            observed={"doses": doses, "scores": target_scores},
            expectation="剂量增加时 readout score 严格增加",
        ),
        CheckResult(
            name="反向干预产生反号效应",
            passed=target_positive_effect > 0.9 and target_negative_effect < -0.9,
            observed={
                "positive": target_positive_effect,
                "negative": target_negative_effect,
            },
            expectation="+1 与 -1 剂量产生大小约 1、符号相反的效应",
        ),
        CheckResult(
            name="目标效应超过等范数随机对照",
            passed=target_positive_effect > random_abs_q99,
            observed={
                "target_effect": target_positive_effect,
                "random_abs_q99": random_abs_q99,
            },
            expectation="目标效应大于随机方向绝对效应的 99% 分位数",
        ),
        CheckResult(
            name="正交方向是零效应对照",
            passed=abs(orthogonal_effect) < 1e-12,
            observed=orthogonal_effect,
            expectation="构造的正交方向对 readout 的效应接近 0",
        ),
    )

    return checked_result(
        experiment_id="C12",
        title="Steering 的剂量、反向与随机方向对照",
        theory_claim=(
            "Steering 成功首先证明可操纵性；只有相对于等范数随机/正交方向、"
            "反向干预和剂量响应具有特异性时，机制解释才更可信。"
        ),
        evidence_level="L1-transparent-methodology",
        metrics={
            "seed": seed,
            "dimensions": dimensions,
            "random_controls": random_controls,
            "doses": doses,
            "target_scores": target_scores,
            "target_positive_effect": target_positive_effect,
            "target_negative_effect": target_negative_effect,
            "random_effect_mean": float(np.mean(random_effects)),
            "random_effect_std": float(np.std(random_effects)),
            "random_abs_q99": random_abs_q99,
            "orthogonal_effect": orthogonal_effect,
        },
        checks=checks,
        caveats=(
            "目标方向由 readout 方向直接构造，因此实验验证的是对照逻辑，不是特征发现。",
            "真实模型 steering 还需错误层、错误位置、行为副作用和跨提示复现。",
            "超过随机方向不证明该方向是唯一自然表征，也不证明它对原行为必要。",
        ),
        metadata=runtime_metadata(),
    )
