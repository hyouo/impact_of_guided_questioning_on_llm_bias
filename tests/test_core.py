from __future__ import annotations

import math

import numpy as np
import pytest

from llm_theory import (
    connection_contributions,
    log_odds_from_logits,
    make_demo_model,
    softmax,
    weight_effectiveness_proxy,
)


def test_softmax_and_log_odds_identity() -> None:
    logits = np.array([1.4, -0.2, 0.7])
    probabilities = softmax(logits, temperature=0.8)
    assert probabilities.sum() == pytest.approx(1.0)
    assert math.log(probabilities[0] / probabilities[1]) == pytest.approx(
        log_odds_from_logits(logits, 0, 1, temperature=0.8)
    )


def test_fixed_weights_different_inputs_activate_different_paths() -> None:
    model = make_demo_model()
    task_features = model.encode([1.0, 0.1, 0.1])
    safety_features = model.encode([0.4, 1.0, 0.1])
    assert task_features[0] > task_features[1]
    assert safety_features[1] > safety_features[0]
    assert np.argmax(model.logits([1.0, 0.1, 0.1])) == 0
    assert np.argmax(model.logits([0.4, 1.0, 0.1])) == 1


def test_connection_contribution_depends_on_source_activation() -> None:
    weights = np.array([[100.0, 2.0]])
    contributions = connection_contributions(weights, [0.0, 3.0])
    assert contributions.tolist() == [[0.0, 6.0]]


def test_forced_first_token_diverges_future_trajectory() -> None:
    model = make_demo_model()
    state = [0.63, 0.60, 0.08]
    answer_path = model.generate(state, 5, forced_tokens=("ANSWER",))
    refusal_path = model.generate(state, 5, forced_tokens=("REFUSE",))
    assert answer_path[0].token == "ANSWER"
    assert refusal_path[0].token == "REFUSE"
    assert [step.token for step in answer_path] != [step.token for step in refusal_path]
    assert not np.allclose(answer_path[-1].state, refusal_path[-1].state)


def test_large_weight_can_be_less_effective_on_data_distribution() -> None:
    large_rare = weight_effectiveness_proxy(10.0, [0.0, 0.0, 0.001, 0.0])
    small_active = weight_effectiveness_proxy(1.0, [1.0, 0.8, 1.2, 1.0])
    assert large_rare < small_active


def test_invalid_temperature_rejected() -> None:
    with pytest.raises(ValueError):
        softmax([1.0, 2.0], temperature=0.0)
