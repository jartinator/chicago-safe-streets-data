/* Screen 1: primary geographic map — density exploration with toggleable,
 * quality-badged overlays and ward -> corridor -> intersection drill-down.
 * URL state: ?layers=crashes,infrastructure&ward=1&corridor=MILWAUKEE%20AVE
 *            &sev=incapacitating&from=2023-01-01&to=2026-01-01&dooring=1 */
(function () {
  const B = window.BSD;
  const BM = window.BSDMap;
  B.initPage("index.html");

  const map = L.map("map", { zoomSnap: 0.5 }).setView([41.87, -87.66], 11);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: "abcd", maxZoom: 19,
  }).addTo(map);

  // Zoom-adaptive density rendering: below DETAIL_ZOOM, crashes/obstructions
  // render as tight, route-hugging density dots (small ~100m cells, capped
  // radii) instead of thousands of individual markers merging into a blob.
  // Purely zoom-derived — no URL/state changes. Cameras and wards untouched.
  const DETAIL_ZOOM = 14;
  const densityCanvas = L.canvas();

  const side = document.getElementById("side");
  const state = {
    layers: new Set((B.qs().get("layers") || "crashes,infrastructure").split(",").filter(Boolean)),
    sev: B.qs().get("sev") || "",
    from: B.qs().get("from") || "",
    to: B.qs().get("to") || "",
    dooring: B.qs().get("dooring") === "1",
    ward: B.qs().get("ward") || "",
    corridor: B.qs().get("corridor") || "",
    shade: B.qs().get("shade") || "density",
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
    B.loadJSON("data/ward_safety_index.json").catch(() => ({ wards: [] })),
    B.loadJSON("data/menu_spending.json").catch(() => ({ wards: {} })),
  ]).then(([crashes, obstructions, routes, planned, cameras, wards, corridors, intersections, aldermen, safety, menu]) => {
    Object.assign(data, { crashes, obstructions, routes, planned, cameras, wards, corridors, intersections });
    data.aldermanByWard = {};
    (aldermen.wards || []).forEach(w => { data.aldermanByWard[w.ward] = w; });
    // safetyByWard/safetyRank: rank is 1-based array order since the file is
    // sorted by comparable_danger_score desc.
    data.safetyByWard = {};
    data.safetyRank = {};
    (safety.wards || []).forEach((w, i) => {
      data.safetyByWard[String(w.ward)] = w;
      data.safetyRank[String(w.ward)] = i + 1;
    });
    data.safetyCount = (safety.wards || []).length;
    data.safetyNote = safety.note || "";
    data.menuByWard = menu.wards || {};
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

  // Individual crash markers for the filtered set. Shared by buildLayers()
  // (initial load) and rebuildCrashes() (filter changes) so both stay in
  // sync with severity/date/dooring styling.
  function buildCrashGroup(filtered) {
    return L.layerGroup(filtered.map(f => {
      const p = f.properties;
      const [lng, lat] = f.geometry.coordinates;
      return L.circleMarker([lat, lng], {
        radius: p.injury_severity === "fatal" ? 7 : p.injury_severity === "incapacitating" ? 5 : 3.5,
        color: B.SEVERITY_COLORS[p.injury_severity] || "#94a3b8",
        weight: 1, fillOpacity: 0.55,
      }).on("click", () => showCrash(p));
    }));
  }

  // Density-mode layer group: grid-bin the given Point features via
  // BSDMap.binPoints and render one small, capped-radius dot per cell on
  // the shared canvas renderer. Clicking a cell "resolves into detail" by
  // zooming to DETAIL_ZOOM at the cell center.
  function buildDensityGroup(features, rampKey) {
    const bins = BM.binPoints(features);
    const maxCount = bins.reduce((m, b) => Math.max(m, b.count), 0);
    const ramp = BM.DENSITY_RAMPS[rampKey];
    return L.layerGroup(bins.map(b => {
      const color = BM.rampColor(b.count, maxCount, ramp);
      return L.circleMarker([b.lat, b.lng], {
        renderer: densityCanvas,
        radius: BM.densityRadius(b.count),
        color, weight: 0, fillColor: color, fillOpacity: 0.55,
      }).on("click", () => map.setView([b.lat, b.lng], DETAIL_ZOOM));
    }));
  }

  function buildLayers() {
    const filteredCrashes = data.crashes.features.filter(f => crashVisible(f.properties));
    groups.crashes = buildCrashGroup(filteredCrashes);
    groups.crashesDensity = buildDensityGroup(filteredCrashes, "crashes");

    groups.obstructions = L.layerGroup((data.obstructions.features || []).map(f => {
      const p = f.properties;
      const [lng, lat] = f.geometry.coordinates;
      return L.circleMarker([lat, lng], {
        radius: 4, color: "#b91c1c", weight: 1, dashArray: "2,2", fillOpacity: 0.35,
      }).on("click", () => showObstruction(p));
    }));
    groups.obstructionsDensity = buildDensityGroup(data.obstructions.features || [], "obstructions");

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

    groups.wards = buildWardsGroup();
  }

  // Ward fill depends on state.shade: "density" (real, current default) uses
  // the wards.geojson density_band; "danger" (derived) uses the comparable
  // danger score from ward_safety_index.json, null-safe via B.scoreColor.
  function wardFill(p) {
    if (state.shade === "danger") {
      const s = data.safetyByWard[String(p.ward)];
      const score = s ? s.comparable_danger_score : null;
      return { fillColor: B.scoreColor(score), fillOpacity: 0.35 };
    }
    const fill = { low: "#e2e8f0", medium: "#f8c471", high: "#e26855" }[p.density_band] || "#e2e8f0";
    return { fillColor: fill, fillOpacity: 0.18 };
  }

  function buildWardsGroup() {
    return L.layerGroup(data.wards.features.map(f => {
      const p = f.properties;
      const { fillColor, fillOpacity } = wardFill(p);
      return L.geoJSON(f, {
        style: { color: "#475569", weight: 1, fillColor, fillOpacity },
      }).on("click", () => showWard(p.ward, true));
    }));
  }

  function rebuildWards() {
    const had = map.hasLayer(groups.wards);
    if (had) map.removeLayer(groups.wards);
    groups.wards = buildWardsGroup();
    if (had) groups.wards.addTo(map);
  }

  // Extended to also rebuild the crash density group from the same filtered
  // set, so density mode respects severity/date/dooring filters exactly
  // like the individual-marker mode does. Which group (if either) is
  // re-added to the map is decided by the syncDensityMode() call that every
  // caller of rebuildCrashes() makes via syncLayers() immediately after.
  function rebuildCrashes() {
    if (map.hasLayer(groups.crashes)) map.removeLayer(groups.crashes);
    if (map.hasLayer(groups.crashesDensity)) map.removeLayer(groups.crashesDensity);
    const filtered = data.crashes.features.filter(f => crashVisible(f.properties));
    groups.crashes = buildCrashGroup(filtered);
    groups.crashesDensity = buildDensityGroup(filtered, "crashes");
  }

  // True when the map is zoomed out past DETAIL_ZOOM and crash/obstruction
  // layers should render as density dots instead of individual markers.
  function isDensityMode() {
    return map.getZoom() < DETAIL_ZOOM;
  }

  // Decides, per layer, whether the individual-marker group or the
  // density group is on the map — honoring state.layers (on/off) and the
  // current zoom (density vs. detail). Called from syncLayers() (layer
  // toggles, filter changes, shade changes) and on map "zoomend".
  function syncDensityMode() {
    // Guard against zoomend firing before the initial data load builds
    // groups (e.g. a scroll-wheel zoom while the map is still loading).
    if (!groups.crashes) return;
    const density = isDensityMode();
    [["crashes", groups.crashes, groups.crashesDensity],
     ["obstructions", groups.obstructions, groups.obstructionsDensity]].forEach(([id, individual, densityGroup]) => {
      const show = state.layers.has(id) ? (density ? densityGroup : individual) : null;
      [individual, densityGroup].forEach(g => {
        if (g !== show && map.hasLayer(g)) map.removeLayer(g);
      });
      if (show && !map.hasLayer(show)) show.addTo(map);
    });
    updateDensityHint();
  }

  // Muted hint shown under the layer control while in density mode with
  // either crashes or obstructions on. Toggles an existing DOM node
  // in-place (called from syncDensityMode on zoomend, no side-panel
  // rebuild needed) and is also invoked at the end of renderSide() so a
  // freshly-rendered panel starts in the correct state regardless of
  // whether renderSide() or syncLayers() ran first.
  function updateDensityHint() {
    const hint = document.getElementById("densityHint");
    if (!hint) return;
    const show = isDensityMode() && (state.layers.has("crashes") || state.layers.has("obstructions"));
    hint.style.display = show ? "" : "none";
  }

  function syncLayers() {
    for (const { id } of LAYERS) {
      if (id === "crashes" || id === "obstructions") continue; // handled by syncDensityMode()
      if (state.layers.has(id)) { if (!map.hasLayer(groups[id])) groups[id].addTo(map); }
      else if (map.hasLayer(groups[id])) map.removeLayer(groups[id]);
    }
    syncDensityMode();
    B.setParams({
      layers: [...state.layers].join(","), sev: state.sev, from: state.from,
      to: state.to, dooring: state.dooring, ward: state.ward, corridor: state.corridor,
      shade: state.shade,
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
    // The last bucket carries two swatches: tan for a real sub-20 score and
    // gray for a ward with no score at all — both fills appear on the map,
    // so both belong in the legend.
    const shadeLegend = state.shade === "danger" ? `
      <div class="muted" style="margin:0.4rem 0" title="${B.esc(data.safetyNote || "")}">
        <strong>Danger score ${B.badgeHTML("derived")}</strong><br>
        ${[[[B.scoreColor(85)], "80+"], [[B.scoreColor(65)], "60+"], [[B.scoreColor(45)], "40+"],
           [[B.scoreColor(25)], "20+"], [[B.scoreColor(10), B.scoreColor(null)], "<20 / no data"]].map(([colors, label]) =>
          `<span style="white-space:nowrap">${colors.map(c =>
            `<span class="legend-swatch" style="background:${c}"></span>`).join("")} ${B.esc(label)}</span>`
        ).join(" &nbsp; ")}
      </div>` : "";

    side.innerHTML = `
      <h2>Infrastructure × policy × outcomes</h2>
      <p class="muted">Where crashes, bike infrastructure, and ward-level policy overlap. Click a ward or corridor to dig in.</p>
      <div class="layer-control">${layerRows}</div>
      <div class="muted" id="densityHint" style="margin:0.4rem 0;display:none">Zoomed out: dots show density per ~100 m cell. Zoom in (or click a cell) to see individual, clickable records.</div>
      <div class="filter-row">
        <label style="display:inline-flex;gap:0.3rem;align-items:center">Ward shading:
          <select id="shade">
            <option value="density" ${state.shade === "density" ? "selected" : ""}>Crash density (real)</option>
            <option value="danger" ${state.shade === "danger" ? "selected" : ""}>Danger score (derived)</option>
          </select>
        </label>
      </div>
      ${shadeLegend}
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
    side.querySelector("#shade").addEventListener("change", e => {
      state.shade = e.target.value;
      rebuildWards();
      syncLayers();
      renderSide(document.getElementById("detail").innerHTML);
    });
    side.querySelector("#sev").addEventListener("change", e => { state.sev = e.target.value; rebuildCrashes(); syncLayers(); });
    side.querySelector("#dooring").addEventListener("change", e => { state.dooring = e.target.checked; rebuildCrashes(); syncLayers(); });
    side.querySelector("#from").addEventListener("change", e => { state.from = e.target.value; rebuildCrashes(); syncLayers(); });
    side.querySelector("#to").addEventListener("change", e => { state.to = e.target.value; rebuildCrashes(); syncLayers(); });
    const go = () => { const v = side.querySelector("#wardSearch").value.trim(); if (v) showWard(v, true); };
    side.querySelector("#wardGo").addEventListener("click", go);
    side.querySelector("#wardSearch").addEventListener("keydown", e => { if (e.key === "Enter") go(); });
    // Self-healing: whichever order renderSide()/syncLayers() ran in, the
    // freshly-created #densityHint node ends up in the correct state.
    updateDensityHint();
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

    // Ward accountability rows: danger score/rank, crash trend, bikeway
    // miles, menu spending — all sourced from ward_safety_index.json and
    // menu_spending.json, both of which are allowed to fail to load or omit
    // this ward, so every field below is null-safe.
    const s = data.safetyByWard[String(w)];
    const rank = s ? data.safetyRank[String(w)] : null;
    const score = s ? s.comparable_danger_score : null;
    const scoreRow = score == null ? "—" : `${score} / 100 — rank ${rank} of ${data.safetyCount} wards`;
    const trendRow = s && s.crash_trend ? B.trendHTML(s.crash_trend) : "—";
    const bikewayMilesRow = s && s.bikeway_miles != null ? B.esc(String(s.bikeway_miles)) : "—";
    const m = data.menuByWard[String(w)];
    const menuRow = m ? `${B.money(m.bike_safety_spent)} of ${B.money(m.total_spent)}` : "no data this run";

    setDetail(`
      <h3>Ward ${B.esc(w)} ${B.badgeHTML("real")}</h3>
      <dl>
        <dt>Cyclist crashes</dt><dd>${B.fmt(p.cyclist_crashes)} (${B.esc(p.density_band)} band)</dd>
        <dt>Injury crashes / fatal</dt><dd>${B.fmt(p.injuries)} / ${B.fmt(p.fatalities)}</dd>
        <dt>311 bike complaints ${B.badgeHTML("proxy")}</dt><dd>${B.fmt(p.complaints_311)}</dd>
        <dt>Alderman</dt><dd>${B.esc(ald.alderman || "—")} — <a href="${B.LINKS.aldermanLookup}" target="_blank" rel="noopener">official lookup</a></dd>
        <dt>Danger score ${B.badgeHTML("derived")}</dt>
        <dd>${scoreRow}</dd>
        <dt>Crash trend ${B.badgeHTML("derived")}</dt>
        <dd>${trendRow}</dd>
        <dt>Bikeway miles</dt><dd>${bikewayMilesRow}</dd>
        <dt>Menu $ on bike safety ${B.badgeHTML("proxy")}</dt>
        <dd>${menuRow}</dd>
      </dl>
      <h4 style="margin:0.5rem 0 0.2rem">Corridors in view</h4>
      ${top.map(([s, v]) => `<div><a href="#" data-corridor="${B.esc(s)}">${B.esc(s)}</a>
        <span class="muted">${B.fmt(v.crashes)} crashes near ${(v.length / 1000).toFixed(1)} km</span></div>`).join("") || '<p class="muted">No bikeways intersect this ward.</p>'}
      <p style="margin-top:0.6rem"><a class="btn" href="table.html?ward=${encodeURIComponent(w)}">Ward data table</a>
      <a class="btn primary" href="action.html?ward=${encodeURIComponent(w)}">Ward report &amp; take action</a></p>`);
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
      ${B.noticeHTML("normalization")}
      <p><a class="btn" href="network.html?corridor=${encodeURIComponent(street)}">Plan a route here →</a></p>`);
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

  // Crossing DETAIL_ZOOM mid-session swaps crash/obstruction rendering
  // between density dots and individual markers.
  map.on("zoomend", syncDensityMode);

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
