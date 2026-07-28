(function () {
  // sourceId must match a card anchor on sources.html (id="src-{sourceId}");
  // sourceName is the short link text. `calc` (derived/proxy files) is a one-
  // sentence plain-language formula shown in a modal. `href` replaces the
  // site-relative download link for files that live outside site/ (repo configs).
  const FILES = [
    {
      name: "crashes_cyclist.geojson", tier: "real",
      title: "Cyclist crashes", sourceId: "crashes", sourceName: "Crashes",
      description: "Every police-reported crash involving a cyclist since Sept 2017, with location, severity, and dooring/hit-and-run flags."
    },
    {
      name: "bike_routes.geojson", tier: "real",
      title: "Bike lane inventory", sourceId: "bike_routes", sourceName: "Bike routes",
      description: "The city's current bike infrastructure: protected, buffered, and painted lanes, greenways, trails."
    },
    {
      name: "road_network.json", tier: "real",
      title: "Street coverage", sourceId: "street_centerlines", sourceName: "Street centerlines",
      description: "Surface-street miles citywide and per ward, plus the share of streets carrying any on-street bike infrastructure."
    },
    {
      name: "wards.geojson", tier: "real",
      title: "Ward boundaries & crash totals", sourceId: "wards", sourceName: "Wards",
      description: "Official 2023 ward boundaries with each ward's crash counts attached."
    },
    {
      name: "corridors.json", tier: "real",
      title: "Most dangerous streets", sourceId: "crashes", sourceName: "Crashes",
      description: "Streets ranked by cyclist crashes per kilometer of bikeway."
    },
    {
      name: "intersections.json", tier: "real",
      title: "Crash hotspot intersections", sourceId: "crashes", sourceName: "Crashes",
      description: "The intersections where the most cyclist crashes cluster."
    },
    {
      name: "findings.json", tier: "real",
      title: "Headline findings", sourceId: "crashes", sourceName: "Crashes",
      description: "The stats behind the Findings page, each with its caveat and map link."
    },
    {
      name: "meta.json", tier: "real",
      title: "Build info", sourceId: null, sourceName: null,
      description: "When this data was generated, from where, and how many records per source."
    },
    {
      name: "ward_311.json", tier: "proxy",
      title: "311 bike complaints by ward", sourceId: "sr311", sourceName: "311 requests",
      description: "Bike-related service requests residents filed with the city, totaled per ward.",
      calc: "Counts self-reported bike-related 311 requests per ward — a signal of who complains, biased toward wards with engaged 311 users, not ground truth of street conditions."
    },
    {
      name: "cameras.json", tier: "proxy",
      title: "Camera violations", sourceId: "cameras", sourceName: "Cameras",
      description: "Speed and red-light violations at fixed cameras — a rough signal of aggressive driving.",
      calc: "Totals violations at fixed camera locations — a proxy for aggressive driving that exists only where cameras are installed, not where violations actually occur."
    },
    {
      name: "planned_routes.geojson", tier: "stub",
      title: "Planned bike routes (empty)", sourceId: "planned_routes", sourceName: "Planned routes",
      description: "Placeholder for future CDOT planned-route data; no structured feed exists yet."
    },
    {
      name: "mellow_routes.geojson", tier: "crowdsourced",
      title: "Community low-stress routes", sourceId: "mellow_map", sourceName: "Mellow map",
      description: "Quiet streets tagged by riders on the volunteer-run Mellow Bike Map."
    },
    {
      name: "osm_trails.geojson", tier: "crowdsourced",
      title: "Off-street trails (OSM)", sourceId: "osm_trails", sourceName: "OSM trails",
      description: "Named off-street trails (Lakefront, 606, Major Taylor…) from OpenStreetMap — volunteer-mapped, unverified."
    },
    {
      name: "main_routes.geojson", tier: "derived",
      title: "Main routes", sourceId: "main_routes", sourceName: "Main routes",
      description: "The 21 marquee corridors — each named line's segments with a facility grade (protected / paint / mellow / none; trails are off-street).",
      calc: "Hand-curated roster in data/main_routes.json; each pipeline run assigns real CDOT/OSM segments to lines and computes grade mileage."
    },
    {
      name: "network_nodes.json", tier: "derived",
      title: "Network nodes", sourceId: "network_nodes", sourceName: "Network nodes",
      description: "Interchange nodes where main routes cross (derived from geometry), plus hand-picked orientation points — wayfinding markers for the network map."
    },
    {
      name: "mellow_connectors.geojson", tier: "crowdsourced",
      title: "Mellow connectors (deduped)", sourceId: "mellow_connectors", sourceName: "Mellow connectors",
      description: "Mellow Bike Map geometry minus anything within 25 m of an official CDOT bikeway — the quiet-street connector tier the network map draws."
    },
    {
      // The roster lives at the repo root (data/, not site/data/), so it isn't
      // servable from the deployed site — link the GitHub blob like SCHEMA.md.
      name: "data/main_routes.json", tier: "derived",
      title: "Main routes roster (config)", sourceId: "main_routes", sourceName: "Main routes",
      description: "The hand-curated list of named corridors, termini, and matching rules that defines the main routes.",
      href: "https://github.com/jartinator/chicago-safe-streets-data/blob/main/data/main_routes.json"
    },
    {
      name: "ward_safety_index.json", tier: "derived",
      title: "Ward concern ranks", sourceId: "ward_safety_index", sourceName: "Concern rank",
      description: "Each ward's 0–100 concern rank (relative to other wards, higher = worse; the JSON field keeps its original name comparable_danger_score), with the rates behind it and 12-month trend.",
      calc: "Average of the ward's percentile ranks on crashes per 10k residents and crashes per bikeway mile — every input is in this file's row."
    },
    {
      name: "council_records.json", tier: "real",
      title: "City Council legislation", sourceId: "council_records", sourceName: "Council records",
      description: "Street- and bike-safety ordinances and resolutions, with sponsors and status."
    },
    {
      name: "aldermen_safety_record.json", tier: "derived",
      title: "Alderperson safety records", sourceId: "aldermen_safety_record", sourceName: "Alderperson records",
      description: "How often each alderperson sponsored bike/traffic-safety legislation.",
      calc: "Counts council records whose sponsor name exactly matches the ward's alderperson."
    },
    {
      name: "aldermen.json", tier: "real",
      title: "Current alderpersons", sourceId: "aldermen", sourceName: "Alderpersons",
      description: "Name and contact info for each ward's current alderperson, from the city's official roster."
    },
    {
      name: "hearings.json", tier: "real",
      title: "Committee hearing calendar", sourceId: "hearings", sourceName: "Hearings",
      description: "Upcoming transportation-committee meetings, or a link to the official calendar."
    },
    {
      name: "menu_spending.json", tier: "proxy",
      title: "Ward discretionary spending", sourceId: "menu_spending", sourceName: "Menu spending",
      description: "What each ward spent its infrastructure \"menu\" money on, with a bike/traffic-calming subtotal.",
      calc: "Community-structured by the volunteer Ward Wise project from the city's quarterly PDF reports — not independently verified against those PDFs by this pipeline."
    },
    {
      name: "citywide_trend.json", tier: "real",
      title: "Citywide crash trend", sourceId: "citywide_trend", sourceName: "Crash trend",
      description: "Monthly citywide cyclist crash, injury, and KSI counts since Sept 2017."
    }
  ];

  const OBSTRUCTION_FIELDS = [
    { name: "id", type: "string", description: "Unique identifier for the obstruction report." },
    { name: "obstruction_type", type: "enum", description: "Category of obstruction: vehicle_in_lane, delivery_vehicle, debris, construction, poor_design, snow_ice, other." },
    { name: "photo_count", type: "integer", description: "Number of photos attached to the report (0–5)." },
    { name: "plate_state", type: "string", description: "License plate state, if identifiable." },
    { name: "plate_number", type: "string", description: "License plate number, if identifiable." },
    { name: "company_name", type: "string", description: "Business or service name, if identifiable." },
    { name: "notes", type: "string", description: "Free-form description provided by the reporter." },
    { name: "metro_city", type: "string", description: "Chicago neighborhood or general location." },
    { name: "lat", type: "number", description: "Latitude coordinate." },
    { name: "lng", type: "number", description: "Longitude coordinate." },
    { name: "occurred_at", type: "ISO 8601", description: "Timestamp when the obstruction was reported." },
    { name: "crash_occurred", type: "boolean", description: "Whether the obstruction resulted in a crash." },
    { name: "data_tier", type: "string", description: "Data source tier of whatever feed is eventually plugged in." }
  ];

  async function render() {
    BSD.initPage("contributing.html");

    const app = document.getElementById("app");

    try {
      const meta = await BSD.loadJSON("data/meta.json");

      // ---- Section 1: Download the processed data ----
      const downloadSection = document.createElement("div");
      downloadSection.innerHTML = `
        <h1>Downloads & Docs</h1>
        <p>This project is open source and open data. Our processed dataset is versioned, documented, and designed to be extended or replaced — swap in new data sources, add analysis layers, or fork for another city.</p>
      `;
      app.appendChild(downloadSection);

      // Download section heading and metadata
      const downloadHeading = document.createElement("h2");
      downloadHeading.textContent = "Download the processed data";
      app.appendChild(downloadHeading);

      // Version line and schema link
      const metadataDiv = document.createElement("div");
      metadataDiv.className = "card";
      const generatedDate = new Date(meta.generated_at).toLocaleString();
      metadataDiv.innerHTML = `
        <p><strong>Contract v${BSD.esc(meta.contract_version)}</strong>, generated ${BSD.esc(generatedDate)}, provenance: <code>${BSD.esc(meta.provenance)}</code></p>
        <p><a href="https://github.com/jartinator/chicago-safe-streets-data/blob/main/SCHEMA.md" target="_blank" rel="noopener">View full field documentation (SCHEMA.md)</a> in the repo.</p>
        <p>Pointing an AI coding assistant at this API? Ask it to read
        <code>https://jartinator.github.io/chicago-safe-streets-data/skills/chicago-bike-safety-data/SKILL.md</code>
        first — it's the same guide <a href="llms.txt">llms.txt</a> already points
        agents at, and it names which file answers which question and how to carry a
        number's caveat along when your code surfaces it. If that path doesn't
        resolve, nothing else here depends on it: every endpoint's own
        <code>_meta</code> and <code>caveats</code> fields carry the same rules on
        their own.</p>
      `;
      app.appendChild(metadataDiv);

      // Files table
      const tableContainer = document.createElement("div");
      tableContainer.className = "table-scroll";
      const table = document.createElement("table");
      table.className = "data table-stack";
      table.innerHTML = `
        <thead>
          <tr>
            <th>Dataset</th>
            <th>Tier</th>
            <th>Source</th>
            <th>Download</th>
          </tr>
        </thead>
        <tbody>
          ${FILES.map((f, i) => `
            <tr>
              <td>
                <strong>${BSD.esc(f.title)}</strong>
                <div class="muted">${BSD.esc(f.description)}</div>
                ${f.calc ? `<button type="button" class="linklike" data-calc="${i}">How it's calculated</button>` : ""}
              </td>
              <td>${BSD.badgeHTML(f.tier)}</td>
              <td>${f.sourceId
                ? `<a href="sources.html#src-${BSD.esc(f.sourceId)}">${BSD.esc(f.sourceName)}</a>`
                : "—"}</td>
              <td>${f.href
                ? `<a href="${BSD.esc(f.href)}" target="_blank" rel="noopener" class="btn">View on GitHub</a>`
                : `<a href="data/${BSD.esc(f.name)}" download class="btn">Download</a>`}<div><code>${BSD.esc(f.name)}</code></div></td>
            </tr>
          `).join("")}
        </tbody>
      `;
      // "How it's calculated" modals for derived/proxy files
      table.querySelectorAll("button[data-calc]").forEach(btn => {
        btn.addEventListener("click", () => {
          const f = FILES[Number(btn.dataset.calc)];
          BSD.openModal({
            title: f.title,
            bodyHTML: `<p>${BSD.esc(f.calc)}</p>` +
              `<p><a href="sources.html#src-${BSD.esc(f.sourceId)}">Full source detail →</a></p>`
          });
        });
      });
      tableContainer.appendChild(table);
      app.appendChild(tableContainer);

      // ---- Section 2: Normalized obstruction schema (swap-in target, no file published) ----
      const obstSchema = document.createElement("div");
      const obstructionHeading = document.createElement("h2");
      obstructionHeading.innerHTML = `Normalized obstruction schema (no file currently published)`;
      obstSchema.appendChild(obstructionHeading);

      const obstCard = document.createElement("div");
      obstCard.className = "card";
      obstCard.innerHTML = `
        <p>On Your Left! does not publish any obstruction data today — see a blocked bike lane? report it at <a href="https://www.bikelaneuprising.com" target="_blank" rel="noopener">Bike Lane Uprising</a>. This schema documents the shape a future obstruction feed (e.g. a Smart Streets FOIA delivery, or a real Bike Lane Uprising feed) would be normalized into, so it can drop in without re-architecting. Each field is defined below:</p>
        <dl style="margin-top: 1rem;">
          ${OBSTRUCTION_FIELDS.map(f => `
            <dt><code>${BSD.esc(f.name)}</code> (${BSD.esc(f.type)})</dt>
            <dd style="margin-bottom: 0.8rem;">${BSD.esc(f.description)}</dd>
          `).join("")}
        </dl>
      `;
      obstSchema.appendChild(obstCard);
      app.appendChild(obstSchema);

      // ---- Section 3: Architecture ----
      const archHeading = document.createElement("h2");
      archHeading.textContent = "Architecture";
      app.appendChild(archHeading);

      const archCard = document.createElement("div");
      archCard.className = "card";
      archCard.innerHTML = `
        <p>The pipeline is designed for offline, asynchronous processing: A Python backend pulls data from the Chicago Data Portal (Socrata) and optional external sources, performs spatial joins to the nearest bikeway segment and containing ward, and emits versioned static JSON and GeoJSON files into this site's <code>data/</code> directory. A static Leaflet front-end consumes these files to render interactive maps and tables. The pipeline runs weekly on a local machine and pushes fresh artifacts to this GitHub Pages site. No server-side processing or database is required — everything is static files and client-side rendering.</p>
        <p>Repo: <a href="https://github.com/jartinator/chicago-safe-streets-data" target="_blank" rel="noopener">github.com/jartinator/chicago-safe-streets-data</a></p>
      `;
      app.appendChild(archCard);

      // ---- Section 4: Extend or fork ----
      const extendHeading = document.createElement("h2");
      extendHeading.textContent = "Extend or fork";
      app.appendChild(extendHeading);

      const extendCard = document.createElement("div");
      extendCard.className = "card";
      extendCard.innerHTML = `
        <p>This project is built to be reused:</p>
        <ul>
          <li><strong>Add an obstruction connector:</strong> Point the pipeline at a real feed (Bike Lane Uprising's eventual API, a Smart Streets FOIA delivery, or your city's 311 equivalent) — the normalized obstruction schema above is designed to accept real data without re-architecting. Add a new pull script that projects the live source into that schema.</li>
          <li><strong>Add an analysis layer:</strong> The pipeline structure supports new aggregate outputs and toggle controls in the front-end. Add a new Python module to compute derived metrics and emit a new JSON file.</li>
          <li><strong>Fork for another city:</strong> Replace the dataset IDs in <code>pipeline/config.py</code> with your city's Socrata portal IDs, update the ward geometry in the spatial-join step, and regenerate.</li>
        </ul>
        <p>See <a href="https://github.com/jartinator/chicago-safe-streets-data/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">CONTRIBUTING.md</a> for detailed setup and contribution guidelines.</p>
      `;
      app.appendChild(extendCard);

    } catch (err) {
      app.innerHTML = `<div class="card" style="color: red;">Error loading page: ${BSD.esc(err.message)}</div>`;
    }
  }

  render();
})();
