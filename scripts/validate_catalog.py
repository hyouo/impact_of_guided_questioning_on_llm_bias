#!/usr/bin/env python3
"""Validate completeness and basic integrity of the source catalog."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "sources" / "transformer_circuits_catalog.csv"
REQUIRED_COLUMNS = {"period", "title", "url", "status", "theme", "role"}
ALLOWED_STATUS = {
    "paper",
    "research_update",
    "cross_post",
    "tool",
    "essay",
    "exercises",
    "education",
    "infrastructure",
    "predecessor",
}
PERIOD_RE = re.compile(r"^\d{4}-\d{2}(?:-\d{2})?(?:/\d{4}-\d{2})?$")
EXPECTED_COUNT = 56
REQUIRED_TITLES = {
    "A Mathematical Framework for Transformer Circuits",
    "Toy Models of Superposition",
    "Towards Monosemanticity: Decomposing Language Models With Dictionary Learning",
    "Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet",
    "Circuit Tracing: Revealing Computational Graphs in Language Models",
    "On the Biology of a Large Language Model",
    "Verbalizable Representations Form a Global Workspace in Language Models",
    "Characterizing interference weights in a tiny language model",
}


def load_rows() -> list[dict[str, str]]:
    with CATALOG.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"catalog missing columns: {sorted(missing)}")
        return list(reader)


def validate(rows: list[dict[str, str]]) -> None:
    errors: list[str] = []
    if len(rows) != EXPECTED_COUNT:
        errors.append(f"expected {EXPECTED_COUNT} records, found {len(rows)}")

    titles = [row["title"].strip() for row in rows]
    urls = [row["url"].strip() for row in rows]
    if len(set(titles)) != len(titles):
        errors.append("titles must be unique")
    if len(set(urls)) != len(urls):
        errors.append("URLs must be unique")

    for line_number, row in enumerate(rows, start=2):
        if not all(row[column].strip() for column in REQUIRED_COLUMNS):
            errors.append(f"line {line_number}: empty required field")
        if not PERIOD_RE.fullmatch(row["period"].strip()):
            errors.append(f"line {line_number}: invalid period {row['period']!r}")
        if row["status"].strip() not in ALLOWED_STATUS:
            errors.append(f"line {line_number}: invalid status {row['status']!r}")
        parsed = urlparse(row["url"].strip())
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"line {line_number}: invalid HTTPS URL {row['url']!r}")

    missing_titles = REQUIRED_TITLES - set(titles)
    if missing_titles:
        errors.append(f"missing foundational titles: {sorted(missing_titles)}")

    if rows and rows[0]["period"] != "2026-08-21":
        errors.append("catalog must be reverse chronological and start at 2026-08-21")
    if rows and rows[-1]["status"] != "predecessor":
        errors.append("catalog must end with the Distill predecessor")

    if errors:
        raise ValueError("\n".join(errors))


def main() -> None:
    rows = load_rows()
    validate(rows)
    print(f"catalog valid: {len(rows)} unique records in {CATALOG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
