"""LLM Theory Lab public API.

The package turns theory claims into explicit, reproducible experiments.
Transparent experiments establish mathematical identities or structural
counterexamples; model-backed experiments remain scoped observations or local
interventions and must not be overgeneralized.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .registry import EXPERIMENTS, get_experiment, list_experiments, run_toy_suite
from .result import CheckResult, ExperimentResult, write_report

try:
    __version__ = version("llm-theory-lab")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0+unknown"

__all__ = [
    "CheckResult",
    "EXPERIMENTS",
    "ExperimentResult",
    "__version__",
    "get_experiment",
    "list_experiments",
    "run_toy_suite",
    "write_report",
]
