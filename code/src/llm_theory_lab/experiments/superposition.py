"""A geometric existence proof for sparse superposition and interference."""

from __future__ import annotations

from itertools import combinations

import numpy as np

from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result


def run_superposition() -> ExperimentResult:
    feature_count = 5
    dimension = 2
    angles = np.linspace(0.0, 2.0 * np.pi, feature_count, endpoint=False)
    directions = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    gram = directions @ directions.T

    single_correct = 0
    for feature in range(feature_count):
        hidden = directions[feature]
        decoded = int(np.argmax(directions @ hidden))
        single_correct += int(decoded == feature)
    single_accuracy = single_correct / feature_count

    pair_correct = 0
    pair_records: list[dict[str, object]] = []
    pairs = list(combinations(range(feature_count), 2))
    for first, second in pairs:
        hidden = directions[first] + directions[second]
        scores = directions @ hidden
        decoded = set(np.argsort(scores)[-2:].tolist())
        expected = {first, second}
        correct = decoded == expected
        pair_correct += int(correct)
        pair_records.append(
            {
                "active_features": [first, second],
                "decoded_top2": sorted(decoded),
                "correct": correct,
                "scores": scores,
            }
        )
    pair_accuracy = pair_correct / len(pairs)

    max_off_diagonal = float(np.max(np.abs(gram - np.eye(feature_count))))
    checks = (
        CheckResult(
            name="特征数大于维度",
            passed=feature_count > dimension,
            observed={"features": feature_count, "dimensions": dimension},
            expectation="F>d，表示是过完备的",
        ),
        CheckResult(
            name="稀疏单特征仍可识别",
            passed=single_accuracy == 1.0,
            observed=single_accuracy,
            expectation="单个特征激活时，最近方向识别准确率为 1",
        ),
        CheckResult(
            name="共激活产生干扰",
            passed=pair_accuracy < single_accuracy and max_off_diagonal > 0.1,
            observed={
                "single_accuracy": single_accuracy,
                "pair_accuracy": pair_accuracy,
                "max_abs_off_diagonal_gram": max_off_diagonal,
            },
            expectation="两特征共激活时识别下降，且方向非正交",
        ),
    )

    return checked_result(
        experiment_id="C06",
        title="稀疏 superposition 与共激活干扰",
        theory_claim="当特征稀疏时，特征数可以超过表示维度；非正交共享容量会在共激活时产生干扰。",
        evidence_level="L1-transparent-toy",
        metrics={
            "feature_directions": directions,
            "gram_matrix": gram,
            "single_feature_accuracy": single_accuracy,
            "pair_feature_accuracy": pair_accuracy,
            "pair_records": pair_records,
        },
        checks=checks,
        caveats=(
            "正五边形方向是人为构造的，不是从模型中学习出的 SAE 字典。",
            "真实语言特征并非独立同分布，且可能位于子空间或连续流形上。",
        ),
        metadata=runtime_metadata(),
    )
