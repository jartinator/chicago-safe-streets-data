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

// CSV provenance (trust-hardening PR): exports must carry their own
// source/tier/as-of as #-comment lines that a parser can strip.
const csv = B.csvText(
  [{ a: 1, b: 'x,y' }, { a: 2, b: null }],
  ["a", "b"],
  B.provenanceLines("Test dataset", "derived", "2026-07-13T01:02:03Z", "A caveat.")
);
const lines = csv.split("\n");
assert.ok(lines[0].startsWith("# On Your Left! (OYL) — Test dataset"));
assert.ok(lines[1].includes("Data as of 2026-07-13"));
assert.ok(lines[1].includes("calculated by us from real data"), "tier rendered in plain words (TIER_PLAIN)");
assert.strictEqual(lines[2], "# A caveat.");
assert.ok(lines[3].startsWith("# Methodology & caveats:"));
assert.strictEqual(lines[4], "a,b");
assert.strictEqual(lines[5], '1,"x,y"');
assert.strictEqual(lines[6], "2,");
// no provenance → plain CSV, no comment lines
assert.strictEqual(B.csvText([{ a: 1 }], ["a"]).split("\n")[0], "a");
// newlines in provenance must not break the comment-line format
assert.ok(!B.provenanceLines("x", "real", null, "two\nlines")
  .some(l => l.includes("\n")) || B.csvText([], ["a"], ["two\nlines"]).split("\n")[0] === "# two lines");

console.log("common-helpers OK");

// ---- agendaHighlights: verbatim labels, ward/safety-first ordering ----
const meeting = {
  agenda_items: [
    { record_number: null, ward: null, section: "MAYORAL",
      agenda_text: "APPOINTMENT OF X - The appointment of X to the CTA board.",
      safety_keyword_match: false, tracked: false },
    { record_number: "O2026-2", ward: 43, section: null,
      agenda_text: "SOMETHING - O2026-2", title: "Protected bike lane on Clark St",
      type: "Ordinance", sponsor: "Doe, Jane",
      matter_url: "https://x/matter/2", safety_keyword_match: true, tracked: true },
    { record_number: "O2026-3", ward: 28, section: null,
      agenda_text: "ALLEY THING - O2026-3", title: "Vacation of alley",
      safety_keyword_match: false, tracked: false },
  ],
};
const hs = B.agendaHighlights(meeting, 28, 2);
assert.strictEqual(hs.length, 2, "capped at max");
assert.strictEqual(hs[0].label, "Vacation of alley", "this ward's item first");
assert.strictEqual(hs[0].forWard, true);
assert.strictEqual(hs[1].label, "Protected bike lane on Clark St", "safety match next");
assert.strictEqual(hs[1].safety, true);
assert.strictEqual(hs[1].url, "https://x/matter/2");
assert.strictEqual(hs[1].sponsor, "Doe, Jane");

const all = B.agendaHighlights(meeting, null, 0);
assert.strictEqual(all.length, 3, "max 0/omitted returns everything");
assert.strictEqual(all[0].label, "Protected bike lane on Clark St",
  "no ward filter: safety match first");
assert.ok(all.some(h => h.label.startsWith("APPOINTMENT OF X")),
  "no-record item falls back to verbatim agenda text");

// Truncation of long PDF text (no title from the record lookup)
const long = B.agendaHighlights({ agenda_items: [
  { agenda_text: "A".repeat(200), safety_keyword_match: false }] }, null, 0)[0];
assert.strictEqual(long.label.length, 141, "140 chars + ellipsis");
assert.ok(long.label.endsWith("…"));

assert.deepStrictEqual(B.agendaHighlights({}, 28, 2), [],
  "meeting without agenda_items (PDF not parsed) yields [] — nothing invented");
assert.deepStrictEqual(B.agendaHighlights(null, 28, 2), []);

