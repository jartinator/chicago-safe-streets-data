# Validation interview: chi-pro-advocate (PFB BNA proposal)

Persona: Reyna Delgado, advocacy manager (see `personas/chi-pro-advocate.md`).
Protocol: `validation/pfb-bna/00-protocol.md`. Stimulus:
`docs/projects/pfb-bna-proposal.md` (elements B1–B4).

## Transcript

### 1. Context re-anchor

**Interviewer:** Quick re-anchor before I show you anything new. Same role as
before — but this time: think of the last time you had to characterize the
*quality* of the bike network itself, not a crash number. Not "how many
people got hurt," but "how good or bad is the network." When did that come
up, and what did you do?

**Reyna:** That comes up more than you'd think, actually, usually when
someone's trying to make the "why should we spend more" argument against us.
Task force meeting in the spring, Neighborhood Bike Network process for the
Northwest Side corridors — a guy from the local chamber, not hostile exactly,
but skeptical, stood up and said something like "PeopleForBikes ranks Chicago
2,919th out of 3,000 cities, worse than half the sprawl in Texas, so what
exactly are we buying with all this money." And I didn't have a clean answer.
I knew the number existed — it gets quoted at me maybe twice a year, usually
by someone trying to make either "see, nothing's working" or "see, we're
finally catching up" depending on which way they want the room to lean — but
I've never sat down and actually worked out where it comes from. I know it's
some kind of OpenStreetMap thing. I don't cite it myself in testimony, on
purpose, because I can't defend the methodology out loud, and you already
know my rule about that. So what I actually did in that meeting was pivot
back to what I can defend — fatal crashes down 30 percent since 2021 — and
just... let his number sit there unanswered, which is not a great feeling,
because it looked like I didn't have a response, when really I just didn't
trust myself to defend or attack a number I hadn't vetted.

**Interviewer:** Got it — hold onto that story, I'll come back to it. Before I
show you anything, here's where the site stands today, in brief: On Your
Left is an independent, read-only dashboard — two maps, a findings page, a
ward table with CSV export, a sources page, an action page pointing to 311
and Bike Lane Uprising. Everything's badged real, proxy, mock, crowdsourced,
derived, or no-data-yet. It has crash data, the CDOT bikeway network graded
by facility type, ward rollups including a relative safety index, coverage
percentages — how much of the street grid has any bike infrastructure — and
council/alderman accountability data. It does not have ridership data of any
kind, and it says so everywhere.

**Reyna:** Right, that all tracks with what I remember. Coverage percentage
and the ward table are the two things I actually use. Go ahead.

### 2. Stimulus, element by element

**Interviewer:** First one — B1. A new findings card: "PeopleForBikes rates
Chicago's bike network 11 out of 100 for 2026. The average rated U.S. city
scores 36. Chicago has 6,267 miles of high-stress streets and 1,834 miles of
low-stress." With a trend line, 2023 through 2026, and a caveat that it's a
third-party score computed from OpenStreetMap — measures the network, not
riders, only as current as OSM mapping.

**Reyna:** My first reaction is honestly a little bit of relief, not
excitement — relief because if it's sitting on OYL with a citation and a
caveat already written out, that's the exact thing I didn't have in that task
force room. I don't have to go build my own understanding of the methodology
from scratch; I can point at OYL's card and say "here's what that number
means and here's what it doesn't measure," and that's a real time-saver. But
I'd use it defensively, not offensively — I'm not going to lead a hearing
with "we're 11 out of 100," because that plays straight into the "nothing's
working, stop spending" argument. What I'd actually use is the trend line —
9 to 11 to 11.08 — because that's a "we're moving, slowly" story that sits
next to my crash-trend story instead of contradicting it. The high-stress
mileage number, 6,267 miles, is useful too, actually, more useful than the
score — that's a concrete "here's how much of the city still isn't safe to
ride" fact, which is closer to how I already talk. What I'd check before
using it anywhere: whether "high-stress" here means the same thing CDOT
engineers mean when they talk about stress, because if PeopleForBikes has its
own definition that doesn't match CDOT's, I'm back in the exact spot I was in
with the facility-grade taxonomy — saying a word that means something
different to the person sitting across from me.

**Interviewer:** B2 next. Ward-level access scores — an annual snapshot,
joined to ward boundaries, presented like this: "In Ward 35, X percent of
residents live on blocks with low-stress bike access to a grocery store."
Explicitly not a 0-to-100 ward ranking — access framing, not a danger score.

