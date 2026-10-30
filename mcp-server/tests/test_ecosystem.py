"""Tests for the ecosystem composition listing."""

from __future__ import annotations

from financial_library_mcp import ecosystem, server


def test_ecosystem_document_loads():
    doc = ecosystem.load_ecosystem()
    assert doc["checked"] == "2026-10-30"
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


def test_tool_names_and_installs_match_the_reviewed_upstreams():
    """Names checked 2026-10-30 against each server's repository."""
    by_id = {s["id"]: s for s in ecosystem.load_ecosystem()["servers"]}
    assert by_id["fred"]["tools"] == ["fred_browse", "fred_search", "fred_get_series"]
    assert "stefanoamorelli/fred-mcp-server:latest" in by_id["fred"]["install"]
    assert "YOUR_OWN_FREE_FRED_KEY" in by_id["fred"]["install"]
    assert len(by_id["fred-mit-alternative"]["tools"]) == 33
    assert "fred_series_observations" in by_id["fred-mit-alternative"]["tools"]
    assert "pip install fred-mcp-server" in by_id["fred-mit-alternative"]["install"]
    assert "get_recent_filings" in by_id["sec-edgar"]["tools"]
    assert "get_cik_by_ticker" in by_id["sec-edgar"]["tools"]
    assert "lookup_company_cik" not in by_id["sec-edgar"]["tools"]
    assert by_id["imf"]["tools"] == [
        "imf_list_databases",
        "imf_search_databases",
        "imf_get_parameter_defs",
        "imf_get_parameter_codes",
        "imf_fetch_data",
    ]
    assert "316fcb14c33fc15afd54f6620a6a240143ef5d35" in by_id["imf"]["install"]
    assert "marketdata-mcp-server YOUR_API_KEY" in by_id["alpha-vantage"]["install"]
    assert "YOUR_API_KEY" in by_id["alpha-vantage"]["install_remote"]
    assert by_id["eu-finance"]["install"] == "npx -y @nexusforgetools/eu-finance"
    assert "get_eu_inflation" in by_id["eu-finance"]["tools"]
    assert by_id["openbb"]["repo"] == "https://github.com/openbq-org/OpenBB"
    assert "openbb-mcp" in by_id["openbb"]["install"]
    assert "call_tool" in by_id["openbb"]["tools"]
    assert len(by_id["financial-library"]["tools"]) == 7
