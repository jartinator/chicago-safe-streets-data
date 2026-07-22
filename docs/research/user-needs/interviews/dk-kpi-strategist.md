# Interview: Søren Lindqvist (Copenhagen KPI & political-narrative strategist)

**Run date:** 2026-07-21
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** (reflects `main` as
of 2026-07-21 — home/orientation page, ward one-pager, methodology page,
static agent API, news-coverage layer, proposed-projects roster, PeopleForBikes
BNA score, and the gated obstructions-preview page all included as "new since
last run").
**Persona file:** `personas/dk-kpi-strategist.md`. **Evidence base:**
`evidence/europe-nl-dk.md`.

---

## Transcript

**Researcher:** Thanks for making time. Start wherever's easiest — describe
your role right now, and walk me through the last decision about street
safety you actually tried to influence. What did that involve, step by step?

**Søren:** Ha, "street safety" — you mean traffic safety generally, or
specifically the bicycle account? Fine, I'll take the broad one. Three weeks
ago I was in Lyon for a delegation briefing — a French mid-size city council
considering whether to commit to a numeric modal-share target for 2030. My
job was two slides. First slide: Copenhagen's satisfaction trajectory,
83% to 97% between the 2006 and 2016 Bicycle Accounts, track width and
quantity broken out separately, with the printed 2025 target sitting right
next to the current number so the gap is visible. Second slide: what
happens when a city publishes an account with no owner attached to the
number — I showed them a German mid-size city's plan that had targets nobody
in the administration had personally signed their name to, and by year three
it had quietly stopped being cited in council. That's the whole talk,
really. Numbers next to promises next to names.

**Researcher:** Who did you need to convince in that room, and what did
"convinced" look like?

**Søren:** The deputy mayor for mobility and, more importantly, her budget
director, who was skeptical because the last cycling investment hadn't
moved ridership as fast as promised. "Convinced" meant the budget director
agreeing to attach a number and a year to the ask before it went to full
council — not "we will improve cycling," but "we will reach 80% satisfaction
with protected-lane coverage by 2028, reported at the halfway point." If I
leave a room with enthusiasm but no printed target, I've failed. Enthusiasm
evaporates by the next budget cycle.

**Researcher:** What information sources do you touch in a normal week for
this kind of work?

**Søren:** The Bicycle Account archive — ours and increasingly other cities'
attempts to copy the format. SWOV's fact sheets when a delegation asks about
crash trends, because SWOV is the one number nobody in the Netherlands
argues with — it's centrally run, methodologically stable across decades, so
you can trust a trend line from it in a way you can't trust a trend line
assembled from three different sources. The Copenhagenize Index when
someone wants a ranking to put on a slide, though I have complicated
feelings about it. And whatever counters or open data the host city
publishes, which is usually the disappointing part — most cities have crash
points and nothing about how anyone feels about riding.

**Researcher:** Tell me about the last time you needed a number, map, or
chart and had to go get it yourself — something you built because nothing
gave it to you directly.

**Søren:** Constantly. For the Lyon brief I needed a side-by-side of
satisfaction-survey questions across four cities that all claim to run
"bicycle accounts," and none of them ask the same question the same way —
one asks "are you satisfied with cycling conditions," another asks about
specific infrastructure types. I built a spreadsheet mapping each city's
question wording to the nearest Copenhagen equivalent, by hand, over about
four hours, because if you put mismatched survey questions on one chart a
sharp council member catches it in the room and the whole account looks
sloppy. That spreadsheet is now version 6. I keep a "translation table" for
basically every delegation because none of this is standardized outside
Denmark.

**Researcher:** And a time when data — or the lack of it — actually sank an
argument you were making?

**Søren:** Amsterdam, two years ago, advising on whether to fund more
protected lanes given SWOV's own numbers showing cyclist fatalities rising
five years running despite infrastructure investment. A city councilor used
that exact fact against me — "you're telling us to spend more on
infrastructure while your own countryman's data says cyclists are dying
more, not less." I did not have exposure data in the room. I could not say
"yes, but ridership grew 30% in that period so the *rate* fell." Nobody had
that number in a form I could cite on the spot, and the meeting ended with
the item tabled. That's the one that stays with me — a true, alarming
absolute number beat a true, reassuring relative one, purely because the
denominator wasn't in the room.

**Researcher:** What data do you actively distrust, and what earned that
distrust?

**Søren:** Rankings assembled by consultancies with no published
methodology — I won't name names, you've seen the "top 10 bike cities"
listicles that appear every spring. And, honestly, any account published
once with no successor. A one-off dashboard reads to me like a press
release wearing a data costume. If I can't find last year's version and the
year before that, I assume nobody's accountable to it and I don't cite it
in front of a skeptical audience.

**Researcher:** Let's look at what a Chicago project called On Your Left! —
OYL — actually publishes. I'll walk through it piece by piece; tell me your
first reaction to each before I explain further. Start with the two maps —
one's a geographic Leaflet map with crash density and bikeway grades, the
other's a schematic transit-style map of 21 named routes with quality
grades and a comfort-floor filter.

**Søren:** The transit-style one is interesting to me immediately — that's
closer to how CROW trains you to think, network first, not intersection
first. A comfort-floor filter that grays out anything below "paint" is
something I'd screenshot and put in a masterclass slide about legibility.
The geographic crash map I've seen fifty versions of and it doesn't move me
much on its own — density maps are a commodity now. What would make me
actually use the network map: does it show *gaps* in the grid, the way
Fietsbalans scores directness? Or is it only showing what exists?

**Researcher:** Only what exists today — quality grade and mileage per
segment, no gap analysis against a spacing standard.

**Søren:** Then it's a nice picture of the present, not a diagnostic. I'd
use it to orient a delegation in five minutes. I would not use it to make
the case for where the next investment should go — for that I'd want to see
the holes, not just the coverage.

**Researcher:** Next — the Findings page. Curated cards: KSI trend,
protected-lane share, street coverage, top corridors, hit-and-run, ward
concentration, dooring undercount, and the PeopleForBikes BNA citywide
score.

**Søren:** Now, this is closer to a Bicycle Account instinct — someone
decided which seven or eight numbers matter and put them on one page
instead of forcing me to explore twenty views. That I respect. But every
card here is either a casualty count or a network-quality score. Where is
the rider's *experience* of it? Copenhagen's account is famous for one
number more than any other: 97% satisfied with cycle-track width. That's
not a casualty statistic, it's a felt-safety statistic, and it's the one
that moves a budget director because it's about voters, not corpses. I see
nothing here that asks a Chicagoan cyclist how safe they *feel*. That's a
hole, and it's the kind of hole that doesn't show up until you notice
what's missing.

**Researcher:** You mentioned a numeric target a moment ago — does anything
on the Findings page read as a target-with-owner to you, versus a
description?

**Søren:** No, and I looked for it instinctively. "11% of surface streets
have any bike infrastructure" is a description. It's not paired with "and
the transportation commissioner has committed to 20% by 2030." Without that
second half, this is a very well-produced status report, not an instrument
that can move a budget meeting the way ours does. I'd use these cards to
brief a delegation on "here is Chicago's baseline." I would not put a single
one of these cards in front of a skeptical alderman as a *reason to act*,
because none of them promises anything.

**Researcher:** Table page — sortable ward rankings, CSV export, percent
protected and percent-with-any-bikeway columns.

**Søren:** Useful, unglamorous, the kind of thing I'd actually download.
Fietsbalans-trained instinct: I want to sort fifty wards against each other
and immediately I'm thinking "this is a ranking without a published scoring
weight." If ward 3 beats ward 14 on your safety index, can I see the exact
formula, the weights? I distrust rankings I can't reproduce. Is the
methodology public?

**Researcher:** There's a separate methodology page — I'll come back to
that. What about the ward one-pager — one page per ward, safety index,
trends, infra stats, alderman contact and sponsorship record, menu-money
proxy, ward-matched news, meant to be handed to an alderman or a neighbor?

**Søren:** This is the most "Bicycle-Account-shaped" thing you've shown me
yet, and I mean that as real praise, which will surprise you given how much
I've been complaining. One page, printable, aimed at a specific person who
has to act — that's exactly the artifact discipline I preach in the
masterclass. My question is whether it publishes on a rhythm. Does ward 3's
one-pager next year look like this year's, so a councilor's staff can hold
two side by side and see movement? Or is it only ever "current state,"
regenerated silently each week with no anchor date printed on it?

**Researcher:** It's regenerated weekly with the rest of the site; there's
no dated, frozen "edition."

**Søren:** Then it's the format without the ritual. The value of a Bicycle
Account isn't the page, it's that the page comes out on a date everyone
expects and journalists diary it. A page that's always "now" can't be
compared to "then" unless somebody archives it. That's a fixable gap, and
it's the single most Copenhagen-flavored complaint I have about this whole
project.

**Researcher:** Understood — flagging that. Now the council and alderman
data — hearings, aldermen's sponsorship counts and no-votes, contacts,
menu-money spend per ward.

**Søren:** Fifty wards, each essentially a mini-municipality with a
veto-shaped budget line — extraordinary, I still find this structure
bizarre coming from a country with 98 municipalities total. Sponsorship
counts as a safety record — I'd use this the way I'd use a BYPAD module
score for "political commitment," except BYPAD scores it jointly with the
cyclist-organization reps in the room, so nobody can dispute the number
afterward. A sponsorship count assembled unilaterally by your team, however
carefully, is something an alderman's staffer will contest the moment it's
unflattering. Have you tested it against them?

**Researcher:** It's marked "derived — sponsorship proxy, not a vote
tally," and most passes are voice votes with no recorded roll call.

**Søren:** Then say that loudly on the page itself, not just in a
methodology footnote, because the first thing an alderman's staffer will
do with an unflattering ranking is find the asterisk and use it to dismiss
the whole card. I've watched a mayor's office do exactly this to a
Copenhagenize Index placement they didn't like — they didn't argue with
the data, they argued with the methodology being "somebody else's opinion."
You want the caveat load-bearing enough that it can't be used as a
dismissal weapon.

**Researcher:** Two more specific things I want your reaction to, since
they're central to how this site handles trust. First: OYL states plainly
that it does not normalize any of its numbers by cyclist ridership — no
counters, no bikeshare trips, no Strava, so nothing here is a per-rider
risk rate, only an absolute count. Does that caveat change how you'd use
the site? What would you accept as good-enough exposure data if you can't
get the real thing?

**Søren:** This is the Amsterdam meeting again, word for word. An absolute
count with a stated "we don't normalize this" is honest, and I respect the
honesty — most American dashboards I've seen don't even flag it, they just
publish the raw number and let you assume it's a rate. But honest omission
is still an omission that will be used against you exactly the way that
councilor used SWOV's rising-fatality count against me. If I'm standing in
front of a skeptical alderman with "crashes up 8% on this corridor" and no
denominator, the alderman's first move is "well, more people are riding
there now, that's success, not failure" — and I have nothing to counter
with either way. Good-enough exposure data, in order of what I'd actually
accept: bikeshare trip-start/end counts by station, even though bikeshare
riders aren't representative of all cyclists; permit or Complete Streets
project counts as a crude proxy for where volume is being induced; or
frankly, a single visible counter on two or three flagship corridors,
Copenhagen-bridge style — not because the data's more rigorous than
Strava, but because a counter people can see themselves passing does
double duty as instrument and as advocacy object. I'd rather have one
imperfect public counter than zero. I notice the BNA score you mentioned is
network quality, not volume — so it doesn't help me here either, it answers
a different question.

**Researcher:** Second: there's a bike-lane-obstructions layer. It's
entirely synthetic — mock data — and as of this version it's been pulled
off both main maps entirely and put behind a gated, watermarked preview
page, pending an actual data-sharing conversation with a group called Bike
Lane Uprising, and it's excluded from the API. What's your reaction to that,
now that it's quarantined rather than sitting on the live map?

**Søren:** Better than what I'd have guessed — pulling fabricated data off
the surfaces a real audience would encounter it is the correct instinct,
and quarantining it behind a watermark rather than deleting it outright
tells me the team wants to keep the schema alive for whenever the real
partnership lands. That's more careful than most projects I audit. But I'll
push on it anyway: a gate and a watermark stop an alderman's staffer from
screenshotting it by accident, they don't stop *me* from finding it if I go
looking, and if I ever found a project like this without having been told
in advance — the way you're telling me now — I would treat the entire
dataset catalog as suspect from that point forward, not just the
obstruction layer. Our world has a name for reports that route to a
government office and get tracked to resolution — the Fietsersbond
Meldpunt. What you're describing is a mockup of that shape with no
government office behind it yet and no real reports inside it. Fine as a
placeholder for a schema you intend to fill later. Not fine as something a
visitor stumbles onto believing it's real, which is presumably exactly why
you gated it. I'd ask one more thing: does the gate say *why* it's mock —
pending partnership — or just that it's a preview? If it doesn't explain
the "why," a journalist will assume you're hiding something rather than
waiting on somebody else.

**Researcher:** It states the reason — pending a Bike Lane Uprising
data-sharing conversation. Let me show you a handful of things that are new
in this version specifically. First, there's now a home/orientation page
that explains what OYL is in plain language, including a section on asking
an AI assistant questions through something called the agent layer.

**Søren:** The orientation page itself — fine, every serious tool needs
one, that's not remarkable. The AI-assistant section is the part I don't
have instincts for. In my world, nobody asks a chatbot about the Bicycle
Account; you read the PDF or you sit in the briefing. I'll be honest: I
don't know whether that's because Copenhagen hasn't needed it yet or
because it's genuinely not useful, and I won't pretend otherwise. I'm
guessing here, not reporting from experience.

**Researcher:** Fair. Related to that — there's a static, versioned agent
API, `/api/v1/`, with a discovery file so an AI tool can fetch structured
JSON directly: citywide trends, ward files, route report cards, council
records, news, proposed projects, each with a provenance tag.

**Søren:** Now that part I can evaluate, because it's just the Bicycle
Account's discipline applied to machine consumers instead of journalists —
versioned, every file stamped with its tier and provenance, nothing
authenticated or rate-limited. If it forces the same provenance rigor onto
whatever a chatbot says about Chicago cycling safety as it does onto the
human page, I approve in principle, the same way I'd approve of a
structured open-data export of the Bicycle Account. Whether anyone's
assistant actually calls it — that's outside what I can judge from Denmark.

**Researcher:** Next — a news-coverage layer. Recent bike/street-safety
headlines from allowlisted RSS feeds, matched to wards, aldermen, routes,
and proposed projects, with an auditable "via" field explaining why each
article got matched to what.

**Søren:** This is closer to something I'd use — a Bicycle Account without
press coverage attached is half the story, because in Copenhagen the
account's *impact* is partly measured by whether the press picks it up and
runs the satisfaction number as a headline. Matching news to wards
automatically is clever, but the auditable "via" field is the part that
actually earns my trust — I've seen automated tagging systems that quietly
mismatch an article about a different city's bike lane to a Chicago ward
because a street name collided, and then nobody can explain why. If I can
see the reasoning for each match, I'll believe the feature. Without it, I'd
assume it's wrong more often than it's right and stop trusting the whole
page after the first bad match I noticed.

**Researcher:** There's also a proposed-and-in-progress-projects roster —
hand-curated, volunteer-reviewed status with a date and note, official
links, citations, auto-joined news — but explicitly no map geometry,
because no machine-readable planned-bikeway layer exists yet, so these are
cards, never lines on a map.

**Søren:** This is exactly the gap I'd expect and exactly the honest way to
handle not having it. A roster of intentions without lines on a map is
still useful to me as a *pipeline* view — how much is promised versus
built — which is a number Copenhagen tracks too, we call it the difference
between "planned" and "realized" kilometers in a given budget cycle. I
would use this to build one slide: committed lane-miles this year versus
delivered lane-miles this year. That gap, tracked over successive editions,
is a KPI in its own right — arguably a better one than any single crash
count, because it's about whether promises get kept.

**Researcher:** Last of the new items — the PeopleForBikes Bicycle Network
Analysis score: a 0–100 citywide network-quality score with subscores,
low/high-stress mileage, score history, and national ranking context, with
a disclosure about how current its map data is.

**Søren:** This is the closest thing here to a Copenhagenize-Index
instinct — a defensible, external, comparable score rather than a number
Chicago invented about itself. I'd use it exactly the way I use the
Copenhagenize Index with a skeptical delegation: not as gospel, but as
social proof that an outside body, not the city itself, is grading the
homework. The national-ranking context is the useful part — a single
city's number in isolation invites "compared to what?" A ranking answers
that in one line. My caution, same as with Copenhagenize: does anyone
outside your team understand the subscore weights well enough to reproduce
them? If it's a black box scored by an external group, I'll cite it, but
I'll caveat that I can't defend the methodology myself if pressed, only
report it.

**Researcher:** Let's do a scenario. You're advising a mid-size US city
council considering a network-investment target, and someone hands you
Chicago's OYL site as "here's what a peer American city built." Open it.
What do you look for first, and where does it fail you?

**Søren:** First click is Findings, because that's where a curated
narrative should live — and it half-delivers, the cards are well-chosen but
none of them is a promise-with-a-date, which I already said. Second click
would be the ward one-pager for whichever ward the delegation's host city
most resembles, because that's the artifact I'd actually adapt into my own
slide deck. It fails me at the same spot both times: nothing on this site
tells me what Chicago has *committed* to by *when*. Every number is a
mirror held up to the present. Not one is a target with a name attached.
That is, for my purposes, the single costliest absence in the whole
catalog — costlier than the missing ridership data, even, because you can
work around a missing denominator with a caveat, but you cannot manufacture
a political commitment that was never made. That's not a data problem you
can fix with an API; it's a City Council problem. But the site could at
least surface *whether* one exists, the way it surfaces provenance tiers
for everything else.

**Researcher:** If OYL handed you one export or artifact every week, what
would it contain, and who would you forward it to?

**Søren:** A one-page delta: what changed since last week's edition — new
crashes, any infrastructure delivered, any council item that moved, any
news mention — with the prior week's numbers printed alongside so I can see
direction, not just state. I'd forward it to exactly the audience the
Bicycle Account is built for: a delegation host before a study tour, so
they arrive with the current baseline already absorbed and we spend the
visit on judgment, not orientation.

**Researcher:** Magic wand — one dataset that doesn't publicly exist
appears tomorrow, clean and current. What is it?

**Søren:** A Chicago-wide cyclist perceived-safety and satisfaction survey,
run on a fixed cadence, with the exact same three or four questions asked
the same way every time, broken out by ward. Not a crash count. A feelings
count, if you'll forgive the phrase — because that is the number that
moved Copenhagen's council for two decades, not the morgue data, and this
site has none of it. Second choice, close behind: real exposure data, any
form, even bikeshare-only.

**Researcher:** One chart or map you could put in front of your hardest
audience that ends an argument?

**Søren:** Two lines on one chart, over ten years: cycled kilometers (or
your nearest proxy — bikeshare trips, whatever) rising, and crash *rate*
falling, crossing visibly. That single crossing chart is what I couldn't
produce in Amsterdam, and its absence cost me the meeting. If Chicago ever
gets even a rough exposure proxy, that's the chart I'd build first, before
anything else on this list.

**Researcher:** Last question — what would make you stop using a site like
this after trying it once?

**Søren:** Finding the mock obstruction data somewhere I wasn't warned
about it — you've told me it's gated and labeled, so today it survives that
test. If I ever find a second undisclosed synthetic layer after being
told "everything's labeled," I stop trusting the labels entirely and I stop
citing anything on the site to a client, because my entire professional
value rests on never bringing a client a number I can't defend when
challenged. The other thing that would make me quietly stop: if next
year's edition looks structurally identical to this year's with no
archived predecessor to compare against. A dashboard that never lets me
see "compared to last time" isn't a Bicycle Account, it's a status page,
and I don't build a masterclass around a status page.

---

## Analysis memo

```
participant: dk-kpi-strategist
confidence_notes: The persona spoke fluently and skeptically everywhere its
  evidence base gives it standing (KPI/target discipline, satisfaction
  surveys, benchmarking, provenance-hawkishness toward mock/proxy data,
  network-vs-project framing). It went openly uncertain, as instructed by
  the shared rules, on the AI-assistant/agent-layer question — correctly
  flagged as outside its documented world rather than faking expertise.
  The scenario answer (what fails him first) leaned hard on one theme
  (targets/ownership) which is faithful to the evidence brief but means
  this interview is thin on, e.g., how he'd react to desktop-only/English-
  only constraints, or accessibility — those weren't raised because his
  world's evidence base doesn't document strong opinions there. Also thin:
  a real Copenhagen strategist would likely have more to say about EU/
  cross-border data-sharing norms (GDPR-adjacent instincts) that the
  evidence brief doesn't cover, so that gap was correctly left unexplored
  rather than invented.

stated_needs:
  - need: A published, numeric, dated political target attached to every
      headline KPI (not just a current-state count).
    evidence_quote: "Not one is a target with a name attached. That is, for
      my purposes, the single costliest absence in the whole catalog."
    underlying_job: Walk into a budget/council meeting holding a promise a
      specific official can be held to, not just a description of the
      present.

  - need: A cyclist perceived-safety / satisfaction survey, fixed
      questions, run on a fixed cadence, broken out by ward.
    evidence_quote: "A Chicago-wide cyclist perceived-safety and
      satisfaction survey... That is the number that moved Copenhagen's
      council for two decades, not the morgue data, and this site has none
      of it."
    underlying_job: Give the budget director something about voters'
      *experience*, not only casualty counts, since felt-safety data is
      what historically moved Copenhagen budgets.

  - need: A published, reproducible scoring methodology for any ranking
      (ward safety index, aldermen records) — weights visible, not a black
      box.
    evidence_quote: "If ward 3 beats ward 14 on your safety index, can I
      see the exact formula, the weights? I distrust rankings I can't
      reproduce."
    underlying_job: Defend a ranking in real time when a skeptical
      official disputes it, without being able to say "trust us."

  - need: An archived, dated "edition" of the ward one-pager (and ideally
      the whole site) so successive versions can be compared, not just a
      perpetually-current snapshot.
    evidence_quote: "A page that's always 'now' can't be compared to 'then'
      unless somebody archives it... it's the format without the ritual."
    underlying_job: Show a councilor's staff movement over time, the way
      the biennial Bicycle Account format is built to do.

  - need: A committed-vs-delivered lane-mileage tracking view built from
      the proposed-projects roster (promise vs. built), tracked across
      editions.
    evidence_quote: "I would use this to build one slide: committed
      lane-miles this year versus delivered lane-miles this year. That
      gap, tracked over successive editions, is a KPI in its own right."
    underlying_job: Produce a single defensible progress KPI that isn't a
      raw casualty count.

latent_needs:
  - need: A load-bearing, prominent (not footnoted) caveat on any
      accountability-facing ranking (aldermen sponsorship records, ward
      safety index) that pre-empts the specific dismissal an implicated
      official would reach for.
    inference_basis: He described watching a mayor's office dismiss an
      unflattering Copenhagenize Index placement not by disputing the
      data but by attacking "somebody else's opinion" / methodology
      framing, and separately predicted an alderman's staffer would "find
      the asterisk and use it to dismiss the whole card" if the caveat is
      buried. This is a documented failure mode in his world (rankings
      dismissed on methodology grounds), not a guess about Chicago.
    risk_if_wrong: If Chicago aldermen's offices don't behave like
      Copenhagen mayoral offices around ranking pushback (e.g., if local
      norms mean nobody reads methodology footnotes either way), over-
      engineering caveat placement could bury the actual number under
      defensive hedging that no one asked for.

  - need: A visible, publicly-encounterable "counter" artifact (a real
      exposure/volume indicator people can see themselves counted in),
      not only a back-end exposure dataset.
    inference_basis: He volunteered the Rådhuspladsen/Dronning Louises Bro
      counters unprompted as his preferred fallback when asked what
      exposure data he'd accept short of the real thing, explicitly
      framing it as "instrument and advocacy object" simultaneously — this
      is a documented, specific practice in his evidence base (data as
      morale/press event), not an inference from OYL's current gaps alone.
    risk_if_wrong: This is a physical/civic intervention (a real counter
      on a real bridge), not a dashboard feature — if OYL's scope is
      strictly data publishing, this need may be entirely outside what
      the product can address, and treating it as a product requirement
      would misdirect effort toward advocacy infrastructure OYL doesn't
      own.

  - need: Explanatory "why it's mock/gated" framing surfaced at the point
      of encounter, not just in a methodology page — because absence of a
      stated reason reads as concealment to his professional instincts.
    inference_basis: He explicitly distinguished "fine as a placeholder...
      not fine as something a visitor stumbles onto believing it's real"
      and asked unprompted whether the gate explains *why* it's mock,
      concluding that without a stated reason "a journalist will assume
      you're hiding something." This tracks his documented professional
      habit of assuming absent methodology = concealment (Copenhagenize
      Index skepticism, distrust of unowned rankings).
    risk_if_wrong: OYL already states the reason (pending Bike Lane
      Uprising partnership) directly on the gated page per the inventory
      description read to him — so this need may already be substantially
      met; the residual ask is really about prominence/placement, not
      absence, and treating it as a bigger gap than it is would be
      overcorrecting on something already implemented.

reactions_to_existing:
  - feature: Network map (schematic, comfort-floor filter)
    verdict: would-use
    why: Matches CROW-trained network-first instinct; comfort-floor filter
      specifically called out as masterclass-slide material. Discounted
      once told it shows only existing coverage, not gaps against a
      spacing standard.

  - feature: Transportation map (crash density / bikeway grade)
    verdict: ignores
    why: "I've seen fifty versions of and it doesn't move me much on its
      own" — treated as a commodity artifact, not a differentiator.

  - feature: Findings cards
    verdict: would-use (with a caveat that limits its power)
    why: Approves of curation ("someone decided which seven or eight
      numbers matter"), but every card is casualty or network-quality, none
      is a felt-safety metric or a dated target — so he'd use it to brief,
      not to persuade a skeptical audience to act.

  - feature: Ward table + CSV
    verdict: would-use
    why: Practical, downloadable — but immediately probes for a
      reproducible scoring formula before trusting a ranked comparison.

  - feature: Ward one-pager
    verdict: would-use
    why: Closest fit to the one-page, named-audience artifact discipline
      he preaches; docked for having no dated, archived "edition" to
      compare against future ones.

  - feature: Council/alderman data (sponsorship, no-votes, menu money)
    verdict: distrusts (conditionally)
    why: Reads as a unilaterally-assembled accountability score without
      the joint stakeholder sign-off his world's comparable instrument
      (BYPAD) uses; wants the "proxy, not a vote tally" caveat made
      prominent rather than footnoted, based on a documented failure
      pattern (methodology-based dismissal of unflattering rankings).

  - feature: No-ridership-normalization caveat
    verdict: distrusts (the underlying data, not the caveat itself)
    why: Praises the honesty of stating it, but treats the absence as
      actively costly — directly analogized to a real documented episode
      (Amsterdam) where a rising absolute count with no denominator lost
      an argument to a hostile reading of the same fact.

  - feature: Mock obstructions layer (now gated/watermarked/API-excluded)
    verdict: would-use provisionally / conditionally distrusts
    why: Approves of quarantining a synthetic layer off primary surfaces
      and stating the reason; but flags that discovery-without-warning of
      any second undisclosed synthetic layer would collapse trust in the
      entire catalog, not just that layer — a documented all-or-nothing
      trust reflex in his world.

  - feature: Home/orientation page + agent-layer explainer (AI assistant
      access)
    verdict: uses (orientation) / unfamiliar (AI-assistant section)
    why: Orientation page treated as table-stakes, unremarkable. On the
      AI-assistant framing he explicitly declined to have an opinion —
      correctly stayed in-world rather than fabricating expertise his
      persona doesn't have.

  - feature: Static agent API (/api/v1/, llms.txt)
    verdict: would-use (evaluated abstractly, approvingly)
    why: Recognized as the same provenance/versioning discipline he values
      in human-facing publishing, applied to machine consumers; approved
      in principle but explicitly declined to judge real-world uptake.

  - feature: News-coverage layer (auditable "via" matching)
    verdict: would-use
    why: The auditable match-reason field is what earns trust; without it
      he says he'd assume frequent mismatches and abandon the feature
      after the first bad one he noticed.

  - feature: Proposed-projects roster (no geometry, cards only)
    verdict: would-use
    why: Reframed unprompted into a "planned vs. realized" pipeline KPI,
      a category his world already tracks; the missing geometry wasn't
      treated as a blocker to using it.

  - feature: PeopleForBikes BNA score
    verdict: would-use, with a defensibility caveat
    why: Closest analog to the Copenhagenize Index — valued precisely
      because it's external, not self-graded; flagged that he could cite
      it but not personally defend its subscore weights under challenge.

data_they_bring: A biennial, standardized cyclist satisfaction survey
  (Bicycle Account model) reported against printed numeric targets; a
  hand-built cross-city "translation table" reconciling incompatible
  survey question wording across cities (current live workaround, v6);
  SWOV-style centrally-run, methodologically stable crash statistics
  trusted specifically because of continuity, not just accuracy;
  BYPAD-style jointly-scored (not unilaterally-assembled) governance
  audits; Copenhagenize Index-style externally-run comparative rankings;
  visible public counters as a hybrid data/advocacy artifact.

deal_breakers: Discovering an undisclosed second mock/synthetic layer after
  being told everything is labeled (collapses trust in the whole catalog,
  not just that layer); a site that never archives dated editions, so no
  year-over-year comparison is possible (degrades it from "instrument" to
  "status page" in his framing, which he says he wouldn't build a
  masterclass around).

vocabulary: bicycle account, KPI, modal share, target (with owner and
  year), satisfaction survey, "the political level," press moment,
  cost-benefit / societal gain per kilometer, black spot, benchmarking,
  quality audit, network cohesion/directness (CROW terms), felt-safety /
  "a feelings count," edition (of a published account), denominator
  (used literally, re: exposure data).
```
