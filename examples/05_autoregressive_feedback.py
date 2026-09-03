"""课程示例：观察首 token 反馈与识别—策略—行为分离。"""

from __future__ import annotations

from llm_theory_lab.experiments.feedback import run_autoregressive_feedback
from llm_theory_lab.experiments.safety_routing import run_recognition_action_dissociation


def main() -> None:
    feedback = run_autoregressive_feedback()
    safety = run_recognition_action_dissociation()

    print("C05 | 首 token 与自回归轨迹")
    print(f"强制 A: {feedback.metrics['trajectory_forced_A']}")
    print(f"强制 B: {feedback.metrics['trajectory_forced_B']}")
    print(f"最终状态距离: {feedback.metrics['final_state_distance']:.4f}")
    print()
    print("C09 | 识别、策略状态与行为分离")
    print(f"状态: {safety.status}")
    for check in safety.checks:
        print(f"- {check.name}: {'通过' if check.passed else '失败'}")
    print("注意: 这是无害访问控制代理，不是越狱载荷或真实安全坐标。")

    assert feedback.status == "pass"
    assert safety.status == "pass"


if __name__ == "__main__":
    main()
