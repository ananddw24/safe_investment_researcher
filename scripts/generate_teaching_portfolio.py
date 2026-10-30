#!/usr/bin/env python3
"""Build the teaching portfolio from checked-in official snapshots.

The pages under ``docs/guides/teaching/`` and the figures beside them are
generated from ``data/teaching/snapshots/``. Those snapshots are raw
responses from keyless official endpoints, except the EDGAR files, which
are excerpts: each fact and filing field is copied unchanged, and the
manifest records the SHA-256 of the full payload.

No API key is used. ``--fetch`` refreshes the snapshots (network). The
default command and ``--check`` stay offline and regenerate or compare
the pages from the snapshots already in the repository.

Educational only. The pages describe public series. They are not
forecasts and not investment advice.

    python3 scripts/generate_teaching_portfolio.py
    python3 scripts/generate_teaching_portfolio.py --check
    python3 scripts/generate_teaching_portfolio.py --fetch
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import textwrap
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# scripts/ is not a package. Put it on the path so tests can load this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teaching_charts as charts  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = REPO_ROOT / "data" / "teaching" / "snapshots"
DOCS = REPO_ROOT / "docs" / "guides" / "teaching"
FIGURES = DOCS / "figures"
VALUES_PATH = REPO_ROOT / "data" / "teaching" / "figure-values.json"
NOTEBOOK_PATH = REPO_ROOT / "examples" / "educators" / "notebooks" / "teaching-portfolio.ipynb"

UA = "FinancialLibrary educator-examples anand.dw24@gmail.com"
WINDOW_START = "2016-10-01"
FRED_KEEP_FROM = "2015-10-01"
WB_KEEP_FROM_YEAR = "2011"
IMF_KEEP_FROM_YEAR = 2016
EDGAR_CIK = "0000019617"
EDGAR_CONCEPTS = ("Assets", "Deposits", "NetIncomeLoss", "Revenues")
FRED_SERIES = (
    "FEDFUNDS",
    "CPIAUCSL",
    "DGS3MO",
    "DGS2",
    "DGS5",
    "DGS10",
    "DGS30",
    "UNRATE",
    "PAYEMS",
    "CIVPART",
)
WB_INDICATORS = (
    "FP.CPI.TOTL.ZG",
    "FX.OWN.TOTL.ZS",
    "FX.OWN.TOTL.FE.ZS",
    "FX.OWN.TOTL.MA.ZS",
)
CURVE = (
    ("DGS3MO", "3-month"),
    ("DGS2", "2-year"),
    ("DGS5", "5-year"),
    ("DGS10", "10-year"),
    ("DGS30", "30-year"),
)
COUNTRIES = (
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
NAMES = dict(COUNTRIES)
DISCLAIMER = (
    '!!! warning "Educational only"\n'
    "    This page is for financial literacy. It is **not** personalized advice,\n"
    "    an offer to sell, or a recommendation to buy, sell, or hold any product.\n"
    "    Rules differ by country; verify with official sources in your jurisdiction."
)


@dataclass(frozen=True)
class Obs:
    observed: str
    raw: str
    value: Decimal


_PROTECTED = re.compile(r"\[[^\]]+\]\([^)]+\)|`[^`]+`")


def prose(text: str, width: int = 96) -> list[str]:
    """Wrap plain text without splitting links, code spans, or hyphenated words."""
    protected: list[str] = []

    def hold(match: re.Match[str]) -> str:
        token = match.group(0)
        marker = f"‹{len(protected)}›"
        protected.append(token)
        # Same width as the token, so a long link moves to its own line.
        if len(token) <= len(marker):
            return marker
        return marker + ("·" * (len(token) - len(marker)))

    safe = _PROTECTED.sub(hold, text)
    lines = textwrap.wrap(safe, width=width, break_long_words=False, break_on_hyphens=False) or [""]
    restored = []
    for line in lines:
        for index, token in enumerate(protected):
            marker = f"‹{index}›"
            if marker in line:
                line = re.sub(re.escape(marker) + "·*", token, line)
        restored.append(line)
    return restored


def quantize(value: Decimal, places: int) -> str:
    quantum = Decimal(1).scaleb(-places)
    return f"{value.quantize(quantum, rounding=ROUND_HALF_UP):.{places}f}"


def exact(value: Decimal | int) -> str:
    if isinstance(value, int):
        return str(value)
    return format(value, "f")


def last_complete_year(as_of: date) -> int:
    """Last calendar year that had ended on ``as_of``.

    A year is complete only after 31 December. The IMF file does not flag
    estimates versus projections, so this rule is the library's, stated
    on the page.
    """
    if as_of.month == 12 and as_of.day == 31:
        return as_of.year
    return as_of.year - 1


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_bytes(url: str, *, timeout: float = 60.0, attempts: int = 3) -> bytes:
    last = "unknown"
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if not data:
                raise OSError("empty response")
            return data
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = str(exc)
            if attempt == attempts:
                raise RuntimeError(f"{url} failed after {attempts} attempts: {last}") from exc
            time.sleep(0.4 * attempt)
    raise RuntimeError(last)


def trim_fred_csv(text: str) -> str:
    """Keep observations from ``FRED_KEEP_FROM`` on, including the prior year the CPI change needs."""
    source = io.StringIO(text)
    reader = csv.DictReader(source)
    if not reader.fieldnames:
        return text
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in reader:
        if (row.get("observation_date") or "") >= FRED_KEEP_FROM:
            writer.writerow(row)
    return output.getvalue()


def trim_world_bank(text: str) -> str:
    payload = json.loads(text)
    if isinstance(payload, dict) and "raw_pages" in payload:
        rows: list[dict] = []
        meta = None
        for page in payload["raw_pages"]:
            parsed = json.loads(page)
            meta = parsed[0]
            rows.extend(parsed[1] or [])
    else:
        meta, rows = payload[0], list(payload[1] or [])
    kept = [row for row in rows if row.get("value") is not None and str(row.get("date") or "") >= WB_KEEP_FROM_YEAR]
    return json.dumps([meta, kept]) + "\n"


def trim_imf_inflation(text: str) -> str:
    payload = json.loads(text)
    block = payload["values"]["PCPIPCH"]
    kept = {}
    for iso3 in NAMES:
        series = block.get(iso3) or {}
        kept[iso3] = {year: series[year] for year in series if str(year).isdigit() and int(year) >= IMF_KEEP_FROM_YEAR}
    payload["values"]["PCPIPCH"] = kept
    return json.dumps(payload) + "\n"


def fred_url(series_id: str) -> str:
    return f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


def fred_page(series_id: str) -> str:
    return f"https://fred.stlouisfed.org/series/{series_id}"


def wb_url(indicator: str, page: int) -> str:
    codes = ";".join(sorted(NAMES))
    return f"https://api.worldbank.org/v2/country/{codes}/indicator/{indicator}?format=json&per_page=2000&page={page}"


def parse_fred(text: str, series_id: str) -> list[Obs]:
    rows: list[Obs] = []
    for row in csv.DictReader(io.StringIO(text)):
        raw = (row.get(series_id) or "").strip()
        observed = (row.get("observation_date") or "").strip()
        if not observed or not raw or raw == ".":
            continue
        rows.append(Obs(observed, raw, Decimal(raw)))
    rows.sort(key=lambda item: item.observed)
    dedup: dict[str, Obs] = {}
    for item in rows:
        dedup[item.observed] = item
    return [dedup[key] for key in sorted(dedup)]


def on_or_before(points: list[Obs], as_of: str) -> list[Obs]:
    return [item for item in points if item.observed <= as_of]


def in_window(points: list[Obs], start: str, as_of: str) -> list[Obs]:
    return [item for item in points if start <= item.observed <= as_of]


def yoy_changes(points: list[Obs], start: str, as_of: str) -> list[tuple[Obs, Obs, Decimal]]:
    """12-month change against the same month a year earlier.

    A nearby month is not a substitute. ``points`` must include the year
    before ``start`` so the first in-window month can find its pair.
    """
    by_date = {item.observed: item for item in points}
    changes: list[tuple[Obs, Obs, Decimal]] = []
    for item in points:
        if item.observed < start or item.observed > as_of:
            continue
        year, month, day = item.observed.split("-")
        prior = by_date.get(f"{int(year) - 1}-{month}-{day}")
        if prior is None or prior.value == 0:
            continue
        pct = (item.value / prior.value - Decimal(1)) * Decimal(100)
        changes.append((item, prior, pct))
    return changes


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal, parse_int=Decimal)


def load_wb(path: Path) -> tuple[str, dict[tuple[str, str], Decimal]]:
    payload = load_json(path)
    if isinstance(payload, dict) and "raw_pages" in payload:
        rows: list[dict] = []
        for page in payload["raw_pages"]:
            parsed = json.loads(page, parse_float=Decimal, parse_int=Decimal)
            rows.extend(parsed[1] or [])
    else:
        rows = payload[1] or []
    official_name = ""
    values: dict[tuple[str, str], Decimal] = {}
    for row in rows:
        if not official_name:
            official_name = str((row.get("indicator") or {}).get("value") or "")
        iso3 = str(row.get("countryiso3code") or "").upper()
        year = str(row.get("date") or "")
        raw = row.get("value")
        if iso3 not in NAMES or raw is None or not year:
            continue
        value = raw if isinstance(raw, Decimal) else Decimal(str(raw))
        key = (iso3, year)
        previous = values.get(key)
        if previous is not None and previous != value:
            raise RuntimeError(f"Conflicting World Bank rows for {iso3} {year} in {path.name}")
        values[key] = value
    if not official_name:
        raise RuntimeError(f"No indicator name in {path}")
    return official_name, values


def select_annual_facts(facts: list[dict], start_year: int, as_of: str) -> list[dict]:
    """Current-year column of each 10-K, not a later filing's comparative.

    Companyfacts repeats prior years inside a new 10-K and tags them with
    the new filing's ``fy``. Keeping a fact only when ``fy`` equals the
    year of ``end`` (and, for a duration fact, ``start`` is in that same
    year) selects the column reported in that year's 10-K.
    """
    chosen: dict[str, dict] = {}
    for fact in facts:
        if fact.get("form") != "10-K" or fact.get("fp") != "FY":
            continue
        end = str(fact.get("end") or "")
        fy = fact.get("fy")
        if fy is None or len(end) < 10:
            continue
        end_year = int(end[:4])
        if int(fy) != end_year:
            continue
        start = fact.get("start")
        if start and int(str(start)[:4]) != end_year:
            continue
        if end_year < start_year or end > as_of:
            continue
        if end in chosen:
            raise RuntimeError(f"More than one selected fact for period end {end}")
        chosen[end] = fact
    return [chosen[key] for key in sorted(chosen)]


def billions(amount: int) -> Decimal:
    return Decimal(amount) / Decimal(1_000_000_000)


def filing_url(cik: str, accession: str, document: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{document}"


def latest_filings(excerpt: dict, as_of: str) -> dict[str, dict]:
    picked: dict[str, dict] = {}
    for row in excerpt["filings"]:
        form = row["form"]
        filed = row["filingDate"]
        if filed > as_of or form not in {"10-K", "10-Q", "8-K"}:
            continue
        previous = picked.get(form)
        if previous is None or (filed, row["accessionNumber"]) > (previous["filingDate"], previous["accessionNumber"]):
            picked[form] = row
    return picked


@dataclass
class CountryRow:
    iso3: str
    name: str
    wb_inflation: dict[str, Decimal]
    imf_inflation: dict[str, Decimal]
    ownership: dict[str, Decimal]
    ownership_female: dict[str, Decimal]
    ownership_male: dict[str, Decimal]


@dataclass
class Portfolio:
    retrieved_on: str
    as_of: date
    complete_year: int
    comparison_year: int
    survey_year: str
    fred: dict[str, list[Obs]]
    cpi_yoy: list[tuple[Obs, Obs, Decimal]]
    gap: list[tuple[str, Decimal, Decimal, Decimal]]
    spread: list[tuple[str, Decimal]]
    curve_date: str
    curve: list[tuple[str, str, Obs]]
    payroll_yoy: list[tuple[Obs, Obs, Decimal]]
    facts: dict[str, list[dict]]
    filings: dict[str, dict]
    edgar_cik: str
    countries: list[CountryRow]
    wb_names: dict[str, str]
    imf_meta: dict
    wb_2025_missing: list[str]
    figures: list
    values: dict


def load_portfolio() -> Portfolio:
    manifest = json.loads((SNAPSHOTS / "manifest.json").read_text(encoding="utf-8"))
    retrieved_on = manifest["retrieved_on"]
    as_of = date.fromisoformat(retrieved_on)
    as_of_s = retrieved_on
    fred = {
        series_id: on_or_before(
            parse_fred((SNAPSHOTS / "fred" / f"{series_id}.csv").read_text(encoding="utf-8"), series_id), as_of_s
        )
        for series_id in FRED_SERIES
    }
    cpi_yoy = yoy_changes(fred["CPIAUCSL"], WINDOW_START, as_of_s)
    funds = {item.observed: item for item in fred["FEDFUNDS"]}
    gap = []
    for now, _prior, pct in cpi_yoy:
        fund = funds.get(now.observed)
        if fund is None:
            continue
        # The gap uses the same rounded readings the page displays, then rounds the difference.
        displayed_fund = Decimal(quantize(fund.value, 2))
        displayed_cpi = Decimal(quantize(pct, 1))
        gap.append((now.observed, displayed_fund, displayed_cpi, displayed_fund - displayed_cpi))
    dgs10 = {item.observed: item.value for item in fred["DGS10"]}
    dgs2 = {item.observed: item.value for item in fred["DGS2"]}
    spread = []
    for observed in sorted(set(dgs10) & set(dgs2)):
        if observed < WINDOW_START or observed > as_of_s:
            continue
        spread.append((observed, dgs10[observed] - dgs2[observed]))
    common = None
    for _series_id, _label in CURVE:
        dates = {item.observed for item in fred[_series_id] if item.observed <= as_of_s}
        common = dates if common is None else common & dates
    if not common:
        raise RuntimeError("No common Treasury yield date")
    curve_date = max(common)
    curve = []
    for series_id, label in CURVE:
        match = next(item for item in fred[series_id] if item.observed == curve_date)
        curve.append((series_id, label, match))
    payroll_yoy = yoy_changes(fred["PAYEMS"], WINDOW_START, as_of_s)

    edgar = load_json(SNAPSHOTS / "edgar" / "jpmorgan-10k-facts.json")
    facts = {concept: select_annual_facts(edgar["concepts"][concept], 2016, as_of_s) for concept in EDGAR_CONCEPTS}
    filings = latest_filings(load_json(SNAPSHOTS / "edgar" / "jpmorgan-filings.json"), as_of_s)

    wb_names: dict[str, str] = {}
    wb_values: dict[str, dict[tuple[str, str], Decimal]] = {}
    for indicator in WB_INDICATORS:
        official, values = load_wb(SNAPSHOTS / "worldbank" / f"{indicator}.json")
        wb_names[indicator] = official
        wb_values[indicator] = values
    imf_raw = load_json(SNAPSHOTS / "imf" / "PCPIPCH.json")
    imf_block = imf_raw["values"]["PCPIPCH"]
    indicators = load_json(SNAPSHOTS / "imf" / "indicators.json")
    imf_meta = indicators["indicators"]["PCPIPCH"]
    complete = last_complete_year(as_of)
    countries: list[CountryRow] = []
    for iso3, name in COUNTRIES:
        imf_years = {}
        for year, raw in (imf_block.get(iso3) or {}).items():
            if raw is None:
                continue
            imf_years[str(year)] = raw if isinstance(raw, Decimal) else Decimal(str(raw))
        countries.append(
            CountryRow(
                iso3,
                name,
                {year: value for (code, year), value in wb_values["FP.CPI.TOTL.ZG"].items() if code == iso3},
                imf_years,
                {year: value for (code, year), value in wb_values["FX.OWN.TOTL.ZS"].items() if code == iso3},
                {year: value for (code, year), value in wb_values["FX.OWN.TOTL.FE.ZS"].items() if code == iso3},
                {year: value for (code, year), value in wb_values["FX.OWN.TOTL.MA.ZS"].items() if code == iso3},
            )
        )
    comparison_year = None
    for year in range(complete, 1999, -1):
        key = str(year)
        if all(key in country.wb_inflation and key in country.imf_inflation for country in countries):
            comparison_year = year
            break
    if comparison_year is None:
        raise RuntimeError("No year has World Bank and IMF inflation for every library country")
    survey_years = None
    for country in countries:
        years = set(country.ownership) & set(country.ownership_female) & set(country.ownership_male)
        survey_years = years if survey_years is None else survey_years & years
    if not survey_years:
        raise RuntimeError("No Findex year covers every library country")
    survey_year = max(survey_years)
    target = str(complete)
    missing = [country.name for country in countries if target not in country.wb_inflation]
    portfolio = Portfolio(
        retrieved_on=retrieved_on,
        as_of=as_of,
        complete_year=complete,
        comparison_year=comparison_year,
        survey_year=survey_year,
        fred=fred,
        cpi_yoy=cpi_yoy,
        gap=gap,
        spread=spread,
        curve_date=curve_date,
        curve=curve,
        payroll_yoy=payroll_yoy,
        facts=facts,
        filings=filings,
        edgar_cik=str(edgar.get("cik_padded") or EDGAR_CIK),
        countries=countries,
        wb_names=wb_names,
        imf_meta={key: str(value) for key, value in imf_meta.items()},
        wb_2025_missing=missing,
        figures=[],
        values={},
    )
    portfolio.figures = build_figures(portfolio)
    portfolio.values = build_values(portfolio)
    return portfolio


def _series(label: str, points: list[tuple[str, Decimal]], color: str, dash: str, places: int) -> charts.LineSeries:
    return charts.LineSeries(
        label,
        tuple(item[0] for item in points),
        tuple(quantize(item[1], places) for item in points),
        color,
        dash,
    )


def build_figures(portfolio: Portfolio) -> list:
    cpi_points = [(now.observed, pct) for now, _prior, pct in portfolio.cpi_yoy]
    fund_points = [
        (item.observed, item.value)
        for item in in_window(portfolio.fred["FEDFUNDS"], WINDOW_START, portfolio.retrieved_on)
    ]
    latest_fund = fund_points[-1]
    latest_cpi = cpi_points[-1]
    gap_points = [(observed, gap) for observed, _fund, _cpi, gap in portfolio.gap]
    spread_points = portfolio.spread
    unrate = [
        (item.observed, item.value)
        for item in in_window(portfolio.fred["UNRATE"], WINDOW_START, portfolio.retrieved_on)
    ]
    part = [
        (item.observed, item.value)
        for item in in_window(portfolio.fred["CIVPART"], WINDOW_START, portfolio.retrieved_on)
    ]
    payroll_points = [(now.observed, pct) for now, _prior, pct in portfolio.payroll_yoy]
    style = charts.StyleLegend(
        "chart-style",
        "Chart style used on every module",
        "Okabe–Ito colors. Lines also use dash patterns. This legend is not data.",
        "Style sample, not data: blue solid, vermillion dashed, green dotted, plus orange, sky, and purple.",
    )
    rates = charts.LineFigure(
        "rates-policy-and-inflation",
        "Effective funds rate and 12-month CPI change",
        f"FRED FEDFUNDS and CPIAUCSL, retrieved {portfolio.retrieved_on}. CPI change is computed.",
        (
            f"Funds rate and computed 12-month CPI change, Oct 2016 to {latest_fund[0][:7]}. "
            f"Ends at {quantize(latest_fund[1], 2)}% and {quantize(latest_cpi[1], 1)}%."
        ),
        "Percent",
        (
            _series("Effective funds rate", fund_points, charts.PALETTE["blue"], "solid", 2),
            _series("CPI, 12-month change", cpi_points, charts.PALETTE["vermillion"], "dashed", 1),
        ),
        True,
        1,
    )
    gap_fig = charts.LineFigure(
        "rates-computed-gap",
        "Displayed funds rate minus the displayed CPI change",
        "Both readings are the rounded values on the page. Not a published real interest rate.",
        (
            f"Computed gap, funds rate minus 12-month CPI change, through {gap_points[-1][0][:7]}. "
            f"Ends at {quantize(gap_points[-1][1], 1)} percentage points."
        ),
        "Percentage points",
        (_series("Computed gap", gap_points, charts.PALETTE["green"], "solid", 1),),
        True,
        1,
    )
    curve = charts.CurveFigure(
        "yield-curve-snapshot",
        f"Treasury constant-maturity yields on {portfolio.curve_date}",
        f"FRED DGS3MO, DGS2, DGS5, DGS10, DGS30. Retrieved {portfolio.retrieved_on}.",
        "Yield curve on "
        + portfolio.curve_date
        + ": "
        + ", ".join(f"{label} {item.raw}%" for _sid, label, item in portfolio.curve)
        + ".",
        "Percent",
        tuple(label for _sid, label, _item in portfolio.curve),
        tuple(item.raw for _sid, _label, item in portfolio.curve),
        charts.PALETTE["blue"],
        2,
    )
    # The curve alt is built after we know it fits; CurveFigure stores it.
    spread_fig = charts.LineFigure(
        "yield-spread",
        "10-year yield minus 2-year yield",
        "Computed from FRED DGS10 and DGS2. Not a separate published series.",
        (
            f"Computed 10-year minus 2-year Treasury spread, Oct 2016 to {spread_points[-1][0]}. "
            f"Ends at {quantize(spread_points[-1][1], 2)} percentage points."
        ),
        "Percentage points",
        (_series("10-year minus 2-year", spread_points, charts.PALETTE["purple"], "solid", 2),),
        True,
        2,
    )
    labor_u = charts.LineFigure(
        "labor-unemployment",
        "Unemployment rate (U-3)",
        f"FRED UNRATE, seasonally adjusted. Retrieved {portfolio.retrieved_on}.",
        (f"US unemployment rate, Oct 2016 to {unrate[-1][0][:7]}. Ends at {quantize(unrate[-1][1], 1)} percent."),
        "Percent",
        (_series("Unemployment rate", unrate, charts.PALETTE["blue"], "solid", 1),),
        True,
        1,
    )
    labor_p = charts.LineFigure(
        "labor-payroll-change",
        "Nonfarm payrolls, 12-month percent change",
        "Computed from FRED PAYEMS levels. Not a separate published series.",
        (
            f"Computed 12-month percent change in nonfarm payrolls through {payroll_points[-1][0][:7]}. "
            f"Ends at {quantize(payroll_points[-1][1], 1)} percent."
        ),
        "Percent",
        (_series("Payrolls, 12-month change", payroll_points, charts.PALETTE["vermillion"], "dashed", 1),),
        True,
        1,
    )
    labor_c = charts.LineFigure(
        "labor-participation",
        "Labor force participation rate",
        f"FRED CIVPART. Retrieved {portfolio.retrieved_on}. Axis does not start at zero.",
        (f"Labor force participation, Oct 2016 to {part[-1][0][:7]}. Ends at {quantize(part[-1][1], 1)} percent."),
        "Percent",
        (_series("Participation rate", part, charts.PALETTE["green"], "dotted", 1),),
        False,
        1,
    )

    def _year_values(concept: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        years = []
        values = []
        for fact in portfolio.facts[concept]:
            scaled, _text, _unit = usd_text(int(fact["val"]))
            years.append(fact["end"][:4])
            values.append(quantize(scaled, 2))
        return tuple(years), tuple(values)

    asset_years, asset_values = _year_values("Assets")
    deposit_years, deposit_values = _year_values("Deposits")
    revenue_years, revenue_values = _year_values("Revenues")
    income_years, income_values = _year_values("NetIncomeLoss")
    if asset_years != deposit_years or revenue_years != income_years:
        raise RuntimeError("10-K concepts do not share fiscal years")
    _assets_scaled, assets_prose, assets_unit = usd_text(int(portfolio.facts["Assets"][-1]["val"]))
    _deposits_scaled, deposits_prose, _deposits_unit = usd_text(int(portfolio.facts["Deposits"][-1]["val"]))
    _revenue_scaled, revenue_prose, income_unit = usd_text(int(portfolio.facts["Revenues"][-1]["val"]))
    _income_scaled, income_prose, _income_unit = usd_text(int(portfolio.facts["NetIncomeLoss"][-1]["val"]))
    filing_balance = charts.GroupedBarFigure(
        "filing-assets-deposits",
        "Total assets and deposits at fiscal year-end",
        "EDGAR 10-K facts. Bars are year-end stocks, not a line through the year.",
        (
            f"Assets and deposits, fiscal years {asset_years[0]} to {asset_years[-1]}. "
            f"{asset_years[-1]}: assets {assets_prose}, deposits {deposits_prose}."
        ),
        asset_years,
        ("Assets", "Deposits"),
        (charts.PALETTE["blue"], charts.PALETTE["orange"]),
        (asset_values, deposit_values),
        2,
        "",
        assets_unit,
    )
    filing_income = charts.GroupedBarFigure(
        "filing-revenue-income",
        "Revenues and net income for the fiscal year",
        "EDGAR 10-K facts for a full fiscal year. Not a view on the company.",
        (
            f"Revenues and net income, fiscal years {revenue_years[0]} to {revenue_years[-1]}. "
            f"{revenue_years[-1]}: revenues {revenue_prose}, net income {income_prose}."
        ),
        revenue_years,
        ("Revenues", "Net income"),
        (charts.PALETTE["sky"], charts.PALETTE["vermillion"]),
        (revenue_values, income_values),
        2,
        "",
        income_unit,
    )
    year = str(portfolio.complete_year)
    wb_rows = []
    for country in portfolio.countries:
        if year in country.wb_inflation:
            wb_rows.append((country.name, country.wb_inflation[year]))
    wb_rows.sort(key=lambda item: item[1])
    wb_fig = charts.BarFigure(
        "cross-country-wb-inflation",
        f"World Bank consumer-price inflation, {year}",
        "Indicator FP.CPI.TOTL.ZG. Countries missing this year are omitted, not drawn as zero.",
        (
            f"Horizontal bars of {year} World Bank inflation. "
            f"Highest among those plotted: {wb_rows[-1][0]} at {quantize(wb_rows[-1][1], 1)} percent."
        ),
        tuple(label for label, _value in wb_rows),
        tuple(quantize(value, 1) for _label, value in wb_rows),
        1,
        "%",
        "Percent",
    )
    comp = str(portfolio.comparison_year)
    paired = []
    for country in portfolio.countries:
        paired.append((country.name, country.wb_inflation[comp], country.imf_inflation[comp]))
    paired.sort(key=lambda item: item[1])
    grouped = charts.GroupedBarFigure(
        "cross-country-wb-imf",
        f"World Bank and IMF inflation, {comp}",
        "Same countries and year. Different official series. Do not average them.",
        (
            f"Paired {comp} inflation bars. Solid: World Bank. Hatched: IMF. "
            f"Highest World Bank: {paired[-1][0]} {quantize(paired[-1][1], 1)}%."
        ),
        tuple(item[0] for item in paired),
        ("World Bank", "IMF WEO"),
        (charts.PALETTE["blue"], charts.PALETTE["orange"]),
        (
            tuple(quantize(item[1], 1) for item in paired),
            tuple(quantize(item[2], 1) for item in paired),
        ),
        1,
        "%",
        "Percent",
    )
    own = []
    gaps = []
    for country in portfolio.countries:
        own.append((country.name, country.ownership[portfolio.survey_year]))
        female = country.ownership_female[portfolio.survey_year]
        male = country.ownership_male[portfolio.survey_year]
        gaps.append((country.name, female - male))
    own.sort(key=lambda item: item[1])
    gaps.sort(key=lambda item: item[1])
    own_fig = charts.BarFigure(
        "inclusion-account-ownership",
        f"Account ownership, ages 15+, {portfolio.survey_year}",
        "World Bank Findex FX.OWN.TOTL.ZS. A survey share, not wealth and not a ranking to act on.",
        (
            f"Account ownership in {portfolio.survey_year}. "
            f"Lowest: {own[0][0]} at {quantize(own[0][1], 1)} percent. "
            f"Highest: {own[-1][0]} at {quantize(own[-1][1], 1)} percent."
        ),
        tuple(label for label, _value in own),
        tuple(quantize(value, 1) for _label, value in own),
        1,
        "%",
        "Percent",
    )
    gap_bar = charts.BarFigure(
        "inclusion-gender-gap",
        f"Female minus male account ownership, {portfolio.survey_year}",
        "Computed from FX.OWN.TOTL.FE.ZS minus FX.OWN.TOTL.MA.ZS. Not a published gap series.",
        (
            f"Computed gender gap in {portfolio.survey_year}. "
            f"Most negative: {gaps[0][0]} at {quantize(gaps[0][1], 2)} percentage points."
        ),
        tuple(label for label, _value in gaps),
        tuple(quantize(value, 2) for _label, value in gaps),
        2,
        "",
        "Percentage points",
        True,
    )
    figures = [
        style,
        rates,
        gap_fig,
        curve,
        spread_fig,
        labor_u,
        labor_p,
        labor_c,
        filing_balance,
        filing_income,
        wb_fig,
        grouped,
        own_fig,
        gap_bar,
    ]
    for fig in figures:
        line = f"![{fig.alt}](figures/{fig.slug}.svg){{.teaching-figure}}"
        if len(line) > 200:
            raise RuntimeError(f"Alt line for {fig.slug} is {len(line)} characters")
    return figures


def _extreme(points: list[Obs]) -> tuple[Obs, Obs]:
    low = min(points, key=lambda item: (item.value, item.observed))
    high = max(points, key=lambda item: (item.value, item.observed))
    return low, high


def build_values(portfolio: Portfolio) -> dict:
    fund = in_window(portfolio.fred["FEDFUNDS"], WINDOW_START, portfolio.retrieved_on)[-1]
    now, prior, pct = portfolio.cpi_yoy[-1]
    observed, fund_value, cpi_value, gap_value = portfolio.gap[-1]
    spread_date, spread_value = portfolio.spread[-1]
    negative = sum(1 for _date, value in portfolio.spread if value < 0)
    unrate = in_window(portfolio.fred["UNRATE"], WINDOW_START, portfolio.retrieved_on)
    part = in_window(portfolio.fred["CIVPART"], WINDOW_START, portfolio.retrieved_on)
    pay_now, pay_prior, pay_pct = portfolio.payroll_yoy[-1]
    pay_level = {item.observed: item for item in portfolio.fred["PAYEMS"]}
    assets = portfolio.facts["Assets"][-1]
    deposits = portfolio.facts["Deposits"][-1]
    revenues = portfolio.facts["Revenues"][-1]
    income = portfolio.facts["NetIncomeLoss"][-1]
    ratio = Decimal(int(deposits["val"])) / Decimal(int(assets["val"])) * Decimal(100)
    asset_scaled, asset_text, _asset_unit = usd_text(int(assets["val"]))
    deposit_scaled, deposit_text, _deposit_unit = usd_text(int(deposits["val"]))
    _revenue_scaled, revenue_text, _revenue_unit = usd_text(int(revenues["val"]))
    _income_scaled, income_text, _income_unit = usd_text(int(income["val"]))
    displayed_ratio = quantize(deposit_scaled / asset_scaled * Decimal(100), 1)
    year = str(portfolio.complete_year)
    comp = str(portfolio.comparison_year)
    wb_latest = []
    comparison = []
    inclusion = []
    for country in portfolio.countries:
        if year in country.wb_inflation:
            wb_latest.append(
                {"iso3": country.iso3, "name": country.name, "year": year, "value": exact(country.wb_inflation[year])}
            )
        comparison.append(
            {
                "iso3": country.iso3,
                "name": country.name,
                "year": comp,
                "world_bank": exact(country.wb_inflation[comp]),
                "imf": exact(country.imf_inflation[comp]),
            }
        )
        female = country.ownership_female[portfolio.survey_year]
        male = country.ownership_male[portfolio.survey_year]
        inclusion.append(
            {
                "iso3": country.iso3,
                "name": country.name,
                "year": portfolio.survey_year,
                "ownership": exact(country.ownership[portfolio.survey_year]),
                "female": exact(female),
                "male": exact(male),
                "gap_female_minus_male": exact(female - male),
            }
        )
    usa = next(country for country in portfolio.countries if country.iso3 == "USA")
    usa_year = max(usa.wb_inflation)
    return {
        "retrieved_on": portfolio.retrieved_on,
        "as_of": portfolio.retrieved_on,
        "window_start": WINDOW_START,
        "last_complete_calendar_year": portfolio.complete_year,
        "comparison_year": portfolio.comparison_year,
        "survey_year": portfolio.survey_year,
        "rounding": "ROUND_HALF_UP",
        "modules": {
            "rates-and-inflation": {
                "fedfunds_latest": {"date": fund.observed, "raw": fund.raw},
                "cpi_yoy_latest": {
                    "date": now.observed,
                    "raw": now.raw,
                    "prior_date": prior.observed,
                    "prior_raw": prior.raw,
                    "yoy_percent": quantize(pct, 1),
                },
                "computed_gap_latest": {
                    "date": observed,
                    "fedfunds": exact(fund_value),
                    "cpi_yoy_percent": quantize(cpi_value, 1),
                    "gap_percentage_points": quantize(gap_value, 1),
                },
            },
            "yield-curve": {
                "curve_date": portfolio.curve_date,
                "yields": [
                    {"series_id": series_id, "label": label, "raw": item.raw}
                    for series_id, label, item in portfolio.curve
                ],
                "spread_latest": {"date": spread_date, "percentage_points": quantize(spread_value, 2)},
                "negative_spread_days": negative,
                "spread_days": len(portfolio.spread),
            },
            "labor-market": {
                "unrate_latest": {"date": unrate[-1].observed, "raw": unrate[-1].raw},
                "participation_latest": {"date": part[-1].observed, "raw": part[-1].raw},
                "payems_latest": {"date": pay_now.observed, "raw": pay_level[pay_now.observed].raw},
                "payems_prior": {"date": pay_prior.observed, "raw": pay_prior.raw},
                "payems_change_thousands": exact(pay_level[pay_now.observed].value - pay_prior.value),
                "payems_yoy_percent": quantize(pay_pct, 1),
            },
            "reading-a-10k": {
                "entity": "JPMORGAN CHASE & CO",
                "cik": portfolio.edgar_cik,
                "fiscal_year_end": assets["end"],
                "filed": assets["filed"],
                "accession": assets["accn"],
                "assets": int(assets["val"]),
                "deposits": int(deposits["val"]),
                "revenues": int(revenues["val"]),
                "net_income": int(income["val"]),
                "deposits_over_assets_percent": quantize(ratio, 1),
                "assets_text": asset_text,
                "deposits_text": deposit_text,
                "revenues_text": revenue_text,
                "net_income_text": income_text,
                "displayed_ratio_percent": displayed_ratio,
                "ten_k_url": filing_url(
                    portfolio.edgar_cik,
                    portfolio.filings["10-K"]["accessionNumber"],
                    portfolio.filings["10-K"]["primaryDocument"],
                ),
            },
            "cross-country-inflation": {
                "world_bank_year": year,
                "world_bank_missing": portfolio.wb_2025_missing,
                "world_bank_rows": wb_latest,
                "comparison_rows": comparison,
                "usa_latest_world_bank": {"year": usa_year, "value": exact(usa.wb_inflation[usa_year])},
                "imf_source": portfolio.imf_meta.get("source", ""),
                "imf_label": portfolio.imf_meta.get("label", ""),
                "imf_unit": portfolio.imf_meta.get("unit", ""),
            },
            "household-finance": {"rows": inclusion},
        },
    }


class Doc:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def add(self, text: str = "") -> None:
        self.lines.append(text)

    def p(self, text: str) -> None:
        self.lines.extend(prose(text))
        self.add("")

    def h(self, level: int, text: str) -> None:
        self.add(f"{'#' * level} {text}")
        self.add("")

    def items(self, rows: list[str], numbered: bool = False) -> None:
        for index, row in enumerate(rows, start=1):
            wrapped = prose(row, 92)
            prefix = f"{index}. " if numbered else "- "
            self.add(prefix + wrapped[0])
            pad = " " * len(prefix)
            for extra in wrapped[1:]:
                self.add(pad + extra)
        self.add("")

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        self.add("| " + " | ".join(headers) + " |")
        self.add("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            self.add("| " + " | ".join(row) + " |")
        self.add("")

    def figure(self, fig, caption: str) -> None:
        self.add(f"![{fig.alt}](figures/{fig.slug}.svg){{.teaching-figure}}")
        self.add("")
        self.p(f"Caption: {caption}")
        self.p(f"PNG of the same chart: [download](figures/{fig.slug}.png).")

    def answer(self, paragraphs: list[str]) -> None:
        self.h(2, "Answer key")
        self.p("Discussion questions stay open. This key answers the exercise only.")
        self.add('<details markdown="1">')
        self.add("<summary>Show the answer key</summary>")
        self.add("")
        for paragraph in paragraphs:
            self.p(paragraph)
        self.add("</details>")
        self.add("")

    def text(self) -> str:
        raw = "\n".join(self.lines)
        lines = [line.rstrip() for line in raw.split("\n")]
        rendered = "\n".join(lines).strip() + "\n"
        too_long = [line for line in rendered.split("\n") if len(line) > 200 and not line.startswith("|")]
        if too_long:
            raise RuntimeError("Markdown line exceeds 200 characters:\n" + "\n".join(too_long[:5]))
        return rendered


def _front(title: str, description: str, topics: str, retrieved: str) -> str:
    return (
        "---\n"
        f"title: {title}\n"
        f"description: {description}\n"
        "audience: [educators, general]\n"
        f"topics: [{topics}]\n"
        "status: published\n"
        f'last_reviewed: "{retrieved}"\n'
        "---\n"
    )


def _longest_run(points: list[Obs], places: int, target: Decimal) -> tuple[str, str]:
    quantized = [(item.observed, Decimal(quantize(item.value, places))) for item in points]
    best: tuple[str, str] | None = None
    start: str | None = None
    previous: int | None = None
    for index, (observed, value) in enumerate(quantized):
        if value != target:
            start = None
            previous = None
            continue
        if start is None or previous != index - 1:
            start = observed
        previous = index
        if best is None or (observed > best[1]) or (observed == best[1] and start < best[0]):
            best = (start, observed)
    if best is None:
        raise RuntimeError("no run for extreme")
    return best


def _when(start: str, end: str) -> str:
    if start == end:
        return f"on {start}"
    return f"from {start} to {end}"


def _range_sentence(label: str, points: list[Obs], places: int, suffix: str) -> str:
    quantized = [Decimal(quantize(item.value, places)) for item in points]
    low_value = min(quantized)
    high_value = max(quantized)
    low_span = _longest_run(points, places, low_value)
    high_span = _longest_run(points, places, high_value)
    return (
        f"In this window, {label} ranges from {low_value:.{places}f}{suffix} ({_when(*low_span)}) "
        f"to {high_value:.{places}f}{suffix} ({_when(*high_span)})."
    )


def _missing_months(points: list[Obs], start: str, end: str) -> list[str]:
    """Months inside the series span that have no observation. Months after the last point are not holes."""
    observed = [item.observed for item in points if start <= item.observed <= end]
    if len(observed) < 2:
        return []
    first, last = min(observed), max(observed)
    have = set(observed)
    missing: list[str] = []
    year, month = int(first[:4]), int(first[5:7])
    stop = (int(last[:4]), int(last[5:7]))
    while (year, month) < stop:
        key = f"{year:04d}-{month:02d}-01"
        if key not in have:
            missing.append(key)
        month += 1
        if month == 13:
            month = 1
            year += 1
    return missing


def _gap_note(points: list[Obs], series_id: str, as_of: str) -> str:
    missing = _missing_months(points, WINDOW_START, as_of)
    if not missing:
        return ""
    listed = ", ".join(missing)
    return (
        f" {series_id} has no observation on {listed} in this FRED snapshot, so the line breaks "
        "instead of bridging that month. This page does not state a cause."
    )


def usd_text(amount: int) -> tuple[Decimal, str, str]:
    """Scaled amount, prose, and axis label. Trillions from 1 trillion up; otherwise billions."""
    value = Decimal(amount)
    if abs(value) >= Decimal("1000000000000"):
        scaled = Decimal(quantize(value / Decimal("1000000000000"), 2))
        return scaled, f"${quantize(value / Decimal('1000000000000'), 2)} trillion", "Trillions of US dollars"
    scaled = Decimal(quantize(value / Decimal("1000000000"), 2))
    return scaled, f"${quantize(value / Decimal('1000000000'), 2)} billion", "Billions of US dollars"


def render_pages(portfolio: Portfolio) -> dict[str, str]:
    by_slug = {fig.slug: fig for fig in portfolio.figures}
    pages = {
        "index.md": page_index(portfolio, by_slug),
        "rates-and-inflation.md": page_rates(portfolio, by_slug),
        "yield-curve.md": page_yield(portfolio, by_slug),
        "labor-market.md": page_labor(portfolio, by_slug),
        "reading-a-10k.md": page_filing(portfolio, by_slug),
        "cross-country-inflation.md": page_countries(portfolio, by_slug),
        "household-finance.md": page_household(portfolio, by_slug),
    }
    return pages


def page_index(portfolio: Portfolio, figs: dict) -> str:
    values = portfolio.values["modules"]
    doc = Doc()
    doc.add(
        _front(
            "Teaching portfolio",
            "Shareable classroom modules with charts from FRED, SEC EDGAR, the IMF, and the World Bank",
            "inflation, teaching",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Teaching portfolio")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "Six short modules for educators and learners. Each one has learning objectives, "
        "charts drawn from a checked-in official snapshot, an explainer, discussion questions, "
        "an exercise, an answer key, and a sources block with series IDs and the retrieval date. "
        "Nothing here is a recommendation to buy, sell, or hold a product."
    )
    doc.p(
        "These modules do not use hypothetical numbers. Where a line is calculated from official "
        "inputs, the caption says it is computed in this library and is not a separate published series."
    )
    doc.h(2, "How the figures were made")
    doc.p(
        f"Retrieved {portfolio.retrieved_on}. Charts use observations from {WINDOW_START} through "
        f"{portfolio.retrieved_on}, and they ignore any later row. Regenerate the pages and figures "
        "from the snapshots with the command below. `--fetch` downloads fresh snapshots and needs "
        "a network; the default command does not. No API key is required. SEC EDGAR is asked for "
        "a User-Agent, and this script sends the same contact string already used by the educator reports."
    )
    doc.add("```bash")
    doc.add("python3 scripts/generate_teaching_portfolio.py")
    doc.add("python3 scripts/generate_teaching_portfolio.py --check")
    doc.add("```")
    doc.add("")
    doc.p(
        "FRED, World Bank, and IMF files under `data/teaching/snapshots/` are trimmed to the years "
        "these modules use. The manifest records the original request URL, the retrieval date, and the "
        "SHA-256 of the trimmed file. The EDGAR companyfacts and submissions documents are large, so the "
        "snapshot keeps the facts and filing fields this portfolio uses, copied unchanged, plus the "
        "SHA-256 of each full payload in `manifest.json`."
    )
    doc.figure(
        figs["chart-style"],
        "A style sample, not a data series. The same colors and dash patterns are used on every module. "
        "Numbers are also printed on the charts.",
    )
    doc.h(2, "Modules")
    rates = values["rates-and-inflation"]
    curve = values["yield-curve"]
    labor = values["labor-market"]
    filing = values["reading-a-10k"]
    doc.table(
        ["Module", "Official sources", "A latest reading in this snapshot"],
        [
            [
                "[Rates and inflation](rates-and-inflation.md)",
                "FRED `FEDFUNDS`, `CPIAUCSL`",
                f"{rates['fedfunds_latest']['raw']}% on {rates['fedfunds_latest']['date']}",
            ],
            [
                "[Yield curve](yield-curve.md)",
                "FRED `DGS3MO`, `DGS2`, `DGS5`, `DGS10`, `DGS30`",
                f"10-year minus 2-year {curve['spread_latest']['percentage_points']} on "
                f"{curve['spread_latest']['date']}",
            ],
            [
                "[Labor market](labor-market.md)",
                "FRED `UNRATE`, `PAYEMS`, `CIVPART`",
                f"Unemployment {labor['unrate_latest']['raw']}% on {labor['unrate_latest']['date']}",
            ],
            [
                "[Reading a 10-K](reading-a-10k.md)",
                "SEC EDGAR companyfacts, CIK `0000019617`",
                f"FY {filing['fiscal_year_end'][:4]} assets {filing['assets_text']}",
            ],
            [
                "[Cross-country inflation](cross-country-inflation.md)",
                "World Bank `FP.CPI.TOTL.ZG`, IMF `PCPIPCH`",
                f"Comparison year {portfolio.comparison_year}",
            ],
            [
                "[Household finance](household-finance.md)",
                "World Bank Findex `FX.OWN.TOTL.ZS` and the female and male series",
                f"Survey year {portfolio.survey_year}",
            ],
        ],
    )
    doc.h(2, "Data terms")
    doc.p(
        "The numbers on these pages are copied or computed from official series. "
        "The prose and chart code are this library's. Each publisher has its own terms."
    )
    doc.items(
        [
            "FRED, from the Federal Reserve Bank of St. Louis, redistributes series from source agencies. "
            "The series on these pages come from the Board of Governors, the Bureau of Labor Statistics, "
            "and the U.S. Treasury. Use follows the [St. Louis Fed legal terms](https://fred.stlouisfed.org/legal) "
            "and the source agency's terms.",
            "World Bank indicators, including Findex, are used under the "
            "[terms of use for datasets](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets), "
            "which apply Creative Commons Attribution 4.0.",
            "IMF DataMapper series, including WEO `PCPIPCH`, are used under the "
            "[IMF copyright and usage terms](https://www.imf.org/en/About/copyright-and-usage). "
            "The edition is the source string in the snapshot metadata.",
            "SEC EDGAR companyfacts are public filings. The amounts are the filer's tagged values. "
            "See the [SEC's EDGAR access guidance](https://www.sec.gov/os/accessing-edgar-data).",
        ]
    )
    doc.h(2, "Related")
    doc.items(
        [
            "[Guides](../index.md)",
            "[Inflation and capital preservation](../inflation-capital-preservation.md)",
            "[Educator examples](../educator-examples.md)",
            "[For educators and NGOs](../../about/for-educators-and-ngos.md)",
            "[Glossary](../../glossary.md)",
        ]
    )
    return doc.text()


def page_rates(portfolio: Portfolio, figs: dict) -> str:
    values = portfolio.values["modules"]["rates-and-inflation"]
    fund = values["fedfunds_latest"]
    cpi = values["cpi_yoy_latest"]
    gap = values["computed_gap_latest"]
    funds = in_window(portfolio.fred["FEDFUNDS"], WINDOW_START, portfolio.retrieved_on)
    gap_points = [Obs(item[0], quantize(item[3], 1), item[3]) for item in portfolio.gap]
    gap_number = Decimal(gap["gap_percentage_points"])
    if gap_number > 0:
        gap_words = "positive"
    elif gap_number < 0:
        gap_words = "negative"
    else:
        gap_words = "zero"
    shown_difference = Decimal(fund["raw"]) - Decimal(cpi["yoy_percent"])
    cpi_note = _gap_note(portfolio.fred["CPIAUCSL"], "CPIAUCSL", portfolio.retrieved_on)
    doc = Doc()
    doc.add(
        _front(
            "Rates and inflation",
            "Read the effective federal funds rate beside a 12-month change in the US CPI",
            "inflation, interest-rates",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Rates and inflation")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "This module shows two US readings that often get collapsed into the word rates: "
        "the effective federal funds rate, and a 12-month percent change in consumer prices "
        "computed from the CPI index. It does not say what a household should do with either number."
    )
    doc.h(2, "Learning objectives")
    doc.items(
        [
            "Distinguish the effective federal funds rate from a 12-month change in the CPI.",
            "Compute that CPI change from two index levels, and say that the result is not itself a FRED "
            "percent series.",
            "Explain why subtracting those two readings is a classroom comparison, not a published real "
            "interest rate and not a savings return.",
        ],
        numbered=True,
    )
    doc.h(2, "The picture")
    doc.figure(
        figs["rates-policy-and-inflation"],
        "Solid blue is FRED `FEDFUNDS`, the monthly average effective federal funds rate. "
        "Dashed vermillion is the 12-month percent change in `CPIAUCSL`, computed here from the index "
        "and rounded half up to one decimal. "
        f"Window: {WINDOW_START} through {portfolio.retrieved_on}. The vertical axis includes zero."
        f"{cpi_note}",
    )
    doc.figure(
        figs["rates-computed-gap"],
        "Each point is the displayed funds rate (two decimals) minus the displayed CPI change (one decimal). "
        "The difference is then rounded half up to one decimal. Computed in this library. "
        "It is not a separate published series and not a real interest rate.",
    )
    doc.h(2, "Explainer")
    doc.p(
        "`FEDFUNDS` is the monthly average effective federal funds rate in the market. "
        "It is not the target range the Federal Open Market Committee sets. That range is a different "
        "pair of FRED series, `DFEDTARL` and `DFEDTARU`. This module does not plot them and does not quote them."
    )
    doc.p(
        "`CPIAUCSL` is the seasonally adjusted Consumer Price Index for all urban consumers, an index, "
        "not a percent. The percent on the chart is `(this month's index / the same month a year earlier - 1) × 100`, "
        "rounded half up to one decimal place. If that prior month is missing, the point is skipped. "
        "A nearby month is not used as a stand-in."
    )
    doc.p(
        f"The latest funds-rate observation in the snapshot on or before {portfolio.retrieved_on} "
        f"is {fund['raw']}% on {fund['date']}. The CPI index on {cpi['date']} is {cpi['raw']}, "
        f"against {cpi['prior_raw']} on {cpi['prior_date']}. That ratio, rounded half up, is a "
        f"{cpi['yoy_percent']}% change. The gap chart uses those displayed readings: "
        f"{fund['raw']} minus {cpi['yoy_percent']} is {shown_difference}, which rounds half up to "
        f"{gap['gap_percentage_points']} percentage points. That result is {gap_words}."
    )
    doc.p(_range_sentence("the effective funds rate", funds, 2, "%"))
    doc.p(_range_sentence("the computed gap", gap_points, 1, " percentage points"))
    doc.p(
        "A household savings rate can sit far from the funds rate because of the product, the bank, "
        "fees, and insurance limits. This page does not collect those rates and does not suggest chasing the gap. "
        "For the literacy framing, use [Inflation and capital preservation](../inflation-capital-preservation.md)."
    )
    doc.h(2, "Discussion questions")
    doc.items(
        [
            "The funds rate and the CPI change are both drawn as percents. What is each one actually measuring?",
            "Why might a savings-account rate and the federal funds rate differ, without treating the "
            "difference as something to act on?",
            "The chart ends at the latest month in the snapshot. What would you open before quoting the "
            "endpoint next month?",
        ],
        numbered=True,
    )
    doc.h(2, "Exercise")
    doc.p(
        f"Using the readings printed for {cpi['date']}, subtract the 12-month CPI change "
        f"({cpi['yoy_percent']}%, one decimal) from the effective federal funds rate "
        f"({fund['raw']}%, two decimals). Round that difference half up to one decimal place. "
        "Say whether the result is positive or negative. Also name the two CPI index levels behind the change."
    )
    doc.answer(
        [
            f"The displayed effective federal funds rate on {fund['date']} is {fund['raw']} percent (`FEDFUNDS`). "
            f"The CPI index is {cpi['raw']} on {cpi['date']} and {cpi['prior_raw']} on {cpi['prior_date']} "
            f"(`CPIAUCSL`). The displayed 12-month change is {cpi['yoy_percent']} percent. "
            f"{fund['raw']} minus {cpi['yoy_percent']} is {shown_difference}, which rounds half up to "
            f"{gap['gap_percentage_points']} percentage points. The result is {gap_words}. "
            "The gap compares two readings. It is not a published real rate and not a return.",
        ]
    )
    doc.h(2, "Sources and citations")
    doc.p(
        f"Retrieved {portfolio.retrieved_on}. Observations after that date are ignored. "
        "Request URLs are also in `data/teaching/snapshots/manifest.json`. "
        "Terms: [data terms](index.md#data-terms)."
    )
    doc.table(
        ["Series", "ID", "Observation", "Value", "Series page"],
        [
            [
                "Effective federal funds rate",
                "FEDFUNDS",
                fund["date"],
                f"{fund['raw']}%",
                f"[FRED]({fred_page('FEDFUNDS')})",
            ],
            ["CPI index, seasonally adjusted", "CPIAUCSL", cpi["date"], cpi["raw"], f"[FRED]({fred_page('CPIAUCSL')})"],
            [
                "CPI index, one year earlier",
                "CPIAUCSL",
                cpi["prior_date"],
                cpi["prior_raw"],
                f"[FRED]({fred_page('CPIAUCSL')})",
            ],
            [
                "12-month CPI change, rounded half up",
                "CPIAUCSL",
                cpi["date"],
                f"{cpi['yoy_percent']}%",
                "Computed here, not a separate FRED series",
            ],
            [
                "Displayed funds rate minus displayed CPI change",
                "FEDFUNDS and CPIAUCSL",
                gap["date"],
                f"{gap['gap_percentage_points']} pp",
                "Not a separate FRED series",
            ],
        ],
    )
    doc.add("```text")
    doc.add(fred_url("FEDFUNDS"))
    doc.add(fred_url("CPIAUCSL"))
    doc.add("```")
    doc.add("")
    doc.h(2, "Related")
    doc.items(
        [
            "[Teaching portfolio](index.md)",
            "[Inflation and capital preservation](../inflation-capital-preservation.md)",
            "[Glossary: inflation](../../glossary.md#inflation)",
            "[Glossary: capital preservation](../../glossary.md#capital-preservation)",
            "[Where to check official figures](../../about/where-to-check.md)",
        ]
    )
    return doc.text()


def page_yield(portfolio: Portfolio, figs: dict) -> str:
    values = portfolio.values["modules"]["yield-curve"]
    yields = values["yields"]
    spread = values["spread_latest"]
    slope = (
        "above the 2-year yield, so the curve slopes upward on this date"
        if Decimal(spread["percentage_points"]) > 0
        else "below the 2-year yield, so the spread is negative on this date"
        if Decimal(spread["percentage_points"]) < 0
        else "equal to the 2-year yield on this date"
    )
    doc = Doc()
    doc.add(
        _front(
            "Yield curve",
            "Read US Treasury constant-maturity yields and the 10-year minus 2-year spread",
            "interest-rates, treasuries",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Yield curve")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "A yield curve plots interest rates against maturity on one date. This module uses US Treasury "
        "constant-maturity yields from FRED. It does not say whether to lend, borrow, or buy a bond."
    )
    doc.h(2, "Learning objectives")
    doc.items(
        [
            "Read a yield curve as yields at several maturities on a single date.",
            "Compute the 10-year minus 2-year spread and state the sign.",
            "Keep Treasury yields distinct from a household savings rate.",
        ],
        numbered=True,
    )
    doc.h(2, "The picture")
    doc.figure(
        figs["yield-curve-snapshot"],
        f"One date, {portfolio.curve_date}, the latest date on or before {portfolio.retrieved_on} "
        "with a value for every maturity plotted. The vertical axis does not start at zero, so read the labels. "
        "The slope is the difference between labels, not the steepness against a zero baseline.",
    )
    doc.figure(
        figs["yield-spread"],
        "Each point is the 10-year constant-maturity yield minus the 2-year yield that same day, in percentage points. "
        "Computed in this library from `DGS10` and `DGS2`. It is not a separate published series. "
        f"The spread is negative on {values['negative_spread_days']} of {values['spread_days']} plotted dates. "
        "The vertical axis includes zero.",
    )
    doc.h(2, "Explainer")
    doc.p(
        "FRED's `DGS` series are constant-maturity Treasury yields, in percent, for business days. "
        "A missing day in the file (often a period instead of a number) is skipped. This chart does not fill the gap."
    )
    doc.p(
        f"On {portfolio.curve_date}, the 10-year yield is {slope}. "
        f"The computed spread, 10-year minus 2-year, is {spread['percentage_points']} percentage points. "
        "A negative spread means the 2-year yield is higher than the 10-year yield that day. "
        "People often call that an inversion. The word names the arithmetic. It is not a forecast on this page."
    )
    listed = ", ".join(f"{item['label']} {item['raw']}%" for item in yields)
    doc.p(f"The five yields on {portfolio.curve_date} are {listed}.")
    doc.p(
        "These are not the rate on a savings account, a certificate of deposit, or a loan. "
        "Comparing them to a household product needs the product's own terms, read from the provider "
        "or a regulator, which this snapshot does not include."
    )
    doc.h(2, "Discussion questions")
    doc.items(
        [
            "On the snapshot date, which maturity has the highest yield and which has the lowest?",
            "What does a negative 10-year-minus-2-year spread mean as arithmetic, before any story about the future?",
            "What else would you need before comparing a Treasury yield with a savings-account rate?",
        ],
        numbered=True,
    )
    ten = next(item for item in yields if item["series_id"] == "DGS10")
    two = next(item for item in yields if item["series_id"] == "DGS2")
    doc.h(2, "Exercise")
    doc.p(
        f"On {portfolio.curve_date}, subtract the 2-year yield from the 10-year yield. "
        "Give the difference to two decimal places. Does the 10-year yield sit above or below the 2-year yield?"
    )
    relation = (
        "above"
        if Decimal(ten["raw"]) > Decimal(two["raw"])
        else "below"
        if Decimal(ten["raw"]) < Decimal(two["raw"])
        else "equal to"
    )
    doc.answer(
        [
            f"On {portfolio.curve_date}, `DGS10` is {ten['raw']}% and `DGS2` is {two['raw']}%. "
            f"{ten['raw']} minus {two['raw']} is {spread['percentage_points']} percentage points. "
            f"The 10-year yield is {relation} the 2-year yield. "
            "That is a description of this date, not a bond recommendation.",
        ]
    )
    doc.h(2, "Sources and citations")
    doc.p(f"Retrieved {portfolio.retrieved_on}. The curve uses {portfolio.curve_date}, the latest common observation.")
    doc.table(
        ["Series", "ID", "Observation", "Value", "Series page"],
        [
            *[
                [
                    item["label"] + " Treasury constant maturity",
                    item["series_id"],
                    portfolio.curve_date,
                    f"{item['raw']}%",
                    f"[FRED]({fred_page(item['series_id'])})",
                ]
                for item in yields
            ],
            [
                "10-year minus 2-year, computed here",
                "DGS10 minus DGS2",
                spread["date"],
                f"{spread['percentage_points']} pp",
                "Not a separate FRED series",
            ],
        ],
    )
    doc.add("```text")
    for series_id, _label in CURVE:
        doc.add(fred_url(series_id))
    doc.add("```")
    doc.add("")
    doc.h(2, "Related")
    doc.items(
        [
            "[Teaching portfolio](index.md)",
            "[Rates and inflation](rates-and-inflation.md)",
            "[TreasuryDirect](../../vehicles/us/treasurydirect.md)",
            "[Glossary](../../glossary.md)",
        ]
    )
    return doc.text()


def page_labor(portfolio: Portfolio, figs: dict) -> str:
    values = portfolio.values["modules"]["labor-market"]
    unrate = in_window(portfolio.fred["UNRATE"], WINDOW_START, portfolio.retrieved_on)
    part = in_window(portfolio.fred["CIVPART"], WINDOW_START, portfolio.retrieved_on)
    change = Decimal(values["payems_change_thousands"])
    verb = "higher" if change > 0 else "lower" if change < 0 else "unchanged"
    doc = Doc()
    doc.add(
        _front(
            "Labor market",
            "Read unemployment, payroll employment, and labor force participation as three different questions",
            "labor, unemployment",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Labor market")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "Three US labor-market series answer three different questions: the share of the labor force "
        "that is unemployed, the count of jobs on payrolls, and the share of the population in the labor force. "
        "This module does not turn any of them into a personal money decision."
    )
    doc.h(2, "Learning objectives")
    doc.items(
        [
            "Say what the unemployment rate, nonfarm payroll employment, and the participation rate each count.",
            "Compute a 12-month percent change in payrolls from two levels, and keep the unit (thousands of "
            "persons) attached to the level.",
            "Name one thing the unemployment rate does not count.",
        ],
        numbered=True,
    )
    doc.h(2, "The picture")
    doc.figure(
        figs["labor-unemployment"],
        f"FRED `UNRATE`, the seasonally adjusted U-3 unemployment rate. Window {WINDOW_START} through "
        f"{portfolio.retrieved_on}. "
        "The vertical axis includes zero." + _gap_note(portfolio.fred["UNRATE"], "UNRATE", portfolio.retrieved_on),
    )
    doc.figure(
        figs["labor-payroll-change"],
        "Twelve-month percent change in FRED `PAYEMS` (total nonfarm payrolls, seasonally adjusted, thousands "
        "of persons). "
        "Computed in this library from the levels. It is not a separate published series. The vertical axis "
        "includes zero.",
    )
    doc.figure(
        figs["labor-participation"],
        "FRED `CIVPART`, the labor force participation rate. The vertical axis does not start at zero, "
        "so a small move looks larger than it would on an axis from zero. Read the labels."
        + _gap_note(portfolio.fred["CIVPART"], "CIVPART", portfolio.retrieved_on),
    )
    doc.h(2, "Explainer")
    doc.p(
        "`UNRATE` is the seasonally adjusted unemployment rate: unemployed people as a percent of the labor force. "
        "People who are not looking for work are outside that rate. `PAYEMS` counts jobs on nonfarm payrolls, "
        "in thousands of persons, not a percent. `CIVPART` is the share of the civilian noninstitutional population "
        "that is in the labor force."
    )
    doc.p(_range_sentence("the unemployment rate", unrate, 1, "%"))
    doc.p(_range_sentence("the participation rate", part, 1, "%"))
    doc.p(
        f"On {values['payems_latest']['date']}, payroll employment is {values['payems_latest']['raw']} "
        f"thousand persons, "
        f"against {values['payems_prior']['raw']} thousand on {values['payems_prior']['date']}. "
        f"The level is {verb} by {values['payems_change_thousands']} thousand persons. "
        f"The computed 12-month percent change is {values['payems_yoy_percent']}%."
    )
    doc.p(
        f"The latest unemployment rate in the window is {values['unrate_latest']['raw']}% "
        f"on {values['unrate_latest']['date']}. The latest participation rate is "
        f"{values['participation_latest']['raw']}% on {values['participation_latest']['date']}."
    )
    doc.h(2, "Discussion questions")
    doc.items(
        [
            "Describe one way the unemployment rate could fall even if payroll employment did not rise.",
            "PAYEMS counts jobs on payrolls. Whose work might that survey miss?",
            "If the question is whether work feels harder to find, which chart would you open, and what would "
            "it still not tell you?",
        ],
        numbered=True,
    )
    doc.h(2, "Exercise")
    doc.p(
        f"Read the unemployment rate for {values['unrate_latest']['date']}. Then subtract payroll employment "
        f"on {values['payems_prior']['date']} from payroll employment on {values['payems_latest']['date']}. "
        "Keep the unit. Is the later level higher or lower?"
    )
    doc.answer(
        [
            f"The unemployment rate on {values['unrate_latest']['date']} is {values['unrate_latest']['raw']} "
            f"percent (`UNRATE`). "
            f"Payroll employment is {values['payems_latest']['raw']} thousand persons on "
            f"{values['payems_latest']['date']} "
            f"and {values['payems_prior']['raw']} thousand on {values['payems_prior']['date']} (`PAYEMS`). "
            f"The difference is {values['payems_change_thousands']} thousand persons, so the later level is {verb}. "
            f"The computed percent change is {values['payems_yoy_percent']} percent. "
            "A higher payroll count is a description of this series, not advice about a job or a product.",
        ]
    )
    doc.h(2, "Sources and citations")
    doc.p(f"Retrieved {portfolio.retrieved_on}. `PAYEMS` is published in thousands of persons.")
    doc.table(
        ["Series", "ID", "Observation", "Value", "Series page"],
        [
            [
                "Unemployment rate",
                "UNRATE",
                values["unrate_latest"]["date"],
                f"{values['unrate_latest']['raw']}%",
                f"[FRED]({fred_page('UNRATE')})",
            ],
            [
                "Nonfarm payrolls",
                "PAYEMS",
                values["payems_latest"]["date"],
                f"{values['payems_latest']['raw']} thousand",
                f"[FRED]({fred_page('PAYEMS')})",
            ],
            [
                "Nonfarm payrolls, one year earlier",
                "PAYEMS",
                values["payems_prior"]["date"],
                f"{values['payems_prior']['raw']} thousand",
                f"[FRED]({fred_page('PAYEMS')})",
            ],
            [
                "Payroll change, computed here",
                "PAYEMS",
                values["payems_latest"]["date"],
                f"{values['payems_change_thousands']} thousand ({values['payems_yoy_percent']}%)",
                "Not a separate FRED series",
            ],
            [
                "Labor force participation",
                "CIVPART",
                values["participation_latest"]["date"],
                f"{values['participation_latest']['raw']}%",
                f"[FRED]({fred_page('CIVPART')})",
            ],
        ],
    )
    doc.add("```text")
    for series_id in ("UNRATE", "PAYEMS", "CIVPART"):
        doc.add(fred_url(series_id))
    doc.add("```")
    doc.add("")
    doc.h(2, "Related")
    doc.items(
        [
            "[Teaching portfolio](index.md)",
            "[Emergency savings](../emergency-savings.md)",
            "[Glossary](../../glossary.md)",
        ]
    )
    return doc.text()


def page_filing(portfolio: Portfolio, figs: dict) -> str:
    values = portfolio.values["modules"]["reading-a-10k"]
    ten_k = portfolio.filings["10-K"]
    doc = Doc()
    doc.add(
        _front(
            "Reading a 10-K",
            "Find assets, deposits, revenues, and net income in a public EDGAR 10-K",
            "filings, deposits",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Reading a 10-K")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "A Form 10-K is a company's annual report filed with the US Securities and Exchange Commission. "
        "This module reads four tagged lines from one public filing, JPMorgan Chase & Co. "
        "(EDGAR name JPMORGAN CHASE & CO, CIK 0000019617). The company is here because the filing is public "
        "and this library already uses it in the educator filing watch. The page is not an assessment of the company "
        "and not a recommendation to buy, sell, or hold its securities."
    )
    doc.h(2, "Learning objectives")
    doc.items(
        [
            "Open a 10-K from its EDGAR accession number and primary document.",
            "Separate balance-sheet amounts (assets, deposits) from full-year flows (revenues, net income).",
            "Explain why a deposit total in a 10-K is not an insured balance.",
        ],
        numbered=True,
    )
    doc.h(2, "The picture")
    doc.figure(
        figs["filing-assets-deposits"],
        "Grouped bars for each fiscal year ending 31 December. The bars are not joined. "
        "Each bar is the current-year column of that year's 10-K: `form` is `10-K`, `fp` is `FY`, "
        "and `fy` matches the year of `end`. Comparative columns repeated in a later 10-K are excluded. "
        "Amounts are the tagged integer divided by one trillion, rounded half up to two decimals.",
    )
    doc.figure(
        figs["filing-revenue-income"],
        "Revenues (`Revenues`) and net income (`NetIncomeLoss`) for the full fiscal year, as separate bars. "
        "Same selection rule. Amounts are the tagged integer divided by one billion, rounded half up to two decimals.",
    )
    doc.h(2, "Explainer")
    doc.p(
        "Assets and deposits are stocks: amounts at a period end. Revenues and net income are flows: "
        "amounts over a fiscal year. Deposits here are an accounting total for the consolidated company. "
        "Deposit insurance is a separate legal limit. This snapshot does not include that limit, so this page "
        "does not state one. Read the current limit on the FDIC's own page, and write down the date you read it."
    )
    doc.p(
        f"For the fiscal year ended {values['fiscal_year_end']}, filed {values['filed']}, "
        f"accession `{values['accession']}`: assets {usd_text(int(values['assets']))[1]}, "
        f"deposits {usd_text(int(values['deposits']))[1]}, "
        f"revenues {usd_text(int(values['revenues']))[1]}, and net income {usd_text(int(values['net_income']))[1]}. "
        "Those are the tagged US dollar amounts scaled and rounded half up. "
        f"Using those rounded amounts, deposits divided by assets are {values['displayed_ratio_percent']} percent."
    )
    doc.p(
        "The same year can show a different number in a later 10-K when the company presents comparative columns "
        "or revises a figure. The charts keep the number from the 10-K whose fiscal-year tag matches that year."
    )
    doc.h(2, "Discussion questions")
    doc.items(
        [
            "Why is a deposit line on a bank's balance sheet not the amount one depositor is insured for?",
            "Why might the number for an earlier year change when you open a later 10-K?",
            "What would you want to see besides these four lines before describing the business in your own words?",
        ],
        numbered=True,
    )
    doc.h(2, "Exercise")
    doc.p(
        f"Using the rounded amounts in the explainer for the fiscal year ended {values['fiscal_year_end']} "
        f"({values['deposits_text']} of deposits and {values['assets_text']} of assets), divide deposits by assets "
        "and give the result as a percent to one decimal place. Then name the filing date and the accession number."
    )
    doc.answer(
        [
            f"The explainer amounts are {values['deposits_text']} of deposits and {values['assets_text']} of assets. "
            f"Dividing those rounded amounts gives {values['displayed_ratio_percent']} percent. "
            f"The 10-K was filed on {values['filed']}, accession `{values['accession']}`, "
            f"for the period ended {values['fiscal_year_end']}. "
            f"Primary document: [10-K on EDGAR]({values['ten_k_url']}). "
            "The ratio describes two lines in a filing. It is not a capital ratio, not an insurance "
            "calculation, and not a recommendation.",
        ]
    )
    doc.h(2, "Sources and citations")
    doc.p(
        f"Retrieved {portfolio.retrieved_on}. Facts are copied from the SEC companyfacts JSON. "
        "The full payload is not stored; `data/teaching/snapshots/manifest.json` records its SHA-256. "
        "Selection rule: `form` `10-K`, `fp` `FY`, `fy` equal to the year of `end`; duration facts must also "
        "start in that year."
    )
    doc.table(
        ["Line", "US-GAAP concept", "Period end", "Filed", "Tagged USD", "Rounded reading"],
        [
            [
                "Assets",
                "Assets",
                values["fiscal_year_end"],
                values["filed"],
                str(values["assets"]),
                values["assets_text"],
            ],
            [
                "Deposits",
                "Deposits",
                values["fiscal_year_end"],
                values["filed"],
                str(values["deposits"]),
                values["deposits_text"],
            ],
            [
                "Revenues",
                "Revenues",
                values["fiscal_year_end"],
                values["filed"],
                str(values["revenues"]),
                values["revenues_text"],
            ],
            [
                "Net income",
                "NetIncomeLoss",
                values["fiscal_year_end"],
                values["filed"],
                str(values["net_income"]),
                values["net_income_text"],
            ],
            [
                "Deposits / assets from the rounded readings",
                "Deposits and Assets",
                values["fiscal_year_end"],
                values["filed"],
                "see tagged amounts",
                f"{values['displayed_ratio_percent']}%",
            ],
        ],
    )
    doc.p(
        f"Latest 10-K on or before {portfolio.retrieved_on}: filed {ten_k['filingDate']}, "
        f"accession `{ten_k['accessionNumber']}`, primary document `{ten_k['primaryDocument']}`."
    )
    doc.add("```text")
    doc.add("https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json")
    doc.add("https://data.sec.gov/submissions/CIK0000019617.json")
    doc.add(values["ten_k_url"])
    doc.add("```")
    doc.add("")
    doc.h(2, "Related")
    doc.items(
        [
            "[Teaching portfolio](index.md)",
            "[Educator examples](../educator-examples.md)",
            "[FDIC savings](../../vehicles/us/fdic-savings.md)",
            "[Glossary: deposit insurance](../../glossary.md#deposit-insurance)",
            "[FDIC deposit insurance](https://www.fdic.gov/resources/deposit-insurance/)",
        ]
    )
    return doc.text()


def page_countries(portfolio: Portfolio, figs: dict) -> str:
    block = portfolio.values["modules"]["cross-country-inflation"]
    year = block["world_bank_year"]
    comp = str(portfolio.comparison_year)
    rows = block["world_bank_rows"]
    highest = max(rows, key=lambda item: Decimal(item["value"]))
    comparison = block["comparison_rows"]
    highest_name = highest["name"]
    imf_for_highest = next(item for item in comparison if item["name"] == highest_name)
    # The highest WB row is for `year`, which may differ from the comparison year.
    # Exercise uses the plotted latest-year chart, so answer that year.
    doc = Doc()
    doc.add(
        _front(
            "Cross-country inflation",
            "Compare World Bank and IMF inflation readings for the library's household countries",
            "inflation, cross-country",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Cross-country inflation")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "Two official compilers publish annual inflation for the same countries. The numbers do not have to match. "
        "This module puts them side by side for the countries in this library. It does not rank places to put money, "
        "and it does not average the two sources into a single true rate."
    )
    doc.h(2, "Learning objectives")
    doc.items(
        [
            "Read an annual inflation bar as one official series for one year, with the year attached.",
            "Treat a missing country as a gap, not as zero.",
            "Label IMF values for years after the last complete calendar year as WEO projections.",
        ],
        numbered=True,
    )
    doc.h(2, "The picture")
    missing = ", ".join(block["world_bank_missing"]) if block["world_bank_missing"] else "none"
    doc.figure(
        figs["cross-country-wb-inflation"],
        f"World Bank indicator `FP.CPI.TOTL.ZG` for {year}, the last complete calendar year on "
        f"{portfolio.retrieved_on}. "
        f"Countries with no {year} value in this snapshot: {missing}. They are omitted. They are not zero.",
    )
    doc.figure(
        figs["cross-country-wb-imf"],
        f"Solid bars are the World Bank. Hatched bars are IMF DataMapper `PCPIPCH` for {comp}, "
        "the latest year in this snapshot where every library country has both. "
        "The series measure related prices differently. A gap between bars is not a data-entry error by itself.",
    )
    doc.h(2, "Explainer")
    doc.p(
        f"The World Bank indicator name in the snapshot is: {portfolio.wb_names['FP.CPI.TOTL.ZG']}. "
        f'The IMF metadata in the snapshot calls `PCPIPCH` "{block["imf_label"]}" '
        f'({block["imf_unit"]}), source "{block["imf_source"]}".'
    )
    doc.p(
        f"On the {year} World Bank chart, the highest value among the countries that have a number is "
        f"{highest['name']}, {quantize(Decimal(highest['value']), 1)} percent. "
        f"The United States' latest World Bank observation in this pull is {block['usa_latest_world_bank']['year']}: "
        f"{quantize(Decimal(block['usa_latest_world_bank']['value']), 1)} percent."
    )
    imf_years = sorted({int(item) for country in portfolio.countries for item in country.imf_inflation})
    imf_last_year = imf_years[-1]
    projection_years = [str(item) for item in range(portfolio.complete_year + 1, imf_last_year + 1)]
    doc.p(
        f'The snapshot metadata names the source as "{block["imf_source"]}". '
        f"For these countries the series runs through {imf_last_year}. "
        f"History charts stop at {portfolio.complete_year}, the last calendar year that had ended on "
        f"{portfolio.retrieved_on}. Later years are in the table below and are labeled WEO projections: "
        "they are the vintage's published values for years that were not finished on the retrieval date, "
        "not measured inflation."
    )
    doc.p(
        f"For {highest['name']} in {comp}, the World Bank value is "
        f"{quantize(Decimal(imf_for_highest['world_bank']), 1)} percent and the IMF value is "
        f"{quantize(Decimal(imf_for_highest['imf']), 1)} percent. "
        "Use the comparison chart and the table for every country. Do not average the pair."
    )
    doc.h(2, "WEO projections")
    doc.p(
        f"IMF `PCPIPCH` for {projection_years[0]} through {projection_years[-1]}, from the source named in the "
        f'snapshot metadata ("{block["imf_source"]}"). Each of these years is a WEO projection in this module. '
        "They are not plotted on the history charts. Values are rounded half up to one decimal."
    )
    future_rows = []
    for country in portfolio.countries:
        row = [country.name, country.iso3]
        for item in projection_years:
            raw = country.imf_inflation.get(item)
            row.append(quantize(raw, 1) if raw is not None else "no value")
        future_rows.append(row)
    doc.table(["Country", "ISO3", *projection_years], future_rows)
    doc.h(2, "Discussion questions")
    doc.items(
        [
            "Pick a country where the two bars differ. What are two reasons official inflation measures can "
            "differ without either number being a typo?",
            "A country is missing from the latest-year chart. What should you do instead of treating the gap as zero?",
            "How should a class label an IMF cell for a year that was not finished on the retrieval date?",
        ],
        numbered=True,
    )
    doc.h(2, "Exercise")
    doc.p(
        f"On the {year} World Bank chart, which plotted country is highest, and what is that value to one decimal "
        "place? If a library country is missing, name it and do not treat it as zero."
    )
    missing_sentence = (
        f"Missing in {year}: {missing}."
        if block["world_bank_missing"]
        else f"Every library country has a {year} World Bank value in this snapshot."
    )
    doc.answer(
        [
            f"The highest plotted World Bank value for {year} is {highest['name']} (`{highest['iso3']}`), "
            f"{quantize(Decimal(highest['value']), 1)} percent (`FP.CPI.TOTL.ZG`, rounded half up to one decimal). "
            f"{missing_sentence} "
            "A higher inflation reading is not a verdict on a country and not a product suggestion.",
        ]
    )
    doc.h(2, "Sources and citations")
    doc.p(
        f"Retrieved {portfolio.retrieved_on}. World Bank indicator page and IMF DataMapper page are linked below. "
        "The exact API requests are in the manifest and in the code block."
    )
    doc.table(
        ["Publisher", "ID", "What the snapshot calls it", "Page"],
        [
            [
                "World Bank",
                "FP.CPI.TOTL.ZG",
                portfolio.wb_names["FP.CPI.TOTL.ZG"],
                "[Indicator](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG)",
            ],
            [
                "IMF DataMapper",
                "PCPIPCH",
                f"{block['imf_label']}; {block['imf_source']}",
                "[DataMapper](https://www.imf.org/external/datamapper/PCPIPCH)",
            ],
        ],
    )
    doc.p(f"World Bank {year} values, rounded half up to one decimal:")
    doc.table(
        ["Country", "ISO3", "Year", "Value"],
        [
            [item["name"], item["iso3"], item["year"], quantize(Decimal(item["value"]), 1)]
            for item in sorted(rows, key=lambda item: item["name"])
        ],
    )
    doc.p(f"Comparison year {comp}, both series rounded half up to one decimal:")
    doc.table(
        ["Country", "ISO3", "World Bank", "IMF PCPIPCH"],
        [
            [
                item["name"],
                item["iso3"],
                quantize(Decimal(item["world_bank"]), 1),
                quantize(Decimal(item["imf"]), 1),
            ]
            for item in sorted(comparison, key=lambda item: item["name"])
        ],
    )
    doc.add("```text")
    doc.add(wb_url("FP.CPI.TOTL.ZG", 1))
    doc.add("https://www.imf.org/external/datamapper/api/v1/PCPIPCH")
    doc.add("https://www.imf.org/external/datamapper/api/v1/indicators")
    doc.add("```")
    doc.add("")
    doc.h(2, "Related")
    doc.items(
        [
            "[Teaching portfolio](index.md)",
            "[Inflation and capital preservation](../inflation-capital-preservation.md)",
            "[Where to check official figures](../../about/where-to-check.md)",
            "[Household finance](household-finance.md)",
        ]
    )
    return doc.text()


def page_household(portfolio: Portfolio, figs: dict) -> str:
    rows = portfolio.values["modules"]["household-finance"]["rows"]
    lowest = min(rows, key=lambda item: Decimal(item["ownership"]))
    widest = min(rows, key=lambda item: Decimal(item["gap_female_minus_male"]))
    doc = Doc()
    doc.add(
        _front(
            "Household finance and financial inclusion",
            "Read Findex account-ownership shares, including the female-minus-male gap",
            "inclusion, household",
            portfolio.retrieved_on,
        )
    )
    doc.h(1, "Household finance and financial inclusion")
    doc.add(DISCLAIMER)
    doc.add("")
    doc.p(
        "Account ownership is a survey share: how many adults said they have an account at a financial institution "
        "or with a mobile-money provider. This module reads that share for the library's countries, and the "
        "female-minus-male difference computed from the two published sex splits. It is not wealth, not control of "
        "the account, and not a ranking of where to bank."
    )
    doc.h(2, "Learning objectives")
    doc.items(
        [
            "Read an account-ownership percent as a share of adults ages 15+ in a survey year.",
            "Compute a female-minus-male gap from the two official series and state the sign.",
            "Name what the share does not measure: balances, fees, or who controls the account.",
        ],
        numbered=True,
    )
    doc.h(2, "The picture")
    doc.figure(
        figs["inclusion-account-ownership"],
        f"World Bank `FX.OWN.TOTL.ZS` for {portfolio.survey_year}, the latest survey year in this snapshot "
        "present for every library country. Sorted from lower to higher. The number is a survey share.",
    )
    doc.figure(
        figs["inclusion-gender-gap"],
        f"Female share minus male share in {portfolio.survey_year}, in percentage points. "
        "Computed in this library from `FX.OWN.TOTL.FE.ZS` and `FX.OWN.TOTL.MA.ZS`. "
        "It is not a separate published series. A negative bar means the reported female share is lower.",
    )
    doc.h(2, "Explainer")
    doc.p(f"The World Bank name for the total series is: {portfolio.wb_names['FX.OWN.TOTL.ZS']}.")
    doc.p(f"The female series is named: {portfolio.wb_names['FX.OWN.TOTL.FE.ZS']}.")
    doc.p(f"The male series is named: {portfolio.wb_names['FX.OWN.TOTL.MA.ZS']}.")
    doc.p(
        f"In {portfolio.survey_year}, the lowest total share among these countries is {lowest['name']} "
        f"at {quantize(Decimal(lowest['ownership']), 1)} percent. "
        f"The most negative female-minus-male gap is {widest['name']} at "
        f"{quantize(Decimal(widest['gap_female_minus_male']), 2)} percentage points "
        f"(female {quantize(Decimal(widest['female']), 2)} minus male {quantize(Decimal(widest['male']), 2)}). "
        "That gap is negative: the reported female share is lower."
    )
    doc.p(
        "Findex years in this snapshot are survey years, not every calendar year. "
        "A higher share means more adults reported an account. It does not say the account is free of fees, "
        "that the balance is large, or that the person who answered controls the money. "
        "The [woman-led household pathway](../../pathways/woman-led-household.md) is about access and control; "
        "this chart can speak to reported access by sex, and it cannot see control inside a household."
    )
    doc.h(2, "Discussion questions")
    doc.items(
        [
            "Account ownership is a share of adults. What does a high share not tell you about balances, "
            "fees, or control?",
            "A positive female-minus-male gap and a negative one mean different things. State both in words.",
            "Which part of access versus control can this chart speak to, and which part can it not?",
        ],
        numbered=True,
    )
    doc.h(2, "Exercise")
    doc.p(
        f"For {portfolio.survey_year}, name the library country with the lowest account-ownership share and "
        "the country with the most negative female-minus-male gap. Give the ownership share to one decimal "
        "place and the gap to two decimal places. Say whether that gap is positive or negative."
    )
    doc.answer(
        [
            f"Lowest account ownership in {portfolio.survey_year} is {lowest['name']} (`{lowest['iso3']}`), "
            f"{quantize(Decimal(lowest['ownership']), 1)} percent (`FX.OWN.TOTL.ZS`). "
            f"The most negative gap is {widest['name']} (`{widest['iso3']}`): female "
            f"{quantize(Decimal(widest['female']), 2)} minus male {quantize(Decimal(widest['male']), 2)} "
            f"is {quantize(Decimal(widest['gap_female_minus_male']), 2)} percentage points. "
            "The result is negative. "
            "The gap is computed in this library. It is not a published series and not a recommendation.",
        ]
    )
    doc.h(2, "Sources and citations")
    doc.p(f"Retrieved {portfolio.retrieved_on}. Survey year used: {portfolio.survey_year}.")
    doc.table(
        ["Series", "ID", "Official name in the snapshot"],
        [
            ["Account ownership, total", "FX.OWN.TOTL.ZS", portfolio.wb_names["FX.OWN.TOTL.ZS"]],
            ["Account ownership, female", "FX.OWN.TOTL.FE.ZS", portfolio.wb_names["FX.OWN.TOTL.FE.ZS"]],
            ["Account ownership, male", "FX.OWN.TOTL.MA.ZS", portfolio.wb_names["FX.OWN.TOTL.MA.ZS"]],
        ],
    )
    doc.table(
        ["Country", "ISO3", "Total", "Female", "Male", "Female minus male"],
        [
            [
                item["name"],
                item["iso3"],
                quantize(Decimal(item["ownership"]), 1),
                quantize(Decimal(item["female"]), 2),
                quantize(Decimal(item["male"]), 2),
                quantize(Decimal(item["gap_female_minus_male"]), 2),
            ]
            for item in sorted(rows, key=lambda item: item["name"])
        ],
    )
    doc.add("```text")
    for indicator in ("FX.OWN.TOTL.ZS", "FX.OWN.TOTL.FE.ZS", "FX.OWN.TOTL.MA.ZS"):
        doc.add(wb_url(indicator, 1))
    doc.add("https://www.worldbank.org/en/publication/globalfindex")
    doc.add("```")
    doc.add("")
    doc.h(2, "Related")
    doc.items(
        [
            "[Teaching portfolio](index.md)",
            "[Woman-led household pathway](../../pathways/woman-led-household.md)",
            "[Emergency savings](../emergency-savings.md)",
            "[Glossary: deposit insurance](../../glossary.md#deposit-insurance)",
        ]
    )
    return doc.text()


def render_notebook(portfolio: Portfolio) -> str:
    values = portfolio.values["modules"]["rates-and-inflation"]["fedfunds_latest"]
    code = (
        "import csv\n"
        "from pathlib import Path\n"
        "\n"
        'path = Path("data/teaching/snapshots/fred/FEDFUNDS.csv")\n'
        "rows = []\n"
        'with path.open(encoding="utf-8") as handle:\n'
        "    for row in csv.DictReader(handle):\n"
        '        raw = (row.get("FEDFUNDS") or "").strip()\n'
        '        observed = (row.get("observation_date") or "").strip()\n'
        f'        if observed and raw and raw != "." and observed <= "{portfolio.retrieved_on}":\n'
        "            rows.append((observed, raw))\n"
        "print(rows[-1])\n"
    )
    output = f"('{values['date']}', '{values['raw']}')\n"
    intro = (
        "# Teaching portfolio notebook\n\n"
        "Educational only. This is not investment advice and not a recommendation "
        "to buy, sell, or hold any product.\n\n"
        "The cell below reads the checked-in FRED snapshot for `FEDFUNDS` and prints "
        f"the latest observation on or before {portfolio.retrieved_on}. "
        "The six modules live under `docs/guides/teaching/`.\n"
    )
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": intro.splitlines(keepends=True)},
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "source": code.splitlines(keepends=True),
                "outputs": [{"output_type": "stream", "name": "stdout", "text": output.splitlines(keepends=True)}],
            },
        ],
    }
    return json.dumps(notebook, indent=2) + "\n"


def text_outputs(portfolio: Portfolio) -> dict[Path, str]:
    pages = render_pages(portfolio)
    outputs = {DOCS / name: text for name, text in pages.items()}
    for fig in portfolio.figures:
        outputs[FIGURES / f"{fig.slug}.svg"] = charts.render_svg(fig)
    outputs[VALUES_PATH] = json.dumps(portfolio.values, indent=2) + "\n"
    outputs[NOTEBOOK_PATH] = render_notebook(portfolio)
    return outputs


def write_pngs(portfolio: Portfolio) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for fig in portfolio.figures:
        charts.render_png(fig, FIGURES / f"{fig.slug}.png")


def write_outputs(portfolio: Portfolio) -> None:
    for path, text in text_outputs(portfolio).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    write_pngs(portfolio)


def check_outputs(portfolio: Portfolio) -> list[str]:
    errors = []
    for path, text in text_outputs(portfolio).items():
        if not path.exists():
            errors.append(f"missing {path.relative_to(REPO_ROOT)}")
            continue
        current = path.read_text(encoding="utf-8")
        if current != text:
            errors.append(f"differs {path.relative_to(REPO_ROOT)}")
    for fig in portfolio.figures:
        png = FIGURES / f"{fig.slug}.png"
        buffer = io.BytesIO()
        charts.render_png(fig, buffer)
        rendered = buffer.getvalue()
        if not png.exists() or png.read_bytes() != rendered:
            errors.append(f"differs png {png.relative_to(REPO_ROOT)}")
    return errors


def _manifest_entry(relative: str, url: str, body: bytes, **extra) -> dict:
    entry = {
        "path": relative,
        "url": url,
        "sha256": sha256_bytes(body),
        "bytes": len(body),
        "kind": extra.pop("kind", "raw"),
    }
    entry.update(extra)
    return entry


def build_edgar_excerpts(companyfacts: bytes, submissions: bytes, retrieved_on: str) -> tuple[dict, dict]:
    facts_payload = json.loads(companyfacts)
    concepts = {}
    gaap = facts_payload["facts"]["us-gaap"]
    for concept in EDGAR_CONCEPTS:
        units = gaap[concept]["units"].get("USD") or []
        concepts[concept] = [fact for fact in units if fact.get("form") == "10-K" and fact.get("fp") == "FY"]
    facts_excerpt = {
        "retrieved_on": retrieved_on,
        "source_url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{EDGAR_CIK}.json",
        "full_payload_sha256": sha256_bytes(companyfacts),
        "full_payload_bytes": len(companyfacts),
        "entityName": facts_payload.get("entityName"),
        "cik": facts_payload.get("cik"),
        "cik_padded": EDGAR_CIK,
        "filter": (
            "Each object under concepts is a fact copied from facts.us-gaap.<concept>.units.USD "
            "where form is 10-K and fp is FY. Wrapper fields are added by this library."
        ),
        "concepts": concepts,
    }
    submissions_payload = json.loads(submissions)
    recent = submissions_payload["filings"]["recent"]
    fields = (
        "form",
        "filingDate",
        "accessionNumber",
        "primaryDocument",
        "primaryDocDescription",
        "reportDate",
        "acceptanceDateTime",
    )
    columns = {field: recent.get(field) or [] for field in fields}
    picked: dict[str, dict] = {}
    for index, form in enumerate(columns["form"]):
        filed = columns["filingDate"][index] if index < len(columns["filingDate"]) else ""
        if form not in {"10-K", "10-Q", "8-K"} or filed > retrieved_on:
            continue
        row = {field: (columns[field][index] if index < len(columns[field]) else None) for field in fields}
        previous = picked.get(form)
        if previous is None or (filed, row["accessionNumber"]) > (previous["filingDate"], previous["accessionNumber"]):
            picked[form] = row
    filings_excerpt = {
        "retrieved_on": retrieved_on,
        "source_url": f"https://data.sec.gov/submissions/CIK{EDGAR_CIK}.json",
        "full_payload_sha256": sha256_bytes(submissions),
        "full_payload_bytes": len(submissions),
        "entityName": submissions_payload.get("name"),
        "cik": submissions_payload.get("cik"),
        "sic": submissions_payload.get("sic"),
        "sicDescription": submissions_payload.get("sicDescription"),
        "filter": (
            "Latest 10-K, 10-Q, and 8-K with filingDate on or before the retrieval date. "
            "Each filing object copies the parallel filings.recent fields for that row."
        ),
        "filings": [picked[form] for form in ("10-K", "10-Q", "8-K") if form in picked],
    }
    return facts_excerpt, filings_excerpt


def fetch_snapshots() -> None:
    retrieved_on = datetime.now(UTC).date().isoformat()
    stage = SNAPSHOTS.parent / "_snapshots_stage"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    entries = []
    try:
        fred_dir = stage / "fred"
        fred_dir.mkdir()
        for series_id in FRED_SERIES:
            url = fred_url(series_id)
            body = trim_fred_csv(fetch_bytes(url).decode("utf-8")).encode("utf-8")
            relative = f"fred/{series_id}.csv"
            (stage / relative).write_bytes(body)
            entries.append(
                _manifest_entry(
                    relative,
                    url,
                    body,
                    series_id=series_id,
                    trimmed_to=f"observations on or after {FRED_KEEP_FROM}",
                )
            )
        wb_dir = stage / "worldbank"
        wb_dir.mkdir()
        for indicator in WB_INDICATORS:
            page = 1
            pages = 1
            raw_pages: list[str] = []
            while page <= pages:
                url = wb_url(indicator, page)
                body = fetch_bytes(url, timeout=90)
                payload = json.loads(body)
                pages = int(payload[0]["pages"])
                raw_pages.append(body.decode("utf-8"))
                page += 1
            relative = f"worldbank/{indicator}.json"
            if len(raw_pages) == 1:
                text = raw_pages[0]
                if not text.endswith("\n"):
                    text += "\n"
            else:
                text = json.dumps({"raw_pages": raw_pages, "note": "Unmodified page bodies."}, indent=2) + "\n"
            data = trim_world_bank(text).encode("utf-8")
            (stage / relative).write_bytes(data)
            entries.append(
                _manifest_entry(
                    relative,
                    wb_url(indicator, 1),
                    data,
                    indicator=indicator,
                    trimmed_to=f"non-null rows from {WB_KEEP_FROM_YEAR} on",
                )
            )
        imf_dir = stage / "imf"
        imf_dir.mkdir()
        for name, url in (
            ("PCPIPCH.json", "https://www.imf.org/external/datamapper/api/v1/PCPIPCH"),
            ("indicators.json", "https://www.imf.org/external/datamapper/api/v1/indicators"),
        ):
            body = fetch_bytes(url, timeout=90)
            text = body.decode("utf-8")
            if name == "PCPIPCH.json":
                text = trim_imf_inflation(text)
            elif not text.endswith("\n"):
                text += "\n"
            data = text.encode("utf-8")
            relative = f"imf/{name}"
            (stage / relative).write_bytes(data)
            extra = (
                {"trimmed_to": f"library countries, years from {IMF_KEEP_FROM_YEAR}"} if name == "PCPIPCH.json" else {}
            )
            entries.append(_manifest_entry(relative, url, data, **extra))
        companyfacts = fetch_bytes(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{EDGAR_CIK}.json",
            timeout=120,
        )
        submissions = fetch_bytes(f"https://data.sec.gov/submissions/CIK{EDGAR_CIK}.json", timeout=120)
        facts_excerpt, filings_excerpt = build_edgar_excerpts(companyfacts, submissions, retrieved_on)
        edgar_dir = stage / "edgar"
        edgar_dir.mkdir()
        for name, payload, url, full in (
            (
                "jpmorgan-10k-facts.json",
                facts_excerpt,
                facts_excerpt["source_url"],
                companyfacts,
            ),
            (
                "jpmorgan-filings.json",
                filings_excerpt,
                filings_excerpt["source_url"],
                submissions,
            ),
        ):
            text = json.dumps(payload, indent=2) + "\n"
            data = text.encode("utf-8")
            relative = f"edgar/{name}"
            (stage / relative).write_bytes(data)
            entries.append(
                _manifest_entry(
                    relative,
                    url,
                    data,
                    kind="excerpt",
                    full_payload_sha256=sha256_bytes(full),
                    full_payload_bytes=len(full),
                )
            )
        manifest = {
            "retrieved_on": retrieved_on,
            "user_agent": UA,
            "note": (
                "FRED, World Bank, and IMF files are trimmed to the years these modules use. "
                "Each file's sha256 is of that trimmed text. url is the original request. "
                "retrieved_on is the retrieval date. EDGAR files are excerpts: each fact and filing "
                "field is copied unchanged, and full_payload_sha256 is the complete response, which is not stored."
            ),
            "files": sorted(entries, key=lambda item: item["path"]),
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if SNAPSHOTS.exists():
            shutil.rmtree(SNAPSHOTS)
        stage.rename(SNAPSHOTS)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the teaching portfolio from official snapshots.")
    parser.add_argument("--fetch", action="store_true", help="Download snapshots, then regenerate pages.")
    parser.add_argument("--check", action="store_true", help="Compare generated files with the repository. Offline.")
    args = parser.parse_args(argv)
    if args.fetch and args.check:
        print("Use either --fetch or --check.", file=sys.stderr)
        return 2
    if args.fetch:
        fetch_snapshots()
    portfolio = load_portfolio()
    if args.check:
        errors = check_outputs(portfolio)
        if errors:
            print("Teaching portfolio is out of date:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("OK: teaching portfolio matches the snapshots.")
        return 0
    write_outputs(portfolio)
    print(f"Wrote the teaching portfolio from snapshots retrieved {portfolio.retrieved_on}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
