#!/usr/bin/env python3
"""Generate the weekly educator example reports for FinancialLibrary.

The reports pair the library's curated records with LIVE data from free,
keyless, official public sources:

- FRED (Federal Reserve Bank of St. Louis) public CSV downloads —
  policy rate, inflation, unemployment, 10-year Treasury, saving rate.
- SEC EDGAR submissions API — recent filings of a small watchlist of
  large US banks (the same institutions a class meets in the library's
  US regulator and deposit-insurance records).
- World Bank Open Data API — annual inflation and financial-inclusion
  indicators for the countries the library covers.

No API keys are used. Every figure carries its source URL and the date
it was retrieved, so a teacher can re-check any number at the source.

Output: dated Markdown files under ``examples/educators/reports/``
plus a refreshed ``latest.md`` index in the same directory.

Educational only — these reports illustrate how to read public
financial data; they are not financial advice.

Run weekly by the Muse ``financial-library-educator-reports-weekly``
job, which opens a pull request with the refreshed reports for review.
Nothing here merges or publishes on its own.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
from datetime import UTC, date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "examples" / "educators" / "reports"

# SEC EDGAR fair-access rules require a declared User-Agent in
# "Name contact-email" form; the contact is the project author's email,
# already public in mcp-server/pyproject.toml.
UA = "FinancialLibrary educator-examples anand.dw24@gmail.com"
DISCLAIMER = (
    "> **Educational only, not financial advice.** Figures are retrieved "
    "from the public sources cited on the retrieval date shown; re-check "
    "any figure at its source before relying on it."
)

FRED_SERIES = [
    ("FEDFUNDS", "Federal funds effective rate", "%"),
    ("CPIAUCSL", "Consumer Price Index (all urban consumers)", "index"),
    ("UNRATE", "Unemployment rate", "%"),
    ("DGS10", "10-year Treasury constant maturity rate", "%"),
    ("PSAVERT", "Personal saving rate", "%"),
]

# Large US banks whose filings a class can read alongside the library's
# US records (FDIC deposit insurance, Federal Reserve, OCC, SEC).
EDGAR_WATCHLIST = [
    ("JPMorgan Chase", "0000019617"),
    ("Bank of America", "0000070858"),
    ("Wells Fargo", "0000072971"),
]
EDGAR_FORMS = {"10-K", "10-Q", "8-K"}

# ISO-3 codes for the countries the library covers (see data/kb-index.json).
LIBRARY_COUNTRIES = [
    ("BRA", "Brazil"), ("CAN", "Canada"), ("CHN", "China"),
    ("DEU", "Germany"), ("FRA", "France"), ("GBR", "United Kingdom"),
    ("GHA", "Ghana"), ("IND", "India"), ("ITA", "Italy"),
    ("JPN", "Japan"), ("KEN", "Kenya"), ("NGA", "Nigeria"),
    ("USA", "United States"), ("ZAF", "South Africa"),
]
WB_INDICATORS = [
    ("FP.CPI.TOTL.ZG", "Inflation, consumer prices (annual %)"),
    ("account.t.d", "Account ownership at a financial institution or mobile-money provider (% of population, 15+)"),
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def fred_latest(series_id: str) -> tuple[str, float] | None:
    """Return (observation date, value) for the latest non-empty point."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    rows = list(csv.DictReader(io.StringIO(fetch(url).decode("utf-8"))))
    for row in reversed(rows):
        raw = (row.get(series_id) or "").strip()
        if raw and raw != ".":
            try:
                return row["observation_date"], float(raw)
            except ValueError:
                continue
    return None


def fred_series(series_id: str) -> list[tuple[str, float]]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    rows = list(csv.DictReader(io.StringIO(fetch(url).decode("utf-8"))))
    out = []
    for row in rows:
        raw = (row.get(series_id) or "").strip()
        if raw and raw != ".":
            try:
                out.append((row["observation_date"], float(raw)))
            except ValueError:
                pass
    return out


def macro_report(today: date, stamp: str) -> str:
    lines = [
        f"# Educator example report — US macro snapshot ({today.isoformat()})",
        "",
        DISCLAIMER,
        "",
        "Live readings from the Federal Reserve Bank of St. Louis (FRED), "
        "retrieved " + stamp + ". Pair this page with the library's US "
        "records (`us-federal-reserve`, `us-fdic-deposit-insurance`, "
        "`us-cfpb`) to show how the institutions in the library publish "
        "the numbers a class can track.",
        "",
        "| Series | Latest value | Observation date | Source |",
        "| --- | --- | --- | --- |",
    ]
    for series_id, label, unit in FRED_SERIES:
        url = f"https://fred.stlouisfed.org/series/{series_id}"
        if series_id == "CPIAUCSL":
            pts = fred_series(series_id)
            if pts:
                d_now, v_now = pts[-1]
                year, month, day = d_now.split("-")
                target = f"{int(year) - 1}-{month}-{day}"
                prev = dict(pts).get(target)
                if prev:
                    yoy = (v_now / prev - 1) * 100
                    lines.append(
                        f"| {label} (year over year) | {yoy:.1f}% | {d_now} "
                        f"(vs {target}) | [FRED {series_id}]({url}) |"
                    )
            continue
        got = fred_latest(series_id)
        if got:
            d, v = got
            lines.append(f"| {label} | {v:.2f}{unit} | {d} | [FRED {series_id}]({url}) |")
    lines += [
        "",
        "**Classroom prompt:** the federal funds rate is set by the Federal "
        "Open Market Committee; the library's record `us-federal-reserve` "
        "explains who they are. Find one savings account or money-market "
        "rate advertised this week and compare it with the policy rate — "
        "what explains the gap?",
        "",
    ]
    return "\n".join(lines)


