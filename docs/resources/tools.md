---
title: Explore and tools
description: Interactive catalog explorer, emergency-fund calculator, and deposit-insurance source lookup
status: published
last_reviewed: "2026-10-27"
---

# Explore and tools

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

Small interactive tools built on the same curated records as the
[resource catalog](catalog.md). Nothing on this page invents figures:
the explorer and the lookup read a data file generated from the records
(`scripts/generate_interactive_data.py`, from `data/kb-index.json`), and the
calculator only does arithmetic on numbers you type in.

## Explore the catalog

Filter the library's curated official links by country, topic, and audience.
If the interactive list does not load (for example with JavaScript off), the
[static catalog](catalog.md) has the same records in plain tables.

<div class="fl-tools" data-fl-data-url="../../assets/data/library-data.json" markdown="0">

<div class="fl-controls">
<div class="fl-field">
<label for="fl-filter-country">Country</label>
<select id="fl-filter-country"><option value="">All countries</option></select>
</div>
<div class="fl-field">
<label for="fl-filter-topic">Topic</label>
<select id="fl-filter-topic"><option value="">All topics</option></select>
</div>
<div class="fl-field">
<label for="fl-filter-audience">Audience</label>
<select id="fl-filter-audience"><option value="">All audiences</option></select>
</div>
<div class="fl-field">
<label for="fl-filter-search">Search titles</label>
<input id="fl-filter-search" type="search" placeholder="e.g. deposit, pension, women">
</div>
<button id="fl-filter-reset" type="button">Reset filters</button>
</div>

<p class="fl-count" id="fl-catalog-count">Loading the catalog data…</p>

<div id="fl-catalog">
<table>
<thead>
<tr><th>Title</th><th>Country</th><th>Type</th><th>Topics</th><th>Audience</th><th>Checked</th></tr>
</thead>
<tbody id="fl-catalog-body">
<tr><td colspan="6">The interactive list needs JavaScript. The <a href="../catalog/">static catalog</a> lists the same records without it.</td></tr>
</tbody>
</table>
</div>

</div>

## Emergency fund target calculator

The [emergency savings guide](../guides/emergency-savings.md) suggests
building a cushion of a few months of **essential** expenses. This calculator
turns that idea into a number using only your own inputs — it is a planning
illustration, not advice, and it stores nothing.

<div class="fl-tools" markdown="0">

<form id="fl-ef-form">
<div class="fl-controls">
<div class="fl-field">
<label for="fl-ef-expenses">Monthly essential expenses (your currency)</label>
<input id="fl-ef-expenses" type="number" min="0" step="any" inputmode="decimal" placeholder="e.g. 1200">
</div>
<div class="fl-field">
<label for="fl-ef-months">Months of cover: <span id="fl-ef-months-label">3 months</span></label>
<input id="fl-ef-months" type="range" min="1" max="12" step="1" value="3">
</div>
</div>
<p class="fl-result" id="fl-ef-result">Enter your monthly essential expenses to see the target.</p>
</form>

</div>

## Deposit insurance — official sources

Does the library hold an official deposit-insurance source for your country?
Pick a country to find out. The records identify the official scheme source
and when it was last checked; they do **not** store coverage-limit amounts,
so no limit is shown here — always confirm the current limit on the official
site. See also [Where to check official figures](../about/where-to-check.md).

<div class="fl-tools" markdown="0">

<div class="fl-controls">
<div class="fl-field">
<label for="fl-di-country">Country</label>
<select id="fl-di-country"><option value="">Choose a country…</option></select>
</div>
</div>

<div class="fl-result" id="fl-di-result"></div>

</div>
