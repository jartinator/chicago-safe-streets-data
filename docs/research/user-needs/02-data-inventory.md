# Stimulus: What "On Your Left!" (OYL) offers today

This is the artifact participants react to during interviews. It reflects
`main` as of 2026-07-21 (data contract **v1.14**, all previously-pending PRs
merged). Show or paraphrase this to persona agents; do not assume they know
any of it beforehand.

## What OYL is

An independent, open-source, **read-only** evidence dashboard for Chicago bike
safety: where bike-lane obstructions, bike infrastructure type, and
cyclist-involved crashes overlap, drillable **ward → corridor → intersection**.
It accepts no reports (it points people to 311 and Bike Lane Uprising). Every
layer carries a **real / proxy / mock / crowdsourced / derived / no-data-yet**
badge. Raw counts are **not normalized by ridership** — no cyclist-volume data
is joined yet, and the site says so. Dooring is flagged as structurally
undercounted (official records only include "reportable" crashes). Alongside
the human site there is now a **static, versioned agent API** (`/api/v1/` +
`llms.txt`) so AI assistants can answer questions from the same data.

## The screens

| Screen | What it shows |
|---|---|
| Home (`index.html`) | Orientation landing page: what OYL is, headline stats, who it's for, how to use it — including a plain-language section on asking an AI assistant questions via the agent layer. |
| Transportation map (`map.html`) | Geographic Leaflet map: crash density, bikeway network colored by facility grade, wards, cameras, main-route overlays. All safety analysis lives here. Mock obstructions are **no longer on this map**. |
| Network map (`network.html`) | Schematic "transit-style" map: 21 named main routes (14 street + 7 trail lines) in solid colors, grouped into three toggleable tiers (Trails / Main routes / Connectors), interchange nodes + orientation points, opt-in quality border with four independent grades (protected / paint / mellow / none), and a comfort-floor filter (Any / Paint+ / Protected only) that grays out below-floor stretches without breaking geometry. **No safety data on this page.** |
| Findings (`findings.html`) | Curated finding cards, each with stat + caveat + deep-link: KSI trend, protected share, street coverage (3,944 mi surface streets, ~11% with any bike infra), top corridors, hit-and-run, ward concentration, dooring undercount, and the PeopleForBikes BNA citywide network score (with national context + "not a reason not to ride" caveat). |
| Table (`table.html`) | Ward rankings, sortable, CSV export, incl. **% protected** and **% streets w/ bikeways** columns. |
| Ward one-pager (`ward.html?ward=NN`) | Printable per-ward page (one HTML file serves all 50): safety index, trends, infra stats, alderman contact + sponsorship record, menu-money proxy, recent ward-matched news. Written in brief/plain-language registers, designed to be handed to an alderman or neighbor. |
| Sources (`sources.html`) | Full provenance catalog with tier badges and known limitations. |
| Methodology (`methodology.html`) | How every number is computed. |
| Action (`action.html`) | "What do I do about it": 311, Bike Lane Uprising, alderman contacts, upcoming council hearings, recent news. |
| Contributing (`contributing.html`) | Downloads and docs; how to swap data sources, fill stubs, fork for another city. |
| Obstructions preview (`obstructions-preview.html`) | Gated, watermarked demo of the **synthetic** obstruction layer — quarantined off the main maps entirely, pending a Bike Lane Uprising data-sharing conversation. |

## The agent layer (`/api/v1/` — static JSON API)

Versioned, additive, generated from the same committed data as the human
site; nothing to authenticate or rate-limit. Discovery via `llms.txt` or
`api/v1/index.json` (endpoint list + byte sizes + fetch recipes). Endpoints:
citywide trend/headlines, corridors + hotspot intersections, all-ward
rankings + per-ward detail files, main-route report cards + per-route
segments, council (hearings, records, aldermen), news, proposed projects.
Every file opens with a `_meta` envelope (tier, provenance, license, link to
the human page, JSON Schema). The synthetic obstruction layer is **excluded
from the API entirely**.

## Published datasets (site/data/ — downloadable, contract v1.14)

