# Network map distinction — design spec

**Date:** 2026-07-12
**Status:** approved (owner walked through the four open questions; all recommendations accepted)
**Supersedes:** the network.html sections of `2026-07-12-main-routes-design.md` §7 where they conflict.

## 1. Problem

The network map (`network.html`) and the transportation map (`index.html`) have
converged: both render grade-colored main routes with white casing, both render
trails, and both render crash/safety data. Grade-coloring each *segment* of a
main route makes routes impossible to visually trace, the "white nodes" are
crash clusters masquerading as stations, and trails are invisible because
`osm_trails.geojson` shipped as a stub.

## 2. The distinction, stated once

| | Transportation map (`index.html`) | Network map (`network.html`) |
|---|---|---|
| Question it answers | "What is it like *here*?" (density, outcomes, policy) | "How do I get from area A to area B?" |
| Route coloring | per-segment by facility grade | **one solid color per named line** |
| Safety data | yes — crashes, obstructions, wards | **none** |
| Infrastructure quality | the line color itself | optional **quality border** layer |
| Nodes | crash drill-down | **interchanges + orientation points** |

The network map has exactly three concerns, in order:
1. **Major routes** — long, continuous, named, solid-colored.
2. **Connecting routes** — two independently toggleable, overlappable levels:
   *connecting infrastructure* and *mellow routes*.
3. **Route quality** — a toggleable border treatment on the major routes
   (the casing treatment, swapped from its old always-on role).

## 3. Roster re-curation (`data/main_routes.json`)

Goal: every line is long and carries you neighborhood-to-neighborhood.
Fragments demote to the connecting-infrastructure level (they are still drawn,
just not as named lines).

**Dropped:** `loop` (downtown circulator; fragment cluster), `belmont`
(3.8 mi), `31st` (1.8 mi). Their segments remain in the local network.

**Kept (10):** milwaukee, halsted, clark, kedzie, damen, state-indiana,
vincennes, elston, lake, jackson-washington — plus the 5 trail lines.

**Added (6):**

| id | name | streets | termini copy |
|---|---|---|---|
| `california` | California Line | CALIFORNIA | Little Village ⇄ West Ridge |
| `mlk-drive` | King Drive Line | MARTIN LUTHER KING JR | Bronzeville ⇄ Chatham |
| `lawrence` | Lawrence Line | LAWRENCE | Jefferson Park ⇄ Uptown |
| `roosevelt` | Roosevelt Line | ROOSEVELT | Lawndale ⇄ Museum Campus |
| `marquette` | Marquette Line | MARQUETTE | West Lawn ⇄ Jackson Park |
| `83rd` | 83rd Street Line | 83RD | Scottsdale ⇄ South Chicago |

Final roster: **16 street lines + 5 trail lines = 21 lines.**
Coverage after the re-cut: E-W spine at Lawrence (north), Lake +
Jackson–Washington + Roosevelt (west/central), Marquette and 83rd (south);
N-S spines from California to the lakefront; three diagonals (Milwaukee,
Elston, Vincennes); five off-street trails.

## 4. Line palette

One solid color per line. Rules used to assign: crossing or parallel-nearby
lines must differ strongly in hue *or* lightness; the facility-grade colors
(§6) are reserved for the quality border, so no line color may sit on top of
an identical grade hue except trails (uniformly off-street; border adds
nothing there). All colors are dark enough for label text on the paper canvas.

```
LINE_COLORS = {
  // diagonals
  "milwaukee":            "#1d4ed8",
  "elston":               "#ea580c",
  "vincennes":            "#c026d3",
  // north-south, west → east
  "california":           "#db2777",
  "kedzie":               "#7c3aed",
  "damen":                "#059669",
  "halsted":              "#dc2626",
  "clark":                "#0891b2",
  "state-indiana":        "#4d7c0f",
  "mlk-drive":            "#92400e",
  // east-west, north → south
  "lawrence":             "#881337",
  "lake":                 "#a16207",
  "jackson-washington":   "#6b21a8",
  "roosevelt":            "#0284c7",
  "marquette":            "#1e40af",
  "83rd":                 "#16a34a",
  // trails
  "lakefront":            "#0369a1",
  "bloomingdale":         "#65a30d",
  "major-taylor":         "#ca8a04",
  "north-shore-channel":  "#0d9488",
  "north-branch":         "#3f6212",
}
FALLBACK_LINE_COLOR = "#334155"   // any line id not in the map
```

Palette is subject to a screenshot review pass; adjust only flagged pairs.

## 5. Network map layer architecture (`network.js` / `network-model.js`)

### Panes, bottom → top

```
wardsPane < localPane < mellowPane < connectingTrailsPane
  < qualityPane < casingPane < linesPane
  < plannedCasingPane < plannedPane < nodesPane
```

`heatPane` and `crashesPane` are **deleted**.

### Layers

