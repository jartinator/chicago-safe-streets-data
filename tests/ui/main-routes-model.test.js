const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const M = require("../../site/assets/js/main-routes-model.js");

// ---- grade constants (spec §4) ----

assert.deepStrictEqual(
  M.GRADE_ORDER, ["offstreet", "protected", "painted", "none"],
  "GRADE_ORDER: off-street > protected > painted > none (user-ranked)"
);
assert.strictEqual(M.GRADE_COLORS.offstreet, "#0369a1", "offstreet grade color matches spec");
assert.strictEqual(M.GRADE_COLORS.protected, "#0b6e4f", "protected grade color matches spec");
assert.strictEqual(M.GRADE_COLORS.painted, "#f59e0b", "painted grade color matches spec");
assert.strictEqual(M.GRADE_COLORS.none, "#94a3b8", "none grade color matches spec");
["offstreet", "protected", "painted", "none"].forEach(g =>
  assert.ok(M.GRADE_LABELS[g], `GRADE_LABELS has a label for ${g}`));

// ---- gradeStyle: grade -> Leaflet-ready stroke style ----

const prot = M.gradeStyle("protected");
assert.strictEqual(prot.color, "#0b6e4f", "gradeStyle(protected): spec color");
assert.strictEqual(prot.weight, 4.5, "gradeStyle: 4.5px stroke per spec §7");
assert.strictEqual(prot.dashArray, null, "gradeStyle(protected): solid line");

const none = M.gradeStyle("none");
assert.strictEqual(none.color, "#94a3b8", "gradeStyle(none): muted gray");
assert.ok(none.dashArray, "gradeStyle(none): dashed per spec §4");

const off = M.gradeStyle("offstreet");
assert.strictEqual(off.color, "#0369a1", "gradeStyle(offstreet): trail blue");
assert.strictEqual(off.dashArray, null, "gradeStyle(offstreet): solid line");

// Unknown grades never crash the renderer — fall back to the none style
// color but stay solid (we don't know it's a sharrow).
const unknown = M.gradeStyle("mystery");
assert.strictEqual(unknown.color, "#94a3b8", "gradeStyle(unknown): falls back to muted gray");

// Casing sits under every grade stroke: white, 8px.
assert.strictEqual(M.CASING_STYLE.color, "#fff", "CASING_STYLE: white casing");
assert.strictEqual(M.CASING_STYLE.weight, 8, "CASING_STYLE: 8px per spec §7");

// ---- completionSegments: miles_by_grade -> stacked-bar segments ----

// Segments come back in GRADE_ORDER with percentage widths of total miles.
const segs = M.completionSegments({ painted: 3, protected: 1 });
assert.strictEqual(segs.length, 2, "completionSegments: one segment per non-zero grade");
assert.strictEqual(segs[0].grade, "protected", "completionSegments: protected before painted (GRADE_ORDER)");
assert.strictEqual(segs[1].grade, "painted", "completionSegments: painted second");
assert.ok(Math.abs(segs[0].pct - 25) < 1e-9, "completionSegments: 1 of 4 miles -> 25%");
assert.ok(Math.abs(segs[1].pct - 75) < 1e-9, "completionSegments: 3 of 4 miles -> 75%");
assert.strictEqual(segs[0].color, "#0b6e4f", "completionSegments: segments carry grade color");
assert.strictEqual(segs[0].miles, 1, "completionSegments: segments carry raw miles");

// Percent widths always sum to 100 (bar fills its track exactly).
const three = M.completionSegments({ protected: 2.21, painted: 6.77, none: 0.51 });
const total = three.reduce((s, x) => s + x.pct, 0);
assert.ok(Math.abs(total - 100) < 1e-6, "completionSegments: pct widths sum to 100");
assert.deepStrictEqual(three.map(s => s.grade), ["protected", "painted", "none"],
  "completionSegments: three grades ordered protected > painted > none");

// Zero and missing grades are omitted; empty input -> empty bar.
const sparse = M.completionSegments({ protected: 0, painted: 2 });
assert.deepStrictEqual(sparse.map(s => s.grade), ["painted"],
  "completionSegments: zero-mile grades omitted");
assert.deepStrictEqual(M.completionSegments({}), [], "completionSegments: empty input -> []");
assert.deepStrictEqual(M.completionSegments(null), [], "completionSegments: null input -> []");

// Trail lines are all off-street.
const trail = M.completionSegments({ offstreet: 18.2 });
assert.strictEqual(trail.length, 1, "completionSegments: single-grade line -> one segment");
assert.ok(Math.abs(trail[0].pct - 100) < 1e-9, "completionSegments: single grade fills the bar");

// ---- rosterOrder: lines with data first, no_data lines last, stable ----

const roster = [
  { id: "loop" },
  { id: "lakefront", no_data: true },
  { id: "milwaukee" },
  { id: "bloomingdale", no_data: true },
  { id: "halsted" },
];
const ordered = M.rosterOrder(roster);
assert.deepStrictEqual(ordered.map(l => l.id),
  ["loop", "milwaukee", "halsted", "lakefront", "bloomingdale"],
  "rosterOrder: no_data lines sink to the bottom, config order preserved within groups");
// Input is not mutated.
assert.strictEqual(roster[1].id, "lakefront", "rosterOrder: does not mutate input");
assert.deepStrictEqual(M.rosterOrder([]), [], "rosterOrder: empty roster -> []");

// ---- no_data handling: badge tier + pct text ----

assert.strictEqual(M.lineBadgeTier({ data_tier: "derived" }), "derived",
  "lineBadgeTier: street line keeps its derived tier");
assert.strictEqual(M.lineBadgeTier({ data_tier: "crowdsourced" }), "crowdsourced",
  "lineBadgeTier: trail line keeps its crowdsourced tier");
assert.strictEqual(M.lineBadgeTier({ data_tier: "crowdsourced", no_data: true }), "stub",
  "lineBadgeTier: no_data line downgrades to stub badge");

assert.strictEqual(M.pctText({ pct_protected: 68.4 }), "68.4% protected",
  "pctText: one decimal kept when meaningful");
assert.strictEqual(M.pctText({ pct_protected: 36.0 }), "36% protected",
  "pctText: trailing .0 stripped");
assert.strictEqual(M.pctText({ pct_protected: 0 }), "0% protected",
  "pctText: zero percent is a real (damning) value, not missing");
assert.strictEqual(M.pctText({}), null,
  "pctText: trail lines carry no pct_protected -> null (never fabricate)");
assert.strictEqual(M.pctText({ no_data: true }), null, "pctText: no_data line -> null");

// ---- window export parity ----
assert.strictEqual(global.window.BSDMainRoutes, M,
  "module exposes the same api object on window.BSDMainRoutes");

console.log("main-routes-model OK");
