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

// ---- getUpcomingForWard: meetings + recently-introduced records ----
const hearingsStructured = {
  structured_data_available: true,
  committees: [
    { committee: "Committee on Pedestrian and Traffic Safety", calendar_url: "https://x/ped", meetings: [] },
    {
      committee: "Committee on Transportation and Public Way", calendar_url: "https://x/tpw",
      meetings: [
        { date: "2026-07-14T13:00:00", status: "Scheduled & Published", location: "Room 201-A",
          agenda_url: "https://x/agenda.pdf", notice_url: null, comment: "Written Public Comment deadline…" },
        { date: "2026-07-01T10:00:00", status: "Scheduled", location: null,
          agenda_url: null, notice_url: null, comment: null }, // already past `today` -> excluded
      ],
    },
  ],
};
const councilRecords = {
  records: [
    { title: "By ward", status: "Introduced", intro_date: "2026-07-01", sponsors: ["Someone Else"], sponsor_wards: ["22"], url: "u1" },
    { title: "By exact name", status: "Referred", intro_date: "2026-06-15", sponsors: ["Jane Doe"], sponsor_wards: [], url: "u2" },
    { title: "Too old", status: "Introduced", intro_date: "2025-09-01", sponsors: ["Jane Doe"], sponsor_wards: ["22"], url: "u3" },
    { title: "Already passed", status: "Passed", intro_date: "2026-07-01", sponsors: ["Jane Doe"], sponsor_wards: ["22"], url: "u4" },
    { title: "Fuzzy name must not match", status: "Introduced", intro_date: "2026-07-02", sponsors: [" jane doe "], sponsor_wards: [], url: "u5" },
    { title: "Other ward", status: "Introduced", intro_date: "2026-07-03", sponsors: ["X"], sponsor_wards: ["7"], url: "u6" },
  ],
};

const up = A.getUpcomingForWard(hearingsStructured, councilRecords, "Jane Doe", "22", "2026-07-12");
assert.strictEqual(up.meetings.length, 1, "getUpcomingForWard: past meetings excluded, future kept");
assert.strictEqual(up.meetings[0].date, "2026-07-14T13:00:00", "getUpcomingForWard: meeting date passed through");
assert.strictEqual(up.meetings[0].committee, "Committee on Transportation and Public Way",
  "getUpcomingForWard: committee name attached to each flattened meeting");
assert.strictEqual(up.meetings[0].calendar_url, "https://x/tpw",
  "getUpcomingForWard: committee calendar_url attached to each meeting");
assert.deepStrictEqual(
  up.introduced.map(r => r.title), ["By ward", "By exact name"],
  "getUpcomingForWard: matches sponsor_wards OR exact sponsor name, newest first; excludes old/passed/fuzzy/other-ward"
);

// A meeting exactly on `today` is still upcoming.
const sameDay = A.getUpcomingForWard(
  { structured_data_available: true, committees: [{ committee: "C", calendar_url: "https://x/c",
    meetings: [{ date: "2026-07-12T09:00:00", status: "Scheduled", agenda_url: null, notice_url: null, comment: null }] }] },
  null, null, "1", "2026-07-12"
);
assert.strictEqual(sameDay.meetings.length, 1, "getUpcomingForWard: same-day meeting counts as upcoming");

// Numeric ward argument coerces; sponsor_wards entries compared as strings.
const numericWard = A.getUpcomingForWard(null, councilRecords, null, 22, "2026-07-12");
assert.deepStrictEqual(numericWard.introduced.map(r => r.title), ["By ward"],
  "getUpcomingForWard: numeric ward matches string sponsor_wards; no name -> ward-only matching");

// Caps at 5, newest first.
const manyRecords = {
  records: Array.from({ length: 7 }, (_, i) => ({
    title: `Rec ${i}`, status: "Introduced", intro_date: `2026-06-${String(i + 10).padStart(2, "0")}`,
    sponsors: [], sponsor_wards: ["3"], url: `u${i}`,
  })),
};
const capped = A.getUpcomingForWard(null, manyRecords, null, "3", "2026-07-12");
assert.strictEqual(capped.introduced.length, 5, "getUpcomingForWard: introduced capped at 5");
assert.strictEqual(capped.introduced[0].title, "Rec 6", "getUpcomingForWard: newest first after cap");
assert.strictEqual(capped.introduced[4].title, "Rec 2", "getUpcomingForWard: oldest of the kept 5 is 5th-newest");

// Legacy link-out hearings shape (structured_data_available: false) -> no meetings.
const legacy = A.getUpcomingForWard(
  { structured_data_available: false, committees: [{ committee: "C", calendar_url: "https://x/c" }] },
  null, null, "1", "2026-07-12"
);
assert.deepStrictEqual(legacy.meetings, [], "getUpcomingForWard: link-out-only hearings shape yields no meetings");

