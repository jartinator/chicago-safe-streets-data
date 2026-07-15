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

  // Default overlay ids enabled when network.html has no ?overlays= param:
  // trails + main + nodes on; connectors (background mesh), quality and
  // planned off. Connectors default off so the metro lines read clean —
  // the toggle brings the mesh back.
  const DEFAULT_OVERLAYS = ["trails", "main", "nodes"];

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

  // Trails (spec §1): core stroke in the line color, drawn over a slightly
  // wider outline stroke in a darkened shade of the same color (not white —
  // trails are their own "express" tier, not a main-route lookalike).
  // Weight 6 over 9 — the same weights as main routes' line/casing, DC-metro
  // style: every roster line is one uniform stroke, and the tiers read by
  // outline treatment (darkened hue vs. white) rather than by bulk.
  function trailStyle(lineId) {
    return { color: LINE_COLORS[lineId] || FALLBACK_LINE_COLOR, weight: 6, opacity: 1 };
  }
  function trailOutlineStyle(lineId) {
    const base = LINE_COLORS[lineId] || FALLBACK_LINE_COLOR;
    return { color: darkenColor(base, TRAIL_OUTLINE_DARKEN), weight: 9, opacity: 1 };
  }

  // Lighten a "#rrggbb" hex color toward white by `amount` (0-1 fraction).
  // darkenColor's mirror — used for gap-filler strokes (a paler shade of the
  // line color, so a filled gap reads as "the line continues here" without
  // pretending to be surveyed geometry). Bad input passes through unchanged.
  function lightenColor(hex, amount) {
    const m = /^#([0-9a-f]{6})$/i.exec(hex || "");
    if (!m) return hex;
    const num = parseInt(m[1], 16);
    const t = Math.max(0, Math.min(1, amount));
    const mix = (v) => Math.round(v + (255 - v) * t).toString(16).padStart(2, "0");
    return `#${mix((num >> 16) & 255)}${mix((num >> 8) & 255)}${mix(num & 255)}`;
  }

  // Constant-pixel strokes are sized for street zoom, so at the citywide
  // fit they crowd into each other — the "smudge" read. Scale every stroke
  // weight by this factor instead: 0.6 at z<=11, 1 from z>=13 (0.2/step
  // between). network.js re-applies it on zoomend via the restyle path.
  function zoomWeightFactor(z) {
    if (!Number.isFinite(z)) return 1;
    return Math.max(0.6, Math.min(1, 0.6 + (z - 11) * 0.2));
  }

  // Connectors (spec §1, amended §12): everything rideable that isn't a
  // roster trail or main route — non-roster bike_routes, deduped mellow
  // geometry (mellow_connectors.geojson), and non-roster named OSM trails.
  // Weight/opacity/base geometry are one style for all three sources (thin,
  // identity-less background mesh) — that part is unchanged. What §12
  // changed: each feature now also carries a per-feature comfort grade,
  // styled by connectorStyle() below with a muted hue + dash tint instead
  // of one flat neutral look.
  const CONNECTOR_STYLE = { color: "#94a3b8", weight: 2.5, opacity: 0.75, dashArray: "4,5" };

  // Per-grade connector tint (spec §12, "Option C" hybrid hue + pattern):
  // muted tints echo the §3 grade colors; dash pattern is the redundant,
  // colorblind-safe channel. Solid reads calm (protected, offstreet);
  // dashed marks a partial/no claim (paint, mellow, none). `none`'s
  // color/dash match CONNECTOR_STYLE's pre-existing look exactly —
  // "today's look, unchanged" per the spec table.
  const CONNECTOR_GRADE_TINTS = {
    protected: { color: "#4d8873", dashArray: null },
    paint: { color: "#4d8873", dashArray: "4,5" },
    mellow: { color: "#9a8fc9", dashArray: "4,5" },
    none: { color: "#94a3b8", dashArray: "4,5" },
    offstreet: { color: "#94a3b8", dashArray: null },
  };

  // Connector style for a per-feature comfort grade (spec §12): inherits
  // CONNECTOR_STYLE's weight/opacity (the subtle background effect is
  // unchanged) and swaps in the grade's color/dash tint. Unrecognized
  // grades fall back to the `none` treatment (loud-not-silent, same
  // rationale as qualityBorderStyle) rather than drawing nothing.
  function connectorStyle(grade) {
    const known = Object.prototype.hasOwnProperty.call(CONNECTOR_GRADE_TINTS, grade);
    const tint = CONNECTOR_GRADE_TINTS[known ? grade : "none"];
    return { ...CONNECTOR_STYLE, color: tint.color, dashArray: tint.dashArray };
  }

  // ---- Quality colors (mix bars / legend swatches only — spec v3 §4/§9) ----
  // The v2 quality-border layer is gone (quality is structural now, §4);
  // these colors survive as the mix-bar and legend palette. `nothing`
  // deliberately reuses the neutral slate — a missing bikeway is an
  // absence, not a red alarm (v3 §4.5: no red, no dash).
  const GRADE_COLORS = {
    protected: "#0b6e4f",
    paint: "#0b6e4f",
    mellow: "#7c3aed",
    none: "#94a3b8",
  };

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

  // Below-floor stretches drain hue to this neutral color at FULL
  // silhouette width and SCHEMATIC.drainedOpacity (v3 §4.4) — "routes never
  // break" is literally true: the structural fill stays, only the color
  // leaves. (The v2 thin-3px DRAINED_STYLE is gone with the border layer.)
  const DRAINED_COLOR = "#b6bec9";

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

  // ---- Render-time geometry straightening ----
  // Raw CDOT/OSM geometry carries a vertex every few meters; drawn at
  // metro-map stroke widths that jitter reads as smudge, not route. At draw
  // time we run Ramer–Douglas–Peucker in meter space (equirectangular
  // approximation — fine at city scale): drop every vertex that deviates
  // less than `toleranceMeters` from the straight line between its kept
  // neighbors. Endpoints always survive, so segment-to-segment continuity
  // is preserved; vertices are only dropped, never moved or invented
  // (DECISIONS.md #10 — still real geometry, just decluttered).

  // Perpendicular distance (meters) from point p to segment a-b, all in
  // pre-projected [x, y] meter coordinates.
  function pointSegDistance(p, a, b) {
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const lenSq = dx * dx + dy * dy;
    let t = lenSq === 0 ? 0 : ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / lenSq;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
  }

  // RDP over one flat [lat,lng][] part. Iterative (explicit stack) so a
  // multi-thousand-vertex trail can't blow the call stack.
  function simplifyPart(part, toleranceMeters) {
    if (!part || part.length <= 2 || !toleranceMeters) return (part || []).slice();
    const mLng = metersPerDegLng(part[0][0]);
    const pts = part.map(([lat, lng]) => [lng * mLng, lat * METERS_PER_DEG_LAT]);
    const keep = new Array(part.length).fill(false);
    keep[0] = keep[part.length - 1] = true;
    const stack = [[0, part.length - 1]];
    while (stack.length > 0) {
      const [s, e] = stack.pop();
      let maxDist = -1, maxIdx = -1;
      for (let i = s + 1; i < e; i++) {
        const d = pointSegDistance(pts[i], pts[s], pts[e]);
        if (d > maxDist) { maxDist = d; maxIdx = i; }
      }
      if (maxDist > toleranceMeters) {
        keep[maxIdx] = true;
        stack.push([s, maxIdx], [maxIdx, e]);
      }
    }
    return part.filter((_, i) => keep[i]);
  }

  // Simplify a toLatLngs()-shaped geometry (flat or multi-part),
  // preserving its shape.
  function simplifyLatLngs(latlngs, toleranceMeters) {
    if (isMultiPart(latlngs)) return latlngs.map((part) => simplifyPart(part, toleranceMeters));
    return simplifyPart(latlngs, toleranceMeters);
  }

  // One tolerance for every drawn tier. ~40 m is invisible at the citywide
  // fit (~57 m/px at z11) and straightens block-level jitter at street
  // zooms without detaching lines from their corridors.
  const SIMPLIFY_TOLERANCE_METERS = 40;

  // toLatLngs + simplify in one call — what network.js draws with.
  function schematicLatLngs(geometry) {
    return simplifyLatLngs(toLatLngs(geometry), SIMPLIFY_TOLERANCE_METERS);
  }

  // ---- Gap fillers: visual continuity for disjoint roster lines ----
  // A roster line's member segments don't always touch — the source data
  // has real holes, so a "line" can render as dashes of itself. Metro-map
  // read demands one continuous stroke, so network.js bridges the holes
  // with straight, lighter-colored connector strokes. This helper finds
  // them: greedily chain a line's parts end-to-end (nearest unused
  // endpoint next), and every join wider than `joinToleranceMeters`
  // becomes a gap segment [[lat,lng],[lat,lng]]. Straight-line bridges are
  // honest here: the lighter color marks them as inferred continuity, not
  // surveyed geometry.

  function distMeters(a, b) {
    const mLng = metersPerDegLng((a[0] + b[0]) / 2);
    return Math.hypot((a[0] - b[0]) * METERS_PER_DEG_LAT, (a[1] - b[1]) * mLng);
  }

  const GAP_JOIN_TOLERANCE_METERS = 30;

  // Chain parts by greedy nearest-endpoint walk, starting from the
  // endpoint farthest from the endpoint centroid (terminus-to-terminus,
  // not out from the middle). Handles a trail's parallel/overlapping side
  // branches well (walks up one branch and back down the other), but can
  // ping-pong on long diagonal corridors. Returns the joins plus the
  // chain's two overall termini.
  function chainGreedy(usable) {
    const endpoints = [];
    usable.forEach((p, i) => {
      endpoints.push({ i, pt: p[0], other: p[p.length - 1] });
      endpoints.push({ i, pt: p[p.length - 1], other: p[0] });
    });
    const cLat = endpoints.reduce((s, e) => s + e.pt[0], 0) / endpoints.length;
    const cLng = endpoints.reduce((s, e) => s + e.pt[1], 0) / endpoints.length;
    let start = endpoints[0], startDist = -1;
    endpoints.forEach((e) => {
      const d = distMeters(e.pt, [cLat, cLng]);
      if (d > startDist) { startDist = d; start = e; }
    });

    const used = new Array(usable.length).fill(false);
    used[start.i] = true;
    let end = start.other;
    const joins = [];
    for (let k = 1; k < usable.length; k++) {
      let bestI = -1, bestDist = Infinity, bestFlip = false;
      usable.forEach((p, i) => {
        if (used[i]) return;
        const dHead = distMeters(end, p[0]);
        const dTail = distMeters(end, p[p.length - 1]);
        if (dHead < bestDist) { bestDist = dHead; bestI = i; bestFlip = false; }
        if (dTail < bestDist) { bestDist = dTail; bestI = i; bestFlip = true; }
      });
      const p = usable[bestI];
      joins.push([end, bestFlip ? p[p.length - 1] : p[0]]);
      end = bestFlip ? p[0] : p[p.length - 1];
      used[bestI] = true;
    }
    return { joins, head: start.pt, tail: end };
  }

  // Chain parts by their projection onto the endpoint cloud's principal
  // axis. Robust for straight/diagonal corridors (no ping-pong), but
  // interleaves a trail's parallel branches into ladder rungs.
  function chainByAxis(usable) {
    const pts = [];
    usable.forEach((p) => { pts.push(p[0], p[p.length - 1]); });
    const cLat = pts.reduce((s, p) => s + p[0], 0) / pts.length;
    const cLng = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    let sxx = 0, sxy = 0, syy = 0;
    pts.forEach((p) => {
      const dy = p[0] - cLat, dx = p[1] - cLng;
      sxx += dx * dx; sxy += dx * dy; syy += dy * dy;
    });
    const theta = 0.5 * Math.atan2(2 * sxy, sxx - syy);
    const ux = Math.cos(theta), uy = Math.sin(theta);
    const proj = (p) => (p[1] - cLng) * ux + (p[0] - cLat) * uy;
    const ordered = usable.map((p) => {
      const a = proj(p[0]), b = proj(p[p.length - 1]);
      return {
        lo: Math.min(a, b),
        head: a <= b ? p[0] : p[p.length - 1],
        tail: a <= b ? p[p.length - 1] : p[0],
      };
    }).sort((A, B) => A.lo - B.lo);
    const joins = [];
    for (let i = 1; i < ordered.length; i++) {
      joins.push([ordered[i - 1].tail, ordered[i].head]);
    }
    return { joins, head: ordered[0].head, tail: ordered[ordered.length - 1].tail };
  }

  // Neither chaining strategy wins everywhere, so run both and keep
  // whichever bridges the line with less total added ink (tie: fewer
  // bridges). On this repo's data the two agree on every straightforward
  // street line and each covers the other's failure mode. Returns
  // { gaps, termini: [chainStart, chainEnd] }.
  function chainPlan(parts, joinToleranceMeters) {
    const tol = joinToleranceMeters == null ? GAP_JOIN_TOLERANCE_METERS : joinToleranceMeters;
    const usable = (parts || []).filter((p) => p && p.length >= 2);
    if (usable.length === 0) return { gaps: [], termini: null };
    if (usable.length === 1) {
      const p = usable[0];
      return { gaps: [], termini: [p[0], p[p.length - 1]] };
    }
    const candidates = [chainGreedy(usable), chainByAxis(usable)].map((chain) => {
      const gaps = chain.joins.filter(([a, b]) => distMeters(a, b) > tol);
      const total = gaps.reduce((s, [a, b]) => s + distMeters(a, b), 0);
      return { gaps, total, termini: [chain.head, chain.tail] };
    });
    candidates.sort((a, b) => a.total - b.total || a.gaps.length - b.gaps.length);
    return { gaps: candidates[0].gaps, termini: candidates[0].termini };
  }


  // ---- Cross-street continuity for multi-street lines ----
  // A line built from several streets (the Jackson–Washington couplet,
  // Clark's Dearborn tail, the downtown Randolph trunk approaches) chains
  // gaps per street, so the couplet never zigzags between its two
  // parallels. Streets then connect to each other with at most ONE feeder
  // bridge per street pair — terminus of one street to the nearest point
  // on the other — and only when the two chains don't already touch or
  // cross, and the feeder isn't longer than `maxFeederMeters` (a couplet's
  // far-apart western ends shouldn't get a phantom crosstown rung).

  function segsCross(p1, p2, p3, p4) {
    const ccw = (a, b, c) => (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0]);
    const d1 = ccw(p3, p4, p1), d2 = ccw(p3, p4, p2);
    const d3 = ccw(p1, p2, p3), d4 = ccw(p1, p2, p4);
    return ((d1 > 0) !== (d2 > 0)) && ((d3 > 0) !== (d4 > 0));
  }

  // Nearest point on any of `segs` (list of [[lat,lng],[lat,lng]]) to `pt`,
  // as { pt: [lat,lng], dist: meters } — meter-space projection around pt.
  function nearestOnChain(pt, segs) {
    const mLng = metersPerDegLng(pt[0]);
    const toM = (p) => [p[1] * mLng, p[0] * METERS_PER_DEG_LAT];
    const pm = toM(pt);
    let best = null;
    segs.forEach(([a, b]) => {
      const am = toM(a), bm = toM(b);
      const dx = bm[0] - am[0], dy = bm[1] - am[1];
      const lenSq = dx * dx + dy * dy;
      let t = lenSq === 0 ? 0 : ((pm[0] - am[0]) * dx + (pm[1] - am[1]) * dy) / lenSq;
      t = Math.max(0, Math.min(1, t));
      const qx = am[0] + t * dx, qy = am[1] + t * dy;
      const dist = Math.hypot(pm[0] - qx, pm[1] - qy);
      if (best == null || dist < best.dist) {
        best = { dist, pt: [qy / METERS_PER_DEG_LAT, qx / mLng] };
      }
    });
    return best;
  }

  const CROSS_STREET_MAX_FEEDER_METERS = 1200;

  // partsByStreet: array of part-lists, one per street of the line.
  // Returns feeder gap segments [[lat,lng],[lat,lng]].
  function crossStreetGaps(partsByStreet, joinToleranceMeters, maxFeederMeters) {
    const tol = joinToleranceMeters == null ? GAP_JOIN_TOLERANCE_METERS : joinToleranceMeters;
    const maxFeeder = maxFeederMeters == null ? CROSS_STREET_MAX_FEEDER_METERS : maxFeederMeters;
    const chains = (partsByStreet || []).map((parts) => {
      const usable = (parts || []).filter((p) => p && p.length >= 2);
      if (usable.length === 0) return null;
      const segs = [];
      usable.forEach((p) => {
        for (let i = 0; i < p.length - 1; i++) segs.push([p[i], p[i + 1]]);
      });
      return { termini: chainPlan(usable, tol).termini, segs };
    }).filter(Boolean);
    if (chains.length <= 1) return [];

    const gaps = [];
    for (let i = 0; i < chains.length; i++) {
      for (let j = i + 1; j < chains.length; j++) {
        const A = chains[i], B = chains[j];
        let best = null;
        [[A, B], [B, A]].forEach(([from, to]) => {
          from.termini.forEach((t) => {
            const hit = nearestOnChain(t, to.segs);
            if (hit && (best == null || hit.dist < best.dist)) {
              best = { dist: hit.dist, gap: [t, hit.pt] };
            }
          });
        });
        if (!best || best.dist <= tol || best.dist > maxFeeder) continue;
        const cross = A.segs.some(([a1, a2]) => B.segs.some(([b1, b2]) => segsCross(a1, a2, b1, b2)));
        if (cross) continue; // chains intersect — already connected
        gaps.push(best.gap);
      }
    }
    return gaps;
  }

  // facility_category -> comfort grade for connector-tier bike_routes
  // segments (same buckets the pipeline's MAIN_ROUTE_GRADE_MAP uses). The
  // v2 Dijkstra gap router that lived alongside this map is gone (v3 §10):
  // a spine just continues through its holes as `nothing`, so there is no
  // gap to route.
  const CONNECTOR_GRADE_MAP = {
    protected: "protected", buffered: "paint", painted: "paint",
    greenway: "mellow", trail: "offstreet",
  };

  function pathLengthMeters(part) {
    let sum = 0;
    for (let i = 1; i < part.length; i++) sum += distMeters(part[i - 1], part[i]);
    return sum;
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

  // Interlined strands must stay visually separated at every zoom, so the
  // render-time strand gap is set in PIXELS and converted to meters at the
  // current zoom (network.js re-offsets on zoomend). This deliberately
  // widens shared runs beyond their true geography at overview zooms —
  // the DC-metro read the network screen aims for.
  const INTERLINE_GAP_PX = 3;
  function metersPerPixel(lat, zoom) {
    return (156543.03392 * Math.cos((lat * Math.PI) / 180)) / Math.pow(2, zoom);
  }

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

  // Pure render plan for an interlined (2+ line_ids) shared run: N parallel
  // offset strands (one per line, in `lineIds` order — strands render solid
  // hue always, v3 §7), one shared casing at zero offset whose structural
  // treatment comes from the trunk stretch's grade via fillPlan (drawn by
  // network.js — the v2 quality border is gone), and capsule marker points
  // at both ends of the shared run.
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
      grade,
      capsules: pathEndpoints(latlngs),
    };
  }

  // ================================================================
  // Schematic spine pipeline (spec 2026-07-15-network-schematic-redesign)
  // ================================================================
  // Every roster line becomes ONE continuous spine at render time:
  // members chained end-to-end, holes spliced in as bridged "nothing"
  // ranges, geometry straightened to long runs at a disciplined angle set,
  // pinned exactly through interchange control points. All pure math —
  // no Leaflet, Node-testable. Everything works in a single equirectangular
  // meter frame around REF_LAT (Chicago spans ~0.3° of latitude; the
  // cos(lat) error across that is ~0.4%, irrelevant at 250 m tolerances).

  const SCHEMATIC = {
    AXES_DEG: [0, 45, 60, 90, 120, 135],   // mod 180; flip-tested vs [0,45,90,135] at the QA gate
    snapToleranceDeg: 10,
    residualRoundDeg: 5,
    tiltMaxDeg: 4,
    trailRoundDeg: 15,
    minBendDeg: 30,
    mergeAngleDeg: 15,
    cornerToleranceMeters: 130,
    minRunMeters: { street: 600, trail: 400 },
    maxDisplacementMeters: 250,
    foldbackFraction: 0.25,
    pinMergeGridMeters: 250,
    pinAttractMeters: 350,
    terminusPairMeters: 300,
    footSnapMeters: 300,
    EXPLICIT_MERGES: [{ id: "nw-terminus", lines: ["milwaukee", "elston"], end: "north" }],
    coupletMaxMeters: 800,
    coupletAngleDeg: 15,
    coupletOverlapMin: 0.6,
    minStretchMeters: 250,
    minStripePx: 1.5,
    minRailPx: 1,
    hollowFallbackOpacity: 0.45,
    drainedOpacity: 0.5,
    labelOffsetPx: 14,
    labelClearPx: 24,
    nodeDedupeMeters: 100,
  };

  const REF_LAT = 41.88;
  const M_LNG_REF = METERS_PER_DEG_LAT * Math.cos((REF_LAT * Math.PI) / 180);
  function llToXY([lat, lng]) { return [lng * M_LNG_REF, lat * METERS_PER_DEG_LAT]; }
  function xyToLL([x, y]) { return [y / METERS_PER_DEG_LAT, x / M_LNG_REF]; }
  function xyDist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }

  // ---- Owner taxonomy: four display levels, `mellow` folded into paint,
  // grade-`none` members and bridged holes both display as `nothing`.
  // GRADE_RANK keeps mellow distinct internally so the comfort floor and
  // connector tints work unchanged (v3 §6).
  const QUALITY_LEVELS = ["offstreet", "protected", "paint", "nothing"];
  function displayGrade(grade) {
    if (grade === "mellow") return "paint";
    if (grade === "none" || grade == null) return "nothing";
    return QUALITY_LEVELS.includes(grade) ? grade : "nothing";
  }

  // ---- Angle helpers (degrees) ----
  function bearingDeg(dx, dy) {
    return ((Math.atan2(dy, dx) * 180) / Math.PI + 360) % 360;
  }
  function angDist360(a, b) {
    const d = Math.abs(((a - b) % 360 + 360) % 360);
    return Math.min(d, 360 - d);
  }
  function angDist180(a, b) {
    const d = Math.abs(((a - b) % 180 + 180) % 180);
    return Math.min(d, 180 - d);
  }
  function unitOf(deg) {
    const r = (deg * Math.PI) / 180;
    return [Math.cos(r), Math.sin(r)];
  }

  // Snap a bearing to the axis family (mod 180, direction preserved) when
  // within tolDeg; otherwise round to roundDeg. Trails pass axes = null and
  // just round (the "Thames treatment", §2.3).
  function snapBearing(deg, axes, tolDeg, roundDeg) {
    if (axes && axes.length > 0) {
      let best = null, bestD = Infinity;
      axes.forEach((a) => {
        [a, a + 180].forEach((cand) => {
          const d = angDist360(deg, cand);
          if (d < bestD) { bestD = d; best = cand % 360; }
        });
      });
      if (bestD <= tolDeg) return best;
    }
    return (Math.round(deg / roundDeg) * roundDeg) % 360;
  }

  // ---- RDP over XY meter points, returning kept indices ----
  function rdpXYIndices(pts, tol) {
    if (pts.length <= 2) return pts.map((_, i) => i);
    const keep = new Array(pts.length).fill(false);
    keep[0] = keep[pts.length - 1] = true;
    const stack = [[0, pts.length - 1]];
    while (stack.length > 0) {
      const [s, e] = stack.pop();
      let maxDist = -1, maxIdx = -1;
      for (let i = s + 1; i < e; i++) {
        const d = pointSegDistance(pts[i], pts[s], pts[e]);
        if (d > maxDist) { maxDist = d; maxIdx = i; }
      }
      if (maxDist > tol) {
        keep[maxIdx] = true;
        stack.push([s, maxIdx], [maxIdx, e]);
      }
    }
    const out = [];
    keep.forEach((k, i) => { if (k) out.push(i); });
    return out;
  }

  // ---- Part ordering: one total order over a line's member parts ----
  // Same greedy-vs-principal-axis hybrid as chainPlan, but returning the
  // actual ordered, oriented parts (chainPlan only reported the joins).
  // parts: [{ pts: XY[], ... }] with pts.length >= 2.
  function orderGreedy(parts) {
    const endpoints = [];
    parts.forEach((p, i) => {
      endpoints.push({ i, pt: p.pts[0], flip: false });
      endpoints.push({ i, pt: p.pts[p.pts.length - 1], flip: true });
    });
    const cx = endpoints.reduce((s, e) => s + e.pt[0], 0) / endpoints.length;
    const cy = endpoints.reduce((s, e) => s + e.pt[1], 0) / endpoints.length;
    let start = endpoints[0], startDist = -1;
    endpoints.forEach((e) => {
      const d = xyDist(e.pt, [cx, cy]);
      if (d > startDist) { startDist = d; start = e; }
    });
    const used = new Array(parts.length).fill(false);
    used[start.i] = true;
    const order = [{ i: start.i, flip: start.flip }];
    let endPt = start.flip ? parts[start.i].pts[0] : parts[start.i].pts[parts[start.i].pts.length - 1];
    for (let k = 1; k < parts.length; k++) {
      let bestI = -1, bestDist = Infinity, bestFlip = false;
      parts.forEach((p, i) => {
        if (used[i]) return;
        const dHead = xyDist(endPt, p.pts[0]);
        const dTail = xyDist(endPt, p.pts[p.pts.length - 1]);
        if (dHead < bestDist) { bestDist = dHead; bestI = i; bestFlip = false; }
        if (dTail < bestDist) { bestDist = dTail; bestI = i; bestFlip = true; }
      });
      order.push({ i: bestI, flip: bestFlip });
      used[bestI] = true;
      const p = parts[bestI];
      endPt = bestFlip ? p.pts[0] : p.pts[p.pts.length - 1];
    }
    return order;
  }
  function orderByAxis(parts) {
    const pts = [];
    parts.forEach((p) => { pts.push(p.pts[0], p.pts[p.pts.length - 1]); });
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    let sxx = 0, sxy = 0, syy = 0;
    pts.forEach((p) => {
      const dx = p[0] - cx, dy = p[1] - cy;
      sxx += dx * dx; sxy += dx * dy; syy += dy * dy;
    });
    const theta = 0.5 * Math.atan2(2 * sxy, sxx - syy);
    const ux = Math.cos(theta), uy = Math.sin(theta);
    const proj = (p) => (p[0] - cx) * ux + (p[1] - cy) * uy;
    return parts.map((p, i) => {
      const a = proj(p.pts[0]), b = proj(p.pts[p.pts.length - 1]);
      return { i, flip: a > b, lo: Math.min(a, b) };
    }).sort((A, B) => A.lo - B.lo).map(({ i, flip }) => ({ i, flip }));
  }
  function orderScore(parts, order, tol) {
    let total = 0, gaps = 0;
    for (let k = 1; k < order.length; k++) {
      const prev = parts[order[k - 1].i];
      const cur = parts[order[k].i];
      const a = order[k - 1].flip ? prev.pts[0] : prev.pts[prev.pts.length - 1];
      const b = order[k].flip ? cur.pts[cur.pts.length - 1] : cur.pts[0];
      const d = xyDist(a, b);
      if (d > tol) { total += d; gaps++; }
    }
    return { total, gaps };
  }
  // Agglomerative chaining: every part starts as its own chain; repeatedly
  // join the two chains whose ends are closest (flipping as needed) until
  // one remains. Slower than the single-pass walks (O(n³)-ish, fine at
  // this data's part counts) but immune to their failure modes: greedy
  // ping-pongs across a trail's parallel banks, axis-projection interleaves
  // branches into ladder rungs — both book phantom kilometers of "nothing"
  // once bridges are spliced into the spine.
  function orderAgglomerative(parts) {
    let chains = parts.map((p, i) => ({
      seq: [{ i, flip: false }],
      head: p.pts[0],
      tail: p.pts[p.pts.length - 1],
    }));
    while (chains.length > 1) {
      let best = null;
      for (let a = 0; a < chains.length; a++) {
        for (let b = a + 1; b < chains.length; b++) {
          const A = chains[a], B = chains[b];
          [
            [xyDist(A.tail, B.head), false, false], // A then B
            [xyDist(A.tail, B.tail), false, true],  // A then reversed B
            [xyDist(A.head, B.head), true, false],  // reversed A then B
            [xyDist(A.head, B.tail), true, true],   // reversed A then reversed B
          ].forEach(([d, flipA, flipB]) => {
            if (best == null || d < best.d) best = { d, a, b, flipA, flipB };
          });
        }
      }
      const A = chains[best.a], B = chains[best.b];
      const rev = (c) => ({
        seq: c.seq.slice().reverse().map((s) => ({ i: s.i, flip: !s.flip })),
        head: c.tail, tail: c.head,
      });
      const left = best.flipA ? rev(A) : A;
      const right = best.flipB ? rev(B) : B;
      const merged = { seq: left.seq.concat(right.seq), head: left.head, tail: right.tail };
      chains = chains.filter((_, i) => i !== best.a && i !== best.b);
      chains.push(merged);
    }
    return chains[0].seq;
  }

  function orderParts(parts, tol) {
    if (parts.length <= 1) return parts.map((_, i) => ({ i, flip: false }));
    const candidates = [orderGreedy(parts), orderByAxis(parts), orderAgglomerative(parts)]
      .map((order) => ({ order, ...orderScore(parts, order, tol) }));
    candidates.sort((a, b) => a.total - b.total || a.gaps - b.gaps);
    return candidates[0].order;
  }

  // ---- Couplet collapse (v3 §6): one-way pairs become one centerline ----
  // Detected per line among its street groups: parallel within
  // coupletAngleDeg, closer than coupletMaxMeters, projection overlap over
  // coupletOverlapMin of the shorter extent. The LONGER street keeps its
  // geometry (shifted halfway toward the partner); the shorter street's
  // parts drop out of the pool but survive as grade OVERLAYS — the
  // centerline renders the BETTER grade of the pair (v3 §6: a
  // floor=protected view must not hide a protected facility that exists).
  function streetStats(groupParts) {
    const pts = [];
    groupParts.forEach((p) => p.pts.forEach((q) => pts.push(q)));
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    let sxx = 0, sxy = 0, syy = 0;
    pts.forEach((p) => {
      const dx = p[0] - cx, dy = p[1] - cy;
      sxx += dx * dx; sxy += dx * dy; syy += dy * dy;
    });
    const theta = 0.5 * Math.atan2(2 * sxy, sxx - syy);
    const ux = Math.cos(theta), uy = Math.sin(theta);
    let lo = Infinity, hi = -Infinity;
    pts.forEach((p) => {
      const t = (p[0] - cx) * ux + (p[1] - cy) * uy;
      if (t < lo) lo = t;
      if (t > hi) hi = t;
    });
    const len = groupParts.reduce((s, p) => s + p.lenM, 0);
    return { theta: bearingDeg(ux, uy), ux, uy, cx, cy, lo, hi, len };
  }
  function coupletMatch(A, B, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    if (angDist180(A.theta, B.theta) > o.coupletAngleDeg) return null;
    // Perpendicular separation of B's centroid from A's axis line.
    const nx = -A.uy, ny = A.ux;
    const sep = Math.abs((B.cx - A.cx) * nx + (B.cy - A.cy) * ny);
    if (sep > o.coupletMaxMeters || sep < 1) return null;
    // Overlap of projections onto A's axis (B's extent carried over —
    // the two axes agree to within coupletAngleDeg, so this is exact
    // enough for a yes/no).
    const bC = (B.cx - A.cx) * A.ux + (B.cy - A.cy) * A.uy;
    const bSpan = (B.hi - B.lo) / 2;
    const b0 = bC - bSpan, b1 = bC + bSpan;
    const overlap = Math.min(A.hi, b1) - Math.max(A.lo, b0);
    const minExtent = Math.min(A.hi - A.lo, b1 - b0);
    if (minExtent <= 0 || overlap / minExtent < o.coupletOverlapMin) return null;
    const signedSep = (B.cx - A.cx) * nx + (B.cy - A.cy) * ny;
    return { sep, signedSep };
  }
  // partsByStreet: Map<street, part[]>. Returns { parts, donors, pairs }:
  // donors are dropped parts kept for grade overlays; pairs name the
  // collapsed couplets for the detail card's disambiguation copy (v3 §6).
  function collapseCouplets(partsByStreet, opts) {
    const groups = [...partsByStreet.entries()]
      .map(([street, parts]) => ({ street, parts, stats: streetStats(parts) }))
      .sort((a, b) => b.stats.len - a.stats.len);
    const donors = [];
    const pairs = [];
    for (let i = 0; i < groups.length; i++) {
      for (let j = groups.length - 1; j > i; j--) {
        const m = coupletMatch(groups[i].stats, groups[j].stats, opts);
        if (!m) continue;
        // Shift the base street halfway toward the donor, then absorb.
        const nx = -groups[i].stats.uy, ny = groups[i].stats.ux;
        const shift = m.signedSep / 2;
        groups[i].parts = groups[i].parts.map((p) => ({
          ...p,
          pts: p.pts.map(([x, y]) => [x + nx * shift, y + ny * shift]),
        }));
        donors.push(...groups[j].parts);
        pairs.push({ base: groups[i].street, donor: groups[j].street });
        groups[i].stats = streetStats(groups[i].parts);
        groups.splice(j, 1);
      }
    }
    const parts = [];
    groups.forEach((g) => parts.push(...g.parts));
    return { parts, donors, pairs };
  }

  // ---- Path tracing over the member-part graph ----
  // A line's members form a GRAPH, not a path: an OSM trail sweeps in both
  // riverbanks, loops, and access spurs; a street line collects downtown
  // fragments that overlap its trunk splices. Chaining parts verbatim
  // ping-pongs across that structure and books the doubling-back as
  // phantom kilometers of "nothing" (North Branch rendered 38 mi of spine
  // over 24 mi of geometry; Milwaukee oscillated across its Randolph
  // tail). So: quantize part endpoints to graph nodes (with T-junction
  // splitting), take each connected component's DIAMETER path
  // (double-sweep Dijkstra — the through-line), drop side branches
  // entirely (they are duplicates and spurs, not missing bikeway), and
  // let buildLineSpine bridge only BETWEEN components — the real holes.
  // Parts survive individually (not fused) so per-part grades flow into
  // gradeStretches unchanged.
  // Split parts wherever another part's endpoint touches them mid-way —
  // OSM T-junctions connect an endpoint to the MIDDLE of a long way, which
  // an endpoint-only graph can't see (the Lakefront read as 10 mi of
  // phantom holes before this). Splitting at the nearest vertex is exact
  // enough: raw vertices arrive every few meters.
  function splitAtJunctions(parts) {
    const eps = [];
    parts.forEach((p, pi) => {
      eps.push({ xy: p.pts[0], pi });
      eps.push({ xy: p.pts[p.pts.length - 1], pi });
    });
    const out = [];
    parts.forEach((p, pi) => {
      // Locked trunk splices are canonical geometry — never split them
      // (an interior cut would break byte-identity across owners, v3 §7).
      if (p.locked) { out.push(p); return; }
      const cuts = new Set();
      eps.forEach((e) => {
        if (e.pi === pi) return;
        let best = -1, bd = Infinity;
        p.pts.forEach((q, qi) => {
          const d = xyDist(q, e.xy);
          if (d < bd) { bd = d; best = qi; }
        });
        if (bd <= 40 && best > 0 && best < p.pts.length - 1) cuts.add(best);
      });
      if (cuts.size === 0) { out.push(p); return; }
      const idxs = [0, ...[...cuts].sort((a, b) => a - b), p.pts.length - 1];
      for (let k = 1; k < idxs.length; k++) {
        const pts = p.pts.slice(idxs[k - 1], idxs[k] + 1);
        if (pts.length < 2) continue;
        out.push({ ...p, pts, lenM: pts.reduce((s, q, i) => i === 0 ? 0 : s + xyDist(pts[i - 1], q), 0) });
      }
    });
    return out;
  }

  function tracePath(parts, opts) {
    const usable = splitAtJunctions((parts || []).filter((p) => p.pts && p.pts.length >= 2));
    if (usable.length <= 1) return usable;
    const cell = 50;
    const keyOf = (p) => Math.round(p[0] / cell) + ":" + Math.round(p[1] / cell);
    const adj = new Map(); // nodeKey -> [{to, part, flip, w}]
    const ensure = (k) => { if (!adj.has(k)) adj.set(k, []); return k; };
    usable.forEach((p) => {
      const a = ensure(keyOf(p.pts[0]));
      const b = ensure(keyOf(p.pts[p.pts.length - 1]));
      if (a === b) return; // pure loop: irrelevant to a through-line
      adj.get(a).push({ to: b, part: p, flip: false, w: p.lenM });
      adj.get(b).push({ to: a, part: p, flip: true, w: p.lenM });
    });
    if (adj.size === 0) return [usable.sort((x, y) => y.lenM - x.lenM)[0]];

    // Connected components.
    const comp = new Map();
    let nComp = 0;
    adj.forEach((_, k) => {
      if (comp.has(k)) return;
      const queue = [k];
      comp.set(k, nComp);
      while (queue.length) {
        const cur = queue.pop();
        adj.get(cur).forEach(({ to }) => {
          if (!comp.has(to)) { comp.set(to, nComp); queue.push(to); }
        });
      }
      nComp++;
    });

    function dijkstra(start) {
      const dist = new Map([[start, 0]]);
      const prev = new Map();
      const done = new Set();
      for (;;) {
        let cur = null, curD = Infinity;
        dist.forEach((d, k) => { if (!done.has(k) && d < curD) { curD = d; cur = k; } });
        if (cur == null) break;
        done.add(cur);
        adj.get(cur).forEach((e) => {
          const nd = curD + e.w;
          if (nd < (dist.has(e.to) ? dist.get(e.to) : Infinity)) {
            dist.set(e.to, nd);
            prev.set(e.to, { from: cur, e });
          }
        });
      }
      return { dist, prev };
    }

    const compParts = [];
    for (let c = 0; c < nComp; c++) {
      const members = [...adj.keys()].filter((k) => comp.get(k) === c);
      if (members.length === 0) continue;
      // Double sweep: farthest node from an arbitrary start, then the
      // farthest node from THAT — a good diameter approximation.
      const far = (from) => {
        const { dist, prev } = dijkstra(from);
        let best = from, bestD = -1;
        members.forEach((k) => {
          const d = dist.has(k) ? dist.get(k) : -1;
          if (d > bestD) { bestD = d; best = k; }
        });
        return { node: best, prev };
      };
      const sweep1 = far(members[0]);
      const sweep2 = far(sweep1.node);
      // Walk sweep2's tree from its farthest node back to sweep1.node.
      const pathParts = [];
      let cur = sweep2.node;
      while (cur !== sweep1.node && sweep2.prev.has(cur)) {
        const { from, e } = sweep2.prev.get(cur);
        // The edge was traversed `from` -> `cur`; orient its points that
        // way (flip means the stored part runs cur -> from) and unshift so
        // the assembled list reads start -> end.
        pathParts.unshift({ ...e.part, pts: e.flip ? e.part.pts.slice().reverse() : e.part.pts.slice() });
        cur = from;
      }
      if (pathParts.length === 0) continue;
      compParts.push({
        parts: pathParts,
        head: pathParts[0].pts[0],
        tail: pathParts[pathParts.length - 1].pts[pathParts[pathParts.length - 1].pts.length - 1],
        lenM: pathParts.reduce((s, p) => s + p.lenM, 0),
      });
    }
    if (compParts.length === 0) return usable;
    // Drop scrap components: a 30 m orphan sliver in the middle of the
    // line forces the chain to double back through it (the Lakefront
    // booked an 8 km phantom bridge detouring through two 30 m scraps).
    // The longest component always stays.
    const minComp = 100;
    const longest = compParts.reduce((a, b) => (b.lenM > (a?.lenM || 0) ? b : a), null);
    const kept = compParts.filter((p) => p === longest || p.lenM >= minComp);
    // Order components into one sequence (components are few — the
    // greedy/axis/agglomerative vote is reliable at this scale), flipping
    // a component's internal part order when it chains tail-first.
    const pseudo = kept.map((c) => ({ pts: [c.head, c.tail] }));
    const order = orderParts(pseudo, GAP_JOIN_TOLERANCE_METERS);
    const out = [];
    order.forEach(({ i, flip }) => {
      const c = kept[i];
      if (!flip) {
        out.push(...c.parts);
      } else {
        c.parts.slice().reverse().forEach((p) => out.push({ ...p, pts: p.pts.slice().reverse() }));
      }
    });
    return out;
  }

  // ---- buildLineSpine: members -> one continuous measured path ----
  // memberParts: [{ pts: XY[], grade, street, locked?, key? }]. Returns
  // { xy, origM, stretches, bridged } — origM is cumulative ORIGINAL
  // meters; a bridge advances measure by its chord length (v3 §2.1), so
  // the measure map stays monotone and nothing downstream special-cases
  // bridges.
  function buildLineSpine(memberParts, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const tol = GAP_JOIN_TOLERANCE_METERS;
    const usable = (memberParts || []).filter((p) => p.pts && p.pts.length >= 2);
    if (usable.length === 0) return null;
    const order = o.preOrdered
      ? usable.map((_, i) => ({ i, flip: false }))
      : orderParts(usable, tol);

    const xy = [], origM = [], stretches = [], bridged = [];
    let m = 0;
    order.forEach(({ i, flip }, k) => {
      const part = usable[i];
      const pts = flip ? part.pts.slice().reverse() : part.pts.slice();
      if (k === 0) {
        xy.push(pts[0]); origM.push(0);
      } else {
        const gap = xyDist(xy[xy.length - 1], pts[0]);
        if (gap > tol) {
          stretches.push({ m0: m, m1: m + gap, grade: "none", bridged: true });
          bridged.push({ m0: m, m1: m + gap });
          m += gap;
          xy.push(pts[0]); origM.push(m);
        } else if (gap > 0.01) {
          // Tiny join: measure advances, the sliver belongs to the next
          // stretch (no bridge, no seam).
          m += gap;
          xy.push(pts[0]); origM.push(m);
        }
      }
      const stretchStart = m;
      for (let q = 1; q < pts.length; q++) {
        const d = xyDist(pts[q - 1], pts[q]);
        if (d < 0.01) continue;
        m += d;
        xy.push(pts[q]); origM.push(m);
      }
      stretches.push({
        m0: stretchStart, m1: m, grade: part.grade,
        locked: !!part.locked, key: part.key,
      });
    });
    return { xy, origM, stretches, bridged };
  }

  // ---- Run detection / snapping / closure (v3 §2.2–§2.4) ----

  function runsFromIndices(pts, ms, kept) {
    const runs = [];
    for (let k = 1; k < kept.length; k++) {
      const i0 = kept[k - 1], i1 = kept[k];
      const disp = [pts[i1][0] - pts[i0][0], pts[i1][1] - pts[i0][1]];
      runs.push({ m0: ms[i0], m1: ms[i1], disp, len: Math.hypot(disp[0], disp[1]) });
    }
    return runs;
  }
  function mergeRunPair(a, b) {
    const disp = [a.disp[0] + b.disp[0], a.disp[1] + b.disp[1]];
    return { m0: a.m0, m1: b.m1, disp, len: Math.hypot(disp[0], disp[1]) };
  }

  function detectRuns(pts, ms, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const kept = rdpXYIndices(pts, o.cornerToleranceMeters);
    let runs = runsFromIndices(pts, ms, kept);
    // Merge near-collinear neighbors.
    let changed = true;
    while (changed && runs.length > 1) {
      changed = false;
      for (let i = 0; i < runs.length - 1; i++) {
        const bA = bearingDeg(runs[i].disp[0], runs[i].disp[1]);
        const bB = bearingDeg(runs[i + 1].disp[0], runs[i + 1].disp[1]);
        if (angDist360(bA, bB) < o.mergeAngleDeg) {
          runs.splice(i, 2, mergeRunPair(runs[i], runs[i + 1]));
          changed = true;
          break;
        }
      }
    }
    // Absorb sub-minimum runs into their longer neighbor.
    const minRun = o.minRunMeters[o.kind === "trail" ? "trail" : "street"];
    while (runs.length > 1) {
      let shortest = -1, shortestLen = Infinity;
      runs.forEach((r, i) => { if (r.len < shortestLen) { shortestLen = r.len; shortest = i; } });
      if (shortestLen >= minRun) break;
      const left = runs[shortest - 1], right = runs[shortest + 1];
      const mergeLeft = right == null || (left != null && left.len >= right.len);
      if (mergeLeft) runs.splice(shortest - 1, 2, mergeRunPair(left, runs[shortest]));
      else runs.splice(shortest, 2, mergeRunPair(runs[shortest], right));
    }
    return runs;
  }

  function snapRuns(runs, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const axes = o.kind === "trail" ? null : o.AXES_DEG;
    const roundDeg = o.kind === "trail" ? o.trailRoundDeg : o.residualRoundDeg;
    let out = runs.map((r) => ({
      ...r,
      bearing: snapBearing(bearingDeg(r.disp[0], r.disp[1]), axes, o.snapToleranceDeg, roundDeg),
    }));
    // Minimum-bend post-pass (v3 §2.3): the six-axis family allows 15°
    // corners (45 vs 60), indistinguishable from the wibble this redesign
    // kills. Merge or re-snap until no adjacent pair bends < minBendDeg.
    let changed = true;
    let guard = 0;
    while (changed && out.length > 1 && guard++ < 40) {
      changed = false;
      for (let i = 0; i < out.length - 1; i++) {
        const bend = angDist360(out[i].bearing, out[i + 1].bearing);
        if (bend < 0.01 || bend >= o.minBendDeg) continue;
        const combined = mergeRunPair(out[i], out[i + 1]);
        const cBearing = bearingDeg(combined.disp[0], combined.disp[1]);
        let newBearing;
        if (axes) {
          const snapped = snapBearing(cBearing, axes, o.snapToleranceDeg, o.residualRoundDeg);
          newBearing = snapped;
        } else {
          newBearing = snapBearing(cBearing, null, 0, o.trailRoundDeg);
        }
        const canMerge = angDist360(cBearing, newBearing) <= o.snapToleranceDeg + 0.01 || !axes;
        if (canMerge) {
          out.splice(i, 2, { ...combined, bearing: newBearing });
        } else {
          // Re-snap the shorter run to the longer neighbor's axis, then
          // merge (equal bearings).
          const winner = out[i].len >= out[i + 1].len ? out[i] : out[i + 1];
          out.splice(i, 2, { ...combined, bearing: winner.bearing });
        }
        changed = true;
        break;
      }
    }
    return out;
  }

  // closeRunLengths (v3 §2.4): with run directions fixed, minimize squared
  // length adjustments subject to hitting targetVec exactly — a 2×2
  // Lagrange solve. Length-only adjustment never rotates a snapped
  // bearing, which is what keeps pins crisp. Runs flagged in lockedMask
  // (interlined trunks) take ZERO adjustment. Returns null when the
  // system is singular or any solved length folds back below
  // foldbackFraction × original.
  function closeRunLengths(runs, targetVec, lockedMask, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const locked = lockedMask || runs.map(() => false);
    const u = runs.map((r) => unitOf(r.bearing));
    const L = runs.map((r, i) => Math.max(1, r.disp[0] * u[i][0] + r.disp[1] * u[i][1]));
    let bx = targetVec[0], by = targetVec[1];
    let a00 = 0, a01 = 0, a11 = 0;
    runs.forEach((r, i) => {
      bx -= L[i] * u[i][0];
      by -= L[i] * u[i][1];
      if (locked[i]) return;
      a00 += u[i][0] * u[i][0];
      a01 += u[i][0] * u[i][1];
      a11 += u[i][1] * u[i][1];
    });
    const det = a00 * a11 - a01 * a01;
    if (Math.abs(det) < 1e-6) return null; // collinear (or all locked)
    const lx = (a11 * bx - a01 * by) / det;
    const ly = (-a01 * bx + a00 * by) / det;
    const t = runs.map((r, i) => locked[i] ? L[i] : L[i] + u[i][0] * lx + u[i][1] * ly);
    for (let i = 0; i < t.length; i++) {
      if (!locked[i] && t[i] < Math.max(0, o.foldbackFraction * L[i])) return null; // fold-back
    }
    return t;
  }

  // Insert a 45° jog at the midpoint of the longest unlocked run — the
  // single shared fallback for both closure degeneracies (collinear and
  // fold-back, v3 §2.4). Returns { runs, lockedMask }.
  function insertJog(runs, lockedMask, targetVec) {
    const locked = lockedMask || runs.map(() => false);
    let j = -1, jLen = -1;
    runs.forEach((r, i) => { if (!locked[i] && r.len > jLen) { jLen = r.len; j = i; } });
    if (j < 0) return null;
    const r = runs[j];
    const half = { ...r, disp: [r.disp[0] / 2, r.disp[1] / 2], len: r.len / 2 };
    const mMid = (r.m0 + r.m1) / 2;
    const h1 = { ...half, m0: r.m0, m1: mMid };
    const h2 = { ...half, m0: mMid, m1: r.m1 };
    // Jog side: point the 45° elbow toward the residual displacement.
    const res = targetVec;
    const cand1 = (r.bearing + 45) % 360, cand2 = (r.bearing + 315) % 360;
    const u1 = unitOf(cand1), u2 = unitOf(cand2);
    const jogBearing = (u1[0] * res[0] + u1[1] * res[1]) >= (u2[0] * res[0] + u2[1] * res[1]) ? cand1 : cand2;
    const jog = {
      m0: mMid, m1: mMid, bearing: jogBearing,
      disp: [unitOf(jogBearing)[0] * 30, unitOf(jogBearing)[1] * 30], len: 30,
    };
    const runs2 = runs.slice(0, j).concat([h1, jog, h2], runs.slice(j + 1));
    const locked2 = locked.slice(0, j).concat([false, false, false], locked.slice(j + 1));
    return { runs: runs2, lockedMask: locked2 };
  }

  // Exact two-run dogleg from origin to targetVec using the two snap-family
  // directions bracketing the target bearing — the last-resort closure when
  // jog insertion still fails. Falls back to one exact straight run when
  // the target sits on a family direction.
  function doglegRuns(targetVec, m0, m1, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const phi = bearingDeg(targetVec[0], targetVec[1]);
    const family = [];
    (o.kind === "trail"
      ? Array.from({ length: Math.round(360 / o.trailRoundDeg) }, (_, i) => i * o.trailRoundDeg)
      : o.AXES_DEG.flatMap((a) => [a, a + 180])
    ).forEach((a) => family.push(((a % 360) + 360) % 360));
    family.sort((a, b) => angDist360(a, phi) - angDist360(b, phi));
    const mMid = (m0 + m1) / 2;
    for (let i = 0; i < family.length; i++) {
      for (let j = i + 1; j < family.length; j++) {
        const u1 = unitOf(family[i]), u2 = unitOf(family[j]);
        const det = u1[0] * u2[1] - u1[1] * u2[0];
        if (Math.abs(det) < 1e-9) continue;
        const t1 = (targetVec[0] * u2[1] - targetVec[1] * u2[0]) / det;
        const t2 = (u1[0] * targetVec[1] - u1[1] * targetVec[0]) / det;
        if (t1 < 0 || t2 < 0) continue;
        return [
          { m0, m1: mMid, bearing: family[i], disp: [u1[0] * t1, u1[1] * t1], len: t1, _t: t1 },
          { m0: mMid, m1, bearing: family[j], disp: [u2[0] * t2, u2[1] * t2], len: t2, _t: t2 },
        ];
      }
    }
    const len = Math.hypot(targetVec[0], targetVec[1]);
    return [{ m0, m1, bearing: phi, disp: targetVec.slice(), len, _t: len }];
  }

  // ---- Section schematization with displacement guard (v3 §2.6) ----
  // pts/ms: the section's original XY points and measures. startTarget/
  // endTarget: pinned endpoint positions (XY). Returns { xy, m } —
  // schematic vertices with their original measures, startTarget/endTarget
  // hit exactly.
  function schematizeSection(pts, ms, startTarget, endTarget, opts, depth) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const d = depth || 0;
    const targetVec = [endTarget[0] - startTarget[0], endTarget[1] - startTarget[1]];
    const straight = () => ({
      xy: [startTarget.slice(), endTarget.slice()],
      m: [ms[0], ms[ms.length - 1]],
    });

    let xy = null, m = null;
    if (pts.length < 2 || Math.hypot(targetVec[0], targetVec[1]) < 5) {
      ({ xy, m } = straight());
    } else {
      let runs = snapRuns(detectRuns(pts, ms, o), o);
      if (runs.length === 0) {
        ({ xy, m } = straight());
      } else {
        let lockedMask = runs.map(() => false);
        let t = closeRunLengths(runs, targetVec, lockedMask, o);
        if (t == null) {
          // Tilt escape: an essentially-straight section whose pinned
          // target sits a hair off-axis draws as ONE exact straight run,
          // tilted by that hair — a 1° tilt is invisible, a 45° jog is
          // not. Without this, every interchange pin on a straight
          // corridor inserted a stair-step (Milwaukee rendered as a jog
          // ladder). Only when the tilt would exceed tiltMaxDeg does the
          // jog machinery take over.
          const targetBearing = bearingDeg(targetVec[0], targetVec[1]);
          const allNearTarget = runs.every((r) => angDist360(r.bearing, targetBearing) <= o.tiltMaxDeg);
          if (allNearTarget) {
            ({ xy, m } = straight());
          } else if (runs.length === 1) {
            // Collinear degeneracy with a real off-axis displacement: the
            // 45° jog at the run's midpoint. Multi-run failures (fold-back)
            // skip straight to the dogleg below — a mid-run jog solved to
            // hundreds of meters reads as an arrowhead spike, not a bend
            // (seen on Jackson–Washington before this gate).
            const jogged = insertJog(runs, lockedMask, targetVec);
            if (jogged) {
              const t2 = closeRunLengths(jogged.runs, targetVec, jogged.lockedMask, o);
              if (t2 != null) { runs = jogged.runs; lockedMask = jogged.lockedMask; t = t2; }
            }
          }
        }
        if (xy == null) {
          if (t == null) {
            runs = doglegRuns(targetVec, ms[0], ms[ms.length - 1], o);
            t = runs.map((r) => r._t);
          }
          // Walk the solved runs into schematic vertices.
          xy = [startTarget.slice()];
          m = [ms[0]];
          runs.forEach((r, i) => {
            const u = unitOf(r.bearing);
            const last = xy[xy.length - 1];
            xy.push([last[0] + u[0] * t[i], last[1] + u[1] * t[i]]);
            m.push(r.m1);
          });
          // Snap the numeric tail exactly onto the pin (closure <1e-6 anyway).
          xy[xy.length - 1] = endTarget.slice();
          m[m.length - 1] = ms[ms.length - 1];
        }
      }
    }

    // Displacement guard — applies to EVERY path out of the solver,
    // including the straight/tilt escapes (a pin dragging a straight
    // section sideways is exactly the case it exists for). Surveyed
    // points only: bridged ranges are declared inventions and exempt by
    // definition (v3 §2.6).
    if (d < 3) {
      const isBridged = (mm) => (o.bridged || []).some((b) => mm > b.m0 + 0.5 && mm < b.m1 - 0.5);
      let worst = -1, worstIdx = -1;
      for (let i = 1; i < pts.length - 1; i++) {
        if (isBridged(ms[i])) continue;
        // Locate the schematic segment containing this original measure.
        let seg = 0;
        while (seg < m.length - 2 && ms[i] > m[seg + 1]) seg++;
        const dist = pointSegDistance(pts[i], xy[seg], xy[seg + 1]);
        if (dist > worst) { worst = dist; worstIdx = i; }
      }
      if (worst > o.maxDisplacementMeters) {
        const left = schematizeSection(
          pts.slice(0, worstIdx + 1), ms.slice(0, worstIdx + 1),
          startTarget, pts[worstIdx], o, d + 1);
        const right = schematizeSection(
          pts.slice(worstIdx), ms.slice(worstIdx),
          pts[worstIdx], endTarget, o, d + 1);
        return {
          xy: left.xy.concat(right.xy.slice(1)),
          m: left.m.concat(right.m.slice(1)),
        };
      }
    }
    return { xy, m };
  }

  // ---- Whole-spine schematization ----
  // spine: buildLineSpine output. pins: [{ m, target: XY }] sorted-ish.
  // Locked stretches (interlined trunks) pass through verbatim — their
  // geometry was schematized once, canonically, and spliced into every
  // owner (v3 §7). Returns { xy, m } (schematic vertices + original
  // measures).
  function schematizeSpine(spine, pins, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}), bridged: spine.bridged };
    const endM = spine.origM[spine.origM.length - 1];

    // Assemble pin list: endpoints always pinned (to themselves when no
    // control point claimed them), locked-stretch boundaries mandatory.
    const pinMap = new Map(); // m -> target
    const addPin = (mm, target, force) => {
      const clamped = Math.max(0, Math.min(endM, mm));
      for (const [existing] of pinMap) {
        if (Math.abs(existing - clamped) < 150 && !force) return; // too close to an existing pin
      }
      if (force) {
        for (const [existing] of pinMap) {
          if (Math.abs(existing - clamped) < 150) pinMap.delete(existing);
        }
      }
      pinMap.set(clamped, target);
    };
    addPin(0, (pins || []).find((p) => p.end === "start")?.target || pointAtMeasure(spine, 0), true);
    addPin(endM, (pins || []).find((p) => p.end === "end")?.target || pointAtMeasure(spine, endM), true);
    spine.stretches.filter((s) => s.locked).forEach((s) => {
      addPin(s.m0, pointAtMeasure(spine, s.m0), true);
      addPin(s.m1, pointAtMeasure(spine, s.m1), true);
    });
    // A pin inside a locked trunk range would split the canonical splice
    // and break byte-identity across owners (v3 §7) — the trunk's own
    // endpoint pins already anchor it, so interior pins are dropped.
    const insideLocked = (mm) => spine.stretches.some(
      (s) => s.locked && mm > s.m0 + 0.5 && mm < s.m1 - 0.5);
    (pins || []).filter((p) => p.end == null && !insideLocked(p.m))
      .forEach((p) => addPin(p.m, p.target, false));

    const pinMs = [...pinMap.keys()].sort((a, b) => a - b);
    const lockedRanges = spine.stretches.filter((s) => s.locked);
    const inLocked = (m0, m1) => lockedRanges.find((s) => m0 >= s.m0 - 0.5 && m1 <= s.m1 + 0.5);

    let outXY = null, outM = null;
    for (let k = 1; k < pinMs.length; k++) {
      const m0 = pinMs[k - 1], m1 = pinMs[k];
      if (m1 - m0 < 0.5) continue;
      let secXY, secM;
      const lockedStretch = inLocked(m0, m1);
      if (lockedStretch) {
        // Locked trunk geometry passes through untouched.
        const sec = extractSection(spine, m0, m1);
        secXY = sec.xy; secM = sec.m;
      } else {
        const sec = extractSection(spine, m0, m1);
        const result = schematizeSection(sec.xy, sec.m, pinMap.get(m0), pinMap.get(m1), o, 0);
        secXY = result.xy; secM = result.m;
      }
      if (outXY == null) { outXY = secXY; outM = secM; }
      else { outXY = outXY.concat(secXY.slice(1)); outM = outM.concat(secM.slice(1)); }
    }
    if (outXY == null) return { xy: spine.xy.slice(), m: spine.origM.slice() };
    return { xy: outXY, m: outM };
  }

  // Interpolated XY at an original measure.
  function pointAtMeasure(spine, mm) {
    const { xy, origM } = spine;
    if (mm <= origM[0]) return xy[0].slice();
    for (let i = 1; i < origM.length; i++) {
      if (mm <= origM[i]) {
        const span = origM[i] - origM[i - 1];
        const f = span < 1e-9 ? 0 : (mm - origM[i - 1]) / span;
        return [
          xy[i - 1][0] + (xy[i][0] - xy[i - 1][0]) * f,
          xy[i - 1][1] + (xy[i][1] - xy[i - 1][1]) * f,
        ];
      }
    }
    return xy[xy.length - 1].slice();
  }

  // Original vertices (with measures) between two measures, boundary
  // points interpolated exactly.
  function extractSection(spine, m0, m1) {
    const xy = [pointAtMeasure(spine, m0)];
    const m = [m0];
    for (let i = 0; i < spine.origM.length; i++) {
      if (spine.origM[i] > m0 + 1e-6 && spine.origM[i] < m1 - 1e-6) {
        xy.push(spine.xy[i].slice());
        m.push(spine.origM[i]);
      }
    }
    xy.push(pointAtMeasure(spine, m1));
    m.push(m1);
    return { xy, m };
  }

  // Slice a schematized spine ({ xy | latlngs, m }) between two ORIGINAL
  // measures. Original measure maps linearly to schematic distance within
  // each schematic segment, so proportional interpolation is exact.
  function sliceSpineByMeasure(schem, m0, m1) {
    const pts = schem.latlngs || schem.xy;
    const ms = schem.m;
    const lerp = (a, b, f) => [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
    const at = (mm) => {
      if (mm <= ms[0]) return pts[0].slice();
      for (let i = 1; i < ms.length; i++) {
        if (mm <= ms[i]) {
          const span = ms[i] - ms[i - 1];
          const f = span < 1e-9 ? 0 : (mm - ms[i - 1]) / span;
          return lerp(pts[i - 1], pts[i], f);
        }
      }
      return pts[pts.length - 1].slice();
    };
    const out = [at(m0)];
    for (let i = 0; i < ms.length; i++) {
      if (ms[i] > m0 + 1e-6 && ms[i] < m1 - 1e-6) out.push(pts[i].slice());
    }
    out.push(at(m1));
    return out;
  }

  // Nearest point on a flat latlng path: { pt, dist (meters), segIdx }.
  function snapPointToPath(pt, path) {
    const segs = [];
    for (let i = 0; i < path.length - 1; i++) segs.push([path[i], path[i + 1]]);
    if (segs.length === 0) return null;
    const hit = nearestOnChain(pt, segs);
    return hit;
  }

  // ---- Quality stretches (v3 §4.3) ----
  // Raw spine stretches + donor-street overlays -> render-ready stretches:
  // overlays upgrade overlapping ranges to the better grade; adjacent
  // same-grade ranges merge; sub-minStretchMeters confetti absorbs into
  // its larger neighbor. Pre-absorption ranges are preserved for the
  // panel's "nothing" mileage (data truth, stable under display tuning —
  // v3 §9.3).
  function gradeStretches(spine, overlays, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    // Boundary set: stretch edges + overlay edges.
    const cuts = new Set();
    spine.stretches.forEach((s) => { cuts.add(s.m0); cuts.add(s.m1); });
    (overlays || []).forEach((s) => { cuts.add(s.m0); cuts.add(s.m1); });
    const sorted = [...cuts].sort((a, b) => a - b);
    const gradeAt = (mm) => {
      const s = spine.stretches.find((st) => mm >= st.m0 - 1e-6 && mm < st.m1 - 1e-6);
      return s || null;
    };
    const raw = [];
    for (let i = 1; i < sorted.length; i++) {
      const m0 = sorted[i - 1], m1 = sorted[i];
      if (m1 - m0 < 0.01) continue;
      const mid = (m0 + m1) / 2;
      const base = gradeAt(mid);
      if (!base) continue;
      let grade = base.grade;
      let bridgedFlag = !!base.bridged;
      let locked = !!base.locked;
      let key = base.key;
      (overlays || []).forEach((ov) => {
        if (mid >= ov.m0 && mid <= ov.m1 && gradeRank(ov.grade) > gradeRank(grade)) {
          grade = ov.grade;
          bridgedFlag = false;
        }
      });
      raw.push({ m0, m1, grade, bridged: bridgedFlag, locked, key });
    }
    // Merge adjacent same-grade ranges (keep locked boundaries intact).
    const merged = [];
    raw.forEach((s) => {
      const prev = merged[merged.length - 1];
      if (prev && prev.grade === s.grade && prev.locked === s.locked && Math.abs(prev.m1 - s.m0) < 0.01) {
        prev.m1 = s.m1;
        prev.bridged = prev.bridged && s.bridged;
      } else {
        merged.push({ ...s });
      }
    });
    const preAbsorption = merged.map((s) => ({ ...s }));
    // Absorb display confetti (never absorb locked-boundary stretches).
    let out = merged.map((s) => ({ ...s }));
    let changed = true;
    while (changed && out.length > 1) {
      changed = false;
      for (let i = 0; i < out.length; i++) {
        const s = out[i];
        if (s.locked || (s.m1 - s.m0) >= o.minStretchMeters) continue;
        const left = out[i - 1], right = out[i + 1];
        const eat = (right && !right.locked && (!left || left.locked || (right.m1 - right.m0) >= (left.m1 - left.m0)))
          ? right : (left && !left.locked ? left : null);
        if (!eat) continue;
        if (eat === right) { right.m0 = s.m0; }
        else { left.m1 = s.m1; }
        out.splice(i, 1);
        changed = true;
        break;
      }
      // Re-merge equal neighbors created by absorption.
      for (let i = 0; i < out.length - 1; i++) {
        if (out[i].grade === out[i + 1].grade && out[i].locked === out[i + 1].locked) {
          out[i].m1 = out[i + 1].m1;
          out.splice(i + 1, 1);
          changed = true;
        }
      }
    }
    return { stretches: out, preAbsorption };
  }

  // "Nothing" mileage for the panel chip (v3 §9.3): pre-absorption bridged
  // + grade-none extents, in original meters — data truth, unaffected by
  // minStretchMeters display tuning.
  function nothingMeters(preAbsorption) {
    return (preAbsorption || [])
      .filter((s) => displayGrade(s.grade) === "nothing")
      .reduce((sum, s) => sum + (s.m1 - s.m0), 0);
  }

  // ---- Level mix (v3 §9.2): ONE denominator for every mix-bar width ----
  // Aggregates stretch measure ranges by display level — the bar is
  // literally proportional to the drawn line. Callers print pipeline
  // miles_by_grade for the built levels (the honest numbers) and the
  // spine-derived figure for `nothing`; widths always come from here.
  const LEVEL_COLORS = {
    offstreet: "#0369a1",
    protected: "#0b6e4f",
    paint: "#f59e0b",
    nothing: "#cbd5e1",
  };
  function levelMixSegments(stretchLists) {
    const meters = { offstreet: 0, protected: 0, paint: 0, nothing: 0 };
    (stretchLists || []).forEach((list) => (list || []).forEach((s) => {
      meters[displayGrade(s.grade)] += (s.m1 - s.m0);
    }));
    const total = QUALITY_LEVELS.reduce((sum, l) => sum + meters[l], 0);
    if (total <= 0) return [];
    return QUALITY_LEVELS.filter((l) => meters[l] > 0).map((l) => ({
      level: l, meters: meters[l], pct: (100 * meters[l]) / total, color: LEVEL_COLORS[l],
    }));
  }

  // ---- fillPlan (v3 §4.1/§4.2): structural ink per display level ----
  // Returns what network.js draws for one stretch at the current
  // zoom-scaled stroke weight: { band, stripeWidth, coreWidth,
  // hollowFallback }. Pure and unit-tested; all breakpoints are SCHEMATIC
  // constants so QA can tune them.
  function fillPlan(level, scaledWeight, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const plan = { band: false, stripeWidth: 0, coreWidth: 0, hollowFallback: false };
    if (level === "offstreet") {
      plan.band = true;
    } else if (level === "paint") {
      const stripe = scaledWeight / 3;
      if (stripe >= o.minStripePx) plan.stripeWidth = stripe;
      // else: stripe coarsens away — paint renders solid (built vs nothing
      // is the honest citywide read, §4.2).
    } else if (level === "nothing") {
      const core = Math.min(0.6 * scaledWeight, scaledWeight - 2);
      const rail = (scaledWeight - core) / 2;
      // Both the rails AND the core must stay visible (>= 1 px) for the
      // hollow read to survive; below that the stretch degrades to solid
      // hue at hollowFallbackOpacity.
      if (core >= 1 && rail >= o.minRailPx) plan.coreWidth = core;
      else plan.hollowFallback = true;
    }
    return plan;
  }

  // ---- Whole-network orchestration (consumed by network.js) ----
  // input: {
  //   lines: [{ id, source }],                       // roster metadata
  //   partsByLine: { lineId: [{ latlngs, grade, street }] },  // OWN members only
  //   trunks: [{ key, lineIds, parts: [{ latlngs, grade }] }],// interlined groups
  //   nodes: [{ lat, lng, kind, label, lines }],
  // }
  // Returns { spines: Map, trunks: Map, interchanges: [...] } where each
  // spine is { latlngs, m, stretches, preAbsorption, nothingM, bridged,
  // trunkRanges }.
  function buildSchematicNetwork(input, opts) {
    const o = { ...SCHEMATIC, ...(opts || {}) };
    const toParts = (arr) => (arr || []).map((p) => ({
      ...p,
      pts: (isMultiPart(p.latlngs) ? p.latlngs : [p.latlngs]).map((part) => part.map(llToXY)),
    })).flatMap((p) => p.pts.map((pts) => ({ ...p, pts })))
      .filter((p) => p.pts.length >= 2)
      .map((p) => ({ ...p, lenM: p.pts.reduce((s, q, i) => i === 0 ? 0 : s + xyDist(p.pts[i - 1], q), 0) }));

    // -- 1. Canonical trunks: schematized once, spliced into every owner
    // (v3 §7 — byte-identity by construction).
    const trunkOut = new Map();
    (input.trunks || []).forEach((trunk) => {
      const parts = toParts(trunk.parts);
      const spine = buildLineSpine(parts, o);
      if (!spine) return;
      const schem = schematizeSpine(spine, [], { ...o, kind: "street" });
      const graded = gradeStretches(spine, [], o);
      trunkOut.set(trunk.key, {
        key: trunk.key, lineIds: trunk.lineIds,
        spine, schem, stretches: graded.stretches, preAbsorption: graded.preAbsorption,
      });
    });

    // -- 2. Per-line raw spines (own parts + locked trunk splices).
    const rawSpines = new Map();   // lineId -> { spine, overlays, kind }
    (input.lines || []).forEach((line) => {
      const own = toParts(input.partsByLine[line.id]);
      const kind = line.source === "osm_trails" ? "trail" : "street";
      let parts = own;
      let overlays = [];
      let coupletPairs = [];
      if (kind === "street") {
        const byStreet = new Map();
        own.forEach((p) => {
          const street = p.street || "";
          if (!byStreet.has(street)) byStreet.set(street, []);
          byStreet.get(street).push(p);
        });
        if (byStreet.size > 1) {
          const collapsed = collapseCouplets(byStreet, o);
          parts = collapsed.parts;
          overlays = collapsed.donors; // projected into measures after the spine exists
          coupletPairs = collapsed.pairs;
        }
      }
      // Locked trunk splices, canonical geometry — added BEFORE the path
      // trace so the trace treats the trunk as ordinary graph structure
      // (owner fragments junction-split against its endpoints). Own parts
      // that run parallel INSIDE a trunk's corridor are the same
      // one-way-pair situation the couplet collapse handles: keeping them
      // as geometry forces the spine to overshoot and double back
      // (Jackson's east tip rendered as an arrowhead), so they demote to
      // grade overlays exactly like couplet donors.
      trunkOut.forEach((t) => {
        if (!t.lineIds.includes(line.id)) return;
        const pts = t.schem.xy.map((p) => p.slice());
        const trunkSegs = [];
        for (let i = 0; i < pts.length - 1; i++) trunkSegs.push([pts[i], pts[i + 1]]);
        const nearTrunk = (q) => trunkSegs.some(([a, b]) => pointSegDistance(q, a, b) <= o.coupletMaxMeters);
        const keep = [];
        parts.forEach((p) => {
          if (p.locked) { keep.push(p); return; }
          const hits = p.pts.reduce((s, q) => s + (nearTrunk(q) ? 1 : 0), 0);
          if (hits / p.pts.length > o.coupletOverlapMin) overlays.push(p);
          else keep.push(p);
        });
        parts = keep.concat([{
          pts, grade: "protected", locked: true, key: t.key,
          lenM: pts.reduce((s, q, i) => i === 0 ? 0 : s + xyDist(pts[i - 1], q), 0),
        }]);
      });
      parts = tracePath(parts, o);
      const spine = buildLineSpine(parts, { ...o, preOrdered: true });
      if (!spine) return;
      // Donor-street grade overlays: project each donor part's endpoints
      // onto the spine -> a measure range carrying the donor grade.
      const projectM = (pt) => {
        let best = null;
        for (let i = 0; i < spine.xy.length - 1; i++) {
          const d = pointSegDistance(pt, spine.xy[i], spine.xy[i + 1]);
          if (best == null || d < best.d) best = { d, i, pt };
        }
        if (!best) return null;
        // Parametric position within the winning segment.
        const a = spine.xy[best.i], b = spine.xy[best.i + 1];
        const dx = b[0] - a[0], dy = b[1] - a[1];
        const lenSq = dx * dx + dy * dy;
        let f = lenSq === 0 ? 0 : ((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / lenSq;
        f = Math.max(0, Math.min(1, f));
        return spine.origM[best.i] + (spine.origM[best.i + 1] - spine.origM[best.i]) * f;
      };
      const overlayRanges = overlays.map((p) => {
        const mA = projectM(p.pts[0]);
        const mB = projectM(p.pts[p.pts.length - 1]);
        if (mA == null || mB == null) return null;
        return { m0: Math.min(mA, mB), m1: Math.max(mA, mB), grade: p.grade };
      }).filter(Boolean);
      rawSpines.set(line.id, { spine, overlays: overlayRanges, kind, coupletPairs });
    });

    // -- 3. Control points (v3 §2.5).
    const cps = [];
    const grid = o.pinMergeGridMeters;
    const cells = new Map();
    (input.nodes || []).filter((n) => n.kind === "interchange").forEach((n) => {
      const xy = llToXY([n.lat, n.lng]);
      const cell = Math.round(xy[0] / grid) + ":" + Math.round(xy[1] / grid);
      if (!cells.has(cell)) cells.set(cell, { xs: 0, ys: 0, count: 0, lines: new Set(), labels: [] });
      const c = cells.get(cell);
      c.xs += xy[0]; c.ys += xy[1]; c.count++;
      (n.lines || []).forEach((id) => c.lines.add(id));
      c.labels.push(n.label);
    });
    cells.forEach((c) => {
      cps.push({ xy: [c.xs / c.count, c.ys / c.count], lines: c.lines, labels: c.labels, fixed: false });
    });
    // Reposition node control points onto the DRAWN network: the node
    // catalog carries true street positions, but a collapsed couplet's
    // centerline (and any traced spine) can sit a couple hundred meters
    // from them — pinning to the raw node would dent the line at every
    // crossing (Jackson–Washington grew an arrowhead per interchange).
    // The natural interchange position is where the drawn lines actually
    // cross: use the intersection of the first crossing pair near the
    // node, else the mean of each member line's nearest point.
    const segIntersect = (a1, a2, b1, b2) => {
      const d1x = a2[0] - a1[0], d1y = a2[1] - a1[1];
      const d2x = b2[0] - b1[0], d2y = b2[1] - b1[1];
      const den = d1x * d2y - d1y * d2x;
      if (Math.abs(den) < 1e-9) return null;
      const s = ((b1[0] - a1[0]) * d2y - (b1[1] - a1[1]) * d2x) / den;
      const u = ((b1[0] - a1[0]) * d1y - (b1[1] - a1[1]) * d1x) / den;
      if (s < 0 || s > 1 || u < 0 || u > 1) return null;
      return [a1[0] + s * d1x, a1[1] + s * d1y];
    };
    const nearSegs = (spine, xy, radius) => {
      const segs = [];
      for (let i = 0; i < spine.xy.length - 1; i++) {
        if (pointSegDistance(xy, spine.xy[i], spine.xy[i + 1]) <= radius) {
          segs.push([spine.xy[i], spine.xy[i + 1]]);
        }
      }
      return segs;
    };
    cps.forEach((cp) => {
      const memberSpines = [...cp.lines]
        .map((id) => rawSpines.get(id))
        .filter(Boolean)
        .map((r) => r.spine);
      if (memberSpines.length === 0) return;
      const radius = o.pinAttractMeters;
      // Crossing point of the first intersecting pair near the node.
      for (let i = 0; i < memberSpines.length; i++) {
        for (let j = i + 1; j < memberSpines.length; j++) {
          const segsA = nearSegs(memberSpines[i], cp.xy, radius);
          const segsB = nearSegs(memberSpines[j], cp.xy, radius);
          for (const [a1, a2] of segsA) {
            for (const [b1, b2] of segsB) {
              const hit = segIntersect(a1, a2, b1, b2);
              if (hit) { cp.xy = hit; return; }
            }
          }
        }
      }
      // No crossing (T-meets, single-line nodes): mean of nearest points.
      const feet = [];
      memberSpines.forEach((spine) => {
        let best = null;
        for (let i = 0; i < spine.xy.length - 1; i++) {
          const a = spine.xy[i], b = spine.xy[i + 1];
          const d = pointSegDistance(cp.xy, a, b);
          if (d > radius || (best && d >= best.d)) continue;
          const dx = b[0] - a[0], dy = b[1] - a[1];
          const lenSq = dx * dx + dy * dy;
          let f = lenSq === 0 ? 0 : ((cp.xy[0] - a[0]) * dx + (cp.xy[1] - a[1]) * dy) / lenSq;
          f = Math.max(0, Math.min(1, f));
          best = { d, pt: [a[0] + dx * f, a[1] + dy * f] };
        }
        if (best) feet.push(best.pt);
      });
      if (feet.length > 0) {
        cp.xy = [
          feet.reduce((s, p) => s + p[0], 0) / feet.length,
          feet.reduce((s, p) => s + p[1], 0) / feet.length,
        ];
      }
    });
    // Trunk endpoints are mandatory control points for every owner.
    trunkOut.forEach((t) => {
      [t.schem.xy[0], t.schem.xy[t.schem.xy.length - 1]].forEach((xy) => {
        cps.push({ xy: xy.slice(), lines: new Set(t.lineIds), labels: [], fixed: true, trunkKey: t.key });
      });
    });

    // Termini bookkeeping.
    const termini = [];
    rawSpines.forEach(({ spine }, lineId) => {
      termini.push(
        { lineId, end: "start", xy: spine.xy[0], attached: false },
        { lineId, end: "end", xy: spine.xy[spine.xy.length - 1], attached: false },
      );
    });
    // (a) terminus -> control point attraction.
    termini.forEach((t) => {
      let best = null;
      cps.forEach((cp) => {
        const d = xyDist(t.xy, cp.xy);
        if (d <= o.pinAttractMeters && (best == null || d < best.d)) best = { d, cp };
      });
      if (best) { t.attached = true; t.target = best.cp.xy; best.cp.lines.add(t.lineId); }
    });
    // (b) explicit merges (owner directive #4 beyond generic thresholds).
    (o.EXPLICIT_MERGES || []).forEach((em) => {
      const ends = em.lines.map((lineId) => {
        const cand = termini.filter((t) => t.lineId === lineId && !t.attached);
        if (cand.length === 0) return null;
        cand.sort((a, b) => em.end === "north" ? b.xy[1] - a.xy[1]
          : em.end === "south" ? a.xy[1] - b.xy[1]
          : em.end === "east" ? b.xy[0] - a.xy[0] : a.xy[0] - b.xy[0]);
        return cand[0];
      }).filter(Boolean);
      if (ends.length < 2) return;
      const cx = ends.reduce((s, t) => s + t.xy[0], 0) / ends.length;
      const cy = ends.reduce((s, t) => s + t.xy[1], 0) / ends.length;
      const cp = { xy: [cx, cy], lines: new Set(ends.map((t) => t.lineId)), labels: [], fixed: false };
      cps.push(cp);
      ends.forEach((t) => { t.attached = true; t.target = cp.xy; });
    });
    // (c) terminus <-> terminus pairing.
    const loose = () => termini.filter((t) => !t.attached);
    loose().forEach((t) => {
      if (t.attached) return;
      const partner = loose().find((u) => u !== t && u.lineId !== t.lineId && xyDist(t.xy, u.xy) <= o.terminusPairMeters);
      if (!partner) return;
      const cp = {
        xy: [(t.xy[0] + partner.xy[0]) / 2, (t.xy[1] + partner.xy[1]) / 2],
        lines: new Set([t.lineId, partner.lineId]), labels: [], fixed: false,
      };
      cps.push(cp);
      t.attached = partner.attached = true;
      t.target = partner.target = cp.xy;
    });
    // (d) terminus -> another line's spine, perpendicular foot point.
    const extraPins = new Map(); // lineId -> [{m, target}]
    loose().forEach((t) => {
      let best = null;
      rawSpines.forEach(({ spine }, otherId) => {
        if (otherId === t.lineId) return;
        for (let i = 0; i < spine.xy.length - 1; i++) {
          const d = pointSegDistance(t.xy, spine.xy[i], spine.xy[i + 1]);
          if (d <= o.footSnapMeters && (best == null || d < best.d)) best = { d, otherId, i };
        }
      });
      if (!best) return;
      const spine = rawSpines.get(best.otherId).spine;
      const a = spine.xy[best.i], b = spine.xy[best.i + 1];
      const dx = b[0] - a[0], dy = b[1] - a[1];
      const lenSq = dx * dx + dy * dy;
      let f = lenSq === 0 ? 0 : ((t.xy[0] - a[0]) * dx + (t.xy[1] - a[1]) * dy) / lenSq;
      f = Math.max(0, Math.min(1, f));
      const foot = [a[0] + dx * f, a[1] + dy * f];
      const footM = spine.origM[best.i] + (spine.origM[best.i + 1] - spine.origM[best.i]) * f;
      t.attached = true;
      t.target = foot;
      if (!extraPins.has(best.otherId)) extraPins.set(best.otherId, []);
      extraPins.get(best.otherId).push({ m: footM, target: foot });
      cps.push({ xy: foot, lines: new Set([t.lineId, best.otherId]), labels: [], fixed: false });
    });

    // -- 4. Per-line pins + schematization.
    const spines = new Map();
    rawSpines.forEach(({ spine, overlays, kind, coupletPairs }, lineId) => {
      const pins = [];
      const t0 = termini.find((t) => t.lineId === lineId && t.end === "start");
      const t1 = termini.find((t) => t.lineId === lineId && t.end === "end");
      if (t0 && t0.attached) pins.push({ end: "start", target: t0.target });
      if (t1 && t1.attached) pins.push({ end: "end", target: t1.target });
      // Interchange/control-point pass-through pins.
      cps.forEach((cp) => {
        if (!cp.lines.has(lineId)) return;
        let best = null;
        for (let i = 0; i < spine.xy.length - 1; i++) {
          const d = pointSegDistance(cp.xy, spine.xy[i], spine.xy[i + 1]);
          if (d <= o.pinAttractMeters && (best == null || d < best.d)) best = { d, i };
        }
        if (!best) return;
        const a = spine.xy[best.i], b = spine.xy[best.i + 1];
        const dx = b[0] - a[0], dy = b[1] - a[1];
        const lenSq = dx * dx + dy * dy;
        let f = lenSq === 0 ? 0 : ((cp.xy[0] - a[0]) * dx + (cp.xy[1] - a[1]) * dy) / lenSq;
        f = Math.max(0, Math.min(1, f));
        const mm = spine.origM[best.i] + (spine.origM[best.i + 1] - spine.origM[best.i]) * f;
        const endM = spine.origM[spine.origM.length - 1];
        if (mm < 200 || mm > endM - 200) return; // endpoint pins own the ends
        pins.push({ m: mm, target: cp.xy });
      });
      (extraPins.get(lineId) || []).forEach((p) => pins.push(p));

      const schem = schematizeSpine(spine, pins, { ...o, kind });
      const graded = gradeStretches(spine, overlays, o);
      const trunkRanges = spine.stretches.filter((s) => s.locked)
        .map((s) => ({ key: s.key, m0: s.m0, m1: s.m1 }));
      spines.set(lineId, {
        latlngs: schem.xy.map(xyToLL),
        m: schem.m,
        stretches: graded.stretches,
        preAbsorption: graded.preAbsorption,
        nothingM: nothingMeters(graded.preAbsorption),
        bridged: spine.bridged,
        trunkRanges,
        kind,
        coupletPairs: coupletPairs || [],
      });
    });

    // Trunk output in latlng space, with schematic-sliceable measures.
    const trunksLL = new Map();
    trunkOut.forEach((t, key) => {
      trunksLL.set(key, {
        key, lineIds: t.lineIds,
        latlngs: t.schem.xy.map(xyToLL),
        m: t.schem.m,
        stretches: t.stretches,
        preAbsorption: t.preAbsorption,
      });
    });

    // Interchange markers: one per control point that carries node labels,
    // deduped by construction (grid merge) and snapped onto the schematic
    // by pinning. Orientation nodes are network.js's business
    // (snapPointToPath onto the nearest spine).
    const interchanges = cps.filter((cp) => cp.labels.length > 0).map((cp) => ({
      latlng: xyToLL(cp.xy),
      label: cp.labels[0],
      lines: [...cp.lines],
    }));

    return { spines, trunks: trunksLL, interchanges };
  }

  const api = {
    flattenCoords, toLatLngs, getPaddedBBox, unionBBox,
    groupByCorridor,
    ZOOM,
    DEFAULT_OVERLAYS, parseOverlays, serializeOverlays,
    LINE_COLORS, FALLBACK_LINE_COLOR, lineStyle,
    darkenColor, lightenColor, trailStyle, trailOutlineStyle,
    zoomWeightFactor, GAP_JOIN_TOLERANCE_METERS,
    CONNECTOR_STYLE, CONNECTOR_GRADE_TINTS, connectorStyle,
    GRADE_COLORS,
    GRADE_RANK, gradeRank, FLOOR_IDS, parseFloor, meetsFloor,
    DRAINED_COLOR,
    QUALITY_MIX_ORDER, qualityMixSegments,
    buildRosterIndex, linesById, splitByRoster, membersOfLine, rosterStreets,
    simplifyPart, simplifyLatLngs, schematicLatLngs, SIMPLIFY_TOLERANCE_METERS,
    chainPlan, crossStreetGaps, CROSS_STREET_MAX_FEEDER_METERS,
    CONNECTOR_GRADE_MAP, pathLengthMeters,
    isMultiPart, offsetPart, offsetLatLngs, strandOffsets, pathEndpoints,
    planInterlinedRoute, INTERLINE_GAP_METERS, INTERLINE_GAP_PX, metersPerPixel,
    // ---- schematic spine pipeline (spec 2026-07-15) ----
    SCHEMATIC, QUALITY_LEVELS, displayGrade,
    buildLineSpine, detectRuns, snapRuns, closeRunLengths,
    schematizeSection, schematizeSpine, sliceSpineByMeasure,
    collapseCouplets, tracePath, snapPointToPath,
    gradeStretches, nothingMeters, fillPlan,
    LEVEL_COLORS, levelMixSegments,
    buildSchematicNetwork,
  };

  root.BSDNet = api;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
