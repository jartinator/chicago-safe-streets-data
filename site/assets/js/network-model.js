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

  const api = {
    flattenCoords, toLatLngs, getPaddedBBox, pointInBBox,
    countObstructions, heatBucket, groupByCorridor,
    parseOverlays, serializeOverlays,
  };

  root.BSDNet = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
