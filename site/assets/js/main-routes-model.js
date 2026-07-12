/* Pure helpers for the main-routes ("rail vs bus") layer: grade -> stroke
 * style, completion-bar segment widths from miles_by_grade, roster ordering,
 * and no_data (stub trail) handling. No DOM, no Leaflet — Node-testable.
 * Exposed as window.BSDMainRoutes in the browser, module.exports in Node.
 * Consumed by map.js to draw roster lines heavy (white casing under
 * grade-colored strokes) and to render the per-line report cards. */
(function (root) {
  // Grade taxonomy, user-ranked: off-street (prized) > protected > painted >
  // none. Colors per design spec §4; `none` (sharrows/other) renders dashed.
  const GRADE_ORDER = ["offstreet", "protected", "painted", "none"];
  const GRADE_COLORS = {
    offstreet: "#0369a1",
    protected: "#0b6e4f",
    painted: "#f59e0b",
    none: "#94a3b8",
  };
  const GRADE_LABELS = {
    offstreet: "Off-street",
    protected: "Protected",
    painted: "Paint only",
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
  // then the stub badge, mirroring the map's other stub layers.
  function lineBadgeTier(line) {
    return line.no_data ? "stub" : line.data_tier;
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
