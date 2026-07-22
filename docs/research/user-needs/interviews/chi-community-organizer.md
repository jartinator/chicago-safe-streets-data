# Interview: Andre Thompson (West Side community organizer, composite persona)

**Run date:** 2026-07-21
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** (post home page,
ward one-pager, methodology page, static agent API, news-coverage layer,
proposed-projects roster, PeopleForBikes BNA score, gated obstructions
preview)
**Interviewer:** Lead Researcher persona (per `01-lead-researcher.md`,
`03-interview-guide.md`)
**Participant:** Andre Thompson persona (per `personas/chi-community-organizer.md`, `_shared-rules.md`)

---

## Transcript

**Researcher:** Thanks for making time. Start wherever's easy — tell me about
your role right now, and the last decision about street safety you tried to
move.

**Andre:** Easy's not really the word for July, but okay. I coordinate the
block-club coalition on the West Side — Austin, mostly, some overlap into
Garfield Park. Last real thing was three weeks ago: CDOT came back to the task
force to talk about phase two of the neighborhood network, the part that's
supposed to connect into North Lawndale. I had to stand up at that meeting and
tell forty residents why the phase-two corridor matters, because half the room
remembers phase one taking two years longer than promised and they want to
know why they should believe this round is different.

**Researcher:** Walk me through what "telling them" actually involved. What
did you bring into that room?

**Andre:** I brought the same one-pager I always bring — I built it myself in
a spreadsheet off the city's crash portal, filtered to our community areas,
plus the mileage numbers CDOT gave the task force directly, because CDOT
actually sends us numbers now, that's new in the last two years. I printed
twenty copies. Half the room doesn't touch a laptop at a 7pm meeting in a
church basement, so it has to be paper, has to be big font, has to say "here's
what got worse, here's what got fixed, here's what's coming." I don't hand
people a dashboard link. Nobody's pulling that up on their phone mid-meeting
except maybe two people, and one of them is me checking my own numbers.

**Researcher:** Who were you convincing, and what does convinced look like for
them?

**Andre:** Two audiences in that room, and they need different things.
Residents need to believe it's not just another study — they need "this
already happened in Belmont Cragin, here's the before-and-after," a promise
with a date on it. And then there's the alderman's staffer sitting in the
back who I need on record saying they'll push CDOT to keep the phase-two
timeline. Convinced for him means I hand him a number he can repeat to his
boss without getting corrected by CDOT's own people. If I say something and
CDOT's rep in the room contradicts me, I've lost the room and I don't get it
back that meeting.

**Researcher:** You mentioned building your own spreadsheet off the crash
portal. Tell me about the last time not having something built for you cost
you time, or cost you an argument.

**Andre:** Two years back, before the task force process really got going, I
tried to make the case that Chicago Avenue needed protection using nothing
but the city's raw crash dataset. Took me a weekend to filter it to just our
wards, because the portal doesn't know what a "community area" is — it wants
ward or it wants police district, and I had to cross-reference which census
tracts sit in Austin versus West Garfield Park myself. Alderman's office
looked at my numbers and said "that includes assaults and rear-enders, that's
not a corridor problem." They weren't wrong, and I didn't have time before
the vote to redo it properly. That's the argument that got tabled. I don't
forget that.

**Researcher:** What data do you distrust today, and what earned that
distrust?

**Andre:** 311. Everybody wants to point at 311 counts like it tells you
where the problems are. Austin's 311 volume on bike stuff is thin — not
because nothing's blocking the lanes, because folks either don't have the app,
don't trust it does anything, or already called three times about the pothole
on their block and gave up. I've had a downtown planner look at a 311 heat map
and say "see, it's quieter out west" like that settles something. It settles
that we report less. Doesn't settle a thing about what's actually happening on
Cicero. And cameras — don't get me started, I'll get to that when you show me
your thing, because I already know I'm going to have opinions.

---

**Researcher:** Let me walk you through what a site called On Your Left! has
built. It's an independent, read-only bike-safety dashboard for Chicago — it
doesn't take reports itself, it points people to 311 and Bike Lane Uprising.
Everything on it is labeled real, proxy, mock, crowdsourced, derived, or
no-data-yet. First: there's a home page now that explains what the whole site
is and who it's for, plus a section on asking an AI assistant questions
through something called an agent layer.

