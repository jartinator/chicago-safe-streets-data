(async function () {
  BSD.initPage("network.html");

  // Paper canvas, not a basemap: this screen renders real geometry
  // metro-style (thick casing + line, node markers, corridor labels)
  // rather than a distorted schematic (DECISIONS.md #10).
  document.getElementById("map").style.background = "#f7f9fb";

  const map = L.map("map", {
    attributionControl: false,
    zoom: 11,
    center: [41.8781, -87.6298],
  });

  // Node/label visibility thresholds live in network-model.js as BSDNet.ZOOM:
  // interchanges read at city scale, orientation points only once you're
  // zoomed to street level. Corridor labels for the connector tier share
  // the orientation threshold.

  // Explicit panes (not DOM insertion order) so z-order is stable no matter
  // which toggles are on at load vs. flipped later. Bottom -> top per spec
  // v2 §1/§3/§7: wards backdrop -> connectors -> trail outline -> trail
  // core -> selection halo -> quality border -> main-route casing -> main
  // strands -> planned casing -> planned lines -> capsule transfer markers
  // -> nodes. Labels use Leaflet's own tooltipPane, already above every
  // overlay pane.
  //
  // IMPORTANT (click-bug fix, spec §7): every pane here holds only
  // *interactive* Leaflet objects that are meant to intercept clicks.
  // network.js never drops an invisible/zero-opacity marker onto the map to
  // "keep a layer non-empty" — that pattern (removed from this file; see
  // the git history of the pre-v2 network.js) silently ate clicks anywhere
  // near the map's initial center, because Leaflet markers default to
  // `interactive: true` and CSS opacity:0 does not disable pointer events.
  // Stub/no-data notices are driven by plain feature-count checks instead.
  const PANE_ORDER = [
    "wardsPane", "connectorsPane", "trailsOutlinePane", "trailsPane", "haloPane",
    "qualityPane", "casingPane", "linesPane",
    "plannedCasingPane", "plannedPane", "capsulesPane", "nodesPane",
  ];
  PANE_ORDER.forEach((name, i) => {
    map.createPane(name);
    map.getPane(name).style.zIndex = 200 + i * 10;
    // Halo/quality/casing panes must never steal clicks meant for the
    // interactive stroke sitting above them — only linesPane/trailsPane/
    // connectorsPane/nodesPane/capsulesPane/plannedPane carry click
    // handlers; the rest are visual-only.
  });
  ["haloPane", "qualityPane", "casingPane", "trailsOutlinePane", "plannedCasingPane"].forEach((name) => {
    map.getPane(name).style.pointerEvents = "none";
  });

  const layers = {
    casing: L.layerGroup(),          // main routes: white casing
    lines: L.layerGroup(),           // main routes: solid line color + interlined strands
    quality: L.layerGroup(),         // quality border, toggle "quality"
    trailsOutline: L.layerGroup(),   // trails: darkened outline
    trails: L.layerGroup(),          // trails: core stroke
    gapsTrails: L.layerGroup(),      // trails: lighter gap-filler strokes
    gapsMain: L.layerGroup(),        // main routes: lighter gap-filler strokes
    connectors: L.layerGroup(),      // connectors tier: non-roster bike_routes + mellow_connectors + non-roster osm_trails
    halo: L.layerGroup(),            // selection halo (spec §7)
    capsules: L.layerGroup(),        // interlining transfer-capsule markers (spec §6)
    nodesInterchange: L.layerGroup(),
    nodesOrientation: L.layerGroup(),
    labels: L.layerGroup(),          // corridor labels for connector-tier streets, z >= 13
    lineLabelsTrails: L.layerGroup(),
    lineLabelsStreets: L.layerGroup(),
    planned: L.layerGroup(),
    plannedCasing: L.layerGroup(),
  };

  // URL state: ?overlays=quality,trails,main,connectors,nodes,planned
  // (legacy ids from the pre-v2 map are simply never checked below, so
  // they're ignored silently) &floor=any|paint|protected &corridor=<street>
  // &line=<roster line id>.
  const state = {
    overlays: BSDNet.parseOverlays(BSD.qs().get("overlays")),
    floor: BSDNet.parseFloor(BSD.qs().get("floor")),
    corridor: BSD.qs().get("corridor") || "",
    line: BSD.qs().get("line") || "",
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
  // pipeline products that may 404 while the concurrent data-regeneration
  // work lands — degrade to an empty layer rather than failing the whole
  // page (same pattern for both, spec v2's data-contract note).
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

  // Roster index: segment_id -> {lineIds, lineId, grade}. A segment
  // normally has one line id; an interlined ("shared track") segment
  // carries 2+ (spec §6).
  const rosterIndex = BSDNet.buildRosterIndex(mainRoutesData.features);
  const linesMeta = BSDNet.linesById(mainRoutesData.lines);
  const { roster: rosterFeatures, local: localFeatures } = BSDNet.splitByRoster(routeFeatures, rosterIndex);
  const rosterTrailFeatures = mainRoutesData.features.filter(
    (f) => (linesMeta.get(f.properties.line_id) || {}).source === "osm_trails"
  );
  const rosterStreetNames = BSDNet.rosterStreets(routeFeatures, rosterIndex);
  const corridorGroups = BSDNet.groupByCorridor(routeFeatures);

  // Ward boundaries: a faint, always-on city anchor beneath the network —
  // context only, not a data layer with its own toggle or tier badge. Not
  // interactive: a click anywhere on a ward should fall through to the map
  // background (deselect), never open a ward detail.
  L.geoJSON(wardsData, {
    pane: "wardsPane", interactive: false,
    style: { color: "#e2e8f0", weight: 1, fill: false },
  }).addTo(map);

  /* ---------------- selection state (spec §7) ---------------- */

  let selectedLineIds = null; // Set<line id> | null

  // All stroke weights scale with zoom (BSDNet.zoomWeightFactor — 0.6 at
  // the citywide fit up to 1 at street zoom) so the metro lines stay slim
  // when zoomed out instead of crowding into a smudge. Every restyle path
  // multiplies its base weights by this; the zoomend handler below updates
  // it and restyles when it changes.
  let weightFactor = BSDNet.zoomWeightFactor(map.getZoom());

  // Per-feature layer records so floor/selection restyles can be applied
  // without rebuilding geometry (spec §5: "restyle existing polylines
  // (setStyle) not rebuilding").
  const mainRouteRecords = []; // { grade, lineIds, casingLayer, casingBaseWeight, borderLayer, strandLayers: [{lineId, layer}] }
  const trailRecords = [];     // { lineId, coreLayer, outlineLayer }
  const gapRecords = [];       // { lineId, layer, baseWeight } — lighter continuity strokes
  const connectorRecords = []; // { layer, grade } — per-feature comfort grade (spec §12)

  function isLineSelected(lineId) {
    return selectedLineIds != null && selectedLineIds.has(lineId);
  }
  function isDimmed(lineIds) {
    return selectedLineIds != null && !lineIds.some((id) => selectedLineIds.has(id));
  }

  function restyleMainRoute(rec) {
    const belowFloor = !BSDNet.meetsFloor(rec.grade, state.floor);
    const dimmed = isDimmed(rec.lineIds);
    const dimOpacity = dimmed ? 0.6 : 1;
    if (belowFloor) {
      rec.casingLayer.setStyle({ opacity: 0 });
      if (rec.borderLayer) rec.borderLayer.setStyle({ opacity: 0 });
      rec.strandLayers.forEach((s) => {
        s.layer.setStyle({
          ...BSDNet.DRAINED_STYLE,
          weight: BSDNet.DRAINED_STYLE.weight * weightFactor,
          dashArray: null, opacity: dimOpacity,
        });
      });
    } else {
      // Interlined braids widen the casing/border by the extra strands'
      // pixel span; single-strand records get plain zoom-scaled weights.
      const extraPx = (rec.strandLayers.length - 1) * strandGapPx();
      rec.casingLayer.setStyle({ opacity: dimOpacity, weight: rec.casingBaseWeight * weightFactor + extraPx });
      const borderStyle = BSDNet.qualityBorderStyle(rec.grade);
      if (rec.borderLayer) {
        rec.borderLayer.setStyle(borderStyle
          ? { ...borderStyle, weight: borderStyle.weight * weightFactor + extraPx, opacity: dimOpacity }
          : { opacity: 0 });
      }
      rec.strandLayers.forEach((s) => {
        const selected = isLineSelected(s.lineId);
        const base = BSDNet.lineStyle(s.lineId);
        s.layer.setStyle({
          ...base,
          weight: base.weight * weightFactor + (selected ? 2 : 0),
          opacity: dimOpacity,
        });
      });
    }
  }

  function restyleTrail(rec) {
    const selected = isLineSelected(rec.lineId);
    const dimmed = isDimmed([rec.lineId]);
    const dimOpacity = dimmed ? 0.6 : 1;
    const base = BSDNet.trailStyle(rec.lineId);
    const outlineBase = BSDNet.trailOutlineStyle(rec.lineId);
    rec.coreLayer.setStyle({
      ...base,
      weight: base.weight * weightFactor + (selected ? 2 : 0),
      opacity: dimOpacity,
    });
    rec.outlineLayer.setStyle({ weight: outlineBase.weight * weightFactor, opacity: dimOpacity });
  }

  // Gap fillers dim with their line and scale with zoom like every other
  // stroke; they carry no selection weight bump (they're continuity hints,
  // not the line itself).
  function restyleGaps() {
    gapRecords.forEach((g) => {
      g.layer.setStyle({
        weight: g.baseWeight * weightFactor,
        opacity: isDimmed([g.lineId]) ? 0.6 : 1,
      });
    });
  }

  function restyleAll() {
    mainRouteRecords.forEach(restyleMainRoute);
    trailRecords.forEach(restyleTrail);
    restyleGaps();
  }

  // Selection halo (spec §7): a soft glow polyline (~16px, 25% opacity of
  // the line color) under casingPane, one per member feature of the
  // selected line(s).
  function updateHalo() {
    layers.halo.clearLayers();
    if (!selectedLineIds) return;
    const seen = new Set();
    selectedLineIds.forEach((lineId) => {
      const isTrail = (linesMeta.get(lineId) || {}).source === "osm_trails";
      const members = isTrail
        ? rosterTrailFeatures.filter((f) => f.properties.line_id === lineId)
        : BSDNet.membersOfLine(rosterFeatures, rosterIndex, lineId);
      const color = BSDNet.LINE_COLORS[lineId] || BSDNet.FALLBACK_LINE_COLOR;
      members.forEach((feature) => {
        const key = feature.properties.segment_id + "|" + lineId;
        if (seen.has(key)) return;
        seen.add(key);
        layers.halo.addLayer(L.polyline(BSDNet.schematicLatLngs(feature.geometry), {
          pane: "haloPane", color, weight: 16 * weightFactor, opacity: 0.25, lineCap: "round", lineJoin: "round",
        }));
      });
    });
  }

  function updateDetailCard() {
    const slot = document.getElementById("detail-card");
    if (!selectedLineIds || selectedLineIds.size === 0) {
      slot.innerHTML = `<p class="muted card-placeholder">appears when you click a route</p>`;
      return;
    }
    slot.innerHTML = [...selectedLineIds].map((id) => detailCardHTML(linesMeta.get(id))).filter(Boolean).join("");
  }

  function detailCardHTML(lineMeta) {
    if (!lineMeta) return "";
    const color = BSDNet.LINE_COLORS[lineMeta.id] || BSDNet.FALLBACK_LINE_COLOR;
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

    const segs = BSDNet.qualityMixSegments(lineMeta.miles_by_grade);
    const mixHTML = segs.length
      ? `
        <div class="muted" style="margin:.4rem 0 .25rem;">Quality mix</div>
        <div class="mix-bar" role="img" aria-label="Facility grade mix along ${BSD.esc(lineMeta.name)}">
          ${segs.map((s) => `<span class="mix-seg grade-${s.grade}" style="width:${s.pct.toFixed(2)}%;background:${s.color}"></span>`).join("")}
        </div>
        <div class="mix-legend">
          ${segs.map((s) => `<span><i style="background:${s.color}"></i>${BSD.esc(GRADE_MIX_LABELS[s.grade])} — ${s.pct.toFixed(0)}%</span>`).join("")}
        </div>
      `
      : `<p class="muted">Off-street the whole way — no quality mix to show.</p>`;

    return `
      <div class="detail-card">
        <div class="detail-card-head"><span class="dot" style="background:${color}"></span><strong>${BSD.esc(lineMeta.name)}</strong> ${BSD.badgeHTML(tier)}</div>
        <div class="muted" style="margin-left:1.1rem;">${BSD.esc(tierLabel)}</div>
        ${mixHTML}
        ${lineMeta.termini ? `<div class="detail-card-termini muted">${BSD.esc(lineMeta.termini)}</div>` : ""}
      </div>
    `;
  }
  const GRADE_MIX_LABELS = { protected: "protected", paint: "paint", mellow: "mellow", none: "none" };

  // Connector detail-card title per comfort grade (spec §12): names the
  // grade the way the quality legend does, with the same facility-type
  // caveat repeated in the card body below. Unknown grade -> the `none`
  // label, matching connectorStyle's fallback.
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

  // Visual half of deselection only — halo, dimming, detail card, roster
  // highlight — with no opinion on state.line/syncURL(). Shared by deselect()
  // and every non-selection detail entry point (showSegmentDetail,
  // showNodeDetail) so clicking a connector/segment/node while a roster line
  // is selected never leaves a stale halo/dim/roster-highlight behind, even
  // though each of those entry points manages its own state.line/syncURL()
  // timing (and must call syncURL() itself, exactly once, to avoid a
  // double-sync).
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

  function fitLineBounds(lineId) {
    const isTrail = (linesMeta.get(lineId) || {}).source === "osm_trails";
    const members = isTrail
      ? rosterTrailFeatures.filter((f) => f.properties.line_id === lineId)
      : BSDNet.membersOfLine(rosterFeatures, rosterIndex, lineId);
    if (members.length === 0) return;
    map.fitBounds(BSDNet.unionBBox(members), { padding: [50, 50], animate: false });
  }

  /* ---------------- draw: main routes (spec §1/§3/§6) ---------------- */

  // Every click handler here calls L.DomEvent.stop(e) first: without it,
  // Leaflet's default `bubblingMouseEvents` propagates the click on to the
  // map's own "click" handler (wired below for deselect-on-empty-click),
  // which would immediately undo the selection this very click just made.
  function drawSimpleMainRoute(feature, entry) {
    const latlngs = BSDNet.schematicLatLngs(feature.geometry);
    const lineId = entry.lineId;

    const borderStyle = BSDNet.qualityBorderStyle(entry.grade);
    const borderLayer = borderStyle
      ? L.polyline(latlngs, { pane: "qualityPane", lineCap: "round", lineJoin: "round", ...borderStyle })
      : null;
    if (borderLayer) layers.quality.addLayer(borderLayer);

    const casingLayer = L.polyline(latlngs, {
      pane: "casingPane", weight: 9, color: "#ffffff", opacity: 1, lineCap: "round", lineJoin: "round",
    });
    layers.casing.addLayer(casingLayer);

    const line = L.polyline(latlngs, {
      pane: "linesPane", lineCap: "round", lineJoin: "round", ...BSDNet.lineStyle(lineId),
    });
    line.feature = feature;
    line.on("click", (e) => { L.DomEvent.stop(e); onLineClick(lineId); });
    layers.lines.addLayer(line);

    mainRouteRecords.push({
      feature, grade: entry.grade, lineIds: entry.lineIds,
      casingLayer, casingBaseWeight: 9, borderLayer, strandLayers: [{ lineId, layer: line }],
    });
  }

  // Capsule transfer marker (spec §6): a small white pill with a dark
  // outline at each end of a shared run, rotated perpendicular to travel
  // direction so it visually "spans" the parallel strands.
  function bearingAt(latlngs, point) {
    const parts = BSDNet.isMultiPart(latlngs) ? latlngs : [latlngs];
    for (const part of parts) {
      if (part.length < 2) continue;
      if (point === part[0]) return Math.atan2(part[1][1] - part[0][1], part[1][0] - part[0][0]);
      if (point === part[part.length - 1]) {
        const p0 = part[part.length - 2], p1 = part[part.length - 1];
        return Math.atan2(p1[1] - p0[1], p1[0] - p0[0]);
      }
    }
    return 0;
  }
  function capsuleIcon(bearingRad, strandCount) {
    const deg = (bearingRad * 180) / Math.PI + 90; // perpendicular to travel
    // The pill spans the whole braid (plus a lip each side), whatever the
    // current zoom's strand spacing is.
    const w = Math.max(16, Math.round(braidWidthPx(strandCount) + 6));
    const topPad = Math.round((w - 8) / 2); // center the 8px-tall pill in the square icon box
    return L.divIcon({
      className: "capsule-marker",
      html: `<span style="transform: rotate(${deg.toFixed(1)}deg); width: ${w}px; margin-top: ${topPad}px"></span>`,
      iconSize: [w, w],
      iconAnchor: [w / 2, w / 2],
    });
  }

  // Interlined strands are spaced a fixed number of PIXELS apart: the
  // meter gap is derived from the current zoom at draw time and re-derived
  // on zoomend (applyStrandOffsets), so shared runs read as parallel
  // colored strands at every zoom instead of collapsing into whichever
  // strand drew last. The pixel gap tracks the zoom-scaled strand width
  // (plus a sliver of casing) so neighbors never cover each other.
  function strandGapPx() {
    return 6 * weightFactor + 1.5;
  }
  function braidWidthPx(strandCount) {
    return (strandCount - 1) * strandGapPx() + 6 * weightFactor;
  }
  function strandGapMeters(latlngs) {
    const refLat = BSDNet.pathEndpoints(latlngs)[0][0];
    return strandGapPx() * BSDNet.metersPerPixel(refLat, map.getZoom());
  }

  function drawInterlinedMainRoute(feature, entry) {
    // Straighten before offsetting so the parallel strands are offset from
    // the same decluttered path (offsetting first would re-wiggle them).
    const latlngs = BSDNet.schematicLatLngs(feature.geometry);
    const plan = BSDNet.planInterlinedRoute(
      latlngs, entry.lineIds, entry.grade,
      (id) => BSDNet.LINE_COLORS[id] || BSDNet.FALLBACK_LINE_COLOR,
      strandGapMeters(latlngs)
    );

    const borderLayer = plan.border
      ? L.polyline(plan.casing.latlngs, { pane: "qualityPane", lineCap: "round", lineJoin: "round", ...plan.border })
      : null;
    if (borderLayer) layers.quality.addLayer(borderLayer);

    // Base casing weight matches the single-strand case; restyleMainRoute
    // adds the extra strands' pixel span on top (strand offsets are
    // pixel-constant, so the braid width is known in px at any zoom).
    const casingBaseWeight = 9;
    const casingLayer = L.polyline(plan.casing.latlngs, {
      pane: "casingPane", weight: casingBaseWeight, color: "#ffffff", opacity: 1,
      lineCap: "round", lineJoin: "round",
    });
    layers.casing.addLayer(casingLayer);

    const strandLayers = plan.strands.map((strand) => {
      const line = L.polyline(strand.latlngs, {
        pane: "linesPane", lineCap: "round", lineJoin: "round", ...BSDNet.lineStyle(strand.lineId),
      });
      line.feature = feature;
      line.on("click", (e) => { L.DomEvent.stop(e); onLineClick(strand.lineId); });
      layers.lines.addLayer(line);
      return { lineId: strand.lineId, layer: line };
    });

    // Capsule markers are deduped after ALL interlined features are drawn:
    // a shared run is usually several roster segments, and a capsule at
    // every interior joint reads as noise — only the run's true ends
    // should carry one. Collect candidates here; drawCapsules() below
    // drops any point where two segments of the same line set meet.
    plan.capsules.forEach((pt) => {
      capsuleCandidates.push({
        pt,
        bearing: bearingAt(latlngs, pt),
        setKey: entry.lineIds.slice().sort().join("|"),
        count: plan.strands.length,
      });
    });

    mainRouteRecords.push({
      feature, grade: entry.grade, lineIds: entry.lineIds,
      casingLayer, casingBaseWeight, borderLayer, strandLayers,
      interlinedLatLngs: latlngs, // base (un-offset) path for re-offsetting on zoom
    });
  }

  // Re-derive interlined strand offsets for the current zoom (pixel-constant
  // spacing). Only multi-strand records carry interlinedLatLngs. Capsules
  // re-size with the braid.
  function applyStrandOffsets() {
    mainRouteRecords.forEach((rec) => {
      if (!rec.interlinedLatLngs || rec.strandLayers.length < 2) return;
      const offsets = BSDNet.strandOffsets(rec.strandLayers.length, strandGapMeters(rec.interlinedLatLngs));
      rec.strandLayers.forEach((s, i) => {
        s.layer.setLatLngs(BSDNet.offsetLatLngs(rec.interlinedLatLngs, offsets[i]));
      });
    });
    capsuleRecords.forEach((c) => c.marker.setIcon(capsuleIcon(c.bearing, c.count)));
  }

  function onLineClick(lineId) {
    if (selectedLineIds && selectedLineIds.size === 1 && selectedLineIds.has(lineId)) {
      deselect();
    } else {
      selectLine(lineId, { fitBounds: false });
    }
  }

  const capsuleCandidates = []; // { pt, bearing, setKey, count }
  const capsuleRecords = [];    // { marker, bearing, count } — for zoom re-sizing

  rosterFeatures.forEach((feature) => {
    const entry = rosterIndex.get(String(feature.properties.segment_id));
    if (!entry) return;
    if (entry.lineIds.length >= 2) drawInterlinedMainRoute(feature, entry);
    else drawSimpleMainRoute(feature, entry);
  });

  // Dedupe capsules to the shared runs' true ends: quantize each candidate
  // to a ~60 m cell (per line set) — interior joints land two candidates in
  // one cell (this segment's end + the next one's start) and are dropped.
  (function drawCapsules() {
    const cells = new Map();
    capsuleCandidates.forEach((c) => {
      const mLng = 111320 * Math.cos((c.pt[0] * Math.PI) / 180);
      const cell = c.setKey + ":" + Math.round((c.pt[0] * 111320) / 60) + ":" + Math.round((c.pt[1] * mLng) / 60);
      if (!cells.has(cell)) cells.set(cell, []);
      cells.get(cell).push(c);
    });
    cells.forEach((cands) => {
      if (cands.length !== 1) return; // interior joint of a longer shared run
      const c = cands[0];
      const marker = L.marker(c.pt, {
        pane: "capsulesPane", icon: capsuleIcon(c.bearing, c.count), interactive: false,
      });
      layers.capsules.addLayer(marker);
      capsuleRecords.push({ marker, bearing: c.bearing, count: c.count });
    });
  })();

  /* ---------------- draw: trails (spec §1) ---------------- */

  rosterTrailFeatures.forEach((feature) => {
    const lineId = feature.properties.line_id;
    const latlngs = BSDNet.schematicLatLngs(feature.geometry);

    const outlineLayer = L.polyline(latlngs, {
      pane: "trailsOutlinePane", lineCap: "round", lineJoin: "round", ...BSDNet.trailOutlineStyle(lineId),
    });
    layers.trailsOutline.addLayer(outlineLayer);

    const coreLayer = L.polyline(latlngs, {
      pane: "trailsPane", lineCap: "round", lineJoin: "round", ...BSDNet.trailStyle(lineId),
    });
    coreLayer.feature = feature;
    coreLayer.on("click", (e) => { L.DomEvent.stop(e); onLineClick(lineId); });
    layers.trails.addLayer(coreLayer);

    trailRecords.push({ lineId, coreLayer, outlineLayer });
  });

  /* ---------------- draw: connectors (spec §1, amended §12) ---------------- */
  // One tier, three sources: non-roster bike_routes (the old
  // "connecting/local" background network, ~1000 small features — SVG is
  // fine), deduped mellow geometry (mellow_connectors.geojson — may 404,
  // degrades to []), and non-roster named OSM trails. Each feature now also
  // carries a per-feature comfort grade (spec §12) — mellow/offstreet are
  // forced by source, everything else derives from facility_category via
  // BSDNet.CONNECTOR_GRADE_MAP — styled with BSDNet.connectorStyle(grade):
  // still one subtle, identity-less background mesh, just tinted. All click
  // through to the plain (non-selection) segment detail card — connectors
  // carry no line identity to select.
  //
  // mellow_connectors.geojson ships as a HANDFUL of features, each one huge
  // citywide MultiLineString (same shape the old mellow_routes.geojson
  // background layer used) — not the thousands of small parts bike_routes
  // has. SVG gives every part of a MultiLineString its own DOM path command
  // and chokes on that; canvas draws directly, no per-part DOM cost. Same
  // reasoning the old mellow layer used (see the v1 network.js history) —
  // this is that pattern, scoped to just this one source.
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

  /* ---------------- draw: gap fillers (metro-map continuity) ---------------- */
  // A roster line's member segments don't always touch — the source data
  // has real holes, so a line can render as dashes of itself. Bridge every
  // hole with a stroke in a lighter shade of the line color: reads as one
  // connected metro line, while the paler shade keeps it honest as
  // inferred continuity rather than surveyed geometry. Non-interactive,
  // and mounted to the map *before* the real strokes in the same pane so
  // it always sits underneath them.
  //
  // Two refinements over a naive whole-line chain:
  // - gaps chain PER SOURCE STREET, then streets connect with at most one
  //   feeder per pair (BSDNet.crossStreetGaps) — so a couplet line like
  //   Jackson–Washington reads as two clean parallels, not a zigzag;
  // - each bridge prefers routing over the connector mesh (mellowest
  //   grade first, detour-capped) and only falls back to a straight
  //   stroke when nothing rideable is nearby.

  const GAP_LIGHTEN = 0.55;
  const GAP_BASE_WEIGHT = 6; // matches the core stroke weight of both tiers

  // Router edges over the whole connector tier (drawn or not — the data is
  // loaded regardless of the connectors toggle).
  const routerEdges = [];
  localFeatures.forEach((f) => {
    const grade = BSDNet.CONNECTOR_GRADE_MAP[f.properties.facility_category] || "none";
    routerEdges.push(...BSDNet.connectorEdges(BSDNet.schematicLatLngs(f.geometry), grade));
  });
  (mellowConnectorsData.features || []).forEach((f) => {
    routerEdges.push(...BSDNet.connectorEdges(BSDNet.schematicLatLngs(f.geometry), "mellow"));
  });
  nonRosterTrailFeatures.forEach((f) => {
    routerEdges.push(...BSDNet.connectorEdges(BSDNet.schematicLatLngs(f.geometry), "offstreet"));
  });

  function drawLineGaps(lineId, features, pane, group) {
    const byStreet = new Map();
    features.forEach((f) => {
      const street = f.properties.street || "";
      const ll = BSDNet.schematicLatLngs(f.geometry);
      if (!byStreet.has(street)) byStreet.set(street, []);
      byStreet.get(street).push(...(BSDNet.isMultiPart(ll) ? ll : [ll]));
    });
    const gaps = [];
    byStreet.forEach((parts) => gaps.push(...BSDNet.chainPlan(parts).gaps));
    gaps.push(...BSDNet.crossStreetGaps([...byStreet.values()]));

    const color = BSDNet.lightenColor(
      BSDNet.LINE_COLORS[lineId] || BSDNet.FALLBACK_LINE_COLOR, GAP_LIGHTEN);
    gaps.forEach(([a, b]) => {
      const path = BSDNet.routeGapThroughConnectors(a, b, routerEdges) || [a, b];
      const layer = L.polyline(path, {
        pane, interactive: false, lineCap: "round", lineJoin: "round",
        color, weight: GAP_BASE_WEIGHT, opacity: 1,
      });
      group.addLayer(layer);
      gapRecords.push({ lineId, layer, baseWeight: GAP_BASE_WEIGHT });
    });
  }

  (mainRoutesData.lines || []).forEach((lineMeta) => {
    const isTrail = lineMeta.source === "osm_trails";
    const members = isTrail
      ? rosterTrailFeatures.filter((f) => f.properties.line_id === lineMeta.id)
      : BSDNet.membersOfLine(rosterFeatures, rosterIndex, lineMeta.id);
    if (members.length === 0) return; // no_data lines: nothing to bridge, never fabricate
    if (isTrail) drawLineGaps(lineMeta.id, members, "trailsPane", layers.gapsTrails);
    else drawLineGaps(lineMeta.id, members, "linesPane", layers.gapsMain);
  });

  /* ---------------- labels ---------------- */

  function labelAnchor(feats) {
    const longest = feats.reduce((best, f) =>
      (f.properties.length_m || 0) > (best.properties.length_m || 0) ? f : best
    );
    const coords = BSDNet.flattenCoords(longest.geometry);
    const mid = coords[Math.floor(coords.length / 2)];
    return [mid[1], mid[0]];
  }
  (mainRoutesData.lines || []).forEach((lineMeta) => {
    const members = lineMeta.source === "osm_trails"
      ? rosterTrailFeatures.filter((f) => f.properties.line_id === lineMeta.id)
      : BSDNet.membersOfLine(rosterFeatures, rosterIndex, lineMeta.id);
    if (members.length === 0) return; // no_data trail lines: nothing to label, never fabricate
    const color = BSDNet.LINE_COLORS[lineMeta.id] || BSDNet.FALLBACK_LINE_COLOR;
    const tooltip = L.tooltip({ permanent: true, direction: "center", className: "line-label" })
      .setLatLng(labelAnchor(members))
      .setContent(`<span style="color:${color}">${BSD.esc(lineMeta.name)}</span>`);
    if (lineMeta.source === "osm_trails") layers.lineLabelsTrails.addLayer(tooltip);
    else layers.lineLabelsStreets.addLayer(tooltip);
  });

  corridorGroups.forEach((feats, street) => {
    if (rosterStreetNames.has(street)) return;
    const tooltip = L.tooltip({ permanent: true, direction: "center", className: "line-label" })
      .setLatLng(labelAnchor(feats))
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

  /* ---------------- nodes (unchanged from v1) ---------------- */

  const NODE_MARKER_STYLE = {
    interchange: { radius: 5, color: "#1a2330", weight: 2.5 },
    orientation: { radius: 3.5, color: "#64748b", weight: 2 },
  };
  function makeNodeMarker(n) {
    const style = NODE_MARKER_STYLE[n.kind];
    const marker = L.circleMarker([n.lat, n.lng], {
      pane: "nodesPane", radius: style.radius, color: style.color, weight: style.weight,
      fillColor: "#ffffff", fillOpacity: 1,
    });
    const tooltipOpts = n.kind === "orientation"
      ? { permanent: true, direction: "top", className: "node-label", offset: [0, -6] }
      : { direction: "top", offset: [0, -8] };
    marker.bindTooltip(BSD.esc(n.label), tooltipOpts);
    marker.on("click", (e) => { L.DomEvent.stop(e); showNodeDetail(n); });
    return marker;
  }
  (nodesData.nodes || []).forEach((n) => {
    if (n.kind === "interchange") layers.nodesInterchange.addLayer(makeNodeMarker(n));
    else if (n.kind === "orientation") layers.nodesOrientation.addLayer(makeNodeMarker(n));
  });

  /* ---------------- mount layers per state.overlays ---------------- */

  // Selection halo (spec §7) has no tier toggle of its own — it's driven
  // purely by selectedLineIds (updateHalo()/clearSelectionVisuals()), which
  // a roster-row click can set regardless of the main/trails tier toggles.
  // Always mounted; addLayer()/clearLayers() populate it, never map.hasLayer.
  layers.halo.addTo(map);

  // Gated on state.overlays so a ?overlays= that excludes "main"/"trails"
  // actually hides these — and so the checkboxes below (rendered from the
  // same state.overlays) agree with what's on the map at load.
  // Within a tier, gap fillers mount before the core strokes: same pane,
  // earlier in the SVG, so the lighter bridges render underneath.
  if (state.overlays.has("main")) { layers.casing.addTo(map); layers.gapsMain.addTo(map); layers.lines.addTo(map); layers.capsules.addTo(map); }
  // lineLabelsStreets mounts via updateDeclutter() once zoomed past BSDNet.ZOOM.lineLabels.
  if (state.overlays.has("quality")) layers.quality.addTo(map);
  if (state.overlays.has("trails")) { layers.trailsOutline.addTo(map); layers.gapsTrails.addTo(map); layers.trails.addTo(map); layers.lineLabelsTrails.addTo(map); }
  // Connector tier mounts by its own toggle only (spec §12 amendment) — the
  // comfort floor no longer hides the whole tier, it filters membership per
  // record instead (applyConnectorFloor, below), applied via applyFloor()
  // before any deep link/paint happens.
  if (state.overlays.has("connectors")) layers.connectors.addTo(map);
  if (state.overlays.has("planned")) { layers.planned.addTo(map); layers.plannedCasing.addTo(map); }

  function setLayerVisible(layer, visible) {
    if (visible) {
      if (!map.hasLayer(layer)) layer.addTo(map);
    } else if (map.hasLayer(layer)) {
      map.removeLayer(layer);
    }
  }

  // Per-record connector floor membership (spec §12 amendment): each
  // connector hides when its grade is below the current floor and stays
  // visible at/above it (BSDNet.meetsFloor) — floors now *reveal* the
  // qualifying background network instead of nuking the whole tier.
  // eachLayer() is deliberately NOT used here (see restyleStaticWeights
  // below) because a floor-removed layer isn't in the group to iterate.
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

  // Comfort floor (spec §5, amended §12): each connector now carries a
  // comfort grade of its own, so a floor no longer hides the whole
  // connectors tier — it filters membership per record instead
  // (applyConnectorFloor, above): below-floor connectors drop out of
  // layers.connectors, at/above-floor ones stay in. The tier's own mount/
  // unmount is toggle-only (setLayerVisible). Main-route stretches below
  // the floor still drain in place via restyleMainRoute (setStyle, not
  // rebuild) — only mainRouteRecords need restyling here; trails are
  // floor-immune (comfort floor only judges on-street facility grade) so
  // restyleAll()'s trail pass would be wasted work. restyleAll() is still
  // used for selection changes, which DO affect trail dimming/highlighting.
  function applyFloor() {
    setLayerVisible(layers.connectors, state.overlays.has("connectors"));
    applyConnectorFloor();
    mainRouteRecords.forEach(restyleMainRoute);
  }

  // Connectors restyle per-record — eachLayer() would miss any layer a
  // floor has removed from the group, leaving it mis-scaled for the next
  // zoom once it's revealed again (spec §12). Planned routes have no
  // per-feature records, so their fixed base weights scale directly.
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
    // Strand spacing is pixel-constant, so it changes on EVERY zoom step,
    // not just when the weight factor bucket does.
    applyStrandOffsets();
  }

  function updateDeclutter() {
    const z = map.getZoom();
    setLayerVisible(layers.lineLabelsStreets, z >= BSDNet.ZOOM.lineLabels);
    setLayerVisible(layers.nodesInterchange, state.overlays.has("nodes") && z >= BSDNet.ZOOM.interchangeNodes);
    setLayerVisible(layers.nodesOrientation, state.overlays.has("nodes") && z >= BSDNet.ZOOM.corridorLabels);
    // Corridor labels are for connector-tier streets specifically. Unlike
    // the connectors layer itself — which now filters per-feature via
    // meetsFloor instead of hiding outright (spec §12 amendment) — labels
    // deliberately KEEP the coarser floor === "any" gate: once a floor
    // thins the background mesh it's meant to read sparse (spec §12), and
    // a floored, partly-labeled background isn't worth the complexity of
    // per-grade label placement. On top of their own zoom threshold.
    setLayerVisible(layers.labels, state.overlays.has("connectors") && state.floor === "any" && z >= BSDNet.ZOOM.corridorLabels);
  }
  map.on("zoomend", () => {
    applyZoomWeights();
    updateDeclutter();
  });

  // Fit bounds to bike network
  if (routeFeatures.length > 0) {
    const allBounds = BSDNet.unionBBox(routeFeatures);
    // animate: false — this citywide fit must apply synchronously so a
    // ?corridor=/?line= restore further down can override it. Animated,
    // its zoom animation lands a frame later and silently undoes the
    // deep link's own fitBounds.
    map.fitBounds(allBounds, { padding: [50, 50], animate: false });
  }
  updateDeclutter();
  // Layers are drawn with unscaled base weights; apply the current zoom's
  // weight factor and strand spacing once now (the zoomend path only
  // restyles on *changes*).
  weightFactor = BSDNet.zoomWeightFactor(map.getZoom());
  restyleAll();
  restyleStaticWeights();
  applyStrandOffsets();

  /* ---------------- deselect triggers (spec §7, click-bug fix) ---------------- */
  // Every feature click handler above calls L.DomEvent.stop(e), so this
  // only fires for genuine background clicks (empty map / wards).
  map.on("click", deselect);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") deselect();
  });

  /* ---------------- side panel (spec §8) ---------------- */

  const plannedBadgeTier = plannedData.properties?.status === "no_data_yet"
    ? "stub"
    : (plannedData.features[0]?.properties?.data_tier || "real");

  // tiers: data_tier(s) backing this row (spec/CONTRIBUTING.md — "all tier
  // labeling must go through BSD.badgeHTML()"). Trails are crowdsourced OSM
  // data; main routes are derived from CDOT source data; connectors blend
  // real CDOT streets (the demoted local network) with crowdsourced sources
  // (mellow_connectors + non-roster OSM trails), so that row carries both.
  const TIER_ROWS = [
    { id: "trails", name: "Trails", desc: "off-street paths", swatchClass: "swatch-trail", tiers: ["crowdsourced"] },
    { id: "main", name: "Main routes", desc: "major on-street routes", swatchClass: "swatch-main", tiers: ["derived"] },
    { id: "connectors", name: "Connectors", desc: "short rideable links between routes", swatchClass: "swatch-connector", tiers: ["real", "crowdsourced"] },
  ];
  // Single badge inline (fits next to the swatch+text with room to spare —
  // .tier-label carries flex:1 1 0; min-width:0 in style.css, so it absorbs
  // the squeeze). Two badges (connectors) are too wide to sit inline next to
  // a swatch *and* a full description in the 320px side panel without
  // crushing the label text down to a couple of characters per line, so that
  // pair gets flex: 1 0 100% instead of the single-badge's inline flex:none
  // — same "wrap the pair in its own span" idea as the pre-v2 connecting-
  // infrastructure row's dual badge (see this file's git history), adapted
  // with a full-width flex-basis so the pair drops to its own line below the
  // label rather than squeezing it.
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

  const QUALITY_LEGEND = [
    ["protected", "protected", false],
    ["paint", "paint", true],
    ["mellow", "mellow", false],
    ["none", "none — ride with traffic", true],
  ];
  function gradeLegendHTML() {
    return QUALITY_LEGEND.map(([grade, label, dashed]) => {
      const bar = dashed
        ? `border-top: 3px dashed ${BSDNet.GRADE_COLORS[grade]};`
        : `background: ${BSDNet.GRADE_COLORS[grade]}; height: 3px;`;
      return `
        <div class="quality-legend-row">
          <div class="quality-swatch" style="${bar}"></div>
          <span>${BSD.esc(label)}</span>
        </div>
      `;
    }).join("") + `
      <div class="quality-legend-row">
        <span class="capsule-glyph" aria-hidden="true"></span>
        <span>transfer — routes meet or share track</span>
      </div>
      <p class="muted quality-footnote">trails are off-street — no border needed</p>
      <p class="muted quality-footnote">connector tints share these colors — grades reflect facility type, not a safety metric</p>
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
      <p class="muted caption">the network that meets your bar stays lit — routes never break</p>
      <p class="muted caption">floors hide connectors below your bar — greenway links need Any</p>
    `;
  }

  function rosterRowHTML(lineMeta) {
    const color = BSDNet.LINE_COLORS[lineMeta.id] || BSDNet.FALLBACK_LINE_COLOR;
    const segs = BSDNet.qualityMixSegments(lineMeta.miles_by_grade);
    const bar = segs.length
      ? segs.map((s) => `<span style="width:${s.pct.toFixed(2)}%;background:${s.color}"></span>`).join("")
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
  // One badge per GROUP header rather than per roster row: tier is uniform
  // within each group (every trail line is crowdsourced, every street line
  // is derived — see LINE_COLORS/data_tier in main_routes.geojson), so a
  // 21-row roster carrying 21 identical per-row badges would be noise; the
  // group-level badge satisfies the visible-badge rule just as well.
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

      <hr class="panel-divider">

      <div class="filter-row">
        <input type="checkbox" id="quality-toggle" ${state.overlays.has("quality") ? "checked" : ""}>
        <label for="quality-toggle">Quality border ${BSD.badgeHTML("derived")}</label>
      </div>
      <div id="quality-legend" class="quality-legend" style="display:${state.overlays.has("quality") ? "" : "none"};">
        ${gradeLegendHTML()}
      </div>
      <p class="muted caption">filter by tier · set your comfort floor</p>

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

  // Empty-state notices for stub datasets: driven directly off feature
  // counts, never off a phantom map marker (the click-bug fix above).
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
      if (t.id === "trails") { setLayerVisible(layers.trailsOutline, e.target.checked); setLayerVisible(layers.gapsTrails, e.target.checked); setLayerVisible(layers.trails, e.target.checked); setLayerVisible(layers.lineLabelsTrails, e.target.checked); }
      if (t.id === "main") { setLayerVisible(layers.casing, e.target.checked); setLayerVisible(layers.gapsMain, e.target.checked); setLayerVisible(layers.lines, e.target.checked); setLayerVisible(layers.capsules, e.target.checked); }
      if (t.id === "connectors") { setLayerVisible(layers.connectors, e.target.checked); updateDeclutter(); }
      syncURL();
    });
  });

  document.getElementById("quality-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("quality"); else state.overlays.delete("quality");
    setLayerVisible(layers.quality, e.target.checked);
    document.getElementById("quality-legend").style.display = e.target.checked ? "" : "none";
    syncURL();
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
      updateDeclutter(); // corridor labels' visibility depends on state.floor too (see updateDeclutter)
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
    // A connector/segment click clears the current roster-line selection
    // (it belongs to none) — reset halo/dim/roster-highlight first so they
    // never disagree with state.line/the URL this function is about to sync.
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
    // Same selection-desync fix as showSegmentDetail: a node click also
    // moves focus away from any selected roster line, so clear its
    // halo/dim/roster-highlight and state.line/URL together rather than
    // leaving the old line's halo lit under the node detail.
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
        // Not a roster member -> a connector segment; carry the same
        // per-feature comfort grade drawConnector() computes (spec §12) so
        // the detail card names it correctly even reached via deep link.
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
      // Legacy/dead line id (e.g. roosevelt/vincennes, demoted off the
      // roster to connectors — spec §2): linesMeta has no entry, so there's
      // nothing to select or show. Silently ignore it (no error notice —
      // same UX as an unrecognized overlay id), but do drop it from the URL
      // rather than leaving a permanently-dead ?line= sitting there.
      state.line = "";
      syncURL();
    }
  }
})();
