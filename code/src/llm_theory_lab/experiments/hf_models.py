"""Optional experiments on open causal language models via Hugging Face.

These experiments download model weights and are intentionally excluded from
continuous integration. They produce observational or local interventional
evidence about the selected model version; they are not universal LLM tests.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import numpy as np

from ..math_utils import cosine_similarity, js_divergence
from ..repro import runtime_metadata, set_global_seed
from ..result import ExperimentResult


def _require_dependencies() -> tuple[Any, Any, Any]:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "model experiments require: pip install -e '.[models]'"
        ) from exc
    return torch, AutoModelForCausalLM, AutoTokenizer


def _load(model_name: str, device: str) -> tuple[Any, Any, Any]:
    torch, auto_model, auto_tokenizer = _require_dependencies()
    tokenizer = auto_tokenizer.from_pretrained(model_name)
    model = auto_model.from_pretrained(model_name)
    model.eval()
    model.to(device)
    return torch, tokenizer, model


def _probabilities(torch: Any, logits: Any) -> np.ndarray:
    return torch.softmax(logits.float(), dim=-1).detach().cpu().numpy().astype(np.float64)


def _top_tokens(torch: Any, tokenizer: Any, logits: Any, top_k: int) -> list[dict[str, Any]]:
    probabilities = torch.softmax(logits.float(), dim=-1)
    values, indices = torch.topk(probabilities, k=min(top_k, probabilities.shape[-1]))
    return [
        {
            "token_id": int(index),
            "token": tokenizer.decode([int(index)]),
            "probability": float(value),
        }
        for value, index in zip(values.detach().cpu(), indices.detach().cpu(), strict=True)
    ]


def run_tokenization_sensitivity(
    *,
    model_name: str = "openai-community/gpt2",
    prompt_a: str = "A careful answer begins with",
    prompt_b: str = "A careful answer begins with\n",
    device: str = "cpu",
    top_k: int = 10,
    seed: int = 0,
) -> ExperimentResult:
    """Compare tokenization, hidden states, attention, and next-token output."""

    set_global_seed(seed)
    torch, tokenizer, model = _load(model_name, device)

    encoded_a = tokenizer(prompt_a, return_tensors="pt").to(device)
    encoded_b = tokenizer(prompt_b, return_tensors="pt").to(device)
    with torch.no_grad():
        output_a = model(
            **encoded_a,
            output_hidden_states=True,
            output_attentions=True,
            use_cache=False,
        )
        output_b = model(
            **encoded_b,
            output_hidden_states=True,
            output_attentions=True,
            use_cache=False,
        )

    final_logits_a = output_a.logits[0, -1]
    final_logits_b = output_b.logits[0, -1]
    probs_a = _probabilities(torch, final_logits_a)
    probs_b = _probabilities(torch, final_logits_b)

    layer_cosines = [
        cosine_similarity(
            hidden_a[0, -1].detach().cpu().numpy(),
            hidden_b[0, -1].detach().cpu().numpy(),
        )
        for hidden_a, hidden_b in zip(output_a.hidden_states, output_b.hidden_states, strict=True)
    ]

    attention_last_query_l1: list[float] = []
    for attention_a, attention_b in zip(output_a.attentions or (), output_b.attentions or (), strict=True):
        # Different sequence lengths make a direct full-vector comparison invalid.
        shared = min(attention_a.shape[-1], attention_b.shape[-1])
        a = attention_a[0, :, -1, -shared:].detach().cpu().numpy()
        b = attention_b[0, :, -1, -shared:].detach().cpu().numpy()
        attention_last_query_l1.append(float(np.mean(np.sum(np.abs(a - b), axis=-1))))

    return ExperimentResult(
        experiment_id="M01",
        title="开放模型中的 tokenization 与格式敏感性",
        theory_claim="表面格式可改变 token 序列、层间表示、注意力路由和下一 token 分布。",
        evidence_level="L2-open-model-observation",
        status="observational",
        metrics={
            "model_name": model_name,
            "prompt_a": prompt_a,
            "prompt_b": prompt_b,
            "token_ids_a": encoded_a["input_ids"][0].detach().cpu().tolist(),
            "token_ids_b": encoded_b["input_ids"][0].detach().cpu().tolist(),
            "tokens_a": tokenizer.convert_ids_to_tokens(encoded_a["input_ids"][0]),
            "tokens_b": tokenizer.convert_ids_to_tokens(encoded_b["input_ids"][0]),
            "next_token_js_divergence_nats": js_divergence(probs_a, probs_b),
            "final_position_hidden_cosine_by_layer": layer_cosines,
            "last_query_attention_l1_by_layer": attention_last_query_l1,
            "top_tokens_a": _top_tokens(torch, tokenizer, final_logits_a, top_k),
            "top_tokens_b": _top_tokens(torch, tokenizer, final_logits_b, top_k),
        },
        caveats=(
            "这个实验同时改变了 tokenization、序列长度和最后位置，不应把差异归因于单一语义因素。",
            "attention 权重变化不是因果解释；需进一步做 patching 或受控对照。",
            "结果只对记录的模型、权重版本、tokenizer、依赖和硬件环境负责。",
        ),
        metadata={**runtime_metadata(), "seed": seed, "device": device},
    )


def run_prefix_feedback(
    *,
    model_name: str = "openai-community/gpt2",
    prompt: str = "The response begins:",
    prefix_a: str = " Yes",
    prefix_b: str = " No",
    device: str = "cpu",
    top_k: int = 10,
    seed: int = 0,
) -> ExperimentResult:
    """Append two alternative first-token prefixes and compare the next step."""

    set_global_seed(seed)
    torch, tokenizer, model = _load(model_name, device)
    text_a = prompt + prefix_a
    text_b = prompt + prefix_b
    encoded_a = tokenizer(text_a, return_tensors="pt").to(device)
    encoded_b = tokenizer(text_b, return_tensors="pt").to(device)

    with torch.no_grad():
        logits_a = model(**encoded_a, use_cache=False).logits[0, -1]
        logits_b = model(**encoded_b, use_cache=False).logits[0, -1]

    probs_a = _probabilities(torch, logits_a)
    probs_b = _probabilities(torch, logits_b)
    return ExperimentResult(
        experiment_id="M02",
        title="开放模型中的前缀反馈与轨迹分叉",
        theory_claim="替代首 token 一旦进入上下文，会改变下一步隐藏状态和条件分布。",
        evidence_level="L2-open-model-counterfactual-context",
        status="observational",
        metrics={
            "model_name": model_name,
            "base_prompt": prompt,
            "prefix_a": prefix_a,
            "prefix_b": prefix_b,
            "token_ids_a": encoded_a["input_ids"][0].detach().cpu().tolist(),
            "token_ids_b": encoded_b["input_ids"][0].detach().cpu().tolist(),
            "next_step_js_divergence_nats": js_divergence(probs_a, probs_b),
            "top_tokens_after_a": _top_tokens(torch, tokenizer, logits_a, top_k),
            "top_tokens_after_b": _top_tokens(torch, tokenizer, logits_b, top_k),
        },
        caveats=(
            "两个前缀可能包含不同数量的 tokenizer token；报告会保留完整 token IDs。",
            "这是条件上下文反事实，不代表自然采样时两个前缀具有相同初始概率。",
            "一次分布差异不能自动解释长期生成，长期效应需多步、重复种子和语义评分。",
        ),
        metadata={**runtime_metadata(), "seed": seed, "device": device},
    )


def _gpt2_blocks(model: Any) -> Any:
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        return model.transformer.h
    raise NotImplementedError(
        "activation patch scan currently supports GPT-2-style models with model.transformer.h"
    )


@contextmanager
def _patch_block_output(block: Any, clean_vector: Any, position: int) -> Iterator[None]:
    def hook(_module: Any, _inputs: Any, output: Any) -> Any:
        if isinstance(output, tuple):
            hidden = output[0].clone()
            hidden[:, position, :] = clean_vector
            return (hidden, *output[1:])
        hidden = output.clone()
        hidden[:, position, :] = clean_vector
        return hidden

    handle = block.register_forward_hook(hook)
    try:
        yield
    finally:
        handle.remove()


def run_activation_patch_scan(
    *,
    model_name: str = "openai-community/gpt2",
    clean_prompt: str = "The capital of France is",
    corrupted_prompt: str = "The capital of Italy is",
    target_token: str = " Paris",
    device: str = "cpu",
    seed: int = 0,
) -> ExperimentResult:
    """Patch the final-position residual output of each GPT-2 block."""

    set_global_seed(seed)
    torch, tokenizer, model = _load(model_name, device)
    clean = tokenizer(clean_prompt, return_tensors="pt").to(device)
    corrupted = tokenizer(corrupted_prompt, return_tensors="pt").to(device)
    if clean["input_ids"].shape != corrupted["input_ids"].shape:
        raise ValueError("clean and corrupted prompts must tokenize to the same shape")

    target_ids = tokenizer.encode(target_token, add_special_tokens=False)
    if len(target_ids) != 1:
        raise ValueError("target_token must tokenize to exactly one token")
    target_id = target_ids[0]

    with torch.no_grad():
        clean_output = model(
            **clean,
            output_hidden_states=True,
            use_cache=False,
        )
        corrupted_output = model(
            **corrupted,
            output_hidden_states=True,
            use_cache=False,
        )

    clean_logit = float(clean_output.logits[0, -1, target_id].detach().cpu())
    corrupted_logit = float(corrupted_output.logits[0, -1, target_id].detach().cpu())
    blocks = _gpt2_blocks(model)
    layer_records: list[dict[str, float | int]] = []

    for layer_index, block in enumerate(blocks):
        clean_vector = clean_output.hidden_states[layer_index + 1][:, -1, :]
        with _patch_block_output(block, clean_vector, position=-1):
            with torch.no_grad():
                patched_output = model(**corrupted, use_cache=False)
        patched_logit = float(patched_output.logits[0, -1, target_id].detach().cpu())
        layer_records.append(
            {
                "layer": layer_index,
                "patched_target_logit": patched_logit,
                "improvement_over_corrupted": patched_logit - corrupted_logit,
            }
        )

    best = max(layer_records, key=lambda record: float(record["improvement_over_corrupted"]))
    return ExperimentResult(
        experiment_id="M03",
        title="开放模型中的逐层 activation patching",
        theory_claim="若某层最终位置状态携带目标信息，把 clean 状态 patch 入 corrupted 运行应改变目标 token logit。",
        evidence_level="L3-open-model-local-intervention",
        status="observational",
        metrics={
            "model_name": model_name,
            "clean_prompt": clean_prompt,
            "corrupted_prompt": corrupted_prompt,
            "target_token": target_token,
            "target_token_id": target_id,
            "clean_target_logit": clean_logit,
            "corrupted_target_logit": corrupted_logit,
            "layer_patch_records": layer_records,
            "best_layer": best,
        },
        caveats=(
            "patch 整个最终位置残差向量会同时替换大量变量，定位粒度较粗。",
            "正向变化说明被 patch 状态足以传递部分效应，不证明该层或向量是唯一机制。",
            "GPT-2 的事实回忆能力和 prompt 选择会影响结果；应加入多组模板、目标和负对照。",
        ),
        metadata={**runtime_metadata(), "seed": seed, "device": device},
    )
