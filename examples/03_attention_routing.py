"""课程示例：观察输入如何同时改变 QK 路由与 OV 聚合输出。"""

from __future__ import annotations

import numpy as np

from llm_theory_lab.experiments.attention import run_attention_routing


def main() -> None:
    result = run_attention_routing()
    metrics = result.metrics
    baseline = np.asarray(metrics["baseline_attention"])
    perturbed = np.asarray(metrics["perturbed_attention"])

    print("C04 | Attention 的 QK 路由与 OV 写回")
    print(f"状态: {result.status}")
    print(f"基线最高注意力位置: {int(np.argmax(baseline))}")
    print(f"扰动后最高注意力位置: {int(np.argmax(perturbed))}")
    print(f"聚合输出 L2 变化: {metrics['output_l2_shift']:.6f}")
    print("注意: Attention pattern 不是完整因果解释。")

    assert result.status == "pass"


if __name__ == "__main__":
    main()
