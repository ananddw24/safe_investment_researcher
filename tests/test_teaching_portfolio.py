"""The teaching portfolio must trace to checked-in official snapshots.

Network is never used. Figure values are recomputed from the snapshot
files, not trusted from the generator's own helpers.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from conftest import load_script

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "guides" / "teaching"
SNAPSHOTS = ROOT / "data" / "teaching" / "snapshots"
gen = load_script("generate_teaching_portfolio")

MODULES = (
    "rates-and-inflation.md",
    "yield-curve.md",
    "labor-market.md",
    "reading-a-10k.md",
    "cross-country-inflation.md",
    "household-finance.md",
)
REQUIRED = (
    '!!! warning "Educational only"',
    "## Learning objectives",
    "## Explainer",
    "## Discussion questions",
    "## Exercise",
    "## Answer key",
    "<summary>Show the answer key</summary>",
    "## Sources and citations",
)
BANNED = (
    "you should buy",
    "you should sell",
    "you should invest",
    "we recommend",
    "guaranteed return",
    "best investment",
)


def _manifest() -> dict:
    return json.loads((SNAPSHOTS / "manifest.json").read_text(encoding="utf-8"))


def _fred(series_id: str) -> dict[str, str]:
    points: dict[str, str] = {}
    with (SNAPSHOTS / "fred" / f"{series_id}.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            raw = (row.get(series_id) or "").strip()
            observed = (row.get("observation_date") or "").strip()
            if observed and raw and raw != ".":
                points[observed] = raw
    return points


def _quantize(value: Decimal, places: int) -> str:
    quantum = Decimal(1).scaleb(-places)
    return f"{value.quantize(quantum, rounding=ROUND_HALF_UP):.{places}f}"


def test_modules_have_objectives_sources_alt_text_and_answer_key() -> None:
    retrieved = _manifest()["retrieved_on"]
    index = (DOCS / "index.md").read_text(encoding="utf-8")
    assert '!!! warning "Educational only"' in index
    assert retrieved in index
    for name in MODULES:
        text = (DOCS / name).read_text(encoding="utf-8")
        assert name.replace(".md", "") in index or name in index
        for part in REQUIRED:
            assert part in text, f"{name} missing {part}"
        assert f"Retrieved {retrieved}" in text
        images = re.findall(r"!\[([^\]]+)\]\(([^)]+\.svg)\)", text)
        assert images, name
        for alt, src in images:
            assert alt.strip()
            assert (DOCS / src).is_file()
            png = DOCS / src.replace(".svg", ".png")
            assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            svg = (DOCS / src).read_text(encoding="utf-8")
            assert 'role="img"' in svg
            assert "<title" in svg
            assert "<desc" in svg
        folded = text.casefold()
        for phrase in BANNED:
            assert phrase not in folded


def test_portfolio_regenerates_from_snapshots() -> None:
    portfolio = gen.load_portfolio()
    assert gen.check_outputs(portfolio) == []


def test_snapshot_manifest_hashes_match_files() -> None:
    manifest = _manifest()
    assert manifest["retrieved_on"] == "2026-10-30"
    for entry in manifest["files"]:
        body = (SNAPSHOTS / entry["path"]).read_bytes()
        assert hashlib.sha256(body).hexdigest() == entry["sha256"]
        assert entry["bytes"] == len(body)
        assert entry["url"].startswith("https://")
        if entry["kind"] == "excerpt":
            assert len(entry["full_payload_sha256"]) == 64
            assert entry["full_payload_bytes"] > entry["bytes"]


def test_rates_trace_to_fred_snapshot() -> None:
    as_of = _manifest()["retrieved_on"]
    funds = {date: raw for date, raw in _fred("FEDFUNDS").items() if date <= as_of}
    latest = max(funds)
    cpi = {date: Decimal(raw) for date, raw in _fred("CPIAUCSL").items() if date <= as_of}
    prior = f"{int(latest[:4]) - 1}{latest[4:]}"
    change = (cpi[latest] / cpi[prior] - Decimal(1)) * Decimal(100)
    rounded = _quantize(change, 1)
    page = (DOCS / "rates-and-inflation.md").read_text(encoding="utf-8")
    svg = (DOCS / "figures" / "rates-policy-and-inflation.svg").read_text(encoding="utf-8")
    assert funds[latest] in page
    assert f"{cpi[latest]}" in page
    assert f"{cpi[prior]}" in page
    assert rounded in page
    assert rounded in svg
    assert "CPIAUCSL" in page and "FEDFUNDS" in page
    # The rounded gap is funds minus the unrounded change, not minus the rounded percent.
    gap = _quantize(Decimal(funds[latest]) - change, 1)
    assert gap in page


def test_yield_curve_spread_traces_to_fred_snapshot() -> None:
    as_of = _manifest()["retrieved_on"]
    series = {
        name: {date: Decimal(raw) for date, raw in _fred(name).items() if date <= as_of}
        for name, _label in gen.CURVE
    }
    common = set.intersection(*(set(points) for points in series.values()))
    curve_date = max(common)
    spread = _quantize(series["DGS10"][curve_date] - series["DGS2"][curve_date], 2)
    page = (DOCS / "yield-curve.md").read_text(encoding="utf-8")
    svg = (DOCS / "figures" / "yield-curve-snapshot.svg").read_text(encoding="utf-8")
    assert curve_date in page
    assert spread in page
    for name, _label in gen.CURVE:
        raw = _fred(name)[curve_date]
        assert raw in page
        assert raw in svg
    assert "DGS10" in page and "DGS2" in page


def test_labor_payroll_change_traces_to_fred_snapshot() -> None:
    as_of = _manifest()["retrieved_on"]
    unrate = {date: raw for date, raw in _fred("UNRATE").items() if date <= as_of}
    payrolls = {date: Decimal(raw) for date, raw in _fred("PAYEMS").items() if date <= as_of}
    latest = max(unrate)
    prior = f"{int(latest[:4]) - 1}{latest[4:]}"
    change = payrolls[latest] - payrolls[prior]
    page = (DOCS / "labor-market.md").read_text(encoding="utf-8")
    assert unrate[latest] in page
    assert f"{payrolls[latest]}" in page
    assert f"{change}" in page
    assert "UNRATE" in page and "PAYEMS" in page and "CIVPART" in page


def _select_fact(facts: list[dict], year: int) -> dict:
    chosen = []
    for fact in facts:
        if fact.get("form") != "10-K" or fact.get("fp") != "FY":
            continue
        end = str(fact.get("end") or "")
        if int(fact["fy"]) != int(end[:4]) or int(end[:4]) != year:
            continue
        if fact.get("start") and int(str(fact["start"])[:4]) != year:
            continue
        chosen.append(fact)
    assert len(chosen) == 1
    return chosen[0]


def test_ten_k_facts_trace_to_edgar_excerpt() -> None:
    excerpt = json.loads((SNAPSHOTS / "edgar" / "jpmorgan-10k-facts.json").read_text(encoding="utf-8"))
    assets = _select_fact(excerpt["concepts"]["Assets"], 2025)
    deposits = _select_fact(excerpt["concepts"]["Deposits"], 2025)
    page = (DOCS / "reading-a-10k.md").read_text(encoding="utf-8")
    assert str(assets["val"]) in page
    assert str(deposits["val"]) in page
    assert assets["accn"] in page
    assert assets["filed"] in page
    assert "0000019617" in page
    ratio = _quantize(Decimal(deposits["val"]) / Decimal(assets["val"]) * Decimal(100), 1)
    assert ratio in page
    assert "not an assessment of the company" in page.casefold() or "not an assessment" in page.casefold()


def test_world_bank_and_imf_trace_to_snapshots() -> None:
    payload = json.loads(
        (SNAPSHOTS / "worldbank" / "FP.CPI.TOTL.ZG.json").read_text(encoding="utf-8"),
        parse_float=Decimal,
        parse_int=Decimal,
    )
    nigeria = [
        row for row in payload[1]
        if row.get("countryiso3code") == "NGA" and row.get("date") == "2025" and row.get("value") is not None
    ]
    assert len(nigeria) == 1
    exact = format(nigeria[0]["value"], "f")
    page = (DOCS / "cross-country-inflation.md").read_text(encoding="utf-8")
    assert exact in page
    assert "United States" in page and "omitted" in page.casefold() or "Missing" in page
    indicators = json.loads((SNAPSHOTS / "imf" / "indicators.json").read_text(encoding="utf-8"))
    meta = indicators["indicators"]["PCPIPCH"]
    assert meta["source"] in page
    assert meta["label"] in page
    assert "PCPIPCH" in page
    assert "2026" in page and "not as measured inflation" in page


def test_findex_gap_traces_to_world_bank_snapshot() -> None:
    def load(indicator: str) -> dict[str, Decimal]:
        payload = json.loads(
            (SNAPSHOTS / "worldbank" / f"{indicator}.json").read_text(encoding="utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
        )
        values = {}
        for row in payload[1]:
            if row.get("date") == "2024" and row.get("value") is not None:
                values[row["countryiso3code"]] = row["value"]
        return values

    total = load("FX.OWN.TOTL.ZS")
    female = load("FX.OWN.TOTL.FE.ZS")
    male = load("FX.OWN.TOTL.MA.ZS")
    lowest = min(total, key=lambda code: total[code])
    gap = {code: female[code] - male[code] for code in female if code in male}
    widest = min(gap, key=lambda code: gap[code])
    names = dict(gen.COUNTRIES)
    page = (DOCS / "household-finance.md").read_text(encoding="utf-8")
    assert names[lowest] in page
    assert format(total[lowest], "f") in page
    assert names[widest] in page
    assert _quantize(gap[widest], 1) in page
    assert "FX.OWN.TOTL.ZS" in page
    assert "not a separate published series" in page.casefold()


def test_notebook_prints_the_snapshot_funds_rate() -> None:
    as_of = _manifest()["retrieved_on"]
    funds = {date: raw for date, raw in _fred("FEDFUNDS").items() if date <= as_of}
    latest = max(funds)
    notebook = (ROOT / "examples" / "educators" / "notebooks" / "teaching-portfolio.ipynb").read_text(encoding="utf-8")
    assert f"('{latest}', '{funds[latest]}')" in notebook
    assert "not investment advice" in notebook.casefold()
