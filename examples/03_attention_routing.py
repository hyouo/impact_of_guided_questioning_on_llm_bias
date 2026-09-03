"""Run C04 and print its QK and OV observations."""

from __future__ import annotations

from llm_theory_lab.registry import get_experiment

result = get_experiment("C04").runner()
metrics = result.metrics

print("baseline scores:   ", metrics["baseline_scores"])
print("perturbed scores:  ", metrics["perturbed_scores"])
print("baseline attention:", metrics["baseline_attention"])
print("perturbed attention:", metrics["perturbed_attention"])
print("output L2 shift:   ", metrics["output_l2_shift"])
