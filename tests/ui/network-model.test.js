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

const grouped2 = N.groupByCorridor([
  { properties: { street: "", segment_id: "4" } },
  { properties: { street: null, segment_id: "5" } },
]);
assert.strictEqual(grouped2.size, 1, "groupByCorridor: empty string and null share (unnamed) bucket");
assert.strictEqual(grouped2.get("(unnamed)").length, 2, "groupByCorridor: both features bucketed");

// ---- toLatLngs / flattenCoords / bboxes ----
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

const bbox = N.getPaddedBBox(singleLine, 0.001);
assert.deepStrictEqual(
  bbox,
  [[41.90 - 0.001, -87.65 - 0.001], [41.91 + 0.001, -87.64 + 0.001]],
  "getPaddedBBox: pads min/max lat/lng"
);

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
assert.strictEqual(unioned[1][1], Math.max(bboxA[1][1], bboxB[1][1]), "unionBBox: max lng across features");

// ---- ZOOM / DEFAULT_OVERLAYS / parseOverlays / serializeOverlays ----
assert.deepStrictEqual(
  N.ZOOM, { interchangeNodes: 11, lineLabels: 11, corridorLabels: 13 },
  "ZOOM: interchange/line-label thresholds at 11, corridor/orientation-label threshold at 13"
);
assert.deepStrictEqual(
  N.DEFAULT_OVERLAYS, ["trails", "main", "nodes"],
  "DEFAULT_OVERLAYS: trails+main+nodes on by default"
);
assert.deepStrictEqual([...N.parseOverlays(null)], ["trails", "main", "nodes"], "parseOverlays: null -> defaults");
assert.strictEqual(N.parseOverlays("").size, 0, "parseOverlays: explicit empty string -> none");
assert.deepStrictEqual(
  [...N.parseOverlays("quality,main")], ["quality", "main"],
  "parseOverlays: legacy ids (the retired 'quality' toggle) still parse — network.js just never checks them"
);
assert.strictEqual(N.serializeOverlays(new Set(["main", "nodes"])), "main,nodes", "serializeOverlays: joins with commas");
assert.strictEqual(N.serializeOverlays(new Set()), "none", "serializeOverlays: empty set -> 'none' sentinel");
assert.strictEqual(N.parseOverlays("none").size, 0, "parseOverlays: 'none' sentinel -> empty set");

// ---- LINE_COLORS / lineStyle ----
const EXPECTED_LINE_COLORS = {
  milwaukee: "#1d4ed8", elston: "#ea580c", halsted: "#dc2626", damen: "#eab308",
  kedzie: "#7c3aed", california: "#db2777", clark: "#0891b2", "state-indiana": "#4d7c0f",
  "mlk-drive": "#92400e", "jackson-washington": "#6b21a8", lawrence: "#881337",
  marquette: "#1e40af", lake: "#a16207", "83rd": "#15803d",
  lakefront: "#0369a1", bloomingdale: "#16a34a", "major-taylor": "#ca8a04",
  "north-shore-channel": "#0d9488", "north-branch": "#3f6212",
  "312-riverrun": "#4f46e5",
  "green-bay": "#a21caf",
};
assert.deepStrictEqual(N.LINE_COLORS, EXPECTED_LINE_COLORS, "LINE_COLORS: exactly the 21 roster entries");
assert.strictEqual(N.lineStyle("milwaukee").color, N.LINE_COLORS.milwaukee, "lineStyle: known line uses LINE_COLORS entry");
assert.strictEqual(N.lineStyle("not-a-real-line").color, N.FALLBACK_LINE_COLOR, "lineStyle: unknown line id falls back");

// ---- darkenColor / lightenColor / trail styles ----
assert.strictEqual(N.darkenColor("#ffffff", 1), "#000000", "darkenColor: amount 1 -> black");
assert.strictEqual(N.darkenColor("not-a-color", 0.5), "not-a-color", "darkenColor: bad input passes through");
assert.strictEqual(N.lightenColor("#000000", 1), "#ffffff", "lightenColor: amount 1 -> white");
assert.strictEqual(N.trailStyle("lakefront").color, N.LINE_COLORS.lakefront, "trailStyle: uses the line color");
assert.strictEqual(
  N.trailOutlineStyle("lakefront").color, N.darkenColor(N.LINE_COLORS.lakefront, 0.35),
  "trailOutlineStyle: darkened line color"
);

