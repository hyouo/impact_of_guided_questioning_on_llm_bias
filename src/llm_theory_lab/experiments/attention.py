"""Transparent single-head attention routing experiment."""

from __future__ import annotations

import math

import numpy as np

from ..math_utils import softmax
from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result


def _attend(tokens: np.ndarray, query_index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Fixed maps chosen to keep the computation readable.
    w_q = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    w_k = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    w_v = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0]])

    query = tokens[query_index] @ w_q
    keys = tokens @ w_k
    values = tokens @ w_v
    scores = keys @ query / math.sqrt(query.size)
    # Causal mask: the query can only read positions up to itself.
    scores[query_index + 1 :] = -np.inf
    probabilities = softmax(scores)
    output = probabilities @ values
    return scores, probabilities, output


def run_attention_routing() -> ExperimentResult:
    baseline_tokens = np.array(
        [
            [0.0, 1.0, 1.0],
            [0.5, 0.0, 0.0],
            [-0.2, 0.0, 2.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )
    perturbed_tokens = baseline_tokens.copy()
    # Change only the first token in a key-relevant direction.
    perturbed_tokens[0, 0] = 3.0

    baseline_scores, baseline_attention, baseline_output = _attend(baseline_tokens, query_index=3)
    perturbed_scores, perturbed_attention, perturbed_output = _attend(perturbed_tokens, query_index=3)

    baseline_top = int(np.argmax(baseline_attention))
    perturbed_top = int(np.argmax(perturbed_attention))
    output_shift = float(np.linalg.norm(perturbed_output - baseline_output))

    checks = (
        CheckResult(
            name="局部 token 改变注意力路由",
            passed=baseline_top != perturbed_top and perturbed_top == 0,
            observed={"baseline_top": baseline_top, "perturbed_top": perturbed_top},
            expectation="修改位置 0 的 key 后，最高注意力位置应转到 0",
        ),
        CheckResult(
            name="路由变化改变写回内容",
            passed=output_shift > 0.1,
            observed=output_shift,
            expectation="OV 聚合输出应产生非平凡变化",
        ),
    )

    return checked_result(
        experiment_id="C04",
        title="Attention 的 QK 路由与 OV 写回",
        theory_claim="输入既改变读取位置的 QK 分数，也改变被读取的 value；attention 不是静态标签。",
        evidence_level="L1-transparent-toy",
        metrics={
            "baseline_scores": baseline_scores,
            "perturbed_scores": perturbed_scores,
            "baseline_attention": baseline_attention,
            "perturbed_attention": perturbed_attention,
            "baseline_output": baseline_output,
            "perturbed_output": perturbed_output,
            "output_l2_shift": output_shift,
        },
        checks=checks,
        caveats=(
            "实验只有一个头、一个查询位置和固定线性映射。",
            "真实 attention 的所有可读位置通过 softmax 耦合，并受到层归一化和其他头影响。",
        ),
        metadata=runtime_metadata(),
    )
