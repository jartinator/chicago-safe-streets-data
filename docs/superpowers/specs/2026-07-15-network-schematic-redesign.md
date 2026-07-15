# Network map v3 — schematic spines: "One Spine, Four Inks, Earned Angles"

**Date:** 2026-07-15
**Status:** binding — product of a full studio cycle (three designer proposals →
draft direction → team review round; all review feedback adjudicated below,
including one blocking item, resolved in §3). Supersedes the quality-border
(§3), gap-filler, and drained-style (§5) parts of
`2026-07-13-network-tiers-design.md`; its tier model, roster, connectors
(incl. the §12 graded-connectors amendment), palette, interlining data model,
and comfort-floor semantics remain.
**Verified against:** `site/assets/js/network-model.js` and
`site/assets/js/network.js` at today's HEAD — every line reference below was
re-checked while finalizing.

Owner directives (outrank everything here): **#1** routes-not-roads,
**#2** quality is an attribute of the line — including a fourth level,
*nothing*, **#3** kill the wibble, **#4** connect and simplify.

## 1. Concept

Every roster line (14 street + 7 trail) is built at render time into **one
continuous spine**, schematized to long straight runs at disciplined angles,
pinned exactly through interchange nodes and shared termini, with quality —
including *nothing* — encoded as always-on structural "ink" on a
hue-constant stroke. The gap fillers, the Dijkstra detour router, and the
quality-border overlay are deleted. The transportation map (index.html)
stays geometry-faithful and untouched.

Invariant, stated once and enforced everywhere: **hue = identity,
structure = quality, dash = futurity** (planned overlay only, on roster
geometry — connectors keep their pre-existing background dash, see §10).

## 2. Spine pipeline (network-model.js, pure functions)

Three stages plus closure, per line, run once at load (21 spines, ~3k
post-RDP vertices — tens of milliseconds).

### 2.1 `buildSpine(members, opts)` → `{ points, measures, bridged }`

Order each line's member parts into one path reusing `chainPlan` /
`crossStreetGaps` (repurposed from gap-finders to spine orderers). Every
join wider than `GAP_JOIN_TOLERANCE_METERS` (30 m) is spliced **into** the
spine as a bridged range `{m0, m1}`, never emitted as a separate stroke.
`measures` are cumulative **original meters**; the measure map (original
arc-length → schematic arc-length) is the load-bearing abstraction — quality
stretches, node snapping, label anchors, and the panel's "nothing" mileage
are all lookups against it.

**Bridged-range measure convention:** original measure advances through a
bridge by the **chord length**, keeping the map monotone so
`gradeStretches`, `sliceSpineByMeasure`, and label anchors never
special-case bridges.

Interlined shared segments are schematized **once** per sorted `line_ids`
key and the canonical result spliced into every owning line's spine
(byte-identical across owners — enforcement mechanism in §7).

### 2.2 `detectRuns(points, opts)`

Iterative RDP via the existing `simplifyPart` at
`cornerToleranceMeters: 130`; merge adjacent segments with bearing
difference < `mergeAngleDeg: 15`; absorb runs shorter than
`minRunMeters` (600 streets / 400 trails) into their longer neighbor.

### 2.3 `snapRuns(runs, opts)`

- **Snap set:** `SCHEMATIC.AXES_DEG = [0, 45, 60, 90, 120, 135]` (mod 180).
  This is the complete six-axis family — the draft's "plus implied 120/150
  complements" phrasing was wrong (150 complements 30, which is in nobody's
  set) and is corrected here.
