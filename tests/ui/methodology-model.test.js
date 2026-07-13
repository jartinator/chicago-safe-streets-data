const assert = require("assert");

// Minimal shim for Node environment
global.window = {};
global.document = undefined;

const M = require("../../site/assets/js/methodology.js");

assert.ok(Array.isArray(M.SECTIONS) && M.SECTIONS.length >= 6, "has the core sections");

const ids = M.SECTIONS.map(s => s.id);
assert.strictEqual(new Set(ids).size, ids.length, "section ids unique");
["ward-index", "severity", "coverage", "facilities", "exposure", "differences", "freshness"]
  .forEach(id => assert.ok(ids.includes(id), `section ${id} present`));

M.SECTIONS.forEach(s => {
  assert.ok(/^[a-z][a-z-]*$/.test(s.id), `id ${s.id} is an anchor-safe slug`);
  assert.ok(s.title && s.title.length > 3, `${s.id} has a title`);
  assert.ok(s.html && s.html.length > 100, `${s.id} has substantive body html`);
});

// Load-bearing claims other screens deep-link to — regressions here break
// the "recitable methodology one click away" contract.
const all = M.SECTIONS.map(s => s.html).join(" ");
assert.ok(all.includes("Higher = worse"), "index direction stated");
assert.ok(all.includes("Relative, not absolute"), "relative-not-absolute stated");
assert.ok(all.includes("3,945"), "coverage denominator stated");
assert.ok(all.includes("2023 remap"), "ward boundary vintage stated");
assert.ok(all.toLowerCase().includes("ksi"), "KSI definition present");

console.log("methodology-model OK");
