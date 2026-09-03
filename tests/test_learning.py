from collections import Counter

from llm_theory_lab.learning import (
    get_course_module,
    get_experiment_guide,
    list_course_modules,
    load_curriculum,
)
from llm_theory_lab.registry import EXPERIMENTS


def test_curriculum_version_and_module_order() -> None:
    curriculum = load_curriculum()
    assert curriculum["curriculum_version"] == "0.3.0"
    assert [module["id"] for module in list_course_modules()] == [
        f"M{index:02d}" for index in range(1, 9)
    ]


def test_course_covers_every_experiment_once() -> None:
    assigned = [lab for module in list_course_modules() for lab in module["labs"]]
    assert Counter(assigned) == Counter(spec.experiment_id for spec in EXPERIMENTS)


def test_experiment_guides_match_registry() -> None:
    curriculum = load_curriculum()
    assert set(curriculum["experiments"]) == {spec.experiment_id for spec in EXPERIMENTS}
    assert get_experiment_guide("c04")["guide"].endswith("c04-attention-routing.md")


def test_module_lookup_is_case_insensitive() -> None:
    assert get_course_module("m06")["title"] == "因果可解释性"
