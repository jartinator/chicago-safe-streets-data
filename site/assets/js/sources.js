(function () {
  // Every card renders with id="src-{id}" — other pages deep-link these anchors
  // (downloads table, explore-data explainers, ward-report provenance modal).
  // `short` is the chip-TOC label.
  const SOURCES = [
    {
      id: "crashes",
      name: "Traffic Crashes — Crashes / People / Vehicles",
      short: "Crashes",
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
      metaId: "crashes"
    },
    {
      id: "citywide_trend",
      name: "Citywide Crash Trend (monthly)",
      short: "Crash trend",
      origin: "Computed from Traffic Crashes",
      tier: "real",
      cadence: "weekly pipeline run",
      description: "Monthly citywide counts of cyclist crashes, injuries, and killed-or-seriously-injured, Sept 2017 to present — the series behind the trend charts.",
      limitations: "Counts, not rates; recent months provisional.",
      links: [],
      metaId: "citywide_trend"
    },
    {
      id: "bike_routes",
      name: "CDOT Bike Routes",
      short: "Bike routes",
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
      id: "street_centerlines",
      name: "Street Center Lines (surface-street grid)",
      short: "Street centerlines",
      origin: "Chicago Data Portal (Socrata)",
      tier: "real",
      cadence: "weekly pipeline run",
      description: "The city's surface-street centerline grid, filtered to classes 2/3/4 (arterial/collector/local) and status N (in service) — expressways, ramps, alleys, and river channels excluded. Used as the surface-street denominator for the ward coverage metrics (% of streets with bikeways).",
      limitations: "The underlying layer was last updated by the city in June 2021 — new streets built since then aren't reflected. No install-date field; this is a snapshot of current-state geometry, not a historical record.",
      links: [
        { text: "Street Center Lines", url: "https://data.cityofchicago.org/d/pr57-gg9e" }
      ],
      metaId: "street_centerlines"
    },
    {
      id: "sr311",
      name: "311 Service Requests (bike-related)",
      short: "311 requests",
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
      short: "Cameras",
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
      short: "Obstructions (demo)",
      origin: "MOCK demonstration data (schema mirrors Bike Lane Uprising's public submission fields)",
      tier: "mock",
      cadence: "regenerated each pipeline run",
      description: "Reports of bike lanes blocked by cars, debris, or other obstructions. This is entirely synthetic MOCK data for schema demonstration — Bike Lane Uprising has no public API yet.",
      limitations: "Entirely synthetic — no real reports, so it never renders on the main maps; it lives only on a gated, watermarked demo page. The category enum is a placeholder pending a data-sharing conversation with Bike Lane Uprising. This layer demonstrates the pipeline's readiness to accept obstruction reports once a public data source becomes available.",
      links: [
        { text: "Synthetic demo page (gated)", url: "obstructions-preview.html" },
        { text: "Bike Lane Uprising", url: "https://www.bikelaneuprising.com" }
      ],
      metaId: "obstructions"
    },
    {
      id: "smart_streets",
      name: "Smart Streets Enforcement (pending FOIA)",
      short: "Smart Streets",
      origin: "City of Chicago Smart Streets pilot (CDOT + Dept. of Finance, Hayden AI cameras) — via FOIA request, not yet received",
      tier: "stub",
      cadence: "N/A — records request in progress",
      description: "Camera-enforced bike lane, bus lane, and bus stop violations from the city's downtown Smart Streets pilot (warnings from Nov 2024, tickets from Dec 2024), including commercial-fleet registrant names — enforcement-grade obstruction data, unlike self-reported 311 signals. No public dataset exists (verified July 2026; the Chicago Tribune obtained its July 2026 delivery-company fine figures via a records request), so this layer is empty until the city answers our FOIA request to the Department of Finance for the violation-level records.",
      limitations: "Not yet integrated — a FOIA request is prepared and awaiting response; nothing renders anywhere until real records arrive. When they do: downtown pilot zone only (Roosevelt–North Ave–Ashland–Lake Michigan), so coverage is geographically sparse by design; private individuals' registrant names are expected to be redacted (commercial fleets are not); locations will need geocoding before any map use.",
      links: [
        { text: "Our FOIA request (repo)", url: "https://github.com/jartinator/chicago-safe-streets-data/blob/main/docs/outbox/2026-07-21--foia--dof--smart-streets-enforcement-data.md" },
        { text: "City Smart Streets page", url: "https://www.chicago.gov/city/en/depts/fin/provdrs/parking_and_redlightcitationadministration/svcs/smart-streets.html" }
      ],
      metaId: null
    },
    {
      id: "wards",
      name: "Ward Boundaries (2023 remap)",
      short: "Wards",
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
      short: "Planned routes",
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
      short: "Mellow map",
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
      short: "OSM trails",
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
      id: "bna_scores",
      name: "PeopleForBikes BNA City Rating (citywide scorecard)",
      short: "BNA score",
      origin: "PeopleForBikes Bicycle Network Analysis (bna.peopleforbikes.org)",
      tier: "crowdsourced",
      cadence: "annual upstream analysis (each spring); pulled weekly, best-effort",
      description: "PeopleForBikes' annual citywide score (0–100) of how well Chicago's bike network connects people to destinations on low-stress streets, with subscores (people, opportunity, core services, recreation, retail, transit), low- vs high-stress street mileage, score history back to 2017, and national context (average across ~3,000 rated cities, rank among large cities). Powers the findings card; methodology is published by PeopleForBikes.",
      limitations: "Computed from OpenStreetMap, so it is only as current as volunteer mapping — which is uneven across neighborhoods and can understate what a neighborhood has or miss hazards nobody mapped. It grades the street network, not riders or crashes: it moves when mapping or infrastructure changes, not when safety outcomes do. A low score is a case for building more, not evidence that people don't or shouldn't ride. Only the current analysis version is hosted upstream (older versions disappear), so history beyond the citywide score is not retained by PeopleForBikes.",
      links: [
        { text: "Chicago on the BNA map", url: "https://bna.peopleforbikes.org/cities/United%20States/Illinois/Chicago" },
        { text: "City Ratings methodology", url: "https://cityratings.peopleforbikes.org/about/methodology" }
      ],
      metaId: "bna_scores"
    },
    {
      id: "main_routes",
      name: "Main Routes (curated line roster)",
      short: "Main routes",
      origin: "Computed from CDOT Bike Routes + OSM trails roster",
      tier: "derived",
      cadence: "weekly pipeline run",
      description: "20 marquee corridors (13 street lines + 7 trail lines, owner-signed roster) drawn heavy on both map screens. A \"line\" is a named corridor end-to-end (Halsted: 79th ⇄ Waveland). The network map is a deliberate schematic: it straightens each line into one continuous spine and draws quality as structural ink along it — off-street / protected / paint / nothing (a hollow stretch marks where no bikeway is built) — while the transportation map colors each member segment directly by its own grade in true geometry, so quality reads segment-by-segment. The line list is hand-picked in a checked-in roster (data/main_routes.json); each pipeline run auto-fills every line with the real CDOT/OSM segments that match it, so grades and mileage stay live.",
      limitations: "the roster is editorial: we chose which corridors count as main routes; segment grades and mileage are computed from source data each run. Gaps in a corridor stay holes in the line — geometry is never fabricated. Street lines are derived from CDOT data; trail lines are crowdsourced OSM data; the two never blend.",
      links: [
        { text: "Roster config (data/main_routes.json)", url: "https://github.com/jartinator/chicago-safe-streets-data/blob/main/data/main_routes.json" }
      ],
      metaId: "main_routes"
    },
    {
      id: "network_nodes",
      name: "Network nodes (interchanges + orientation points)",
      short: "Network nodes",
      origin: "Computed from Main Routes geometry + a curated orientation-points list",
      tier: "derived",
      cadence: "weekly pipeline run",
      description: "Derived interchange nodes computed from geometric intersections between main-route lines (merged within 150 m, only where 2+ lines meet) plus hand-picked orientation points (data/orientation_points.json) for wayfinding on the network map.",
      limitations: "Interchanges only appear where two or more main-route lines actually cross in main_routes.geojson's geometry — a real-world crossing that isn't on the roster produces no node. Orientation points are a hand-picked list, not derived from any line's geometry, so their coverage is only as complete as that list.",
      links: [
        { text: "Orientation points config (data/orientation_points.json)", url: "https://github.com/jartinator/chicago-safe-streets-data/blob/main/data/orientation_points.json" }
      ],
      metaId: "network_nodes"
    },
    {
      id: "mellow_connectors",
      name: "Mellow connectors (deduped low-stress links)",
      short: "Mellow connectors",
      origin: "Computed from Mellow Bike Map geometry minus CDOT Bike Routes overlap",
      tier: "crowdsourced",
      cadence: "weekly pipeline run",
      description: "The connector-tier remainder of the community Mellow Bike Map: mellow geometry within 25 m of an official CDOT bikeway is dropped as a duplicate, and what's left ships as one citywide layer of quiet-street links between routes for the network map.",
      limitations: "Inherits the Mellow Bike Map's crowdsourced tier — volunteer-tagged streets, no official review. The 25 m dedupe is purely geometric: a mellow street just beyond the buffer of a parallel bikeway survives, one hugging it is dropped, regardless of how riders treat them.",
      links: [
        { text: "Mellow Bike Map", url: "https://mellowbikemap.com" }
      ],
      metaId: "mellow_connectors"
    },
    {
      id: "ward_safety_index",
      name: "Ward Safety Index (concern rank)",
      short: "Concern rank",
      origin: "Computed from crash data + ACS 5-Year by Ward population + CDOT Bike Routes",
      tier: "derived",
      cadence: "weekly pipeline run",
      description: "A 0-100 relative concern rank per ward (higher = worse), blending crashes-per-capita and crashes-per-bikeway-mile so wards can be compared fairly rather than by raw crash count, plus year-over-year crash trend and bikeway-mile growth trend.",
      limitations: "A relative ranking across wards, not an absolute risk measure. Population comes from Census ACS estimates (sampling error applies). Infrastructure growth trend is null until at least two dated bike-route snapshots exist.",
      links: [
        { text: "ACS 5-Year Data by Ward", url: "https://data.cityofchicago.org/Community-Economic-Development/ACS-5-Year-Data-by-Ward-Most-Recent-Year/k5pk-wpt9" }
      ],
      metaId: "ward_safety_index"
    },
    {
      id: "council_records",
      name: "Council Records (street/bike-safety legislation)",
      short: "Council records",
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
      id: "aldermen",
      name: "Current Alderpersons (Ward Offices)",
      short: "Alderpersons",
      origin: "Chicago Data Portal (Socrata)",
      tier: "real",
      cadence: "weekly pipeline run",
      description: "Official roster of current alderpersons — name, email, phone, and website per ward.",
      limitations: "Vacant seats appear as null; the roster is the city's own and may lag a resignation by days.",
      links: [
        { text: "Ward Offices dataset", url: "https://data.cityofchicago.org/d/htai-wnw4" }
      ],
      metaId: null
    },
    {
      id: "aldermen_safety_record",
      name: "Alderperson Safety Voting Record",
      short: "Alderperson records",
      origin: "Derived from council_records.json",
      tier: "derived",
      cadence: "weekly pipeline run",
      description: "Per-alderperson rollup of sponsorships on safety-tagged legislation — an aggregate score and the individual record list behind it.",
      limitations: "A broad proxy — primarily sponsorships; the only roll-call signal is recorded_no_votes from rare contested votes. ward resolves only when a sponsor name exactly matches the ward's aldermen.json entry — null otherwise, by design (never auto-matched).",
      links: [],
      metaId: "aldermen_safety_record"
    },
    {
      id: "hearings",
      name: "Upcoming Bike/Traffic-Safety Committee Hearings",
      short: "Hearings",
      origin: "City Clerk eLMS public API (api.chicityclerkelms.chicago.gov)",
      tier: "real",
      cadence: "weekly pipeline run, best-effort",
      description: "Tracks the Committee on Pedestrian and Traffic Safety and Committee on Transportation and Public Way. Pulls structured meetings — date, location, agenda, and written-public-comment instructions — from the City Clerk's eLMS public API every run; if the pull fails, the page links directly to the live official calendar instead.",
      limitations: "The eLMS API is undocumented and unversioned, so we treat it as best-effort — verify against the official calendar before attending. When the API breaks we show a link-out, not a parsed list. Never shows stale or fabricated dates.",
      links: [
        { text: "eLMS meeting calendar", url: "https://chicityclerkelms.chicago.gov/Meetings" }
      ],
      metaId: "hearings"
    },
    {
      id: "menu_spending",
      name: "Aldermanic Menu Program Spending",
      short: "Menu spending",
      origin: "Ward Wise (wardwisechicago.org, Chi Hack Night volunteer project)",
      tier: "proxy",
      cadence: "weekly pipeline run, best-effort",
      description: "Ward-level aldermanic discretionary capital spending, including a bike/traffic-calming-tagged subtotal — the city itself only publishes this as quarterly PDFs.",
      limitations: "Community-structured from a volunteer project, not independently verified against source PDFs by this pipeline. Falls back to empty if Ward Wise is unreachable.",
      links: [
        { text: "Ward Wise", url: "https://www.wardwisechicago.org" }
      ],
      metaId: "menu_spending"
    },
    {
      id: "news_items",
      name: "News Coverage (public RSS headlines)",
      short: "News coverage",
      origin: "Streetsblog Chicago, Block Club Chicago (transportation category), and a Google News search — public RSS feeds only",
      tier: "real",
      cadence: "weekly pipeline run, best-effort; 90-day window",
      description: "Recent news coverage of Chicago bike/street safety, shown on ward and action pages: verbatim headline, link, date, and outlet name — never article text or images. Items are matched to wards, alderpersons, and main routes by conservative name rules (publisher tags first; street names need a type suffix; bare surnames never match), and every match records exactly which rule made it.",
      limitations: "These are independent editorial outlets — listing coverage is not an endorsement, and outlets cover some neighborhoods far more than others, so absence of coverage never means nothing happened. Matching is computed and errs toward missing items rather than mislabeling them, but a wrong match is still possible — the linked article is always authoritative. Feeds that block or rate-limit our fetcher are skipped, never worked around. There is deliberately no story-to-meeting or story-to-ordinance matching: news text almost never carries the identifiers that would make that reliable.",
      links: [
        { text: "Streetsblog Chicago", url: "https://chi.streetsblog.org/" },
        { text: "Block Club Chicago", url: "https://blockclubchicago.org/" }
      ],
      metaId: "news_items"
    },
    {
      id: "proposed_projects",
      name: "Proposed & In-Progress Bikeway Projects (curated roster)",
      short: "Proposed projects",
      origin: "Hand-curated roster (data/proposed_projects.json) + news coverage auto-attached from the news_items dataset",
      tier: "derived",
      cadence: "roster: volunteer-reviewed as news breaks; coverage: weekly pipeline run",
      description: "A short editorial roster of active Chicago bikeway/trail proposals — the 606/Bloomingdale extension, Archer Avenue, Grand Avenue phase 2, the DuSable Lake Shore Drive redesign, the Englewood Nature Trail, the Weber Spur. Each entry carries a volunteer-written status with the date it was last reviewed and the citation backing it, links to the official record, and recent news headlines matched by curated project phrases. Selection criteria: an official record exists, the outcome is unresolved, and the list keeps geographic spread — under-covered South and West Side projects are deliberately included. News-coverage volume is NOT a selection criterion.",
      limitations: "Statuses are volunteer judgments, not city statements — they can lag reality between reviews (the last-reviewed date is always shown, and the official project page is authoritative). No map geometry is drawn: CDOT publishes planned bikeways only as a spreadsheet plus static maps, and CMAP's regional inventory is 2012-era plan archaeology (verified 2026-07), so honest line geometry does not exist to draw. An empty coverage list measures press attention, not project activity. Roster picks are editorial; propose additions or corrections via a GitHub issue.",
      links: [
        { text: "CDOT: planned bike projects", url: "https://www.chicago.gov/city/en/depts/cdot/supp_info/bike-program/planned-bike-projects.html" },
        { text: "Suggest a roster change (GitHub)", url: "https://github.com/jartinator/chicago-safe-streets-data/issues" }
      ],
      metaId: "proposed_projects"
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

      // Chip TOC — one jump link per source card
      const toc = document.createElement("nav");
      toc.className = "chip-toc";
      toc.setAttribute("aria-label", "Jump to a data source");
      toc.innerHTML = SOURCES.map(s =>
        `<a class="btn" href="#src-${s.id}">${BSD.esc(s.short)}</a>`
      ).join("");
      app.appendChild(toc);

      // One full-width card per source
      for (const source of SOURCES) {
        const card = document.createElement("section");
        card.className = "card source-card";
        card.id = `src-${source.id}`;

        let html = `<h2 class="card-heading">${BSD.esc(source.name)} ${BSD.badgeHTML(source.tier)}</h2>`;

        // One-line fact row: origin · cadence · record count
        const records = source.metaId ? recordCounts[source.metaId] : null;
        html += `<p class="muted">${BSD.esc(source.origin)} · updated ${BSD.esc(source.cadence)}` +
          `${records ? ` · ${BSD.fmt(records)} records` : ""}</p>`;

        // Description
        html += `<p>${BSD.esc(source.description)}</p>`;

        // Raw dataset links
        if (source.links && source.links.length > 0) {
          const linkHtml = source.links.map(l =>
            `<a href="${BSD.esc(l.url)}" target="_blank" rel="noopener">${BSD.esc(l.text)}</a>`
          ).join(", ");
          html += `<dl class="source-facts"><dt>Raw dataset:</dt><dd>${linkHtml}</dd></dl>`;
        }

        // Limitations as a visual callout
        html += `<div class="notice"><strong>Known limitations:</strong> ${BSD.esc(source.limitations)}</div>`;

        card.innerHTML = html;
        app.appendChild(card);
      }

      // Content renders async, so the browser's native anchor scroll already
      // fired against an empty page — replay the deep link now.
      if (location.hash) {
        const target = document.getElementById(location.hash.slice(1));
        if (target) target.scrollIntoView();
      }

    } catch (err) {
      app.innerHTML = `<div class="card" style="color: red;">Error loading sources: ${BSD.esc(err.message)}</div>`;
    }
  }

  render();
})();
