const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const N = require("../../site/assets/js/network-model.js");

// ---- heatBucket ----
assert.strictEqual(N.heatBucket(0), null, "heatBucket(0) is null");
assert.strictEqual(N.heatBucket(1).color, "#fbbf24", "heatBucket(1) is amber");
assert.strictEqual(N.heatBucket(2).color, "#fbbf24", "heatBucket(2) is amber");
assert.strictEqual(N.heatBucket(2).label, "1–2", "heatBucket(2) label");
assert.strictEqual(N.heatBucket(3).color, "#f97316", "heatBucket(3) is orange");
assert.strictEqual(N.heatBucket(5).color, "#f97316", "heatBucket(5) is orange");
assert.strictEqual(N.heatBucket(3).label, "3–5", "heatBucket(3) label");
assert.strictEqual(N.heatBucket(6).color, "#dc2626", "heatBucket(6) is red");
assert.strictEqual(N.heatBucket(6).label, "6+", "heatBucket(6) label");
assert.strictEqual(N.heatBucket(20).color, "#dc2626", "heatBucket(20) is red");

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

// ---- countObstructions ----
const routeFeatures = [
  {
    properties: { segment_id: "A" },
    geometry: {
      type: "LineString",
      coordinates: [[-87.65, 41.90], [-87.64, 41.91]],
    },
  },
];
const obstructionPoints = [
  { geometry: { coordinates: [-87.645, 41.905] } }, // inside bbox
  { geometry: { coordinates: [-87.6445, 41.906] } }, // inside bbox
  { geometry: { coordinates: [-87.9, 42.5] } }, // far outside bbox
];
const counts = N.countObstructions(routeFeatures, obstructionPoints);
assert.strictEqual(counts.get("A"), 2, "countObstructions: 2 of 3 points inside bbox");

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

// ---- parseOverlays / serializeOverlays (network.html URL state) ----
assert.deepStrictEqual(
  [...N.parseOverlays(null)], ["heat", "stations", "trails"],
  "parseOverlays: null (param absent) falls back to defaults heat+stations+trails"
);
assert.deepStrictEqual(
  [...N.parseOverlays(undefined)], ["heat", "stations", "trails"],
  "parseOverlays: undefined falls back to defaults heat+stations+trails"
);
assert.strictEqual(
  N.parseOverlays("").size, 0,
  "parseOverlays: explicit empty string means no overlays enabled"
);
assert.deepStrictEqual(
  [...N.parseOverlays("heat,crashes")], ["heat", "crashes"],
  "parseOverlays: comma list parses in order"
);
assert.strictEqual(
  N.serializeOverlays(new Set(["heat", "crashes"])), "heat,crashes",
  "serializeOverlays: joins a Set with commas"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays("heat,crashes,stations")),
  "heat,crashes,stations",
  "round-trip: parseOverlays -> serializeOverlays preserves content"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays(null)),
  "heat,stations,trails",
  "round-trip: absent param -> defaults -> 'heat,stations,trails'"
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

// ---- main routes: GRADE_COLORS / gradeLineStyle (spec §4) ----
assert.strictEqual(N.GRADE_COLORS.offstreet, "#0369a1", "GRADE_COLORS: offstreet");
assert.strictEqual(N.GRADE_COLORS.protected, "#0b6e4f", "GRADE_COLORS: protected");
assert.strictEqual(N.GRADE_COLORS.painted, "#f59e0b", "GRADE_COLORS: painted");
assert.strictEqual(N.GRADE_COLORS.none, "#94a3b8", "GRADE_COLORS: none");

