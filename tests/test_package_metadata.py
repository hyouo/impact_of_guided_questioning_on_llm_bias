from importlib.metadata import version

import llm_theory_lab


def test_runtime_version_matches_installed_distribution() -> None:
    assert llm_theory_lab.__version__ == version("llm-theory-lab")


def test_public_experiment_registry_is_not_empty() -> None:
    assert llm_theory_lab.EXPERIMENTS
