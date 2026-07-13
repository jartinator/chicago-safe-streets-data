# Validation Interview: chi-ward-office — PFB BNA proposal

*Persona: Marcus Webb, chief of staff, Chicago ward office (see
`personas/chi-ward-office.md`, `personas/_shared-rules.md`). Validating
`docs/projects/pfb-bna-proposal.md` per
`validation/pfb-bna/00-protocol.md`. This is a follow-up session with the
same composite persona interviewed in the original study
(`interviews/chi-ward-office.md`); continuity of voice and prior
workarounds is intentional.*

## 1. Context re-anchor

**Interviewer:** Good to talk to you again. Different question this time —
not crashes. Walk me through the last time you needed to characterize how
*good* the bike network is in your ward — not how many people got hit, just
whether it's actually decent to ride on.

**chi-ward-office:** That's actually a harder question than the crash one,
which is funny because you'd think I'd have better data for the easier-sounding
one. This was maybe six weeks ago — CDOT put out a call for the next round of
Neighborhood Greenways nominations, and my alderwoman wanted to know which two
or three streets in the ward we should put forward. Not "where are people
getting hurt," but "which streets are actually low-stress enough that a
greenway makes sense there versus a street that's already lost." I pulled up
our CDOT bikeway layer — fine, it tells me painted versus protected versus
nothing — but it doesn't tell me if a "painted" lane on a four-lane arterial
with a 35-mile-an-hour speed limit is actually rideable, versus a painted lane
on a quiet residential block. Those are both "painted" in the data and they
are not the same street. I ended up doing what I always end up doing, which is
calling Andrea and just asking her, informally, "which of these streets would
you let your kid ride on." She gave me four off the top of her head. That's my
quality data right now — one CDOT project manager's gut, relayed over the
phone, and I wrote it down in an email so I wouldn't lose it. I don't have
anything that tells me quality independent of a phone call.

**Interviewer:** Anything else you've tried, or is the phone call the whole
method?

**chi-ward-office:** I've eyeballed the map — literally zoomed in and looked
at whether a lane has posts or paint or nothing, which tells you facility
type, not comfort. I know facility type isn't the same thing as "would I ride
here," I just don't have a better number. If a resident asks me "is that new
lane on Damen actually safe or did they just paint a line," I don't have a
citable answer for that beyond my own opinion or Andrea's.

## 2. Product recap

**Interviewer:** Quick recap since it's been a while. On Your Left — same
site — is a read-only Chicago bike-safety dashboard: crash map, the bikeway
network graded by facility type, a ward table, findings cards, sources page
with tier badges (real / proxy / mock / crowdsourced / derived), and it
doesn't take reports itself, it points people to 311 and Bike Lane Uprising.
Since you last saw it, they've added a schematic route map and coverage
percentages — percent of on-street bikeway miles that are protected, percent
of surface streets with any bike infrastructure at all. Still no ridership
data, still labels everything by tier. That the same site you remember?

**chi-ward-office:** Yeah, that's the one — the ward table's the piece I said
I'd actually export. Good, so we're building on top of what I already looked
at, not starting over.

## 3. Stimulus walkthrough

**Interviewer:** They're proposing to bring in a new outside source —
PeopleForBikes, a national bike advocacy group. Four pieces. First, B1: a
citywide scorecard — one number, updated yearly, for how good Chicago's whole
bike network is, plus how many miles of street are "high-stress" versus
"low-stress" to ride on. Gut reaction?

**chi-ward-office:** My first thought, honestly, is "who commissioned this" —
is this a group with an agenda, or is it more like the ATA letter, a group
that's just publishing numbers. Assuming it's the second kind: a citywide
number, one number for the whole city, that doesn't immediately worry me the
way a ward number would, because it's not pointed at my alderwoman
specifically — it's pointed at the whole council, the mayor, everybody. If
anything my first instinct is that's useful *ammunition*, not a threat.

