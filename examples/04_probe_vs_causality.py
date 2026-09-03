"""课程示例：构造高 probe 准确率但零输出效应的变量。"""

from __future__ import annotations

from llm_theory_lab.experiments.probe_causality import run_probe_vs_causality


def main() -> None:
    result = run_probe_vs_causality(seed=13, samples=4_000)
    metrics = result.metrics

    print("C07 | 可解码信息不等于因果使用")
    print(f"状态: {result.status}")
    print(f"未使用变量的 probe 准确率: {metrics['probe_accuracy_unused_variable']:.4f}")
    print(
        "消融未使用变量后的平均输出变化: "
        f"{metrics['mean_output_change_after_unused_ablation']:.12f}"
    )
    print(
        "消融真实因果变量后的平均输出变化: "
        f"{metrics['mean_output_change_after_causal_ablation']:.4f}"
    )
    print("结论: probe 证明信息可读，不自动证明原模型使用它。")

    assert result.status == "pass"


if __name__ == "__main__":
    main()
