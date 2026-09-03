import pytest

from llm_theory_lab.registry import run_toy_suite


def test_all_toy_experiments_pass() -> None:
    results = run_toy_suite()
    assert len(results) == 12
    assert {result.experiment_id for result in results} == {
        f"C{index:02d}" for index in range(1, 13)
    }
    failures = [result.experiment_id for result in results if result.status != "pass"]
    assert failures == []


def test_probe_counterexample_has_positive_control() -> None:
    result = run_toy_suite(["C07"])[0]
    assert result.metrics["probe_accuracy_unused_variable"] > 0.98
    assert result.metrics["mean_output_change_after_unused_ablation"] == pytest.approx(0.0)
    assert result.metrics["mean_output_change_after_causal_ablation"] > 1.5


def test_superposition_exposes_coactivation_interference() -> None:
    result = run_toy_suite(["C06"])[0]
    assert result.metrics["single_feature_accuracy"] == pytest.approx(1.0)
    assert result.metrics["pair_feature_accuracy"] < 1.0


def test_basis_change_preserves_function_only_when_compensated() -> None:
    result = run_toy_suite(["C10"])[0]
    assert result.metrics["mean_hidden_coordinate_shift"] > 0.2
    assert result.metrics["max_output_error_after_compensated_change"] < 1e-12
    assert result.metrics["mean_output_error_without_compensation"] > 0.1


def test_redundant_paths_hide_effect_from_accuracy() -> None:
    result = run_toy_suite(["C11"])[0]
    assert result.metrics["baseline_accuracy"] == pytest.approx(1.0)
    assert result.metrics["accuracy_after_ablate_a"] == pytest.approx(1.0)
    assert result.metrics["accuracy_after_ablate_b"] == pytest.approx(1.0)
    assert result.metrics["accuracy_after_joint_ablation"] == pytest.approx(0.5)
    assert result.metrics["mean_margin_change_after_ablate_a"] > 0.9


def test_steering_target_exceeds_control_distribution() -> None:
    result = run_toy_suite(["C12"])[0]
    assert result.metrics["target_positive_effect"] > result.metrics["random_abs_q99"]
    assert result.metrics["target_negative_effect"] < 0.0
    assert result.metrics["orthogonal_effect"] == pytest.approx(0.0, abs=1e-12)
