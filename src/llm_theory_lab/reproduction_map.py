"""Load, validate, filter, and render the public reproduction coverage map."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from importlib import resources
from pathlib import Path
from typing import Any

REGISTRY_SCHEMA_VERSION = "1.0.0"
REGISTRY_KIND = "transformer-circuits-reproduction-map"
REGISTRY_REPOSITORY_PATH = "reproductions/transformer_circuits_v1.json"
CATALOG_REPOSITORY_PATH = "sources/transformer_circuits_catalog.csv"
REGISTRY_PACKAGE_NAME = "transformer_circuits_reproduction_v1.json"
CATALOG_PACKAGE_NAME = "transformer_circuits_catalog.csv"

COVERAGE_STATUSES = {
    "implemented-complete",
    "implemented-partial",
    "planned",
    "reference-only",
}
MODES = {
    "exact-reproduction",
    "open-model-analogue",
    "transparent-proxy",
    "reference",
}
PROTOCOL_KINDS = MODES - {"reference"}
PROTOCOL_MATURITY = {"validated", "prototype", "planned"}
FEASIBILITY = {
    "public-protocol-likely-feasible",
    "blocked-by-proprietary-or-unpublished-assets",
    "source-specific-audit-required",
    "not-applicable",
}
TARGET_MODES = {
    "exact-or-close-reproduction",
    "open-model-analogue",
    "source-audit-then-decide",
    "reference-only",
}
PRIORITIES = {"P0", "P1", "P2", "P3"}
COMPUTE_TIERS = {"none", "cpu", "single-gpu", "multi-gpu", "unknown"}


class ReproductionMapError(ValueError):
    """Raised when the reproduction map violates its semantic contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReproductionMapError(message)


def _read_repository_or_package(
    root: Path,
    *,
    repository_path: str,
    package_name: str,
) -> bytes:
    candidate = root / repository_path
    if candidate.is_file():
        return candidate.read_bytes()
    package_file = resources.files("llm_theory_lab.data").joinpath(package_name)
    try:
        return package_file.read_bytes()
    except FileNotFoundError as exc:
        raise ReproductionMapError(
            f"missing repository and packaged resource: {repository_path}"
        ) from exc


def load_reproduction_map(root: str | Path | None = None) -> dict[str, Any]:
    """Load the canonical registry from a checkout or installed package."""

    repository_root = Path(root) if root is not None else Path.cwd()
    content = _read_repository_or_package(
        repository_root,
        repository_path=REGISTRY_REPOSITORY_PATH,
        package_name=REGISTRY_PACKAGE_NAME,
    )
    payload = json.loads(content.decode("utf-8"))
    _require(isinstance(payload, dict), "reproduction registry must be a JSON object")
    return payload


def load_catalog_bytes(root: str | Path | None = None) -> bytes:
    """Load the source catalog from a checkout or installed package."""

    repository_root = Path(root) if root is not None else Path.cwd()
    return _read_repository_or_package(
        repository_root,
        repository_path=CATALOG_REPOSITORY_PATH,
        package_name=CATALOG_PACKAGE_NAME,
    )


def load_catalog_rows(content: bytes) -> list[dict[str, str]]:
    """Parse the canonical CSV catalog while preserving row order."""

    text = content.decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    expected_fields = ["period", "title", "url", "status", "theme", "role"]
    _require(reader.fieldnames == expected_fields, "source catalog columns changed unexpectedly")
    rows = [{key: str(value) for key, value in row.items()} for row in reader]
    _require(rows, "source catalog is empty")
    return rows


def _source_id(url: str) -> str:
    return "TC-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:10].upper()


def _strings(value: Any, name: str, *, allow_empty: bool = False) -> list[str]:
    _require(isinstance(value, list), f"{name} must be a list")
    result = []
    for index, item in enumerate(value):
        _require(
            isinstance(item, str) and bool(item.strip()),
            f"{name}[{index}] must be a non-empty string",
        )
        result.append(item)
    _require(len(result) == len(set(result)), f"{name} contains duplicates")
    if not allow_empty:
        _require(result, f"{name} must not be empty")
    return result