assert.strictEqual(N.gradeLineStyle("protected").color, "#0b6e4f", "gradeLineStyle: protected color");
assert.strictEqual(N.gradeLineStyle("protected").dashArray, undefined, "gradeLineStyle: protected is solid");
assert.strictEqual(N.gradeLineStyle("offstreet").color, "#0369a1", "gradeLineStyle: offstreet color");
assert.strictEqual(N.gradeLineStyle("painted").color, "#f59e0b", "gradeLineStyle: painted color");
assert.strictEqual(N.gradeLineStyle("none").color, "#94a3b8", "gradeLineStyle: none color");
assert.ok(N.gradeLineStyle("none").dashArray, "gradeLineStyle: none is dashed");
assert.strictEqual(
  N.gradeLineStyle("bogus").color, "#94a3b8",
  "gradeLineStyle: unknown grade falls back to the none treatment"
);
assert.ok(N.gradeLineStyle("bogus").dashArray, "gradeLineStyle: unknown grade dashed like none");
assert.ok(N.gradeLineStyle("protected").weight > N.LOCAL_STYLE.weight,
  "gradeLineStyle: roster lines heavier than local network");

// ---- main routes: LOCAL_STYLE (demoted "bus" network, spec §7) ----
assert.strictEqual(N.LOCAL_STYLE.color, "#cbd5e1", "LOCAL_STYLE: muted slate color");
assert.strictEqual(N.LOCAL_STYLE.weight, 1.5, "LOCAL_STYLE: 1.5px");

// ---- main routes: buildRosterIndex / splitByRoster / membersOfLine ----
const mainRouteFeatures = [
  { properties: { segment_id: "7", line_id: "loop", grade: "protected" } },
  { properties: { segment_id: "8", line_id: "loop", grade: "painted" } },
  { properties: { segment_id: "42", line_id: "halsted", grade: "none" } },
  { properties: { segment_id: "osm-trail-lakefront-trail", line_id: "lakefront", grade: "offstreet" } },
];
const rosterIdx = N.buildRosterIndex(mainRouteFeatures);
assert.strictEqual(rosterIdx.size, 4, "buildRosterIndex: one entry per member");
assert.deepStrictEqual(rosterIdx.get("7"), { lineId: "loop", grade: "protected" },
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
  N.membersOfLine(networkFeatures, rosterIdx, "loop").map(f => f.properties.segment_id),
  ["7"],
  "membersOfLine: filters features to one line's members"
);
assert.deepStrictEqual(
  N.membersOfLine(networkFeatures, rosterIdx, "no-such-line"), [],
  "membersOfLine: unknown line -> empty"
);

// ---- main routes: linesById ----
const linesMeta = N.linesById([
  { id: "loop", name: "Downtown circulator", no_data: false },
  { id: "lakefront", name: "Lakefront Trail", no_data: true },
]);
assert.strictEqual(linesMeta.get("loop").name, "Downtown circulator", "linesById: lookup by id");
assert.strictEqual(linesMeta.get("lakefront").no_data, true, "linesById: no_data preserved");
assert.strictEqual(N.linesById(undefined).size, 0, "linesById: missing lines array -> empty map");

// ---- main routes: rosterStreets (corridor labels defer to line labels) ----
const streets = N.rosterStreets(networkFeatures, rosterIdx);
assert.ok(streets.has("DEARBORN"), "rosterStreets: roster member street included");
assert.ok(streets.has("HALSTED"), "rosterStreets: second roster street included");
assert.ok(!streets.has("MARQUETTE"), "rosterStreets: local-only street excluded");

// ---- main routes: station split (no stations on the bus layer below LABEL_MIN_ZOOM) ----
const rosterBBoxes = [N.getPaddedBBox(singleLine, 0.001)];
const stations = [
  { lat: 41.905, lng: -87.645, label: "on roster" },
  { lat: 42.5, lng: -87.9, label: "far away" },
];
assert.ok(N.stationInAnyBBox(stations[0], rosterBBoxes), "stationInAnyBBox: near roster line");
assert.ok(!N.stationInAnyBBox(stations[1], rosterBBoxes), "stationInAnyBBox: far from roster");
const stationSplit = N.splitStations(stations, rosterBBoxes);
assert.strictEqual(stationSplit.onRoster.length, 1, "splitStations: 1 station on roster");
assert.strictEqual(stationSplit.onRoster[0].label, "on roster", "splitStations: right station kept");
assert.strictEqual(stationSplit.offRoster.length, 1, "splitStations: 1 station off roster");
assert.strictEqual(N.splitStations([], rosterBBoxes).onRoster.length, 0,
  "splitStations: empty stations -> empty partitions");

console.log("network-model OK");
