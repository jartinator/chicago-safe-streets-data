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

  const layers = {
    casing: L.layerGroup(),
    infrastructure: L.layerGroup(),
    stations: L.layerGroup(),
    labels: L.layerGroup(),
    obstructions: L.layerGroup(),
    crashes: L.layerGroup(),
    mellow: L.layerGroup(),
    planned: L.layerGroup(),
  };

  let routeFeatures = [];
  let obstructionPoints = [];
  let selectedRoute = null;

  // Load data
  const [bikeRoutes, obstructionsData, mellowData, plannedData, wardsData, stations] = await Promise.all([
    BSD.loadJSON("data/bike_routes.geojson"),
    BSD.loadJSON("data/obstructions_mock.geojson"),
    BSD.loadJSON("data/mellow_routes.geojson"),
    BSD.loadJSON("data/planned_routes.geojson"),
    BSD.loadJSON("data/wards.geojson"),
    BSD.loadJSON("data/intersections.json"),
  ]);

  routeFeatures = bikeRoutes.features;
  obstructionPoints = obstructionsData.features;

  // Count obstructions per route segment and group segments into corridors —
  // pure helpers live in network-model.js so Task 3's overlays can reuse them.
  const obstructionCounts = BSDNet.countObstructions(routeFeatures, obstructionPoints);
  const corridorGroups = BSDNet.groupByCorridor(routeFeatures);

  // Ward boundaries: a faint, always-on city anchor beneath the network —
  // context only, not a data layer with its own toggle or tier badge.
  L.geoJSON(wardsData, { style: { color: "#e2e8f0", weight: 1, fill: false } }).addTo(map);

  // Draw metro lines: white casing underneath, colored line on top, so
  // overlapping routes read as distinct "lines" like a transit diagram.
  routeFeatures.forEach((feature) => {
    const latlngs = BSDNet.toLatLngs(feature.geometry);
    const casing = L.polyline(latlngs, {
      weight: 10, color: "#ffffff", opacity: 1, lineCap: "round", lineJoin: "round",
    });
    layers.casing.addLayer(casing);

    const props = feature.properties;
    const color = BSD.FACILITY_COLORS[props.facility_category] || BSD.FACILITY_COLORS.other;
    const line = L.polyline(latlngs, {
      color, weight: 7, lineCap: "round", lineJoin: "round", opacity: 1,
    });
    line.on("click", () => showDetail(feature));
    line.feature = feature;
    layers.infrastructure.addLayer(line);
  });

  // Draw station markers (crash hotspot clusters from data/intersections.json).
  stations.forEach((s) => {
    const marker = L.circleMarker([s.lat, s.lng], {
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
    layers.stations.addLayer(marker);
  });

  // Draw corridor labels: one permanent tooltip per street, positioned at
  // the midpoint of that corridor's longest segment.
  corridorGroups.forEach((feats, street) => {
    const longest = feats.reduce((best, f) =>
      (f.properties.length_m || 0) > (best.properties.length_m || 0) ? f : best
    );
    const coords = BSDNet.flattenCoords(longest.geometry);
    const mid = coords[Math.floor(coords.length / 2)];
    const tooltip = L.tooltip({ permanent: true, direction: "center", className: "line-label" })
      .setLatLng([mid[1], mid[0]])
      .setContent(BSD.esc(street));
    layers.labels.addLayer(tooltip);
  });

  // Draw obstruction overlay (dashed lines on segments with count >= 3)
  routeFeatures.forEach((feature) => {
    const count = obstructionCounts.get(feature.properties.segment_id);
    if (count >= 3) {
      const dashed = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        { color: "#000", weight: 2.5, dashArray: "4,7", opacity: 0.6 }
      );
      layers.obstructions.addLayer(dashed);
    }
  });

  // Draw crash severity overlay
  routeFeatures.forEach((feature) => {
    const crashes = feature.properties.crashes_within_30m;
    if (crashes >= 5) {
      const coords = BSDNet.flattenCoords(feature.geometry);
      const mid = coords[Math.floor(coords.length / 2)];
      const marker = L.circleMarker([mid[1], mid[0]], {
        radius: Math.min(crashes / 2, 15),
        color: "#dc2626",
        fillOpacity: 0.5,
        weight: 0,
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
    const mellowRenderer = L.canvas();
    mellowData.features.forEach((feature) => {
      const line = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        { color: "#ec4899", weight: 2, opacity: 0.6, renderer: mellowRenderer }
      );
      layers.mellow.addLayer(line);
    });
  }

  // Planned overlay (stub)
  if (plannedData.features.length === 0) {
    const noDataMarker = L.marker([41.8781, -87.6298], { opacity: 0 });
    noDataMarker._plannedStub = true;
    layers.planned.addLayer(noDataMarker);
  } else {
    plannedData.features.forEach((feature) => {
      const line = L.polyline(
        BSDNet.toLatLngs(feature.geometry),
        { color: "#8b5cf6", weight: 3, opacity: 0.7 }
      );
      layers.planned.addLayer(line);
    });
  }

  // Add always-on layers to map (casing beneath colored lines)
  layers.casing.addTo(map);
  layers.infrastructure.addTo(map);
  layers.obstructions.addTo(map);

  let stationsEnabled = true;

  // Zoom-dependent declutter: station markers+labels and corridor labels
  // are dense at city scale, so they're only shown once zoomed in enough
  // to read them. Simplest compliant approach: add/remove the whole group.
  function updateDeclutter() {
    const z = map.getZoom();
    if (stationsEnabled && z >= STATION_MIN_ZOOM) {
      if (!map.hasLayer(layers.stations)) layers.stations.addTo(map);
    } else if (map.hasLayer(layers.stations)) {
      map.removeLayer(layers.stations);
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
    map.fitBounds(allBounds, { padding: [50, 50] });
  }
  updateDeclutter();

  // Build side panel
  const side = document.getElementById("side");
  side.innerHTML = `
    <div>
      <h2>Bikeway network</h2>
      <p class="muted">Route-planning view: pick streets with real infrastructure, see where lanes get blocked, and what's being built next. For why a street is dangerous, see the <a href="index.html">Map</a>.</p>

      <div class="layer-control">
        <div class="filter-row">
          <input type="checkbox" id="infra-toggle" checked disabled>
          <label for="infra-toggle">Infrastructure ${BSD.badgeHTML("real")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="station-toggle" checked>
          <label for="station-toggle">Crash hotspots (stations) ${BSD.badgeHTML("real")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="obstruct-toggle" checked>
          <label for="obstruct-toggle">Obstruction treatment ${BSD.badgeHTML("mock")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="crash-toggle">
          <label for="crash-toggle">Crash severity ${BSD.badgeHTML("real")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="mellow-toggle">
          <label for="mellow-toggle">Mellow streets ${BSD.badgeHTML("crowdsourced")}</label>
        </div>
        <div class="filter-row">
          <input type="checkbox" id="planned-toggle">
          <label for="planned-toggle">Planned routes ${BSD.badgeHTML("stub")}</label>
        </div>
      </div>

      <p class="muted" style="font-size: 0.82em; margin: 0 0 0.6rem;">Station circle size = crashes in that intersection cluster.</p>

      <div class="legend-swatch">
        <div style="margin-bottom: 0.75rem;">
          <strong>Facility types</strong>
        </div>
  `;

  for (const [cat, label] of Object.entries(BSD.FACILITY_LABELS)) {
    const color = BSD.FACILITY_COLORS[cat];
    side.innerHTML += `
      <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.9em;">
        <div style="width: 24px; height: 3px; background: ${color};"></div>
        <span>${label}</span>
      </div>
    `;
  }

  side.innerHTML += `
      </div>
      ${BSD.noticeHTML("directional")}
      <div id="dooring-note" style="display:none">${BSD.noticeHTML("dooring")}</div>
      <div class="side-detail" id="detail"></div>
    </div>
  `;

  // Toggle handlers
  document.getElementById("station-toggle").addEventListener("change", (e) => {
    stationsEnabled = e.target.checked;
    updateDeclutter();
  });

  document.getElementById("obstruct-toggle").addEventListener("change", (e) => {
    if (e.target.checked) layers.obstructions.addTo(map);
    else map.removeLayer(layers.obstructions);
  });

  document.getElementById("crash-toggle").addEventListener("change", (e) => {
    if (e.target.checked) layers.crashes.addTo(map);
    else map.removeLayer(layers.crashes);
    // Dooring undercount disclaimer is mandatory wherever crash density shows.
    document.getElementById("dooring-note").style.display = e.target.checked ? "" : "none";
  });

  document.getElementById("mellow-toggle").addEventListener("change", (e) => {
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
  });

  document.getElementById("planned-toggle").addEventListener("change", (e) => {
    if (e.target.checked) {
      layers.planned.addTo(map);
      if (plannedData.features.length === 0) {
        showDetail({ _plannedStub: true, properties: plannedData.properties });
      }
    } else {
      map.removeLayer(layers.planned);
      if (plannedData.features.length === 0) {
        document.getElementById("detail").innerHTML = "";
      }
    }
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

    if (feature._plannedStub) {
      detail.innerHTML = `
        <div>
          <strong>Planned bikeways</strong>
          <p class="muted">${BSD.esc(feature.properties.note)}</p>
        </div>
      `;
      return;
    }

    const props = feature.properties;
    const streetLabel = props.street || "(unnamed)";
    const obCount = obstructionCounts.get(props.segment_id) || 0;

    // Corridor context: aggregate every segment sharing this street name.
    const corridorFeats = corridorGroups.get(streetLabel) || [feature];
    const corridorLength = corridorFeats.reduce((sum, f) => sum + (f.properties.length_m || 0), 0);
    const corridorCrashes = corridorFeats.reduce((sum, f) => sum + (f.properties.crashes_within_30m || 0), 0);

    const corridor = encodeURIComponent(props.street);
    const link = `index.html?layers=crashes,infrastructure&corridor=${corridor}`;

    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(streetLabel)}</strong>
        <dl>
          <dt>Facility type</dt>
          <dd>${BSD.esc(BSD.FACILITY_LABELS[props.facility_category] || props.facility_type_raw)}</dd>

          <dt>Segment length</dt>
          <dd>${BSD.fmt(Math.round(props.length_m))} m</dd>

          <dt>Segment crashes within 30m</dt>
          <dd>${BSD.fmt(props.crashes_within_30m)}</dd>

          <dt>Obstruction count</dt>
          <dd>${BSD.fmt(obCount)} ${BSD.badgeHTML("mock")}</dd>

          <dt>Corridor total length</dt>
          <dd>${BSD.fmt(Math.round(corridorLength))} m across ${corridorFeats.length} segment${corridorFeats.length === 1 ? "" : "s"}</dd>

          <dt>Corridor crashes within 30m</dt>
          <dd>${BSD.fmt(corridorCrashes)}</dd>

          <dt></dt>
          <dd><a href="${link}">Density view →</a></dd>
        </dl>
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
})();
