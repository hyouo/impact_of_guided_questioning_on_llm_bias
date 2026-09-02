#!/usr/bin/env python3
"""Validate that the source-by-source digest covers the complete catalog.

This is deliberately a structural check, not a factuality judge. It prevents a
future edit from silently dropping a Transformer Circuits timeline entry.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "sources" / "transformer_circuits_catalog.csv"
DIGEST = ROOT / "docs" / "10_SOURCE_BY_SOURCE_DIGEST.md"

REQUIRED_FIELDS = (
    "**证据状态：**",
    "**研究问题。**",
    "**方法与对象。**",
    "**核心精华。**",
    "**在统一理论中的位置。**",
    "**证据边界。**",
)


@dataclass(frozen=True)
class Source:
    period: str
    title: str
    url: str


def load_catalog() -> list[Source]:
    with CATALOG.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    required_columns = {"period", "title", "url", "status", "theme", "role"}
    missing = required_columns - set(rows[0] if rows else {})
    if missing:
        raise ValueError(f"catalog 缺少字段: {sorted(missing)}")

    sources = [
        Source(row["period"].strip(), row["title"].strip(), row["url"].strip()) for row in rows
    ]
    if len(sources) != 56:
        raise ValueError(f"预期 56 条来源，实际 {len(sources)} 条")
    if len({source.title for source in sources}) != len(sources):
        raise ValueError("catalog 中存在重复标题")
    if len({source.url for source in sources}) != len(sources):
        raise ValueError("catalog 中存在重复 URL")
    return sources


def parse_source_blocks(text: str) -> dict[tuple[str, str], str]:
    """Return {(title, url): block_text} for source headings in the digest."""
    lines = text.splitlines()
    starts: list[tuple[int, str, str]] = []

    for index, line in enumerate(lines):
        if not line.startswith("## ") or "｜[" not in line or "](" not in line:
            continue
        prefix, rest = line[3:].split("｜[", 1)
        try:
            title, url_part = rest.rsplit("](", 1)
        except ValueError as exc:
            raise ValueError(f"无法解析来源标题行: {line}") from exc
        if not url_part.endswith(")"):
            raise ValueError(f"来源标题行缺少右括号: {line}")
        url = url_part[:-1]
        if not prefix.strip():
            raise ValueError(f"来源标题行缺少日期: {line}")
        starts.append((index, title, url))

    blocks: dict[tuple[str, str], str] = {}
    for position, (start, title, url) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        key = (title, url)
        if key in blocks:
            raise ValueError(f"digest 中重复来源: {title}")
        blocks[key] = "\n".join(lines[start:end])

    return blocks


def validate() -> None:
    sources = load_catalog()
    text = DIGEST.read_text(encoding="utf-8")
    blocks = parse_source_blocks(text)

    expected = {(source.title, source.url) for source in sources}
    found = set(blocks)

    missing = expected - found
    extra = found - expected
    if missing:
        details = "\n".join(f"- {title}: {url}" for title, url in sorted(missing))
        raise ValueError(f"digest 缺少来源:\n{details}")
    if extra:
        details = "\n".join(f"- {title}: {url}" for title, url in sorted(extra))
        raise ValueError(f"digest 出现目录外来源标题:\n{details}")

    for source in sources:
        link = f"[{source.title}]({source.url})"
        count = text.count(link)
        if count != 1:
            raise ValueError(
                f"来源链接应在主条目中恰好出现一次，{source.title!r} 实际出现 {count} 次"
            )

        block = blocks[(source.title, source.url)]
        missing_fields = [field for field in REQUIRED_FIELDS if field not in block]
        if missing_fields:
            raise ValueError(f"{source.title!r} 缺少结构字段: {', '.join(missing_fields)}")

    print(f"source digest 校验通过：{len(sources)} 条 catalog 来源均有独立、结构完整的精华条目。")


def main() -> int:
    try:
        validate()
    except (OSError, ValueError) as exc:
        print(f"source digest 校验失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
