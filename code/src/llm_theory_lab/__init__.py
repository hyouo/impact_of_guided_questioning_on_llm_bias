"""LLM Theory Lab.

The package turns selected claims from the theory repository into explicit,
reproducible experiments. Toy experiments are exact or causally transparent;
model-backed experiments are observational or interventional studies on open
models and must not be overgeneralized.
"""

from .registry import EXPERIMENTS, get_experiment, list_experiments, run_toy_suite
from .result import CheckResult, ExperimentResult, write_report

__all__ = [
    "CheckResult",
    "EXPERIMENTS",
    "ExperimentResult",
    "get_experiment",
    "list_experiments",
    "run_toy_suite",
    "write_report",
]

__version__ = "0.1.0"
