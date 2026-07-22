# Cross-interview synthesis memo — run of 2026-07-21 (stimulus: inventory v1.14)

Nine interviews, nine memos. This memo aggregates them for the UX synthesis
step. Participant ids are used throughout; "stated" and "latent" follow the
per-memo classifications (every latent need cited here carries an inference
basis in its source memo).

## Recurring themes

### T1. The caveat must travel with the number — everywhere the number goes
The single most widely supported theme, and it sharpened this run because
v1.14 multiplied the surfaces a number can travel to (print, API, AI answer).
- chi-cdot-planner (stated): menu-money and denominator caveats on the same
  page as the figure, "not two clicks away."
- chi-community-organizer (stated): "that caveat has to survive the print."
- uk-ward-campaigner (stated): the plain-language one-pager register must not
  drop "relative, not absolute" — "brevity and honesty are in tension."
- us-bna-analyst (latent, strong basis): caveats must be machine-readable
  inside `/api/v1/` `_meta`, not just page copy — "the same caveat-stripping
  problem" as a cropped screenshot.
- nl-network-planner (stated): caveat propagation through an AI assistant
  must be *tested*, not just described — "restating its own limitation in
  the same breath."
- chi-pro-advocate (latent): methodology must be *recitable in one breath*
  in a hostile room, not merely present.
- dk-kpi-strategist (latent): a buried caveat becomes the asterisk an
  implicated official uses to dismiss the whole card.

Consequence: caveat placement is not copy polish; it is the load-bearing
trust mechanism, and each new output channel (one-pager print, API payload,
AI answer) needs its own explicit caveat-carriage rule.

### T2. Exposure/ridership: the honest gap everyone respects and nobody is done with
All nine touched it (mandatory probe). The split is *what to do about it*:
- Want a labeled proxy now: chi-pro-advocate (Divvy trips, honest-biased 311
  — she has lost a real argument to this gap), us-bna-analyst (crashes per
  bikeway-mile beside per-capita, "proxy for exposure, not exposure"),
  nl-network-planner (any denominator beats an incident log),
  uk-ward-campaigner (a counter-style exposure source),
  chi-everyday-rider (latent — she independently reinvented the gap from a
  kitchen-table argument; "even just busy/quiet would be something").
- Honest absence over fabricated precision: chi-ward-office ("I'd rather the
  site keep saying 'we don't know' loudly"), chi-community-organizer (the
  caveat must be *worded defensively* so "nobody rides out there" can't be
  used to wave off West Side crash concentration).
- New this run: juxtaposing the BNA score with raw crash counts created two
  documented misread paths — "score = safety" (us-bna-analyst, stated;
  chi-ward-office reads any unfamiliar ranking as a press threat) and the
  adversarial "more bike lanes causes more crashes" reading
  (uk-ward-campaigner, latent, emerged only because both stimuli now share a
  page).