| Layer | Toggle id | Default | Style |
|---|---|---|---|
| Ward outlines | — (always) | on | unchanged (`#e2e8f0` w1) |
| **Major routes** | — (always) | on | white casing w9 in `casingPane` + solid `LINE_COLORS[line_id]` stroke w6 in `linesPane`. No dashes, no per-segment styling. Roster trail members get the identical treatment. |
| Line name labels | — (always) | on | permanent tooltips as today, tinted to the line color |
| **Quality border** | `quality` | **off** | grade-colored casing **w13** in `qualityPane`, per segment, colors = `GRADE_COLORS`; grade `none` uses `dashArray "6,9"`. Reads as: solid line color, thin white rim, grade-colored border. Toggling on also shows the grade legend block. |
| **Connecting infrastructure** | `connecting` | on | the local network (all non-roster `bike_routes` segments, `LOCAL_STYLE` `#cbd5e1` w1.5) **plus** non-roster OSM trails (`#38bdf8` w2 op0.8 in `connectingTrailsPane`). Real toggle — the old disabled `local-toggle` checkbox becomes live. |
| **Mellow routes** | `mellow` | on | unchanged (`#ec4899` w2 op0.6, canvas renderer, `mellowPane`). Independent of `connecting`; the two overlap freely (separate panes). |
| **Nodes** | `nodes` | on | from `network_nodes.json` (§7). Interchange: circleMarker r5, fill `#ffffff`, stroke `#1a2330` w2.5, hover tooltip with label; visible ≥ z11. Orientation: r3.5, stroke `#64748b` w2, permanent small label ≥ z13, hover below. No crash scaling anywhere. |
| Planned routes | `planned` | off | unchanged (dashed casing + facility color) |

**Deleted outright:** obstruction heat halos (`heat`), crash severity rings
(`crashes`), crash-cluster stations and `splitStations`, the dooring note, and
every read of `intersections.json` on this page. `intersections.json` remains
a transportation-map/pipeline artifact.

`DEFAULT_OVERLAYS = ["connecting", "mellow", "nodes"]`. The `?overlays=` URL
param keeps working with the new ids; unknown/legacy ids are ignored silently.

### Legend / side panel

- Line legend grouped **Trails** then **Street lines**, each row: color chip,
  name, termini.
- Quality legend block (the four grades) renders only while `quality` is on.
- Toggle list: Quality border · Connecting infrastructure · Mellow routes ·
  Nodes · Planned. Nothing else.

## 6. Quality border semantics

`GRADE_COLORS` are unchanged (`offstreet #0369a1`, `protected #0b6e4f`,
`painted #f59e0b`, `none #94a3b8`) and stay shared with the transportation
map and roster report cards. The *swap*: casing used to be a constant white
outline while grade colored the line; now the line is constant (line color)
and grade colors the border, opt-in.

## 7. Nodes (`site/data/network_nodes.json`)

New pipeline product. Two sources merged into one file:

1. **Interchanges (derived):** `build_network_nodes(main_routes_gj,
   orientation_points)` in `aggregate.py`. Compute exact 2-D segment
   intersections between the member geometries of every pair of *distinct*
   lines (pure python; no new deps). Merge intersection points within 150 m
   into one node (centroid), collect the set of `line_ids`. Emit only nodes
   where ≥ 2 distinct lines meet. Label = names joined with " × "
   (e.g. `"Milwaukee Line × Bloomingdale Trail (606)"`).
2. **Orientation points (curated):** new `data/orientation_points.json`,
   hand-picked major-road crossings that sit on roster lines, for wayfinding:

```json
[
  {"label": "Milwaukee / North / Damen", "lat": 41.9103, "lng": -87.6773},
  {"label": "Logan Square",              "lat": 41.9296, "lng": -87.7074},
  {"label": "Halsted / Fullerton",       "lat": 41.9254, "lng": -87.6484},
  {"label": "Lawrence / Western",        "lat": 41.9686, "lng": -87.6889},
  {"label": "Halsted / Roosevelt",       "lat": 41.8672, "lng": -87.6465},
  {"label": "MLK / 35th",                "lat": 41.8308, "lng": -87.6169},
  {"label": "Halsted / 63rd",            "lat": 41.7796, "lng": -87.6448},
  {"label": "Vincennes / 79th",          "lat": 41.7509, "lng": -87.6350},
  {"label": "Kedzie / Marquette",        "lat": 41.7715, "lng": -87.7027},
  {"label": "83rd / Cottage Grove",      "lat": 41.7434, "lng": -87.6046}
]
```

Output schema:

```json
{"nodes": [
  {"id": "node-001", "kind": "interchange", "lat": 41.91, "lng": -87.67,
   "label": "Milwaukee Line × Bloomingdale Trail (606)",
   "lines": ["milwaukee", "bloomingdale"], "data_tier": "derived"},
  {"id": "orient-001", "kind": "orientation", "lat": 41.9103, "lng": -87.6773,
   "label": "Milwaukee / North / Damen", "lines": [], "data_tier": "derived"}
], "data_tier": "derived"}
```

`refresh_reporting.py` rebuilds it alongside `main_routes.geojson`; `meta.json`
gets a `network_nodes` source entry (tier derived).

## 8. Trails

The Overpass pull is blocked by this environment's egress policy (proxy 403
on `overpass-api.de` and the kumi.systems mirror; Socrata is blocked too).
Fallback, per owner approval: **hand-traced curated geometry** in
`data/curated_trails.geojson` (tier `crowdsourced`, approximate, clearly
labeled — same provenance posture as the mellow routes).

Pipeline behavior: `aggregate.py` (and `refresh_reporting.py`) build
`site/data/osm_trails.geojson` from, in priority order:
1. `pipeline/raw/osm_trails.json` (real Overpass pull) via `build_osm_trails`;
2. `data/curated_trails.geojson` (this fallback), passed through with
   pipeline-computed `length_m`;
3. the existing stub.

Roster trail lines match the curated names via the existing `name_tokens`
mechanism and light up as major routes. Non-roster named trails (none in the
curated file; present once OSM runs) join the connecting-infrastructure layer.

## 9. Transportation map

**No changes.** It keeps per-segment grade coloring, crashes, obstructions,
wards, cameras — that is its identity. It picks up the re-cut roster
automatically via the rebuilt `main_routes.geojson`.

## 10. Out of scope

Safety data of any kind on the network map; mellow routes on the
transportation map; route-planning/directions features; palette perfection
beyond the screenshot review pass.
