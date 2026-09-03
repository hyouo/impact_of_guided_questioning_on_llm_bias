"""Exact linear-algebra experiment for representation basis non-uniqueness."""

from __future__ import annotations

import numpy as np

from ..repro import runtime_metadata, set_global_seed
from ..result import CheckResult, ExperimentResult, checked_result


def run_basis_invariance(seed: int = 17, samples: int = 512) -> ExperimentResult:
    """Apply an invertible basis change while preserving the linear function."""

    if samples < 16:
        raise ValueError("samples must be at least 16")
    set_global_seed(seed)
    rng = np.random.default_rng(seed)

    hidden = rng.normal(size=(samples, 3))
    output_map = rng.normal(size=(3, 2))
    basis = np.array(
        [
            [1.20, 0.30, -0.10],
            [0.00, 0.80, 0.25],
            [0.15, -0.20, 1.10],
        ],
        dtype=np.float64,
    )

    original_output = hidden @ output_map
    transformed_hidden = hidden @ basis
    transformed_output_map = np.linalg.solve(basis, output_map)
    transformed_output = transformed_hidden @ transformed_output_map

    # Positive control: changing coordinates without updating the downstream map
    # generally changes the function.
    uncompensated_output = transformed_hidden @ output_map

    max_preservation_error = float(np.max(np.abs(transformed_output - original_output)))
    mean_coordinate_shift = float(np.mean(np.linalg.norm(transformed_hidden - hidden, axis=1)))
    mean_uncompensated_error = float(
        np.mean(np.linalg.norm(uncompensated_output - original_output, axis=1))
    )
    condition_number = float(np.linalg.cond(basis))

    checks = (
        CheckResult(
            name="协调变换保持输出",
            passed=max_preservation_error < 1e-12,
            observed=max_preservation_error,
            expectation="同步变换表示和下游权重后，最大输出误差 < 1e-12",
        ),
        CheckResult(
            name="内部坐标发生实质变化",
            passed=mean_coordinate_shift > 0.2,
            observed=mean_coordinate_shift,
            expectation="平均隐藏坐标 L2 变化 > 0.2",
        ),
        CheckResult(
            name="未补偿变换会改变函数",
            passed=mean_uncompensated_error > 0.1,
            observed=mean_uncompensated_error,
            expectation="只变表示、不变下游映射时，平均输出误差 > 0.1",
        ),
        CheckResult(
            name="变换矩阵数值稳定",
            passed=condition_number < 10.0,
            observed=condition_number,
            expectation="基底矩阵条件数 < 10",
        ),
    )

    return checked_result(
        experiment_id="C10",
        title="可逆基底变换与函数不变性",
        theory_claim=(
            "在线性子图中，表示坐标可做可逆变换并同步调整下游权重而保持函数；"
            "单个神经元坐标因此不是自动唯一的语义原子。"
        ),
        evidence_level="L0-exact-linear-equivalence",
        metrics={
            "seed": seed,
            "samples": samples,
            "basis": basis,
            "basis_condition_number": condition_number,
            "max_output_error_after_compensated_change": max_preservation_error,
            "mean_hidden_coordinate_shift": mean_coordinate_shift,
            "mean_output_error_without_compensation": mean_uncompensated_error,
        },
        checks=checks,
        caveats=(
            "这是线性子图中的精确等价；非线性、LayerNorm 和架构约束会限制可用变换。",
            "函数等价不意味着所有基底同样稀疏、稳定或容易解释。",
            "实际训练可能形成 privileged basis，因此结论不是‘神经元永远没有意义’。",
        ),
        metadata=runtime_metadata(),
    )