| Data | Tier | Notes / known limits |
|---|---|---|
| Cyclist-involved crashes (points, ≥ Sept 2017) | real | Severity, dooring flag, hit-and-run, lighting, ward, nearest-bikeway join. Recent months provisional; dooring undercounted. |
| CDOT bikeway network (segments) | real | Facility category: protected / buffered / painted / greenway / sharrow / trail / other. **No install dates** — history built forward from snapshots only. |
| Off-street trails (OSM/curated) | crowdsourced | Lakefront, 606, Major Taylor, etc. Hand-traced fallback while Overpass is unreachable. |
| Road network / coverage metrics | real | Citywide + per-ward: % of on-street bikeway miles protected; % of surface-street miles with any bike infra (denominator: 3,945 centerline miles). |
| Ward rollups + boundaries (2023 remap) | real | Crashes, injuries, fatalities, 311 counts, density band. |
| Ward safety index | derived | 0–100 comparable danger score (percentile blend of crashes/10k pop + crashes/bikeway-mile), 12-mo crash trend, infra growth trend, monthly series. Explicitly relative, not absolute risk. |
| Corridor + intersection hotspots | real | Per-street corridor crash rates and facility mix; labeled crash-cluster intersections. |
| Main routes report cards | derived | 21 curated corridors, mileage graded offstreet / protected / painted / none, pct protected, crashes along line. Editorial roster; gaps stay holes. |
| PeopleForBikes BNA citywide score | crowdsourced | 0–100 network score + subscores, low/high-stress miles, score history, national ranking context. OSM-currency disclosure travels with the data. Network quality, **not** crash data. |
| News coverage | real (matches derived) | Recent bike/street-safety headlines from allowlisted RSS feeds — headline/link/date/outlet only, matched to wards, aldermen, routes, and projects with an auditable `via` on every match. Precision over recall; unmatched items still publish as citywide. |
| Proposed & in-progress projects | derived | Hand-curated roster of active bikeway/trail proposals with volunteer-reviewed status (+ status date + note), official links, citations, and auto-joined news coverage. **No geometry** — no machine-readable planned-bikeway data exists (verified 2026-07), so projects are cards, never map lines. |
| 311 bike-related requests per ward | proxy | Self-reported; biased toward wards with engaged 311 users. |
| Speed / red-light camera violations | proxy | Aggressive-driving proxy; only exists at camera locations. |
| Bike-lane obstructions | **mock** | Entirely synthetic; never rendered on the main maps (gated preview page only); excluded from the API. Schema mirrors Bike Lane Uprising fields, pending a data-sharing conversation. |
| Council records (bike/street-safety legislation) | real | Legistar (frozen 2023-06) + Councilmatic union — current to the present; automated topic tag (derived); contested roll-call votes where they exist (~1.4% — most passes are voice votes). |
| Aldermen safety records | derived | Per-alderman sponsorship counts + recorded no-votes. Sponsorship proxy, not a vote tally. |
| Aldermen contacts | real | Ward Offices dataset: name, email, phone, website, all 50 wards. |
| Committee hearings | real | Upcoming Pedestrian & Traffic Safety etc. meetings from the City Clerk eLMS API, incl. public-comment info. |
| Menu-money spending | proxy | Ward Wise (Chi Hack Night) extract of the aldermanic menu program; bike-safety spend per ward. Not verified against source PDFs. |
| Citywide monthly trend | real | Crashes / injury crashes / KSI / fatal per month since Sept 2017. |
| Bikeway mileage series | derived | Citywide miles by facility type per snapshot date (forward-built history). |
| Mellow routes / connectors | crowdsourced | Community-curated calm-streets network (mellowbikemap.com), deduped against CDOT bikeways into connector-tier geometry on the network map. |
| Planned routes (geometry) | stub | Still empty — no public planned/future-bikeway **geometry** layer exists (the proposed-projects roster covers status, not lines). |

## What OYL deliberately is NOT (today)

- No ridership/exposure data (no counters, no bikeshare trips, no Strava) —
  so no per-rider risk rates. (The BNA score is network quality, not volume.)
- No real obstruction reports; no crowdsourced input beyond map geometry.
- No accounts, alerts, notifications, or subscriptions.
- No pedestrian data — cyclist crashes only.
- No equity overlays (demographics beyond population denominators, no
  race/income lens).
- No enforcement/ticketing data yet (a FOIA for Smart Streets enforcement
  data is in flight; a placeholder layer exists but nothing is published).
- English only; desktop-oriented static site; the API is static flat files —
  no query service, no real-time anything.
- Weekly, human-reviewed data refresh (automated PR each Monday, merged
  after review).
