# Stimulus: What "On Your Left!" (OYL) offers today

This is the artifact participants react to during interviews. It reflects
`main` **plus two pending PRs** (#15 network-map distinction, #16 coverage
metrics), which we treat as part of the baseline. Show or paraphrase this to
persona agents; do not assume they know any of it beforehand.

## What OYL is

An independent, open-source, **read-only** evidence dashboard for Chicago bike
safety: where bike-lane obstructions, bike infrastructure type, and
cyclist-involved crashes overlap, drillable **ward → corridor → intersection**.
It accepts no reports (it points people to 311 and Bike Lane Uprising). Every
layer carries a **real / proxy / mock / crowdsourced / derived / no-data-yet**
badge. Raw counts are **not normalized by ridership** — no cyclist-volume data
is joined yet, and the site says so. Dooring is flagged as structurally
undercounted (official records only include "reportable" crashes).

## The seven screens

| Screen | What it shows |
|---|---|
| Transportation map (`index.html`) | Geographic Leaflet map: crash density, bikeway network colored by facility grade, wards, cameras, mock obstruction heat, main-route overlays. All safety analysis lives here. |
| Network map (`network.html`) | Schematic "transit-style" map (post-PR #15): 21 named main routes each in one solid color end-to-end, 40 derived interchange nodes + 10 orientation points, opt-in quality border (grade-colored rim, dashed = sharrow), toggles for connecting infrastructure and crowdsourced "mellow routes". **No safety data on this page.** |
| Findings (`findings.html`) | Curated finding cards, each with stat + caveat + deep-link into the map: KSI trend, protected share, street coverage (post-PR #16: 3,944 mi of surface streets, 446 mi / 11% with any bike infra), top corridors, hit-and-run, ward concentration, dooring undercount. |
| Table (`table.html`) | Ward rankings, sortable, CSV export. Post-PR #16 adds **% protected** and **% streets w/ bikeways** columns. |
| Sources (`sources.html`) | Full provenance catalog with tier badges and known limitations. |
| Action (`action.html`) | "What do I do about it": links to 311, Bike Lane Uprising, alderman contacts. |
| Contributing (`contributing.html`) | How to swap data sources, fill stubs, fork for another city. |

## Published datasets (site/data/ — downloadable, contract v1.9)

| Data | Tier | Notes / known limits |
|---|---|---|
| Cyclist-involved crashes (points, ≥ Sept 2017) | real | Severity, dooring flag, hit-and-run, lighting, ward, nearest-bikeway join. Recent months provisional; dooring undercounted. |
| CDOT bikeway network (segments) | real | Facility category: protected / buffered / painted / greenway / sharrow / trail / other. **No install dates** — history built forward from snapshots only. |
| Off-street trails (OSM/curated) | crowdsourced | Lakefront, 606, Major Taylor, etc. Hand-traced fallback while Overpass is unreachable. |
| Ward rollups + boundaries (2023 remap) | real | Crashes, injuries, fatalities, 311 counts, density band. |
| Ward safety index | derived | 0–100 comparable danger score (percentile blend of crashes/10k pop + crashes/bikeway-mile), 12-mo crash trend, infra growth trend, monthly series. Explicitly relative, not absolute risk. |
| Coverage metrics (PR #16) | real | Citywide + per-ward: % of on-street bikeway miles protected; % of surface-street miles with any bike infra (denominator: 3,945 centerline miles). |
| Main routes report cards | derived | 21 curated corridors, mileage graded offstreet / protected / painted / none, pct protected, crashes along line. Editorial roster; gaps stay holes. |
| 311 bike-related requests per ward | proxy | Self-reported; biased toward wards with engaged 311 users. |
| Speed / red-light camera violations | proxy | Aggressive-driving proxy; only exists at camera locations. |
| Bike-lane obstructions | **mock** | Entirely synthetic; schema mirrors Bike Lane Uprising fields, pending a data-sharing conversation. |
| Council records (bike/street-safety legislation) | real | Legistar (frozen 2023-06) + Councilmatic union; automated topic tag (derived); contested roll-call votes where they exist (~1.4% — most passes are voice votes). |
| Aldermen safety records | derived | Per-alderman sponsorship counts + recorded no-votes. Sponsorship proxy, not a vote tally. |
| Aldermen contacts | real | Ward Offices dataset: name, email, phone, website, all 50 wards. |
| Committee hearings | real | Upcoming Pedestrian & Traffic Safety etc. meetings from the City Clerk eLMS API, incl. public-comment info. |
| Menu-money spending | proxy | Ward Wise (Chi Hack Night) extract of the aldermanic menu program; bike-safety spend per ward. Not verified against source PDFs. |
| Citywide monthly trend | real | Crashes / injury crashes / KSI / fatal per month since Sept 2017. |
| Bikeway mileage series | derived | Citywide miles by facility type per snapshot date (forward-built history). |
| Mellow routes | crowdsourced | Community-curated calm-streets network (mellowbikemap.com). |
| Planned routes | stub | Empty — no public planned/future-bikeway layer found yet. |

## What OYL deliberately is NOT (today)

- No ridership/exposure data (no counters, no bikeshare trips, no Strava) —
  so no per-rider risk rates.
- No real obstruction reports; no crowdsourced anything beyond map geometry.
- No accounts, alerts, notifications, or subscriptions.
- No pedestrian data — cyclist crashes only.
- No project/construction tracking (what's being built, what was promised).
- No equity overlays (demographics beyond population denominators, no
  race/income lens).
- English only; desktop-oriented static site; no API beyond flat-file
  downloads.
- Weekly, human-reviewed data refresh; no real-time anything.
