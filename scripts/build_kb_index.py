#!/usr/bin/env python3
"""Build data/kb-index.json — the consolidated, agent-consumable index.

Reads every resource and vehicle YAML record, normalizes the fields agents
need, computes per-record freshness from the verification date, and reports
docs-page coverage per country so the prose/data gap stays visible.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = ROOT / "data" / "resources"
VEHICLES_DIR = ROOT / "data" / "vehicles"
DOCS_VEHICLES_DIR = ROOT / "docs" / "vehicles"
OUT = ROOT / "data" / "kb-index.json"
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


def freshness(checked: dt.date | None, today: dt.date) -> tuple[int | None, str]:
    if checked is None:
        return None, "unknown"
    age = (today - checked).days
    if age <= FRESH_DAYS:
        return age, "fresh"
    if age <= STALE_DAYS:
        return age, "aging"
    return age, "stale"


def iter_records(directory: Path):
    if not directory.exists():
        return
    for path in sorted(directory.rglob("*.yaml")) + sorted(directory.rglob("*.yml")):
        if path.name in SKIP_NAMES or SKIP_PARTS & set(path.parts):
            continue
        yield path


def load(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def docs_coverage() -> dict[str, int]:
    coverage: dict[str, int] = {}
    if DOCS_VEHICLES_DIR.exists():
        for country_dir in sorted(DOCS_VEHICLES_DIR.iterdir()):
            if country_dir.is_dir():
                pages = [p for p in country_dir.glob("*.md") if p.name != "index.md"]
                coverage[country_dir.name] = len(pages)
    return coverage


def main() -> int:
    today = dt.date.today()
    resources: list[dict] = []
    for path in iter_records(RESOURCES_DIR):
        data = load(path)
        checked = parse_date(data.get("last_checked"))
        age, bucket = freshness(checked, today)
        resources.append(
            {
                "id": data.get("id", path.stem),
                "title": data.get("title"),
                "url": data.get("url"),
                "country": data.get("country"),
                "language": data.get("language"),
                "topics": data.get("topics", []),
                "audience": data.get("audience", []),
                "source_type": data.get("source_type"),
                "last_checked": checked.isoformat() if checked else None,
                "age_days": age,
                "freshness": bucket,
                "file": str(path.relative_to(ROOT)),
            }
        )

    vehicles: list[dict] = []
    for path in iter_records(VEHICLES_DIR):
        data = load(path)
        checked = parse_date(data.get("last_reviewed"))
        age, bucket = freshness(checked, today)
        vehicles.append(
            {
                "id": data.get("id", path.stem),
                "name": data.get("name"),
                "country": data.get("country"),
                "category": data.get("category"),
                "liquidity": data.get("liquidity"),
                "status": data.get("status"),
                "official_url": data.get("official_url"),
                "docs_path": data.get("docs_path"),
                "source_types": data.get("source_types", []),
                "last_reviewed": checked.isoformat() if checked else None,
                "age_days": age,
                "freshness": bucket,
                "file": str(path.relative_to(ROOT)),
            }
        )

    resources.sort(key=lambda r: r["id"])
    vehicles.sort(key=lambda v: v["id"])
    coverage = docs_coverage()
    yaml_countries: dict[str, int] = {}
    for v in vehicles:
        if v["country"]:
            yaml_countries[v["country"]] = yaml_countries.get(v["country"], 0) + 1

    def bucket_counts(rows: list[dict]) -> dict[str, int]:
        out = {"fresh": 0, "aging": 0, "stale": 0, "unknown": 0}
        for r in rows:
            out[r["freshness"]] += 1
        return out

    index = {
        "kb": "FinancialLibrary",
        "kb_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "generator": "scripts/build_kb_index.py",
        "notes": (
            "Educational only, not financial advice. Freshness buckets: "
            "fresh <= 90 days since verification, aging 91-180, stale > 180, "
            "unknown = no verification date. Source of truth is the YAML "
            "records; this index is a derived view."
        ),
        "counts": {
            "resources": len(resources),
            "vehicles": len(vehicles),
            "resource_countries": len({r["country"] for r in resources if r["country"]}),
            "vehicle_yaml_countries": len(yaml_countries),
            "vehicle_docs_countries": len(coverage),
        },
        "freshness": {
            "resources": bucket_counts(resources),
            "vehicles": bucket_counts(vehicles),
        },
        "coverage": {
            "vehicle_docs_pages_by_country": coverage,
            "vehicle_yaml_by_country": yaml_countries,
        },
        "resources": resources,
        "vehicles": vehicles,
    }
    OUT.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(resources)} resources, {len(vehicles)} vehicle records, "
          f"{len(coverage)} docs countries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