**Interviewer:** More detail — it's the PeopleForBikes Bicycle Network
Analysis. Chicago scored 11 out of 100 for 2026, up from 9 in 2024. National
average for rated cities is 36. 6,267 miles of high-stress street, 1,834
low-stress.

**chi-ward-office:** Okay, now I've got a use for this. When my alderwoman's
deciding how much menu money goes to bike infrastructure versus just
repaving — which is the fight every single cycle — "the whole city is an 11
out of 100 against a national average of 36" is a sentence I can put in the
budget one-pager that says "this isn't optional, this isn't just our ward
being behind, the entire city is behind." That's actually a better argument
for her than a ward-specific crash number, because nobody can say "well
that's just your ward's problem." The trend line helps too — nine to eleven,
I can say "and it's moving the right direction," which is the sentence she
needs when someone asks "why bother." What I'd check before I used it: who
is PeopleForBikes, are they going to show up in the room and get asked about
by name, and is the methodology going to survive one skeptical question from
a merchant who says "who says so." If it's a credentialed group with a
published method, like ATA, fine. If it's some outfit nobody's heard of, I'm
not citing it cold.

**Interviewer:** B2 — same source, but broken down by ward. For each ward,
what share of residents live somewhere with easy, low-stress bike access to
things like groceries.

**chi-ward-office:** Okay, my guard's up immediately, before you even
finish — "broken down by ward" is the phrase that makes my stomach drop, I've
told you why. Two years ago it was Ward Wise ranking us on spending and it
cost me an afternoon. So my honest gut reaction is: this is a danger score
with a nicer name on it.

**Interviewer:** They're deliberately not framing it as danger — the language
is access. Something like: "In Ward 35, 40% of residents live on blocks with
low-stress bike access to a grocery store." Not a 0–100 ranking of the ward
against other wards. React to that specifically.

**chi-ward-office:** That's smarter language, I'll give them that — "access"
gives me something to say back that isn't defensive. "Low-stress access to
groceries" sounds like an investment ask, not a report card. If my
alderwoman's making the case for spending, "only 40% of our residents can get
to the grocery store safely by bike" is a sentence that argues *for* her
doing something, which is a completely different room than "your ward scored
worst." I could actually use that in the same budget one-pager as the citywide
number — makes the case locally instead of just citywide.

But — and I want to push on this, because you asked me to be honest about
it — a percentage per ward is still a number per ward, and the second it sits
in a sortable table next to forty-nine other wards, somebody is going to sort
it. I don't care what you call it on the label. If Streetsblog pulls this
number and writes "Ward 35 residents twice as likely to lack safe grocery
access as Ward 43," that headline reads exactly like a danger ranking to my
alderwoman, and the word "access" in your database schema doesn't change how
it reads in the paper. So: does it help, some — it gives me better words to
say out loud than a bare score would. Does it fully get me out of the "who
else will see this" question? No. I'd want to know exactly where this number
can be sorted, and by who, before I'd relax about it.

**Interviewer:** For what it's worth, the current proposal lists a possible
ward-table column as one of the surfaces — sortable, like the existing
table.

**chi-ward-office:** Then it's a ranking. I'm sorry, but it is. You can call
the column "access score" all day, if it's a column in the same sortable
table I already told you I export and hand to my alderwoman, somebody is
going to click the header and sort it low to high, and the ward at the bottom
is the ward that gets the headline, access framing or not. I'd want that
number somewhere I have to go looking for it deliberately — a ward page, a
sentence, not a column next to forty-nine others begging to be sorted. Put it
in a table and the framing's just a caption nobody reads.

**Interviewer:** B3 — this one attaches a stress rating to every street
segment in the city, not just bikeways — speed limit, lane count,
intersections, all folded into one grade.

**chi-ward-office:** "Stress rating" — my first read on that, honestly, is
traffic stress, like congestion, like how bad the driving is on that block.
Is that what this is, or is it about how stressful it is to bike there?

**Interviewer:** Bike comfort specifically — how stressful it would feel to
ride a bike on that segment, given speed and traffic, regardless of whether
there's a bike lane at all.

