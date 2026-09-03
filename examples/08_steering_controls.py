"""Run C12 and inspect steering specificity controls."""

from __future__ import annotations

from llm_theory_lab.registry import get_experiment

result = get_experiment("C12").runner()
metrics = result.metrics

print("doses:", metrics["doses"])
print("target scores:", metrics["target_scores"])
print("target positive effect:", metrics["target_positive_effect"])
print("random absolute q99:", metrics["random_abs_q99"])
print("orthogonal effect:", metrics["orthogonal_effect"])
