"""Open-model induction-head measurements with a pure NumPy scoring core."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from ..model_runtime import ModelLoadRequest, load_causal_lm
from ..repro import runtime_metadata
from ..result import ExperimentResult

_CANDIDATE_WORDS = (
    " red",
    " blue",
    " green",
    " black",
    " white",
    " small",
    " large",
    " old",
    " new",
    " slow",
    " fast",
    " warm",
    " cold",
    " north",
    " south",
    " east",
    " west",
    " one",
    " two",
    " three",
    " cat",
    " dog",
    " bird",
    " tree",
    " stone",
    " river",
    " cloud",
    " music",
    " paper",
    " glass",
)


def induction_targets(token_ids: Sequence[int]) -> list[tuple[int, int]]:
    """Return `(query_position, previous-token-successor)` pairs.

    For a sequence `A B ... A`, the later `A` is the query and the earlier
    `B` position is the induction target.
    """

    targets: list[tuple[int, int]] = []
    for query_position, token_id in enumerate(token_ids):
        previous = [
            index
            for index in range(query_position - 1)
            if token_ids[index] == token_id and index + 1 < query_position
        ]
        if previous:
            targets.append((query_position, previous[-1] + 1))
    return targets


def score_induction_attention(
    attentions: np.ndarray,
    token_ids: Sequence[int],
) -> dict[str, np.ndarray | int]:
    """Score target attention against the mean of other causal positions.

    `attentions` must have shape `[layers, heads, query, key]`.
    """

    array = np.asarray(attentions, dtype=np.float64)
    if array.ndim != 4:
        raise ValueError("attentions must have shape [layers, heads, query, key]")
    if array.shape[2] != array.shape[3]:
        raise ValueError("attention query and key lengths must match")
    if array.shape[2] != len(token_ids):
        raise ValueError("token_ids length must match the attention sequence length")

    targets = induction_targets(token_ids)
    if not targets:
        raise ValueError("token sequence contains no induction target")

    target_values: list[np.ndarray] = []
    control_values: list[np.ndarray] = []
    for query_position, target_position in targets:
        causal_slice = array[:, :, query_position, : query_position + 1]
        target = array[:, :, query_position, target_position]
        control_count = causal_slice.shape[-1] - 1
        if control_count <= 0:
            raise ValueError("induction target has no control positions")
        control = (causal_slice.sum(axis=-1) - target) / control_count
        target_values.append(target)
        control_values.append(control)

    target_mean = np.mean(np.stack(target_values), axis=0)
    control_mean = np.mean(np.stack(control_values), axis=0)
    return {
        "target_attention": target_mean,
        "control_attention": control_mean,
        "induction_score": target_mean - control_mean,
        "target_count": len(targets),
    }


def rank_induction_heads(
    score_matrix: np.ndarray,
    *,
    top_k: int = 20,
) -> list[dict[str, int | float]]:
    array = np.asarray(score_matrix, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError("score_matrix must have shape [layers, heads]")
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    ranked = np.argsort(array, axis=None)[::-1][: min(top_k, array.size)]
    rows: list[dict[str, int | float]] = []
    for flat_index in ranked:
        layer, head = np.unravel_index(int(flat_index), array.shape)
        rows.append(
            {
                "layer": int(layer),
                "head": int(head),
                "score": float(array[layer, head]),
            }
        )
    return rows


def _single_token_candidates(tokenizer: Any) -> list[tuple[str, int]]:
    special_ids = set(getattr(tokenizer, "all_special_ids", None) or ())
    candidates: list[tuple[str, int]] = []
    seen: set[int] = set()
    for text in _CANDIDATE_WORDS:
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        if len(token_ids) != 1:
            continue
        token_id = int(token_ids[0])
        if token_id in special_ids or token_id in seen:
            continue
        seen.add(token_id)
        candidates.append((text, token_id))
    if len(candidates) < 6:
        raise RuntimeError("tokenizer produced fewer than six safe single-token candidates")
    return candidates


def run_induction_head_scan(
    *,
    model_name: str = "openai-community/gpt2",
    revision: str | None = None,
    device: str = "cpu",
    samples: int = 24,
    top_k: int = 20,
    seed: int = 0,
    allow_download: bool = False,
) -> ExperimentResult:
    """Measure induction-style attention on repeated-token synthetic sequences."""

    if samples <= 0:
        raise ValueError("samples must be positive")
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if seed < 0:
        raise ValueError("seed must be non-negative")

    loaded = load_causal_lm(
        ModelLoadRequest(
            model_name=model_name,
            revision=revision,
            device=device,
            allow_download=allow_download,
        )
    )
    torch = loaded.torch
    tokenizer = loaded.tokenizer
    model = loaded.model
    candidates = _single_token_candidates(tokenizer)
    rng = np.random.default_rng(seed)

    target_total: np.ndarray | None = None
    control_total: np.ndarray | None = None
    margin_values: list[float] = []
    sample_rows: list[dict[str, Any]] = []

    for sample_index in range(samples):
        chosen_indices = rng.choice(len(candidates), size=4, replace=False)
        chosen = [candidates[int(index)] for index in chosen_indices]
        token_ids = [chosen[0][1], chosen[1][1], chosen[2][1], chosen[3][1], chosen[0][1]]
        input_ids = torch.tensor([token_ids], dtype=torch.long, device=device)
        attention_mask = torch.ones_like(input_ids)

        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True,
                use_cache=False,
            )
        if outputs.attentions is None:
            raise RuntimeError("model did not return attention tensors")

        attention_array = np.stack(
            [layer[0].detach().cpu().numpy() for layer in outputs.attentions]
        )
        scored = score_induction_attention(attention_array, token_ids)
        target = np.asarray(scored["target_attention"])
        control = np.asarray(scored["control_attention"])
        target_total = target.copy() if target_total is None else target_total + target
        control_total = control.copy() if control_total is None else control_total + control

        final_logits = outputs.logits[0, -1]
        target_logit = float(final_logits[chosen[1][1]].detach().cpu())
        distractor_ids = [chosen[2][1], chosen[3][1]]
        distractor_mean = float(final_logits[distractor_ids].detach().cpu().float().mean())
        margin_values.append(target_logit - distractor_mean)

        if sample_index < 8:
            sample_rows.append(
                {
                    "token_ids": token_ids,
                    "tokens": [tokenizer.convert_ids_to_tokens(item) for item in token_ids],
                    "target_token_id": chosen[1][1],
                    "target_token_text": chosen[1][0],
                    "target_logit_margin": margin_values[-1],
                }
            )

    if target_total is None or control_total is None:
        raise RuntimeError("no induction measurements were produced")

    target_mean = target_total / samples
    control_mean = control_total / samples
    score_matrix = target_mean - control_mean
    metadata = runtime_metadata()
    metadata.update(
        {
            "model": loaded.identity,
            "seed": seed,
            "samples": samples,
            "sequence_pattern": "[A, B, C, D, A]",
            "attention_target": "the token following the earlier occurrence of A",
            "download_policy": (
                "network downloads explicitly allowed"
                if allow_download
                else "local cache only"
            ),
        }
    )
    metrics = {
        "target_attention_by_layer_head": target_mean,
        "control_attention_by_layer_head": control_mean,
        "induction_score_by_layer_head": score_matrix,
        "top_heads": rank_induction_heads(score_matrix, top_k=top_k),
        "mean_target_logit_margin": float(np.mean(margin_values)),
        "std_target_logit_margin": float(np.std(margin_values)),
        "sample_preview": sample_rows,
    }
    return ExperimentResult(
        experiment_id="M04",
        title="开放模型 induction-head 扫描",
        theory_claim=(
            "在重复 token 的受控序列中，一些注意力头可能更偏向读取先前匹配 token "
            "之后的位置；该模式应与下一 token 行为分开记录。"
        ),
        evidence_level="L2-open-model-observation",
        status="observational",
        metrics=metrics,
        checks=(),
        caveats=(
            "Attention pattern 是候选机制证据，不是完整因果解释。",
            "最高分头可能依赖模型、tokenizer、序列模板和样本选择。",
            "该协议没有复现 Anthropic 的原始训练相变或全部 induction-head 证据。",
            "需要进一步加入头消融、路径 patching、跨模板和跨模型复现。",
        ),
        metadata=metadata,
    )
