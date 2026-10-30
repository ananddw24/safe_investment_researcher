---
title: Cross-country inflation
description: Compare World Bank and IMF inflation readings for the library's household countries
audience: [educators, general]
topics: [inflation, cross-country]
status: published
last_reviewed: "2026-10-30"
---

# Cross-country inflation

!!! warning "Educational only"
    This page is for financial literacy. It is **not** personalized advice,
    an offer to sell, or a recommendation to buy, sell, or hold any product.
    Rules differ by country; verify with official sources in your jurisdiction.

Two official compilers publish annual inflation for the same countries. The numbers do not have
to match. This module puts them side by side for the countries in this library. It does not rank
places to put money, and it does not average the two sources into a single true rate.

## Learning objectives

1. Read an annual inflation bar as one official series for one year, with the year attached.
2. Treat a missing country as a gap, not as zero.
3. Label IMF values for years that were not finished on the retrieval date as unpublished
   outcomes.

## The picture

![Horizontal bars of 2025 World Bank inflation. Highest among those plotted: Nigeria at 23.0 percent.](figures/cross-country-wb-inflation.svg){.teaching-figure}

Caption: World Bank indicator `FP.CPI.TOTL.ZG` for 2025, the last complete calendar year on
2026-10-30. Countries with no 2025 value in this snapshot: United States. They are omitted. They
are not zero.

PNG of the same chart: [download](figures/cross-country-wb-inflation.png).

![Paired 2024 inflation bars. Solid: World Bank. Hatched: IMF. Highest World Bank: Nigeria 33.2%.](figures/cross-country-wb-imf.svg){.teaching-figure}

Caption: Solid bars are the World Bank. Hatched bars are IMF DataMapper `PCPIPCH` for 2024, the
latest year in this snapshot where every library country has both. The series measure related
prices differently. A gap between bars is not a data-entry error by itself.

PNG of the same chart: [download](figures/cross-country-wb-imf.png).

## Explainer

The World Bank indicator name in the snapshot is: Inflation, consumer prices (annual %). The IMF
metadata in the snapshot calls `PCPIPCH` "Inflation rate, average consumer prices" (Annual
percent change), source "World Economic Outlook (October 2026)".

On the 2025 World Bank chart, the highest value among the countries that have a number is
Nigeria, 23.0 percent. The unrounded snapshot value is 23.0101235833333. The United States'
latest World Bank observation in this pull is 2024: 2.94952520485207.

The IMF series in the file runs past 2025, through later years including 2031. The metadata does
not mark each year as an actual or a projection. This module plots only through 2025, the last
calendar year that had ended on 2026-10-30. Values for later years are in the table below and in
the snapshot. Read them as numbers the October 2026 World Economic Outlook vintage published for
years that were not finished on the retrieval date, not as measured inflation.

For Nigeria in 2024, the World Bank value is 33.2416590552748 and the IMF value is 33.2. Use the
comparison chart and the table for every country. Do not average the pair.

## Years not complete on the retrieval date

IMF `PCPIPCH` for 2026, the first year that was not finished on 2026-10-30. These are not
plotted on the history charts.

| Country | ISO3 | Year | IMF PCPIPCH |
| --- | --- | --- | --- |
| Brazil | BRA | 2026 | 4.4 |
| Canada | CAN | 2026 | 2.8 |
| China | CHN | 2026 | 1 |
| Egypt | EGY | 2026 | 13.3 |
| France | FRA | 2026 | 2.4 |
| Germany | DEU | 2026 | 2.7 |
| Ghana | GHA | 2026 | 4.8 |
| India | IND | 2026 | 5 |
| Italy | ITA | 2026 | 3.3 |
| Japan | JPN | 2026 | 2 |
| Kenya | KEN | 2026 | 6 |
| Nigeria | NGA | 2026 | 15.6 |
| South Africa | ZAF | 2026 | 4.4 |
| United Kingdom | GBR | 2026 | 3.3 |
| United States | USA | 2026 | 3.6 |

## Discussion questions

1. Pick a country where the two bars differ. What are two reasons official inflation measures
   can differ without either number being a typo?
2. A country is missing from the latest-year chart. What should you do instead of treating the
   gap as zero?