**chi-ward-office:** Got it, okay, that's actually the exact thing I was
missing on the Greenways call six weeks ago — that's the number that would
have replaced my phone call to Andrea. If I could pull up a street and see
"this one's low-stress even with no painted lane, this one's high-stress even
with paint," that's a real upgrade over facility type alone. That's the one
I'd genuinely use for the next greenway nomination round, no hesitation.

**Interviewer:** There's a wrinkle — the proposal wants to cross-check it
against OYL's own facility grades. Where CDOT calls something "protected" but
this source still rates the corridor high-stress, it'd get flagged.

**chi-ward-office:** Now you've got me nervous instead of interested. Because
here's the scenario that actually keeps me up: we defended a "protected"
bike lane at a community meeting, my one-pager says protected, CDOT calls it
protected, and then some outside methodology says no, actually, that
intersection's still high-stress because of the turn lane or the speed limit
or whatever. If a resident finds that flag before I do, I look like I either
didn't know or didn't say. That's exactly the "burned" scenario from last
time, just with a new source instead of Ward Wise. So — I want this flag to
exist, because I'd rather know before the room does. But I want it pushed to
me, not something I have to go discover. If CDOT's calling something
protected on paper and an outside group disagrees, I need that in my scar
sheet before the next meeting on that corridor, not after.

**Interviewer:** B4 — last one. Same source covers about three thousand
cities. A comparison strip: Chicago's score next to a handful of peer
cities — New York, LA, Philly, Minneapolis, Seattle.

**chi-ward-office:** Honestly, my first reaction is that sounds like
something the mayor's press office would put out, not something that lands
on my desk — "how do we stack up against other big cities" is a talking-point
question, not a ward question. Nobody in the field house basement is asking
me how Chicago compares to Minneapolis, they're asking me about the corner by
the Jewel. Is this for me, or is this for the fifth floor?

**Interviewer:** It's a findings-page comparison, mostly citywide framing —
not ward-specific.

**chi-ward-office:** Then yeah, that confirms it, that's not my tool. I could
see it being useful exactly once — if my alderwoman gets asked "why is
Chicago behind Minneapolis" at some citywide forum and I need one sentence of
context for her — but that's rare, and when it happens I'd rather just look
it up that day than have it sitting on a page I check regularly. It's not
something I'd build a habit around. Not hostile to it, I just don't have a
recurring use for it the way I do the ward table or, now, that stress-flag
thing.

## 4. Trust probes

**Interviewer:** It's computed from OpenStreetMap by a national advocacy
group, updated once a year, only as current as volunteer mapping. Does that
change anything for you?

**chi-ward-office:** It changes how I'd caveat it, not whether I'd use it.
"Volunteer-mapped" makes me think of the same problem I already have with
install dates on the CDOT layer — if it's stale or incomplete, it's stale in
a specific, dangerous direction: it could make my ward look worse than it
actually is because our infrastructure isn't well mapped, not because it
doesn't exist. That's a new argument I'd have to be ready to make in a room —
"the score's low because the map's incomplete, not because the street's
unsafe" — and that argument only works if I can actually check it, meaning I
need to know when it was last updated and, ideally, be able to say "yes, our
lane on Damen is in there" before I cite the number. If I can't verify our
own ward's mapping is current, I don't use the number cold.

**Interviewer:** Chicago scores 11 out of 100. Does that help you or hurt
you?

**chi-ward-office:** Genuinely both, and it depends who's asking. It helps me
with my alderwoman internally, for the budget case — "the whole city is
behind, this isn't us uniquely failing." It could hurt if a challenger turns
it into "eleven years on the council and we're still an eleven out of a
hundred," making it about tenure instead of about the ward. But that's a
citywide number pointed at the mayor and the whole council first — it's not
pointed at her specifically the way a ward ranking would be, so the damage,
if it happens, is spread out, not concentrated on her. I'd rather defend an
11/100 citywide than a 47th-of-50 ward number, every time. Scale of the
target matters to me as much as the number itself.

