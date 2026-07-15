const assert = require("assert");

// Same shim pattern as the other UI model tests: home.js guards all DOM code
// behind `typeof document`, so requiring it in Node exercises only the pure
// model function.
global.window = {};
global.document = undefined;

const H = require("../../site/assets/js/home.js");

const citywide = {
  findings: [
    { id: "ksi-trend", stat: "216", data_tier: "real", title: "Cyclists killed or seriously injured" },
    { id: "protected-share", stat: "15%", data_tier: "real", title: "How much of the network protects riders" },
    { id: "street-coverage", stat: "11%", data_tier: "real", title: "Street grid coverage" },
    { id: "bna-score", stat: "11/100", data_tier: "crowdsourced", title: "National score" },
    { id: "hit-and-run", stat: "27%", data_tier: "real", title: "How often the driver leaves" },
    { id: "no-stat", data_tier: "real", title: "Missing stat" },
  ],
};

// ---- picks the requested ids, in order ----
const picked = H.pickHeadlineStats(citywide, ["ksi-trend", "protected-share", "bna-score", "hit-and-run"]);
assert.strictEqual(picked.length, 4, "returns one entry per requested id");
assert.deepStrictEqual(picked.map((p) => p.id),
  ["ksi-trend", "protected-share", "bna-score", "hit-and-run"], "preserves requested order");

// ---- carries the finding's own stat and tier (so tile matches source) ----
assert.strictEqual(picked[0].stat, "216", "carries the source stat verbatim");
assert.strictEqual(picked[0].tier, "real", "carries the finding's own data_tier");
assert.strictEqual(picked[2].tier, "crowdsourced", "bna-score keeps its crowdsourced tier");

// ---- missing ids are skipped, never faked ----
const withMissing = H.pickHeadlineStats(citywide, ["ksi-trend", "does-not-exist"]);
assert.strictEqual(withMissing.length, 1, "unknown ids are dropped");
assert.strictEqual(withMissing[0].id, "ksi-trend", "only the real finding survives");

// ---- findings without a stat are dropped ----
const withNoStat = H.pickHeadlineStats(citywide, ["no-stat", "hit-and-run"]);
assert.deepStrictEqual(withNoStat.map((p) => p.id), ["hit-and-run"], "stat-less findings are dropped");

// ---- defensive: bad inputs return [] rather than throwing ----
assert.deepStrictEqual(H.pickHeadlineStats(null, ["ksi-trend"]), [], "null citywide → []");
assert.deepStrictEqual(H.pickHeadlineStats(citywide, null), [], "null ids → []");
assert.deepStrictEqual(H.pickHeadlineStats({}, ["ksi-trend"]), [], "no findings array → []");

// ---- tier falls back to derived only when the finding omits data_tier ----
const noTier = H.pickHeadlineStats({ findings: [{ id: "x", stat: "1" }] }, ["x"]);
assert.strictEqual(noTier[0].tier, "derived", "missing data_tier falls back to derived");

console.log("home-model.test.js: all assertions passed");
