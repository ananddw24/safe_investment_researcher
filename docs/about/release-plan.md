---
title: Release plan
description: Semver roadmap for FinancialLibrary content milestones
status: published
last_reviewed: "2026-10-22"
---

# Release plan

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.


This project ships educational content in small, reviewable releases. Tags use
semantic versioning. Force-push is forbidden on `main` and on published tags.

## Sequence

| Release | Scope | Status |
| --- | --- | --- |
| **v0.1.0** | Scaffold only | Shipped |
| **v0.2.0** | India household vehicles + 3 literacy guides + woman-led pathway + resources | Shipped |
| **v0.3.0** | United States + Kenya vehicle pages and resources | Shipped |
| **v0.4.0** | Remaining Top 10 GDP countries as short vehicle pages | Shipped |
| **v0.5.0** | Africa cluster: Nigeria, South Africa, Ghana, Egypt (Kenya linked) | Shipped |
| **v0.6.0** | Docs hub: coverage map, Start here paths; consolidates PR #11 reader pages + deep Top 10 prose | Shipped (this release) |
| **v1.0.0** | Stable contribution model, **public Pages live**, OpenSSF hygiene | Planned — waits on a public site |

## What each content release already shipped

- **v0.2.0** — India vehicles; guides (emergency savings, inflation, unregulated
  schemes); woman-led household pathway; verified India resources
- **v0.3.0** — United States and Kenya vehicles + resources
- **v0.4.0** — China, Germany, Japan, UK, France, Italy, Brazil, Canada (short)
- **v0.5.0** — Nigeria, South Africa, Ghana, Egypt (short); Kenya not rewritten
- **PR #11** (merged before the v0.6.0 tag) — reader onboarding (*Using this
  library*, educators/NGOs page, new-reader pathway), generated resource
  catalog, knowledge-base index, and deep prose for CN/DE/JP/GB/FR/IT/BR/CA

## Rules for every release

- Educational only — no personalized advice or product sales language
- Disclaimer on Guides, Vehicles, and Pathways
- Prefer government / regulator / NGO / multilateral sources
- Cite `source_type` and keep `last_checked` current for YAML resources
- Schema validation and `mkdocs build --strict` must pass before merge

## Current focus

**v0.6.0** makes shipped coverage easy to find for first-time readers. It does
**not** add new country research. **v1.0.0** remains planned until the
repository is public and GitHub Pages is enabled by the owner.
