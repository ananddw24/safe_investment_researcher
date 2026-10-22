# FinancialLibrary

[![Docs](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-docs.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-docs.yml)
[![Data](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-data.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-data.yml)
[![Links](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-links.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-links.yml)
[![Markdown](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-markdown.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-markdown.yml)
[![License: MIT](https://img.shields.io/badge/license%20(code)-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/license%20(content)-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT)
[![Pages](https://img.shields.io/badge/docs-GitHub%20Pages-222222.svg)](https://ananddw24.github.io/safe_investment_researcher/)

**FinancialLibrary** is an open educational hub that helps low-income households and women
understand money basics, regulated savings and investment *types* by country, and trusted
public resources — without opening accounts, selling products, or giving personalized advice.
Everything is educational only; always verify with official sources in your jurisdiction.

**Read online:** [GitHub Pages docs](https://ananddw24.github.io/safe_investment_researcher/) ·
**New here?** Start with [Using this library](docs/about/using-this-library.md) and the
[New reader pathway](docs/pathways/new-reader.md).

## What this is / is not

| Is | Is not |
| --- | --- |
| Static MkDocs docs site + curated YAML resource DB | Brokerage, robo-advisor, or account-opening funnel |
| Guides, Vehicles (by country), Resources, Pathways | Personalized “you should buy X” recommendations |
| Cite-first educational material for NGOs & educators | KYC, user financial data, or commercial lead gen |
| Fork-friendly MIT (code) + CC BY 4.0 (content) | Unregulated product promotion or “guaranteed returns” content |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
mkdocs serve
```

Or: `make serve` · build: `make build` · validate data: `make validate`

Docs site: <https://ananddw24.github.io/safe_investment_researcher/>

## Taxonomy map

| Type | Path | Purpose |
| --- | --- | --- |
| Guides | `docs/guides/` | Plain-language literacy explainers |
| Vehicles | `docs/vehicles/<iso>/` | Regulated savings/investment *types* by country |
| Resources | `data/resources/` + [catalog](docs/resources/catalog.md) | Curated outbound links (YAML + generated tables) |
| Pathways | `docs/pathways/` | Ordered reading paths (no advice engine) |

See also [docs/disclaimer.md](docs/disclaimer.md).

## How to add a resource

1. Copy [`data/resources/_template.yaml`](data/resources/_template.yaml) to a new file.
2. Fill required fields (`id`, `title`, `url`, `country`, `language`, `topics`, `audience`, `source_type`, `last_checked`).
3. Run `make validate` and `make catalog`.
4. Open a PR (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## Knowledge base (for agents)

FinancialLibrary is maintained as a machine-readable knowledge base that other
agents and tools can consume directly:

- **Agent guide:** [docs/knowledge-base.md](docs/knowledge-base.md) — how to
  query the base, freshness semantics, and citation rules.
- **Index:** `data/kb-index.json` — a single consolidated JSON index of every
  resource and vehicle record, regenerated weekly (build it any time with
  `make kb` or `python scripts/build_kb_index.py`).
- **Records:** the YAML files under `data/resources/` and `data/vehicles/` are
  the source of truth; `data/schemas/` defines their shape.
- **Freshness:** every record carries `last_checked`. Weekly maintenance
  (`.github/workflows/weekly-maintenance.yml`) validates the data, rebuilds
  the index, and reports records going stale — see
  `python scripts/staleness_report.py`.
- **Agent entry point:** [`llms.txt`](llms.txt) at the repository root.

## License

- **Code, scripts, schemas, workflows:** [MIT](LICENSE)
- **Educational prose and curated metadata:** [CC BY 4.0](LICENSE-CONTENT)

## What's inside

Current release: **v0.6.0**.

- **Guides** — plain-language explainers: emergency savings, inflation and
  capital preservation, and spotting unregulated schemes.
- **Vehicle pages** — savings and investment *types* for 15 countries:
  deep guide sets for the Top 10 GDP economies (India, the United States,
  Kenya, China, Germany, Japan, the United Kingdom, France, Italy, Brazil,
  and Canada); introductory overviews for Nigeria, South Africa, Ghana,
  and Egypt.
- **Records** — 80 curated links to regulators, government portals,
  deposit insurers, and other public sources (as of October 2026), each
  carrying a verification date. Browse them in the
  [resource catalog](docs/resources/catalog.md).
- **Pathways** — suggested reading orders, including a
  [new reader pathway](docs/pathways/new-reader.md) and a pathway for
  woman-led households.

What changed in each version is recorded in the
[release history](docs/about/release-plan.md).