- Snap a run's length-weighted mean bearing to the nearest axis when within
  `snapToleranceDeg: 10`; otherwise round to `residualRoundDeg: 5`. Tight
  tolerance means angles are *earned* (owner: "notable angles where they
  occur").
- **Trails:** no axis gate; bearings rounded to `trailRoundDeg: 15` (the
  "Thames treatment" — the Lakefront keeps its shoreline character).
- **Minimum-bend post-pass (`minBendDeg: 30`):** the six-axis family
  permits adjacent runs to meet at 15° (45 vs 60, 120 vs 135) — visually
  indistinguishable from the wibble directive #3 kills. When two adjacent
  snapped runs' axes differ by less than 30°: merge them if the combined
  run still passes `snapToleranceDeg` against a single axis; otherwise
  re-snap the **shorter** run to the longer neighbor's axis. The 60/120
  family survives for genuine diagonals; soft corners are forbidden.
- The axis set ships as **one exported constant**; the six-axis vs
  `[0,45,90,135]` octolinear flip is decided on rendered downtown
  screenshots before merge (§13), crossing order the tiebreaker.

### 2.4 Closure — `closeRunLengths(runs, targetVec, lockedMask)`

With run directions fixed, minimize squared length adjustments subject to
the pinned end displacement: one 2×2 linear solve, exact closure
(< 1e-6 m), on-axis by construction — length-only adjustments never rotate
snapped bearings, which is what keeps pins crisp.

Two guarded degeneracies, both falling back to the **same** machinery
(45° jog inserted at the longest unlocked run's midpoint — no new code
path):

1. **Collinear:** all runs on one axis, displacement off-axis.
2. **Fold-back:** if any solved run length falls below
   `max(0, foldbackFraction (0.25) × original length)`, reject the solve
   and insert the jog. This bites first on short sections between close
   pins — post-collapse downtown blocks — not the collinear case.

`lockedMask` marks runs inside interlined shared segments: they carry
**zero** length adjustment; the solve distributes closure over unlocked
runs only (still 2×2). See §7.

### 2.5 Pins — `deriveControlPoints`, `snapSharedTermini`

The review round found the draft's pin constants internally inconsistent
(blocking: the Loop hub's own 314 m spread failed the shipped 300 m
constant). Reconciled here under four self-describing names; **tests
reference the names, not raw numbers**:

| Constant | Value | Job |
|---|---|---|
| `pinMergeGridMeters` | 250 | interchange nodes from `network_nodes.json` quantized to a merge grid |
| `pinAttractMeters` | 350 | line terminus → control point merge (governs the Loop hub: four termini within 314 m merge; a 360 m spread must not) |
| `terminusPairMeters` | 300 | terminus ↔ terminus merge in `snapSharedTermini` |
| `footSnapMeters` | 300 | terminus → another line's schematic spine, snapped to the perpendicular foot point |

The draft's orphan `pinSnap 150` is deleted.

**Explicit merges** (`SCHEMATIC.EXPLICIT_MERGES`): merges the owner's
directive #4 demands but that exceed the generic thresholds are declared,
not threshold-fished. One entry ships:
`{ id: "nw-terminus", lines: ["milwaukee", "elston"], end: "north" }`
(measured 532 m apart — a real place, one node). The Loop hub and the
North Shore Channel / North Branch river join (201 m) fall out of the
generic thresholds and need no entry. 312 RiverRun attaches as a branch
interchange pin. These are *visual* joins via pins — never roster merges.

Additionally, **both endpoints of every interlined trunk are mandatory
pins on every owning line** (§7).

Accepted pins split the spine into sections; each section is schematized
and closed independently (subject to `lockedMask`).

### 2.6 Displacement guard — `MAX_DISPLACEMENT_METERS = 250`

Any run whose **surveyed** original points deviate more than 250 m
perpendicular from the schematic is split at its worst point and refit
(depth ≤ 3, then RDP-130 fallback). This is the number the provenance copy
states; non-negotiable — it is what lets DECISIONS.md #10 relax without
abandoning the honesty ethos.

**Scope:** the guard applies only to measure ranges backed by surveyed
points. Bridged ranges are exempt **by definition** — they are declared
inventions, labeled *nothing*; a naive implementation measuring against
the synthetic chord would "pass" 6.4 km of invented line as faithful.
Fixture required: a 6 km bridged range never triggers a guard split.

Connectors keep today's RDP-40 geographic geometry (background texture,
off by default — all three proposals agreed).

## 3. `SCHEMATIC` constants (exported, network-model.js)

