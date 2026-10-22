---
title: Release plan
description: Semver roadmap for FinancialLibrary content milestones
status: published
last_reviewed: "2026-10-17"
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
| **v0.2.0** | India household vehicles + guides + pathway + resources | Shipped |
| **v0.3.0** | United States + Kenya vehicle pages and resources | Shipped |
| **v0.4.0** | Remaining Top 10 GDP countries as short vehicle pages | Shipped |
| **v0.5.0** | Africa cluster: Nigeria, South Africa, Ghana, Egypt | Shipped |
| **v0.6.0** | Deep household vehicle pages for remaining Top 10 GDP economies (CN, DE, JP, GB, FR, IT, BR, CA) | Shipped (this release) |
| **v1.0.0** | Stable contribution model, public Pages live, OpenSSF hygiene | Planned |

## Rules for every release

- Educational only — no personalized advice or product sales language
- Disclaimer on Guides, Vehicles, and Pathways
- Prefer government / regulator / NGO / multilateral sources
- Cite `source_type` and keep `last_checked` current for YAML resources
- Schema validation and `mkdocs build --strict` must pass before merge

## Current focus

**v0.6.0** deepens Top 10 GDP vehicle prose for China, Germany, Japan, United
Kingdom, France, Italy, Brazil, and Canada (India, US, Kenya were already deep).
Africa cluster short pages remain for a future release. Do **not** start **v1.0.0**
in this release.