// ---- connectorStyle (unchanged from v2 §12) ----
assert.strictEqual(N.CONNECTOR_STYLE.color, "#94a3b8", "CONNECTOR_STYLE: neutral gray-family color");
assert.strictEqual(N.connectorStyle("protected").color, "#4d8873", "connectorStyle: protected muted green");
assert.strictEqual(N.connectorStyle("protected").dashArray, null, "connectorStyle: protected solid");
assert.strictEqual(N.connectorStyle("mellow").color, "#9a8fc9", "connectorStyle: mellow muted lavender");
assert.strictEqual(N.connectorStyle("mellow").dashArray, "4,5", "connectorStyle: mellow dashed — the connector dash survives the roster dash rule (v3 §10)");
assert.deepStrictEqual(N.connectorStyle("bogus"), N.connectorStyle("none"), "connectorStyle: unknown grade -> none treatment");

// ---- comfort floor ----
assert.deepStrictEqual(
  N.GRADE_RANK, { none: 0, mellow: 1, paint: 2, protected: 3, offstreet: 4 },
  "GRADE_RANK: none < mellow < paint < protected < offstreet — mellow stays distinct internally (v3 §6)"
);
assert.strictEqual(N.parseFloor("bogus"), "any", "parseFloor: garbage -> any");
assert.ok(N.meetsFloor("offstreet", "protected"), "meetsFloor: offstreet clears every floor");
assert.ok(!N.meetsFloor("mellow", "paint"), "meetsFloor: mellow below paint floor");
assert.ok(!N.meetsFloor("none", "paint"), "meetsFloor: none below paint floor");
assert.match(N.DRAINED_COLOR, /^#[0-9a-f]{6}$/i, "DRAINED_COLOR: hex color (drained = full silhouette at drainedOpacity, v3 §4.4)");

// ---- qualityMixSegments (legacy helper, still exported) ----
const mix = N.qualityMixSegments({ protected: 3, paint: 1, offstreet: 50 });
assert.deepStrictEqual(mix.map((s) => s.grade), ["protected", "paint"], "qualityMixSegments: offstreet excluded");
assert.strictEqual(mix[0].color, N.GRADE_COLORS.protected, "qualityMixSegments: carries GRADE_COLORS");

// ---- buildRosterIndex / splitByRoster / membersOfLine ----
const mainRouteFeatures = [
  { properties: { segment_id: "7", line_id: "milwaukee", line_ids: ["milwaukee"], grade: "protected" } },
  { properties: { segment_id: "42", line_id: "halsted", line_ids: ["halsted"], grade: "none" } },
  { properties: { segment_id: "99", line_id: "milwaukee", line_ids: ["milwaukee", "damen"], grade: "protected" } },
];
const rosterIdx = N.buildRosterIndex(mainRouteFeatures);
assert.deepStrictEqual(rosterIdx.get("7"), { lineIds: ["milwaukee"], lineId: "milwaukee", grade: "protected" },
  "buildRosterIndex: maps segment_id to lineIds + lineId + grade");
assert.deepStrictEqual(rosterIdx.get("99").lineIds, ["milwaukee", "damen"],
  "buildRosterIndex: preserves multi-id line_ids for interlined segments");

const networkFeatures = [
  { properties: { segment_id: "7", street: "DEARBORN" } },
  { properties: { segment_id: "999", street: "MARQUETTE" } },
];
const split = N.splitByRoster(networkFeatures, rosterIdx);
assert.strictEqual(split.roster.length, 1, "splitByRoster: roster members");
assert.strictEqual(split.local[0].properties.segment_id, "999", "splitByRoster: unmatched -> connector bucket");
assert.deepStrictEqual(
  N.membersOfLine([{ properties: { segment_id: "99" } }], rosterIdx, "damen").map((f) => f.properties.segment_id),
  ["99"],
  "membersOfLine: an interlined segment counts for every one of its lines"
);

// ---- interlining offset helpers ----
const straightNS = [[41.90, -87.65], [41.91, -87.65], [41.92, -87.65]];
const offsetPos = N.offsetPart(straightNS, 5);
const offsetNeg = N.offsetPart(straightNS, -5);
straightNS.forEach((pt, i) => {
  assert.ok(Math.abs(offsetPos[i][0] - pt[0]) < 1e-9, "offsetPart: N-S offset does not change lat");
});
assert.ok(
  Math.sign(offsetPos[1][1] - straightNS[1][1]) === -Math.sign(offsetNeg[1][1] - straightNS[1][1]),
  "offsetPart: +/- offsets move to opposite sides"
);
assert.deepStrictEqual(N.strandOffsets(3, 3), [-3, 0, 3], "strandOffsets: middle strand at zero for odd count");
assert.deepStrictEqual(N.pathEndpoints(straightNS), [straightNS[0], straightNS[2]], "pathEndpoints: first/last vertex");

// planInterlinedRoute: strands render solid hue always; the shared casing
// carries the structural treatment via the trunk grade (v3 §7) — the v2
// per-plan quality border is gone.
const colorFor = (id) => ({ milwaukee: "#1d4ed8", damen: "#eab308" }[id] || "#000000");
const plan = N.planInterlinedRoute(straightNS, ["milwaukee", "damen"], "protected", colorFor);
assert.strictEqual(plan.strands.length, 2, "planInterlinedRoute: one strand per line_id");
assert.strictEqual(plan.strands[0].color, "#1d4ed8", "planInterlinedRoute: strand color from colorFor");
assert.deepStrictEqual(plan.casing.latlngs, straightNS, "planInterlinedRoute: shared casing on un-offset geometry");
assert.strictEqual(plan.grade, "protected", "planInterlinedRoute: carries the trunk grade for the casing treatment");
assert.strictEqual(plan.border, undefined, "planInterlinedRoute: no border — quality borders are retired (v3 §10)");
assert.deepStrictEqual(plan.capsules, [straightNS[0], straightNS[2]], "planInterlinedRoute: capsules at run ends");

// ---- simplifyPart / schematicLatLngs (connectors still use RDP-40) ----
const wobbly = [
  [41.90, -87.65],
  [41.91, -87.65009],
  [41.92, -87.64991],
  [41.93, -87.65005],
  [41.94, -87.65],
];
assert.deepStrictEqual(
  N.simplifyPart(wobbly, 40),
  [[41.90, -87.65], [41.94, -87.65]],
  "simplifyPart: sub-tolerance wobble collapses to endpoints"
);
const wobblyGeom = { type: "LineString", coordinates: wobbly.map(([lat, lng]) => [lng, lat]) };
assert.deepStrictEqual(
  N.schematicLatLngs(wobblyGeom),
  N.simplifyLatLngs(N.toLatLngs(wobblyGeom), N.SIMPLIFY_TOLERANCE_METERS),
  "schematicLatLngs: toLatLngs + simplify at the default tolerance"
);

// ---- zoomWeightFactor ----
assert.strictEqual(N.zoomWeightFactor(11), 0.6, "zoomWeightFactor: 0.6 at the citywide fit");
assert.strictEqual(N.zoomWeightFactor(13), 1, "zoomWeightFactor: full weight from z13");

// ---- chainPlan / crossStreetGaps (survive as pure helpers) ----
const partA = [[41.90, -87.65], [41.91, -87.65]];
const partB = [[41.93, -87.65], [41.92, -87.65]]; // reversed
const partC = [[41.94, -87.65], [41.95, -87.65]];
const planABC = N.chainPlan([partC, partA, partB]);
assert.strictEqual(planABC.gaps.length, 2, "chainPlan: two holes -> two gaps");
const termKeys = planABC.termini.map((p) => p.join(",")).sort();
assert.deepStrictEqual(termKeys, ["41.9,-87.65", "41.95,-87.65"], "chainPlan: termini are the outermost endpoints");

const streetWest = [[[41.90, -87.66], [41.94, -87.66]]];
const eastWest = [[[41.90, -87.66], [41.90, -87.64]]];
const northSouth = [[[41.88, -87.65], [41.92, -87.65]]];
assert.deepStrictEqual(N.crossStreetGaps([northSouth, eastWest]), [], "crossStreetGaps: crossing chains need no feeder");
assert.strictEqual(N.crossStreetGaps([streetWest, [[[41.88, -87.65], [41.92, -87.65]]]]).length, 1,
  "crossStreetGaps: one feeder per parallel pair");

/* ================================================================
 * Schematic spine pipeline (spec 2026-07-15, §12 fixture list)
 * ================================================================ */

const M_LAT = 111320;
const M_LNG = M_LAT * Math.cos((41.88 * Math.PI) / 180);
// Build a meter-space XY part from [x, y] meter offsets around the origin.
const xyPart = (pairs, extra) => ({
  pts: pairs.map(([x, y]) => [x, y]),
  lenM: pairs.reduce((s, p, i) => (i === 0 ? 0 : s + Math.hypot(p[0] - pairs[i - 1][0], p[1] - pairs[i - 1][1])), 0),
  grade: "paint",
  ...(extra || {}),
});
// Convert meter XY to [lat, lng] for buildSchematicNetwork-level fixtures.
const xyToLL = ([x, y]) => [y / M_LAT, x / M_LNG];

// -- SCHEMATIC constants: names the tests below reference.
assert.deepStrictEqual(N.SCHEMATIC.AXES_DEG, [0, 45, 60, 90, 120, 135], "SCHEMATIC: six-axis family");
["snapToleranceDeg", "minBendDeg", "cornerToleranceMeters", "maxDisplacementMeters",
  "foldbackFraction", "pinMergeGridMeters", "pinAttractMeters", "terminusPairMeters",
  "footSnapMeters", "coupletMaxMeters", "minStretchMeters", "minStripePx", "minRailPx",
].forEach((k) => assert.ok(Number.isFinite(N.SCHEMATIC[k]), `SCHEMATIC.${k} is a number`));
assert.strictEqual(N.SCHEMATIC.EXPLICIT_MERGES[0].id, "nw-terminus", "SCHEMATIC: the NW-terminus explicit merge ships");

// -- QUALITY_LEVELS / displayGrade: the owner's four levels.
assert.deepStrictEqual(N.QUALITY_LEVELS, ["offstreet", "protected", "paint", "nothing"], "QUALITY_LEVELS: four display levels");
assert.strictEqual(N.displayGrade("mellow"), "paint", "displayGrade: mellow folds into paint for display");
assert.strictEqual(N.displayGrade("none"), "nothing", "displayGrade: grade-none displays as nothing");
assert.strictEqual(N.displayGrade("bogus"), "nothing", "displayGrade: unknown grades read as nothing, loud not silent");

// -- Fixture 1: jittery street -> one 90° (north-south) run.
{
  const jitter = [];
  for (let i = 0; i <= 40; i++) jitter.push([(i % 2) * 18 - 9, i * 100]); // 4 km north, ±9 m wobble
  const spine = N.buildLineSpine([xyPart(jitter)], {});
  const schem = N.schematizeSpine(spine, [], { kind: "street" });
  assert.strictEqual(schem.xy.length, 2, "fixture 1: jittery street collapses to one run (two vertices)");
  const brg = Math.atan2(schem.xy[1][1] - schem.xy[0][1], schem.xy[1][0] - schem.xy[0][0]) * 180 / Math.PI;
  assert.ok(Math.abs(brg - 90) < 0.01, "fixture 1: the run sits exactly on the 90° axis");
}

// -- Fixture 2: 8°-off bearing snaps to its axis; 25°-off does not.
{
  const mk = (deg) => [{
    m0: 0, m1: 1000, len: 1000,
    disp: [Math.cos(deg * Math.PI / 180) * 1000, Math.sin(deg * Math.PI / 180) * 1000],
  }];
  const snapped = N.snapRuns(mk(98), { kind: "street" });
  assert.strictEqual(snapped[0].bearing, 90, "fixture 2: 8° off the 90° axis snaps (within snapToleranceDeg)");
  const rounded = N.snapRuns(mk(25), { kind: "street" });
  assert.strictEqual(rounded[0].bearing, 25, "fixture 2: 25° is outside every axis tolerance — rounds to residualRoundDeg");
}

// -- Fixture 3: closure exactness < 1e-6 m.
{
  const runs = N.snapRuns([
    { m0: 0, m1: 1000, len: 1000, disp: [0, 1000] },
    { m0: 1000, m1: 2000, len: 1000, disp: [995, 40] },
  ], { kind: "street" });
  const target = [1030, 1080];
  const t = N.closeRunLengths(runs, target, null, {});
  assert.ok(t, "fixture 3: solvable system");
  let x = 0, y = 0;
  runs.forEach((r, i) => {
    x += Math.cos(r.bearing * Math.PI / 180) * t[i];
    y += Math.sin(r.bearing * Math.PI / 180) * t[i];
  });
  assert.ok(Math.hypot(x - target[0], y - target[1]) < 1e-6, "fixture 3: closure error under 1e-6 m");
}

// -- Fixtures 4 + 13: pin pass-through, and the collinear jog when the pin
// displacement exceeds tiltMaxDeg.
{
  const straightN = [];
  for (let i = 0; i <= 30; i++) straightN.push([0, i * 100]); // 3 km due north
  const spine = N.buildLineSpine([xyPart(straightN)], {});
  // Mid pin displaced 60 m east: within tiltMaxDeg of the run for each
  // 1.5 km half (atan(60/1500) ≈ 2.3°) -> both halves tilt, both pass
  // through the pin exactly.
  const schem = N.schematizeSpine(spine, [{ m: 1500, target: [60, 1500] }], { kind: "street" });
  const hit = schem.xy.some((p) => Math.hypot(p[0] - 60, p[1] - 1500) < 1e-6);
  assert.ok(hit, "fixture 4: the schematic passes exactly through the interchange pin");
  // End pin displaced 300 m east over a 2 km section (8.5° > tiltMaxDeg):
  // the jog machinery fires — end still exact, and some interior bend ≥ 30°.
  const spine2 = N.buildLineSpine([xyPart(straightN.slice(0, 21))], {});
  const schem2 = N.schematizeSpine(spine2, [{ end: "end", target: [300, 2000] }], { kind: "street" });
  const last = schem2.xy[schem2.xy.length - 1];
  assert.ok(Math.hypot(last[0] - 300, last[1] - 2000) < 1e-6, "fixture 13: jogged section still ends exactly on the pin");
  assert.ok(schem2.xy.length >= 4, "fixture 13: collinear + off-axis pin inserts a jog (extra vertices)");
}

// -- Fixture 5: measure conservation — adjacent slices share their boundary
// vertex exactly (stretch boundaries meet, guaranteed by construction).
{
  const path = [];
  for (let i = 0; i <= 20; i++) path.push([i * 100, i * 100 * 0.2]);
  const spine = N.buildLineSpine([xyPart(path)], {});
  const schem = N.schematizeSpine(spine, [], { kind: "street" });
  const sliceable = { xy: schem.xy, m: schem.m };
  const endM = spine.origM[spine.origM.length - 1];
  const a = N.sliceSpineByMeasure(sliceable, 0, endM * 0.4);
  const b = N.sliceSpineByMeasure(sliceable, endM * 0.4, endM);
  assert.deepStrictEqual(a[a.length - 1], b[0], "fixture 5: adjacent slices share the boundary vertex exactly");
}

// -- Fixture 6: displacement guard — a 600 m-deep mid-line excursion whose
// legs are shorter than minRunMeters gets absorbed into the straight run;
// the guard must notice the surveyed points left > 250 m behind, split at
// the deepest one, and pull the schematic back through it.
{
  const arc = [];
  for (let i = 0; i <= 20; i++) arc.push([0, i * 100]);         // 2 km north
  for (let i = 1; i <= 6; i++) arc.push([i * 100, 2000]);       // 600 m east
  for (let i = 1; i <= 4; i++) arc.push([600, 2000 + i * 100]); // 400 m north
  for (let i = 1; i <= 6; i++) arc.push([600 - i * 100, 2400]); // 600 m back west
  for (let i = 1; i <= 20; i++) arc.push([0, 2400 + i * 100]);  // 2 km north
  const spine = N.buildLineSpine([xyPart(arc)], {});
  const schem = N.schematizeSpine(spine, [], { kind: "street" });
  assert.ok(schem.xy.length > 2, "fixture 6: the guard split the straightened-over excursion");
  // The deepest surveyed point became a split pin — it lies ON the schematic.
  const deepest = [600, 2200];
  const onSchem = schem.xy.some((p) => Math.hypot(p[0] - deepest[0], p[1] - deepest[1]) < 150);
  const worst = arc.reduce((w, p) => {
    let best = Infinity;
    for (let i = 0; i < schem.xy.length - 1; i++) {
      const [ax, ay] = schem.xy[i], [bx, by] = schem.xy[i + 1];
      const dx = bx - ax, dy = by - ay;
      const lenSq = dx * dx + dy * dy;
      let t = lenSq === 0 ? 0 : ((p[0] - ax) * dx + (p[1] - ay) * dy) / lenSq;
      t = Math.max(0, Math.min(1, t));
      best = Math.min(best, Math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy)));
    }
    return Math.max(w, best);
  }, 0);
  assert.ok(onSchem || worst <= N.SCHEMATIC.maxDisplacementMeters + 60,
    `fixture 6: the schematic returns through the excursion (worst ${Math.round(worst)} m)`);
  assert.ok(worst < 600 - 100,
    `fixture 6: the guard materially reduced the excursion's displacement (worst ${Math.round(worst)} m of 600)`);
}

