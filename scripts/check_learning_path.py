#!/usr/bin/env python3
"""Validate that the repository has one coherent, executable learning path."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
    "docs/course/01-model-as-conditional-system.md": ("C03", "C05"),
    "docs/course/02-weights-activations-and-logits.md": ("C01", "C02"),
    "docs/course/03-attention-and-circuits.md": ("C04",),
    "docs/course/04-features-and-superposition.md": ("C06",),
    "docs/course/05-reasoning-and-feedback.md": ("C05",),
    "docs/course/06-causal-interpretability.md": ("C07", "C08"),
    "docs/course/07-safety-routing.md": ("C09",),
}

LAB_FILES = (
    "docs/labs/index.md",
    "docs/labs/01-softmax-and-odds.md",
    "docs/labs/02-weight-vs-activation.md",
    "docs/labs/03-attention-routing.md",
    "docs/labs/04-probe-vs-causality.md",
    "docs/labs/05-feedback-and-safety.md",
)

EXERCISE_FILES = (
    "docs/exercises/index.md",
    "docs/exercises/solutions.md",
)

EXAMPLE_FILES = tuple(
    f"examples/{index:02d}_{name}.py"
    for index, name in (
        (1, "softmax_temperature"),
        (2, "weight_vs_activation"),
        (3, "attention_routing"),
        (4, "probe_vs_causality"),
        (5, "autoregressive_feedback"),
    )
)

REQUIRED_HEADINGS = (
    "## 学完你应该能",
    "## 核心模型",
    "## 动手验证",
    "## 常见误区",
    "## 自测",
    "## 来源",
)

LEGACY_PATHS = (
    "code/README.md",
    "docs/00_THEORY_MAP.md",
    "docs/01_PARAMETERS_ACTIVATIONS_AND_TOKENS.md",
    "docs/02_REPRESENTATIONS_SUPERPOSITION_AND_GEOMETRY.md",
    "docs/03_CIRCUITS_ATTENTION_AND_CONDITIONAL_COMPUTATION.md",
    "docs/04_REASONING_CONTEXT_AND_GENERATION.md",
    "docs/05_SAFETY_JAILBREAK_AND_PROMPT_INJECTION.md",
    "docs/06_METHODS_AND_CAUSAL_VALIDATION.md",
    "docs/07_EVIDENCE_LIMITS_AND_CLAIMS.md",
    "docs/08_OPEN_PROBLEMS_AND_RESEARCH_ROADMAP.md",
    "docs/13_FIRST_PRINCIPLES_TUTORIAL.md",
    "docs/14_THEORY_TO_CODE_LAB.md",
)


def fail(message: str) -> None:
    print(f"learning-path error: {message}", file=sys.stderr)


def _require_text(path: Path, snippets: tuple[str, ...], relative: str) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    errors = 0
    for snippet in snippets:
        if snippet not in text:
            fail(f"{relative} missing required content {snippet!r}")
            errors += 1
    return errors


def main() -> int:
    errors = 0

    required_files = COURSE_FILES + LAB_FILES + EXERCISE_FILES + EXAMPLE_FILES
    for relative in required_files:
        if not (ROOT / relative).is_file():
            fail(f"missing required learning file: {relative}")
            errors += 1

    for relative, experiment_ids in LESSON_REQUIREMENTS.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                fail(f"{relative} missing heading {heading!r}")
                errors += 1
        for experiment_id in experiment_ids:
            if experiment_id not in text:
                fail(f"{relative} does not connect to experiment {experiment_id}")
                errors += 1
        if "不能" not in text and "边界" not in text:
            fail(f"{relative} does not state a conclusion boundary")
            errors += 1

    exercise_path = ROOT / "docs/exercises/index.md"
    solution_path = ROOT / "docs/exercises/solutions.md"
    exercise_sections = tuple(f"# {letter}｜" for letter in "ABCDEFGH")
    solution_sections = tuple(f"# {letter}｜" for letter in "ABCDEFGH")
    errors += _require_text(exercise_path, exercise_sections, "docs/exercises/index.md")
    errors += _require_text(solution_path, solution_sections, "docs/exercises/solutions.md")
    errors += _require_text(
        exercise_path,
        tuple(f"C{index:02d}" for index in range(1, 10)),
        "docs/exercises/index.md",
    )
    errors += _require_text(
        solution_path,
        ("# 自我评分量表", "必要与充分", "Prompt injection"),
        "docs/exercises/solutions.md",
    )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in (
        "docs/course/index.md",
        "docs/labs/index.md",
        "docs/exercises/index.md",
        "llm-theory-lab explain",
    ):
        if required not in readme:
            fail(f"README.md missing primary entry {required!r}")
            errors += 1

    course_index = (ROOT / "docs/course/index.md").read_text(encoding="utf-8")
    for required in ("../labs/index.md", "../exercises/index.md", "../exercises/solutions.md"):
        if required not in course_index:
            fail(f"course index does not complete the learning loop with {required!r}")
            errors += 1

    for relative in LEGACY_PATHS:
        if (ROOT / relative).exists():
            fail(f"legacy duplicate remains in the active tree: {relative}")
            errors += 1

    if errors:
        return 1

    print(
        "learning path: OK "
        f"({len(COURSE_FILES) - 1} lessons, {len(LAB_FILES) - 1} labs, "
        f"{len(EXERCISE_FILES)} exercise documents, {len(EXAMPLE_FILES)} examples)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
