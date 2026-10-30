# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-10-29

### Added

- **MCP ecosystem composition** (`mcp-server/ECOSYSTEM.md`,
  `mcp-server/configs/`): a curated set of free, live-data MCP servers
  that pair with FinancialLibrary — FRED and SEC EDGAR (Amorelli) and
  IMF Data (c-cf) as the core, Alpha Vantage as a licensed optional,
  EU Finance as a pilot, OpenBB as an advanced alternative — with
  ready-to-paste Claude Desktop and Cursor configurations, key-hygiene
  and licensing rules (AGPL servers run unmodified; every user holds
  their own free keys), and named exclusions (Yahoo Finance data is
  personal-use only; Financial Datasets is not free). The MCP server
  gains a seventh tool, `list_ecosystem_servers`, serving the same
  curated list (server package 0.2.0)
- **Educator examples** (`examples/educators/`): three worked example
  reports generated from live, keyless official data — a US macro
  snapshot (FRED), a real-bank-filing watch (SEC EDGAR), and a World
  Bank snapshot of the library's countries — plus three reusable
  classroom pipelines (weekly rates brief; read a real filing; one
  question, sixteen countries) and a new **Educator examples** guide
  page. Reports are refreshed weekly by
  `scripts/generate_educator_reports.py`, driven by a Muse job that
  opens a pull request for human review

## [1.1.0] - 2026-10-29

### Added

- Guide **Talk to the library** (`docs/guides/talk-to-the-library.md`):
  collaborator steps for Claude Desktop (local MCP config), a short Cursor
  pointer to `mcp-server/README.md`, plain limits for ChatGPT and Grok apps
  that cannot attach this stdio server yet, three example questions, and the
  educational disclaimer; linked from the homepage and Guides nav
- **MCP server** (`mcp-server/`): read-only Model Context Protocol server
  (stdio, official Python SDK) exposing the library's YAML records to
  Claude Desktop, Cursor, and other MCP clients — six tools
  (`search_records`, `get_record`, `get_catalog`, `list_countries`,
  `list_topics`, `library_status`), with educational-only instructions
  and source-URL citation required. See `mcp-server/README.md`.
- Interactive **Explore and tools** page (`docs/resources/tools.md`):
  a filterable catalog explorer (country, topic, audience, title search)
  over the curated records; an emergency-fund target calculator that does
  arithmetic on visitor inputs only (planning illustration, not advice);
  and a deposit-insurance source lookup. The lookup shows only what the
  records hold — the official insurer source and its last-checked date —
  and plainly marks countries not yet covered; coverage-limit amounts are
  never shown because the records do not store them
- `scripts/generate_interactive_data.py`, generating
  `docs/assets/data/library-data.json` from `data/kb-index.json` for the
  tools page; `extra_javascript` / `extra_css` wiring in `mkdocs.yml`
  (`docs/assets/javascripts/interactive.js`,
  `docs/assets/stylesheets/interactive.css`). With JavaScript off, the
  static catalog remains fully readable

### Changed

- Exclude contributor `_template.md` pages from the published MkDocs site so
  readers do not land on stubs; templates remain in-repo for contributors

## [1.0.0] - 2026-10-27

### Added

- Public-release README: mission, audience (low-income households and women),
  educational disclaimer, live site URL, and outsider contribution path

### Changed

- Release plan marks v0.7.0 shipped and positions **v1.0.0** as the public
  educational release of coverage through training sessions, glossary,
  where-to-check, and the weekly update job
- Homepage status reflects v1.0.0 and the live Pages URL

### Notes

- Coverage through v0.7.0 remains: Top 10 GDP + Africa cluster vehicles, three
  literacy guides, community training sessions, weekly maintenance PRs
- External catalog [toddrjones/datasets](https://github.com/toddrjones/datasets)
  was reviewed and **not** integrated (including no CPI-U / SCF links)

## [0.7.0] - 2026-10-24

### Added

- Community training: three 75-minute facilitator session plans under
  `docs/training/` (emergency savings, inflation, unregulated schemes) plus
  facilitator index; woman-led pathway linked as optional discussion only
- [Glossary](docs/glossary.md) for terms already used (inflation, liquidity,
  emergency fund, regulated vs unregulated, and related)
- [Where to check official figures](docs/about/where-to-check.md) — dated
  publisher links only; no invented rates or forecasts
- `.github/workflows/weekly-update.yml` (Monday 13:00 UTC) opens a PR or issue;
  never pushes to `main`. Helper `scripts/weekly_where_to_check.py`

### Changed

- Plain-language accessibility pass on homepage, Start here, and the three
  guides; site `theme.language: en`
- Existing `weekly-maintenance.yml` proposes a PR for catalog/index refresh
  instead of pushing to `main`
- Release plan adds v0.7.0; v1.0.0 remains contribution/OpenSSF polish

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

[Unreleased]: https://github.com/ananddw24/safe_investment_researcher/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/ananddw24/safe_investment_researcher/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v1.1.0
[1.0.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v1.0.0
[0.7.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.7.0
[0.6.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.6.0
[0.5.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.5.0
[0.4.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.4.0
[0.3.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.3.0
[0.2.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.2.0
[0.1.0]: https://github.com/ananddw24/safe_investment_researcher/releases/tag/v0.1.0
