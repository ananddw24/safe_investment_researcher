# Educator example report — reading real bank filings (2026-10-30)

> **Educational only, not investment advice.** These figures teach how to read public
> data. They are not financial advice and not a recommendation to buy, sell, or hold any
> product. Re-check each figure at the official series linked in the table. The
> observation date is the series date. The report date is the pinned `--as-of` date.

The latest 10-K, 10-Q, and 8-K on or before 2026-10-30 for three large US banks, from
the SEC EDGAR submissions API. Rows are always in form order 10-K, 10-Q, 8-K. Each link
is the filing's primary document. Pair with library records `us-sec`, `us-fdic-deposit-
insurance`, and `us-occ`. Those records identify the institution; they do not store a
deposit-insurance dollar limit.

## JPMorgan Chase

| Form | Filed | What it is | Filing |
| --- | --- | --- | --- |
| 10-K | 2026-02-13 | Annual report (audited) | [EDGAR](https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/jpm-20251231.htm) |
| 10-Q | 2026-08-06 | Quarterly report | [EDGAR](https://www.sec.gov/Archives/edgar/data/19617/000162828026054343/jpm-20260630.htm) |
| 8-K | 2026-10-20 | Material event report | [EDGAR](https://www.sec.gov/Archives/edgar/data/19617/000119312526426704/d351999d8k.htm) |

## Bank of America

| Form | Filed | What it is | Filing |
| --- | --- | --- | --- |
| 10-K | 2026-02-25 | Annual report (audited) | [EDGAR](https://www.sec.gov/Archives/edgar/data/70858/000007085826000157/bac-20251231.htm) |
| 10-Q | 2026-07-31 | Quarterly report | [EDGAR](https://www.sec.gov/Archives/edgar/data/70858/000007085826000394/bac-20260630.htm) |
| 8-K | 2026-10-23 | Material event report | [EDGAR](https://www.sec.gov/Archives/edgar/data/70858/000119312526430566/d176604d8k.htm) |

## Wells Fargo

| Form | Filed | What it is | Filing |
| --- | --- | --- | --- |
| 10-K | 2026-02-24 | Annual report (audited) | [EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000007297126000133/wfc-20251231_d2.htm) |
| 10-Q | 2026-10-28 | Quarterly report | [EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000007297126000327/wfc-20260930.htm) |
| 8-K | 2026-10-13 | Material event report | [EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000007297126000318/wfc-20261013.htm) |

All requested series in this report were retrieved.

**Classroom prompt:** open one 10-K and find the balance sheet. Which line is customer
deposits? The FDIC record names the insurer and links to the official page. Read any
dollar limit on that page, and label the date you read it. The library record does not
store the limit.

Pinned report date: 2026-10-30. Generator seed: 0.