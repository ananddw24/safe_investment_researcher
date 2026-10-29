---
title: Contributing
description: How to contribute to FinancialLibrary
---

# Contributing

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

Thank you for helping improve open financial literacy materials.

## Ground rules

- **Educational only** — no personalized advice, product sales, account-opening
  funnels, or collecting user financial data.
- **Cite sources** — new resources need `source_type` and `last_checked`
  (`YYYY-MM-DD`).
- **Prefer official sources** — regulators, government portals, deposit insurers,
  multilaterals.
- **Licenses** — code MIT; prose and curated metadata CC BY 4.0.

## Good first contribution

Add one curated resource YAML file using
[`data/resources/_template.yaml`](https://github.com/ananddw24/safe_investment_researcher/blob/main/data/resources/_template.yaml),
then run:

```bash
make validate
make catalog
mkdocs build --strict
```

## Pull requests

1. Fork and branch (`add-resource-<id>`, `fix-docs-…`).
2. Keep changes focused.
3. Complete the PR checklist in the repository.
4. See [GOVERNANCE.md](https://github.com/ananddw24/safe_investment_researcher/blob/main/GOVERNANCE.md)
   for lazy consensus and taxonomy changes.

Full contributor guide:
[CONTRIBUTING.md](https://github.com/ananddw24/safe_investment_researcher/blob/main/CONTRIBUTING.md)

## Page templates

Contributor page templates live in the repo as `docs/guides/_template.md`,
`docs/pathways/_template.md`, and `docs/vehicles/_template.md`. They are
excluded from the published MkDocs site so readers do not land on stub pages.
