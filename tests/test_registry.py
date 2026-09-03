from pathlib import Path

import pytest

from llm_theory_lab.registry import EXPERIMENTS, get_experiment, list_experiments

ROOT = Path(__file__).resolve().parents[1]


def test_registry_ids_are_unique_and_ordered() -> None:
    ids = [spec.experiment_id for spec in EXPERIMENTS]
    assert len(ids) == len(set(ids))
    assert ids == [f"C{index:02d}" for index in range(1, 13)]
    assert list_experiments() == EXPERIMENTS


def test_get_experiment_is_case_insensitive() -> None:
    assert get_experiment("c04").experiment_id == "C04"
    assert get_experiment("c12").experiment_id == "C12"


def test_unknown_experiment_raises() -> None:
    with pytest.raises(KeyError):
        get_experiment("C99")


def test_every_experiment_has_learning_context_and_unique_lab() -> None:
    lab_paths = []
    for spec in EXPERIMENTS:
        assert spec.falsifier.strip()
        assert spec.intuition.strip()
        assert spec.does_not_show.strip()
        assert (ROOT / spec.lesson_path).is_file()
        assert (ROOT / spec.lab_path).is_file()
        lab_paths.append(spec.lab_path)
    assert len(lab_paths) == len(set(lab_paths))