// -- Fixture 7: a 6 km bridged range never triggers a guard split.
{
  const south = xyPart([[0, 0], [0, 2000]]);
  const north = xyPart([[0, 8000], [0, 10000]]);
  const spine = N.buildLineSpine([south, north], {});
  assert.strictEqual(spine.bridged.length, 1, "fixture 7: one bridge");
  assert.ok(Math.abs((spine.bridged[0].m1 - spine.bridged[0].m0) - 6000) < 1,
    "fixture 7: bridge advances measure by the chord (v3 §2.1)");
  const schem = N.schematizeSpine(spine, [], { kind: "street" });
  assert.strictEqual(schem.xy.length, 2, "fixture 7: the bridged spine stays one clean run — no guard split inside a declared invention");
  for (let i = 1; i < schem.m.length; i++) assert.ok(schem.m[i] >= schem.m[i - 1], "fixture 7: measure map monotone");
}

// -- Fixture 8: couplet collapse at Jackson–Washington-like parameters;
// no collapse at 900 m separation (> coupletMaxMeters).
{
  const west = [];
  const east = [];
  for (let i = 0; i <= 30; i++) {
    west.push([i * 100, 0]);
    east.push([i * 100, 500]);
  }
  const byStreet = new Map([
    ["JACKSON", [xyPart(west, { street: "JACKSON", grade: "protected" })]],
    ["WASHINGTON", [xyPart(east, { street: "WASHINGTON", grade: "paint" })]],
  ]);
  const collapsed = N.collapseCouplets(byStreet, {});
  assert.strictEqual(collapsed.pairs.length, 1, "fixture 8: a 500 m parallel pair collapses");
  assert.strictEqual(collapsed.donors.length, 1, "fixture 8: donor parts survive as grade overlays");
  const midY = collapsed.parts[0].pts[15][1];
  assert.ok(Math.abs(midY - 250) < 1, "fixture 8: the centerline sits halfway between the pair");

  const farEast = east.map(([x]) => [x, 900]);
  const byStreetFar = new Map([
    ["A", [xyPart(west, { street: "A" })]],
    ["B", [xyPart(farEast, { street: "B" })]],
  ]);
  const notCollapsed = N.collapseCouplets(byStreetFar, {});
  assert.strictEqual(notCollapsed.pairs.length, 0, "fixture 8: a 900 m-apart pair does NOT collapse");
}

