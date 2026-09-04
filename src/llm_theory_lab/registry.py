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
    claim_id: str
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
    source_urls: tuple[str, ...]
    claim_revision: int = 1
    model_revision: str = "transparent-numpy-v1"
    reproduction_status: str = "transparent-proxy"


EXPERIMENTS: tuple[ExperimentSpec, ...] = (
    ExperimentSpec(
        claim_id="H-C01",
        experiment_id="C01",
        title="权重、激活与有效性",
        theory_claim="大权重不必有大当前作用或大分布有效性。",
        category="weights",
        runner=run_weight_activation,
        intuition="连接的当前贡献至少要乘以源激活；在数据分布上还要考虑激活频率。",
        falsifier="在构造分布中，大权重无论源激活如何都始终产生更大作用。",
        lesson_path="docs/course/02-weights-activations-and-logits.md",
        lab_path="docs/labs/02-weight-vs-activation.md",
        does_not_show="不估计真实大模型中 interference weights 的比例，也不包含完整下游抵消。",
        source_urls=(
            "https://transformer-circuits.pub/2025/interference-weights/index.html",
            "https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C02",
        experiment_id="C02",
        title="温度与赔率",
        theory_claim="正温度下，token 对数赔率等于相对 logit 除以温度。",
        category="decoding",
        runner=run_temperature_odds,
        intuition="softmax 的公共分母在两个 token 的比值中消去，因此只剩 logit 差。",
        falsifier="数值 softmax 系统性偏离 log(p_i/p_j)=(z_i-z_j)/T。",
        lesson_path="docs/course/02-weights-activations-and-logits.md",
        lab_path="docs/labs/01-softmax-and-odds.md",
        does_not_show="不保证赔率更高的 token 一定被采样，也不把 API 的 temperature=0 代入公式。",
        source_urls=("https://transformer-circuits.pub/2021/framework/index.html",),
    ),
    ExperimentSpec(
        claim_id="H-C03",
        experiment_id="C03",
        title="输入条件计算",
        theory_claim="权重固定时，不同输入仍可激活不同路径并翻转输出。",
        category="conditional-computation",
        runner=run_input_conditioning,
        intuition="参数定义函数，输入决定函数本次落在哪个激活区域。",
        falsifier="固定权重网络对不同输入无法形成不同激活或输出。",
        lesson_path="docs/course/01-model-as-conditional-system.md",
        lab_path="docs/labs/06-input-conditioning.md",
        does_not_show="不说明真实模型只有少数可分离状态，也不证明某个 prompt 只走一条路径。",
        source_urls=(
            "https://transformer-circuits.pub/2021/framework/index.html",
            "https://transformer-circuits.pub/2025/bulk-update/index.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C04",
        experiment_id="C04",
        title="Attention 路由",
        theory_claim="改变 token 表示可通过 QK 改变读取位置，并通过 OV 改变写回。",
        category="attention",
        runner=run_attention_routing,
        intuition="QK 决定相对读取权重，value 与输出映射决定写回内容。",
        falsifier="key-relevant 扰动不改变注意力分布或聚合输出。",
        lesson_path="docs/course/03-attention-and-circuits.md",
        lab_path="docs/labs/03-attention-routing.md",
        does_not_show="不证明 Attention 热图就是解释，也不为真实模型中的头赋予单一语义标签。",
        source_urls=(
            "https://transformer-circuits.pub/2021/framework/index.html",
            "https://transformer-circuits.pub/2025/attention-qk/index.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C05",
        experiment_id="C05",
        title="自回归反馈",
        theory_claim="首 token 写回上下文后可放大成长期轨迹分叉。",
        category="generation",
        runner=run_autoregressive_feedback,
        intuition="每个已选 token 都成为下一步输入，因此局部选择会改变未来状态。",
        falsifier="只改变首 token 后，后续状态与序列仍完全相同。",
        lesson_path="docs/course/05-reasoning-and-feedback.md",
        lab_path="docs/labs/05-autoregressive-feedback.md",
        does_not_show="不估计自然语言模型中的真实效应大小，也不证明所有轨迹都有正反馈。",
        source_urls=(
            "https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html",
            "https://transformer-circuits.pub/2025/attribution-graphs/biology.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C06",
        experiment_id="C06",
        title="Superposition",
        theory_claim="稀疏特征可过完备表示，但共激活会产生非正交干扰。",
        category="representation",
        runner=run_superposition,
        intuition="稀疏特征很少共现时，可以共享少量维度并接受有限干扰。",
        falsifier="F>d 时单特征完全不可辨认，或共激活从不增加干扰。",
        lesson_path="docs/course/04-features-and-superposition.md",
        lab_path="docs/labs/07-superposition.md",
        does_not_show="人工二维几何不是学习出的 SAE 字典，也不代表真实模型特征独立。",
        source_urls=(
            "https://transformer-circuits.pub/2022/toy_model/index.html",
            "https://transformer-circuits.pub/2023/superposition-composition/index.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C07",
        experiment_id="C07",
        title="Probe 与因果使用",
        theory_claim="可解码不等于被模型输出头实际使用。",
        category="methods",
        runner=run_probe_vs_causality,
        intuition="表示可以包含冗余信息，而原模型的下游计算完全忽略它。",
        falsifier="任何高准确率 probe 的变量被消融后都必须改变输出。",
        lesson_path="docs/course/06-causal-interpretability.md",
        lab_path="docs/labs/04-probe-vs-causality.md",
        does_not_show="不估计现实 probe 的平均可靠度；它只构造一个反例推翻错误蕴含。",
        source_urls=(
            "https://transformer-circuits.pub/2022/mech-interp-essay/index.html",
            "https://transformer-circuits.pub/2025/attribution-graphs/methods.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C08",
        experiment_id="C08",
        title="Activation patching",
        theory_claim="反事实替换中间状态可测试候选因果中介。",
        category="methods",
        runner=run_activation_patching,
        intuition="把 clean 中间状态放入 corrupted 运行，能检验该状态是否传递目标信息。",
        falsifier="patch 候选中介与 patch 无关维度对输出恢复没有区别。",
        lesson_path="docs/course/06-causal-interpretability.md",
        lab_path="docs/labs/08-activation-patching.md",
        does_not_show="恢复不证明候选状态是唯一、最自然或完整的中介。",
        source_urls=(
            "https://transformer-circuits.pub/2025/attribution-graphs/methods.html",
            "https://transformer-circuits.pub/2025/attribution-graphs/biology.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C09",
        experiment_id="C09",
        title="识别与行为分离",
        theory_claim="识别信号存在不保证策略状态和最终行为一致。",
        category="safety-proxy",
        runner=run_recognition_action_dissociation,
        intuition="内容属性、权限/策略状态和动作 logits 可以由不同路径承载。",
        falsifier="检测维度一旦存在就必然直接决定最终动作。",
        lesson_path="docs/course/07-safety-routing.md",
        lab_path="docs/labs/09-safety-routing.md",
        does_not_show="无害代理不证明真实聊天模型使用相同坐标，也不提供可复用越狱方法。",
        source_urls=(
            "https://transformer-circuits.pub/2025/attribution-graphs/biology.html",
            "https://transformer-circuits.pub/2025/november-update/index.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C10",
        experiment_id="C10",
        title="基底不变性",
        theory_claim="可逆表示变换可配合下游权重变换保持线性函数不变。",
        category="representation",
        runner=run_basis_invariance,
        intuition="神经元是某个坐标系中的轴；同一函数可以由不同内部坐标描述。",
        falsifier="协调改变表示与下游映射后，输出仍无法在数值精度内保持一致。",
        lesson_path="docs/course/04-features-and-superposition.md",
        lab_path="docs/labs/10-basis-invariance.md",
        does_not_show="不说明所有基底同样有用，也不否认实际架构可能形成 privileged basis。",
        source_urls=(
            "https://transformer-circuits.pub/2022/mech-interp-essay/index.html",
            "https://transformer-circuits.pub/2023/privileged-basis/index.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C11",
        experiment_id="C11",
        title="冗余路径与消融",
        theory_claim="单路径消融不降低准确率，不足以证明该路径未参与计算。",
        category="methods",
        runner=run_redundant_paths,
        intuition="两个冗余路径可让离散行为饱和，同时每条路径仍改变连续 margin。",
        falsifier="在双路径构造中，单点消融必然降低准确率，或联合消融仍不暴露冗余。",
        lesson_path="docs/course/06-causal-interpretability.md",
        lab_path="docs/labs/11-redundant-paths.md",
        does_not_show="不证明所有无消融效应都来自冗余；干预错误和指标不敏感也可能造成零结果。",
        source_urls=(
            "https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html",
            "https://transformer-circuits.pub/2025/attribution-graphs/methods.html",
        ),
    ),
    ExperimentSpec(
        claim_id="H-C12",
        experiment_id="C12",
        title="Steering 对照",
        theory_claim="Steering 的机制特异性需要剂量、反向和等范数方向对照。",
        category="methods",
        runner=run_steering_controls,
        intuition="任意扰动都可能改变输出，目标方向必须相对合理控制表现出特异性。",
        falsifier="目标方向不呈剂量/符号响应，或不超过等范数随机方向。",
        lesson_path="docs/course/06-causal-interpretability.md",
        lab_path="docs/labs/12-steering-controls.md",
        does_not_show="超过随机方向只增强可操纵性证据，不证明方向自然、唯一或必要。",
        source_urls=(
            "https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html",
            "https://transformer-circuits.pub/2026/may-update/index.html",
            "https://transformer-circuits.pub/2026/emotions/index.html",
        ),
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
        "claim_id": spec.claim_id,
        "claim_revision": spec.claim_revision,
        "category": spec.category,
        "intuition": spec.intuition,
        "falsifier": spec.falsifier,
        "lesson_path": spec.lesson_path,
        "lab_path": spec.lab_path,
        "does_not_show": spec.does_not_show,
        "source_urls": list(spec.source_urls),
        "model_revision": spec.model_revision,
        "reproduction_status": spec.reproduction_status,
    }
    return replace(
        result,
        title=spec.title,
        theory_claim=spec.theory_claim,
        metadata=metadata,
    )


def run_toy_suite(experiment_ids: Iterable[str] | None = None) -> list[ExperimentResult]:
    specs = (
        EXPERIMENTS
        if experiment_ids is None
        else tuple(get_experiment(item) for item in experiment_ids)
    )
    return [_run_with_learning_context(spec) for spec in specs]
