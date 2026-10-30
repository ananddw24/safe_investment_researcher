# FinancialLibrary MCP Server

A read-only [Model Context Protocol](https://modelcontextprotocol.io)
(MCP) server for **FinancialLibrary**, the financial-literacy knowledge
base in this repository. It lets MCP clients — Claude Desktop, Cursor,
and other agents — search and browse the library's curated records:
official financial-literacy resources (central banks, securities
regulators, deposit insurers, treasuries, government portals) and
savings/investment vehicle explainers.

> **Educational only, not financial advice.** The server serves general
> financial-literacy information. Its instructions tell the client model
> never to turn a record into a personalized recommendation, and to cite
> each record's `source_url` so readers can verify claims at the
> official source.

## Tools

| Tool | What it does |
| --- | --- |
| `search_records` | Free-text search over titles, topics, audiences, categories and notes, with optional `country` / `topic` / `audience` / `kind` filters and a `limit`. |
| `get_record` | One full record by id (e.g. `us-cfpb`, `in-ppf`), including `source_url`, `last_checked`, freshness, and vehicle notes. |
| `get_catalog` | Browse record summaries matching optional `country` / `topic` / `audience` / `kind` filters (no filters = whole catalog). |
| `list_countries` | Countries covered, with resource/vehicle counts. |
| `list_topics` | Topics, audiences, and vehicle categories with record counts. |
| `library_status` | Totals, countries covered, and the freshness summary. |
| `list_ecosystem_servers` | Free live-data MCP servers curated to compose with this one (FRED, SEC EDGAR, IMF, …), each with licence, key requirement, and a classroom use — plus the excluded servers and why. Optional `status` filter. |

## Compose with live data

This server is the explainer layer; it holds no live numbers. For the
classroom pattern — a library record beside today's figure from an
official source — see **[ECOSYSTEM.md](ECOSYSTEM.md)** and the
ready-to-paste composed client configurations in
[`configs/`](configs/) (FinancialLibrary + FRED + SEC EDGAR + IMF).
Worked examples and reusable lesson pipelines live in
[`examples/educators/`](../examples/educators/) in this repository,
including example reports refreshed weekly from FRED, SEC EDGAR and
the World Bank.

All tools are read-only. Records carry a freshness bucket that matches
`scripts/build_kb_index.py`: **fresh** ≤ 90 days since verification,
**aging** 91–180, **stale** > 180, **unknown** = no verification date.

## How it reads the data

The YAML records under `data/resources/` and `data/vehicles/` are the
source of truth (the same files `data/kb-index.json` is generated from).
The server loads them directly at startup — no index rebuild needed.
It finds the data directory by, in order:

1. `FINANCIAL_LIBRARY_DATA_DIR` — path to the `data/` directory itself.
2. `FINANCIAL_LIBRARY_ROOT` — path to a repository checkout
   (data is read from `<root>/data`).
3. Walking up from the current directory / package location looking for
   a `data/resources` directory — i.e. running inside a checkout works
   with no configuration.

## Install

From a checkout of this repository:

```bash
git clone https://github.com/ananddw24/safe_investment_researcher.git
cd safe_investment_researcher
pip install ./mcp-server
```

This installs the `financial-library-mcp` command. (For development:
`pip install -e "./mcp-server[dev]"`.)

## Configure your client

Set `FINANCIAL_LIBRARY_ROOT` to your checkout path so the server can
find the records wherever the client launches it from.

### Claude Desktop

Add to `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`;
Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "financial-library": {
      "command": "financial-library-mcp",
      "env": {
        "FINANCIAL_LIBRARY_ROOT": "/path/to/safe_investment_researcher"
      }
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project):

```json
{
  "mcpServers": {
    "financial-library": {
      "command": "financial-library-mcp",
      "env": {
        "FINANCIAL_LIBRARY_ROOT": "/path/to/safe_investment_researcher"
      }
    }
  }
}
```

Restart the client; the six `financial-library` tools should appear.

## Develop and test

```bash
cd mcp-server
pip install -e ".[dev]"
python -m pytest
```

Tests run the tool handlers against a small fixture data set — they do
not need the full library. To smoke-test against the real records, run
the server from the repository root and call `library_status`, or use
the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector financial-library-mcp
```

## Not included

- No write tools — the server can never modify records.
- No hosted/remote transport yet: stdio only, one local checkout per
  client. An HTTP transport can be added later without changing the
  tool handlers.
- No personalized advice, recommendations, or product comparisons —
  by design.
