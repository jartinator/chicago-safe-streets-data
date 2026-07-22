# UX Proposal — OYL data access & visualization (run of 2026-07-21)

*Output of the user-needs research study in this directory: 6 cited evidence
briefs → 9 evidence-grounded persona interviews (re-run against inventory
v1.14) → stated/latent needs memos → cross-interview synthesis → this
proposal. Method limits at the end. Nothing here is implemented; this
document exists for maintainer review and decision.*

Persona ids abbreviate: NL (nl-network-planner), DK (dk-kpi-strategist),
UK (uk-ward-campaigner), US (us-bna-analyst), ADV (chi-pro-advocate),
WARD (chi-ward-office), CDOT (chi-cdot-planner), RIDER (chi-everyday-rider),
ORG (chi-community-organizer). S = stated need, L = latent need with a
documented inference basis (see `interviews/*.md`).

---

## Executive summary — decisions requested

**What changed since the last run:** the previous report's two headline
proposals shipped and were *validated by this round* — demoting the mock
obstruction layer was called "the single biggest trust-earning move" (CDOT),
"the single best change" (US), "the single correct decision in this entire
update" (NL); and the ward one-pager is now the artifact four participants
say replaces a documented manual workaround (ADV's four-hour quarterly ward
letters, ORG's evening of Legistar cross-referencing, WARD's hand-built
defensive brief, UK's hand-assembled leaflet).

**The new headline: trust has moved up the stack.** With the data layer
broadly accepted, this round's failures happen where a number *travels* —
onto a printed one-pager, into an API payload, out of an AI assistant's
mouth, next to an unrelated score on the same page. The study's sharpest new
finding only exists because v1.14 juxtaposed two features: the BNA network
score beside raw crash counts creates an adversarial reading ("more bike
lanes causes more crashes" — UK; "score = safety" — US) that nothing on the
site currently rebuts.

Decisions requested (each maps to a numbered proposal):

1. **Adopt caveat-carriage as a standing rule per output channel** — print,
   plain-language register, API `_meta`, AI answers (P1). *Broadest support
   of any theme; effort S/M.*
2. **Put a visual and verbal wall between network-quality and crash-outcome
   numbers** wherever they share a surface, starting with the BNA card (P2,
   S effort — this is the cheapest high-severity fix in the study).
3. **Harden the one-pager** instead of expanding it: address-based entry,
   committee-vs-floor labeling, a Ward Wise reconciliation line, and visual
   tiering of certain-vs-uncertain numbers (P3).
4. **Surface freshness as data**: loud status-as-of on roster cards, BNA
   vintage on the card, an auditable public correction path (P4).
5. **Start the promise-vs-delivered ledger** from data OYL already has
   (snapshot-built mileage series vs. the city's published Cycling Strategy
   commitments), and pursue install dates as a FOIA ask (P5).
6. **Fix the agent layer's cheap trust gaps now** (copy disambiguation,
   refuse-don't-hallucinate guidance in `llms.txt`, machine-readable
   caveats), and defer everything else about it pending real-human signal
   (P6).
7. **Meet people at their own geography**: address→ward resolver and a
   community-area crosswalk (P7).
8. Approve the **kill list** (§ below) — notably: no preview/embargo channel
   for ward offices, no fabricated per-rider risk rates, no news sentiment
   scoring, no in-page chatbot.
9. Approve the **alternative data source shortlist** — two near-term opens
   (Divvy trips, Cook County ME cross-check), one FOIA continuation
   (install dates), one partnership ask (Bike Lane Uprising, now with a
   deadline attached — see P8).

If only one thing ships from this round, participants' behavior says it
should be **P1 + P2 together**: they protect the artifacts that already work
(the one-pager, the badge system, the new API) from the failure mode every
audience independently described — a true number, stripped of its caveat,
read as a claim it never made.

---

## Themes & evidence (affinity map + jobs ledger)

Full attributions and quotes live in `interviews/_synthesis-memo.md`; this
table is the jobs ledger over those themes.

| # | Theme | Job-to-be-done | Audiences | OYL coverage today |
|---|---|---|---|---|
| T1 | Caveat travels with the number | Repeat a number in a hostile or unsupervised context without it shedding its limitation | all nine | **partially served** — page copy is disciplined; print/plain-register/API/AI carriage is unaudited |
| T2 | Exposure denominator | Survive the "more riders, not more danger" rebuttal | ADV, US, NL, UK, RIDER (proxy now) vs. WARD, ORG (honest absence) | **unserved**, honestly disclosed; new BNA juxtaposition makes the gap *actively harmful* on findings.html |
| T3 | Synthetic-data containment | Never be the person who circulated fake data | all nine | **served** by the quarantine, with three residual exposures (existence, silent-decay of "pending", blast radius) |
| T4 | Ward one-pager | Hand power a page that survives the room | ADV, WARD, ORG, UK, RIDER | **partially served** — format validated, five precise conditions unmet |
| T5 | Freshness as first-class data | Cite a status without citing a zombie | UK, CDOT, US, WARD, DK, NL | **partially served** — fields exist (status_as_of, BNA version), prominence and correction path don't |
| T6 | Install dates / promise-vs-delivered | Adjudicate "what was promised and did we deliver" | CDOT, WARD, DK, ORG, ADV | **unserved** — the most-cited magic-wand item; snapshot history is the seed |
| T7 | Agent-layer trust | Let an assistant answer without laundering a caveat away | US, NL, UK, ADV, RIDER, WARD | **partially served** — structure praised, behavior untested, copy ambiguous |
| T8 | Self-locating geography | Find "my block / my community area", not ward NN | RIDER, ORG, WARD | **unserved** at entry (ward-number-keyed); community areas absent |
| T9 | Ranked numbers carry their rebuttal | Use a rank as ammunition without it becoming stigma | ORG, CDOT, DK, UK | **partially served** — caveats exist but are footnote-weight; "0–100" self-misreads as a grade |

---

## Proposals

### P1 — Caveat-carriage rules, one per output channel — effort S/M
**Job:** a number that leaves the page keeps its limitation (T1).
**Evidence:** CDOT (S), ORG (S — "survive the print"), UK (S — plain
register must keep "relative, not absolute"), US (L — caveats in `_meta`),
NL (S — tested propagation), ADV (L — recitable in one breath), DK (L).
**Design response (smallest per channel):**
- *Print/one-pager:* audit the print CSS and both registers so the safety
  index's "relative, not absolute", menu-money "proxy, not verified", and
  sponsorship "proxy, not a vote tally" lines are physically on the printed
  page. A checklist in CONTRIBUTING, not a new system.
- *API:* add a structured `caveats` array to each endpoint's `_meta`
  (machine-readable flags: `not_normalized_by_ridership`,
  `dooring_undercounted`, `recent_months_provisional`, `sponsorship_proxy`,
  per-file as applicable). Additive; CONTRACT bump per SCHEMA.md rules.
- *AI answers:* one paragraph in `llms.txt`: "when quoting a number, restate
  its caveat in the same answer; when asked for data OYL does not publish
  (ridership, obstructions), say so rather than estimating."
**Surfaces/contracts:** ward.html print CSS, api/v1 schemas (+ contract
bump), llms.txt.
**Success signal:** NL's adversarial protocol run against a real assistant —
five questions, zero caveat-stripped answers; a print audit of three wards'
one-pagers.

### P2 — Wall between network-quality and crash-outcome numbers — effort S
**Job:** prevent "score = safety" and "more lanes → more crashes" readings
(T2-new).
**Evidence:** US (S — "that's not what a BNA score says"), UK (L — the
adversarial reading emerged from the juxtaposition), WARD (L — unfamiliar
rankings read as press threats), CDOT (L — news volume vs. safety metrics
separation, same structural worry).
**Design response:** on findings.html, visually separate the BNA card
(distinct section header: "Network quality — not crash data"), add one
reconciliation sentence pre-empting the causal misread ("a growing network
and rising raw crash counts can both be true when more people ride —
see why we don't normalize"), and carry the BNA `version`/`as_of` (already
in the data) onto the card face. Same separation rule wherever news volume
sits near safety numbers (ward.html).
**Surfaces/contracts:** findings.html, ward.html copy; no contract change.
**Success signal:** a cold reader asked "is biking getting safer here?"
after seeing the page does not cite the BNA score as evidence.

### P3 — Harden the one-pager (don't expand it) — effort M
**Job:** hand power a page that survives the room (T4).
**Evidence:** ADV (S — three named kill conditions), UK (S), ORG (S),
WARD (S+L), RIDER (S+L), NL (L — composite-verdict risk).
**Design response:**
- Address-based entry: client-side point-in-polygon against the committed
  `wards.geojson` (no server), plus alderman-name lookup; RIDER knows her
  address and alderman, not her ward number.
- Committee-vs-floor: where `council_records.json` statuses distinguish
  committee action from floor votes, label them; where they can't be
  distinguished, say so on the sponsorship line (ADV's kill condition is
  the *conflation*, not the absence).
- Menu-money line names its source and links Ward Wise, with the divergence
  caveat on the same line (ADV: her audience cross-checks live; ORG: he
  phone-verifies anyway).
- Visual tiering (NL's composite-verdict fix): group the page into
  "measured" (crashes, mileage) vs. "derived/proxy" (index, menu money,
  sponsorship) bands so three uncertain numbers can't read as one verdict.
**Surfaces/contracts:** ward.html; possibly a small `committee_vs_floor`
field addition in council records (contract-additive).
**Success signal:** ADV's three kill conditions each individually
addressed; a printed one-pager passes ORG's church-basement read-aloud test
without him adding spoken caveats.

### P4 — Freshness surfaced, corrections auditable — effort S/M
**Job:** cite a status without citing a zombie (T5).
**Evidence:** CDOT (S — stamp + fast correction path; L — non-editorial
flag channel), US (L — zombie projects; BNA vintage), WARD (L — staleness
is what he expects to be caught by), UK (S — measurement dates), DK (S —
dated editions), NL (L — granular OSM currency).
**Design response:**
- Make `status_as_of` + a "last checked" line the visual lead of each
  proposed-project card (field already exists — prominence fix).
- Public correction path: a "flag an error on this card" link opening a
  pre-filled GitHub issue (auditable, non-editorial, no accounts on OYL
  itself — satisfies CDOT's independence framing).
- BNA card carries analysis version + date (P2) and a one-line OSM-currency
  note; granular per-ward currency (NL) goes to the kill list — the
  upstream endpoints don't publish it.
- Editions (DK): cheapest honest version is a dated "what changed" page
  generated from `meta.json` history / git tags, not archived page
  snapshots. Classify as tranche 2.
**Surfaces/contracts:** ward.html / findings.html cards, one new static
changelog page; no contract change.
**Success signal:** a stale-status complaint arrives through the flag link
instead of through a CDOT PM's meeting; card-face dates visible in a
screenshot.

### P5 — Promise-vs-delivered ledger — effort M (data), L (full vision)
**Job:** adjudicate "what was promised and did we deliver" (T6) — the
study's most-cited magic-wand item.
**Evidence:** CDOT (S — her #1, above ridership), WARD (S — "settles more
arguments than any crash number"), DK (S — committed-vs-delivered as a KPI),
ORG (S — before/after tied to a named community process), ADV (workaround).
**Design response (smallest first step):** a findings card + small view
pairing the city's *published* Cycling Strategy mileage commitments (dated,
owned public promises — also answers DK's "no number is a target" critique
without OYL minting targets) against the snapshot-built
`bikeway_mileage_series.json`. Label the series' limitation honestly
(forward-built, no install dates). In parallel: FOIA CDOT for install-date /
as-built records (alt-data §; the repo's FOIA machinery already exists).
Full corridor before/after remains blocked on install dates — say so where
the card lives.
**Surfaces/contracts:** findings.json (new derived card), possibly a small
`commitments` input roster (curated, like main_routes.json).
**Success signal:** DK's one slide ("committed vs. delivered lane-miles
this year") can be built from OYL alone.

### P6 — Agent-layer: cheap fixes now, the rest waits — effort S
**Job:** an assistant answer that can be trusted or safely distrusted (T7).
**Evidence:** RIDER (S — provenance; L — chatbox-vs-external confusion is a
*documented live misreading*), ADV (S — refuse, don't invent), UK (S — same
published files, said loudly), NL (S — tested propagation), US (L —
in-payload caveats), WARD (L — blindside vector).
**Design response:** three copy-level changes: (1) home-page agent section
states plainly "this is not a chatbox on this site — it lets an AI tool you
already use read our published files, the same ones you can download";
(2) `llms.txt` refuse-don't-hallucinate + caveat-restatement guidance (P1);
(3) the "same files a human can download" sentence UK asked for, verbatim,
on the home page. Defer anything heavier: seven of nine memos flag their
agent-layer reactions as extrapolated; buy real-human signal before
investing further.
**Surfaces/contracts:** index.html copy, llms.txt.
**Success signal:** RIDER-profile tester correctly describes what the
feature is after reading the section once.

### P7 — Geography that matches self-location — effort S/M
**Job:** find "my street / my community area" without knowing ward numbers
(T8).
**Evidence:** RIDER (L — direct observed failure at the ward-number door),
ORG (L — twice-documented weekend-of-work crosswalk workaround), WARD (S —
corridor/block granularity, noted as blocked on P5 data).
**Design response:** the P3 address resolver covers entry. Add a
community-area ↔ ward crosswalk as a published data file (Chicago's 77
community areas are a stable open boundary set) and show community-area
names on ward pages ("Ward 28 includes parts of Austin, West Garfield
Park…"). Full community-area rollups are tranche 2 — the crosswalk alone
retires ORG's hand-built cross-reference.
**Surfaces/contracts:** one new small data file + ward.html line; additive.
**Success signal:** ORG can answer "which wards do I lobby for Austin?"
from the site in under a minute.

### P8 — Name the counterpart or set a sunset on the mock layer — effort S (decision, not code)
**Job:** keep the quarantine's trust win from silently decaying (T3).
**Evidence:** NL (S — "a real negotiation has a name attached"; her new
hardest-to-detect deal-breaker is a stalled "pending" becoming permanent),
ADV (L — existence itself is her bar), RIDER (S — "I'd rather it just say
'we don't have this yet, here's the Bike Lane Uprising link'"), WARD (S —
screenshot escape), DK (L — reason-at-point-of-encounter).
**Design response:** a maintainer decision with two acceptable outcomes:
(a) the Bike Lane Uprising conversation gets a dated, named, public status
line on the preview page (the outbox/tracker machinery in this repo already
manages that correspondence), or (b) after a set date without progress, the
preview page is retired in favor of a plain "no obstruction data yet — here
is BLU" link (which three participants prefer *today*). What is not
acceptable to this panel is the current undated "pending" persisting
indefinitely.
**Success signal:** the preview page shows either a named counterpart +
date, or is gone.

---

## Kill list — what this research says not to build

1. **A preview/embargo channel for ward offices** (WARD, L). It is the
   capture that ADV, ORG, and CDOT's independence framing all warn against;
   it breaks the no-accounts static model; it is one latent need from the
   study's most-extrapolated political simulation. The one-pager stays
   public and simultaneous for everyone.
2. **Any fabricated-precision per-rider risk rate.** WARD and ORG rank an
   honest "we don't know" above a shaky denominator; ADV's deal-breaker is
   a number she can't defend live. Exposure work proceeds only as loudly
   labeled proxy-tier context (P5/alt-data), never as a "risk rate."
3. **News sentiment/valence scoring** (WARD's favorability flag). Headline
   sentiment analysis is precision-hostile and would violate the news
   layer's validated precision-over-recall rule; a wrong "unfavorable" tag
   on an alderman-matched story is exactly the defect the layer was
   designed to never produce. The auditable `via` trail stays the answer.
4. **An in-page chatbot.** Nobody asked for one; RIDER's confusion is a
   copy problem (P6), and ADV/WARD's fears argue for fewer unsupervised
   answer surfaces, not more.
5. **A second synthetic layer of any kind, ever.** DK, ADV, and ORG
   independently describe total-catalog trust collapse on discovering one.
   Standing rule, not a feature decision.
6. **Network gap-analysis geometry** (NL's core professional ask). The
   planned-bikeway geometry doesn't exist publicly (verified 2026-07, and
   NL's memo accepts the roster "cannot answer" her question). Killed as
   UX; lives on only as the alt-data "planned geometry" watch item.
7. **Per-ward OSM-currency disclosure for the BNA score** (NL, L). Upstream
   doesn't publish it; approximating it would be manufactured precision.
   The citywide vintage line (P2/P4) is the honest ceiling.
8. **Push notifications / subscriptions** (RIDER, L). Conflicts with
   no-accounts by design; the static weekly refresh + forwardable ward
   one-pager URL is the substitute the model supports. (A generated weekly
   per-ward digest *file* — ADV, WARD, ORG each described one — is a
   legitimate tranche-2 candidate precisely because it needs no accounts.)

---

## Alternative data sources

Raised by participants or briefs, plus sources this synthesis judges likely
to exist. "Next step" is calibrated to a volunteer project.

| Source | Raised by | Access model | Chicago availability | Quality caveats | Realistic next step |
|---|---|---|---|---|---|
| **Divvy trip data** | ADV (S) | open download (Lyft/city) | station-level trips, current | not all cycling; station-area skew; system-area bias vs. West Side | **Near-term win.** Ward-level trip-density as proxy-tier exposure context (P5-adjacent) |
| **Cook County Medical Examiner case archive** | alt-data brief | open data portal, daily | 2014– | fatalities only | **Near-term win.** Annual fatality cross-check vs. crash layer; publishes as a findings caveat, not a new layer |
| **CDOT install dates / as-built records** | CDOT (S), WARD (S), ADV (workaround) | FOIA | unknown until asked | record quality unknown | **FOIA continuation** — repo's FOIA machinery + tracker #33; unblocks P5's full vision |
| **Chicago Cycling Strategy commitments** | DK (S, as "targets with owners") | published city documents | yes | commitments shift wording across editions | Curate into the P5 `commitments` roster with citations |
| **CMAP Bikeway Inventory System + My Daily Travel survey** | alt-data brief | open (CMAP Data Hub) | regional; 2024–25 survey wave public | suburban focus; survey is sample-based | Cross-check facility taxonomy; mode-share context for the exposure caveat |
| **311 request volume as engagement proxy** | ADV (S), US (S) | already in OYL | yes | self-report bias (already documented) | Reframe existing data as *engagement*, never exposure |
| **IDPH trauma registry / EMS (NEMSIS)** | alt-data brief; US's HIN world (L) | data-use agreement | statewide | aggregation, lag, DUA burden | Medium-term letter; the honest fix for dooring undercount |
| **Bike Lane Uprising** | ADV, RIDER, NL, brief | partnership | Chicago-founded | crowdsourced; litigated dataset — handle with care | P8: named/dated status or retire the preview |
| **Mapillary imagery** | alt-data brief | open API (CC BY-SA) | patchy | CV-derived; volunteer effort | Backlog: spot-audit facility categories on contested corridors |
| **Strava Metro** | brief; US (skeptical) | free for advocates | applicable | US's documented "BMX kid" rebuttal — sample skew is a live credibility risk | Do not lead with it; note as available if ever paired with counters |
| **StreetLight / Replica** | brief | enterprise SaaS | via CMAP/CDOT license only | opaque models | Long shot; ask CMAP if a license could be piggybacked, once, politely |
| **Cyclist satisfaction survey** | DK (S) | doesn't exist; would need a partner (ATA?) | no | self-selection unless designed well | Not OYL's to run; flag to ATA in any partnership conversation |
| **Planned-bikeway geometry** | NL (S) | doesn't exist publicly (verified 2026-07) | no | — | Watch item; re-verify annually |

---

## Sequencing recommendation

**Tranche 1 — high evidence, S effort, protects what already works:**
P2 (BNA wall — cheapest severe fix), P1 (caveat-carriage audit + API
`_meta` caveats + llms.txt guidance), P6 (agent-layer copy), P3's address
resolver, P4's card-face freshness + correction link, T9's "relative
comparison, not a grade" line on the index. P8 is a maintainer decision,
not code — make it in this tranche.

**Tranche 2 — M effort, needs the tranche-1 trust floor:**
P3's remaining hardening (committee-vs-floor, Ward Wise reconciliation,
visual tiering), P5's commitments-vs-delivered card, P7's community-area
crosswalk, Divvy exposure context, the weekly per-ward digest file, DK's
changelog/editions page.

**Research follow-ups with real humans (before any tranche-3 bets):**
1. An ATA-style advocacy staffer on the one-pager's three kill conditions.
2. A current or former ward staffer on preview/blindside behavior (tests
   kill-list #1's assumption).
3. Two or three residents on the home page → one-pager path and the
   AI-assistant copy (P6's success test).
4. A CDOT-adjacent planner on the correction-channel design (P4).

---

## Method limits

Carried from the lead researcher's candid list (see
`interviews/_synthesis-memo.md` for the full version):

- Simulated participants cannot reveal true usability failures — e.g.,
  whether an organizer can actually parse the percentile-blend methodology
  under meeting-prep time pressure.
- Nearly all agent-layer/AI-assistant reactions are extrapolations beyond
  the evidence bases (flagged in seven of nine memos). Direction is
  consistent (provenance anxiety, refuse-don't-hallucinate); intensity is
  unmeasured. Hence P6's copy-only scope.
- Real political dynamics are unknowable here: whether Chicago ward offices
  behave like the composite's blindside-averse model, and whether an
  embargo request would be followed by weaponization, are assumptions —
  which is why kill-list #1 pairs with follow-up #2.
- Imported frames may not transfer: London's borough-coordination problem,
  Copenhagen's edition ritual, and Dutch gap-audit practice are documented
  in their own worlds; their Chicago analogs are hypotheses.
- Individual memos self-diagnose their thin spots in `confidence_notes`
  (NL's too-fluent API test protocol, RIDER's AI-literacy read, CDOT's
  roster reaction); proposals resting mainly on those spots (P6, parts of
  P4) are deliberately scoped small.
- Persona simulation cannot measure actual Chicago rider behavior, real
  political retaliation, or true hostile-room dynamics; every proposal
  above is sized so that a wrong bet is cheap.
