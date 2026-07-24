# Interview: US BNA / think-tank analyst (Dana Okafor, composite/fictional)

**Run date:** 2026-07-21
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** (post-#51 home page
split, methodology page, static agent API, news-coverage layer, proposed-projects
roster, PeopleForBikes BNA citywide score, obstructions moved to gated preview)
**Interviewer:** Lead Researcher (per `01-lead-researcher.md` / `03-interview-guide.md`)
**Participant:** Dana Okafor persona (`personas/us-bna-analyst.md`, evidence base
`evidence/us-thinktank.md`)

This is a re-run of the study against the July 2026 inventory. This transcript
does not assume any prior session happened — the persona reacts fresh.

---

## Transcript

**LR:** Thanks for making time. Start wherever's easiest — what's your role day
to day, and what's the last decision about street safety you actually tried to
move?

**Dana:** Last one was three weeks ago. A mid-size city — I won't say which,
doesn't matter — asked us to sanity-check their capital plan against their BNA
score before they submitted it for a federal Safe Streets for All grant. Their
score had ticked up four points year over year and their DOT wanted to lead
the narrative with that. My job was to open the network layer, find out *why*
it moved — was it a new protected corridor, or did they just repaint some
sharrows into "buffered" and reclassify — and write two paragraphs the grant
writer could use without me getting a call in six months asking why the
number didn't hold up under review. Took me a day and a half, mostly because
their GIS shop hands off shapefiles with no changelog, so I had to diff two
exports of the same layer myself in QGIS to find what actually changed on the
ground.

**LR:** Who's the audience for those two paragraphs, and what does "convinced"
look like to them?

**Dana:** The federal reviewer, one step removed — the DOT staffer is really
convincing *me*, and I'm the one who has to be willing to put our name near
their claim. Convinced means: the delta in the score maps to a specific,
named, geometrically real intervention, not a reclassification. If I can't
trace it to a segment I can point at on a map, I won't sign off, and I've said
no to exactly that kind of thing before — a city wanted credit for "low-stress
connectivity gains" that turned out to be a data vendor updating the OSM speed
tags under a re-striping project that hadn't been built yet.

**LR:** What information sources do you touch in a normal week for this kind
of work?

**Dana:** Our own BNA pipeline output, obviously. City-published crash open
data portals when I need a sanity check on where the risk actually is versus
where the connectivity gain is — those are two different questions people
collapse into one. NACTO's design guide when someone's facility taxonomy
looks nonstandard. And a lot of PDFs. Council committee reports, capital
plan memos, sometimes a FOIA'd spreadsheet if a city won't publish something
that should be public.

**LR:** Tell me about a time data — or the lack of it — sank an argument you
were making.

**Dana:** The Utah intersection work I cited to a partner city once — safety-
in-numbers, using Strava as an exposure proxy — got laughed out of a room
by a city engineer who pointed out, correctly, that Strava skews toward
recreational, higher-income riders and doesn't capture a kid on a BMX bike
going to school, which was exactly the population we were trying to talk
about. I didn't have a rebuttal. That's the actual state of exposure data in
this field — every proxy has a name-brand flaw, and if you don't say it out
loud first, someone else will, worse, in front of your audience.

**LR:** What data do you distrust, and what earned that?

**Dana:** Raw crash counts by geography, full stop, unless someone shows me
the denominator next to it. And any "danger index" that doesn't have a
methodology page linked from the same screen — I've had three different
consultants build me three different "risk scores" that were secretly just
z-scored crash counts with a good font.

---

### Stimulus walkthrough

**LR:** Let me walk you through what a site called On Your Left! does today —
independent, open-source, Chicago-only, read-only bike safety dashboard.
Ward-to-corridor-to-intersection drilldown, everything carries a real/proxy/
mock/crowdsourced/derived badge. Start with the home page — it's an
orientation landing page now, headline stats, who it's for, and a section
about asking an AI assistant questions through something they call the agent
layer.

**Dana:** Fine, that's a front door, I don't have strong feelings about a
front door. The "ask an AI assistant" bit is the interesting part and I want
to come back to it once you tell me what's actually behind it — if it's just
a chatbot skin over the same site I don't care, if it's a real structured
feed I might.

