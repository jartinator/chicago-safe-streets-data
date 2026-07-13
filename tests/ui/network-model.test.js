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

// ---- getPaddedBBox ----
const bbox = N.getPaddedBBox(singleLine, 0.001);
assert.deepStrictEqual(
  bbox,
  [[41.90 - 0.001, -87.65 - 0.001], [41.91 + 0.001, -87.64 + 0.001]],
  "getPaddedBBox: pads min/max lat/lng"
);

// ---- unionBBox (dedup: fitLineBounds / citywide fit / corridor deep link) ----
assert.deepStrictEqual(N.unionBBox([]), [], "unionBBox: empty input -> []");
assert.deepStrictEqual(N.unionBBox(undefined), [], "unionBBox: missing input -> []");
assert.deepStrictEqual(
  N.unionBBox([{ geometry: singleLine }]),
  N.getPaddedBBox(singleLine),
  "unionBBox: single feature matches its own getPaddedBBox (default pad)"
);
const secondLine = { type: "LineString", coordinates: [[-87.70, 41.70], [-87.69, 41.72]] };
const unioned = N.unionBBox([{ geometry: singleLine }, { geometry: secondLine }]);
const bboxA = N.getPaddedBBox(singleLine);
const bboxB = N.getPaddedBBox(secondLine);
assert.strictEqual(unioned[0][0], Math.min(bboxA[0][0], bboxB[0][0]), "unionBBox: min lat across features");
assert.strictEqual(unioned[0][1], Math.min(bboxA[0][1], bboxB[0][1]), "unionBBox: min lng across features");
assert.strictEqual(unioned[1][0], Math.max(bboxA[1][0], bboxB[1][0]), "unionBBox: max lat across features");
assert.strictEqual(unioned[1][1], Math.max(bboxA[1][1], bboxB[1][1]), "unionBBox: max lng across features");

// ---- ZOOM thresholds ----
assert.deepStrictEqual(
  N.ZOOM, { interchangeNodes: 11, lineLabels: 11, corridorLabels: 13 },
  "ZOOM: interchange/line-label thresholds at 11, corridor/orientation-label threshold at 13"
);

// ---- DEFAULT_OVERLAYS (design v2 §10: all three tiers + nodes on, quality/planned off) ----
assert.deepStrictEqual(
  N.DEFAULT_OVERLAYS, ["trails", "main", "connectors", "nodes"],
  "DEFAULT_OVERLAYS: trails+main+connectors+nodes on by default, quality/planned off"
);

