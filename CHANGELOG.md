# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Knowledge-base layer for agent consumers: `llms.txt` entry point,
  `docs/knowledge-base.md` agent guide (consumption paths, freshness
  semantics, citation rules), and `data/kb-index.json`, a consolidated
  machine-readable index of all resource and vehicle records
- `scripts/build_kb_index.py` (index builder) and
  `scripts/staleness_report.py` (last_checked aging report with
  fresh / aging / stale buckets); `make kb` runs both
- Weekly maintenance workflow (`.github/workflows/weekly-maintenance.yml`):
  validates data, rebuilds the index, and files a maintenance issue when
  records go stale
- Python quality tooling: `ruff` lint configuration in `pyproject.toml`
  (`make lint`) and a `pytest` suite under `tests/` (`make test`) covering
  the knowledge-base scripts' date/freshness logic and schema validation
  of conforming and non-conforming records
- Dependabot now also watches `scripts/requirements-dev.txt`
- `RELEASING.md`: the release checklist (version bumps across
  pyproject/CITATION/README/SECURITY, changelog, tag, verification)

### Fixed

- Version drift: `pyproject.toml` and the README status section now agree
  with the changelog (v0.5.0)
- Lint findings in the scripts: `datetime.UTC` alias, sorted imports in
  `extract_resource_urls.py`, and wrapped over-length lines in
  `staleness_report.py` (no behavior changes)
- Remaining version drift from the open-source readiness audit:
  `CITATION.cff` now reports 0.5.0, `SECURITY.md` supported versions cover
  the 0.5.x release line, and `GOVERNANCE.md` no longer carries v0.1 labels

### Changed

- README gains badges for the link-check and markdown-lint workflows
- `pyproject.toml` uses the SPDX license string and adds package classifiers


## [0.5.0] - 2026-10-17

### Added

- Africa cluster household vehicle pages for Nigeria, South Africa, Ghana, and
  Egypt (6 vehicles each), with inflation/FX and unregulated-scheme framing
- Verified regulator/government resource YAML for those countries
- Homepage and nav links for Nigeria, South Africa, Ghana, and Egypt
- Kenya index links to Africa cluster peers (Kenya content not rewritten)

### Changed

- Release plan marks v0.5.0 shipped

## [0.4.0] - 2026-10-17

### Added

- Short household vehicle pages for remaining Top 10 GDP countries: China,
  Germany, Japan, United Kingdom, France, Italy, Brazil, Canada (6 vehicles each)
- Verified regulator/government resource YAML for those countries
- Homepage and nav links for all Top 10 country sections

### Changed

- Release plan marks v0.4.0 shipped

## [0.3.0] - 2026-10-17

### Added

- United States household vehicle pages (FDIC savings/MMDA, 401(k)/IRA concepts,
  TreasuryDirect, index funds/ETFs literacy, credit union savings, 529/Coverdell)
- Kenya household vehicle pages (mobile money savings/locks, bank/MFI deposits,
  money market fund literacy, treasury bills/bonds, SACCOs, NSSF/pensions)
- Additional verified US and Kenya resource YAML records
- Homepage and nav links for United States and Kenya

### Changed

- Release plan status marks v0.3.0 shipped

## [0.2.0] - 2026-10-17

### Added

- India household vehicle pages (bank savings, RD, FD, PPF, SSY, NPS, SIP/ELSS
  literacy, postal schemes, gold SGB vs physical, SHG/microfinance literacy)
- Guides: emergency savings; inflation and capital preservation; spotting
  unregulated “guaranteed return” schemes
- Pathway: woman-led household (links only to pages shipped in this release)
- Homepage and section indexes rewritten as a public educational hub
- Verified resource YAML records (India regulators + selected global literacy
  portals) and matching vehicle YAML stubs
- Release plan page (`docs/about/release-plan.md`)

### Changed

- README status notes private visibility / Pages expectations until owner flips
  the repository to public (or enables private Pages)

## [0.1.0] - 2026-10-17

### Added

- Public repository scaffold: MkDocs Material site, dual MIT + CC BY 4.0 licenses
- Community health pack (CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, GOVERNANCE)
- JSON Schemas and example YAML for resources and vehicles
- Validation / export scripts and Makefile (`serve`, `build`, `validate`)
- GitHub Actions: docs, data, links (soft-fail), markdown, Pages deploy, release
- Issue and PR templates, Dependabot, AGENTS.md and Cursor rules
- India vehicles stub landing and content templates (Guides / Vehicles / Pathways)

### Notes

- **Scaffold only** at 0.1.0. Content seeding begins with 0.2.0 (India).

[Unreleased]: https://github.com/ananddw24/safe_investment_researcher/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.5.0
[0.4.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.4.0
[0.3.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.3.0
[0.2.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.2.0
[0.1.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.1.0
