#!/usr/bin/env python3
"""Generate docs/resources/catalog.md from data/resources/*.yaml.

Human-readable browse view for the curated link database. Regenerate with
`make catalog` or as part of `make build`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = ROOT / "data" / "resources"
OUT = ROOT / "docs" / "resources" / "catalog.md"
SKIP_NAMES = {"_index.yaml", "_template.yaml"}
SKIP_PARTS = {"examples"}

COUNTRY_LABELS: dict[str, str] = {
    "br": "Brazil",
    "ca": "Canada",
    "cn": "China",
    "de": "Germany",
    "eg": "Egypt",
    "fr": "France",
    "gb": "United Kingdom",
    "gh": "Ghana",
    "global": "Global",
    "in": "India",
    "it": "Italy",
    "jp": "Japan",
    "ke": "Kenya",
    "ng": "Nigeria",
    "us": "United States",
    "za": "South Africa",
}

HEADER = """---
title: Resource catalog
description: Generated tables of curated official links by country
status: published
---

# Resource catalog

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

This page is **generated** from the YAML records under `data/resources/`.
Do not edit it by hand — run `make catalog` or `python3 scripts/generate_resources_catalog.py`
after changing resource files.

Each link was checked on the date shown. Rules and URLs change; prefer the
official site if something looks outdated.

## Summary

| Country / region | Records |
| --- | ---: |
"""


def iter_resource_paths() -> list[Path]:
    paths: list[Path] = []
    if not RESOURCES_DIR.exists():
        return paths
    for path in sorted(RESOURCES_DIR.rglob("*.yaml")) + sorted(RESOURCES_DIR.rglob("*.yml")):
        if path.name in SKIP_NAMES or SKIP_PARTS & set(path.parts):
            continue
        paths.append(path)
    return paths


def load_record(path: Path) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def country_heading(code: str) -> str:
    label = COUNTRY_LABELS.get(code, code.upper())
    return f"## {label} (`{code}`) {{ #{code} }}"


def render_table(rows: list[dict]) -> str:
    lines = [
        "| Title | Type | Topics | Checked |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        title = f"[{escape_cell(row['title'])}]({row['url']})"
        topics = ", ".join(row.get("topics") or [])
        checked = row.get("last_checked") or "—"
        lines.append(
            f"| {title} | {escape_cell(row.get('source_type') or '—')} "
            f"| {escape_cell(topics)} | {checked} |"
        )
    return "\n".join(lines) + "\n"


def build_markdown(records: list[dict]) -> str:
    by_country: dict[str, list[dict]] = {}
    for rec in records:
        code = rec.get("country") or "unknown"
        by_country.setdefault(code, []).append(rec)

    for rows in by_country.values():
        rows.sort(key=lambda r: (r.get("title") or "").lower())

    parts = [HEADER]
    for code in sorted(by_country.keys(), key=lambda c: (c != "global", c)):
        label = COUNTRY_LABELS.get(code, code)
        parts.append(f"| [{label} (`{code}`)](#{code}) | {len(by_country[code])} |\n")
    parts.append("\n")

    for code in sorted(by_country.keys(), key=lambda c: (c != "global", c)):
        parts.append(country_heading(code))
        parts.append("\n")
        parts.append(render_table(by_country[code]))
        parts.append("\n")

    parts.append(
        "See also the [Resources overview](index.md) and "
        "[Contributing](../contributing.md) to propose a new link.\n"
    )
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if catalog.md would change (for CI).",
    )
    args = parser.parse_args()

    records: list[dict] = []
    for path in iter_resource_paths():
        data = load_record(path)
        if not data:
            print(f"ERROR: could not load {path}", file=sys.stderr)
            return 1
        records.append(data)

    records.sort(key=lambda r: r.get("id", ""))
    content = build_markdown(records)

    if args.check:
        if not OUT.exists():
            print(f"ERROR: missing {OUT.relative_to(ROOT)} — run generate_resources_catalog.py", file=sys.stderr)
            return 1
        if OUT.read_text(encoding="utf-8") != content:
            print("ERROR: catalog.md is out of date — run make catalog", file=sys.stderr)
            return 1
        print("OK: catalog.md is up to date.")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(records)} records).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
