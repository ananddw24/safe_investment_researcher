# Pipeline 2 — Read a real bank filing

> **Educational only, not investment advice.** Reading a filing is
> practice in finding a published number. It is not financial advice
> and not a view on the bank.

**Lesson goal:** demystify the 10-K. A class opens one real annual
report, finds the balance sheet, and connects the deposits line to
the deposit-insurance record they read first.

**Servers:** FinancialLibrary + SEC EDGAR (no key; the config carries
a declared `SEC_EDGAR_USER_AGENT`). **Time:** ~45 minutes.
**Output:** an annotated one-pager in the shape of the filing-watch
report in [`reports/`](../reports/).

## Prompt sequence

1. *Library:* "Use `get_record` for `us-fdic-deposit-insurance` and
   `us-sec`. What does each institution do? Cite both `source_url`s.
   The deposit-insurance record does not store a dollar limit. If the
   class wants the limit, open the FDIC page in `source_url` and quote
   the figure with the date you read it."
2. *EDGAR:* "Using `get_recent_filings` for CIK 0000019617 (JPMorgan
   Chase), list the most recent 10-K, 10-Q and 8-K with filing dates
   and links. Do not invent a tool name."
3. *EDGAR:* "From the latest 10-K, extract the balance-sheet totals:
   total assets, total deposits, total liabilities. Give the filing
   section each number came from."
4. *Combine:* "The deposits figure you found is the pool the FDIC
   insures bank-by-bank up to the limit from step 1. Explain in three
   sentences why a depositor with less than the limit does not need
   to read a 10-K to be safe — and one thing the 10-K still tells
   them that insurance does not."
5. *Extend (optional):* repeat steps 2–3 for Bank of America and
   Wells Fargo; tabulate the three deposit totals with filing dates.

## Guardrails

- Extract sections and statements; never paste a whole 10-K into the
  session — it is enormous and the lesson is navigation, not volume.
- Every figure needs its form, filing date and section. A number
  without a provenance line is treated as unwritten.
- Respect EDGAR fair access: under 10 requests/second, declared user
  agent — the shipped config already does this.
