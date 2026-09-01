"""A fixed-weight network whose active features depend on the input."""

from __future__ import annotations

import numpy as np

from ..math_utils import softmax
from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result


def run_input_conditioning() -> ExperimentResult:
    # Input axes: answer evidence, policy evidence, uncertainty.
    feature_map = np.array(
        [
            [1.3, 0.0, 0.2, 0.6],
            [0.0, 1.4, 0.1, -0.2],
            [0.1, 0.1, 1.2, 0.0],
        ],
        dtype=np.float64,
    )
    bias = np.array([-0.1, -0.1, -0.05, 0.0], dtype=np.float64)
    output_map = np.array(
        [
            [2.0, -0.6, 0.0],
            [-0.8, 2.1, 0.1],
            [-0.1, -0.1, 1.8],
            [0.8, 0.0, 0.1],
        ],
        dtype=np.float64,
    )
    labels = ("ANSWER", "DECLINE", "CLARIFY")

    inputs = {
        "task_dominant": np.array([1.0, 0.0, 0.1]),
        "policy_dominant": np.array([0.1, 1.0, 0.0]),
        "uncertain": np.array([0.1, 0.1, 1.0]),
    }
    observations: dict[str, dict[str, object]] = {}
    top_tokens: list[str] = []

    for name, vector in inputs.items():
        features = np.maximum(0.0, vector @ feature_map + bias)
        logits = features @ output_map
        probabilities = softmax(logits)
        top_token = labels[int(np.argmax(probabilities))]
        top_tokens.append(top_token)
        observations[name] = {
            "input": vector,
            "features": features,
            "logits": logits,
            "probabilities": probabilities,
            "top_token": top_token,
        }

    expected = ["ANSWER", "DECLINE", "CLARIFY"]
    checks = (
        CheckResult(
            name="固定权重下形成不同激活模式",
            passed=len({tuple(np.round(obs["features"], 8)) for obs in observations.values()}) == 3,
            observed={key: value["features"] for key, value in observations.items()},
            expectation="三个输入应产生三个不同特征向量",
        ),
        CheckResult(
            name="输出模式随输入翻转",
            passed=top_tokens == expected,
            observed=top_tokens,
            expectation=f"预期顺序为 {expected}",
        ),
    )

    return checked_result(
        experiment_id="C03",
        title="固定权重下的输入条件计算",
        theory_claim="标准推理中权重可以完全不变，而不同 input 仍选择不同特征和输出路径。",
        evidence_level="L1-transparent-toy",
        metrics={"weights_fixed": True, "observations": observations},
        checks=checks,
        caveats=(
            "这是低维 ReLU 网络，不代表真实模型只有四个可分离特征。",
            "真实网络的输入作用分布在 token、位置、层、头和非线性之中。",
        ),
        metadata=runtime_metadata(),
    )
