"""Data layer for the FinancialLibrary MCP server.

Reads the curated YAML records that are the library's source of truth:

- ``data/resources/*.yaml`` — official financial-literacy resources
  (regulators, deposit insurers, government portals, multilaterals).
- ``data/vehicles/*.yaml`` — savings/investment vehicle explainers.

Freshness buckets mirror ``scripts/build_kb_index.py`` so the MCP server
and the generated ``data/kb-index.json`` agree: fresh <= 90 days since
verification, aging 91-180, stale > 180, unknown = no verification date.

Educational only — this module serves catalog data, never advice.
"""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import yaml

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


def find_data_dir(explicit: str | Path | None = None) -> Path:
    """Locate the directory that contains ``resources/`` and ``vehicles/``.

    Resolution order: explicit argument, ``FINANCIAL_LIBRARY_DATA_DIR``,
    ``FINANCIAL_LIBRARY_ROOT`` (repo root; data lives under ``<root>/data``),
    then walk up from the current directory and from this file looking for a
    ``data/resources`` directory (i.e. running inside a repo checkout).
    """
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit))
    env_data = os.environ.get("FINANCIAL_LIBRARY_DATA_DIR")
    if env_data:
        candidates.append(Path(env_data))
    env_root = os.environ.get("FINANCIAL_LIBRARY_ROOT")
    if env_root:
        candidates.append(Path(env_root) / "data")
    for start in (Path.cwd(), Path(__file__).resolve()):
        for parent in (start, *start.parents):
            candidates.append(parent / "data")
    for candidate in candidates:
        if (candidate / "resources").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not locate the FinancialLibrary data directory (a folder "
        "containing resources/ and vehicles/). Run the server from a "
        "checkout of the FinancialLibrary repository, or set "
        "FINANCIAL_LIBRARY_ROOT to the checkout path."
    )


def _iter_record_files(directory: Path):
    if not directory.exists():
        return
    for path in sorted(directory.rglob("*.yaml")) + sorted(directory.rglob("*.yml")):
        if path.name in SKIP_NAMES or SKIP_PARTS & set(path.parts):
            continue
        yield path


def _load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _as_list(value: object) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


