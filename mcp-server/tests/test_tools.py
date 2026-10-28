"""Tests for the FinancialLibrary MCP server's tool handlers.

Runs against a tiny fixture data dir built in tmp_path — the handlers are
exercised through the same functions the MCP tools call.
"""

from __future__ import annotations

import datetime as dt

import pytest
import yaml
from financial_library_mcp import catalog as catalog_module
from financial_library_mcp import server

TODAY = dt.date(2026, 10, 27)

RESOURCE = {
    "id": "us-cfpb",
    "title": "Consumer Financial Protection Bureau",
    "url": "https://www.consumerfinance.gov/",
    "country": "us",
    "language": "en",
    "topics": ["financial-literacy", "banking", "debt"],
    "audience": ["general", "low-income"],
    "source_type": "government-portal",
    "last_checked": "2026-10-17",
}

RESOURCE_2 = {
    "id": "in-rbi-financial-literacy",
    "title": "Reserve Bank of India — Financial Literacy",
    "url": "https://www.rbi.org.in/",
    "country": "in",
    "language": "en",
    "topics": ["financial-literacy", "savings"],
    "audience": ["general", "rural"],
    "source_type": "central-bank",
    "last_checked": "2026-01-01",  # stale relative to TODAY (>180 days)
}

VEHICLE = {
    "id": "in-ppf",
    "name": "Public Provident Fund (PPF)",
    "country": "in",
    "category": "government-scheme",
    "liquidity": "locked-term",
    "suitability_notes": "Long-horizon small-savings scheme. Not a recommendation.",
    "risk_notes": "Lock-in applies; read current official terms.",
    "literacy_angle": "Teaching goal-based saving.",
    "source_types": ["ministry", "government-portal"],
    "official_url": "https://financialservices.gov.in/",
    "docs_path": "vehicles/in/ppf.md",
    "status": "published",
    "last_reviewed": "2026-10-17",
}


@pytest.fixture()
def data_dir(tmp_path):
    resources = tmp_path / "data" / "resources"
    vehicles = tmp_path / "data" / "vehicles"
    resources.mkdir(parents=True)
    vehicles.mkdir(parents=True)
    (resources / "us-cfpb.yaml").write_text(yaml.safe_dump(RESOURCE), encoding="utf-8")
    (resources / "in-rbi-financial-literacy.yaml").write_text(yaml.safe_dump(RESOURCE_2), encoding="utf-8")
    (vehicles / "in-ppf.yaml").write_text(yaml.safe_dump(VEHICLE), encoding="utf-8")
    # Files the loader must skip, mirroring scripts/build_kb_index.py
    (resources / "_template.yaml").write_text(yaml.safe_dump({"id": "xx-template"}), encoding="utf-8")
    examples = resources / "examples"
    examples.mkdir()
    (examples / "demo.yaml").write_text(yaml.safe_dump({"id": "xx-demo"}), encoding="utf-8")
    return tmp_path / "data"


@pytest.fixture()
def library(data_dir):
    return catalog_module.Library(data_dir, today=TODAY)


@pytest.fixture()
def tools(library, monkeypatch):
    monkeypatch.setattr(server, "_library", library)
    return server


def test_loads_resources_and_vehicles_skipping_templates(library):
    assert sorted(r["id"] for r in library.records) == [
        "in-ppf",
        "in-rbi-financial-literacy",
        "us-cfpb",
    ]


def test_freshness_buckets(library):
    assert library.get("us-cfpb")["freshness"] == "fresh"
    assert library.get("in-rbi-financial-literacy")["freshness"] == "stale"
    assert library.get("in-ppf")["last_checked"] == "2026-10-17"


def test_get_record_full_fields(tools):
    record = tools.get_record("in-ppf")
    assert record["kind"] == "vehicle"
    assert record["title"] == "Public Provident Fund (PPF)"
    assert record["source_url"] == "https://financialservices.gov.in/"
    assert record["risk_notes"].startswith("Lock-in")


def test_get_record_missing(tools):
    assert "error" in tools.get_record("nope")


def test_search_records_matches_and_filters(tools):
    hits = tools.search_records("banking")
    assert [h["id"] for h in hits["results"]] == ["us-cfpb"]

    hits = tools.search_records("financial literacy", country="in")
    assert [h["id"] for h in hits["results"]] == ["in-rbi-financial-literacy"]

    hits = tools.search_records("saving", kind="vehicle")
    assert [h["id"] for h in hits["results"]] == ["in-ppf"]

    hits = tools.search_records("literacy", audience="low-income")
    assert [h["id"] for h in hits["results"]] == ["us-cfpb"]


def test_get_catalog_filters(tools):
    assert tools.get_catalog()["count"] == 3
    india = tools.get_catalog(country="in")
    assert india["count"] == 2
    assert {r["kind"] for r in india["results"]} == {"resource", "vehicle"}


def test_list_countries(tools):
    countries = {c["country"]: c for c in tools.list_countries()["countries"]}
    assert countries["us"] == {"country": "us", "resources": 1, "vehicles": 0, "total": 1}
    assert countries["in"]["total"] == 2


def test_list_topics(tools):
    facets = tools.list_topics()
    topics = {t["topic"] for t in facets["topics"]}
    assert {"banking", "debt", "savings", "financial-literacy"} <= topics
    assert {c["category"] for c in facets["vehicle_categories"]} == {"government-scheme"}


def test_library_status(tools):
    status = tools.library_status()
    assert status["records_total"] == 3
    assert status["resources"] == 2
    assert status["vehicles"] == 1
    assert status["countries_covered"] == 2
    assert status["freshness"] == {"fresh": 2, "aging": 0, "stale": 1, "unknown": 0}
    assert status["educational_only"] is True
