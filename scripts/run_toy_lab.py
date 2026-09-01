#!/usr/bin/env python3
"""Run transparent toy demonstrations for the theory documentation."""

from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

# Allow `python scripts/run_toy_lab.py` from a fresh clone, before installation.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_theory import (
    connection_contributions,
    log_odds_from_logits,
    make_demo_model,
    softmax,
    weight_effectiveness_proxy,
)


def fmt(values: np.ndarray) -> str:
    return np.array2string(values, precision=3, suppress_small=True)


def main() -> None:
    model = make_demo_model()

    print("1) Fixed weights, input-dependent activations")
    task_heavy = np.array([1.0, 0.15, 0.10])
    safety_heavy = np.array([0.55, 0.95, 0.10])
    for name, state in (("task-heavy", task_heavy), ("safety-heavy", safety_heavy)):
        features = model.encode(state)
        logits = model.logits(state)
        probs = model.probabilities(state)
        print(f"  {name:12s} state={fmt(state)}")
        print(f"  {'':12s} features={fmt(features)}")
        print(f"  {'':12s} logits={fmt(logits)} probs={fmt(probs)}")
        print(f"  {'':12s} selected={model.token_labels[int(np.argmax(probs))]}")

    print("\n2) Weight magnitude is not current contribution")
    weights = np.array([[8.0, 1.2], [-2.0, 0.8]])
    activations = np.array([0.0, 1.5])
    print(f"  weights=\n{weights}")
    print(f"  source activations={fmt(activations)}")
    print(f"  W * activation per connection=\n{connection_contributions(weights, activations)}")
    print("  The largest raw weight contributes zero because its source is inactive.")

    print("\n3) Small relative-logit shifts change odds exponentially")
    base_logits = np.array([0.0, 0.0])
    shifted_logits = np.array([1.0, 0.0])
    base_odds = math.exp(log_odds_from_logits(base_logits, 0, 1))
    shifted_odds = math.exp(log_odds_from_logits(shifted_logits, 0, 1))
    print(f"  base probabilities={fmt(softmax(base_logits))}, odds={base_odds:.3f}")
    print(f"  +1 relative logit probabilities={fmt(softmax(shifted_logits))}, odds={shifted_odds:.3f}")

    print("\n4) Token feedback creates trajectory dependence")
    ambiguous = np.array([0.63, 0.60, 0.08])
    answer_path = model.generate(ambiguous, 5, forced_tokens=("ANSWER",))
    refusal_path = model.generate(ambiguous, 5, forced_tokens=("REFUSE",))
    print("  forced ANSWER prefix:", " -> ".join(step.token for step in answer_path))
    print("  forced REFUSE prefix:", " -> ".join(step.token for step in refusal_path))
    print("  Model weights are identical; only the selected first token differs.")

    print("\n5) Distributional effectiveness can reverse magnitude rankings")
    large_but_rare = weight_effectiveness_proxy(10.0, [0.0, 0.0, 0.001, 0.0])
    smaller_but_active = weight_effectiveness_proxy(1.0, [1.0, 0.8, 1.2, 1.0])
    print(f"  |w|=10, almost inactive feature: effectiveness proxy={large_but_rare:.6f}")
    print(f"  |w|=1, routinely active feature: effectiveness proxy={smaller_but_active:.6f}")


if __name__ == "__main__":
    main()
