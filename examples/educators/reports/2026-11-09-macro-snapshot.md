# Educator example report — US macro snapshot (2026-11-09)

> **Educational only, not investment advice.** These figures teach how to read public
> data. They are not financial advice and not a recommendation to buy, sell, or hold any
> product. Re-check each figure at the official series linked in the table. The
> observation date is the series date. The report date is the pinned `--as-of` date.

## What changed since the 2026-11-02 report

| Series | Previous (2026-11-02) | This report (2026-11-09) | Note |
| --- | --- | --- | --- |
| DFEDTARL / DFEDTARU | 3.75–4.00% | 3.75–4.00% | Target range unchanged; observation date rolled forward |
| FEDFUNDS | 3.75% (2026-09-01) | **3.88% (2026-10-01)** | New October monthly average |
| UNRATE | 4.2% (2026-09-01) | **4.1% (2026-10-01)** | New October observation; modest decline |
| DGS10 (10-year Treasury) | 4.98% (2026-10-29) | **4.84% (2026-11-05)** | Decline continues |
| PSAVERT, CPI | Unchanged | Unchanged | Still on September 2026 observations |

## How to read this snapshot

Readings come from the Federal Reserve Bank of St. Louis (FRED). Only observations on or before 2026-11-09 are used.

- The **FOMC sets the target range** (`DFEDTARL`–`DFEDTARU`). This is a policy decision.
- `FEDFUNDS` is the **monthly average effective rate** in the market, not the target. It often lands inside the range but can differ.
- CPI percent changes shown here are **computed from the index levels** (12-month change). They are not a separate published percent series.
- Several series are **monthly** and lag the report date: FEDFUNDS and UNRATE now show October 2026 data, while PSAVERT and CPI still show September 2026 data. The report date does not mean every series is current as of 9 November.

Pair this page with the library records `us-federal-reserve`, `us-fdic-deposit-insurance`, and `us-cfpb`.

## The numbers

| Series | Series ID | Latest value | Observation date | Source |
| --- | --- | --- | --- | --- |
| Federal funds target range, lower bound | DFEDTARL | 3.75% | 2026-11-09 | [FRED DFEDTARL](https://fred.stlouisfed.org/series/DFEDTARL) |
| Federal funds target range, upper bound | DFEDTARU | 4.00% | 2026-11-09 | [FRED DFEDTARU](https://fred.stlouisfed.org/series/DFEDTARU) |
| Federal funds effective rate, monthly average | FEDFUNDS | 3.88% | 2026-10-01 | [FRED FEDFUNDS](https://fred.stlouisfed.org/series/FEDFUNDS) |
| Unemployment rate | UNRATE | 4.1% | 2026-10-01 | [FRED UNRATE](https://fred.stlouisfed.org/series/UNRATE) |
| 10-year Treasury constant maturity rate | DGS10 | 4.84% | 2026-11-05 | [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) |
| Personal saving rate | PSAVERT | 3.8% | 2026-09-01 | [FRED PSAVERT](https://fred.stlouisfed.org/series/PSAVERT) |
| Consumer Price Index, seasonally adjusted, 12-month percent change computed from the index | CPIAUCSL | 3.7% | 2026-09-01 index 336.298 vs 2025-09-01 index 324.245 | [FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL) |
| Consumer Price Index, not seasonally adjusted, 12-month percent change computed from the index | CPIAUCNS | 3.7% | 2026-09-01 index 336.940 vs 2025-09-01 index 324.800 | [FRED CPIAUCNS](https://fred.stlouisfed.org/series/CPIAUCNS) |

All requested series in this report were retrieved.

## Classroom prompts

1. **Identify the roles.** Which number did the FOMC set? Which number is a market average? Why might they differ even when the target range has not changed?
2. **Compare with a real advertisement.** Find one savings or money-market rate
   advertised this week. Place it next to the target range. List two possible reasons
   for any gap (for example: timing of the advertisement, product features, or how
   the rate is calculated). Do not treat any gap as a recommendation.
3. **Notice the lags.** Which series have moved on to October data, and which are still showing September data? What does that tell you about how “current” a macro snapshot can be?

## Teacher notes

- Use the “what changed” table to show students that some series move daily while others update only monthly — this week FEDFUNDS and UNRATE rolled to October, while PSAVERT and CPI did not.
- The 10-year Treasury decline from 4.98% to 4.84% is the clearest daily-series move; the teaching point is that market rates can move independently of the policy target, which was unchanged.
- Keep the discussion on *reading* the data, not on what anyone should do with their money.

Pinned report date: 2026-11-09. Generator seed: 0.
