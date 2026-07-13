const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const N = require("../../site/assets/js/network-model.js");

// ---- groupByCorridor ----
const corridorFeatures = [
  { properties: { street: "MILWAUKEE AVE", segment_id: "1" } },
  { properties: { street: "MILWAUKEE AVE", segment_id: "2" } },
  { properties: { street: null, segment_id: "3" } },
];
const grouped = N.groupByCorridor(corridorFeatures);
assert.strictEqual(grouped.size, 2, "groupByCorridor: two distinct keys");
assert.ok(grouped.has("MILWAUKEE AVE"), "groupByCorridor: has named street");
assert.strictEqual(grouped.get("MILWAUKEE AVE").length, 2, "groupByCorridor: 2 features for Milwaukee");
assert.ok(grouped.has("(unnamed)"), "groupByCorridor: null street becomes (unnamed)");
assert.strictEqual(grouped.get("(unnamed)").length, 1, "groupByCorridor: 1 feature for (unnamed)");

// empty-string street also becomes (unnamed) and merges with null-street bucket
const grouped2 = N.groupByCorridor([
  { properties: { street: "", segment_id: "4" } },
  { properties: { street: null, segment_id: "5" } },
]);
assert.strictEqual(grouped2.size, 1, "groupByCorridor: empty string and null share (unnamed) bucket");
assert.strictEqual(grouped2.get("(unnamed)").length, 2, "groupByCorridor: both features bucketed");

// ---- toLatLngs ----
const multiLine = {
  type: "MultiLineString",
  coordinates: [
    [[-87.65, 41.90], [-87.64, 41.91]],
    [[-87.60, 41.80], [-87.59, 41.81]],
  ],
};
const latlngs = N.toLatLngs(multiLine);
assert.deepStrictEqual(
  latlngs,
  [
    [[41.90, -87.65], [41.91, -87.64]],
    [[41.80, -87.60], [41.81, -87.59]],
  ],
  "toLatLngs: MultiLineString round-trips into nested [lat,lng] parts"
);

const singleLine = {
  type: "LineString",
  coordinates: [[-87.65, 41.90], [-87.64, 41.91]],
};
assert.deepStrictEqual(
  N.toLatLngs(singleLine),
  [[41.90, -87.65], [41.91, -87.64]],
  "toLatLngs: LineString returns flat [lat,lng] list"
);

// ---- flattenCoords ----
assert.deepStrictEqual(
  N.flattenCoords(multiLine),
  [[-87.65, 41.90], [-87.64, 41.91], [-87.60, 41.80], [-87.59, 41.81]],
  "flattenCoords: MultiLineString flattens all parts"
);
assert.deepStrictEqual(
  N.flattenCoords(singleLine),
  [[-87.65, 41.90], [-87.64, 41.91]],
  "flattenCoords: LineString returns coordinates as-is"
);

// ---- getPaddedBBox / pointInBBox ----
const bbox = N.getPaddedBBox(singleLine, 0.001);
assert.deepStrictEqual(
  bbox,
  [[41.90 - 0.001, -87.65 - 0.001], [41.91 + 0.001, -87.64 + 0.001]],
  "getPaddedBBox: pads min/max lat/lng"
);
assert.ok(
  N.pointInBBox({ geometry: { coordinates: [-87.645, 41.905] } }, bbox),
  "pointInBBox: point inside bbox"
);
assert.ok(
  !N.pointInBBox({ geometry: { coordinates: [-87.9, 42.5] } }, bbox),
  "pointInBBox: point outside bbox"
);

// ---- ZOOM thresholds (spec §5): interchanges read at city scale,
// orientation nodes wait for street level ----
assert.deepStrictEqual(
  N.ZOOM, { interchangeNodes: 11, lineLabels: 11, corridorLabels: 13 },
  "ZOOM: interchange/line-label thresholds at 11, corridor/orientation-label threshold at 13"
);

// ---- DEFAULT_OVERLAYS (spec §5) ----
assert.deepStrictEqual(
  N.DEFAULT_OVERLAYS, ["connecting", "mellow", "nodes"],
  "DEFAULT_OVERLAYS: connecting+mellow+nodes on by default, quality/planned off"
);