// -- Fixture 18: better-grade couplet — the collapsed corridor passes a
// protected floor when either street does.
{
  const base = xyPart([[0, 0], [0, 3000]], { grade: "paint" });
  const spine = N.buildLineSpine([base], {});
  const graded = N.gradeStretches(spine, [{ m0: 0, m1: 3000, grade: "protected" }], {});
  assert.strictEqual(graded.stretches.length, 1, "fixture 18: one merged stretch");
  assert.strictEqual(graded.stretches[0].grade, "protected",
    "fixture 18: overlay upgrades to the BETTER grade of the pair (v3 §6)");
  assert.ok(N.meetsFloor(graded.stretches[0].grade, "protected"), "fixture 18: collapsed corridor clears floor=protected");
}

// -- Fixtures 9/10 (integration): terminus merging via buildSchematicNetwork.
{
  const mkLine = (id, pts, grade) => ({
    id, source: "bike_routes",
    parts: [{ latlngs: pts.map(xyToLL), grade: grade || "paint", street: id.toUpperCase() }],
  });
  // Two lines whose south termini sit 250 m apart (< terminusPairMeters):
  // they must merge to one shared endpoint. A third line 4 km away with a
  // terminus 360 m from anything must NOT merge.
  const lines = [
    mkLine("a", [[0, 0], [0, 5000]]),
    mkLine("b", [[250, 0], [250, -5000]]),
    mkLine("c", [[4000, 360], [4000, 5360]]),
  ];
  const net = N.buildSchematicNetwork({
    lines: lines.map((l) => ({ id: l.id, source: l.source })),
    partsByLine: Object.fromEntries(lines.map((l) => [l.id, l.parts])),
    trunks: [], nodes: [],
  });
  const aEnds = [net.spines.get("a").latlngs[0], net.spines.get("a").latlngs.at(-1)].map((p) => p.join(","));
  const bEnds = [net.spines.get("b").latlngs[0], net.spines.get("b").latlngs.at(-1)].map((p) => p.join(","));
  const shared = aEnds.some((e) => bEnds.includes(e));
  assert.ok(shared, "fixture 9: termini 250 m apart merge to one shared pin (terminusPairMeters)");
  const cEnds = [net.spines.get("c").latlngs[0], net.spines.get("c").latlngs.at(-1)].map((p) => p.join(","));
  assert.ok(!cEnds.some((e) => aEnds.includes(e) || bEnds.includes(e)),
    "fixture 9: a distant line's termini stay unmerged");
}
{
  // Fixture 10: a terminus 200 m from another line's mid-spine snaps to
  // the perpendicular foot point (footSnapMeters) — both lines share it.
  const mkLine = (id, pts) => ({
    id, source: "bike_routes",
    parts: [{ latlngs: pts.map(xyToLL), grade: "paint", street: id.toUpperCase() }],
  });
  const lines = [
    mkLine("trunkline", [[0, -6000], [0, 6000]]),
    mkLine("feeder", [[200, 0], [6200, 0]]),
  ];
  const net = N.buildSchematicNetwork({
    lines: lines.map((l) => ({ id: l.id, source: l.source })),
    partsByLine: Object.fromEntries(lines.map((l) => [l.id, l.parts])),
    trunks: [], nodes: [],
  });
  const feeder = net.spines.get("feeder");
  const trunkline = net.spines.get("trunkline");
  const feederEnds = [feeder.latlngs[0], feeder.latlngs.at(-1)];
  const onTrunk = feederEnds.some((e) => {
    const hit = N.snapPointToPath(e, trunkline.latlngs);
    return hit && hit.dist < 1;
  });
  assert.ok(onTrunk, "fixture 10: the feeder's near terminus foot-snaps onto the other line's spine");
}

