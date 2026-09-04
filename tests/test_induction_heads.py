import numpy as np
import pytest

from llm_theory_lab.experiments.induction_heads import (
    induction_targets,
    rank_induction_heads,
    score_induction_attention,
)


def test_induction_targets_find_previous_successor() -> None:
    assert induction_targets([10, 11, 12, 13, 10]) == [(4, 1)]
    assert induction_targets([5, 6, 5, 7, 5]) == [(2, 1), (4, 3)]


def test_score_induction_attention_separates_target_from_controls() -> None:
    attentions = np.zeros((2, 2, 5, 5), dtype=np.float64)
    attentions[:, :, 4, :5] = 0.2

    attentions[1, 0, 4, :5] = 0.05
    attentions[1, 0, 4, 1] = 0.8

    result = score_induction_attention(attentions, [10, 11, 12, 13, 10])
    scores = np.asarray(result["induction_score"])

    assert result["target_count"] == 1
    assert scores[1, 0] == pytest.approx(0.75)
    assert scores[0, 0] == pytest.approx(0.0)

    ranked = rank_induction_heads(scores, top_k=2)
    assert ranked[0]["layer"] == 1
    assert ranked[0]["head"] == 0
    assert ranked[0]["score"] == pytest.approx(0.75)


def test_induction_scoring_rejects_bad_shapes_and_sequences() -> None:
    with pytest.raises(ValueError):
        score_induction_attention(np.zeros((2, 5, 5)), [1, 2, 1])
    with pytest.raises(ValueError):
        score_induction_attention(np.zeros((1, 1, 3, 3)), [1, 2, 3])
    with pytest.raises(ValueError):
        rank_induction_heads(np.zeros((2, 2, 2)))
    with pytest.raises(ValueError):
        rank_induction_heads(np.zeros((2, 2)), top_k=0)