**LR:** We'll get there — it's a static `/api/v1/` JSON API plus an
`llms.txt`. Hold that thought. Next: the transportation map. Crash density,
bikeway network colored by facility grade, wards, cameras, main-route
overlays.

**Dana:** Crash density on a map is the thing I warned you about thirty
seconds ago on a call — you've built a ridership map, not a risk map. I say
that reflexively, it's not really an insult, it's just true of every
heat-dot map I've seen without a denominator, this one included until you
tell me otherwise. Facility grade colored by category — protected, buffered,
painted, sharrow, trail — that part I'd actually use, that's basically our
taxonomy, and if it's traceable to NACTO's categories I don't have to
re-explain it to a client. Cameras on the same map worry me a little, I'll
get to that.

**LR:** What would you check before trusting the crash layer in front of your
audience?

**Dana:** Whether it's severity-weighted or just a count. Whether it says
anywhere that police data undercounts non-fatal cyclist injuries — COST
TU1101 puts average police-reporting rate around 10%, US estimates run
7 to 46%, and it skews against exactly the victims a city most needs to see:
lower-severity, non-motor-vehicle, and disproportionately Black and Hispanic
riders. If that caveat isn't sitting right next to the map, I read the map as
naive, even if the underlying data is fine.

**LR:** Next, there's a second map — a schematic "transit-style" network map.
Named main routes, three toggleable tiers, a comfort-floor filter from "any"
to "protected only," but explicitly no safety data on that page.

**Dana:** That's closer to what I actually build for a living — that's a
connectivity artifact, not a crash artifact, and I respect that they didn't
try to cram crash dots onto it. The comfort-floor filter is basically a poor
man's LTS threshold — "show me only what a nervous rider would use" — which is
the right instinct even if it's not computed the way our BNA does it, off
lane widths, speeds, signal presence. I'd ask what "protected / paint / mellow
/ none" is actually keyed off of before I called it LTS-equivalent in a
client deck. If it's eyeballed by a volunteer, say so; don't let it look like
a stress classification if it isn't one.

**LR:** Findings cards next — curated stat-plus-caveat cards: KSI trend,
protected share, street coverage, top corridors, hit-and-run, ward
concentration, the dooring undercount, and — new since you'd have seen this
last — a card for the PeopleForBikes BNA citywide network score, with
national ranking context and a line noting it's "not a reason not to ride."

**Dana:** Say that last part again.

**LR:** The BNA card presents Chicago's citywide 0–100 network score plus
subscores, low/high-stress mileage, score history over time, where Chicago
ranks nationally, and it flags that OSM data currency travels with the score
— plus a line framing the score as encouragement, not a safety verdict.

**Dana:** Okay, first — good, they used the real thing, not a knockoff. I was
fully braced for someone's homebrew "bikeability index" wearing our
initialism. If it's actually sourced to PeopleForBikes' methodology, citing
the population-size peer group, I'll take it seriously immediately, more
than anything else on this list. Second — I need to see the vintage. Our
2026 update tightened what counts as low-stress; if this card is running on
a stale pull from before that update, the score isn't comparable to what a
grant reviewer sees today, and someone should say which methodology vintage
it is, not just "PeopleForBikes BNA."

Third, and this is the part that'll actually make me put my pen down: a
network-quality score sitting on a page titled "Findings" next to a crash
trend card is going to get *misread* by literally everyone who isn't me. A
council staffer sees "score: 62" next to "KSI trend: down" on the same page
and hears one sentence: bikes here are getting safer. That's not what a BNA
score says. It says the low-stress network is getting more connected. Those
can move in completely opposite directions in the same city — I've watched a
city's BNA score climb while its severe-injury corridors stayed exactly where
they were, because connectivity and crash severity are answering different
questions. If the card doesn't put a wall between "network quality" and
"safety outcome" — different heading, different color, something — I will
actively distrust the page, not just the card, because it tells me nobody who
built this page understood the distinction I just made. The "not a reason
not to ride" line is doing some work, I'll give them that, but a caveat
sentence doesn't fix a layout problem.

**LR:** If it were laid out more carefully — separated visually, vintage
disclosed — would you use the card?

