# Validation verdict: PFB BNA proposal

Synthesis of six persona interviews (US, ADV, WARD, CDOT, RIDER, ORG —
transcripts and memos in `interviews/`) against
`docs/projects/pfb-bna-proposal.md`. Method: `00-protocol.md`. Advancement
rule: support from named participants across ≥2 audiences.

## Headline

**Three of four elements advance, all with changes; B4 dies.** The
surprise of the run: **B3 (segment stress cross-check) is the strongest
element across every audience** — it automates a fact-check that three
different participants already perform by hand (ORG's field walks, WARD's
"ask CDOT which street you'd let your kid ride on" calls, RIDER's
repeated-ride verification ritual). The most heavily conditioned element
is B2, and the conditions are structural, not copy: framing language does
not survive sortable tables, headline compression, or casual retelling.

## Per-element verdicts

### B1 — Citywide scorecard: ADVANCE WITH CHANGES

Would-use from ADV, WARD, CDOT, US, ORG (conditional); RIDER misread it
as a neighborhood grade and flagged discouragement risk.

Required changes:
1. **Never standalone.** The 11/100 card must ship with ward-level
   detail adjacent (ORG: a citywide number alone is "too easy to hide
   behind") and with a reconciliation sentence against OYL's own crash
   trend (ADV: it collides head-on with her "fatal crashes down 30%"
   talking point; she will not touch the number in a hostile room
   without a pre-written answer to "which is it?").
2. **Context on the 36.** State the comparison set (all rated cities vs
   large cities — Chicago ranks 73rd of large cities but 2,919th overall;
   US flagged the unqualified average as misleading either way).
3. **Anti-discouragement copy for residents.** One sentence: this grades
   the *network*, not the act of biking, and not your neighborhood
   (RIDER's misread is the predictable one).

### B2 — Ward access scores: ADVANCE WITH CHANGES (license-gated)

The most polarized element: strongest endorsement (ADV — "a genuinely
new argument"; CDOT ranked it #1 for her actual work) and the most
misread (3 of 6 — ADV, CDOT, RIDER — initially heard it as a danger
ranking despite the access framing).

Required changes:
1. **No sortable ward-table column.** WARD saw through the framing the
   moment it landed in a sortable table: "then it's a ranking… the
   framing's just a caption nobody reads." Sortability, not wording, is
   what makes a number weaponizable. Surfaces: ward page + ward
   one-pager only.
2. **Differential OSM disclosure, not generic.** ORG (unprompted, twice)
   pattern-matched OSM volunteer mapping onto 311 undercount bias: the
   caveat must name uneven mapping density *by neighborhood*, in body
   text next to every number, and must address both failure directions —
   scores that look worse (unmapped infra) and scores that look better
   (unmapped hazards) than reality.
3. **Show the distribution, not just the average.** US: ward-level
   averaging smooths away the block-level meaning that makes BNA
   defensible; show block-score spread (or a small map) on the ward page.
4. **Neighborhood-name framing alongside ward numbers.** RIDER doesn't
   know her ward number; percentages compress to pass/fail grades in
   retelling. Plain-sentence form ("Most of Avondale can't reach a
   grocery store on low-stress streets").
5. **Pre-launch read-aloud test.** ORG's precondition: the copy must
   survive being spoken in a low-context room, not just read on the
   site. This is a real-human check this study cannot substitute for.

### B3 — Segment stress cross-check: ADVANCE WITH CHANGES (license-gated)

Ranked #1 by RIDER, unconditionally welcomed by ORG, would-use from US,
ADV, WARD; CDOT distrusts it *as a public per-segment finding* while
calling it the most professionally interesting element.

The audience tension that shapes the design: US and ORG demand
disagreements between OYL's facility grade and BNA stress be **published,
never silently reconciled** (US's stated kill condition), while RIDER
stops trusting the site if she must **adjudicate two conflicting numbers
herself** (her stated kill condition). These are compatible — by surface:

1. **Two-surface rule.** Expert surfaces (sources, methodology, findings,
   CSV) publish the disagreement explicitly with likely causes (OSM lag
   vs facility underperforming its label). Resident surfaces (maps) show
   one adjudicated, conservative comfort view — the site "has already
   done the arguing" (RIDER), and the arguing is documented where
   experts look (US, ORG).
2. **Artifact triage before per-segment publication.** CDOT's kill
   condition: a public "still high-stress" flag on a facility she
   installed that turns out to be an OSM mapping-lag artifact, with no
   recourse. Before any named-segment flag publishes: check OSM edit
   recency for that segment, and provide a documented correction path
   (an issue template is enough for a static site). Ship as internal QA
   first; publish aggregate findings ("N miles of bikeways sit on
   streets BNA rates high-stress") before any per-segment naming.
3. **Disclose the buffer-match method and its error rate** (US), same
   discipline as the Mellow dedup in DECISIONS.md #24.
4. **Weaponization framing check** (ADV): the aggregate finding must be
   worded as an upgrade case, not an infrastructure-isn't-worth-it case —
   same anti-disinvestment copy rule as P1.

### B4 — Peer-city strip: KILL

Unanimous ignore, 6 of 6, across every altitude: "I don't organize
against Minneapolis" (ORG), "not my desk, that's the fifth floor" (WARD),
"trivia" (RIDER), US pulls it herself in two minutes, CDOT defers it to
the Commissioner's office, ADV delegates it to press colleagues. No
participant named a meeting, document, or conversation where they would
use it. Peer scores remain one API call away if a future press-kit need
materializes; nothing ships now.

## Cross-cutting requirements

- **OSM currency is the master caveat.** Every BNA surface carries: the
  analysis version (26.05), the run date, and the uneven-volunteer-mapping
  disclosure. Four of six participants raised OSM staleness unprompted.
- **The score must not be launderable into disinvestment.** ORG's
  deal-breaker (a decent-looking score read as "they don't need it"; a
  bad one read as "nobody bikes there") and RIDER's discouragement risk
  are the same failure from opposite directions. The anti-disinvestment
  copy rule from P1 applies to every BNA number.
- **Sequencing:** B1 can ship now (facts, attributed). B2/B3 wait on the
  PFB license answer, and B3's public per-segment form additionally waits
  on the triage/correction mechanism.

## What this method cannot tell us

Simulated personas cannot measure real misread rates, real headline
behavior, or whether access framing actually survives a church basement —
ORG's read-aloud precondition and WARD's sortability instinct are exactly
the findings that deserve confirmation with real humans before B2 ships
publicly. They also cannot answer the license question or predict PFB's
actual response; the ask should go out regardless of build order. Finally,
persona consistency with the original study (US re-issuing her
silent-reconciliation kill condition; ORG re-deriving 311-undercount
logic) raises confidence in direction, but these are the same simulated
minds — agreement across runs is coherence, not replication.