def _validate_protocols(protocols: Any) -> dict[str, Mapping[str, Any]]:
    _require(isinstance(protocols, Mapping) and protocols, "protocols must be a non-empty object")
    validated: dict[str, Mapping[str, Any]] = {}
    for protocol_id, raw in protocols.items():
        _require(
            isinstance(protocol_id, str)
            and len(protocol_id) == 3
            and protocol_id[0] in {"C", "M"}
            and protocol_id[1:].isdigit(),
            f"invalid protocol ID: {protocol_id!r}",
        )
        _require(isinstance(raw, Mapping), f"{protocol_id} must be an object")
        kind = raw.get("kind")
        maturity = raw.get("maturity")
        _require(kind in PROTOCOL_KINDS, f"{protocol_id}: invalid kind")
        _require(maturity in PROTOCOL_MATURITY, f"{protocol_id}: invalid maturity")
        _require(
            isinstance(raw.get("runner"), str) and bool(raw["runner"].strip()),
            f"{protocol_id}: runner missing",
        )
        _require(
            isinstance(raw.get("evidence_ceiling"), str)
            and bool(raw["evidence_ceiling"].strip()),
            f"{protocol_id}: evidence ceiling missing",
        )
        _require(isinstance(raw.get("default_ci"), bool), f"{protocol_id}: default_ci invalid")
        _strings(raw.get("requires"), f"{protocol_id}.requires")
        validated[protocol_id] = raw

    from .registry import list_experiments

    experiment_specs = {spec.experiment_id: spec for spec in list_experiments()}
    for experiment_id in experiment_specs:
        _require(experiment_id in validated, f"registered experiment missing protocol: {experiment_id}")
        protocol = validated[experiment_id]
        _require(
            protocol.get("kind") == "transparent-proxy",
            f"{experiment_id}: transparent experiment must be classified as a proxy",
        )
        _require(
            protocol.get("maturity") == "validated",
            f"{experiment_id}: CI experiment must be validated",
        )
        _require(
            protocol.get("default_ci") is True,
            f"{experiment_id}: validated transparent experiment must run in CI",
        )
    return validated


