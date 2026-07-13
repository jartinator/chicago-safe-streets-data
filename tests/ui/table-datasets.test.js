const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const T = require("../../site/assets/js/table.js");

// ---- buildSafetyIndexRows ----

const wards = [
  {
    ward: "42", cyclist_crashes: 1092, population: 72572, bikeway_miles: 8.18,
    crashes_per_10k_pop: 150.47, crashes_per_bikeway_mile: 133.56, comparable_danger_score: 96.0,
    crash_trend: { direction: "worsening", pct_change: 17.6 },
    bikeway_pct_protected: 24.6, road_miles: 71.3, bikeway_pct_of_roads: 11.5,
  },
  {
    // stale/edge shape: nulls throughout (ward absent from ward_demographics.json etc.)
    ward: "10", cyclist_crashes: 87, population: null, bikeway_miles: 16.21,
    crashes_per_10k_pop: null, crashes_per_bikeway_mile: 5.37, comparable_danger_score: null,
    crash_trend: { direction: "insufficient_data", pct_change: null },
    bikeway_pct_protected: null, road_miles: null, bikeway_pct_of_roads: null,
  },
];

const siRows = T.buildSafetyIndexRows(wards);

assert.strictEqual(siRows.length, 2, "buildSafetyIndexRows: one row per ward");
assert.strictEqual(siRows[0].rank, 1, "buildSafetyIndexRows: rank from array order (first = 1)");
assert.strictEqual(siRows[1].rank, 2, "buildSafetyIndexRows: rank from array order (second = 2)");
assert.strictEqual(siRows[0].ward, "42", "buildSafetyIndexRows: ward passed through");
assert.strictEqual(siRows[0].comparable_danger_score, 96.0, "buildSafetyIndexRows: score passed through");
assert.strictEqual(siRows[0].cyclist_crashes, 1092, "buildSafetyIndexRows: crashes passed through");
assert.strictEqual(siRows[0].crashes_per_10k_pop, 150.47, "buildSafetyIndexRows: per-10k passed through");
assert.strictEqual(siRows[0].crashes_per_bikeway_mile, 133.56, "buildSafetyIndexRows: per-mile passed through");
assert.strictEqual(siRows[0].bikeway_miles, 8.18, "buildSafetyIndexRows: bikeway_miles passed through");
assert.strictEqual(siRows[0].population, 72572, "buildSafetyIndexRows: population passed through");
assert.strictEqual(siRows[0].trend_direction, "worsening", "buildSafetyIndexRows: trend_direction from crash_trend");
assert.strictEqual(siRows[0].trend_pct_change, 17.6, "buildSafetyIndexRows: trend_pct_change from crash_trend");

// nulls pass through, not coerced to 0/"" — required for "nulls sort last" downstream
assert.strictEqual(siRows[1].population, null, "buildSafetyIndexRows: null population passes through");
assert.strictEqual(siRows[1].comparable_danger_score, null, "buildSafetyIndexRows: null score passes through");
assert.strictEqual(siRows[1].crashes_per_10k_pop, null, "buildSafetyIndexRows: null per-10k passes through");
assert.strictEqual(siRows[1].trend_direction, "insufficient_data", "buildSafetyIndexRows: insufficient_data trend direction");
assert.strictEqual(siRows[1].trend_pct_change, null, "buildSafetyIndexRows: null trend pct_change passes through");

assert.strictEqual(siRows[0].bikeway_pct_protected, 24.6, "coverage: pct protected passes through");
assert.strictEqual(siRows[0].road_miles, 71.3, "coverage: road miles passes through");
assert.strictEqual(siRows[0].bikeway_pct_of_roads, 11.5, "coverage: pct of roads passes through");
assert.strictEqual(siRows[1].bikeway_pct_protected, null, "coverage: null preserved (not 0)");
assert.strictEqual(siRows[1].bikeway_pct_of_roads, null, "coverage: null preserved (not 0)");

