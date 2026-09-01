"""A minimal activation-patching causal intervention."""

from __future__ import annotations

import numpy as np

from ..repro import runtime_metadata
from ..result import CheckResult, ExperimentResult, checked_result


def _output_gap(hidden: np.ndarray) -> float:
    output_map = np.array([[2.0, -2.0], [0.15, 0.15]], dtype=np.float64)
    logits = hidden @ output_map
    return float(logits[0] - logits[1])


def run_activation_patching() -> ExperimentResult:
    clean_hidden = np.array([1.0, 0.25], dtype=np.float64)
    corrupted_hidden = np.array([-1.0, 0.25], dtype=np.float64)
    patched_hidden = corrupted_hidden.copy()
    patched_hidden[0] = clean_hidden[0]

    clean_gap = _output_gap(clean_hidden)
    corrupted_gap = _output_gap(corrupted_hidden)
    patched_gap = _output_gap(patched_hidden)
    denominator = clean_gap - corrupted_gap
    restoration = (patched_gap - corrupted_gap) / denominator if denominator else 0.0

    control_patched = corrupted_hidden.copy()
    control_patched[1] = clean_hidden[1]
    control_gap = _output_gap(control_patched)
    control_restoration = (control_gap - corrupted_gap) / denominator if denominator else 0.0

    checks = (
        CheckResult(
            name="候选中介恢复输出",
            passed=abs(restoration - 1.0) < 1e-12,
            observed=restoration,
            expectation="把 clean 的因果维度 patch 到 corrupted 后恢复比例为 1",
        ),
        CheckResult(
            name="无关维度负对照",
            passed=abs(control_restoration) < 1e-12,
            observed=control_restoration,
            expectation="patch 无关维度不应恢复输出",
        ),
    )

    return checked_result(
        experiment_id="C08",
        title="Activation patching 与中间状态因果性",
        theory_claim="把 clean 运行中的候选中间状态替换进 corrupted 运行，可检验该状态是否传递答案因果效应。",
        evidence_level="L1-transparent-toy",
        metrics={
            "clean_hidden": clean_hidden,
            "corrupted_hidden": corrupted_hidden,
            "patched_hidden": patched_hidden,
            "clean_output_gap": clean_gap,
            "corrupted_output_gap": corrupted_gap,
            "patched_output_gap": patched_gap,
            "restoration_fraction": restoration,
            "negative_control_restoration": control_restoration,
        },
        checks=checks,
        caveats=(
            "真实 activation patching 可能把分布外状态注入模型，必须配置位置、层和负对照。",
            "成功恢复说明该状态足以传递效应，不自动证明它是唯一自然中介。",
        ),
        metadata=runtime_metadata(),
    )
