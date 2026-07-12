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
      description: "Current bike facility inventory (protected lanes, buffered lanes, painted lanes, greenways, shared-lane markings). On-street only — off-street trails come from the separate OpenStreetMap trails layer. We snapshot the layer on every run to build install history over time.",
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
        { text: "Red-Light Camera Violations", url: "https://data.cityofchicago.org/d/spqx-js37" }
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
      origin: "mellowbikemap.com (jeancochrane/mellow-bike-map, MIT licensed)",
      tier: "crowdsourced",
      cadence: "weekly pipeline run, best-effort (small third-party app, no uptime SLA)",
      description: "Community-tagged low-stress Chicago streets, pulled from the project's public GeoJSON route API.",
      limitations: "Crowdsourced/manually curated — unverified, coverage depends on contributors. The API returns geometry only, no street names or route labels. Small third-party app: if it's unreachable during a pipeline run, this layer falls back to a stub until the next run.",
      links: [
        { text: "Mellow Bike Map", url: "https://mellowbikemap.com" },
        { text: "Source (GitHub)", url: "https://github.com/jeancochrane/mellow-bike-map" }
      ],
      metaId: "mellow_routes"
    },
    {
      id: "osm_trails",
      name: "OpenStreetMap Off-street Trails",
      origin: "OpenStreetMap via the Overpass API",
      tier: "crowdsourced",
      cadence: "weekly pipeline run, best-effort (public Overpass instance, no uptime SLA)",
      description: "Named off-street trails — Lakefront Trail, 312 RiverRun, North Shore Channel Trail, North Branch Trail, and peers — that CDOT's on-street Bike Routes layer structurally omits. Pulled as named off-street ways and grouped into one feature per trail.",
      limitations: "Community-edited, so completeness and naming vary by contributor. No install dates. Geometry intentionally extends beyond the city line where a trail continues into the forest preserves. Road-parallel cycle tracks (is_sidepath) are excluded to avoid duplicating CDOT segments. Falls back to a stub if Overpass is unreachable during a run.",
      links: [
        { text: "OpenStreetMap", url: "https://www.openstreetmap.org" },
        { text: "Overpass API", url: "https://overpass-api.de" }
      ],
      metaId: "osm_trails"
    },
    {
      id: "ward_safety_index",
      name: "Ward Safety Index (comparable danger score)",
      origin: "Computed from crash data + ACS 5-Year by Ward population + CDOT Bike Routes",
      tier: "derived",
      cadence: "weekly pipeline run",
      description: "A 0-100 relative danger ranking per ward, blending crashes-per-capita and crashes-per-bikeway-mile so wards can be compared fairly rather than by raw crash count, plus year-over-year crash trend and bikeway-mile growth trend.",
      limitations: "A relative ranking across wards, not an absolute risk measure. Population comes from Census ACS estimates (sampling error applies). Infrastructure growth trend is null until at least two dated bike-route snapshots exist.",
      links: [
        { text: "ACS 5-Year Data by Ward", url: "https://data.cityofchicago.org/Community-Economic-Development/ACS-5-Year-Data-by-Ward-Most-Recent-Year/k5pk-wpt9" }
      ],
      metaId: "ward_safety_index"
    },
    {
      id: "council_records",
      name: "Council Records (street/bike-safety legislation)",
      origin: "Legistar Web API (webapi.legistar.com) through 2023-06-21, plus Chicago Councilmatic (chicago.councilmatic.org, DataMade) from then to the present",
      tier: "real",
      cadence: "weekly pipeline run",
      description: "Ordinances, orders, and resolutions matching a broad street/bike-safety keyword net, with sponsors and status. Each record is tagged topic_relevant by an automated classifier (see limitations) layered on top of the real fetched record. The `source` column on each record shows which pull produced it.",
      limitations: "Legistar data is frozen at 2023-06-21 — Chicago's council migrated to a new system (eLMS) after that date with no confirmed public API. That gap is covered post-2023 by Chicago Councilmatic, a republished mirror of the official record, so council_records.json overall is current to the present even though the Legistar half alone is frozen. Exactly how Councilmatic's scraper reaches the post-migration source isn't verifiable from outside DataMade. Most street-safety actions pass by voice vote with no individual roll-call recorded — Vote is populated only for the rare contested (non-unanimous) roll calls. topic_relevant is an automated tag (LLM or keyword fallback), not a human review.",
      links: [
        { text: "Legistar Web API", url: "https://webapi.legistar.com/v1/chicago/matters" },
        { text: "Chicago Councilmatic", url: "https://chicago.councilmatic.org" }
      ],
      metaId: "council_records"
    },
    {
      id: "aldermen_safety_record",
      name: "Alderman Safety Voting Record",
      origin: "Derived from council_records.json",
      tier: "derived",
      cadence: "weekly pipeline run",
      description: "Per-alderman rollup of sponsorships on safety-tagged legislation — an aggregate score and the individual record list behind it.",
      limitations: "A broad proxy — primarily sponsorships; the only roll-call signal is recorded_no_votes from rare contested votes. ward resolves only when a Legistar sponsor name exactly matches a manually-filled aldermen.json entry — null otherwise, by design (never auto-matched).",
      links: [],
      metaId: "aldermen_safety_record"
    },
    {
      id: "hearings",
      name: "Upcoming Bike/Traffic-Safety Committee Hearings",
      origin: "City Clerk eLMS meeting calendar (chicityclerkelms.chicago.gov)",
      tier: "real",
      cadence: "weekly pipeline run, best-effort",
      description: "Tracks the Committee on Pedestrian and Traffic Safety and Committee on Transportation and Public Way. Attempts a structured pull every run; links directly to the live official calendar when no structured data is available.",
      limitations: "No public JSON/RSS endpoint for the eLMS calendar has been confirmed — this most often shows a link-out, not a parsed meeting list. Never shows stale or fabricated dates.",
      links: [
        { text: "eLMS meeting calendar", url: "https://chicityclerkelms.chicago.gov/Meetings" }
      ],
      metaId: "hearings"
    },
    {
      id: "menu_spending",
      name: "Aldermanic Menu Program Spending",
      origin: "Ward Wise (wardwisechicago.org, Chi Hack Night volunteer project)",
      tier: "proxy",
      cadence: "weekly pipeline run, best-effort",
      description: "Ward-level aldermanic discretionary capital spending, including a bike/traffic-calming-tagged subtotal — the city itself only publishes this as quarterly PDFs.",
      limitations: "Community-structured from a volunteer project, not independently verified against source PDFs by this pipeline. Falls back to empty if Ward Wise is unreachable.",
      links: [
        { text: "Ward Wise", url: "https://www.wardwisechicago.org" }
      ],
      metaId: "menu_spending"
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