**Dana:** Then yes, honestly, more than I expected to. A 0–100 connectivity
score for Chicago specifically, broken into subscores, with national rank —
that's most of a paragraph of my grant memo already written for me, if
Chicago ever comes across my desk, which it hasn't yet but could. I'd still
independently verify the vintage against the methodology page before I
quoted it anywhere with my name on it. That's not distrust of OYL
specifically, that's just what I do with every number I didn't compute.

**LR:** Table next — ward rankings, sortable, CSV export, percent-protected
and percent-streets-with-bikeways columns.

**Dana:** The CSV export is the only feature on this whole list I'd call a
must-have without an asterisk. Everything else I want to interrogate first;
give me the CSV and I'll do my own math in five minutes and trust my own
math. Percent protected by ward is a real metric, that's basically a
DIY facility-taxonomy rollup, fine.

**LR:** There's now a ward one-pager — printable HTML per ward, safety index,
trends, infra stats, alderman contact and sponsorship record, menu-money
proxy, recent ward-matched news.

**Dana:** That's not built for me, and I want to be honest about that instead
of pretending it is. That's an advocate's leave-behind, a thing you hand an
alderman's staffer at a ward night. I've built the input data for things like
that but I'm never the one standing in the room handing over the page. The
one piece I'd actually pull from it is the menu-money-versus-safety-index
juxtaposition — if it's really sitting the ward's danger score next to its
menu spend on the same page, that is precisely the mismatch Active Trans has
been naming for years as the mechanism behind inequitable lane distribution
on the South and West Sides. If that pairing is really there and not just
two unrelated numbers on the same page, that's more useful to my work than
almost anything else you've shown me, because I currently do that
cross-reference by hand, ward by ward, from two separate PDFs.

**LR:** Two separate PDFs — say more.

**Dana:** The Daily Line's menu-money writeups and whatever capital-plan PDF
the city published that quarter. I keep a shared doc, embarrassingly, that's
just me copy-pasting ward numbers from one PDF next to numbers from another
PDF so I can eyeball whether the wards with the worst crash severity are
also the wards getting painted lanes instead of protected ones. It's slow
and it's manual and I redo it maybe twice a year because nobody's paying me
to keep it current.

**LR:** Does the one-pager's danger index change anything, given what you
said earlier about denominators?

**Dana:** Only if I can see the math. "Safety index" as a phrase makes me
brace the same way "danger score" does — tell me it's a percentile blend of
crashes-per-10k-population and crashes-per-bikeway-mile, tell me the window,
tell me the severity weighting, or I file it as a marketing number, not an
analytical one, and I won't put it in front of a client no matter how good
the ward-page layout is.

**LR:** There's a Sources page — full provenance catalog and known
limitations — and a separate Methodology page, new since the last time this
kind of site would've come across your desk, explaining how every number is
computed.

**Dana:** That's the one I actually go looking for first on any dashboard now,
before I look at a single map. If it exists and it's specific — not "we use
industry-standard methods," actual formulas, actual windows — that buys the
whole rest of the site a lot of benefit of the doubt from me. If the safety
index math I just asked about lives there in plain language, I'll take back
some of what I said about filing it as marketing.

**LR:** Action page — 311, Bike Lane Uprising links, alderman contacts,
upcoming hearings, recent news.

**Dana:** Not my page. That's downstream of my work, not part of it. I don't
call 311, I write memos that other people use to decide what to call 311
about.

**LR:** There's a Contributing page — downloads, docs, how to fork this for
another city.

**Dana:** Now that's interesting to me in a completely different way than
you'd expect — not because I'd contribute code, but because "fork this for
another city" is exactly the sentence that makes me want to check whether
the facility taxonomy and the BNA integration are portable or Chicago-
hardcoded. If a city I advise wanted to stand up something like this, I'd
want to know the answer's "yes, cleanly" before I recommended it, not after.

**LR:** Now the two areas I want to spend real time on. First: bike-lane
obstructions. There used to be a mock obstruction layer on the main map; it's
now been pulled off the main maps entirely and moved to a separate gated,
watermarked preview page, explicitly synthetic, excluded from the API,
pending an actual data-sharing conversation with Bike Lane Uprising.

