"""Run C10 and compare coordinated with uncompensated basis changes."""

from __future__ import annotations

from llm_theory_lab.registry import get_experiment

result = get_experiment("C10").runner()
metrics = result.metrics

print("hidden coordinate shift:", metrics["mean_hidden_coordinate_shift"])
print("compensated output error:", metrics["max_output_error_after_compensated_change"])
print("uncompensated output error:", metrics["mean_output_error_without_compensation"])
print("basis condition number:", metrics["basis_condition_number"])
