"""Single source of truth for theory-linked toy experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .experiments.attention import run_attention_routing
from .experiments.conditional import run_input_conditioning
from .experiments.feedback import run_autoregressive_feedback
from .experiments.patching import run_activation_patching
from .experiments.probe_causality import run_probe_vs_causality
from .experiments.safety_routing import run_recognition_action_dissociation
from .experiments.superposition import run_superposition
from .experiments.temperature import run_temperature_odds
from .experiments.weights import run_weight_activation
from .result import ExperimentResult

Runner = Callable[[], ExperimentResult]


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    title: str
    theory_claim: str
    category: str
    runner: Runner
    falsifier: str


EXPERIMENTS: tuple[ExperimentSpec, ...] = (
    ExperimentSpec(
        "C01",
        "权重、激活与有效性",
        "大权重不必有大当前作用或大分布有效性。",
        "weights",
        run_weight_activation,
        "在构造分布中，大权重无论源激活如何都始终产生更大作用。",
    ),
    ExperimentSpec(
        "C02",
        "温度与赔率",
        "正温度下，token 对数赔率等于相对 logit 除以温度。",
        "decoding",
        run_temperature_odds,
        "数值 softmax 系统性偏离 log(p_i/p_j)=(z_i-z_j)/T。",
    ),
    ExperimentSpec(
        "C03",
        "输入条件计算",
        "权重固定时，不同输入仍可激活不同路径并翻转输出。",
        "conditional-computation",
        run_input_conditioning,
        "固定权重网络对不同输入无法形成不同激活或输出。",
    ),
    ExperimentSpec(
        "C04",
        "Attention 路由",
        "改变 token 表示可通过 QK 改变读取位置，并通过 OV 改变写回。",
        "attention",
        run_attention_routing,
        "key-relevant 扰动不改变注意力分布或聚合输出。",
    ),
    ExperimentSpec(
        "C05",
        "自回归反馈",
        "首 token 写回上下文后可放大成长期轨迹分叉。",
        "generation",
        run_autoregressive_feedback,
        "只改变首 token 后，后续状态与序列仍完全相同。",
    ),
    ExperimentSpec(
        "C06",
        "Superposition",
        "稀疏特征可过完备表示，但共激活会产生非正交干扰。",
        "representation",
        run_superposition,
        "F>d 时单特征完全不可辨认，或共激活从不增加干扰。",
    ),
    ExperimentSpec(
        "C07",
        "Probe 与因果使用",
        "可解码不等于被模型输出头实际使用。",
        "methods",
        run_probe_vs_causality,
        "任何高准确率 probe 的变量被消融后都必须改变输出。",
    ),
    ExperimentSpec(
        "C08",
        "Activation patching",
        "反事实替换中间状态可测试候选因果中介。",
        "methods",
        run_activation_patching,
        "patch 候选中介与 patch 无关维度对输出恢复没有区别。",
    ),
    ExperimentSpec(
        "C09",
        "识别与行为分离",
        "识别信号存在不保证策略状态和最终行为一致。",
        "safety-proxy",
        run_recognition_action_dissociation,
        "检测维度一旦存在就必然直接决定最终动作。",
    ),
)


def list_experiments() -> tuple[ExperimentSpec, ...]:
    return EXPERIMENTS


def get_experiment(experiment_id: str) -> ExperimentSpec:
    normalized = experiment_id.upper()
    for experiment in EXPERIMENTS:
        if experiment.experiment_id == normalized:
            return experiment
    raise KeyError(f"unknown experiment: {experiment_id}")


def run_toy_suite(experiment_ids: Iterable[str] | None = None) -> list[ExperimentResult]:
    specs = EXPERIMENTS if experiment_ids is None else tuple(get_experiment(item) for item in experiment_ids)
    return [spec.runner() for spec in specs]
