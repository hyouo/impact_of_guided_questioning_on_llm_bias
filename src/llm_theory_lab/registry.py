"""Single source of truth for theory-linked transparent experiments."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace

from .experiments.attention import run_attention_routing
from .experiments.basis_invariance import run_basis_invariance
from .experiments.conditional import run_input_conditioning
from .experiments.feedback import run_autoregressive_feedback
from .experiments.patching import run_activation_patching
from .experiments.probe_causality import run_probe_vs_causality
from .experiments.redundancy import run_redundant_paths
from .experiments.safety_routing import run_recognition_action_dissociation
from .experiments.steering_controls import run_steering_controls
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
    intuition: str
    falsifier: str
    lesson_path: str
    lab_path: str
    does_not_show: str


EXPERIMENTS: tuple[ExperimentSpec, ...] = (
    ExperimentSpec(
        "C01",
        "权重、激活与有效性",
        "大权重不必有大当前作用或大分布有效性。",
        "weights",
        run_weight_activation,
        "连接的当前贡献至少要乘以源激活；在数据分布上还要考虑激活频率。",
        "在构造分布中，大权重无论源激活如何都始终产生更大作用。",
        "docs/course/02-weights-activations-and-logits.md",
        "docs/labs/02-weight-vs-activation.md",
        "不估计真实大模型中 interference weights 的比例，也不包含完整下游抵消。",
    ),
    ExperimentSpec(
        "C02",
        "温度与赔率",
        "正温度下，token 对数赔率等于相对 logit 除以温度。",
        "decoding",
        run_temperature_odds,
        "softmax 的公共分母在两个 token 的比值中消去，因此只剩 logit 差。",
        "数值 softmax 系统性偏离 log(p_i/p_j)=(z_i-z_j)/T。",
        "docs/course/02-weights-activations-and-logits.md",
        "docs/labs/01-softmax-and-odds.md",
        "不保证赔率更高的 token 一定被采样，也不把 API 的 temperature=0 代入公式。",
    ),
    ExperimentSpec(
        "C03",
        "输入条件计算",
        "权重固定时，不同输入仍可激活不同路径并翻转输出。",
        "conditional-computation",
        run_input_conditioning,
        "参数定义函数，输入决定函数本次落在哪个激活区域。",
        "固定权重网络对不同输入无法形成不同激活或输出。",
        "docs/course/01-model-as-conditional-system.md",
        "docs/labs/06-input-conditioning.md",
        "不说明真实模型只有少数可分离状态，也不证明某个 prompt 只走一条路径。",
    ),
    ExperimentSpec(
        "C04",
        "Attention 路由",
        "改变 token 表示可通过 QK 改变读取位置，并通过 OV 改变写回。",
        "attention",
        run_attention_routing,
        "QK 决定相对读取权重，value 与输出映射决定写回内容。",
        "key-relevant 扰动不改变注意力分布或聚合输出。",
        "docs/course/03-attention-and-circuits.md",
        "docs/labs/03-attention-routing.md",
        "不证明 Attention 热图就是解释，也不为真实模型中的头赋予单一语义标签。",
    ),
    ExperimentSpec(
        "C05",
        "自回归反馈",
        "首 token 写回上下文后可放大成长期轨迹分叉。",
        "generation",
        run_autoregressive_feedback,
        "每个已选 token 都成为下一步输入，因此局部选择会改变未来状态。",
        "只改变首 token 后，后续状态与序列仍完全相同。",
        "docs/course/05-reasoning-and-feedback.md",
        "docs/labs/05-autoregressive-feedback.md",
        "不估计自然语言模型中的真实效应大小，也不证明所有轨迹都有正反馈。",
    ),
    ExperimentSpec(
        "C06",
        "Superposition",
        "稀疏特征可过完备表示，但共激活会产生非正交干扰。",
        "representation",
        run_superposition,
        "稀疏特征很少共现时，可以共享少量维度并接受有限干扰。",
        "F>d 时单特征完全不可辨认，或共激活从不增加干扰。",
        "docs/course/04-features-and-superposition.md",
        "docs/labs/07-superposition.md",
        "人工二维几何不是学习出的 SAE 字典，也不代表真实模型特征独立。",
    ),
    ExperimentSpec(
        "C07",
        "Probe 与因果使用",
        "可解码不等于被模型输出头实际使用。",
        "methods",
        run_probe_vs_causality,
        "表示可以包含冗余信息，而原模型的下游计算完全忽略它。",
        "任何高准确率 probe 的变量被消融后都必须改变输出。",
        "docs/course/06-causal-interpretability.md",
        "docs/labs/04-probe-vs-causality.md",
        "不估计现实 probe 的平均可靠度；它只构造一个反例推翻错误蕴含。",
    ),
    ExperimentSpec(
        "C08",
        "Activation patching",
        "反事实替换中间状态可测试候选因果中介。",
        "methods",
        run_activation_patching,
        "把 clean 中间状态放入 corrupted 运行，能检验该状态是否传递目标信息。",
        "patch 候选中介与 patch 无关维度对输出恢复没有区别。",
        "docs/course/06-causal-interpretability.md",
        "docs/labs/08-activation-patching.md",
        "恢复不证明候选状态是唯一、最自然或完整的中介。",
    ),
    ExperimentSpec(
        "C09",
        "识别与行为分离",
        "识别信号存在不保证策略状态和最终行为一致。",
        "safety-proxy",
        run_recognition_action_dissociation,
        "内容属性、权限/策略状态和动作 logits 可以由不同路径承载。",
        "检测维度一旦存在就必然直接决定最终动作。",
        "docs/course/07-safety-routing.md",
        "docs/labs/09-safety-routing.md",
        "无害代理不证明真实聊天模型使用相同坐标，也不提供可复用越狱方法。",
    ),
    ExperimentSpec(
        "C10",
        "基底不变性",
        "可逆表示变换可配合下游权重变换保持线性函数不变。",
        "representation",
        run_basis_invariance,
        "神经元是某个坐标系中的轴；同一函数可以由不同内部坐标描述。",
        "协调改变表示与下游映射后，输出仍无法在数值精度内保持一致。",
        "docs/course/04-features-and-superposition.md",
        "docs/labs/10-basis-invariance.md",
        "不说明所有基底同样有用，也不否认实际架构可能形成 privileged basis。",
    ),
    ExperimentSpec(
        "C11",
        "冗余路径与消融",
        "单路径消融不降低准确率，不足以证明该路径未参与计算。",
        "methods",
        run_redundant_paths,
        "两个冗余路径可让离散行为饱和，同时每条路径仍改变连续 margin。",
        "在双路径构造中，单点消融必然降低准确率，或联合消融仍不暴露冗余。",
        "docs/course/06-causal-interpretability.md",
        "docs/labs/11-redundant-paths.md",
        "不证明所有无消融效应都来自冗余；干预错误和指标不敏感也可能造成零结果。",
    ),
    ExperimentSpec(
        "C12",
        "Steering 对照",
        "Steering 的机制特异性需要剂量、反向和等范数方向对照。",
        "methods",
        run_steering_controls,
        "任意扰动都可能改变输出，目标方向必须相对合理控制表现出特异性。",
        "目标方向不呈剂量/符号响应，或不超过等范数随机方向。",
        "docs/course/06-causal-interpretability.md",
        "docs/labs/12-steering-controls.md",
        "超过随机方向只增强可操纵性证据，不证明方向自然、唯一或必要。",
    ),
)


def list_experiments() -> tuple[ExperimentSpec, ...]:
    return EXPERIMENTS


def get_experiment(experiment_id: str) -> ExperimentSpec:
    normalized = experiment_id.upper()
    for experiment in EXPERIMENTS:
        if experiment.experiment_id == normalized:
            return experiment
    known = ", ".join(spec.experiment_id for spec in EXPERIMENTS)
    raise KeyError(f"unknown experiment: {experiment_id!r}; choose one of {known}")


def _run_with_learning_context(spec: ExperimentSpec) -> ExperimentResult:
    result = spec.runner()
    metadata = dict(result.metadata)
    metadata["learning"] = {
        "category": spec.category,
        "intuition": spec.intuition,
        "falsifier": spec.falsifier,
        "lesson_path": spec.lesson_path,
        "lab_path": spec.lab_path,
        "does_not_show": spec.does_not_show,
    }
    return replace(result, metadata=metadata)


def run_toy_suite(experiment_ids: Iterable[str] | None = None) -> list[ExperimentResult]:
    specs = (
        EXPERIMENTS
        if experiment_ids is None
        else tuple(get_experiment(item) for item in experiment_ids)
    )
    return [_run_with_learning_context(spec) for spec in specs]
