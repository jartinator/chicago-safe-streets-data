const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const B = require("../../site/assets/js/common.js");

assert.strictEqual(B.scoreColor(null), "#e2e8f0");
assert.strictEqual(B.scoreColor(86.8), "#991b1b");
assert.strictEqual(B.scoreColor(45), "#f59e0b");
assert.strictEqual(B.money(19416.66), "$19,417");
assert.strictEqual(B.money(null), "—");
assert.ok(B.trendHTML({ direction: "worsening", pct_change: 25.0 }).includes("▲"));
assert.ok(B.trendHTML({ direction: "insufficient_data" }).includes("Insufficient"));

// Rebrand regression: the brand render is DOM-only, but the Node-facing exports
// must keep working exactly as before.
assert.strictEqual(typeof B.esc, "function");
assert.strictEqual(B.esc('<a href="x">& \'y\'</a>'),
  "&lt;a href=&quot;x&quot;&gt;&amp; &#39;y&#39;&lt;/a&gt;");
assert.strictEqual(B.esc(null), "");
assert.strictEqual(B.fmt(19416), "19,416");
assert.strictEqual(B.fmt(null), "—");

// Regression: improving trends carry NEGATIVE pct_change from the pipeline;
// the sign must render as-is, not be flipped to "+".
const improving = B.trendHTML({ direction: "improving", pct_change: -30.0 });
assert.ok(improving.includes("▼"), "improving trend shows down arrow");
assert.ok(improving.includes("-30%"), "improving trend shows signed -30%");
assert.ok(!improving.includes("+30%"), "improving trend must not show +30%");

// Tappable badges: badgeHTML renders a <button> carrying data-tier so the
// delegated click handler can open the tier explainer.
const proxyBadge = B.badgeHTML("proxy");
assert.ok(proxyBadge.includes("<button"), "badge renders as a <button>");
assert.ok(proxyBadge.includes('data-tier="proxy"'), "badge carries data-tier");
assert.ok(proxyBadge.includes("tier-proxy"), "badge keeps tier-{t} class");
const bogusBadge = B.badgeHTML("bogus");
assert.ok(bogusBadge.includes('data-tier="stub"'), "unknown tier falls back to stub");
assert.ok(bogusBadge.includes("no data yet"), "stub badge label is 'no data yet'");

// Plain-language tier explainers for the modal.
assert.strictEqual(typeof B.TIER_PLAIN, "object");
for (const tier of ["real", "proxy", "derived", "mock", "crowdsourced", "stub"]) {
  assert.ok(typeof B.TIER_PLAIN[tier] === "string" && B.TIER_PLAIN[tier].length > 0,
    `TIER_PLAIN has plain wording for '${tier}'`);
}

// Trend chart + trailing-window + .ics helpers (pure, Node-testable).
const months = [];
for (let i = 0; i < 24; i++) {
  months.push({
    month: `20${24 + Math.floor(i / 12)}-${String((i % 12) + 1).padStart(2, "0")}`,
    crashes: 10, injury_crashes: 3, ksi: 1, fatal: 0,
  });
}

// rollingSums: 24 input months, window 12 -> 13 points, each value 120;
// entries before a full window are omitted.
const rolled = B.rollingSums(months, "crashes", 12);
assert.strictEqual(rolled.length, 13, "24 months / window 12 -> 13 points");
assert.strictEqual(rolled[0].month, "2024-12", "first point ends the first full window");
assert.strictEqual(rolled[rolled.length - 1].month, "2025-12");
for (const p of rolled) assert.strictEqual(p.value, 120, "each trailing-12 sum is 120");
const rolledKsi = B.rollingSums(months, "ksi", 12);
assert.strictEqual(rolledKsi[0].value, 12);
assert.deepStrictEqual(B.rollingSums(months.slice(0, 5), "crashes", 12), [],
  "fewer months than the window -> no points");

