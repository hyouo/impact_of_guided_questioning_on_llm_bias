"""Exact numerical checks for temperature, softmax, and token odds."""

from __future__ import annotations

import math

import numpy as np

from ..math_utils import log_odds, softmax
from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result


def run_temperature_odds() -> ExperimentResult:
    logits = np.array([0.2, -0.1, 1.4], dtype=np.float64)
    token_i, token_j = 2, 0
    temperatures = (0.5, 1.0, 2.0)

    identity_errors: dict[str, float] = {}
    for temperature in temperatures:
        probabilities = softmax(logits, temperature)
        observed = math.log(probabilities[token_i] / probabilities[token_j])
        expected = log_odds(logits, token_i, token_j, temperature)
        identity_errors[str(temperature)] = abs(observed - expected)

    base = softmax(logits, 1.0)
    shifted_logits = logits.copy()
    shifted_logits[token_i] += 1.0
    shifted = softmax(shifted_logits, 1.0)
    odds_multiplier = (shifted[token_i] / shifted[token_j]) / (base[token_i] / base[token_j])

    checks = (
        CheckResult(
            name="赔率恒等式",
            passed=max(identity_errors.values()) < 1e-12,
            observed=identity_errors,
            expectation="log(p_i/p_j) = (z_i-z_j)/T，数值误差 < 1e-12",
        ),
        CheckResult(
            name="T=1 时 logit +1",
            passed=abs(odds_multiplier - math.e) < 1e-12,
            observed=odds_multiplier,
            expectation="赔率乘数应等于 e",
        ),
        CheckResult(
            name="低温放大相对差异",
            passed=abs(log_odds(logits, token_i, token_j, 0.5))
            > abs(log_odds(logits, token_i, token_j, 2.0)),
            observed={
                "T=0.5": log_odds(logits, token_i, token_j, 0.5),
                "T=2.0": log_odds(logits, token_i, token_j, 2.0),
            },
            expectation="相同 logit 差在较低正温度下具有更大 log-odds",
        ),
    )

    return checked_result(
        experiment_id="C02",
        title="温度、softmax 与 token 赔率",
        theory_claim="两个 token 的相对赔率只由 logit 差与正温度决定；小 logit 变化可指数放大赔率。",
        evidence_level="L0-exact-identity",
        metrics={
            "logits": logits,
            "identity_absolute_errors": identity_errors,
            "odds_multiplier_after_plus_one_logit_at_T1": odds_multiplier,
            "e": math.e,
        },
        checks=checks,
        caveats=(
            "数学 softmax 要求 T>0；许多 API 的 temperature=0 是 greedy/argmax 的约定。",
            "赔率变化本身不保证最终采样 token 翻转，还取决于全部词表 logits 和解码规则。",
        ),
        metadata=runtime_metadata(),
    )
