/* Pure geometry/aggregation helpers for the Network (metro-map) screen.
 * No DOM, no Leaflet — Node-testable. Exposed as window.BSDNet in the
 * browser, module.exports in Node. Consumed by network.js.
 *
 * Spec: docs/superpowers/specs/2026-07-12-network-map-distinction.md
 * The network map has exactly three concerns (§2): major routes (one solid
 * color per line), connecting routes (local network + trails + mellow), and
 * route quality (an opt-in grade-colored border). No safety data lives here
 * — that's the transportation map's job (index.html / map.js). */
(function (root) {
  // Flatten LineString or MultiLineString coordinates to one list of [lng, lat]
  // pairs. The live CDOT bike-routes feed is MultiLineString (each feature can
  // hold multiple disjoint parts); other layers may still be plain LineString.
  function flattenCoords(geometry) {
    const coords = geometry.coordinates;
    if (geometry.type === "MultiLineString") {
      return coords.flat();
    }
    return coords;
  }

  // Convert geometry to Leaflet latlngs, preserving MultiLineString's nested
  // parts so Leaflet draws one multi-part polyline instead of joining
  // disjoint segments with a straight line.
  function toLatLngs(geometry) {
    if (geometry.type === "MultiLineString") {
      return geometry.coordinates.map((part) => part.map(([lng, lat]) => [lat, lng]));
    }
    return geometry.coordinates.map(([lng, lat]) => [lat, lng]);
  }

  // Calculate padded bbox: [[minLat, minLng], [maxLat, maxLng]].
  function getPaddedBBox(geometry, pad = 0.0006) {
    let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;
    for (const [lng, lat] of flattenCoords(geometry)) {
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
    }
    return [
      [minLat - pad, minLng - pad],
      [maxLat + pad, maxLng + pad],
    ];
  }

  // Point-in-bbox test. `point` is a GeoJSON Feature<Point>.
  function pointInBBox(point, bbox) {
    const [lng, lat] = point.geometry.coordinates;
    return lat >= bbox[0][0] && lat <= bbox[1][0] &&
           lng >= bbox[0][1] && lng <= bbox[1][1];
  }

  // Group route features by corridor (street name). A missing/empty street
  // is bucketed under "(unnamed)". Returns Map<street, feature[]>.
  function groupByCorridor(routeFeatures) {
    const groups = new Map();
    routeFeatures.forEach((feature) => {
      const raw = feature.properties.street;
      const key = raw == null || raw === "" ? "(unnamed)" : raw;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(feature);
    });
    return groups;
  }

  // Default overlay ids enabled when network.html has no ?overlays= param.
  // Spec §5: quality (border) defaults off; connecting/mellow/nodes default on.
  const DEFAULT_OVERLAYS = ["connecting", "mellow", "nodes"];

  // Sentinel for "explicitly no overlays": BSD.setParams deletes params
  // whose value is "", so an empty set serialized as "" would vanish from
  // the URL and reload back as the defaults. "none" survives the round-trip.
  const OVERLAYS_NONE = "none";

  // Parse the `overlays` URL param into a Set of overlay ids. `str` is
  // whatever BSD.qs().get("overlays") returns: null when the param is
  // absent (fall back to defaults), the "none" sentinel (empty set), or a
  // comma-joined string ("" also yields an empty set). Unknown/legacy ids
  // (e.g. "heat", "crashes", "stations", "trails" from the pre-distinction
  // map) are not filtered here — network.js simply never looks them up, so
  // they're silently ignored per spec §5.
  function parseOverlays(str) {
    if (str == null) return new Set(DEFAULT_OVERLAYS);
    if (str === OVERLAYS_NONE) return new Set();
    return new Set(str.split(",").filter(Boolean));
  }

  // Serialize an overlay Set back into the URL param value: comma-joined
  // ids, or the "none" sentinel when the set is empty.
  function serializeOverlays(overlaySet) {
    return overlaySet.size === 0 ? OVERLAYS_NONE : [...overlaySet].join(",");
  }

  // ---- Main routes ("rail vs bus") helpers — spec §4/§5/§6 of
  // docs/superpowers/specs/2026-07-12-network-map-distinction.md ----

  // Grade colors, user-ranked offstreet > protected > painted > none.
  // Duplicated from the grade taxonomy rather than imported from
  // main-routes-model.js: network.html only loads this model file. Shared
  // with the transportation map and roster report cards (spec §6).
  const GRADE_COLORS = {
    offstreet: "#0369a1",
    protected: "#0b6e4f",
    painted: "#f59e0b",
    none: "#94a3b8",
  };

  // Demoted local ("bus") network: thin, muted, no casing.
  const LOCAL_STYLE = { color: "#cbd5e1", weight: 1.5, opacity: 0.9 };

  // Non-roster OSM trails join the connecting-infrastructure level too
  // (spec §5, "Connecting infrastructure" row).
  const CONNECTING_TRAIL_STYLE = { color: "#38bdf8", weight: 2, opacity: 0.8 };

  // One solid color per named line (spec §4). Crossing/parallel-nearby
  // lines differ strongly in hue or lightness; the GRADE_COLORS hues are
  // reserved for the quality border, so no line color repeats a grade hue
  // except trails (uniformly off-street; the border adds nothing there).
  const LINE_COLORS = {
    // diagonals
    "milwaukee":            "#1d4ed8",
    "elston":               "#ea580c",
    "vincennes":            "#c026d3",
    // north-south, west -> east
    "california":           "#db2777",
    "kedzie":               "#7c3aed",
    "damen":                "#059669",
    "halsted":               "#dc2626",
    "clark":                "#0891b2",
    "state-indiana":        "#4d7c0f",
    "mlk-drive":            "#92400e",
    // east-west, north -> south
    "lawrence":             "#881337",
    "lake":                 "#a16207",
    "jackson-washington":   "#6b21a8",
    "roosevelt":            "#0284c7",
    "marquette":            "#1e40af",
    "83rd":                 "#16a34a",
    // trails
    "lakefront":            "#0369a1",
    "bloomingdale":         "#65a30d",
    "major-taylor":         "#ca8a04",
    "north-shore-channel":  "#0d9488",
    "north-branch":         "#3f6212",
  };
  const FALLBACK_LINE_COLOR = "#334155"; // any line id not in the map

  // Major-route stroke style (spec §5): one solid color per line, weight 6,
  // no dashes, no per-segment styling. Falls back for any line id not yet
  // in LINE_COLORS (new roster additions, typos) rather than drawing nothing.
  function lineStyle(lineId) {
    return { color: LINE_COLORS[lineId] || FALLBACK_LINE_COLOR, weight: 6, opacity: 1 };
  }

  // Quality border (spec §5/§6): a toggleable, per-segment grade-colored
  // casing drawn *around* the constant line color — the swap from the old
  // always-on white-casing/grade-line roles. Weight 13 so it reads as a rim
  // around the weight-6 line + weight-9 white casing. `none` grade (sharrows
  // / unknown) renders dashed — the line exists on paper, not on the street.
  function qualityCasingStyle(grade) {
    const known = Object.prototype.hasOwnProperty.call(GRADE_COLORS, grade);
    const style = { color: known ? GRADE_COLORS[grade] : GRADE_COLORS.none, weight: 13 };
    if (!known || grade === "none") style.dashArray = "6,9";
    return style;
  }

  // Index main_routes.geojson member features: Map<segment_id, {lineId, grade}>.
  function buildRosterIndex(mainRouteFeatures) {
    const idx = new Map();
    (mainRouteFeatures || []).forEach((f) => {
      const p = f.properties || {};
      if (p.segment_id != null && p.line_id) {
        idx.set(String(p.segment_id), { lineId: p.line_id, grade: p.grade });
      }
    });
    return idx;
  }

  // FC-level `lines` metadata array -> Map<line id, line>.
  function linesById(lines) {
    return new Map((lines || []).map((l) => [l.id, l]));
  }

  // Partition network features into roster members (heavy treatment) and
  // the local background network (demoted).
  function splitByRoster(features, rosterIndex) {
    const roster = [];
    const local = [];
    (features || []).forEach((f) => {
      (rosterIndex.has(String(f.properties.segment_id)) ? roster : local).push(f);
    });
    return { roster, local };
  }

  // Features belonging to one roster line, in input order.
  function membersOfLine(features, rosterIndex, lineId) {
    return (features || []).filter((f) => {
      const entry = rosterIndex.get(String(f.properties.segment_id));
      return entry != null && entry.lineId === lineId;
    });
  }

  // Streets that have at least one roster member — those corridors get a
  // line label instead of the generic corridor label.
  function rosterStreets(features, rosterIndex) {
    const streets = new Set();
    (features || []).forEach((f) => {
      if (rosterIndex.has(String(f.properties.segment_id)) && f.properties.street) {
        streets.add(f.properties.street);
      }
    });
    return streets;
  }

  const api = {
    flattenCoords, toLatLngs, getPaddedBBox, pointInBBox,
    groupByCorridor,
    DEFAULT_OVERLAYS, parseOverlays, serializeOverlays,
    GRADE_COLORS, LOCAL_STYLE, CONNECTING_TRAIL_STYLE,
    LINE_COLORS, FALLBACK_LINE_COLOR, lineStyle, qualityCasingStyle,
    buildRosterIndex, linesById, splitByRoster, membersOfLine, rosterStreets,
  };

  root.BSDNet = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
