/* Pure helpers for the main-routes ("rail vs bus") layer: grade -> stroke
 * style, completion-bar segment widths from miles_by_grade, roster ordering,
 * and no_data (stub trail) handling. No DOM, no Leaflet — Node-testable.
 * Exposed as window.BSDMainRoutes in the browser, module.exports in Node.
 * Consumed by map.js to draw roster lines heavy (white casing under
 * grade-colored strokes) and to render the per-line report cards. */
(function (root) {
  // BSD.lineBadgeTier lives in common.js, which every page that loads this
  // file loads first (index.html: common.js -> map-model.js ->
  // main-routes-model.js -> map.js). In Node, common.js isn't required by
  // the test harness ahead of time, so pull it in directly there.
  const BSD = (typeof module !== "undefined" && module.exports)
    ? require("./common.js")
    : root.BSD;

  // Grade taxonomy, user-ranked: off-street (prized) > protected > paint >
  // mellow > none. Colors match the network map's quality-border palette
  // (docs/superpowers/specs/2026-07-13-network-tiers-design.md §3/§9) so a
  // grade reads the same color on both screens; `none` (sharrows/other)
  // renders dashed. `mellow` (greenway / mellow-derived geometry) is new in
  // the v2 taxonomy — `painted` was renamed `paint` to match the pipeline's
  // main_routes.geojson grade values exactly.
  const GRADE_ORDER = ["offstreet", "protected", "paint", "mellow", "none"];
  const GRADE_COLORS = {
    offstreet: "#0369a1",
    protected: "#0b6e4f",
    paint: "#f59e0b",
    mellow: "#7c3aed",
    none: "#94a3b8",
  };
  const GRADE_LABELS = {
    offstreet: "Off-street",
    protected: "Protected",
    paint: "Paint only",
    mellow: "Mellow (greenway)",
    none: "Nothing",
  };

  // White casing drawn under every grade stroke (metro-line treatment).
  const CASING_STYLE = { color: "#fff", weight: 8, opacity: 1 };

  // Leaflet-ready stroke style for a member segment's grade. Unknown grades
  // fall back to the muted `none` color but stay solid (we only dash what we
  // know is a sharrow/nothing stretch).
  function gradeStyle(grade) {
    const known = Object.prototype.hasOwnProperty.call(GRADE_COLORS, grade);
    return {
      color: known ? GRADE_COLORS[grade] : GRADE_COLORS.none,
      weight: 4.5,
      opacity: 0.95,
      dashArray: grade === "none" ? "6,7" : null,
    };
  }

  // Stacked completion-bar segments from a line's miles_by_grade: one entry
  // per non-zero grade, in GRADE_ORDER, with pct width of total member miles
  // (widths sum to exactly 100). Grade shares are over *existing* member
  // mileage — corridor gaps are holes in the line, never fabricated.
  function completionSegments(milesByGrade) {
    if (!milesByGrade) return [];
    const present = GRADE_ORDER
      .map(g => ({ grade: g, miles: milesByGrade[g] || 0 }))
      .filter(s => s.miles > 0);
    const total = present.reduce((sum, s) => sum + s.miles, 0);
    if (total <= 0) return [];
    return present.map(s => ({
      grade: s.grade,
      miles: s.miles,
      pct: (s.miles / total) * 100,
      color: GRADE_COLORS[s.grade],
      label: GRADE_LABELS[s.grade],
    }));
  }

  // Roster panel ordering: keep the curated config order, but sink lines
  // with no data this run (stub trails) to the bottom so the report card
  // leads with lines that actually have grades. Stable; input untouched.
  function rosterOrder(lines) {
    const withData = (lines || []).filter(l => !l.no_data);
    const noData = (lines || []).filter(l => l.no_data);
    return withData.concat(noData);
  }

  // Badge tier for a roster line: its own data_tier (derived for street
  // lines, crowdsourced for trails) unless there is no data this run —
  // then the stub badge, mirroring the map's other stub layers. Delegates
  // to the shared BSD.lineBadgeTier (common.js); kept as its own export
  // here since map.js and this file's tests call it as BSDMainRoutes.lineBadgeTier.
  function lineBadgeTier(line) {
    return BSD.lineBadgeTier(line);
  }

  // Printed "{pct}% protected" report-card number. Street lines only —
  // trail lines carry no pct_protected (100% off-street by definition) and
  // get null: we never fabricate a number. 0 is a real value.
  function pctText(line) {
    const pct = line.pct_protected;
    if (pct == null) return null;
    const str = pct % 1 === 0 ? pct.toFixed(0) : pct.toFixed(1);
    return `${str}% protected`;
  }

  const api = {
    GRADE_ORDER, GRADE_COLORS, GRADE_LABELS, CASING_STYLE,
    gradeStyle, completionSegments, rosterOrder, lineBadgeTier, pctText,
  };

  root.BSDMainRoutes = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