**Dana:** Good. That's the single best change you've described to me today,
and I want to say clearly why, because I was ready to be much angrier about
this than I'm about to be. Mock data sitting on a live map, next to real
crash points, is a trust bomb — someone screenshots it, it ends up in a
council deck with no asterisk, and six months later a reporter calls the
city asking why bike lane blockages are "down 40%" when nothing changed, and
the answer is "oh, that was never real." I have watched exactly that kind of
thing happen with a placeholder layer somebody forgot to caveat loudly
enough. Pulling it off the main map, watermarking it, gating it behind a
page that announces itself as a preview, and excluding it from the machine-
readable API so nobody's script can accidentally treat it as ground truth —
that's the correct move, full stop. I still don't love that it exists at
all rendered as anything, even gated — Bike Lane Uprising's actual value is
its 3-hour refresh cadence and its use in real litigation, and a synthetic
stand-in can't do either of those jobs, so I'd tell them: don't let anyone
mistake the preview for a roadmap toward "we'll always have synthetic
obstructions," make sure the page reads as "we want the real feed and here's
what it'll look like the day we get it," not as a permanent feature.

**LR:** And the second: OYL is explicit that it does not normalize any crash
count by ridership — no counters, no bikeshare trips, no Strava — and says so
directly. The BNA card is network quality, separately, not crash-rate
normalization.

