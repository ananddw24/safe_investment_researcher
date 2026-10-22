---
title: For educators and NGOs
description: Reusing FinancialLibrary in programs and materials
status: published
last_reviewed: "2026-10-22"
---

# For educators and NGOs

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

FinancialLibrary is designed to be **forked, cited, and adapted** in classrooms,
self-help groups, and NGO programs — without turning into product sales or
personalized advice.

## What you can reuse

| Material | License | Typical use |
| --- | --- | --- |
| Prose in `docs/` (guides, vehicles, pathways) | [CC BY 4.0](licenses.md) | Handouts, LMS modules, workshop slides (with attribution) |
| Curated link metadata in `data/resources/` | CC BY 4.0 | Program resource lists, intranet link hubs |
| Code, schemas, scripts | MIT | Pipelines that validate or mirror the YAML |

Attribution example: “Adapted from FinancialLibrary (CC BY 4.0),
https://ananddw24.github.io/safe_investment_researcher/”.

## How to build a session

1. Pick a **[pathway](../pathways/index.md)** or compose your own sequence from
   [guides](../guides/index.md) + one [country](../vehicles/index.md).
2. Pair every vehicle page with **official links** from the
   [resource catalog](../resources/catalog.md) for that country.
3. Keep the **disclaimer** visible: literacy only, not advice for a specific
   person. The standard admonition text is on every content page.
4. Avoid quizzes that imply “the right product” for a participant — focus on
   access, liquidity, fees, documentation, and scam red flags.

## Woman-led and low-income framing

The project prioritizes barriers around **access, documentation, fees, and
control of accounts** — not investment outperformance. The
[woman-led household pathway](../pathways/woman-led-household.md) is one
example ordering; localize with your country’s vehicle index when you teach
outside India.

## Staying current

Resource records include a `last_checked` date. Before you cite a figure or
policy detail in a printed curriculum, open the **official URL** and confirm
it still matches. You can run `python scripts/staleness_report.py` locally to
see aging records.

## Contribute back

Corrections and new official links help everyone. See
[Contributing](../contributing.md) — small YAML additions are the preferred
first contribution.
