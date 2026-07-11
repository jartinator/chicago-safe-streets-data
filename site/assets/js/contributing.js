(function () {
  const FILES = [
    { name: "crashes_cyclist.geojson", tier: "real" },
    { name: "bike_routes.geojson", tier: "real" },
    { name: "wards.geojson", tier: "real" },
    { name: "corridors.json", tier: "real" },
    { name: "intersections.json", tier: "real" },
    { name: "findings.json", tier: "real" },
    { name: "meta.json", tier: "real" },
    { name: "ward_311.json", tier: "proxy" },
    { name: "cameras.json", tier: "proxy" },
    { name: "obstructions_mock.geojson", tier: "mock" },
    { name: "planned_routes.geojson", tier: "stub" },
    { name: "mellow_routes.geojson", tier: "crowdsourced" },
    { name: "ward_safety_index.json", tier: "derived" },
    { name: "council_records.json", tier: "real" },
    { name: "aldermen_safety_record.json", tier: "derived" },
    { name: "hearings.json", tier: "real" },
    { name: "menu_spending.json", tier: "proxy" }
  ];

  const OBSTRUCTION_FIELDS = [
    { name: "id", type: "string", description: "Unique identifier for the obstruction report." },
    { name: "obstruction_type", type: "enum", description: "Category of obstruction. Placeholder enum (pending Bike Lane Uprising consultation): vehicle_in_lane, delivery_vehicle, debris, construction, poor_design, snow_ice, other." },
    { name: "photo_count", type: "integer", description: "Number of photos attached to the report (0–5)." },
    { name: "plate_state", type: "string", description: "License plate state (always mock data in this demo)." },
    { name: "plate_number", type: "string", description: "License plate number (always fake \"MOCK…\" values in mock data)." },
    { name: "company_name", type: "string", description: "Business or service name if identifiable (generic placeholders only in mock data)." },
    { name: "notes", type: "string", description: "Free-form description provided by the reporter." },
    { name: "metro_city", type: "string", description: "Chicago neighborhood or general location." },
    { name: "lat", type: "number", description: "Latitude coordinate." },
    { name: "lng", type: "number", description: "Longitude coordinate." },
    { name: "occurred_at", type: "ISO 8601", description: "Timestamp when the obstruction was reported." },
    { name: "crash_occurred", type: "boolean", description: "Whether the obstruction resulted in a crash." },
    { name: "data_tier", type: "string", description: "Data source tier (always \"mock\" in this demonstration)." }
  ];

  async function render() {
    BSD.initPage("contributing.html");

    const app = document.getElementById("app");

    try {
      const meta = await BSD.loadJSON("data/meta.json");

      // ---- Section 1: Download the processed data ----
      const downloadSection = document.createElement("div");
      downloadSection.innerHTML = `
        <h1>Open Data & Contributing</h1>
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
      `;
      app.appendChild(metadataDiv);

      // Files table
      const tableContainer = document.createElement("div");
      tableContainer.className = "table-scroll";
      const table = document.createElement("table");
      table.className = "data";
      table.innerHTML = `
        <thead>
          <tr>
            <th>File</th>
            <th>Tier</th>
            <th>Download</th>
          </tr>
        </thead>
        <tbody>
          ${FILES.map(f => `
            <tr>
              <td><code>${BSD.esc(f.name)}</code></td>
              <td>${BSD.badgeHTML(f.tier)}</td>
              <td><a href="data/${BSD.esc(f.name)}" download class="btn">Download</a></td>
            </tr>
          `).join("")}
        </tbody>
      `;
      tableContainer.appendChild(table);
      app.appendChild(tableContainer);

      // ---- Section 2: Obstruction schema (placeholder) ----
      const obstSchema = document.createElement("div");
      const obstructionHeading = document.createElement("h2");
      obstructionHeading.innerHTML = `Obstruction schema (placeholder) ${BSD.badgeHTML("mock")}`;
      obstSchema.appendChild(obstructionHeading);

      const obstCard = document.createElement("div");
      obstCard.className = "card";
      obstCard.innerHTML = `
        <p>This schema is designed to be swappable so real Bike Lane Uprising data — or another city's obstruction source — can drop in without re-architecting. Each field is defined below:</p>
        <dl style="margin-top: 1rem;">
          ${OBSTRUCTION_FIELDS.map(f => `
            <dt><code>${BSD.esc(f.name)}</code> (${BSD.esc(f.type)})</dt>
            <dd style="margin-bottom: 0.8rem;">${BSD.esc(f.description)}</dd>
          `).join("")}
        </dl>
        <p style="margin-top: 1.2rem; font-size: 0.88rem; color: var(--ink-soft);"><strong>Note on obstruction_type:</strong> The enum value is a placeholder pending consultation with Bike Lane Uprising to align on their real categorization. This demonstrates the pipeline's readiness to accept live obstruction reports once a data-sharing agreement is in place.</p>
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
          <li><strong>Swap the obstruction connector:</strong> Point the pipeline at a real feed (Bike Lane Uprising's eventual API, or your city's 311 equivalent) — the schema is designed to accept real data without re-architecting. Modify <code>make_mock_obstructions.py</code>'s successor to pull from the live source.</li>
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