def validate_reproduction_map(
    registry: Mapping[str, Any],
    *,
    catalog_content: bytes | None = None,
) -> None:
    """Validate structure, catalog coverage, and experiment/source relationships."""

    _require(
        registry.get("schema_version") == REGISTRY_SCHEMA_VERSION,
        "unsupported reproduction registry schema",
    )
    _require(registry.get("registry_kind") == REGISTRY_KIND, "unexpected registry kind")
    _require(
        isinstance(registry.get("snapshot_date"), str) and bool(registry["snapshot_date"]),
        "snapshot_date missing",
    )
    _require(
        registry.get("catalog_path") == CATALOG_REPOSITORY_PATH,
        "catalog_path must point to the canonical catalog",
    )
    catalog_sha256 = registry.get("catalog_sha256")
    _require(
        isinstance(catalog_sha256, str)
        and len(catalog_sha256) == 64
        and all(character in "0123456789abcdef" for character in catalog_sha256),
        "catalog_sha256 is invalid",
    )
    _require(
        isinstance(registry.get("audit_note"), str) and bool(registry["audit_note"].strip()),
        "audit_note missing",
    )

    coverage_definitions = registry.get("coverage_status_definitions")
    _require(isinstance(coverage_definitions, Mapping), "coverage definitions missing")
    _require(
        set(coverage_definitions) == COVERAGE_STATUSES,
        "coverage definitions do not match allowed statuses",
    )
    mode_definitions = registry.get("mode_definitions")
    _require(isinstance(mode_definitions, Mapping), "mode definitions missing")
    _require(set(mode_definitions) == MODES, "mode definitions do not match allowed modes")

    protocols = _validate_protocols(registry.get("protocols"))
    raw_sources = registry.get("sources")
    _require(isinstance(raw_sources, list) and raw_sources, "sources must be a non-empty list")

    if catalog_content is None:
        catalog_content = load_catalog_bytes()
    actual_catalog_sha = hashlib.sha256(catalog_content).hexdigest()
    _require(
        catalog_sha256 == actual_catalog_sha,
        "catalog_sha256 does not match the canonical source catalog",
    )
    catalog_rows = load_catalog_rows(catalog_content)
    _require(
        len(raw_sources) == len(catalog_rows),
        "reproduction map must contain exactly one row per catalog source",
    )

    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    sources_by_url: dict[str, Mapping[str, Any]] = {}

    required_fields = {
        "source_id",
        "period",
        "title",
        "url",
        "source_type",
        "theme",
        "catalog_role",
        "coverage_status",
        "current_modes",
        "protocol_ids",
        "exact_reproduction_feasibility",
        "target_mode",
        "priority",
        "compute_tier",
        "blockers",
        "acceptance_criteria",
        "next_step",
    }
    for index, (raw_source, catalog_row) in enumerate(
        zip(raw_sources, catalog_rows, strict=True)
    ):
        _require(isinstance(raw_source, Mapping), f"source {index} must be an object")
        source = raw_source
        missing = required_fields - set(source)
        extra = set(source) - required_fields
        _require(not missing, f"source {index} missing fields: {sorted(missing)}")
        _require(not extra, f"source {index} has unknown fields: {sorted(extra)}")

        url = source.get("url")
        _require(isinstance(url, str) and url.startswith("https://"), f"source {index}: bad URL")
        source_id = source.get("source_id")
        _require(source_id == _source_id(url), f"{url}: unstable or invalid source_id")
        _require(source_id not in seen_ids, f"duplicate source_id: {source_id}")
        _require(url not in seen_urls, f"duplicate source URL: {url}")
        seen_ids.add(str(source_id))
        seen_urls.add(url)
        sources_by_url[url] = source

        for registry_key, catalog_key in (
            ("period", "period"),
            ("title", "title"),
            ("url", "url"),
            ("source_type", "status"),
            ("theme", "theme"),
            ("catalog_role", "role"),
        ):
            _require(
                source.get(registry_key) == catalog_row[catalog_key],
                f"{url}: {registry_key} drifted from source catalog",
            )

        status = source.get("coverage_status")
        _require(status in COVERAGE_STATUSES, f"{url}: invalid coverage_status")
        modes = _strings(source.get("current_modes"), f"{url}.current_modes", allow_empty=True)
        _require(set(modes) <= MODES, f"{url}: invalid current mode")
        protocol_ids = _strings(
            source.get("protocol_ids"),
            f"{url}.protocol_ids",
            allow_empty=True,
        )
        unknown_protocols = set(protocol_ids) - set(protocols)
        _require(not unknown_protocols, f"{url}: unknown protocols {sorted(unknown_protocols)}")

        expected_modes: list[str] = []
        for protocol_id in protocol_ids:
            kind = str(protocols[protocol_id]["kind"])
            if kind not in expected_modes:
                expected_modes.append(kind)
        if status == "reference-only":
            _require(not protocol_ids, f"{url}: reference-only source cannot claim a protocol")
            expected_modes = ["reference"]
        _require(
            modes == expected_modes,
            f"{url}: current_modes must be derived from protocol kinds",
        )
        if status in {"implemented-complete", "implemented-partial"}:
            _require(protocol_ids, f"{url}: implemented source lacks a protocol")
        if status == "planned":
            _require(not protocol_ids, f"{url}: planned source already lists a protocol")

        feasibility = source.get("exact_reproduction_feasibility")
        _require(feasibility in FEASIBILITY, f"{url}: invalid feasibility")
        target = source.get("target_mode")
        _require(target in TARGET_MODES, f"{url}: invalid target mode")
        _require(source.get("priority") in PRIORITIES, f"{url}: invalid priority")
        _require(source.get("compute_tier") in COMPUTE_TIERS, f"{url}: invalid compute tier")
        _strings(source.get("blockers"), f"{url}.blockers", allow_empty=True)
        _require(
            isinstance(source.get("acceptance_criteria"), str)
            and bool(source["acceptance_criteria"].strip()),
            f"{url}: acceptance criteria missing",
        )
        _require(
            isinstance(source.get("next_step"), str) and bool(source["next_step"].strip()),
            f"{url}: next_step missing",
        )

        if feasibility == "not-applicable":
            _require(status == "reference-only", f"{url}: not-applicable must be reference-only")
            _require(target == "reference-only", f"{url}: reference item has wrong target")
            _require(source.get("compute_tier") == "none", f"{url}: reference item needs no compute")
        if feasibility == "blocked-by-proprietary-or-unpublished-assets":
            _require(
                target == "open-model-analogue",
                f"{url}: blocked exact result must target an open-model analogue",
            )
            _require(source.get("blockers"), f"{url}: blocked result must explain blockers")
        if feasibility == "public-protocol-likely-feasible":
            _require(
                target == "exact-or-close-reproduction",
                f"{url}: publicly feasible result has wrong target",
            )
        if feasibility == "source-specific-audit-required":
            _require(
                target == "source-audit-then-decide",
                f"{url}: unaudited source has wrong target",
            )

    from .registry import list_experiments

    for spec in list_experiments():
        for source_url in spec.source_urls:
            _require(
                source_url in sources_by_url,
                f"{spec.experiment_id}: source is absent from reproduction map: {source_url}",
            )
            source = sources_by_url[source_url]
            _require(
                spec.experiment_id in source["protocol_ids"],
                f"{spec.experiment_id}: source does not link back to the experiment",
            )
            _require(
                "transparent-proxy" in source["current_modes"],
                f"{spec.experiment_id}: source must label the current implementation as a proxy",
            )


