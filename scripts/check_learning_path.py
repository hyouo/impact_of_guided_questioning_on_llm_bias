#!/usr/bin/env python3
"""Validate the learning contract across course, labs, exercises, and code."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llm_theory_lab.registry import EXPERIMENTS  # noqa: E402

COURSE_FILES = (
    "docs/course/index.md",
    "docs/course/01-model-as-conditional-system.md",
    "docs/course/02-weights-activations-and-logits.md",
    "docs/course/03-attention-and-circuits.md",
    "docs/course/04-features-and-superposition.md",
    "docs/course/05-reasoning-and-feedback.md",
    "docs/course/06-causal-interpretability.md",
    "docs/course/07-safety-routing.md",
    "docs/course/08-capstone.md",
)

LESSON_REQUIREMENTS = {
    "docs/course/01-model-as-conditional-system.md": ("C03",),
    "docs/course/02-weights-activations-and-logits.md": ("C01", "C02"),
    "docs/course/03-attention-and-circuits.md": ("C04",),
    "docs/course/04-features-and-superposition.md": ("C06", "C10"),
    "docs/course/05-reasoning-and-feedback.md": ("C05",),
    "docs/course/06-causal-interpretability.md": ("C07", "C08", "C11", "C12"),
    "docs/course/07-safety-routing.md": ("C09",),
}

EXERCISE_FILES = (
    "docs/exercises/index.md",
    "docs/exercises/solutions.md",
    "docs/exercises/advanced.md",
    "docs/exercises/advanced-solutions.md",
)

EXAMPLE_FILES = (
    "examples/01_softmax_temperature.py",
    "examples/02_weight_vs_activation.py",
    "examples/03_attention_routing.py",
    "examples/04_probe_vs_causality.py",
    "examples/05_autoregressive_feedback.py",
    "examples/06_basis_invariance.py",
    "examples/07_redundant_paths.py",
    "examples/08_steering_controls.py",
)

REQUIRED_CHAPTER_HEADINGS = (
    "## 学完你应该能",
    "## 核心模型",
    "## 动手验证",
    "## 常见误区",
    "## 自测",
    "## 来源",
)

REQUIRED_LAB_MARKERS = (
    "## 问题",
    "## 运行",
    "## 结论边界",
    "llm-theory-lab",
)

LEGACY_PATHS = (
    "docs/00_THEORY_MAP.md",
    "docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md",
    "docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md",
    "docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md",
    "docs/04_REASONING_CONTEXT_AND_GENERATION.md",
    "docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md",
    "docs/06_METHODS_AND_CAUSAL_VALIDATION.md",
    "docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md",
    "docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md",
    "docs/09_UNIFIED_SYNTHESIS.md",
    "docs/10_SOURCE_BY_SOURCE_DIGEST.md",
    "docs/11_CANONICAL_CASE_STUDIES.md",
    "docs/12_METHODS_AND_INTERPRETATION_MATRIX.md",
    "docs/13_FIRST_PRINCIPLES_TUTORIAL.md",
    "docs/14_THEORY_TO_CODE_LAB.md",
    "docs/labs/05-feedback-and-safety.md",
)


def _require_file(relative: str) -> Path:
    path = ROOT / relative
    if not path.is_file():
        raise ValueError(f"missing learning artifact: {relative}")
    return path


def _require_text(path: Path, snippets: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise ValueError(f"{path.relative_to(ROOT)} missing required content: {missing}")


def validate() -> None:
    experiment_ids = [spec.experiment_id for spec in EXPERIMENTS]
    expected_ids = [f"C{index:02d}" for index in range(1, 13)]
    if experiment_ids != expected_ids:
        raise ValueError(f"experiment registry must be sequential: {expected_ids}")

    lab_paths = [spec.lab_path for spec in EXPERIMENTS]
    if len(lab_paths) != len(set(lab_paths)):
        raise ValueError("every transparent experiment must have a unique lab guide")

    for relative in COURSE_FILES:
        path = _require_file(relative)
        if relative != "docs/course/index.md":
            _require_text(path, REQUIRED_CHAPTER_HEADINGS)

    for relative, ids in LESSON_REQUIREMENTS.items():
        _require_text(_require_file(relative), ids)

    lab_index = _require_file("docs/labs/index.md")
    lab_index_text = lab_index.read_text(encoding="utf-8")
    for spec in EXPERIMENTS:
        lesson = _require_file(spec.lesson_path)
        lab = _require_file(spec.lab_path)
        _require_text(lesson, (spec.experiment_id,))
        _require_text(lab, REQUIRED_LAB_MARKERS + (spec.experiment_id,))
        if Path(spec.lab_path).name not in lab_index_text:
            raise ValueError(f"lab index does not reference {spec.lab_path}")

    for relative in EXERCISE_FILES + EXAMPLE_FILES:
        _require_file(relative)

    _require_text(
        _require_file("docs/exercises/advanced.md"),
        ("C10", "C11", "C12", "基底", "冗余", "Steering"),
    )
    _require_text(
        _require_file("docs/exercises/advanced-solutions.md"),
        ("协调变换", "联合消融", "随机方向"),
    )
    _require_text(
        _require_file("README.md"),
        ("十二个透明实验", "docs/exercises/advanced.md", "C10", "C11", "C12"),
    )
    _require_text(
        _require_file("docs/course/index.md"),
        ("C01–C12", "../labs/index.md", "../exercises/advanced.md"),
    )

    for relative in LEGACY_PATHS:
        if (ROOT / relative).exists():
            raise ValueError(f"legacy duplicate learning path still exists: {relative}")

    print(
        "learning path: OK "
        f"({len(COURSE_FILES) - 1} lessons, {len(EXPERIMENTS)} unique labs, "
        f"{len(EXERCISE_FILES)} exercise documents, {len(EXAMPLE_FILES)} examples)"
    )


def main() -> int:
    try:
        validate()
    except (OSError, ValueError) as exc:
        print(f"learning path check failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
