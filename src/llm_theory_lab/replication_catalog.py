"""Machine-readable replication coverage for the Transformer Circuits source catalog.

The catalog deliberately separates three questions:

1. Is the original result exactly reproducible from public assets?
2. What related protocol is implemented in this repository today?
3. What would still be required to reproduce the source's main empirical claims?

A transparent toy proxy is never labelled as an exact reproduction of a
proprietary-model result.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from .registry import list_experiments

EXPECTED_SOURCE_COUNT = 56
CATALOG_RESOURCE = "transformer_circuits_catalog.csv"

SOURCE_KINDS = frozenset(
    {
        "paper",
        "research_update",
        "cross_post",
        "essay",
        "tool",
        "infrastructure",
        "exercises",
        "education",
        "predecessor",
    }
)
EMPIRICAL_SOURCE_KINDS = frozenset({"paper", "research_update", "cross_post"})
REFERENCE_SOURCE_KINDS = SOURCE_KINDS - EMPIRICAL_SOURCE_KINDS

EXACT_FEASIBILITY_VALUES = frozenset(
    {"partial-public", "blocked-proprietary-assets", "not-applicable"}
)
CURRENT_STAGE_VALUES = frozenset(
    {"open-model-partial", "transparent-proxy", "planned", "reference-synthesis"}
)
PROTOCOL_STATES = frozenset(
    {"implemented-transparent", "implemented-open-model", "implemented-mixed", "planned"}
)
OPEN_MODEL_EXPERIMENT_IDS = frozenset({"M01", "M02", "M03", "M04"})


class ReplicationCatalogError(ValueError):
    """Raised when the source-to-replication contract is inconsistent."""


@dataclass(frozen=True)
class ReplicationProtocol:
    protocol_id: str
    title: str
    implementation_state: str
    experiment_ids: tuple[str, ...]
    purpose: str
    limitation: str


@dataclass(frozen=True)
class ReplicationRecord:
    source_id: str
    period: str
    title: str
    url: str
    source_kind: str
    theme: str
    role: str
    exact_feasibility: str
    current_stage: str
    protocol_ids: tuple[str, ...]
    available_experiment_ids: tuple[str, ...]
    blocker: str
    next_step: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PROTOCOLS: tuple[ReplicationProtocol, ...] = (
    ReplicationProtocol(
        protocol_id="P01-CIRCUIT-ALGEBRA",
        title="Residual-stream, QK/OV and basis algebra",
        implementation_state="implemented-transparent",
        experiment_ids=("C02", "C03", "C04", "C10"),
        purpose="Test algebraic identities and counterexamples behind circuit-level reasoning.",
        limitation="Transparent NumPy systems do not establish which circuits a frontier model learned.",
    ),
    ReplicationProtocol(
        protocol_id="P02-SUPERPOSITION-WEIGHTS",
        title="Superposition, interference and redundant paths",
        implementation_state="implemented-transparent",
        experiment_ids=("C01", "C06", "C10", "C11"),
        purpose="Reproduce controlled geometry, effectiveness and redundancy phenomena.",
        limitation="The experiments are existence proofs, not estimates for a production model.",
    ),
    ReplicationProtocol(
        protocol_id="P03-ATTENTION-OPEN-MODEL",
        title="Open-model attention and residual observations",
        implementation_state="implemented-mixed",
        experiment_ids=("C04", "M01", "M03", "M04"),
        purpose="Inspect format sensitivity, residual patching and induction-style attention in open models.",
        limitation="The protocol is model- and prompt-specific and does not reproduce proprietary Claude runs.",
    ),
    ReplicationProtocol(
        protocol_id="P04-AUTOREGRESSIVE-FEEDBACK",
        title="Autoregressive prefix and trajectory counterfactuals",
        implementation_state="implemented-mixed",
        experiment_ids=("C05", "M02"),
        purpose="Measure how an alternative prefix changes the next conditional distribution.",
        limitation="A one-step counterfactual does not by itself explain long-form behaviour.",
    ),
    ReplicationProtocol(
        protocol_id="P05-CAUSAL-CONTROLS",
        title="Probe, ablation, steering and patching controls",
        implementation_state="implemented-mixed",
        experiment_ids=("C07", "C08", "C11", "C12", "M03"),
        purpose="Separate decodability, manipulability, necessity, sufficiency and faithfulness.",
        limitation="Passing controls strengthens a scoped claim; it does not establish uniqueness.",
    ),
    ReplicationProtocol(
        protocol_id="P06-SAFETY-ROUTING-PROXY",
        title="Harmless recognition-policy-action proxy",
        implementation_state="implemented-transparent",
        experiment_ids=("C09",),
        purpose="Demonstrate that recognition, policy state and final action can be dissociated.",
        limitation="The harmless proxy contains no reusable jailbreak payload and is not a Claude circuit map.",
    ),
    ReplicationProtocol(
        protocol_id="P07-DICTIONARY-LEARNING",
        title="SAE, transcoder and crosscoder reproduction",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Train sparse dictionaries, evaluate reconstruction and test feature interventions.",
        limitation="Exact runs require original checkpoints, activation distributions and hyperparameters.",
    ),
    ReplicationProtocol(
        protocol_id="P08-MODEL-DIFFING",
        title="Checkpoint and model-diffing reproduction",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Compare matched public checkpoints with cross-model or stage-wise representations.",
        limitation="Matched original checkpoints and training-stage data are often unavailable.",
    ),
    ReplicationProtocol(
        protocol_id="P09-CIRCUIT-TRACING",
        title="Transcoder attribution-graph reproduction",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Train replacement models and validate prompt-specific attribution paths causally.",
        limitation="Exact Anthropic graphs depend on proprietary models, dictionaries and tooling.",
    ),
    ReplicationProtocol(
        protocol_id="P10-ACTIVATION-INTERFACES",
        title="Activation verbalization and reconstruction",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Evaluate natural-language or learned interfaces to internal activations.",
        limitation="Original activation-oracle, NLA and internal-state training assets are not fully public.",
    ),
    ReplicationProtocol(
        protocol_id="P11-MANIFOLD-GEOMETRY",
        title="Continuous manifold and counting geometry",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Reproduce continuous latent geometry, local coordinates and attention-mediated updates.",
        limitation="The original model, activation cache and task-specific analysis assets are unavailable.",
    ),
    ReplicationProtocol(
        protocol_id="P12-INTROSPECTION-WORKSPACE",
        title="Introspection and verbalizable workspace tests",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Test injected-state reporting, controllability, reuse and causal readout in open models.",
        limitation="Claims must not be upgraded to consciousness claims; original model assets are private.",
    ),
    ReplicationProtocol(
        protocol_id="P13-AUDITING",
        title="Automated interpretability and alignment auditing",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Evaluate agents and interpretability tools against seeded, auditable test cases.",
        limitation="Original audit environments, model access and some task generators are not public.",
    ),
    ReplicationProtocol(
        protocol_id="P14-ARCHITECTURE",
        title="Architecture and activation-function comparisons",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Train matched small models and compare interpretability and behavioural metrics.",
        limitation="Comparable conclusions require controlled training budgets and multiple seeds.",
    ),
    ReplicationProtocol(
        protocol_id="P15-LEARNING-DYNAMICS",
        title="Training dynamics, phase changes and double descent",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Track circuit formation, memorization, superposition and generalization through training.",
        limitation="Checkpoint-dense training and repeated seeds are required for stable conclusions.",
    ),
    ReplicationProtocol(
        protocol_id="P16-EDUCATION-INFRA",
        title="Educational or infrastructure reference",
        implementation_state="planned",
        experiment_ids=(),
        purpose="Document tools, exercises, videos and historical context rather than reproduce a result.",
        limitation="These sources are supporting material, not a single empirical claim.",
    ),
    ReplicationProtocol(
        protocol_id="P17-PERSONA-SAFETY",
        title="Persona, role and policy-routing tests",
        implementation_state="planned",
        experiment_ids=("C09",),
        purpose="Separate role representation, knowledge access, policy state and emitted behaviour.",
        limitation="A proxy cannot recover the original model's persona features or safety circuits.",
    ),
)

PROTOCOLS_BY_ID = {protocol.protocol_id: protocol for protocol in PROTOCOLS}

THEME_PROTOCOLS: Mapping[str, tuple[str, ...]] = {
    "global_weights": ("P02-SUPERPOSITION-WEIGHTS", "P05-CAUSAL-CONTROLS"),
    "reasoning": ("P04-AUTOREGRESSIVE-FEEDBACK", "P12-INTROSPECTION-WORKSPACE"),
    "representations": ("P02-SUPERPOSITION-WEIGHTS", "P07-DICTIONARY-LEARNING"),
    "activation_interfaces": ("P10-ACTIVATION-INTERFACES",),
    "attention": ("P03-ATTENTION-OPEN-MODEL", "P05-CAUSAL-CONTROLS"),
    "safety": ("P06-SAFETY-ROUTING-PROXY", "P17-PERSONA-SAFETY"),
    "introspection": ("P12-INTROSPECTION-WORKSPACE",),
    "geometry": ("P11-MANIFOLD-GEOMETRY",),
    "in_context_learning": ("P03-ATTENTION-OPEN-MODEL", "P15-LEARNING-DYNAMICS"),
    "persona": ("P17-PERSONA-SAFETY",),
    "methods": ("P05-CAUSAL-CONTROLS", "P09-CIRCUIT-TRACING"),
    "circuits": ("P01-CIRCUIT-ALGEBRA", "P03-ATTENTION-OPEN-MODEL"),
    "auditing": ("P13-AUDITING",),
    "case_studies": ("P09-CIRCUIT-TRACING", "P05-CAUSAL-CONTROLS"),
    "model_diffing": ("P08-MODEL-DIFFING", "P07-DICTIONARY-LEARNING"),
    "dictionary_learning": ("P07-DICTIONARY-LEARNING",),
    "evaluation": ("P07-DICTIONARY-LEARNING", "P05-CAUSAL-CONTROLS"),
    "methodology": ("P05-CAUSAL-CONTROLS",),
    "strategy": ("P13-AUDITING",),
    "learning_dynamics": ("P15-LEARNING-DYNAMICS", "P02-SUPERPOSITION-WEIGHTS"),
    "architecture": ("P14-ARCHITECTURE",),
    "foundations": ("P01-CIRCUIT-ALGEBRA",),
    "education": ("P16-EDUCATION-INFRA",),
    "visualization": ("P16-EDUCATION-INFRA",),
    "infrastructure": ("P16-EDUCATION-INFRA",),
}

CURRENT_STAGE_BY_THEME: Mapping[str, str] = {
    "global_weights": "transparent-proxy",
    "reasoning": "planned",
    "representations": "transparent-proxy",
    "activation_interfaces": "planned",
    "attention": "open-model-partial",
    "safety": "transparent-proxy",
    "introspection": "planned",
    "geometry": "planned",
    "in_context_learning": "open-model-partial",
    "persona": "planned",
    "methods": "transparent-proxy",
    "circuits": "transparent-proxy",
    "auditing": "planned",
    "case_studies": "planned",
    "model_diffing": "planned",
    "dictionary_learning": "planned",
    "evaluation": "planned",
    "methodology": "reference-synthesis",
    "strategy": "reference-synthesis",
    "learning_dynamics": "transparent-proxy",
    "architecture": "planned",
    "foundations": "transparent-proxy",
    "education": "reference-synthesis",
    "visualization": "reference-synthesis",
    "infrastructure": "reference-synthesis",
}

PARTIAL_PUBLIC_URLS = frozenset(
    {
        "https://transformer-circuits.pub/2026/interference_effectiveness_helpfulness/index.html",
        "https://transformer-circuits.pub/2025/faithfulness-toy-model/index.html",
        "https://transformer-circuits.pub/2025/interference-weights/index.html",
        "https://transformer-circuits.pub/2025/bulk-update/index.html",
        "https://transformer-circuits.pub/2023/monosemantic-features/index.html",
        "https://transformer-circuits.pub/2023/privileged-basis/index.html",
        "https://transformer-circuits.pub/2023/toy-double-descent/index.html",
        "https://transformer-circuits.pub/2022/toy_model/index.html",
        "https://transformer-circuits.pub/2022/solu/index.html",
        "https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html",
        "https://transformer-circuits.pub/2021/framework/index.html",
    }
)

BLOCKED_REASON = (
    "Exact reproduction requires at least one original model checkpoint, activation cache, "
    "learned dictionary, training distribution, internal interface or evaluation asset that "
    "is not available in the public source set."
)


def _source_id(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12].upper()
    return f"TC-{digest}"


def _resource_text() -> str:
    return resources.files("llm_theory_lab.data").joinpath(CATALOG_RESOURCE).read_text(
        encoding="utf-8"
    )


def load_source_rows(path: str | Path | None = None) -> list[dict[str, str]]:
    """Load the canonical source catalog from a path or installed package data."""

    if path is None:
        text = _resource_text()
        rows = csv.DictReader(text.splitlines())
        return [{key: str(value or "").strip() for key, value in row.items()} for row in rows]

    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [
            {key: str(value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def _exact_feasibility(row: Mapping[str, str]) -> tuple[str, str]:
    source_kind = row["status"]
    if source_kind in REFERENCE_SOURCE_KINDS:
        return "not-applicable", ""
    if row["url"] in PARTIAL_PUBLIC_URLS:
        return "partial-public", ""
    return "blocked-proprietary-assets", BLOCKED_REASON


def _current_stage(row: Mapping[str, str]) -> str:
    if row["status"] in REFERENCE_SOURCE_KINDS:
        return "reference-synthesis"
    return CURRENT_STAGE_BY_THEME[row["theme"]]


def build_replication_catalog(
    path: str | Path | None = None,
) -> list[ReplicationRecord]:
    """Build one explicit replication record for every source row."""

    records: list[ReplicationRecord] = []
    for row in load_source_rows(path):
        protocol_ids = THEME_PROTOCOLS.get(row["theme"])
        if protocol_ids is None:
            raise ReplicationCatalogError(f"unmapped source theme: {row['theme']!r}")
        exact_feasibility, blocker = _exact_feasibility(row)
        experiment_ids = tuple(
            dict.fromkeys(
                experiment_id
                for protocol_id in protocol_ids
                for experiment_id in PROTOCOLS_BY_ID[protocol_id].experiment_ids
            )
        )
        next_step = (
            "Use as conceptual, educational or infrastructure context."
            if row["status"] in REFERENCE_SOURCE_KINDS
            else (
                "Run and review the listed protocol, then add matched open-model controls."
                if _current_stage(row) in {"transparent-proxy", "open-model-partial"}
                else "Implement the listed protocol with pinned public assets and preregistered controls."
            )
        )
        records.append(
            ReplicationRecord(
                source_id=_source_id(row["url"]),
                period=row["period"],
                title=row["title"],
                url=row["url"],
                source_kind=row["status"],
                theme=row["theme"],
                role=row["role"],
                exact_feasibility=exact_feasibility,
                current_stage=_current_stage(row),
                protocol_ids=protocol_ids,
                available_experiment_ids=experiment_ids,
                blocker=blocker,
                next_step=next_step,
            )
        )
    return records


def validate_replication_catalog(
    records: Sequence[ReplicationRecord],
    *,
    expected_count: int = EXPECTED_SOURCE_COUNT,
) -> None:
    """Reject missing, duplicated or overclaimed replication records."""

    if len(records) != expected_count:
        raise ReplicationCatalogError(
            f"expected {expected_count} source records, found {len(records)}"
        )

    source_ids = [record.source_id for record in records]
    urls = [record.url for record in records]
    if len(source_ids) != len(set(source_ids)):
        raise ReplicationCatalogError("source IDs are not unique")
    if len(urls) != len(set(urls)):
        raise ReplicationCatalogError("source URLs are not unique")

    transparent_ids = {spec.experiment_id for spec in list_experiments()}
    known_experiments = transparent_ids | OPEN_MODEL_EXPERIMENT_IDS
    for record in records:
        if record.source_kind not in SOURCE_KINDS:
            raise ReplicationCatalogError(
                f"{record.source_id}: unknown source kind {record.source_kind!r}"
            )
        if record.exact_feasibility not in EXACT_FEASIBILITY_VALUES:
            raise ReplicationCatalogError(
                f"{record.source_id}: invalid exact feasibility {record.exact_feasibility!r}"
            )
        if record.current_stage not in CURRENT_STAGE_VALUES:
            raise ReplicationCatalogError(
                f"{record.source_id}: invalid current stage {record.current_stage!r}"
            )
        if not record.protocol_ids:
            raise ReplicationCatalogError(f"{record.source_id}: no replication protocol")
        unknown_protocols = set(record.protocol_ids) - set(PROTOCOLS_BY_ID)
        if unknown_protocols:
            raise ReplicationCatalogError(
                f"{record.source_id}: unknown protocols {sorted(unknown_protocols)}"
            )
        unknown_experiments = set(record.available_experiment_ids) - known_experiments
        if unknown_experiments:
            raise ReplicationCatalogError(
                f"{record.source_id}: unknown experiments {sorted(unknown_experiments)}"
            )
        if record.exact_feasibility == "blocked-proprietary-assets" and not record.blocker:
            raise ReplicationCatalogError(f"{record.source_id}: blocked source lacks a reason")
        if record.source_kind in REFERENCE_SOURCE_KINDS:
            if record.exact_feasibility != "not-applicable":
                raise ReplicationCatalogError(
                    f"{record.source_id}: reference source cannot claim exact reproduction"
                )
            if record.current_stage != "reference-synthesis":
                raise ReplicationCatalogError(
                    f"{record.source_id}: reference source has an empirical current stage"
                )

    for protocol in PROTOCOLS:
        if protocol.implementation_state not in PROTOCOL_STATES:
            raise ReplicationCatalogError(
                f"{protocol.protocol_id}: invalid implementation state"
            )
        unknown_experiments = set(protocol.experiment_ids) - known_experiments
        if unknown_experiments:
            raise ReplicationCatalogError(
                f"{protocol.protocol_id}: unknown experiments {sorted(unknown_experiments)}"
            )


def replication_summary(
    records: Iterable[ReplicationRecord],
) -> dict[str, dict[str, int]]:
    record_list = list(records)
    return {
        "current_stage": dict(
            sorted(Counter(record.current_stage for record in record_list).items())
        ),
        "exact_feasibility": dict(
            sorted(Counter(record.exact_feasibility for record in record_list).items())
        ),
        "source_kind": dict(
            sorted(Counter(record.source_kind for record in record_list).items())
        ),
        "theme": dict(sorted(Counter(record.theme for record in record_list).items())),
    }


def find_replication_records(
    query: str,
    records: Sequence[ReplicationRecord] | None = None,
) -> list[ReplicationRecord]:
    normalized = query.strip().casefold()
    if not normalized:
        raise ReplicationCatalogError("query must not be empty")
    candidates = list(records) if records is not None else build_replication_catalog()
    return [
        record
        for record in candidates
        if normalized
        in " ".join(
            (
                record.source_id,
                record.period,
                record.title,
                record.url,
                record.theme,
                record.source_kind,
            )
        ).casefold()
    ]


def write_replication_matrix(
    path: str | Path,
    records: Sequence[ReplicationRecord] | None = None,
) -> None:
    record_list = list(records) if records is not None else build_replication_catalog()
    validate_replication_catalog(record_list, expected_count=len(record_list))
    summary = replication_summary(record_list)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Transformer Circuits replication matrix",
        "",
        "> Generated from the packaged 56-source catalog. "
        "A proxy or partial open-model protocol is not an exact reproduction.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "| ID | Period | Source | Theme | Exact feasibility | Current stage | Protocols | Experiments |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for record in record_list:
        protocols = "<br>".join(f"`{item}`" for item in record.protocol_ids)
        experiments = (
            "<br>".join(f"`{item}`" for item in record.available_experiment_ids)
            or "—"
        )
        title = record.title.replace("|", "\\|")
        lines.append(
            f"| `{record.source_id}` | {record.period} | "
            f"[{title}]({record.url}) | `{record.theme}` | "
            f"`{record.exact_feasibility}` | `{record.current_stage}` | "
            f"{protocols} | {experiments} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `blocked-proprietary-assets` means exact reproduction is not currently possible "
            "from the public asset set; it does not mean the scientific result is false.",
            "- `transparent-proxy` means a scoped mathematical or structural analogue exists.",
            "- `open-model-partial` means at least one public-model observation or intervention "
            "is implemented, but the original model/result is not reproduced exactly.",
            "- `planned` is an explicit implementation gap, not a silent omission.",
            "",
        ]
    )
    target.write_text("\n".join(lines), encoding="utf-8")
