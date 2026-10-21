# Knowledge base guide (for agents)

!!! warning "Educational only"
    FinancialLibrary is educational material, not financial advice. Records
    describe regulated savings and investment *types* and link to official
    sources. Never convert a record into a personalized recommendation.

This page is the operating manual for agents and tools that consume
FinancialLibrary as a knowledge base: what to read, how fresh it is, and how
to cite it.

## What the knowledge base contains

| Layer | Location | Contents |
| --- | --- | --- |
| Index | `data/kb-index.json` | One consolidated JSON index of all records, with freshness computed per record. Regenerated weekly. |
| Resource records | `data/resources/*.yaml` | Curated links to official resources (regulators, government portals, deposit insurers, pension authorities, multilaterals). |
| Vehicle records | `data/vehicles/*.yaml` | Machine-readable records for regulated savings/investment types by country. |
| Schemas | `data/schemas/*.schema.json` | The contract every record must satisfy (JSON Schema, draft 2020-12). |
| Prose | `docs/guides/`, `docs/vehicles/<iso>/`, `docs/pathways/` | Human-readable explainers and per-country vehicle pages. |

The YAML records are the source of truth. The index and the website are
derived views.

## How to consume it

1. **Start with the index.** Fetch `data/kb-index.json` from the repository.
   It lists every record with its key fields, its verification date, its age
   in days, and a freshness bucket — no need to crawl the YAML tree.
2. **Fetch individual records when you need full detail** (risk notes,
   suitability notes, literacy angle). Record files are named
   `<country>-<slug>.yaml` under `data/resources/` and `data/vehicles/`.
3. **Read the prose pages for explanation.** Each vehicle record carries a
   `docs_path` pointing at its human-readable page.
4. **Validate before you republish.** If you mirror or transform records,
   run `python scripts/validate_data.py` against the schemas first.

## Freshness semantics

Every record is verified by a human or agent against its official source on
a known date:

- Resources carry `last_checked`; vehicles carry `last_reviewed`.
- **Fresh** — verified within the last 90 days.
- **Aging** — verified 91–180 days ago. Usable, but re-verify figures
  (rates, limits, thresholds) against the official source before citing them.
- **Stale** — verified more than 180 days ago, or missing a date. Do not
  present stale figures as current; flag the record instead.

`scripts/staleness_report.py` prints the current aging table and can emit
Markdown/JSON reports (`--md-out`, `--json-out`).

## Citation rules

- Cite the record's official URL as the authority; cite the record `id`
  (e.g. `in-ppf`, `gb-fca`) when referencing the base itself.
- Prefer records whose `source_type` is a regulator, government, or deposit
  insurer over secondary sources.
- Carry the verification date with the fact: "as checked on
  `<last_checked>`" — financial rules change by notification.

## Coverage notes (honest gaps)

- Prose vehicle pages cover 15 countries; machine-readable vehicle YAML
  currently covers a subset (India, Kenya, United States). The index reports
  both counts per country so consumers can see the gap instead of guessing.
- Resource records favor official sources in English; local-language depth
  varies by country.

## How the base stays current

- A weekly GitHub Actions workflow (`weekly-maintenance.yml`) validates all
  records, rebuilds `data/kb-index.json`, and opens or updates a maintenance
  issue listing stale records for review.
- Updates land as pull requests; `last_checked` / `last_reviewed` are only
  bumped when the source was actually re-verified.
- See [Contributing](contributing.md) to propose a record or a correction.

## Licenses

Code, scripts, and schemas: MIT. Educational prose and curated metadata:
CC BY 4.0. Attribution to FinancialLibrary is appreciated when records are
reused.
