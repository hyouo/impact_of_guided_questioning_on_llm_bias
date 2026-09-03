"""课程示例：比较权重大小、当前贡献和分布有效性。"""

from __future__ import annotations

from llm_theory_lab.experiments.weights import run_weight_activation


def main() -> None:
    result = run_weight_activation(seed=7, samples=20_000)
    metrics = result.metrics

    print("C01 | 权重大小不等于当前贡献")
    print(f"状态: {result.status}")
    print(f"当前贡献: {metrics['current_contributions']}")
    print(
        "大权重 / 小权重的 effectiveness proxy 比值: "
        f"{metrics['effectiveness_ratio_large_over_small']:.6f}"
    )
    print("注意: 这里使用的是透明玩具代理，不是前沿模型中的真实比例。")

    assert result.status == "pass"


if __name__ == "__main__":
    main()
