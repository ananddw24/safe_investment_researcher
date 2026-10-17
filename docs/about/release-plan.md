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

| Release | Scope |
| --- | --- |
| **v0.1.0** | Scaffold only (site shell, schemas, CI, community health) — shipped |
| **v0.2.0** | India household vehicles + core literacy guides + one pathway + verified resources |
| **v0.3.0** | United States + Kenya vehicle pages and resources |
| **v0.4.0** | Remaining Top 10 GDP countries as short vehicle pages |
| **v0.5.0** | Africa cluster: Nigeria, South Africa, Ghana, Egypt |
| **v1.0.0** | Stable contribution model, public Pages live, OpenSSF hygiene |

## Rules for every release

- Educational only — no personalized advice or product sales language
- Disclaimer on Guides, Vehicles, and Pathways
- Prefer government / regulator / NGO / multilateral sources
- Cite `source_type` and keep `last_checked` current for YAML resources
- Schema validation and `mkdocs build --strict` must pass before merge

## Current focus

**v0.2.0** is the first country seed (India). Later milestones are listed so
contributors know what *not* to bulk-add in this release.
