# Interview: uk-ward-campaigner

**Run date:** 2026-07-21
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** (re-run — see new
areas since the last pass: home/orientation page, ward one-pager,
methodology page, the static agent API `/api/v1` + `llms.txt`, news-coverage
layer, proposed-projects roster, PeopleForBikes BNA score, and the
bike-lane-obstruction layer's move to a gated `obstructions-preview.html`).

## Round 1 transcript

**Interviewer:** Thanks for coming back. Same as before — describe your role,
and walk me through the last decision you tried to influence about street
safety, step by step.

**Priya Shah:** Still Thameside Cyclists, still twelve volunteers, still me
doing the numbers because I'm the one with a day job in data. The live one
right now is a Liveable Neighbourhood consultation — new branding, same fight
as the old LTN rows — covering a chunk of ward that includes a secondary
school on Ilderton Road. I've got until the end of August to get a submission
in before the committee looks at it in September.

Step one was pulling the last three years of STATS19 pedal-cycle casualties
for the roads inside the proposed boundary, via CycleStreets, because the
scheme's opponents' opening line is always "prove it's dangerous, not just
annoying." Step two, cross-referencing against TfL's Strategic Cycling
Analysis again, same as always, because I need the "this is also a network
corridor" framing to get Transport committee members interested, not just
Education. Step three — and this is new for this round — I actually tried to
get ahead of the boundary-displacement objection *before* anyone raised it,
because that's the lesson from the LTN fight I told you about last time. I
built the before/after table pre-emptively this time instead of waiting to
be asked for it. Took most of a Sunday.

Who am I convincing? Same shape as always — not the councillor, she's already
sympathetic, it's the highways officer who has to sign off feasibility.
Different officer this time, a man called Desmond Okafor, newer to the role,
which actually made this one harder — I don't yet know what he distrusts by
instinct the way I knew with Priti.

**Interviewer:** What information do you touch in a normal week for this
kind of work?

**Priya Shah:** Cyclescape for what other borough groups are logging, TfL's
counter dashboard, STATS19 via CycleStreets when a casualty question comes
up, the Scorecard when it's scoring season — which it isn't right now,
that's annual — and, I'll be honest, a WhatsApp group with three other
borough coordinators where we just ask each other "has anyone actually
verified this stat" before using it. That last one isn't a dataset, but it's
genuinely part of my week. It's my informal version of what I'd want a
credibility badge to do automatically.

**Interviewer:** Tell me about a recent time you needed a number or chart and
what you did with it.

**Priya Shah:** The Ilderton Road before/after table, again, but let me give
you a different one so I'm not just repeating myself — a councillor asked me
in May, off the cuff, "how does our ward compare to the one next door on
cycling infrastructure, not just danger." I didn't have a clean answer. The
Scorecard gives me a composite 0–10 but that's about the *borough*, not the
adjacent ward within it, and boroughs contain several wards with wildly
different infrastructure. I ended up hand-counting protected-lane kilometres
off a council PDF map for both wards, on a Saturday, with a ruler basically,
because there's no ward-level infrastructure-mileage number anywhere in our
system. Two hours, and I still don't fully trust my own count.

**Interviewer:** What have you built yourself because nothing gave it to you
directly?

**Priya Shah:** The spreadsheet's still going — two and a half years now,
one row per ward, and I've added a column since we last spoke: "corridor
demand source," because I got tired of re-deriving which SCA corridor a
given ask sits on every single time. And a new one this year, sadly: a
column literally called "is this number still true," because council data
gets quietly revised and I've been caught citing something that changed
underneath me without an announcement.

**Interviewer:** Tell me about a time data, or the lack of it, sank an
argument.

**Priya Shah:** Nothing as dramatic as the LTN meeting this round, thankfully,
but a smaller version — I cited a "recent" cycling-growth figure from a TfL
counter near the school in a written submission, and a committee clerk
pointed out, politely but pointedly, that the underlying count was from
before a major diversion went in eighteen months prior, so it wasn't
measuring what I claimed. Small, embarrassing, entirely avoidable if the data
had carried a date more loudly. I now check "when was this actually
measured" before "what does this say" every single time.

**Interviewer:** What data do you distrust, and why?

**Priya Shah:** Same answer as last time, if I'm honest — anything modelled
rather than counted, until I've seen the assumptions, because of the Waltham
Forest air-quality business. And now, additionally: anything that claims
currency without a visible date stamp, because of the counter incident I just
described. A number with no date on it is worse to me than a number that
admits it's six months stale, because at least the second one I can adjust
for.

**Interviewer:** Let's walk the stimulus. Same city, same dashboard, but it's
grown since we last looked — On Your Left, Chicago, read-only, ward →
corridor → intersection. First thing that's new: there's now a home page
before you even reach a map — orientation, headline stats, who it's for, and
apparently a section explaining how to ask an AI assistant questions against
it directly.

**Priya Shah:** Genuinely didn't expect that last part. My first reaction is
mild suspicion, not excitement — "ask an AI assistant" sounds like it's
solving a problem I don't have. I don't ask a chatbot for a casualty count, I
pull the row myself, because if I'm going to stand in front of Desmond Okafor
I need to know exactly where the number came from, and "the AI told me" is
not a sentence I can survive saying out loud in that room. So on first pass,
that section isn't for me — it reads like it's for someone earlier in the
funnel than I am, a resident maybe, not a campaign coordinator. The
orientation part above it, though, "who it's for" — that I'd actually use,
because I still don't fully know what's under the hood of this tool even
after our first conversation, and a two-minute "here's what this is and
isn't" page would have saved me some of the confusion I had last time with
the schematic map.

**Interviewer:** Tell me more about the suspicion — is it the AI framing
specifically, or something about trust?

**Priya Shah:** It's that an AI assistant summarizing data for me adds a
layer between me and the source I can't independently re-derive in a
meeting. If Desmond asks "where does that 12% come from" I need to be able
to say "the ward table, dated this week, methodology page section 4" — I
can't say "I asked an AI and it told me." It's not that I think the
underlying data's worse for being served that way, it's that *I* become a
worse witness for it. Unless — actually, hold on, is the AI just reading the
same published files I could read myself? If it's genuinely just fetching
the same JSON I'd otherwise download, then it's a convenience layer, not a
different data source, and that's less alarming. But you'd need to tell me
that loudly, because my gut reaction was "black box," not "same data, faster
lookup."

**Interviewer:** That's right — it's a static API generated from the same
committed files as the human site, versioned, nothing hidden behind it. Let's
come back to that. Next: the two maps. Geographic — crash density, bikeway
grade, wards, cameras, main routes. Schematic — twenty-one named routes,
tube-map style, three tiers, opt-in quality border, comfort-floor filter.

**Priya Shah:** The geographic one's still my QGIS evening done for me, same
as before, and I still want the clean unbranded export. The schematic one —
I remembered this time that there's no safety data on it, so I didn't make
the same mistake of expecting a "tube map with danger coded on," which I'll
admit is progress on my part, not the tool's. What's new to me is the
comfort-floor filter — "Any / Paint-plus / Protected-only" — and I actually
like that quite a bit, more than I expected to. It's the closest thing here
to how TfL talks about "Level of Service" bands for routes, and a resident
deciding whether their kid can ride somewhere thinks in exactly those terms:
"is this a real protected lane or is it paint in a bus lane." I'd screenshot
that filtered view for a "why this specific corridor, not the one three
streets over" argument, actually, which is closer to my SCA problem than I
expected the schematic map to ever get me.

**Interviewer:** Findings page — curated cards including two new ones: the
PeopleForBikes BNA citywide network score, and the general finding-card
model with caveats built in.

**Priya Shah:** Ah — I know of PeopleForBikes' BNA from cycling-advocacy
Twitter, it comes up when Americans compare cities to each other, but I've
never had to use one myself, we don't have a UK equivalent, we've got the
Healthy Streets Scorecard instead, which scores boroughs against ten
weighted indicators, not a single network-connectivity number. So my first
read of "0 to 100 network score" was, again, to reach for the Scorecard
mental model — I assumed it was a danger-adjacent composite the way our
Scorecard blends inputs and outcomes. Then you said "network quality, not
crash data" and "not a reason not to ride," and that second phrase actually
did the job for me immediately — it's basically PeopleForBikes pre-writing
the caveat I'd otherwise have to write myself, the way I asked for on the
KSI card last time. I'd use this one exactly as a citywide comparator, "how
does Chicago's network stack up nationally," which isn't my ward fight
directly, but it's the kind of number a councillor likes dropped into a
speech about ambition. I would not use it as evidence about any specific
street, and the caveat sentence is doing real work stopping me from doing
that by accident.

**Interviewer:** The ward one-pager — a single printable page per ward:
safety index, trends, infra stats, alderman contact and sponsorship record,
menu-money proxy, and recent ward-matched news, all in one document.

**Priya Shah:** Now *that's* the thing I've been asking you for since the
first conversation, without knowing it existed. This is my leaflet, more or
less, pre-assembled. Safety index, trends, alderman info, spend, and news all
on one printable page is exactly the object I hand-build every consultation
season, and you're telling me it's one file per ward, already made. My
immediate question, before I trust it for a second, is the same question I
had about the safety index last time — how much of this can I hand to a
resident versus a councillor's aide, because those two audiences need
different sentences around the same numbers. A resident reads "safety index
71" as "71% dangerous," full stop, same misreading I told you about before.
If the one-pager doesn't carry that caveat as loudly for a *resident* register
as it does for a *technical* one, I'd have to intercept it before handing it
out, which defeats the point of it being pre-made.

**Interviewer:** It says it's written in brief and plain-language registers
specifically for handing to an alderman or a neighbour.

**Priya Shah:** Good — that's the right instinct, but I'd want to actually
see both registers before I trust the plain-language one hasn't quietly
dropped the "relative, not absolute" caveat in the name of being readable,
because that's exactly the kind of thing that gets simplified away when
someone's optimizing for a neighbour's five-second attention span. Brevity
and honesty are in tension on that specific number, and I've been burned
enough times to want to check, not assume.

The menu-money line on it, though — same reaction as before, it's flagged
unverified against source PDFs, so it goes on my private read of the
one-pager, not the copy I actually hand across a table, until someone's
spot-checked it.

And the ward-matched news — that's new to me and I like it more than I
expected, actually. Half my job is knowing "did the local paper already write
about this street" before I walk into a meeting, because if a journalist's
already covered it, that's a different opening line than if I'm introducing
it cold. Right now I do that by manually searching one local outlet's site
per ward, which is tedious and I usually only do it for my own ward, not
neighbouring ones.

**Interviewer:** How exactly do you use that "has the paper covered it"
check — walk me through what changes if the news card is there versus you
searching manually?

**Priya Shah:** If I know a piece ran, I open my ask with "as [outlet] already
reported" — instantly more credible than "I'm telling you this is a problem,"
because now it's not just campaigner-says-so, it's independently
documented. Manually, I search maybe once per consultation, for my own
patch, and I miss things — a neighbouring ward's coverage that would've
strengthened a network-wide argument, say. If OYL's already matched news to
ward and alderman for me, I get the neighbouring-ward hits too, which I
currently just don't have the time to go looking for. My one worry, and I'd
ask this directly: how does it decide a story's "about" my ward — because a
mis-match, a story about a different street wrongly tagged to my alderman,
is exactly the kind of thing a hostile aide would delight in catching me
repeating.

**Interviewer:** It's allowlisted RSS feeds only, matched by an auditable
rule the site calls "via" — visible per match — and it favors precision over
recall, so unmatched stories still show up citywide rather than being force-
matched to a ward.

**Priya Shah:** That "via" visibility is the bit that actually matters to me
— if I can see *why* it thinks a story's about my ward before I repeat that
claim, that's the same discipline as wanting the sponsorship link to point at
a primary Legistar record instead of just asserting itself. I'd check the
"via" once per story before quoting it, same reflex as everything else.
Favouring precision over recall is the right call for my use case
specifically — I'd rather manually catch three missed stories than
accidentally cite one wrongly-matched one in front of Desmond.

**Interviewer:** Proposed and in-progress projects — a hand-curated roster of
active bikeway proposals with a volunteer-reviewed status, status date, note,
official links, and auto-joined news, but explicitly no geometry, because no
machine-readable planned-bikeway layer exists anywhere.

**Priya Shah:** This is trying to be my SCA-equivalent problem from last
time, isn't it — the "where's the demand/pipeline layer" gap I flagged. It's
not quite that, and I want to be precise about why. TfL's Strategic Cycling
Analysis tells me where a corridor *should* go based on modelled demand,
independent of whether anyone's proposed it yet — it's a justification tool.
This is a status tracker for asks that already exist, which is genuinely
useful for a different reason: "is someone already fighting for my street, so
I don't duplicate effort or, worse, contradict an ally's framing." That's a
real, separate job — coordination, not justification — and I don't currently
have a good way to check that for Chicago-shaped reasons, obviously, but even
translating it to my own patch, I don't have a clean citywide view of "which
of the twelve other borough groups are already working this stretch." So I'd
actually use this, just not for the job I originally asked for. No geometry
is a real limitation though — a card telling me a project exists on "Route X"
without a line on a map means I still can't tell at a glance whether it
overlaps the specific block I care about, I'd have to read the note text
carefully every time.

**Interviewer:** Methodology page — a full explanation of how every number on
the site is computed.

**Priya Shah:** This is the thing I asked for indirectly last time, when I
said I'd want the safety-index weighting one click away. My honest reaction
is relief, and also — I probably won't read all of it, cover to cover, most
weeks. But its existence changes what I'm willing to say out loud. If Desmond
asks "how's this calculated" and I can say "here's the page, section on the
safety index, here's the formula" instead of "I'm not sure, I just saw the
number," that's the difference between looking prepared and looking like I
copied a stat off a website. I'd read the specific section relevant to
whatever number I'm about to cite, each time, rather than the whole document
once. That's actually a more realistic habit for me than reading it
cover-to-cover and remembering it — I'd bookmark the anchor for the safety
index section specifically.

**Interviewer:** Now the two I most need your honest reaction to. First — as
before, the obstruction layer. It's moved: it's no longer anywhere on the
main maps at all, it's excluded from the API entirely, and it now lives on a
separate, gated, watermarked preview page, clearly labeled synthetic, pending
an actual data-sharing conversation with a real obstruction-reporting tool.

**Priya Shah:** Good — that's the right move, and I'll say plainly that it's
better than what you described last time, when it was mock but still sort of
present on the main experience. Quarantining it, watermarking it, keeping it
out of the API so nothing downstream can accidentally ingest it as if it were
real — that's exactly the discipline I said I respected in the badge system
before, just taken a step further. Would I ever open that preview page
myself? Honestly, maybe once, out of curiosity about what the real version
might eventually look like, the way I'd look at a mock-up in a proposal deck.
But I would not screenshot it, quote it, or let a volunteer near it, because
"gated and watermarked" still means someone determined enough can get a
screenshot out of it, and a watermark doesn't stop a screenshot from
circulating without the caption once it's out of my hands. If I were advising
you, I'd say: good instinct, and I still wouldn't trust myself around it with
a room full of volunteers I don't fully supervise.

**Interviewer:** And second — the no-ridership-normalization position. It's
unchanged: no cyclist-volume data joined anywhere, stated plainly, including
now on the BNA card you just reacted to.

**Priya Shah:** Also unchanged is my answer, really — it doesn't stop me
using raw counts, it just means every one of them is a "where to look," never
a "how bad, definitively," and I still do the same silent mental adjustment I
described before: is this ward dangerous, or does it just have a lot of
cyclists. What's slightly different this time is I've now seen the BNA
score sitting next to the raw crash counts on the same Findings page, and
that actually makes the gap more visible to me, not less — because the BNA
score is a network-quality measure that implicitly assumes more good
infrastructure correlates with more riders, which is a *volume-adjacent*
claim dressed up as an infrastructure claim. If a hostile resident is sharp,
they could point at a high-BNA, high-crash-count ward and say "see, more bike
lanes causes more crashes," and without ridership data, nothing on this
whole site can rebut that specific bad-faith reading cleanly. I still think a
bikeshare-trip proxy would get me most of the way, same answer as before —
it's not that I need TfL-grade counters, I need *something* that lets me say
"more riders, not just more danger" in one sentence.

## Follow-up round

**Interviewer:** You said the AI-assistant section might be for someone
earlier in the funnel than you. Who, specifically, and would you ever forward
it to them?

**Priya Shah:** Probably a resident who's never opened a dashboard in their
life and wants a plain answer to "is my street dangerous" without learning
to use a table or a map. If a neighbour asked me that on the doorstep, I
might genuinely say "go ask the site's assistant thing, it'll walk you
through it" — that's actually a real use, now that I say it out loud, I just
wouldn't do it myself for anything I'm about to stand behind in a meeting.
So: I'd forward it, but with a mental label attached — "good for a first
look, not a citable source," the same tier I'd put a friendly explainer
video in. I would not forward it to Desmond or to Councillor Fenwick. I'd
forward it to the parent at the school gate who just wants to know if
Ilderton Road is bad before deciding on a walking bus.

**Interviewer:** Would that change if you knew, concretely, that the
assistant only ever answers from the same versioned, published files a human
could also download — no separate model-generated claims?

**Priya Shah:** A bit, yes, and I appreciate you being precise about it just
now rather than me having to assume the best. If it's genuinely constrained
to citing the same published JSON, then technically I *could* use it and
then go verify the specific file it pointed me to before repeating the claim
— that's actually not so different from how I already treat a Findings card,
which is also a pre-summarized version of some underlying number. The
difference that still nags at me is that a Findings card is fixed and
reviewable in advance by me, once, and I know exactly what it says every
time I look at it — an assistant's phrasing of the same fact could vary
answer to answer, and a hostile aide who asked the same assistant a slightly
different question and got slightly different wording could make hay out of
the inconsistency, even if the underlying number never changed. So: same
data, lower risk than I first assumed, but not zero risk, and not something
I'd rely on for a fixed quote I need to say identically twice.

**Interviewer:** On the ward one-pager — if you had to pick only one of the
two registers, plain-language or technical, to actually trust putting in
front of a resident without checking it first yourself every time, which,
and what would make you stop checking?

**Priya Shah:** The plain-language one, obviously, that's the one meant for
the doorstep. What would make me stop checking it every time is if the
"relative, not absolute" caveat on the safety index survived translation
into that register in a form a resident would actually read — not "this
index is relative" as jargon, but something like "this compares your ward to
other wards, it's not a percentage chance of a crash." If I read that
sentence once, in that register, and it held up, I'd trust future one-pagers
from the same page template without re-checking each one, the same way I now
trust a Findings card's caveat is there without re-reading the whole card
every single time — I check the *pattern* once, then I extend trust to the
template, not to each new instance individually. That's actually how most of
my trust in this whole tool works, now that you make me say it: I don't
re-verify every ward's number personally, I verify the *rule* the tool
claims to follow once, hard, and then I trust the rule was applied
consistently — until something breaks that trust, at which point it resets
to zero the way I told you before.

**Interviewer:** On the proposed-projects roster — you said it solves a
coordination job, not a demand-justification job. What would it need for you
to actually use it that way, concretely, this consultation season?

**Priya Shah:** A status that tells me not just "active" but roughly *how*
active — is this a funded, scheduled scheme, or is it a wishlist line item
some councillor mentioned once at a ward forum three years ago. Right now
"volunteer-reviewed status plus a status date and a note" sounds like it
could cover that, if the note actually says which of those two worlds it's
in, but I'd want that distinction to be a structured field I can scan across
many projects at once, not prose I have to read project by project, because
I'm trying to scan a whole ward's pipeline quickly, not read one entry
closely. Concretely: before I submit for Ilderton Road in August, I'd want
to check whether anything on this roster already covers that stretch, so I
don't contradict an existing ask by proposing something incompatible — and
for that I'd need the note to name the actual street, reliably, not just the
route or ward, because "ward 14" is too coarse to tell me if it's my specific
block.

**Interviewer:** Last one — the news-matching "via" transparency. Would you
actually click through and check it every time, or only sometimes, and what
determines which?

**Priya Shah:** Only when I'm about to repeat the claim to someone who could
push back — Desmond, a committee document, anything with my name on it going
somewhere official. If I'm just scanning the one-pager privately to get a
feel for what's going on in a ward, I wouldn't click through every story, I'd
skim headlines the way I skim my own news feed. The line for me is always
the same one, actually, across everything we've talked about today: private
situational awareness, no check needed; anything I'm about to say out loud
where someone could contradict me, full check, every time, no exceptions.
That's not really a rule about news matching specifically, it's just the
rule, applied again.

## Analysis memo

participant: uk-ward-campaigner
confidence_notes: Priya stays in-world and consistent with the prior round —
her Space-for-Cycling/Scorecard reflexes, her "check source, date, can the
officer contradict me" rule, and her private-vs-public trust tiering recur
naturally rather than being re-explained from scratch, which is a good sign
the character is stable rather than improvised per-question. The one place
the simulation runs thinner this round is her reaction to the agent API/AI-
assistant framing: she reasons her way to a nuanced, plausible position
(useful for residents, not for herself, contingent on data-source
transparency), but a real UK data-analyst campaigner's first reaction to
"ask an AI" branding in 2026 might be blunter — more dismissive or more
alarmed about hallucination specifically — than the fairly measured, almost
too-quick arrival at "same data, lower risk" she shows here once told how it
works. Her read of the proposed-projects roster as solving "coordination, not
justification" is a sharp, well-grounded distinction but is close to the line
of her analyzing the product rather than just reacting to it; it's kept
in-bounds because it's expressed entirely through her own translated
experience (checking whether other borough groups are already working a
stretch), not as a design proposal.

stated_needs:
  - need: A ward-level infrastructure-mileage comparison (not just a borough/
    citywide composite), so she can answer "how does my ward compare to the
    one next door" without hand-counting kilometres off a PDF map.
    evidence_quote: "I ended up hand-counting protected-lane kilometres off a
    council PDF map for both wards, on a Saturday, with a ruler basically,
    because there's no ward-level infrastructure-mileage number anywhere in
    our system."
    underlying_job: Answer an off-the-cuff councillor question about relative
    ward standing within hours, not days, without inventing a manual count
    method each time.
  - need: Loud, visible measurement dates on any statistic claiming currency,
    not just a general "last updated" note on the site.
    evidence_quote: "I cited a 'recent' cycling-growth figure... a committee
    clerk pointed out... the underlying count was from before a major
    diversion went in eighteen months prior... I now check 'when was this
    actually measured' before 'what does this say' every single time."
    underlying_job: Avoid citing a technically-true but functionally stale
    number in an official submission where a clerk or officer can catch the
    mismatch and damage her credibility.
  - need: Explicit confirmation that an AI-assistant/agent layer answers only
    from the same versioned published files a human could independently
    download, not separately generated claims.
    evidence_quote: "is the AI just reading the same published files I could
    read myself? ... you'd need to tell me that loudly, because my gut
    reaction was 'black box,' not 'same data, faster lookup.'"
    underlying_job: Decide whether a new access channel is a citable-adjacent
    convenience (safe to point a resident toward) or an unverifiable new risk
    surface she must keep herself and her volunteers away from.
  - need: The plain-language ward one-pager must carry the "relative, not
    absolute" safety-index caveat in genuinely resident-legible language, not
    have it simplified away in the name of brevity.
    evidence_quote: "I'd want to actually see both registers before I trust
    the plain-language one hasn't quietly dropped the 'relative, not
    absolute' caveat in the name of being readable... Brevity and honesty are
    in tension on that specific number."
    underlying_job: Hand a pre-made artifact directly to a resident or
    neighbour without having to personally intercept and re-caveat it first,
    which is the entire point of it being pre-assembled.
  - need: A structured (not prose-only) field on the proposed-projects
    roster distinguishing funded/scheduled status from aspirational/wishlist
    status, and reliable street-level (not just route/ward-level) naming.
    evidence_quote: "I'd want that distinction to be a structured field I can
    scan across many projects at once, not prose I have to read project by
    project... 'ward 14' is too coarse to tell me if it's my specific block."
    underlying_job: Quickly check, before submitting her own ask, whether an
    existing proposal already covers or conflicts with her specific target
    street, without reading every entry's free text closely.

latent_needs:
  - need: A "verify the rule once, then trust the template" model of
    engagement — she doesn't want to re-verify every individual instance of a
    recurring artifact (ward one-pagers, Findings cards), she wants to
    verify the underlying rule/pattern once and then extend trust to all
    instances that claim to follow it.
    inference_basis: She stated this explicitly and generalized it herself
    unprompted in the follow-up: "I don't re-verify every ward's number
    personally, I verify the rule the tool claims to follow once... and then
    I trust the rule was applied consistently — until something breaks that
    trust." This reframes nearly every other reaction in the interview (the
    badge system, the "via" news transparency, the caveat language) as
    instances of one underlying operating principle rather than isolated
    preferences, which is a stronger and more economical inference than
    treating each as separate.
    risk_if_wrong: If OYL treats this as license to under-invest in per-
    instance quality (assuming "the rule was stated once, so any instance is
    fine"), a single visible violation of the rule (one bad ward one-pager,
    one wrongly-matched news story) could collapse trust in the entire
    template class at once, which is a much larger blast radius than if she
    genuinely checked each instance independently — the tool must actually
    earn template-level trust, not just claim it.
  - need: A distinction, surfaced somewhere on the site, between claims that
    are "private situational awareness" grade versus "citable to a hostile
    official" grade — essentially a confidence/citability tier orthogonal to
    the existing real/proxy/mock badge.
    inference_basis: She drew this line explicitly and repeatedly across
    unrelated features (the AI assistant, the news "via" links, generally):
    "private situational awareness, no check needed; anything I'm about to
    say out loud where someone could contradict me, full check, every time."
    This is a consistent behavioral filter she applies to everything shown to
    her, not a one-off answer to one question, and it doesn't map onto the
    existing real/proxy/mock/crowdsourced/derived badge, which grades data
    provenance, not situational stakes.
    risk_if_wrong: If this is idiosyncratic to her (a data-analyst-by-trade
    habit of mentally tiering evidence by stakes), most users may not
    separate "private glance" from "public citation" at all, making an
    explicit UI distinction between the two unnecessary complexity for
    everyone except the small subset of users, like her, who face a hostile
    technical gatekeeper as a matter of routine.
  - need: A visible mechanism (even just a documented sentence) addressing
    the specific bad-faith reframing risk that a high-BNA/high-crash-count
    ward could be read as "more bike lanes causes more crashes," given no
    ridership data exists to rebut it.
    inference_basis: She connected two previously separate reactions
    (the BNA score's citywide framing and the no-ridership-normalization
    caveat) unprompted, once she saw them on the same Findings page, and
    named a specific adversarial argument ("more bike lanes causes more
    crashes") that nothing on the site currently has an answer to. This is a
    new inference this round specifically because it required both stimuli
    (BNA card + raw crash counts) to be presented together, which only
    happened due to this run's new BNA feature — it did not exist as a
    latent need in the prior round.
    risk_if_wrong: This may be a low-probability adversarial argument that
    real hostile residents rarely actually make (most objections in her prior
    stories were about displacement and staleness, not this specific
    correlation-causation move); over-engineering a rebuttal to a rare attack
    vector could distract from more commonly-needed caveats.
  - need: A per-ward or per-corridor register of "who else is already
    working this" — a coordination signal distinct from a justification/
    demand-potential signal — that surfaces overlapping or adjacent
    volunteer/advocacy effort, not just official project status.
    inference_basis: She reinterpreted the proposed-projects roster's
    purpose for herself unprompted, distinguishing it sharply from her
    stated SCA-equivalent ask from the prior round ("It's not quite that...
    This is a status tracker for asks that already exist... that's a real,
    separate job — coordination, not justification"), and grounded it in a
    concrete translated need ("I don't have a clean citywide view of which
    of the twelve other borough groups are already working this stretch").
    risk_if_wrong: Chicago's civic-advocacy landscape may not have an
    equivalent density of overlapping local groups the way London's 30
    borough groups do, making a "who else is working this" layer solve a
    problem that doesn't really exist at Chicago's scale or organizational
    structure — this could be an artifact of importing a London-specific
    organizational reality onto a different city.

reactions_to_existing:
  - feature: Home/orientation page with AI-assistant explainer section
    verdict: would-use (for others) / ignores (for herself)
    why: Reads it as aimed at someone earlier in the funnel than her; would
    forward it to a resident or neighbour as a "good first look, not
    citable" resource, but would not use it herself for anything she has to
    defend to a skeptical official, and her suspicion softened only
    partially once told the assistant is constrained to the same published
    files.
  - feature: Schematic route map's comfort-floor filter (Any/Paint+/
    Protected-only)
    verdict: would-use
    why: Unprompted positive reaction, maps directly onto how she already
    thinks about route quality tiers (TfL "Level of Service"-style bands) and
    gives her a screenshot-able artifact for justifying a specific corridor
    over an adjacent one, closer to her SCA-equivalent need than she expected
    the schematic map to get her.
  - feature: PeopleForBikes BNA citywide score
    verdict: would-use (citywide comparator only) / distrusts (as
    street-level evidence)
    why: Initially misread through her Scorecard mental model as a
    danger-adjacent composite; the "network quality, not crash data" and
    "not a reason not to ride" caveats corrected this quickly and she
    praised the caveat as pre-doing work she'd otherwise do herself, but she
    flags it creates a new adversarial reading risk when placed next to raw
    crash counts absent ridership data.
  - feature: Ward one-pager (safety index, trends, alderman info, menu-money,
    ward-matched news, one printable page)
    verdict: would-use, conditionally
    why: Immediately recognized as the pre-built version of the leaflet she
    hand-assembles every consultation season; contingent on verifying the
    plain-language register actually preserves the safety-index caveat, and
    still treats the menu-money line as private-use-only per her established
    unverified-data rule.
  - feature: Ward-matched news coverage with auditable "via" match reasoning
    verdict: would-use, conditionally
    why: Directly replaces a manual per-ward local-news search she currently
    only has time to do for her own ward, extending coverage to neighbouring
    wards for free; she would check the "via" link before any public-facing
    citation but not for private situational scanning — an instance of her
    broader private-vs-citable tiering rule.
  - feature: Proposed & in-progress projects roster (no geometry)
    verdict: would-use, for a different job than justification
    why: Reinterpreted its purpose as solving cross-group coordination
    ("who else is already working this stretch") rather than her originally-
    stated demand-justification gap; the lack of geometry and prose-only
    status description limits how quickly she could scan it against her own
    target street.
  - feature: Methodology page
    verdict: would-use (as a reference, not read cover-to-cover)
    why: Its existence changes what she's willing to assert in an official
    setting ("here's the page, here's the formula" vs. "I'm not sure"); she
    expects to bookmark and cite specific sections at point of use rather
    than read it in full.
  - feature: Bike-lane obstruction layer, now gated/watermarked on a separate
    preview page, excluded from maps and API
    verdict: distrusts / would-never-cite, but approves of the containment
    why: Explicitly judges this an improvement over the prior mock layer's
    placement, praising the quarantine as consistent with the badge-system
    discipline she praised before; still would not let a volunteer near it
    or screenshot it, noting a watermark doesn't stop a screenshot from
    circulating without its caption once it leaves the page.
  - feature: No-ridership-normalization stance (unchanged, now cross-referenced
    against the BNA score)
    verdict: distrusts raw counts as standalone evidence, uses them as a
    "where to look" signal
    why: Same position as the prior round, but newly sharpened: seeing the
    BNA score and raw crash counts on the same page surfaced a specific
    adversarial reading (more infrastructure "causing" more crashes) that a
    bikeshare-trip-level exposure proxy would let her pre-empt.

data_they_bring: TfL's Strategic Cycling Analysis (demand/route-potential
layer, independent of crash data, her benchmark for "why this street"); the
Healthy Streets Scorecard (multi-stakeholder-weighted composite she treats as
more citable than any single-author index, and the mental model she
mistakenly reaches for on both the safety index and the BNA score); STATS19
via CycleStreets (granular, dated, independently verifiable crash records);
TfL's cycle-counter network (an imperfect but real exposure source, "more
riders, not just more danger"); a two-and-a-half-year hand-built ward
spreadsheet, now with an added "is this number still true" staleness column;
an informal cross-borough WhatsApp verification habit ("has anyone actually
checked this stat") that functions as an ad hoc trust layer OYL's badge
system partially automates; and her own manual, ruler-on-a-PDF-map method for
ward-level infrastructure comparison, which a ward-level mileage stat would
retire outright.

deal_breakers: (1) Any statistic presented as current without a visible
measurement date, given she was already burned this round by a stale counter
figure a clerk caught in a submission. (2) A plain-language artifact (like
the ward one-pager) that quietly drops a load-bearing caveat (the safety
index's "relative, not absolute" framing) in the name of readability — this
would force her to intercept and re-caveat every pre-made artifact herself,
destroying the labor-saving point of it existing. (3) Any single instance
where a "rule" the site claims to follow (a badge, a caveat, a "via" match)
turns out not to hold for one specific instance — per her newly explicit
verify-the-rule-once-then-trust-the-template model, one broken instance
doesn't just cost her that one number, it collapses her trust in the entire
class of artifact.

vocabulary: "the ask" / "corridor" / "displacement" / "boundary-road numbers"
/ "mean vs. distribution" / "relative, not absolute" / "primary source" /
"exposure" (all carried over, unchanged, from the prior round); new this
round — "Level of Service"-style bands (her frame for the comfort-floor
filter); "is this number still true" (her new staleness-tracking column,
now her explicit test for any claimed-current stat); "private situational
awareness vs. citable" (her explicit two-tier stakes framework, applied
across the AI assistant, news matching, and one-pagers alike); "verify the
rule once, trust the template" (her explicit description of how she extends
or withholds trust across repeated artifacts); "coordination, not
justification" (her distinction between the proposed-projects roster's real
use and the SCA-equivalent gap she originally asked about).