class Library:
    """In-memory view over the YAML records, loaded once at startup."""

    def __init__(self, data_dir: str | Path | None = None, today: dt.date | None = None):
        self.data_dir = find_data_dir(data_dir)
        self.today = today or dt.date.today()
        self.records: list[dict] = []
        self._by_id: dict[str, dict] = {}
        for record in self._load_resources():
            self._add(record)
        for record in self._load_vehicles():
            self._add(record)
        self.records.sort(key=lambda r: r["id"])

    # -- loading ---------------------------------------------------------

    def _add(self, record: dict) -> None:
        self.records.append(record)
        self._by_id[record["id"]] = record

    def _load_resources(self):
        for path in _iter_record_files(self.data_dir / "resources"):
            data = _load_yaml(path)
            if not data.get("id"):
                continue
            checked = parse_date(data.get("last_checked"))
            age, bucket = freshness(checked, self.today)
            yield {
                "id": data["id"],
                "kind": "resource",
                "title": data.get("title"),
                "source_url": data.get("url"),
                "country": data.get("country"),
                "region": data.get("region"),
                "language": data.get("language"),
                "topics": _as_list(data.get("topics")),
                "audience": _as_list(data.get("audience")),
                "source_type": data.get("source_type"),
                "notes": data.get("notes"),
                "license_hint": data.get("license_hint"),
                "last_checked": checked.isoformat() if checked else None,
                "age_days": age,
                "freshness": bucket,
                "file": path.name,
            }

    def _load_vehicles(self):
        for path in _iter_record_files(self.data_dir / "vehicles"):
            data = _load_yaml(path)
            if not data.get("id"):
                continue
            checked = parse_date(data.get("last_reviewed"))
            age, bucket = freshness(checked, self.today)
            yield {
                "id": data["id"],
                "kind": "vehicle",
                "title": data.get("name"),
                "source_url": data.get("official_url"),
                "country": data.get("country"),
                "category": data.get("category"),
                "liquidity": data.get("liquidity"),
                "status": data.get("status"),
                "source_types": _as_list(data.get("source_types")),
                "suitability_notes": data.get("suitability_notes"),
                "risk_notes": data.get("risk_notes"),
                "literacy_angle": data.get("literacy_angle"),
                "docs_path": data.get("docs_path"),
                "last_checked": checked.isoformat() if checked else None,
                "age_days": age,
                "freshness": bucket,
                "file": path.name,
            }

    # -- queries ---------------------------------------------------------

    def get(self, record_id: str) -> dict | None:
        return self._by_id.get(record_id.strip().lower())

    @staticmethod
    def summary(record: dict) -> dict:
        """Compact view used in search/catalog results."""
        return {
            "id": record["id"],
            "kind": record["kind"],
            "title": record["title"],
            "country": record["country"],
            "source_url": record["source_url"],
            "topics": record.get("topics") or ([record["category"]] if record.get("category") else []),
            "audience": record.get("audience") or [],
            "last_checked": record["last_checked"],
            "freshness": record["freshness"],
        }

    def _matches_filters(self, record: dict, country=None, topic=None, audience=None, kind=None) -> bool:
        if kind and record["kind"] != kind:
            return False
        if country and (record.get("country") or "").lower() != country.strip().lower():
            return False
        if topic:
            topics = {t.lower() for t in record.get("topics") or []}
            if record.get("category"):
                topics.add(record["category"].lower())
            if topic.strip().lower() not in topics:
                return False
        if audience:
            audiences = {a.lower() for a in record.get("audience") or []}
            if audience.strip().lower() not in audiences:
                return False
        return True

    def catalog(self, country=None, topic=None, audience=None, kind=None) -> list[dict]:
        return [
            self.summary(r)
            for r in self.records
            if self._matches_filters(r, country=country, topic=topic, audience=audience, kind=kind)
        ]

    def search(self, query: str, country=None, topic=None, audience=None, kind=None, limit: int = 20) -> list[dict]:
        terms = [t for t in query.lower().split() if t]
        if not terms:
            return []
        scored: list[tuple[int, dict]] = []
        for record in self.records:
            if not self._matches_filters(record, country=country, topic=topic, audience=audience, kind=kind):
                continue
            haystacks = {
                "title": (record.get("title") or "").lower(),
                "id": record["id"].lower(),
                "topics": " ".join(record.get("topics") or []).lower(),
                "audience": " ".join(record.get("audience") or []).lower(),
                "meta": " ".join(
                    str(record.get(k) or "") for k in ("country", "source_type", "category", "language", "liquidity")
                ).lower(),
                "notes": " ".join(
                    str(record.get(k) or "") for k in ("notes", "suitability_notes", "risk_notes", "literacy_angle")
                ).lower(),
            }
            score = 0
            for term in terms:
                if term in haystacks["title"]:
                    score += 4
                if term in haystacks["id"]:
                    score += 3
                if term in haystacks["topics"]:
                    score += 3
                if term in haystacks["audience"]:
                    score += 2
                if term in haystacks["meta"]:
                    score += 1
                if term in haystacks["notes"]:
                    score += 1
            if score > 0:
                scored.append((score, record))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        return [self.summary(r) for _, r in scored[: max(1, limit)]]

    # -- facets & status ---------------------------------------------------

    def countries(self) -> list[dict]:
        counts: dict[str, dict[str, int]] = {}
        for record in self.records:
            country = record.get("country")
            if not country:
                continue
            entry = counts.setdefault(country, {"resources": 0, "vehicles": 0})
            entry["resources" if record["kind"] == "resource" else "vehicles"] += 1
        return [
            {"country": country, **counts[country], "total": counts[country]["resources"] + counts[country]["vehicles"]}
            for country in sorted(counts)
        ]

    def topics(self) -> list[dict]:
        topic_counts: dict[str, int] = {}
        audience_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}
        for record in self.records:
            for topic in record.get("topics") or []:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            for aud in record.get("audience") or []:
                audience_counts[aud] = audience_counts.get(aud, 0) + 1
            if record.get("category"):
                category_counts[record["category"]] = category_counts.get(record["category"], 0) + 1
        return {
            "topics": [{"topic": t, "records": n} for t, n in sorted(topic_counts.items())],
            "audiences": [{"audience": a, "records": n} for a, n in sorted(audience_counts.items())],
            "vehicle_categories": [{"category": c, "records": n} for c, n in sorted(category_counts.items())],
        }

    def status(self) -> dict:
        buckets = {"fresh": 0, "aging": 0, "stale": 0, "unknown": 0}
        for record in self.records:
            buckets[record["freshness"]] += 1
        resources = sum(1 for r in self.records if r["kind"] == "resource")
        vehicles = sum(1 for r in self.records if r["kind"] == "vehicle")
        countries = {r["country"] for r in self.records if r.get("country")}
        return {
            "library": "FinancialLibrary",
            "educational_only": True,
            "disclaimer": (
                "Educational only, not financial advice. Records point to "
                "official sources; always cite the record's source_url."
            ),
            "records_total": len(self.records),
            "resources": resources,
            "vehicles": vehicles,
            "countries_covered": len(countries),
            "countries": sorted(countries),
            "freshness": buckets,
            "freshness_note": (
                "fresh <= 90 days since verification, aging 91-180, stale > 180, unknown = no verification date."
            ),
            "as_of": self.today.isoformat(),
        }
