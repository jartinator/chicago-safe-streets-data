# Main Routes ("Rail vs Bus") — Design & Handoff Report

**Date:** 2026-07-12
**Status:** Approved design (user-validated); handed to the *P3: D-p2 Improve UI* session for incorporation & execution
**Author session:** route-map-main-routes (worktree `route-map-main-routes-000a87`)

---

## 0. Why you (the UI session) are reading this

Your data-reporting-clarity plan (`docs/superpowers/plans/2026-07-12-oyl-data-reporting-clarity.md`)
deliberately scoped out "map.js/index.html layout, network.js layout." This document is that
missing piece, solved independently with the user: a **visual hierarchy for the route map**.
The user wants you to incorporate this into your work and execute it. Everything you need —
decisions already locked with the user, the data analysis receipts, the curated route roster,
pipeline + UI specs, tier rules, tests, and merge-order constraints — is below.

**The problem in one sentence:** both the geographic map (`index.html`) and the metro-style
network (`network.html`) render all 1,008 CDOT segments with equal weight, so the map reads as
spaghetti; the user wants a transit-agency distinction — a few **"rail" trunk lines** drawn
heavy, everything else demoted to a thin **"bus" local network**.

## 1. Decisions already made with the user (binding)

Asked and answered 2026-07-12 in the brainstorming session:

1. **Line concept = corridor with grade shown.** A "rail line" is a named street corridor
   end-to-end (e.g. *Halsted: 79th ⇄ Waveland*), drawn as one heavy line whose color varies
   **along its length** by facility grade. Not protected-segments-only, not a distorted
   schematic. The accountability story is the point: "the line exists; X% of it is unprotected."
2. **Roster = curated list, auto-filled.** The ~16 lines are hand-picked in a checked-in config;
   each pipeline run assigns real segments to them so grades/mileage stay live. No algorithmic
   promotion/demotion between runs; new lines are added deliberately.
3. **Off-street trails are first-class** — the user ranks the four grades:
   **off-street (prized) > protected > painted > nothing.** Originally this meant a new trails
   pull; that has since been **superseded by the OSM trails work** (see §2).

## 2. What changed since the design was drafted (revision, 2026-07-12)

The `claude/missing-chicago-trails-493a90` branch (13 commits, spec at
`docs/superpowers/specs/2026-07-12-osm-offstreet-trails-design.md` on that branch) landed the
off-street trails layer:

- Source is **OpenStreetMap via Overpass** (`pipeline/pull_osm_trails.py`) — CMAP was
  investigated and rejected (Chicago layers frozen at 2015–16); no city portal trail dataset
  exists. **Do not add another trails source.**
- Output `site/data/osm_trails.geojson`: **one feature per named trail** (grouped by OSM
  `name`), properties `segment_id` (`osm-trail-<slug>`), `name`, `facility_category: "trail"`,
  `length_m`, `data_tier: "crowdsourced"`. Stub-file fallback identical to the Mellow layer.
- Rendered on both map and network already, **on by default**, with `crowdsourced` badges.
- Hard rule from that spec, which this design inherits: **crowdsourced trail data never enters
  real/derived-tier statistics.**

Consequences for this design:

- Off-street "rail" lines (Lakefront Trail, Bloomingdale/606, Major Taylor, North Shore
  Channel, North Branch) are **matched from `osm_trails.geojson` by trail name** — no new pull.
- A main-routes line therefore has one of two provenances, and they must not blend:
  street lines (CDOT, `real` segments → line stats are `derived`) and trail lines
  (OSM, `crowdsourced` throughout).
