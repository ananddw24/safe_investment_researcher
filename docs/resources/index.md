---
title: Resources
description: Curated YAML resource database
status: published
last_reviewed: "2026-10-22"
---

# Resources

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

FinancialLibrary maintains a **curated link database** of public, official
sources: central banks, securities regulators, treasuries, deposit insurers,
pension authorities, and selected multilateral literacy portals.

## Browse (recommended)

**[Resource catalog](catalog.md)** — human-readable tables grouped by country,
generated from the YAML records. Each row shows the verification date
(`last_checked`).

**[Explore and tools](tools.md)** — the same records, interactively:
filter the catalog by country, topic, and audience; try an emergency-fund
target calculator; and look up which countries have an official
deposit-insurance source in the library.

## Source data (for contributors)

Records live as YAML under [`data/resources/`](https://github.com/ananddw24/safe_investment_researcher/tree/main/data/resources)
and must pass [`scripts/validate_data.py`](https://github.com/ananddw24/safe_investment_researcher/blob/main/scripts/validate_data.py)
against [`data/schemas/resource.schema.json`](https://github.com/ananddw24/safe_investment_researcher/blob/main/data/schemas/resource.schema.json).

To add a link:

1. Copy [`data/resources/_template.yaml`](https://github.com/ananddw24/safe_investment_researcher/blob/main/data/resources/_template.yaml).
2. Fill required fields (`id`, `title`, `url`, `country`, `language`, `topics`,
   `audience`, `source_type`, `last_checked`).
3. Run `make validate` and `make catalog`, then open a pull request.

See [Contributing](../contributing.md).

## Coverage

Records span India, the United States, Kenya, the Africa cluster (Nigeria,
South Africa, Ghana, Egypt), remaining Top 10 GDP countries, and selected
global literacy portals. The catalog summary table lists exact counts per
country.
