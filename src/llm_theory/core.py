"""Small numerical models illustrating conditional computation.

These functions isolate a few mathematical claims used in the documentation:

* weights can stay fixed while inputs produce different activations;
* a connection's current contribution depends on weight times source activity;
* relative logit changes alter token odds exponentially;
* selected tokens can feed back into state and create path dependence.

Nothing here is a mechanistic model of a real frontier LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]


def _as_float_array(value: ArrayLike, *, ndim: int | None = None) -> FloatArray:
    array = np.asarray(value, dtype=np.float64)
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"expected {ndim} dimensions, received shape {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError("arrays must contain only finite values")
    return array


def softmax(logits: ArrayLike, temperature: float = 1.0) -> FloatArray:
    """Compute a numerically stable softmax over the final axis."""

    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be a positive finite number")
    values = _as_float_array(logits)
    shifted = values / temperature
    shifted = shifted - np.max(shifted, axis=-1, keepdims=True)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values, axis=-1, keepdims=True)


def log_odds_from_logits(
    logits: ArrayLike,
    token_i: int,
    token_j: int,
    temperature: float = 1.0,
) -> float:
    """Return log(p_i / p_j), equal to (z_i - z_j) / temperature."""

    values = _as_float_array(logits, ndim=1)
    if not 0 <= token_i < values.size or not 0 <= token_j < values.size:
        raise IndexError("token index is outside the logit vector")
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be a positive finite number")
    return float((values[token_i] - values[token_j]) / temperature)


def connection_contributions(weights: ArrayLike, source_activations: ArrayLike) -> FloatArray:
    """Return direct per-connection contributions W[i, j] * x[j]."""

    matrix = _as_float_array(weights, ndim=2)
    activations = _as_float_array(source_activations, ndim=1)
    if matrix.shape[1] != activations.size:
        raise ValueError(
            "weight source dimension and activation dimension do not match: "
            f"{matrix.shape[1]} != {activations.size}"
        )
    return matrix * activations[np.newaxis, :]


def weight_effectiveness_proxy(weight: float, source_activations: ArrayLike) -> float:
    """Return a transparent toy proxy for distributional effectiveness.

    The metric is E[(w*a)^2] over a supplied activation distribution. It is
    not the exact metric used in the 2026 Transformer Circuits paper; it only
    demonstrates why magnitude is insufficient when a feature rarely fires.
    """

    if not np.isfinite(weight):
        raise ValueError("weight must be finite")
    activations = _as_float_array(source_activations)
    if activations.size == 0:
        raise ValueError("source_activations must not be empty")
    return float(np.mean(np.square(weight * activations)))


@dataclass(frozen=True)
class ToyStep:
    """One autoregressive step recorded before token feedback is applied."""

    state: FloatArray
    features: FloatArray
    logits: FloatArray
    probabilities: FloatArray
    token_index: int
    token: str


@dataclass(frozen=True)
class FixedWeightToyModel:
    """A tiny fixed-weight conditional-computation and feedback model.

    ``state @ feature_map`` forms gated features. Features are mapped to token
    logits by ``output_map``. The selected token then adds a fixed feedback
    vector to the state, making future activations path-dependent.
    """

    feature_map: FloatArray
    output_map: FloatArray
    token_feedback: FloatArray
    token_labels: tuple[str, ...]
    feature_bias: FloatArray

    def __post_init__(self) -> None:
        feature_map = _as_float_array(self.feature_map, ndim=2).copy()
        output_map = _as_float_array(self.output_map, ndim=2).copy()
        token_feedback = _as_float_array(self.token_feedback, ndim=2).copy()
        feature_bias = _as_float_array(self.feature_bias, ndim=1).copy()
        labels = tuple(self.token_labels)

        input_dim, feature_dim = feature_map.shape
        if output_map.shape[0] != feature_dim:
            raise ValueError("feature_map and output_map feature dimensions differ")
        vocab_size = output_map.shape[1]
        if token_feedback.shape != (vocab_size, input_dim):
            raise ValueError(
                "token_feedback must have shape "
                f"({vocab_size}, {input_dim}), got {token_feedback.shape}"
            )
        if len(labels) != vocab_size:
            raise ValueError("token_labels length must equal vocabulary size")
        if feature_bias.shape != (feature_dim,):
            raise ValueError("feature_bias length must equal feature dimension")
        if len(set(labels)) != len(labels):
            raise ValueError("token labels must be unique")

        for array in (feature_map, output_map, token_feedback, feature_bias):
            array.setflags(write=False)
        object.__setattr__(self, "feature_map", feature_map)
        object.__setattr__(self, "output_map", output_map)
        object.__setattr__(self, "token_feedback", token_feedback)
        object.__setattr__(self, "feature_bias", feature_bias)
        object.__setattr__(self, "token_labels", labels)

    @property
    def input_dim(self) -> int:
        return int(self.feature_map.shape[0])

    @property
    def feature_dim(self) -> int:
        return int(self.feature_map.shape[1])

    @property
    def vocab_size(self) -> int:
        return int(self.output_map.shape[1])

    def encode(self, state: ArrayLike) -> FloatArray:
        vector = _as_float_array(state, ndim=1)
        if vector.shape != (self.input_dim,):
            raise ValueError(f"state must have shape ({self.input_dim},)")
        return np.maximum(0.0, vector @ self.feature_map + self.feature_bias)

    def logits(self, state: ArrayLike) -> FloatArray:
        return self.encode(state) @ self.output_map

    def probabilities(self, state: ArrayLike, temperature: float = 1.0) -> FloatArray:
        return softmax(self.logits(state), temperature=temperature)

    def token_index(self, token: int | str) -> int:
        if isinstance(token, str):
            try:
                return self.token_labels.index(token)
            except ValueError as exc:
                raise ValueError(f"unknown token label: {token!r}") from exc
        index = int(token)
        if not 0 <= index < self.vocab_size:
            raise IndexError("token index outside vocabulary")
        return index

    def step(
        self,
        state: ArrayLike,
        *,
        forced_token: int | str | None = None,
        temperature: float = 1.0,
    ) -> tuple[ToyStep, FloatArray]:
        """Run one deterministic step and return the record and next state."""

        vector = _as_float_array(state, ndim=1)
        features = self.encode(vector)
        logits = features @ self.output_map
        probabilities = softmax(logits, temperature=temperature)
        index = int(np.argmax(probabilities)) if forced_token is None else self.token_index(forced_token)
        record = ToyStep(
            state=vector.copy(),
            features=features.copy(),
            logits=logits.copy(),
            probabilities=probabilities.copy(),
            token_index=index,
            token=self.token_labels[index],
        )
        next_state = vector + self.token_feedback[index]
        return record, next_state

    def generate(
        self,
        initial_state: ArrayLike,
        steps: int,
        *,
        forced_tokens: Sequence[int | str] | None = None,
        temperature: float = 1.0,
    ) -> list[ToyStep]:
        """Generate an argmax trajectory with optional prefix interventions."""

        if steps < 0:
            raise ValueError("steps must be non-negative")
        prefix: Sequence[int | str] = forced_tokens or ()
        state = _as_float_array(initial_state, ndim=1).copy()
        trajectory: list[ToyStep] = []
        for position in range(steps):
            forced = prefix[position] if position < len(prefix) else None
            record, state = self.step(state, forced_token=forced, temperature=temperature)
            trajectory.append(record)
        return trajectory


def make_demo_model() -> FixedWeightToyModel:
    """Return a documented three-token model used by scripts and tests."""

    # State axes: task evidence, safety evidence, uncertainty.
    # Feature axes: answer, refusal, clarification, continuation/format.
    feature_map = np.array(
        [
            [1.20, 0.00, 0.10, 0.65],
            [0.00, 1.30, 0.20, -0.15],
            [0.05, 0.10, 1.20, 0.00],
        ],
        dtype=np.float64,
    )
    feature_bias = np.array([-0.10, -0.10, -0.05, 0.00], dtype=np.float64)

    # Columns: ANSWER, REFUSE, CLARIFY.
    output_map = np.array(
        [
            [2.00, -0.70, 0.10],
            [-0.80, 2.10, 0.10],
            [-0.20, -0.10, 1.80],
            [0.85, 0.05, 0.15],
        ],
        dtype=np.float64,
    )

    # Selecting a token changes the next state while all weights stay fixed.
    token_feedback = np.array(
        [
            [0.35, -0.05, -0.05],
            [-0.15, 0.35, -0.02],
            [-0.05, -0.05, 0.28],
        ],
        dtype=np.float64,
    )

    return FixedWeightToyModel(
        feature_map=feature_map,
        output_map=output_map,
        token_feedback=token_feedback,
        token_labels=("ANSWER", "REFUSE", "CLARIFY"),
        feature_bias=feature_bias,
    )