**Andre:** An AI assistant asking it questions on my behalf — for who, though?
Because that's not me and it's not the room I stand in front of. If some
alderman's staffer types "is Austin dangerous" into a chatbot and gets a
number back with no context, that's a new way for my community to get
described by somebody who never set foot here. I'm not against it existing.
I'm against it being the only front door. Show me the human page still says
the same thing plain, and I'll leave the AI part alone — that's for whoever
that's for.

**Researcher:** Next, the two maps. One's a geographic map — crash density,
bikeway network, wards, cameras. The other's a schematic transit-style map of
21 named routes, no safety data on it at all.

**Andre:** The geographic one — cameras on it. Right there is where I stop and
ask what "cameras" means before I let anybody in that church basement see it.
Because if it's coloring my ward by camera violations like that's a danger
score, I already know what that map says: Austin's dangerous because Austin
gets ticketed. And I know from ProPublica, from UIC, that Black and Latino
ZIP codes get ticketed at close to double the rate white ones do for the
same driving, and the late fees land on damn near half of low-income tickets.
So a map that shows "more red near you" where red means camera hits — that's
not a safety map to me, that's an extraction map. I need to know before I put
that on a screen in front of anybody: is it labeled a proxy for aggressive
driving, or does it read like ground truth? Because I've seen "objective"
tools get used to justify more enforcement in exactly the neighborhoods that
already have too much of it.

**Researcher:** It's labeled proxy — "aggressive-driving proxy, only exists at
camera locations." Does the label change your read?

**Andre:** It changes what I'd say out loud about it, not what the room sees
first. People don't read badges, they read color. If it's on the same map as
crash density and it's red where cameras are, somebody's going to conflate the
two whether the tooltip says "proxy" or not. I'd want it off by default, or I'd
want it a different visual language entirely — not the same red as crashes.
That's a "would use, but only if I control what's toggled on before I project
it."

The trail/route map — schematic, no safety data — that one I actually like
the idea of, but it's not my tool. That's for somebody planning a ride. I'm
not bringing a transit map to a public safety meeting, I'm bringing "here's
where people got hurt."

**Researcher:** Findings page — curated cards: KSI trend, protected share,
street coverage, top corridors, hit-and-run, ward concentration, dooring
undercount, and a PeopleForBikes network score with national context.

**Andre:** Ward concentration card — that's the one I'd actually screenshot.
"West Side wards carry the highest severe-crash concentration" — I've been
saying that in meetings for years with a printout from Governing magazine
because nobody funded a real study. If OYL just has that as a card with a
citation, that saves me a step. But — and I need you to actually hear this —
that same card is also the one that gets weaponized against me. Somebody at
a budget hearing pulls "Austin has the worst numbers" and uses it to say
"see, those neighborhoods are just dangerous" instead of "those neighborhoods
were never invested in." Same number, opposite conclusion, and the card
doesn't pick a side. Does it say why the numbers look like that, or does it
just say the number?

**Researcher:** It states the concentration as a fact with a deep-link into
ward detail; it doesn't attach a causal narrative in the card itself.

**Andre:** Then that's a stigma risk with my name on it if I'm the one who
hands it out. I'd want it paired — same page, not a click away — with
something like "this reflects decades of underinvestment, not neighborhood
behavior," or I'm not using that card solo in a room where somebody could spin
it. I'll use it, but I'll say the sentence myself before anyone else does.

The PeopleForBikes score, the network score — I don't know what that
organization is, honestly. Never heard the name before today. If it's telling
me Chicago's overall network is graded some number against other cities, I
don't have a use for that in Austin. That's a citywide bragging-rights number.
Somebody downtown cares about that for a grant application. I care whether my
block has a protected lane.

**Researcher:** Table page — ward rankings, sortable, CSV, percent protected,
percent streets with bikeways.

