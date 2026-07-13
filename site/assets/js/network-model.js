/* Pure geometry/aggregation helpers for the Network (metro-map) screen.
 * No DOM, no Leaflet — Node-testable. Exposed as window.BSDNet in the
 * browser, module.exports in Node. Consumed by network.js.
 *
 * Spec: docs/superpowers/specs/2026-07-13-network-tiers-design.md (v2 —
 * tiers, comfort floor, quality regrade). Supersedes the layer/toggle/
 * coloring parts of 2026-07-12-network-map-distinction.md; this file keeps
 * that spec's node derivation and geometry helpers unchanged (§11).
 * The network map's concerns (v2 §1): three tiers (trails / main routes /
 * connectors), an opt-in quality border, and an opt-in comfort floor. No
 * safety data lives here — that's the transportation map's job (index.html
 * / map.js). */
(function (root) {
  // BSD.mixSegments (common.js) backs qualityMixSegments below — common.js is
  // loaded before this file in every page that uses it (network.html); in
  // Node, common.js isn't required by the test harness ahead of time, so
  // pull it in directly there (same pattern main-routes-model.js uses).
  const BSD = (typeof module !== "undefined" && module.exports)
    ? require("./common.js")
    : root.BSD;

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

  // Union of getPaddedBBox across a feature list, merged into one
  // [[minLat, minLng], [maxLat, maxLng]] bbox — the same reduce network.js
  // repeated at three fitBounds call sites (single line, full network,
  // corridor deep link). Empty input -> [] (matches the bare reduce's
  // behavior with no initial value's equivalent no-op).
  function unionBBox(features) {
    return (features || []).map((f) => getPaddedBBox(f.geometry))
      .reduce((acc, bbox) => {
        if (acc.length === 0) return bbox;
        return [
          [Math.min(acc[0][0], bbox[0][0]), Math.min(acc[0][1], bbox[0][1])],
          [Math.max(acc[1][0], bbox[1][0]), Math.max(acc[1][1], bbox[1][1])],
        ];
      }, []);
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

  // Node visibility/declutter zoom thresholds: interchanges read at city
  // scale; orientation points wait for street level. Corridor labels for
  // connector-tier streets share the orientation threshold, and street-line
  // name labels (collision-prone downtown) share the interchange threshold
  // — trails stay labeled at every zoom.
  const ZOOM = {
    interchangeNodes: 11,
    lineLabels: 11,
    corridorLabels: 13,
  };

  // Default overlay ids enabled when network.html has no ?overlays= param
  // (design v2 §10): all three tiers on, quality off, nodes on, planned off.
  const DEFAULT_OVERLAYS = ["trails", "main", "connectors", "nodes"];

  // Sentinel for "explicitly no overlays": BSD.setParams deletes params
  // whose value is "", so an empty set serialized as "" would vanish from
  // the URL and reload back as the defaults. "none" survives the round-trip.
  const OVERLAYS_NONE = "none";

  // Parse the `overlays` URL param into a Set of overlay ids. `str` is
  // whatever BSD.qs().get("overlays") returns: null when the param is
  // absent (fall back to defaults), the "none" sentinel (empty set), or a
  // comma-joined string ("" also yields an empty set). Legacy ids from the
  // pre-v2 map (e.g. "connecting", "mellow") are not filtered here —
  // network.js simply never looks them up, so they're silently ignored
  // per spec v2 §10.
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

  // ---- Main routes ("rail vs bus") helpers — spec v2 §1/§2/§3/§9 ----

  // One solid color per named line (spec §9) — the 14 street + 7 trail
  // roster, exactly as listed. roosevelt/vincennes are demoted to
  // connectors (spec §2) and carry no line color; 312-riverrun and
  // green-bay joined the trail roster after the spec (DECISIONS.md #26/#27).
  const LINE_COLORS = {
    // street lines
    "milwaukee":            "#1d4ed8",
    "elston":               "#ea580c",
    "halsted":              "#dc2626",
    "damen":                "#eab308",
    "kedzie":               "#7c3aed",
    "california":           "#db2777",
    "clark":                "#0891b2",
    "state-indiana":        "#4d7c0f",
    "mlk-drive":            "#92400e",
    "jackson-washington":   "#6b21a8",
    "lawrence":             "#881337",
    "marquette":            "#1e40af",
    "lake":                 "#a16207",
    "83rd":                 "#15803d",
    // trails
    "lakefront":            "#0369a1",
    "bloomingdale":         "#16a34a",
    "major-taylor":         "#ca8a04",
    "north-shore-channel":  "#0d9488",
    "north-branch":         "#3f6212",
    "312-riverrun":         "#4f46e5",
    "green-bay":            "#a21caf",
  };
  const FALLBACK_LINE_COLOR = "#334155"; // any line id not in the map

  // ---- Tier styles (spec §1) ----

  // Main routes: one solid color per line, weight 6, white casing (drawn
  // separately by network.js at weight 9). Falls back for any line id not
  // yet in LINE_COLORS (new roster additions, typos) rather than drawing
  // nothing.
  function lineStyle(lineId) {
    return { color: LINE_COLORS[lineId] || FALLBACK_LINE_COLOR, weight: 6, opacity: 1 };
  }

  // Darken a "#rrggbb" hex color by `amount` (0-1 fraction). Used to derive
  // a trail's outline color from its line color (spec §1: "darkened-hue
  // outline" instead of a white casing) so trails read as their own,
  // heavier "express" tier rather than main-route lookalikes. Unknown/bad
  // input returns the input unchanged rather than throwing.
  function darkenColor(hex, amount) {
    const m = /^#([0-9a-f]{6})$/i.exec(hex || "");
    if (!m) return hex;
    const num = parseInt(m[1], 16);
    const r = (num >> 16) & 255, g = (num >> 8) & 255, b = num & 255;
    const scale = Math.max(0, Math.min(1, 1 - amount));
    const toHex = (v) => Math.round(v * scale).toString(16).padStart(2, "0");
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }
  const TRAIL_OUTLINE_DARKEN = 0.35;

  // Trails (spec §1): weight 11 core stroke in the line color, drawn over a
  // slightly wider outline stroke in a darkened shade of the same color
  // (not white — trails are their own "express" tier, not a main-route
  // lookalike).
  function trailStyle(lineId) {
    return { color: LINE_COLORS[lineId] || FALLBACK_LINE_COLOR, weight: 11, opacity: 1 };
  }
  function trailOutlineStyle(lineId) {
    const base = LINE_COLORS[lineId] || FALLBACK_LINE_COLOR;
    return { color: darkenColor(base, TRAIL_OUTLINE_DARKEN), weight: 15, opacity: 1 };
  }

  // Connectors (spec §1): everything rideable that isn't a roster trail or
  // main route — non-roster bike_routes, deduped mellow geometry
  // (mellow_connectors.geojson), and non-roster named OSM trails. One
  // style for all three sources: thin, dashed, neutral, identity-less.
  const CONNECTOR_STYLE = { color: "#94a3b8", weight: 2.5, opacity: 0.75, dashArray: "4,5" };

  // ---- Quality border (spec §3) ----

  // Border colors per grade. `offstreet` (trail members) intentionally has
  // no entry — trails never carry a quality border (they're off-street by
  // definition; see qualityBorderStyle).
  const GRADE_COLORS = {
    protected: "#0b6e4f",
    paint: "#0b6e4f",
    mellow: "#7c3aed",
    none: "#dc2626",
  };
  const GRADE_DASHED = new Set(["paint", "none"]);

  // Quality-border style for a main-route segment's grade, or null when no
  // border should render (`offstreet` — trails are off-street, no border
  // needed; borders only make sense on main/street routes). Unrecognized
  // grades fall back to the `none` treatment (dashed red) rather than
  // drawing nothing, so a data/taxonomy mismatch is loud, not silent.
  // Weight 13 so it reads as a rim around the weight-6 line + weight-9
  // white casing (same geometry as the v1 layer it replaces).
  function qualityBorderStyle(grade) {
    if (grade === "offstreet") return null;
    const known = Object.prototype.hasOwnProperty.call(GRADE_COLORS, grade);
    const effective = known ? grade : "none";
    const style = { color: GRADE_COLORS[effective], weight: 13 };
    if (GRADE_DASHED.has(effective)) style.dashArray = "6,6";
    return style;
  }

  // ---- Comfort floor (spec §5) ----

  // Grade rank, worst to best: none < mellow < paint < protected < offstreet.
  const GRADE_RANK = { none: 0, mellow: 1, paint: 2, protected: 3, offstreet: 4 };
  function gradeRank(grade) {
    return Object.prototype.hasOwnProperty.call(GRADE_RANK, grade) ? GRADE_RANK[grade] : -1;
  }

  const FLOOR_IDS = ["any", "paint", "protected"];
  // Parse the `?floor=` URL param: only "paint" and "protected" are
  // recognized; anything else (missing, "any", garbage) is the default,
  // permissive "any" floor.
  function parseFloor(str) {
    return str === "paint" || str === "protected" ? str : "any";
  }

  // Does `grade` meet or exceed `floor`? Always true for floor "any" (or
  // anything that parses to it). A grade this function has never heard of
  // ranks below everything, so it never slips through a real floor.
  function meetsFloor(grade, floor) {
    const f = parseFloor(floor);
    if (f === "any") return true;
    return gradeRank(grade) >= GRADE_RANK[f];
  }

  // Below-floor main-route stretches drain to this neutral core color
  // (spec §5): 3px solid, no border, geometry continuous — the route never
  // breaks, it just stops being colored.
  const DRAINED_COLOR = "#b6bec9";
  const DRAINED_STYLE = { color: DRAINED_COLOR, weight: 3, opacity: 1 };

  // ---- Quality mix (spec §7/§8: detail card + roster row mini-bar) ----

  // The four *bordered* grades, in a fixed display order (best to worst on
  // the ground, not the floor-ranking order): protected, paint, mellow,
  // none. Deliberately excludes `offstreet` — this bar is about main-route
  // quality, and trail lines (100% offstreet) get their own card copy
  // instead of a mix bar.
  const QUALITY_MIX_ORDER = ["protected", "paint", "mellow", "none"];

  // Stacked mix-bar segments from a line's miles_by_grade: one entry per
  // non-zero grade among QUALITY_MIX_ORDER, with pct width of *that* total
  // (widths sum to 100). Scoped to the four bordered grades only. Thin
  // wrapper around the shared BSD.mixSegments (common.js), which also backs
  // BSDMainRoutes.completionSegments — same stacked-bar math, different
  // grade order/colors/no per-segment label.
  function qualityMixSegments(milesByGrade) {
    return BSD.mixSegments(milesByGrade, QUALITY_MIX_ORDER, { colors: GRADE_COLORS });
  }

  // Index main_routes.geojson member features: Map<segment_id, {lineIds, lineId, grade}>.
  // A segment normally belongs to exactly one line (`lineIds` has length 1);
  // shared-track ("interlined") segments carry 2+ ids in `line_ids` (spec
  // §6) and this index preserves all of them. `lineId` (singular, first of
  // `lineIds`) is kept for call sites that only need "a" line for this
  // segment (e.g. legacy corridor lookups); anything that needs to know
  // about sharing must use `lineIds`.
  function buildRosterIndex(mainRouteFeatures) {
    const idx = new Map();
    (mainRouteFeatures || []).forEach((f) => {
      const p = f.properties || {};
      const lineIds = Array.isArray(p.line_ids) && p.line_ids.length > 0
        ? p.line_ids.slice()
        : (p.line_id ? [p.line_id] : []);
      if (p.segment_id != null && lineIds.length > 0) {
        idx.set(String(p.segment_id), { lineIds, lineId: lineIds[0], grade: p.grade });
      }
    });
    return idx;
  }

  // FC-level `lines` metadata array -> Map<line id, line>.
  function linesById(lines) {
    return new Map((lines || []).map((l) => [l.id, l]));
  }

  // Partition network features into roster members (heavy treatment) and
  // the connector-tier background network.
  function splitByRoster(features, rosterIndex) {
    const roster = [];
    const local = [];
    (features || []).forEach((f) => {
      (rosterIndex.has(String(f.properties.segment_id)) ? roster : local).push(f);
    });
    return { roster, local };
  }

  // Features belonging to one roster line, in input order. A shared
  // ("interlined") segment belongs to every line in its `line_ids` — this
  // returns it for each of them, so per-line bounds/labels still include it.
  function membersOfLine(features, rosterIndex, lineId) {
    return (features || []).filter((f) => {
      const entry = rosterIndex.get(String(f.properties.segment_id));
      return entry != null && entry.lineIds.includes(lineId);
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

  // ---- Interlining (spec §6): shared-track render-plan helpers ----
  // Pure geometry only — no Leaflet objects are created here. network.js
  // turns the plan this produces into actual polylines/markers. Kept pure
  // so the offset math and endpoint logic are Node-testable without a
  // browser, per spec §6 ("unit-test the offset helper in tests/ui").

  const METERS_PER_DEG_LAT = 111320;
  function metersPerDegLng(lat) {
    return METERS_PER_DEG_LAT * Math.cos((lat * Math.PI) / 180) || 1;
  }

  // True when `latlngs` is a MultiLineString-shaped nested array (parts of
  // points) rather than a single flat array of points, matching toLatLngs's
  // two possible shapes.
  function isMultiPart(latlngs) {
    return Array.isArray(latlngs) && Array.isArray(latlngs[0]) && Array.isArray(latlngs[0][0]);
  }

  // Offset one flat [lat,lng][] path perpendicular to its local direction
  // by `offsetMeters` (signed — sign picks the side). Direction at each
  // vertex is estimated from its immediate neighbors, which keeps the
  // offset path roughly parallel around gentle bends; this is a render-time
  // approximation (not a true parallel-curve construction), which is all
  // spec §6 asks for ("geographic offset via a small helper is fine at
  // these zooms").
  function offsetPart(part, offsetMeters) {
    if (!part || part.length === 0) return [];
    if (!offsetMeters) return part.map(([lat, lng]) => [lat, lng]);
    return part.map(([lat, lng], i) => {
      const prev = part[Math.max(0, i - 1)];
      const next = part[Math.min(part.length - 1, i + 1)];
      const dLat = next[0] - prev[0];
      const dLng = next[1] - prev[1];
      const len = Math.hypot(dLat, dLng) || 1;
      // Rotate the local direction vector 90°: (dLat, dLng) -> (-dLng, dLat).
      const perpLat = -dLng / len;
      const perpLng = dLat / len;
      const offLat = (offsetMeters / METERS_PER_DEG_LAT) * perpLat;
      const offLng = (offsetMeters / metersPerDegLng(lat)) * perpLng;
      return [lat + offLat, lng + offLng];
    });
  }

  // Offset a toLatLngs()-shaped geometry (flat or multi-part) perpendicular
  // by `offsetMeters`, preserving its shape.
  function offsetLatLngs(latlngs, offsetMeters) {
    if (isMultiPart(latlngs)) return latlngs.map((part) => offsetPart(part, offsetMeters));
    return offsetPart(latlngs, offsetMeters);
  }

  const INTERLINE_GAP_METERS = 2.2;

  // Symmetric per-strand offsets (meters), one per parallel strand sharing
  // a track, spaced `gapMeters` apart center-to-center and centered on 0
  // (e.g. count=2 -> [-gap/2, +gap/2]; count=3 -> [-gap, 0, +gap]).
  function strandOffsets(count, gapMeters) {
    const gap = gapMeters == null ? INTERLINE_GAP_METERS : gapMeters;
    const mid = (count - 1) / 2;
    return Array.from({ length: count }, (_, i) => (i - mid) * gap);
  }

  // First and last vertex of a (possibly multi-part) latlng geometry —
  // where capsule transfer markers sit for a shared run (spec §6).
  function pathEndpoints(latlngs) {
    const parts = isMultiPart(latlngs) ? latlngs : [latlngs];
    const first = parts[0][0];
    const last = parts[parts.length - 1][parts[parts.length - 1].length - 1];
    return [first, last];
  }

  // Pure render plan for an interlined (2+ line_ids) main-route feature: N
  // parallel offset strands (one per line, in `lineIds` order), one shared
  // white casing at zero offset (drawn by network.js), one shared quality
  // border (from qualityBorderStyle(grade) — null when the shared grade is
  // offstreet, though that never happens for street-line interlining), and
  // capsule marker points at both ends of the shared run.
  // `colorFor(lineId)` looks up each strand's line color — injected so this
  // stays a pure function with no import-ordering dependency on LINE_COLORS.
  function planInterlinedRoute(latlngs, lineIds, grade, colorFor, gapMeters) {
    const offsets = strandOffsets(lineIds.length, gapMeters);
    const strands = lineIds.map((lineId, i) => ({
      lineId,
      color: colorFor(lineId),
      latlngs: offsetLatLngs(latlngs, offsets[i]),
    }));
    return {
      strands,
      casing: { latlngs },
      border: qualityBorderStyle(grade),
      capsules: pathEndpoints(latlngs),
    };
  }

  const api = {
    flattenCoords, toLatLngs, getPaddedBBox, unionBBox,
    groupByCorridor,
    ZOOM,
    DEFAULT_OVERLAYS, parseOverlays, serializeOverlays,
    LINE_COLORS, FALLBACK_LINE_COLOR, lineStyle,
    darkenColor, trailStyle, trailOutlineStyle,
    CONNECTOR_STYLE,
    GRADE_COLORS, qualityBorderStyle,
    GRADE_RANK, gradeRank, FLOOR_IDS, parseFloor, meetsFloor,
    DRAINED_COLOR, DRAINED_STYLE,
    QUALITY_MIX_ORDER, qualityMixSegments,
    buildRosterIndex, linesById, splitByRoster, membersOfLine, rosterStreets,
    isMultiPart, offsetPart, offsetLatLngs, strandOffsets, pathEndpoints,
    planInterlinedRoute, INTERLINE_GAP_METERS,
  };

  root.BSDNet = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