// -- Fixture 11: shared-trunk geometry byte-identical across owners AFTER
// full per-line schematization (two-owner fixture).
{
  const mkParts = (pts, street) => [{ latlngs: pts.map(xyToLL), grade: "paint", street }];
  const shared = [[0, 0], [0, 2500]];
  const net = N.buildSchematicNetwork({
    lines: [{ id: "x", source: "bike_routes" }, { id: "y", source: "bike_routes" }],
    partsByLine: {
      x: mkParts([[0, 2500], [0, 8000]], "X ST"),
      y: mkParts([[80, 2540], [4000, 6500]], "Y ST"),
    },
    trunks: [{ key: "x|y", lineIds: ["x", "y"], parts: [{ latlngs: shared.map(xyToLL), grade: "protected" }] }],
    nodes: [],
  });
  const trunk = net.trunks.get("x|y");
  ["x", "y"].forEach((id) => {
    const s = net.spines.get(id);
    const r = s.trunkRanges.find((t) => t.key === "x|y");
    assert.ok(r, `fixture 11: line ${id} carries its trunk range`);
    const slice = N.sliceSpineByMeasure(s, r.m0, r.m1).map((p) => p.map((v) => v.toFixed(7)));
    const canon = trunk.latlngs.map((p) => p.map((v) => v.toFixed(7)));
    const same = JSON.stringify(slice) === JSON.stringify(canon)
      || JSON.stringify(slice.slice().reverse()) === JSON.stringify(canon);
    assert.ok(same, `fixture 11: trunk geometry byte-identical for owner ${id} after full closure`);
  });
}