**Andre:** Now that's useful, that's the kind of number I already dig for
manually. If I can pull my ward's percent-protected against the citywide
average and put it next to the alderman's name, that's ammunition I don't have
to build myself this time. But — ranking. If it's "Austin ranked 47th of 50,"
that's the same stigma problem as the findings card, times ten, because now
it's a leaderboard and leaderboards get repeated without context by design.
I'd want to know: does the table itself explain why some wards rank low, or
does a resident just see a number next to their neighborhood's name with
nothing else? Because a rank without a reason is a headline waiting to
happen, and not the headline I want.

**Researcher:** Ward one-pager — a printable page per ward: safety index,
trends, infra stats, alderman contact and sponsorship record, a menu-money
proxy, recent ward-matched news.

**Andre:** Okay, now we're getting somewhere close to what I actually carry
into a room. Alderman contact plus sponsorship record on one page — that's
the "who's at the table, and have they shown up" piece I currently build by
calling the Ward Office myself and cross-referencing Legistar by hand, which
takes me most of an evening every time I need it fresh. If it's already done,
printable, one page — that's the thing I'd hand a neighbor and say "call
this number, ask about this vote."

But menu money — how sure is that number? Because menu money is the one
lever I actually use, and if I hand a neighbor a page that says "your
alderman spent $40,000 on bike safety" and it turns out the real ledger says
something different, I've burned trust with that neighbor and probably with
the alderman's office too, and I don't get a redo on that relationship.

**Researcher:** It's flagged proxy — a Ward Wise / Chi Hack Night extract,
not verified against source PDFs.

**Andre:** Then it doesn't go in front of a resident as a dollar figure
without me calling the Ward Office first to confirm it, same as I do now.
That caveat has to survive the print. If the plain-language version drops
"proxy, not verified" because it reads clunky on a one-pager, that's the kind
of thing that gets me embarrassed in front of a room I've spent years
building trust with. I need the asterisk to make it to paper, not just to
the webpage.

The "safety index" language — what is that, exactly?

**Researcher:** A 0–100 score blending crashes per population and crashes per
bikeway-mile, percentile-ranked against other wards. Explicitly relative, not
an absolute risk number.

**Andre:** Relative to what, though — relative to each other, or relative to
some standard? Because if my first instinct reading "62 out of 100" is "we're
failing a test," and that's wrong, then the page needs to say that up front,
not in a footnote. I'll be honest, on first look I read a score like that as
a grade, and grades under 100 read as failing to most people I know. If
that's a misread, that's a misread the page is going to cause for a lot of
folks in that basement, not just me.

Ward-matched news — recent stories tied to my ward?

**Researcher:** Yes — headlines from allowlisted RSS feeds matched to wards,
aldermen, routes, and projects, each with an auditable "why this was matched"
link.

**Andre:** That I like more than I expected to. Half of what convinces a room
is "did anybody outside our four walls notice this" — a Block Club headline
about our corridor sitting right there on the page saves me a Google search
I already do before every meeting. I'd want to know it's not padding the page
with stuff that barely relates — you said "auditable," meaning I can click
and see why it matched?

**Researcher:** Correct — every match carries a visible reason.

**Andre:** Good, because if I hand somebody a page that says "news about your
ward" and it's actually a citywide story that got tagged in by a stretch,
that's the kind of thing that makes a skeptical room stop trusting the rest
of the page too. One bad link and I lose the room's benefit of the doubt for
everything else on it.

**Researcher:** Sources page and a new Methodology page — full provenance
catalog with tier badges, plus how every number's computed.

**Andre:** That's not for the room, that's for me, the night before, checking
my own back before I stand up. Does it tell me in plain words, or is it
built for somebody who already knows what a percentile blend is? Because I
need to be able to read it fast at 9pm and then translate it myself — I'm
not going to read a methodology page out loud to forty people, I'm going to
read it so I can answer the one guy in the back who always asks "where'd you
get that."

**Researcher:** Action page — 311, Bike Lane Uprising, alderman contacts,
upcoming hearings, recent news, all together.

**Andre:** Upcoming hearings is the part I'd actually forward to people,
because "there's a public-comment slot on the 14th, here's how to sign up" is
the single most useful sentence I can put in a text message to a neighbor.
That's a real "what do I do" and it's more valuable to me than another chart.

