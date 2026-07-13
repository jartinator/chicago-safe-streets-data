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

  // Node visibility thresholds (spec §5): interchanges read at city scale,
  // orientation points only once you're zoomed to street level. Corridor
  // labels for the demoted local network share the orientation threshold.
  const NODE_INTERCHANGE_MIN_ZOOM = 11;
  const LINE_LABEL_MIN_ZOOM = 11; // street-line labels collide at citywide zoom; trails stay labeled
  const LABEL_MIN_ZOOM = 13;

  // Explicit panes (not DOM insertion order) so z-order is stable no matter
  // which toggles are on at load vs. flipped later. Bottom -> top per spec
  // §5: wards backdrop -> local ("bus") background network -> mellow
  // background -> connecting trails -> quality border -> major-route casing
  // -> major-route lines -> planned casing -> planned lines -> nodes.
  // Labels use Leaflet's own tooltipPane, already above every overlay pane.
  const PANE_ORDER = [
    "wardsPane", "localPane", "mellowPane", "connectingTrailsPane", "qualityPane",
    "casingPane", "linesPane", "plannedCasingPane", "plannedPane", "nodesPane",
  ];
  PANE_ORDER.forEach((name, i) => {
    map.createPane(name);
    map.getPane(name).style.zIndex = 200 + i * 10;
  });

  const layers = {
    casing: L.layerGroup(),        // major routes: white casing, always on
    lines: L.layerGroup(),         // major routes: solid line color, always on
    quality: L.layerGroup(),       // quality border: grade-colored casing, toggle "quality"
    local: L.layerGroup(),         // connecting infrastructure: demoted local network
    connectingTrails: L.layerGroup(), // connecting infrastructure: non-roster OSM trails
    mellow: L.layerGroup(),        // mellow routes, toggle "mellow"
    nodesInterchange: L.layerGroup(), // interchange nodes, toggle "nodes" + z >= 11
    nodesOrientation: L.layerGroup(), // orientation nodes, toggle "nodes" + z >= 13
    labels: L.layerGroup(),        // corridor labels for local streets, z >= 13
    lineLabelsTrails: L.layerGroup(),  // trail-line name labels: peripheral, shown at all zooms
    lineLabelsStreets: L.layerGroup(), // street-line name labels: central and collision-prone, z >= LINE_LABEL_MIN_ZOOM
    planned: L.layerGroup(),
    plannedCasing: L.layerGroup(),
  };

  let routeFeatures = [];
  let selectedRoute = null;

  // URL state: ?overlays=quality,connecting,mellow,nodes,planned&corridor=<street>&line=<roster line id>
  // Legacy overlay ids from the pre-distinction map (heat, crashes, stations,
  // trails) are simply never checked below, so they're ignored silently.
  const state = {
    overlays: BSDNet.parseOverlays(BSD.qs().get("overlays")),
    corridor: BSD.qs().get("corridor") || "",
    line: BSD.qs().get("line") || "",
  };
  function syncURL() {
    BSD.setParams({
      overlays: BSDNet.serializeOverlays(state.overlays),
      corridor: state.corridor,
      line: state.line,
    });
  }

  // Load data. network_nodes.json is a new pipeline product (spec §7) that
  // may 404 while the concurrent aggregate.py work lands — degrade to an
  // empty node set rather than failing the whole page.
  async function loadNodesSafe() {
    try {
      return await BSD.loadJSON("data/network_nodes.json");
    } catch (e) {
      return { nodes: [] };
    }
  }

  const [bikeRoutes, mellowData, plannedData, osmTrailsData, mainRoutesData, wardsData, nodesData] = await Promise.all([
    BSD.loadJSON("data/bike_routes.geojson"),
    BSD.loadJSON("data/mellow_routes.geojson"),
    BSD.loadJSON("data/planned_routes.geojson"),
    BSD.loadJSON("data/osm_trails.geojson"),
    BSD.loadJSON("data/main_routes.geojson"),
    BSD.loadJSON("data/wards.geojson"),
    loadNodesSafe(),
  ]);

  routeFeatures = bikeRoutes.features;

  // Group local-network segments into corridors — a pure helper so it stays
  // Node-testable in network-model.js.
  const corridorGroups = BSDNet.groupByCorridor(routeFeatures);

  // Major routes (spec §2/§5): the curated roster gets the heavy metro
  // treatment, one solid color per named line; every other segment demotes
  // to the connecting-infrastructure level.
  const rosterIndex = BSDNet.buildRosterIndex(mainRoutesData.features);
  const linesMeta = BSDNet.linesById(mainRoutesData.lines);
  const { roster: rosterFeatures, local: localFeatures } = BSDNet.splitByRoster(routeFeatures, rosterIndex);
  // Roster trail members live only in main_routes.geojson (their source is
  // osm_trails, not bike_routes). Empty until osm_trails is populated —
  // every trail line carries no_data: true until then — but the render path
  // below is the same one the first live trail pull lights up.
  const rosterTrailFeatures = mainRoutesData.features.filter(
    (f) => (linesMeta.get(f.properties.line_id) || {}).source === "osm_trails"
  );
  const rosterStreetNames = BSDNet.rosterStreets(routeFeatures, rosterIndex);

  // Ward boundaries: a faint, always-on city anchor beneath the network —
  // context only, not a data layer with its own toggle or tier badge.
  L.geoJSON(wardsData, { pane: "wardsPane", style: { color: "#e2e8f0", weight: 1, fill: false } }).addTo(map);

  // Draw one major route member: white casing (always on), solid line-color
  // stroke (always on), and a grade-colored quality-border casing (toggle
  // "quality", off by default) — the layer stack that reads as "solid line
  // color, thin white rim, grade-colored border" per spec §6.
  function drawMajorRoute(feature, lineId, grade, onClick) {
    const latlngs = BSDNet.toLatLngs(feature.geometry);

    const qualityCasing = L.polyline(latlngs, {
      pane: "qualityPane", lineCap: "round", lineJoin: "round",
      ...BSDNet.qualityCasingStyle(grade),
    });
    layers.quality.addLayer(qualityCasing);

    const casing = L.polyline(latlngs, {
      pane: "casingPane", weight: 9, color: "#ffffff", opacity: 1, lineCap: "round", lineJoin: "round",
    });
    layers.casing.addLayer(casing);

    const line = L.polyline(latlngs, {
      pane: "linesPane", lineCap: "round", lineJoin: "round",
      ...BSDNet.lineStyle(lineId),
    });
    line.feature = feature;
    line.on("click", onClick);
    layers.lines.addLayer(line);
  }

  rosterFeatures.forEach((feature) => {
    const entry = rosterIndex.get(String(feature.properties.segment_id));
    drawMajorRoute(feature, entry.lineId, entry.grade, () => showDetail(feature));
  });

  // Roster OSM trails get the identical major-route treatment. Their stats
  // stay crowdsourced-tier — the detail panel says so. The pipeline
  // (pipeline/aggregate.py) always stamps trail members' grade as
  // "offstreet"; the `|| "offstreet"` fallback here is purely defensive.
  rosterTrailFeatures.forEach((feature) => {
    drawMajorRoute(
      feature, feature.properties.line_id, feature.properties.grade || "offstreet",
      () => showRosterTrailDetail(feature)
    );
  });

  // Connecting infrastructure (toggle "connecting", default on): the local
  // ("bus") background network — everything not on the roster — plus
  // non-roster named OSM trails. Real toggle; the old disabled local-toggle
  // checkbox becomes this live one.
  localFeatures.forEach((feature) => {
    const line = L.polyline(BSDNet.toLatLngs(feature.geometry), {
      pane: "localPane", lineCap: "round", lineJoin: "round", ...BSDNet.LOCAL_STYLE,
    });
    line.on("click", () => showDetail(feature));
    line.feature = feature;
    layers.local.addLayer(line);
  });

  if ((osmTrailsData.features || []).length === 0) {
    // Mirror the mellow-layer stub pattern: no trail data yet, so drop an
    // invisible marker in the layer (keeps it non-empty for Leaflet) and let
    // the toggle handler / detail panel show the same no_data_yet notice.
    const noDataMarker = L.marker([41.8781, -87.6298], { opacity: 0 });
    noDataMarker._trailsStub = true;
    layers.connectingTrails.addLayer(noDataMarker);
  } else {
    osmTrailsData.features.forEach((feature) => {
      // Roster trails are already drawn heavy as major routes above — don't
      // double-draw them in the connecting-infrastructure layer.
      if (rosterIndex.has(String(feature.properties.segment_id))) return;
      const line = L.polyline(BSDNet.toLatLngs(feature.geometry), {
        pane: "connectingTrailsPane", lineCap: "round", lineJoin: "round", ...BSDNet.CONNECTING_TRAIL_STYLE,
      });
      line.on("click", () => showDetail({ ...feature, _trail: true }));
      layers.connectingTrails.addLayer(line);
    });
  }

  // Major-route line-name labels: one permanent tooltip per line at the
  // midpoint of its longest member — always visible, tinted to the line's
  // color so the label reads as part of the line, not generic chrome.
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
    // Trail labels sit at the city's edges and read fine citywide; the street
    // lines cluster downtown and their labels pile up below LINE_LABEL_MIN_ZOOM.
    if (lineMeta.source === "osm_trails") layers.lineLabelsTrails.addLayer(tooltip);
    else layers.lineLabelsStreets.addLayer(tooltip);
  });

  // Corridor labels for the local network: one permanent tooltip per street,
  // positioned at the midpoint of that corridor's longest segment. Streets
  // with a roster line skip this — they already carry the line label.
  corridorGroups.forEach((feats, street) => {
    if (rosterStreetNames.has(street)) return;
    const tooltip = L.tooltip({ permanent: true, direction: "center", className: "line-label" })
      .setLatLng(labelAnchor(feats))
      .setContent(BSD.esc(street));
    layers.labels.addLayer(tooltip);
  });

  if (mellowData.features.length === 0) {
    const noDataMarker = L.marker([41.8781, -87.6298], { opacity: 0 });
    noDataMarker._mellowStub = true;
    layers.mellow.addLayer(noDataMarker);
  } else {
    // Canvas renderer, not SVG: each feature's MultiLineString can carry tens
    // of thousands of parts (citywide street coverage) — SVG gives each part
    // its own DOM path command and chokes; canvas draws directly, no DOM cost.
    const mellowRenderer = L.canvas({ pane: "mellowPane" });
    mellowData.features.forEach((feature) => {
      const line = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        // Kept faint (w1.5 op0.4) so the citywide view reads major-routes-first;
        // mellow is background texture, not a competing network.
        { color: "#ec4899", weight: 1.5, opacity: 0.4, renderer: mellowRenderer, pane: "mellowPane" }
      );
      layers.mellow.addLayer(line);
    });
  }

  // Planned overlay: metro "under construction" convention — dashed line in
  // the facility color with its own dashed white casing. Stub behavior is
  // unchanged: an empty planned_routes.geojson renders nothing but still
  // shows the no_data_yet note when toggled on.
  if (plannedData.features.length === 0) {
    const noDataMarker = L.marker([41.8781, -87.6298], { opacity: 0 });
    noDataMarker._plannedStub = true;
    layers.planned.addLayer(noDataMarker);
  } else {
    plannedData.features.forEach((feature) => {
      const latlngs = BSDNet.toLatLngs(feature.geometry);
      const props = feature.properties;
      const color = BSD.FACILITY_COLORS[props.facility_category] || BSD.FACILITY_COLORS.other;

      const casing = L.polyline(latlngs, {
        pane: "plannedCasingPane", weight: 8, color: "#ffffff", dashArray: "10,8", opacity: 1, lineCap: "round",
      });
      layers.plannedCasing.addLayer(casing);

      const line = L.polyline(latlngs, {
        pane: "plannedPane", color, weight: 5, dashArray: "10,8", opacity: 0.85, lineCap: "round",
      });
      line.on("click", () => showDetail({ ...feature, _planned: true }));
      layers.planned.addLayer(line);
    });
  }

  // Nodes (spec §7): interchanges (derived intersections between distinct
  // lines) and orientation points (curated major-road crossings). No crash
  // scaling anywhere — these are wayfinding markers, not safety data.
  function makeInterchangeMarker(n) {
    const marker = L.circleMarker([n.lat, n.lng], {
      pane: "nodesPane", radius: 5, color: "#1a2330", weight: 2.5,
      fillColor: "#ffffff", fillOpacity: 1,
    });
    marker.bindTooltip(BSD.esc(n.label), { direction: "top", offset: [0, -8] });
    marker.on("click", () => showNodeDetail(n));
    return marker;
  }
  function makeOrientationMarker(n) {
    const marker = L.circleMarker([n.lat, n.lng], {
      pane: "nodesPane", radius: 3.5, color: "#64748b", weight: 2,
      fillColor: "#ffffff", fillOpacity: 1,
    });
    marker.bindTooltip(BSD.esc(n.label), {
      permanent: true, direction: "top", className: "node-label", offset: [0, -6],
    });
    marker.on("click", () => showNodeDetail(n));
    return marker;
  }
  (nodesData.nodes || []).forEach((n) => {
    if (n.kind === "interchange") layers.nodesInterchange.addLayer(makeInterchangeMarker(n));
    else if (n.kind === "orientation") layers.nodesOrientation.addLayer(makeOrientationMarker(n));
  });

  // Always-on layers (major routes: casing under colored line, line-name
  // labels on top). Toggleable overlays are mounted below from `state.overlays`.
  layers.casing.addTo(map);
  layers.lines.addTo(map);
  layers.lineLabelsTrails.addTo(map);
  // lineLabelsStreets mounts via updateDeclutter() once zoomed past LINE_LABEL_MIN_ZOOM.
  if (state.overlays.has("quality")) layers.quality.addTo(map);
  if (state.overlays.has("connecting")) {
    layers.local.addTo(map);
    layers.connectingTrails.addTo(map);
  }
  if (state.overlays.has("mellow")) layers.mellow.addTo(map);
  if (state.overlays.has("planned")) {
    layers.planned.addTo(map);
    layers.plannedCasing.addTo(map);
  }

  // Zoom-dependent declutter: node markers and corridor labels are dense at
  // city scale, so they're only shown once zoomed in enough to read them.
  // Simplest compliant approach: add/remove the whole group. Interchange
  // nodes read at NODE_INTERCHANGE_MIN_ZOOM; orientation nodes and the
  // demoted local network's corridor labels wait for LABEL_MIN_ZOOM.
  function updateDeclutter() {
    const z = map.getZoom();
    if (z >= LINE_LABEL_MIN_ZOOM) {
      if (!map.hasLayer(layers.lineLabelsStreets)) layers.lineLabelsStreets.addTo(map);
    } else if (map.hasLayer(layers.lineLabelsStreets)) {
      map.removeLayer(layers.lineLabelsStreets);
    }
    if (state.overlays.has("nodes") && z >= NODE_INTERCHANGE_MIN_ZOOM) {
      if (!map.hasLayer(layers.nodesInterchange)) layers.nodesInterchange.addTo(map);
    } else if (map.hasLayer(layers.nodesInterchange)) {
      map.removeLayer(layers.nodesInterchange);
    }
    if (state.overlays.has("nodes") && z >= LABEL_MIN_ZOOM) {
      if (!map.hasLayer(layers.nodesOrientation)) layers.nodesOrientation.addTo(map);
    } else if (map.hasLayer(layers.nodesOrientation)) {
      map.removeLayer(layers.nodesOrientation);
    }
    if (state.overlays.has("connecting") && z >= LABEL_MIN_ZOOM) {
      if (!map.hasLayer(layers.labels)) layers.labels.addTo(map);
    } else if (map.hasLayer(layers.labels)) {
      map.removeLayer(layers.labels);
    }
  }
  map.on("zoomend", updateDeclutter);

  // Fit bounds to bike network
  if (routeFeatures.length > 0) {
    const allBounds = routeFeatures.map(f => BSDNet.getPaddedBBox(f.geometry))
      .reduce((acc, bbox) => {
        if (acc.length === 0) return bbox;
        return [
          [Math.min(acc[0][0], bbox[0][0]), Math.min(acc[0][1], bbox[0][1])],
          [Math.max(acc[1][0], bbox[1][0]), Math.max(acc[1][1], bbox[1][1])],
        ];
      }, []);
    // animate: false — this citywide fit must apply synchronously so a
    // ?corridor=/?line= restore further down can override it. Animated,
    // its zoom animation lands a frame later and silently undoes the
    // deep link's own fitBounds.
    map.fitBounds(allBounds, { padding: [50, 50], animate: false });
  }
  updateDeclutter();

  // Dynamic planned-toggle badge: stub while planned_routes.geojson is
  // still empty; once the pipeline populates it, shows the real data tier
  // with zero UI changes needed.
  const plannedBadgeTier = plannedData.properties?.status === "no_data_yet"
    ? "stub"
    : (plannedData.features[0]?.properties?.data_tier || "real");

  // Connecting-infrastructure badge: this one toggle gates two tiers at once
  // — the demoted local ("bus") street network (real CDOT data) and the
  // non-roster OSM trails (crowdsourced) — so show both badges rather than
  // just "real". Grouped in their own flex span (instead of two bare
  // .badge buttons) so the layer-control CSS's `margin-left: auto` right-align
  // rule pushes them over as one unit instead of splitting the free space
  // between them and spreading them apart / wrapping awkwardly in the 300px panel.
  const connectingBadgesHTML =
    `<span style="display:inline-flex; gap:0.3rem; margin-left:auto; flex:none;">${BSD.badgeHTML("real")}${BSD.badgeHTML("crowdsourced")}</span>`;

  // Quality-border grade legend (spec §6): main-route quality border colors
  // per segment grade. `none` is dashed on the map, so its swatch is dashed
  // too. Only rendered while the "quality" toggle is on.
  const GRADE_LEGEND = [
    ["offstreet", "Off-street trail"],
    ["protected", "Protected lane"],
    ["painted", "Paint only (buffered / painted / greenway)"],
    ["none", "Nothing (sharrows)"],
  ];
  function gradeLegendHTML() {
    return GRADE_LEGEND.map(([grade, label]) => {
      const dashed = grade === "none";
      const bar = dashed
        ? `border-top: 3px dashed ${BSDNet.GRADE_COLORS[grade]};`
        : `background: ${BSDNet.GRADE_COLORS[grade]}; height: 3px;`;
      return `
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; font-size: 0.85em;">
          <div style="width: 22px; ${bar}"></div>
          <span>${BSD.esc(label)}</span>
        </div>
      `;
    }).join("");
  }

  // Line legend: grouped Trails then Street lines, color chip + name +
  // termini, sourced from main_routes.geojson's `lines` array.
  function legendRow(line) {
    const color = BSDNet.LINE_COLORS[line.id] || BSDNet.FALLBACK_LINE_COLOR;
    const tier = line.no_data ? "stub" : line.data_tier;
    // Name row and termini row are separate lines: with the tier badge in the
    // flex row there isn't enough width left for "name — termini" without
    // one-word-per-line wrapping in the 300px panel.
    const termini = line.termini
      ? `<div style="margin-left: calc(22px + 0.5rem); color: #64748b; font-size: 0.92em;">${BSD.esc(line.termini)}</div>`
      : "";
    return `
      <div style="margin-bottom: 0.45rem; font-size: 0.85em;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <div style="width: 22px; height: 4px; border-radius: 2px; background: ${color}; flex: none;"></div>
          <span style="flex: 1; min-width: 0;">${BSD.esc(line.name)}</span>
          ${BSD.badgeHTML(tier)}
        </div>
        ${termini}
      </div>
    `;
  }
  const allLines = mainRoutesData.lines || [];
  const trailLines = allLines.filter(l => l.source === "osm_trails");
  const streetLines = allLines.filter(l => l.source !== "osm_trails");
  function legendGroupHTML(title, lines) {
    if (lines.length === 0) return "";
    return `
      <div style="margin: 0.7rem 0 0.4rem;"><strong>${BSD.esc(title)}</strong></div>
      ${lines.map(legendRow).join("")}
    `;
  }

  // Build side panel
  const side = document.getElementById("side");
  side.innerHTML = `
    <div>
      <h2>Bikeway network</h2>
      <p class="muted">Route-planning view: how to get from area A to area B. Major routes are drawn heavy, one solid color per named line. Toggle the quality border to see how much of a route actually protects you, and connecting infrastructure or mellow routes to see the lower-stress options that feed into it. For crash and infrastructure-condition data by location, see the <a href="index.html">Map</a>.</p>

      <div class="layer-control">
        <div class="filter-row">
          <input type="checkbox" id="quality-toggle" ${state.overlays.has("quality") ? "checked" : ""}>
          <label for="quality-toggle">Quality border ${BSD.badgeHTML("derived")}</label>
        </div>
        <div id="quality-legend" style="display:${state.overlays.has("quality") ? "" : "none"}; margin: 0 0 0.6rem 1.6rem;">
          ${gradeLegendHTML()}
        </div>
        <div class="filter-row">
          <input type="checkbox" id="connecting-toggle" ${state.overlays.has("connecting") ? "checked" : ""}>
          <label for="connecting-toggle" style="flex: 1 1 0; min-width: 0;"><span style="flex: 1 1 auto; min-width: 0;">Connecting infrastructure</span>${connectingBadgesHTML}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="mellow-toggle" ${state.overlays.has("mellow") ? "checked" : ""}>
          <label for="mellow-toggle">Mellow routes ${BSD.badgeHTML("crowdsourced")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="nodes-toggle" ${state.overlays.has("nodes") ? "checked" : ""}>
          <label for="nodes-toggle">Nodes ${BSD.badgeHTML("derived")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="planned-toggle" ${state.overlays.has("planned") ? "checked" : ""}>
          <label for="planned-toggle">Planned routes ${BSD.badgeHTML(plannedBadgeTier)}</label>
        </div>
      </div>

      <div class="line-legend">
        ${legendGroupHTML("Trails", trailLines)}
        ${legendGroupHTML("Street lines", streetLines)}
      </div>

      ${BSD.noticeHTML("directional")}
      <div class="side-detail" id="detail"></div>
    </div>
  `;

  // Mirror the toggle handlers' stub-note logic for overlays restored from
  // the URL (e.g. ?overlays=mellow or ?overlays=planned): the toggle
  // handlers only show the no_data_yet note in response to a checkbox
  // "change" event, so a layer mounted directly from state.overlays above
  // needs the same check applied here, now that #detail exists.
  if (state.overlays.has("mellow") && mellowData.features.length === 0) {
    showDetail({ _mellowStub: true, properties: mellowData.properties });
  }
  if (state.overlays.has("planned") && plannedData.features.length === 0) {
    showDetail({ _plannedStub: true, properties: plannedData.properties });
  }
  if (state.overlays.has("connecting") && (osmTrailsData.features || []).length === 0) {
    showDetail({ _trailsStub: true, properties: osmTrailsData.properties });
  }

  // Toggle handlers: mutate state.overlays, sync the map layer, then push
  // the new state to the URL so every toggle is deep-linkable.
  document.getElementById("quality-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("quality"); else state.overlays.delete("quality");
    if (e.target.checked) layers.quality.addTo(map);
    else map.removeLayer(layers.quality);
    document.getElementById("quality-legend").style.display = e.target.checked ? "" : "none";
    syncURL();
  });

  document.getElementById("connecting-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("connecting"); else state.overlays.delete("connecting");
    if (e.target.checked) {
      layers.local.addTo(map);
      layers.connectingTrails.addTo(map);
      if ((osmTrailsData.features || []).length === 0) {
        showDetail({ _trailsStub: true, properties: osmTrailsData.properties });
      }
    } else {
      map.removeLayer(layers.local);
      map.removeLayer(layers.connectingTrails);
      if ((osmTrailsData.features || []).length === 0) {
        document.getElementById("detail").innerHTML = "";
      }
    }
    updateDeclutter(); // corridor labels only make sense while connecting infra is drawn
    syncURL();
  });

  document.getElementById("mellow-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("mellow"); else state.overlays.delete("mellow");
    if (e.target.checked) {
      layers.mellow.addTo(map);
      if (mellowData.features.length === 0) {
        showDetail({ _mellowStub: true, properties: mellowData.properties });
      }
    } else {
      map.removeLayer(layers.mellow);
      if (mellowData.features.length === 0) {
        document.getElementById("detail").innerHTML = "";
      }
    }
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
      if (plannedData.features.length === 0) {
        showDetail({ _plannedStub: true, properties: plannedData.properties });
      }
    } else {
      map.removeLayer(layers.planned);
      map.removeLayer(layers.plannedCasing);
      if (plannedData.features.length === 0) {
        document.getElementById("detail").innerHTML = "";
      }
    }
    syncURL();
  });

  function showDetail(feature) {
    const detail = document.getElementById("detail");

    if (feature._mellowStub) {
      detail.innerHTML = `
        <div>
          <strong>Mellow Bike Map</strong>
          <p class="muted">${BSD.esc(feature.properties.note)}</p>
        </div>
      `;
      return;
    }

    if (feature._trailsStub) {
      detail.innerHTML = `
        <div>
          <strong>OpenStreetMap Off-street Trails</strong>
          <p class="muted">${BSD.esc(feature.properties.note)}</p>
        </div>
      `;
      return;
    }

    if (feature._trail) {
      const props = feature.properties;
      detail.innerHTML = `
        <div>
          <strong>${BSD.esc(props.name || "Off-street trail")}</strong> ${BSD.badgeHTML("crowdsourced")}
          <dl>
            <dt>Type</dt><dd>${BSD.esc(BSD.FACILITY_LABELS.trail)}</dd>
            <dt>Length</dt><dd>${BSD.fmt(Math.round(props.length_m))} m</dd>
          </dl>
          <p class="muted">Trail geometry from OpenStreetMap — crowdsourced, coverage varies.</p>
        </div>
      `;
      return;
    }

    if (feature._plannedStub) {
      detail.innerHTML = `
        <div>
          <strong>Planned bikeways</strong>
          <p class="muted">${BSD.esc(feature.properties.note)}</p>
        </div>
      `;
      return;
    }

    if (feature._planned) {
      const props = feature.properties;
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

    const props = feature.properties;
    const streetLabel = props.street || "(unnamed)";
    // Keep state.corridor (and state.line) in sync with the visible corridor
    // so a later toggle-driven syncURL() call doesn't write a stale/empty
    // param while this street's detail is still on screen.
    state.corridor = streetLabel;
    const rosterEntry = rosterIndex.get(String(props.segment_id));
    const lineMeta = rosterEntry ? linesMeta.get(rosterEntry.lineId) : null;
    state.line = lineMeta ? lineMeta.id : "";

    // Corridor context: aggregate every segment sharing this street name.
    const corridorFeats = corridorGroups.get(streetLabel) || [feature];
    const corridorLength = corridorFeats.reduce((sum, f) => sum + (f.properties.length_m || 0), 0);

    const corridor = encodeURIComponent(props.street);
    const link = `index.html?layers=crashes,infrastructure&corridor=${corridor}`;

    // Main-route context: name the line this segment belongs to and print
    // its report-card number. Stats are derived tier (computed each run).
    const lineRows = lineMeta ? `
          <dt>Major route</dt>
          <dd>${BSD.esc(lineMeta.name)}${lineMeta.termini ? ` — ${BSD.esc(lineMeta.termini)}` : ""}</dd>

          <dt>Line protected end-to-end</dt>
          <dd>${lineMeta.pct_protected != null ? `${BSD.fmt(lineMeta.pct_protected)} %` : "—"} of ${BSD.fmt(lineMeta.miles_total)} mi ${BSD.badgeHTML("derived")}</dd>
    ` : "";

    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(streetLabel)}</strong>
        <dl>
          ${lineRows}
          <dt>Facility type</dt>
          <dd>${BSD.esc(BSD.FACILITY_LABELS[props.facility_category] || props.facility_type_raw)}</dd>

          <dt>Segment length</dt>
          <dd>${BSD.fmt(Math.round(props.length_m))} m</dd>

          <dt>Corridor total length</dt>
          <dd>${BSD.fmt(Math.round(corridorLength))} m across ${corridorFeats.length} segment${corridorFeats.length === 1 ? "" : "s"} ${BSD.badgeHTML("real")}</dd>

          <dt></dt>
          <dd><a href="${link}">Crash & infrastructure data →</a></dd>
        </dl>
      </div>
    `;

    selectedRoute = feature;
  }

  // Detail panel for an interchange or orientation node (spec §7). Purely
  // wayfinding — no crash scaling, no safety data.
  function showNodeDetail(n) {
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
    selectedRoute = null;
  }

  // Detail panel for a major-route trail member (source: osm_trails).
  // Everything here is crowdsourced tier and stays that way — no crash
  // stats exist for trails and none are shown (never fabricate).
  function showRosterTrailDetail(feature) {
    const props = feature.properties;
    const lineMeta = linesMeta.get(props.line_id);
    state.line = props.line_id;
    state.corridor = "";
    const detail = document.getElementById("detail");
    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(lineMeta ? lineMeta.name : "Off-street trail")}</strong> ${BSD.badgeHTML("crowdsourced")}
        ${lineMeta && lineMeta.termini ? `<p class="muted">${BSD.esc(lineMeta.termini)}</p>` : ""}
        <dl>
          <dt>Type</dt>
          <dd>${BSD.esc(BSD.FACILITY_LABELS.trail)}</dd>

          <dt>Line length</dt>
          <dd>${lineMeta && lineMeta.miles_total
            ? `${BSD.fmt(lineMeta.miles_total)} mi`
            : `${BSD.fmt(Math.round(props.length_m))} m`} ${BSD.badgeHTML("crowdsourced")}</dd>
        </dl>
        <p class="muted">Trail geometry from OpenStreetMap — crowdsourced, coverage varies. Off-street the whole way.</p>
      </div>
    `;
    selectedRoute = null;
  }

  // Restore ?corridor= from the URL: select the corridor's longest segment
  // (same behavior showDetail gives a line click) and fit the map to the
  // corridor's combined bounds. This is the contract the Map screen's
  // "Plan a route here ->" link relies on (network.html?corridor=<street>).
  if (state.corridor) {
    const corridorFeats = corridorGroups.get(state.corridor);
    if (corridorFeats && corridorFeats.length > 0) {
      const longest = corridorFeats.reduce((best, f) =>
        (f.properties.length_m || 0) > (best.properties.length_m || 0) ? f : best
      );
      showDetail(longest);
      const corridorBounds = corridorFeats.map(f => BSDNet.getPaddedBBox(f.geometry))
        .reduce((acc, bbox) => {
          if (acc.length === 0) return bbox;
          return [
            [Math.min(acc[0][0], bbox[0][0]), Math.min(acc[0][1], bbox[0][1])],
            [Math.max(acc[1][0], bbox[1][0]), Math.max(acc[1][1], bbox[1][1])],
          ];
        }, []);
      map.fitBounds(corridorBounds, { padding: [50, 50], animate: false });
    }
  } else if (state.line) {
    // Restore ?line= (major-route deep link): fit the whole line and open
    // its detail via the same mechanisms a click would use. ?corridor= wins
    // when both are present — it is the older, more specific contract.
    const lineMeta = linesMeta.get(state.line);
    const members = lineMeta && lineMeta.source === "osm_trails"
      ? rosterTrailFeatures.filter((f) => f.properties.line_id === state.line)
      : BSDNet.membersOfLine(rosterFeatures, rosterIndex, state.line);
    if (members.length > 0) {
      const longest = members.reduce((best, f) =>
        (f.properties.length_m || 0) > (best.properties.length_m || 0) ? f : best
      );
      if (lineMeta.source === "osm_trails") showRosterTrailDetail(longest);
      else showDetail(longest);
      const lineBounds = members.map(f => BSDNet.getPaddedBBox(f.geometry))
        .reduce((acc, bbox) => {
          if (acc.length === 0) return bbox;
          return [
            [Math.min(acc[0][0], bbox[0][0]), Math.min(acc[0][1], bbox[0][1])],
            [Math.max(acc[1][0], bbox[1][0]), Math.max(acc[1][1], bbox[1][1])],
          ];
        }, []);
      map.fitBounds(lineBounds, { padding: [50, 50], animate: false });
    } else if (lineMeta && lineMeta.no_data) {
      // Honest empty state: the trail line is on the roster but osm_trails
      // is still a stub — say so instead of drawing nothing silently.
      document.getElementById("detail").innerHTML = `
        <div>
          <strong>${BSD.esc(lineMeta.name)}</strong> ${BSD.badgeHTML("crowdsourced")}
          <p class="muted">No trail geometry yet — this off-street line fills in with the first live OpenStreetMap trails pull. We never draw fabricated geometry.</p>
        </div>
      `;
    }
  }
})();
