(async function () {
  BSD.initPage("network.html");

  // Paper canvas, not a basemap: this screen renders real geometry
  // metro-style (thick casing + line, station markers, corridor labels)
  // rather than a distorted schematic (DECISIONS.md #10).
  document.getElementById("map").style.background = "#f7f9fb";

  const map = L.map("map", {
    attributionControl: false,
    zoom: 11,
    center: [41.8781, -87.6298],
  });

  const STATION_MIN_ZOOM = 12;
  const LABEL_MIN_ZOOM = 13;

  // Explicit panes (not DOM insertion order) so z-order is stable no matter
  // which toggles are on at load vs. flipped later: wards backdrop -> local
  // ("bus") background network -> mellow background -> heat halos -> casing
  // -> planned casing -> lines -> planned lines -> crash rings -> stations.
  // Labels use Leaflet's own tooltipPane, already above every overlay pane.
  const PANE_ORDER = [
    "wardsPane", "localPane", "mellowPane", "trailsPane", "heatPane", "casingPane",
    "plannedCasingPane", "linesPane", "plannedPane", "crashesPane", "stationsPane",
  ];
  PANE_ORDER.forEach((name, i) => {
    map.createPane(name);
    map.getPane(name).style.zIndex = 200 + i * 10;
  });

  const layers = {
    casing: L.layerGroup(),
    infrastructure: L.layerGroup(), // roster ("rail") lines, heavy metro treatment
    local: L.layerGroup(), // everything else: thin muted "bus" background network
    stations: L.layerGroup(), // hotspot stations on/near roster lines
    stationsLocal: L.layerGroup(), // hotspot stations off the roster (declutter later)
    labels: L.layerGroup(), // corridor labels for local streets (LABEL_MIN_ZOOM+)
    lineLabels: L.layerGroup(), // roster line-name labels, always on
    obstructions: L.layerGroup(), // obstruction heat halos
    crashes: L.layerGroup(),
    mellow: L.layerGroup(),
    planned: L.layerGroup(),
    plannedCasing: L.layerGroup(),
    trails: L.layerGroup(),
  };

  let routeFeatures = [];
  let obstructionPoints = [];
  let selectedRoute = null;

  // URL state: ?overlays=heat,crashes,stations,mellow,planned&corridor=<street>&line=<roster line id>
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

  // Load data
  const [bikeRoutes, obstructionsData, mellowData, plannedData, osmTrailsData, mainRoutesData, wardsData, stations] = await Promise.all([
    BSD.loadJSON("data/bike_routes.geojson"),
    BSD.loadJSON("data/obstructions_mock.geojson"),
    BSD.loadJSON("data/mellow_routes.geojson"),
    BSD.loadJSON("data/planned_routes.geojson"),
    BSD.loadJSON("data/osm_trails.geojson"),
    BSD.loadJSON("data/main_routes.geojson"),
    BSD.loadJSON("data/wards.geojson"),
    BSD.loadJSON("data/intersections.json"),
  ]);

  routeFeatures = bikeRoutes.features;
  obstructionPoints = obstructionsData.features;

  // Count obstructions per route segment and group segments into corridors —
  // pure helpers live in network-model.js so Task 3's overlays can reuse them.
  const obstructionCounts = BSDNet.countObstructions(routeFeatures, obstructionPoints);
  const corridorGroups = BSDNet.groupByCorridor(routeFeatures);

  // Main routes ("rail vs bus", spec §7): the curated roster keeps the heavy
  // metro treatment, colored by facility grade along the line; every other
  // segment demotes to a thin muted background network.
  const rosterIndex = BSDNet.buildRosterIndex(mainRoutesData.features);
  const linesMeta = BSDNet.linesById(mainRoutesData.lines);
  const { roster: rosterFeatures, local: localFeatures } = BSDNet.splitByRoster(routeFeatures, rosterIndex);
  // Roster trail members live only in main_routes.geojson (their source is
  // osm_trails, not bike_routes). Currently empty while osm_trails is a stub —
  // every trail line carries no_data: true — but the render path below is the
  // same one the first live OSM pull will light up.
  const rosterTrailFeatures = mainRoutesData.features.filter(
    (f) => (linesMeta.get(f.properties.line_id) || {}).source === "osm_trails"
  );
  const rosterStreetNames = BSDNet.rosterStreets(routeFeatures, rosterIndex);

  // Ward boundaries: a faint, always-on city anchor beneath the network —
  // context only, not a data layer with its own toggle or tier badge.
  L.geoJSON(wardsData, { pane: "wardsPane", style: { color: "#e2e8f0", weight: 1, fill: false } }).addTo(map);

  // Draw roster ("rail") lines: white casing underneath, grade-colored line
  // on top, so overlapping routes read as distinct "lines" like a transit
  // diagram. Grade colors per spec §4; `none` grade renders dashed.
  rosterFeatures.forEach((feature) => {
    const latlngs = BSDNet.toLatLngs(feature.geometry);
    const casing = L.polyline(latlngs, {
      pane: "casingPane", weight: 10, color: "#ffffff", opacity: 1, lineCap: "round", lineJoin: "round",
    });
    layers.casing.addLayer(casing);

    const grade = rosterIndex.get(String(feature.properties.segment_id)).grade;
    const line = L.polyline(latlngs, {
      pane: "linesPane", lineCap: "round", lineJoin: "round", opacity: 1,
      ...BSDNet.gradeLineStyle(grade),
    });
    line.on("click", () => showDetail(feature));
    line.feature = feature;
    layers.infrastructure.addLayer(line);
  });

  // Draw the local ("bus") network: everything not on the roster, 1.5px
  // muted, no casing, no stations/labels until zoomed past LABEL_MIN_ZOOM.
  // Still clickable so corridor detail (and ?corridor= links) work citywide.
  localFeatures.forEach((feature) => {
    const line = L.polyline(BSDNet.toLatLngs(feature.geometry), {
      pane: "localPane", lineCap: "round", lineJoin: "round", ...BSDNet.LOCAL_STYLE,
    });
    line.on("click", () => showDetail(feature));
    line.feature = feature;
    layers.local.addLayer(line);
  });

  // Roster OSM trails get the heavy treatment too (offstreet grade color).
  // Their stats stay crowdsourced-tier — the detail panel says so.
  rosterTrailFeatures.forEach((feature) => {
    const latlngs = BSDNet.toLatLngs(feature.geometry);
    const casing = L.polyline(latlngs, {
      pane: "casingPane", weight: 10, color: "#ffffff", opacity: 1, lineCap: "round", lineJoin: "round",
    });
    layers.casing.addLayer(casing);

    const line = L.polyline(latlngs, {
      pane: "linesPane", lineCap: "round", lineJoin: "round", opacity: 1,
      ...BSDNet.gradeLineStyle(feature.properties.grade || "offstreet"),
    });
    line.on("click", () => showRosterTrailDetail(feature));
    layers.infrastructure.addLayer(line);
  });

  // Draw station markers (crash hotspot clusters from data/intersections.json).
  // Stations on/near a roster line keep metro prominence (STATION_MIN_ZOOM);
  // stations out on the local network wait for LABEL_MIN_ZOOM like the labels.
  const rosterBBoxes = rosterFeatures.concat(rosterTrailFeatures)
    .map((f) => BSDNet.getPaddedBBox(f.geometry, 0.001));
  const { onRoster: rosterStations, offRoster: localStations } = BSDNet.splitStations(stations, rosterBBoxes);
  function makeStationMarker(s) {
    const marker = L.circleMarker([s.lat, s.lng], {
      pane: "stationsPane",
      radius: 4 + Math.min(s.crashes, 12) * 0.5,
      color: "#1a2330",
      weight: 2.5,
      fillColor: "#ffffff",
      fillOpacity: 1,
    });
    marker.bindTooltip(BSD.esc(s.label), {
      permanent: true, direction: "top", className: "station-label", offset: [0, -8],
    });
    marker.on("click", () => showStationDetail(s));
    return marker;
  }
  rosterStations.forEach((s) => layers.stations.addLayer(makeStationMarker(s)));
  localStations.forEach((s) => layers.stationsLocal.addLayer(makeStationMarker(s)));

  // Roster line-name labels: one permanent tooltip per line at the midpoint
  // of its longest member — always visible, these ARE the metro map.
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
    const tooltip = L.tooltip({ permanent: true, direction: "center", className: "line-label" })
      .setLatLng(labelAnchor(members))
      .setContent(BSD.esc(lineMeta.name));
    layers.lineLabels.addLayer(tooltip);
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

  // Draw obstruction heat: translucent color halos, sized/colored by
  // BSDNet.heatBucket, under the casing for every segment with count >= 1.
  routeFeatures.forEach((feature) => {
    const count = obstructionCounts.get(feature.properties.segment_id);
    const bucket = BSDNet.heatBucket(count);
    if (bucket) {
      const halo = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        { pane: "heatPane", color: bucket.color, weight: 16, opacity: 0.45, lineCap: "round" }
      );
      layers.obstructions.addLayer(halo);
    }
  });

  // Draw crash severity overlay: metro-legible rings, not filled dots.
  routeFeatures.forEach((feature) => {
    const crashes = feature.properties.crashes_within_30m;
    if (crashes >= 5) {
      const coords = BSDNet.flattenCoords(feature.geometry);
      const mid = coords[Math.floor(coords.length / 2)];
      const marker = L.circleMarker([mid[1], mid[0]], {
        pane: "crashesPane",
        radius: Math.min(4 + crashes / 3, 14),
        color: "#dc2626",
        weight: 2,
        fillColor: "#dc2626",
        fillOpacity: 0.15,
      });
      layers.crashes.addLayer(marker);
    }
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
        { color: "#ec4899", weight: 2, opacity: 0.6, renderer: mellowRenderer, pane: "mellowPane" }
      );
      layers.mellow.addLayer(line);
    });
  }

  if (osmTrailsData.features.length === 0) {
    const noDataMarker = L.marker([41.8781, -87.6298], { opacity: 0 });
    noDataMarker._trailsStub = true;
    layers.trails.addLayer(noDataMarker);
  } else {
    osmTrailsData.features.forEach((feature) => {
      // Roster trails are already drawn heavy with the main routes above —
      // don't double-draw them in this overlay.
      if (rosterIndex.has(String(feature.properties.segment_id))) return;
      const line = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        { color: BSD.FACILITY_COLORS.trail, weight: 4, opacity: 0.9, lineCap: "round", pane: "trailsPane" }
      );
      line.on("click", () => showDetail({ ...feature, _trail: true }));
      layers.trails.addLayer(line);
    });
  }

  // Planned overlay: metro "under construction" convention — dashed line in
  // the facility color with its own dashed white casing. Stub behavior is
  // unchanged: an empty planned_routes.geojson renders nothing but still
  // shows the no_data_yet note when toggled on (Task 3 brief #2).
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

  // Always-on layers (local background beneath casing beneath colored roster
  // lines, line-name labels on top). Toggleable overlays are mounted below
  // from `state.overlays`.
  layers.local.addTo(map);
  layers.casing.addTo(map);
  layers.infrastructure.addTo(map);
  layers.lineLabels.addTo(map);
  if (state.overlays.has("heat")) layers.obstructions.addTo(map);
  if (state.overlays.has("crashes")) layers.crashes.addTo(map);
  if (state.overlays.has("mellow")) layers.mellow.addTo(map);
  if (state.overlays.has("trails")) layers.trails.addTo(map);
  if (state.overlays.has("planned")) {
    layers.planned.addTo(map);
    layers.plannedCasing.addTo(map);
  }

  let stationsEnabled = state.overlays.has("stations");

  // Zoom-dependent declutter: station markers+labels and corridor labels
  // are dense at city scale, so they're only shown once zoomed in enough
  // to read them. Simplest compliant approach: add/remove the whole group.
  // The demoted local network shows no stations or labels below
  // LABEL_MIN_ZOOM (spec §7); roster stations keep STATION_MIN_ZOOM.
  function updateDeclutter() {
    const z = map.getZoom();
    if (stationsEnabled && z >= STATION_MIN_ZOOM) {
      if (!map.hasLayer(layers.stations)) layers.stations.addTo(map);
    } else if (map.hasLayer(layers.stations)) {
      map.removeLayer(layers.stations);
    }
    if (stationsEnabled && z >= LABEL_MIN_ZOOM) {
      if (!map.hasLayer(layers.stationsLocal)) layers.stationsLocal.addTo(map);
    } else if (map.hasLayer(layers.stationsLocal)) {
      map.removeLayer(layers.stationsLocal);
    }
    if (z >= LABEL_MIN_ZOOM) {
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
  // with zero UI changes needed (Task 3 brief #2).
  const plannedBadgeTier = plannedData.properties?.status === "no_data_yet"
    ? "stub"
    : (plannedData.features[0]?.properties?.data_tier || "real");

  // 3-swatch heat legend, using the same buckets/colors as the halos.
  const heatSwatches = [BSDNet.heatBucket(1), BSDNet.heatBucket(3), BSDNet.heatBucket(6)];

  // Build side panel
  const side = document.getElementById("side");
  side.innerHTML = `
    <div>
      <h2>Bikeway network</h2>
      <p class="muted">Route-planning view: the main routes drawn heavy, graded by how much actually protects you; every other bikeway sits underneath as the thin local network. For why a street is dangerous, see the <a href="index.html">Map</a>.</p>

      <div class="layer-control">
        <div class="filter-row">
          <input type="checkbox" id="mainroutes-toggle" checked disabled>
          <label for="mainroutes-toggle">Main routes ${BSD.badgeHTML("derived")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="local-toggle" checked disabled>
          <label for="local-toggle">Local network ${BSD.badgeHTML("real")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="station-toggle" ${state.overlays.has("stations") ? "checked" : ""}>
          <label for="station-toggle">Crash hotspots (stations) ${BSD.badgeHTML("real")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="heat-toggle" ${state.overlays.has("heat") ? "checked" : ""}>
          <label for="heat-toggle">Obstruction heat ${BSD.badgeHTML("mock")}</label>
        </div>
        <div id="heat-legend" style="display:${state.overlays.has("heat") ? "" : "none"}; margin: 0 0 0.6rem 1.6rem;">
          ${heatSwatches.map(b => `
            <span style="display:inline-flex; align-items:center; gap:0.3rem; margin-right:0.7rem; font-size:0.8em;">
              <span class="legend-swatch" style="width:14px; height:14px; border-radius:50%; background:${b.color}; opacity:0.45;"></span>
              ${BSD.esc(b.label)}
            </span>`).join("")}
        </div>
        <div class="filter-row">
          <input type="checkbox" id="crash-toggle" ${state.overlays.has("crashes") ? "checked" : ""}>
          <label for="crash-toggle">Crash severity ${BSD.badgeHTML("real")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="mellow-toggle" ${state.overlays.has("mellow") ? "checked" : ""}>
          <label for="mellow-toggle">Mellow streets ${BSD.badgeHTML("crowdsourced")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="trails-toggle" ${state.overlays.has("trails") ? "checked" : ""}>
          <label for="trails-toggle">Off-street trails ${BSD.badgeHTML("crowdsourced")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="planned-toggle" ${state.overlays.has("planned") ? "checked" : ""}>
          <label for="planned-toggle">Planned routes ${BSD.badgeHTML(plannedBadgeTier)}</label>
        </div>
      </div>

      <p class="muted" style="font-size: 0.82em; margin: 0 0 0.6rem;">Station circle size = crashes in that intersection cluster.</p>

      <div class="legend-swatch">
        <div style="margin-bottom: 0.75rem;">
          <strong>Main-route grades</strong>
        </div>
  `;

  // Grade legend (spec §4): main-route lines are colored by facility grade
  // along their length, not by raw facility type. `none` is dashed on the
  // map, so its swatch is dashed too. The local network gets its own row.
  const GRADE_LEGEND = [
    ["offstreet", "Off-street trail"],
    ["protected", "Protected lane"],
    ["painted", "Paint only (buffered / painted / greenway)"],
    ["none", "Nothing (sharrows)"],
  ];
  for (const [grade, label] of GRADE_LEGEND) {
    const dashed = grade === "none";
    const bar = dashed
      ? `border-top: 3px dashed ${BSDNet.GRADE_COLORS[grade]};`
      : `background: ${BSDNet.GRADE_COLORS[grade]}; height: 3px;`;
    side.innerHTML += `
      <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.9em;">
        <div style="width: 24px; ${bar}"></div>
        <span>${label}</span>
      </div>
    `;
  }
  side.innerHTML += `
      <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.9em;">
        <div style="width: 24px; height: 2px; background: ${BSDNet.LOCAL_STYLE.color};"></div>
        <span>Local network (all other bikeways)</span>
      </div>
  `;

  side.innerHTML += `
      </div>
      ${BSD.noticeHTML("directional")}
      <div id="dooring-note" style="display:${state.overlays.has("crashes") ? "" : "none"}">${BSD.noticeHTML("dooring")}</div>
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
  if (state.overlays.has("trails") && osmTrailsData.features.length === 0) {
    showDetail({ _trailsStub: true, properties: osmTrailsData.properties });
  }

  // Toggle handlers: mutate state.overlays, sync the map layer, then push
  // the new state to the URL so every toggle is deep-linkable.
  document.getElementById("station-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("stations"); else state.overlays.delete("stations");
    stationsEnabled = e.target.checked;
    updateDeclutter();
    syncURL();
  });

  document.getElementById("heat-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("heat"); else state.overlays.delete("heat");
    if (e.target.checked) layers.obstructions.addTo(map);
    else map.removeLayer(layers.obstructions);
    document.getElementById("heat-legend").style.display = e.target.checked ? "" : "none";
    syncURL();
  });

  document.getElementById("crash-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("crashes"); else state.overlays.delete("crashes");
    if (e.target.checked) layers.crashes.addTo(map);
    else map.removeLayer(layers.crashes);
    // Dooring undercount disclaimer is mandatory wherever crash density shows.
    document.getElementById("dooring-note").style.display = e.target.checked ? "" : "none";
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

  document.getElementById("trails-toggle").addEventListener("change", (e) => {
    if (e.target.checked) state.overlays.add("trails"); else state.overlays.delete("trails");
    if (e.target.checked) {
      layers.trails.addTo(map);
      if (osmTrailsData.features.length === 0) {
        showDetail({ _trailsStub: true, properties: osmTrailsData.properties });
      }
    } else {
      map.removeLayer(layers.trails);
      if (osmTrailsData.features.length === 0) {
        document.getElementById("detail").innerHTML = "";
      }
    }
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
          <strong>Off-street trails</strong>
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
    const obCount = obstructionCounts.get(props.segment_id) || 0;

    // Corridor context: aggregate every segment sharing this street name.
    const corridorFeats = corridorGroups.get(streetLabel) || [feature];
    const corridorLength = corridorFeats.reduce((sum, f) => sum + (f.properties.length_m || 0), 0);
    const corridorCrashes = corridorFeats.reduce((sum, f) => sum + (f.properties.crashes_within_30m || 0), 0);

    const corridor = encodeURIComponent(props.street);
    const link = `index.html?layers=crashes,infrastructure&corridor=${corridor}`;

    // Main-route context: name the line this segment belongs to and print
    // its report-card number. Stats are derived tier (computed each run).
    const lineRows = lineMeta ? `
          <dt>Main route</dt>
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

          <dt>Segment crashes within 30m</dt>
          <dd>${BSD.fmt(props.crashes_within_30m)} ${BSD.badgeHTML("real")}</dd>

          <dt>Obstruction count</dt>
          <dd>${BSD.fmt(obCount)} ${BSD.badgeHTML("mock")}</dd>

          <dt>Corridor total length</dt>
          <dd>${BSD.fmt(Math.round(corridorLength))} m across ${corridorFeats.length} segment${corridorFeats.length === 1 ? "" : "s"} ${BSD.badgeHTML("real")}</dd>

          <dt>Corridor crashes within 30m</dt>
          <dd>${BSD.fmt(corridorCrashes)} ${BSD.badgeHTML("real")}</dd>

          <dt></dt>
          <dd><a href="${link}">Density view →</a></dd>
        </dl>
        ${BSD.noticeHTML("dooring")}
      </div>
    `;

    selectedRoute = feature;
  }

  function showStationDetail(s) {
    const detail = document.getElementById("detail");
    const link = "index.html?layers=crashes,infrastructure";

    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(s.label)}</strong>
        <dl>
          <dt>Crashes in cluster</dt>
          <dd>${BSD.fmt(s.crashes)} ${BSD.badgeHTML(s.data_tier || "real")}</dd>
        </dl>
        ${BSD.noticeHTML("dooring")}
        <p><a href="${link}">Density view →</a></p>
        <p><a href="#" id="station-center">Center map here →</a></p>
      </div>
    `;

    document.getElementById("station-center").addEventListener("click", (e) => {
      e.preventDefault();
      map.setView([s.lat, s.lng], 16);
    });

    selectedRoute = null;
  }

  // Detail panel for a roster trail line member (source: osm_trails).
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
        <p class="muted">Trail geometry from OpenStreetMap — crowdsourced, coverage varies. Off-street the whole way; no crash stats are computed for trails.</p>
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
    // Restore ?line= (roster line deep link): fit the whole line and open
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
