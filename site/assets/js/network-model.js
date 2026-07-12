/* Pure geometry/aggregation helpers for the Network (metro-map) screen.
 * No DOM, no Leaflet — Node-testable. Exposed as window.BSDNet in the
 * browser, module.exports in Node. Consumed by network.js and (per
 * DECISIONS.md #10 / task-3 overlays) reused for heatBucket/countObstructions. */
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

  // Count obstructions falling within each route segment's padded bbox.
  // Returns Map<segment_id, count>.
  function countObstructions(routeFeatures, obstructionPoints) {
    const counts = new Map();
    routeFeatures.forEach((feature) => {
      const bbox = getPaddedBBox(feature.geometry);
      const count = obstructionPoints.filter((p) => pointInBBox(p, bbox)).length;
      counts.set(feature.properties.segment_id, count);
    });
    return counts;
  }

  // Bucket an obstruction count into a heat tier: null for 0, else a
  // { color, label } tier used for overlay styling and legends.
  function heatBucket(count) {
    if (!count || count <= 0) return null;
    if (count <= 2) return { color: "#fbbf24", label: "1–2" };
    if (count <= 5) return { color: "#f97316", label: "3–5" };
    return { color: "#dc2626", label: "6+" };
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
  const DEFAULT_OVERLAYS = ["heat", "stations", "trails"];

  // Sentinel for "explicitly no overlays": BSD.setParams deletes params
  // whose value is "", so an empty set serialized as "" would vanish from
  // the URL and reload back as the defaults. "none" survives the round-trip.
  const OVERLAYS_NONE = "none";

  // Parse the `overlays` URL param into a Set of overlay ids. `str` is
  // whatever BSD.qs().get("overlays") returns: null when the param is
  // absent (fall back to defaults), the "none" sentinel (empty set), or a
  // comma-joined string ("" also yields an empty set).
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

  // ---- Main routes ("rail vs bus") helpers — spec §4/§7 of
  // docs/superpowers/specs/2026-07-12-main-routes-design.md ----

  // Grade colors, user-ranked offstreet > protected > painted > none.
  // Duplicated from the grade taxonomy rather than imported from
  // main-routes-model.js: network.html only loads this model file.
  const GRADE_COLORS = {
    offstreet: "#0369a1",
    protected: "#0b6e4f",
    painted: "#f59e0b",
    none: "#94a3b8",
  };

  // Demoted local ("bus") network: thin, muted, no casing.
  const LOCAL_STYLE = { color: "#cbd5e1", weight: 1.5, opacity: 0.9 };

  // Heavy metro stroke for a roster line member. `none` grade (sharrows /
  // unknown) renders dashed — the line exists on paper, not on the street.
  function gradeLineStyle(grade) {
    const known = Object.prototype.hasOwnProperty.call(GRADE_COLORS, grade);
    const style = { color: known ? GRADE_COLORS[grade] : GRADE_COLORS.none, weight: 7 };
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

  // Station {lat, lng} vs a list of [[minLat,minLng],[maxLat,maxLng]] bboxes.
  function stationInAnyBBox(station, bboxes) {
    return bboxes.some((b) =>
      station.lat >= b[0][0] && station.lat <= b[1][0] &&
      station.lng >= b[0][1] && station.lng <= b[1][1]
    );
  }

  // Partition stations: on/near a roster line (kept at metro prominence)
  // vs off-roster (declutters with the labels, not before).
  function splitStations(stations, rosterBBoxes) {
    const onRoster = [];
    const offRoster = [];
    (stations || []).forEach((s) => {
      (stationInAnyBBox(s, rosterBBoxes) ? onRoster : offRoster).push(s);
    });
    return { onRoster, offRoster };
  }

  const api = {
    flattenCoords, toLatLngs, getPaddedBBox, pointInBBox,
    countObstructions, heatBucket, groupByCorridor,
    parseOverlays, serializeOverlays,
    GRADE_COLORS, LOCAL_STYLE, gradeLineStyle,
    buildRosterIndex, linesById, splitByRoster, membersOfLine,
    rosterStreets, stationInAnyBBox, splitStations,
  };

  root.BSDNet = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
