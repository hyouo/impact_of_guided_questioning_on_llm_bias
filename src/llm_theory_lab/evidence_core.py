"""Deterministic evidence serialization, hashes, and runtime identity."""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import os
import subprocess
from collections.abc import Mapping
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .registry import ExperimentSpec
from .result import ALLOWED_RESULT_STATUSES, ExperimentResult

LEDGER_SCHEMA_VERSION = "1.0.0"


BUNDLE_SCHEMA_VERSION = "1.0.0"


ALLOWED_STATUSES = set(ALLOWED_RESULT_STATUSES)


_VOLATILE_METADATA_KEYS = {
    "python",
    "platform",
    "numpy",
    "torch",
    "transformers",
    "safetensors",
    "git_revision",
}


class EvidenceValidationError(ValueError):
    """Raised when an evidence ledger or reproduction bundle is inconsistent."""


def _utc_now() -> str:
    epoch = os.getenv("SOURCE_DATE_EPOCH")
    if epoch:
        return datetime.fromtimestamp(int(epoch), timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def _package_version() -> str:
    try:
        return version("llm-theory-lab")
    except PackageNotFoundError:  # pragma: no cover - source tree without installation
        return "0+unknown"


def _normalized_float(value: float) -> float:
    if not math.isfinite(value):
        raise EvidenceValidationError("evidence payloads cannot contain NaN or infinity")
    if value == 0.0:
        return 0.0
    return float(f"{value:.12g}")


def canonicalize(value: Any) -> Any:
    """Convert a JSON-like value to a deterministic, finite representation."""

    if isinstance(value, Mapping):
        return {str(key): canonicalize(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [canonicalize(item) for item in value]
    if isinstance(value, float):
        return _normalized_float(value)
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if hasattr(value, "tolist"):
        return canonicalize(value.tolist())
    if hasattr(value, "item"):
        return canonicalize(value.item())
    raise EvidenceValidationError(f"unsupported evidence value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonicalize(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_json_bytes(value)).hexdigest()}"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def detect_code_revision(root: str | Path | None = None) -> str:
    """Return the exact Git revision when available, otherwise an explicit sentinel."""

    for name in ("LLM_THEORY_LAB_GIT_REVISION", "GITHUB_SHA"):
        value = os.getenv(name, "").strip()
        if value:
            return value

    cwd = Path(root) if root is not None else Path.cwd()
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return "unknown"
    revision = completed.stdout.strip()
    return revision or "unknown"


def runner_descriptor(spec: ExperimentSpec) -> dict[str, Any]:
    signature = inspect.signature(spec.runner)
    parameters: dict[str, Any] = {}
    for name, parameter in signature.parameters.items():
        if parameter.default is inspect.Parameter.empty:
            parameters[name] = {"required": True}
        else:
            parameters[name] = canonicalize(parameter.default)
    return {
        "kind": "synthetic-builtin",
        "runner": f"{spec.runner.__module__}:{spec.runner.__qualname__}",
        "parameters": parameters,
        "generator_revision": "1",
    }


def canonical_result(result: ExperimentResult) -> dict[str, Any]:
    """Strip timestamps and runtime-only metadata before drift comparison."""

    payload = result.to_dict()
    payload.pop("created_at", None)
    metadata = dict(payload.get("metadata", {}))
    for key in _VOLATILE_METADATA_KEYS:
        metadata.pop(key, None)
    payload["metadata"] = metadata
    return canonicalize(payload)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceValidationError(message)


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    digest = value.removeprefix("sha256:")
    return len(digest) == 64 and all(character in "0123456789abcdef" for character in digest)
