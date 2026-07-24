(async function () {
  BSD.initPage("network.html");

  // Paper canvas, not a basemap. Since the 2026-07-15 schematic redesign
  // this screen is a DELIBERATE schematic (DECISIONS.md #10): each roster
  // line renders as one continuous spine, straightened to a disciplined
  // angle set and pinned through interchanges, with quality — including
  // "nothing" — drawn as structural ink on a hue-constant stroke.
  // Spec: docs/superpowers/specs/2026-07-15-network-schematic-redesign.md.
  document.getElementById("map").style.background = "#f7f9fb";

  const map = L.map("map", {
    attributionControl: false,
    zoom: 11,
    center: [41.8781, -87.6298],
  });

  // Explicit panes (not DOM insertion order) so z-order is stable no matter
  // which toggles are on at load vs. flipped later. Bottom -> top: wards
  // backdrop -> connectors -> trail band -> trail slices -> selection halo
  // -> street casing -> street slices/strands -> planned casing -> planned
  // lines -> capsule transfer markers -> nodes. The v2 qualityPane is gone
  // with the border layer (spec v3 §10). Labels use Leaflet's own
  // tooltipPane, already above every overlay pane.
  //
  // IMPORTANT (click-bug fix, v2 spec §7, still binding): every pane here
  // holds only *interactive* Leaflet objects that are meant to intercept
  // clicks. network.js never drops an invisible/zero-opacity marker onto
  // the map to "keep a layer non-empty" — that pattern silently ate clicks
  // near the map center once. Stub/no-data notices are driven by plain
  // feature-count checks instead.
  const PANE_ORDER = [
    "wardsPane", "connectorsPane", "trailsOutlinePane", "trailsPane", "haloPane",
    "casingPane", "linesPane",
    "plannedCasingPane", "plannedPane", "capsulesPane", "nodesPane",
  ];
  PANE_ORDER.forEach((name, i) => {
    map.createPane(name);
    map.getPane(name).style.zIndex = 200 + i * 10;
  });
  // Halo/casing/band panes must never steal clicks meant for the
  // interactive slices above them; stripes and cores live in the
  // interactive panes but are created with interactive: false themselves.
  ["haloPane", "casingPane", "trailsOutlinePane", "plannedCasingPane"].forEach((name) => {
    map.getPane(name).style.pointerEvents = "none";
  });

  const layers = {
    casing: L.layerGroup(),          // street spines: white casing + trunk casings
    lines: L.layerGroup(),           // street spines: hue slices + stripes/cores + trunk strands
    trailsOutline: L.layerGroup(),   // trail spines: white casing + darkened offstreet band
    trails: L.layerGroup(),          // trail spines: hue slices + cores
    connectors: L.layerGroup(),      // connectors tier: non-roster bike_routes + mellow_connectors + non-roster osm_trails
    halo: L.layerGroup(),            // selection halo
    capsules: L.layerGroup(),        // trunk transfer-capsule markers
    nodesInterchange: L.layerGroup(),
    nodesOrientation: L.layerGroup(),
    labels: L.layerGroup(),          // corridor labels for connector-tier streets, z >= 13
    lineLabelsTrails: L.layerGroup(),
    lineLabelsStreets: L.layerGroup(),
    terminusLabelsTrails: L.layerGroup(),
    terminusLabelsStreets: L.layerGroup(),
    planned: L.layerGroup(),
    plannedCasing: L.layerGroup(),
  };

  // URL state: ?overlays=trails,main,connectors,nodes,planned (legacy ids —
  // including the retired "quality" — are simply never checked below, so
  // they're ignored silently) &floor=any|paint|protected &corridor=<street>
  // &line=<roster line id>.
  // milwaukee + jackson-washington merged into one L-shaped through-line
  // (DECISIONS.md #28). Old shared ?line= links resolve to the merged id so
  // they still land on a route instead of silently dropping.
  const LEGACY_LINE_ALIASES = {
    "milwaukee": "milwaukee-washington",
    "jackson-washington": "milwaukee-washington",
  };
  const rawLine = BSD.qs().get("line") || "";
  const state = {
    overlays: BSDNet.parseOverlays(BSD.qs().get("overlays")),
    floor: BSDNet.parseFloor(BSD.qs().get("floor")),
    corridor: BSD.qs().get("corridor") || "",
    line: LEGACY_LINE_ALIASES[rawLine] || rawLine,
  };
  function syncURL() {
    BSD.setParams({
      overlays: BSDNet.serializeOverlays(state.overlays),
      floor: state.floor === "any" ? "" : state.floor,
      corridor: state.corridor,
      line: state.line,
    });
  }

  // Load data. network_nodes.json and mellow_connectors.geojson are newer
  // pipeline products that may 404 — degrade to an empty layer rather than
  // failing the whole page.
  async function loadOrEmpty(path, empty) {
    try {
      return await BSD.loadJSON(path);
    } catch (e) {
      return empty;
    }
  }

  const [bikeRoutes, plannedData, osmTrailsData, mainRoutesData, wardsData, nodesData, mellowConnectorsData] = await Promise.all([
    BSD.loadJSON("data/bike_routes.geojson"),
    BSD.loadJSON("data/planned_routes.geojson"),
    BSD.loadJSON("data/osm_trails.geojson"),
    BSD.loadJSON("data/main_routes.geojson"),
    BSD.loadJSON("data/wards.geojson"),
    loadOrEmpty("data/network_nodes.json", { nodes: [] }),
    loadOrEmpty("data/mellow_connectors.geojson", { features: [] }),
  ]);

  const routeFeatures = bikeRoutes.features;

  const rosterIndex = BSDNet.buildRosterIndex(mainRoutesData.features);
  const linesMeta = BSDNet.linesById(mainRoutesData.lines);
  const { roster: rosterFeatures, local: localFeatures } = BSDNet.splitByRoster(routeFeatures, rosterIndex);
  const rosterTrailFeatures = mainRoutesData.features.filter(
    (f) => (linesMeta.get(f.properties.line_id) || {}).source === "osm_trails"
  );
  const rosterStreetNames = BSDNet.rosterStreets(routeFeatures, rosterIndex);
  const corridorGroups = BSDNet.groupByCorridor(routeFeatures);

  /* ---------------- build the schematic network (v3 §2) ---------------- */
  // Members partition into per-line pools and canonical interlined trunks
  // (2+ line_ids — the downtown shared tracks). The model does the rest:
  // couplet collapse, trail graph tracing, chaining, pinning, angle
  // snapping, exact closure, displacement guard.

  const partsByLine = {};
  (mainRoutesData.lines || []).forEach((l) => { partsByLine[l.id] = []; });
  const trunkGroups = new Map();
  rosterFeatures.forEach((f) => {
    const entry = rosterIndex.get(String(f.properties.segment_id));
    if (!entry) return;
    const item = { latlngs: BSDNet.toLatLngs(f.geometry), grade: entry.grade, street: f.properties.street };
    if (entry.lineIds.length >= 2) {
      const key = entry.lineIds.slice().sort().join("|");
      if (!trunkGroups.has(key)) trunkGroups.set(key, { key, lineIds: entry.lineIds.slice().sort(), parts: [] });
      trunkGroups.get(key).parts.push(item);
    } else if (partsByLine[entry.lineId]) {
      partsByLine[entry.lineId].push(item);
    }
  });
  rosterTrailFeatures.forEach((f) => {
    if (partsByLine[f.properties.line_id]) {
      partsByLine[f.properties.line_id].push({ latlngs: BSDNet.toLatLngs(f.geometry), grade: "offstreet" });
    }
  });

  const NET = BSDNet.buildSchematicNetwork({
    lines: mainRoutesData.lines || [],
    partsByLine,
    trunks: [...trunkGroups.values()],
    nodes: nodesData.nodes || [],
  });

  // Ward boundaries: a faint, always-on city anchor beneath the network —
  // context only. Not interactive: a click on a ward falls through to the
  // map background (deselect).
  L.geoJSON(wardsData, {
    pane: "wardsPane", interactive: false,
    style: { color: "#e2e8f0", weight: 1, fill: false },
  }).addTo(map);

  /* ---------------- selection state ---------------- */

  let selectedLineIds = null; // Set<line id> | null

  let weightFactor = BSDNet.zoomWeightFactor(map.getZoom());

  function lineColor(lineId) {
    return BSDNet.LINE_COLORS[lineId] || BSDNet.FALLBACK_LINE_COLOR;
  }
  function isLineSelected(lineId) {
    return selectedLineIds != null && selectedLineIds.has(lineId);
  }
  function isDimmed(lineIds) {
    return selectedLineIds != null && !lineIds.some((id) => selectedLineIds.has(id));
  }

  /* ---------------- draw: spines (v3 §4, hollow per QA-gate fix 1) ----------------
   * Per line: white casing slices over the BUILT ranges only, then per
   * quality stretch, in this spine's own insertion order: offstreet's
   * darkened band (casing pane, over the white), the hue slice, and its
   * paint stripe. `nothing` stretches render as TWO OFFSET HUE RAILS with
   * no casing and no white core (the spec §15.3 variant): a white
   * casing/core under a hollow run severed every line it crossed —
   * Major Taylor visually broke where 83rd's hole crossed it — which is
   * the exact artifact this redesign exists to kill. Stripes render
   * immediately after their own spine's hue slices, NOT in a global pane.
   * Interior caps are butt; a round cap would bulge over the neighboring
   * rails and read as a blob at every quality transition. */

  const casingRecords = []; // { lineIds, layer, strandCount }
  const bandRecords = [];   // { lineIds, layer }
  const sliceRecords = [];  // solid: { lineIds, grade, display, layer, stripeLayer }
                            // hollow: { lineIds, grade, display: "nothing", rails: [a, b], center }
  const strandRecords = []; // { key, lineId, count, idx, grade, display, layer, center }

  // Source street names arrive SHOUTING from CDOT ("JACKSON"); title-case
  // them for prose, preserving directionals (N/S/E/W) and ordinal suffixes
  // (31ST, 79TH) that shouldn't be lowercased.
  function titleCaseStreet(name) {
    return String(name || "").toLowerCase().replace(/\b[a-z0-9]+\b/g, (w) => {
      if (/^[nsew]$/.test(w)) return w.toUpperCase();
      if (/^\d+(st|nd|rd|th)$/.test(w)) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    });
  }
  function coupletNoteFor(lineId) {
    const spine = NET.spines.get(lineId);
    if (!spine || !spine.coupletPairs || spine.coupletPairs.length === 0) return null;
    const pair = spine.coupletPairs[0];
    return `Runs as a ${BSD.esc(titleCaseStreet(pair.base))}/${BSD.esc(titleCaseStreet(pair.donor))} one-way pair — drawn as one line; each stretch shows the better facility of the pair.`;
  }

  function drawSpine(lineMeta, spine) {
    const lineId = lineMeta.id;
    const isTrail = spine.kind === "trail";
    const casingPane = isTrail ? "trailsOutlinePane" : "casingPane";
    const slicePane = isTrail ? "trailsPane" : "linesPane";
    const casingGroup = isTrail ? layers.trailsOutline : layers.casing;
    const sliceGroup = isTrail ? layers.trails : layers.lines;
    const coupletNote = coupletNoteFor(lineId);

    // Casing slices over contiguous BUILT ranges only — hollow ranges get
    // no casing, so crossing lines show through the rails' gap.
    const casingRanges = [];
    let open = null;
    spine.stretches.forEach((s) => {
      if (s.locked || BSDNet.displayGrade(s.grade) === "nothing") { open = null; return; }
      if (open && Math.abs(open.m1 - s.m0) < 0.01) { open.m1 = s.m1; }
      else { open = { m0: s.m0, m1: s.m1 }; casingRanges.push(open); }
    });
    casingRanges.forEach((r) => {
      const latlngs = BSDNet.sliceSpineByMeasure(spine, r.m0, r.m1);
      if (latlngs.length < 2) return;
      const casingLayer = L.polyline(latlngs, {
        pane: casingPane, color: "#ffffff", weight: 9, opacity: 1,
        lineCap: "butt", lineJoin: "round",
      });
      casingGroup.addLayer(casingLayer);
      casingRecords.push({ lineIds: [lineId], layer: casingLayer, strandCount: 1 });
    });

    spine.stretches.forEach((s) => {
      if (s.locked) return; // interlined trunk range — rendered once, below
      const display = BSDNet.displayGrade(s.grade);
      const latlngs = BSDNet.sliceSpineByMeasure(spine, s.m0, s.m1);
      if (latlngs.length < 2) return;

      if (display === "nothing") {
        // Hollow = two offset hue rails (offsets are pixel-constant,
        // re-derived per zoom by applyRailOffsets). The rails never drain
        // under a comfort floor (QA-gate fix 2): "no facility at all" is
        // floor-independent and must never converge with drained gray.
        const rails = [0, 1].map(() => {
          const rail = L.polyline(latlngs, {
            pane: slicePane, color: lineColor(lineId), weight: 1.2, opacity: 1,
            lineCap: "butt", lineJoin: "round",
          });
          rail.on("click", (e) => { L.DomEvent.stop(e); onLineClick(lineId); });
          // Cheap insurance against misreading a hollow run as a rendering
          // artifact: hovering the gap says what it means.
          rail.bindTooltip(coupletNote || "No bikeway here — you ride with traffic on this stretch.",
            { sticky: true, className: "couplet-tip" });
          sliceGroup.addLayer(rail);
          return rail;
        });
        sliceRecords.push({ lineIds: [lineId], grade: s.grade, display, rails, center: latlngs });
        return;
      }

      if (display === "offstreet") {
        // Darkened-hue band: a per-stretch w9 slice over the white casing
        // in the same pane — visually a darkened casing, structurally an
        // underlay slice (v3 §4.1).
        const band = L.polyline(latlngs, {
          pane: casingPane, color: BSDNet.darkenColor(lineColor(lineId), 0.35),
          weight: 9, opacity: 1, lineCap: "butt", lineJoin: "round",
        });
        casingGroup.addLayer(band);
        bandRecords.push({ lineIds: [lineId], layer: band });
      }

      const hue = L.polyline(latlngs, {
        pane: slicePane, color: lineColor(lineId), weight: 6, opacity: 1,
        lineCap: "butt", lineJoin: "round",
      });
      hue.on("click", (e) => { L.DomEvent.stop(e); onLineClick(lineId); });
      if (coupletNote) hue.bindTooltip(coupletNote, { sticky: true, className: "couplet-tip" });
      sliceGroup.addLayer(hue);

      let stripeLayer = null;
      if (display === "paint") {
        stripeLayer = L.polyline(latlngs, {
          pane: slicePane, color: "#ffffff", weight: 2, opacity: 1,
          lineCap: "butt", lineJoin: "round", interactive: false,
        });
        sliceGroup.addLayer(stripeLayer);
      }
      sliceRecords.push({ lineIds: [lineId], grade: s.grade, display, layer: hue, stripeLayer });
    });
  }

  // Interlined strands are spaced a fixed number of PIXELS apart, re-derived
  // on zoomend so shared runs read as parallel colored strands at every zoom.
  function strandGapPx() {
    return 6 * weightFactor + 1.5;
  }
  function braidWidthPx(strandCount) {
    return (strandCount - 1) * strandGapPx() + 6 * weightFactor;
  }
  function strandGapMeters(latlngs) {
    const refLat = latlngs[0][0];
    return strandGapPx() * BSDNet.metersPerPixel(refLat, map.getZoom());
  }

  const capsuleCandidates = []; // { pt, bearing, count }
  const capsuleRecords = [];    // { marker, bearing, count }

  function endBearing(latlngs, atStart) {
    const a = atStart ? latlngs[0] : latlngs[latlngs.length - 1];
    const b = atStart ? latlngs[1] : latlngs[latlngs.length - 2];
    return Math.atan2(a[1] - b[1], a[0] - b[0]);
  }
  function capsuleIcon(bearingRad, strandCount) {
    const deg = (bearingRad * 180) / Math.PI + 90; // perpendicular to travel
    const w = Math.max(16, Math.round(braidWidthPx(strandCount) + 6));
    const topPad = Math.round((w - 8) / 2);
    return L.divIcon({
      className: "capsule-marker",
      html: `<span style="transform: rotate(${deg.toFixed(1)}deg); width: ${w}px; margin-top: ${topPad}px"></span>`,
      iconSize: [w, w],
      iconAnchor: [w / 2, w / 2],
    });
  }

  function drawTrunk(trunk) {
    // Shared casing carries the trunk's structural treatment (v3 §7);
    // strands render solid hue always. Today's data has no grade-`none`
    // shared trunk (all three downtown trunks grade protected/paint), so
    // the hollow-casing case is clamped to solid until the data grows one.
    const casingLayer = L.polyline(trunk.latlngs, {
      pane: "casingPane", color: "#ffffff", weight: 9, opacity: 1,
      lineCap: "butt", lineJoin: "round",
    });
    layers.casing.addLayer(casingLayer);
    casingRecords.push({ lineIds: trunk.lineIds, layer: casingLayer, strandCount: trunk.lineIds.length });

    trunk.stretches.forEach((s) => {
      const center = BSDNet.sliceSpineByMeasure(trunk, s.m0, s.m1);
      if (center.length < 2) return;
      trunk.lineIds.forEach((lineId, idx) => {
        const layer = L.polyline(center, {
          pane: "linesPane", color: lineColor(lineId), weight: 6, opacity: 1,
          lineCap: "butt", lineJoin: "round",
        });
        layer.on("click", (e) => { L.DomEvent.stop(e); onLineClick(lineId); });
        layers.lines.addLayer(layer);
        strandRecords.push({
          key: trunk.key, lineId, count: trunk.lineIds.length, idx,
          grade: s.grade, display: BSDNet.displayGrade(s.grade), layer, center,
        });
      });
    });

    capsuleCandidates.push(
      { pt: trunk.latlngs[0], bearing: endBearing(trunk.latlngs, true), count: trunk.lineIds.length },
      { pt: trunk.latlngs[trunk.latlngs.length - 1], bearing: endBearing(trunk.latlngs, false), count: trunk.lineIds.length },
    );
  }

  (mainRoutesData.lines || []).forEach((lineMeta) => {
    const spine = NET.spines.get(lineMeta.id);
    if (!spine) return; // no_data lines: nothing to draw, never fabricate
    drawSpine(lineMeta, spine);
  });
  NET.trunks.forEach((trunk) => drawTrunk(trunk));

  // Capsules: trunks can share an endpoint (the Loop hub) — keep one
  // capsule per ~60 m cell, the widest braid winning.
  (function drawCapsules() {
    const cells = new Map();
    capsuleCandidates.forEach((c) => {
      const mLng = 111320 * Math.cos((c.pt[0] * Math.PI) / 180);
      const cell = Math.round((c.pt[0] * 111320) / 60) + ":" + Math.round((c.pt[1] * mLng) / 60);
      if (!cells.has(cell) || cells.get(cell).count < c.count) cells.set(cell, c);
    });
    cells.forEach((c) => {
      const marker = L.marker(c.pt, {
        pane: "capsulesPane", icon: capsuleIcon(c.bearing, c.count), interactive: false,
      });
      layers.capsules.addLayer(marker);
      capsuleRecords.push({ marker, bearing: c.bearing, count: c.count, pt: c.pt });
    });
  })();

  // A capsule already says "transfer here" better than a plain circle, so
  // suppress any interchange pin sitting under a capsule's footprint —
  // otherwise the Loop hub stacks a pin cluster behind the pill.
  function underCapsule(latlng) {
    return capsuleRecords.some((c) => {
      const mLng = 111320 * Math.cos((c.pt[0] * Math.PI) / 180);
      const d = Math.hypot((latlng[0] - c.pt[0]) * 111320, (latlng[1] - c.pt[1]) * mLng);
      return d <= 140;
    });
  }

  // Re-derive strand offsets for the current zoom (pixel-constant spacing).
  function applyStrandOffsets() {
    strandRecords.forEach((rec) => {
      if (rec.count < 2) return;
      const offsets = BSDNet.strandOffsets(rec.count, strandGapMeters(rec.center));
      rec.layer.setLatLngs(BSDNet.offsetLatLngs(rec.center, offsets[rec.idx]));
    });
    capsuleRecords.forEach((c) => c.marker.setIcon(capsuleIcon(c.bearing, c.count)));
  }

  // Hollow rails are also pixel-constant offsets from the spine center,
  // re-derived on every zoom step (rec._railOffsetPx is set by
  // restyleSlice from the current fillPlan).
  function applyRailOffsets() {
    sliceRecords.forEach((rec) => {
      if (!rec.rails) return;
      const px = rec._railOffsetPx || 0;
      const mpp = BSDNet.metersPerPixel(rec.center[0][0], map.getZoom());
      rec.rails.forEach((rail, i) => {
        rail.setLatLngs(BSDNet.offsetLatLngs(rec.center, (i === 0 ? -1 : 1) * px * mpp));
      });
    });
  }

  /* ---------------- restyle machinery (floor / selection / zoom) ---------------- */
  // Everything restyles via setStyle on existing polylines — geometry is
  // never rebuilt. Below-floor stretches DRAIN: hue -> DRAINED_COLOR at
  // full silhouette width and SCHEMATIC.drainedOpacity; the structural
  // fill (stripe/core) stays, so drained hollow still reads as hollow
  // (v3 §4.4 — "routes never break" is literally true).

  function restyleSlice(rec) {
    const lineId = rec.lineIds[0];
    const dim = isDimmed(rec.lineIds) ? 0.6 : 1;
    const selected = rec.lineIds.some(isLineSelected);
    const scaled = 6 * weightFactor;
    const plan = BSDNet.fillPlan(rec.display, scaled);

    if (rec.rails) {
      // Hollow rails: hue always — absence is floor-independent (QA-gate
      // fix 2), so `nothing` never drains to gray. Below the clamp the
      // rails collapse onto the centerline at fallback opacity.
      const hollow = plan.coreWidth > 0;
      const railWeight = hollow ? (scaled - plan.coreWidth) / 2 : scaled;
      rec._railOffsetPx = hollow ? (plan.coreWidth + railWeight) / 2 : 0;
      rec.rails.forEach((rail) => rail.setStyle({
        color: lineColor(lineId),
        weight: railWeight + (selected ? 0.5 : 0),
        opacity: dim * (hollow ? 1 : BSDNet.SCHEMATIC.hollowFallbackOpacity),
      }));
      return;
    }

    const drained = !BSDNet.meetsFloor(rec.grade, state.floor);
    rec.layer.setStyle({
      color: drained ? BSDNet.DRAINED_COLOR : lineColor(lineId),
      weight: scaled + (selected ? 2 : 0),
      opacity: dim * (drained ? BSDNet.SCHEMATIC.drainedOpacity : 1),
    });
    if (rec.stripeLayer) {
      rec.stripeLayer.setStyle({
        weight: Math.max(plan.stripeWidth, 0.1),
        opacity: plan.stripeWidth > 0 ? dim : 0,
      });
    }
  }

  function restyleStrand(rec) {
    const dim = isDimmed([rec.lineId]) ? 0.6 : 1;
    const selected = isLineSelected(rec.lineId);
    const drained = !BSDNet.meetsFloor(rec.grade, state.floor);
    rec.layer.setStyle({
      color: drained ? BSDNet.DRAINED_COLOR : lineColor(rec.lineId),
      weight: 6 * weightFactor + (selected ? 2 : 0),
      opacity: dim * (drained ? BSDNet.SCHEMATIC.drainedOpacity : 1),
    });
  }

  function restyleAll() {
    casingRecords.forEach((rec) => {
      const extra = (rec.strandCount - 1) * strandGapPx();
      rec.layer.setStyle({
        weight: 9 * weightFactor + extra,
        opacity: isDimmed(rec.lineIds) ? 0.6 : 1,
      });
    });
    bandRecords.forEach((rec) => {
      rec.layer.setStyle({ weight: 9 * weightFactor, opacity: isDimmed(rec.lineIds) ? 0.6 : 1 });
    });
    sliceRecords.forEach(restyleSlice);
    strandRecords.forEach(restyleStrand);
  }

  // Selection halo (v3 §5): ONE polyline per selected spine, from the
  // schematic geometry — aligned with the drawn line by construction (the
  // old per-member rebuild would ghost the true alignment up to 250 m off
  // the schematic stroke).
  function updateHalo() {
    layers.halo.clearLayers();
    if (!selectedLineIds) return;
    selectedLineIds.forEach((lineId) => {
      const spine = NET.spines.get(lineId);
      if (!spine) return;
      layers.halo.addLayer(L.polyline(spine.latlngs, {
        pane: "haloPane", color: lineColor(lineId),
        weight: 16 * weightFactor, opacity: 0.25, lineCap: "round", lineJoin: "round",
      }));
    });
  }

  /* ---------------- detail card (v3 §9) ---------------- */

  function updateDetailCard() {
    const slot = document.getElementById("detail-card");
    if (!selectedLineIds || selectedLineIds.size === 0) {
      slot.innerHTML = `<p class="muted card-placeholder">appears when you click a route</p>`;
      return;
    }
    slot.innerHTML = [...selectedLineIds].map((id) => detailCardHTML(linesMeta.get(id))).filter(Boolean).join("");
  }

  const LEVEL_LABELS = {
    offstreet: "off-street", protected: "protected",
    paint: "paint & greenway", nothing: "nothing",
  };

  // Every mix-bar width comes from ONE denominator: the spine's stretch
  // measure ranges (the bar is literally proportional to the drawn line).
  // Printed numbers for the built levels stay pipeline miles_by_grade (the
  // honest number); "nothing" is derived render-time from pre-absorption
  // extents and SUBSUMES the pipeline `none` bucket — never both.
  function mixStretchLists(lineId) {
    const spine = NET.spines.get(lineId);
    if (!spine) return [];
    const lists = [spine.preAbsorption.filter((s) => !s.locked)];
    NET.trunks.forEach((t) => {
      if (t.lineIds.includes(lineId)) lists.push(t.preAbsorption);
    });
    return lists;
  }

  function printedMiles(lineMeta, level, spineNothingM) {
    const by = lineMeta.miles_by_grade || {};
    if (level === "offstreet") return by.offstreet;
    if (level === "protected") return by.protected;
    if (level === "paint") return (by.paint || 0) + (by.mellow || 0) || undefined;
    if (level === "nothing") return spineNothingM / 1609.344;
    return undefined;
  }

  function detailCardHTML(lineMeta) {
    if (!lineMeta) return "";
    const color = lineColor(lineMeta.id);
    const isTrail = lineMeta.source === "osm_trails";
    const tierLabel = isTrail ? "Trail" : "Main route";
    const tier = BSD.lineBadgeTier(lineMeta);

    if (lineMeta.no_data) {
      return `
        <div class="detail-card">
          <div class="detail-card-head"><span class="dot" style="background:${color}"></span><strong>${BSD.esc(lineMeta.name)}</strong> ${BSD.badgeHTML(tier)}</div>
          <div class="muted" style="margin-left:1.1rem;">${BSD.esc(tierLabel)}</div>
          <p class="muted">No data yet — fills in with the first live data pull. We never draw fabricated geometry.</p>
        </div>
      `;
    }

    const spine = NET.spines.get(lineMeta.id);
    const segs = BSDNet.levelMixSegments(mixStretchLists(lineMeta.id));
    const nothingM = spine ? spine.nothingM : 0;
    const legendRows = segs.map((s) => {
      const mi = printedMiles(lineMeta, s.level, nothingM);
      const printed = s.level === "nothing"
        ? `about ${mi.toFixed(mi < 1 ? 1 : 0)} mi with nothing built`
        : (mi != null ? `${Number(mi).toFixed(1)} mi` : `${s.pct.toFixed(0)}%`);
      return `<span><i style="background:${s.color}"></i>${BSD.esc(LEVEL_LABELS[s.level])} — ${BSD.esc(printed)}</span>`;
    }).join("");
    const mixHTML = segs.length
      ? `
        <div class="muted" style="margin:.4rem 0 .25rem;">Along the line</div>
        <div class="mix-bar" role="img" aria-label="Quality along ${BSD.esc(lineMeta.name)}">
          ${segs.map((s) => `<span class="mix-seg level-${s.level}" style="width:${s.pct.toFixed(2)}%;background:${s.color}"></span>`).join("")}
        </div>
        <div class="mix-legend">${legendRows}</div>
      `
      : "";
    const coupletNote = coupletNoteFor(lineMeta.id);

    return `
      <div class="detail-card">
        <div class="detail-card-head"><span class="dot" style="background:${color}"></span><strong>${BSD.esc(lineMeta.name)}</strong> ${BSD.badgeHTML(tier)}</div>
        <div class="muted" style="margin-left:1.1rem;">${BSD.esc(tierLabel)}</div>
        ${mixHTML}
        ${coupletNote ? `<p class="muted couplet-note">${coupletNote}</p>` : ""}
        ${lineMeta.termini ? `<div class="detail-card-termini muted">${BSD.esc(lineMeta.termini)}</div>` : ""}
      </div>
    `;
  }

  // Connector detail-card title per comfort grade: names the grade the way
  // the tier row's tint note does. Unknown grade -> the `none` label.
  const CONNECTOR_GRADE_LABELS = {
    protected: "Protected connector",
    paint: "Painted connector",
    mellow: "Mellow connector",
    none: "Connector",
  };
  function connectorGradeLabel(grade) {
    return CONNECTOR_GRADE_LABELS[grade] || CONNECTOR_GRADE_LABELS.none;
  }

  function selectLine(lineId, opts) {
    const o = opts || {};
    selectedLineIds = new Set([lineId]);
    state.line = lineId;
    state.corridor = "";
    restyleAll();
    updateHalo();
    updateDetailCard();
    highlightRosterRow(lineId);
    syncURL();
    if (o.fitBounds) fitLineBounds(lineId);
  }

  // Visual half of deselection only — shared by deselect() and the
  // non-selection detail entry points (showSegmentDetail, showNodeDetail)
  // so clicking a connector/segment/node while a roster line is selected
  // never leaves a stale halo/dim/roster-highlight behind.
  function clearSelectionVisuals() {
    if (!selectedLineIds) return;
    selectedLineIds = null;
    restyleAll();
    updateHalo();
    updateDetailCard();
    highlightRosterRow(null);
  }

  function deselect() {
    if (!selectedLineIds) return;
    clearSelectionVisuals();
    state.line = "";
    syncURL();
  }

  function highlightRosterRow(lineId) {
    document.querySelectorAll(".roster-row").forEach((el) => {
      el.classList.toggle("selected", el.dataset.line === lineId);
    });
  }

  function spineBounds(lineId) {
    const spine = NET.spines.get(lineId);
    if (!spine || spine.latlngs.length === 0) return null;
    let minLat = Infinity, maxLat = -Infinity, minLng = Infinity, maxLng = -Infinity;
    spine.latlngs.forEach(([lat, lng]) => {
      minLat = Math.min(minLat, lat); maxLat = Math.max(maxLat, lat);
      minLng = Math.min(minLng, lng); maxLng = Math.max(maxLng, lng);
    });
    const pad = 0.0006;
    return [[minLat - pad, minLng - pad], [maxLat + pad, maxLng + pad]];
  }

  function fitLineBounds(lineId) {
    const bounds = spineBounds(lineId);
    if (bounds) map.fitBounds(bounds, { padding: [50, 50], animate: false });
  }

  function onLineClick(lineId) {
    if (selectedLineIds && selectedLineIds.size === 1 && selectedLineIds.has(lineId)) {
      deselect();
    } else {
      selectLine(lineId, { fitBounds: false });
    }
  }

  /* ---------------- draw: connectors (v2 spec §1/§12, unchanged) ---------------- */
  // One tier, three sources: non-roster bike_routes, deduped mellow
  // geometry (may 404, degrades to []), and non-roster named OSM trails.
  // Connectors keep RDP-40 geographic geometry (schematicLatLngs) — they
  // are background texture, not schematic lines (v3 §2.6).
  const connectorRecords = []; // { layer, grade }
  const mellowConnectorCanvas = L.canvas({ pane: "connectorsPane" });
  function drawConnector(feature, pane, extraProps, renderer) {
    const props = extraProps || {};
    const grade = props._mellowConnector ? "mellow"
      : props._trail ? "offstreet"
      : BSDNet.CONNECTOR_GRADE_MAP[feature.properties.facility_category] || "none";
    const opts = { pane, lineCap: "round", lineJoin: "round", ...BSDNet.connectorStyle(grade) };
    if (renderer) opts.renderer = renderer;
    const line = L.polyline(BSDNet.schematicLatLngs(feature.geometry), opts);
    line.feature = feature;
    line._connectorGrade = grade;
    line.on("click", (e) => { L.DomEvent.stop(e); showSegmentDetail({ ...feature, ...extraProps, _connectorGrade: grade }); });
    layers.connectors.addLayer(line);
    connectorRecords.push({ layer: line, grade });
    return line;
  }
  localFeatures.forEach((feature) => drawConnector(feature, "connectorsPane"));
  (mellowConnectorsData.features || []).forEach((feature) =>
    drawConnector(feature, "connectorsPane", { _mellowConnector: true }, mellowConnectorCanvas));
  const nonRosterTrailFeatures = (osmTrailsData.features || []).filter(
    (f) => !rosterIndex.has(String(f.properties.segment_id))
  );
  nonRosterTrailFeatures.forEach((feature) => drawConnector(feature, "connectorsPane", { _trail: true }));

  /* ---------------- labels (v3 §8) ---------------- */
  // Main label: midpoint of the line's longest schematic run, offset
  // labelOffsetPx perpendicular — to the LEFT of increasing measure,
  // flipped when that side hosts another spine within labelClearPx at the
  // anchor. Terminus labels at both spine ends. Shipped unrotated.

  const M_PER_DEG_LAT = 111320;
  function segMeters(a, b) {
    const mLng = M_PER_DEG_LAT * Math.cos(((a[0] + b[0]) / 2) * Math.PI / 180);
    return Math.hypot((a[0] - b[0]) * M_PER_DEG_LAT, (a[1] - b[1]) * mLng);
  }
  function distToOtherSpines(latlng, excludeId) {
    let best = Infinity;
    NET.spines.forEach((spine, id) => {
      if (id === excludeId) return;
      const hit = BSDNet.snapPointToPath(latlng, spine.latlngs);
      if (hit && hit.dist < best) best = hit.dist;
    });
    return best;
  }
  // Collision bookkeeping (QA-gate fix 4): label boxes are estimated in
  // layer-pixel space at the citywide build zoom (~ name.length × 6.5 px
  // wide, 14 px tall). Resolution order: preferred side -> flipped side ->
  // slide along the run (±60/±120 px). Two overlapping labels at the
  // default view are illegible — that's a fail, not polish.
  const placedLabelBoxes = [];
  function labelBox(latlng, offsetPx, name) {
    const pt = map.latLngToLayerPoint(latlng);
    const w = name.length * 6.5, h = 14;
    return { x: pt.x + offsetPx[0] - w / 2, y: pt.y + offsetPx[1] - h / 2, w, h };
  }
  function boxCollides(b) {
    return placedLabelBoxes.some((o) =>
      !(b.x + b.w < o.x || o.x + o.w < b.x || b.y + b.h < o.y || o.y + o.h < b.y));
  }

  function lineLabelPlacement(lineId, spine, name) {
    let best = null;
    for (let i = 0; i < spine.latlngs.length - 1; i++) {
      const len = segMeters(spine.latlngs[i], spine.latlngs[i + 1]);
      if (best == null || len > best.len) best = { i, len };
    }
    if (!best) return null;
    const a = spine.latlngs[best.i], b = spine.latlngs[best.i + 1];
    const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    const mLng = M_PER_DEG_LAT * Math.cos(mid[0] * Math.PI / 180);
    // Travel direction in east/north meters; left of travel = (-n, e).
    const e = (b[1] - a[1]) * mLng, n = (b[0] - a[0]) * M_PER_DEG_LAT;
    const norm = Math.hypot(e, n) || 1;
    const travelE = e / norm, travelN = n / norm;
    let leftE = -travelN, leftN = travelE;
    const mpp = BSDNet.metersPerPixel(mid[0], map.getZoom());
    const clearM = BSDNet.SCHEMATIC.labelClearPx * mpp;
    const probe = [
      mid[0] + (leftN * BSDNet.SCHEMATIC.labelOffsetPx * mpp) / M_PER_DEG_LAT,
      mid[1] + (leftE * BSDNet.SCHEMATIC.labelOffsetPx * mpp) / mLng,
    ];
    if (distToOtherSpines(probe, lineId) < clearM) { leftE = -leftE; leftN = -leftN; }

    const offsetFor = (lE, lN) => [
      Math.round(lE * BSDNet.SCHEMATIC.labelOffsetPx),
      Math.round(-lN * BSDNet.SCHEMATIC.labelOffsetPx),
    ];
    const slideTo = (slidePx) => [
      mid[0] + (travelN * slidePx * mpp) / M_PER_DEG_LAT,
      mid[1] + (travelE * slidePx * mpp) / mLng,
    ];
    // Candidate order: hand-rule side, flipped side, then slides along the
    // run on the hand-rule side.
    const candidates = [
      { latlng: mid, offset: offsetFor(leftE, leftN) },
      { latlng: mid, offset: offsetFor(-leftE, -leftN) },
      { latlng: slideTo(60), offset: offsetFor(leftE, leftN) },
      { latlng: slideTo(-60), offset: offsetFor(leftE, leftN) },
      { latlng: slideTo(120), offset: offsetFor(leftE, leftN) },
    ];
    const pick = candidates.find((c) => !boxCollides(labelBox(c.latlng, c.offset, name))) || candidates[0];
    placedLabelBoxes.push(labelBox(pick.latlng, pick.offset, name));
    return pick;
  }

  // Long lines first, so the network's anchors claim space before the
  // short lines squeeze in around them.
  const labelOrder = (mainRoutesData.lines || []).slice().sort((a, b) => {
    const sa = NET.spines.get(a.id), sb = NET.spines.get(b.id);
    return ((sb ? sb.m[sb.m.length - 1] : 0) - (sa ? sa.m[sa.m.length - 1] : 0));
  });
  const terminusCells = new Map(); // shared-terminus stacking (merged pins)
  labelOrder.forEach((lineMeta) => {
    const spine = NET.spines.get(lineMeta.id);
    if (!spine) return; // no_data lines: nothing to label, never fabricate
    const color = lineColor(lineMeta.id);
    const isTrail = lineMeta.source === "osm_trails";
    const place = lineLabelPlacement(lineMeta.id, spine, lineMeta.name);
    if (place) {
      const tooltip = L.tooltip({
        permanent: true, direction: "center", className: "line-label", offset: place.offset,
      })
        .setLatLng(place.latlng)
        .setContent(`<span style="color:${color}">${BSD.esc(lineMeta.name)}</span>`);
      (isTrail ? layers.lineLabelsTrails : layers.lineLabelsStreets).addLayer(tooltip);
    }
    // Terminus labels only earn their ink on long lines — on a short line
    // (the 606 is 2.7 mi) they just triple the mid-line label. Lines
    // sharing a merged terminus pin stack their labels instead of
    // overprinting.
    const spineMeters = spine.m[spine.m.length - 1] || 0;
    if (spineMeters > 8000) {
      const terminusGroup = isTrail ? layers.terminusLabelsTrails : layers.terminusLabelsStreets;
      [spine.latlngs[0], spine.latlngs[spine.latlngs.length - 1]].forEach((pt) => {
        const cell = Math.round(pt[0] * 2000) + ":" + Math.round(pt[1] * 2000); // ~50 m
        const stackIdx = terminusCells.get(cell) || 0;
        terminusCells.set(cell, stackIdx + 1);
        terminusGroup.addLayer(
          L.tooltip({
            permanent: true, direction: "top", className: "terminus-label",
            offset: [0, -6 - stackIdx * 12],
          })
            .setLatLng(pt)
            .setContent(`<span style="color:${color}">${BSD.esc(lineMeta.name)}</span>`)
        );
      });
    }
  });

  corridorGroups.forEach((feats, street) => {
    if (rosterStreetNames.has(street)) return;
    const longest = feats.reduce((best, f) =>
      (f.properties.length_m || 0) > (best.properties.length_m || 0) ? f : best
    );
    const coords = BSDNet.flattenCoords(longest.geometry);
    const midPt = coords[Math.floor(coords.length / 2)];
    const tooltip = L.tooltip({ permanent: true, direction: "center", className: "line-label" })
      .setLatLng([midPt[1], midPt[0]])
      .setContent(BSD.esc(street));
    layers.labels.addLayer(tooltip);
  });

  /* ---------------- planned overlay (unchanged from v1) ---------------- */

  if (plannedData.features.length > 0) {
    plannedData.features.forEach((feature) => {
      const latlngs = BSDNet.schematicLatLngs(feature.geometry);
      const props = feature.properties;
      const color = BSD.FACILITY_COLORS[props.facility_category] || BSD.FACILITY_COLORS.other;

      const casing = L.polyline(latlngs, {
        pane: "plannedCasingPane", weight: 8, color: "#ffffff", dashArray: "10,8", opacity: 1, lineCap: "round",
      });
      layers.plannedCasing.addLayer(casing);

      const line = L.polyline(latlngs, {
        pane: "plannedPane", color, weight: 5, dashArray: "10,8", opacity: 0.85, lineCap: "round",
      });
      line.on("click", (e) => { L.DomEvent.stop(e); showSegmentDetail({ ...feature, _planned: true }); });
      layers.planned.addLayer(line);
    });
  }

  /* ---------------- nodes (v3 §8: pinned interchanges + snapped orientation) ---------------- */
  // Interchange markers come straight from the model's control points —
  // after schematization every interchange sits exactly on every line
  // through it, by construction, and the grid merge already deduped the
  // downtown cluster. Orientation nodes snap onto the nearest spine.

  const NODE_MARKER_STYLE = {
    interchange: { radius: 5, color: "#1a2330", weight: 2.5 },
    orientation: { radius: 3.5, color: "#64748b", weight: 2 },
  };
  function makeNodeMarker(n, kind) {
    const style = NODE_MARKER_STYLE[kind];
    const marker = L.circleMarker([n.lat, n.lng], {
      pane: "nodesPane", radius: style.radius, color: style.color, weight: style.weight,
      fillColor: "#ffffff", fillOpacity: 1,
    });
    const tooltipOpts = kind === "orientation"
      ? { permanent: true, direction: "top", className: "node-label", offset: [0, -6] }
      : { direction: "top", offset: [0, -8] };
    marker.bindTooltip(BSD.esc(n.label), tooltipOpts);
    marker.on("click", (e) => { L.DomEvent.stop(e); showNodeDetail(n); });
    return marker;
  }
  NET.interchanges.forEach((n) => {
    if (underCapsule(n.latlng)) return; // the capsule already marks this transfer
    layers.nodesInterchange.addLayer(makeNodeMarker({
      lat: n.latlng[0], lng: n.latlng[1], label: n.label, lines: n.lines,
    }, "interchange"));
  });
  (nodesData.nodes || []).filter((n) => n.kind === "orientation").forEach((n) => {
    let best = null;
    NET.spines.forEach((spine) => {
      const hit = BSDNet.snapPointToPath([n.lat, n.lng], spine.latlngs);
      if (hit && (best == null || hit.dist < best.dist)) best = hit;
    });
    const pos = best && best.dist <= 400 ? best.pt : [n.lat, n.lng];
    layers.nodesOrientation.addLayer(makeNodeMarker({ ...n, lat: pos[0], lng: pos[1] }, "orientation"));
  });

  /* ---------------- mount layers per state.overlays ---------------- */

  layers.halo.addTo(map);

  if (state.overlays.has("main")) { layers.casing.addTo(map); layers.lines.addTo(map); layers.capsules.addTo(map); }
  if (state.overlays.has("trails")) { layers.trailsOutline.addTo(map); layers.trails.addTo(map); layers.lineLabelsTrails.addTo(map); }
  if (state.overlays.has("connectors")) layers.connectors.addTo(map);
  if (state.overlays.has("planned")) { layers.planned.addTo(map); layers.plannedCasing.addTo(map); }

  function setLayerVisible(layer, visible) {
    if (visible) {
      if (!map.hasLayer(layer)) layer.addTo(map);
    } else if (map.hasLayer(layer)) {
      map.removeLayer(layer);
    }
  }

  // Per-record connector floor membership: each connector hides when its
  // grade is below the current floor (floors *reveal* the qualifying
  // background network instead of nuking the whole tier).
  function applyConnectorFloor() {
    connectorRecords.forEach((rec) => {
      const show = BSDNet.meetsFloor(rec.grade, state.floor);
      if (show) {
        if (!layers.connectors.hasLayer(rec.layer)) layers.connectors.addLayer(rec.layer);
      } else if (layers.connectors.hasLayer(rec.layer)) {
        layers.connectors.removeLayer(rec.layer);
      }
    });
  }

  function applyFloor() {
    setLayerVisible(layers.connectors, state.overlays.has("connectors"));
    applyConnectorFloor();
    sliceRecords.forEach(restyleSlice);
    strandRecords.forEach(restyleStrand);
  }

  function restyleStaticWeights() {
    connectorRecords.forEach((rec) => rec.layer.setStyle({ weight: BSDNet.CONNECTOR_STYLE.weight * weightFactor }));
    layers.planned.eachLayer((l) => l.setStyle({ weight: 5 * weightFactor }));
    layers.plannedCasing.eachLayer((l) => l.setStyle({ weight: 8 * weightFactor }));
  }

  function applyZoomWeights() {
    const f = BSDNet.zoomWeightFactor(map.getZoom());
    if (f !== weightFactor) {
      weightFactor = f;
      restyleAll();
      updateHalo();
      restyleStaticWeights();
    }
    // Strand spacing is pixel-constant, so it changes on EVERY zoom step.
    applyStrandOffsets();
    applyRailOffsets();
  }

  function updateDeclutter() {
    const z = map.getZoom();
    setLayerVisible(layers.lineLabelsStreets, state.overlays.has("main") && z >= BSDNet.ZOOM.lineLabels);
    // Terminus labels wait for street zoom — at the citywide fit they
    // would double every line name (main label + two termini).
    setLayerVisible(layers.terminusLabelsStreets, state.overlays.has("main") && z >= BSDNet.ZOOM.corridorLabels);
    setLayerVisible(layers.terminusLabelsTrails, state.overlays.has("trails") && z >= BSDNet.ZOOM.corridorLabels);
    // Interchange pins wait one zoom past the citywide fit: at z11 the
    // downtown cluster fuses into unreadable blobs (the Lake-corridor
    // "88"), and the metro lines already communicate the network there.
    setLayerVisible(layers.nodesInterchange, state.overlays.has("nodes") && z > BSDNet.ZOOM.interchangeNodes);
    setLayerVisible(layers.nodesOrientation, state.overlays.has("nodes") && z >= BSDNet.ZOOM.corridorLabels);
    // Corridor labels are for connector-tier streets: coarser floor === "any"
    // gate on purpose — once a floor thins the background mesh it's meant to
    // read sparse.
    setLayerVisible(layers.labels, state.overlays.has("connectors") && state.floor === "any" && z >= BSDNet.ZOOM.corridorLabels);
  }
  map.on("zoomend", () => {
    applyZoomWeights();
    updateDeclutter();
  });

  // Fit bounds to bike network. animate: false so a ?corridor=/?line=
  // restore further down can override it synchronously.
  if (routeFeatures.length > 0) {
    const allBounds = BSDNet.unionBBox(routeFeatures);
    map.fitBounds(allBounds, { padding: [50, 50], animate: false });
  }
  updateDeclutter();
  weightFactor = BSDNet.zoomWeightFactor(map.getZoom());
  restyleAll();
  restyleStaticWeights();
  applyStrandOffsets();
  applyRailOffsets();

  /* ---------------- deselect triggers ---------------- */
  map.on("click", deselect);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") deselect();
  });

  /* ---------------- side panel (v3 §9) ---------------- */

  const plannedBadgeTier = plannedData.properties?.status === "no_data_yet"
    ? "stub"
    : (plannedData.features[0]?.properties?.data_tier || "real");

  const TIER_ROWS = [
    { id: "trails", name: "Trails", desc: "off-street paths", swatchClass: "swatch-trail", tiers: ["crowdsourced"] },
    { id: "main", name: "Main routes", desc: "major on-street routes", swatchClass: "swatch-main", tiers: ["derived"] },
    { id: "connectors", name: "Connectors", desc: "short rideable links between routes", swatchClass: "swatch-connector", tiers: ["real", "crowdsourced"] },
  ];
  function tierBadgesHTML(tiers) {
    if (tiers.length === 1) return BSD.badgeHTML(tiers[0]);
    return `<span class="tier-badges-wrap">${tiers.map((t) => BSD.badgeHTML(t)).join("")}</span>`;
  }
  function tierRowHTML(t) {
    return `
      <div class="filter-row">
        <input type="checkbox" id="${t.id}-toggle" ${state.overlays.has(t.id) ? "checked" : ""}>
        <label for="${t.id}-toggle" class="tier-label">
          <span class="tier-swatch ${t.swatchClass}"></span>
          <span class="tier-text"><span class="tier-name">${BSD.esc(t.name)}</span><span class="muted tier-desc">${BSD.esc(t.desc)}</span></span>
        </label>
        ${tierBadgesHTML(t.tiers)}
      </div>
    `;
  }

  // "How to read a line" (v3 §9.1): a permanent legend of the four
  // structural inks, heaviest to hollow — replacing the v2 quality-border
  // toggle. Quality is intrinsic and always on now. "Nothing" gets the
  // full sentence: it is the level most likely to be misread as a
  // rendering artifact.
  function readLegendHTML() {
    return `
      <div class="read-legend">
        <div class="muted" style="margin-bottom:.3rem;">How to read a line</div>
        <div class="read-row"><span class="read-swatch read-offstreet"></span><span>off-street</span></div>
        <div class="read-row"><span class="read-swatch read-protected"></span><span>protected</span></div>
        <div class="read-row"><span class="read-swatch read-paint"></span><span>paint &amp; greenway</span></div>
        <div class="read-row"><span class="read-swatch read-nothing"></span><span>nothing — no bikeway here; you ride with traffic</span></div>
        <div class="read-row"><span class="capsule-glyph" aria-hidden="true"></span><span>transfer — routes meet or share track</span></div>
        <p class="muted quality-footnote">gaps shorter than ~250 m render as continuous</p>
      </div>
    `;
  }

  const FLOOR_OPTIONS = [["any", "Any"], ["paint", "Paint +"], ["protected", "Protected only"]];
  function floorControlHTML() {
    return `
      <div class="segmented" role="group" aria-label="Comfort floor">
        ${FLOOR_OPTIONS.map(([id, label]) =>
          `<button type="button" class="segmented-opt${state.floor === id ? " active" : ""}" data-floor="${id}">${BSD.esc(label)}</button>`
        ).join("")}
      </div>
      <p class="muted caption">below your bar, stretches lose their color — the line never breaks</p>
      <p class="muted caption">floors hide connectors below your bar — greenway links need Any</p>
    `;
  }

  // Roster mini-bars (v3 §9.4): the full four-ink dialect doesn't survive
  // 60×6 px, so rows use a degraded dialect at 8 px — solid-dark /
  // solid / diagonal hatch / hollow outline box.
  function rosterRowHTML(lineMeta) {
    const color = lineColor(lineMeta.id);
    const segs = BSDNet.levelMixSegments(mixStretchLists(lineMeta.id));
    const bar = segs.length
      ? segs.map((s) => `<span class="mm-${s.level}" style="width:${s.pct.toFixed(2)}%"></span>`).join("")
      : `<span style="width:100%;background:${color}"></span>`;
    return `
      <button type="button" class="roster-row${lineMeta.no_data ? " no-data" : ""}" data-line="${BSD.esc(lineMeta.id)}">
        <span class="dot" style="background:${color}"></span>
        <span class="roster-row-name">${BSD.esc(lineMeta.name)}</span>
        <span class="mini-mix">${bar}</span>
      </button>
    `;
  }
  const allLines = mainRoutesData.lines || [];
  const trailLines = allLines.filter((l) => l.source === "osm_trails");
  const streetLines = allLines.filter((l) => l.source !== "osm_trails");
  function rosterGroupHTML(title, lines, tier) {
    if (lines.length === 0) return "";
    return `<div class="roster-group-title">${BSD.esc(title)} ${BSD.badgeHTML(tier)}</div>${lines.map(rosterRowHTML).join("")}`;
  }

  const side = document.getElementById("side");
  side.innerHTML = `
    <div>
      <h2>Route tiers</h2>

      <div class="layer-control tier-toggles">
        ${TIER_ROWS.map(tierRowHTML).join("")}
      </div>
      <div id="connector-tint-note" class="muted caption" style="display:${state.overlays.has("connectors") ? "" : "none"};">
        connector tints reflect facility type (green built, lavender mellow) — not a safety metric
      </div>
      <p class="muted caption">Schematic view — lines simplified, shifted up to ~250 m · <a href="map.html">true geometry on the Map tab</a></p>

      <hr class="panel-divider">

      ${readLegendHTML()}

      <div class="comfort-floor">
        <div class="muted" style="margin-bottom:.3rem;">Comfort floor</div>
        ${floorControlHTML()}
      </div>

      <hr class="panel-divider">

      <div class="side-detail" id="detail-card">
        <p class="muted card-placeholder">appears when you click a route</p>
      </div>

      <hr class="panel-divider">

      <div class="filter-row">
        <input type="checkbox" id="nodes-toggle" ${state.overlays.has("nodes") ? "checked" : ""}>
        <label for="nodes-toggle">Nodes ${BSD.badgeHTML("derived")}</label>
      </div>
      <div class="filter-row">
        <input type="checkbox" id="planned-toggle" ${state.overlays.has("planned") ? "checked" : ""}>
        <label for="planned-toggle">Planned routes ${BSD.badgeHTML(plannedBadgeTier)}</label>
      </div>

      <div class="roster-title">All routes</div>
      <div class="roster-list">
        ${rosterGroupHTML("Trails", trailLines, "crowdsourced")}
        ${rosterGroupHTML("Main routes", streetLines, "derived")}
      </div>

      ${BSD.noticeHTML("directional")}
      <div class="side-detail" id="detail"></div>
    </div>
  `;

  // Schematic provenance chip on the map itself (v3 §9.6) — the honesty
  // note travels with the map, not just the panel.
  const chip = document.createElement("div");
  chip.className = "schematic-chip";
  chip.innerHTML = `Schematic view — lines simplified, shifted up to ~250 m · <a href="map.html">true geometry on the Map tab</a>`;
  document.querySelector(".map-wrap").appendChild(chip);

  // Empty-state notices for stub datasets: driven directly off feature
  // counts, never off a phantom map marker.
  function showStubNotice(title, note) {
    document.getElementById("detail").innerHTML = `
      <div><strong>${BSD.esc(title)}</strong><p class="muted">${BSD.esc(note)}</p></div>
    `;
  }
  if (state.overlays.has("connectors") && (mellowConnectorsData.features || []).length === 0 && (osmTrailsData.features || []).length === 0 && localFeatures.length === 0) {
    showStubNotice("Connectors", "No connector data yet — this tier fills in as bike_routes, mellow_connectors, and OpenStreetMap trail data come online. We never draw fabricated geometry.");
  }
  if (state.overlays.has("planned") && plannedData.features.length === 0) {
    showStubNotice("Planned bikeways", plannedData.properties?.note || "CDOT publishes planned bikeways only as PDF maps — no structured feed yet.");
  }

  /* ---------------- toggle handlers ---------------- */

  TIER_ROWS.forEach((t) => {
    document.getElementById(`${t.id}-toggle`).addEventListener("change", (e) => {
      if (e.target.checked) state.overlays.add(t.id); else state.overlays.delete(t.id);
      if (t.id === "trails") { setLayerVisible(layers.trailsOutline, e.target.checked); setLayerVisible(layers.trails, e.target.checked); setLayerVisible(layers.lineLabelsTrails, e.target.checked); updateDeclutter(); }
      if (t.id === "main") { setLayerVisible(layers.casing, e.target.checked); setLayerVisible(layers.lines, e.target.checked); setLayerVisible(layers.capsules, e.target.checked); updateDeclutter(); }
      if (t.id === "connectors") {
        setLayerVisible(layers.connectors, e.target.checked);
        document.getElementById("connector-tint-note").style.display = e.target.checked ? "" : "none";
        updateDeclutter();
      }
      syncURL();
    });
  });

  document.getElementById("nodes-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("nodes"); else state.overlays.delete("nodes");
    updateDeclutter();
    syncURL();
  });

  document.getElementById("planned-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("planned"); else state.overlays.delete("planned");
    if (e.target.checked) {
      layers.planned.addTo(map);
      layers.plannedCasing.addTo(map);
      if (plannedData.features.length === 0) showStubNotice("Planned bikeways", plannedData.properties?.note || "CDOT publishes planned bikeways only as PDF maps — no structured feed yet.");
    } else {
      map.removeLayer(layers.planned);
      map.removeLayer(layers.plannedCasing);
      if (plannedData.features.length === 0) document.getElementById("detail").innerHTML = "";
    }
    syncURL();
  });

  document.querySelectorAll(".segmented-opt").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.floor = btn.dataset.floor;
      document.querySelectorAll(".segmented-opt").forEach((b) => b.classList.toggle("active", b === btn));
      applyFloor();
      updateDeclutter(); // corridor labels' visibility depends on state.floor too
      syncURL();
    });
  });

  document.querySelectorAll(".roster-row").forEach((row) => {
    row.addEventListener("click", () => {
      const lineId = row.dataset.line;
      if (isLineSelected(lineId) && selectedLineIds.size === 1) deselect();
      else selectLine(lineId, { fitBounds: true });
    });
  });

  /* ---------------- non-selection detail (connectors/planned/nodes) ---------------- */

  function showSegmentDetail(feature) {
    const detail = document.getElementById("detail");
    const props = feature.properties;

    if (feature._planned) {
      detail.innerHTML = `
        <div>
          <strong>${BSD.esc(props.street || "(unnamed)")}</strong>
          <dl>
            <dt>Facility type</dt>
            <dd>${BSD.esc(BSD.FACILITY_LABELS[props.facility_category] || props.facility_type_raw || "—")} ${BSD.badgeHTML(plannedBadgeTier)}</dd>
          </dl>
          <div class="notice">Planned — not yet built</div>
        </div>
      `;
      return;
    }

    if (feature._trail) {
      detail.innerHTML = `
        <div>
          <strong>${BSD.esc(props.name || "Off-street trail")}</strong> ${BSD.badgeHTML("crowdsourced")}
          <dl>
            <dt>Type</dt><dd>${BSD.esc(BSD.FACILITY_LABELS.trail)}</dd>
            <dt>Length</dt><dd>${BSD.fmt(Math.round(props.length_m))} m</dd>
          </dl>
          <p class="muted">Trail geometry from OpenStreetMap — crowdsourced, coverage varies. Part of the connector tier.</p>
        </div>
      `;
      return;
    }

    if (feature._mellowConnector) {
      detail.innerHTML = `
        <div>
          <strong>Mellow connector</strong> ${BSD.badgeHTML(props.data_tier || "crowdsourced")}
          <dl>
            <dt>Length</dt><dd>${BSD.fmt(Math.round(props.length_m || 0))} m</dd>
          </dl>
          <p class="muted">Mellow/low-stress geometry that doesn't overlap the curated bikeway roster — a short rideable link, not its own route — grade reflects facility type, not a safety metric.</p>
        </div>
      `;
      return;
    }

    const streetLabel = props.street || "(unnamed)";
    const connectorLabel = connectorGradeLabel(feature._connectorGrade);
    clearSelectionVisuals();
    state.corridor = streetLabel;
    state.line = "";
    const corridorFeats = corridorGroups.get(streetLabel) || [feature];
    const corridorLength = corridorFeats.reduce((sum, f) => sum + (f.properties.length_m || 0), 0);
    const corridor = encodeURIComponent(props.street);
    const link = `map.html?layers=crashes,infrastructure&corridor=${corridor}`;

    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(streetLabel)}</strong> ${BSD.badgeHTML("real")}
        <dl>
          <dt>Facility type</dt>
          <dd>${BSD.esc(BSD.FACILITY_LABELS[props.facility_category] || props.facility_type_raw)}</dd>

          <dt>Segment length</dt>
          <dd>${BSD.fmt(Math.round(props.length_m))} m</dd>

          <dt>Corridor total length</dt>
          <dd>${BSD.fmt(Math.round(corridorLength))} m across ${corridorFeats.length} segment${corridorFeats.length === 1 ? "" : "s"}</dd>

          <dt></dt>
          <dd><a href="${link}">Crash & infrastructure data →</a></dd>
        </dl>
        <p class="muted">${BSD.esc(connectorLabel)} — a short rideable link, not part of the curated route roster — grade reflects facility type, not a safety metric.</p>
      </div>
    `;
    syncURL();
  }

  function showNodeDetail(n) {
    if (selectedLineIds) {
      clearSelectionVisuals();
      state.line = "";
      syncURL();
    }
    const detail = document.getElementById("detail");
    const lineNames = (n.lines || []).map((id) => (linesMeta.get(id) || {}).name || id).join(" × ");
    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(n.label)}</strong> ${BSD.badgeHTML(n.data_tier || "derived")}
        ${lineNames ? `<p class="muted">${BSD.esc(lineNames)}</p>` : ""}
        <p><a href="#" id="node-center">Center map here →</a></p>
      </div>
    `;
    document.getElementById("node-center").addEventListener("click", (e) => {
      e.preventDefault();
      map.setView([n.lat, n.lng], 15);
    });
  }

  /* ---------------- deep links: ?corridor=, ?line=, ?floor= ---------------- */

  applyFloor(); // apply floor state before any deep-link fit/select

  if (state.corridor) {
    const corridorFeats = corridorGroups.get(state.corridor);
    if (corridorFeats && corridorFeats.length > 0) {
      const longest = corridorFeats.reduce((best, f) =>
        (f.properties.length_m || 0) > (best.properties.length_m || 0) ? f : best
      );
      const entry = rosterIndex.get(String(longest.properties.segment_id));
      if (entry) {
        selectLine(entry.lineId, { fitBounds: false });
      } else {
        const grade = BSDNet.CONNECTOR_GRADE_MAP[longest.properties.facility_category] || "none";
        showSegmentDetail({ ...longest, _connectorGrade: grade });
      }
      map.fitBounds(BSDNet.unionBBox(corridorFeats), { padding: [50, 50], animate: false });
    }
  } else if (state.line) {
    const lineMeta = linesMeta.get(state.line);
    if (lineMeta && !lineMeta.no_data) {
      selectLine(state.line, { fitBounds: true });
    } else if (lineMeta && lineMeta.no_data) {
      selectedLineIds = new Set([state.line]);
      updateDetailCard();
      highlightRosterRow(state.line);
    } else {
      // Legacy/dead line id: silently ignore, but drop it from the URL.
      state.line = "";
      syncURL();
    }
  }
})();
