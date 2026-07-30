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

// ---- newsForWard + buildOnePager news (contract v1.12) ----
{
  const newsData = {
    items: [
      { title: "A", url: "u1", source: "Streetsblog Chicago", published: "2026-07-10T00:00:00+00:00",
        matches: { wards: [{ ward: "1", via: "publisher tag '1st Ward'" }], aldermen: [], routes: [] },
        extraneous: "dropped" },
      { title: "B", url: "u2", source: null, published: "2026-07-09T00:00:00+00:00",
        matches: { wards: [{ ward: "2", via: "t" }], aldermen: [], routes: [] } },
    ],
  };
  const hits = W.newsForWard(newsData, 1);
  assert.deepStrictEqual(hits, [
    { title: "A", url: "u1", source: "Streetsblog Chicago", published: "2026-07-10T00:00:00+00:00" },
  ], "newsForWard: matched, and slimmed to the four render fields");
  assert.deepStrictEqual(W.newsForWard(newsData, 9), [], "no match → empty");
  assert.deepStrictEqual(W.newsForWard(null, 1), [], "null data → empty");

  const withNews = W.buildOnePager({ newsData }, 1, "2026-07-13");
  assert.strictEqual(withNews.news.length, 1, "buildOnePager threads news through");
  assert.deepStrictEqual(W.buildOnePager({}, 1, "2026-07-13").news, [],
    "missing news data → empty list, never null (renders explicit empty state)");
  console.log("ward-model news OK");
}

// ---- roundForDisplay: Confidence Signal, boundary cases (03-experience.md
// §6.3; must be BSD-free per critique round-2 §3.2/§7.1.1) ----
{
  assert.deepStrictEqual(W.roundForDisplay(82), { display: "82", approx: false });
  assert.deepStrictEqual(W.roundForDisplay(999), { display: "999", approx: false }, "999: exact branch");
  assert.deepStrictEqual(W.roundForDisplay(1000), { display: "about 1,000", approx: true },
    "1000: rounded branch, nearest-100");
  assert.deepStrictEqual(W.roundForDisplay(9999), { display: "about 10,000", approx: true },
    "9999: rounded branch, nearest-100, still under the nearest-1000 unit switch");
  assert.deepStrictEqual(W.roundForDisplay(10000), { display: "about 10,000", approx: true },
    "10000: rounded branch, nearest-1000 unit");
  assert.deepStrictEqual(W.roundForDisplay(104720), { display: "about 105,000", approx: true },
    "ward 42 worked example");
  assert.deepStrictEqual(W.roundForDisplay(59589), { display: "about 60,000", approx: true },
    "ward 27 worked example");
  console.log("roundForDisplay OK");
}

// ---- monthsBetween / isDivvyStale (03-experience.md §6.5) ----
{
  assert.strictEqual(W.monthsBetween("2026-06", "2026-07-27"), 1);
  assert.strictEqual(W.monthsBetween("2026-04", "2026-07-27"), 3);
  assert.strictEqual(W.monthsBetween("2026-03", "2026-07-27"), 4);
  assert.strictEqual(W.monthsBetween("2025-12", "2026-01-01"), 1, "year boundary");

  assert.strictEqual(W.isDivvyStale("2026-06", "2026-07-27T18:07:34+00:00"), false, "1 month: live, not stale");
  assert.strictEqual(W.isDivvyStale("2026-04", "2026-07-27"), false, "3 months: at threshold, not stale");
  assert.strictEqual(W.isDivvyStale("2026-03", "2026-07-27"), true, "4 months: over threshold, stale");
  assert.strictEqual(W.isDivvyStale(null, "2026-07-27"), false, "null as_of: can't assess, don't guess");
  assert.strictEqual(W.isDivvyStale("2026-03", null), false, "null build date: can't assess, don't guess");
  console.log("isDivvyStale OK");
}

// ---- fmtMonth ----
{
  assert.strictEqual(W.fmtMonth("2026-06"), "June 2026");
  assert.strictEqual(W.fmtMonth("2026-06-15T00:00:00Z"), "June 2026");
  assert.strictEqual(W.fmtMonth(null), "—");
  console.log("fmtMonth OK");
}

// ---- buildOnePager: Divvy state selection (A/B/C, plus the E flag) ----
{
  const divvyOkData = {
    status: "ok", as_of: "2026-06",
    wards: [{ ward: "42", trip_count: 104720 }, { ward: "41", trip_count: 82 }],
  };
  const meta = { generated_at: "2026-07-27T18:07:34+00:00" };

  // State A — ward present, live (rounded branch).
  const a = W.buildOnePager({ divvyData: divvyOkData, metaData: meta }, 42, "2026-07-13");
  assert.strictEqual(a.divvy.tripCount, 104720);
  assert.strictEqual(a.divvy.hasCoverage, true);
  assert.strictEqual(a.divvy.asOf, "2026-06");
  assert.strictEqual(a.divvy.isStale, false);

  // State B — ward absent from wards[], but status ok and file loaded.
  const b = W.buildOnePager({ divvyData: divvyOkData, metaData: meta }, 7, "2026-07-13");
  assert.strictEqual(b.divvy.hasCoverage, false);
  assert.strictEqual(b.divvy.tripCount, null, "state B: no number, never zero");

  // State C — file missing/fetch failed (divvyData null).
  const c = W.buildOnePager({ divvyData: null, metaData: meta }, 42, "2026-07-13");
  assert.strictEqual(c.divvy, null, "state C: no file → divvy is null, not an object with nulls");

  // State C — status !== "ok".
  const cBadStatus = W.buildOnePager(
    { divvyData: { status: "error", wards: [] }, metaData: meta }, 42, "2026-07-13");
  assert.strictEqual(cBadStatus.divvy, null, "state C: status !== ok → null");

  // State E flag — co-occurs with A, doesn't replace it.
  const staleData = { status: "ok", as_of: "2026-03", wards: [{ ward: "42", trip_count: 104720 }] };
  const e = W.buildOnePager({ divvyData: staleData, metaData: meta }, 42, "2026-07-13");
  assert.strictEqual(e.divvy.isStale, true);
  assert.strictEqual(e.divvy.tripCount, 104720, "E is a flag alongside A, not a replacement for it");

  // No divvyData input at all (existing fixtures that don't pass it).
  const none = W.buildOnePager({}, 42, "2026-07-13");
  assert.strictEqual(none.divvy, null);

  console.log("buildOnePager divvy state selection OK");
}
