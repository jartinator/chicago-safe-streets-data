(async function () {
  BSD.initPage("network.html");

  const map = L.map("map", {
    attributionControl: false,
    zoom: 11,
    center: [41.8781, -87.6298],
  });

  const layers = {
    infrastructure: L.layerGroup(),
    obstructions: L.layerGroup(),
    crashes: L.layerGroup(),
    mellow: L.layerGroup(),
    planned: L.layerGroup(),
  };

  let routeFeatures = [];
  let obstructionPoints = [];
  let selectedRoute = null;
  const obstructionCounts = new Map();

  // Load data
  const [bikeRoutes, obstructionsData, mellowData, plannedData] = await Promise.all([
    BSD.loadJSON("data/bike_routes.geojson"),
    BSD.loadJSON("data/obstructions_mock.geojson"),
    BSD.loadJSON("data/mellow_routes.geojson"),
    BSD.loadJSON("data/planned_routes.geojson"),
  ]);

  routeFeatures = bikeRoutes.features;
  obstructionPoints = obstructionsData.features;

  // Helper: calculate padded bbox
  function getPaddedBBox(lineString, pad = 0.0006) {
    let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;
    for (const [lng, lat] of lineString.coordinates) {
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

  // Helper: point in bbox
  function pointInBBox(point, bbox) {
    const [lng, lat] = point.geometry.coordinates;
    return lat >= bbox[0][0] && lat <= bbox[1][0] &&
           lng >= bbox[0][1] && lng <= bbox[1][1];
  }

  // Count obstructions per route segment
  routeFeatures.forEach((feature) => {
    const bbox = getPaddedBBox(feature.geometry);
    const count = obstructionPoints.filter(p => pointInBBox(p, bbox)).length;
    obstructionCounts.set(feature.properties.segment_id, count);
  });

  // Draw infrastructure layer
  routeFeatures.forEach((feature) => {
    const props = feature.properties;
    const color = BSD.FACILITY_COLORS[props.facility_category] || BSD.FACILITY_COLORS.other;
    const line = L.polyline(
      feature.geometry.coordinates.map(([lng, lat]) => [lat, lng]),
      { color, weight: 6, lineCap: "round", opacity: 0.9 }
    );

    line.on("click", () => showDetail(feature));
    layers.infrastructure.addLayer(line);
    line.feature = feature;
  });

  // Draw obstruction overlay (dashed lines on segments with count >= 3)
  routeFeatures.forEach((feature) => {
    const count = obstructionCounts.get(feature.properties.segment_id);
    if (count >= 3) {
      const dashed = L.polyline(
        feature.geometry.coordinates.map(([lng, lat]) => [lat, lng]),
        { color: "#000", weight: 2.5, dashArray: "4,7", opacity: 0.6 }
      );
      layers.obstructions.addLayer(dashed);
    }
  });

  // Draw crash severity overlay
  routeFeatures.forEach((feature) => {
    const crashes = feature.properties.crashes_within_30m;
    if (crashes >= 5) {
      const coords = feature.geometry.coordinates;
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

  // Mellow overlay: geometry is MultiLineString (one feature per route_type,
  // thousands of parts each) — Leaflet draws a nested coordinate array as one
  // multi-part polyline, so convert without flattening.
  function toLatLngs(geometry) {
    if (geometry.type === "MultiLineString") {
      return geometry.coordinates.map((part) => part.map(([lng, lat]) => [lat, lng]));
    }
    return geometry.coordinates.map(([lng, lat]) => [lat, lng]);
  }

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
        toLatLngs(feature.geometry),
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
        feature.geometry.coordinates.map(([lng, lat]) => [lat, lng]),
        { color: "#8b5cf6", weight: 3, opacity: 0.7 }
      );
      layers.planned.addLayer(line);
    });
  }

  // Add all layers to map
  layers.infrastructure.addTo(map);
  layers.obstructions.addTo(map);

  // Fit bounds to bike network
  if (routeFeatures.length > 0) {
    const allBounds = routeFeatures.map(f => {
      const bbox = getPaddedBBox(f.geometry);
      return bbox;
    }).reduce((acc, bbox) => {
      if (acc.length === 0) return bbox;
      return [
        [Math.min(acc[0][0], bbox[0][0]), Math.min(acc[0][1], bbox[0][1])],
        [Math.max(acc[1][0], bbox[1][0]), Math.max(acc[1][1], bbox[1][1])],
      ];
    }, []);
    map.fitBounds(allBounds, { padding: [50, 50] });
  }

  // Build side panel
  const side = document.getElementById("side");
  side.innerHTML = `
    <div>
      <h2>Bikeway network</h2>
      <p>How do I get across town on safe infrastructure?</p>

      <div class="layer-control">
        <div class="filter-row">
          <input type="checkbox" id="infra-toggle" checked disabled>
          <label for="infra-toggle">Infrastructure ${BSD.badgeHTML("real")}</label>
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
    const obCount = obstructionCounts.get(props.segment_id) || 0;
    const corridor = encodeURIComponent(props.street);
    const link = `index.html?layers=crashes,infrastructure&corridor=${corridor}`;

    detail.innerHTML = `
      <div>
        <strong>${BSD.esc(props.street)}</strong>
        <dl>
          <dt>Facility type</dt>
          <dd>${BSD.esc(BSD.FACILITY_LABELS[props.facility_category] || props.facility_type_raw)}</dd>

          <dt>Length</dt>
          <dd>${BSD.fmt(Math.round(props.length_m))} m</dd>

          <dt>Crashes within 30m</dt>
          <dd>${BSD.fmt(props.crashes_within_30m)}</dd>

          <dt>Obstruction count</dt>
          <dd>${BSD.fmt(obCount)} ${BSD.badgeHTML("mock")}</dd>

          <dt></dt>
          <dd><a href="${link}">Density view →</a></dd>
        </dl>
      </div>
    `;

    selectedRoute = feature;
  }
})();
