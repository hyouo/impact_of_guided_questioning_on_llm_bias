"""Harmless proxy for separating recognition, policy state, and output action."""

from __future__ import annotations

import numpy as np

from ..math_utils import softmax
from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result


def _action_distribution(state: np.ndarray) -> np.ndarray:
    # State axes: restricted-category detected, decline-policy state, completion state.
    # The first axis is deliberately not read directly by the output head.
    output_map = np.array(
        [
            [0.0, 0.0, 0.0],
            [-0.2, 2.2, 0.2],
            [2.0, -0.4, 0.2],
        ],
        dtype=np.float64,
    )
    return softmax(state @ output_map)


def run_recognition_action_dissociation() -> ExperimentResult:
    labels = ("PROCEED", "DECLINE", "ASK")
    natural_state = np.array([1.0, 0.10, 1.20], dtype=np.float64)
    patched_state = natural_state.copy()
    patched_state[1] = 1.50

    natural_probabilities = _action_distribution(natural_state)
    patched_probabilities = _action_distribution(patched_state)
    natural_action = labels[int(np.argmax(natural_probabilities))]
    patched_action = labels[int(np.argmax(patched_probabilities))]

    checks = (
        CheckResult(
            name="识别信号存在但不保证行为",
            passed=natural_state[0] == 1.0 and natural_action == "PROCEED",
            observed={
                "restriction_detected": natural_state[0],
                "chosen_action": natural_action,
                "probabilities": natural_probabilities,
            },
            expectation="检测维度可为高，但若未路由到 policy state，输出仍可选择 PROCEED",
        ),
        CheckResult(
            name="增强策略状态可翻转行为",
            passed=patched_action == "DECLINE",
            observed={"chosen_action": patched_action, "probabilities": patched_probabilities},
            expectation="只 patch decline-policy state 后应转为 DECLINE",
        ),
    )

    return checked_result(
        experiment_id="C09",
        title="识别、策略状态与最终行为的分离",
        theory_claim="内部识别到某类输入，不等于相应策略状态已形成，也不等于该行为会赢得输出竞争。",
        evidence_level="L1-harmless-structural-counterexample",
        metrics={
            "labels": labels,
            "natural_state": natural_state,
            "natural_probabilities": natural_probabilities,
            "patched_state": patched_state,
            "patched_probabilities": patched_probabilities,
        },
        checks=checks,
        caveats=(
            "这是访问控制类无害代理，不模拟任何真实有害请求或越狱载荷。",
            "它只证明 detection、policy、action 在机制上可分离，不证明具体模型采用同一坐标。",
        ),
        metadata=runtime_metadata(),
    )