// -- Fixture 12: measure-map round-trip with a bridge (chord convention).
{
  const spine = N.buildLineSpine([
    xyPart([[0, 0], [0, 1000]], { grade: "protected" }),
    xyPart([[0, 1500], [0, 2500]], { grade: "none" }),
  ], {});
  for (let i = 1; i < spine.origM.length; i++) {
    assert.ok(spine.origM[i] >= spine.origM[i - 1], "fixture 12: origM monotone through the bridge");
  }
  assert.ok(Math.abs(spine.origM[spine.origM.length - 1] - 2500) < 1,
    "fixture 12: total measure = surveyed + chord");
  const bridge = spine.stretches.find((s) => s.bridged);
  assert.ok(bridge && Math.abs(bridge.m0 - 1000) < 1 && Math.abs(bridge.m1 - 1500) < 1,
    "fixture 12: the bridge occupies exactly its chord range");
}

// -- Fixture 14: fold-back guard — a short section pinned both ends with a
// large lateral displacement never self-folds; ends stay exact.
{
  const pts = [];
  for (let i = 0; i <= 4; i++) pts.push([0, i * 100]); // 400 m north
  const spine = N.buildLineSpine([xyPart(pts)], {});
  const schem = N.schematizeSpine(spine, [{ end: "end", target: [250, 400] }], { kind: "street" });
  const last = schem.xy[schem.xy.length - 1];
  assert.ok(Math.hypot(last[0] - 250, last[1] - 400) < 1e-6, "fixture 14: end pin hit exactly");
  let travel = 0;
  for (let i = 1; i < schem.xy.length; i++) {
    travel += Math.hypot(schem.xy[i][0] - schem.xy[i - 1][0], schem.xy[i][1] - schem.xy[i - 1][1]);
  }
  const direct = Math.hypot(250, 400);
  assert.ok(travel < direct * 2.5, "fixture 14: no self-folding detour (path stays near the direct span)");
}