**Reyna:** Okay, wait — say that again. "X percent have low-stress access to
a grocery store" — so this is telling me how many people in a ward can get
to groceries on a bike without a stressful street. My first read, honestly,
before you clarified, was that this was another version of the ward safety
index — another single number per ward that I'd have to defend against a
CDOT engineer's version of the same thing. I need a second to recalibrate,
because those two things — "how dangerous is my ward" and "can my ward reach
a grocery store safely" — are genuinely different asks and I use them for
different rooms. Once I get that it's access, not danger: this is actually
more useful to me than I expected, but for a different fight than the one I
usually bring numbers to. It's not testimony ammunition, it's an equity
argument — it's the kind of thing I'd use with an alderman whose ward has
zero protected mileage, to say "it's not just crashes, your residents can't
even get to the store without riding on a stressful street, and that's an
investment case, not evidence of low demand." That's language I've actually
started borrowing from the CDOT corridor economic study people, so it fits.
What I'd check: whether "grocery store" access means the same corner store
list I'd get pushback on from a skeptical alderman — food deserts are already
a fight in this city, and if the underlying destination list is thin or
weird for a specific ward, someone will find it and use it against me before
I even get to make my point.

**Interviewer:** B3. A segment-level cross-check — every street segment gets
a stress rating pulled from this same PeopleForBikes analysis, including
speed limits and intersection stress, matched onto the bikeway network OYL
already shows. Where OYL's facility grade says "protected" but this stress
rating says the segment is still high-stress — speed, lane count,
intersections — it gets flagged.

**Reyna:** Oh. Okay, this one I have real feelings about, and they're mixed.
Part of me wants this immediately, because it's exactly the kind of thing
that would have saved me in that Northwest Side task force meeting when the
CDOT engineer picked apart my ward-concentration number — if I'd had an
independent, published-methodology source saying "this stretch is graded
protected but still rates high-stress because of the intersections," that's
not me making an amateur mistake, that's two credible sources agreeing on a
gap. That's actually stronger than either number alone. But the other part
of me is nervous, because I can already see the exact meeting where this
backfires — Ald. Dowell's office, or anyone doing the 18th Street move again,
standing up and saying "even PeopleForBikes says your precious protected lane
isn't actually safe, so why are we defending it." A flag meant as a
data-quality signal for internal use becomes a talking point for someone
trying to rip out infrastructure I need to defend. Before I'd ever put this
in front of an audience I'd need to know exactly how OYL is presenting the
disagreement — is it "this needs an upgrade" framing, or is it neutral
"these two sources disagree, here's why," because neutral framing in a
hostile room reads as "even you admit it's not safe."

**Interviewer:** Last one — B4. A findings-page comparison: Chicago's score
next to a handful of peer cities you'd pick — say New York, LA, Philadelphia,
Minneapolis, Seattle — same scoring run, same methodology.

**Reyna:** Honestly? This is the one I care least about. It's a citywide
number compared to other citywide numbers, and my whole world is ward-by-ward
— nobody in the 15th Ward cares that Minneapolis beats us, they care about
Archer Avenue. I could maybe see BikePAC or the policy director using
something like this in a press release or a citywide op-ed — "even
Minneapolis is pulling ahead of us" has a certain shame-into-action energy
that works at that altitude — but it's not something I'd build a ward letter
around, and it's not testimony material, because the second you compare
Chicago to Minneapolis a skeptical alderman's staffer says "that's not a fair
comparison, different city, different weather, different density," and now
I'm defending a comparison instead of making my actual point. I'd let someone
else on my team own this one if we used it at all.

### 3. Trust probes

**Interviewer:** Four specific things I need to ask everyone. First: this is
computed from OpenStreetMap, by a national advocacy org, updated once a year,
and it's only as current as whatever volunteers have mapped. Does that change
anything for you?

**Reyna:** It changes how fast I'd trust any specific segment, yeah. I know
enough about OSM to know it's crowdsourced — same reason I already treat the
Mellow routes layer as "somebody's opinion, not a survey." Once a year is
slow for my world; menu-money cycles and hearing calendars move faster than
that. If CDOT actually finishes a protected lane in March and PeopleForBikes
doesn't run their next analysis until May of the following year, I've got a
year-plus where the site is telling me a street is worse than it actually
is. That's not a dealbreaker on its own — I already live with CDOT's own
network having no install dates — but it means I'd never use this to make a
claim about something that happened in the last twelve months. Old news,
fine. Breaking news, no.

**Interviewer:** Second. Chicago scores 11 out of 100. Does that number help
you or hurt you?

