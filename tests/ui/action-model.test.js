const assert = require("assert");

// Minimal shim for Node environment — action.js must guard all DOM-touching
// code behind `typeof document !== "undefined"` so requiring it here doesn't
// blow up. Pure functions take data as arguments, no BSD dependency.
global.window = {};
global.document = undefined;

const A = require("../../site/assets/js/action.js");

// ---- getSafetyIndexForWard: rank from array position ----
const safetyIndex = {
  data_tier: "derived",
  note: "some note",
  wards: [
    { ward: "42", comparable_danger_score: 96.0 },
    { ward: "43", comparable_danger_score: 88.8 },
    { ward: "1", comparable_danger_score: 87.8 },
  ],
};

const r1 = A.getSafetyIndexForWard(safetyIndex, "42");
assert.strictEqual(r1.rank, 1, "getSafetyIndexForWard: ward 42 is rank 1 (first in array)");
assert.strictEqual(r1.total, 3, "getSafetyIndexForWard: total reflects array length");
assert.strictEqual(r1.entry.ward, "42", "getSafetyIndexForWard: entry is the matching ward record");

const r2 = A.getSafetyIndexForWard(safetyIndex, "1");
assert.strictEqual(r2.rank, 3, "getSafetyIndexForWard: ward 1 is rank 3 (third in array), not derived from score");

// Numeric ward argument must coerce to string for comparison.
const r3 = A.getSafetyIndexForWard(safetyIndex, 43);
assert.strictEqual(r3.rank, 2, "getSafetyIndexForWard: numeric ward argument coerces to string");

assert.strictEqual(
  A.getSafetyIndexForWard(safetyIndex, "99"), null,
  "getSafetyIndexForWard: ward absent from data returns null"
);
assert.strictEqual(
  A.getSafetyIndexForWard(null, "42"), null,
  "getSafetyIndexForWard: null data returns null"
);

// ---- getSponsorRecordsForWard: exact-match-only sponsor resolution ----
const aldermenData = {
  note: "some note",
  wards: [
    { ward: "22", alderman: "Jane Doe", email: null },
    { ward: "23", alderman: null, email: null },
  ],
};

// Case A: pipeline already pre-resolved record.ward === String(ward). Must match.
const aldermenSafetyByWard = {
  note: "n",
  aldermen: [
    { sponsor_name: "Someone Else", ward: "22", safety_sponsorships: 3, recorded_no_votes: 1, records: [] },
  ],
};
const byWard = A.getSponsorRecordsForWard(aldermenSafetyByWard, aldermenData, "22");
assert.ok(byWard.matched, "getSponsorRecordsForWard: matches on pre-resolved record.ward");
assert.strictEqual(byWard.matched.sponsor_name, "Someone Else");
assert.strictEqual(byWard.aldermanName, "Jane Doe", "getSponsorRecordsForWard: returns the aldermen.json name for the ward");

// Case B: no record.ward match, but sponsor_name exactly equals aldermen.json name. Must match.
const aldermenSafetyByName = {
  note: "n",
  aldermen: [
    { sponsor_name: "Jane Doe", ward: null, safety_sponsorships: 2, recorded_no_votes: 0, records: [] },
  ],
};
const byName = A.getSponsorRecordsForWard(aldermenSafetyByName, aldermenData, "22");
assert.ok(byName.matched, "getSponsorRecordsForWard: matches on exact sponsor_name === aldermen.json name");
assert.strictEqual(byName.matched.sponsor_name, "Jane Doe");

// Case C: sponsor_name differs only by case/spacing from the aldermen.json name.
// Must NOT match — exact-match only, never fuzzy.
const aldermenSafetyFuzzy = {
  note: "n",
  aldermen: [
    { sponsor_name: " jane doe ", ward: null, safety_sponsorships: 5, recorded_no_votes: 2, records: [] },
    { sponsor_name: "JANE DOE", ward: null, safety_sponsorships: 5, recorded_no_votes: 2, records: [] },
  ],
};
const fuzzy = A.getSponsorRecordsForWard(aldermenSafetyFuzzy, aldermenData, "22");
assert.strictEqual(fuzzy.matched, null, "getSponsorRecordsForWard: case/spacing-differing sponsor_name must NOT match");

// Case D: no aldermen.json name at all (null) — can only match via record.ward.
const noName = A.getSponsorRecordsForWard(aldermenSafetyByName, aldermenData, "23");
assert.strictEqual(noName.matched, null, "getSponsorRecordsForWard: no aldermen.json name and no record.ward match -> null");
assert.strictEqual(noName.aldermanName, null, "getSponsorRecordsForWard: aldermanName is null when alderman field is null");

// Case E: missing recorded_no_votes (stale-fixture shape) is handled as 0.
const staleShape = {
  note: "n",
  aldermen: [
    { sponsor_name: "Someone Else", ward: "22", safety_sponsorships: 0, records: [] }, // no recorded_no_votes key at all
  ],
};
const stale = A.getSponsorRecordsForWard(staleShape, aldermenData, "22");
assert.ok(stale.matched, "getSponsorRecordsForWard: stale-fixture entry still matches");
assert.strictEqual(stale.matched.recorded_no_votes, 0, "getSponsorRecordsForWard: missing recorded_no_votes normalized to 0");
assert.strictEqual(stale.matched.safety_sponsorships, 0, "getSponsorRecordsForWard: sponsorships 0 with recorded_no_votes present renders sensibly");

// No aldermenSafetyData at all.
assert.deepStrictEqual(
  A.getSponsorRecordsForWard(null, aldermenData, "22"),
  { matched: null, aldermanName: "Jane Doe" },
  "getSponsorRecordsForWard: null safety data still resolves aldermanName, matched is null"
);

// ---- getMenuSpendingForWard ----
const menuData = {
  data_tier: "proxy",
  note: "menu note",
  wards: {
    "21": { total_spent: 39176.76, items: 4, bike_safety_spent: 7807.86 },
  },
};

const menuHit = A.getMenuSpendingForWard(menuData, "21");
assert.deepStrictEqual(
  menuHit,
  { total_spent: 39176.76, items: 4, bike_safety_spent: 7807.86 },
  "getMenuSpendingForWard: returns the ward's spending record"
);

// Numeric ward argument coerces to string key lookup.
assert.deepStrictEqual(
  A.getMenuSpendingForWard(menuData, 21),
  { total_spent: 39176.76, items: 4, bike_safety_spent: 7807.86 },
  "getMenuSpendingForWard: numeric ward argument coerces to string"
);

// Ward absent from the file -> null (not an empty object, not a thrown error).
assert.strictEqual(
  A.getMenuSpendingForWard(menuData, "22"), null,
  "getMenuSpendingForWard: ward absent from file returns null"
);
assert.strictEqual(
  A.getMenuSpendingForWard(null, "21"), null,
  "getMenuSpendingForWard: null data returns null"
);

console.log("action-model OK");
