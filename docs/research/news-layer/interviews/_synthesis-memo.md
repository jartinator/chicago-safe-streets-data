# Synthesis memo — news-coverage concept validation (2026-07-13)

Four persona interviews (same research subjects as the 2026-07 user-needs
study; transcripts in this folder). Interviewing on Sonnet-class agents,
synthesis by the orchestrating session, per the study's routing policy.

## Verdict: SHIP v1, with four amendments

4/4 participants land on **conditional use** — nobody distrusts-and-abandons,
nobody ignores it outright. Value is confirmed for all four: the rider gets a
better path than Facebook-comment archaeology; the ward office replaces a
half-trusted Google Alert + colleague-text network; the advocate fills a
named monitoring gap (she missed a floor defeat her topic alert didn't
catch); the organizer gets screenshot-and-text material next to the meeting
list.

## Theme 1 — match precision is the entire trust budget (4/4)

One wrong ward/street match: the rider "scrolls past it like an ad" *and
starts doubting the site's other numbers*; the advocate calls it "visibly,
embarrassingly wrong" with **"no methodology to recite"** — unlike a crash
number she can defend; the organizer files it under "of course" (miscoded
West Side data history); the ward office downgrades the whole feature from
"forward it" to "fact-check all five links first," clawing back most of the
time savings.

**Amendment A (from the advocate's "no methodology" complaint):** every match
carries visible provenance — a `matched_via` field per match (e.g.
`publisher tag "35th Ward"`, `street name "Milwaukee Ave" in headline`) so a
match is auditable the same way a crash stat is. This converts the
indefensible failure into a defensible one.

**Amendment B (precision rules tightened):** ward matches only from an
explicit "Nth Ward" publisher tag or the same string in the headline;
alderman matches require an "Ald./Alderman/Alderwoman <surname>" pattern or
the full name (bare surnames are off-limits); street matches keep the
street-type-suffix requirement. Recall is sacrificed willingly — a thinner
correct list beats a fuller list with one landmine.

## Theme 2 — per-meeting/ordinance linkage: killed permanently (4/4)

Every participant rejected auto-linking stories to specific meetings or
ordinances, including as an opt-in "even if sometimes wrong" (rider:
"stacking a second maybe on top of a maybe"; advocate independently
re-derived the design's own cut and wants the interpretive step to stay
hers; organizer: the mismatch "now embarrassing him in front of his own task
force"; ward office: a hard failure he won't risk "in the room"). This moves
from v1 scope-cut to **permanent kill** — recorded here so a future session
doesn't resurrect it as an enhancement.

## Theme 3 — outlet-mix optics (2/4, the two public-facing roles)

A Streetsblog-heavy list makes the rider suspect "a bike-advocacy thing
dressed up as a data site"; the advocate says opponents will call it "the
bike lobby's newsletter" and wants Block Club *visibly* represented.

**Amendment C:** outlet name rendered as a first-class visible label on every
item (not hover text); Block Club's transportation feed stays a first-class
source, Google News supplement keeps non-advocacy outlets (Tribune,
Sun-Times, neighborhood outlets) in the mix; the sources card and the UI
section carry the neutrality note ("independent outlets' own headlines;
coverage, not endorsement"). No per-outlet quota — deterministic
newest-first only.

## Theme 4 — empty states and coverage gaps (organizer, decisive)

An empty box must not read as calm: **Amendment D** — the empty state renders
explicitly ("No coverage found for this ward in the last 90 days — outlets
cover some neighborhoods more than others"), acknowledging the documented
North Side/West Side coverage skew rather than hiding it.

## Placement: keep both, they have different champions

Ward office ignores the action-page duplicate but adopts the ward page; the
organizer is the reverse. Both placements are one shared helper — keep both.

## Noted, not actioned (honest limits)

- Ward office: even an accurate badged headline is "a second place the same
  bad headline lives" — a political-distribution liability inherent to the
  feature, disclosed in the sources card, not fixable by design.
- Rider wants "tell me up front if my forty-five seconds matters" — a
  meetings-UX need, out of this feature's scope; belongs to the agenda-items
  line of work.
- Method limits: simulated participants can't reveal real usability failures
  or real political dynamics; the coverage-skew reaction (organizer) and the
  screenshot-forwarding behavior (rider/organizer) deserve validation with
  real humans if this feature grows.
