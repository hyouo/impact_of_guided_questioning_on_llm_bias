"""Reproducibility helpers and runtime metadata."""

from __future__ import annotations

import importlib.metadata
import os
import platform
import random
import sys
from typing import Any

import numpy as np


def set_global_seed(seed: int, *, deterministic_torch: bool = False) -> None:
    """Seed Python, NumPy, and PyTorch when available.

    This reduces avoidable variance. It does not guarantee bitwise identity
    across library versions, devices, drivers, or hardware platforms.
    """

    if seed < 0:
        raise ValueError("seed must be non-negative")
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch
    except ImportError:
        return

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic_torch:
        torch.use_deterministic_algorithms(True, warn_only=True)


def _version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def runtime_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
    }
    for package in ("torch", "transformers", "safetensors"):
        version = _version(package)
        if version is not None:
            metadata[package] = version
    return metadata
