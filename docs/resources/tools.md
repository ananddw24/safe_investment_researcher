---
title: Explore and tools
description: Interactive catalog explorer, emergency-fund and impact calendar calculators, and deposit-insurance source lookup
status: published
last_reviewed: "2026-11-11"
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
calculators only do arithmetic on numbers you type in.

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

</div>

<div id="fl-catalog" markdown="span">
<table markdown="span">
<thead markdown="0">
<tr><th>Title</th><th>Country</th><th>Type</th><th>Topics</th><th>Audience</th><th>Checked</th></tr>
</thead>
<tbody id="fl-catalog-body" markdown="span">
<tr markdown="span">
<td colspan="6" markdown="1">The interactive list needs JavaScript. The [static catalog](catalog.md) lists the same records without it.</td>
</tr>
</tbody>
</table>
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

## Impact calendar calculator

What does a small, regular amount add up to across real calendar time?
This calculator lays contributions onto an actual calendar, month by
month from a start date you choose, and shows the running totals plus
the month in which the total reaches each round-number milestone. Like
the emergency fund calculator above, it only does arithmetic on numbers
you type in — no figures come from the records, nothing is stored or
sent anywhere, and the result is an illustration, not advice. The
optional growth rate is an **assumption for illustration — not a
prediction or a promised return**; real savings and investments do not
grow in a smooth line.

<div class="fl-tools" markdown="0">

<form id="fl-ic-form">
<div class="fl-controls">
<div class="fl-field">
<label for="fl-ic-amount">Amount (your currency)</label>
<input id="fl-ic-amount" type="number" min="0" step="any" inputmode="decimal" value="10">
</div>
<div class="fl-field">
<label for="fl-ic-frequency">How often</label>
<select id="fl-ic-frequency">
<option value="day" selected>per day</option>
<option value="week">per week</option>
<option value="month">per month</option>
</select>
</div>
<div class="fl-field">
<label for="fl-ic-start">Start date</label>
<input id="fl-ic-start" type="date">
</div>
<div class="fl-field">
<label for="fl-ic-years">Time horizon: <span id="fl-ic-years-label">10 years</span></label>
<input id="fl-ic-years" type="range" min="1" max="40" step="1" value="10">
</div>
<div class="fl-field">
<label for="fl-ic-years-num">Horizon (years)</label>
<input id="fl-ic-years-num" type="number" min="1" max="40" step="1" value="10">
</div>
<div class="fl-field">
<label for="fl-ic-start-balance">Starting balance (optional)</label>
<input id="fl-ic-start-balance" type="number" min="0" step="any" inputmode="decimal" value="0">
</div>
<div class="fl-field">
<label for="fl-ic-growth">Growth assumption per year: <span id="fl-ic-growth-label">0%</span> — an assumption for illustration, not a prediction or a promised return</label>
<input id="fl-ic-growth" type="range" min="0" max="10" step="0.5" value="0">
</div>
</div>
</form>

<div class="fl-result" id="fl-ic-summary">This calculator needs JavaScript. It runs entirely in your browser; nothing is stored or sent anywhere.</div>

<div id="fl-ic-milestones"></div>

<details class="fl-ic-details">
<summary>Year by year</summary>
<div id="fl-ic-years-table"></div>
</details>

<details class="fl-ic-details">
<summary>Month by month</summary>
<div id="fl-ic-months-table"></div>
</details>

</div>

How the arithmetic works: contributions are counted by whole calendar
months from the start month — a daily amount is multiplied by the
number of days in each month, and a weekly amount by 52 ÷ 12 each
month. Growth, when set above zero, is applied each month at one
twelfth of the annual rate to the balance carried into that month,
before the month's contributions are added. Milestones are the first
month whose end-of-month total reaches each mark; marks a starting
balance has already passed are not listed. Amounts are shown with a $
sign; the arithmetic is the same in any currency.

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