```js
const SCHEMATIC = {
  AXES_DEG: [0, 45, 60, 90, 120, 135],   // mod 180; flip-tested vs [0,45,90,135]
  snapToleranceDeg: 10,
  residualRoundDeg: 5,
  trailRoundDeg: 15,
  minBendDeg: 30,
  mergeAngleDeg: 15,
  cornerToleranceMeters: 130,
  minRunMeters: { street: 600, trail: 400 },
  maxDisplacementMeters: 250,
  foldbackFraction: 0.25,
  pinMergeGridMeters: 250,
  pinAttractMeters: 350,
  terminusPairMeters: 300,
  footSnapMeters: 300,
  EXPLICIT_MERGES: [{ id: "nw-terminus", lines: ["milwaukee", "elston"], end: "north" }],
  coupletMaxMeters: 800,
  coupletAngleDeg: 15,
  coupletOverlapMin: 0.6,
  minStretchMeters: 250,
  minStripePx: 1.5,
  minRailPx: 1,
  hollowFallbackOpacity: 0.45,
  drainedOpacity: 0.5,
  labelOffsetPx: 14,
  labelClearPx: 24,
  nodeDedupeMeters: 100,
};
```

New model functions: `buildLineSpine`, `deriveControlPoints`,
`detectRuns`, `snapRuns`, `closeRunLengths`, `schematizeSpine` (guard +
measure map), `snapSharedTermini`, `collapseCouplet`, `snapPointToPath`,
`gradeStretches`, `remapStretches`, `sliceSpineByMeasure`,
`QUALITY_LEVELS`, `displayGrade(grade)` (mellow→paint),
`fillPlan(grade, scaledWeight)`. Keep `chainPlan` / `chainGreedy` /
`chainByAxis` / `nearestOnChain` / `simplifyPart`.

## 4. Four-level quality: "Fill Level"

Continuity is structural: a line IS one spine, so it cannot render as
dashes of itself. Hue never changes along a line; quality is structure:

