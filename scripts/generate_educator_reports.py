#!/usr/bin/env python3
"""Generate educator example reports for FinancialLibrary.

The reports pair the library's curated records with data from free,
keyless, official public sources:

- FRED (Federal Reserve Bank of St. Louis) public CSV downloads —
  policy-rate target range, effective funds rate, inflation,
  unemployment, 10-year Treasury, saving rate.
- SEC EDGAR submissions API — recent 10-K, 10-Q, and 8-K filings for
  a small watchlist of large US banks.
- World Bank Open Data API — annual inflation and account ownership
  for the 15 countries with household vehicle pages.

No API keys are used. Every figure carries its series id, observation
date, and source URL.

The report date is pinned with ``--as-of`` (default: today's UTC date).
Observations after that date are ignored, so the same date and the same
upstream responses always produce the same files. ``SEED`` is applied
at the start of a run; the generator does not sample or shuffle.

A failed request is retried, then recorded in the report. The other
sections are still written. The process exits 1 when any source failed.

Educational only — these reports show how to read public financial
data. They are not investment advice and not financial advice.

Run it, then review the diff before publishing:

    python3 scripts/generate_educator_reports.py --as-of 2026-10-30
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import sys
import textwrap
import time
import urllib.error
import urllib.request
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "examples" / "educators" / "reports"

# SEC EDGAR fair-access rules require a declared User-Agent. The contact
# is the project author's email, already public in pyproject.toml.
UA = "FinancialLibrary educator-examples anand.dw24@gmail.com"
SEED = 0
DISCLAIMER = (
    "**Educational only, not investment advice.** These figures teach "
    "how to read public data. They are not financial advice and not a "
    "recommendation to buy, sell, or hold any product. Re-check each "
    "figure at the official series linked in the table. The observation "
    "date is the series date. The report date is the pinned `--as-of` date."
)


def prose(text: str, width: int = 88) -> list[str]:
    """Wrap a paragraph so published Markdown stays within the line limit."""
    return textwrap.wrap(text, width=width) or [""]


def quote(text: str, width: int = 88) -> list[str]:
    return ["> " + line for line in prose(text, width=width)]

# Household countries with vehicle pages. `global` is a resource bucket
# in the catalog, not an extra country. Display order is by name.
LIBRARY_COUNTRIES = (
    ("BRA", "Brazil"),
    ("CAN", "Canada"),
    ("CHN", "China"),
    ("EGY", "Egypt"),
    ("FRA", "France"),
    ("DEU", "Germany"),
    ("GHA", "Ghana"),
    ("IND", "India"),
    ("ITA", "Italy"),
    ("JPN", "Japan"),
    ("KEN", "Kenya"),
    ("NGA", "Nigeria"),
    ("ZAF", "South Africa"),
    ("GBR", "United Kingdom"),
    ("USA", "United States"),
)
ISO2_TO_ISO3 = {
    "BR": "BRA",
    "CA": "CAN",
    "CN": "CHN",
    "EG": "EGY",
    "FR": "FRA",
    "DE": "DEU",
    "GH": "GHA",
    "IN": "IND",
    "IT": "ITA",
    "JP": "JPN",
    "KE": "KEN",
    "NG": "NGA",
    "ZA": "ZAF",
    "GB": "GBR",
    "US": "USA",
}

# (series id, label, decimal places as FRED publishes the level)
FRED_LEVELS = (
    ("DFEDTARL", "Federal funds target range, lower bound", 2),
    ("DFEDTARU", "Federal funds target range, upper bound", 2),
    ("FEDFUNDS", "Federal funds effective rate, monthly average", 2),
    ("UNRATE", "Unemployment rate", 1),
    ("DGS10", "10-year Treasury constant maturity rate", 2),
    ("PSAVERT", "Personal saving rate", 1),
)
FRED_CPI = (
    ("CPIAUCSL", "Consumer Price Index, seasonally adjusted, 12-month percent change computed from the index"),
    ("CPIAUCNS", "Consumer Price Index, not seasonally adjusted, 12-month percent change computed from the index"),
)

EDGAR_WATCHLIST = (
    ("JPMorgan Chase", "0000019617"),
    ("Bank of America", "0000070858"),
    ("Wells Fargo", "0000072971"),
)
FORM_ORDER = ("10-K", "10-Q", "8-K")
FORM_WHAT = {
    "10-K": "Annual report (audited)",
    "10-Q": "Quarterly report",
    "8-K": "Material event report",
}

WB_INDICATORS = (
    ("FP.CPI.TOTL.ZG", "Inflation, consumer prices (annual %)"),
    (
        "FX.OWN.TOTL.ZS",
        "Account ownership at a financial institution or with a mobile-money-service provider "
        "(% of population ages 15+)",
    ),
)

SLUGS = ("macro-snapshot", "filing-watch", "world-snapshot")


class FetchError(Exception):
    """A URL still failed after the allowed attempts."""

    def __init__(self, url: str, reason: str, attempts: int):
        self.url = url
        self.reason = reason
        self.attempts = attempts
        super().__init__(f"{reason} after {attempts} attempts: {url}")


def fetch_bytes(
    url: str,
    *,
    timeout: float = 20.0,
    attempts: int = 3,
    sleep=time.sleep,
    opener=None,
    backoff: float = 0.25,
) -> bytes:
    """GET ``url``, retrying timeouts and transport errors.

    ``sleep`` and ``opener`` are injectable so tests do not touch the network.
    """
    if opener is None:
        opener = urllib.request.urlopen
    last_reason = "unknown"
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": UA, "Accept": "application/json,text/csv,*/*"},
            )
            with opener(req, timeout=timeout) as resp:
                data = resp.read()
            if not data:
                raise OSError("empty response")
            return data
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_reason = _failure_reason(exc)
            if attempt == attempts:
                raise FetchError(url, last_reason, attempts) from exc
            sleep(backoff * (2 ** (attempt - 1)))
    raise FetchError(url, last_reason, attempts)


def _failure_reason(exc: BaseException) -> str:
    if isinstance(exc, TimeoutError):
        return "timeout"
    text = str(exc).lower()
    if "timed out" in text or "timeout" in text:
        return "timeout"
    return type(exc).__name__


def _read(url: str, fetch) -> bytes:
    try:
        return fetch(url)
    except FetchError:
        raise
    except (TimeoutError, OSError, urllib.error.URLError) as exc:
        raise FetchError(url, _failure_reason(exc), 1) from exc


def _quantize(value: Decimal, places: int) -> str:
    quantum = Decimal("1").scaleb(-places)
    return f"{value.quantize(quantum, rounding=ROUND_HALF_UP):.{places}f}"


def format_level(raw: str, places: int) -> str:
    return _quantize(Decimal(raw), places)


def latest_on_or_before(points: list[tuple[str, str]], as_of: date) -> tuple[str, str] | None:
    """Latest ``(date, raw value)`` on or before ``as_of``.

    Equal dates keep the later row, so a repeated observation cannot
    change order between runs.
    """
    cutoff = as_of.isoformat()
    best: tuple[str, str] | None = None
    for observed, raw in points:
        if observed <= cutoff and (best is None or observed >= best[0]):
            best = (observed, raw)
    return best


def fred_points(series_id: str, fetch) -> list[tuple[str, str]]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    text = _read(url, fetch).decode("utf-8")
    points: list[tuple[str, str]] = []
    for row in csv.DictReader(io.StringIO(text)):
        raw = (row.get(series_id) or "").strip()
        observed = (row.get("observation_date") or "").strip()
        if not observed or not raw or raw == ".":
            continue
        points.append((observed, raw))
    return points


def cpi_change(points: list[tuple[str, Decimal]], as_of: date) -> tuple[str, Decimal, str, Decimal] | None:
    """12-month change against the same month a year earlier.

    Returns None when that prior observation is missing. A nearby month
    is not a substitute.
    """
    raw_points = [(observed, str(value)) for observed, value in points]
    latest = latest_on_or_before(raw_points, as_of)
    if latest is None:
        return None
    observed, raw_now = latest
    year, month, day = observed.split("-")
    target = f"{int(year) - 1}-{month}-{day}"
    previous = {item[0]: item[1] for item in points}.get(target)
    if previous is None:
        return None
    return observed, Decimal(raw_now), target, previous


def yoy_percent(now: Decimal, previous: Decimal) -> str:
    pct = (now / previous - Decimal(1)) * Decimal(100)
    return _quantize(pct, 1)


def _fred_link(series_id: str) -> str:
    return f"https://fred.stlouisfed.org/series/{series_id}"


def _gap(label: str, series_id: str) -> str:
    return f"| {label} | {series_id} | not retrieved | — | [FRED {series_id}]({_fred_link(series_id)}) |"


def macro_report(as_of: date, fetch) -> tuple[str, list[str]]:
    failures: list[str] = []
    lines = [
        f"# Educator example report — US macro snapshot ({as_of.isoformat()})",
        "",
        *quote(DISCLAIMER),
        "",
        *prose(
            "Readings from the Federal Reserve Bank of St. Louis (FRED). "
            f"Only observations on or before {as_of.isoformat()} are used. "
            "The FOMC sets the target range (`DFEDTARL`–`DFEDTARU`). "
            "`FEDFUNDS` is the monthly average effective rate in the market, "
            "not the target. A 12-month CPI percent change here is computed "
            "from the index levels; it is not a separate published percent series. "
            "Pair the page with the library records `us-federal-reserve`, "
            "`us-fdic-deposit-insurance`, and `us-cfpb`."
        ),
        "",
        "| Series | Series ID | Latest value | Observation date | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for series_id, label, places in FRED_LEVELS:
        try:
            got = latest_on_or_before(fred_points(series_id, fetch), as_of)
        except FetchError as exc:
            failures.append(f"{series_id}: {exc}")
            lines.append(_gap(label, series_id))
            continue
        if got is None:
            failures.append(f"{series_id}: no observation on or before {as_of.isoformat()}")
            lines.append(_gap(label, series_id))
            continue
        observed, raw = got
        lines.append(
            f"| {label} | {series_id} | {format_level(raw, places)}% | {observed} | "
            f"[FRED {series_id}]({_fred_link(series_id)}) |"
        )
    for series_id, label in FRED_CPI:
        try:
            points = [(observed, Decimal(raw)) for observed, raw in fred_points(series_id, fetch)]
        except FetchError as exc:
            failures.append(f"{series_id}: {exc}")
            lines.append(_gap(label, series_id))
            continue
        change = cpi_change(points, as_of)
        if change is None:
            failures.append(f"{series_id}: prior-year same-month observation missing")
            lines.append(_gap(label, series_id))
            continue
        observed, now, target, previous = change
        lines.append(
            f"| {label} | {series_id} | {yoy_percent(now, previous)}% | "
            f"{observed} index {now} vs {target} index {previous} | "
            f"[FRED {series_id}]({_fred_link(series_id)}) |"
        )
    lines += [
        "",
        *prose(_failure_note(failures)),
        "",
        *prose(
            "**Classroom prompt:** which number did the FOMC set, and which "
            "number is a market average? Find one savings or money-market rate "
            "advertised this week and compare it with the target range — what "
            "could explain a gap, without treating the gap as a recommendation?"
        ),
        "",
        _footer(as_of),
    ]
    return "\n".join(lines), failures


def filing_report(as_of: date, fetch) -> tuple[str, list[str]]:
    failures: list[str] = []
    lines = [
        f"# Educator example report — reading real bank filings ({as_of.isoformat()})",
        "",
        *quote(DISCLAIMER),
        "",
        *prose(
            "The latest 10-K, 10-Q, and 8-K on or before "
            f"{as_of.isoformat()} for three large US banks, from the SEC EDGAR "
            "submissions API. Rows are always in form order 10-K, 10-Q, 8-K. "
            "Each link is the filing's primary document. Pair with library "
            "records `us-sec`, `us-fdic-deposit-insurance`, and `us-occ`. "
            "Those records identify the institution; they do not store a "
            "deposit-insurance dollar limit."
        ),
        "",
    ]
    for name, cik in EDGAR_WATCHLIST:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        lines.append(f"## {name}")
        lines.append("")
        try:
            data = json.loads(_read(url, fetch).decode("utf-8"))
            recent = data["filings"]["recent"]
        except (FetchError, KeyError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
            reason = exc if isinstance(exc, FetchError) else FetchError(url, type(exc).__name__, 1)
            failures.append(f"{name} ({cik}): {reason}")
            lines.append(f"Filings were not retrieved ({reason.reason}).")
            lines.append("")
            continue
        picked: dict[str, tuple[str, str, str]] = {}
        forms = recent.get("form") or []
        filed_dates = recent.get("filingDate") or []
        accessions = recent.get("accessionNumber") or []
        documents = recent.get("primaryDocument") or []
        for form, filed, accession, doc in zip(forms, filed_dates, accessions, documents, strict=False):
            if filed > as_of.isoformat():
                continue
            if form in FORM_ORDER and form not in picked:
                picked[form] = (filed, accession, doc)
        lines.append("| Form | Filed | What it is | Filing |")
        lines.append("| --- | --- | --- | --- |")
        for form in FORM_ORDER:
            if form not in picked:
                lines.append(f"| {form} | not retrieved | {FORM_WHAT[form]} | — |")
                failures.append(f"{name} {form}: no filing on or before {as_of.isoformat()}")
                continue
            filed, accession, doc = picked[form]
            acc = accession.replace("-", "")
            link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
            lines.append(f"| {form} | {filed} | {FORM_WHAT[form]} | [EDGAR]({link}) |")
        lines.append("")
    lines += [
        *prose(_failure_note(failures)),
        "",
        *prose(
            "**Classroom prompt:** open one 10-K and find the balance sheet. "
            "Which line is customer deposits? The FDIC record names the insurer "
            "and links to the official page. Read any dollar limit on that page, "
            "and label the date you read it. The library record does not store the limit."
        ),
        "",
        _footer(as_of),
    ]
    return "\n".join(lines), failures


def _world_bank_url(indicator: str, page: int) -> str:
    codes = ";".join(sorted(code for code, _name in LIBRARY_COUNTRIES))
    return (
        "https://api.worldbank.org/v2/country/"
        f"{codes}/indicator/{indicator}?format=json&mrnev=1&per_page=100&page={page}"
    )


def row_iso3(row: dict) -> str | None:
    iso3 = str(row.get("countryiso3code") or "").strip().upper()
    if len(iso3) == 3 and iso3.isalpha():
        return iso3
    cid = str((row.get("country") or {}).get("id") or "").strip().upper()
    if len(cid) == 3 and cid.isalpha():
        return cid
    if len(cid) == 2:
        return ISO2_TO_ISO3.get(cid)
    return None


def world_bank_rows(indicator: str, fetch) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while page <= 20:
        url = _world_bank_url(indicator, page)
        payload = json.loads(_read(url, fetch).decode("utf-8"))
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[0], dict):
            raise FetchError(url, "unexpected payload", 1)
        data = payload[1] or []
        if not isinstance(data, list):
            raise FetchError(url, "unexpected payload", 1)
        rows.extend(data)
        pages = int(payload[0].get("pages") or 1)
        if page >= pages:
            break
        page += 1
    return rows


def latest_by_country(rows: list[dict]) -> dict[str, tuple[str, Decimal]]:
    best: dict[str, tuple[str, Decimal]] = {}
    for row in rows:
        iso3 = row_iso3(row)
        if iso3 is None or row.get("value") is None:
            continue
        year = str(row.get("date") or "")
        value = Decimal(str(row["value"]))
        previous = best.get(iso3)
        if previous is None or year >= previous[0]:
            best[iso3] = (year, value)
    return best


def world_report(as_of: date, fetch) -> tuple[str, list[str]]:
    failures: list[str] = []
    lines = [
        f"# Educator example report — the library's countries in World Bank data ({as_of.isoformat()})",
        "",
        *quote(DISCLAIMER),
        "",
        *prose(
            "Annual indicators from the World Bank Open Data API for the 15 "
            "countries with household vehicle pages (retrieved for report date "
            f"{as_of.isoformat()}). `global` in the catalog is a resource bucket, "
            "not a sixteenth country. The year column is the Bank's observation "
            "year and can lag the report date. A country with no value is listed "
            "as 'not in source response' so a gap is visible. "
            "`FX.OWN.TOTL.ZS` is the Bank's account-ownership series."
        ),
        "",
    ]
    for indicator, label in WB_INDICATORS:
        src = f"https://data.worldbank.org/indicator/{indicator}"
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| Country | Latest value | Year | Series ID | Source |")
        lines.append("| --- | --- | --- | --- | --- |")
        try:
            indexed = latest_by_country(world_bank_rows(indicator, fetch))
        except (FetchError, json.JSONDecodeError, UnicodeError, ValueError) as exc:
            reason = exc if isinstance(exc, FetchError) else FetchError(indicator, type(exc).__name__, 1)
            failures.append(f"{indicator}: {reason}")
            lines.append(f"| — | not retrieved | — | {indicator} | [World Bank]({src}) |")
            lines.append("")
            continue
        for code, name in LIBRARY_COUNTRIES:
            if code not in indexed:
                lines.append(f"| {name} | not in source response | — | {indicator} | [World Bank]({src}) |")
                continue
            year, value = indexed[code]
            lines.append(f"| {name} | {_quantize(value, 1)} | {year} | {indicator} | [World Bank]({src}) |")
        lines.append("")
    lines += [
        *prose(_failure_note(failures)),
        "",
        *prose(
            "**Classroom prompt:** pick two countries and compare account "
            "ownership with the library's deposit-insurance record for each. "
            "Where the library has no insurer record, write 'not covered' "
            "instead of filling the cell from memory."
        ),
        "",
        _footer(as_of),
    ]
    return "\n".join(lines), failures


def _failure_note(failures: list[str]) -> str:
    if not failures:
        return "All requested series in this report were retrieved."
    items = "; ".join(failures)
    return f"Some series were not retrieved after retries: {items}."


def _footer(as_of: date) -> str:
    return f"Pinned report date: {as_of.isoformat()}. Generator seed: {SEED}."


def render_index(as_of: date, names: list[str]) -> str:
    lines = [
        "# Latest educator example reports",
        "",
        *prose(
            f"Generated {as_of.isoformat()} by `scripts/generate_educator_reports.py` "
            "from FRED, SEC EDGAR, and the World Bank Open Data API. A maintainer "
            "runs the script and reviews the result before it is published. Dated "
            "snapshots stay in this directory."
        ),
        "",
        *quote(DISCLAIMER),
        "",
    ]
    lines.extend(f"- [{name}]({name})" for name in names)
    lines.append("")
    lines.append(_footer(as_of))
    lines.append("")
    return "\n".join(lines)


def build_reports(as_of: date, fetch) -> tuple[dict[str, str], list[str]]:
    """Return ``{slug: markdown}`` and a sorted list of source failures."""
    random.seed(SEED)
    builders = {
        "macro-snapshot": macro_report,
        "filing-watch": filing_report,
        "world-snapshot": world_report,
    }
    reports: dict[str, str] = {}
    failures: list[str] = []
    for slug in SLUGS:
        text, section_failures = builders[slug](as_of, fetch)
        reports[slug] = text
        failures.extend(section_failures)
    failures.sort()
    return reports, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate educator example reports.")
    parser.add_argument(
        "--as-of",
        dest="as_of",
        default=None,
        help="Pinned report date YYYY-MM-DD (default: UTC today).",
    )
    parser.add_argument("--output-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args(argv)
    if args.as_of:
        as_of = date.fromisoformat(args.as_of)
    else:
        as_of = datetime.now(UTC).date()

    def fetch(url: str) -> bytes:
        return fetch_bytes(url, timeout=args.timeout, attempts=args.attempts)

    reports, failures = build_reports(as_of, fetch)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for slug in SLUGS:
        name = f"{as_of.isoformat()}-{slug}.md"
        (args.output_dir / name).write_text(reports[slug], encoding="utf-8")
        written.append(name)
        print(f"wrote {name}")
    index = render_index(as_of, written)
    (args.output_dir / "latest.md").write_text(index, encoding="utf-8")
    print("wrote latest.md")
    for item in failures:
        print(f"gap: {item}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
