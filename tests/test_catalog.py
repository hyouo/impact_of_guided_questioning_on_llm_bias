from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_validator():
    path = Path(__file__).resolve().parents[1] / "scripts" / "validate_catalog.py"
    spec = importlib.util.spec_from_file_location("validate_catalog", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_is_complete_and_valid() -> None:
    validator = _load_validator()
    rows = validator.load_rows()
    validator.validate(rows)
    assert len(rows) == 56
    assert sum(row["status"] == "paper" for row in rows) >= 15
    assert sum(row["status"] == "research_update" for row in rows) >= 20
