"""Run C07 and contrast decodability with causal use."""

from __future__ import annotations

from llm_theory_lab.registry import get_experiment

result = get_experiment("C07").runner()
metrics = result.metrics

print("probe accuracy on unused variable:", metrics["probe_accuracy_unused_variable"])
print("output change after unused ablation:", metrics["mean_output_change_after_unused_ablation"])
print("output change after causal ablation:", metrics["mean_output_change_after_causal_ablation"])