// Empty-safe on null/missing data.
assert.deepStrictEqual(
  A.getUpcomingForWard(null, null, null, "1", "2026-07-12"),
  { meetings: [], introduced: [] },
  "getUpcomingForWard: null data returns empty lists"
);
assert.deepStrictEqual(
  A.getUpcomingForWard({}, {}, "Jane Doe", "1", "2026-07-12"),
  { meetings: [], introduced: [] },
  "getUpcomingForWard: shapeless data returns empty lists"
);

console.log("action-model OK");

// ---- getUpcomingForWard: agenda_items survive the meeting flattening ----
{
  const hearingsAgenda = { structured_data_available: true, committees: [
    { committee: "Committee on Transportation", calendar_url: "https://x/cal",
      meetings: [{ date: "2026-07-20T09:00:00",
        agenda_items: [{ record_number: "O2026-9", ward: 5,
          title: "Protected bike lane", safety_keyword_match: true, tracked: true }],
        agenda_amended: true }] },
  ] };
  const up = A.getUpcomingForWard(hearingsAgenda, null, null, "5", "2026-07-13");
  assert.strictEqual(up.meetings.length, 1);
  assert.strictEqual(up.meetings[0].agenda_amended, true);
  assert.strictEqual(up.meetings[0].agenda_items[0].title, "Protected bike lane");
}

// ---- getNoVoteRecordsForAlderman: exact-name join against recorded roll-calls ----
{
  const councilWithVotes = {
    records: [
      { matter_id: 1, title: "Newer no vote", type: "Ordinance", status: "Passed",
        intro_date: "2026-05-01T00:00:00", topic_relevant: true, url: "v1",
        sponsors: ["X"],
        recorded_votes: { yes: 40, no: 2, no_voters: ["Jane Doe", "Other, O"], result: "pass" } },
      { matter_id: 2, title: "Older no vote", type: "Ordinance", status: "Passed",
        intro_date: "2025-11-15T00:00:00", topic_relevant: true, url: "v2",
        sponsors: [],
        recorded_votes: { yes: 38, no: 1, no_voters: ["Jane Doe"], result: "pass" } },
      { matter_id: 3, title: "Off-topic no vote", type: "Ordinance", status: "Passed",
        intro_date: "2026-06-01T00:00:00", topic_relevant: false, url: "v3",
        sponsors: [],
        recorded_votes: { yes: 30, no: 5, no_voters: ["Jane Doe"], result: "pass" } },
      { matter_id: 4, title: "Voice vote (no roll call)", type: "Ordinance", status: "Passed",
        intro_date: "2026-06-10T00:00:00", topic_relevant: true, url: "v4",
        sponsors: ["Jane Doe"] },
      { matter_id: 5, title: "Someone else's no", type: "Ordinance", status: "Passed",
        intro_date: "2026-06-20T00:00:00", topic_relevant: true, url: "v5",
        sponsors: [],
        recorded_votes: { yes: 41, no: 1, no_voters: ["Other, O"], result: "pass" } },
      { matter_id: 6, title: "Fuzzy name must not match", type: "Ordinance", status: "Passed",
        intro_date: "2026-06-25T00:00:00", topic_relevant: true, url: "v6",
        sponsors: [],
        recorded_votes: { yes: 41, no: 1, no_voters: [" jane doe ", "JANE DOE"], result: "pass" } },
    ],
  };

  const noVotes = A.getNoVoteRecordsForAlderman(councilWithVotes, "Jane Doe");
  assert.deepStrictEqual(
    noVotes.map(r => r.matter_id), [1, 2],
    "getNoVoteRecordsForAlderman: exact-name, topic-relevant roll-calls only, newest first"
  );
  assert.strictEqual(noVotes[0].title, "Newer no vote",
    "getNoVoteRecordsForAlderman: record fields pass through");

  // Count agrees with the pipeline's recorded_no_votes semantics (topic_relevant
  // + recorded_votes + exact name) so the card never shows a count the list
  // contradicts.
  assert.strictEqual(noVotes.length, 2,
    "getNoVoteRecordsForAlderman: list length matches pipeline counting rule");

  assert.deepStrictEqual(A.getNoVoteRecordsForAlderman(councilWithVotes, null), [],
    "getNoVoteRecordsForAlderman: null name returns empty list");
  assert.deepStrictEqual(A.getNoVoteRecordsForAlderman(null, "Jane Doe"), [],
    "getNoVoteRecordsForAlderman: null data returns empty list");
  assert.deepStrictEqual(A.getNoVoteRecordsForAlderman({}, "Jane Doe"), [],
    "getNoVoteRecordsForAlderman: shapeless data returns empty list");
  assert.deepStrictEqual(A.getNoVoteRecordsForAlderman(councilWithVotes, "Nobody"), [],
    "getNoVoteRecordsForAlderman: unknown name returns empty list");

  console.log("action-model no-vote join OK");
}
