# Contributing to FinancialLibrary

Thank you for helping improve open financial literacy materials.

## Ground rules

- **Educational only.** Do not add personalized advice (“you should buy X”),
  product sales, account-opening funnels, or KYC/data collection.
- **Cite sources.** New claims and resources need `source_type` and
  `last_checked` (ISO date `YYYY-MM-DD`).
- **Prefer official sources.** Central banks, securities regulators, treasuries,
  ministries, government portals, NGOs, multilaterals, universities.
- **Licenses.** Code/scripts/schemas/workflows = MIT. Educational prose and
  curated metadata = CC BY 4.0. No DCO/CLA required.

## Good first contribution

Add a single curated resource YAML file (see
[`data/resources/_template.yaml`](data/resources/_template.yaml)). That is our
preferred good-first-issue shape.

## Pull request flow

1. Fork the repo and create a branch (`add-resource-<id>`, `fix-docs-…`).
2. Make a focused change (prefer small PRs).
3. Run locally:
   - `python scripts/validate_data.py` (if you touched `data/`)
   - `python scripts/check_ids.py` (if you added IDs)
   - `mkdocs build --strict` (if you touched docs)
4. Open a PR and complete the PR checklist template.
5. Maintainers use lazy consensus; breaking taxonomy changes need an issue +
   7-day notice (see [GOVERNANCE.md](GOVERNANCE.md)).

## Content rules (quick)

| Do | Don’t |
| --- | --- |
| Explain how a regulated vehicle *typically* works | Recommend a specific purchase |
| Use ISO 3166-1 alpha-2 country codes | Blend products across borders |
| Keep the educational disclaimer block | Remove or weaken disclaimers |
| Link official portals | Promote unregulated “guaranteed return” schemes |

## Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions

See [SUPPORT.md](SUPPORT.md). Do not use issues for personal financial advice.
