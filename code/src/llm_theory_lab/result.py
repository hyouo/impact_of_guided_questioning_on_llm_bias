"""Typed experiment results and deterministic JSON/Markdown reporting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


def _builtin(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _builtin(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_builtin(item) for item in value]
    return value


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    observed: Any
    expectation: str
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _builtin(asdict(self))


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    title: str
    theory_claim: str
    evidence_level: str
    status: str
    metrics: Mapping[str, Any] = field(default_factory=dict)
    checks: tuple[CheckResult, ...] = ()
    caveats: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        allowed = {"pass", "fail", "observational", "skipped"}
        if self.status not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        if self.status == "pass" and self.checks and not all(check.passed for check in self.checks):
            raise ValueError("a passing result cannot contain a failed check")
        if self.status == "fail" and self.checks and all(check.passed for check in self.checks):
            raise ValueError("a failing result must contain at least one failed check")

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "theory_claim": self.theory_claim,
            "evidence_level": self.evidence_level,
            "status": self.status,
            "metrics": _builtin(self.metrics),
            "checks": [check.to_dict() for check in self.checks],
            "caveats": list(self.caveats),
            "metadata": _builtin(self.metadata),
            "created_at": self.created_at,
        }


def checked_result(
    *,
    experiment_id: str,
    title: str,
    theory_claim: str,
    evidence_level: str,
    metrics: Mapping[str, Any],
    checks: Iterable[CheckResult],
    caveats: Iterable[str],
    metadata: Mapping[str, Any],
) -> ExperimentResult:
    checks_tuple = tuple(checks)
    return ExperimentResult(
        experiment_id=experiment_id,
        title=title,
        theory_claim=theory_claim,
        evidence_level=evidence_level,
        status="pass" if all(check.passed for check in checks_tuple) else "fail",
        metrics=metrics,
        checks=checks_tuple,
        caveats=tuple(caveats),
        metadata=metadata,
    )


def write_report(
    results: Iterable[ExperimentResult],
    *,
    json_path: str | Path,
    markdown_path: str | Path | None = None,
) -> None:
    result_list = list(results)
    json_target = Path(json_path)
    json_target.parent.mkdir(parents=True, exist_ok=True)
    json_target.write_text(
        json.dumps([result.to_dict() for result in result_list], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if markdown_path is None:
        return

    markdown_target = Path(markdown_path)
    markdown_target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LLM Theory Lab 实验报告",
        "",
        "| ID | 实验 | 证据层级 | 状态 |",
        "|---|---|---|---|",
    ]
    for result in result_list:
        lines.append(
            f"| `{result.experiment_id}` | {result.title} | {result.evidence_level} | **{result.status}** |"
        )

    for result in result_list:
        lines.extend(
            [
                "",
                f"## {result.experiment_id}｜{result.title}",
                "",
                f"**理论命题：** {result.theory_claim}",
                "",
                f"**状态：** `{result.status}`；**证据层级：** `{result.evidence_level}`",
                "",
                "### 检查",
                "",
            ]
        )
        if result.checks:
            lines.extend(["| 检查 | 通过 | 观测 | 预期 |", "|---|---:|---|---|"])
            for check in result.checks:
                observed = json.dumps(_builtin(check.observed), ensure_ascii=False)
                lines.append(
                    f"| {check.name} | {'是' if check.passed else '否'} | `{observed}` | {check.expectation} |"
                )
        else:
            lines.append("该实验是探索性观测，不使用二元通过/失败标准。")

        lines.extend(["", "### 指标", "", "```json"])
        lines.append(json.dumps(_builtin(result.metrics), ensure_ascii=False, indent=2))
        lines.extend(["```", "", "### 限制", ""])
        for caveat in result.caveats:
            lines.append(f"- {caveat}")

    markdown_target.write_text("\n".join(lines) + "\n", encoding="utf-8")
