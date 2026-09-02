"""Small, dependency-light numerical utilities used by the experiments."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def as_float_array(value: ArrayLike, *, ndim: int | None = None) -> FloatArray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected {ndim} dimensions, received {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError("array must contain only finite values")
    return array


def softmax(logits: ArrayLike, temperature: float = 1.0) -> FloatArray:
    """Numerically stable softmax for strictly positive temperature.

    Temperature zero is not a valid value in the mathematical softmax. APIs
    that expose ``temperature=0`` generally mean deterministic argmax decoding.
    """

    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be positive and finite")
    values = as_float_array(logits)
    scaled = values / temperature
    scaled = scaled - np.max(scaled, axis=-1, keepdims=True)
    exponentials = np.exp(scaled)
    return exponentials / np.sum(exponentials, axis=-1, keepdims=True)


def log_odds(logits: ArrayLike, i: int, j: int, temperature: float = 1.0) -> float:
    values = as_float_array(logits, ndim=1)
    if not (0 <= i < values.size and 0 <= j < values.size):
        raise IndexError("token index is outside the logit vector")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be positive and finite")
    return float((values[i] - values[j]) / temperature)


def cosine_similarity(left: ArrayLike, right: ArrayLike, eps: float = 1e-12) -> float:
    a = as_float_array(left, ndim=1)
    b = as_float_array(right, ndim=1)
    if a.shape != b.shape:
        raise ValueError("vectors must have the same shape")
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator <= eps:
        return 0.0
    return float(np.dot(a, b) / denominator)


def kl_divergence(p: ArrayLike, q: ArrayLike, eps: float = 1e-12) -> float:
    p_array = as_float_array(p, ndim=1)
    q_array = as_float_array(q, ndim=1)
    if p_array.shape != q_array.shape:
        raise ValueError("distributions must have the same shape")
    p_safe = np.clip(p_array, eps, 1.0)
    q_safe = np.clip(q_array, eps, 1.0)
    p_safe = p_safe / p_safe.sum()
    q_safe = q_safe / q_safe.sum()
    return float(np.sum(p_safe * np.log(p_safe / q_safe)))


def js_divergence(p: ArrayLike, q: ArrayLike, eps: float = 1e-12) -> float:
    p_array = as_float_array(p, ndim=1)
    q_array = as_float_array(q, ndim=1)
    midpoint = 0.5 * (p_array + q_array)
    return 0.5 * kl_divergence(p_array, midpoint, eps) + 0.5 * kl_divergence(q_array, midpoint, eps)


def mean_squared(values: Iterable[float]) -> float:
    array = np.asarray(tuple(values), dtype=np.float64)
    if array.size == 0:
        raise ValueError("values must not be empty")
    return float(np.mean(np.square(array)))
