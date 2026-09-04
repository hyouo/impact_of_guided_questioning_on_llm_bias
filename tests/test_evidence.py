import json
from dataclasses import replace
from pathlib import Path

import pytest

from llm_theory_lab import evidence_run
from llm_theory_lab.evidence import (
    EvidenceValidationError,
    build_ledger,
    canonical_result,
    compare_canonical_baseline,
    load_catalog_urls,
    run_preserving_failures,
    sha256_file,
    sha256_value,
    validate_bundle,
    validate_ledger,
    write_reproduction_bundle,
)
from llm_theory_lab.registry import EXPERIMENTS, run_toy_suite
from llm_theory_lab.reproduction_map import ReproductionMapError
from llm_theory_lab.result import ExperimentResult

ROOT = Path(__file__).resolve().parents[1]


def _reseal_ledger(ledger: dict) -> None:
    ledger["ledger_sha256"] = sha256_value(
        {key: value for key, value in ledger.items() if key != "ledger_sha256"}
    )


def _reseal_manifest(bundle: Path) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries_by_path = {}
    for entry in manifest["files"]:
        path = bundle / entry["path"]
        entry["bytes"] = path.stat().st_size
        entry["sha256"] = sha256_file(path)
        entries_by_path[entry["path"]] = entry
    for input_entry in manifest["inputs"]:
        input_entry["sha256"] = entries_by_path[input_entry["bundle_path"]]["sha256"]
    manifest["manifest_sha256"] = sha256_value(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_every_experiment_has_catalogued_sources_and_versioned_claim() -> None:
    catalog_urls = load_catalog_urls(ROOT / "sources/transformer_circuits_catalog.csv")
    claim_ids = [spec.claim_id for spec in EXPERIMENTS]
    assert len(claim_ids) == len(set(claim_ids))
    for spec in EXPERIMENTS:
        assert spec.claim_id == f"H-{spec.experiment_id}"
        assert spec.claim_revision >= 1
        assert spec.reproduction_status == "transparent-proxy"
        assert spec.source_urls
        assert set(spec.source_urls) <= catalog_urls


def test_canonical_result_ignores_time_and_runtime_metadata() -> None:
    result = run_toy_suite(["C02"])[0]
    changed = replace(
        result,
        created_at="2099-01-01T00:00:00+00:00",
        metadata={**result.metadata, "python": "different", "platform": "different"},
    )
    assert canonical_result(result) == canonical_result(changed)


def test_complete_ledger_validates_and_detects_unsealed_tampering() -> None:
    ledger = build_ledger(run_toy_suite(), code_revision="test-revision")
    catalog_urls = load_catalog_urls(ROOT / "sources/transformer_circuits_catalog.csv")
    validate_ledger(ledger, catalog_urls=catalog_urls)

    tampered = json.loads(json.dumps(ledger))
    tampered["records"][0]["claim"] = "silent narrative upgrade"
    with pytest.raises(EvidenceValidationError, match="ledger checksum mismatch"):
        validate_ledger(tampered, catalog_urls=catalog_urls)


def test_red_team_ledger_rejects_resealed_structural_attacks() -> None:
    catalog_urls = load_catalog_urls(ROOT / "sources/transformer_circuits_catalog.csv")
    original = build_ledger(run_toy_suite(), code_revision="test-revision")

    missing = json.loads(json.dumps(original))
    del missing["records"][0]["scope_limit"]
    _reseal_ledger(missing)
    with pytest.raises(EvidenceValidationError, match="missing fields"):
        validate_ledger(missing, catalog_urls=catalog_urls)

    dataset_tamper = json.loads(json.dumps(original))
    dataset_tamper["records"][0]["dataset"]["generator_revision"] = "forged"
    _reseal_ledger(dataset_tamper)
    with pytest.raises(EvidenceValidationError, match="dataset checksum mismatch"):
        validate_ledger(dataset_tamper, catalog_urls=catalog_urls)

    source_tamper = json.loads(json.dumps(original))
    source_tamper["records"][0]["source_urls"] = ["https://example.invalid/claim"]
    _reseal_ledger(source_tamper)
    with pytest.raises(EvidenceValidationError, match="source drift"):
        validate_ledger(source_tamper, catalog_urls=catalog_urls)

    duplicate = json.loads(json.dumps(original))
    duplicate["records"].append(duplicate["records"][0])
    duplicate["status_counts"]["pass"] += 1
    _reseal_ledger(duplicate)
    with pytest.raises(EvidenceValidationError, match="duplicate record_id"):
        validate_ledger(duplicate, catalog_urls=catalog_urls)


def test_partial_reproduction_bundle_is_self_verifying(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    manifest = write_reproduction_bundle(output, experiment_ids=["C01", "C02"], root=ROOT)
    assert manifest["experiment_ids"] == ["C01", "C02"]
    assert manifest["source_coverage"]["total_sources"] == 56
    assert (output / "context/canonical-results-v1.json").is_file()
    assert (output / "context/claim-sources.json").is_file()
    assert (output / "context/transformer_circuits_catalog.csv").is_file()
    assert (output / "context/transformer_circuits_reproduction_v1.json").is_file()
    assert (output / "context/reproduction-registry-v1.schema.json").is_file()
    validated = validate_bundle(output, require_complete=False)
    assert validated["manifest_sha256"] == manifest["manifest_sha256"]

    report = output / "report.md"
    report.write_text(report.read_text(encoding="utf-8") + "tamper\n", encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="(size|checksum) mismatch"):
        validate_bundle(output, require_complete=False)


def test_bundle_cross_checks_canonical_result_against_ledger(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    write_reproduction_bundle(output, experiment_ids=["C01"], root=ROOT)
    canonical_path = output / "canonical-results.json"
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    canonical[0]["metrics"]["samples"] = 123
    canonical_path.write_text(
        json.dumps(canonical, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _reseal_manifest(output)
    with pytest.raises(EvidenceValidationError, match="canonical result checksum mismatch"):
        validate_bundle(output, require_complete=False)


def test_bundle_rejects_semantically_forged_reproduction_status(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    write_reproduction_bundle(output, experiment_ids=["C01"], root=ROOT)
    registry_path = output / "context/transformer_circuits_reproduction_v1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    target = next(source for source in registry["sources"] if "C01" in source["protocol_ids"])
    target["coverage_status"] = "planned"
    registry_path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _reseal_manifest(output)
    with pytest.raises(
        (ReproductionMapError, EvidenceValidationError),
        match="(planned source already lists a protocol|manifest source coverage differs)",
    ):
        validate_bundle(output, require_complete=False)


def test_bundle_rejects_manifest_path_traversal(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    write_reproduction_bundle(output, experiment_ids=["C01"], root=ROOT)
    manifest_path = output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][0]["path"] = "../escape.json"
    manifest["manifest_sha256"] = sha256_value(
        {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(EvidenceValidationError, match="parent traversal"):
        validate_bundle(output, require_complete=False)


def test_bundle_uses_packaged_context_outside_repository(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    manifest = write_reproduction_bundle(output, experiment_ids=["C02"], root=empty_root)
    assert manifest["source_coverage"]["total_sources"] == 56
    validate_bundle(output, require_complete=False)


def test_runner_preserves_execution_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(_ids):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr(evidence_run, "run_toy_suite", explode)
    result = run_preserving_failures(["C01"])[0]
    assert result.status == "error"
    assert result.metadata["error_type"] == "RuntimeError"
    assert "synthetic failure" in result.caveats


def test_error_and_inconclusive_are_distinct_supported_states() -> None:
    for status in ("error", "inconclusive"):
        result = ExperimentResult(
            experiment_id="X00",
            title="state test",
            theory_claim="state semantics",
            evidence_level="L0-test",
            status=status,
        )
        assert result.status == status


def test_baseline_comparison_rejects_drift(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    generated = tmp_path / "generated.json"
    baseline.write_text('[{"experiment_id": "C01", "value": 1.0}]\n', encoding="utf-8")
    generated.write_text('[{"value": 1, "experiment_id": "C01"}]\n', encoding="utf-8")
    compare_canonical_baseline(generated, baseline)

    generated.write_text('[{"value": 2, "experiment_id": "C01"}]\n', encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="drifted"):
        compare_canonical_baseline(generated, baseline)
