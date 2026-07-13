const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const W = require("../../site/assets/js/ward-model.js");

// ---- bboxOf ----
assert.deepStrictEqual(
  W.bboxOf({ type: "LineString", coordinates: [[-87.7, 41.9], [-87.6, 42.0]] }),
  [-87.7, 41.9, -87.6, 42.0]);

// ---- topCorridorsForWard: overlap screen, crash-ranked, top-n ----
const wardFeature = {
  properties: { ward: "1", cyclist_crashes: 120 },
  geometry: { type: "Polygon", coordinates: [[[-87.7, 41.9], [-87.6, 41.9], [-87.6, 42.0], [-87.7, 42.0], [-87.7, 41.9]]] },
};
const routes = [
  { properties: { street: "MILWAUKEE AVE", crashes_within_30m: 40, length_m: 900 },
    geometry: { type: "LineString", coordinates: [[-87.68, 41.95], [-87.65, 41.97]] } },
  { properties: { street: "MILWAUKEE AVE", crashes_within_30m: 10, length_m: 300 },
    geometry: { type: "LineString", coordinates: [[-87.65, 41.97], [-87.63, 41.98]] } },
  { properties: { street: "DAMEN AVE", crashes_within_30m: 5, length_m: 500 },
    geometry: { type: "LineString", coordinates: [[-87.67, 41.92], [-87.67, 41.99]] } },
  { properties: { street: "FAR AWAY RD", crashes_within_30m: 99, length_m: 100 },
    geometry: { type: "LineString", coordinates: [[-87.9, 41.5], [-87.91, 41.51]] } },
];
const top = W.topCorridorsForWard(wardFeature, routes, 3);
assert.strictEqual(top[0].street, "MILWAUKEE AVE");
assert.strictEqual(top[0].crashes, 50, "segments aggregate per street");
assert.ok(!top.some(c => c.street === "FAR AWAY RD"), "non-overlapping street excluded");
assert.deepStrictEqual(W.topCorridorsForWard(null, routes, 3), [], "null ward is safe");

// ---- nextMeeting: soonest future, honest about legacy pulls ----
const hearings = {
  structured_data_available: true,
  committees: [
    { committee: "Committee on Pedestrian and Traffic Safety", meetings: [
      { date: "2026-07-10T10:00:00", comment: "past — must be skipped" },
      { date: "2026-07-21T10:00:00", comment: "Written comment by Jul 18" },
    ] },
    { committee: "Committee on Transportation", meetings: [
      { date: "2026-07-15T09:00:00" },
    ] },
  ],
};
const nm = W.nextMeeting(hearings, "2026-07-13");
assert.strictEqual(String(nm.date).slice(0, 10), "2026-07-15", "soonest future across committees");
assert.strictEqual(nm.committee, "Committee on Transportation");
assert.strictEqual(W.nextMeeting({ structured_data_available: false, committees: [] }, "2026-07-13"),
  null, "legacy link-out pull yields null, never a fabricated meeting");
assert.strictEqual(W.nextMeeting(null, "2026-07-13"), null);

// ---- buildOnePager: assembles nulls honestly ----
const safetyIndexData = { wards: [
  { ward: "3", comparable_danger_score: 71, cyclist_crashes: 200, bikeway_miles: 12.5,
    bikeway_pct_protected: 18, bikeway_pct_of_roads: 9,
    windows: { window_end: "2026-06-30",
      recent_12mo: { crashes: 41, injury_crashes: 12, ksi: 3, fatal: 1 },
      prior_12mo: { crashes: 50, injury_crashes: 15, ksi: 5, fatal: 0 } } },
  { ward: "1", comparable_danger_score: 55, cyclist_crashes: 120 },
] };
const aldermenData = { wards: [{ ward: "3", alderman: "Doe, Jane", email: "jane@example.org", phone: null }] };
const menuData = { wards: { "3": { total_spent: 1200000, items: 14, bike_safety_spent: 80000 } } };
const metaData = { generated_at: "2026-07-12T08:00:00Z" };

const o = W.buildOnePager(
  { safetyIndexData, aldermenData, wardsData: { features: [wardFeature] },
    routesData: { features: routes }, hearingsData: hearings, menuData, metaData },
  3, "2026-07-13");
assert.strictEqual(o.ward, "3");
assert.strictEqual(o.asOf, "2026-07-12");
assert.strictEqual(o.alderman.name, "Doe, Jane");
assert.strictEqual(o.concern.score, 71);
assert.strictEqual(o.concern.rank, 1, "rank is file order, never recomputed");
assert.strictEqual(o.windows.recent.crashes, 41);
assert.strictEqual(o.pctProtected, 18);
assert.strictEqual(o.pctRoads, 9);
assert.strictEqual(o.menuBikeSpent, 80000);
assert.strictEqual(String(o.nextMeeting.date).slice(0, 10), "2026-07-15");
assert.deepStrictEqual(o.topCorridors, [], "ward 3 has no ward feature → no corridors, not a crash");

// Missing everything → honest nulls, no throws
const empty = W.buildOnePager({}, 7, "2026-07-13");
assert.strictEqual(empty.ward, "7");
assert.strictEqual(empty.concern, null);
assert.strictEqual(empty.alderman, null);
assert.strictEqual(empty.windows, null);
assert.strictEqual(empty.menuBikeSpent, null, "missing menu data is null, never 0");
assert.deepStrictEqual(empty.topCorridors, []);

console.log("ward-model OK");

// ---- nextMeeting: contract v1.10 agenda_items pass through untouched ----
const hearingsWithAgenda = {
  structured_data_available: true,
  committees: [{ committee: "Committee on Transportation", meetings: [
    { date: "2026-07-15T09:00:00",
      agenda_items: [{ record_number: "O2026-1", ward: 28, title: "Vacation of alley",
                       safety_keyword_match: false, tracked: false }] },
  ] }],
};
const nmAgenda = W.nextMeeting(hearingsWithAgenda, "2026-07-13");
assert.strictEqual(nmAgenda.agenda_items.length, 1, "agenda_items passed through");
assert.strictEqual(nmAgenda.agenda_amended, false, "agenda_amended always present as bool");
assert.strictEqual(nmAgenda.agenda_items[0].title, "Vacation of alley");
assert.strictEqual(W.nextMeeting(hearings, "2026-07-13").agenda_items, null,
  "meetings without parsed agendas carry null, not a fabricated empty list");