**Interviewer:** And to be direct about it — the ward number is framed as
access, not danger. You already reacted to that in the walkthrough. Anything
to add now that you've sat with all four pieces?

**chi-ward-office:** Just that I'd hold them to it structurally, not just in
the copy. Access framing in the sentence and a sortable column in the same
table undoes itself — I said that already. What would actually convince me
it's not a ranking in disguise: don't let me sort forty-nine wards by that
number in one view. Show me my ward's number in a sentence, on our own page,
with the methodology one click away like you already do for other stuff.
That's the difference between "here's an investment case for your ward" and
"here's where your ward lands out of fifty," and right now, on paper, it
reads like it could become either one depending on where you put it.

**Interviewer:** Last one — where OYL's own quality grade for a segment
disagrees with this source's stress rating, which do you believe, and what
should the site do?

**chi-ward-office:** I don't fully believe either one on its own, honestly —
I believe whichever one I can explain in one sentence to a room. CDOT's grade
comes from CDOT, which is the same agency my alderwoman has to keep a working
relationship with, so there's an incentive question there I'm aware of even
if I don't say it out loud. The outside source has no reason to make CDOT
look good, which actually makes it more useful to me as a check, not less —
I'd trust a disagreement more than I'd trust either number by itself. What
the site should do: don't average them into one new grade, don't pick a
winner quietly. Show both, say why they disagree in plain words — "CDOT
calls this protected; this source flags it high-stress because of the
45-mile-an-hour cross street" — and let me decide what I say in the room.
The worst version is a single blended number where I can't tell which
source is driving it, because then when someone challenges me on it I can't
answer where it came from, and "I don't know where that number's from" is
the one sentence that actually ends a meeting badly.

## 5. Forced choice

**Interviewer:** Rank B1 through B4 for your own work — most useful to
least.

**chi-ward-office:** B1 first — the citywide score and trend, because it's
budget ammunition I can use in the next menu-money brief with basically zero
risk to my alderwoman personally. B3 second, the stress cross-check, but only
if it's pushed to me as a flag on corridors I'm actively defending — as
something I go looking for on demand, it's exactly what would have replaced
my phone call to Andrea. B2 third — genuinely useful language for the
budget case, but I'm not comfortable with it until I know it can't be sorted
into a fifty-ward leaderboard by accident. B4 last — not because it's bad,
it's just not built for my desk, that's a press-office tool.

**Interviewer:** Should OYL skip all four and put the effort somewhere
else? If so, where?

**chi-ward-office:** I wouldn't kill it outright — B1's cheap and it's real
ammunition, and B3 solves a problem I actually have right now. But if you're
asking me to trade effort, I'd put it into the thing I already told you I
wanted most last time we talked: promised-versus-delivered on capital
projects, tied to source, by ward. That's the thing I rebuild by hand every
time a resident says "you told us." A national bike-quality score is nice to
have. Knowing whether the bike lane we promised in 2022 actually got built is
the thing that costs me real hours every month. If it's a choice between
polishing this and building that, build that.

## 6. Kill question

**Interviewer:** What single thing about this integration, done wrong, would
make you stop trusting the site?

**chi-ward-office:** If the ward access number ends up in a sortable column
and somebody — a reporter, a challenger, doesn't matter who — builds a
"worst wards for bike access" list out of it, and OYL either enabled that
directly or didn't warn me it was coming before I saw it in print. That's
the whole thing I've been afraid of since Ward Wise burned us, just with a
new source and nicer words on the label. The access framing is good copy,
but copy doesn't stop a spreadsheet from getting sorted. If "access, not
danger" turns out to be true in the sentence but false in the table, I go
right back to treating this the way I treat the menu-money layer now —
distrusted by default, checked against something else before it ever goes
near my alderwoman.

## Analysis memo