// ---- parseOverlays / serializeOverlays (network.html URL state) ----
assert.deepStrictEqual(
  [...N.parseOverlays(null)], ["trails", "main", "connectors", "nodes"],
  "parseOverlays: null (param absent) falls back to defaults"
);
assert.deepStrictEqual(
  [...N.parseOverlays(undefined)], ["trails", "main", "connectors", "nodes"],
  "parseOverlays: undefined falls back to defaults"
);
assert.strictEqual(
  N.parseOverlays("").size, 0,
  "parseOverlays: explicit empty string means no overlays enabled"
);
assert.deepStrictEqual(
  [...N.parseOverlays("quality,main")], ["quality", "main"],
  "parseOverlays: comma list parses in order"
);
assert.deepStrictEqual(
  [...N.parseOverlays("connecting,mellow,trails")], ["connecting", "mellow", "trails"],
  "parseOverlays: legacy/unknown ids (pre-v2 'connecting'/'mellow') still parse into the Set — network.js just never checks for them, so they're ignored silently"
);
assert.strictEqual(
  N.serializeOverlays(new Set(["quality", "nodes"])), "quality,nodes",
  "serializeOverlays: joins a Set with commas"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays("quality,trails,connectors")),
  "quality,trails,connectors",
  "round-trip: parseOverlays -> serializeOverlays preserves content"
);
assert.strictEqual(
  N.serializeOverlays(N.parseOverlays(null)),
  "trails,main,connectors,nodes",
  "round-trip: absent param -> defaults -> 'trails,main,connectors,nodes'"
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

// ---- LINE_COLORS / FALLBACK_LINE_COLOR / lineStyle (spec §9) ----
const EXPECTED_LINE_COLORS = {
  milwaukee: "#1d4ed8", elston: "#ea580c", halsted: "#dc2626", damen: "#eab308",
  kedzie: "#7c3aed", california: "#db2777", clark: "#0891b2", "state-indiana": "#4d7c0f",
  "mlk-drive": "#92400e", "jackson-washington": "#6b21a8", lawrence: "#881337",
  marquette: "#1e40af", lake: "#a16207", "83rd": "#15803d",
  lakefront: "#0369a1", bloomingdale: "#16a34a", "major-taylor": "#ca8a04",
  "north-shore-channel": "#0d9488", "north-branch": "#3f6212",
  "312-riverrun": "#4f46e5",
};
assert.deepStrictEqual(N.LINE_COLORS, EXPECTED_LINE_COLORS,
  "LINE_COLORS: exactly the 20 roster entries (spec §9 + DECISIONS.md #26 312-riverrun)");
assert.strictEqual(Object.keys(N.LINE_COLORS).length, 20, "LINE_COLORS: exactly 20 entries (14 street + 6 trail)");
assert.ok(!("roosevelt" in N.LINE_COLORS), "LINE_COLORS: roosevelt demoted off the roster");
assert.ok(!("vincennes" in N.LINE_COLORS), "LINE_COLORS: vincennes demoted off the roster");
assert.match(N.FALLBACK_LINE_COLOR, /^#[0-9a-f]{6}$/i, "FALLBACK_LINE_COLOR is a 7-char hex color");

assert.strictEqual(N.lineStyle("milwaukee").color, N.LINE_COLORS.milwaukee, "lineStyle: known line uses LINE_COLORS entry");
assert.strictEqual(N.lineStyle("milwaukee").weight, 6, "lineStyle: weight 6 (spec §1)");
assert.strictEqual(N.lineStyle("milwaukee").opacity, 1, "lineStyle: opacity 1, no dashes/per-segment styling");
assert.strictEqual(N.lineStyle("milwaukee").dashArray, undefined, "lineStyle: main routes never dashed");
assert.strictEqual(N.lineStyle("not-a-real-line").color, N.FALLBACK_LINE_COLOR, "lineStyle: unknown line id falls back");
assert.strictEqual(N.lineStyle("not-a-real-line").weight, 6, "lineStyle: fallback still weight 6");

// ---- darkenColor / trailStyle / trailOutlineStyle (spec §1) ----
assert.strictEqual(N.darkenColor("#1d4ed8", 0), "#1d4ed8", "darkenColor: amount 0 -> unchanged");
assert.strictEqual(N.darkenColor("#ffffff", 1), "#000000", "darkenColor: amount 1 -> black");
assert.strictEqual(N.darkenColor("#c8c8c8", 0.5), "#646464", "darkenColor: halves each channel");
assert.strictEqual(N.darkenColor("not-a-color", 0.5), "not-a-color", "darkenColor: bad input passes through unchanged");

assert.strictEqual(N.trailStyle("lakefront").weight, 11, "trailStyle: weight 11 (spec §1)");
assert.strictEqual(N.trailStyle("lakefront").color, N.LINE_COLORS.lakefront, "trailStyle: uses the line color");
const outline = N.trailOutlineStyle("lakefront");
assert.strictEqual(outline.color, N.darkenColor(N.LINE_COLORS.lakefront, 0.35),
  "trailOutlineStyle: darkened line color (~35%), not white casing (spec §1)");
assert.ok(outline.weight > N.trailStyle("lakefront").weight,
  "trailOutlineStyle: wider than the core stroke so it reads as an outline");

// ---- CONNECTOR_STYLE (spec §1) ----
assert.strictEqual(N.CONNECTOR_STYLE.color, "#94a3b8", "CONNECTOR_STYLE: neutral gray-family color");
assert.strictEqual(N.CONNECTOR_STYLE.weight, 2.5, "CONNECTOR_STYLE: weight 2.5");
assert.strictEqual(N.CONNECTOR_STYLE.opacity, 0.75, "CONNECTOR_STYLE: opacity 0.75");
assert.ok(N.CONNECTOR_STYLE.dashArray, "CONNECTOR_STYLE: dashed");

// ---- qualityBorderStyle (spec §3) ----
assert.strictEqual(N.qualityBorderStyle("protected").color, "#0b6e4f", "qualityBorderStyle: protected color");
assert.strictEqual(N.qualityBorderStyle("protected").dashArray, undefined, "qualityBorderStyle: protected solid");
assert.strictEqual(N.qualityBorderStyle("protected").weight, 13, "qualityBorderStyle: weight 13 (rim around casing)");

assert.strictEqual(N.qualityBorderStyle("paint").color, "#0b6e4f", "qualityBorderStyle: paint shares protected's green");
assert.strictEqual(N.qualityBorderStyle("paint").dashArray, "6,6", "qualityBorderStyle: paint dashed 6,6");

assert.strictEqual(N.qualityBorderStyle("mellow").color, "#7c3aed", "qualityBorderStyle: mellow purple");
assert.strictEqual(N.qualityBorderStyle("mellow").dashArray, undefined, "qualityBorderStyle: mellow solid");

assert.strictEqual(N.qualityBorderStyle("none").color, "#dc2626", "qualityBorderStyle: none red");
assert.strictEqual(N.qualityBorderStyle("none").dashArray, "6,6", "qualityBorderStyle: none dashed 6,6");

assert.strictEqual(N.qualityBorderStyle("offstreet"), null,
  "qualityBorderStyle: offstreet -> no border (trails are off-street, spec §3)");

assert.strictEqual(N.qualityBorderStyle("bogus").color, "#dc2626",
  "qualityBorderStyle: unknown grade falls back to the none (red dashed) treatment");
assert.strictEqual(N.qualityBorderStyle("bogus").dashArray, "6,6", "qualityBorderStyle: unknown grade dashed like none");

// ---- comfort floor: GRADE_RANK / gradeRank / parseFloor / meetsFloor (spec §5) ----
assert.deepStrictEqual(
  N.GRADE_RANK, { none: 0, mellow: 1, paint: 2, protected: 3, offstreet: 4 },
  "GRADE_RANK: none < mellow < paint < protected < offstreet"
);
assert.strictEqual(N.gradeRank("protected"), 3, "gradeRank: known grade");
assert.strictEqual(N.gradeRank("bogus"), -1, "gradeRank: unknown grade ranks below everything");

assert.strictEqual(N.parseFloor(undefined), "any", "parseFloor: missing -> any");
assert.strictEqual(N.parseFloor("bogus"), "any", "parseFloor: garbage -> any");
assert.strictEqual(N.parseFloor("paint"), "paint", "parseFloor: paint recognized");
assert.strictEqual(N.parseFloor("protected"), "protected", "parseFloor: protected recognized");

assert.ok(N.meetsFloor("none", "any"), "meetsFloor: any floor accepts everything");
assert.ok(N.meetsFloor("offstreet", "protected"), "meetsFloor: offstreet clears every floor");
assert.ok(N.meetsFloor("protected", "protected"), "meetsFloor: grade == floor passes");
assert.ok(!N.meetsFloor("paint", "protected"), "meetsFloor: paint below protected floor");
assert.ok(N.meetsFloor("paint", "paint"), "meetsFloor: paint clears paint floor");
assert.ok(!N.meetsFloor("mellow", "paint"), "meetsFloor: mellow below paint floor");
assert.ok(N.meetsFloor("protected", "paint"), "meetsFloor: protected clears paint floor");
assert.ok(!N.meetsFloor("none", "paint"), "meetsFloor: none below paint floor");

assert.strictEqual(N.DRAINED_STYLE.color, N.DRAINED_COLOR, "DRAINED_STYLE: uses DRAINED_COLOR");
assert.strictEqual(N.DRAINED_STYLE.weight, 3, "DRAINED_STYLE: 3px core per spec §5");
assert.strictEqual(N.DRAINED_STYLE.dashArray, undefined, "DRAINED_STYLE: solid, continuous — routes never break");

// ---- qualityMixSegments (spec §7/§8 detail card + roster mini-bar) ----
assert.deepStrictEqual(N.QUALITY_MIX_ORDER, ["protected", "paint", "mellow", "none"],
  "QUALITY_MIX_ORDER: the four bordered grades, excludes offstreet");

const mix = N.qualityMixSegments({ protected: 3, paint: 1, offstreet: 50 });
assert.deepStrictEqual(mix.map(s => s.grade), ["protected", "paint"],
  "qualityMixSegments: offstreet excluded even when present in miles_by_grade");
assert.ok(Math.abs(mix[0].pct - 75) < 1e-9, "qualityMixSegments: pct computed over the 4-grade total only");
assert.ok(Math.abs(mix[1].pct - 25) < 1e-9, "qualityMixSegments: second segment pct");
assert.strictEqual(mix[0].color, N.GRADE_COLORS.protected, "qualityMixSegments: carries the border color");

assert.deepStrictEqual(N.qualityMixSegments({ offstreet: 18 }), [],
  "qualityMixSegments: pure-offstreet (trail) line -> empty bar");
assert.deepStrictEqual(N.qualityMixSegments(null), [], "qualityMixSegments: null input -> []");
assert.deepStrictEqual(N.qualityMixSegments({}), [], "qualityMixSegments: empty input -> []");

const allFour = N.qualityMixSegments({ protected: 1, paint: 1, mellow: 1, none: 1 });
assert.deepStrictEqual(allFour.map(s => s.grade), ["protected", "paint", "mellow", "none"],
  "qualityMixSegments: all four grades in QUALITY_MIX_ORDER");
const totalPct = allFour.reduce((s, x) => s + x.pct, 0);
assert.ok(Math.abs(totalPct - 100) < 1e-6, "qualityMixSegments: pct widths sum to 100");

// ---- buildRosterIndex / splitByRoster / membersOfLine (spec §2/§6) ----
const mainRouteFeatures = [
  { properties: { segment_id: "7", line_id: "milwaukee", line_ids: ["milwaukee"], grade: "protected" } },
  { properties: { segment_id: "8", line_id: "milwaukee", line_ids: ["milwaukee"], grade: "paint" } },
  { properties: { segment_id: "42", line_id: "halsted", line_ids: ["halsted"], grade: "none" } },
  { properties: { segment_id: "osm-trail-lakefront-trail", line_id: "lakefront", grade: "offstreet" } },
  // interlined (shared-track) segment: no real roster overlap today, but the
  // pipeline contract allows line_ids.length >= 2 (spec §6).
  { properties: { segment_id: "99", line_id: "milwaukee", line_ids: ["milwaukee", "damen"], grade: "protected" } },
];
const rosterIdx = N.buildRosterIndex(mainRouteFeatures);
assert.strictEqual(rosterIdx.size, 5, "buildRosterIndex: one entry per member");
assert.deepStrictEqual(rosterIdx.get("7"), { lineIds: ["milwaukee"], lineId: "milwaukee", grade: "protected" },
  "buildRosterIndex: maps segment_id to lineIds + lineId + grade");
assert.deepStrictEqual(rosterIdx.get("42"), { lineIds: ["halsted"], lineId: "halsted", grade: "none" },
  "buildRosterIndex: none-grade member indexed");
assert.deepStrictEqual(rosterIdx.get("osm-trail-lakefront-trail"),
  { lineIds: ["lakefront"], lineId: "lakefront", grade: "offstreet" },
  "buildRosterIndex: falls back to line_id when line_ids is absent");
assert.deepStrictEqual(rosterIdx.get("99").lineIds, ["milwaukee", "damen"],
  "buildRosterIndex: preserves multi-id line_ids for interlined segments");
assert.strictEqual(N.buildRosterIndex(undefined).size, 0,
  "buildRosterIndex: missing features -> empty index");

const networkFeatures = [
  { properties: { segment_id: "7", street: "DEARBORN" } },
  { properties: { segment_id: "42", street: "HALSTED" } },
  { properties: { segment_id: "999", street: "MARQUETTE" } },
];
const split = N.splitByRoster(networkFeatures, rosterIdx);
assert.strictEqual(split.roster.length, 2, "splitByRoster: 2 roster members");
assert.strictEqual(split.local.length, 1, "splitByRoster: 1 local/connector segment");
assert.strictEqual(split.local[0].properties.segment_id, "999",
  "splitByRoster: unmatched segment lands in the connector bucket");

assert.deepStrictEqual(
  N.membersOfLine(networkFeatures, rosterIdx, "milwaukee").map(f => f.properties.segment_id),
  ["7"],
  "membersOfLine: filters features to one line's members"
);
assert.deepStrictEqual(
  N.membersOfLine(networkFeatures, rosterIdx, "no-such-line"), [],
  "membersOfLine: unknown line -> empty"
);
const sharedFeatures = [{ properties: { segment_id: "99", street: "SHARED ST" } }];
assert.deepStrictEqual(
  N.membersOfLine(sharedFeatures, rosterIdx, "damen").map(f => f.properties.segment_id),
  ["99"],
  "membersOfLine: an interlined segment counts as a member of every one of its lines"
);
assert.deepStrictEqual(
  N.membersOfLine(sharedFeatures, rosterIdx, "milwaukee").map(f => f.properties.segment_id),
  ["99"],
  "membersOfLine: same interlined segment also counts for its other line"
);

// ---- linesById ----
const linesMeta = N.linesById([
  { id: "milwaukee", name: "Milwaukee Line", no_data: false },
  { id: "lakefront", name: "Lakefront Trail", no_data: true },
]);
assert.strictEqual(linesMeta.get("milwaukee").name, "Milwaukee Line", "linesById: lookup by id");
assert.strictEqual(linesMeta.get("lakefront").no_data, true, "linesById: no_data preserved");
assert.strictEqual(N.linesById(undefined).size, 0, "linesById: missing lines array -> empty map");

// ---- rosterStreets (corridor labels defer to line labels) ----
const streets = N.rosterStreets(networkFeatures, rosterIdx);
assert.ok(streets.has("DEARBORN"), "rosterStreets: roster member street included");
assert.ok(streets.has("HALSTED"), "rosterStreets: second roster street included");
assert.ok(!streets.has("MARQUETTE"), "rosterStreets: local/connector-only street excluded");

// ---- interlining offset helpers (spec §6) ----

assert.strictEqual(N.isMultiPart([[41.9, -87.6], [41.91, -87.61]]), false,
  "isMultiPart: flat [lat,lng] list is not multi-part");
assert.strictEqual(N.isMultiPart([[[41.9, -87.6], [41.91, -87.61]]]), true,
  "isMultiPart: nested parts array is multi-part");

// A straight north-south segment (constant lng, increasing lat). Offsetting
// it east/west (perpendicular) by a positive amount should move it east
// (increase lng) or west depending on sign, while never touching lat.
const straightNS = [[41.90, -87.65], [41.91, -87.65], [41.92, -87.65]];
const offsetZero = N.offsetPart(straightNS, 0);
assert.deepStrictEqual(offsetZero, straightNS, "offsetPart: zero offset returns the path unchanged (by value)");
assert.notStrictEqual(offsetZero, straightNS, "offsetPart: zero offset still returns a new array, not the same reference");

const offsetPos = N.offsetPart(straightNS, 5);
const offsetNeg = N.offsetPart(straightNS, -5);
straightNS.forEach((pt, i) => {
  assert.ok(Math.abs(offsetPos[i][0] - pt[0]) < 1e-9, "offsetPart: perpendicular offset of a N-S line does not change lat");
  assert.notStrictEqual(offsetPos[i][1], pt[1], "offsetPart: perpendicular offset of a N-S line changes lng");
});
assert.ok(
  Math.sign(offsetPos[1][1] - straightNS[1][1]) === -Math.sign(offsetNeg[1][1] - straightNS[1][1]),
  "offsetPart: positive and negative offsets move to opposite sides"
);
// Roughly symmetric magnitude around the original point.
const dPos = Math.abs(offsetPos[1][1] - straightNS[1][1]);
const dNeg = Math.abs(offsetNeg[1][1] - straightNS[1][1]);
assert.ok(Math.abs(dPos - dNeg) < 1e-9, "offsetPart: +/- offsets of equal magnitude land equidistant from the original");

assert.deepStrictEqual(N.offsetPart([], 5), [], "offsetPart: empty path -> empty path");

// offsetLatLngs dispatches on shape.
const multiPartPath = [straightNS, [[41.80, -87.60], [41.81, -87.60]]];
const offsetMulti = N.offsetLatLngs(multiPartPath, 5);
assert.strictEqual(offsetMulti.length, 2, "offsetLatLngs: multi-part shape preserved");
assert.deepStrictEqual(offsetMulti[0], N.offsetPart(straightNS, 5), "offsetLatLngs: each part individually offset");
const offsetFlat = N.offsetLatLngs(straightNS, 5);
assert.deepStrictEqual(offsetFlat, N.offsetPart(straightNS, 5), "offsetLatLngs: flat shape delegates directly to offsetPart");

// strandOffsets: symmetric around zero, spaced by gapMeters.
assert.deepStrictEqual(N.strandOffsets(1, 2), [0], "strandOffsets: single strand -> no offset");
const two = N.strandOffsets(2, 2);
assert.strictEqual(two.length, 2, "strandOffsets: one offset per strand");
assert.ok(Math.abs(two[0] + two[1]) < 1e-9, "strandOffsets: symmetric around zero");
assert.ok(Math.abs((two[1] - two[0]) - 2) < 1e-9, "strandOffsets: gap of 2 between adjacent strands");
const three = N.strandOffsets(3, 3);
assert.deepStrictEqual(three, [-3, 0, 3], "strandOffsets: middle strand sits at zero for an odd count");
assert.deepStrictEqual(N.strandOffsets(2), [-N.INTERLINE_GAP_METERS / 2, N.INTERLINE_GAP_METERS / 2],
  "strandOffsets: default gap is INTERLINE_GAP_METERS when omitted");

// pathEndpoints
assert.deepStrictEqual(N.pathEndpoints(straightNS), [straightNS[0], straightNS[2]],
  "pathEndpoints: flat path -> first/last vertex");
assert.deepStrictEqual(
  N.pathEndpoints(multiPartPath),
  [multiPartPath[0][0], multiPartPath[1][multiPartPath[1].length - 1]],
  "pathEndpoints: multi-part -> first vertex of first part, last vertex of last part"
);

// ---- planInterlinedRoute: synthetic two-line shared-track fixture (spec §6) ----
// Real data has no shared streets today, so this is the only place the
// interlining render logic gets exercised — a straight shared segment
// carried by two roster lines (e.g. a hypothetical Milwaukee/Damen overlap).
const sharedLatLngs = [[41.90, -87.65], [41.905, -87.65], [41.91, -87.65]];
const colorFor = (id) => ({ milwaukee: "#1d4ed8", damen: "#eab308" }[id] || "#000000");
const plan = N.planInterlinedRoute(sharedLatLngs, ["milwaukee", "damen"], "protected", colorFor);

assert.strictEqual(plan.strands.length, 2, "planInterlinedRoute: one strand per line_id");
assert.strictEqual(plan.strands[0].lineId, "milwaukee", "planInterlinedRoute: strand order matches lineIds order");
assert.strictEqual(plan.strands[1].lineId, "damen", "planInterlinedRoute: second strand");
assert.strictEqual(plan.strands[0].color, "#1d4ed8", "planInterlinedRoute: strand color from colorFor(lineId)");
assert.strictEqual(plan.strands[1].color, "#eab308", "planInterlinedRoute: second strand color");
assert.notDeepStrictEqual(plan.strands[0].latlngs, plan.strands[1].latlngs,
  "planInterlinedRoute: the two strands render as visually distinct (offset) geometry");
assert.deepStrictEqual(plan.strands[0].latlngs, N.offsetLatLngs(sharedLatLngs, N.strandOffsets(2)[0]),
  "planInterlinedRoute: strand geometry matches the offset helper directly");

assert.deepStrictEqual(plan.casing.latlngs, sharedLatLngs,
  "planInterlinedRoute: shared casing uses the original (un-offset) geometry, drawn once");

assert.deepStrictEqual(plan.border, N.qualityBorderStyle("protected"),
  "planInterlinedRoute: shared quality border matches qualityBorderStyle(grade), drawn once");

assert.deepStrictEqual(plan.capsules, [sharedLatLngs[0], sharedLatLngs[2]],
  "planInterlinedRoute: capsule markers sit at the shared run's two endpoints");

// offstreet grade (shouldn't occur for street-line interlining in practice,
// but the plan must stay well-defined) -> no border, matching qualityBorderStyle.
const planOffstreet = N.planInterlinedRoute(sharedLatLngs, ["milwaukee", "damen"], "offstreet", colorFor);
assert.strictEqual(planOffstreet.border, null, "planInterlinedRoute: offstreet grade -> no shared border");

console.log("network-model OK");