// trendChartSVG: sparkline-plus SVG string.
const svg = B.trendChartSVG(rolled, { label: "Crashes, trailing 12 months", median: 100 });
assert.ok(svg.startsWith("<svg"), "returns an <svg> string");
assert.ok(svg.includes("polyline"), "renders a polyline");
assert.ok(svg.includes("2024-12"), "labels the first month");
assert.ok(svg.includes("2025-12"), "labels the last month");
assert.ok(svg.includes(">120<"), "labels the current value");
assert.ok(svg.includes("city median"), "labels the median line when given");
assert.strictEqual(B.trendChartSVG([{ month: "2024-01", value: 1 }], {}), "",
  "fewer than 2 points -> empty string");

// icsForEvent: RFC-5545 VEVENT with floating local DTSTART and CRLF endings.
const ics = B.icsForEvent({
  title: "Committee on Transportation and Public Way",
  startISO: "2026-07-14T13:00:00",
  location: "City Hall, Room 201-A",
  url: "https://example.org/agenda.pdf",
  description: "Agenda:\nPublic comment",
});
assert.ok(ics.includes("BEGIN:VCALENDAR"));
assert.ok(ics.includes("BEGIN:VEVENT"));
assert.ok(ics.includes("DTSTART:20260714T130000"), "DTSTART is floating local time");
assert.ok(ics.includes("LOCATION:City Hall\\, Room 201-A"), "commas escaped in text fields");
assert.ok(ics.includes("DESCRIPTION:Agenda:\\nPublic comment"), "newlines escaped as \\n");
assert.ok(ics.includes("UID:"), "event carries a UID");
assert.ok(!/[^\r]\n/.test(ics), "every LF is part of a CRLF");
assert.ok(ics.includes("\r\n"), "uses CRLF line endings");

// downloadICS is DOM-bound but must be exported alongside the pure helpers.
assert.strictEqual(typeof B.downloadICS, "function");

// mixSegments: shared stacked-bar helper behind BSDMainRoutes.completionSegments
// (main routes report card) and BSDNet.qualityMixSegments (network map mix bar).
const mix1 = B.mixSegments({ a: 3, b: 1 }, ["a", "b"], { colors: { a: "#111111", b: "#222222" } });
assert.deepStrictEqual(mix1.map(s => s.grade), ["a", "b"], "mixSegments: one entry per non-zero grade, in `order`");
assert.ok(Math.abs(mix1[0].pct - 75) < 1e-9, "mixSegments: pct is share of the present-grade total");
assert.ok(Math.abs(mix1[1].pct - 25) < 1e-9, "mixSegments: second entry's pct");
assert.strictEqual(mix1[0].color, "#111111", "mixSegments: color from opts.colors");
assert.strictEqual(mix1[0].miles, 3, "mixSegments: raw miles carried through");
assert.strictEqual(mix1[0].label, undefined, "mixSegments: no label field when opts.labels omitted");

const mix2 = B.mixSegments({ a: 1, b: 1 }, ["a", "b"], { colors: { a: "#111111", b: "#222222" }, labels: { a: "Alpha", b: "Beta" } });
assert.strictEqual(mix2[0].label, "Alpha", "mixSegments: label from opts.labels when supplied");
assert.strictEqual(mix2[1].label, "Beta", "mixSegments: label for second entry");

// Grade order in `order` controls output order, not input key order.
const mix3 = B.mixSegments({ b: 1, a: 1 }, ["a", "b"], { colors: {} });
assert.deepStrictEqual(mix3.map(s => s.grade), ["a", "b"], "mixSegments: output follows `order`, not input key order");

// Zero-value and absent grades are omitted; totally-empty input -> [].
assert.deepStrictEqual(B.mixSegments({ a: 0, b: 2 }, ["a", "b"], { colors: {} }).map(s => s.grade), ["b"],
  "mixSegments: zero-mile grades omitted");
assert.deepStrictEqual(B.mixSegments(null, ["a"], {}), [], "mixSegments: null input -> []");
assert.deepStrictEqual(B.mixSegments({}, ["a"], {}), [], "mixSegments: empty input -> []");
assert.deepStrictEqual(B.mixSegments({ a: 0 }, ["a"], {}), [], "mixSegments: all-zero input -> []");

console.log("common-helpers OK");
