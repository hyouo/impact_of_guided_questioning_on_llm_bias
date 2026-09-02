#!/usr/bin/env python3
"""Validate the repository's standard layout and version contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "GOVERNANCE.md",
    "CITATION.cff",
    "pyproject.toml",
    "mkdocs.yml",
    ".editorconfig",
    ".gitattributes",
    ".pre-commit-config.yaml",
    ".github/dependabot.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/theory.yml",
    ".github/ISSUE_TEMPLATE/experiment.yml",
    "src/llm_theory_lab/__init__.py",
    "src/llm_theory_lab/py.typed",
    "tests/test_package_metadata.py",
)

REQUIRED_DIRS = (
    "docs",
    "examples",
    "scripts",
    "sources",
    "src/llm_theory_lab",
    "tests",
)

STALE_PATTERNS = (
    'pip install -e "./code',
    "pytest code/tests",
    "code/src/llm_theory_lab",
    "cd code\n",
)


def fail(message: str) -> None:
    print(f"repository contract error: {message}", file=sys.stderr)


def main() -> int:
    errors = 0

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}")
            errors += 1

    for relative in REQUIRED_DIRS:
        if not (ROOT / relative).is_dir():
            fail(f"missing required directory: {relative}")
            errors += 1

    pyproject_path = ROOT / "pyproject.toml"
    if pyproject_path.is_file():
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        version = str(project.get("version", ""))
        name = str(project.get("name", ""))
        if name != "llm-theory-lab":
            fail(f"unexpected project name: {name!r}")
            errors += 1
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            fail(f"project.version is not a stable semantic version: {version!r}")
            errors += 1

        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        citation_match = re.search(r"(?m)^version:\s*[\"']?([^\"'\s]+)", citation)
        citation_version = citation_match.group(1) if citation_match else ""
        if citation_version != version:
            fail(
                "version mismatch between pyproject.toml "
                f"({version}) and CITATION.cff ({citation_version})"
            )
            errors += 1

        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        if f"## [{version}]" not in changelog:
            fail(f"CHANGELOG.md has no section for version {version}")
            errors += 1

    for path in [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "docs"]:
        candidates = [path] if path.is_file() else sorted(path.rglob("*.md"))
        for candidate in candidates:
            text = candidate.read_text(encoding="utf-8")
            for pattern in STALE_PATTERNS:
                if pattern in text:
                    fail(
                        f"stale nested-project reference {pattern!r} "
                        f"in {candidate.relative_to(ROOT)}"
                    )
                    errors += 1

    if errors:
        return 1

    print("repository contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