**Reyna:** Both, and it depends entirely on who's in the room, which is
exactly why I've never used it myself. It helps me with a friendly audience —
an alderman's office that already wants to invest, a room of engaged
residents — because it backs up "we have a long way to go" with a number a
national group put a name behind, not just me saying it. It hurts me badly
with a hostile audience, the exact task force room I told you about, because
"11 out of 100" sounds like "everything you've spent is a failure," and
that's precisely the read the chamber guy went for. The honest problem is
that it directly collides with my best number — fatal crashes down 30
percent — and a hostile questioner doesn't have to disprove either number,
they just have to say "well which is it, is it working or isn't it," and
make me look like I'm citing contradictory evidence. I'd need OYL to hold my
hand on the "these measure different things — network quality versus crash
outcomes, and both can be true at once" explanation, in writing, or I will
keep doing what I did in that meeting: not touching the number at all.

**Interviewer:** Third. The ward number is framed as access — "X percent have
low-stress access to a grocery store" — not a danger ranking. Reaction?

**Reyna:** Already told you my gut reaction — I heard "ward number" and
braced for another 0-to-100 danger score I'd have to defend, the same fight
I already have over the existing ward safety index. Once I understood it's
access-framed, I actually like that it's *not* a ranking — a ranking would
just give every skeptical alderman's office a new excuse to say "well we're
not the worst ward, so why are you bothering us." Access framing dodges that
entirely, and it matches the "investment case, not low demand" language I
already use. My only worry is whether residents and alders will actually
read "access" the way it's intended, or whether "35 percent of your
residents have low-stress access" just gets heard as "your ward scores 35,"
and I'm back to explaining a ranking I never claimed to make. I'd want that
distinction printed in plain words right next to the number, not just implied
by the phrasing.

**Interviewer:** Fourth. Where OYL's own facility grade disagrees with the
BNA stress rating — OYL says protected, BNA says high-stress — which do you
believe, and what should the site do about it?

**Reyna:** I believe neither one automatically, honestly — I believe
"something here needs a human to look at it before I use it in a hearing."
CDOT's facility grade tells me what was built; PeopleForBikes' stress rating
is trying to tell me how it actually rides, speed and lanes and
intersections included, which is a real and useful distinction — a protected
lane on a street with a nasty unprotected intersection every three blocks
genuinely can be high-stress even though the lane itself is "protected." So
in principle I don't think it's a contradiction, I think it's two different
questions. But if I'm standing in front of an audience, I need the site to
have already done the work of explaining that, in one sentence I can repeat,
not leave me to reconcile it live. What the site should not do is silently
pick a winner and just show me one grade — that's worse than showing the
disagreement, because then I don't even know there's a conversation to have.

### 4. Forced choice

**Interviewer:** Rank B1 through B4 for your own work — most useful to least.
Then: should OYL skip this whole integration and spend the effort somewhere
else? If so, where?

**Reyna:** B2, the ward access scores, first — it's the one genuinely new
argument I don't already have, the equity/investment-case angle, and it's
ward-shaped, which is the only shape that matters to me. B1, the citywide
scorecard, second — mostly for defense, so I stop getting blindsided by that
number in a hostile room, plus the high-stress mileage figure is a decent
standalone fact. B3, the segment cross-check, third — genuinely powerful, but
it's the one I'm most nervous about, because the exact same flag that helps
me internally is the one that gets weaponized against a lane I'm trying to
protect, so it needs the most careful presentation before I'd trust it. B4,
the peer-city strip, last — nice for a press release, does nothing for a
ward letter or a hearing.

As for skipping it entirely — no, I wouldn't say skip it, but if you're
asking me to trade effort, I'd put it after the ridership gap, not before.
I told you last time: we lost the 18th Street fight because we could prove
danger but not demand. None of B1 through B4 gets me a single rider-count
number. If I had to pick one thing for your team to build instead of any of
this, it's still Divvy trip data or CDOT counter numbers joined to a
corridor. This is good, and I'd use at least two of the four pieces. But it's
not the thing that would have saved 18th Street.

### 5. Kill question

**Interviewer:** Last one. What single thing about this integration, done
wrong, would make you stop trusting the site?

**Reyna:** If the B3 flag shows up on a corridor I personally know just got
finished — like if CDOT closes out a protected lane this fall and OYL's BNA
overlay is still calling it high-stress next spring because the OSM mapping
hasn't caught up — and somebody in a community meeting catches that before I
do. That's not a hypothetical for me, that's exactly the kind of gotcha that
happened with a different tool before, and once it happens once, I stop
trusting the whole overlay, not just that one segment, because I have no way
to know which other segments are also stale without re-checking every one by
hand — which defeats the entire point of using the site instead of building
it myself.