| Level | Treatment (street; base w6 hue over w9 casing, × weightFactor) |
|---|---|
| `offstreet` | solid hue over **darkened-hue band** (today's trail look — heaviest ink) |
| `protected` | solid hue over white casing |
| `paint` (+`mellow`, merged for display) | solid hue over white casing + **thin white center stripe** w2 — the line wears its painted stripe |
| `nothing` | **hollow** — hue rails with white core (bridged ranges and grade-`none` members both) |

### 4.1 Layer decomposition (resolves the casing contradiction)

The review round caught that "one shared casing polyline" contradicts
per-level casing colors. Resolution — **white is the only continuous
layer**:

- **One white w9 casing polyline per street spine** — no seams, all four
  levels, the whole spine.
- `offstreet`'s darkened-hue **band** is a per-stretch w9 slice rendered
  after the white casing in `casingPane` (visually identical to a darkened
  casing; structurally an underlay slice).
- Per-stretch **hue slices** w6 in `linesPane`.
- `paint`'s stripe and `nothing`'s core are per-stretch polylines rendered
  in **`linesPane`, immediately after their own spine's hue slices** — NOT
  in a global pane above everything. A global cores pane would knock a
  white channel through every line a hollow run crosses (where 83rd's
  6.4 km hole crosses Halsted, Halsted would appear to break — the exact
  read this redesign kills, inflicted on bystanders). Per-spine insertion
  order gives whole-line-over-whole-line stacking at crossings: the
  legible metro convention. **There is no `coresPane`**; `PANE_ORDER`
  (network.js:36–40) is unchanged.
- **Trails** keep `trailsOutlinePane` (band) + `trailsPane` (hue slices +
  cores, same within-pane ordering). Trail-vs-street z-order does not
  change.
- `fillPlan(grade, scaledWeight)` returns
  `{ band, stripePx, coreWidth }` — pure, unit-tested.

### 4.2 Low-zoom legibility

- **Hollow clamp:** core width = `min(0.6 × scaledWeight, scaledWeight − 2px)`
  so each rail keeps ≥ `minRailPx` (1 px); below that the stretch degrades
  to solid hue at `hollowFallbackOpacity` (0.45).
- **Stripe coarsening:** below `minStripePx` (1.5 px) paint drops its
  stripe and renders solid. The citywide read coarsens honestly to
  two-level — *built vs nothing* — and the four-level read returns on zoom.
  Both breakpoints are `SCHEMATIC` constants so QA can tune them.

### 4.3 Slice mechanics

`gradeStretches(members, spine, { minStretchMeters: 250 })` projects
member grades onto spine measure ranges; bridged ranges get `nothing`;
adjacent same-grade ranges merge; sub-250 m confetti absorbs into
neighbors; overlapping couplet parallels take the corridor grade per §6.
Stretch boundaries share vertices exactly (`remapStretches` guarantee).
**Interior slice caps are `butt`; `round` only at spine termini** — a
round cap on a protected slice bulges over the adjacent hollow core and
reads as a blob at every quality transition. Cap choice comes from the
stretch's position in the measure map.

### 4.4 Comfort floor (redefined)

Below-floor stretches keep their structural fill but drain hue to
`DRAINED_COLOR` at **full silhouette width** and **`drainedOpacity` 0.5**
— "routes never break" becomes literally true, and the opacity term keeps
a floor=protected map from becoming mostly wide gray (2–3× the ink of
today's weight-3 `DRAINED_STYLE`, network-model.js:316). Tune in QA with
the criterion "lit network pops in under a second". Same
`setStyle`-not-rebuild restyle path; `mainRouteRecords` become per-slice
records. Drained-vs-hollow disambiguation at z11 is an explicit QA gate
(§13); if they converge, the fallback is a hue-tinted casing on drained
slices.

### 4.5 "Nothing" copy

A bridged range is "no mapped facility," not confirmed sharrows. Legend:
**"nothing — no bikeway here; you ride with traffic."** No red, no dash.

## 5. Selection halo

`updateHalo` is NOT a mechanical rewire (it currently rebuilds from member
features' geographic geometry, network.js:249 — left alone it would draw
a 16 px ghost of the true alignment up to 250 m off the schematic stroke).
Rewire: **one halo polyline per selected spine** from the schematic
points — weight `16 × weightFactor`, line hue, 0.25 opacity, `haloPane`.
Less code than the per-member loop; aligned by construction.

## 6. Connect / merge / cut

**Connected** (all via pins, §2.5): Loop hub (Milwaukee / Clark / Lake /
Jackson-Washington downtown termini, within 314 m → one hub pin via
`pinAttractMeters`); NW terminus (explicit merge); river join (North Shore
Channel + North Branch at 201 m, 312 RiverRun branch); near-miss termini
(Marquette/Halsted, Kedzie/Marquette, Lakefront-adjacent trail ends via
`terminusPairMeters` / `footSnapMeters`).

**Couplet collapse** (`collapseCouplet`: parallel within 15°, < 800 m
apart, > 60% overlap → one fitted centerline): Jackson–Washington and
State–Indiana become single lines; Clark's Dearborn tail folds in.

**Couplet grade — decided WITH the geometry, not separately:** the
collapsed centerline renders the **better** grade of the pair. Worse-grade
would make a floor=protected view drain the whole corridor even though a
protected route exists on the ground — the one case where "we never invent
facilities" inverts into "we hide real ones." Disambiguation ships in both
surfaces: detail card gains *"Runs as a Jackson/Washington one-way pair;
protected eastbound on Jackson"* (adjust per data), and the same sentence
appears as hover/selected tooltip copy — the rider's confusion moment is
at the map click, not in the card. The two-parallels fallback remains a
reversible branch in `buildLineSpine`, judged at the QA gate (§13).

**Mellow → paint** in display everywhere; `GRADE_RANK` keeps mellow
distinct internally so the comfort floor and connector tints work
unchanged.

**Not merged (deferred):** the Milwaukee + Jackson-Washington L-shaped
through-run is a roster change rippling through pipeline metadata, deep
links, and panel identity — referred to the owner. The Loop hub pin
already makes them visibly meet. **Long holes stay honest:** 83rd's 6.4 km
and North Branch's 6.5 km gaps render as prominent hollow runs — that is
the advocacy point, not a bug.

## 7. Interlining (closure-invariant by construction)

The review round's sharpest catch: schematize-once + independent
per-section closure would silently stretch a shared trunk differently per
owner, breaking byte-identity. Mechanism, in order:

1. `deriveControlPoints` promotes **both endpoints of every canonical
   shared segment** (sorted `line_ids` key) to mandatory pins on every
   owning line.
2. The trunk is schematized and closed exactly **once**, keyed by the
   sorted `line_ids`.
3. Each owner's closure runs only on its sections outside the trunk, with
   trunk runs in `lockedMask` (zero length adjustment, §2.4).
4. Test byte-identity **after full per-line closure** on a two-owner
   fixture, not just after schematization.

Rendering on multi-strand records: **strands render solid hue always**;
the shared no-seam casing carries the structural treatment for the trunk's
grade (darkened band for offstreet; white for protected/paint; hollow for
nothing). Per-strand stripes/cores at 5–7 px strand spacing would moire.
"Shared trunk with grade none" joins the QA screenshot list; if it never
occurs in data, say so in the code comment and clamp to solid.

`planInterlinedRoute` consumes canonical schematic geometry; braids stay
byte-identical across lines; capsule bearings come from the schematized
shared run so pills sit truly perpendicular.

## 8. Labels & nodes

- Interchange nodes are pins — after schematization every interchange sits
  exactly on every line through it, by construction. Orientation nodes
  snap via `snapPointToPath`. Post-snap **100 m node dedupe pass**
  downtown.
- **Label anchors:** midpoint of the line's longest schematic run, offset
  `labelOffsetPx` (14) perpendicular. **Hand rule:** offset to the LEFT of
  increasing measure; flip when that side hosts another spine within
  `labelClearPx` (24 px) at the anchor (cheap check against the other 20
  spines' bounding segments) — without it, downtown's parallel spines
  coin-flip labels into each other. **Ship unrotated**; rotation is a
  cheap CSS follow-up.
- **Terminus labels:** line name at both spine ends, at `ZOOM.lineLabels`.
- Capsule dedupe, corridor labels, `BSDNet.ZOOM`: unchanged.

## 9. Panel

1. The "Quality border" toggle row (network.js:1026–1032) is **deleted**;
   in its place a permanent **"How to read a line"** legend: four
   structural swatches in a neutral hue, CSS-only, ordered
   offstreet → protected → paint → nothing top-to-bottom (heaviest ink to
   hollow, matching the mix bar). "Nothing" gets its full sentence; the
   other three stay one-word — deliberate emphasis on the level most
   likely to be misread as a rendering artifact.
2. **Mix bar basis (one denominator):** ALL four detail-card bar widths
   come from the spine's stretch measure ranges (sum of original-meter
   lengths per level via `gradeStretches` — the bar is literally
   proportional to the drawn line). Printed numbers for
   offstreet/protected/paint stay pipeline `miles_by_grade` (the honest
   number); the "nothing" figure is derived render-time and printed as
   **"about X mi with nothing built."** Spine-derived nothing **subsumes**
   the pipeline `none` bucket — never show both, never double-count.
3. **Nothing-chip measure domain:** computed from **pre-absorption**
   bridged + grade-`none` **original-measure** extents (m0/m1) — data
   truth, stable under display tuning (closure changes schematic lengths;
   absorption is a display parameter). Legend footnote: *"gaps shorter
   than ~250 m render as continuous."*
4. **Roster mini-bars:** the full four-ink swatch dialect doesn't survive
   60×6 px (hollow rails ~1.5 px). Bump `.mini-mix` to 8 px tall and use a
   degraded dialect: solid-dark / solid / the existing `grade-paint`
   diagonal hatch (style.css, already shipped and small-size legible) /
   hollow-as-1px-outline-box. Full literal swatches only in the detail
   card and legend, where they have room.
5. Paint bucket labeled **"paint & greenway"** (merged mellow miles must
   not mislead).
6. Provenance, twice: muted caption under the tier toggles + a corner
   chip — **"Schematic view — lines simplified, shifted up to ~250 m ·
   true geometry on the Map tab"** (verbatim).
7. Comfort-floor copy: "below your bar, stretches lose their color — the
   line never breaks."
8. **Orphaned legend footnotes** (network.js:970–971): deleting the
   quality legend deletes the only explanation of connector tints, which
   survive. Relocate the connector-tint sentence into the connectors
   tier-row description (or a conditional block shown only while the
   connectors toggle is on) so the explanation lives and dies with its
   layer. The trails footnote dies with the border concept.
9. Deep links `?line=`, `?corridor=`, `?floor=`, `?overlays=` survive;
   `?overlays=quality` joins the silently-ignored legacy ids (precedent:
   network-model.js:112–115). `fitLineBounds` fits the schematic spine's
   bbox.

## 10. Deliberate cuts

| Cut | Rationale |
|---|---|
| Gap-filler strokes (network.js:626–693, `layers.gapsMain`/`gapsTrails`, mounts at 784/787, `gapRecords`, `restyleGaps`, `gapSegments` export, `GAP_LIGHTEN`, `lightenColor`'s gap use) | Superseded by structural `nothing` — owner directive #2 verbatim. All three proposals. |
| Dijkstra detour router (`routeGapThroughConnectors`, `connectorEdges`, `routerEdges`, `ROUTE_GRADE_PENALTY`, `ROUTE_SNAP_PENALTY`) | The line just continues; a routed detour contradicts the spine model. If the "plausible detour" affordance is missed it returns as detail-card *copy* naming nearby connector streets, never geometry. |
| Quality border layer + toggle (`qualityBorderStyle`, `qualityPane` stays as a dormant pane slot or is removed with `PANE_ORDER` renumbered — implementer's call, weight-13 rims die either way) | Quality is intrinsic and always on. Note: deleting `qualityBorderStyle` removes `GRADE_DASHED`'s only consumer (verified: network-model.js:269 defines it, 283 is the sole use) — **delete both together**; connector dashes come from `CONNECTOR_STYLE`/`CONNECTOR_GRADE_TINTS` strings and are unaffected. |
| Mellow as a display level | Owner's four-level taxonomy; internal rank preserved. |
| `crossStreetGaps` as phantom-rung generator | Couplets collapse instead; survives only for spine ordering. |
| DECISIONS.md #10's literal geometry-faithfulness | Relaxed by the owner; survives as the 250 m guard + provenance copy (§14). |

**Dash rule, scoped exactly:** no dashes on roster lines; the planned
overlay owns dash on named geometry; connectors keep their pre-existing
dash as background-mesh texture (owner-approved Option C, tiers spec §12).

## 11. Implementation order

1. **network-model.js — spine + schematization** (pure, Node-testable):
   `SCHEMATIC` constants (§3) + the pipeline functions (§2). Keep
   `chainPlan`/`chainGreedy`/`chainByAxis`/`nearestOnChain`/`simplifyPart`.
2. **network-model.js — quality**: `gradeStretches`, `remapStretches`,
   `sliceSpineByMeasure`, `QUALITY_LEVELS`, `displayGrade`, `fillPlan`
   (with clamp + stripe coarsening). Delete router functions, `gapSegments`
   export, `qualityBorderStyle` + `GRADE_DASHED`.
3. **tests/ui/network-model.test.js** — retire router/gap tests; add the
   §12 fixture list. Run `node --test tests/ui/`.
4. **network.js — draw loop**: replace the `rosterFeatures.forEach` loop
   (line 533) and trail loop (564) with per-line `buildLineSpines()` →
   `drawSpine(lineMeta, spine, stretches)` (one white casing + per-stretch
   band/hue/stripe/core slices per §4.1, butt interior caps);
   `mainRouteRecords` per-slice; rewire `restyleMainRoute`/`applyFloor`
   (mechanical) and **`updateHalo` per §5 (explicitly not mechanical)**;
   delete the gap-filler section and mounts; interlined trunks per §7;
   nodes `snapPointToPath` + 100 m dedupe; labels per §8; `fitLineBounds`
   spine bbox.
5. **Panel + style.css**: legend, mix-bar re-encode + basis, mini-bar
   dialect, provenance caption + chip, floor copy, footnote relocation,
   delete quality toggle row.
6. **DECISIONS.md #10** replacement (§14, exact text).
7. **Visual QA gate** (§13) before merge.

## 12. Test fixtures (tests reference constant NAMES, not raw numbers)

1. Jittery street → one 90° run.
2. 8°-off bearing snaps to axis; 25° bend does not.
3. Closure exactness < 1e-6 m.
4. Pin pass-through: every interchange on every line through it.
5. Stretch-remap length conservation.
6. Displacement-guard split on a surveyed run > 250 m off.
7. **A 6 km bridged range never triggers a guard split.**
8. Couplet collapse (Jackson–Washington parameters) and non-collapse
   (a 900 m-apart pair).
9. **Loop hub: four termini at offsets 0/180/260/314 m all merge to one
   hub pin (`pinAttractMeters`); a 360 m spread does not.**
10. Terminus-pair merge at `terminusPairMeters`, foot snap at
    `footSnapMeters`.
11. **Shared-segment geometry byte-identical across owning lines AFTER
    full per-line closure** (two-owner fixture, `lockedMask` exercised).
12. Measure-map round-trip, fixture including one bridged range
    (chord-length convention, monotone).
13. Kedzie/California collinear-degenerate jog insertion.
14. **Fold-back guard: a 400 m section pinned both ends with 250 m
    displacement (and a two-200 m-run / large-displacement variant)
    rejects the solve and inserts the jog — spine never self-folds.**
15. **Min-bend: a 45° run meeting a 58° run emits a single run or a ≥ 30°
    bend, never a 15° elbow.**
16. `fillPlan`: clamp keeps rails ≥ 1 px; below → opacity fallback; stripe
    drops below `minStripePx`; band/stripe/core per grade.
17. Nothing-chip mileage = pre-absorption bridged + `none` original-meter
    sum; unaffected by `minStretchMeters` tuning.
18. Better-grade couplet: collapsed corridor passes floor=protected when
    either street does.

## 13. Visual QA gate (before merge; `/verify` flow + before/after
screenshots at citywide fit and z13 — baselines already captured)

1. **Six-axis vs octolinear flip** downtown; crossing order is the
   tiebreaker (the map is judged by what it draws, not the histogram).
2. **Hollow legibility at citywide zoom** + its emotional tone: 83rd's
   6.4 km hole should be loud — we believe loud is the owner's intent, but
   eyes-on decides; fallback is dashed-casing or opacity treatment.
   Also prototype the offset-rails hollow variant (§15.3) here.
3. **Drained vs hollow at z11 with floor=protected** — they mean opposite
   things ("good facility, below YOUR bar" vs "no facility at all") and
   must not converge; fallback = hue-tinted casing on drained.
4. **Crossings:** a hollow run crossing a solid line — no false break on
   the bystander (§4.1); whole-line stacking reads as intended.
5. **Quality-transition joints at z13** (butt caps, no blobs).
6. Jackson–Washington centerline: simplification or lie? (Two-parallels
   fallback branch ready.)
7. Milwaukee/Elston braid ends; connectors-on disagreement check;
   shared-trunk-grade-none if present in data.
8. Floor=protected full-map: lit network pops in under a second
   (drained opacity tuning).

## 14. Replacement text for DECISIONS.md #10 (exact)

> **10. The network map is a deliberate schematic; the geographic map
> stays geometry-faithful.** Screen 2 (network.html) draws each roster
> line as one continuous schematized spine: geometry is straightened to a
> disciplined angle set, interchanges are consolidated to shared pinned
> points, and positions are approximate by design — a drawn line may sit
> up to ~250 m from its true alignment (enforced by
> `MAX_DISPLACEMENT_METERS`). We still never invent facilities:
> connectivity, quality grades — including "nothing," which marks
> stretches with no mapped bikeway — and all quoted mileage come from
> source data, and the map carries an always-visible "schematic view"
> note. The transportation map (index.html) remains geometry-faithful and
> is the reference for where things actually are.
> - *(prior entries retained as history below)*

## 15. Considered and declined (review-round suggestions not adopted)

1. **Retire the connector dash** (design-engineer). Declined: connector
   dash is the colorblind-safe channel of the owner-approved "Option C"
   (tiers spec §12) — undoing an explicit owner call is outside this
   redesign's scope. Also corrected: connector dashes never came from
   `GRADE_DASHED` (they're literal strings in `CONNECTOR_GRADE_TINTS`),
   so no code change is needed to keep them. The dash rule is scoped
   instead (§10).
2. **`footSnapMeters: 150`** (cartographer's reconciliation number).
   Declined in favor of 300: the draft's prose and the §6 near-miss merges
   (Marquette/Halsted, Kedzie/Marquette) were designed against 300; 150
   was the orphan constant being deleted, not a measured requirement.
3. **Offset-rails hollow as the primary encoding** (information-designer's
   option (b)). Adopted only as a QA-gate prototype: option (a) — cores
   in `linesPane` after their own hue slices — fixes the crossing knockout
   with zero new geometry machinery; (b) reuses `strandOffsets` but makes
   every hollow stretch a multi-polyline special case. If (a)'s crossings
   misread at the gate, (b) is the named fallback.
4. **Worse-grade on collapsed couplets** (draft's own position, and
   cartographer's conservative alternative). Declined for better-grade
   with named-street copy (§6): the floor answers "can I ride here at my
   bar," and a protected route exists on the ground — hiding it inverts
   the honesty rule.
5. **Fold-back fallback via section re-split / RDP-130 unsnapped**
   (design-engineer). Declined for cartographer's jog insertion: it
   reuses the collinear-case machinery — one fallback path, not three.
6. **Lighten `DRAINED_COLOR` via `lightenColor`** (information-designer's
   alternative). Declined for the opacity term: one tunable knob
   (`drainedOpacity`), no second derived color to keep in sync.
7. **Strict octolinear axis set** (information-designer). Still declined
   on the two independent ~120–127° Milwaukee/Elston measurements and the
   owner's explicit non-mandate — but it remains one constant away and is
   screenshot-tested at the QA gate before this ships (§13.1).

**Referred to the owner** (outside team authority): cutting the
`?overlays=quality` deep-link behavior (brief's "deliberately, explicitly
cut" clause); the deferred Milwaukee + Jackson-Washington through-run
roster change.

## 16. Studio credits

- **Cartographer** (*True Diagonals*): six-axis family, exact on-axis
  `closeRunLengths` closure, pin/control-point geometry, Loop hub / NW
  terminus / river join measurements, dash-reservation rule, long-holes-
  are-the-point advocacy framing, DECISIONS #10 base text, min-bend and
  fold-back and guard-scope fixes from review.
- **Information-designer** (*Fill Level*): the four-ink structural
  encoding (paint stripe, hollow nothing, low-zoom clamp), hue-is-identity
  invariant, panel-as-miniature (legend, mix bar, swatches), drained-at-
  silhouette floor redesign, and the review round's biggest structural
  catch (the cores-pane crossing knockout) plus stripe coarsening,
  mix-bar basis, and mini-bar dialect.
- **Design-engineer** (*Spine & Snap*): three-stage pipeline architecture
  and the measure map, run-detection parameters from wibble measurement,
  displacement guard, couplet centerline collapse, no-seam casing (and
  its white-only resolution), honest-numbers panel split, provenance chip
  wording, ship-unrotated discipline, the blocking Loop-hub constant
  catch, halo rewire, bridged-measure convention, and interior-cap rule.
- **Creative director**: synthesis calls — axis policy + screenshot gate,
  closure choice, better-grade couplet pairing, cores-in-linesPane
  crossing fix, pin-constant reconciliation, scope cuts and owner
  referrals.
