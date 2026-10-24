---
title: Release plan
description: Semver roadmap for FinancialLibrary content milestones
status: published
last_reviewed: "2026-10-24"
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
| **v0.6.0** | Docs hub: coverage map, Start here paths; consolidates PR #11 reader pages + deep Top 10 prose | Shipped |
| **v0.7.0** | Facilitator training, glossary, where-to-check official figures, weekly update PR workflow | This release (mark Shipped only after tag `v0.7.0`) |
| **v1.0.0** | Stable contribution model + public-site hygiene (OpenSSF and contribution polish) | Planned |

## What each content release already shipped

- **v0.2.0** — India vehicles; guides; woman-led pathway; verified India resources
- **v0.3.0** — United States and Kenya vehicles + resources
- **v0.4.0** — China, Germany, Japan, UK, France, Italy, Brazil, Canada (short)
- **v0.5.0** — Nigeria, South Africa, Ghana, Egypt (short); Kenya not rewritten
- **v0.6.0** — Docs hub + PR #11 onboarding, catalog, and deep Top 10 prose
- **v0.7.0** — Community training sessions; glossary; where-to-check; weekly PR automation

## Rules for every release

- Educational only — no personalized advice or product sales language
- Disclaimer on Guides, Vehicles, Pathways, and Training
- Prefer government / regulator / NGO / multilateral sources
- Cite `source_type` and keep `last_checked` current for YAML resources
- Schema validation and `mkdocs build --strict` must pass before merge

## Current focus

**v0.7.0** helps facilitators run workshops from existing pages and keeps
official-figure links maintainable via a weekly pull request — never a silent
push to `main`. **v1.0.0** remains for contribution-model and OpenSSF polish
after the public site is already live.
