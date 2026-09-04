#!/usr/bin/env python3
"""Validate full Transformer Circuits source-to-replication coverage."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llm_theory_lab.replication_catalog import (  # noqa: E402
    build_replication_catalog,
    replication_summary,
    validate_replication_catalog,
)


def main() -> int:
    repository_catalog = ROOT / "sources/transformer_circuits_catalog.csv"
    packaged_catalog = (
        ROOT
        / "src"
        / "llm_theory_lab"
        / "data"
        / "transformer_circuits_catalog.csv"
    )
    try:
        if repository_catalog.read_bytes() != packaged_catalog.read_bytes():
            raise ValueError("packaged source catalog differs from repository catalog")
        records = build_replication_catalog(repository_catalog)
        validate_replication_catalog(records)
    except (OSError, ValueError) as exc:
        print(f"replication catalog validation failed: {exc}", file=sys.stderr)
        return 1

    summary = replication_summary(records)
    print(
        "replication catalog: OK "
        f"({len(records)} sources; stages={summary['current_stage']}; "
        f"exact={summary['exact_feasibility']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