**Researcher:** Now — bike-lane obstructions. This used to be discussed
alongside the crash map; it's moved. It's synthetic data, entirely fake for
now, kept off both main maps, and only shown on a separate gated, watermarked
preview page while they have a data-sharing conversation with Bike Lane
Uprising.

**Andre:** Wait — fake. Made up. Not "estimated," not "modeled off real
patterns" — invented.

**Researcher:** Correct, synthetic, and it's excluded from the API entirely,
not just gated on the site.

**Andre:** Okay, I want to sit on that a second, because my first reaction
before you said "excluded from the API" was actually anger, not confusion. If
that had shown up on the map I use in a meeting, mixed in with real crash
dots, and somebody in that room found out afterward it was made up — that's
not a bug to my crowd, that's the whole site burning down. That's the exact
thing that gets a tool permanently blacklisted in my coalition's group chat.
"They were showing us fake blockage data" is a sentence that ends relationships
with block clubs for good, and it doesn't matter how many other layers are
real. One caught fake number poisons the well for everything else on the
page, forever, in my experience.

So — good that it's not on the main map anymore. Good that it's watermarked.
But I need to ask: why does it exist at all if it's not real? What's a
"gated preview" for, and gated behind what — do I need a login, does a
neighbor stumble into it by accident?

**Researcher:** It's a separate page, clearly labeled as a demo/mockup, meant
to show what a future real obstruction layer could look like once real data
is available — it's not linked from the main navigation people would
normally use.

**Andre:** Then keep it exactly that buried. I don't want to have to explain
to a room why there's fake data anywhere on a site I vouched for, even on a
back page nobody clicks. If it ever migrates onto the map before Bike Lane
Uprising's real data is actually flowing, I'm done recommending this site,
full stop. That's not a maybe.

**Researcher:** Understood — noted as a hard line. Last stimulus item: the
site states plainly it does not normalize any crash count by ridership — no
counters, no bikeshare data, no volume data at all — and says so.

**Andre:** Honestly? That one bothers me less than you'd think, and it
bothers me for a different reason than you'd expect. Nobody in my meetings
is asking "per rider" — they're asking "did somebody get hit near my kid's
route." Raw counts are what a resident feels. What I'd actually push back on
is the flip side: don't let anybody use "no ridership data" as an excuse to
say "well maybe fewer people bike out west so the numbers look worse than
they are." I've heard that exact argument in a real room — "of course Austin's
crash count seems concentrated, nobody rides out there" — used to wave off a
real problem. If the caveat reads as "we can't tell you if it's actually more
dangerous per rider," that's a door somebody at CDOT could walk through to
minimize us again. The caveat has to protect against being used that way, not
just disclose the gap.

---

**Researcher:** Picture you're prepping for another task-force meeting next
month. You open OYL. What do you look for first, and where does it fail you?

**Andre:** First thing I look for is my own community areas, not wards —
Austin, Garfield Park, North Lawndale — because that's how residents actually
name their world, not "the 29th ward" mixed with pieces of two others. If
everything's sliced by ward and I have to do the cross-reference myself
again like I did with the city portal two years ago, that's the same
weekend of work I already told you about, just with better-looking charts.

**Researcher:** Of everything OYL doesn't have — what single absence costs you
most?

**Andre:** The task-force story. CDOT tripled our mileage and cut serious
injuries almost 40 percent in two years because residents sat at a table and
named the actual barriers — not because a website existed. Nowhere in what
you described is there a place that says "here's what happened when the
community and the city sat down and did this together," with a before number
and an after number, tied to which corridors, which task force. That's the
one story that gets a skeptical room to lean forward, because it's proof it
worked here, not somewhere else, not in theory.

**Researcher:** If OYL handed you one export a week, what's in it, who gets
it?

**Andre:** My ward's one-pager, refreshed, the day before whatever meeting's
coming — plus whatever news matched it that week. I'd forward it to the two
other block-club coordinators I coordinate with regularly and to the
alderman's staffer, so he's seeing the same page I am before we're in the
room together. That's actually most of what I already do by hand every week,
so if it showed up done, that's real time back.

