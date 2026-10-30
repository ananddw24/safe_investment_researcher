"""Tests for the ecosystem composition listing."""

from __future__ import annotations

from financial_library_mcp import ecosystem, server


def test_ecosystem_document_loads():
    doc = ecosystem.load_ecosystem()
    assert doc["checked"] == "2026-10-29"
    ids = {s["id"] for s in doc["servers"]}
    assert {"financial-library", "fred", "sec-edgar", "imf"} <= ids
    excluded = {e["id"] for e in doc["excluded"]}
    assert "yahoo-finance" in excluded


def test_list_servers_all_and_filtered():
    all_servers = ecosystem.list_servers()
    assert all_servers["count"] == len(all_servers["servers"])
    assert all_servers["count"] >= 6

    core = ecosystem.list_servers(status="core")
    assert {s["id"] for s in core["servers"]} == {
        "financial-library",
        "fred",
        "sec-edgar",
        "imf",
    }
    for entry in core["servers"]:
        assert entry["repo"].startswith("https://")
        assert entry["api_key"]
        assert entry["classroom_use"]


def test_list_servers_unknown_status_is_empty():
    assert ecosystem.list_servers(status="nope")["count"] == 0


def test_tool_wrapper():
    result = server.list_ecosystem_servers()
    assert result["count"] >= 6
    assert "excluded" in result
