#!/usr/bin/env python3
"""Generate, validate, and compare the canonical transparent evidence bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llm_theory_lab.evidence import (  # noqa: E402
    EvidenceValidationError,
    load_catalog_urls,
    load_reviewed_baseline,
    validate_bundle,
    validate_ledger,
    write_reproduction_bundle,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports/reproduction")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    output_dir = ROOT / args.output_dir
    try:
        reviewed_baseline = load_reviewed_baseline(ROOT)
        manifest = write_reproduction_bundle(output_dir, root=ROOT)
        validate_bundle(output_dir)

        ledger_path = output_dir / "evidence-ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        catalog_urls = load_catalog_urls(ROOT / "sources/transformer_circuits_catalog.csv")
        validate_ledger(ledger, catalog_urls=catalog_urls)
        generated = json.loads(
            (output_dir / "canonical-results.json").read_text(encoding="utf-8")
        )
        if generated != reviewed_baseline:
            raise EvidenceValidationError(
                "canonical experiment results drifted from the reviewed baseline"
            )
    except (EvidenceValidationError, OSError, ValueError) as exc:
        print(f"evidence validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        "evidence baseline: OK "
        f"({len(manifest['experiment_ids'])} experiments, {manifest['status_counts']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
