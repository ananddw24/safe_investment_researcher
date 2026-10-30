# Pipeline 3 — One question, sixteen countries

**Lesson goal:** comparative institutions. A class asks one question
— "how high is inflation, and who insures deposits?" — across the
countries the library covers, and learns that the honest answer mixes
live data, curated records, and admitted gaps.

**Servers:** FinancialLibrary + IMF. **Time:** ~40 minutes.
**Output:** a comparison table in the shape of the world-snapshot
report in [`reports/`](../reports/). Euro-area variant: add the EU
Finance pilot server (ECB rates, Eurostat HICP) for Germany, France
and Italy.

## Prompt sequence

1. *Library:* "Use `list_countries`. For three countries I choose,
   use `get_catalog` filtered by country and find each one's
   deposit-insurance record (or say plainly that none exists yet)."
2. *IMF:* "For the same three countries, fetch the latest CPI
   inflation (database CPI) with its period. One source, one
   definition, three countries."
3. *Combine:* "Build the table: country | latest inflation (IMF,
   period) | deposit insurer (library record title) | insured limit
   as the record states it | the record's `last_checked` date. Where
   a cell has no source, write 'not covered' — do not fill it from
   memory."
4. *Argue:* "Which country's saver is best protected against (a)
   inflation and (b) a bank failure? Defend each answer with one
   figure and one record — and state what extra fact would change
   your answer."

## Guardrails

- "Not covered" is a correct answer. The library's gaps are part of
  the curriculum: they show what curation costs and why freshness
  dates exist.
- IMF figures must carry their period; annual and monthly inflation
  are different claims.
- Pin the IMF server to a reviewed commit in class configs (see
  `mcp-server/ECOSYSTEM.md`) so the lesson is reproducible.