### T3. The synthetic-obstructions quarantine bought trust — and revealed the floor beneath it
The gating/watermark/API-exclusion is the most-approved single change of the
update: chi-cdot-planner ("the single biggest trust-earning move"),
us-bna-analyst ("the single best change"), nl-network-planner ("the single
correct decision in this entire update"), uk-ward-campaigner,
dk-kpi-strategist, chi-ward-office (partial credit) all approve.
Remaining exposure, in descending severity:
- Existence itself: chi-pro-advocate's bar is that synthetic data mirroring a
  real, named, litigated dataset (Bike Lane Uprising) should not exist in any
  public build; chi-everyday-rider ("I would feel kind of tricked... why not
  just link to Bike Lane Uprising"); chi-ward-office keeps it as a
  deal-breaker category (screenshot escaping the gate).
- Silent-decay of the promise: nl-network-planner (latent → stated this run):
  "pending a data-sharing conversation" needs a named, dated counterpart or
  it becomes a permanent vague state indistinguishable from a compromise.
- Blast radius: dk-kpi-strategist, chi-pro-advocate, chi-community-organizer
  independently state that discovering one *more* undisclosed synthetic
  element would collapse trust in the entire catalog, not one layer.

### T4. The ward one-pager is the study's star artifact — and its biggest liability
Seven of nine would use or forward it; for four it directly replaces a
documented manual workaround (chi-pro-advocate's four-hour quarterly ward
letters; chi-community-organizer's evening of Legistar cross-referencing;
chi-ward-office's hand-built defensive brief; uk-ward-campaigner's
hand-assembled consultation leaflet). The conditions attached are precise:
- Composite-verdict risk (nl-network-planner, latent, strong basis): three
  individually-caveated uncertain numbers (safety index, menu money,
  sponsorship) on one skimmable page read as one certain conclusion about an
  alderman. The per-number badge discipline does not prevent this.
- Political control (chi-ward-office, latent): "a report card on my boss I
  don't control" — he wants preview/advance notice of anything scored or
  news-matched under his alderman's name.
- Verification hooks (chi-pro-advocate, stated, three named kill conditions):
  committee-vs-floor vote separation; menu-money reconciliation with Ward
  Wise; safety-index interpretability.
- Register fidelity (uk-ward-campaigner, chi-community-organizer): the
  plain-language and print versions must keep the caveats.
- Entry point (chi-everyday-rider, latent): she cannot self-locate on a
  ward-number-keyed URL; she knows her address and her alderman's name.

### T5. Freshness is a first-class data field, not a site footer
- uk-ward-campaigner (stated): visible *measurement* dates on any
  claimed-current stat (she was burned by a stale counter figure).
- chi-cdot-planner (stated): "status as of [date], last checked against
  [official link]" on every proposed-project card, plus a fast correction
  path; (latent) an auditable, non-editorial flag channel for subjects.
- us-bna-analyst (latent): a stale "proposed" card is a "zombie project"
  worse than no roster; also methodology *vintage* disclosure for the BNA.
- chi-ward-office (latent): roster staleness, not bias, is what he expects
  to be caught out by.
- dk-kpi-strategist (stated): dated, archived *editions* so movement can be
  shown over time; a perpetually-current page "can't be compared to 'then'."
- nl-network-planner (latent): granular (per-ward/corridor) OSM-currency
  disclosure for the BNA score, not one blanket citywide date.

### T6. Install dates and promise-vs-delivered are the same unmet job
- chi-cdot-planner (stated, her #1): install-date history with as-built
  facility type — she ranks it above ridership.
- chi-ward-office (stated): "a clean timeline, ward by ward, would settle
  more arguments in my job than any crash number" — half his fights are
  promise-vs-delivery; (latent) the project → ward → spend → status → date
  join across menu money, infrastructure grade, and the roster.
- dk-kpi-strategist (stated): committed-vs-delivered lane-miles per year,
  tracked across editions, as a KPI in its own right.
- chi-community-organizer (stated): a before/after story tied to a *named
  community process* (his Belmont Cragin ledger) — the existence proof that
  organized pressure converts data into infrastructure.
- chi-pro-advocate (workaround): hand-counts crash records against install
  dates scraped from press coverage.

### T7. The agent layer: structurally admired, behaviorally untrusted
Highest praise and hardest conditions in the same breath.
- us-bna-analyst: "better hygiene than most paid data products" — her
  strongest single reaction; wants caveats in-payload (T1).
- dk-kpi-strategist: same provenance discipline he values in publishing;
  declines to judge uptake.
- Conditions: refuse-don't-hallucinate on missing data (chi-pro-advocate
  stated, chi-everyday-rider stated); a *tested* caveat-propagation
  discipline (nl-network-planner); loud confirmation it reads only the same
  published files a human could download (uk-ward-campaigner); provenance on
  any AI answer (chi-everyday-rider).
- New failure surface: chi-ward-office reframes the assistant as a blindside
  vector (a number reaching a reporter through a chatbot before it reaches
  him); chi-everyday-rider genuinely cannot tell whether "ask an AI
  assistant" means an in-page chatbox or an external tool — a documented
  live misreading of the current copy.
- Confidence caution: nearly every memo flags its agent-layer reaction as
  extrapolated beyond the evidence base. Treat direction, not intensity.

### T8. Geography that matches how people self-locate
- chi-everyday-rider (latent, direct observation): address → ward resolver;
  ward-number-keyed URLs lose her at the front door.
- chi-community-organizer (latent, twice-documented workaround):
  community-area (Austin, North Lawndale) framing as first-class geography;
  ward slicing costs him "the same weekend of work."
- chi-ward-office (stated): corridor/block-level before/after, because "what
  happens on THIS block" is the question hostile rooms actually ask.
- nl-network-planner (stated): network-cohesion gaps, not rosters — the
  geography of what's *missing*.

### T9. Ranked numbers need their rebuttal on the same screen
- chi-community-organizer (latent, raised independently twice):
  ranked/scored resident-facing numbers need same-screen "why" context
  (disinvestment, reporting bias) or they become stigma instead of
  ammunition; "0–100" self-misread as a pass/fail grade.
- chi-cdot-planner (stated): "explicitly relative needs to be loud, not a
  footnote."
- dk-kpi-strategist (latent): pre-empt the methodology-dismissal move he has
  watched a mayor's office perform.
- uk-ward-campaigner (latent): the citable-vs-situational distinction —
  stakes tiering orthogonal to the provenance badge.
- Tension flag: us-bna-analyst wants unadorned recomputable numbers;
  editorializing every stat conflicts with analyst-audience restraint (see
  Tensions).

## Tensions between audiences

1. **Honest absence vs. usable proxy** (T2): chi-ward-office and
   chi-community-organizer rank an honest "we don't know" above any shaky
   denominator; chi-pro-advocate, us-bna-analyst, nl-network-planner, and
   uk-ward-campaigner each want a labeled proxy now. Any exposure proxy must
   satisfy the advocate's caveat rigor *and* not hand the organizer's
   opponents a minimization tool.
2. **Neutral evidence layer vs. causal context**: the organizer wants
   disinvestment context welded to every ranking; the analyst wants clean,
   recomputable numbers without editorial narrative. Same screen, opposite
   needs.
3. **Independence vs. subject participation**: chi-cdot-planner wants a
   correction channel that is auditable and non-editorial (she pre-empts the
   capture objection herself); chi-ward-office wants preview/embargo of
   pages about his alderman. Both collide with OYL's no-accounts static
   independence — and the ward office's ask, if granted, is exactly the
   capture the advocate and organizer would flag.
4. **Brevity vs. caveat completeness** (uk-ward-campaigner's phrase):
   plain-language registers exist to be skimmable; every dropped caveat is a
   trust failure for the intermediary who forwarded it.
5. **Roster as coordination vs. roster as justification**
   (uk-ward-campaigner's distinction): the proposed-projects roster serves
   status-tracking/coordination; nl-network-planner needs gap-analysis
   geometry it deliberately doesn't have. Serving the second job is a
   different (and possibly impossible) data acquisition, not a UX tweak.

## Needs unique to one audience but strategically important

- **Dated targets with owners** (dk-kpi-strategist): nothing on OYL is a
  promise — no number has a named owner and a deadline. He ranks this above
  the ridership gap. OYL cannot mint targets, but it can surface the city's
  own published commitments (Cycling Strategy mileage pledges) as
  promise-vs-delivered (converges with T6).
- **"Verify the rule once, trust the template"** (uk-ward-campaigner,
  self-stated): trust attaches to artifact *classes*, and one broken
  instance burns the whole class. This is the study's best articulation of
  why per-instance QA on generated artifacts (50 one-pagers) matters more
  than any new feature.
- **News valence and name-collision confidence** (chi-ward-office): matching
  accuracy is necessary but not sufficient; favorable/unfavorable context
  blindness is what triggers the 9pm phone call.
- **Chatbox-vs-external-tool disambiguation** (chi-everyday-rider): a copy
  fix, cheap, and she is the only persona who hit it because she is the only
  one who'd arrive without a mental model.

## What this method cannot tell us

Inherited candidly from the memos, for verbatim carry-over into the report:
- Simulated participants cannot reveal true usability failures (e.g.,
  whether an organizer can actually parse the percentile-blend methodology
  under meeting-prep time pressure — flagged in chi-community-organizer).
- Nearly all agent-layer/AI-assistant reactions are extrapolations beyond
  the evidence bases (flagged in seven of nine memos). The direction
  (provenance anxiety, refuse-don't-hallucinate) is consistent; the
  intensity is unmeasured. Real-human validation needed before investing
  beyond copy fixes.
- Real political dynamics are unknowable here: whether Chicago ward offices
  actually behave like the composite's blindside-averse model, whether the
  name-collision fear is real, whether an embargo request would in fact be
  followed by weaponization.
- Imported frames may not transfer: London's 30-borough coordination
  problem (uk), Copenhagen's edition ritual (dk), and Dutch gap-audit
  practice (nl) are documented in *their* worlds; their Chicago analogs are
  assumptions.
- Several personas self-diagnosed thin spots (nl's too-fluent API test
  protocol; chi-everyday-rider's AI-literacy read; chi-cdot-planner's
  roster reaction) — these are recorded in each memo's confidence_notes and
  should be weighted down accordingly.
- Recommended real-human follow-ups, in priority order: (1) an ATA-style
  advocacy staffer on the one-pager's three kill conditions; (2) a current
  or former ward staffer on preview/blindside behavior; (3) two or three
  residents on the home page → one-pager path and the AI-assistant copy;
  (4) a CDOT-adjacent planner on the correction-channel design.
