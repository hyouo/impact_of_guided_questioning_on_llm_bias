"""Machine-readable curriculum access for the CLI and validation tools."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any


@lru_cache(maxsize=1)
def load_curriculum() -> dict[str, Any]:
    """Load the packaged curriculum registry.

    The registry is bundled with the distribution so that `course` and
    `explain` work after installation, not only from a source checkout.
    """

    resource = files("llm_theory_lab").joinpath("data/curriculum.json")
    data = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("curriculum root must be an object")
    if data.get("schema_version") != 1:
        raise ValueError("unsupported curriculum schema version")
    return data


def list_course_modules() -> tuple[dict[str, Any], ...]:
    modules = load_curriculum().get("modules")
    if not isinstance(modules, list):
        raise ValueError("curriculum.modules must be a list")
    return tuple(dict(module) for module in modules)


def get_course_module(module_id: str) -> dict[str, Any]:
    normalized = module_id.upper()
    for module in list_course_modules():
        if module.get("id") == normalized:
            return module
    raise KeyError(f"unknown course module: {module_id}")


def get_experiment_guide(experiment_id: str) -> dict[str, Any]:
    guides = load_curriculum().get("experiments")
    if not isinstance(guides, dict):
        raise ValueError("curriculum.experiments must be an object")
    normalized = experiment_id.upper()
    guide = guides.get(normalized)
    if not isinstance(guide, dict):
        raise KeyError(f"unknown experiment guide: {experiment_id}")
    return dict(guide)
