"""Build and validate versioned run-evidence ledgers."""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .evidence_core import (
    ALLOWED_STATUSES,
    LEDGER_SCHEMA_VERSION,
    EvidenceValidationError,
    _is_sha256,
    _package_version,
    _require,
    _utc_now,
    canonical_result,
    canonicalize,
    runner_descriptor,
    sha256_value,
)
from .registry import ExperimentSpec, list_experiments
from .result import ExperimentResult


def build_record(
    spec: ExperimentSpec,
    result: ExperimentResult,
    *,
    code_revision: str,
    artifact_path: str,
) -> dict[str, Any]:
    normalized_result = canonical_result(result)
    dataset = runner_descriptor(spec)
    result_digest = sha256_value(normalized_result)
    record: dict[str, Any] = {
        "claim_id": spec.claim_id,
        "claim_revision": spec.claim_revision,
        "experiment_id": spec.experiment_id,
        "claim": spec.theory_claim,
        "title": spec.title,
        "status": result.status,
        "evidence_level": result.evidence_level,
        "model_revision": spec.model_revision,
        "reproduction_status": spec.reproduction_status,
        "dataset": dataset,
        "dataset_sha256": sha256_value(dataset),
        "code_revision": code_revision,
        "source_urls": list(spec.source_urls),
        "effect_size": normalized_result.get("metrics", {}),
        "uncertainty": {
            "kind": "not-estimated",
            "reason": (
                "Canonical transparent runs use fixed inputs or seeds; no population "
                "confidence interval is inferred from a single construction."
            ),
        },
        "preregistered_checks": normalized_result.get("checks", []),
        "deviations": [],
        "scope_limit": spec.does_not_show,
        "lesson_path": spec.lesson_path,
        "lab_path": spec.lab_path,
        "result_sha256": result_digest,
        "artifacts": [
            {
                "path": artifact_path,
                "selector": spec.experiment_id,
                "sha256": result_digest,
            }
        ],
    }
    record["record_id"] = sha256_value(
        {
            "claim_id": record["claim_id"],
            "claim_revision": record["claim_revision"],
            "experiment_id": record["experiment_id"],
            "model_revision": record["model_revision"],
            "dataset_sha256": record["dataset_sha256"],
            "code_revision": record["code_revision"],
            "result_sha256": record["result_sha256"],
        }
    )
    return canonicalize(record)


def build_ledger(
    results: Sequence[ExperimentResult],
    *,
    code_revision: str,
    artifact_path: str = "canonical-results.json",
) -> dict[str, Any]:
    specs = {spec.experiment_id: spec for spec in list_experiments()}
    records: list[dict[str, Any]] = []
    for result in results:
        try:
            spec = specs[result.experiment_id]
        except KeyError as exc:
            raise EvidenceValidationError(
                f"result references unknown experiment {result.experiment_id!r}"
            ) from exc
        records.append(
            build_record(
                spec,
                result,
                code_revision=code_revision,
                artifact_path=artifact_path,
            )
        )

    ledger: dict[str, Any] = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "ledger_kind": "run-evidence",
        "generated_by": f"llm-theory-lab/{_package_version()}",
        "generated_at": _utc_now(),
        "code_revision": code_revision,
        "status_counts": dict(sorted(Counter(record["status"] for record in records).items())),
        "records": records,
    }
    ledger["ledger_sha256"] = sha256_value(
        {key: value for key, value in ledger.items() if key != "ledger_sha256"}
    )
    return canonicalize(ledger)


_REQUIRED_RECORD_FIELDS = {
    "record_id",
    "claim_id",
    "claim_revision",
    "experiment_id",
    "claim",
    "title",
    "status",
    "evidence_level",
    "model_revision",
    "reproduction_status",
    "dataset",
    "dataset_sha256",
    "code_revision",
    "source_urls",
    "effect_size",
    "uncertainty",
    "preregistered_checks",
    "deviations",
    "scope_limit",
    "lesson_path",
    "lab_path",
    "result_sha256",
    "artifacts",
}


def _record_identity(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "claim_id": record.get("claim_id"),
        "claim_revision": record.get("claim_revision"),
        "experiment_id": record.get("experiment_id"),
        "model_revision": record.get("model_revision"),
        "dataset_sha256": record.get("dataset_sha256"),
        "code_revision": record.get("code_revision"),
        "result_sha256": record.get("result_sha256"),
    }


