#!/usr/bin/env python3
"""Refresh docs/about/where-to-check.md 'as of' date when official URLs fetch OK.

Never invent figures. Only updates the as-of date / front-matter when at least
one URL returns HTTP 200. Writes a markdown report of successes and failures
for the weekly PR or issue body.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAGE = ROOT / "docs" / "about" / "where-to-check.md"
USER_AGENT = "FinancialLibraryWeeklyBot/0.7 (+https://github.com/ananddw24/safe_investment_researcher)"
URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")


def extract_urls(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for match in URL_RE.finditer(text):
        url = match.group(0).rstrip(".,;")
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def fetch_status(url: str, timeout: float = 15.0) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), "ok"
    except urllib.error.HTTPError as exc:
        return int(exc.code), str(exc.reason)
    except Exception as exc:  # noqa: BLE001 — report any fetch failure
        return None, f"{type(exc).__name__}: {exc}"


def update_as_of(text: str, today: str) -> str:
    text = re.sub(
        r'(as_of:\s*")[^"]+(")',
        rf"\g<1>{today}\2",
        text,
        count=1,
    )
    text = re.sub(
        r"(last_reviewed:\s*\")[^\"]+(\")",
        rf"\g<1>{today}\2",
        text,
        count=1,
    )
    text = re.sub(
        r"(\*\*As of:\*\*\s*)[0-9]{4}-[0-9]{2}-[0-9]{2}",
        rf"\g<1>{today}",
        text,
        count=1,
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", type=Path, default=DEFAULT_PAGE)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--today", default=date.today().isoformat())
    args = parser.parse_args()

    page: Path = args.page
    if not page.is_file():
        print(f"missing page: {page}", file=sys.stderr)
        return 2

    original = page.read_text(encoding="utf-8")
    urls = extract_urls(original)
    ok: list[tuple[str, int]] = []
    failed: list[tuple[str, str]] = []

    for url in urls:
        status, detail = fetch_status(url)
        if status == 200:
            ok.append((url, status))
        else:
            label = f"HTTP {status}" if status is not None else detail
            failed.append((url, label))

    refreshed = bool(ok)
    if refreshed:
        page.write_text(update_as_of(original, args.today), encoding="utf-8")

    lines = [
        f"# Weekly where-to-check report ({args.today})",
        "",
        f"- URLs checked: **{len(urls)}**",
        f"- Fetch succeeded (HTTP 200): **{len(ok)}**",
        f"- Needs human re-check: **{len(failed)}**",
        f"- As-of date refreshed: **{'yes' if refreshed else 'no'}**",
        "",
        "This job never invents inflation or deposit figures. It only probes",
        "official publisher URLs already listed on the page.",
        "",
    ]
    if failed:
        lines.append("## Re-check these URLs")
        lines.append("")
        for url, label in failed:
            lines.append(f"- `{label}` — {url}")
        lines.append("")
    if ok:
        lines.append("## Succeeded")
        lines.append("")
        for url, status in ok:
            lines.append(f"- HTTP {status} — {url}")
        lines.append("")

    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ok={len(ok)} failed={len(failed)} refreshed={refreshed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
