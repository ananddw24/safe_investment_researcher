---
title: Educator examples — live data with the library
description: Worked examples and reusable pipelines pairing FinancialLibrary records with free live-data MCP servers (FRED, SEC EDGAR, IMF) for teachers and educators
audience: [educators, general]
topics: [resources, literacy]
status: published
last_reviewed: "2026-10-29"
---

# Educator examples: live data with the library

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

The library explains the institutions. A class also needs *this
week's numbers*. This page is the bridge: worked examples that pair a
library record with live data from **free, official sources**, through
the same Model Context Protocol (MCP) setup as
[Talk to the library](talk-to-the-library.md).

## The composition in one paragraph

Alongside the FinancialLibrary MCP server, a teacher's client can run
a few **free companion MCP servers**: **FRED** for US macro data
(policy rate, inflation, unemployment), **SEC EDGAR** for real
company filings, and the **IMF** for cross-country data covering the
countries in this library. Ready-made client configurations and the
full curation notes — licences, keys, and the servers deliberately
excluded and why — live in the repository at
[`mcp-server/ECOSYSTEM.md`](https://github.com/ananddw24/safe_investment_researcher/blob/main/mcp-server/ECOSYSTEM.md).
The server itself can recite the list: ask for `list_ecosystem_servers`.

The rule in every example: **cite the record for the explanation, and
the live source — with its date — for the figure.**

## Example reports, refreshed weekly

Three example reports are generated from live, keyless official
endpoints (FRED, SEC EDGAR, the World Bank) and refreshed weekly by
an automated job that opens a pull request for human review — nothing
publishes itself:

- **US macro snapshot** — the policy rate, inflation, unemployment,
  the 10-year Treasury and the saving rate, beside the library's US
  records.
- **Reading real bank filings** — the latest 10-K, 10-Q and 8-K of
  three large US banks, beside the records on who regulates and
  insures them.
- **The library's countries in World Bank data** — inflation and
  account ownership across the countries this library covers.

Read them in the repository:
[`examples/educators/`](https://github.com/ananddw24/safe_investment_researcher/tree/main/examples/educators)
(start with `reports/latest.md` there).

## Pipelines to run live in class

The same folder holds three reusable lesson pipelines — setup, exact
prompt sequence, output shape, guardrails:

1. **The weekly rates brief** — policy rate and inflation, set
   against the library's US records (~30 min).
2. **Read a real bank filing** — open a 10-K, find the deposits line,
   connect it to deposit insurance (~45 min).
3. **One question, sixteen countries** — inflation and deposit
   insurance compared across the library's countries, with "not
   covered" treated as a correct answer (~40 min).

## What is deliberately not used

Yahoo Finance data never appears in published examples — it is
licensed for personal use, and a wrapper's code licence cannot change
that. Paid data MCPs are excluded for the simpler reason that this
library's examples must stay free to reproduce. The
[ecosystem notes](https://github.com/ananddw24/safe_investment_researcher/blob/main/mcp-server/ECOSYSTEM.md)
name each exclusion and its reason.
