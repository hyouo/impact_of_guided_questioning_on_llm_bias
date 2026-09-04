"""Verify reproduction bundle integrity and reviewed-baseline agreement."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from .evidence_core import (
    BUNDLE_SCHEMA_VERSION,
    LEDGER_SCHEMA_VERSION,
    EvidenceValidationError,
    _is_sha256,
    _require,
    canonicalize,
    sha256_file,
    sha256_value,
)
from .evidence_ledger import load_catalog_urls, validate_ledger
from .evidence_run import _claim_source_index, _manifest_without_digest


def _safe_bundle_path(root: Path, relative: Any) -> Path:
    _require(isinstance(relative, str) and relative, "bundle path must be a string")
    posix = PurePosixPath(relative)
    _require(not posix.is_absolute(), f"absolute bundle path is forbidden: {relative}")
    _require(".." not in posix.parts, f"parent traversal is forbidden: {relative}")
    return root.joinpath(*posix.parts)


def validate_bundle(path: str | Path, *, require_complete: bool = True) -> dict[str, Any]:
    root = Path(path)
    manifest_path = root / "manifest.json"
    _require(manifest_path.is_file(), "manifest.json is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require(manifest.get("schema_version") == BUNDLE_SCHEMA_VERSION, "unsupported bundle version")
    _require(
        manifest.get("bundle_kind") == "llm-theory-lab-reproduction",
        "unexpected bundle kind",
    )
    _require(isinstance(manifest.get("package_version"), str), "invalid package version")
    _require(isinstance(manifest.get("code_revision"), str), "invalid code revision")
    _require(isinstance(manifest.get("experiment_ids"), list), "invalid experiment IDs")
    _require(isinstance(manifest.get("status_counts"), Mapping), "invalid status counts")
    _require(isinstance(manifest.get("inputs"), list), "manifest inputs must be a list")
    _require(_is_sha256(manifest.get("manifest_sha256")), "invalid manifest checksum")
    _require(
        manifest["manifest_sha256"] == sha256_value(_manifest_without_digest(manifest)),
        "manifest checksum mismatch",
    )

    file_entries = manifest.get("files")
    _require(isinstance(file_entries, list), "manifest files must be a list")
    seen_paths: set[str] = set()
    entries_by_path: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(file_entries):
        _require(isinstance(entry, Mapping), f"manifest file {index} must be an object")
        relative = entry.get("path")
        _require(
            isinstance(relative, str) and relative,
            f"manifest file {index} path must be a string",
        )
        _require(relative not in seen_paths, f"duplicate manifest file: {relative}")
        seen_paths.add(relative)
        entries_by_path[relative] = entry
        file_path = _safe_bundle_path(root, relative)
        _require(file_path.is_file(), f"bundle file is missing: {relative}")
        _require(
            isinstance(entry.get("bytes"), int) and entry["bytes"] >= 0,
            f"invalid size metadata: {relative}",
        )
        _require(file_path.stat().st_size == entry["bytes"], f"size mismatch: {relative}")
        _require(_is_sha256(entry.get("sha256")), f"invalid checksum metadata: {relative}")
        _require(sha256_file(file_path) == entry["sha256"], f"checksum mismatch: {relative}")

    required_paths = {
        "results.json",
        "report.md",
        "canonical-results.json",
        "evidence-ledger.json",
        "evidence-matrix.md",
        "context/claim-sources.json",
        "context/evidence-ledger-v1.schema.json",
        "context/canonical-results-v1.json",
    }
    _require(
        required_paths <= seen_paths,
        f"bundle manifest missing required files: {sorted(required_paths - seen_paths)}",
    )

    for index, input_entry in enumerate(manifest["inputs"]):
        _require(isinstance(input_entry, Mapping), f"manifest input {index} must be an object")
        bundle_path = input_entry.get("bundle_path")
        _require(
            isinstance(bundle_path, str) and bundle_path in entries_by_path,
            f"manifest input {index} is not a checksummed bundle file",
        )
        _require(
            input_entry.get("sha256") == entries_by_path[bundle_path].get("sha256"),
            f"manifest input hash mismatch: {bundle_path}",
        )

    schema_payload = json.loads(
        (root / "context/evidence-ledger-v1.schema.json").read_text(encoding="utf-8")
    )
    _require(
        schema_payload.get("properties", {})
        .get("schema_version", {})
        .get("const")
        == LEDGER_SCHEMA_VERSION,
        "bundled ledger schema version differs from runtime",
    )

    ledger = json.loads((root / "evidence-ledger.json").read_text(encoding="utf-8"))
    canonical_results = json.loads(
        (root / "canonical-results.json").read_text(encoding="utf-8")
    )
    _require(isinstance(canonical_results, list), "canonical-results.json must be a list")

    claim_source_payload = json.loads(
        (root / "context/claim-sources.json").read_text(encoding="utf-8")
    )
    _require(
        claim_source_payload.get("schema_version") == "1.0.0",
        "unsupported claim-source index",
    )
    claim_rows = claim_source_payload.get("claims")
    _require(isinstance(claim_rows, list), "claim-source claims must be a list")
    _require(
        claim_rows == _claim_source_index()["claims"],
        "claim-source index differs from registry",
    )
    claim_urls = {
        url
        for row in claim_rows
        for url in row.get("source_urls", [])
        if isinstance(url, str)
    }

    catalog_path = root / "context/transformer_circuits_catalog.csv"
    catalog_urls = load_catalog_urls(catalog_path) if catalog_path.is_file() else claim_urls
    _require(claim_urls <= catalog_urls, "claim-source index contains uncatalogued URLs")
    validate_ledger(
        ledger,
        require_complete=require_complete,
        catalog_urls=catalog_urls,
    )
    _require(
        ledger.get("code_revision") == manifest.get("code_revision"),
        "ledger and manifest code revisions differ",
    )

    canonical_by_experiment: dict[str, Mapping[str, Any]] = {}
    for index, result in enumerate(canonical_results):
        _require(isinstance(result, Mapping), f"canonical result {index} must be an object")
        experiment_id = result.get("experiment_id")
        _require(isinstance(experiment_id, str), f"canonical result {index} lacks experiment_id")
        _require(
            experiment_id not in canonical_by_experiment,
            f"duplicate canonical result: {experiment_id}",
        )
        canonical_by_experiment[experiment_id] = result

    ledger_ids = [str(record["experiment_id"]) for record in ledger["records"]]
    _require(
        ledger_ids == manifest.get("experiment_ids"),
        "ledger and manifest experiment order differ",
    )
    _require(set(ledger_ids) == set(canonical_by_experiment), "canonical results coverage differs")
    for record in ledger["records"]:
        experiment_id = str(record["experiment_id"])
        _require(
            record["result_sha256"] == sha256_value(canonical_by_experiment[experiment_id]),
            f"{experiment_id}: canonical result checksum mismatch",
        )

    _require(
        manifest.get("status_counts") == ledger.get("status_counts"),
        "manifest and ledger status_counts differ",
    )
    baseline_results = json.loads(
        (root / "context/canonical-results-v1.json").read_text(encoding="utf-8")
    )
    _require(isinstance(baseline_results, list), "reviewed baseline must be a list")
    baseline_by_experiment: dict[str, Mapping[str, Any]] = {}
    for index, result in enumerate(baseline_results):
        _require(isinstance(result, Mapping), f"baseline result {index} must be an object")
        experiment_id = result.get("experiment_id")
        _require(isinstance(experiment_id, str), f"baseline result {index} lacks experiment_id")
        _require(
            experiment_id not in baseline_by_experiment,
            f"duplicate baseline result: {experiment_id}",
        )
        baseline_by_experiment[experiment_id] = result
    _require(
        set(ledger_ids) <= set(baseline_by_experiment),
        "reviewed baseline does not cover requested experiments",
    )
    expected_subset = [baseline_by_experiment[experiment_id] for experiment_id in ledger_ids]
    if canonicalize(canonical_results) != canonicalize(expected_subset):
        raise EvidenceValidationError(
            "canonical experiment results drifted from the reviewed bundle baseline"
        )
    return manifest


def compare_canonical_baseline(
    generated_path: str | Path,
    baseline_path: str | Path,
) -> None:
    generated = json.loads(Path(generated_path).read_text(encoding="utf-8"))
    baseline = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    if canonicalize(generated) != canonicalize(baseline):
        raise EvidenceValidationError(
            "canonical experiment results drifted; inspect the generated reproduction bundle "
            "and update the baseline only after reviewing the scientific meaning"
        )
