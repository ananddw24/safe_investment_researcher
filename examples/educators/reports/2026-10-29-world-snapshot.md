# Educator example report — the library's countries in World Bank data (2026-10-29)

> **Educational only, not investment advice.** Not financial advice.
> This file no longer carries a data table.

Checked on 2026-10-30, the table first published with this date was
incomplete and is withdrawn.

- Inflation (`FP.CPI.TOTL.ZG`) stopped after 500 historical rows, so
  Italy, Japan, Kenya, Nigeria, South Africa, the United States, and
  Egypt were missing. Egypt was also absent from the country list.
  The eight values that did appear matched the World Bank's 2025
  figures at one decimal place.
- Account ownership used indicator `account.t.d`. That series returns
  ISO3 country ids, and the generator looked them up as ISO2, so every
  row was dropped and the table was empty. The canonical series is
  `FX.OWN.TOTL.ZS`.

Use [2026-10-30-world-snapshot.md](2026-10-30-world-snapshot.md).
