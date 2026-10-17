# FinancialLibrary

[![Docs](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-docs.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-docs.yml)
[![Data](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-data.yml/badge.svg)](https://github.com/ananddw24/safe_investment_researcher/actions/workflows/ci-data.yml)
[![License: MIT](https://img.shields.io/badge/license%20(code)-MIT-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/license%20(content)-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT)
[![Pages](https://img.shields.io/badge/docs-GitHub%20Pages-222222.svg)](https://ananddw24.github.io/safe_investment_researcher/)

**FinancialLibrary** is an open educational hub that helps low-income households and women
understand money basics, regulated savings and investment *types* by country, and trusted
public resources — without opening accounts, selling products, or giving personalized advice.
Everything is educational only; always verify with official sources in your jurisdiction.

> **Repository name:** This project currently lives at
> [`ananddw24/safe_investment_researcher`](https://github.com/ananddw24/safe_investment_researcher).
> You can rename it to `financial-library` later in GitHub **Settings → General → Repository name**
> (do not rely on API rename if it returns 403). Product name remains **FinancialLibrary**.

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

Docs site (after Pages is enabled): <https://ananddw24.github.io/safe_investment_researcher/>

## Taxonomy map

| Type | Path | Purpose |
| --- | --- | --- |
| Guides | `docs/guides/` | Plain-language literacy explainers |
| Vehicles | `docs/vehicles/<iso>/` | Regulated savings/investment *types* by country |
| Resources | `data/resources/` | Curated outbound links (YAML + schema) |
| Pathways | `docs/pathways/` | Ordered reading paths (no advice engine) |

See also [docs/disclaimer.md](docs/disclaimer.md).

## How to add a resource

1. Copy [`data/resources/_template.yaml`](data/resources/_template.yaml) to a new file.
2. Fill required fields (`id`, `title`, `url`, `country`, `language`, `topics`, `audience`, `source_type`, `last_checked`).
3. Run `python scripts/validate_data.py`.
4. Open a PR (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## License

- **Code, scripts, schemas, workflows:** [MIT](LICENSE)
- **Educational prose and curated metadata:** [CC BY 4.0](LICENSE-CONTENT)

## Status

**v0.3.0** — United States + Kenya household vehicles and resources (after India
in v0.2.0).

The GitHub repository may remain **private** until the owner flips visibility in
Settings. GitHub Pages (Actions) becomes available at
<https://ananddw24.github.io/safe_investment_researcher/> once the repo is public
(or private Pages is enabled) and **Settings → Pages → Source: GitHub Actions** is
selected.

Next: **v0.4.0** remaining Top 10 GDP countries (see
[release plan](docs/about/release-plan.md)).
