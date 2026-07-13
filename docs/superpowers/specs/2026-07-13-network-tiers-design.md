# Network map v2 — route tiers, comfort floor, quality regrade

**Date:** 2026-07-13
**Status:** approved — product of a full design cycle (owner feedback rounds +
a 5-persona research panel; see PR description for the research summary).
Supersedes the layer/toggle/coloring parts of `2026-07-12-network-map-distinction.md`;
its node derivation, panes, and data plumbing remain.
**Visual reference:** the Iteration-2 concept mockup (session artifact
`mockup-iter2.png`) — implementers should study it.

## 1. Tier model

Three tiers replace the flat major/connecting split. Filter by tier, not
pavement type.

| Tier | Definition | Treatment |
|---|---|---|
| **Trails** | Off-street, long-haul (the 5 roster trails) | weight 11, darkened-hue outline, "express" look |
| **Main routes** | Major on-street corridors, roster-curated | weight 6, white casing, one solid color per line |
| **Connectors** | Everything else that is rideable: non-roster bikeways + deduped mellow geometry. Stubs, links, transfers. | weight 2.5, dashed, opacity 0.75, neutral `#94a3b8`-family, identity-less |

Panel toggle rows carry a mini line-style swatch + one-line muted
description: "off-street paths" / "major on-street routes" / "short rideable
links between routes".

## 2. Roster (owner-signed count: 14 main + 5 trails = 19 lines)

Keep 14: milwaukee, elston, halsted, damen, kedzie, california, clark,
state-indiana, mlk-drive, jackson-washington, lawrence, marquette, **lake**
(comfort-floor flagship, 68% protected), **83rd** (only far-south crosstown).
**Demote to connectors: roosevelt, vincennes** — remove from the roster
config; their segments fall into the connector tier automatically. Trails
unchanged.

## 3. Quality regrade (4 independent levels; borders only; lines never break)

New `MAIN_ROUTE_GRADE_MAP`:

| Grade | From facility_category | Border |
|---|---|---|
| `protected` | protected | **solid green** `#0b6e4f` |
| `paint` | buffered, painted | **dashed green** `#0b6e4f`, dash 6,6 |
| `mellow` | greenway + mellow-derived geometry | **solid purple** `#7c3aed` |
| `none` | sharrow, other/unmatched | **dashed red** `#dc2626`, dash 6,6 — legend copy "none — ride with traffic" |

`offstreet` remains the grade for trail members but takes **no border**:
legend footnote "trails are off-street — no border needed". Border geometry
uniform everywhere (same px per side, same dash rhythm). Quality toggle
default **off**; grade legend shows only while on.

## 4. Mellow layer retirement + dedupe (pipeline)

The standalone mellow overlay dies. In the pipeline: buffer-match mellow
geometry against bike_routes (~25 m); overlapping mellow is dropped
(bike_routes wins); mellow-only remainders become **connector features**
with `facility_category: "mellow"`, `data_tier: "crowdsourced"`, emitted into
a new connectors product (or appended to the existing local-network path —
implementer's call, but the site must be able to draw connectors as ONE
tier). `mellow_routes.geojson` keeps shipping (other pages may read it);
the network page stops loading it.

## 5. Comfort floor (headline research finding: 4/5 demanded quality filtering)

Segmented control in the panel: **Any | Paint + | Protected only**
(default Any). Semantics: any main-route stretch whose grade is *below* the
floor **drains** — core renders thin (3px) neutral `#b6bec9`, borders
removed, geometry continuous (routes never break). At/above-floor stretches
keep full color + border. Trails always lit (above any floor). Connectors:
below floor → hidden entirely (they have no identity to preserve).
Floor state in the URL (`?floor=paint|protected`). Caption: "the network
that meets your bar stays lit — routes never break".

## 6. Shared tracks (interlining)