---

**Researcher:** Magic wand — one dataset that doesn't publicly exist appears,
clean and current. What is it?

**Andre:** Real bike-lane obstruction data, not fake — actual Bike Lane
Uprising reports, joined by ward, with a flag for which blocks are chronic
repeat spots versus one-offs. That's the thing residents already photograph
themselves and have no idea where it goes. Second choice, and don't laugh:
menu money verified against the actual ledger, not the Chi Hack Night guess,
because that number is the one that gets an alderman's staffer defensive
fastest, and I want to be standing on solid ground when he pushes back.

**Researcher:** One chart or map you'd put in front of your hardest audience
that ends an argument.

**Andre:** Side by side, same scale: Austin's crash concentration next to
Austin's bikeway-mile share, both over the same ten years, with the task-force
start date marked as a vertical line, and the after-numbers from Belmont
Cragin sitting right next to it as the "this is what worked" comparison. Not a
danger index. A before-and-after with a name and a date on it. That's the
chart that makes a room believe change is possible, not just that things are
bad.

**Researcher:** What would make you stop using a site like this after trying
it once?

**Andre:** Catching one number that's wrong when I already told a room to
trust it. That's it, that's the whole list. Doesn't even have to be big — one
wrong menu-money figure, one fake obstruction dot that slipped somewhere it
shouldn't be, one ranking with no explanation that gets read out loud as "see,
Austin's just dangerous" — any one of those, and I'm not the guy who
recommends it to the next coalition meeting. I don't get a lot of chances
with these rooms. I'm not spending one on a tool that isn't sure of itself.

---

## Analysis memo

