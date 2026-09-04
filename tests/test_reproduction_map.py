from __future__ import annotations

import copy
from pathlib import Path

import pytest

from llm_theory_lab.registry import list_experiments
from llm_theory_lab.reproduction_map import (
    ReproductionMapError,
    load_catalog_bytes,
    load_reproduction_map,
    render_reproduction_map,
    select_sources,
    summarize_reproduction_map,
    validate_reproduction_map,
)

ROOT = Path(__file__).resolve().parents[1]


def test_reproduction_map_covers_every_catalog_source() -> None:
    registry = load_reproduction_map(ROOT)
    validate_reproduction_map(registry, catalog_content=load_catalog_bytes(ROOT))
    summary = summarize_reproduction_map(registry)

    assert summary["total_sources"] == 56
    assert summary["coverage_status"] == {
        "implemented-partial": 20,
        "planned": 28,
        "reference-only": 8,
    }
    assert summary["current_modes"] == {
        "open-model-analogue": 4,
        "reference": 8,
        "transparent-proxy": 17,
    }


def test_every_transparent_claim_is_linked_back_from_all_sources() -> None:
    registry = load_reproduction_map(ROOT)
    sources = {source["url"]: source for source in registry["sources"]}

    for spec in list_experiments():
        protocol = registry["protocols"][spec.experiment_id]
        assert protocol["kind"] == "transparent-proxy"
        assert protocol["maturity"] == "validated"
        assert protocol["default_ci"] is True
        for url in spec.source_urls:
            assert spec.experiment_id in sources[url]["protocol_ids"]
            assert "transparent-proxy" in sources[url]["current_modes"]


def test_filters_preserve_catalog_order() -> None:
    registry = load_reproduction_map(ROOT)
    planned_p0 = select_sources(
        registry,
        coverage_status="planned",
        priority="P0",
    )
    assert planned_p0
    positions = {source["source_id"]: index for index, source in enumerate(registry["sources"])}
    assert [positions[source["source_id"]] for source in planned_p0] == sorted(
        positions[source["source_id"]] for source in planned_p0
    )

    proxy_sources = select_sources(registry, mode="transparent-proxy")
    assert len(proxy_sources) == 17
    assert all(source["protocol_ids"] for source in proxy_sources)


def test_tampered_catalog_or_protocol_mapping_is_rejected() -> None:
    registry = load_reproduction_map(ROOT)
    catalog = load_catalog_bytes(ROOT)

    tampered_hash = copy.deepcopy(registry)
    tampered_hash["catalog_sha256"] = "0" * 64
    with pytest.raises(ReproductionMapError, match="catalog_sha256"):
        validate_reproduction_map(tampered_hash, catalog_content=catalog)

    tampered_protocol = copy.deepcopy(registry)
    target = next(
        source for source in tampered_protocol["sources"] if "C01" in source["protocol_ids"]
    )
    target["protocol_ids"].remove("C01")
    target["current_modes"] = []
    with pytest.raises(ReproductionMapError, match="C01"):
        validate_reproduction_map(tampered_protocol, catalog_content=catalog)


def test_rendered_markdown_is_committed_snapshot() -> None:
    registry = load_reproduction_map(ROOT)
    expected = render_reproduction_map(registry)
    actual = (ROOT / "docs/reference/reproduction-map.md").read_text(encoding="utf-8")
    assert actual == expected
    assert "implemented-partial" in actual
    assert "blocked-by-proprietary-or-unpublished-assets" in actual
