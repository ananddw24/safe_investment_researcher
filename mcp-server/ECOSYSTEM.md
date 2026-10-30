# Composing FinancialLibrary with free live-data MCP servers

FinancialLibrary is the **explainer layer**: curated records that say
who the FDIC, the Federal Reserve, a deposit insurer or a regulator
*is*, with an official `source_url` and a `last_checked` date for every
claim. It deliberately holds no live numbers.

Teachers kept asking the obvious next question: *where do this week's
numbers come from?* This document answers it — a curated set of
**free MCP servers** that supply live, official financial data to sit
beside the library in the same client session, so a class can read an
explanation and a live figure side by side. The same list is available
inside the server itself via the `list_ecosystem_servers` tool.

> **Educational only, not investment advice.** Nothing here turns a
> record or a live figure into personalised financial advice or a
> recommendation.

## The core composition

| Server | Live data | Key | Licence (code) |
| --- | --- | --- | --- |
| [FRED MCP — Amorelli](https://github.com/stefanoamorelli/fred-mcp-server) | US macro: policy rate, CPI, unemployment, yields, saving rate (800k+ FRED series) | Free FRED key (your own) | AGPL-3.0 |
| [SEC EDGAR MCP — Amorelli](https://github.com/stefanoamorelli/sec-edgar-mcp) | Real filings: 10-K / 10-Q / 8-K, XBRL statements, insider trades | None (declared user agent) | AGPL-3.0 |
| [IMF Data MCP — c-cf](https://github.com/c-cf/imf-data-mcp) | Cross-country macro for the library's 15 household countries | None | Apache-2.0 |

Ready-to-paste client configurations for exactly this set are in
[`configs/`](configs/) for Claude Desktop and Cursor. The pattern in
every worked example in [`examples/educators/`](../examples/educators/)
is the same:

1. **Library first** — `search_records` / `get_record` for the
   explainer and its official source.
2. **Live second** — the companion server for today's figure, always
   with its series/filing identifier and date.
3. **Keep them apart in the answer** — cite the record for the
   explanation, the live source for the number.

## Optional, pilot and advanced

- **Alpha Vantage** (official, MIT code) — licensed market and
  fundamentals data. Alpha Vantage's support page (checked 2026-10-30)
  allows 25 requests/day on the free key, and unlimited requests for
  verified open-source or educational projects. Real-time US market
  data is premium-only. Local install:
  `uvx marketdata-mcp-server YOUR_API_KEY`. Remote install:
  `https://mcp.alphavantage.co/mcp?apikey=YOUR_API_KEY`. Tool names are
  the API function names (the upstream README lists them). It is the
  licensed substitute for Yahoo Finance data in anything published.
- **EU Finance** (MIT, no key) — ECB rates and Eurostat inflation for
  the euro-area records (EdB, FGDR, FITD). Install:
  `npx -y @nexusforgetools/eu-finance`. Tools include `get_ecb_rates`
  and `get_eu_inflation`. Free during the vendor's beta; the upstream
  README says a Pro tier is coming. A labelled pilot, not a dependency.
- **OpenBB** (advanced alternative) — package `openbb-mcp-server`,
  command `openbb-mcp` (streamable HTTP on `127.0.0.1:8001` by
  default). The canonical repository is
  [openbq-org/OpenBB](https://github.com/openbq-org/OpenBB);
  `OpenBB-finance/OpenBB` redirects there. The LICENSE file is
  Apache-2.0. Offer it *instead of* the standalone servers for advanced
  classes, with versions pinned and `--allowed-categories` restricted.
  Discovery tools, when enabled, are `available_categories`,
  `available_tools`, `search_tools`, and `call_tool`. Other tool names
  come from the installed providers (the platform includes `fred`,
  `imf`, and `cboe`). Each provider keeps its own key and terms.

## Rules of the composition

- **Your own keys, always.** FRED (and Alpha Vantage, if used) require
  a free key per user. FRED's terms expect each user to hold their
  own. Never commit, share or publish a key — configs in this repo
  carry placeholders only.
- **AGPL servers run unmodified.** The FRED and EDGAR servers are
  AGPL-3.0 code. They are referenced by configuration and run as
  separate processes (the configs use the authors' Docker images
  `stefanoamorelli/fred-mcp-server` and `stefanoamorelli/sec-edgar-mcp`);
  nothing from them is vendored or modified here. Amorelli's FRED server
  has three tools: `fred_browse`, `fred_search`, `fred_get_series`.
  EDGAR tool names are the functions in `sec_edgar_mcp/server.py`
  (`get_recent_filings`, `get_filing_sections`, `get_financials`, and
  the rest listed in `ecosystem.json`). An MIT-licensed FRED alternative
  ([floriancaro/fred-mcp-server](https://github.com/floriancaro/fred-mcp-server),
  `pip install fred-mcp-server`, 33 tools, Docker image
  `ghcr.io/floriancaro/fred-mcp-server`) is listed for users who prefer it.
- **Respect upstream fair use.** EDGAR asks for a declared user agent
  in `Name (email)` form and under 10 requests/second. The IMF server's
  README describes a limit of about 10 requests / 5 seconds. FRED allows
  120 requests/minute per key.
- **Yahoo Finance data never feeds published examples.** yfinance-based
  servers are MIT code over data licensed for *personal use*; the code
  licence grants no redistribution or public educational-display
  rights. Explore privately if you like; do not publish from it.
  (Financial Datasets' MCP is excluded for a simpler reason: it is
  not free.)
- **Pin small projects.** The IMF server is a small community project
  (Apache-2.0). The composed configs pin commit
  `316fcb14c33fc15afd54f6620a6a240143ef5d35` (the v0.2.0 move to
  `data.imf.org`; the old `dataservices.imf.org` host no longer
  answers). Tools: `imf_list_databases`, `imf_search_databases`,
  `imf_get_parameter_defs`, `imf_get_parameter_codes`, `imf_fetch_data`.
  Consumer prices are database id `CPI`. Do not track `main`.

The weekly example reports in
[`examples/educators/reports/`](../examples/educators/reports/) are
generated by [`scripts/generate_educator_reports.py`](../scripts/generate_educator_reports.py)
from the same official sources through their free, keyless public
endpoints (FRED CSV downloads, the EDGAR submissions API, the World
Bank Open Data API) — the pipeline a teacher can also drive live,
interactively, through the composed MCP setup above.