def summarize_reproduction_map(registry: Mapping[str, Any]) -> dict[str, dict[str, int] | int]:
    """Return deterministic counts for CLI and documentation."""

    sources = registry.get("sources", [])
    _require(isinstance(sources, Sequence), "sources missing")
    return {
        "total_sources": len(sources),
        "coverage_status": dict(
            sorted(Counter(str(source["coverage_status"]) for source in sources).items())
        ),
        "current_modes": dict(
            sorted(
                Counter(
                    str(mode)
                    for source in sources
                    for mode in source.get("current_modes", [])
                ).items()
            )
        ),
        "exact_reproduction_feasibility": dict(
            sorted(
                Counter(
                    str(source["exact_reproduction_feasibility"]) for source in sources
                ).items()
            )
        ),
        "priority": dict(
            sorted(Counter(str(source["priority"]) for source in sources).items())
        ),
    }


def select_sources(
    registry: Mapping[str, Any],
    *,
    coverage_status: str | None = None,
    mode: str | None = None,
    theme: str | None = None,
    priority: str | None = None,
) -> list[Mapping[str, Any]]:
    """Filter sources without changing catalog order."""

    if coverage_status is not None:
        _require(coverage_status in COVERAGE_STATUSES, "unknown coverage status")
    if mode is not None:
        _require(mode in MODES, "unknown reproduction mode")
    if priority is not None:
        _require(priority in PRIORITIES, "unknown priority")

    selected: list[Mapping[str, Any]] = []
    for source in registry["sources"]:
        if coverage_status is not None and source["coverage_status"] != coverage_status:
            continue
        if mode is not None and mode not in source["current_modes"]:
            continue
        if theme is not None and source["theme"] != theme:
            continue
        if priority is not None and source["priority"] != priority:
            continue
        selected.append(source)
    return selected


def render_reproduction_map(registry: Mapping[str, Any]) -> str:
    """Render a deterministic human-readable coverage matrix."""

    summary = summarize_reproduction_map(registry)
    lines = [
        "# Transformer Circuits 公开结果复现地图",
        "",
        "> 本页由机器可读复现注册表生成。`implemented-partial` 不等于原论文完整复现；",
        "> `open-model-analogue` 也不等于在 Claude 私有权重上复现原始数值。",
        "",
        f"快照日期：`{registry['snapshot_date']}`；来源总数：**{summary['total_sources']}**。",
        "",
        "## 当前覆盖",
        "",
        "| 覆盖状态 | 数量 |",
        "|---|---:|",
    ]
    for status, count in summary["coverage_status"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## 精确复现可行性审计",
            "",
            "| 可行性 | 数量 |",
            "|---|---:|",
        ]
    )
    for status, count in summary["exact_reproduction_feasibility"].items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## 全部来源",
            "",
            "| ID | 日期 | 来源 | 主题 | 当前覆盖 | 当前模式 | 协议 | 精确复现可行性 | 优先级 | 计算 |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for source in registry["sources"]:
        protocols = ", ".join(f"`{item}`" for item in source["protocol_ids"]) or "—"
        modes = ", ".join(f"`{item}`" for item in source["current_modes"]) or "—"
        title = str(source["title"]).replace("|", "\\|")
        lines.append(
            f"| `{source['source_id']}` | {source['period']} | "
            f"[{title}]({source['url']}) | `{source['theme']}` | "
            f"`{source['coverage_status']}` | {modes} | {protocols} | "
            f"`{source['exact_reproduction_feasibility']}` | `{source['priority']}` | "
            f"`{source['compute_tier']}` |"
        )

    lines.extend(
        [
            "",
            "## 怎样使用这张表",
            "",
            "1. 先看 `coverage_status`：仓库是否已经有协议，以及是否只覆盖部分结果；",
            "2. 再看 `current_modes`：当前代码是数学/透明代理，还是开放模型类比；",
            "3. 查看 `exact_reproduction_feasibility`：原始模型、数据和中间资产是否足够公开；",
            "4. 只有满足该来源的 `acceptance_criteria`，才能提高覆盖状态；",
            "5. 所有状态升级都必须附带 evidence ledger、固定 revision、结果哈希与失败记录。",
            "",
            "## 状态语义",
            "",
        ]
    )
    for status, description in registry["coverage_status_definitions"].items():
        lines.append(f"- **`{status}`**：{description}")
    lines.append("")
    for mode, description in registry["mode_definitions"].items():
        lines.append(f"- **`{mode}`**：{description}")

    lines.extend(
        [
            "",
            "## 机器可读入口",
            "",
            "```bash",
            "llm-theory-lab reproduction-map",
            "llm-theory-lab reproduction-map --status planned --priority P0",
            "llm-theory-lab reproduction-map --mode open-model-analogue --json",
            "llm-theory-lab validate-reproduction-map",
            "```",
            "",
            "规范文件：",
            "",
            "- `reproductions/transformer_circuits_v1.json`",
            "- `schemas/reproduction-registry-v1.schema.json`",
            "- `sources/transformer_circuits_catalog.csv`",
            "",
        ]
    )
    return "\n".join(lines)