// ---- buildCouncilRows ----

const councilRecords = [
  {
    // stale-fixture shape: no `source` key, no `recorded_votes` key, short date
    matter_id: 123,
    title: "Amend traffic code",
    type: "ordinance",
    status: "Passed",
    intro_date: "2020-01-02",
    sponsors: ["Harris, Michelle A.", "Conway, William"],
    url: "https://chicago.legistar.com/LegislationDetail.aspx?ID=123",
    topic_tagged_by: "llm",
  },
  {
    // v1.5 shape: string matter_id, full timestamp intro_date, contested vote
    matter_id: "R2026-0026846",
    title: "Committee reassignment",
    type: "resolution",
    status: "Adopted",
    intro_date: "2026-07-09T00:00:00",
    sponsors: ["Ramirez-Rosa, Daniel"],
    source: "councilmatic",
    recorded_votes: { yes: 38, no: 7, result: "pass", no_voters: ["Smith", "Jones"] },
    url: "https://chicago.councilmatic.org/legislation/R2026-0026846/",
    topic_tagged_by: "keyword_fallback",
  },
];

const crRows = T.buildCouncilRows(councilRecords);

assert.strictEqual(crRows.length, 2, "buildCouncilRows: one row per record");

// row 0: stale-fixture shape
assert.strictEqual(crRows[0].intro_date, "2020-01-02", "buildCouncilRows: short date left as YYYY-MM-DD");
assert.strictEqual(crRows[0].title, "Amend traffic code", "buildCouncilRows: title passed through");
assert.strictEqual(crRows[0].type, "ordinance", "buildCouncilRows: type passed through");
assert.strictEqual(crRows[0].status, "Passed", "buildCouncilRows: status passed through");
assert.strictEqual(crRows[0].sponsors, "Harris, Michelle A.; Conway, William", "buildCouncilRows: sponsors joined with '; '");
assert.strictEqual(crRows[0].source, "legistar", "buildCouncilRows: missing source defaults to 'legistar'");
assert.strictEqual(crRows[0].vote, "", "buildCouncilRows: vote empty when recorded_votes absent");
assert.strictEqual(crRows[0].topic_tagged_by, "llm", "buildCouncilRows: topic_tagged_by passed through");
assert.strictEqual(crRows[0].url, "https://chicago.legistar.com/LegislationDetail.aspx?ID=123", "buildCouncilRows: url passed through");

// row 1: v1.5 shape with contested vote
assert.strictEqual(crRows[1].intro_date, "2026-07-09", "buildCouncilRows: full timestamp sliced to YYYY-MM-DD");
assert.strictEqual(crRows[1].sponsors, "Ramirez-Rosa, Daniel", "buildCouncilRows: single sponsor, no separator added");
assert.strictEqual(crRows[1].source, "councilmatic", "buildCouncilRows: explicit source passed through");
assert.strictEqual(crRows[1].vote, "38–7 pass", "buildCouncilRows: recorded_votes renders as '{yes}–{no} {result}'");
assert.strictEqual(crRows[1].topic_tagged_by, "keyword_fallback", "buildCouncilRows: keyword_fallback passed through");

// matter_id may be int (row 0) or string (row 1) — must not throw either way
assert.doesNotThrow(() => T.buildCouncilRows([{ matter_id: 999, sponsors: [] }]),
  "buildCouncilRows: accepts int matter_id");
assert.doesNotThrow(() => T.buildCouncilRows([{ matter_id: "R2026-1", sponsors: [] }]),
  "buildCouncilRows: accepts string matter_id");

// sponsors missing entirely (defensive) shouldn't throw and should give ""
const noSponsors = T.buildCouncilRows([{ matter_id: 1, sponsors: [] }]);
assert.strictEqual(noSponsors[0].sponsors, "", "buildCouncilRows: empty sponsors array joins to ''");

console.log("table-datasets OK");
