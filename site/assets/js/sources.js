(function () {
  const SOURCES = [
    {
      id: "crashes",
      name: "Traffic Crashes — Crashes / People / Vehicles",
      origin: "Chicago Data Portal (Socrata)",
      tier: "real",
      cadence: "weekly pipeline run; portal updates daily",
      description: "All traffic crashes reported to Chicago Police, including data on crashes, people involved, and vehicles. Cyclist-involved crashes found via the People dataset (person type = BICYCLE), joined on CRASH_RECORD_ID, then spatially joined to the nearest bikeway segment and containing ward.",
      limitations: "Reliable citywide only from Sept 2017 onwards; recent months are provisional (records get amended and reclassified over time); only \"reportable\" crashes (>$1,500 damage or injury) are included — bike dooring is structurally excluded unless it meets other reportable criteria, so dooring is UNDERCOUNTED in this data.",
      links: [
        { text: "Crashes dataset", url: "https://data.cityofchicago.org/d/85ca-t3if" },
        { text: "People dataset", url: "https://data.cityofchicago.org/d/u6pd-qa9d" },
        { text: "Vehicles dataset", url: "https://data.cityofchicago.org/d/68nd-jvt3" }
      ],
      metaId: "crashes",
      showDooringNotice: true
    },
    {
      id: "bike_routes",
      name: "CDOT Bike Routes",
      origin: "Chicago Data Portal (Socrata)",
      tier: "real",
      cadence: "weekly + dated snapshots",
      description: "Current bike facility inventory (protected lanes, buffered lanes, painted lanes, greenways, shared-lane markings, trails). We snapshot the layer on every run to build install history over time.",
      limitations: "No install-date field — current-state only with no planned/future layer; facility taxonomy mapped to public-facing categories; historical snapshots let us infer installation over time but exact dates are not authoritative.",
      links: [
        { text: "CDOT Bike Routes", url: "https://data.cityofchicago.org/d/hvv9-38ut" }
      ],
      metaId: "bike_routes"
    },
    {
      id: "sr311",
      name: "311 Service Requests (bike-related)",
      origin: "Chicago Data Portal (Socrata)",
      tier: "proxy",
      cadence: "weekly",
      description: "Self-reported service requests related to biking and bike infrastructure, categorized by issue type (potholes, street debris, bike lane complaints, etc.). Used as a directional proxy for where cyclists experience problems.",
      limitations: "Self-reported and biased toward wards with engaged 311 users; request-type names shift over time (we match on substrings to bucket requests); good directional proxy for engagement and concern, not ground truth of actual conditions.",
      links: [
        { text: "311 Service Requests", url: "https://data.cityofchicago.org/d/v6vf-nfxy" }
      ],
      metaId: "sr311"
    },
    {
      id: "cameras",
      name: "Speed & Red-Light Camera Violations",
      origin: "Chicago Data Portal (Socrata)",
      tier: "proxy",
      cadence: "weekly",
      description: "Speed and red-light camera violation counts at fixed intersections citywide. Used as a proxy signal for aggressive driving patterns that affect cyclist safety.",
      limitations: "Proxy for aggressive driving, not crashes — exists only at fixed camera locations, so sparse and biased toward where cameras are installed rather than where violations actually occur.",
      links: [
        { text: "Speed Camera Violations", url: "https://data.cityofchicago.org/d/hhkd-xvj4" },
        { text: "Red-Light Camera Violations", url: "https://data.cityofchicago.org/d/spng-6irc" }
      ],
      metaId: "cameras"
    },
    {
      id: "obstructions",
      name: "Bike Lane Obstructions",
      origin: "MOCK demonstration data (schema mirrors Bike Lane Uprising's public submission fields)",
      tier: "mock",
      cadence: "regenerated each pipeline run",
      description: "Reports of bike lanes blocked by cars, debris, or other obstructions. This is entirely synthetic MOCK data for schema demonstration — Bike Lane Uprising has no public API yet.",
      limitations: "Entirely synthetic — no real reports. The category enum is a placeholder pending a data-sharing conversation with Bike Lane Uprising. This layer demonstrates the pipeline's readiness to accept obstruction reports once a public data source becomes available.",
      links: [
        { text: "Bike Lane Uprising", url: "https://www.bikelaneuprising.com" }
      ],
      metaId: "obstructions"
    },
    {
      id: "wards",
      name: "Ward Boundaries (2023 remap)",
      origin: "Chicago Data Portal",
      tier: "real",
      cadence: "static until redistricting",
      description: "Official City of Chicago ward boundaries from the 2023 redistricting. Used as a spatial-join target to aggregate crash and request data by ward.",
      limitations: "None — clean and authoritative until the next redistricting cycle.",
      links: [],
      metaId: "wards"
    },
    {
      id: "planned_routes",
      name: "Planned bike routes",
      origin: "Chicago Department of Transportation",
      tier: "stub",
      cadence: "N/A",
      description: "Placeholder for future planned/under-construction bike route data.",
      limitations: "CDOT publishes planned bikeways only as PDF maps — no structured feed yet.",
      links: [],
      metaId: null
    },
    {
      id: "mellow_map",
      name: "Mellow Bike Map",
      origin: "Community crowdsourced",
      tier: "crowdsourced",
      cadence: "N/A",
      description: "Placeholder for future crowdsourced low-stress street tags.",
      limitations: "Crowdsourced/manually curated — unverified, coverage depends on contributors. Not yet integrated; no public API.",
      links: [],
      metaId: null
    }
  ];

  async function render() {
    BSD.initPage("sources.html");

    const app = document.getElementById("app");

    try {
      const meta = await BSD.loadJSON("data/meta.json");

      // Build a map of id -> record count
      const recordCounts = {};
      if (meta.sources) {
        for (const src of meta.sources) {
          if (src.id && src.records) {
            recordCounts[src.id] = src.records;
          }
        }
      }

      // Page heading and intro
      const heading = document.createElement("div");
      heading.innerHTML = `
        <h1>Data Sources</h1>
        <p>Transparency and enablement — here's where the data comes from and how we use it. Get the raw datasets yourself.</p>
      `;
      app.appendChild(heading);

      // Directional notice
      const noticeContainer = document.createElement("div");
      noticeContainer.innerHTML = BSD.noticeHTML("directional");
      app.appendChild(noticeContainer);

      // Cards grid
      const grid = document.createElement("div");
      grid.className = "cards-grid";

      for (const source of SOURCES) {
        const card = document.createElement("div");
        card.className = "card";

        // Title and origin
        let titleHtml = `<h2>${BSD.esc(source.name)}</h2>`;
        titleHtml += `<p class="muted"><strong>Origin:</strong> ${BSD.esc(source.origin)}</p>`;

        // Record count if available
        if (source.metaId && recordCounts[source.metaId]) {
          titleHtml += `<p class="muted"><strong>Records:</strong> ${BSD.fmt(recordCounts[source.metaId])}</p>`;
        }

        // Tier badge and cadence
        let badgeHtml = `<div style="margin: 0.6rem 0;">`;
        badgeHtml += BSD.badgeHTML(source.tier);
        badgeHtml += `<span class="muted" style="margin-left: 0.5rem;">Updated ${BSD.esc(source.cadence)}</span>`;
        badgeHtml += `</div>`;

        // Description
        let descHtml = `<p>${BSD.esc(source.description)}</p>`;

        // Limitations
        let limitHtml = `<div><strong>Known limitations:</strong> <p>${BSD.esc(source.limitations)}</p></div>`;

        // Links to raw data
        let linksHtml = "";
        if (source.links && source.links.length > 0) {
          linksHtml = `<div><strong>Raw dataset:</strong>`;
          for (const link of source.links) {
            linksHtml += ` <a href="${BSD.esc(link.url)}" target="_blank" rel="noopener">${BSD.esc(link.text)}</a>`;
            if (link !== source.links[source.links.length - 1]) {
              linksHtml += `, `;
            }
          }
          linksHtml += `</div>`;
        }

        card.innerHTML = titleHtml + badgeHtml + descHtml + limitHtml + linksHtml;

        // Add dooring notice for crashes
        if (source.showDooringNotice) {
          card.innerHTML += BSD.noticeHTML("dooring");
        }

        grid.appendChild(card);
      }

      app.appendChild(grid);

    } catch (err) {
      app.innerHTML = `<div class="card" style="color: red;">Error loading sources: ${BSD.esc(err.message)}</div>`;
    }
  }

  render();
})();
