#!/usr/bin/env python3
"""Check repository-local Markdown links without making network requests."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "data:")


def normalize_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " " in target and not target.startswith(("http://", "https://")):
        target = target.split(" ", 1)[0]
    return unquote(urlsplit(target).path)


def main() -> int:
    errors: list[str] = []
    markdown_files = sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts and "site" not in path.parts
    )

    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        image_targets = {match.group(1) for match in IMAGE_RE.finditer(text)}
        for match in LINK_RE.finditer(text):
            raw_target = match.group(1)
            if raw_target in image_targets or raw_target.startswith(SKIP_PREFIXES):
                continue
            target = normalize_target(raw_target)
            if not target:
                continue
            resolved = (document.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(
                    f"{document.relative_to(ROOT)}: link escapes repository: {raw_target}"
                )
                continue
            if not resolved.exists():
                errors.append(f"{document.relative_to(ROOT)}: missing target {raw_target}")

    if errors:
        print("internal Markdown link errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"internal Markdown links: OK ({len(markdown_files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