```
participant: chi-community-organizer
confidence_notes: >
  The persona speaks fluently to power dynamics, data provenance, and
  church-basement legibility because the evidence base is rich there. It is
  thinner on the newer agent-API and network-map areas, where the persona
  correctly signals disinterest/out-of-world rather than fabricating
  expertise (per shared-rules #2) — that disinterest itself is a valid
  finding, not a simulation gap, but the *depth* of that reaction is
  necessarily shallow because the evidence brief has little to say about
  AI-assistant consumption patterns for this audience. The BNA/PeopleForBikes
  reaction is similarly thin — the persona has no documented opinion of that
  organization, so "never heard of them" is the honest ceiling, not a richer
  critique.

stated_needs:
  - need: A single printable per-ward page combining alderman contact,
      sponsorship record, and local numbers, so he stops manually
      cross-referencing Legistar and calling the Ward Office each time.
    evidence_quote: "Alderman contact plus sponsorship record on one page —
      that's the... piece I currently build by calling the Ward Office
      myself and cross-referencing Legistar by hand, which takes me most of
      an evening every time I need it fresh."
    underlying_job: Arrive at a task-force or block-club meeting able to
      name, without hesitation, who is accountable and what they've done —
      credibility depends on not being caught unprepared in front of a room
      he has to keep convincing meeting after meeting.

  - need: Ward-percent-protected and percent-with-bikeways figures, pre-built,
      to compare against citywide and against the alderman's record.
    evidence_quote: "That's the kind of number I already dig for manually. If
      I can pull my ward's percent-protected against the citywide average
      and put it next to the alderman's name, that's ammunition I don't have
      to build myself this time."
    underlying_job: Build a specific, falsifiable ask ("you're below average,
      here's the gap") rather than a vague complaint, because vague asks get
      tabled.

  - need: Confirmation that provenance/reliability caveats (proxy labels,
      "not verified against source PDFs") survive onto the printed,
      plain-language version of a page, not just the web version's fine
      print.
    evidence_quote: "That caveat has to survive the print. If the
      plain-language version drops 'proxy, not verified' because it reads
      clunky on a one-pager, that's the kind of thing that gets me
      embarrassed in front of a room."
    underlying_job: Protect his own credibility as the trusted intermediary
      — he cannot afford to be the person who repeated an unverified number
      as fact to a room that trusts him personally, not the website.

  - need: A visible record of the CDOT task-force process itself — before/
      after numbers tied to a named community process, not just current-
      state stats.
    evidence_quote: "Nowhere in what you described is there a place that
      says 'here's what happened when the community and the city sat down
      and did this together,' with a before number and an after number...
      That's the one story that gets a skeptical room to lean forward."
    underlying_job: Give a skeptical audience proof that organized pressure
      converts data into infrastructure here, in Chicago, not as an abstract
      possibility — because his entire pitch to residents is "this can
      work," and he needs an existence proof, not a projection.

  - need: A weekly digest of his own ward's one-pager plus that week's
      matched news, ready to forward to coalition partners and the
      alderman's staffer.
    evidence_quote: "My ward's one-pager, refreshed, the day before whatever
      meeting's coming — plus whatever news matched it that week. I'd
      forward it to the two other block-club coordinators... and to the
      alderman's staffer."
    underlying_job: Keep every stakeholder who needs to show up "in the
      room" already aligned on the same facts before the meeting starts, so
      the meeting itself isn't spent relitigating numbers.

latent_needs:
  - need: Community-area (Austin / Garfield Park / North Lawndale) framing
      as a first-class geography, not just ward — or at minimum a mapping
      users can apply themselves without redoing the cross-reference by
      hand.
    inference_basis: >
      He independently volunteered, twice — once describing his current
      workaround with the city crash portal ("the portal doesn't know what a
      'community area' is... I had to cross-reference which census tracts
      sit in Austin versus West Garfield Park myself") and once as his first
      instinct opening OYL ("First thing I look for is my own community
      areas... If everything's sliced by ward... that's the same weekend of
      work"). This is a documented, repeated workaround costing him real
      hours, not a hypothetical preference.
    risk_if_wrong: If community-area framing turns out to be a niche ask
      specific to this composite and not shared by other West/South Side
      organizers, adding it could be low-leverage effort; but ward-only
      framing risks alienating exactly the audience OYL says it wants to
      reach (organizers who translate for residents), so the downside of
      omitting it looks larger than the downside of investigating it.

  - need: A visual/design safeguard so that camera-violation and crash-
      density layers cannot be read as the same kind of "danger," even when
      a badge correctly labels the camera layer as proxy.
    inference_basis: >
      He explicitly distinguished the label from the read: "People don't
      read badges, they read color... I'd want it off by default, or I'd
      want it a different visual language entirely — not the same red as
      crashes." This is a stated observation about how badges fail in
      practice for his audience, not a request for a feature per se, but it
      licenses a latent design need beyond what the badge system alone
      solves.
    risk_if_wrong: If badge-plus-tooltip already does enough (e.g., other
      personas or real users read labels more carefully than this composite
      predicts), a mandatory default-off/distinct-palette rule could be
      overcorrection that hides a legitimately useful proxy layer from
      users who do read labels.

  - need: Every ranked or scored resident-facing number (ward rank, safety
      index) needs an adjacent, same-screen explanation of *why* the number
      looks the way it does (historical disinvestment, reporting bias) —
      not just a caveat available a click away.
    inference_basis: >
      He raised the identical concern twice, independently, for two
      different features — the findings-page ward-concentration card ("Same
      number, opposite conclusion, and the card doesn't pick a side... I'd
      want it paired — same page, not a click away") and the ward table's
      ranking ("does the table itself explain why some wards rank low, or
      does a resident just see a number... a rank without a reason is a
      headline waiting to happen"). Two independent occurrences of the same
      structural worry, tied directly to his documented lived pattern of
      data "existing for years without producing investment," is a stronger
      basis than a single offhand remark.
    risk_if_wrong: Baking causal narrative into every ranked stat risks
      editorializing what's meant to be a neutral evidence layer, and other
      audiences (e.g., an analyst persona) may want the unadorned number
      without narrative attached — this need may conflict with a different
      audience's need for restraint.

  - need: A plain-language read-first line on the safety index clarifying it
      is a *relative* comparison, not a pass/fail grade — because "0-100"
      formatting reads as a school grade by default.
    inference_basis: >
      Unprompted, on hearing "0-100 score," he asked "relative to what,
      though" and volunteered his own misreading: "if my first instinct
      reading '62 out of 100' is 'we're failing a test,' and that's wrong,
      then the page needs to say that up front." Per shared-rules #7, this
      is exactly the kind of honest misreading the protocol asks the
      persona to surface, and it's self-diagnosed rather than led by the
      interviewer (the researcher had already explained "explicitly
      relative, not absolute risk" before he raised this).
    risk_if_wrong: This may be a generic numeracy/UX issue affecting all
      audiences equally rather than something specific to this persona's
      world — if so it's still valid but not distinctively "his" need; low
      risk either way since the fix (a plain clarifying line) is cheap and
      broadly beneficial.

  - need: The no-ridership-normalization caveat needs to be worded
      defensively, not just disclosed — specifically to foreclose a
      "maybe fewer people bike there so it's not really worse" reading that
      could be used to minimize West Side crash concentration.
    inference_basis: >
      He connected the caveat directly to a documented real-world argument
      he says he's heard used against his community: "I've heard that exact
      argument in a real room — 'of course Austin's crash count seems
      concentrated, nobody rides out there' — used to wave off a real
      problem... The caveat has to protect against being used that way, not
      just disclose the gap." This ties a general stated reaction (the
      caveat "bothers me less than you'd think") to a specific documented
      pattern in his world (data used to justify disinvestment, per his
      persona file's "instinctive frustrations"), which is what licenses
      treating it as latent rather than just his stated opinion.
    risk_if_wrong: If no real-world actor actually makes this exact
      "low-ridership" counter-argument in practice, defensive wording could
      be solving a problem that doesn't occur, at the cost of a slightly
      more editorial caveat than a purely neutral site might prefer.

reactions_to_existing:
  - feature: Home page + agent-layer (AI assistant) section
    verdict: ignores
    why: He explicitly carves it out as "not me and not the room I stand in
      front of" — he's fine with it existing as long as it isn't the only
      front door and doesn't change what the human page says. This tracks
      his documented pattern of never sending a neighbor to a data portal in
      the first place; an AI intermediary is simply outside his workflow,
      not a rejection of the underlying data.

  - feature: Transportation map — camera-violation layer
    verdict: distrusts
    why: Directly triggered by the evidence base's documented camera-equity
      disparities (ProPublica, UIC ticketing-rate findings). He accepts the
      "proxy" label intellectually but distrusts the visual presentation —
      color-coding reads as danger regardless of the badge, and he predicts
      real misuse by others ("objective tools... enforcement in exactly the
      neighborhoods that already have too much of it").

  - feature: Network/schematic route map (no safety data)
    verdict: ignores
    why: Correctly identifies it as out of his job — route planning for
      riders, not evidence for a safety meeting. Low-confidence engagement
      by design, not a flaw in the feature.

  - feature: Findings cards — ward-concentration stat
    verdict: would-use (conditionally)
    why: Matches a number he already carries into meetings from a magazine
      citation; he'd use it, but only paired with his own spoken causal
      framing, because he distrusts the bare stat's potential for
      stigmatizing misuse by others.

  - feature: PeopleForBikes BNA citywide network score
    verdict: ignores
    why: Genuinely unfamiliar with the organization and the scope (citywide
      network grade) doesn't match his neighborhood-level frame. This is the
      shallowest reaction in the interview and should be read as low-
      confidence/out-of-world rather than a considered critique.

  - feature: Ward table — rankings + CSV, percent protected/bikeways
    verdict: would-use
    why: Matches an existing manual workaround directly; caveat is the same
      stigma/no-context concern as the findings card, raised independently a
      second time.

  - feature: Ward one-pager — alderman contact/sponsorship + menu-money
      proxy + ward-matched news
    verdict: would-use (alderman/sponsorship, news) / distrusts (menu-money
      figure until independently verified)
    why: The alderman-contact and news portions replace hours of manual
      work he currently does by hand. The menu-money figure is flagged
      proxy/unverified in the inventory, and he treats that flag as
      binding on his own behavior (won't repeat the dollar figure without
      calling the Ward Office first) — a direct, correct read of the
      tier badge.

  - feature: Sources / Methodology pages
    verdict: would-use
    why: Positions them as prep material for himself the night before a
      meeting, not resident-facing — consistent with his role as translator
      who checks his own back before standing in front of a room.

  - feature: Action page (311, Bike Lane Uprising, alderman contacts,
      hearings, news)
    verdict: would-use
    why: Singles out the hearings/public-comment info specifically as the
      most forwardable, concrete "what do I do" content — matches his
      documented preference for action over more charts.

  - feature: Obstructions preview page (mock, gated, excluded from API)
    verdict: distrusts (with an explicit deal-breaker attached)
    why: Strong, immediate reaction to "fake" — ties directly to his
      documented pattern that a single caught fabrication poisons trust in
      every other (real) layer on the same site. Approves of current
      gating/exclusion from the API as the only acceptable state; treats
      any future leak of synthetic data onto the real maps as
      non-negotiable grounds to stop recommending the site.

  - feature: No-ridership-normalization caveat
    verdict: uses (accepts the limitation, but wants it reworded)
    why: Raw counts already match how residents feel harm ("did somebody
      get hit near my kid's route"), so the absence of per-rider
      normalization doesn't bother him on its own terms — but he flags the
      caveat's wording as a latent risk (see latent_needs) because of how
      it could be weaponized by others.

data_they_bring: >
  A hand-built spreadsheet cross-referencing the city's open crash portal
  against community-area boundaries (ward/police-district data doesn't map
  cleanly to how residents name their neighborhoods); phone calls to the
  Ward Office and manual Legistar lookups to confirm sponsorship/voting
  records before repeating them; a magazine citation (used in lieu of a
  dedicated study) for West Side crash-severity concentration; his own
  running mental ledger of CDOT's task-force before/after numbers
  (Belmont Cragin mileage tripling, ~39% KSI drop) that he treats as the
  single most persuasive artifact available to him, sourced from his direct
  participation rather than any published dashboard.

deal_breakers: >
  (1) Any single verified-wrong number he has already repeated to a room —
  he describes this as the one thing on the list, full stop, because his
  credibility with residents is personal and finite, not the tool's. (2) The
  synthetic obstruction layer migrating onto a real map or appearing anywhere
  a neighbor could mistake it for real data — he frames this as an
  immediate, permanent end to his recommending the site, independent of how
  much other real data exists elsewhere on it. (3) A ranked/scored stat
  (ward rank, safety index) being read aloud in a hostile room as evidence a
  neighborhood is "just dangerous" with no rebuttal readily at hand on the
  same page — not framed as an instant walk-away like (1)/(2), but as
  reputational damage he'd have to personally absorb and would resent the
  tool for causing.

vocabulary: >
  "the community," "folks," "over east/downtown," "the room," "who's at the
  table," "receipts," "task force," "church basement," "menu money,"
  community-area names (Austin, Garfield Park, North Lawndale) used ahead of
  ward numbers, "they" for the city, "ammunition" vs. "stigma" as the two
  possible fates of the same statistic, "danger index" used skeptically/
  quoted back at the interviewer rather than adopted natively.

confidence_notes: >
  Strongest and most in-world where the evidence base is richest: camera-
  equity distrust, 311 under-reporting, stigma-vs-ammunition framing of
  ranked data, the task-force counter-example, and the reaction to the mock
  obstruction layer all track directly to cited sources in
  chi-community-organizer.md and everyday-civic.md and produced concrete,
  resistive, story-grounded answers as the protocol requires. Weakest on the
  home page's agent-API/AI-assistant section and the PeopleForBikes BNA
  score — the evidence base gives this persona no documented opinion on
  either AI-assistant consumption of civic data or network-quality scoring
  orgs, so the honest response was disinterest/unfamiliarity rather than a
  substantive reaction; that thinness is itself accurately represented
  (per shared-rules #2) rather than papered over, but it means those two
  areas got shallower probing than the church-basement/311/camera themes the
  quality gate required. The methodology-page reaction is plausible but
  under-specified — a real organizer's actual reading comprehension of a
  percentile-blend methodology write-up under meeting-prep time pressure is
  a real-world usability question this simulation cannot answer and should
  be validated with an actual participant.
```
