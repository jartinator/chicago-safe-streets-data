const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const B = require("../../site/assets/js/common.js");

assert.strictEqual(B.scoreColor(null), "#e2e8f0");
assert.strictEqual(B.scoreColor(86.8), "#991b1b");
assert.strictEqual(B.scoreColor(45), "#f59e0b");
assert.strictEqual(B.money(19416.66), "$19,417");
assert.strictEqual(B.money(null), "—");
assert.ok(B.trendHTML({ direction: "worsening", pct_change: 25.0 }).includes("▲"));
assert.ok(B.trendHTML({ direction: "insufficient_data" }).includes("Insufficient"));

// Regression: improving trends carry NEGATIVE pct_change from the pipeline;
// the sign must render as-is, not be flipped to "+".
const improving = B.trendHTML({ direction: "improving", pct_change: -30.0 });
assert.ok(improving.includes("▼"), "improving trend shows down arrow");
assert.ok(improving.includes("-30%"), "improving trend shows signed -30%");
assert.ok(!improving.includes("+30%"), "improving trend must not show +30%");

console.log("common-helpers OK");
