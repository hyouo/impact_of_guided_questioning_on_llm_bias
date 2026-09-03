"""Run C11 and compare accuracy with continuous margin effects."""

from __future__ import annotations

from llm_theory_lab.registry import get_experiment

result = get_experiment("C11").runner()
metrics = result.metrics

print("baseline accuracy:", metrics["baseline_accuracy"])
print("single A ablation accuracy:", metrics["accuracy_after_ablate_a"])
print("single B ablation accuracy:", metrics["accuracy_after_ablate_b"])
print("joint ablation accuracy:", metrics["accuracy_after_joint_ablation"])
print("margin change after A ablation:", metrics["mean_margin_change_after_ablate_a"])
