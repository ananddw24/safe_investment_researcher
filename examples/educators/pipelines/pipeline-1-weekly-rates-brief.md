# Pipeline 1 — The weekly rates brief

> **Educational only, not investment advice.** The brief explains public
> series. It is not financial advice and must not recommend an account
> or a product.

**Lesson goal:** a class leaves able to say what the policy rate is,
what inflation did, and *which institution is responsible for each
number* — and to notice when a savings account's advertised rate does
not move with the policy rate.

**Servers:** FinancialLibrary + FRED (`configs/` in
[`mcp-server/`](../../mcp-server/)). Each student (or the teacher's
machine) uses their **own free FRED key**.

**Time:** ~30 minutes. **Output:** a one-page brief in the shape of
[`reports/latest.md`](../reports/) → the macro snapshot.

## Prompt sequence

1. *Library:* "Use `search_records` for the US central bank and the US
   deposit insurer. For each, give me the title, what the institution
   does in one sentence, and the `source_url`."
2. *FRED:* "Using `fred_get_series` (Amorelli server) or
   `fred_series_observations` (MIT alternative), get the latest values
   and dates for `DFEDTARL`, `DFEDTARU`, `FEDFUNDS`, `CPIAUCSL`
   (12-month percent change computed from the index, and say whether
   the index is seasonally adjusted), `UNRATE`, `DGS10` and `PSAVERT`.
   Present them as a table with the series id and the observation date
   for each. Label `DFEDTARL`–`DFEDTARU` as the target range the FOMC
   sets, and `FEDFUNDS` as the monthly average effective rate."
3. *Combine:* "Write a five-sentence brief for a saver: what the
   policy rate and saving rate are doing, and one question a saver
   should ask their bank this week. Cite the library record for every
   institutional claim and FRED for every figure."
4. *Argue:* "Find one savings or money-market rate advertised today.
   Compare it with `FEDFUNDS`. List two reasons the two numbers
   differ, and say which reason the evidence supports."

## Guardrails

- Figures without a FRED series id and date don't count — send the
  student back for them.
- The brief must not recommend any account or product; if the model
  drifts into advice, that's the teachable moment: re-run step 3 with
  "explain only, recommend nothing" appended.
