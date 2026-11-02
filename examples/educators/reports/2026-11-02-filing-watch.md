# Educator example report — reading real bank filings (2026-11-02)

> **Educational only, not investment advice.** These figures teach how to read public
> data. They are not financial advice and not a recommendation to buy, sell, or hold any
> product. Re-check each figure at the official series linked in the table. The
> observation date is the series date. The report date is the pinned `--as-of` date.

## What changed since the 2026-10-30 report

- **Bank of America 10-Q**: new quarterly report filed 2026-10-30 (period ending 2026-09-30). Previously the latest 10-Q was filed 2026-07-31 (period ending 2026-06-30).
- JPMorgan Chase and Wells Fargo: no new 10-K, 10-Q, or 8-K since the prior report.

## How to read this table

These are the latest 10-K, 10-Q, and 8-K on or before 2026-11-02 for three large US banks, from the SEC EDGAR submissions API.

- Rows are always in form order: **10-K** (annual, audited), **10-Q** (quarterly), **8-K** (material event).
- Each link goes to the filing’s primary document on EDGAR.
- Pair with library records `us-sec`, `us-fdic-deposit-insurance`, and `us-occ`. Those records identify the institution and its regulators/insurer; they do **not** store a deposit-insurance dollar limit. Students should look up the current limit on the official FDIC page and note the date they checked.

## The filings

### JPMorgan Chase

| Form | Filed | What it is | Filing |
| --- | --- | --- | --- |
| 10-K | 2026-02-13 | Annual report (audited) | [EDGAR](https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/jpm-20251231.htm) |
| 10-Q | 2026-08-06 | Quarterly report | [EDGAR](https://www.sec.gov/Archives/edgar/data/19617/000162828026054343/jpm-20260630.htm) |
| 8-K | 2026-10-20 | Material event report | [EDGAR](https://www.sec.gov/Archives/edgar/data/19617/000119312526426704/d351999d8k.htm) |

### Bank of America

| Form | Filed | What it is | Filing |
| --- | --- | --- | --- |
| 10-K | 2026-02-25 | Annual report (audited) | [EDGAR](https://www.sec.gov/Archives/edgar/data/70858/000007085826000157/bac-20251231.htm) |
| 10-Q | **2026-10-30** | Quarterly report | [EDGAR](https://www.sec.gov/Archives/edgar/data/70858/000007085826000548/bac-20260930.htm) |
| 8-K | 2026-10-23 | Material event report | [EDGAR](https://www.sec.gov/Archives/edgar/data/70858/000119312526430566/d176604d8k.htm) |

### Wells Fargo

| Form | Filed | What it is | Filing |
| --- | --- | --- | --- |
| 10-K | 2026-02-24 | Annual report (audited) | [EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000007297126000133/wfc-20251231_d2.htm) |
| 10-Q | 2026-10-28 | Quarterly report | [EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000007297126000327/wfc-20260930.htm) |
| 8-K | 2026-10-13 | Material event report | [EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000007297126000318/wfc-20261013.htm) |

All requested series in this report were retrieved.

## Classroom prompts

1. **Open a 10-K.** Choose one bank’s annual report and locate the consolidated balance sheet. Identify the line that represents customer deposits. Note the period end date of the report.
2. **Check the insurer.** Use the library’s FDIC record to find the official page. Look up the current deposit-insurance limit, then write both the limit and the date you read it. Observe that the library record itself does not store the dollar limit.
3. **Compare freshness.** Which bank has the newest 10-Q? What reporting period does it cover? Why might a class care about the difference between a filing date and a period-end date?

## Teacher notes

- The new Bank of America 10-Q is the clearest “something changed” item this week. Have students open both the new and prior 10-Q (if available) and notice the period-end dates.
- Emphasize that 8-Ks are event-driven; their content varies widely. A useful exercise is to open one 8-K and summarize the event in one sentence without interpreting its importance.
- Keep the focus on *how to find and read* public filings, not on any bank’s prospects.

Pinned report date: 2026-11-02. Generator seed: 0.