**Dana:** This is the caveat I respect most on the entire site, and also the
one I'll push hardest on, because respecting it and accepting it aren't the
same thing. Saying "we have no exposure data and we're not going to pretend
otherwise" is more intellectually honest than 90% of the crash dashboards
I've reviewed for a living — most of them just don't mention it, which is
worse than what OYL is doing. But it doesn't change my behavior much, because
it can't — I still can't hand a raw crash-density map to a room and say
"this is where it's dangerous," because a corridor with 40 crashes and heavy
ridership might be objectively safer per rider than a corridor with 8 crashes
and almost nobody riding it, and the map alone will make the second one look
fine. What I'd accept as good-enough: even a rough proxy is better than none
— 311 bike-related request volume as a crude ridership signal (imperfect,
but I saw it's already in your data as a proxy layer for something else), or
CDOT's own bike counter program if Chicago runs one, or frankly just
publishing bikeway-mile density as an explicit *second* denominator next to
the crash count, the way the coverage metrics already do it for
infrastructure. The site clearly has the instinct — the ward table already
reports percent-protected against street-miles as a denominator. Do the same
thing for crashes: crashes per bikeway-mile alongside crashes per capita, and
say plainly "this is a proxy for exposure, not exposure itself." That's not
the full HIN-style fusion I'd want in an ideal world, but it's honest and
it's better than raw dots.

**LR:** New areas I haven't covered yet: a news-coverage layer — recent
bike-safety headlines from allowlisted RSS feeds, matched to wards, aldermen,
routes, and projects with an auditable "via" showing why each match was made;
and a proposed-and-in-progress-projects roster — hand-curated,
volunteer-reviewed status, no geometry, just cards.

**Dana:** The news layer I'd mostly scroll past — journalism-adjacent context
isn't my input, I work from primary data, and a headline match is one more
layer of indirection I'd have to verify before citing. The "via" audit trail
is the only reason I'd even glance at it — if I ever did use a matched
headline I'd want to see exactly why the matcher thought it belonged to that
ward before I repeated the claim, and it sounds like that's there, which is
the right call given how easy it is for keyword matching to misattribute a
story to the wrong ward.

The proposed-projects roster is more interesting to me, actually, more than I
expected. "No geometry, cards only, because no machine-readable planned-
bikeway data exists" — that's a real, documented gap, that's not OYL being
lazy, I've hit that exact wall myself trying to get a future-network layer
out of a city's own planning department. A hand-curated status roster with
citations is a legitimate stopgap for that, and it's honest about being a
stopgap. What I'd want to know before I used it: who's doing the volunteer
review, how often, and what happens when a project status goes stale — a
"proposed" project that quietly died two years ago and nobody updated the
card is worse than not having the roster at all, because now I'm citing a
zombie project as evidence of momentum.

**LR:** And the agent layer you flagged earlier — the static `/api/v1/` JSON
API plus `llms.txt`, versioned, additive, every file opening with a `_meta`
envelope: tier, provenance, license, link to the human page, JSON schema.
The obstruction layer is excluded from it entirely.

**Dana:** Okay, now I care. A static, versioned, schema'd API where every
file declares its own tier and provenance in the payload — that's actually
better hygiene than most paid data products I've paid for. The tier badge
traveling *with the data itself*, not just displayed on a webpage a human
happens to be looking at, means if someone downstream builds an AI summary
off this feed, the "proxy" or "mock" label can't get silently stripped out
in translation the way it does today when someone screenshots a webpage into
a slide deck. That's the actual fix for the trust-bomb problem I described
with the obstruction layer, generalized — and excluding the synthetic layer
from the API entirely means no chatbot can accidentally cite mock obstruction
data as fact to someone who asked it a real question. That's the single most
methodologically serious thing on this whole tour, more than the BNA card,
more than the CSV export. I'd want the crash layer's `_meta` to explicitly
carry the no-ridership-normalization caveat and the dooring-undercount flag
in the payload, not just on the webpage — if it's only on the webpage, the
same caveat-stripping problem I just described happens to an AI reading the
API instead of a human reading the site.

---

### Gap probing

**LR:** Picture yourself prepping to advise a city on network investment
targets — your persona-appropriate scenario. You open OYL. What do you look
for first, and where does it fail you?

**Dana:** First thing I do on any city's dashboard is find the methodology
page, which exists here, so that's already ahead of most. Then I go looking
for a severity-weighted, multi-source injury network — something built like
SF's HIN, hospital data plus police data — because that's the actual
capital-prioritization artifact I'd bring into that meeting. It fails me
there completely: everything here is single-source, police-report crash
data, full stop, same undercounting problem as everywhere else. The dooring
flag is a start, but it's one narrow slice of a much bigger undercounting
problem that touches severity and race, not just crash type.

**LR:** Of everything OYL does not have, which single absence costs you
most?

**Dana:** Exposure data, no contest, and I said why already — without it,
every crash-count comparison between corridors risks conflating danger with
popularity. Second place, not close, is the lack of a real HIN-style fusion
with hospital records. Those are actually the same complaint at two
different altitudes: OYL has one denominator missing and one numerator
uncorrected.

**LR:** If OYL handed you one export a week, what's in it, who gets it?

**Dana:** The ward CSV, with percent-protected and crashes-per-bikeway-mile
added as an exposure proxy column, plus whatever the BNA subscore delta was
that week if it moved. I'd forward that to whichever partner city or funder
is asking me for a Chicago comparison point that week — right now that's
nobody specific, but the ask comes up two or three times a year and I
currently build that comparison from scratch each time.

**LR:** Does the no-ridership-normalization caveat change how you'd use the
site, concretely?

**Dana:** It changes my caption, not my map. I'd still show the crash-density
map in a room if I had to, but I'd never let it stand alone — I'd put the
sentence "no exposure data; treat corridor comparisons as suggestive, not
risk-ranked" directly under it every single time, in my own words, because I
don't trust an audience to remember a caveat that lived on a different page
than the picture they're looking at.

---

### Magic-wand close

**LR:** Magic wand — one dataset that doesn't publicly exist appears, clean
and current. What is it?

**Dana:** Chicago bike counter data, city-run, permanent counters, published
like a transit ridership feed. Not Strava, not a proxy — actual counts at a
representative sample of corridors, the way Portland and a couple of others
already do it. That's the one thing that would let me stop hedging every
sentence I say about this city with "but we don't know how many people are
actually riding here."

**LR:** One chart or map you could put in front of your hardest audience
that ends an argument?

**Dana:** A corridor map where color is severity-weighted injury rate per
estimated rider-exposure — hospital-fused if I'm dreaming, police-only with
an honest undercounting disclosure if I'm not — with facility grade as a
second encoding, protected versus painted versus nothing, laid right over
it. That single image says "here's where it's actually dangerous, here's
what kind of infrastructure is or isn't there, and here's how much that risk
is or isn't explained by just having more riders." Nobody's built that for
Chicago specifically that I've seen. If OYL's crash layer, coverage metrics,
and a real exposure proxy ever got fused into one map like that, I would
actually stop being the person in the room who says "you've built a
ridership map, not a risk map."

**LR:** What would make you stop using a site like this after trying it
once?

**Dana:** Finding one number I could disprove. If I pull the CSV, do my own
math, and the safety index or the BNA score doesn't reproduce what the
methodology page says it should, I don't come back — not because the error
is big, but because I no longer trust anything else on the site, and I don't
have the bandwidth to re-verify a source that's already burned me once. The
honesty about tiers earns a lot of goodwill up front; one broken number
spends all of it at once.

---

## Analysis memo

```
participant: us-bna-analyst
confidence_notes: >
  Reasonably in-world throughout — the persona's fixations (denominators,
  methodology transparency, HIN fusion, menu-money equity) map cleanly onto
  the stimulus's new BNA card and ward one-pager, so those exchanges felt
  earned rather than forced. Two places felt thinner: (1) her reaction to
  the news-coverage layer is mostly indifference by design (out of her
  evidentiary world), which is correct per the rules but means that section
  is low-information — a real informant in her role might have more to say
  about journalism-as-corroboration than this transcript captures. (2) her
  enthusiasm for the agent-layer/API section leans on inferring intent
  (tier-in-payload prevents caveat-stripping) that is plausible for her
  world but not explicitly evidenced in the us-thinktank.md brief — flagged
  as an inference, not given as fact, and reflected as a latent need below
  rather than a stated one.

stated_needs:
  - need: A machine-verifiable, downloadable ward-level dataset she can
      independently recompute and cross-check against published summary
      numbers.
    evidence_quote: "The CSV export is the only feature on this whole list
      I'd call a must-have without an asterisk... give me the CSV and I'll
      do my own math in five minutes and trust my own math."
    underlying_job: She must be willing to attach her professional
      credibility to any number before it goes in a client memo; the export
      lets her verify rather than trust.

  - need: A per-number methodology page with actual formulas (windows,
      weighting, denominators) rather than a general description.
    evidence_quote: "If it exists and it's specific — not 'we use
      industry-standard methods,' actual formulas, actual windows — that
      buys the whole rest of the site a lot of benefit of the doubt from me."
    underlying_job: She has been burned by consultants presenting z-scored
      counts as risk scores, and needs a defensible paper trail before she
      will repeat a number to a funder or reviewer.

  - need: Explicit disclosure of which methodology "vintage" a cited score
      (specifically the BNA card) reflects, given that the underlying
      methodology itself changes over time.
    evidence_quote: "Our 2026 update tightened what counts as low-stress; if
      this card is running on a stale pull from before that update, the
      score isn't comparable to what a grant reviewer sees today."
    underlying_job: She must certify that a comparison (year-over-year, or
      city-to-city) is apples-to-apples before she'll let a client use it in
      a funding submission.

  - need: A visual/structural separation between "network quality/
      connectivity" metrics (BNA) and "safety outcome" metrics (crash
      trend) so they cannot be read as the same claim.
    evidence_quote: "A council staffer sees 'score: 62' next to 'KSI trend:
      down' on the same page and hears one sentence: bikes here are getting
      safer. That's not what a BNA score says."
    underlying_job: She needs the artifact itself to prevent the single
      misreading she is most professionally afraid of being blamed for
      downstream.

  - need: Some form of exposure/ridership proxy joined to the crash layer,
      even an admittedly imperfect one (bikeway-mile density, 311 volume),
      rather than raw counts alone.
    evidence_quote: "Do the same thing for crashes: crashes per bikeway-mile
      alongside crashes per capita, and say plainly 'this is a proxy for
      exposure, not exposure itself.'"
    underlying_job: She cannot present a raw-count comparison across
      corridors without inviting the exact "ridership map, not a risk map"
      critique she herself levels at others.

latent_needs:
  - need: A severity-weighted, multi-source ("HIN-style") injury layer that
      corrects for police-data undercounting, distinct from a simple dooring
      flag.
    inference_basis: She named this unprompted as the very first thing she
      looks for on any city dashboard ("First thing I do... then I go
      looking for a severity-weighted, multi-source injury network") and
      explicitly said the existing dooring flag addresses only "one narrow
      slice of a much bigger undercounting problem." This is a documented
      requirement of her world (HIN methodology, SF DPH fusion), not a
      guess.
    risk_if_wrong: If overbuilt as a literal hospital-data integration, this
      is a multi-year, cross-agency data-sharing project OYL cannot pull off
      alone; if underbuilt as cosmetic ("severity" color-coding without a
      real undercounting correction), it will not satisfy her and may read
      as performative to exactly the audience most likely to check.

  - need: A ward-level cross-reference view that puts menu-money spend
      directly beside the ward safety/danger index on the same screen (not
      just adjacent sections of the one-pager).
    inference_basis: She described, unprompted, a specific personal
      workaround — a manual shared doc where she copy-pastes ward numbers
      from two separate PDFs (Daily Line menu-money writeups, city capital
      PDFs) "twice a year" specifically to eyeball this mismatch — and
      called the one-pager's juxtaposition of the two "more useful to my
      work than almost anything else you've shown me" if genuinely paired.
      The workaround, not the stated praise, is the evidence.
    risk_if_wrong: If the one-pager's menu-money and safety-index numbers
      are laid out far apart or not visually paired, this need goes
      unsatisfied even though the raw data exists — the risk is a layout
      failure being mistaken for a data-coverage success.

  - need: Machine-readable caveats (tier, undercounting/no-ridership-
      normalization flags) carried inside the API payload itself, not only
      rendered as page copy on the human site.
    inference_basis: She drew a direct, unprompted analogy between the
      obstruction-layer trust failure mode she described ("someone
      screenshots it... six months later... 'oh, that was never real'")
      and what she called "the same caveat-stripping problem" applied to an
      AI reading the API instead of a human reading a page — explicitly
      requesting the no-ridership-normalization and dooring caveats live in
      the crash endpoint's `_meta`, not just the webpage.
    risk_if_wrong: This assumes AI/agent consumers of the API are a real,
      near-term audience for OYL; if that channel sees negligible use, this
      is low-value engineering effort relative to her higher-priority asks
      (exposure proxy, HIN-style severity fusion).

  - need: A visible revalidation/staleness signal on the proposed-projects
      roster (last-reviewed date, explicit "still active" confirmation),
      not just a status label.
    inference_basis: She raised this without being asked a follow-up on it —
      "a 'proposed' project that quietly died two years ago and nobody
      updated the card is worse than not having the roster at all, because
      now I'm citing a zombie project as evidence of momentum" — generalizing
      from her own professional fear of citing something that turns out to
      be stale, the same fear that drove her BNA-vintage question.
    risk_if_wrong: If the roster's existing "status + status date + note"
      fields already satisfy this (per the inventory, they do carry a status
      date), the gap may be smaller than she perceives — worth checking
      whether her objection is about a missing field or about that field's
      visibility/prominence on the card.

reactions_to_existing:
  - feature: Transportation map (crash density + facility grade + cameras)
    verdict: distrusts (crash layer) / would-use (facility-grade layer)
    why: Reflexively invokes "ridership map, not risk map" for raw crash
      density absent a denominator; treats facility-grade coloring as
      directly usable if traceable to NACTO taxonomy.

  - feature: Network map (schematic, comfort-floor filter, no safety data)
    verdict: would-use, with a correction
    why: Reads the comfort-floor filter as a lay analog to an LTS threshold
      and approves of the instinct, but wants to know what it's actually
      keyed off before calling it stress-equivalent in a client deck —
      misreading risk flagged by her own hedge, not a misreading she fully
      commits to.

  - feature: Findings card — PeopleForBikes BNA citywide score
    verdict: would-use, conditionally / distrusts current presentation
    why: Genuinely enthusiastic that OYL used the real named methodology
      rather than a knockoff index, and would want to use it as a ready-
      made grant-memo paragraph — but currently distrusts the page layout
      because it sits beside a crash-trend card without a visual wall,
      inviting the "score = safety" misreading she considers the single
      most damaging failure mode a reader could walk away with.

  - feature: Ward table + CSV export
    verdict: uses
    why: The one feature endorsed without qualification — lets her
      recompute and independently verify rather than trust a published
      number.

  - feature: Ward one-pager (safety index + menu-money + alderman record)
    verdict: would-use (menu-money/index pairing) / ignores (rest, not her
      audience)
    why: Explicitly says most of the one-pager isn't built for her role
      ("not the one standing in the room handing it over"), but singles out
      the menu-money-vs-safety-index juxtaposition as replacing a manual
      cross-PDF workaround she currently does by hand.

  - feature: Sources / Methodology pages
    verdict: uses
    why: First page she says she'd look for on any dashboard; explicit
      formulas would retroactively raise her trust in the safety index she
      otherwise flags as a marketing number.

  - feature: Action page (311, hearings, contacts)
    verdict: ignores
    why: "Not my page... I write memos that other people use to decide what
      to call 311 about." Clean out-of-role indifference, consistent with
      shared-rules requirement for genuine disinterest.

  - feature: Contributing / fork-for-another-city page
    verdict: would-use (for a different purpose than intended)
    why: Not interested in contributing code, but interested in whether the
      BNA integration and facility taxonomy are portable, as due diligence
      before recommending the OYL model to a different client city.

  - feature: Mock obstruction layer (moved to gated preview, excluded from
      API)
    verdict: would-use (the change itself), residual distrust of the
      artifact
    why: Calls the demotion off the main map "the single best change" in
      the stimulus and explicitly approves of API exclusion as preventing
      downstream misuse; still uneasy about the preview page existing at
      all as a rendered artifact rather than purely a stated intent to seek
      real data.

  - feature: No-ridership-normalization caveat
    verdict: distrusts-but-respects the disclosure; behavior largely
      unchanged
    why: Calls it the most intellectually honest caveat on the site, better
      than most dashboards she reviews professionally, but says it changes
      her caption, not her map — she still won't present raw crash density
      as risk without appending her own spoken caveat every time.

  - feature: News-coverage layer (ward-matched, "via" audit trail)
    verdict: ignores, mostly
    why: Out of her evidentiary world by design (works from primary data,
      not journalism); the audit trail is the only element she'd check if
      she ever did use a match, consistent with her general demand for
      traceable provenance.

  - feature: Proposed-projects roster (status cards, no geometry)
    verdict: would-use, cautiously
    why: Recognizes the underlying gap (no machine-readable planned-
      bikeway geometry exists anywhere) as real and documented from her own
      professional experience, not an OYL shortcoming; wants staleness
      controls before treating any card as current evidence of momentum.

  - feature: Agent layer (/api/v1/, llms.txt, _meta envelope, tier/
      provenance in-payload)
    verdict: would-use / uses (highest-praise reaction in the interview)
    why: Calls the tier-and-provenance-in-payload design "better hygiene
      than most paid data products I've paid for" and the strongest
      structural answer to the obstruction-layer trust problem, generalized
      to every layer; wants the crash layer's caveats specifically pulled
      into machine-readable metadata, not left as page copy.

data_they_bring: >
  A working cross-PDF manual practice of pairing ward-level menu-money
  writeups (The Daily Line) against capital-plan PDFs to eyeball equity
  mismatches, redone roughly twice a year. A standing habit of diffing two
  GIS exports of the same bikeway layer to distinguish real infrastructure
  change from reclassification/relabeling when a city's score moves. A
  default skepticism toward any Strava-based exposure proxy, grounded in a
  specific remembered rebuttal (a city engineer's "BMX kid going to school"
  objection) rather than abstract methodology critique. A working definition
  of "convinced" that requires geometric traceability — a score delta must
  map to a segment she can point to on a map, not just a reclassified label.

deal_breakers: >
  Finding one number on the site that fails to reproduce when she does the
  underlying math herself from the CSV/methodology page — she frames this as
  an unrecoverable trust event ("I don't come back... I no longer trust
  anything else on the site"), not a proportional one. Separately: a "danger
  index" or "safety index" presented without an accessible formula reads to
  her as marketing, not analysis, and she will not cite it regardless of how
  good the surrounding site is.

vocabulary: >
  LTS / low-stress network, connectivity (vs. lane-miles), HIN /
  severity-weighted, exposure / denominator, underreporting /
  undercounting, KSI, facility taxonomy ("consistent with NACTO"),
  "who's not in this data," "ridership map, not a risk map" (her
  signature phrase), "vintage" (of a methodology/score), tier/provenance,
  peer-group / population-size grouping (BNA-specific).

confidence_notes: >
  See the top-level confidence_notes field above; duplicated here per the
  template's field name in 01-lead-researcher.md — the analyst's degree of
  enthusiasm for the agent-layer/API design is the most extrapolated
  reaction in this transcript (plausible for her professional world's
  concerns about provenance, but not drawn from a specific documented
  precedent in evidence/us-thinktank.md the way, e.g., her HIN or
  menu-money reactions are). Treat that section's strength as a
  medium-confidence read, not a high-confidence one.
```
