#!/usr/bin/env python3
"""Shared, accessible chart style for the teaching portfolio.

Figures are drawn as deterministic SVG (the page image) and, when
matplotlib is installed, as a matching PNG. Colors are the Okabe–Ito
palette. Lines also use dash patterns, and bars carry numeric labels,
so a reading does not depend on color alone.

Educational only. These charts describe public series. They are not
forecasts and not investment advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal
from xml.sax.saxutils import escape

# Okabe–Ito, plus neutral interface colors. Do not introduce one-off hexes.
PALETTE = {
    "ink": "#1A1A1A",
    "muted": "#333333",
    "axis": "#1A1A1A",
    "grid": "#E6E6E6",
    "bg": "#FFFFFF",
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "yellow": "#F0E442",
    "sky": "#56B4E9",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
}

DASH = {
    "solid": "",
    "dashed": "7 4",
    "dotted": "1.5 3",
}

FOOTER = "FinancialLibrary teaching chart · educational only · not a forecast or a recommendation"


def _d(value: Decimal | str | int) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _nice_step(raw: Decimal) -> Decimal:
    if raw <= 0:
        return Decimal(1)
    exp = raw.adjusted()
    frac = raw.scaleb(-exp)
    if frac <= 1:
        nice = Decimal(1)
    elif frac <= 2:
        nice = Decimal(2)
    elif frac <= Decimal("2.5"):
        nice = Decimal("2.5")
    elif frac <= 5:
        nice = Decimal(5)
    else:
        nice = Decimal(10)
    return nice.scaleb(exp)


def _ticks(lo: Decimal, hi: Decimal, count: int = 5) -> list[Decimal]:
    span = hi - lo
    if span <= 0:
        return [lo]
    step = _nice_step(span / Decimal(count))
    start = (lo / step).to_integral_value(rounding=ROUND_FLOOR) * step
    if start < lo - step / Decimal(1000):
        start += step
    ticks: list[Decimal] = []
    value = start
    guard = 0
    while value <= hi + step / Decimal(1000) and guard < 24:
        if value >= lo - step / Decimal(1000):
            ticks.append(value)
        value += step
        guard += 1
    return ticks or [lo, hi]


def _tick_text(value: Decimal) -> str:
    exponent = value.normalize().as_tuple().exponent
    places = 0 if not isinstance(exponent, int) or exponent >= 0 else min(4, -exponent)
    return f"{value:.{places}f}"


def _limits(values: list[Decimal], include_zero: bool) -> tuple[Decimal, Decimal]:
    lo = min(values)
    hi = max(values)
    if include_zero:
        lo = min(lo, Decimal(0))
        hi = max(hi, Decimal(0))
    if lo == hi:
        lo -= Decimal(1)
        hi += Decimal(1)
    span = hi - lo
    pad = span * Decimal("0.08")
    if include_zero and lo == 0:
        return Decimal(0), hi + pad
    if include_zero and hi == 0:
        return lo - pad, Decimal(0)
    return lo - pad, hi + pad


def _fmt(value: Decimal, places: int) -> str:
    text = f"{value:.{places}f}"
    # A negative amount must not render as -0.0.
    if value < 0 and Decimal(text) == 0:
        text = f"{value:.{places + 1}f}"
    return text


def _segments(dates: tuple[str, ...] | list[str], values: tuple[str, ...] | list[str], max_gap_days: int):
    """Split a series where an observation is missing, so the line does not bridge the gap."""
    runs: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    previous: str | None = None
    for observed, raw in zip(dates, values, strict=True):
        if previous is not None and _ordinal(observed) - _ordinal(previous) > max_gap_days:
            if current:
                runs.append(current)
            current = []
        current.append((observed, raw))
        previous = observed
    if current:
        runs.append(current)
    return runs


def label_plan(fig: Figure) -> list[str]:
    """Text both the SVG and the PNG must show."""
    labels = [fig.title]
    if isinstance(fig, LineFigure):
        labels.append(fig.y_label)
        for series in fig.series:
            labels.append(series.label)
            if series.values:
                labels.append(series.values[-1])
    elif isinstance(fig, CurveFigure):
        labels.append(fig.y_label)
        labels.extend(fig.categories)
        labels.extend(_fmt(_d(value), fig.places) for value in fig.values)
    elif isinstance(fig, BarFigure):
        labels.append(fig.x_label)
        labels.extend(fig.labels)
        labels.extend(f"{_fmt(_d(value), fig.places)}{fig.suffix}" for value in fig.values)
    elif isinstance(fig, GroupedBarFigure):
        labels.append(fig.x_label)
        labels.extend(fig.series_labels)
        labels.extend(fig.labels)
        for series in fig.series_values:
            labels.extend(f"{_fmt(_d(value), fig.places)}{fig.suffix}" for value in series)
    elif isinstance(fig, StyleLegend):
        labels.extend(["Blue, solid", "Vermillion, dashed", "Green, dotted", "Orange", "Sky", "Purple"])
    return labels


@dataclass(frozen=True)
class LineSeries:
    label: str
    dates: tuple[str, ...]
    values: tuple[str, ...]
    color: str
    dash: str = "solid"


@dataclass(frozen=True)
class LineFigure:
    slug: str
    title: str
    subtitle: str
    alt: str
    y_label: str
    series: tuple[LineSeries, ...]
    include_zero: bool
    places: int
    # Break the line when the next observation is more than this many days later.
    max_gap_days: int = 40


@dataclass(frozen=True)
class CurveFigure:
    """A single line across named categories (the yield curve)."""

    slug: str
    title: str
    subtitle: str
    alt: str
    y_label: str
    categories: tuple[str, ...]
    values: tuple[str, ...]
    color: str
    places: int


@dataclass(frozen=True)
class BarFigure:
    slug: str
    title: str
    subtitle: str
    alt: str
    labels: tuple[str, ...]
    values: tuple[str, ...]
    places: int
    suffix: str
    x_label: str = "Percent"
    diverging: bool = False


@dataclass(frozen=True)
class GroupedBarFigure:
    slug: str
    title: str
    subtitle: str
    alt: str
    labels: tuple[str, ...]
    series_labels: tuple[str, ...]
    series_colors: tuple[str, ...]
    series_values: tuple[tuple[str, ...], ...]
    places: int
    suffix: str
    x_label: str = "Percent"


@dataclass(frozen=True)
class StyleLegend:
    slug: str
    title: str
    subtitle: str
    alt: str


Figure = LineFigure | CurveFigure | BarFigure | GroupedBarFigure | StyleLegend


def render_svg(fig: Figure) -> str:
    if isinstance(fig, LineFigure):
        return _svg_line(fig)
    if isinstance(fig, CurveFigure):
        return _svg_curve(fig)
    if isinstance(fig, BarFigure):
        return _svg_bars(fig)
    if isinstance(fig, GroupedBarFigure):
        return _svg_grouped(fig)
    if isinstance(fig, StyleLegend):
        return _svg_legend(fig)
    raise TypeError(type(fig))


def render_png(fig: Figure, path) -> None:
    """Write a PNG twin. Matplotlib is imported here so tests can skip it."""
    import matplotlib

    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt

    if isinstance(fig, StyleLegend):
        _png_legend(fig, path, plt)
        return
    if isinstance(fig, LineFigure):
        _png_line(fig, path, plt)
        return
    if isinstance(fig, CurveFigure):
        _png_curve(fig, path, plt)
        return
    if isinstance(fig, BarFigure):
        _png_bars(fig, path, plt)
        return
    if isinstance(fig, GroupedBarFigure):
        _png_grouped(fig, path, plt)
        return
    raise TypeError(type(fig))


def _svg_header(slug: str, title: str, alt: str, width: int, height: int) -> list[str]:
    title_id = f"title-{slug}"
    desc_id = f"desc-{slug}"
    return [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="{title_id} {desc_id}">'
        ),
        f'<title id="{title_id}">{escape(title)}</title>',
        f'<desc id="{desc_id}">{escape(alt)}</desc>',
        f'<rect width="{width}" height="{height}" fill="{PALETTE["bg"]}"/>',
    ]


def _svg_footer(lines: list[str], width: int, height: int) -> str:
    lines.append(
        f'<text x="24" y="{height - 16}" fill="{PALETTE["muted"]}" font-size="11" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(FOOTER)}</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _titles(lines: list[str], title: str, subtitle: str) -> None:
    lines.append(
        f'<text x="24" y="28" fill="{PALETTE["ink"]}" font-size="16" font-weight="700" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(title)}</text>'
    )
    lines.append(
        f'<text x="24" y="48" fill="{PALETTE["muted"]}" font-size="12" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(subtitle)}</text>'
    )


def _legend_row(lines: list[str], items: list[tuple[str, str, str]], x: int, y: int) -> None:
    cursor = x
    for label, color, dash in items:
        lines.append(
            f'<line x1="{cursor}" y1="{y}" x2="{cursor + 28}" y2="{y}" stroke="{color}" '
            f'stroke-width="2.5" stroke-dasharray="{dash}"/>'
        )
        lines.append(
            f'<text x="{cursor + 34}" y="{y + 4}" fill="{PALETTE["ink"]}" font-size="12" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(label)}</text>'
        )
        cursor += 34 + max(48, 7 * len(label))


def _svg_line(fig: LineFigure) -> str:
    width, height = 760, 460
    left, right, top, bottom = 64, 28, 92, 64
    plot_w = width - left - right
    plot_h = height - top - bottom
    lines = _svg_header(fig.slug, fig.title, fig.alt, width, height)
    _titles(lines, fig.title, fig.subtitle)
    _legend_row(
        lines,
        [(s.label, s.color, DASH[s.dash]) for s in fig.series],
        24,
        70,
    )
    all_values = [_d(v) for series in fig.series for v in series.values]
    all_dates = [d for series in fig.series for d in series.dates]
    lo, hi = _limits(all_values, fig.include_zero)
    x0 = min(all_dates)
    x1 = max(all_dates)
    span_days = _ordinal(x1) - _ordinal(x0) or 1

    def x_of(iso: str) -> float:
        return left + (_ordinal(iso) - _ordinal(x0)) / span_days * plot_w

    def y_of(value: Decimal) -> float:
        return top + float((hi - value) / (hi - lo)) * plot_h

    for tick in _ticks(lo, hi):
        y = y_of(tick)
        lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" '
            f'stroke="{PALETTE["grid"]}" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" fill="{PALETTE["ink"]}" '
            f'font-size="11" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
            f"{escape(_tick_text(tick))}</text>"
        )
    lines.append(
        f'<text x="16" y="{top + plot_h / 2:.0f}" fill="{PALETTE["muted"]}" font-size="11" '
        f'transform="rotate(-90 16 {top + plot_h / 2:.0f})" text-anchor="middle" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(fig.y_label)}</text>'
    )
    years = _year_ticks(x0, x1)
    for year in years:
        iso = f"{year}-01-01" if f"{year}-01-01" >= x0 else x0
        if iso > x1:
            continue
        x = x_of(iso if iso != x0 or iso.endswith("-01-01") else x0)
        # Label January when it falls inside the window; otherwise the first point's year.
        label_iso = f"{year}-01-01"
        if label_iso < x0 or label_iso > x1:
            if year != int(x0[:4]) and year != int(x1[:4]):
                continue
            label_iso = x0 if year == int(x0[:4]) else x1
        x = x_of(label_iso)
        lines.append(
            f'<text x="{x:.1f}" y="{height - bottom + 18}" text-anchor="middle" '
            f'fill="{PALETTE["ink"]}" font-size="11" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{year}</text>'
        )
    lines.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="{PALETTE["axis"]}"/>')
    lines.append(
        f'<line x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}" stroke="{PALETTE["axis"]}"/>'
    )
    for index, series in enumerate(fig.series):
        for run in _segments(series.dates, series.values, fig.max_gap_days):
            coords = [f"{x_of(iso):.1f},{y_of(_d(raw)):.1f}" for iso, raw in run]
            lines.append(
                f'<polyline fill="none" stroke="{series.color}" stroke-width="2.25" '
                f'stroke-dasharray="{DASH[series.dash]}" stroke-linejoin="round" '
                f'stroke-linecap="round" points="{" ".join(coords)}"/>'
            )
        last_x = x_of(series.dates[-1])
        last_y = y_of(_d(series.values[-1]))
        lines.append(f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="3.5" fill="{series.color}"/>')
        # White stroke keeps the value readable when it sits on the line.
        dy = -16 if index % 2 == 0 else 18
        lines.append(
            f'<text x="{last_x - 8:.1f}" y="{last_y + dy:.1f}" text-anchor="end" '
            f'fill="{series.color}" font-size="12" font-weight="700" '
            f'stroke="#FFFFFF" stroke-width="3" paint-order="stroke fill" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(series.values[-1])}</text>'
        )
    return _svg_footer(lines, width, height)


def _ordinal(iso: str) -> int:
    year, month, day = (int(part) for part in iso.split("-"))
    # Howard Hinnant civil-from-days inverse, enough for 1900–2100 chart axes.
    month_adj = month + (12 if month <= 2 else 0)
    year_adj = year - (1 if month <= 2 else 0)
    era = (year_adj if year_adj >= 0 else year_adj - 399) // 400
    yoe = year_adj - era * 400
    doy = (153 * (month_adj - 3) + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _year_ticks(x0: str, x1: str) -> list[int]:
    start = int(x0[:4])
    end = int(x1[:4])
    step = 2 if end - start > 8 else 1
    years = list(range(start, end + 1, step))
    if years[-1] != end:
        years.append(end)
    return years


def _svg_curve(fig: CurveFigure) -> str:
    width, height = 760, 420
    left, right, top, bottom = 64, 28, 78, 72
    plot_w = width - left - right
    plot_h = height - top - bottom
    lines = _svg_header(fig.slug, fig.title, fig.alt, width, height)
    _titles(lines, fig.title, fig.subtitle)
    values = [_d(v) for v in fig.values]
    lo, hi = _limits(values, include_zero=False)
    n = len(fig.categories)

    def x_of(index: int) -> float:
        if n == 1:
            return left + plot_w / 2
        return left + index / (n - 1) * plot_w

    def y_of(value: Decimal) -> float:
        return top + float((hi - value) / (hi - lo)) * plot_h

    for tick in _ticks(lo, hi):
        y = y_of(tick)
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="{PALETTE["grid"]}"/>')
        lines.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" fill="{PALETTE["ink"]}" '
            f'font-size="11" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
            f"{escape(_tick_text(tick))}</text>"
        )
    lines.append(
        f'<text x="16" y="{top + plot_h / 2:.0f}" fill="{PALETTE["muted"]}" font-size="11" '
        f'transform="rotate(-90 16 {top + plot_h / 2:.0f})" text-anchor="middle" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(fig.y_label)}</text>'
    )
    coords = []
    for index, value in enumerate(values):
        x = x_of(index)
        y = y_of(value)
        coords.append(f"{x:.1f},{y:.1f}")
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{fig.color}"/>')
        lines.append(
            f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" fill="{fig.color}" '
            f'font-size="12" font-weight="700" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
            f"{escape(_fmt(value, fig.places))}</text>"
        )
        lines.append(
            f'<text x="{x:.1f}" y="{height - bottom + 22}" text-anchor="middle" '
            f'fill="{PALETTE["ink"]}" font-size="12" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(fig.categories[index])}</text>'
        )
    lines.append(f'<polyline fill="none" stroke="{fig.color}" stroke-width="2.25" points="{" ".join(coords)}"/>')
    lines.append(
        f'<text x="{width / 2:.0f}" y="{height - 36}" text-anchor="middle" '
        f'fill="{PALETTE["muted"]}" font-size="12" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">'
        "Vertical axis does not start at zero. Read the labels for the slope.</text>"
    )
    return _svg_footer(lines, width, height)


def _svg_bars(fig: BarFigure) -> str:
    n = len(fig.labels)
    row = 28
    left = 168
    right = 78
    top = 78
    bottom = 62
    width = 760
    height = top + bottom + n * row
    plot_w = width - left - right
    lines = _svg_header(fig.slug, fig.title, fig.alt, width, height)
    _titles(lines, fig.title, fig.subtitle)
    values = [_d(v) for v in fig.values]
    if fig.diverging:
        bound = max(abs(v) for v in values) * Decimal("1.18") or Decimal(1)
        lo, hi = -bound, bound
    else:
        lo, hi = Decimal(0), max(values) * Decimal("1.08") or Decimal(1)

    def x_of(value: Decimal) -> float:
        return left + float((value - lo) / (hi - lo)) * plot_w

    zero_x = x_of(Decimal(0))
    lines.append(
        f'<line x1="{zero_x:.1f}" y1="{top}" x2="{zero_x:.1f}" y2="{top + n * row - 6}" stroke="{PALETTE["axis"]}"/>'
    )
    for index, (label, value) in enumerate(zip(fig.labels, values, strict=True)):
        y = top + index * row + 4
        x = x_of(value)
        color = PALETTE["vermillion"] if value < 0 else PALETTE["blue"] if value > 0 else PALETTE["axis"]
        bar_x = min(zero_x, x)
        bar_w = abs(x - zero_x) or 1
        lines.append(f'<rect x="{bar_x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="16" fill="{color}" rx="1"/>')
        text = f"{_fmt(value, fig.places)}{fig.suffix}"
        # Keep the number in the right margin so it does not sit on the bar or the country name.
        text_x = width - 12
        anchor = "end"
        lines.append(
            f'<text x="16" y="{y + 13:.1f}" fill="{PALETTE["ink"]}" font-size="13" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(label)}</text>'
        )
        lines.append(
            f'<text x="{text_x:.1f}" y="{y + 13:.1f}" text-anchor="{anchor}" fill="{PALETTE["ink"]}" '
            f'font-size="12" font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(text)}</text>'
        )
    lines.append(
        f'<text x="{left + plot_w / 2:.0f}" y="{height - 28}" text-anchor="middle" '
        f'fill="{PALETTE["ink"]}" font-size="12" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
        f"{escape(fig.x_label)}</text>"
    )
    return _svg_footer(lines, width, height)


def _svg_grouped(fig: GroupedBarFigure) -> str:
    n = len(fig.labels)
    row = 36
    left = 150
    right = 92
    top = 96
    bottom = 48
    width = 760
    height = top + bottom + n * row
    plot_w = width - left - right
    lines = _svg_header(fig.slug, fig.title, fig.alt, width, height)
    _titles(lines, fig.title, fig.subtitle)
    lines.append(
        f'<defs><pattern id="hatch-{fig.slug}" patternUnits="userSpaceOnUse" width="6" height="6">'
        f'<path d="M0,6 l6,-6" stroke="{fig.series_colors[1]}" stroke-width="1.2"/>'
        f"</pattern></defs>"
    )
    lines.append(
        f'<rect x="24" y="66" width="22" height="10" fill="{fig.series_colors[0]}" stroke="{fig.series_colors[0]}"/>'
    )
    lines.append(
        f'<text x="50" y="75" fill="{PALETTE["ink"]}" font-size="12" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(fig.series_labels[0])}</text>'
    )
    lines.append(
        f'<rect x="180" y="66" width="22" height="10" fill="url(#hatch-{fig.slug})" '
        f'stroke="{fig.series_colors[1]}" stroke-width="1"/>'
    )
    lines.append(
        f'<text x="206" y="75" fill="{PALETTE["ink"]}" font-size="12" '
        f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(fig.series_labels[1])} (hatched)</text>'
    )
    flat = [_d(v) for series in fig.series_values for v in series]
    hi = max(max(flat), Decimal(0)) * Decimal("1.12") or Decimal(1)
    lo = Decimal(0)

    def x_of(value: Decimal) -> float:
        return left + float((value - lo) / (hi - lo)) * plot_w

    for index, label in enumerate(fig.labels):
        y = top + index * row
        lines.append(
            f'<text x="12" y="{y + 22:.1f}" fill="{PALETTE["ink"]}" font-size="12" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(label)}</text>'
        )
        for series_index in (0, 1):
            value = _d(fig.series_values[series_index][index])
            bar_y = y + 4 + series_index * 14
            bar_w = max(x_of(value) - left, 1)
            fill = fig.series_colors[0] if series_index == 0 else f"url(#hatch-{fig.slug})"
            stroke = fig.series_colors[series_index]
            lines.append(
                f'<rect x="{left}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="12" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            )
            lines.append(
                f'<text x="{left + bar_w + 4:.1f}" y="{bar_y + 10:.1f}" fill="{PALETTE["ink"]}" '
                f'font-size="10" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
                f"{escape(_fmt(value, fig.places) + fig.suffix)}</text>"
            )
    lines.append(
        f'<text x="{left + plot_w / 2:.0f}" y="{height - 28}" text-anchor="middle" '
        f'fill="{PALETTE["ink"]}" font-size="12" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
        f"{escape(fig.x_label)}</text>"
    )
    return _svg_footer(lines, width, height)


def _svg_legend(fig: StyleLegend) -> str:
    width, height = 760, 220
    lines = _svg_header(fig.slug, fig.title, fig.alt, width, height)
    _titles(lines, fig.title, fig.subtitle)
    swatches = [
        ("Blue, solid", PALETTE["blue"], "solid"),
        ("Vermillion, dashed", PALETTE["vermillion"], "dashed"),
        ("Green, dotted", PALETTE["green"], "dotted"),
        ("Orange", PALETTE["orange"], "solid"),
        ("Sky", PALETTE["sky"], "solid"),
        ("Purple", PALETTE["purple"], "solid"),
    ]
    for index, (label, color, dash) in enumerate(swatches):
        col = index % 3
        row = index // 3
        x = 32 + col * 240
        y = 100 + row * 48
        lines.append(
            f'<line x1="{x}" y1="{y}" x2="{x + 48}" y2="{y}" stroke="{color}" '
            f'stroke-width="4" stroke-dasharray="{DASH[dash]}"/>'
        )
        lines.append(
            f'<text x="{x + 58}" y="{y + 4}" fill="{PALETTE["ink"]}" font-size="13" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">{escape(label)}</text>'
        )
    return _svg_footer(lines, width, height)


def _style_axes(ax, title: str, subtitle: str) -> None:
    ax.set_title(title + "\n" + subtitle, loc="left", color=PALETTE["ink"], fontsize=11, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=PALETTE["grid"])
    ax.tick_params(colors=PALETTE["ink"])


def _png_setup() -> None:
    import matplotlib

    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.unicode_minus": False,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def _save_png(fig_m, path) -> None:
    # Fixed metadata so two renders of the same figure match byte for byte.
    fig_m.savefig(path, dpi=120, metadata={"Software": "FinancialLibrary", "Creation Time": "2026-10-30"})
    import matplotlib.pyplot as plt

    plt.close(fig_m)


def _png_line(fig: LineFigure, path, plt) -> None:
    from datetime import datetime

    _png_setup()
    fig_m, ax = plt.subplots(figsize=(9.6, 5.4), dpi=120)
    fig_m.patch.set_facecolor("white")
    ax.set_facecolor("white")
    for series in fig.series:
        linestyle = {"solid": "solid", "dashed": "dashed", "dotted": "dotted"}[series.dash]
        labeled = False
        for run in _segments(series.dates, series.values, fig.max_gap_days):
            xs = [datetime.fromisoformat(observed) for observed, _raw in run]
            ys = [float(_d(raw)) for _observed, raw in run]
            ax.plot(
                xs,
                ys,
                color=series.color,
                linestyle=linestyle,
                linewidth=2,
                label=series.label if not labeled else None,
            )
            labeled = True
        ax.annotate(
            series.values[-1],
            (datetime.fromisoformat(series.dates[-1]), float(_d(series.values[-1]))),
            textcoords="offset points",
            xytext=(-8, 8 if series == fig.series[0] else -12),
            ha="right",
            color=series.color,
            fontsize=9,
            fontweight="bold",
        )
    if fig.include_zero:
        ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
    ax.set_ylabel(fig.y_label, color=PALETTE["ink"])
    ax.legend(frameon=False)
    _style_axes(ax, fig.title, fig.subtitle)
    fig_m.text(0.01, 0.01, FOOTER, color=PALETTE["ink"], fontsize=8)
    fig_m.tight_layout()
    _save_png(fig_m, path)


def _png_curve(fig: CurveFigure, path, plt) -> None:
    _png_setup()
    fig_m, ax = plt.subplots(figsize=(9.6, 5.0), dpi=120)
    fig_m.patch.set_facecolor("white")
    ys = [float(_d(v)) for v in fig.values]
    ax.plot(range(len(ys)), ys, color=fig.color, marker="o", linewidth=2)
    for index, value in enumerate(ys):
        ax.annotate(
            _fmt(_d(fig.values[index]), fig.places),
            (index, value),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            color=fig.color,
            fontsize=9,
            fontweight="bold",
        )
    ax.set_xticks(range(len(fig.categories)), list(fig.categories))
    ax.set_ylabel(fig.y_label, color=PALETTE["ink"])
    _style_axes(ax, fig.title, fig.subtitle)
    fig_m.text(0.01, 0.01, FOOTER, color=PALETTE["ink"], fontsize=8)
    fig_m.tight_layout()
    _save_png(fig_m, path)


def _png_bars(fig: BarFigure, path, plt) -> None:
    _png_setup()
    fig_m, ax = plt.subplots(figsize=(9.6, max(4.8, 0.38 * len(fig.labels) + 1.8)), dpi=120)
    fig_m.patch.set_facecolor("white")
    values = [float(_d(v)) for v in fig.values]
    colors = [PALETTE["vermillion"] if v < 0 else PALETTE["blue"] if v > 0 else PALETTE["axis"] for v in values]
    positions = list(range(len(fig.labels) - 1, -1, -1))
    ax.barh(positions, values, color=colors, height=0.7)
    span = max(abs(v) for v in values) or 1
    if fig.diverging:
        ax.set_xlim(-span * 1.35, span * 1.45)
    else:
        ax.set_xlim(0, max(values) * 1.28)
    for position, raw in zip(positions, fig.values, strict=True):
        value = _d(raw)
        label = f"{_fmt(value, fig.places)}{fig.suffix}"
        ax.text(ax.get_xlim()[1], position, label, va="center", ha="right", fontsize=8, color=PALETTE["ink"])
    ax.set_yticks(positions, list(fig.labels))
    ax.axvline(0, color=PALETTE["axis"], linewidth=0.8)
    ax.set_xlabel(fig.x_label, color=PALETTE["ink"])
    _style_axes(ax, fig.title, fig.subtitle)
    fig_m.text(0.01, 0.01, FOOTER, color=PALETTE["ink"], fontsize=8)
    fig_m.tight_layout()
    _save_png(fig_m, path)


def _png_grouped(fig: GroupedBarFigure, path, plt) -> None:
    from matplotlib.patches import Patch

    _png_setup()
    fig_m, ax = plt.subplots(figsize=(9.6, max(5.2, 0.46 * len(fig.labels) + 1.8)), dpi=120)
    fig_m.patch.set_facecolor("white")
    y = list(range(len(fig.labels)))
    height = 0.36
    for series_index, (color, values) in enumerate(zip(fig.series_colors, fig.series_values, strict=True)):
        offset = (series_index - 0.5) * height
        nums = [float(_d(v)) for v in values]
        ax.barh(
            [item + offset for item in y],
            nums,
            height=height,
            color="white" if series_index else color,
            edgecolor=color,
            hatch="//" if series_index else None,
        )
        for item, raw in zip(y, values, strict=True):
            ax.text(
                float(_d(raw)),
                item + offset,
                f"{_fmt(_d(raw), fig.places)}{fig.suffix}",
                va="center",
                ha="left",
                fontsize=7,
                color=PALETTE["ink"],
            )
    ax.set_yticks(y, list(fig.labels))
    ax.invert_yaxis()
    ax.legend(
        handles=[
            Patch(facecolor=fig.series_colors[0], edgecolor=fig.series_colors[0], label=fig.series_labels[0]),
            Patch(
                facecolor="white",
                edgecolor=fig.series_colors[1],
                hatch="//",
                label=f"{fig.series_labels[1]} (hatched)",
            ),
        ],
        frameon=False,
    )
    ax.set_xlabel(fig.x_label, color=PALETTE["ink"])
    _style_axes(ax, fig.title, fig.subtitle)
    fig_m.text(0.01, 0.01, FOOTER, color=PALETTE["ink"], fontsize=8)
    fig_m.tight_layout()
    _save_png(fig_m, path)


def _png_legend(fig: StyleLegend, path, plt) -> None:
    _png_setup()
    fig_m, ax = plt.subplots(figsize=(9.6, 3.2), dpi=120)
    fig_m.patch.set_facecolor("white")
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(fig.title + "\n" + fig.subtitle, loc="left", color=PALETTE["ink"], fontsize=11)
    samples = [
        ("Blue, solid", PALETTE["blue"], "solid"),
        ("Vermillion, dashed", PALETTE["vermillion"], "dashed"),
        ("Green, dotted", PALETTE["green"], "dotted"),
        ("Orange", PALETTE["orange"], "solid"),
        ("Sky", PALETTE["sky"], "solid"),
        ("Purple", PALETTE["purple"], "solid"),
    ]
    for index, (label, color, style) in enumerate(samples):
        col = index % 3
        row = index // 3
        x = 0.05 + col * 0.32
        y = 0.62 - row * 0.28
        ax.plot([x, x + 0.08], [y, y], color=color, linestyle=style, linewidth=3)
        ax.text(x + 0.1, y, label, color=PALETTE["ink"], fontsize=11, va="center")
    fig_m.text(0.01, 0.02, FOOTER, color=PALETTE["ink"], fontsize=8)
    fig_m.tight_layout()
    _save_png(fig_m, path)
