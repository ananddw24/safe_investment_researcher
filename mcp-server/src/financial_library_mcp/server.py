"""FinancialLibrary MCP server (read-only, stdio transport).

Exposes the FinancialLibrary financial-literacy knowledge base — curated
YAML records of official resources and savings/investment vehicle
explainers — to MCP clients such as Claude Desktop and Cursor.

EDUCATIONAL ONLY: this server provides general financial-literacy
information. It is not financial advice and must never be used to make
personalized recommendations. Answers built on these records must cite
the record's source_url.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .catalog import Library
from .ecosystem import list_servers as _ecosystem_servers

INSTRUCTIONS = """\
FinancialLibrary is an educational knowledge base of official
financial-literacy resources (central banks, securities regulators,
deposit insurers, treasuries, government portals, multilaterals) and
savings/investment vehicle explainers, curated as YAML records.

Rules for using these tools:
- EDUCATIONAL ONLY. This is general financial-literacy information, not
  financial advice. Never turn a record into a personalized
  recommendation for a specific person.
- CITE THE SOURCE. Whenever a record informs an answer, cite the
  record's title and its source_url so the reader can verify it at the
  official source.
- MIND FRESHNESS. Each record carries last_checked and a freshness
  bucket (fresh <= 90 days, aging 91-180, stale > 180). Prefer fresh
  records; flag aging or stale ones when you rely on them.
- COMPOSE FOR LIVE DATA. These records are the explainer layer, not a
  live data feed. list_ecosystem_servers names free companion MCP
  servers (FRED, SEC EDGAR, IMF, ...) whose live official data pairs
  with these records; when an answer combines both, keep the two
  apart — cite the record for the explanation and the live source,
  with its date, for the figure.
"""

mcp = FastMCP("financial-library", instructions=INSTRUCTIONS)

_library: Library | None = None


def get_library() -> Library:
    global _library
    if _library is None:
        _library = Library()
    return _library


@mcp.tool()
def search_records(
    query: str,
    country: str | None = None,
    topic: str | None = None,
    audience: str | None = None,
    kind: str | None = None,
    limit: int = 20,
) -> dict:
    """Search FinancialLibrary records by free text, with optional filters.

    Matches against titles, topics, audiences, categories, and notes.
    `kind` is "resource" (official literacy resources) or "vehicle"
    (savings/investment vehicle explainers). Returns record summaries —
    use get_record for full details. Cite each record's source_url in
    any answer. Educational only, not financial advice.
    """
    results = get_library().search(query, country=country, topic=topic, audience=audience, kind=kind, limit=limit)
    return {"count": len(results), "results": results}


@mcp.tool()
def get_record(record_id: str) -> dict:
    """Get one full record by its id (e.g. "us-cfpb", "in-ppf").

    Returns every curated field, including source_url, last_checked and
    freshness, plus vehicle notes (suitability, risk, literacy angle)
    where present. Cite source_url when using the record.
    """
    record = get_library().get(record_id)
    if record is None:
        return {"error": f"No record with id '{record_id}'. Use search_records or get_catalog to find ids."}
    return record


@mcp.tool()
def get_catalog(
    country: str | None = None,
    topic: str | None = None,
    audience: str | None = None,
    kind: str | None = None,
) -> dict:
    """Browse the catalog: all record summaries matching the filters.

    With no filters, returns the whole catalog (resources and vehicles).
    Use list_countries / list_topics to discover valid filter values.
    """
    results = get_library().catalog(country=country, topic=topic, audience=audience, kind=kind)
    return {"count": len(results), "results": results}


@mcp.tool()
def list_countries() -> dict:
    """List countries covered by the library, with record counts."""
    countries = get_library().countries()
    return {"count": len(countries), "countries": countries}


@mcp.tool()
def list_topics() -> dict:
    """List topics, audiences, and vehicle categories with record counts."""
    return get_library().topics()


@mcp.tool()
def library_status() -> dict:
    """Library overview: record counts, countries covered, freshness summary."""
    return get_library().status()


@mcp.tool()
def list_ecosystem_servers(status: str | None = None) -> dict:
    """List free MCP servers curated to compose with FinancialLibrary.

    FinancialLibrary holds the curated explainers; these companion
    servers supply LIVE official data to set against them — FRED macro
    series, SEC EDGAR filings, IMF cross-country data, and more. Each
    entry gives the repository, licence, API-key requirement, and a
    classroom use. Optionally filter by `status`: "core",
    "alternative", "optional", "pilot", or "advanced". The list also
    names excluded servers and why (for example, Yahoo Finance data is
    personal-use only, so it never feeds published examples). Keys are
    always the user's own — never share or commit one. Educational
    only, not financial advice.
    """
    return _ecosystem_servers(status)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