// ---- parseOverlays / serializeOverlays (network.html URL state) ----
assert.deepStrictEqual(
  [...N.parseOverlays(null)], ["connecting", "mellow", "nodes"],
  "parseOverlays: null (param absent) falls back to defaults"
);
assert.deepStrictEqual(
  [...N.parseOverlays(undefined)], ["connecting", "mellow", "nodes"],
  "parseOverlays: undefined falls back to defaults"
);
assert.strictEqual(
  N.parseOverlays("").size, 0,
  "parseOverlays: explicit empty string means no overlays enabled"
);
assert.deepStrictEqual(
  [...N.parseOverlays("quality,connecting")], ["quality", "connecting"],
  "parseOverlays: comma list parses in order"
);
assert.deepStrictEqual(
  [...N.parseOverlays("heat,stations,trails")], ["heat", "stations", "trails"],
  "parseOverlays: legacy/unknown ids still parse into the Set (network.js just never checks for them, so they're ignored silently)"
);
assert.strictEqual(
  N.serializeOverlays(new Set(["quality", "nodes"])), "quality,nodes",
  "serializeOverlays: joins a Set with commas"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays("quality,connecting,mellow")),
  "quality,connecting,mellow",
  "round-trip: parseOverlays -> serializeOverlays preserves content"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays(null)),
  "connecting,mellow,nodes",
  "round-trip: absent param -> defaults -> 'connecting,mellow,nodes'"
);

// Empty set must survive the URL: BSD.setParams deletes empty-string params
// (so "" would fall back to defaults on reload). An empty set therefore
// serializes to the sentinel "none" instead of "".
assert.strictEqual(
  N.serializeOverlays(new Set()), "none",
  "serializeOverlays: empty set -> 'none' sentinel (not '')"
);
assert.strictEqual(
  N.parseOverlays("none").size, 0,
  "parseOverlays: 'none' sentinel -> empty set"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays("none")), "none",
  "round-trip: 'none' -> empty set -> 'none'"
);
assert.deepStrictEqual(
  [...N.parseOverlays(N.serializeOverlays(new Set()))], [],
  "round-trip: serialize(empty) parses back to empty, not defaults"
);

// ---- main routes: GRADE_COLORS / qualityCasingStyle (spec §4/§6) ----
assert.strictEqual(N.GRADE_COLORS.offstreet, "#0369a1", "GRADE_COLORS: offstreet");
assert.strictEqual(N.GRADE_COLORS.protected, "#0b6e4f", "GRADE_COLORS: protected");
assert.strictEqual(N.GRADE_COLORS.painted, "#f59e0b", "GRADE_COLORS: painted");
assert.strictEqual(N.GRADE_COLORS.none, "#94a3b8", "GRADE_COLORS: none");

assert.strictEqual(N.qualityCasingStyle("protected").color, "#0b6e4f", "qualityCasingStyle: protected color");
assert.strictEqual(N.qualityCasingStyle("protected").dashArray, undefined, "qualityCasingStyle: protected is solid");
assert.strictEqual(N.qualityCasingStyle("protected").weight, 13, "qualityCasingStyle: weight 13 (quality border, spec §5)");
assert.strictEqual(N.qualityCasingStyle("offstreet").color, "#0369a1", "qualityCasingStyle: offstreet color");
assert.strictEqual(N.qualityCasingStyle("painted").color, "#f59e0b", "qualityCasingStyle: painted color");
assert.strictEqual(N.qualityCasingStyle("none").color, "#94a3b8", "qualityCasingStyle: none color");
assert.strictEqual(N.qualityCasingStyle("none").dashArray, "6,9", "qualityCasingStyle: none is dashed 6,9");
assert.strictEqual(
  N.qualityCasingStyle("bogus").color, "#94a3b8",
  "qualityCasingStyle: unknown grade falls back to the none treatment"
);
assert.ok(N.qualityCasingStyle("bogus").dashArray, "qualityCasingStyle: unknown grade dashed like none");