def filing_report(today: date, stamp: str) -> str:
    lines = [
        f"# Educator example report — reading real bank filings ({today.isoformat()})",
        "",
        DISCLAIMER,
        "",
        "The most recent filings of three large US banks, straight from "
        "SEC EDGAR (retrieved " + stamp + "). Each row links to the "
        "filing index on EDGAR, where the full document is free to read. "
        "Pair with the library's records `us-sec`, `us-fdic-deposit-insurance` "
        "and `us-occ` on who regulates whom.",
        "",
    ]
    for name, cik in EDGAR_WATCHLIST:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        data = json.loads(fetch(url))
        recent = data["filings"]["recent"]
        lines.append(f"## {name}")
        lines.append("")
        lines.append("| Form | Filed | What it is | Filing |")
        lines.append("| --- | --- | --- | --- |")
        # Latest one of each form type — a class meets the annual and
        # quarterly reports, not just the most recent event filings.
        picked: dict[str, tuple[str, str, str]] = {}
        for form, filed, accession, doc in zip(
            recent["form"], recent["filingDate"],
            recent["accessionNumber"], recent["primaryDocument"],
            strict=True,
        ):
            if form in EDGAR_FORMS and form not in picked:
                picked[form] = (filed, accession, doc)
        what = {
            "10-K": "Annual report (audited)",
            "10-Q": "Quarterly report",
            "8-K": "Material event report",
        }
        for form in sorted(picked, key=lambda f: picked[f][0], reverse=True):
            filed, accession, doc = picked[form]
            acc = accession.replace("-", "")
            link = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
            )
            lines.append(f"| {form} | {filed} | {what[form]} | [EDGAR]({link}) |")
        lines.append("")
    lines += [
        "**Classroom prompt:** open one 10-K and find the balance sheet. "
        "Which line shows customer deposits — the same deposits the FDIC "
        "insures (see record `us-fdic-deposit-insurance`)?",
        "",
    ]
    return "\n".join(lines)


def world_report(today: date, stamp: str) -> str:
    lines = [
        f"# Educator example report — the library's countries in World Bank data ({today.isoformat()})",
        "",
        DISCLAIMER,
        "",
        "Annual indicators from the World Bank Open Data API (retrieved "
        + stamp + ") for the countries FinancialLibrary covers. Annual "
        "series update slowly — this page changes when the Bank revises "
        "or extends a series, which is itself a lesson in data freshness "
        "(compare the library's own `last_checked` dates).",
        "",
    ]
    codes = ";".join(c for c, _ in LIBRARY_COUNTRIES)
    for indicator, label in WB_INDICATORS:
        url = (
            f"https://api.worldbank.org/v2/country/{codes}/indicator/"
            f"{indicator}?format=json&per_page=500"
        )
        payload = json.loads(fetch(url))
        rows = (payload[1] or []) if len(payload) > 1 else []
        latest: dict[str, tuple[str, float]] = {}
        for row in rows:
            code = row["country"]["id"]
            if row.get("value") is not None and code not in latest:
                latest[code] = (row["date"], float(row["value"]))
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| Country | Latest value | Year | Source |")
        lines.append("| --- | --- | --- | --- |")
        src = f"https://data.worldbank.org/indicator/{indicator}"
        for code, name in LIBRARY_COUNTRIES:
            iso2 = {
                "BRA": "BR", "CAN": "CA", "CHN": "CN", "DEU": "DE",
                "FRA": "FR", "GBR": "GB", "GHA": "GH", "IND": "IN",
                "ITA": "IT", "JPN": "JP", "KEN": "KE", "NGA": "NG",
                "USA": "US", "ZAF": "ZA",
            }[code]
            if iso2 in latest:
                yr, val = latest[iso2]
                lines.append(f"| {name} | {val:.1f} | {yr} | [World Bank]({src}) |")
        lines.append("")
    lines += [
        "**Classroom prompt:** pick two countries and compare account "
        "ownership with the library's deposit-insurance record for each — "
        "does broader account ownership come with a deposit-insurance "
        "scheme in both?",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    try:
        from zoneinfo import ZoneInfo

        today = datetime.now(ZoneInfo("America/New_York")).date()
    except Exception:
        today = datetime.now(UTC).date()
    stamp = today.isoformat()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    builders = [
        ("macro-snapshot", macro_report),
        ("filing-watch", filing_report),
        ("world-snapshot", world_report),
    ]
    written = []
    for slug, builder in builders:
        text = builder(today, stamp)
        path = REPORTS_DIR / f"{today.isoformat()}-{slug}.md"
        path.write_text(text, encoding="utf-8")
        written.append(path.name)
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    index = [
        "# Latest educator example reports",
        "",
        f"Generated {stamp} by `scripts/generate_educator_reports.py` "
        "from FRED, SEC EDGAR and the World Bank Open Data API — all "
        "free, keyless, official sources. Refreshed weekly by a Muse "
        "job that opens a pull request for review; dated snapshots are "
        "kept in this directory.",
        "",
    ] + [f"- [{name}]({name})" for name in written] + [""]
    (REPORTS_DIR / "latest.md").write_text("\n".join(index), encoding="utf-8")
    print(f"wrote {(REPORTS_DIR / 'latest.md').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
