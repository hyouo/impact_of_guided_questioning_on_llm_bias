import pytest

from llm_theory_lab.registry import run_toy_suite


def test_all_toy_experiments_pass() -> None:
    results = run_toy_suite()
    assert len(results) == 9
    assert {result.experiment_id for result in results} == {
        "C01",
        "C02",
        "C03",
        "C04",
        "C05",
        "C06",
        "C07",
        "C08",
        "C09",
    }
    failures = [result.experiment_id for result in results if result.status != "pass"]
    assert failures == []


def test_probe_counterexample_has_positive_control() -> None:
    result = next(item for item in run_toy_suite(["C07"]) if item.experiment_id == "C07")
    assert result.metrics["probe_accuracy_unused_variable"] > 0.98
    assert result.metrics["mean_output_change_after_unused_ablation"] == pytest.approx(0.0)
    assert result.metrics["mean_output_change_after_causal_ablation"] > 1.5


def test_superposition_exposes_coactivation_interference() -> None:
    result = run_toy_suite(["C06"])[0]
    assert result.metrics["single_feature_accuracy"] == pytest.approx(1.0)
    assert result.metrics["pair_feature_accuracy"] < 1.0