// ---- main routes: LINE_COLORS / FALLBACK_LINE_COLOR / lineStyle (spec §4) ----
const EXPECTED_LINE_IDS = [
  "milwaukee", "elston", "vincennes",
  "california", "kedzie", "damen", "halsted", "clark", "state-indiana", "mlk-drive",
  "lawrence", "lake", "jackson-washington", "roosevelt", "marquette", "83rd",
  "lakefront", "bloomingdale", "major-taylor", "north-shore-channel", "north-branch",
];
assert.strictEqual(EXPECTED_LINE_IDS.length, 21, "test fixture: 21 line ids (16 street + 5 trail)");
EXPECTED_LINE_IDS.forEach((id) => {
  assert.ok(
    Object.prototype.hasOwnProperty.call(N.LINE_COLORS, id),
    `LINE_COLORS: has entry for "${id}"`
  );
  assert.match(
    N.LINE_COLORS[id], /^#[0-9a-f]{6}$/i,
    `LINE_COLORS["${id}"] is a 7-char hex color`
  );
});
assert.strictEqual(Object.keys(N.LINE_COLORS).length, 21, "LINE_COLORS: exactly 21 entries");
assert.match(N.FALLBACK_LINE_COLOR, /^#[0-9a-f]{6}$/i, "FALLBACK_LINE_COLOR is a 7-char hex color");

assert.strictEqual(N.lineStyle("milwaukee").color, N.LINE_COLORS.milwaukee, "lineStyle: known line uses LINE_COLORS entry");
assert.strictEqual(N.lineStyle("milwaukee").weight, 6, "lineStyle: weight 6 (spec §4)");
assert.strictEqual(N.lineStyle("milwaukee").opacity, 1, "lineStyle: opacity 1, no dashes/per-segment styling");
assert.strictEqual(N.lineStyle("milwaukee").dashArray, undefined, "lineStyle: major routes never dashed");
assert.strictEqual(N.lineStyle("not-a-real-line").color, N.FALLBACK_LINE_COLOR, "lineStyle: unknown line id falls back");
assert.strictEqual(N.lineStyle("not-a-real-line").weight, 6, "lineStyle: fallback still weight 6");

// ---- main routes: LOCAL_STYLE / CONNECTING_TRAIL_STYLE (spec §5) ----
assert.strictEqual(N.LOCAL_STYLE.color, "#cbd5e1", "LOCAL_STYLE: muted slate color");
assert.strictEqual(N.LOCAL_STYLE.weight, 1.5, "LOCAL_STYLE: 1.5px");
assert.strictEqual(N.CONNECTING_TRAIL_STYLE.color, "#38bdf8", "CONNECTING_TRAIL_STYLE: sky-blue color");
assert.strictEqual(N.CONNECTING_TRAIL_STYLE.weight, 2, "CONNECTING_TRAIL_STYLE: weight 2");
assert.strictEqual(N.CONNECTING_TRAIL_STYLE.opacity, 0.8, "CONNECTING_TRAIL_STYLE: opacity 0.8");

// ---- main routes: buildRosterIndex / splitByRoster / membersOfLine ----
const mainRouteFeatures = [
  { properties: { segment_id: "7", line_id: "milwaukee", grade: "protected" } },
  { properties: { segment_id: "8", line_id: "milwaukee", grade: "painted" } },
  { properties: { segment_id: "42", line_id: "halsted", grade: "none" } },
  { properties: { segment_id: "osm-trail-lakefront-trail", line_id: "lakefront", grade: "offstreet" } },
];
const rosterIdx = N.buildRosterIndex(mainRouteFeatures);
assert.strictEqual(rosterIdx.size, 4, "buildRosterIndex: one entry per member");
assert.deepStrictEqual(rosterIdx.get("7"), { lineId: "milwaukee", grade: "protected" },
  "buildRosterIndex: maps segment_id to line + grade");
assert.deepStrictEqual(rosterIdx.get("42"), { lineId: "halsted", grade: "none" },
  "buildRosterIndex: none-grade member indexed");
assert.strictEqual(N.buildRosterIndex(undefined).size, 0,
  "buildRosterIndex: missing features -> empty index");

const networkFeatures = [
  { properties: { segment_id: "7", street: "DEARBORN" } },
  { properties: { segment_id: "42", street: "HALSTED" } },
  { properties: { segment_id: "999", street: "MARQUETTE" } },
];
const split = N.splitByRoster(networkFeatures, rosterIdx);
assert.strictEqual(split.roster.length, 2, "splitByRoster: 2 roster members");
assert.strictEqual(split.local.length, 1, "splitByRoster: 1 local segment");
assert.strictEqual(split.local[0].properties.segment_id, "999",
  "splitByRoster: unmatched segment lands in local");

assert.deepStrictEqual(
  N.membersOfLine(networkFeatures, rosterIdx, "milwaukee").map(f => f.properties.segment_id),
  ["7"],
  "membersOfLine: filters features to one line's members"
);
assert.deepStrictEqual(
  N.membersOfLine(networkFeatures, rosterIdx, "no-such-line"), [],
  "membersOfLine: unknown line -> empty"
);

// ---- main routes: linesById ----
const linesMeta = N.linesById([
  { id: "milwaukee", name: "Milwaukee Line", no_data: false },
  { id: "lakefront", name: "Lakefront Trail", no_data: true },
]);
assert.strictEqual(linesMeta.get("milwaukee").name, "Milwaukee Line", "linesById: lookup by id");
assert.strictEqual(linesMeta.get("lakefront").no_data, true, "linesById: no_data preserved");
assert.strictEqual(N.linesById(undefined).size, 0, "linesById: missing lines array -> empty map");

// ---- main routes: rosterStreets (corridor labels defer to line labels) ----
const streets = N.rosterStreets(networkFeatures, rosterIdx);
assert.ok(streets.has("DEARBORN"), "rosterStreets: roster member street included");
assert.ok(streets.has("HALSTED"), "rosterStreets: second roster street included");
assert.ok(!streets.has("MARQUETTE"), "rosterStreets: local-only street excluded");

console.log("network-model OK");
