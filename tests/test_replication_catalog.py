from pathlib import Path

import pytest

from llm_theory_lab.replication_catalog import (
    EXPECTED_SOURCE_COUNT,
    ReplicationCatalogError,
    build_replication_catalog,
    find_replication_records,
    replication_summary,
    validate_replication_catalog,
    write_replication_matrix,
)

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_covers_every_source_once() -> None:
    records = build_replication_catalog(ROOT / "sources/transformer_circuits_catalog.csv")
    validate_replication_catalog(records)
    assert len(records) == EXPECTED_SOURCE_COUNT
    assert len({record.source_id for record in records}) == EXPECTED_SOURCE_COUNT
    assert len({record.url for record in records}) == EXPECTED_SOURCE_COUNT


def test_packaged_catalog_matches_repository_catalog() -> None:
    packaged = (
        ROOT
        / "src"
        / "llm_theory_lab"
        / "data"
        / "transformer_circuits_catalog.csv"
    )
    repository = ROOT / "sources" / "transformer_circuits_catalog.csv"
    assert packaged.read_bytes() == repository.read_bytes()


def test_empirical_sources_have_protocols_and_blockers_when_needed() -> None:
    records = build_replication_catalog()
    for record in records:
        assert record.protocol_ids
        if record.exact_feasibility == "blocked-proprietary-assets":
            assert record.blocker
        if record.source_kind in {"paper", "research_update", "cross_post"}:
            assert record.current_stage != "reference-synthesis"


def test_summary_and_search_are_stable() -> None:
    records = build_replication_catalog()
    summary = replication_summary(records)
    assert sum(summary["current_stage"].values()) == EXPECTED_SOURCE_COUNT

    matches = find_replication_records("induction heads", records)
    assert matches
    assert any("Induction Heads" in record.title for record in matches)


def test_empty_query_is_rejected() -> None:
    with pytest.raises(ReplicationCatalogError):
        find_replication_records("   ")


def test_matrix_can_render_a_filtered_subset(tmp_path: Path) -> None:
    records = [record for record in build_replication_catalog() if record.theme == "attention"]
    target = tmp_path / "matrix.md"
    write_replication_matrix(target, records)
    text = target.read_text(encoding="utf-8")
    assert "Progress on Attention" in text
    assert "exact reproduction" in text
