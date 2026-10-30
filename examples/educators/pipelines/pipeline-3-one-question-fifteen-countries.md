# Pipeline 3 — One question, fifteen countries

> **Educational only, not investment advice.** The table compares
> published inflation series with library records. It is not financial
> advice and not a ranking of where someone should keep money.

**Lesson goal:** comparative institutions. A class asks one question
— "how high is inflation, and who insures deposits?" — across the
15 countries with household vehicle pages, and learns that the honest
answer mixes live data, curated records, and admitted gaps.

The catalog's `list_countries` result also includes `global`, a bucket
for multilateral records. That bucket is not a sixteenth country.

**Servers:** FinancialLibrary + IMF. **Time:** ~40 minutes.
**Output:** a comparison table in the shape of the world-snapshot
report in [`reports/`](../reports/). The pre-generated world snapshot
uses World Bank `FP.CPI.TOTL.ZG` (annual). This live exercise uses IMF
database `CPI`. Those are different series; do not mix the numbers
without saying which source and which period. Euro-area variant: add
the EU Finance pilot server (`get_ecb_rates`, `get_eu_inflation`) for
Germany, France and Italy.

## Prompt sequence

1. *Library:* "Use `list_countries`. Set aside `global`. For three
   household countries I choose, use `get_catalog` filtered by country
   and find each one's deposit-insurance record (or say plainly that
   none exists yet)."
2. *IMF:* "Use `imf_search_databases` for consumer prices, then
   `imf_fetch_data` on database id `CPI` for the same three countries.
   Return the latest period and say whether it is monthly or annual.
   One source, one definition, three countries."
3. *Combine:* "Build the table: country | latest inflation (IMF,
   database `CPI`, period) | deposit insurer (library record title) |
   insured limit only if you opened the record's `source_url` and read
   it there, with that date | the record's `last_checked` date. Where
   a cell has no source, write 'not covered' — do not fill it from
   memory. The library records do not store coverage amounts."
4. *Argue:* "Which country's saver is best protected against (a)
   inflation and (b) a bank failure? Defend each answer with one
   figure and one record — and state what extra fact would change
   your answer. Do not turn the answer into advice to move money."

## Guardrails

- "Not covered" is a correct answer. The library's gaps are part of
  the curriculum: they show what curation costs and why freshness
  dates exist.
- IMF figures must carry database id `CPI` and their period. Annual
  and monthly inflation are different claims, and both differ from the
  World Bank annual series in the pre-generated report.
- The composed configs pin the IMF server to commit
  `316fcb14c33fc15afd54f6620a6a240143ef5d35`. Keep that pin so the
  lesson is reproducible.
