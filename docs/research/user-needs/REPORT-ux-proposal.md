# UX Proposal — OYL data access & visualization

*Output of the user-needs research study in this directory: 6 cited evidence
briefs → 9 evidence-grounded persona interviews (2 rounds each) → stated/
latent needs memos → this synthesis. Method limits at the end. Nothing here
is implemented; this document exists for maintainer review and decision.*

---

## Executive summary — decisions requested

The study's headline: **OYL's data is more trusted than its packaging.** The
badge/tier discipline was called "the single most professionally respectable
thing on this site" (NL planner) and "makes me take the whole project more
seriously" (US analyst) — but the artifacts people actually need are not
pages: they are **a ward-scoped one-pager, a screenshot that carries its own
caveat, and a sentence with a denominator in it**. And one asset actively
spends down the trust the rest earns: the mock obstruction layer.

Decisions requested (each maps to a numbered proposal below):

1. **Ship an exposure proxy now** (Divvy trips, proxy tier, loudly labeled)
   rather than waiting for real counts — P1. *Unanimous finding.*
2. **Demote the mock obstruction layer** off both map surfaces to a gated
   "preview/synthetic" page with watermarked rendering — P2. *Unanimous,
   deal-breaker grade.*
3. **Build the per-ward one-pager generator** (print-first, auto-generated
   from existing data) as the flagship new artifact — P3.
4. **Make provenance travel**: as-of dates + source + caveat baked into every
   card, export, and a new "share crop" affordance — P4.
5. **Open the methodology**: publish the index's math, expose components,
   split committee/floor legislative status — P5, P6.
6. **Add a resident register**: address search, plain-language route
   answers, one-tap action bundle; treat the network map as the resident
   surface — P7.
7. Approve the second tranche direction (equity context, gap candidates,
   menu-money verification, annual "bike account" moment) — P8–P11.
8. Approve the **alternative data source shortlist** (§ Alt data sources)
   — three near-term opens, two partnership asks, one FOIA continuation.

If only one thing ships from this study, participants' behavior says it
should be P3 (one-pager) with P4 (traveling provenance) built into it —
that combination converts OYL from "a site advocates check" into "the thing
advocates hand to power."

---

## How to read the proposals

Each proposal lists: the **job** (from stated/latent needs), **evidence**
(which participants; S=stated, L=latent-with-basis), **design response**
(smallest thing that does the job), **surfaces & contracts** touched,
**effort** (S/M/L for this static-site + Python-pipeline codebase), and
**success signal**. Persona ids abbreviate: NL (nl-network-planner), DK
(dk-kpi-strategist), UK (uk-ward-campaigner), US (us-bna-analyst), ADV
(chi-pro-advocate), WARD (chi-ward-office), CDOT (chi-cdot-planner), RIDER
(chi-everyday-rider), ORG (chi-community-organizer).

---

## P1 — Exposure proxy: "per rider, is my street risky, or just busy?"

- **Job:** Present crash concentration as risk, not popularity; arm users
  with the "ridership is not zero / ridership doubled and crashes didn't"
  sentence; stop experts from dismissing every count on sight.
- **Evidence:** All 9. S: NL, DK, UK, US, ADV, WARD, CDOT, RIDER. Explicit
  don't-wait-for-perfect: DK (twice, unprompted), CDOT, UK, WARD. Guardrails:
  skew caveat (UK, US), anti-disinvestment framing (RIDER-L, ORG).
