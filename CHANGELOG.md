# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-10-22

### Added

- Docs hub for first-time readers: homepage country map (Top 10 + Africa),
  Start here path into guides and both pathways, Vehicles nav grouped by
  region
- Reader onboarding from PR #11: [Using this library](docs/about/using-this-library.md),
  [For educators and NGOs](docs/about/for-educators-and-ngos.md), and
  [New reader pathway](docs/pathways/new-reader.md)
- Generated [resource catalog](docs/resources/catalog.md) (`make catalog`) with
  CI freshness check; official-link sections on country vehicle indexes
- Deep household vehicle prose for remaining Top 10 GDP economies: China,
  Germany, Japan, United Kingdom, France, Italy, Brazil, and Canada (48 pages
  expanded with access, fee, fraud, and official-source literacy) — shipped in
  PR #11 and tagged with this release
- Knowledge-base layer: `llms.txt`, `docs/knowledge-base.md`,
  `data/kb-index.json`, `scripts/build_kb_index.py`,
  `scripts/staleness_report.py`, weekly maintenance workflow, pytest suite,
  `RELEASING.md`

### Changed

- Release plan matches reality through v0.5.0 and notes PR #11; v1.0.0 still
  waits on a public GitHub Pages site
- Guides, pathways, and audience pages cross-link Start here routes; woman-led
  pathway links Africa cluster peers without rewriting Kenya or India steps
- Softened “live site” claims until Pages is enabled by the owner
- `SECURITY.md` supported line covers `0.6.x`

### Fixed

- Changelog no longer has duplicate `[Unreleased]` blocks left from the PR #11
  merge window

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

[Unreleased]: https://github.com/ananddw24/safe_investment_researcher/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.6.0
[0.5.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.5.0
[0.4.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.4.0
[0.3.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.3.0
[0.2.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.2.0
[0.1.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.1.0
