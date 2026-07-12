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

// Rebrand regression: the brand render is DOM-only, but the Node-facing exports
// must keep working exactly as before.
assert.strictEqual(typeof B.esc, "function");
assert.strictEqual(B.esc('<a href="x">& \'y\'</a>'),
  "&lt;a href=&quot;x&quot;&gt;&amp; &#39;y&#39;&lt;/a&gt;");
assert.strictEqual(B.esc(null), "");
assert.strictEqual(B.fmt(19416), "19,416");
assert.strictEqual(B.fmt(null), "—");

// Regression: improving trends carry NEGATIVE pct_change from the pipeline;
// the sign must render as-is, not be flipped to "+".
const improving = B.trendHTML({ direction: "improving", pct_change: -30.0 });
assert.ok(improving.includes("▼"), "improving trend shows down arrow");
assert.ok(improving.includes("-30%"), "improving trend shows signed -30%");
assert.ok(!improving.includes("+30%"), "improving trend must not show +30%");

// Tappable badges: badgeHTML renders a <button> carrying data-tier so the
// delegated click handler can open the tier explainer.
const proxyBadge = B.badgeHTML("proxy");
assert.ok(proxyBadge.includes("<button"), "badge renders as a <button>");
assert.ok(proxyBadge.includes('data-tier="proxy"'), "badge carries data-tier");
assert.ok(proxyBadge.includes("tier-proxy"), "badge keeps tier-{t} class");
const bogusBadge = B.badgeHTML("bogus");
assert.ok(bogusBadge.includes('data-tier="stub"'), "unknown tier falls back to stub");
assert.ok(bogusBadge.includes("no data yet"), "stub badge label is 'no data yet'");

// Plain-language tier explainers for the modal.
assert.strictEqual(typeof B.TIER_PLAIN, "object");
for (const tier of ["real", "proxy", "derived", "mock", "crowdsourced", "stub"]) {
  assert.ok(typeof B.TIER_PLAIN[tier] === "string" && B.TIER_PLAIN[tier].length > 0,
    `TIER_PLAIN has plain wording for '${tier}'`);
}

console.log("common-helpers OK");
