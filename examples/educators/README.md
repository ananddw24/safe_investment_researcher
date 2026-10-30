# Educator examples — live data meets the library

Worked examples for teachers and educators, built to be copied,
adapted and argued with. Each one pairs a **FinancialLibrary record**
(the explainer, with its official source) with **live data from a
free, official source** — the same composition the MCP ecosystem in
[`mcp-server/ECOSYSTEM.md`](../../mcp-server/ECOSYSTEM.md) sets up.

> **Educational only, not financial advice.** These examples teach how
> to read public financial data and institutions. They never recommend
> a product, an account or an action for any individual.

## What's here

- **[`reports/`](reports/)** — actual example reports, generated from
  live data. Start with
  [`reports/latest.md`](reports/latest.md). Three reports:
  - *US macro snapshot* — policy rate, inflation, unemployment, the
    10-year Treasury and the saving rate (FRED), beside the library's
    US records.
  - *Reading real bank filings* — the latest 10-K, 10-Q and 8-K of
    three large US banks (SEC EDGAR), beside the records on who
    regulates and insures them.
  - *The library's countries in World Bank data* — inflation and
    account ownership for the countries the library covers.
- **[`pipelines/`](pipelines/)** — reusable lesson pipelines: the
  server setup, the exact prompt sequence, and the output shape, so a
  teacher can run the same exercise live in class with the composed
  MCP setup instead of the pre-generated report.

## How the reports refresh

[`scripts/generate_educator_reports.py`](../../scripts/generate_educator_reports.py)
pulls from free, keyless, official endpoints only (FRED public CSV
downloads, the SEC EDGAR submissions API, the World Bank Open Data
API). A maintainer runs it and reviews the diff before publishing.
Nothing in this repository runs it on a schedule. Dated snapshots
stay in `reports/` so a class can also study how the numbers moved.
The 2026-10-30 snapshot corrects the 2026-10-29 world table, which
dropped countries and left account ownership empty.

Run it yourself any time. `--as-of` pins the report date so the same
inputs produce the same files:

```bash
python3 scripts/generate_educator_reports.py --as-of 2026-10-30
```

## Ground rules baked into every example

- Every figure names its source and retrieval date; re-check at the
  source before relying on it.
- Library claims cite the record's `source_url`, exactly as the MCP
  server instructs.
- No Yahoo Finance data appears in any published example (its data is
  personal-use only); market-data examples use licensed or official
  sources instead.
