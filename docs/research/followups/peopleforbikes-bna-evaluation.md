# PeopleForBikes (BNA / City Ratings) — data-source evaluation

Evaluated 2026-07-13. Verdict up front: **yes, we can get the data — no
signup, no API key, no scraping — and it is useful, with one licensing
question to settle before we redistribute anything.** It does *not* fill
the ridership/exposure gap (that remains Strava Metro's job, see
`strava-metro-application.md`); what it adds is an independent,
methodology-published *quality* measure: Level of Traffic Stress for every
street segment in Chicago, and a bike-access score for every census block.

## What PeopleForBikes publishes

PeopleForBikes runs the Bicycle Network Analysis (BNA) annually over
~3,000 U.S. cities and publishes the results as its City Ratings. The BNA
is open-source (MIT-licensed
[brokenspoke-analyzer](https://github.com/PeopleForBikes/brokenspoke-analyzer));
inputs are OpenStreetMap (infrastructure), the 2020 Decennial Census
(population, blocks), and LEHD (jobs). Scores are 0–100. Chicago's 2026
score is **11.08 / 100** (all-cities average network score: 36) — rank
2,919 of ~3,000 overall, though 73rd among large cities. Chicago's history:
9 (2024) → 11 (2025) → 11.08 (2026, run May 8). Low-stress miles: 1,834 vs
6,267 high-stress.

## Access — all verified working, unauthenticated

JSON APIs on the BNA site (Nuxt server routes, plain GET):

| Endpoint | Returns |
|---|---|
| `https://bna.peopleforbikes.org/api/cities-index` | All 3,019 rated cities: id, name, lat/lon, current score, analysis version. One ~1 MB call. |
| `https://bna.peopleforbikes.org/api/city-ratings/United%20States/Illinois/Chicago` | City record + **full ratings history** (one entry per analysis year back to 2023). |
| `https://bna.peopleforbikes.org/api/ratings/<rating-uuid>` | Subscores for one analysis: people, opportunity, core services, recreation, retail, transit, low/high-stress miles. |

Raw result files on a public file store, path pattern
`https://files.storage.bna.peopleforbikes.org/<country>/<state>/<city>/<version>/`
(lowercase, URL-encoded spaces; Chicago's current version is `26.05`):

| File | Contents |
|---|---|
| `neighborhood_census_blocks.geojson` | Every 2020 census block: `geoid20`, `pop20`, and per-destination-category access scores (`pop_score`, `emp_score`, `schools_score`, doctors/dentists/hospitals/pharmacies/grocery/retail/parks/transit…) plus low-stress vs high-stress reachable counts. Large (served chunked; expect 10⁵ features citywide). |
| `neighborhood_ways.geojson` | Every street segment, OSM-derived: `osm_id`, `name`, `functional_class`, `speed_limit`, per-direction bike-infra fields (`ft_bike_infra`/`tf_bike_infra`), and **per-direction segment + intersection stress** (`ft_seg_stress`, `ft_int_stress`, …) — the full LTS network. Large. |
| `neighborhood_overall_scores.csv` | 2.3 KB, citywide subscores with human explanations. |
| `residential_speed_limit.csv` | 71 bytes. |
| `neighborhood_<destination>.geojson` | Destination layers (schools, hospitals, parks, transit stops, supermarkets…). |

Caveats found while probing:

- **Only the current analysis version is hosted.** Every older version path
  404s for Chicago. Citywide score history survives in the ratings API, but
  block/segment-level history does not — if we want a stress-network time
  series we must snapshot annually, exactly like we already do for the CDOT
  Bike Routes layer (`data/snapshots/`).
- **Annual cadence**, new run each spring (Chicago: May 2026).
- The site's "Download the data set" button serves these same files; the
  file store allows cross-origin GETs, so the pipeline can fetch directly.
- Our pipeline environment's egress policy blocked Overpass before
  (DECISIONS.md #20); whether `files.storage.bna.peopleforbikes.org` is
  reachable from a pipeline run is untested — may need the local-pull
  runbook treatment (`local-pull-runbook.md`).

## Licensing — the one open question

The analyzer software is MIT, and the data derives from OSM (ODbL) +
Census (public domain). But the *result files* carry no license statement
anywhere we could find — not on the BNA site, the city pages, or the file
store. Since OYL redistributes its `site/data/` outputs, we should ask
PeopleForBikes for terms (or at minimum attribute and link, as we do for
Mellow Bike Map) before shipping derived layers. Their public posture —
open-source tooling, free downloads, advocacy mission — suggests they'll
say yes.

## Would it be useful?

**What it fills:**

1. **Segment-level stress grades we didn't build ourselves.** Our
   quality grades (protected / paint / mellow / none) are derived from
   CDOT facility types plus Mellow tags. BNA's LTS is an independent,
   published-methodology measure that also accounts for speed limits, lane
   counts, parking, and intersection stress. Even used only as a
   cross-check ("our 'protected' grade vs BNA low-stress"), it hardens the
   quality layer; used directly, it grades *every* street, not just ones
   with bike facilities.
2. **A ward-joinable access metric.** Block-level scores spatial-join to
   wards trivially (the pipeline already does crash→ward joins), giving
   each ward page a "bike network connectivity" figure with a citable
   national methodology behind it.
3. **Findings-page ammunition.** "Chicago scores 11/100, versus a national
   average of 36, and has 6,267 high-stress street miles against 1,834
   low-stress" is exactly the kind of on-the-record, third-party evidence
   the site exists to surface. Trend (9 → 11) and peer-city comparisons
   come free from the same APIs.

**What it does not fill:** ridership/exposure. BNA measures the network,
not who rides it. Crash counts still cannot be normalized with this.

**Tier:** crowdsourced/derived — it's OSM-derived and PFB-computed, so it
badges like our Mellow/OSM layers, never "real". Known OSM-lag caveat: PFB
themselves run OSM mapathons because unmapped infrastructure lowers
scores; Chicago's score is only as current as OSM tagging.

**Overlap risk:** `neighborhood_ways` duplicates street geometry we
already render from CDOT. We should import *attributes* (stress grades,
speed limits) — e.g. buffer-matched onto existing geometry like the Mellow
dedup (DECISIONS.md #24) — not add a third overlapping line layer.

## Recommendation

Two-step adoption, cheapest first:

1. **Citywide scores + history (trivial, do first):** pull the three JSON
   endpoints in the pipeline, ship a small `bna_scores.json`, surface on
   findings + sources pages. No licensing concern at this scale
   (facts/figures with attribution), no geometry.
2. **Block scores + stress network (real feature, gated on license
   answer):** annual snapshot of the two big GeoJSONs, ward-join the block
   scores, buffer-match segment stress onto the existing network as an
   additional quality signal. Ask PFB about redistribution terms first.
