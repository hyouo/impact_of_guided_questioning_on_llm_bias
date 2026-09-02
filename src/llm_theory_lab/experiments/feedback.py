"""Autoregressive feedback and prefix-dependent trajectory experiment."""

from __future__ import annotations

import numpy as np

from ..math_utils import softmax
from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result

TOKEN_LABELS = ("A", "B", "C")
OUTPUT_MAP = np.array(
    [
        [2.0, -1.0, 0.0],
        [-1.0, 2.0, 0.0],
    ],
    dtype=np.float64,
)
FEEDBACK = np.array(
    [
        [0.55, -0.10],
        [-0.10, 0.55],
        [0.05, 0.05],
    ],
    dtype=np.float64,
)


def _generate(
    initial_state: np.ndarray, first_token: int, steps: int = 6
) -> tuple[list[str], np.ndarray]:
    state = initial_state.copy()
    tokens: list[str] = []
    for step in range(steps):
        logits = state @ OUTPUT_MAP
        probabilities = softmax(logits)
        token_index = first_token if step == 0 else int(np.argmax(probabilities))
        tokens.append(TOKEN_LABELS[token_index])
        state = state + FEEDBACK[token_index]
    return tokens, state


def run_autoregressive_feedback() -> ExperimentResult:
    initial_state = np.array([0.02, 0.02], dtype=np.float64)
    trajectory_a, final_a = _generate(initial_state, first_token=0)
    trajectory_b, final_b = _generate(initial_state, first_token=1)
    final_distance = float(np.linalg.norm(final_a - final_b))

    checks = (
        CheckResult(
            name="不同首 token 产生不同序列",
            passed=trajectory_a != trajectory_b,
            observed={"prefix_A": trajectory_a, "prefix_B": trajectory_b},
            expectation="在相同权重与初态下，只改变首 token 应使轨迹分叉",
        ),
        CheckResult(
            name="反馈强化局部模式",
            passed=trajectory_a[1:] == ["A"] * 5 and trajectory_b[1:] == ["B"] * 5,
            observed={"prefix_A": trajectory_a, "prefix_B": trajectory_b},
            expectation="A/B 的反馈应分别强化后续 A/B",
        ),
        CheckResult(
            name="最终状态显著分离",
            passed=final_distance > 2.0,
            observed=final_distance,
            expectation="两条轨迹的最终状态 L2 距离 > 2",
        ),
    )

    return checked_result(
        experiment_id="C05",
        title="首 token 与自回归轨迹分叉",
        theory_claim="被选中的 token 写回上下文后成为新输入，因此很小的首步差异可累积成大轨迹差异。",
        evidence_level="L1-transparent-toy",
        metrics={
            "initial_state": initial_state,
            "trajectory_forced_A": trajectory_a,
            "trajectory_forced_B": trajectory_b,
            "final_state_A": final_a,
            "final_state_B": final_b,
            "final_state_distance": final_distance,
        },
        checks=checks,
        caveats=(
            "反馈矩阵是人为构造的，证明的是结构可能性，不是自然语言生成中的效应大小。",
            "真实模型还会受长上下文、采样和多条竞争路径影响。",
        ),
        metadata=runtime_metadata(),
    )
