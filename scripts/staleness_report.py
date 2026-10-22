#!/usr/bin/env python3
"""Report verification-date aging for knowledge-base records.

Resources carry ``last_checked``; vehicles carry ``last_reviewed``.
Buckets: fresh (<= 90 days), aging (91-180 days), stale (> 180 days),
unknown (missing or unparseable date).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ("resources", ROOT / "data" / "resources", "last_checked"),
    ("vehicles", ROOT / "data" / "vehicles", "last_reviewed"),
]
SKIP_NAMES = {"_index.yaml", "_template.yaml"}
SKIP_PARTS = {"examples"}
FRESH_DAYS = 90
STALE_DAYS = 180


def parse_date(value: object) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def bucket_for(age_days: int | None) -> str:
    if age_days is None:
        return "unknown"
    if age_days <= FRESH_DAYS:
        return "fresh"
    if age_days <= STALE_DAYS:
        return "aging"
    return "stale"


def iter_records(directory: Path):
    if not directory.exists():
        return
    for path in sorted(directory.rglob("*.yaml")) + sorted(directory.rglob("*.yml")):
        if path.name in SKIP_NAMES or SKIP_PARTS & set(path.parts):
            continue
        yield path


def collect(today: dt.date) -> list[dict]:
    rows: list[dict] = []
    for kind, directory, field in SOURCES:
        for path in iter_records(directory):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                data = {}
            checked = parse_date(data.get(field)) if isinstance(data, dict) else None
            age = (today - checked).days if checked else None
            rows.append(
                {
                    "kind": kind,
                    "id": data.get("id", path.stem) if isinstance(data, dict) else path.stem,
                    "country": data.get("country") if isinstance(data, dict) else None,
                    "file": str(path.relative_to(ROOT)),
                    "checked_field": field,
                    "last_verified": checked.isoformat() if checked else None,
                    "age_days": age,
                    "bucket": bucket_for(age),
                }
            )
    return rows


def render_markdown(rows: list[dict], today: dt.date) -> str:
    counts = {b: sum(1 for r in rows if r["bucket"] == b) for b in ("fresh", "aging", "stale", "unknown")}
    lines = [
        "## Knowledge-base staleness report",
        "",
        f"Generated {today.isoformat()}. Buckets: fresh <= {FRESH_DAYS} days, "
        f"aging {FRESH_DAYS + 1}-{STALE_DAYS} days, stale > {STALE_DAYS} days.",
        "",
        f"- Total records: {len(rows)}",
        f"- Fresh: {counts['fresh']} · Aging: {counts['aging']} · "
        f"Stale: {counts['stale']} · Unknown date: {counts['unknown']}",
        "",
    ]
    attention = [r for r in rows if r["bucket"] in {"stale", "unknown"}]
    if attention:
        lines += [
            "### Records needing re-verification",
            "",
            "| Record | Kind | Country | Last verified | Age (days) |",
            "| --- | --- | --- | --- | --- |",
        ]
        for r in sorted(attention, key=lambda r: (r["age_days"] is None, -(r["age_days"] or 0))):
            lines.append(
                f"| `{r['id']}` | {r['kind']} | {r['country'] or '—'} | "
                f"{r['last_verified'] or 'never'} | {r['age_days'] if r['age_days'] is not None else '—'} |"
            )
        lines.append("")
    else:
        lines += ["No stale or undated records. ✓", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--md-out", type=Path, help="Write a Markdown report to this path")
    parser.add_argument("--json-out", type=Path, help="Write a JSON report to this path")
    parser.add_argument("--fail-on-stale", action="store_true", help="Exit 1 if any record is stale or undated")
    args = parser.parse_args()

    today = dt.date.today()
    rows = collect(today)
    counts = {b: sum(1 for r in rows if r["bucket"] == b) for b in ("fresh", "aging", "stale", "unknown")}

    print(f"Knowledge-base staleness — {today.isoformat()}")
    print(
        f"  records: {len(rows)}  fresh: {counts['fresh']}  aging: {counts['aging']}  "
        f"stale: {counts['stale']}  unknown: {counts['unknown']}"
    )
    for r in sorted((r for r in rows if r["bucket"] in {"stale", "unknown"}), key=lambda r: -(r["age_days"] or 0)):
        print(f"  [{r['bucket']}] {r['id']} ({r['kind']}, {r['file']}) last verified {r['last_verified'] or 'never'}")

    if args.md_out:
        args.md_out.write_text(render_markdown(rows, today), encoding="utf-8")
    if args.json_out:
        payload = {"generated_on": today.isoformat(), "counts": {"total": len(rows), **counts}, "records": rows}
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.fail_on_stale and (counts["stale"] or counts["unknown"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
