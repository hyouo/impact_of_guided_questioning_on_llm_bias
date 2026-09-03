"""Run C05 and inspect two trajectories that differ only at the first token."""

from __future__ import annotations

from llm_theory_lab.registry import get_experiment

result = get_experiment("C05").runner()
metrics = result.metrics

print("forced A trajectory:", metrics["trajectory_forced_A"])
print("forced B trajectory:", metrics["trajectory_forced_B"])
print("final state distance:", metrics["final_state_distance"])
