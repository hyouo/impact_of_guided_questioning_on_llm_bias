"""Strict, auditable loading policy for optional open-model experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelLoadRequest:
    """Parameters that materially affect an open-model run."""

    model_name: str
    device: str = "cpu"
    revision: str | None = None
    allow_download: bool = False


@dataclass(frozen=True)
class LoadedCausalLM:
    torch: Any
    tokenizer: Any
    model: Any
    identity: dict[str, Any]


def require_model_dependencies() -> tuple[Any, Any, Any]:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "open-model experiments require: pip install -e '.[models]'"
        ) from exc
    return torch, AutoModelForCausalLM, AutoTokenizer


def _resolved_revision(model: Any, tokenizer: Any, requested: str | None) -> str | None:
    candidates = (
        getattr(getattr(model, "config", None), "_commit_hash", None),
        getattr(tokenizer, "_commit_hash", None),
        requested,
    )
    return next((str(value) for value in candidates if value), None)


def load_causal_lm(request: ModelLoadRequest) -> LoadedCausalLM:
    """Load a causal LM without executing repository-provided remote code.

    Downloads are disabled by default. A user must opt in explicitly, and the
    resolved Hub commit is recorded when Transformers exposes it.
    """

    if not request.model_name.strip():
        raise ValueError("model_name must not be empty")
    if not request.device.strip():
        raise ValueError("device must not be empty")

    torch, auto_model, auto_tokenizer = require_model_dependencies()
    common: dict[str, Any] = {
        "revision": request.revision,
        "local_files_only": not request.allow_download,
        "trust_remote_code": False,
    }
    tokenizer = auto_tokenizer.from_pretrained(request.model_name, **common)
    model = auto_model.from_pretrained(request.model_name, **common)
    model.eval()
    model.to(request.device)

    config = getattr(model, "config", None)
    identity = {
        "model_name": request.model_name,
        "requested_revision": request.revision,
        "resolved_revision": _resolved_revision(model, tokenizer, request.revision),
        "allow_download": request.allow_download,
        "local_files_only": not request.allow_download,
        "trust_remote_code": False,
        "device": request.device,
        "model_class": type(model).__name__,
        "tokenizer_class": type(tokenizer).__name__,
        "architectures": list(getattr(config, "architectures", None) or ()),
        "vocab_size": getattr(config, "vocab_size", None),
        "hidden_size": getattr(config, "hidden_size", None),
        "num_hidden_layers": getattr(config, "num_hidden_layers", None),
        "num_attention_heads": getattr(config, "num_attention_heads", None),
        "torch_dtype": str(getattr(config, "torch_dtype", None)),
    }
    return LoadedCausalLM(
        torch=torch,
        tokenizer=tokenizer,
        model=model,
        identity=identity,
    )
