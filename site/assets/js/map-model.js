/* Pure geometry/aggregation helpers for the geographic map's zoom-adaptive
 * density rendering. No DOM, no Leaflet — Node-testable. Exposed as
 * window.BSDMap in the browser, module.exports in Node. Consumed by map.js
 * to render tight, route-hugging density dots (instead of individual
 * markers) when zoomed out past DETAIL_ZOOM. */
(function (root) {
  // Grid-bin Point features (GeoJSON [lng, lat] coordinates) into cells of
  // cellDeg degrees (~111 m lat / ~83 m lng in Chicago — deliberately fine
  // so density hugs streets rather than smearing into blobs). Returns cell
  // centers with their point counts. Deterministic: cell index =
  // Math.floor(coord / cellDeg), center = (index + 0.5) * cellDeg.
  function binPoints(features, cellDeg = 0.001) {
    const cells = new Map();
    features.forEach((f) => {
      const [lng, lat] = f.geometry.coordinates;
      const ix = Math.floor(lng / cellDeg);
      const iy = Math.floor(lat / cellDeg);
      const key = `${ix},${iy}`;
      const existing = cells.get(key);
      if (existing) {
        existing.count += 1;
      } else {
        cells.set(key, {
          lat: (iy + 0.5) * cellDeg,
          lng: (ix + 0.5) * cellDeg,
          count: 1,
        });
      }
    });
    return [...cells.values()];
  }

  // Color ramps for density dots, keyed by layer id.
  const DENSITY_RAMPS = {
    crashes: ["#fecaca", "#f87171", "#dc2626", "#7f1d1d"],
    obstructions: ["#fde68a", "#fbbf24", "#f97316", "#b91c1c"],
  };

  // Pick a ramp step by count / maxCount quartile.
  function rampColor(count, maxCount, ramp) {
    if (maxCount <= 0) return ramp[0];
    const frac = count / maxCount;
    if (frac <= 0.25) return ramp[0];
    if (frac <= 0.5) return ramp[1];
    if (frac <= 0.75) return ramp[2];
    return ramp[3];
  }

  // Dot radius for a density cell, hard-capped at 9px so the rendering
  // stays tight (never a large diffuse blob) regardless of cell count.
  function densityRadius(count) {
    return Math.min(3 + Math.sqrt(count) * 1.2, 9);
  }

  const api = { binPoints, DENSITY_RAMPS, rampColor, densityRadius };

  root.BSDMap = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
