import math

import numpy as np
import pytest

from llm_theory_lab.math_utils import js_divergence, log_odds, softmax


def test_softmax_is_normalized_and_shift_invariant() -> None:
    logits = np.array([1.0, 2.0, 4.0])
    probabilities = softmax(logits)
    shifted = softmax(logits + 1000.0)
    assert probabilities.sum() == pytest.approx(1.0)
    assert np.allclose(probabilities, shifted)


def test_temperature_must_be_positive() -> None:
    with pytest.raises(ValueError):
        softmax([1.0, 2.0], 0.0)


def test_log_odds_identity() -> None:
    logits = np.array([0.4, -0.2, 1.1])
    probabilities = softmax(logits, 0.7)
    assert math.log(probabilities[2] / probabilities[0]) == pytest.approx(
        log_odds(logits, 2, 0, 0.7)
    )


def test_js_divergence_properties() -> None:
    p = np.array([0.8, 0.2])
    q = np.array([0.3, 0.7])
    assert js_divergence(p, p) == pytest.approx(0.0)
    assert js_divergence(p, q) == pytest.approx(js_divergence(q, p))
    assert js_divergence(p, q) > 0.0
