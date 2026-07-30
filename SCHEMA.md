# SCHEMA.md — published data contracts (v1.5)

Everything the site consumes lives in `site/data/` and is produced by
`pipeline/aggregate.py`. These files ARE the
public dataset (Screen 7 links them for download). Do not add/rename keys
without bumping `CONTRACT_VERSION` in `pipeline/config.py` and updating this file.

Every record and/or file carries a `data_tier`:

| tier | meaning |
|---|---|
| `real` | From the named public source, raw counts (recent months provisional) |
| `proxy` | Correlated but biased signal (self-reports, sensor placement) — direction, not magnitude |
| `mock` | Synthetic demonstration data. Exists in the tier vocabulary in principle; not currently used by any published dataset |
| `crowdsourced` | Community-curated, unverified (Mellow Bike Map) |
| `derived` | Computed from real underlying data (a rate, trend, or automated topic tag) rather than sourced directly |
| (stub) | Empty FeatureCollection with `properties.status = "no_data_yet"` |

## meta.json
```json
{
  "generated_at": "ISO-8601",
  "contract_version": "1.1",
  "provenance": "socrata" | "fixtures",
  "sources": [{"id","name","tier","records","date_range": ["YYYY-MM-DD","YYYY-MM-DD"]|null}]
}
```
`provenance` other than `"socrata"` makes every page render a synthetic-data banner.

## crashes_cyclist.geojson — tier real
Point FeatureCollection, one feature per located cyclist-involved crash
(≥ 2017-09-01). Properties:

| key | type | notes |
|---|---|---|
| crash_id | string | `CRASH_RECORD_ID` |
| date | ISO datetime | |
| injury_severity | enum | `fatal, incapacitating, non_incapacitating, reported_not_evident, none, unknown` (crash-level most-severe) |
| dooring | bool | `DOORING_I == 'Y'` — **structurally undercounted**, see README |
| hit_and_run | bool | |
| crash_type | string | raw `FIRST_CRASH_TYPE` |
| lighting | string | raw lighting condition |
| street | string | number + direction + name |
| ward | string\|null | containing 2023 ward |
| segment_id | string\|null | nearest bikeway within 30 m, else null |
| data_tier | "real" | |

## bike_routes.geojson — tier real
LineString FeatureCollection (current CDOT network; no install dates — see
`data/snapshots/`). Properties: `segment_id`, `street`, `facility_type_raw`,
`facility_category` (`protected|buffered|painted|greenway|sharrow|trail|other`,
mapped via `FACILITY_CATEGORY_MAP`), `length_m`, `crashes_within_30m`,
`data_tier`.

## wards.geojson — tier real
Polygon FeatureCollection, 2023 remap. Properties: `ward`, `alderman`
(null until filled from the official lookup — never auto-generated),
`cyclist_crashes`, `injuries` (fatal+incapacitating+non-incapacitating crashes),
`fatalities`, `complaints_311` (proxy-badged in UI), `density_band`
(`low|medium|high`, terciles), `data_tier`.

## ward_311.json — tier proxy
`{ data_tier, note, wards: [{ ward, total, by_type: {sr_type: count} }] }`,
sorted by total desc. Wards resolved by point-in-polygon, not the raw 311 ward field.

## cameras.json — tier proxy
`{ data_tier, note, cameras: [{ camera_id, kind: "speed"|"red_light", address,
lat, lng, violations_total, first_date, last_date }] }`

## corridors.json — tier real
Per-street rollup of bikeway segments, sorted by `crashes_per_km` desc:
`[{ street, segments, length_m, crashes, crashes_per_km (null if < 200 m),
facility_mix: {category: meters}, data_tier }]`

## intersections.json — tier real
Top 25 crash clusters (~100 m grid, ≥ 2 crashes):
`[{ lat, lng, label, crashes, data_tier }]`

## findings.json — tier per finding
`[{ id, title, stat, description, caveat, caveat_tags, data_tier,
map_state: { screen: "map"|"table", layers: [..], ward?, corridor?, filters: {dooring?} } }]`
`map_state` is translated into `map.html` query params by the findings screen.
`caveat_tags` is the structured twin of `caveat` (CC-5), drawn from the closed
vocabulary in `pipeline/caveats.py`. The assignment per `id` is canonical and
lives in exactly one place, `caveats.FINDING_CAVEAT_TAGS`; a new finding gets a
row there in the same PR that adds the finding. Never build a second list.