3. How should a class label an IMF cell for a year that was not finished on the retrieval date?

## Exercise

On the 2025 World Bank chart, which plotted country is highest, and what is that value rounded
half up to one decimal place? Also write the unrounded snapshot value. If a library country is
missing, name it and do not treat it as zero.

## Answer key

Discussion questions stay open. This key answers the exercise only.

<details markdown="1">
<summary>Show the answer key</summary>

The highest plotted World Bank value for 2025 is Nigeria (`NGA`), 23.0 percent, from the
unrounded snapshot value 23.0101235833333 (`FP.CPI.TOTL.ZG`). Missing in 2025: United States. A
higher inflation reading is not a verdict on a country and not a product suggestion.

</details>

## Sources and citations

Retrieved 2026-10-30. World Bank indicator page and IMF DataMapper page are linked below. The
exact API requests are in the manifest and in the code block.

| Publisher | ID | What the snapshot calls it | Page |
| --- | --- | --- | --- |
| World Bank | FP.CPI.TOTL.ZG | Inflation, consumer prices (annual %) | [Indicator](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG) |
| IMF DataMapper | PCPIPCH | Inflation rate, average consumer prices; World Economic Outlook (October 2026) | [DataMapper](https://www.imf.org/external/datamapper/PCPIPCH) |

World Bank 2025 values in this snapshot, unrounded:

| Country | ISO3 | Year | Value |
| --- | --- | --- | --- |
| Brazil | BRA | 2025 | 5.01675279604836 |
| Canada | CAN | 2025 | 2.07232411149103 |
| China | CHN | 2025 | 0.0595646916565402 |
| Egypt | EGY | 2025 | 14.0735136645933 |
| France | FRA | 2025 | 0.943824761520197 |
| Germany | DEU | 2025 | 2.17178770949721 |
| Ghana | GHA | 2025 | 14.2046755548989 |
| India | IND | 2025 | 2.39884954182294 |
| Italy | ITA | 2025 | 1.5316735709312 |
| Japan | JPN | 2025 | 3.17253034260247 |
| Kenya | KEN | 2025 | 4.0693076061457 |
| Nigeria | NGA | 2025 | 23.0101235833333 |
| South Africa | ZAF | 2025 | 3.20550474112603 |
| United Kingdom | GBR | 2025 | 3.88306881625999 |

Comparison year 2024, unrounded World Bank value and IMF value:

| Country | ISO3 | World Bank | IMF PCPIPCH |
| --- | --- | --- | --- |
| Brazil | BRA | 4.36746407652336 | 4.4 |
| Canada | CAN | 2.38158383281173 | 2.4 |
| China | CHN | 0.218128938439177 | 0.2 |
| Egypt | EGY | 28.2705899322082 | 33.3 |
| France | FRA | 1.99742599742599 | 2.3 |
| Germany | DEU | 2.2564981433876 | 2.5 |
| Ghana | GHA | 22.8483281157842 | 22.9 |
| India | IND | 4.9530355097366 | 4.6 |
| Italy | ITA | 0.982375111637719 | 1.1 |
| Japan | JPN | 2.7385368163524 | 2.7 |
| Kenya | KEN | 4.48978854243447 | 4.5 |
| Nigeria | NGA | 33.2416590552748 | 33.2 |
| South Africa | ZAF | 4.36115246518962 | 4.4 |
| United Kingdom | GBR | 3.2715729463592 | 2.5 |
| United States | USA | 2.94952520485207 | 3 |

```text
https://api.worldbank.org/v2/country/BRA;CAN;CHN;DEU;EGY;FRA;GBR;GHA;IND;ITA;JPN;KEN;NGA;USA;ZAF/indicator/FP.CPI.TOTL.ZG?format=json&per_page=2000&page=1
https://www.imf.org/external/datamapper/api/v1/PCPIPCH
https://www.imf.org/external/datamapper/api/v1/indicators
```

## Related

- [Teaching portfolio](index.md)
- [Inflation and capital preservation](../inflation-capital-preservation.md)
- [Where to check official figures](../../about/where-to-check.md)
- [Household finance](household-finance.md)