## Analysis memo

```
participant: chi-pro-advocate
confidence_notes: >
  Interview stayed inside Reyna's documented world and callback-referenced
  her established episodes (18th Street ridership gap, the February
  committee/floor split, the facility-grade-taxonomy anxiety, the CDOT
  engineer who dismantled her ward-concentration number) rather than
  inventing new unrelated backstory, which is the intended behavior for a
  validation re-run of an existing persona. The task-force "11 out of 100"
  episode is new but built directly from documented traits: "you'd sooner
  use a weaker number you can defend than a stronger one you can't," the
  CDOT corridor economic study as her newest weapon, and her general
  hostile-room posture — treat it as plausible in-world extrapolation, not
  verified fact, same caveat as any invented episode in this method.
  The B2 misread (bracing for a danger ranking before parsing the access
  framing) is a deliberate persona-consistent moment per shared-rule 7, not
  a modeling error. Weakest point: her claim that PFB's "high-stress"
  mileage might not match CDOT's internal stress vocabulary is asserted
  confidently but she has no documented episode of actually checking this
  for BNA specifically — it's an extrapolation from her established
  facility-grade-taxonomy worry, not a verified distinct concern.

reactions_to_proposal:
  - element: B1 — citywide BNA scorecard
    verdict: would-use
    why: >
      Wants it strictly as a defensive/explanatory tool ("here's what that
      number means and doesn't measure"), not as offense — she has been
      caught flat-footed by the raw "11/100" figure before and would rather
      cite OYL's caveat than build her own explanation from scratch. Prefers
      the trend line and the 6,267-high-stress-mile figure over the bare
      score, because the trend pairs with her existing "crashes down 30%"
      narrative instead of contradicting it. Conditional check: whether
      "high-stress" tracks CDOT's own internal stress vocabulary.

  - element: B2 — ward-level access scores
    verdict: misreads, then would-use
    why: >
      Initially misread "ward number" as a new 0-100 danger ranking she'd
      have to defend (exactly the risk flagged in the proposal itself —
      "the prior study's US/WARD interviews killed that shape"); once
      corrected to access framing, endorsed it as a genuinely new
      equity/investment-case argument distinct from anything she currently
      has, and tied it to language she already borrows from CDOT's 2026
      corridor economic study. Flags the underlying destination-list
      (grocery access) as a likely attack surface in food-desert-sensitive
      wards.

  - element: B3 — segment stress cross-check
    verdict: would-use, with real reservations
    why: >
      Most emotionally mixed reaction of the four. Wants it because an
      independent source agreeing with her on a "protected-but-still-risky"
      corridor is stronger than her word alone against a CDOT engineer.
      Distrusts how it could be used by the exact people who tried to rip
      out the 18th Street protected intersection — "even PeopleForBikes says
      it's not safe" as a removal argument. Would not present it to an
      audience without OYL first deciding and stating a clear framing
      ("needs upgrade" vs. neutral disagreement).

  - element: B4 — peer-city strip
    verdict: ignores
    why: >
      Citywide-to-citywide comparison is the wrong altitude for her
      ward-by-ward work; anticipates an easy "not a fair comparison"
      deflection from any skeptical staffer. Would delegate ownership to
      BikePAC/press-release-level colleagues rather than use it herself.

latent_needs:
  - need: A single, repeatable sentence reconciling "network quality is
      bad (BNA score)" with "outcomes are improving (crash trend)" that she
      can say verbatim under hostile questioning
    inference_basis: >
      She described the two numbers as colliding in a hostile room — "a
      hostile questioner doesn't have to disprove either number, they just
      have to say 'well which is it'" — and said without a ready
      explanation she would keep doing what she did in the task-force
      meeting: not touching the BNA number at all. This is a stronger,
      more specific ask than "add a caveat"; she needs the reconciliation
      pre-written, not just the individual caveats each element already
      carries.
    risk_if_wrong: >
      If B1 ships with only the generic OSM/network-not-riders caveat and
      no explicit reconciliation with the crash-trend narrative, she
      continues to avoid citing the score entirely (as she does today),
      and OYL gains a defensive tool she still won't use offensively or
      even neutrally in a hearing.

  - need: A stated, visible position (not silence) whenever OYL's own
      facility grade and the BNA stress rating disagree on the same
      segment — not just a raw side-by-side display of two numbers
    inference_basis: >
      When asked directly which source she'd believe, she said she trusts
      neither automatically and needs "something here needs a human to
      look at it" signaled to her, and explicitly said the worst outcome
      is the site "silently picking a winner and just showing me one
      grade" — she needs to know a disagreement exists at all before she
      can decide how to handle it in front of an audience.
    risk_if_wrong: >
      If the buffer-matched cross-check (B3) is only used as a silent
      internal QA signal that quietly adjusts or hides one grade, she will
      unknowingly repeat a facility-grade claim that a BNA-literate
      audience member (or a CDOT engineer) can contradict on the spot —
      recreating the exact "sloppy in front of an engineer" failure mode
      she already fears from facility-grade mismatches.

  - need: A segment-level "as of" / OSM-currency flag she can check against
      her own personal knowledge of recently completed projects, not just a
      general once-a-year-updates caveat on the whole layer
    inference_basis: >
      Her kill-question answer named a specific, concrete failure mode:
      CDOT finishing a protected lane in fall, the BNA-derived overlay
      still showing it high-stress the following spring because OSM
      mapping lagged, and a community-meeting attendee catching the
      discrepancy before she does. She explicitly said one such catch would
      make her distrust "the whole overlay, not just that one segment,"
      because she'd have no way to know which other segments were also
      stale without manually re-checking each one.
    risk_if_wrong: >
      A layer-wide "updated annually, OSM-derived" caveat is true but
      insufficient at the segment level; without a way to flag or at least
      timestamp individual segments, one visible staleness catch in public
      generalizes in her mind to the entire B3 feature being unreliable,
      and she reverts to never using the cross-check at all.

  - need: A destination-list (or methodology-detail) drill-down for B2's
      access framing, specifically for food-desert-sensitive wards, before
      she'd cite a specific ward's grocery-access percentage in public
    inference_basis: >
      She flagged, unprompted, that "food deserts are already a fight in
      this city" and predicted that if the underlying grocery-destination
      list is "thin or weird for a specific ward," an opponent would find
      and use that gap against her before she could make her actual
      equity point — mirroring her established pattern of pre-vetting any
      number against its exact definitional edges before a hearing.
    risk_if_wrong: >
      If B2 ships with an aggregate ward percentage but no visibility into
      which destinations fed the score, she cannot pre-empt the "your
      grocery list missed X" objection, and one such challenge in a
      food-desert-sensitive ward discredits the whole access framing for
      her, not just that ward's number.

data_they_bring: >
  The CDOT 2026 corridor economic study, now her go-to counter to the
  merchant-objection argument, which she is already porting into equity/
  investment-case language that maps naturally onto B2. Direct, lived
  memory of task-force and community-meeting moments where the raw
  PeopleForBikes score was invoked by others (for and against investment)
  without her having a rehearsed response — a gap she is actively aware of
  and has so far handled by avoidance rather than resolution. Her existing
  distrust calibration for OSM-derived, crowdsourced-quality layers,
  carried over directly from how she already treats the Mellow routes
  layer on OYL today.

deal_breakers: >
  (1) A visible, catchable staleness gap on B3 — a segment she knows was
  recently upgraded still showing old BNA stress data in a public setting,
  discovered by someone other than her — which would discredit the entire
  cross-check layer, not just the one segment.
  (2) B3 disagreements (OYL protected vs. BNA high-stress) presented as a
  flat, unexplained juxtaposition rather than a stated position, handing a
  ready-made "even they admit it's not safe" line to anyone trying to
  remove infrastructure she is defending (explicit callback to the 18th
  Street removal fight).
  (3) The B1 scorecard shipping without an explicit reconciliation between
  "network still bad" and "crash outcomes improving" — without it, she
  continues to avoid the number entirely rather than risk a hostile
  audience playing the two narratives against each other.
  (4) B2's access percentages presented without visibility into the
  underlying destination list, in a city where food-desert methodology is
  already contested terrain.

vocabulary: >
  (carried over from the base interview, plus proposal-specific additions)
  network quality vs. outcomes, "prove danger but can't prove demand,"
  investment case / not low demand, access framing, stress rating,
  high-stress mile, low-stress mile, "who's the alder there?", task force
  (Neighborhood Bike Network process), the chamber (business community),
  merchant-objection meeting, hostile room, defensible number, "which do I
  believe," staleness / gone-stale, OSM mapping lag, corridor economic
  study.
```
