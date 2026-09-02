import pytest

from llm_theory_lab.registry import EXPERIMENTS, get_experiment, list_experiments


def test_registry_ids_are_unique_and_ordered() -> None:
    ids = [spec.experiment_id for spec in EXPERIMENTS]
    assert len(ids) == len(set(ids))
    assert ids == [f"C{index:02d}" for index in range(1, 10)]
    assert list_experiments() == EXPERIMENTS


def test_get_experiment_is_case_insensitive() -> None:
    assert get_experiment("c04").experiment_id == "C04"


def test_unknown_experiment_raises() -> None:
    with pytest.raises(KeyError):
        get_experiment("C99")


def test_every_experiment_has_a_falsifier() -> None:
    assert all(spec.falsifier.strip() for spec in EXPERIMENTS)
