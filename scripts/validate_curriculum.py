#!/usr/bin/env python3
"""Validate the course, labs, experiment registry, and packaged curriculum."""

from __future__ import annotations

import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llm_theory_lab.learning import load_curriculum  # noqa: E402
from llm_theory_lab.registry import EXPERIMENTS  # noqa: E402

CHAPTER_HEADINGS = (
    "## 学完你应该能",
    "## 核心模型",
    "## 动手验证",
    "## 常见误区",
    "## 自测",
    "## 来源",
)
LAB_HEADINGS = (
    "## 问题",
    "## 运行",
    "## 运行前预测",
    "## 读结果",
    "## 改动实验",
    "## 结论边界",
    "## 延伸阅读",
)


def fail(message: str) -> None:
    raise ValueError(message)


def require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{name} must be an object")
    return value


def require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{name} must be a list")
    return value


def validate() -> None:
    curriculum = load_curriculum()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = str(pyproject["project"]["version"])
    if curriculum.get("curriculum_version") != project_version:
        fail("curriculum_version must match project.version")

    modules = require_list(curriculum.get("modules"), "modules")
    expected_module_ids = [f"M{index:02d}" for index in range(1, 9)]
    module_ids = [require_mapping(item, "module").get("id") for item in modules]
    if module_ids != expected_module_ids:
        fail(f"module IDs must be sequential: {expected_module_ids}")

    course_index = (ROOT / "docs/course/index.md").read_text(encoding="utf-8")
    seen_modules: set[str] = set()
    assigned_labs: list[str] = []
    for raw_module in modules:
        module = require_mapping(raw_module, "module")
        module_id = str(module["id"])
        prerequisites = require_list(module.get("prerequisites"), f"{module_id}.prerequisites")
        unknown = set(prerequisites) - seen_modules
        if unknown:
            fail(f"{module_id} has missing or forward prerequisites: {sorted(unknown)}")

        hours = module.get("estimated_hours")
        if not isinstance(hours, (int, float)) or hours <= 0:
            fail(f"{module_id}.estimated_hours must be positive")

        outcomes = require_list(module.get("outcomes"), f"{module_id}.outcomes")
        if len(outcomes) < 2 or not all(str(item).strip() for item in outcomes):
            fail(f"{module_id} must define at least two learning outcomes")
        if not str(module.get("deliverable", "")).strip():
            fail(f"{module_id} must define a deliverable")

        chapter = ROOT / str(module["chapter"])
        if not chapter.is_file():
            fail(f"missing chapter for {module_id}: {chapter.relative_to(ROOT)}")
        text = chapter.read_text(encoding="utf-8")
        missing_headings = [heading for heading in CHAPTER_HEADINGS if heading not in text]
        if missing_headings:
            fail(f"{chapter.relative_to(ROOT)} missing headings: {missing_headings}")
        if chapter.name not in course_index:
            fail(f"course index does not reference {chapter.name}")

        labs = require_list(module.get("labs"), f"{module_id}.labs")
        assigned_labs.extend(str(item) for item in labs)
        seen_modules.add(module_id)

    experiment_ids = [spec.experiment_id for spec in EXPERIMENTS]
    guides = require_mapping(curriculum.get("experiments"), "experiments")
    if set(guides) != set(experiment_ids):
        fail("curriculum experiment guides must exactly match the registry")

    counts = Counter(assigned_labs)
    if set(counts) != set(experiment_ids):
        fail("course modules must cover every registered experiment")
    duplicated = sorted(item for item, count in counts.items() if count != 1)
    if duplicated:
        fail(f"experiments must be assigned to exactly one module: {duplicated}")

    lab_index = (ROOT / "docs/labs/index.md").read_text(encoding="utf-8")
    for experiment_id in experiment_ids:
        guide = require_mapping(guides[experiment_id], experiment_id)
        required_fields = {
            "guide",
            "readings",
            "why_it_matters",
            "inspection_points",
            "allowed_conclusion",
            "forbidden_inference",
        }
        missing = required_fields - set(guide)
        if missing:
            fail(f"{experiment_id} guide missing fields: {sorted(missing)}")

        guide_path = ROOT / str(guide["guide"])
        if not guide_path.is_file():
            fail(f"missing lab guide: {guide_path.relative_to(ROOT)}")
        guide_text = guide_path.read_text(encoding="utf-8")
        missing_headings = [heading for heading in LAB_HEADINGS if heading not in guide_text]
        if missing_headings:
            fail(f"{guide_path.relative_to(ROOT)} missing headings: {missing_headings}")
        if guide_path.name not in lab_index:
            fail(f"lab index does not reference {guide_path.name}")

        readings = require_list(guide["readings"], f"{experiment_id}.readings")
        if not readings:
            fail(f"{experiment_id} must have at least one reading")
        for reading in readings:
            reading_path = ROOT / str(reading)
            if not reading_path.is_file():
                fail(f"{experiment_id} reading does not exist: {reading}")

        points = require_list(guide["inspection_points"], f"{experiment_id}.inspection_points")
        if len(points) < 2:
            fail(f"{experiment_id} must define at least two inspection points")

    print(
        "curriculum valid: "
        f"{len(modules)} modules, {len(experiment_ids)} experiments, "
        "complete chapter/lab coverage"
    )


def main() -> int:
    try:
        validate()
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"curriculum validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
