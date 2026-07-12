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

console.log("network-model OK");
