/* Screen 1: primary geographic map — density exploration with toggleable,
 * quality-badged overlays and ward -> corridor -> intersection drill-down.
 * URL state: ?layers=crashes,infrastructure&ward=1&corridor=MILWAUKEE%20AVE
 *            &sev=incapacitating&from=2023-01-01&to=2026-01-01&dooring=1 */
(function () {
  const B = window.BSD;
  B.initPage("index.html");

  const map = L.map("map", { zoomSnap: 0.5 }).setView([41.87, -87.66], 11);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: "abcd", maxZoom: 19,
  }).addTo(map);

  const side = document.getElementById("side");
  const state = {
    layers: new Set((B.qs().get("layers") || "crashes,infrastructure").split(",").filter(Boolean)),
    sev: B.qs().get("sev") || "",
    from: B.qs().get("from") || "",
    to: B.qs().get("to") || "",
    dooring: B.qs().get("dooring") === "1",
    ward: B.qs().get("ward") || "",
    corridor: B.qs().get("corridor") || "",
  };

  const LAYERS = [
    { id: "crashes", label: "Cyclist crashes", tier: "real" },
    { id: "obstructions", label: "Obstructions", tier: "mock" },
    { id: "infrastructure", label: "Bike infrastructure", tier: "real" },
    { id: "planned", label: "Planned routes", tier: "stub" },
    { id: "cameras", label: "Camera violations", tier: "proxy" },
    { id: "wards", label: "Ward boundaries", tier: "real" },
  ];

  const data = {};
  const groups = {};
  let corridorHighlight = null;

  Promise.all([
    B.loadJSON("data/crashes_cyclist.geojson"),
    B.loadJSON("data/obstructions_mock.geojson").catch(() => ({ features: [] })),
    B.loadJSON("data/bike_routes.geojson"),
    B.loadJSON("data/planned_routes.geojson"),
    B.loadJSON("data/cameras.json"),
    B.loadJSON("data/wards.geojson"),
    B.loadJSON("data/corridors.json"),
    B.loadJSON("data/intersections.json"),
    B.loadJSON("data/aldermen.json").catch(() => ({ wards: [] })),
  ]).then(([crashes, obstructions, routes, planned, cameras, wards, corridors, intersections, aldermen]) => {
    Object.assign(data, { crashes, obstructions, routes, planned, cameras, wards, corridors, intersections });
    data.aldermanByWard = {};
    (aldermen.wards || []).forEach(w => { data.aldermanByWard[w.ward] = w; });
    buildLayers();
    renderSide();
    syncLayers();
    // showWard() clears state.corridor as a side effect, so capture the
    // URL's initial corridor before it and re-apply it after.
    const initialCorridor = state.corridor;
    if (state.ward) showWard(state.ward, false);
    if (initialCorridor) showCorridor(initialCorridor, false);
  }).catch(err => {
    side.innerHTML = `<div class="notice">Failed to load data: ${B.esc(err.message)}</div>`;
  });

  function crashVisible(p) {
    if (state.dooring && !p.dooring) return false;
    if (state.sev && p.injury_severity !== state.sev) return false;
    const d = (p.date || "").slice(0, 10);
    if (state.from && d < state.from) return false;
    if (state.to && d > state.to) return false;
    return true;
  }

  function buildLayers() {
    groups.crashes = L.layerGroup(data.crashes.features.filter(f => crashVisible(f.properties)).map(f => {
      const p = f.properties;
      const [lng, lat] = f.geometry.coordinates;
      return L.circleMarker([lat, lng], {
        radius: p.injury_severity === "fatal" ? 7 : p.injury_severity === "incapacitating" ? 5 : 3.5,
        color: B.SEVERITY_COLORS[p.injury_severity] || "#94a3b8",
        weight: 1, fillOpacity: 0.55,
      }).on("click", () => showCrash(p));
    }));

    groups.obstructions = L.layerGroup((data.obstructions.features || []).map(f => {
      const p = f.properties;
      const [lng, lat] = f.geometry.coordinates;
      return L.circleMarker([lat, lng], {
        radius: 4, color: "#b91c1c", weight: 1, dashArray: "2,2", fillOpacity: 0.35,
      }).on("click", () => showObstruction(p));
    }));

    groups.infrastructure = L.layerGroup(data.routes.features.map(f => {
      const p = f.properties;
      const line = L.geoJSON(f, {
        style: { color: B.FACILITY_COLORS[p.facility_category] || "#64748b", weight: 3.5, opacity: 0.85 },
      }).on("click", () => showSegment(p));
      return line;
    }));

    groups.planned = L.layerGroup(data.planned.features.map(f =>
      L.geoJSON(f, { style: { color: "#64748b", weight: 3, dashArray: "6,6" } })));

    groups.cameras = L.layerGroup((data.cameras.cameras || []).filter(c => c.lat && c.lng).map(c =>
      L.circleMarker([c.lat, c.lng], {
        radius: Math.max(4, Math.min(11, Math.sqrt((c.violations_total || 0) / 400))),
        color: "#b45309", weight: 1.5, fillOpacity: 0.25,
      }).on("click", () => showCamera(c))));

    groups.wards = L.layerGroup(data.wards.features.map(f => {
      const p = f.properties;
      const fill = { low: "#e2e8f0", medium: "#f8c471", high: "#e26855" }[p.density_band] || "#e2e8f0";
      return L.geoJSON(f, {
        style: { color: "#475569", weight: 1, fillColor: fill, fillOpacity: 0.18 },
      }).on("click", () => showWard(p.ward, true));
    }));
  }

  function rebuildCrashes() {
    const had = map.hasLayer(groups.crashes);
    if (had) map.removeLayer(groups.crashes);
    groups.crashes = L.layerGroup(data.crashes.features.filter(f => crashVisible(f.properties)).map(f => {
      const p = f.properties;
      const [lng, lat] = f.geometry.coordinates;
      return L.circleMarker([lat, lng], {
        radius: p.injury_severity === "fatal" ? 7 : p.injury_severity === "incapacitating" ? 5 : 3.5,
        color: B.SEVERITY_COLORS[p.injury_severity] || "#94a3b8",
        weight: 1, fillOpacity: 0.55,
      }).on("click", () => showCrash(p));
    }));
    if (had) groups.crashes.addTo(map);
  }

  function syncLayers() {
    for (const { id } of LAYERS) {
      if (state.layers.has(id)) { if (!map.hasLayer(groups[id])) groups[id].addTo(map); }
      else if (map.hasLayer(groups[id])) map.removeLayer(groups[id]);
    }
    B.setParams({
      layers: [...state.layers].join(","), sev: state.sev, from: state.from,
      to: state.to, dooring: state.dooring, ward: state.ward, corridor: state.corridor,
    });
  }

  /* ---------- side panel ---------- */

  function renderSide(detailHTML) {
    const layerRows = LAYERS.map(l => `
      <label><input type="checkbox" data-layer="${l.id}" ${state.layers.has(l.id) ? "checked" : ""}>
        ${l.label} ${B.badgeHTML(l.tier)}</label>`).join("");
    const sevOpts = ['<option value="">All severities</option>']
      .concat(B.SEVERITY_ORDER.map(s =>
        `<option value="${s}" ${state.sev === s ? "selected" : ""}>${B.SEVERITY_LABELS[s]}</option>`)).join("");
    const legend = Object.entries(B.FACILITY_COLORS).map(([k, c]) =>
      `<span style="white-space:nowrap"><span class="legend-swatch" style="background:${c}"></span> ${B.FACILITY_LABELS[k]}</span>`
    ).join(" &nbsp; ");

    side.innerHTML = `
      <h2>Layers</h2>
      <div class="layer-control">${layerRows}</div>
      <div class="filter-row">
        <select id="sev">${sevOpts}</select>
        <label style="display:inline-flex;gap:0.3rem;align-items:center">
          <input type="checkbox" id="dooring" ${state.dooring ? "checked" : ""}> dooring only</label>
      </div>
      <div class="filter-row">
        <input type="date" id="from" value="${B.esc(state.from)}" title="from">
        <input type="date" id="to" value="${B.esc(state.to)}" title="to">
      </div>
      <div class="filter-row">
        <input type="search" id="wardSearch" placeholder="Ward # (what ward am I in? click map)" style="flex:1">
        <button id="wardGo">Go</button>
      </div>
      <div class="muted" style="margin:0.4rem 0">${legend}</div>
      ${state.layers.has("crashes") ? B.noticeHTML("dooring") : ""}
      ${B.noticeHTML("directional")}
      <div class="side-detail" id="detail">${detailHTML || '<p class="muted">Click a crash, segment, ward, or camera for detail. Search a ward number to drill down: ward → corridor → intersection.</p>'}</div>`;

    side.querySelectorAll("[data-layer]").forEach(cb => cb.addEventListener("change", () => {
      cb.checked ? state.layers.add(cb.dataset.layer) : state.layers.delete(cb.dataset.layer);
      if (cb.dataset.layer === "planned" && cb.checked) {
        setDetail(`<h3>Planned routes ${B.badgeHTML("stub")}</h3><p class="muted">${B.esc(data.planned.properties?.note || "No data yet.")}</p>`);
      }
      renderSide(document.getElementById("detail").innerHTML);
      syncLayers();
    }));
    side.querySelector("#sev").addEventListener("change", e => { state.sev = e.target.value; rebuildCrashes(); syncLayers(); });
    side.querySelector("#dooring").addEventListener("change", e => { state.dooring = e.target.checked; rebuildCrashes(); syncLayers(); });
    side.querySelector("#from").addEventListener("change", e => { state.from = e.target.value; rebuildCrashes(); syncLayers(); });
    side.querySelector("#to").addEventListener("change", e => { state.to = e.target.value; rebuildCrashes(); syncLayers(); });
    const go = () => { const v = side.querySelector("#wardSearch").value.trim(); if (v) showWard(v, true); };
    side.querySelector("#wardGo").addEventListener("click", go);
    side.querySelector("#wardSearch").addEventListener("keydown", e => { if (e.key === "Enter") go(); });
  }

  function setDetail(html) {
    const d = document.getElementById("detail");
    if (d) d.innerHTML = html;
  }

  /* ---------- drill-down: ward -> corridor -> intersection ---------- */

  function wardFeature(w) {
    return data.wards.features.find(f => String(f.properties.ward) === String(w));
  }

  function bboxOf(geom) {
    let minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
    const scan = c => {
      if (typeof c[0] === "number") {
        minX = Math.min(minX, c[0]); maxX = Math.max(maxX, c[0]);
        minY = Math.min(minY, c[1]); maxY = Math.max(maxY, c[1]);
      } else c.forEach(scan);
    };
    scan(geom.coordinates);
    return [minX, minY, maxX, maxY];
  }
  const inBbox = (lng, lat, b) => lng >= b[0] && lng <= b[2] && lat >= b[1] && lat <= b[3];

  function showWard(w, zoom) {
    const f = wardFeature(w);
    if (!f) { setDetail(`<p class="muted">No ward “${B.esc(w)}” found (1–50).</p>`); return; }
    state.ward = String(w); state.corridor = "";
    const p = f.properties;
    const b = bboxOf(f.geometry);
    if (zoom) map.fitBounds([[b[1], b[0]], [b[3], b[2]]]);

    const streets = {};
    data.routes.features.forEach(rf => {
      const [minX, minY, maxX, maxY] = bboxOf(rf.geometry);
      if (maxX < b[0] || minX > b[2] || maxY < b[1] || minY > b[3]) return;
      const s = rf.properties.street || "(unnamed)";
      (streets[s] = streets[s] || { crashes: 0, length: 0 });
      streets[s].crashes += rf.properties.crashes_within_30m;
      streets[s].length += rf.properties.length_m;
    });
    const top = Object.entries(streets).sort((a, z) => z[1].crashes - a[1].crashes).slice(0, 6);
    const ald = data.aldermanByWard[String(w)] || {};
    setDetail(`
      <h3>Ward ${B.esc(w)} ${B.badgeHTML("real")}</h3>
      <dl>
        <dt>Cyclist crashes</dt><dd>${B.fmt(p.cyclist_crashes)} (${B.esc(p.density_band)} band)</dd>
        <dt>Injury crashes / fatal</dt><dd>${B.fmt(p.injuries)} / ${B.fmt(p.fatalities)}</dd>
        <dt>311 bike complaints ${B.badgeHTML("proxy")}</dt><dd>${B.fmt(p.complaints_311)}</dd>
        <dt>Alderman</dt><dd>${B.esc(ald.alderman || "—")} — <a href="${B.LINKS.aldermanLookup}" target="_blank" rel="noopener">official lookup</a></dd>
      </dl>
      <h4 style="margin:0.5rem 0 0.2rem">Corridors in view</h4>
      ${top.map(([s, v]) => `<div><a href="#" data-corridor="${B.esc(s)}">${B.esc(s)}</a>
        <span class="muted">${B.fmt(v.crashes)} crashes near ${(v.length / 1000).toFixed(1)} km</span></div>`).join("") || '<p class="muted">No bikeways intersect this ward.</p>'}
      <p style="margin-top:0.6rem"><a class="btn" href="table.html?ward=${encodeURIComponent(w)}">Ward data table</a>
      <a class="btn" href="action.html?ward=${encodeURIComponent(w)}">Take action</a></p>`);
    document.querySelectorAll("[data-corridor]").forEach(a =>
      a.addEventListener("click", e => { e.preventDefault(); showCorridor(a.dataset.corridor, true); }));
    syncLayers();
  }

  function showCorridor(street, zoom) {
    state.corridor = street;
    const segs = data.routes.features.filter(f => (f.properties.street || "(unnamed)") === street);
    if (!segs.length) { setDetail(`<p class="muted">No corridor “${B.esc(street)}”.</p>`); return; }
    if (corridorHighlight) map.removeLayer(corridorHighlight);
    corridorHighlight = L.geoJSON({ type: "FeatureCollection", features: segs },
      { style: { color: "#111", weight: 8, opacity: 0.35 } }).addTo(map);
    if (zoom) map.fitBounds(corridorHighlight.getBounds().pad(0.2));
    const c = data.corridors.find(r => r.street === street) || {};
    const b = corridorHighlight.getBounds();
    const spots = data.intersections.filter(s => inBbox(s.lng, s.lat, [b.getWest(), b.getSouth(), b.getEast(), b.getNorth()])).slice(0, 5);
    setDetail(`
      <h3>${B.esc(street)} ${B.badgeHTML("real")}</h3>
      <dl>
        <dt>Crashes near bikeway</dt><dd>${B.fmt(c.crashes)}</dd>
        <dt>Crashes / km</dt><dd>${c.crashes_per_km ?? "—"}</dd>
        <dt>Facility mix (m)</dt><dd>${Object.entries(c.facility_mix || {}).map(([k, v]) => `${B.FACILITY_LABELS[k] || k}: ${B.fmt(Math.round(v))}`).join("<br>") || "—"}</dd>
      </dl>
      <h4 style="margin:0.5rem 0 0.2rem">Crash hotspots on corridor</h4>
      ${spots.map(s => `<div><a href="#" data-spot="${s.lat},${s.lng}">${B.esc(s.label)}</a> <span class="muted">${s.crashes} crashes</span></div>`).join("") || '<p class="muted">No clustered hotspots here.</p>'}
      ${B.noticeHTML("normalization")}`);
    document.querySelectorAll("[data-spot]").forEach(a => a.addEventListener("click", e => {
      e.preventDefault();
      const [lat, lng] = a.dataset.spot.split(",").map(Number);
      map.setView([lat, lng], 17);
    }));
    syncLayers();
  }

  /* ---------- feature detail views ---------- */

  function showCrash(p) {
    setDetail(`
      <h3>Crash ${B.badgeHTML("real")}</h3>
      <dl>
        <dt>Date</dt><dd>${B.esc((p.date || "").replace("T", " "))}</dd>
        <dt>Severity</dt><dd>${B.esc(B.SEVERITY_LABELS[p.injury_severity] || p.injury_severity)}</dd>
        <dt>Type</dt><dd>${B.esc(p.crash_type || "—")}${p.dooring ? " · DOORING" : ""}${p.hit_and_run ? " · hit &amp; run" : ""}</dd>
        <dt>Street</dt><dd>${B.esc(p.street || "—")}</dd>
        <dt>Ward</dt><dd>${p.ward ? `<a href="#" id="crashWard">${B.esc(p.ward)}</a>` : "—"}</dd>
        <dt>Lighting</dt><dd>${B.esc(p.lighting || "—")}</dd>
      </dl>${B.noticeHTML("dooring")}`);
    const a = document.getElementById("crashWard");
    if (a) a.addEventListener("click", e => { e.preventDefault(); showWard(p.ward, true); });
  }

  function showObstruction(p) {
    setDetail(`
      <h3>Obstruction ${B.badgeHTML("mock")}</h3>
      <div class="notice">${B.esc(B.TIER_INFO.mock)}</div>
      <dl>
        <dt>Type</dt><dd>${B.esc(p.obstruction_type)}</dd>
        <dt>When</dt><dd>${B.esc((p.occurred_at || "").replace("T", " "))}</dd>
        <dt>Photos</dt><dd>${B.fmt(p.photo_count)}</dd>
        <dt>Crash occurred</dt><dd>${p.crash_occurred ? "yes" : "no"}</dd>
      </dl>
      <p class="muted">See something real? <a href="${B.LINKS.blu}" target="_blank" rel="noopener">Report to Bike Lane Uprising</a> or <a href="${B.LINKS.threeOneOne}" target="_blank" rel="noopener">311</a>.</p>`);
  }

  function showSegment(p) {
    setDetail(`
      <h3>${B.esc(p.street || "Segment")} ${B.badgeHTML("real")}</h3>
      <dl>
        <dt>Facility</dt><dd>${B.esc(B.FACILITY_LABELS[p.facility_category] || p.facility_category)} <span class="muted">(raw: ${B.esc(p.facility_type_raw)})</span></dd>
        <dt>Length</dt><dd>${B.fmt(Math.round(p.length_m))} m</dd>
        <dt>Crashes within 30 m</dt><dd>${B.fmt(p.crashes_within_30m)}</dd>
      </dl>
      <p><a href="#" id="segCorridor">Whole corridor →</a></p>`);
    const a = document.getElementById("segCorridor");
    if (a) a.addEventListener("click", e => { e.preventDefault(); showCorridor(p.street || "(unnamed)", true); });
  }

  function showCamera(c) {
    setDetail(`
      <h3>${B.esc(c.kind === "speed" ? "Speed camera" : "Red-light camera")} ${B.badgeHTML("proxy")}</h3>
      <div class="notice">${B.esc(data.cameras.note || "")}</div>
      <dl>
        <dt>Location</dt><dd>${B.esc(c.address || "—")}</dd>
        <dt>Total violations</dt><dd>${B.fmt(c.violations_total)}</dd>
        <dt>Range</dt><dd>${B.esc(c.first_date || "?")} → ${B.esc(c.last_date || "?")}</dd>
      </dl>`);
  }

  // "What ward am I in": clicking bare map reports the containing ward.
  map.on("click", e => {
    if (!data.wards) return;
    const { lat, lng } = e.latlng;
    const hit = data.wards.features.find(f => {
      const polys = f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates;
      return polys.some(rings => pointInRing(lng, lat, rings[0]));
    });
    if (hit && !state.layers.has("wards")) showWard(hit.properties.ward, false);
  });

  function pointInRing(x, y, ring) {
    let inside = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }
})();
