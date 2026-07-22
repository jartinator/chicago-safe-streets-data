const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const M = require("../../site/assets/js/map-model.js");

// ---- binPoints ----

// Two points in the same 0.001° cell (cell index floor(-87.6499/0.001) =
// -87650 for both lng values, floor(41.9001/0.001) = 41900 for both lat
// values) bin to one entry with count: 2.
const samePoints = [
  { geometry: { coordinates: [-87.6499, 41.9001] } },
  { geometry: { coordinates: [-87.64995, 41.90005] } },
];
const sameBins = M.binPoints(samePoints, 0.001);
assert.strictEqual(sameBins.length, 1, "binPoints: two points in the same cell collapse to one entry");
assert.strictEqual(sameBins[0].count, 2, "binPoints: same-cell count is 2");

// Points in adjacent cells stay separate.
const adjacentPoints = [
  { geometry: { coordinates: [-87.6499, 41.9001] } }, // cell ix=-87650
  { geometry: { coordinates: [-87.6485, 41.9001] } }, // cell ix=-87649, one cell east
];
const adjacentBins = M.binPoints(adjacentPoints, 0.001);
assert.strictEqual(adjacentBins.length, 2, "binPoints: adjacent-cell points stay separate");
adjacentBins.forEach(b => assert.strictEqual(b.count, 1, "binPoints: each adjacent cell has count 1"));

// Cell centers are deterministic: center = (Math.floor(v/c)+0.5)*c
const cellDeg = 0.001;
const [pt] = M.binPoints([{ geometry: { coordinates: [-87.6499, 41.9001] } }], cellDeg);
const expectedLng = (Math.floor(-87.6499 / cellDeg) + 0.5) * cellDeg;
const expectedLat = (Math.floor(41.9001 / cellDeg) + 0.5) * cellDeg;
assert.ok(Math.abs(pt.lng - expectedLng) < 1e-9, "binPoints: cell center lng is deterministic");
assert.ok(Math.abs(pt.lat - expectedLat) < 1e-9, "binPoints: cell center lat is deterministic");

// Default cellDeg is 0.001 when omitted.
const defaultBins = M.binPoints(samePoints);
assert.strictEqual(defaultBins.length, 1, "binPoints: default cellDeg (0.001) also merges same-cell points");

// ---- DENSITY_RAMPS ----
assert.deepStrictEqual(
  M.DENSITY_RAMPS.crashes, ["#fecaca", "#f87171", "#dc2626", "#7f1d1d"],
  "DENSITY_RAMPS.crashes matches spec"
);
assert.deepStrictEqual(
  M.DENSITY_RAMPS.obstructions, undefined,
  "no obstructions ramp: On Your Left! publishes no obstruction data at all"
);

// ---- rampColor ----
const ramp = M.DENSITY_RAMPS.crashes;
assert.strictEqual(M.rampColor(1, 4, ramp), ramp[0], "rampColor: <=0.25 quartile -> ramp[0]");
assert.strictEqual(M.rampColor(2, 4, ramp), ramp[1], "rampColor: <=0.5 quartile -> ramp[1]");
assert.strictEqual(M.rampColor(3, 4, ramp), ramp[2], "rampColor: <=0.75 quartile -> ramp[2]");
assert.strictEqual(M.rampColor(4, 4, ramp), ramp[3], "rampColor: >0.75 quartile -> ramp[3]");
assert.strictEqual(M.rampColor(0, 0, ramp), ramp[0], "rampColor: maxCount <= 0 -> ramp[0]");
assert.strictEqual(M.rampColor(5, -1, ramp), ramp[0], "rampColor: negative maxCount -> ramp[0]");

// ---- densityRadius ----
assert.ok(
  Math.abs(M.densityRadius(1) - 4.2) < 0.01,
  "densityRadius(1) is approximately 4.2"
);
assert.strictEqual(M.densityRadius(100), 9, "densityRadius(100) is hard-capped at 9");
assert.strictEqual(M.densityRadius(1000), 9, "densityRadius(1000) stays capped at 9");

console.log("map-model OK");