- Trail geometry intentionally extends past the city line (their decision #2); render as-is.

## 3. The data analysis (receipts)

From `data/snapshots/bike_routes_2026-07-12.geojson` (1,008 CDOT segments, on-street only).
Citywide mileage by `displayrou`: Bike Lane 138.5 mi, Buffered 106.5 mi, Greenway 85.2 mi,
**Protected 68.7 mi**, Sharrow 47.0 mi.

Protected mileage is not scattered — it clusters onto a handful of named streets. Top corridors
by total mileage with facility mix (PBL = protected, BUF = buffered, BL = bike lane,
NG = greenway, SHR = sharrow):

| Street | Total | Mix (miles) |
|---|---|---|
| HALSTED | 13.5 | BL 5.0 · PBL 4.1 · BUF 3.9 · SHR 0.4 |
| DAMEN | 13.3 | BL 8.6 · BUF 3.0 · PBL 1.5 |
| KEDZIE | 11.1 | BL 6.7 · PBL 2.9 · BUF 1.5 |
| MILWAUKEE | 10.7 | **PBL 5.1** (most in city) · BUF 2.1 · BL 1.8 · SHR 1.6 |
| ELSTON | 9.6 | BUF 8.2 · PBL 1.0 |
| CLARK | 6.8 | PBL 2.8 · BUF 1.9 · BL 1.6 |
| LAKE | 6.6 | **PBL 4.5** · BUF 1.4 — most complete E-W protected corridor |
| JACKSON | 5.1 | PBL 2.2 · BUF 2.3 |
| WASHINGTON | 5.6 | BUF 4.0 · PBL 0.7 |
| VINCENNES | 4.9 | BUF 3.1 · PBL 1.8 |
| INDIANA | 4.4 | **PBL 3.0** (single continuous run) · SHR 1.4 |
| HARRISON | 4.1 | PBL 2.3 · BL 1.7 |
| BELMONT | 3.8 | PBL 1.9 · BL 2.0 |
| DEARBORN | — | PBL 1.9 (the two-way Loop lane) |

Headline the treatment will surface: Chicago has ~3 finished-feeling lines (Milwaukee core,
Lake, Dearborn), a dozen aspirational trunks that are 20–40 % protected, and the prized
off-street corridors now arrive via OSM at crowdsourced trust.

## 4. Grade taxonomy (4 grades)

User-specified, mapped from the published `facility_category` on each segment:

| Grade | From `facility_category` | Render color | Notes |
|---|---|---|---|
| `offstreet` | `trail` (osm_trails features) | `FACILITY_COLORS.trail` `#0369a1` | crowdsourced tier |
| `protected` | `protected` | `FACILITY_COLORS.protected` `#0b6e4f` | |
| `painted` | `buffered`, `painted`, `greenway` | `FACILITY_COLORS.painted` `#f59e0b` | buffers/greenways are still just paint & signs |
| `none` | `sharrow`, `other` | `#94a3b8`, dashed | sharrows count as nothing |

True corridor gaps (stretches with no CDOT segment at all) are **holes in the line, not drawn**
— we never fabricate geometry (provenance ethos). The per-line completion bar (§6) carries the
"incomplete" message instead. Grade shares are computed over *existing* member mileage.

## 5. The line roster

Checked-in config `data/main_routes.json` (pipeline input, committed like other configs).
Assignment rules (§7) use it in order. Draft roster — implementers may tune bboxes after
looking at rendered output, but the line list itself is user-approved:

**Trail lines** (`source: "osm_trails"`, match on normalized OSM `name` containing the token;
verify exact names after the first live Overpass pull — fixture only guarantees "Lakefront Trail"):

| id | name | termini label |
|---|---|---|
| `lakefront` | Lakefront Trail | Ardmore ⇄ 71st |
| `bloomingdale` | Bloomingdale Trail (606) | Ridgeway ⇄ Ashland |
| `major-taylor` | Major Taylor Trail | Dan Ryan Woods ⇄ Whistler Woods |
| `north-shore-channel` | North Shore Channel Trail | Green Bay Rd ⇄ Lawrence |
| `north-branch` | North Branch Trail | Gompers Park ⇄ Botanic Garden |

**Street lines** (`source: "bike_routes"`, match on uppercased `street` property; normalize
suffix variants — the raw data contains e.g. both `RANDOLPH` and `RANDOLPH ST`):

| id | name | termini label | streets | clip |
|---|---|---|---|---|
| `loop` | Downtown circulator | Loop | DEARBORN, CLINTON, DESPLAINES, RANDOLPH, WASHINGTON, WABASH | bbox ≈ (41.868, ‑87.647) – (41.900, ‑87.615) |
| `milwaukee` | Milwaukee Line | Downtown ⇄ Jefferson Park | MILWAUKEE | — |
| `halsted` | Halsted Line | 79th ⇄ Waveland | HALSTED | — |
| `clark` | Clark Line | River North ⇄ Devon | CLARK | — |
| `kedzie` | Kedzie Line | Brighton Park ⇄ Touhy | KEDZIE | — |
| `damen` | Damen Line | 81st ⇄ Bryn Mawr | DAMEN | — |
| `state-indiana` | State–Indiana Line | South Loop ⇄ Roseland | STATE, INDIANA | — |
| `vincennes` | Vincennes Line | 79th ⇄ Beverly | VINCENNES | — |
| `elston` | Elston Line | Goose Island ⇄ Forest Glen | ELSTON | — |
| `lake` | Lake Street Line | Austin ⇄ Fulton Market | LAKE | — |
| `jackson-washington` | Jackson–Washington Line | Austin ⇄ Loop | JACKSON, WASHINGTON | — |
| `belmont` | Belmont Line | Avondale ⇄ Lakeview | BELMONT | — |
| `31st` | 31st Street Line | Bronzeville ⇄ Lakefront | 31ST | — |

Notes: `loop` is listed **first** so its bbox claims the downtown WASHINGTON/STATE segments
before the couplet/state-indiana lines match the rest (first-match-wins, §7). Termini labels
are display copy on the config, not computed — they name where the corridor runs today, and
were inferred from segment extents (Halsted 41.740–41.951 ≈ 79th→Waveland, etc.).

Everything not matched to a line = the **local ("bus") network**, rendered thin/muted.

## 6. Pipeline spec

New builder in `pipeline/aggregate.py` (mirrors existing builder patterns):

`build_main_routes(routes_gj, osm_trails_gj, roster)`:

1. For each roster line in order, collect member features: street lines match segments whose
   normalized `street` is in `streets` and (if `clip`) whose geometry midpoint falls in the
   bbox; trail lines match `osm_trails` features by normalized name. First match wins;
   a segment joins at most one line.
2. Tag each member with `line_id` and computed `grade` (§4 mapping).
3. Emit `site/data/main_routes.geojson`:
   - `features`: the member segments (geometry passthrough) with properties
     `{segment_id, line_id, grade, facility_category, length_m, crashes_within_30m (street only), data_tier}`.
   - top-level `lines` key (same FC-level-metadata pattern as stub notes): per line
     `{id, name, termini, source, data_tier ("derived" for street lines, "crowdsourced" for
     trail lines), miles_total, miles_by_grade, pct_protected, crashes_total
     (street lines only — sum of member crashes_within_30m; omit for trails, never fabricate)}`.
4. `pct_protected` = (protected miles) / (total member miles). Street lines can only contain
   protected/painted/none grades (trails come from the other source), so this is the whole
   story for them; trail lines are 100 % off-street by definition and get no percentage.
5. When `osm_trails.geojson` is a stub (no live pull yet), trail lines appear in `lines` with
   `no_data: true` and zero features — UI shows them greyed with the stub badge, mirroring
   the map's existing `_mellowStub` handling.
6. `meta.json` gains a `main_routes` source entry, tier `derived`.
7. **CONTRACT_VERSION**: your plan bumps to 1.7; this lands after → bump to **1.8** and add the
   `main_routes.geojson` contract + `data/main_routes.json` roster format to `SCHEMA.md`.

No new pull stage. `run_all.py` untouched (aggregate-only change). Works identically in
`--fixtures` mode — add a couple of roster streets to the fixture corridors if needed.

## 7. UI spec

### index.html (geographic map)

- New default-on layer `mainroutes` (label "Main routes", tier badge `derived`) added to
  `LAYERS`; the existing `infrastructure` (all 1,008 segments) and `trails` layers become
  **default-off** (they remain available as the "all detail" view — keep their URL param
  behavior; update the default `layers` string). This does *not* revert the trails branch's
  "trails visible by default" decision: the major trails stay visible by default as roster
  lines inside `mainroutes`; only the full every-named-trail OSM layer moves behind the
  detail toggle.
- Render main-route members grouped by line: casing (white/`#fff` 8px, existing
  `casingPane` idea from network.js) under a 4.5px colored stroke per **grade** (§4 colors);
  `none`-grade dashed. Local network unchanged when its layer is toggled on.
- Click a line member → line detail panel (use your new primitives:
  `.card-heading` + tappable `badgeHTML(line.data_tier)`):
  - name + termini ("Halsted Line — 79th ⇄ Waveland")
  - **completion bar**: single stacked horizontal bar of miles_by_grade in grade colors —
    this is the report card; add the printed number "`{pct}` % protected"
  - crashes along line (real badge) for street lines; length + crowdsourced notice for trails
  - "Where does this come from?" → `BSD.openModal` with tier explainer + link
    `sources.html#src-main_routes` (add the source card, §8)
- Roster panel (side panel section, above layer controls or via a "Lines" button): the full
  line list, each row = name + mini completion bar + pct; click → fitBounds to line + detail
  panel. This is the at-a-glance report card the user wants.

### network.html (metro view)

- This page currently gives *every* segment the metro treatment — that is the reported
  "too detailed" problem. Change: roster lines keep the heavy casing+line+stations treatment
  (grade colors along the line); **non-roster segments drop to a 1.5px muted `#cbd5e1`
  background network** (the "bus" layer), no stations/labels below `LABEL_MIN_ZOOM`.
- The existing `?corridor=` deep links keep working (corridor = street name); add `?line=` for
  roster lines if cheap, else map line clicks onto the existing corridor mechanism.
- OSM trail features on this page inherit their existing rendering but roster trails get the
  heavy treatment + label.

### Findings cross-link (optional, cheap)

Your Task 5 `protected-share` finding ("How much of the network protects riders") is the same
story as the roster report card. After main routes land, point its `map_state` at
`{screen: "map", layers: ["mainroutes"]}` and/or append "See the main routes →".

## 8. Docs & sources

- `sources.js`: add a `main_routes` card — tier `derived`, origin "Computed from CDOT Bike
  Routes + OSM trails roster", description of the curated-roster method, limitation: "the
  roster is editorial: we chose which corridors count as main routes; segment grades and
  mileage are computed from source data each run." This honesty note is required — the user's
  project is "on the record."
- `README.md` data-sources table row; `SCHEMA.md` contracts (§6).
- `DECISIONS.md`: record the roster-is-curated decision and the rail/bus rationale.

## 9. Tests

- `pipeline/tests/test_aggregate_main_routes.py`: first-match-wins assignment (loop bbox claims
  downtown WASHINGTON before jackson-washington), suffix normalization (`RANDOLPH ST` →
  `RANDOLPH`), grade mapping incl. greenway→painted and sharrow→none, pct math, trail matching
  by name, stub-trails → `no_data` lines, crashes_total absent on trail lines.
- `tests/ui/main-routes-model.test.js`: pure helpers (grade→style, completion-bar segment
  widths, roster ordering) in a new `main-routes-model.js` following the existing
  `map-model.js`/`network-model.js` pattern (window.BSDMainRoutes + module.exports).
- Existing suites must stay green: `python -m pytest pipeline/tests -q` and `node --test tests/ui/`.

## 10. Merge order & conflict map (important)

Three concurrent workstreams touch the same files. Recommended order:

1. **Trails branch** `claude/missing-chicago-trails-493a90` merges first (it's complete).
2. **Your data-reporting-clarity branch** rebases on that (conflict surface: `map.js` —
   trails added a layer + changed the `loadJSON` array; `sources.js`; `aggregate.py`;
   `config.py`; `run_all.py`; `make_fixtures.py`).
3. **This main-routes work** is implemented by you on top of both (as new tasks appended to
   your plan, or a follow-up branch). It depends on: trails branch's `osm_trails.geojson`
   (hard dependency for trail lines) and your Task 2 primitives (`openModal`, tappable
   `badgeHTML`) for the line panel.

If you implement main routes before your Task 2 lands, fall back to plain badges — but the
natural sequencing is after Task 2.

## 11. Open knobs (implementer's judgment, everything else is decided)

- Exact `loop` bbox and whether WABASH belongs in it or in `state-indiana`.
- Whether 31st/Belmont make the roster cut visually — keep them unless they read as clutter.
- OSM trail name matching tokens after the first live pull (fixture guarantees only
  "Lakefront Trail").
- Stroke weights/zoom breakpoints; midpoint-in-bbox vs any-point-in-bbox for clip matching.

---

*Analysis provenance: all mileage/extent figures computed 2026-07-12 from
`data/snapshots/bike_routes_2026-07-12.geojson` (CDOT Bike Routes `hvv9-38ut`, 1,008 features);
trails facts from the `claude/missing-chicago-trails-493a90` branch spec and diff; UI-plan
facts from `docs/superpowers/plans/2026-07-12-oyl-data-reporting-clarity.md` in the
`data-reporting-clarity-d2db77` worktree.*
