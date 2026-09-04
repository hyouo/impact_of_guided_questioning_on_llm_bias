"""Run experiments and write self-contained reproduction bundles."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from collections.abc import Iterable, Mapping
from importlib import resources
from pathlib import Path
from typing import Any

from .evidence_core import (
    BUNDLE_SCHEMA_VERSION,
    EvidenceValidationError,
    _package_version,
    _utc_now,
    canonical_result,
    canonicalize,
    detect_code_revision,
    sha256_file,
    sha256_value,
)
from .evidence_ledger import (
    build_ledger,
    load_catalog_urls,
    validate_ledger,
    write_evidence_matrix,
)
from .registry import ExperimentSpec, list_experiments, run_toy_suite
from .repro import runtime_metadata
from .reproduction_map import summarize_reproduction_map, validate_reproduction_map
from .result import ExperimentResult, write_report


def _error_result(spec: ExperimentSpec, exc: Exception) -> ExperimentResult:
    metadata = runtime_metadata()
    metadata["error_type"] = type(exc).__name__
    return ExperimentResult(
        experiment_id=spec.experiment_id,
        title=spec.title,
        theory_claim=spec.theory_claim,
        evidence_level="L0-execution-error",
        status="error",
        metrics={},
        checks=(),
        caveats=(
            "实验运行异常；该状态既不是理论反证，也不是支持性证据。",
            str(exc),
        ),
        metadata=metadata,
    )


def run_preserving_failures(
    experiment_ids: Iterable[str] | None = None,
) -> list[ExperimentResult]:
    """Run experiments independently so one exception does not erase the rest."""

    selected = list(list_experiments())
    if experiment_ids is not None:
        requested = [item.upper() for item in experiment_ids]
        if len(requested) != len(set(requested)):
            raise KeyError("experiment IDs must not be repeated")
        by_id = {spec.experiment_id: spec for spec in selected}
        unknown = [item for item in requested if item not in by_id]
        if unknown:
            raise KeyError(f"unknown experiments: {', '.join(unknown)}")
        selected = [by_id[item] for item in requested]

    results: list[ExperimentResult] = []
    for spec in selected:
        try:
            result = run_toy_suite([spec.experiment_id])[0]
        except Exception as exc:  # noqa: BLE001 - preserving the failed record is intentional
            result = _error_result(spec, exc)
        results.append(result)
    return results


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(canonicalize(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _manifest_without_digest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "manifest_sha256"}


def _copy_context_bytes(
    *,
    content: bytes,
    output: Path,
    filename: str,
    source_label: str,
) -> tuple[Path, dict[str, Any]]:
    destination = output / "context" / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return destination, {
        "source_path": source_label,
        "bundle_path": destination.relative_to(output).as_posix(),
        "sha256": sha256_file(destination),
    }


def _repository_or_package_bytes(
    repository_root: Path,
    *,
    repository_path: str,
    package_filename: str,
) -> tuple[bytes, str]:
    candidate = repository_root / repository_path
    if candidate.is_file():
        return candidate.read_bytes(), repository_path

    source_package_file = Path(__file__).resolve().parent / "data" / package_filename
    if source_package_file.is_file():
        return (
            source_package_file.read_bytes(),
            f"package:llm_theory_lab.data/{package_filename}",
        )

    packaged = resources.files("llm_theory_lab.data").joinpath(package_filename)
    try:
        return packaged.read_bytes(), f"package:llm_theory_lab.data/{package_filename}"
    except FileNotFoundError as exc:
        raise EvidenceValidationError(
            f"missing repository and packaged evidence resource: {repository_path}"
        ) from exc


def _load_reviewed_baseline_with_source(
    repository_root: Path,
) -> tuple[list[dict[str, Any]], str]:
    repository_dir = repository_root / "evidence/baseline-v1"
    if repository_dir.is_dir():
        entries = sorted(repository_dir.glob("C*.json"))
        source_label = "evidence/baseline-v1/*.json"
        payloads = [json.loads(path.read_text(encoding="utf-8")) for path in entries]
    else:
        package_dir = resources.files("llm_theory_lab.data").joinpath("baseline-v1")
        entries = sorted(
            (entry for entry in package_dir.iterdir() if entry.name.startswith("C")),
            key=lambda entry: entry.name,
        )
        source_label = "package:llm_theory_lab.data/baseline-v1/*.json"
        payloads = [json.loads(entry.read_text(encoding="utf-8")) for entry in entries]

    expected_ids = [spec.experiment_id for spec in list_experiments()]
    actual_ids = [
        str(payload.get("experiment_id")) for payload in payloads if isinstance(payload, Mapping)
    ]
    if actual_ids != expected_ids:
        raise EvidenceValidationError("reviewed baseline IDs do not match the registry")
    return [canonicalize(payload) for payload in payloads], source_label


def load_reviewed_baseline(
    repository_root: str | Path | None = None,
) -> list[dict[str, Any]]:
    root = Path(repository_root) if repository_root is not None else Path.cwd()
    baseline, _ = _load_reviewed_baseline_with_source(root)
    return baseline


def _claim_source_index() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "claims": [
            {
                "claim_id": spec.claim_id,
                "claim_revision": spec.claim_revision,
                "experiment_id": spec.experiment_id,
                "source_urls": list(spec.source_urls),
            }
            for spec in list_experiments()
        ],
    }


def _add_context_resource(
    *,
    repository_root: Path,
    output: Path,
    repository_path: str,
    package_filename: str,
    bundle_filename: str,
    file_paths: list[Path],
    inputs: list[dict[str, Any]],
) -> tuple[Path, bytes]:
    content, source_label = _repository_or_package_bytes(
        repository_root,
        repository_path=repository_path,
        package_filename=package_filename,
    )
    destination, input_entry = _copy_context_bytes(
        content=content,
        output=output,
        filename=bundle_filename,
        source_label=source_label,
    )
    file_paths.append(destination)
    inputs.append(input_entry)
    return destination, content


def write_reproduction_bundle(
    output_dir: str | Path,
    *,
    experiment_ids: Iterable[str] | None = None,
    root: str | Path | None = None,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for filename in (
        "results.json",
        "report.md",
        "canonical-results.json",
        "evidence-ledger.json",
        "evidence-matrix.md",
        "manifest.json",
    ):
        candidate = output / filename
        if candidate.exists():
            candidate.unlink()
    context_dir = output / "context"
    if context_dir.exists():
        shutil.rmtree(context_dir)

    repository_root = Path(root) if root is not None else Path.cwd()
    code_revision = detect_code_revision(repository_root)
    results = run_preserving_failures(experiment_ids)

    results_path = output / "results.json"
    report_path = output / "report.md"
    write_report(results, json_path=results_path, markdown_path=report_path)

    canonical_results = [canonical_result(result) for result in results]
    canonical_path = output / "canonical-results.json"
    _write_json(canonical_path, canonical_results)

    ledger = build_ledger(results, code_revision=code_revision)
    ledger_path = output / "evidence-ledger.json"
    _write_json(ledger_path, ledger)

    matrix_path = output / "evidence-matrix.md"
    write_evidence_matrix(ledger, matrix_path)

    file_paths = [results_path, report_path, canonical_path, ledger_path, matrix_path]
    inputs: list[dict[str, Any]] = []

    claim_sources_path = output / "context/claim-sources.json"
    _write_json(claim_sources_path, _claim_source_index())
    file_paths.append(claim_sources_path)
    inputs.append(
        {
            "source_path": "generated:experiment-registry",
            "bundle_path": claim_sources_path.relative_to(output).as_posix(),
            "sha256": sha256_file(claim_sources_path),
        }
    )

    _add_context_resource(
        repository_root=repository_root,
        output=output,
        repository_path="schemas/evidence-ledger-v1.schema.json",
        package_filename="evidence-ledger-v1.schema.json",
        bundle_filename="evidence-ledger-v1.schema.json",
        file_paths=file_paths,
        inputs=inputs,
    )

    baseline_payload, baseline_source = _load_reviewed_baseline_with_source(repository_root)
    baseline_destination = output / "context/canonical-results-v1.json"
    _write_json(baseline_destination, baseline_payload)
    file_paths.append(baseline_destination)
    inputs.append(
        {
            "source_path": baseline_source,
            "bundle_path": baseline_destination.relative_to(output).as_posix(),
            "sha256": sha256_file(baseline_destination),
        }
    )

    catalog_destination, catalog_content = _add_context_resource(
        repository_root=repository_root,
        output=output,
        repository_path="sources/transformer_circuits_catalog.csv",
        package_filename="transformer_circuits_catalog.csv",
        bundle_filename="transformer_circuits_catalog.csv",
        file_paths=file_paths,
        inputs=inputs,
    )
    _, reproduction_registry_content = _add_context_resource(
        repository_root=repository_root,
        output=output,
        repository_path="reproductions/transformer_circuits_v1.json",
        package_filename="transformer_circuits_reproduction_v1.json",
        bundle_filename="transformer_circuits_reproduction_v1.json",
        file_paths=file_paths,
        inputs=inputs,
    )
    _add_context_resource(
        repository_root=repository_root,
        output=output,
        repository_path="schemas/reproduction-registry-v1.schema.json",
        package_filename="reproduction-registry-v1.schema.json",
        bundle_filename="reproduction-registry-v1.schema.json",
        file_paths=file_paths,
        inputs=inputs,
    )

    reproduction_registry = json.loads(reproduction_registry_content.decode("utf-8"))
    validate_reproduction_map(reproduction_registry, catalog_content=catalog_content)
    source_coverage = summarize_reproduction_map(reproduction_registry)

    catalog_urls = load_catalog_urls(catalog_destination)
    validate_ledger(
        ledger,
        require_complete=experiment_ids is None,
        catalog_urls=catalog_urls,
    )

    files = [
        {
            "path": path.relative_to(output).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in file_paths
    ]

    manifest: dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_kind": "llm-theory-lab-reproduction",
        "created_at": _utc_now(),
        "package_version": _package_version(),
        "code_revision": code_revision,
        "command": "llm-theory-lab reproduce",
        "experiment_ids": [result.experiment_id for result in results],
        "status_counts": dict(sorted(Counter(result.status for result in results).items())),
        "source_coverage": source_coverage,
        "runtime": runtime_metadata(),
        "inputs": inputs,
        "files": files,
    }
    manifest["manifest_sha256"] = sha256_value(_manifest_without_digest(manifest))
    _write_json(output / "manifest.json", manifest)
    return manifest
