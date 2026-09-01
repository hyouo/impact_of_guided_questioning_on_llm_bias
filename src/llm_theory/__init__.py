"""Minimal, dependency-light demonstrations for the LLM theory repository.

The package is intentionally a toy laboratory. It does not claim to recover
or simulate the mechanisms of any production language model.
"""

from .core import (
    FixedWeightToyModel,
    ToyStep,
    connection_contributions,
    log_odds_from_logits,
    make_demo_model,
    softmax,
    weight_effectiveness_proxy,
)

__all__ = [
    "FixedWeightToyModel",
    "ToyStep",
    "connection_contributions",
    "log_odds_from_logits",
    "make_demo_model",
    "softmax",
    "weight_effectiveness_proxy",
]