// -- Fixture 15: min-bend — a 45° run meeting a 58° run emits one run or a
// bend >= minBendDeg, never a 15° elbow.
{
  const runs = N.snapRuns([
    { m0: 0, m1: 2000, len: 2000, disp: [Math.cos(Math.PI / 4) * 2000, Math.sin(Math.PI / 4) * 2000] },
    { m0: 2000, m1: 3500, len: 1500, disp: [Math.cos(58 * Math.PI / 180) * 1500, Math.sin(58 * Math.PI / 180) * 1500] },
  ], { kind: "street" });
  if (runs.length > 1) {
    for (let i = 1; i < runs.length; i++) {
      const bend = Math.abs(runs[i].bearing - runs[i - 1].bearing);
      const bendNorm = Math.min(bend % 360, 360 - (bend % 360));
      assert.ok(bendNorm === 0 || bendNorm >= N.SCHEMATIC.minBendDeg,
        `fixture 15: no soft corner (got ${bendNorm}°)`);
    }
  } else {
    assert.strictEqual(runs.length, 1, "fixture 15: merged into a single run");
  }
}

// -- Fixture 16: fillPlan clamp / coarsening / band.
{
  const full = N.fillPlan("nothing", 6);
  assert.ok(full.coreWidth > 0, "fillPlan: hollow core at full weight");
  assert.ok((6 - full.coreWidth) / 2 >= N.SCHEMATIC.minRailPx, "fillPlan: rails keep >= minRailPx");
  const tiny = N.fillPlan("nothing", 2.5);
  assert.ok(tiny.hollowFallback, "fillPlan: below the clamp the stretch degrades to the opacity fallback");
  assert.strictEqual(tiny.coreWidth, 0, "fillPlan: no core in fallback mode");
  const paintFull = N.fillPlan("paint", 6);
  assert.ok(paintFull.stripeWidth >= N.SCHEMATIC.minStripePx, "fillPlan: paint stripe at full weight");
  const paintTiny = N.fillPlan("paint", 3.6);
  assert.strictEqual(paintTiny.stripeWidth, 0, "fillPlan: stripe coarsens away below minStripePx — paint renders solid");
  assert.ok(N.fillPlan("offstreet", 6).band, "fillPlan: offstreet takes the darkened band");
  assert.ok(!N.fillPlan("protected", 6).band, "fillPlan: protected is plain white-cased hue");
}