## Normalized obstruction schema — swap-in target, no file currently published
On Your Left! publishes no bike-lane-obstruction data today (see a blocked
bike lane? report it at Bike Lane Uprising, https://www.bikelaneuprising.com).
This section documents the shape a future obstruction feed (a Bike Lane
Uprising export, a Smart Streets FOIA delivery, or a 311-derived extract)
would be normalized into, so a real source can drop in without
re-architecting. Top level would carry
`properties: { data_tier, note }`; every Point feature's properties:

| key | type | notes |
|---|---|---|
| id | string | source-assigned unique identifier |
| obstruction_type | enum | `vehicle_in_lane, delivery_vehicle, debris, construction, poor_design, snow_ice, other` |
| photo_count | int 0–5 | |
| plate_state | string | or "unknown" |
| plate_number | string\|null | |
| company_name | string\|null | |
| notes | string | free text |
| metro_city | "Chicago" | |
| lat, lng | float | duplicated from geometry for table use |
| occurred_at | ISO datetime | obstruction time, not submission time |
| crash_occurred | bool | did a crash occur? |
| data_tier | string | the real tier of whatever feed is plugged in, required on every record |

Swapping in real data (a Bike Lane Uprising export, another city's feed, a
311-derived extract): produce this exact schema, set the real `data_tier`,
and nothing downstream re-architects. See CONTRIBUTING.md.

## planned_routes.geojson — stub
`{ type: "FeatureCollection", features: [], properties: { status: "no_data_yet", note } }`
Populate with the same LineString schema as `bike_routes.geojson`
(`facility_category` may be `"other"`).

## mellow_routes.geojson — tier crowdsourced (falls back to stub)
MultiLineString FeatureCollection, pulled live from mellowbikemap.com's public
API by `pull_mellow.py`/`aggregate.py` — see CONTRIBUTING.md. The source groups
the entire layer into one feature per `route_type` (4 features total: sidewalk,
street, route, path), each a MultiLineString with thousands of parts; these are
kept intact, not exploded into per-segment LineStrings (Leaflet renders a
MultiLineString's nested coordinate array as one efficient multi-part polyline).
Properties:

| key | type | notes |
|---|---|---|
| segment_id | string | `mellow-<route_type>`, e.g. `mellow-street` |
| route_type | enum | `sidewalk\|street\|route\|path`, as returned by the source API |
| length_m | float | total length across all parts of the MultiLineString |
| data_tier | "crowdsourced" | |

No `street` name — the source API doesn't label individual segments. If the
pull didn't run or the source was unreachable, this file falls back to the
stub shape above with `properties.note` explaining why.

## osm_trails.geojson — tier crowdsourced (three-tier fallback, never stub-or-nothing)
LineString/MultiLineString FeatureCollection of named off-street trails. CDOT's
`bike_routes.geojson` is on-street only, so these trails (Lakefront, Bloomingdale/606,
Major Taylor, North Shore Channel, North Branch, etc.) come from elsewhere. Built by
`build_osm_trails_layer()` (shared by `aggregate.py` and `refresh_reporting.py`) in
priority order:

1. `pipeline/raw/osm_trails.json` — a real pull from the OpenStreetMap Overpass API
   (`pull_osm_trails.py`) — via `build_osm_trails()`. OSM ways sharing a `name` are
   grouped into one feature (a MultiLineString when the trail spans several ways).
2. else `data/curated_trails.geojson` — a checked-in, hand-traced editorial fallback
   (see below) — via `build_curated_trails()`, passed through with pipeline-computed
   `length_m`.
3. else the empty stub (`properties.status = "no_data_yet"`).

This environment's egress policy blocks Overpass (and the kumi.systems mirror, and
Socrata), so tier 2 — the curated fallback — is what currently ships in
`site/data/osm_trails.geojson`. Properties (both real-Overpass and curated-fallback
features share this shape):

| key | type | notes |
|---|---|---|
| segment_id | string | `osm-trail-<slug>` (Overpass) or `curated-trail-<slug>` (fallback) |
| name | string | trail name (OSM `tags.name`, or the curated file's `name`) |
| facility_category | "trail" | reuses the shared facility styling |
| length_m | float | total length across all parts, always pipeline-computed (never trusted from the source) |
| data_tier | "crowdsourced" | |

The top-level envelope is uniform across tiers 1 and 2 — both
`build_osm_trails()` and `build_curated_trails()` stamp `data_tier: "crowdsourced"`
on the FeatureCollection itself (not just per-feature), so a consumer can read
the layer's tier without inspecting individual features. Only `note` (the
curated fallback's provenance/approximation caveat) is tier-2-specific; tier 1
carries no top-level `note`. Tier 3 (the empty stub) uses `stub_layer()`'s
different shape (`properties.status`/`properties.note`, no top-level
`data_tier` — see the stub note in `aggregate.py`).

The Overpass query (when it can run) pulls only named off-street ways
(`highway=cycleway`, or `path`/`footway` with `bicycle=designated`) and excludes
`is_sidepath=yes` to drop road-parallel cycle tracks that duplicate CDOT on-street
segments.

### data/curated_trails.geojson — checked-in editorial input (pipeline INPUT), tier crowdsourced
Hand-traced fallback geometry for the 5 roster trail lines, written because
Overpass is unreachable from this build environment (see DECISIONS.md). Not a
published site file; consumed by `build_curated_trails()` at
`pipeline.config.CURATED_TRAILS_PATH`. Same FeatureCollection shape as
`osm_trails.geojson`'s per-feature properties (`segment_id`, `name`,
`facility_category: "trail"`, `data_tier: "crowdsourced"`), plus a per-feature
`note` giving the tracing rationale and a top-level `note` (provenance/approximation
caveat, ~100-300 m tolerance) that passes through onto the built `osm_trails.geojson`
whenever this fallback is the active tier. Editorial and approximate by design —
`build_osm_trails_layer()` prefers a real Overpass pull the moment
`pipeline/raw/osm_trails.json` exists, with no changes needed to this file to
"upgrade" away from it.

## aldermen.json
`{ note, lookup_url, wards: [{ ward, alderman: null, email: null }] }` —
static, hand-maintained; see DECISIONS.md #8.

## ward_safety_index.json — tier derived
Comparable, density-normalized danger score per ward, sorted by
`comparable_danger_score` desc:
```
{ data_tier: "derived", note,
  wards: [{ ward, cyclist_crashes, population (nullable), bikeway_miles (nullable),
            crashes_per_10k_pop (nullable), crashes_per_bikeway_mile (nullable),
            comparable_danger_score (0-100, nullable), data_tier: "derived",
            crash_trend: { direction: "improving"|"worsening"|"flat"|"insufficient_data",
                           window_end (nullable), recent_12mo (nullable), prior_12mo (nullable),
                           pct_change (nullable) },
            infra_growth_trend: { miles_added, pct_growth (nullable), since,
                                  by_category: { <category>: { miles_added, pct_growth (nullable) } } } | null,
            bikeway_pct_protected (nullable), road_miles (nullable),
            bikeway_pct_of_roads (nullable) }] }
```
`comparable_danger_score` is a 0-100 blend of each ward's percentile rank on
crashes-per-10k-population and crashes-per-bikeway-mile — a relative ranking
across wards, not an absolute risk measure (ties/no-data wards sort after every
ward with a real score, including a real score of 0). `population` comes from
`pull_ward_demographics.py` (ACS 5-Year by Ward); `bikeway_miles` clips
`bike_routes.geojson` to each ward polygon. `crash_trend` compares the trailing
365 days to the prior 365 days (anchored to the ward's latest crash date), not
calendar years — a calendar-year comparison would bias "improving" for any
pipeline run mid-year, when the current year's bucket is partial. `infra_growth_trend`
is `null` until at least two `data/snapshots/bike_routes_*.geojson` snapshots exist;
its `by_category` breaks the delta down by facility type (protected, buffered, painted,
greenway, sharrow, trail, other), omitting types absent from both snapshots — a flat total
can still hide a painted→protected upgrade, which the per-category split surfaces.
`bikeway_pct_protected`, `road_miles`, and `bikeway_pct_of_roads` are documented under
Contract v1.9 below (all nullable).

## bikeway_mileage_series.json — tier derived
Citywide **on-street** bikeway miles by facility type over time, 2010 → present — a
machine-readable equivalent of CDOT's Bike Lane Mileage Tracker, spliced from two
sources and tagged per point:
```
{ data_tier: "derived", note,
  series: [{ date: "YYYY-MM-DD",
             source: "cdot_foia_dashboard" | "oyl_snapshot",
             by_category: { protected, buffered, painted, greenway, sharrow },
             total,
             off_street: { trail, other } | null,
             off_street_total: number | null }] }
```
Sorted by date ascending.

- `cdot_foia_dashboard` — CDOT's own year-end figures for **2010–2025**, from the Complete
  Streets program dashboard released under FOIA S145367-071326 (see
  `data/foia/S145367-071326/`). Dated `YYYY-12-31`. This is history we could not compute.
- `oyl_snapshot` — one entry per committed `bike_routes_*.geojson`, computed from the
  public CDOT layer, continuing the series forward. Miles use the CDOT-provided centerline
  mileage (`mi_ctrline`) where present, else projected geometry length.

**The series is on-street only.** That is the only basis on which the two sources are
comparable: the public Bike Routes layer structurally omits off-street trails, so a
snapshot's trail mileage is 0 while CDOT reports ~55. Where the two overlap they agree to
0.03 mi (OYL 2026-07 on-street 445.91 vs CDOT's 2025 column 445.88), which is what makes
the splice defensible. CDOT's off-street figures ride in `off_street` for the years it
reported them; on snapshot points `off_street` is **`null`, meaning unknown, not zero** —
publishing 0 there would read as the trails having disappeared.

Facility-mix changes between years can reflect **upgrades** as well as new construction: a
buffered lane rebuilt as protected moves miles from `buffered` to `protected` with no
change in total. CDOT's buffered mileage falling after 2022 (115.6 → 106.5) is exactly
this. See DECISIONS.md #35–#36.

## council_records.json — tier real (topic_relevant tag: tier derived)
Street/bike-safety-related City Council legislation, unioned from the Legistar
Web API and Chicago Councilmatic (DataMade), sorted by `intro_date` desc:
```
{ data_tier: "real", topic_tag_tier: "derived", note,
  records: [{ matter_id, title, type, status, intro_date, sponsors: [name],
              sponsor_wards: [ward] (resolved only via exact aldermen.json name match),
              url, source: "legistar"|"councilmatic",
              recorded_votes: { date, yes, no, absent, no_voters: [name], result } | (absent),
              topic_relevant (bool), topic_reason, topic_tagged_by: "llm"|"keyword_fallback",
              data_tier: "real", topic_tag_tier: "derived" }] }
```
`source` distinguishes which pull produced the record; `matter_id` is an int
for Legistar records and a string for Councilmatic records, and dedup between
the two sources is keyed on `(source, matter_id)`. `recorded_votes` is present
only on bills with an actual contested roll-call split (at least one "no"
vote) — sourced from Councilmatic, since Legistar's pull doesn't fetch vote
detail. It is absent (not `null`) on records with no contested vote, including
all Legistar records. `recorded_votes.result` is a free-text string as
reported by Councilmatic's vote event (e.g. `"pass"` / `"fail"`) — not a
constrained enum, and passed through as-is. **Coverage:** Legistar data is frozen at
`LEGISTAR_DATA_FROZEN_AT` (2023-06-21) — Chicago's council migrated to a new
system (eLMS) after that date with no confirmed public API (see
DECISIONS.md). Chicago Councilmatic covers the gap: it mirrors the council's
post-migration data and is current through the present, so the union is not
frozen even though the Legistar half is. `topic_relevant` is an automated tag
(see `classify_safety_topic.py`) on a real, deterministically fetched record —
it never fabricates the underlying matter/sponsor/date/vote.

## aldermen_safety_record.json — tier derived
Per-sponsor rollup of `council_records.json`, sorted by `safety_sponsorships` desc:
```
{ data_tier: "derived", note,
  aldermen: [{ sponsor_name, ward (nullable, exact-name-match only), safety_sponsorships,
               total_matched_sponsorships, recorded_no_votes (int),
               records: [{ matter_id, title, type, status,
               intro_date, topic_relevant, url }], data_tier: "derived" }] }
```
A broad proxy record (sponsorships on tagged legislation), not a roll-call
vote tally — most Chicago council street-safety actions pass by voice vote
with no individual vote recorded. `recorded_no_votes` counts how many times
that alderman is named in a `no_voters` list across tagged, contested
`recorded_votes` — the rare cases where an actual "no" was cast and captured.
Because that count comes from `no_voters` rather than from `sponsors`, an
alderman can appear in `aldermen` solely as a recorded no-voter, with zero
sponsorships.

## hearings.json — tier real (best-effort)
```
{ data_tier: "real", as_of, structured_data_available (bool), note,
  committees: [{ committee, meetings: [...] (empty if unstructured),
                calendar_url }] }
```
Refreshed every pipeline run. If `structured_data_available` is `false`,
`meetings` is empty and `calendar_url` is the live link-out — no public
JSON/RSS endpoint for eLMS's meeting calendar was confirmed as of this
contract version (see DECISIONS.md).

Since contract v1.11, each meeting whose agenda PDF was fetched and parsed
also carries `agenda_items` and `agenda_amended` — see "Contract v1.11
changes" below for the item shape and provenance rules.

## menu_spending.json — tier proxy
```
{ data_tier: "proxy", note,
  wards: { ward: { total_spent, items, bike_safety_spent } } }
```
Sourced from Ward Wise (Chi Hack Night), the only structured alternative to
the city's PDF-only Aldermanic Menu Program reports; not independently
verified against source PDFs. Empty `wards` if Ward Wise was unreachable this
run (see CONTRIBUTING.md).

## Severity definitions (injury / KSI)

Used by `citywide_trend.json`, `ward_safety_index.json`'s `windows`/`monthly`,
and the `ksi-trend` finding:

- **injury crashes** = crashes whose most-severe injury is `fatal`,
  `incapacitating`, or `non_incapacitating`.
- **KSI** ("killed or seriously injured") = `fatal` + `incapacitating` only.

Computed by `pipeline/crash_metrics.py` (pure module, shared by the live
`aggregate.py` path and the offline `refresh_reporting.py` so the two can
never drift).

## citywide_trend.json — tier real

Monthly counts of police-reported cyclist crashes citywide since Sept 2017
(`CRASH_START_DATE`), one contiguous bucket per calendar month (months with no
crashes appear with zeros):
```
{ data_tier: "real", window_end: "YYYY-MM-DD", note,
  months: [{ month: "YYYY-MM", crashes, injury_crashes, ksi, fatal }] }
```
`window_end` is the latest crash date in the underlying pull. Recent months
are provisional — crash records get amended upstream.

## Contract v1.7 changes (data-reporting clarity)

Amendments to sections above; the shapes below supersede where they overlap.

- **`ward_safety_index.json`** — each ward record gains two fields:
  - `windows`: same shape as `crash_metrics.window_counts` output —
    `{ recent_12mo: { crashes, injury_crashes, ksi, fatal },
    prior_12mo: { …same keys… }, window_end: "YYYY-MM-DD" }`. Unlike
    `crash_trend` (anchored per-ward), `windows` is anchored at the **global**
    latest crash date so wards are directly comparable.
  - `monthly`: the same contiguous `[{ month, crashes, injury_crashes, ksi,
    fatal }]` series as `citywide_trend.json`, for that ward's located crashes
    (zeros-only for a ward with none).
- **`findings.json`** — full swap of the findings set. Removed ids:
  `painted-vs-protected`, `vehicle-types`. Current ids, in order: `ksi-trend`,
  `protected-share`, `top-corridors`, `hit-and-run`, `ward-concentration`,
  `dooring-undercount` (retitled "Dooring: structurally undercounted").
  `ward-concentration` gains a `wards: [ward, …]` key (the five wards named in
  its stat, for UI drill-down links). The `protected-share` finding counts
  **on-street** bikeway miles only — the `trail` facility category is excluded
  from both numerator and denominator (off-street trails live in
  `osm_trails.geojson` at crowdsourced tier and never enter real-tier
  statistics).
- **`aldermen.json`** — no longer hand-maintained on the live path:
  `pull_aldermen.py` fills it each run from the city's Ward Offices dataset
  (`htai-wnw4`). New shape:
  ```
  { as_of, source, data_tier: "real", note, lookup_url,
    wards: [{ ward, alderman: "Last, First"|null, email, phone, website }] }
  ```
  All 50 wards always present; vacant seats appear as `null` (never invented).
  A failed or sparse pull (< 40 named wards) keeps the previous file. The
  null-filled hand-maintained shape remains the fixtures/offline fallback.
- **`hearings.json`** — meetings are now real, pulled from the City Clerk eLMS
  public API (`api.chicityclerkelms.chicago.gov`). When structured data was
  fetched, the top level carries `source: "elms_api"` and each committee's
  `meetings` contains future, non-cancelled meetings, oldest first:
  ```
  meetings: [{ date (ISO datetime), status: "Scheduled"|"Scheduled & Published",
               location|null, agenda_url|null, notice_url|null, comment|null }]
  ```
  `comment` typically carries the written-public-comment deadline/address. An
  empty `meetings` list with `structured_data_available: true` means "no
  upcoming meetings" (honest data); on API failure the pre-v1.7 link-out
  fallback shape is written instead (`structured_data_available: false`, no
  `source` key).

## Contract v1.8 changes (main routes)

### data/main_routes.json — checked-in roster config (pipeline INPUT)

Curated "main routes" line roster (see
`docs/superpowers/specs/2026-07-12-main-routes-design.md`). Not a published
site file, but its format is contract because `aggregate.py` and
`refresh_reporting.py` both consume it:

```
{ note,
  lines: [{ id, name, termini,                  // termini is display copy, not computed
            source: "bike_routes" | "osm_trails",
            streets: ["HALSTED", …],             // bike_routes lines: normalized street names
            clip_bbox: [south, west, north, east] | (absent),  // optional midpoint clip
            name_tokens: ["lakefront", …] }] }   // osm_trails lines: lowercase contains-tokens
```

Lines match in roster order, **first match wins**, and a segment joins at most
one line (`loop` is first so its bbox claims the downtown couplet segments).
Street matching: the segment's `street` is uppercased and ONE trailing
street-type suffix token (`ST|AVE|BLVD|RD|DR|WAY|PKWY`) is stripped, then
compared for exact equality (never substring). `clip_bbox` keeps only segments
whose geometry midpoint (middle vertex) falls inside. Trail matching: the
`osm_trails.geojson` feature's lowercased `name` must contain any token in
`name_tokens`. The roster is **editorial** — the line list is hand-curated;
membership, grades, and mileage are recomputed from source data each run.

### main_routes.geojson — tier derived (produced by `build_main_routes`)

FeatureCollection of the roster lines' member segments, plus a top-level
`lines` report-card list (same FC-level-metadata pattern as the stub notes):

```
{ type: "FeatureCollection", data_tier: "derived", note,
  lines: [{ id, name, termini, source,
            data_tier: "derived" (street lines) | "crowdsourced" (trail lines),
            miles_total, miles_by_grade: { <grade>: miles },   // grades present only
            pct_protected (street lines only; null when no members),
            crashes_total (street lines only — sum of member crashes_within_30m),
            no_data: true (only on lines with zero member segments) }],
  features: [ member segments, geometry passthrough ] }
```

Member feature properties: `segment_id`, `line_id`, `grade`,
`facility_category`, `length_m`, `crashes_within_30m` (street members only),
`data_tier` (passthrough: `"real"` for CDOT street segments, `"crowdsourced"`
for OSM trail features).

Grades (4, user-locked order off-street > protected > painted > none), mapped
from `facility_category` via `MAIN_ROUTE_GRADE_MAP` in `config.py`:

| grade | from facility_category |
|---|---|
| `offstreet` | `trail` (osm_trails features) |
| `protected` | `protected` |
| `painted` | `buffered`, `painted`, `greenway` |
| `none` | `sharrow`, `other` |

Hard rules: corridor gaps are holes in the line (geometry is never
fabricated); `pct_protected` is over existing member miles only; street-line
stats are `derived` and trail lines `crowdsourced` — the two provenances never
blend; `crashes_total` never appears on trail lines. When `osm_trails.geojson`
is a stub (no live Overpass pull yet), trail lines appear with
`no_data: true` and zero features — the UI greys them with the stub badge.

- **`meta.json`** — `sources` gains
  `{ id: "main_routes", name: "Main Routes (curated line roster)", tier: "derived",
  records: <line count>, date_range: null }`.

## Contract v1.9 changes (network map distinction)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.9"` for this round — it
adds a new published file, `site/data/network_nodes.json` (see below). See
`docs/superpowers/specs/2026-07-12-network-map-distinction.md` for the full design;
this section documents what's actually built.

### data/main_routes.json — roster re-cut
Same checked-in-config contract as the v1.8 section above (format unchanged); the
line **list** was re-curated to 21 lines:

- **Dropped:** `loop` (downtown circulator; fragment cluster), `belmont` (3.8 mi),
  `31st` (1.8 mi). Their segments remain in the local/connecting network, just not
  as named lines.
- **Added (6):** `california`, `mlk-drive`, `lawrence`, `roosevelt`, `marquette`,
  `83rd` — each a single-street line matched on one `streets` token, chosen so
  every roster line is long enough to carry a rider neighborhood-to-neighborhood.
- **Final roster: 16 street lines + 5 trail lines = 21 lines**, up from ~18.
  `data/main_routes.json`'s `note` field and DECISIONS.md #19's "~18" line-count
  description predate this re-cut.

### data/orientation_points.json — checked-in editorial input (pipeline INPUT)
Curated wayfinding points (major-road crossings on roster lines), hand-picked —
not derived from any source dataset:
```json
[{"label": "Milwaukee / North / Damen", "lat": 41.9103, "lng": -87.6773}, …]
```
Not a published site file; consumed by `build_network_nodes()` at
`pipeline.config.ORIENTATION_POINTS_PATH` and passed through into
`network_nodes.json` (below) with `kind: "orientation"`, `lines: []`, and
`data_tier: "derived"` — "derived" because the *node* is a pipeline-emitted record
even though the underlying lat/lng were hand-picked, matching the tier already used
elsewhere for editorial-but-machine-published records (e.g. `aldermen.json`'s
pre-v1.7 shape).

### site/data/network_nodes.json — tier derived (produced by `build_network_nodes`)
New pipeline product for the network map's white nodes — replaces the crash-cluster
"stations" the network map used to show. Rebuilt by both the live `aggregate.py`
path and `refresh_reporting.py`, from `main_routes.geojson` + `orientation_points.json`,
so the two build paths can never drift:
```json
{ "nodes": [
    { "id": "node-001" | "orient-001", "kind": "interchange" | "orientation",
      "lat": 41.91, "lng": -87.67, "label": "…",
      "lines": ["milwaukee", "bloomingdale"] | [], "data_tier": "derived" }
  ], "data_tier": "derived" }
```
Two kinds, both `data_tier: "derived"`:

- **`interchange`** — geometric line-crossing nodes, derived (no editorial input).
  For every pair of *distinct* roster line ids, `build_network_nodes()` checks all
  member-segment pairs for exact 2-D line-segment intersections (pure Python, no new
  deps). Raw intersection points within **150 m** of each other are unioned into one
  cluster and collapsed to their centroid; a cluster is only emitted as a node if it
  spans **≥ 2 distinct line ids** (`lines` is that id set, sorted by roster order).
  `label` joins the involved lines' display names with `" × "` (e.g.
  `"Milwaukee Line × Bloomingdale Trail (606)"`). `id` is `node-NNN`, assigned after
  sorting nodes by `(lat, lng)` — not stable across a roster change, since a dropped
  or added line can shift the whole node count and ordering.
- **`orientation`** — one node per `data/orientation_points.json` entry, passed
  through verbatim (`label`, `lat`, `lng`) with `lines: []`. `id` is `orient-NNN` in
  file order.

Current build: 40 interchange nodes + 10 orientation nodes = 50 total (matches
`meta.json`'s `network_nodes` source `records` count).

### meta.json — new/changed source entries
- **`network_nodes`** (new): `{ id: "network_nodes", name: "Network Map Nodes
  (interchanges + orientation points)", tier: "derived", records: <node count>,
  date_range: null }`. Written by both build paths; placed just after `main_routes`,
  before `citywide_trend`.
- **`osm_trails`** (formalized, was previously implicit): `{ id: "osm_trails",
  name: "OpenStreetMap Off-street Trails", tier: "crowdsourced",
  records: <feature count>, date_range: null }`, placed just before `main_routes`.
  **Conditional:** this entry is only written/updated when the built
  `osm_trails.geojson` has at least one feature — i.e. tier 1 (real Overpass) or
  tier 2 (curated fallback) produced something. A stub build (tier 3) leaves any
  prior `osm_trails` source entry untouched rather than overwriting it with a
  zero-record one, so `meta.json` never claims a source ran when it didn't.

## Contract v1.9 changes (road-network coverage)

Adds the `road_network.json` file below and three per-ward fields in
`ward_safety_index.json` (`bikeway_pct_protected`, `road_miles`,
`bikeway_pct_of_roads` — documented in that section above).

## road_network.json — tier real

Surface-street centerline miles citywide and per ward, plus the citywide share
of street miles carrying any on-street bike infrastructure:

```
{ data_tier: "real", as_of: "YYYY-MM-DD" | null, note,
  citywide: { road_miles, onstreet_bikeway_miles, pct_with_bike_infra } | null,
  wards: [{ ward, road_miles }] }
```

`as_of` and `citywide` are `null` — and `wards` is `[]` — when
`street_centerlines.geojson` wasn't pulled this run (`pull_street_centerlines.py`
didn't run); the `note` explains why. `road_miles` is the Street Center Lines
layer (dataset `pr57-gg9e`) filtered to `STREET_CLASSES_INCLUDED` (classes
2/3/4 = arterial/collector/local) x `STREET_STATUS_INCLUDED` (status N, in
service) — expressways, ramps, alleys, and river channels are excluded (see
DECISIONS.md). `onstreet_bikeway_miles` is `bike_routes.geojson` mileage
excluding the `trail` facility category (off-street trails aren't roads).
Both sides of `pct_with_bike_infra` are projected centerline lengths
(`METRIC_CRS`), so the ratio is method-consistent. `wards` is sorted by ward
number ascending.

- **`ward_safety_index.json`** — each ward record gains three nullable fields
  (documented inline in that section's shape above):
  - `bikeway_pct_protected` — the protected share of the ward's on-street
    (non-trail) bikeway miles; `null` when the ward has no on-street bikeway
    miles.
  - `road_miles` — the ward's surface-street centerline miles from
    `road_network.json`; `null` when street centerlines weren't pulled this run.
  - `bikeway_pct_of_roads` — the share of the ward's surface-street miles with
    any on-street bike infrastructure; `null` when `road_miles` is missing or
    zero.
- **`findings.json`** — gains a new `street-coverage` finding, inserted
  immediately after `protected-share`. Current order: `ksi-trend`,
  `protected-share`, `street-coverage`, `top-corridors`, `hit-and-run`,
  `ward-concentration`, `dooring-undercount`. Present only when
  `road_network.json`'s `citywide.road_miles` is available (i.e. street
  centerlines were pulled).
- **`meta.json`** — `sources` gains
  `{ id: "street_centerlines", name: "Street Center Lines (surface-street grid)",
  tier: "real", records: <feature count> | null, date_range: null }`, placed
  directly after the `bike_routes` entry.

## Contract v1.10 changes (network tiers)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.10"` for this round.
See `docs/superpowers/specs/2026-07-13-network-tiers-design.md` for the full
design (three route tiers, quality regrade, mellow dedupe, comfort floor,
interlining, selection state); this section documents what's actually built
in the pipeline. `site/data/meta.json` on disk carries
`"contract_version": "1.10"`, aligned with `CONTRACT_VERSION` — it was
brought in line with this round's `CONTRACT_VERSION` bump in the same commit
that cut it, and already reflects this round's outputs (19-line roster,
`mellow_connectors` source entry). If `pipeline/config.py`'s
`CONTRACT_VERSION` is bumped again in a future round, a full pipeline run
(`python3 pipeline/run_all.py` or `refresh_reporting.py`) is needed to pick
up the new string.

### data/main_routes.json — roster re-cut (14 street + 5 trail = 19 lines)
Same checked-in-config contract as the v1.8/v1.9 sections above (format
unchanged); the line **list** drops two street lines added in the v1.9
re-cut:

- **Demoted to connectors:** `roosevelt`, `vincennes` — removed from the
  roster entirely (not just unrendered as major routes); their segments still
  flow through the pipeline, they just land in the connector tier
  (`build_mellow_connectors`'s sibling connector geometry / the non-roster
  remainder of `bike_routes.geojson`) rather than as named `main_routes.geojson`
  lines.
- **Final roster: 14 street lines + 5 trail lines = 19 lines**, owner-signed
  count per spec §2 (down from 21 in the v1.9 re-cut). Confirmed against the
  checked-in `data/main_routes.json` and the built `main_routes.geojson`'s
  `lines` array (both list exactly: `milwaukee`, `halsted`, `clark`, `kedzie`,
  `damen`, `state-indiana`, `elston`, `lake`, `jackson-washington`,
  `california`, `mlk-drive`, `lawrence`, `marquette`, `83rd` — the 14 street
  lines — plus `lakefront`, `bloomingdale`, `major-taylor`,
  `north-shore-channel`, `north-branch` — the 5 trail lines, unchanged).

### main_routes.geojson — `line_ids` (multi-line segment membership)
`build_main_routes` no longer assigns a `bike_routes` street segment to only
the first roster line whose `streets` list matches it — **every** matching
line claims it (spec §6, "interlining" groundwork). Each such segment is
still emitted as **one** feature, now carrying two properties instead of one:

| key | type | notes |
|---|---|---|
| `line_ids` | string[] | every matching roster line id, in roster order |
| `line_id` | string | `line_ids[0]`, kept for back-compat with any code that only needs "a" line for this segment |

The segment's length and crash count fold into **every** matching line's
`miles_total` / `miles_by_grade` / `crashes_total` (a shared segment is not
split or double-discounted). Trail features are unaffected — trail matching
stays first-match-wins over `osm_trails.geojson` via `name_tokens` (spec §6
only lifts the restriction for `bike_routes` street matchers) — and always
carry `line_ids` of length 1. On the current roster no two lines' `streets`
lists overlap, so on real data every feature's `line_ids` still has length 1
(confirmed: `site/data/main_routes.geojson`, all 286 features). The
multi-membership behavior is covered by synthetic fixtures in
`pipeline/tests/test_aggregate_main_routes.py`, not by live data yet.

### Quality regrade — `MAIN_ROUTE_GRADE_MAP` (4 independent grades, not a ranked ladder)
`config.py`'s `MAIN_ROUTE_GRADE_MAP` changes from the v1.8 three-level
`offstreet > painted > none` ladder to four independent grade strings — no
grade is "between" the others, each maps from a disjoint set of
`facility_category` values:

| grade | from facility_category | change from v1.8/v1.9 |
|---|---|---|
| `protected` | `protected` | unchanged |
| `paint` | `buffered`, `painted` | renamed from `painted`; **no longer includes `greenway`** |
| `mellow` | `greenway` | **new grade** — greenways are traffic-calmed streets, not painted lanes, so they get their own grade instead of being lumped into `paint` |
| `none` | `sharrow`, `other` (default for any unmatched category) | unchanged in membership, renamed from a "worst" rung to an independent grade |
| `offstreet` | `trail` (osm_trails features) | unchanged |

`mellow` is also the grade stamped on `mellow_connectors.geojson`'s
`facility_category` (`"mellow"`), so the same grade string spans both
main-route greenway segments and deduped connector geometry. Verified against
`pipeline/config.py`'s `MAIN_ROUTE_GRADE_MAP` dict.

### site/data/mellow_connectors.geojson — tier crowdsourced (new file, produced by `build_mellow_connectors`)
Replaces the standalone mellow overlay on the network map (spec §4).
`mellow_routes.geojson` itself is unchanged and keeps shipping (this is an
additional file, not a rename). Built by `build_mellow_connectors()` in
`pipeline/aggregate.py` (shared by the live `aggregate.py` path and the
offline `refresh_reporting.py` path, so the two can never drift on dedupe
logic):

```
{ type: "FeatureCollection", data_tier: "crowdsourced", note,
  features: [ {                                   // 0 or 1 features, never more
    type: "Feature",
    geometry: { type: "MultiLineString", coordinates: [...] },
    properties: { segment_id: "mellow-connectors", facility_category: "mellow",
                  length_m, parts, data_tier: "crowdsourced" }
  } ] }
```

Algorithm: `mellow_routes.geojson`'s per-`route_type` MultiLineStrings are
exploded into their individual block-length parts; a part is **dropped** when
it falls within `MELLOW_DEDUPE_BUFFER_M` (25 m, applied in `METRIC_CRS` /
EPSG:26916) of any published `bike_routes.geojson` segment (`bike_routes`
wins — real infrastructure de-duplicates the crowdsourced layer, not the
other way around); everything a `bike_routes` buffer union doesn't touch is
kept. The bike-route buffers are unioned once and wrapped in a shapely
`PreparedGeometry` so every part pays one indexed `.intersects()` call rather
than testing against each bike segment individually.

Because connectors are identity-less by design (spec §1 — no named line, no
per-segment properties worth keeping), every surviving part collapses into
**one** feature whose geometry is a single MultiLineString of all kept parts
— the same shape `mellow_routes.geojson` itself already uses. Coordinates are
rounded to 6 decimal places (~0.1 m). `properties.parts` is the kept-part
count; that count is also what `meta.json` reports as this source's
`records` (via `mellow_connector_records()`) — there is no other feature to
count. When zero parts survive dedupe, `features` is `[]` (no zero-part
feature is ever emitted) but the envelope keeps `data_tier: "crowdsourced"` —
dedupe genuinely ran, it just kept nothing. When `mellow_routes.geojson`
itself had no features to dedupe this run (nothing to run dedupe against in
the first place), the file instead uses the project's standard stub shape
(`stub_layer()`; same convention as `planned_routes.geojson` and the
`osm_trails.geojson` tier-3 stub): `{ type: "FeatureCollection", features:
[], properties: { status: "no_data_yet", note } }` — no top-level
`data_tier`, so a stub can never be mistaken for a real crowdsourced-tier
result with zero records.

The top-level `note` also carries the run's drop rate as prose (e.g. "This
run dropped 34.1% of mellow route miles as duplicates of on-street bike
infrastructure") — computed as `1 - (kept length / pre-dedupe length)`, not a
separate structured field. Current build: 38,114 parts, ~936 route-miles kept,
2.2 MB on disk, 34.1% of mellow route-miles dropped as duplicates (confirmed
against the committed `site/data/mellow_connectors.geojson`).

### meta.json — new source entry
- **`mellow_connectors`** (new): `{ id: "mellow_connectors", name: "Mellow
  Connectors (deduped crowdsourced low-stress links)", tier: "crowdsourced",
  records: <kept-part count>, date_range: null }`. Registered by both build
  paths (`aggregate.py` inline; `refresh_reporting.py`'s
  `upsert_meta_sources`), only when the built layer has at least one feature
  — same "don't overwrite a prior real entry with a zero-record one on a
  degraded run" posture as `osm_trails`'s v1.9 entry. Placed just before
  `osm_trails` in source order. Confirmed present in the committed
  `site/data/meta.json` with `records: 38114`, matching the geojson's `parts`
  count exactly.
- **`main_routes`** — `records` drops from 21 (v1.9) to 19, reflecting the
  roster re-cut above. Confirmed in the committed `meta.json`.

## Contract v1.11 changes (agenda items)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.11"`. Additive only.

- **`hearings.json`** — each meeting whose agenda PDF was downloaded and
  yielded text (new `pull_agenda_items.py`, merged by `aggregate.py`) gains:

  ```
  meetings: [{ …existing fields…,
    agenda_amended: bool,          // "AMENDED" banner on the PDF cover page
    agenda_items: [{
      record_number|null,          // e.g. "O2026-0026797"; null for items the
                                   // agenda lists without one (appointments,
                                   // Rule 45 approvals)
      ward|null,                   // the "(28)" tag printed on the agenda line
      section|null,                // agenda section heading, verbatim
      agenda_text,                 // verbatim item text from the official PDF
      title|null, type|null, status|null, sponsor|null, category|null,
      matter_url|null,             // eLMS matter API lookup by record_number;
                                   // all null when the lookup failed
      safety_keyword_match: bool,  // SAFETY_TOPIC_KEYWORDS hit (derived)
      tracked: bool                // record_number is in council_records.json
    }] }]
  ```

  Both keys are **absent** (not empty) on meetings whose PDF could not be
  fetched or parsed — an empty `agenda_items` list means "parsed fine, nothing
  listed", never "extraction failed". Every published string is verbatim from
  the official agenda PDF or the eLMS matter API — nothing is generated. The
  two boolean flags are the only derived fields. When any agenda was merged,
  the top-level `note` gains a sentence saying extraction is best-effort and
  the PDF is authoritative.

## Roster additions under v1.11 (no contract change): 312 RiverRun, Green Bay

`data/main_routes.json` gains a 6th and 7th trail line — `312-riverrun`
(`name_tokens` `["riverrun", "river run"]`, matching the "312 RiverRun" and
"West 312 RiverRun" `osm_trails.geojson` features) and `green-bay`
(`name_tokens` `["green bay"]`, one matching feature, fully suburban — see
DECISIONS.md #27) — **14 street + 7 trail = 21 lines**, superseding the v1.10
re-cut's count of 19 (DECISIONS.md #26/#27). Data edits only: no keys added
or renamed anywhere, so `CONTRACT_VERSION` stays `"1.11"`. `meta.json`'s
`main_routes.records` moves 19 → 21, `main_routes.geojson` gains the two line
entries plus their three member features (289 features total), and
`network_nodes.json` picks up one derived interchange (North Branch Trail ×
Green Bay Trail), 42 → 43 nodes.

## news_items.json — tier real (matches derived)

Recent public news coverage of Chicago bike/street safety, for the "In the
news" sections (ward page, action page). Headline + link + date + outlet
**only** — never article body text or images (licensing evidence:
docs/research/news-layer/evidence-feeds.md). Weekly pull (`pull_news.py`)
from the public RSS feeds allowlisted in `config.NEWS_FEEDS`; relevance
filtering and entity matching are computed in `aggregate.py`
(`build_news_items`), design and persona-validation basis in
docs/superpowers/specs/2026-07-13-news-coverage-design.md.

```
{ data_tier: "real",            // headlines/links/dates/outlets are verbatim
  match_tier: "derived",        // the matches object is computed
  as_of,                        // the pull's fetched_at (null if it didn't run)
  note,
  items: [{                     // newest first; published within
                                // NEWS_WINDOW_DAYS of as_of; capped at
                                // NEWS_MAX_ITEMS; undated items are dropped
    title,                      // verbatim headline
    url,                        // canonical article URL (Google News redirect
                                // links are resolved; unresolvable ones kept)
    source|null,                // outlet name, e.g. "Streetsblog Chicago"
    published,                  // ISO 8601, from the feed's pubDate
    matches: {                  // every entry carries `via`: an auditable,
                                // human-readable record of the exact rule
                                // that made the match (amendment A)
      wards:    [{ ward, via }],        // explicit "Nth Ward" tag/headline
                                        // hit, or the ward of a matched
                                        // alderperson (via says which)
      aldermen: [{ name, ward|null, via }], // honorific+surname or full-name
                                        // rule only; bare surnames and
                                        // shared surnames never match alone
      routes:   [{ id, name, via }]     // main-routes roster: street name +
                                        // type suffix, or trail name token
    } }] }
```

Precision over recall throughout: a missing match is expected, a wrong match
is a defect (persona study, 4/4). Items with **no** matches still publish —
they're citywide coverage. There is deliberately no item↔meeting or
item↔record-number matching (record numbers never appear in news text;
permanently killed by the validation study).

## Contract v1.12 changes (news coverage)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.12"`. Additive only.

- **`news_items.json`** (new file) — schema above.
- **`SAFETY_TOPIC_KEYWORDS`** gains `"dooring"` (config edit, cast-wide by
  design; affects the derived `safety_keyword_match` agenda-item flag and
  the pull-time council-records net, both downstream-filtered).

### meta.json — new source entry
- **`news_items`** (new): `{ id: "news_items", name: "News Coverage (public
  RSS headlines)", tier: "real", records: <published item count>,
  date_range: null }`. Unconditional (the file is always written; zero
  records on a degraded/offline run is honest, not absent). Placed last,
  after `menu_spending`.

## proposed_projects.json — tier derived (coverage headlines real, matching derived)

A short, hand-curated editorial roster of active Chicago bikeway/trail
proposals (`data/proposed_projects.json`, the `main_routes.json` pattern),
published with per-project news coverage auto-joined from `news_items.json`.
Design + persona validation:
docs/superpowers/specs/2026-07-13-proposed-projects-design.md; evidence:
docs/research/proposed-routes-news/evidence-proposals.md. No geometry — no
machine-readable planned-bikeway data exists (verified 2026-07), so projects
render as cards, never map lines.

```
{ data_tier: "derived",       // the roster and its statuses are curated
  coverage_tier: "real",      // coverage headlines/links/dates are verbatim
  match_tier: "derived",      // the phrase-matching is computed
  as_of,                      // the news pull's fetched_at (null = no pull)
  note,
  projects: [{
    id, name,
    status,                   // controlled vocab (roster file lists it)
    status_as_of,             // date the status was last volunteer-reviewed
    status_note,              // which-kind specifics (which funding, which
                              // block) — validation amendment B
    description,
    wards: [],                // curator-assigned; empty = citywide/unassigned
    official_links: [{text, url}],
    news_phrases: [],         // curated multi-word match phrases (bare
                              // corridor tokens are forbidden — "606" alone
                              // is ~1/12 on-topic, evidence brief §2)
    citations: [{title, url, source, published}],  // status evidence
    coverage: [{title, url, source, published, via}]  // joined from
                              // news_items, newest first, cap 8
  }] }
```

## Contract v1.13 changes (proposed projects)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.13"`. Additive only.

- **`proposed_projects.json`** (new file) — schema above.
- **`news_items.json`** — each item's `matches` gains `projects:
  [{ id, name, via }]` (same auditable-`via` mechanics as routes). An item
  that names a rostered project is relevant by definition, even without a
  safety-keyword hit. The newest-first `NEWS_MAX_ITEMS` cap no longer drops
  project-matched items: any windowed item with a project match survives the
  cap (project coverage is sparse, milestone-driven, and is what
  `proposed_projects.json` joins on).
- **`pull_news.py`** adds one roster-derived Google News query feed (the
  projects' curated phrases), so coverage follows the roster — several real
  projects' current coverage lives on outlets outside the base allowlist.

### meta.json — new source entry
- **`proposed_projects`** (new): `{ id: "proposed_projects", name:
  "Proposed & In-Progress Bikeway Projects (curated roster)", tier:
  "derived", records: <project count>, date_range: null }`. Unconditional;
  placed last, after `news_items`.

## Contract v1.14 changes (PFB BNA citywide scorecard)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.14"` (this branch
was cut before v1.12/v1.13 above landed on `main`; renumbered at merge — no
functional overlap with either). Additive only (validated proposal B1 —
`docs/projects/pfb-bna-proposal.md`; six-persona verdict in
`docs/research/user-needs/validation/pfb-bna/VERDICT.md`).

- **`bna_scores.json` (new) — tier crowdsourced.** PeopleForBikes' Bicycle
  Network Analysis citywide scorecard for Chicago, shaped by
  `pipeline/bna_metrics.py` from the three unauthenticated JSON endpoints
  `pull_bna.py` pulls (endpoint survey:
  `docs/research/followups/peopleforbikes-bna-evaluation.md`):

  ```
  { data_tier: "crowdsourced",
    as_of,                     // latest analysis date, YYYY-MM-DD
    version,                   // PFB analysis version, e.g. "26.05"
    score,                     // 0-100 citywide BNA score
    subscores: { people?, opportunity?, core_services?,
                 recreation?, retail?, transit? },   // 0-100 each
    low_stress_miles, high_stress_miles,
    history: [{ version, score, as_of }],            // ascending by as_of
    context: { cities_rated, mean_score,             // over all rated cities
               large_city_count, large_city_rank,    // population >= floor
               large_city_min_population },
    note }                     // OSM-currency disclosure, travels with the data
  ```

  Source-priority chain (`aggregate.build_bna`, mirrored by
  `refresh_reporting.apply_bna`): `raw/bna.json` (live pull) → the committed
  `bna_scores.json` (bna.peopleforbikes.org may be egress-blocked; an offline
  or blocked run never drops or degrades the layer) → absent entirely. Only a
  run with a real raw pull rewrites the file or its meta entry. A
  `--fixtures` run's synthetic `raw/bna.json` is treated as absent for this
  purpose too (`build_bna(ignore_raw=...)`), same as the `news_items`/
  `osm_trails` fixtures guard above — fixture scores never overwrite committed
  real reporting data.

- **`findings.json`** — gains the `bna-score` finding (tier crowdsourced),
  appended after the crash-derived cards. Its copy rules are contract-adjacent
  (verdict B1): national-average context in the description, a
  network-not-crashes reconciliation sentence, and a caveat carrying the
  analysis version/date, the OSM-currency disclosure, and the
  "not a reason not to ride" anti-discouragement line. Omitted entirely when
  no BNA source is available (fresh fork, host unreachable, file deleted).

- **`meta.json`** — `sources` gains `bna_scores` (tier crowdsourced, inserted
  between `osm_trails` and `main_routes`; `records` = number of analysis
  years in `history`, `date_range` = first analysis date → `as_of`) — only on
  runs that actually pulled (meta never claims a source ran when it didn't).

## Contract v1.14 (agent API)

`pipeline/emit_api.py` builds a separate, additive JSON namespace under
`site/api/v1/` for LLM agents — smaller, self-describing files sized for a
handful of fetches, generated from this file's own contract (`site/data/`),
never a second source of truth. Every endpoint's shape is a hand-written
JSON Schema under `site/api/v1/schemas/`, validated in CI
(`pipeline/check_api.py`); this file does NOT restate those shapes
field-by-field — the schemas are the contract for `/api/v1/`, this section
just says it exists. Discovery for a cold agent: `site/llms.txt` (plain
text) and `/api/v1/index.json` both list every endpoint, its size, and
fetch recipes for common questions; `site/sitemap.xml` and `site/robots.txt`
point crawlers at both.

Two trade-offs worth knowing about:

- **Crash IDs are truncated.** `crashes/ward-NN.json` rows carry a
  `CRASH_ID_PREFIX_LEN`-hex-char prefix of the full crash_id, not the full
  128-char id — cheaper to fetch and parse at scale. On the (astronomically
  unlikely) event two ids in the same build share that prefix, both fall
  back to their full id rather than colliding (`emit_api.crash_id_prefixes`);
  an agent wanting the full id set uses `full_data_url`.
- **No obstruction data.** On Your Left! publishes no obstruction data at
  all — not on the human site, not under `/api/v1/` in any form —
  `index.json`'s `no_synthetic_data` field and `llms.txt`'s matching
  disclaimer say so explicitly, so an agent doesn't go looking for it.

## PLANNED (not yet published): smart_streets_enforcement.json — tier real

**Status: pending FOIA — no file exists yet, and nothing below is contract
until it ships.** Publishing this file (and any keys it adds) requires the
usual `CONTRACT_VERSION` bump at that time; it is documented here now so the
placeholder Data Sources card, the FOIA request, and the integration plan
(`docs/superpowers/plans/2026-07-21-smart-streets-enforcement-integration.md`)
all point at one agreed shape.

Violation-level records from Chicago's Smart Streets pilot (automated camera
enforcement of bike/bus lane and bus stop violations, CDOT + Dept. of
Finance, Nov 2024–present). No public dataset exists (verified 2026-07-21);
a FOIA request is prepared — see `docs/foia/smart-streets-enforcement.md`.
Target shape, mirroring the fields the Tribune's reporting shows are already
compiled:

```
{ data_tier: "real", as_of, note,
  source: "foia" | "portal",       // portal, if the city ever publishes it
  violations: [{
    id,                            // citation/notice number as released, else row index
    occurred_at,                   // ISO datetime
    location,                      // address / block / intersection as released
    lat, lng,                      // null until geocoded (geocoding is derived work)
    violation_type,                // "bike_lane" | "bus_lane" | "bus_stop"
    outcome,                       // "warning" | "citation"
    fine_amount,                   // USD int; null for warnings / if withheld
    company_name,                  // commercial/fleet registrant; null for private
                                   // individuals (expected redacted)
    ward,                          // null until spatially joined (derived)
    data_tier: "real" }] }
```

Rules already settled: records with a geocodable location may ALSO be
projected into the normalized obstruction schema (see the "Normalized
obstruction schema" section above — `obstruction_type: "vehicle_in_lane"` / `"delivery_vehicle"`,
real `company_name`, `data_tier: "real"`), which is exactly the swap-in path
that schema was built for; geocodes and ward joins are derived enrichment and
never overwrite the released fields; if the FOIA yields only aggregate
figures, they become an article-/response-sourced static finding, not a
mappable layer.

## Contract v1.15 changes (agent API caveats)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.15"`. Additive
only — no existing key changes shape or meaning.

- **`_meta.caveats` (new, optional)** — every `site/api/v1/` `_meta`
  envelope (see `_envelope()` in `pipeline/emit_api.py`) may now carry a
  `caveats` array: `[{ code, text }]`, machine-readable flags for
  known limitations of that file's numbers, alongside the existing
  prose-only `tier_note`. Present only when at least one flag applies to
  that endpoint — files with none (network-quality/manifest/news
  endpoints) stay clean rather than emitting an empty array. Schema:
  `site/api/v1/schemas/envelope.schema.json`'s new `caveats` property
  (not required; the envelope schema's `additionalProperties: false`
  meant it had to be declared explicitly).

  Four flag codes, catalog text in `emit_api.CAVEAT_TEXT`:
  - `not_normalized_by_ridership` — crash counts are raw, not normalized by
    ridership, so busy corridors look worse than dangerous quiet ones.
  - `recent_months_provisional` — recent months are provisional; crash
    records get amended upstream and may still move.
  - `dooring_undercounted` — dooring crashes are structurally undercounted
    in police crash reports.
  - `sponsorship_proxy_not_vote_tally` — council sponsorship counts are a
    proxy for engagement, not a roll-call vote tally (most street-safety
    measures pass by voice vote).

  Endpoint → flags mapping:
  - `citywide.json` — `not_normalized_by_ridership`,
    `recent_months_provisional`, `dooring_undercounted`
  - `corridors.json` — `not_normalized_by_ridership`
  - `wards/index.json` — `not_normalized_by_ridership`
  - `wards/ward-NN.json` — `not_normalized_by_ridership`,
    `recent_months_provisional`, `sponsorship_proxy_not_vote_tally`
  - `crashes/ward-NN.json` — `not_normalized_by_ridership`,
    `recent_months_provisional`, `dooring_undercounted`
  - `council/index.json` — `sponsorship_proxy_not_vote_tally`
  - `council/records.json` — `sponsorship_proxy_not_vote_tally`
  - `council/aldermen.json` — `sponsorship_proxy_not_vote_tally`
  - `news.json`, `proposed.json`, `routes/index.json`,
    `routes/line-<id>.json`, `index.json` — none (network-quality/
    manifest/news endpoints carry no caveat flag).

- **`site/llms.txt`** — new "## When answering from this data" section
  (after the no-synthetic-data disclaimer, before "## Human pages")
  instructing an agent to restate a quoted number's caveat, cite
  `data_tier`, and say plainly (never estimate) when asked for data this
  API doesn't publish (ridership/exposure denominators, real obstruction
  reports).

### data/commitments.json — checked-in editorial roster (pipeline INPUT), tier real

Curated editorial roster (not pipeline-derived) of the City of Chicago's
*published* bikeway-network commitments, each with a direct citation — kept
separate from anything OYL measures itself (the `data/main_routes.json`
pattern). Top level: `note` (methodology + FOIA cross-reference), then
`commitments: [{ id, text, number, unit, year_committed, deadline (nullable),
source_name, citations: [url], data_tier: "real" }]`. Consumed by
`pipeline/commitments_metrics.py::build_commitments_finding` to produce the
`commitments-vs-delivered` finding in `findings.json`; the finding is skipped
entirely if the roster is empty. Add new commitments only with a citable
public source — never inferred or estimated numbers.

## divvy_ward_exposure.json — tier proxy

**Published as of contract v1.19** (scaffolded in v1.16; see that section's
entry). Per-ward Divvy trip-density for the latest published month,
aggregated from Lyft's public monthly trip exports
(`divvy-tripdata.s3.amazonaws.com` — the modern feed; the old Data Portal
"Divvy Trips" set is deprecated). Trips are grouped to station level (start
station), then station points are joined to wards by point-in-polygon (same
method as `spatial_join.py`). Built by `pipeline/pull_divvy.py`, which writes
this file directly and is non-fatal on any failure — the file is left
untouched, never guessed.

```
{ data_tier: "proxy", status: "ok", as_of, source_key, note,
  wards: [{ ward, trip_count }] }
```

- `as_of` — the month the trips cover, `"YYYY-MM"`, derived from the source
  key (`202606-divvy-tripdata.zip` → `2026-06`).
- `wards` — one entry per ward with at least one located start station,
  sorted numerically by ward. A missing ward means no station coverage, not
  zero riding. Stations without usable coordinates, or falling outside every
  ward polygon, are excluded — never guessed into a ward.

Rules (settled at scaffolding time, unchanged by promotion): this is a
SYSTEM-AREA-BIASED PROXY FOR CYCLING VOLUME, NOT EXPOSURE — it covers Divvy
trips only (not all cycling), and station placement itself skews
downtown/North Side vs. the West Side, so an absent or low ward count means
fewer stations, not necessarily less riding. This number is never divided by,
or used to divide, crash counts — no per-rider risk rate is ever computed
from it; it is published only as ward-level CONTEXT beside crash counts. The
agent API mirrors this file at `site/api/v1/divvy.json` (see the v1.19
changes section); the human ward-page display is a separate, design-led
integration and does not exist yet.

## Contract v1.16 changes (obstruction-layer removal; promise-vs-delivered seed; Divvy scaffolding)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.16"`, and
`site/data/meta.json`'s `contract_version` is hand-set to match. This round is
**not** purely additive — it includes one breaking removal (below).

- **BREAKING — the synthetic obstruction layer is removed.** The published
  file `site/data/obstructions_mock.geojson` (tier `mock`), its generator
  `pipeline/make_mock_obstructions.py`, the gated preview page, and the
  `obstructions` entry in `meta.json`'s `sources` are all deleted. Removing a
  previously-published dataset file is a breaking change for any consumer that
  fetched it. OYL now publishes **no obstruction data at all** — the site and
  `llms.txt` say so plainly and point to Bike Lane Uprising as where real
  blocked-lane reports go (maintainer decision; user-needs study P8 / T3). The
  `mock` tier remains in the `DATA_TIERS` vocabulary and the normalized
  obstruction *schema* remains documented above as a swap-in target (the
  Smart Streets FOIA projection still targets it) — but no file is produced
  from it. The `/api/v1/` namespace never carried obstruction data and still
  doesn't; its disclaimer copy was updated to reflect the removal.

- **Added `commitments-vs-delivered` finding** (in `findings.json`, tier
  `derived`): pairs the 2023 Chicago Cycling Strategy's 150-new-miles /
  80%-low-stress commitment against the current bikeway-network snapshot
  (`bikeway_mileage_series.json`). Backed by the new curated roster
  `data/commitments.json` (documented above) via
  `commitments_metrics.build_commitments_finding`. The finding's caveat states
  plainly that delivery-since-commitment is **not** measurable from OYL data
  (no install dates) pending the ready CDOT install-date FOIA
  (`docs/outbox/2026-07-12--foia--cdot--bikeway-mileage-history.md`, item 4).

- **Divvy exposure scaffolding (PLANNED at the time; published in v1.19)** —
  see the `divvy_ward_exposure.json` section above. `pipeline/pull_divvy.py`
  and the `config.py` Divvy stanza ship as scaffolding only; nothing is
  published and no contract shape is added this round.

## Contract v1.17 changes (bikeway mileage history; promise-vs-delivered becomes measurable)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.17"`. This round is
**not** purely additive — `bikeway_mileage_series.json` changes shape (below).

- **BREAKING — `bikeway_mileage_series.json` moves to an on-street basis and gains
  history.** `by_category` no longer carries `trail` or `other`; those move to a new
  `off_street` object, which is `null` on snapshot points because the public Bike
  Routes layer cannot see off-street mileage at all. `total` is now the on-street
  total. Each point gains a `source` of `"cdot_foia_dashboard"` or `"oyl_snapshot"`.
  A consumer that summed `by_category` for a "total network" figure will now get the
  on-street figure and must add `off_street_total` where it is non-null. In exchange
  the series runs from **2010** instead of 2026-07-11 — 16 years of CDOT's own annual
  figures, recovered via FOIA S145367-071326. Full field documentation in the
  `bikeway_mileage_series.json` section above; rationale in DECISIONS.md #36.

- **`findings.json`'s `commitments-vs-delivered` card now measures delivery.** Its
  previous caveat said flatly that miles delivered since the 2023 commitment were not
  measurable from OYL data pending the install-date FOIA. That FOIA was answered, so
  the card now reports miles built since 2023 against the 150-mile pledge, on two
  explicit bases: genuinely new mileage (the headline, because the pledge says "new")
  and CDOT's own larger count, which folds in concrete upgrades to protected lanes
  that already existed. Both numbers, and the gap between them, are published. The
  card's `stat` changes from `"150 new miles"` to `"<delivered> of 150 new miles"`,
  and its `title` from "Promised bikeway miles vs. the network on the ground" to
  "Promised bikeway miles vs. what got built". When the released history is absent
  (a `--fixtures` run, or a fork that has not pulled it) the card falls back to the
  old snapshot-only framing and says so — it never implies a measurement it did not make.

- **Two low-stress definitions now coexist, and each number says which it uses.**
  `config.CDOT_LOW_STRESS_CATEGORIES` (protected + greenway + trail) is CDOT's own,
  verified against its dashboard's arithmetic, and **excludes buffered lanes**.
  `commitments_metrics.LOW_STRESS_CATEGORIES` (protected + buffered + greenway +
  trail) is OYL's network-level definition and includes them. CDOT's 80%-low-stress
  pledge is scored on CDOT's definition, because the pledge is CDOT's; network
  descriptions elsewhere continue to use OYL's.

- **`data/cdot_bikeway_history.json`** (added in the previous round, contract-neutral
  then) is now a pipeline input rather than a standalone artifact: `aggregate.py` and
  `refresh_reporting.py` both read it. It is not published under `/api/v1/`; the
  history reaches API consumers through `bikeway_mileage_series.json`.

- **Fix: `refresh_reporting.py` no longer drops the `commitments-vs-delivered` card.**
  The script fully rebuilds `findings.json`, but `build_findings_core` never produced
  that card (it needs the curated roster and CDOT's install history, not crash data),
  so an offline refresh silently deleted a published finding. It is now rebuilt and
  re-appended alongside the BNA card. The script also rebuilds
  `bikeway_mileage_series.json` itself now — both of its inputs (`data/snapshots/`
  and `data/cdot_bikeway_history.json`) are committed, so it is fully derivable
  offline and no longer read back as a possibly-stale file.

## commitments_ledger.json — tier derived

Chicago's published bikeway commitments scored against CDOT's own year-by-year figures
(recovered under FOIA S145367-071326). Both sides of every comparison are the City's own
data. Backed by the curated roster `data/commitments.json`; built by
`commitments_metrics.build_commitments_ledger`.

```
{ data_tier: "derived", note, source,
  scored: int, met: int,
  commitments: [{
    id, text, claim_quote, target, unit, year_committed, deadline,
    basis: "network_state"|"network_delta"|"miles_added"|"low_stress_share"|"not_measurable",
    categories: [facility_category] | null,     // null = all on-street
    source_name, source_record, citations: [url], data_tier: "derived",
    measurable: bool,
    // when measurable:
    actual, window, pct_of_target, met,
    // only where a claim needs a more generous reading to clear:
    actual_as_claimed, as_claimed_categories, as_claimed_met, alt_note,
    // when not measurable:
    reason
  }] }
```

Sorted oldest commitment first. **The roster spans administrations deliberately** — the
lens is the bikeway network, not who held office, and every pledge is scored the same way.

`basis` says *how* each was measured, because "50 miles of protected bike lanes" and "150
miles of new bikeways" are not the same kind of claim:

| basis | meaning |
|---|---|
| `network_state` | the standing network in the target year |
| `network_delta` | change in the standing network between baseline and target year |
| `miles_added` | CDOT's installed miles summed over the window, **less** concrete upgrades |
| `low_stress_share` | low-stress share of miles added over the window |
| `not_measurable` | listed with a `reason`; never given a number |

**`actual_as_claimed` is the honesty mechanism.** Where a claim is only reachable under a
more generous reading of which facilities count, both numbers are published rather than
one being chosen. The 2015 "first 100 miles of protected bike lanes" pledge scores 21.35
on protected alone and 108.35 once buffered lanes are folded in; the ledger publishes
both and says which is which. See DECISIONS.md #38.

## Contract v1.18 changes (commitments ledger)

`CONTRACT_VERSION` -> `"1.18"`. **Purely additive.**

- **Added `site/data/commitments_ledger.json`** (documented above) and its
  `commitments_ledger` entry in `meta.json`'s `sources`. No existing field changes shape.
- **`data/commitments.json` entries gain scoring fields** — `basis`, `categories`,
  `baseline_year`, `target_year`, and optionally `alt_categories` / `alt_note` /
  `claim_quote` / `source_record`. Existing fields are untouched, and an entry without a
  `basis` is reported `measurable: false` rather than silently skipped.
- **Three pre-2023 commitments added to the roster**, sourced from City Council budget
  filings found via the eLMS attachment sweep (`docs/foia/elms-attachment-sweep.md`).
- Not exposed under `/api/v1/` this round; the ledger reaches API consumers only through
  `findings.json`'s `commitments-vs-delivered` card for now.

## Agent-API caveat co-location (contract v1.18, additive — no version bump)

The `site/api/v1/` namespace now obeys a **caveat co-location contract**,
declared per file as `_meta.caveat_contract: "v1"` and implemented in
`pipeline/caveats.py`. Additive throughout: no existing key changes shape or
meaning, so per this repo's own rule (README, "For agents") the change ships
under the current `CONTRACT_VERSION` of `1.18` rather than bumping it.

**Why no bump, stated plainly:** `contract_version` is emitted from
`config.CONTRACT_VERSION` and `check_provenance.py` requires it to equal
`site/data/meta.json`'s. That file is written by the aggregate step, which this
change does not run — `site/data/` is untouched here. A bump therefore belongs
to the next real refresh, and this is flagged for the maintainer rather than
silently skipped: if you prefer the stamp to move with the contract, bump
`CONTRACT_VERSION` during the next Monday refresh, when `meta.json` is rewritten
anyway.

- **`_meta.caveat_contract` (new, required)** — `"v1"`. Declares that every
  quotable number in the file carries its qualifier in its own object (Form A),
  as a `<field>_caveat` sibling (Form B), or via `caveat_ref` into a map in the
  **same** file (Form C). Cross-file references are forbidden by the contract.
- **`_meta.agent_instruction` (new, required)** — the positive imperative, one
  verbatim string in every file. An instruction that varies per file reads as
  decoration; `test_agent_instruction_identical_in_every_file` pins it.
- Both are declared in `envelope.schema.json`'s `properties` **and** `required`
  — the envelope is `additionalProperties: false`, so they had to be.

**`wards/ward-NN.json`** is the first payload migrated, because it is the file a
ward-scoped agent fetches alone and its counts previously carried no qualifier
at all — the "recent months are provisional" caveat lived only in `llms.txt` and
`index.json`, one fetch away:

- `safety.windows.recent_12mo` — Form A, `data_tier: "real"`, tags
  `provisional` + `not_ridership_normalized`.
- `safety.windows.prior_12mo` — Form A, tagged `not_ridership_normalized`
  **only**. This window has closed. The two blocks are deliberately separate and
  must not be merged: one caveat over `windows` would be false about the prior
  window (rule CC-2), and a blanket disclaimer that is wrong about one of the
  numbers it covers teaches a reader to discount a figure that is settled.
- `safety.crash_trend` — Form A, `data_tier: "derived"`, plus `small_n` when
  either 12-month count is under `SMALL_N_THRESHOLD` (20). Data-derived, not
  editorial: 11 of 50 wards carry it today.
- `safety.monthly` — Form B (`monthly_caveat` / `monthly_caveat_tags`) on
  `safety`, plus per-item `caveat_tags: ["provisional"]` on the trailing
  `PROVISIONAL_MONTHS` (2) entries, so the provisional boundary is machine-
  visible instead of prose.
- `safety.comparable_danger_score` — Form B, beside the existing `score_note`,
  which keeps its current value. Retire `score_note` at the next `api_version`;
  removing it now would not be additive.
- `see_also.council` — new link, closing a parity gap: a ward file pointed at
  crashes and corridors but never at the council record for the same ward.

**New schema `claim.schema.json`** carries the shared `$defs` (`qualifier_block`,
`caveat_tags` closed enum, `caveat_text`, `item_override`, `caveat_ref_block`,
`caveats_map`), referenced by `ward.schema.json`.

**`PROVISIONAL_MONTHS = 2` and `SMALL_N_THRESHOLD = 20` ship as flagged
proposals, not findings** — `caveats.ASSUMPTIONS` is the machine-readable form of
that label. `PROVISIONAL_MONTHS` is being observed forward (one row per build in
`_system/marge/oyl-provisional-observations.csv`); a backward `git diff` over
this repo's history would measure pipeline churn and mislabel it as agency
amendment behaviour. `SMALL_N_THRESHOLD` is a judgement about adequate evidence
and nothing can settle it.

**Not migrated yet, by design.** `citywide.json` findings still carry prose
caveats without the structured `caveat_tags` twin, and 6 of its 9 caveat strings
name no referent ("A floor, not a full count."), so the CC-3 lint is scoped to
the ward files rather than run globally. `wards/index.json` needs Form C, since
50 inline blocks would take it past the size budget. Those are separate phases
and each is independently stop-safe.

> **Amended 2026-07-25 (see the citywide section below).** The `citywide.json`
> half of that paragraph is now done: findings carry `caveat_tags`, the five
> caveats that named no referent are rewritten, and the CC-3 lint covers the
> file. `wards/index.json` Form C is still outstanding.

## citywide.json caveat co-location (contract v1.18, additive — no version bump)

`citywide.json` is the second payload under `caveat_contract: "v1"`, after the
ward files.

- **`findings[]`** — every card is a Form A claim: `stat` is the number,
  `data_tier` + `caveat_tags` + `caveat` are its qualifier. Tags come from
  `caveats.FINDING_CAVEAT_TAGS`. The field is added to `site/data/findings.json`
  upstream, in the three modules that author the cards
  (`crash_metrics.build_findings_core`, `bna_metrics.build_bna_finding`,
  `commitments_metrics.build_commitments_finding`), and `emit_api` passes it
  through verbatim — so the human findings page and the agent API read one list.
- **`trend`** — gains a Form A block (`caveat_tags` + `caveat`) covering the
  whole month series, and the trailing `PROVISIONAL_MONTHS` items of
  `trend.months` carry `caveat_tags: ["provisional"]` of their own (CC-4).
  `trend.note` is **unchanged and not merged into the caveat**: `note` says what
  the series is, `caveat` says how a count can be wrong.
- **Five caveat strings were rewritten** so each names its own referent and
  survives being quoted alone (CC-3): `ksi-trend`, `top-corridors`,
  `hit-and-run`, `ward-concentration`, `dooring-undercount`. Any value they
  restate is in CC-8's canonical parenthetical form, `(2040 crashes)`.
- **Enforcement**: `COLOCATION_ENFORCED_CLAIMS` gains `citywide.json` →
  `trend`, `findings[*]`. 260 claims enforced, up from 250.

`citywide.json` grows 22,847 → 24,956 bytes against a 100,000-byte budget.

## Contract v1.19 changes (Divvy trip-volume proxy published)

`pipeline/config.py`'s `CONTRACT_VERSION` is bumped to `"1.19"`, and
`site/data/meta.json`'s `contract_version` is hand-set to match. Purely
additive.

- **`site/data/divvy_ward_exposure.json` is published** (tier `proxy`) — the
  v1.16 scaffolding ran for real. First landed month is `2026-06`: 1,521
  stations, 600,357 trips, all 50 wards matched. `pull_divvy.py` is wired
  into `run_all.py` as a non-fatal stage (WARNING + exit 0 on any failure,
  matching `pull_bna`/`pull_osm_trails`) and now emits `as_of`. Prerequisite
  fix (PR #101): Divvy zips carry a binary `__MACOSX/._*.csv` AppleDouble
  member the CSV selection now skips.
- **New API endpoint `site/api/v1/divvy.json`** with hand-written schema
  `schemas/divvy.schema.json`: `{ _meta, status, note, exposure }`, where
  `exposure` is `{ as_of, source_key, wards[], data_tier, caveat_tags,
  caveat }` — one Form A qualifier block over the trip counts, generated by
  `caveats.divvy_caveat()`. `COLOCATION_ENFORCED_CLAIMS` gains `divvy.json`
  → `exposure`. When no pull has landed, the endpoint still exists with
  `status: "no_data_yet"` and no `exposure` key — the endpoint's existence
  is contract; its numbers are not. New `_meta.caveats` code
  `divvy_volume_proxy` (`envelope.schema.json`'s enum updated in the same
  PR, per that schema's rule).
- **`meta.json` gains a conditional `divvy_ward_exposure` sources entry**,
  present iff the data file exists, appended after `proposed_projects`.
- The hard rule survives promotion verbatim: no per-rider risk rate is ever
  computed from this data, anywhere in the pipeline or the API.
