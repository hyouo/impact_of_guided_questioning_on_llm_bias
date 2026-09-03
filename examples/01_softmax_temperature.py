"""Inspect the exact softmax log-odds identity used in C02."""

from __future__ import annotations

import math

import numpy as np

from llm_theory_lab.math_utils import log_odds, softmax

logits = np.array([0.2, -0.1, 1.4], dtype=np.float64)
for temperature in (0.5, 1.0, 2.0):
    probabilities = softmax(logits, temperature)
    observed = math.log(probabilities[2] / probabilities[0])
    expected = log_odds(logits, 2, 0, temperature)
    print(f"T={temperature}: probabilities={probabilities.round(4)}")
    print(f"  observed log-odds={observed:.6f}, analytic={expected:.6f}")