// -- Fixture 17: nothing-chip mileage comes from PRE-absorption extents —
// unaffected by minStretchMeters display tuning.
{
  const spine = N.buildLineSpine([
    xyPart([[0, 0], [0, 2000]], { grade: "paint" }),
    xyPart([[0, 2050], [0, 2130]], { grade: "none" }),   // 80 m none between two 50 m bridges
    xyPart([[0, 2180], [0, 4000]], { grade: "paint" }),
  ], {});
  const graded = N.gradeStretches(spine, [], {});
  const displayNothing = graded.stretches.filter((s) => N.displayGrade(s.grade) === "nothing");
  assert.strictEqual(displayNothing.length, 0, "fixture 17: sub-250 m confetti absorbed from the DISPLAY stretches");
  const chipM = N.nothingMeters(graded.preAbsorption);
  assert.ok(Math.abs(chipM - 180) < 2,
    `fixture 17: the chip still counts the real 180 m of nothing (got ${Math.round(chipM)})`);
}

// -- levelMixSegments: one denominator, four levels, mellow folded in.
{
  const segs = N.levelMixSegments([[
    { m0: 0, m1: 1000, grade: "protected" },
    { m0: 1000, m1: 1500, grade: "mellow" },
    { m0: 1500, m1: 2000, grade: "none" },
  ]]);
  assert.deepStrictEqual(segs.map((s) => s.level), ["protected", "paint", "nothing"],
    "levelMixSegments: levels in QUALITY_LEVELS order, mellow displayed as paint");
  assert.ok(Math.abs(segs.reduce((s, x) => s + x.pct, 0) - 100) < 1e-6, "levelMixSegments: widths sum to 100");
  assert.strictEqual(segs[0].color, N.LEVEL_COLORS.protected, "levelMixSegments: carries LEVEL_COLORS");
  assert.deepStrictEqual(N.levelMixSegments([[]]), [], "levelMixSegments: empty input -> []");
}

// -- tracePath: parallel-bank duplicates drop; the diameter path survives.
{
  const bankA = xyPart(Array.from({ length: 41 }, (_, i) => [i * 100, 0]));
  const bankB = xyPart(Array.from({ length: 41 }, (_, i) => [i * 100, 60]), { grade: "paint" });
  const link1 = xyPart([[0, 0], [0, 60]]);
  const link2 = xyPart([[4000, 0], [4000, 60]]);
  const traced = N.tracePath([bankA, bankB, link1, link2], {});
  const total = traced.reduce((s, p) => s + p.lenM, 0);
  assert.ok(total < 4300, `tracePath: one bank + at most the short links survive (got ${Math.round(total)} m, not ~8 km)`);
}

// -- tracePath: two banks joined at only ONE end (the North Shore Channel
// shape) — the "diameter" walks up bank A and back down bank B; the
// sustained-re-coverage rule must truncate the doubled bank.
{
  const bankA = xyPart(Array.from({ length: 41 }, (_, i) => [i * 100, 0]));
  const bankB = xyPart(Array.from({ length: 41 }, (_, i) => [i * 100, 160]), { grade: "paint" });
  const northLink = xyPart([[4000, 0], [4000, 160]]);
  const traced = N.tracePath([bankA, bankB, northLink], {});
  const total = traced.reduce((s, p) => s + p.lenM, 0);
  assert.ok(total < 5000,
    `tracePath: the doubled-back bank truncates — one bank + link, not ~8.2 km (got ${Math.round(total)} m)`);
}

console.log("network-model OK");