- **Design response:** New pipeline pull of Divvy trip data (open, station
  level) aggregated to corridor/ward trip densities at **proxy tier**, named
  a *floor, not a denominator* (DK's words). Surfaces: (a) an "exposure
  context" line on corridor and ward views — "≥ N Divvy trips started/ended
  within 400 m in the last 12 mo"; (b) an optional trips-vs-crashes paired
  view (never a silent division into a rate); (c) a fixed caveat string —
  bikeshare skews by station coverage, income, and trip type — that travels
  with any surface showing the number (see P4). Explicit copy rule: a low
  exposure floor is never rendered as "low demand."
- **Surfaces & contracts:** new `divvy_exposure.json` (tier proxy) +
  SCHEMA.md; corridor rollups; ward table column (nullable); findings copy.
- **Effort:** M (new Socrata pull + aggregation; UI additions are small).
- **Success signal:** the README's own "not normalized by ridership" caveat
  can be rewritten from "we have nothing" to "here is the labeled floor";
  expert-persona re-run stops leading with the denominator objection.

## P2 — Contain the synthetic: mock obstructions off the map surfaces

- **Job:** Make it impossible for a rushed staffer, a cropped screenshot, or
  a church-basement audience to mistake invented data for real reports.
- **Evidence:** All 9 distrust; deal-breaker for US, ADV, WARD, ORG, NL.
  Badge-doesn't-survive-screenshot: CDOT (lived incident), NL, RIDER.
  "A toggle implies parity": DK. Recurring click-through: WARD-S.
  Real-or-nothing: ORG, UK. Real crowdsourced would be *more* trusted than
  official: RIDER.
- **Design response:** (a) Remove the mock layer from `index.html` and any
  default surface; (b) move it to a dedicated demo page framed as a
  *schema preview pending the Bike Lane Uprising conversation*, behind a
  recurring click-through; (c) watermark the map render itself (diagonal
  "SYNTHETIC" tiling) so any screenshot self-labels — rendering, not badges,
  is the mitigation that survives cropping; (d) keep the schema and swap
  story (CONTRIBUTING.md already does this well) — the *architecture* was
  praised even by hostile reviewers.
- **Surfaces & contracts:** index.html layer roster; new preview page; no
  contract change (file stays).
- **Effort:** S.
- **Success signal:** no surface exists from which a screenshot of synthetic
  data can travel unlabeled.

## P3 — The ward one-pager: OYL's flagship artifact

- **Job:** Replace the hand-built quarterly ward letter (ADV), feed the
  Monday-briefing folder (WARD), give the block-captain text thread a dated
  standing record (ORG), give a parent one forwardable fact + action
  (RIDER) — the same artifact, four rooms.
- **Evidence:** S: ADV, WARD, ORG, RIDER, CDOT, UK (6/9 independently
  described it). Audience-split requirement: ORG-S (leave-behind vs.
  packet), WARD-L (merchant packet), ADV-L (press vs. resident register).
- **Design response:** A print-first, per-ward page (50 pre-generated at
  build time — no server needed): ward KSI trend vs. prior 12 mo, %
  protected + % streets with bikeways (PR #16 columns), top corridor, one
  plain-language finding, alderman + contact, next relevant hearing +
  comment deadline, menu-money bike spend (verification-gated, see P10),
  as-of date and source footer on the page itself (P4). One toggle for
  register: **brief** (advocate/alderman framing) vs. **plain** (6th–8th
  grade reading level, one suggested action). A second-tranche "merchant
  packet" variant adds the CDOT economic-study citation and a peer-corridor
  comparison (WARD's split-screen ask). Print CSS so ⌘P produces the
  leave-behind; a "download PDF" affordance is not required for v1.
- **Surfaces & contracts:** new `ward/<n>.html` static pages (or one page +
  query param, pre-rendered); consumes existing `ward_safety_index.json`,
  `aldermen.json`, `hearings.json`, `menu_spending.json`, findings.
- **Effort:** M.
- **Success signal:** an advocate or ward staffer can produce a current,
  sourced, defensible one-pager for any ward in under a minute; the ATA-
  letter cross-check (ADV's ritual) reconciles or explains itself (P5).

## P4 — Provenance that travels: as-of, source, caveat on every artifact

- **Job:** Survive the screenshot, the CSV, the printout, and the eight-
  month-old number at a hearing; never let polish strip the caveat.
- **Evidence:** L with strong bases: ADV (exported caveats), RIDER (cropped
  cards in group chats), CDOT (standalone-artifact behavior), NL + ORG
  (per-number as-of; both one-strike-ish), WARD (point-in-time snapshots,
  "I look sloppy, not the dashboard"), DK (stale weekly = abandoned
  instrument). S: WARD (methodology-matched exports), ORG (paper).
- **Design response:** (a) Every findings card, table view, and one-pager
  renders a compact footer: *source • tier • as-of date • one-line caveat*;
  (b) CSV exports gain header comment rows carrying the same (documented in
  SCHEMA.md so parsers can skip them — or a sidecar `README.txt` in a zip if
  comment rows break consumers); (c) a "copy share image" button on cards
  that produces a self-contained PNG with the footer baked in (html2canvas-
  class, vendored — aligns with the no-CDN posture); (d) surface the git
  history OYL already has as a human-readable **data changelog** page
  ("what changed in this week's refresh"), answering WARD's snapshot
  workaround; (e) a visible site-wide "last refreshed" in the header of
  every screen, not just meta.json.
- **Effort:** S–M (footers/as-of S; share-image M; changelog S given git).
- **Success signal:** any artifact found in the wild — screenshot, print,
  CSV — identifies its source, date, and biggest caveat without the site.

## P5 — Open the math: methodology page + de-blended index

- **Job:** Let a user recite the provenance and weighting out loud against a
  CDOT engineer; prevent the "political-will score wearing a danger score's
  clothes" failure; kill the higher-is-safer misread.
- **Evidence:** S: NL (Fietsbalans-style public weighting), US (components
  separately, window/stability), ADV (recitable methodology, severity
  weighting), DK (sub-scores, "the number under the number"), ORG
  (direction cue). L: US (bivariate view — he builds it by hand every
  time), ADV (date cutoffs/severity definitions documented so mismatches
  vs. her letters are explainable), WARD (ranking as press liability —
  wants trend context adjacent).
- **Design response:** (a) A METHODOLOGY page (site + repo) covering: index
  formula and why-percentiles, crash windows and boundary vintage (2023
  remap — name it), severity definitions (already in SCHEMA.md — surface
  them), coverage denominator definition (PR #16's 3,945 mi: classes,
  exclusions), facility-category mapping vs. CDOT raw values; every derived
  number links here ("why this number") in one click. (b) Ward table: show
  the two component rates as first-class sortable columns beside the
  blended score; add a small two-axis scatter (US's bivariate) on the table
  page. (c) Rename/re-caption the score to signal direction and relativity
  ("relative concern rank — higher = worse, ranked among wards, not absolute
  risk"). (d) Publish a short "if our number differs from ATA's letter"
  explainer covering window/definition differences (ADV's and WARD's
  number-one abandonment trigger).
- **Effort:** S (page + captions) + M (scatter).
- **Success signal:** every derived figure on the site can answer "how was
  this computed" in one click; the index misread disappears in a persona
  re-run.

## P6 — Legislation: two-stage status; hearings as a first-class feature

- **Job:** Never let "passed committee" masquerade as "passed Council"
  (the Feb 2026 pattern); let a staffer whip votes from committee records;
  keep the one feature every Chicago participant loved (hearings + comment
  deadlines) reliable and visibly fresh.
- **Evidence:** S: ADV ("actively dangerous" collapsed status), WARD
  (committee roll-calls "the only number I'd stake a strategy on"), UK
  (sponsorship ≠ vote labeling must be loud; primary-source links). L: ADV
  (hearing feed must not inherit Legistar's staleness silently).
- **Design response:** (a) Represent legislative progress as explicit
  stages (introduced → committee [vote where recorded] → floor [vote] →
  outcome) rather than one status string — contract change to
  `council_records.json` records adding a `stages` array; keep `status` for
  compatibility. (b) Loud inline caption wherever sponsorship counts render:
  "sponsorships, not votes — most items pass by voice vote." (c) Every
  record links to its Legistar/Councilmatic source page (mostly exists —
  make it per-claim). (d) Hearings page shows fetch time and the eLMS
  source, with an explicit "check the official calendar before traveling"
  line — honesty about the exact failure ADV was burned by.
- **Effort:** M (pipeline stage extraction) + S (captions/links).
- **Success signal:** the Feb-2026-shaped error is unrepresentable in the UI.

## P7 — The resident register: address in, route answer out

- **Job:** Answer "is this route okay for us?" on a phone at a red light;
  let a room that doesn't know its ward find its corner; convert one
  grievance into one completed action; never scare without an action.
- **Evidence:** S: RIDER (route stoplight-summary, no jargon, no downloads,
  one-tap action bundle, weekly personal digest), ORG (address/cross-street
  search — "half my room doesn't know what ward they're in"). L: RIDER
  (fear→driving misread of crash dots; cards must survive cropping; rating
  must not contradict visible street reality without explanation). Evidence
  briefs: plain-language standards (6th–8th grade), smartphone-only usage.
- **Design response:** (a) Address/cross-street search (client-side against
  a pre-built street-segment index; no external geocoder — respects the
  static/no-server posture) that resolves to: containing ward, nearest main
  routes with their facility-grade mileage bars, and a **plain-language
  summary**: "Kimball: mostly protected lane. Milwaukee: painted lane —
  paint doesn't physically stop cars." Grades, not scores; no invented
  safety rating (RIDER's trust-model warning and NL's index critique both
  say don't ship a per-route safety score OYL can't defend). (b) Position
  the network map (post-PR #15) as the resident-facing surface: lane-type
  is the register RIDER cares most about — add the plain-language grade
  vocabulary there. (c) One-tap action block per location: 311 (with the
  "aggregate, not tickets" honesty), Bike Lane Uprising, alderman email
  (prefilled subject including the street) — RIDER has never emailed her
  alderman purely due to lookup cost. (d) Inline glossary: first use of any
  term (KSI, corridor, protected) expands in place; resident surfaces avoid
  the terms entirely. (e) Mobile pass on these surfaces specifically (not
  the whole site in v1).
- **Surfaces & contracts:** network.html + a new lightweight "my streets"
  view; `main_routes.geojson` already carries what's needed; action.html
  gets the bundle treatment.
- **Effort:** M–L (search index M; copy register S; mobile pass M).
- **Success signal:** the RIDER persona path — search street, get answer,
  take action — completes in under a minute on a phone without hitting one
  term she'd bounce off.

## P8 — Context welded to danger: equity + cause framing

- **Job:** Make the map say "skipped for forty years," not "war zone";
  flag where proxy data is blind; keep camera data from reading as safety.
- **Evidence:** S: ORG (race/income disinvestment layer; camera reframing
  or nothing), US (who's not in the data; enforcement-bias literacy), NL
  (cameras out of the safety narrative). L: ORG (narrative-defusing context
  on any crash-density view), WARD (loud-vs-dangerous 311 distinction —
  his hand-built spreadsheet), RIDER (camera "money grab" trust bleed).
  Evidence briefs: 311 underreporting research; ProPublica/UIC camera
  equity findings.
- **Design response:** (a) Ward demographic context (ACS: median income,
  race/ethnicity shares — the pipeline already pulls ACS population) shown
  beside crash concentration, framed as investment context, never as a
  score input. (b) A "data blind spots" annotation pattern: on 311 views,
  a fixed line — "few complaints ≠ few problems: reporting rates are lower
  in lower-income, majority-Black/Latino areas (cited)" — with the citation
  from the evidence brief. (c) Cameras move off the default safety map into
  an "enforcement" view captioned with the documented ticketing-equity
  context; violations never render as a safety proxy without that frame.
  (d) Crash-density views always co-render infrastructure absence (the
  cause layer) — never dots alone.
- **Effort:** M.
- **Success signal:** ORG's framing check — "what does this make Austin look
  like, and who's looking?" — has an answer designed into every danger view.

## P9 — Network gaps: from curated corridors to missing links

- **Job:** Show where the network *fails* (gap, discontinuity, grade drop),
  not only how curated routes grade out; justify asks on non-flagship
  streets.
- **Evidence:** S: NL (the gap map is the opening artifact of her
  engagements), UK (SCA-equivalent demand justification), US (stress/
  connectivity as the teachable visualization), RIDER (protected-vs-paint
  is her top signal — gaps are where that breaks). L: NL (machine
  candidates as hypothesis generator only, never authoritative).
- **Design response:** v1 (cheap, honest): per-main-route **gap ledger** —
  PR #15 already computes members and holes; enumerate the holes as
  first-class objects ("Halsted: protected ends at 26th, resumes 35th —
  1.1 mi unprotected") on the route report cards, labeled *derived,
  candidate gaps — field-verify before citing* (NL's epistemic rule).
  v2 (later, opt-in): grade-transition markers on arterial crossings.
  Full LTS/connectivity scoring is deliberately deferred — it's a
  methodology commitment OYL can't currently defend (P5 discipline).
- **Effort:** S–M for v1 (data exists; it's an aggregation + UI list).
- **Success signal:** an advocate can name a specific, bounded gap with
  mileage in an ask, sourced to OYL, with the field-verify caveat attached.

## P10 — Menu money: promised vs. delivered, verified or gated

- **Job:** Answer "you told us in 2021, where is it"; put a spend-vs-risk
  chart in front of a chief of staff without staking credibility on an
  unverified scrape.
- **Evidence:** S: WARD (promised-vs-delivered = his single biggest
  hours-saver; unverified figure burned his office before), CDOT
  (verification against OBM PDFs is disqualifying-if-absent), ORG (private
  use only until human-verified), ADV (promised-vs-delivered slice; joined
  to corridors), US (controlled taxonomy + ordinance-page citation). L:
  WARD (OYL owns the "delivered" side only; his provenance tiers stay his).
- **Design response:** (a) Gate the existing menu-money layer: render as
  "unverified extract — research lead, not a citation" until (b) a
  documented **verification workflow** exists — a contributor checklist for
  spot-checking ward-years against OBM source PDFs, with per-ward-year
  `verified: true/by/date` fields; verified rows graduate to citable
  styling. (c) Add bike-relevant project rows joined to segments/corridors
  where locations allow. (d) "Delivered" side v1: pair spend with the
  infra-growth trend OYL already computes per ward (snapshot diffs) — an
  honest partial answer to promised-vs-delivered that requires no new
  source. (e) Note which wards run participatory budgeting (a structural
  transparency difference — evidence brief).
- **Effort:** M (workflow + fields) — the verification labor itself is
  community work the design must invite, not code.
- **Success signal:** no unverified dollar figure can be read as citable;
  verified ones carry their check's provenance.

## P11 — The annual moment: a "Chicago Bike Account"

- **Job:** Give the data a recurring press/political event; pair progress
  with harm so politicians see something other than blame; state the city's
  own published targets next to actuals.
- **Evidence:** S: DK (cadence, targets-with-owners, the headline
  progress+harm chart he designed unprompted), NL (satisfaction/perception
  as the missing voice), UK (scorecard-as-annual-pressure model). Evidence
  briefs: Copenhagen Bicycle Account, Healthy Streets Scorecard, ATA's
  annual ward letters (the local rhythm to align with).
- **Design response:** An annually compiled, dated, versioned page/PDF:
  the year in KSI and coverage; the headline two-line chart (% protected
  rising vs. KSI, explicitly *not* divided while exposure data is proxy);
  city targets (Cycling Strategy 150 mi / 80% low-stress; Vision Zero) vs.
  measured actuals — OYL doesn't own targets, it *mirrors* the city's and
  shows the gap (DK's owner problem, honestly finessed); per-ward one-page
  annex reusing P3. Perception survey: flagged as an alternative-data
  aspiration (see below), not faked.
- **Effort:** M, mostly editorial; almost all data exists.
- **Success signal:** an annual artifact whose publication date journalists
  and ward offices can anticipate (the DK test: an event, not a feed).

---

## Kill list — what the research says NOT to build

1. **Report-status tracking / follow-up features.** RIDER's latent finding:
   she has no follow-up habit to serve — the need is a *confirmation
   moment*, not a tracker. 311's no-enforcement reality makes a tracking UI
   actively misleading. (RIDER-L, WARD's 311 framing, evidence brief.)
2. **A per-route or per-street safety *score*.** Every expert cross-examined
   the ward index; a street-level score would multiply the attack surface
   and RIDER abandons it the first time it contradicts her gut on a street
   she knows. Grades of *infrastructure* (observable, defensible) yes;
   composite safety scores below ward level, no. (NL, US, ADV, RIDER-L.)
3. **Crowd-editable contribution features.** ORG's evidentiary power depends
   on sole authorship; crowdsourced editing would keep real evidence out.
   An export/side-by-side path is the most OYL should do. (ORG-L.)
4. **More citywide findings volume.** The unit of persuasion is the ward and
   the corridor; citywide stats are raw material, not deliverables. Keep the
   findings set small and ward-linkable. (WARD, ADV, RIDER, UK.)
5. **The schematic network map as an advocacy artifact.** ADV: "marketing
   map"; CDOT/WARD: ignore it professionally. Don't add safety data back
   onto it (PR #15's separation is correct) — instead lean into what RIDER
   revealed: it's the *resident* surface (P7). No further investment for
   expert audiences.
6. **Silent tier promotions.** US's deal-breaker: mock→real without a
   visible changelog note retroactively poisons every badge. The changelog
   (P4d) is the mechanism; make tier changes its loudest entry class.
7. **Camera violations as a safety proxy anywhere.** Reframe as enforcement/
   equity data or drop from safety surfaces. (ORG, RIDER, NL.)

---

## Alternative data sources

Raised by participants or briefs; "synthesized" = identified by this study
as likely to exist and worth verifying. Ordered by feasibility.

**Near-term, open, volunteer-feasible**
| Source | What it gives OYL | Access | Caveats | Next step |
|---|---|---|---|---|
| **Divvy trip data** (Chicago portal / Lyft) | The exposure floor (P1) | Open | Station-coverage & income skew; bikeshare ≠ all cycling | Build `pull_divvy.py`; proxy tier |
| **Cook County Medical Examiner Case Archive** | Independent cyclist-fatality cross-check vs. CPD records | Open, daily-updated | Manner-of-death coding needs careful filtering | Small pull; reconcile annually; report divergences |
| **CMAP Bikeway Inventory System (BIS)** | Regional facility inventory to cross-check CDOT layer, esp. boundary wards | Open geodata | Regional cadence ≠ CDOT's | Diff against `bike_routes.geojson`; publish discrepancies |
| **CMAP My Daily Travel survey (2024–25 microdata)** | Mode-share and trip-purpose context; the only public "who rides" data | Open microdata | Sample-based; not corridor-level | Cite in methodology + annual account |
| **CDOT High Injury Network / High Crash Corridors** (public ArcGIS) | The severity-weighted corridor standard every expert benchmarked OYL against | Public dashboard/layers | City-produced; update cadence unclear | Ingest as a real-tier comparison layer; align findings vocabulary |
| **CDOT corridor economic study (2026)** | The merchant-objection rebuttal (WARD's packet) | Published report | Six corridors only | Cite in one-pager merchant variant |
| **Mapillary street imagery** | Crowd-verifiable facility auditing (verify "protected" claims, DK's cross-section need) | Open API, CC BY-SA | Coverage varies | Link imagery per segment on route report cards |

**Partnership asks (medium-term)**
| Source | What | Access | Next step |
|---|---|---|---|
| **Bike Lane Uprising** | Replaces the mock layer with the real thing — 65k+ reports, ward-sortable; the single most-demanded swap | Partnership (no public API) | The conversation the mock schema was built for; P2 makes OYL a safer partner |
| **Strava Metro** | Corridor-level relative volumes | **Free for advocacy orgs** since 2020 | Apply; if granted, becomes a second labeled exposure proxy (recreational skew caveat) |
| **CDOT counter data** (Chicago/Wells Eco-Counter; any manual counts) | Ground-truth calibration for proxies | Ask/FOIA | Request via existing FOIA channel (`docs/foia/log.md`) |

**Long-shots / flagged honestly**
- **IDPH Trauma Registry / EMS (NEMSIS)** — the HIN-grade injury fusion (US's
  magic wand); requires a data-use agreement; realistic only with an
  institutional partner. Park it; name it on the methodology page as the
  known ceiling of crash-data honesty.
- **IDOT statewide crash data** — superset cross-check (expressways,
  non-CPD); useful for a divergence note, heavy for routine use.
- **StreetLight / Replica** — enterprise pricing, no nonprofit tier found;
  only viable by piggybacking a CDOT/CMAP license.
- **Citation/adjudication outcomes** (Circuit Court e-Citation) — fragmented,
  FOIA territory.
- **Insurance/bike telematics** — no accessible dataset verified; omit.

**Synthesized (this study's own flags — verify existence)**
- **CDOT quarterly Bike Lane Mileage Tracker** — OYL already mirrors the
  concept forward from snapshots; verify whether CDOT will share install
  dates or historic tracker editions (this is CDOT-persona's #1 need and the
  FOIA in `docs/foia/cdot-bikeway-mileage-history.md` is the right thread —
  continue it).
- **Candidate questionnaires / pledge records** (ATA election questionnaires,
  BikePAC endorsements) — the UK pledge-tracker analog. If public editions
  exist per election, they're the missing "commitment" layer that
  sponsorship data can't provide. Handle as real-tier documents with dates.
- **School travel data** (CPS Safe Routes; crossing-guard postings) — RIDER's
  school-run frame and near-miss ask have no dataset today; Safe Routes
  program documents may be the nearest public object. Near-miss data itself:
  no credible public source — say so on the methodology page rather than
  proxying it.
- **Perception/satisfaction survey** — nothing exists for Chicago riders.
  A lightweight annual survey run *by an advocacy partner* (not by OYL,
  which is read-only by principle) mirroring FUB/ADFC barometer items would
  fill the European personas' loudest structural gap. OYL's role: publish
  the instrument design + host results at crowdsourced tier.

---

## Sequencing recommendation

**Tranche 1 — trust hardening + the artifact (S/M, highest evidence):**
P2 (mock containment) → P4a/b/e (as-of + traveling caveats) → P5a/c/d
(methodology page, captions, ATA-difference explainer) → P3 (ward
one-pager, brief+plain registers) → P6b/c (sponsorship captions, source
links) → P1 (Divvy exposure floor).

**Tranche 2 — reach + depth (M/L):** P7 (address search, resident register,
mobile pass) → P6a (stage model) → P9 v1 (gap ledger) → P8 (equity/context
framing) → P10 (menu-money verification + delivered-side pairing) → P4c
(share-image) → P11 (first annual account).

**Research follow-ups (before/during Tranche 2):** five real-human sessions
(ATA staffer, ward chief of staff, two everyday riders on phones, one West
Side organizer) validating P3's one-pager and P7's route answer; the BLU
conversation (P2 makes OYL presentable as a partner); Strava Metro
application; continue the CDOT install-date FOIA.

---

## Method limits (inherited verbatim in spirit from the researcher memo)

Simulated participants cannot reveal real usability failures, actual
political dynamics beyond documented cases, real task time-costs, or true
misreading rates. Persona episodes are invented texture around documented
practice: quotes evidence *need shape*, not fact. Confidence flags from the
per-interview memos worth repeating: the pro-advocate's specific exposure-
source list and the everyday rider's Divvy suggestion were improvised
in-character (the *acceptance of an imperfect proxy* is the reliable
signal, not the specific source); the ward chief's promise-tracker detail
is tidier than a real neglected document would be; one follow-up round
(chi-pro-advocate) failed procedurally and that interview is single-round.
Every proposal above meets the bar of 3+ independent participants from
different worlds, or is explicitly marked to a single persona whose need is
strategically load-bearing (P11's cadence: DK; P9's candidate-gap
discipline: NL). Real-human validation is scheduled in the sequencing, not
optional.
