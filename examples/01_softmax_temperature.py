"""课程示例：验证温度、logit 差与 token 赔率的精确关系。"""

from __future__ import annotations

from llm_theory_lab.experiments.temperature import run_temperature_odds


def main() -> None:
    result = run_temperature_odds()
    multiplier = result.metrics["odds_multiplier_after_plus_one_logit_at_T1"]

    print("C02 | 温度、softmax 与 token 赔率")
    print(f"状态: {result.status}")
    print(f"当 T=1 且目标 token 的相对 logit +1，赔率乘数: {multiplier:.12f}")
    print("预期: e ≈ 2.718281828459")
    print("注意: 赔率增大不等于该 token 一定被采样。")

    assert result.status == "pass"


if __name__ == "__main__":
    main()