Mechanism, data-driven: allow a bike_routes segment to belong to MORE THAN
ONE roster line (build_main_routes currently first-match-wins — lift that
only for segments explicitly listed by multiple lines' street lists).
Rendering: where a segment carries 2+ line_ids, draw the strands
side-by-side (per-line offset, tight ~2px gap, one shared white casing,
**one shared quality border** wrapping both), and mark the ends of a shared
run with **capsule transfer markers** (white pill, dark outline, spanning
the strands) instead of plain circles. Legend row (small, in the quality
block): capsule glyph + "transfer — routes meet or share track".
The current roster has no shared streets, so this ships dark — covered by
synthetic-fixture tests, lights up when the roster gains an overlap.

## 7. Selection state

Click a route → its line gets weight +2 and a soft halo (~16px, 25% opacity
of the line color, in a pane under casings); all other routes dim to 0.6;
the detail card populates (name, tier, quality-mix bar with the four grades,
termini). Deselect on: click on empty map, Escape, or re-click of the
selected route — everything reverts. One selection at a time. Card slot
shows muted "appears when you click a route" when nothing is selected.
Investigate and fix the reported click bug on the current page (owner:
"some sort of opening click issue") while in here.

## 8. Panel (single column, per Iteration 2)

Top → bottom: "Route tiers" title · 3 tier toggles (swatch + description) ·
divider · Quality border toggle + 4-row grade legend + capsule row +
footnotes · caption "filter by tier · set your comfort floor" · Comfort
floor control · divider · detail-card slot · "All routes" roster: one row
per line (color dot · name · tiny quality-mix bar, no percentages),
grouped Trails then Main routes, scrollable. Row click = same as clicking
the line on the map.

## 9. Palette (primary-forward; free hue reuse — borders carry quality)

```
milwaukee #1d4ed8  elston #ea580c   halsted #dc2626   damen #eab308
kedzie #7c3aed     california #db2777  clark #0891b2  state-indiana #4d7c0f
mlk-drive #92400e  jackson-washington #6b21a8  lawrence #881337
marquette #1e40af  lake #a16207     83rd #15803d
lakefront #0369a1  bloomingdale #16a34a  major-taylor #ca8a04
north-shore-channel #0d9488  north-branch #3f6212
```
Damen (#eab308) keeps its white casing prominent — yellow needs it.

## 10. Defaults & URL

All three tiers on · quality off · floor Any · nothing selected.
`?overlays=` keeps working with ids `quality,trails,main,connectors,nodes,planned`
(legacy ids ignored); plus `?floor=`, `?line=`, `?corridor=` as today.

## 11. Out of scope

Transportation map (index.html) untouched. Mellow stays available to any
other page that reads it. Node derivation unchanged (nodes still computed
from line intersections; capsules only at shared-track ends).

## 12. Amendment (2026-07-13, later the same day): graded connectors

Owner request + light re-convene of the research panel (same 5 personas,
one follow-up pass; Option C below was unanimous). Amends §1's connector
row and §5's connector clause.

**Connectors carry a per-feature comfort grade** — same buckets as §3,
derived client-side from `facility_category` via the existing
`CONNECTOR_GRADE_MAP` (protected; buffered/painted → paint; greenway →
mellow; unknown/sharrow → none), `mellow_connectors.geojson` → mellow,
non-roster OSM trails → offstreet.

**Styling (hybrid hue + pattern, "Option C"):** weight 2.5, opacity 0.75,
identity-less — the subtle background effect is unchanged. Muted tints
echo the §3 grade colors; dash pattern is the redundant (colorblind-safe)
channel:

| Grade | Line |
|---|---|
| `protected` | **solid**, muted green `#4d8873` |
| `paint` | dashed 4,5, muted green `#4d8873` |
| `mellow` | dashed 4,5, muted lavender `#9a8fc9` |
| `none` | dashed 4,5, slate `#94a3b8` (today's look, unchanged) |
| `offstreet` | **solid**, slate `#94a3b8` (pattern says calm; neutral hue makes no facility claim) |

Tints are **always on** (owner call — the panel split 3–2 toward gating
behind the Quality toggle; owner's explicit ask wins). The Quality
legend (visible only while the toggle is on, per §3) gains a footnote:
connector tints share the grade colors, and grades reflect **facility
type, not a safety metric** (panel risk #1).

**Comfort floor applies per-grade** (replaces §5's "hidden entirely"
all-or-nothing): each connector hides when its grade is below the floor
and stays visible at/above it (`meetsFloor`). Floors now *reveal* the
qualifying background network instead of nuking the tier. Offstreet
passes every floor; mellow hides at Paint+ — a muted caption under the
floor control says so (panel risk #2): "floors hide connectors below
your bar — greenway links need Any".

Connector detail cards name the grade ("Protected connector", …) with
the same facility-type caveat. Corridor labels keep their existing
floor === any gate (a floored background is intentionally sparse).
