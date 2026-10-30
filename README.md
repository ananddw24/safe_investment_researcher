# FinancialLibrary

[![Docs](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-docs.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-docs.yml)
[![Data](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-data.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-data.yml)
[![Links](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-links.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-links.yml)
[![Markdown](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-markdown.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-markdown.yml)
[![License: MIT](https://img.shields.io/badge/license%20(code)-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/license%20(content)-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT)
[![Pages](https://img.shields.io/badge/docs-GitHub%20Pages-222222.svg)](https://ananddw24.github.io/safe_investment_researcher/)

**FinancialLibrary** is an open **educational** hub for **low-income households**
and **women**. It explains money basics, regulated savings and investment
*types* by country, and trusted public resources — without opening accounts,
selling products, or giving personalized advice.

**Educational only.** Nothing here is personalized financial, tax, or legal
advice, or an offer to buy, sell, or hold any product. Always verify with
official sources in your jurisdiction. Full text:
[docs/disclaimer.md](docs/disclaimer.md).

**Live site:**
[https://ananddw24.github.io/safe_investment_researcher/](https://ananddw24.github.io/safe_investment_researcher/)

**New here?** Start with [Using this library](docs/about/using-this-library.md),
the [New reader pathway](docs/pathways/new-reader.md), the
[Woman-led household pathway](docs/pathways/woman-led-household.md), or
[Community training](docs/training/index.md) for facilitators.

## What this is / is not

| Is | Is not |
| --- | --- |
| Static MkDocs docs site + curated YAML resource DB | Brokerage, robo-advisor, or account-opening funnel |
| Guides, Vehicles (by country), Resources, Pathways, Training | Personalized “you should buy X” recommendations |
| Cite-first educational material for NGOs & educators | KYC, user financial data, or commercial lead gen |
| Fork-friendly MIT (code) + CC BY 4.0 (content) | Unregulated product promotion or “guaranteed returns” content |

## How an outsider contributes

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the
   [Code of Conduct](CODE_OF_CONDUCT.md).
2. Prefer a small first change: add one resource YAML from
   [`data/resources/_template.yaml`](data/resources/_template.yaml).
3. Run `make validate` (and `make catalog` if you changed resources) plus
   `mkdocs build --strict` for docs.
4. Open a pull request. Questions go to Issues via [SUPPORT.md](SUPPORT.md) —
   not for personal financial advice.

## Quick start (local docs)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
mkdocs serve
```

Or: `make serve` · build: `make build` · validate data: `make validate`

## Taxonomy map

| Type | Path | Purpose |
| --- | --- | --- |
| Guides | `docs/guides/` | Plain-language literacy explainers |
| Training | `docs/training/` | 75-minute facilitator session plans |
| Vehicles | `docs/vehicles/<iso>/` | Regulated savings/investment *types* by country |
| Resources | `data/resources/` + [catalog](docs/resources/catalog.md) | Curated outbound links (YAML + generated tables) |
| Pathways | `docs/pathways/` | Ordered reading paths (no advice engine) |

## Knowledge base (for agents)

- **Agent guide:** [docs/knowledge-base.md](docs/knowledge-base.md)
- **Index:** `data/kb-index.json` (`make kb`)
- **Records:** YAML under `data/resources/` and `data/vehicles/`; schemas in
  `data/schemas/`
- **Freshness:** weekly workflows open maintenance PRs/issues — they never
  push silently to `main`
- **Agent entry point:** [`llms.txt`](llms.txt)

## License

- **Code, scripts, schemas, workflows:** [MIT](LICENSE)
- **Educational prose and curated metadata:** [CC BY 4.0](LICENSE-CONTENT)

## Status

**v1.3.0** — Current release. A teaching portfolio of six classroom
modules charts checked-in FRED, SEC EDGAR, IMF, and World Bank snapshots.
v1.2.0 added educator examples and a curated set of free live-data servers
beside the read-only MCP server. v1.1.0 added Talk to the library and the
Explore and tools page. v1.0.0 is the public educational hub: Top 10 GDP +
Africa cluster vehicle pages, literacy guides, community training sessions,
glossary, where-to-check official publishers, curated resources, and weekly
maintenance PRs. An external datasets catalog
([toddrjones/datasets](https://github.com/toddrjones/datasets))
was reviewed and **not** integrated. Live docs:
[ananddw24.github.io/safe_investment_researcher](https://ananddw24.github.io/safe_investment_researcher/).

See the [release plan](docs/about/release-plan.md).
