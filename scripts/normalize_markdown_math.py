#!/usr/bin/env python3
r"""Normalize Markdown math delimiters to GitHub-supported dollar syntax.

GitHub reliably renders inline math as ``$...$`` and display math as
``$$...$$``.  This script converts legacy ``\(...\)`` and ``\[...\]``
delimiters outside fenced code blocks.
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPLACEMENTS = (
    (r"\[", "$$"),
    (r"\]", "$$"),
    (r"\(", "$"),
    (r"\)", "$"),
)


def normalize_text(text: str) -> str:
    """Return *text* with GitHub-compatible math delimiters."""
    output: list[str] = []
    in_fence = False
    fence_marker: str | None = None

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = None
        if stripped.startswith("```"):
            marker = "```"
        elif stripped.startswith("~~~"):
            marker = "~~~"

        if marker is not None:
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            output.append(line)
            continue

        if not in_fence:
            for old, new in REPLACEMENTS:
                line = line.replace(old, new)

        output.append(line)

    return "".join(output)


def markdown_files(root: Path) -> list[Path]:
    """Return tracked-style Markdown paths, excluding common generated dirs."""
    ignored = {".git", ".venv", "venv", "build", "dist", "node_modules"}
    return sorted(
        path for path in root.rglob("*.md") if not any(part in ignored for part in path.parts)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if normalization is needed")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    changed: list[Path] = []
    for path in markdown_files(args.root):
        original = path.read_text(encoding="utf-8")
        normalized = normalize_text(original)
        if normalized == original:
            continue
        changed.append(path)
        if not args.check:
            path.write_text(normalized, encoding="utf-8")

    if changed:
        action = "need normalization" if args.check else "normalized"
        print(f"Markdown files that {action}:")
        for path in changed:
            print(f"- {path.relative_to(args.root)}")
        return 1 if args.check else 0

    print("Markdown math delimiters are GitHub-compatible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