participant: chi-ward-office
confidence_notes: Marcus stays in-register throughout — the political
triage lens (whose desk this lands on, who gets blamed, what survives a
room) governs every reaction, consistent with round 1 and with the
evidence base's documented ranking-as-liability instinct. The B3 misread
("stress rating" read first as traffic/congestion stress, not bike
comfort) is a clean, plausible in-world misreading per shared rule 7 — his
vocabulary has no prior exposure to LTS-style terminology, so defaulting
to the everyday meaning of "stress" on a street is exactly what a
non-specialist staffer would do. One point of lower confidence: his answer
on OSM-mapping currency ("could make my ward look worse than it actually
is because our infrastructure isn't well mapped") is a reasonable
extrapolation from his documented install-dates frustration and the
evidence base's PFB-mapathon note, but he has never actually encountered
an OSM-coverage argument in-world, so this is a first-exposure inference
rather than a recalled pattern — flag as directionally right but untested
against how he'd *actually* verify his ward's OSM coverage, which he
doesn't describe a method for. The B2 test — whether access framing
defuses the ranking instinct — produced a genuinely mixed answer rather
than a clean yes/no, which reads as authentic resistance (shared rule 3)
rather than flattening toward either "it works" or "it's useless."

stated_needs:
  - need: A stress/comfort rating per street segment, independent of
    facility type, to replace his informal "call CDOT and ask which
    streets you'd let your kid ride on" method for greenway and corridor
    nominations.
    evidence_quote: "That's actually the exact thing I was missing on the
    Greenways call six weeks ago — that's the number that would have
    replaced my phone call to Andrea."
    underlying_job: Recommend specific streets for limited greenway/quality
    funding slots with a citable, non-personal justification, rather than
    relaying one CDOT staffer's informal opinion as if it were data.
  - need: A citywide bike-network quality score with year-over-year trend,
    usable as budget-justification language distinct from ward-specific
    numbers.
    evidence_quote: "'The whole city is an 11 out of 100 against a national
    average of 36' is a sentence I can put in the budget one-pager that
    says this isn't optional, this isn't just our ward being behind."
    underlying_job: Justify menu-money allocation toward bike infrastructure
    over the politically easier default (repaving) using an argument that
    can't be dismissed as "just this ward's problem."
  - need: Advance, pushed notice — not a discoverable flag he has to go
    looking for — when an outside source contradicts a facility already
    described as "protected" in his own materials.
    evidence_quote: "If CDOT's calling something protected on paper and an
    outside group disagrees, I need that in my scar sheet before the next
    meeting on that corridor, not after."
    underlying_job: Avoid being contradicted in public by a resident or
    reporter holding data he didn't know existed, on a claim ("protected")
    he already made in his own one-pager.
  - need: Ward-level access language ("X% of residents lack low-stress
    access") usable in a spending-justification document, distinct from
    any sortable, cross-ward comparison surface.
    evidence_quote: "'Low-stress access to groceries' sounds like an
    investment ask, not a report card... I could actually use that in the
    same budget one-pager."
    underlying_job: Make the case for spending as an investment gap in his
    own ward, in his own document, on his own terms — not have the number
    used against him in someone else's.
  - need: When two data sources disagree (OYL's own grade vs. an outside
    stress rating), both numbers shown with a plain-language reason for
    the disagreement — never silently blended into one new score.
    evidence_quote: "Don't average them into one new grade, don't pick a
    winner quietly... 'I don't know where that number's from' is the one
    sentence that actually ends a meeting badly."
    underlying_job: Always be able to answer, on the spot, exactly which
    source a contested number came from and why it differs from a
    competing claim, so he is never caught unable to explain his own
    material.

latent_needs:
  - need: A pre-emptive rebuttal argument, built into how OYL frames a
    volunteer-mapped source, for the specific case where his ward's real
    infrastructure is undercounted by incomplete OSM tagging rather than
    genuinely absent.
    inference_basis: When told the source is OSM-derived and
    volunteer-updated, he did not just ask "is it current" (his round-1
    reflex on the geographic map) — he specifically constructed the
    argument he'd need in a room ("the score's low because the map's
    incomplete, not because the street's unsafe") before being asked to.
    This mirrors his round-1 install-dates frustration (needing to say
    "we did that in 2021" and having no way to prove it) and the evidence
    base's note that PFB itself runs mapathons because unmapped
    infrastructure lowers scores — he is extrapolating a known failure
    mode (source lag costs him credibility) onto a new source unprompted.
    risk_if_wrong: If OYL presents the BNA score as a clean fact without
    a way for ward staff to check whether their own known infrastructure
    is captured in the underlying OSM data, a ward office with genuinely
    good but under-mapped infrastructure has no defense against a score
    that makes them look worse than reality — and once he discovers that
    gap, per his deal-breakers below, he treats the whole source as
    another Ward-Wise-style liability rather than a source-specific
    caveat.
  - need: A structural (not just copy-level) separation between
    "framing language" and "sortable surface" for any ward-level number —
    i.e., the access percentage should not live as a column in the same
    table he already exports and hands to his alderwoman.
    inference_basis: He volunteered, unprompted, that "access" language is
    genuinely better rhetoric for him ("gives me better words to say out
    loud than a bare score would") — the framing worked partially, per the
    task's own test — but when told the proposal's candidate surface
    includes a ward-table column, he reversed hard: "then it's a ranking...
    the framing's just a caption nobody reads." This is a direct, in-session
    test of whether copy alone defuses his documented ranking-as-liability
    instinct (evidence base, persona file: "you distrust rankings of
    wards... who else will see this and what will they write"), and the
    answer is explicitly conditional on surface, not wording.
    risk_if_wrong: If B2 ships as a nullable column in the existing
    sortable ward table (as the proposal's own candidate-surfaces list
    suggests), the access framing fails exactly the audience it was
    designed to reassure — reproducing the Ward-Wise ranking incident from
    round 1 with a new, ostensibly friendlier data source, and burning
    trust faster because it was marketed as the fix for that exact problem.
  - need: A source-credibility check surfaced alongside any new external
    score — who published it, whether it has a track record comparable to
    ATA's — before he'll cite it in a document that leaves his desk.
    inference_basis: His very first reaction to B1, before any detail was
    given, was "who commissioned this... is this a group with an agenda" —
    unprompted, before the interviewer offered any framing about
    PeopleForBikes at all. This mirrors his established trust hierarchy
    from round 1 (ATA trusted because "they've never made us look worse
    than we actually are without cause"; Ward Wise distrusted after being
    burned once) — a new, unfamiliar source triggers the same vetting
    reflex by default, not conditional on being asked to vet it.
    risk_if_wrong: If OYL surfaces PeopleForBikes numbers without
    equivalent-to-ATA framing of who they are and why they're credible,
    ward staff either won't cite the numbers at all (wasted integration
    effort) or will cite them without vetting and get exposed if a
    skeptical audience asks "who says so" and the answer isn't ready.

reactions_to_proposal:
  - element: B1 — citywide BNA scorecard (score + trend + high/low-stress
    mileage)
    verdict: would-use
    why: Read immediately as low personal risk (citywide, not
    ward-specific) and directly reusable as budget-justification language
    ("this isn't just our ward being behind") for the menu-money
    repaving-vs-bike-infra fight he described in round 1. Conditional only
    on source credibility being vetted before he cites it, and on the
    trend line being included (he specifically wants "it's moving the
    right direction," not just the raw score).
  - element: B2 — ward-level access scores
    verdict: distrusts (conditionally — misreads the proposal's own
    framing intent until surface is specified, then partially reconciles)
    why: Initial gut reaction to "broken down by ward" was immediate,
    unprompted alarm ("this is a danger score with a nicer name on it"),
    before the access framing was even explained — confirming the
    ranking-as-liability instinct fires on the word "ward," not on the
    metric's actual shape. The access-framed language partially defused
    it (he called it "smarter language" and found a genuine budget use for
    the sentence form), but he explicitly reversed to distrust once told
    the candidate surface includes a sortable ward-table column, on the
    grounds that sortability — not wording — is what makes a number
    reusable as a ranking by a hostile third party. This is the interview's
    central finding: the access framing works in isolation as copy, and
    fails as soon as it's placed in a sortable, multi-ward surface.
  - element: B3 — segment stress cross-check against OYL's own facility
    grades
    verdict: misreads, then would-use with a specific delivery condition
    why: Initially misread "stress rating" as traffic/congestion stress
    (an everyday, non-specialist reading of the word, consistent with his
    documented vocabulary having no prior LTS exposure) before being
    corrected to bike-comfort stress. Once corrected, this was the single
    most enthusiastically received element — it directly answers a stated
    gap from the context re-anchor (the Greenways-nomination phone call to
    Andrea) — but his enthusiasm flipped to worry once told it cross-checks
    and can contradict his own "protected" claims; he wants disagreements
    pushed to him proactively (into his scar sheet / pre-brief workflow),
    not something he discovers passively or a resident finds first.
  - element: B4 — peer-city comparison strip
    verdict: ignores
    why: Read it as built for a different desk entirely ("that sounds like
    something the mayor's press office would put out... is this for me, or
    is this for the fifth floor?"). No recurring ward-level use case;
    conceded a rare, one-off utility if his alderwoman is ever asked to
    contextualize Chicago against peer cities at a citywide forum, but
    explicitly said he would look that up on demand rather than build a
    checking habit around it. One of the elements the protocol asked to
    confirm genuinely doesn't interest him — confirmed directly, not
    performed.

data_they_bring: The informal CDOT-liaison phone call ("which streets
would you let your kid ride on") as his current, sole quality-of-network
signal, written down in email so it isn't lost — a workaround this
proposal (specifically B3) would be the first thing to actually replace,
by his own account. Otherwise the same apparatus documented in round 1:
the ATA ward letter as trust baseline, the pre-brief ritual with a named
CDOT liaison, the scar/brag sheet for promised-vs-delivered tracking, and
the standing wariness toward any Ward-Wise-adjacent ranking, now
explicitly generalized to any new source that arrives "broken down by
ward" regardless of label.

deal_breakers: (1) The ward access number (B2) appearing as a sortable
column in a table alongside all fifty wards — he states this converts
"access" framing into a ranking regardless of the copy used, and treats it
as functionally identical to the Ward Wise incident that already burned
his office. (2) A blended or averaged score that silently resolves a
disagreement between OYL's own facility grade and an outside stress
rating, leaving him unable to say which source drove a number he's
citing — "I don't know where that number's from" is named explicitly as
the sentence that ends a meeting badly. (3) An unvetted, unfamiliar
third-party source presented without ATA-equivalent credibility framing,
which he would decline to cite in anything that leaves his desk. (4) A
segment-stress disagreement with his own "protected" claim discovered by
a resident or reporter before it reaches him — a direct extension of the
round-1 "burned" pattern to a new data source.

vocabulary: "access framing" / "danger score with a nicer name" (his terms
for testing whether relabeling a ranking actually changes its function);
"who else will see this" (recurring risk-assessment question, carried
forward from round 1, applied here to B2 specifically); "ammunition" (his
term for citywide, low-personal-risk numbers usable in the budget
one-pager, distinct from ward-specific numbers he treats as liabilities);
"investment ask, not a report card" (his read of well-executed access
language, offered as the standard he wants held to structurally, not just
in copy); "who commissioned this" / "who says so" (his source-vetting
reflex, applied unprompted to an unfamiliar national source); "leaderboard"
(what a sortable multi-ward column becomes regardless of its label); "the
fifth floor" (shorthand for content built for the mayor's office / press
office, not his desk — used to dismiss B4); "pushed to me" (his standard
for how a data-disagreement flag must be delivered — proactively, into his
existing workflow, not something he must discover); "scale of the target"
(his framework for why a citywide number is safer to defend than a
ward-specific one — the same bad number does less damage the more broadly
it's aimed).
