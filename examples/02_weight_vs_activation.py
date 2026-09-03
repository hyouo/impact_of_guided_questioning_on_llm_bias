"""Compare weight magnitude with input-conditioned contribution."""

from __future__ import annotations

import numpy as np

weights = np.array([100.0, 3.0, 0.5])
activations = np.array([0.0, 2.0, 20.0])
contributions = weights * activations

print("weights:       ", weights)
print("activations:   ", activations)
print("contributions: ", contributions)
print("rank by |weight|:      ", np.argsort(-np.abs(weights)))
print("rank by |contribution|:", np.argsort(-np.abs(contributions)))
