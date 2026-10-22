"""Tests for scripts/generate_resources_catalog.py."""

from conftest import load_script

catalog = load_script("generate_resources_catalog")


def test_country_labels_cover_common_codes():
    assert catalog.COUNTRY_LABELS["in"] == "India"
    assert catalog.COUNTRY_LABELS["global"] == "Global"


def test_build_markdown_includes_country_anchor_and_table():
    records = [
        {
            "id": "in-dfs",
            "title": "Department of Financial Services",
            "url": "https://financialservices.gov.in/",
            "country": "in",
            "source_type": "ministry",
            "topics": ["regulation"],
            "last_checked": "2026-10-17",
        }
    ]
    md = catalog.build_markdown(records)
    assert "## India (`in`)" in md
    assert "{ #in }" in md
    assert "Department of Financial Services" in md
    assert "2026-10-17" in md
    assert "generated" in md.lower()
