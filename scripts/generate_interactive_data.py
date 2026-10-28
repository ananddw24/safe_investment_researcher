#!/usr/bin/env python3
"""Generate the interactive-tools data file from the knowledge-base index.

Reads ``data/kb-index.json`` (built by ``scripts/build_kb_index.py`` from the
YAML records under ``data/``) and writes ``docs/assets/data/library-data.json``,
a trimmed snapshot that the site's interactive tools page
(``docs/resources/tools.md`` + ``docs/assets/javascripts/interactive.js``)
uses for:

- the filterable catalog explorer (country / topic / audience), and
- the deposit-insurance source lookup.

Data provenance rules (do not weaken these):

- Every value in the output comes from the records via the index. Nothing is
  added from outside knowledge.
- The records do **not** store deposit-insurance coverage-limit amounts, so
  the lookup below only identifies which official deposit-insurer sources the
  library holds per country and links out to them. It must never grow a
  ``limit`` field unless the underlying records gain one first (schema +
  validation changes), because a figure shown here would otherwise be
  invented rather than curated.

Usage: ``python3 scripts/generate_interactive_data.py``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "data" / "kb-index.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "assets" / "data" / "library-data.json"

# Human-readable names for the ISO codes used by the records. Names only —
# no facts — so the tools can label filters readably.
COUNTRY_NAMES = {
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

# Resource-record ids that are the official deposit-insurance (or
# share-insurance) source for their country, as curated in data/resources/.
# Identification only: the tool shows the record's title, official URL and
# last-checked date. Coverage limits are not stored in the records and are
# therefore never shown (see module docstring).
DEPOSIT_INSURER_IDS = [
    "br-fgc",
    "ca-cdic",
    "gb-fscs",
    "in-dicgc",
    "it-fitd",
    "us-fdic-deposit-insurance",
    "us-ncua-consumers",
]


def country_name(code: str) -> str:
    return COUNTRY_NAMES.get(code, code)


def main() -> int:
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    resources = index.get("resources", [])

    slim_resources = []
    for r in resources:
        slim_resources.append(
            {
                "id": r["id"],
                "title": r["title"],
                "url": r["url"],
                "country": r["country"],
                "country_name": country_name(r["country"]),
                "language": r.get("language", ""),
                "topics": r.get("topics", []),
                "audience": r.get("audience", []),
                "source_type": r.get("source_type", ""),
                "last_checked": r.get("last_checked", ""),
                "freshness": r.get("freshness", ""),
            }
        )
    slim_resources.sort(key=lambda r: (r["country_name"], r["title"]))

    counts: dict[str, int] = {}
    for r in slim_resources:
        counts[r["country"]] = counts.get(r["country"], 0) + 1
    countries = [
        {"code": code, "name": country_name(code), "resource_count": n}
        for code, n in sorted(counts.items(), key=lambda kv: country_name(kv[0]))
    ]
    topics = sorted({t for r in slim_resources for t in r["topics"]})
    audiences = sorted({a for r in slim_resources for a in r["audience"]})

    by_id = {r["id"]: r for r in slim_resources}
    deposit_insurance = []
    for record_id in DEPOSIT_INSURER_IDS:
        record = by_id.get(record_id)
        if record is None:
            print(
                f"warning: deposit-insurer record {record_id!r} not in index; skipped",
                file=sys.stderr,
            )
            continue
        deposit_insurance.append(
            {
                "country": record["country"],
                "country_name": record["country_name"],
                "record_id": record["id"],
                "insurer": record["title"],
                "url": record["url"],
                "last_checked": record["last_checked"],
            }
        )
    deposit_insurance.sort(key=lambda d: d["country_name"])

    data = {
        "generated_from": "data/kb-index.json",
        "index_generated_at": index.get("generated_at", ""),
        "counts": index.get("counts", {}),
        "countries": countries,
        "topics": topics,
        "audiences": audiences,
        "resources": slim_resources,
        "deposit_insurance": deposit_insurance,
        "deposit_insurance_note": (
            "The library's records identify the official deposit-insurance "
            "source for a country but do not store coverage-limit amounts. "
            "Always confirm the current limit on the official site."
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}: "
        f"{len(slim_resources)} resources, {len(countries)} countries, "
        f"{len(deposit_insurance)} deposit-insurance sources"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
