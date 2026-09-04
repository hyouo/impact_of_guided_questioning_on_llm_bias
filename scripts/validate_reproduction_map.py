#!/usr/bin/env python3
"""Validate and optionally render the Transformer Circuits reproduction map."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llm_theory_lab.reproduction_map import (  # noqa: E402
    ReproductionMapError,
    load_catalog_bytes,
    load_reproduction_map,
    render_reproduction_map,
    summarize_reproduction_map,
    validate_reproduction_map,
)

DOC_PATH = ROOT / "docs/reference/reproduction-map.md"
REPOSITORY_REGISTRY = ROOT / "reproductions/transformer_circuits_v1.json"
PACKAGED_REGISTRY = (
    ROOT / "src/llm_theory_lab/data/transformer_circuits_reproduction_v1.json"
)
REPOSITORY_SCHEMA = ROOT / "schemas/reproduction-registry-v1.schema.json"
PACKAGED_SCHEMA = ROOT / "src/llm_theory_lab/data/reproduction-registry-v1.schema.json"
REPOSITORY_CATALOG = ROOT / "sources/transformer_circuits_catalog.csv"
PACKAGED_CATALOG = ROOT / "src/llm_theory_lab/data/transformer_circuits_catalog.csv"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-docs",
        action="store_true",
        help="rewrite docs/reference/reproduction-map.md from the registry",
    )
    return parser


def _require_mirror(source: Path, packaged: Path) -> None:
    if not source.is_file():
        raise ReproductionMapError(f"missing canonical resource: {source.relative_to(ROOT)}")
    if not packaged.is_file():
        raise ReproductionMapError(f"missing packaged resource: {packaged.relative_to(ROOT)}")
    if source.read_bytes() != packaged.read_bytes():
        raise ReproductionMapError(
            f"package mirror drift: {source.relative_to(ROOT)} != {packaged.relative_to(ROOT)}"
        )


def main() -> int:
    args = _build_parser().parse_args()
    try:
        _require_mirror(REPOSITORY_REGISTRY, PACKAGED_REGISTRY)
        _require_mirror(REPOSITORY_SCHEMA, PACKAGED_SCHEMA)
        _require_mirror(REPOSITORY_CATALOG, PACKAGED_CATALOG)

        registry = load_reproduction_map(ROOT)
        catalog = load_catalog_bytes(ROOT)
        validate_reproduction_map(registry, catalog_content=catalog)
        expected = render_reproduction_map(registry)
        if args.write_docs:
            DOC_PATH.write_text(expected, encoding="utf-8")
        elif not DOC_PATH.is_file() or DOC_PATH.read_text(encoding="utf-8") != expected:
            raise ReproductionMapError(
                "generated reproduction map is stale; run "
                "python scripts/validate_reproduction_map.py --write-docs"
            )
    except (OSError, ReproductionMapError, ValueError) as exc:
        print(f"reproduction-map validation failed: {exc}", file=sys.stderr)
        return 1

    summary = summarize_reproduction_map(registry)
    print(
        "reproduction map: OK "
        f"({summary['total_sources']} sources; "
        f"{summary['coverage_status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
