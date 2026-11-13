/**
 * Locks the Impact Calendar Calculator to the worked examples on the
 * tools page, and to labels that show those same cents.
 *
 * Run from the repository root:
 *   node --test tests/js/impact_calendar.test.mjs
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const SCRIPT = readFileSync(
  resolve(ROOT, "docs/assets/javascripts/interactive.js"),
  "utf8",
);

const FORM = `<!DOCTYPE html>
<html><body>
<form id="fl-ic-form">
  <button type="button" class="fl-ic-chip" data-ic-amount="10" data-ic-frequency="day">$10 a day</button>
  <button type="button" class="fl-ic-chip" data-ic-amount="25" data-ic-frequency="week">$25 a week</button>
  <input id="fl-ic-amount" type="number" value="10">
  <select id="fl-ic-frequency">
    <option value="day" selected>per day</option>
    <option value="week">per week</option>
    <option value="month">per month</option>
  </select>
  <input id="fl-ic-start" type="date" value="2026-11-01">
  <input id="fl-ic-years" type="range" min="1" max="40" value="1">
  <span id="fl-ic-years-label"></span>
  <input id="fl-ic-years-num" type="number" min="1" max="40" value="1">
  <input id="fl-ic-start-balance" type="number" value="0">
  <input id="fl-ic-growth" type="range" min="0" max="10" step="0.5" value="0">
  <span id="fl-ic-growth-label"></span>
  <p id="fl-ic-oneline"></p>
  <div id="fl-ic-chart"></div>
  <p id="fl-ic-chart-legend"></p>
  <div id="fl-ic-yearbars"></div>
  <div id="fl-ic-summary"></div>
  <div id="fl-ic-milestones"></div>
  <div id="fl-ic-years-table"></div>
  <div id="fl-ic-months-table"></div>
</form>
</body></html>`;

function load() {
  const dom = new JSDOM(FORM, {
    url: "https://example.test/tools/",
    runScripts: "outside-only",
  });
  vm.runInContext(SCRIPT, dom.getInternalVMContext());
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  return dom;
}

function cents(n) {
  return Math.round(n * 100) / 100;
}

function render(values) {
  const dom = load();
  const doc = dom.window.document;
  for (const [id, value] of Object.entries(values)) {
    doc.getElementById(id).value = String(value);
  }
  doc
    .getElementById("fl-ic-form")
    .dispatchEvent(new dom.window.Event("input", { bubbles: true }));
  return doc;
}

test("worked examples match the calendar recurrence to the cent", () => {
  const compute = load().window.flImpactCalendarCompute;

  const daily = compute({
    amount: 10,
    frequency: "day",
    startYear: 2026,
    startMonth: 10,
    years: 1,
    startBalance: 0,
    growthPct: 0,
  });
  assert.equal(cents(daily.contributed), 3650);
  assert.equal(daily.rows.reduce((n, r) => n + r.contributedMonth, 0), 3650);
  assert.deepEqual(
    JSON.parse(
      JSON.stringify(daily.milestones.map((ms) => [ms.amount, ms.year, ms.month])),
    ),
    [
      [500, 2026, 11],
      [1000, 2027, 1],
    ],
  );

  const saved = compute({
    amount: 200,
    frequency: "month",
    startYear: 2027,
    startMonth: 0,
    years: 5,
    startBalance: 1000,
    growthPct: 0,
  });
  assert.equal(cents(saved.contributed), 12000);
  assert.equal(cents(saved.total), 13000);
  assert.deepEqual(
    JSON.parse(
      JSON.stringify(saved.milestones.map((ms) => [ms.amount, ms.year, ms.month])),
    ),
    [
      [5000, 2028, 7],
      [10000, 2030, 8],
    ],
  );

  const grown = compute({
    amount: 100,
    frequency: "month",
    startYear: 2026,
    startMonth: 0,
    years: 10,
    startBalance: 0,
    growthPct: 5,
  });
  assert.equal(cents(grown.contributed), 12000);
  assert.equal(cents(grown.growth), 3528.23);
  assert.equal(cents(grown.total), 15528.23);

  const leap = compute({
    amount: 1,
    frequency: "day",
    startYear: 2024,
    startMonth: 1,
    years: 1,
    startBalance: 0,
    growthPct: 0,
  });
  const century = compute({
    amount: 1,
    frequency: "day",
    startYear: 2100,
    startMonth: 1,
    years: 1,
    startBalance: 0,
    growthPct: 0,
  });
  assert.equal(leap.rows[0].contributedMonth, 29);
  assert.equal(century.rows[0].contributedMonth, 28);
});

test("tables, year bars, and the chart show the same cents as the recurrence", () => {
  const week = render({
    "fl-ic-amount": "25",
    "fl-ic-frequency": "week",
    "fl-ic-start": "2026-01-01",
    "fl-ic-years": "1",
    "fl-ic-years-num": "1",
    "fl-ic-start-balance": "0",
    "fl-ic-growth": "0",
  });
  const weekMonths = [...week.querySelectorAll("#fl-ic-months-table tbody td")].map(
    (td) => td.textContent,
  );
  assert.equal(weekMonths[1], "$108.33");
  assert.ok(week.querySelector("#fl-ic-summary").textContent.includes("$1,300.00"));

  const saved = render({
    "fl-ic-amount": "200",
    "fl-ic-frequency": "month",
    "fl-ic-start": "2027-01-01",
    "fl-ic-years": "5",
    "fl-ic-years-num": "5",
    "fl-ic-start-balance": "1000",
    "fl-ic-growth": "0",
  });
  const bars = [...saved.querySelectorAll(".fl-ic-yrow-value")].map(
    (el) => el.textContent,
  );
  assert.equal(bars[0], "$2,400.00 put in · $3,400.00 running total");
  assert.equal(bars[bars.length - 1], "$2,400.00 put in · $13,000.00 running total");

  const grown = render({
    "fl-ic-amount": "100",
    "fl-ic-frequency": "month",
    "fl-ic-start": "2026-01-01",
    "fl-ic-years": "10",
    "fl-ic-years-num": "10",
    "fl-ic-start-balance": "0",
    "fl-ic-growth": "5",
  });
  const summary = grown.querySelector("#fl-ic-summary").textContent;
  assert.ok(summary.includes("$3,528.23"));
  assert.ok(summary.includes("$15,528.23"));
  assert.ok(
    summary.includes(
      "an assumption for illustration, not a prediction or a promised return",
    ),
  );
  const lastBar = [...grown.querySelectorAll(".fl-ic-yrow-value")].at(-1).textContent;
  assert.ok(lastBar.includes("$15,528.23 running total"));

  const daily = render({
    "fl-ic-amount": "10",
    "fl-ic-frequency": "day",
    "fl-ic-start": "2026-11-01",
    "fl-ic-years": "1",
    "fl-ic-years-num": "1",
    "fl-ic-start-balance": "0",
    "fl-ic-growth": "0",
  });
  const labels = [...daily.querySelectorAll("#fl-ic-chart text")].map(
    (el) => el.textContent,
  );
  assert.ok(labels.includes("$3,650.00 put in"));
  assert.ok(labels.includes("$1,250.00"));
  assert.ok(labels.includes("$3,750.00"));
  assert.equal(
    labels.some((label) => /\$3\.\dk/.test(label)),
    false,
  );
  assert.ok(
    daily.querySelector("#fl-ic-milestones").textContent.includes("February 2027"),
  );
});
