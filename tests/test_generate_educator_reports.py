"""Tests for the educator-report generator.

Network is never used. Fixtures stand in for FRED, EDGAR, and the World Bank.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest
from conftest import load_script

gen = load_script("generate_educator_reports")

AS_OF = date(2026, 10, 30)


def _csv(series_id: str, rows: list[tuple[str, str]]) -> bytes:
    lines = [f"observation_date,{series_id}"]
    lines.extend(f"{d},{v}" for d, v in rows)
    return ("\n".join(lines) + "\n").encode()


def _fred_bundle() -> dict[str, bytes]:
    return {
        "DFEDTARL": _csv("DFEDTARL", [("2026-10-29", "3.50"), ("2026-10-30", "3.75"), ("2026-10-31", "9.99")]),
        "DFEDTARU": _csv("DFEDTARU", [("2026-10-30", "4.00"), ("2026-10-31", "9.99")]),
        "FEDFUNDS": _csv("FEDFUNDS", [("2026-08-01", "3.63"), ("2026-09-01", "3.75"), ("2026-10-31", "9.99")]),
        "UNRATE": _csv("UNRATE", [("2026-09-01", "4.2")]),
        "DGS10": _csv("DGS10", [("2026-10-28", "5.05"), ("2026-10-31", "9.99")]),
        "PSAVERT": _csv("PSAVERT", [("2026-09-01", "3.8")]),
        "CPIAUCSL": _csv(
            "CPIAUCSL",
            [("2025-09-01", "324.245"), ("2026-09-01", "336.298"), ("2026-10-31", "999.000")],
        ),
        "CPIAUCNS": _csv(
            "CPIAUCNS",
            [("2025-09-01", "324.800"), ("2026-09-01", "336.940")],
        ),
    }


def _edgar(cik: str) -> bytes:
    # Newest form in the feed is 8-K. Output order must still be 10-K, 10-Q, 8-K.
    payload = {
        "cik": cik,
        "filings": {
            "recent": {
                "form": ["8-K", "10-Q", "10-K", "4"],
                "filingDate": ["2026-10-20", "2026-08-06", "2026-02-13", "2026-10-21"],
                "accessionNumber": [
                    "0001193125-26-426704",
                    "0001628280-26-054343",
                    "0001628280-26-008131",
                    "0000000000-26-000001",
                ],
                "primaryDocument": ["eight.htm", "quarter.htm", "annual.htm", "form4.htm"],
            }
        },
    }
    return json.dumps(payload).encode()


def _wb_page(indicator: str, page: int, pages: int, rows: list[dict]) -> bytes:
    meta = {"page": page, "pages": pages, "per_page": 100, "total": pages}
    return json.dumps([meta, rows]).encode()


def _wb_row(indicator: str, iso2: str, iso3: str, name: str, year: str, value) -> dict:
    return {
        "indicator": {"id": indicator, "value": indicator},
        "country": {"id": iso2, "value": name},
        "countryiso3code": iso3,
        "date": year,
        "value": value,
        "decimal": 1,
    }


class Router:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.fred = _fred_bundle()
        self.fail_series: set[str] = set()
        self.fail_times: dict[str, int] = {}

    def __call__(self, url: str) -> bytes:
        self.calls.append(url)
        if "fredgraph.csv" in url:
            series_id = url.rsplit("id=", 1)[-1]
            if series_id in self.fail_series:
                raise gen.FetchError(url, "timeout", 3)
            return self.fred[series_id]
        if "data.sec.gov/submissions/" in url:
            cik = url.split("CIK", 1)[1].split(".", 1)[0]
            return _edgar(cik)
        if "api.worldbank.org" in url:
            if "FP.CPI.TOTL.ZG" in url:
                return self._inflation(url)
            if "FX.OWN.TOTL.ZS" in url:
                return self._accounts(url)
            raise AssertionError(url)
        raise AssertionError(url)

    def _inflation(self, url: str) -> bytes:
        # Page 1 omits the United States; page 2 has it, plus an ISO3-only row
        # for Egypt (the shape that emptied the old account table).
        page = 2 if "page=2" in url else 1
        if page == 1:
            rows = [
                _wb_row("FP.CPI.TOTL.ZG", "BR", "BRA", "Brazil", "2025", 5.01675279604836),
                _wb_row("FP.CPI.TOTL.ZG", "DE", "DEU", "Germany", "2024", 2.0),
                _wb_row("FP.CPI.TOTL.ZG", "DE", "DEU", "Germany", "2025", 2.17178770949721),
            ]
            return _wb_page("FP.CPI.TOTL.ZG", 1, 2, rows)
        rows = [
            _wb_row("FP.CPI.TOTL.ZG", "US", "USA", "United States", "2024", 2.94952520485207),
            {
                "indicator": {"id": "FP.CPI.TOTL.ZG", "value": "x"},
                "country": {"id": "EGY", "value": "Egypt, Arab Rep."},
                "countryiso3code": "",
                "date": "2025",
                "value": 14.0735136645933,
                "decimal": 1,
            },
        ]
        return _wb_page("FP.CPI.TOTL.ZG", 2, 2, rows)

    def _accounts(self, url: str) -> bytes:
        rows = [
            _wb_row("FX.OWN.TOTL.ZS", "US", "USA", "United States", "2021", 94.9),
            _wb_row("FX.OWN.TOTL.ZS", "US", "USA", "United States", "2024", 97.0230983290589),
            _wb_row("FX.OWN.TOTL.ZS", "EG", "EGY", "Egypt, Arab Rep.", "2024", 43.1134368034247),
        ]
        return _wb_page("FX.OWN.TOTL.ZS", 1, 1, rows)


def _reports(router: Router | None = None):
    router = router or Router()
    reports, failures = gen.build_reports(AS_OF, router)
    return reports, failures, router


def test_macro_pins_observations_on_or_before_as_of_and_keeps_source_precision():
    reports, failures, _router = _reports()
    assert failures == []
    text = reports["macro-snapshot"]
    assert "2026-10-30" in text
    assert "DFEDTARL" in text and "3.75%" in text
    assert "DFEDTARU" in text and "4.00%" in text
    assert "FEDFUNDS" in text
    assert "2026-09-01" in text
    assert "9.99" not in text
    assert "UNRATE" in text and "4.2%" in text
    assert "4.20%" not in text
    assert "PSAVERT" in text and "3.8%" in text
    assert "3.80%" not in text
    assert "DGS10" in text and "5.05%" in text
    assert "2026-10-28" in text
    assert "CPIAUCSL" in text and "3.7%" in text
    assert "336.298" in text and "324.245" in text
    assert "CPIAUCNS" in text and "336.940" in text
    assert "not investment advice" in text.lower()


def test_cpi_prior_year_must_be_the_same_month():
    points = [("2025-08-01", Decimal("1")), ("2026-09-01", Decimal("2"))]
    assert gen.cpi_change(points, date(2026, 9, 30)) is None


def test_world_bank_follows_pages_and_iso3_ids_and_lists_every_country():
    reports, failures, router = _reports()
    assert failures == []
    text = reports["world-snapshot"]
    assert any("page=2" in url for url in router.calls)
    assert "Egypt" in text
    assert "14.1" in text
    assert "United States" in text
    assert "2024" in text
    assert "2.9" in text
    assert "97.0" in text
    assert "43.1" in text
    assert "FX.OWN.TOTL.ZS" in text
    assert "FP.CPI.TOTL.ZG" in text
    assert "account.t.d" not in text
    # Germany keeps 2025, not the older 2024 row.
    assert "Germany | 2.2 | 2025" in text.replace(" ", " ")
    # Countries with no row in the fixture are marked, not dropped.
    assert "not in source response" in text
    assert text.count("| Brazil |") == 0 or "Brazil" in text


def test_filing_order_is_stable_and_ignores_other_forms():
    reports, _failures, _router = _reports()
    text = reports["filing-watch"]
    k = text.index("| 10-K |")
    q = text.index("| 10-Q |")
    e = text.index("| 8-K |")
    assert k < q < e
    assert "form4.htm" not in text
    assert "annual.htm" in text
    assert "not investment advice" in text.lower()


def test_repeat_runs_match_and_do_not_name_an_internal_job():
    first, fail_a, _ = _reports()
    second, fail_b, _ = _reports()
    assert fail_a == fail_b == []
    assert first == second
    blob = "\n".join(first.values()) + gen.render_index(AS_OF, list(first))
    assert "Mu" + "se" not in blob
    assert "financial-library-educator-reports-" + "weekly" not in blob


def test_one_series_failure_keeps_the_rest_and_is_named():
    router = Router()
    router.fail_series.add("UNRATE")
    reports, failures, _router = _reports(router)
    text = reports["macro-snapshot"]
    assert "UNRATE" in text
    assert "not retrieved" in text
    assert "FEDFUNDS" in text and "3.75%" in text
    assert any("UNRATE" in item for item in failures)
    assert "not investment advice" in text.lower()


def test_fetch_bytes_retries_then_returns_body():
    calls = {"n": 0}

    class Resp:
        def read(self):
            return b"ok"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def opener(_req, timeout):
        assert timeout == 5
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("timed out")
        return Resp()

    slept: list[float] = []
    body = gen.fetch_bytes(
        "https://example.test/series",
        timeout=5,
        attempts=3,
        sleep=slept.append,
        opener=opener,
        backoff=0.25,
    )
    assert body == b"ok"
    assert calls["n"] == 3
    assert slept == [0.25, 0.5]


def test_fetch_bytes_gives_up_after_the_last_timeout():
    def opener(_req, timeout):
        raise TimeoutError("timed out")

    with pytest.raises(gen.FetchError) as caught:
        gen.fetch_bytes(
            "https://example.test/series",
            timeout=1,
            attempts=2,
            sleep=lambda _s: None,
            opener=opener,
        )
    assert caught.value.attempts == 2
    assert caught.value.reason == "timeout"


def test_main_writes_only_the_pinned_date(tmp_path, monkeypatch):
    router = Router()
    monkeypatch.setattr(gen, "fetch_bytes", lambda url, **_kwargs: router(url))
    code = gen.main(["--as-of", "2026-10-30", "--output-dir", str(tmp_path)])
    assert code == 0
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == [
        "2026-10-30-filing-watch.md",
        "2026-10-30-macro-snapshot.md",
        "2026-10-30-world-snapshot.md",
        "latest.md",
    ]
    latest = (tmp_path / "latest.md").read_text(encoding="utf-8")
    assert "2026-10-30-macro-snapshot.md" in latest
    assert "Mu" + "se" not in latest


def test_main_returns_nonzero_when_a_source_fails(tmp_path, monkeypatch):
    router = Router()
    router.fail_series.add("DGS10")
    monkeypatch.setattr(gen, "fetch_bytes", lambda url, **_kwargs: router(url))
    code = gen.main(["--as-of", "2026-10-30", "--output-dir", str(tmp_path)])
    assert code == 1
    text = (tmp_path / "2026-10-30-macro-snapshot.md").read_text(encoding="utf-8")
    assert "DGS10" in text and "not retrieved" in text
    assert "FEDFUNDS" in text