def validate_ledger(
    ledger: Mapping[str, Any],
    *,
    require_complete: bool = True,
    catalog_urls: set[str] | None = None,
) -> None:
    _require(ledger.get("schema_version") == LEDGER_SCHEMA_VERSION, "unsupported schema version")
    _require(ledger.get("ledger_kind") == "run-evidence", "unexpected ledger kind")
    _require(isinstance(ledger.get("generated_by"), str), "generated_by must be a string")
    _require(isinstance(ledger.get("generated_at"), str), "generated_at must be a string")
    _require(isinstance(ledger.get("code_revision"), str), "code_revision must be a string")
    _require(isinstance(ledger.get("records"), list), "records must be a list")
    _require(_is_sha256(ledger.get("ledger_sha256")), "ledger_sha256 is invalid")

    expected_ledger_digest = sha256_value(
        {key: value for key, value in ledger.items() if key != "ledger_sha256"}
    )
    _require(ledger["ledger_sha256"] == expected_ledger_digest, "ledger checksum mismatch")

    specs = {spec.experiment_id: spec for spec in list_experiments()}
    seen_records: set[str] = set()
    seen_experiments: set[str] = set()
    seen_claims: set[str] = set()
    status_counts: Counter[str] = Counter()

    for index, raw_record in enumerate(ledger["records"]):
        _require(isinstance(raw_record, Mapping), f"record {index} must be an object")
        record = raw_record
        missing_fields = _REQUIRED_RECORD_FIELDS - set(record)
        _require(not missing_fields, f"record {index} missing fields: {sorted(missing_fields)}")

        experiment_id = record.get("experiment_id")
        _require(
            isinstance(experiment_id, str),
            f"record {index} experiment_id must be a string",
        )
        _require(
            experiment_id in specs,
            f"record {index} has unknown experiment {experiment_id!r}",
        )
        spec = specs[str(experiment_id)]

        record_id = record.get("record_id")
        _require(_is_sha256(record_id), f"{experiment_id}: invalid record_id")
        _require(record_id not in seen_records, f"duplicate record_id: {record_id}")
        seen_records.add(str(record_id))
        _require(
            experiment_id not in seen_experiments,
            f"duplicate experiment record: {experiment_id}",
        )
        seen_experiments.add(str(experiment_id))

        claim_id = record.get("claim_id")
        _require(isinstance(claim_id, str), f"{experiment_id}: claim_id must be a string")
        _require(claim_id not in seen_claims, f"duplicate claim record: {claim_id}")
        seen_claims.add(str(claim_id))
        _require(claim_id == spec.claim_id, f"{experiment_id}: claim_id drift")
        _require(
            record.get("claim_revision") == spec.claim_revision,
            f"{experiment_id}: claim revision drift",
        )
        _require(record.get("claim") == spec.theory_claim, f"{experiment_id}: claim text drift")
        _require(record.get("title") == spec.title, f"{experiment_id}: title drift")
        _require(
            record.get("model_revision") == spec.model_revision,
            f"{experiment_id}: model revision drift",
        )
        _require(
            record.get("reproduction_status") == spec.reproduction_status,
            f"{experiment_id}: reproduction status drift",
        )
        _require(record.get("scope_limit") == spec.does_not_show, f"{experiment_id}: scope drift")
        _require(record.get("lesson_path") == spec.lesson_path, f"{experiment_id}: lesson drift")
        _require(record.get("lab_path") == spec.lab_path, f"{experiment_id}: lab drift")
        _require(
            record.get("code_revision") == ledger.get("code_revision"),
            f"{experiment_id}: code revision differs from ledger",
        )

        source_urls = record.get("source_urls")
        _require(isinstance(source_urls, list) and source_urls, f"{experiment_id}: sources missing")
        _require(
            all(isinstance(url, str) and url for url in source_urls),
            f"{experiment_id}: source URLs must be non-empty strings",
        )
        _require(
            len(source_urls) == len(set(source_urls)),
            f"{experiment_id}: duplicate source URLs",
        )
        _require(source_urls == list(spec.source_urls), f"{experiment_id}: source drift")
        if catalog_urls is not None:
            missing_sources = set(source_urls) - catalog_urls
            _require(
                not missing_sources,
                f"{experiment_id}: uncatalogued sources {sorted(missing_sources)}",
            )

        status = record.get("status")
        _require(status in ALLOWED_STATUSES, f"{experiment_id}: invalid status")
        status_counts[str(status)] += 1
        evidence_level = record.get("evidence_level")
        _require(
            isinstance(evidence_level, str)
            and evidence_level.startswith(("L0", "L1", "L2", "L3", "L4", "L5")),
            f"{experiment_id}: invalid evidence level",
        )

        dataset = record.get("dataset")
        _require(isinstance(dataset, Mapping), f"{experiment_id}: dataset must be an object")
        dataset_sha256 = record.get("dataset_sha256")
        _require(_is_sha256(dataset_sha256), f"{experiment_id}: invalid dataset hash")
        _require(
            dataset_sha256 == sha256_value(dataset),
            f"{experiment_id}: dataset checksum mismatch",
        )
        result_sha256 = record.get("result_sha256")
        _require(_is_sha256(result_sha256), f"{experiment_id}: invalid result hash")
        _require(
            record_id == sha256_value(_record_identity(record)),
            f"{experiment_id}: record_id checksum mismatch",
        )

        _require(
            isinstance(record.get("effect_size"), Mapping),
            f"{experiment_id}: effect_size must be an object",
        )
        uncertainty = record.get("uncertainty")
        _require(
            isinstance(uncertainty, Mapping)
            and bool(uncertainty.get("kind"))
            and bool(uncertainty.get("reason")),
            f"{experiment_id}: uncertainty is incomplete",
        )
        _require(
            isinstance(record.get("deviations"), list),
            f"{experiment_id}: deviations must be a list",
        )
        checks = record.get("preregistered_checks")
        _require(
            isinstance(checks, list),
            f"{experiment_id}: preregistered_checks must be a list",
        )
        artifacts = record.get("artifacts")
        _require(isinstance(artifacts, list) and artifacts, f"{experiment_id}: artifacts missing")
        for artifact_index, artifact in enumerate(artifacts):
            _require(
                isinstance(artifact, Mapping),
                f"{experiment_id}: artifact {artifact_index} must be an object",
            )
            _require(
                bool(artifact.get("path")) and bool(artifact.get("selector")),
                f"{experiment_id}: artifact {artifact_index} is incomplete",
            )
            _require(
                artifact.get("selector") == experiment_id,
                f"{experiment_id}: artifact selector mismatch",
            )
            _require(
                artifact.get("sha256") == result_sha256,
                f"{experiment_id}: artifact hash differs from result hash",
            )

        if status == "pass":
            _require(
                all(isinstance(check, Mapping) and check.get("passed") is True for check in checks),
                f"{experiment_id}: pass contains failed or malformed checks",
            )
        if status == "fail":
            _require(bool(checks), f"{experiment_id}: fail lacks checks")
            _require(
                any(
                    isinstance(check, Mapping) and check.get("passed") is False
                    for check in checks
                ),
                f"{experiment_id}: fail lacks a failed check",
            )

    if require_complete:
        _require(
            seen_experiments == set(specs),
            "ledger does not cover every registered experiment",
        )

    expected_counts = dict(sorted(status_counts.items()))
    _require(ledger.get("status_counts") == expected_counts, "status_counts do not match records")


def load_catalog_urls(path: str | Path) -> set[str]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        urls = {str(row.get("url", "")).strip() for row in rows}
    urls.discard("")
    return urls


def write_evidence_matrix(ledger: Mapping[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Evidence matrix",
        "",
        "> This file is generated from the machine-readable evidence ledger.",
        "",
        "| Claim | Experiment | Reproduction | Evidence | Status | Dataset | Result |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in ledger["records"]:
        lines.append(
            f"| `{record['claim_id']}@{record['claim_revision']}` | "
            f"`{record['experiment_id']}` | `{record['reproduction_status']}` | "
            f"`{record['evidence_level']}` | **{record['status']}** | "
            f"`{record['dataset_sha256'][7:19]}` | `{record['result_sha256'][7:19]}` |"
        )
    lines.extend(
        [
            "",
            (
                "A row records one scoped run. It does not upgrade transparent toy "
                "evidence to a claim about proprietary frontier-model internals."
            ),
        ]
    )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
