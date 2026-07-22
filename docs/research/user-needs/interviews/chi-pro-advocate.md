# Interview: chi-pro-advocate (Reyna Delgado)

**Run date:** 2026-07-21
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** (post-PR #51 — home/orientation page,
ward one-pager, methodology page, static agent API, news-coverage layer, proposed-projects
roster, PeopleForBikes BNA score, obstructions moved to gated preview page)
**Persona:** Reyna Delgado, advocacy manager, Chicago regional active-transportation nonprofit
(composite/fictional; see `personas/chi-pro-advocate.md` and evidence briefs
`evidence/chicago-system.md`, `evidence/us-thinktank.md`)

---

## Transcript

**Researcher:** Thanks for making time. Let's start with your actual work. Describe your role, and
walk me through the last decision you tried to influence about street safety — step by step, what
did that involve?

**Reyna:** Two weeks ago I was prepping testimony for the Committee on Pedestrian and Traffic
Safety — there was a hearing on the Archer Avenue redesign, which Lopez has been slow-walking for
two years. My job was to hand the committee something they couldn't wave off. Step by step: I
pulled the ward crash numbers for the 15th from our own quarterly letter draft — which was already
three weeks stale because our data person was out — then I called CDOT's community liaison to ask
if the corridor mileage numbers had changed since our last cycle, then I built a one-page PDF with
three bullets: deaths/injuries in the ward year to date, what % of Archer has any protection, and
the "72% of fatalities involve speeding" citywide line we always lead with. Took me about four
hours, mostly waiting on CDOT to call back and reformatting a table so it didn't look like a
spreadsheet dump.

**Researcher:** Who did you need to convince, and what does "convinced" look like for them?

**Reyna:** La Spata's committee, technically, but really I was writing for the aldermen who show up
undecided — the ones who haven't been burned yet by an angry ward night. Convinced looks like: they
ask CDOT a follow-up question in the hearing instead of just thanking us for our testimony. That's
the tell. If nobody on the dais asks a number-based question, we lost the room to whoever spoke
after us about parking.

**Researcher:** What information sources do you touch in a normal week for this?

**Reyna:** The city's crash portal directly — the raw Traffic Crashes dataset, because our letters
need it fresher than anything else publishes it. Ward Wise for menu money, because nobody else has
that scraped and clean. Bike Lane Uprising's dashboard when a company keeps showing up blocking the
same lane. Legistar, painfully, for hearing dates and who sponsored what. And a group text with two
other advocacy staffers where we just ask each other "does anyone have current numbers for the
32nd?"

---

**Researcher:** Tell me about the last time you needed a number, map, or chart about bike safety
and it actually took real effort to get.

**Reyna:** The 18th Street thing. After Dowell ordered CDOT to rip out the protected intersection,
I needed to know: had *any* crash reduction shown up in the months it was installed, so we could
argue removing it was reversing a safety gain, not just an aesthetic call. That data doesn't exist
in any one place. I ended up hand-counting crash records from the portal for a six-block radius, by
date, cross-referencing against the CDOT install date I got from a Streetsblog article because
CDOT itself won't publish exact install dates. Took the better part of a day. And in the end the
sample was so small — a few months, one corridor — that legally I couldn't say anything stronger
than "no increase in serious injuries during the period of protection," which is a weak sentence to
put in front of an alderman who wants to reopen the block to parking.

**Researcher:** What have you built yourself because nothing gave it to you directly?

**Reyna:** The ward letters, obviously — quarterly, by hand, in a shared Google Doc template, fifty
times over. A spreadsheet that cross-references menu money categories against what Ward Wise
labels "bike/ped" versus what CDOT calls "traffic calming," because those two sources don't agree
and I have to reconcile them by eye. And a personal doc I keep of committee-vote outcomes, because
Legistar doesn't make it easy to see "passed committee, died on the floor" as a single fact — I
watched that happen to the citizen-reporting ordinance in February and almost cited it as "passed"
in a follow-up email before I double-checked.

**Researcher:** Tell me about a time data — or the lack of it — sank an argument you were making.

**Reyna:** The Archer testimony, actually — a follow-up. An alderman's staffer asked me point blank:
"how many actual cyclists use this corridor, so I know if this is worth the parking we're
removing?" I had nothing. I had crash counts, I had lane-mileage, I had zero ridership. I said "we
don't have a good number for that" and you could watch the room recalibrate — like our whole ask
suddenly weighed less. That one stings because I don't think there IS a good public number for that
in Chicago. Bikeshare trip counts exist but Archer isn't near a Divvy-dense area.

**Researcher:** What data do you distrust, and what earned that distrust?

**Reyna:** 311 bike-lane complaints — because we've been told to our face by CDOT liaisons that they
don't drive enforcement, they're "for pattern identification only," which is bureaucratic for "we
collect it so people feel heard." I used it once in testimony as a volume signal and a CDOT witness
immediately said "that's not enforcement data, that's just what people reported," in a tone that
made it sound like I didn't know that, which undercut me in front of the room. Now I only use it as
color, never as a headline number.

---

**Researcher:** I want to walk you through what a dashboard called On Your Left is doing today.
It's read-only, doesn't take reports, drills ward to corridor to intersection, and every layer
carries a real/proxy/mock/crowdsourced/derived badge. There's also a static agent API now so an AI
assistant can query the same data. Let's go screen by screen and I'll ask your gut reaction to each
before I say more.

First: there's a new home page — plain-language orientation, headline stats, who it's for, and a
section on asking an AI assistant questions through the "agent layer." Reaction?

**Reyna:** Honestly the AI-assistant framing makes me suspicious before I even see the numbers.
Every "ask our AI" thing I've touched in the last year has been a chatbot wrapper someone bolted on
to look modern, and none of them cite a source I could read into a hearing record. If it's
literally just querying the same published JSON, fine, but I'd want to test it on something I
already know cold — like ward 15 crash counts — before I'd trust an answer it gave a resident.

**Researcher:** Noted — we'll come back to the agent layer specifically. Next: the transportation
map, with crash density, bikeway network by facility grade, wards, cameras, main-route overlays.
Mock obstructions are no longer shown here.

**Reyna:** Good, actually — that's the right call, because if I'd opened this map eight months ago
and seen fake obstruction dots sitting next to real crash dots, that's the kind of thing that gets
screenshotted and used against us by someone at a community meeting who says "see, they're making
stuff up." Facility grade by color I'd use for exactly what I did with Archer — showing "here's the
gap in protection" visually instead of in a table. I'd want to zoom to ward first, though; a
citywide map is not what I open before a hearing about one corridor.

**Researcher:** There's also a network map — a schematic transit-style map of 21 named main routes,
with a comfort-floor filter and no safety data at all on that page.

**Reyna:** That one's not for me. It's pretty, but I don't bring a "how legible is the network"
argument to a hearing — I bring "people got hurt here." If a resident asked me to help them plan a
commute I might send them there, but that's not my job description.

**Researcher:** Findings page — curated cards: KSI trend, protected share, street coverage, top
corridors, hit-and-run, ward concentration, dooring undercount, and the PeopleForBikes BNA citywide
score with national ranking context.

**Reyna:** The KSI trend and ward concentration cards, I'd screenshot those into a slide deck
tomorrow, assuming the caveat text is actually readable and not buried. The BNA score I don't know
what to do with — is 100 good? Compared to what other city? I've genuinely never had anyone at a
hearing ask me "what's Chicago's BNA score," and I don't think an alderman's staffer would know
what it means without me explaining it first, which means it's homework, not ammunition. I'd read
the caveat before I'd repeat the number out loud.

**Researcher:** Table page — ward rankings, sortable, CSV, with percent-protected and
percent-streets-with-bikeways columns.

**Reyna:** This I'd actually use for the reconciliation work I described — checking Ward Wise's
numbers against something else. CSV export matters a lot to me; I don't want to copy-paste fifty
rows out of a webpage.

**Researcher:** Ward one-pager — one HTML file per ward, printable: safety index, trends, infra
stats, alderman contact and sponsorship record, menu-money proxy, recent ward-matched news.

**Reyna:** [leans in] Okay, this is the first thing you've shown me that's literally the artifact I
build by hand every quarter. So now I have real questions. The safety index — is that comparable
ward to ward, or relative within itself? Because if ward 15's "safety index" moved from 40 to 45
that means nothing to me unless I know whether that's percentile-based or some raw score, and I
will absolutely get asked "what does 45 mean" by someone in the room, and "it's a percentile blend
of crashes per 10k and crashes per bikeway-mile" is a sentence I'd need to have memorized before I'd
say it out loud. Second — the sponsorship record. Does it show committee AND floor votes
separately, or just "sponsored"? Because if Lopez's staffer looks at this and it just says
"sponsored," they'll say "he was FOR it" about something he later gutted on the floor, and that's
exactly the kind of mismatch that would blow up on me if I handed this to a reporter. Third, the
menu-money — you said "proxy," not verified against source PDFs. That's a real problem for me
specifically, because Ward Wise already does menu money and if your number doesn't match theirs,
the first thing a ward staffer does is pull up Ward Wise on their phone mid-meeting and go "that's
not what it says here." One mismatch I can't explain and I stop using this for anything
ward-specific, full stop.

**Researcher:** To be clear on the sponsorship data — it tracks sponsorship counts and recorded
no-votes, and it's explicitly labeled a sponsorship proxy, not a vote tally.

**Reyna:** Then it needs to say that in bold, not in a footnote, because "proxy" is a word data
people use and a word alderman's staff will skip right past. If it just shows a number of bills
sponsored, somebody will read that as "this alderman is good on bike safety" and I've watched that
exact mistake get someone's testimony torn apart in committee before — because sponsorship is often
just a courtesy signature, not commitment. Show me the no-votes prominently or don't bother.

**Researcher:** Sources and methodology pages — full provenance catalog, tier badges, and how every
number is computed.

**Reyna:** This is the page I'd actually screenshot to defend myself if someone challenges a number
in the room — "here, this is exactly how it's built, here's the source." That's worth more to me
than most of the visualizations, honestly, because my job half the time is surviving the
cross-examination after I say a number out loud.

**Researcher:** Action page — 311, Bike Lane Uprising, alderman contacts, hearings, recent news.

**Reyna:** The hearing calendar I'd use — I currently track that by hand and it's the single most
annoying thing I do every week. If it's actually current the week I need it, that alone might get me
to open this site regularly, more than any map would.

**Researcher:** And there's a new obstructions preview page — gated, watermarked, explicitly
synthetic, quarantined off the main maps, pending an actual Bike Lane Uprising conversation.

**Reyna:** [flat] I want to be really clear about this one. I know Bike Lane Uprising's real
dataset — 65,000-plus reports, refreshed every few hours, used in actual litigation. If I clicked
into a preview page and it wasn't obviously, aggressively labeled fake — big watermark, can't
mistake it for real — I would assume for one confused second that OYL had struck a data deal with
BLU, and then I'd be furious when I found out it was made up. That's the fastest way to lose me
permanently, not just on this feature — on the whole site. Because now I have to ask "what ELSE
here isn't what it looks like?" Gating it behind a warning and excluding it from the API entirely
is the right instinct. But I'd want it to not exist at all in a public build, honestly — synthetic
crash-adjacent data is the one category where "clearly labeled" isn't good enough for me, because
the whole reason a mock layer is dangerous is that it doesn't stay clearly labeled once someone
screenshots it into a flyer without the watermark.

**Researcher:** Let's talk about the "no ridership normalization" caveat directly — the site says
it doesn't normalize by ridership because no cyclist-volume data is joined yet. Does that caveat
change how you'd use it?

**Reyna:** It doesn't change whether I'd use the raw counts — I already use raw counts today,
because that's all Chicago has, full stop, the same way CDOT's own High Injury Network doesn't
normalize by ridership either, it's just severity-weighted crash density. So on that specific point
OYL isn't behind CDOT. But saying the caveat out loud is exactly what saved me nothing in that
Archer meeting — the staffer's question wasn't "does OYL normalize," it was "do YOU have a
ridership number," and neither of us did. What I'd accept as good-enough exposure data: honestly,
Divvy trip counts by station, imperfect as they are, would be something — at least I could say
"here's a lower-bound proxy for people who biked near here" instead of nothing. Or even a rough
count of 311 bike-complaint volume as an activity proxy, labeled honestly as biased toward wards
with engaged residents — I'd rather have a bad proxy I can caveat than the silence I have now. A
BNA-style network score doesn't answer this for me at all — that's about the streets, not the
riders on them, and I said that already about the findings card.

---

**Researcher:** Let's do the new pieces you haven't reacted to yet. The news-coverage layer —
recent bike-safety headlines from RSS feeds, matched to wards, aldermen, routes, projects, with an
auditable link showing why each match was made.

**Reyna:** The "why matched" link is the only reason I wouldn't immediately distrust this. My fear
walking in was: some algorithm decides a story about a shooting near a bike lane counts as "ward 15
bike safety news" and now I'm associated with a mismatch I didn't check. If I can click through and
see the actual matching logic, I could maybe use this to catch news I missed for a ward I don't
cover closely. But I'd never cite it directly in testimony — I'd use it to go find the original
article and cite that instead. It's a lead generator, not a source.

**Researcher:** Proposed and in-progress projects — a hand-curated roster of active bikeway/trail
proposals, volunteer-reviewed status with a status date and note, official links and citations, no
map geometry.

**Reyna:** "Volunteer-reviewed" is doing a lot of work in that sentence and I'd want to know who the
volunteers are before I'd put this in front of an alderman's staffer, because the fastest way CDOT
discredits us is finding one stale or wrong status on a project list and using it to imply
everything we cite is sloppy. No geometry doesn't bother me — I don't need a line on a map, I need
to know if Archer's redesign is "approved," "stalled," or "dead," and a status date tells me whether
that's this month's truth or six months old. If the status date is old I'd treat the whole card as
suspect until I called CDOT myself to confirm — which, honestly, is exactly the phone call I
already make today, so this doesn't remove work unless the update cadence is fast and visible.

**Researcher:** And the agent API — you reacted early with suspicion. Walk me through what would
change your mind.

**Reyna:** I'd want to ask it the exact question that burned me — "how many cyclists use Archer
Avenue" — and see if it says "I don't have that data" instead of hallucinating a number, because
that's the actual failure mode I'm scared of. A chatbot that confidently invents a ridership figure
because it pattern-matched from somewhere is worse than the silence I have now, because now a
staffer might repeat a wrong number in a hearing and attribute it to "the data." If every response
links back to the actual published file with the tier badge, and it just refuses when there's no
data, I could see forwarding it to a ward staffer who doesn't want to learn to read a CSV. But I'd
test it myself first, on my own turf, before I ever pointed a stranger at it.

---

**Researcher:** Picture you're prepping for a council hearing next Tuesday on a ward you don't
normally cover. You open OYL. What do you look for first, and where does it fail you?

**Reyna:** First thing I do is the ward one-pager for that ward, because that's the fastest way to
get oriented on unfamiliar turf. Where it fails me: if the alderman's sponsorship record doesn't
distinguish committee votes from floor votes, I have to go verify in Legistar anyway, which means
the one-pager saved me zero time on the part I actually needed saved.

**Researcher:** Of everything OYL does not have, what single absence costs you most?

**Reyna:** Ridership. I said it already and I'll say it again — it's the one question I get asked
that I have no answer for, in any dataset, from anyone, and it's the one that makes a room stop
taking us seriously mid-sentence.

**Researcher:** If OYL handed you one export or artifact each week, what would it contain, and who
would you forward it to?

**Reyna:** A one-page PDF per ward that's actually current — crash trend, sponsorship record with
committee-vs-floor distinction, and this week's hearing dates if any — and I'd forward it straight
to whichever ATA staffer covers that ward's letter that quarter, because it would replace the four
hours I spend building that by hand. But only once I've caught it lying to me zero times.

---

**Researcher:** Magic wand — one dataset that doesn't publicly exist appears, clean and current.
What is it?

**Reyna:** Cyclist volume counts, ward by ward, updated regularly — actual bike traffic counters or
something as good as them, not proxies. If that existed I could finally answer the Archer question
and I'd trust every crash rate on this site twice as much.

**Researcher:** One chart or map you could put in front of your hardest audience that ends an
argument.

**Reyna:** A single ward map showing crash severity concentration overlaid with menu-money spend on
safety versus everything else, side by side, so a room can see in one glance "this ward has the
worst numbers and the least money went to fixing it." That argument makes itself if the chart is
honest and doesn't need me to say a word.

**Researcher:** What would make you stop using a site like this after trying it once?

**Reyna:** One number that contradicts a source I already trust, that I can't explain to a room.
That's it. Doesn't even need to be big — a ward count off by ten, a "sponsored" that should've said
"co-sponsored, later voted no." One unexplainable mismatch and I go back to building my own
spreadsheets, because my job doesn't survive being wrong in public.

---

## Analysis Memo

```
participant: chi-pro-advocate (Reyna Delgado)
confidence_notes: The persona's specificity about committee-vs-floor voting and Ward Wise
  reconciliation is well-grounded in the evidence brief. Weaker ground: her reaction to the agent
  API is plausible extrapolation (advocacy staff distrust of AI chatbots) rather than something
  directly documented in the evidence base — flagged as informed inference, not a citable fact.
  Her reaction to the network map (dismissive, "not my job") is a confident in-character read but
  is thinner than her ward-letter material since the evidence base says little about advocates'
  network-legibility use cases one way or the other.

stated_needs:
  - need: A ward one-pager that separates committee votes from full-Council floor votes in
      sponsorship/legislative records, not a single "status" or "sponsored" field.
    evidence_quote: "if it just says 'sponsored,' they'll say 'he was FOR it' about something he
      later gutted on the floor, and that's exactly the kind of mismatch that would blow up on me"
    underlying_job: Defend a legislative claim in front of a hostile or skeptical room without
      being corrected live by someone who knows the real vote history.

  - need: Menu-money figures that reconcile with (or explicitly diverge from and explain) Ward
      Wise's numbers, since her audience will cross-check live.
    evidence_quote: "if your number doesn't match theirs, the first thing a ward staffer does is
      pull up Ward Wise on their phone mid-meeting... One mismatch I can't explain and I stop using
      this for anything ward-specific, full stop."
    underlying_job: Avoid public credibility loss when a number is checked against a source her
      audience already trusts more than OYL.

  - need: A weekly per-ward export/artifact (crash trend + sponsorship w/ committee-vs-floor +
      that week's hearing dates) to replace her hand-built quarterly ward letter.
    evidence_quote: "A one-page PDF per ward that's actually current... I'd forward it straight to
      whichever ATA staffer covers that ward's letter that quarter, because it would replace the
      four hours I spend building that by hand."
    underlying_job: Stop rebuilding the same artifact from scratch every quarter under time
      pressure with stale inputs.

  - need: A current, reliable hearing calendar (Committee on Pedestrian and Traffic Safety).
    evidence_quote: "I currently track that by hand and it's the single most annoying thing I do
      every week. If it's actually current the week I need it, that alone might get me to open this
      site regularly."
    underlying_job: Know when and what to prepare testimony for without manually monitoring
      Legistar.

  - need: An honest, un-hallucinating answer from the agent API when asked a question with no
      underlying data (e.g., ridership), rather than a plausible-sounding invented number.
    evidence_quote: "A chatbot that confidently invents a ridership figure... is worse than the
      silence I have now, because now a staffer might repeat a wrong number in a hearing and
      attribute it to 'the data.'"
    underlying_job: Prevent a junior/less-data-literate colleague from unknowingly citing a
      fabricated number in public.

latent_needs:
  - need: A ridership/exposure proxy layer (even an imperfect one, honestly labeled) surfaced
      adjacent to crash and safety-index numbers — not just a caveat that none exists.
    inference_basis: She independently proposed two concrete substitute proxies unprompted (Divvy
      trip counts, 311 volume "labeled honestly as biased") when asked what she'd accept as
      good-enough — she is not merely tolerating the absence, she has already identified workaround
      candidates because the absence has cost her in a real meeting (the Archer staffer question).
    risk_if_wrong: If OYL never surfaces any exposure proxy, its safety-index and crash-rate numbers
      stay permanently vulnerable to the single question that has already sunk one of her
      arguments; if it adds one without her level of caveat rigor, it risks becoming exactly the
      kind of unexplainable number that would trigger her stated deal-breaker.

  - need: Provenance/methodology material written so it can be recited verbatim in a hostile room,
      not just read for her own understanding.
    inference_basis: She singled out the sources/methodology pages as "worth more to me than most
      of the visualizations" specifically because her job is "surviving the cross-examination after
      I say a number out loud" — she evaluates every page by whether she could defend it live, not
      whether she personally understands it.
    risk_if_wrong: If methodology text reads well to a data-literate reader but isn't quotable in
      one breath, it will look present on paper but fail in the actual use moment (a hearing),
      which the study can't detect without watching her actually testify.

  - need: The mock-obstructions layer excluded from any build she might link a stranger to, not
      merely watermarked/gated — i.e., her trust threshold for synthetic data adjacent to a real,
      named, litigated real-world dataset (Bike Lane Uprising) is categorically stricter than for
      other proxy/derived tiers.
    inference_basis: Unprompted, she generalized from the single feature to the whole site
      ("now I have to ask what ELSE here isn't what it looks like") and explicitly said watermark
      labeling "isn't good enough for me" for this category specifically, distinguishing it from
      her calmer reaction to other proxy-tier data (311, menu-money) earlier in the interview.
    risk_if_wrong: Overbuilding trust-repair here (e.g., more aggressive watermarking) could satisfy
      a casual user while missing that her actual bar is non-existence in any public-facing build —
      a stricter, costlier requirement than the current design assumes.

  - need: A comparative, not just descriptive, ward view — danger/need vs. money actually spent —
      as the unit of political argument, not raw ward stats alone.
    inference_basis: Her unprompted magic-wand answer combined two datasets OYL already has
      separately (safety index, menu-money) into one overlay and said the argument "makes itself"
      without her needing to speak — she is describing a combination the site doesn't currently
      offer as a single view, inferred from what she reached for when given a free choice.
    risk_if_wrong: If this reads as "she just wants a chart," the real signal — that her political
      argument's entire structure is disparity-between-two-existing-numbers, not either number
      alone — could get lost, leading to a chart feature that shows both numbers without forcing
      the comparison she actually needs.

reactions_to_existing:
  - feature: Transportation map (crash density + facility grade, mock obstructions removed)
    verdict: would-use
    why: Matches her actual testimony-prep pattern (visualizing a protection gap), and she
      explicitly approved of obstructions being removed from it as reputational risk mitigation.

  - feature: Network map (schematic, no safety data)
    verdict: ignores
    why: Out of scope for her job description ("I don't bring a 'how legible is the network'
      argument to a hearing"); she'd redirect residents there but wouldn't use it herself.

  - feature: Findings cards — KSI trend, ward concentration
    verdict: uses
    why: Directly screenshot-into-deck material, matching her existing citywide framing lines.

  - feature: Findings card — PeopleForBikes BNA score
    verdict: ignores / misreads-risk
    why: No context for what a good score is relative to other cities; she flags it as homework
      she'd have to explain rather than ammunition she could deploy, and worries a staffer would
      need it pre-explained.

  - feature: Ward table + CSV export
    verdict: would-use
    why: Fits her existing reconciliation workflow (cross-checking scraped sources against each
      other); CSV format specifically named as necessary.

  - feature: Ward one-pager
    verdict: would-use, conditionally / distrusts pending verification
    why: Matches her core artifact exactly, but she flagged three specific unresolved risks
      (safety-index interpretability, sponsorship granularity, menu-money reconciliation) any one
      of which she said would break trust if wrong.

  - feature: Sources / methodology pages
    verdict: uses
    why: Named as her go-to defense artifact for hostile-room cross-examination — valued for
      recitability, not just accuracy.

  - feature: Action page (hearings calendar, contacts, 311/BLU links)
    verdict: would-use
    why: The hearing calendar specifically replaces a manual tracking task she already described
      as her most annoying recurring chore.

  - feature: Obstructions preview page (gated, watermarked, synthetic)
    verdict: distrusts
    why: Recognizes the real Bike Lane Uprising dataset by name and scale; treats any synthetic
      stand-in — however labeled — as a categorical credibility hazard that would generalize into
      distrust of the whole site if surfaced carelessly.

  - feature: News-coverage layer (auditable ward/alder/route matching)
    verdict: would-use, narrowly
    why: Values the "why matched" audit link as a lead-generation tool but would never cite the
      aggregation itself in testimony — treats it as a pointer to primary sources, not a source.

  - feature: Proposed-projects roster (volunteer-reviewed status)
    verdict: would-use, conditionally
    why: Wants to know who "volunteer-reviewed" means and treats stale status dates as reason to
      independently verify by phone — doesn't remove her existing CDOT-call workaround unless
      update cadence is visibly fast.

  - feature: Static agent API / "ask an AI assistant"
    verdict: distrusts, pending her own test
    why: Primed to distrust by prior experience with unsourced chatbot wrappers; would only trust
      it after personally testing it on a question she already knows the answer to, and specifically
      wants to see it refuse rather than hallucinate on missing-data questions (ridership).

data_they_bring: Quarterly hand-built ward letters (crash data by ward, sourced from the raw city
  crash portal directly rather than any secondary dashboard); a personal reconciliation spreadsheet
  cross-referencing Ward Wise menu-money categories against CDOT's own labels; a private log of
  committee-vs-floor vote outcomes because Legistar doesn't surface that distinction cleanly;
  manual hand-counts of crash records against unpublished CDOT install dates (sourced from press
  coverage, not CDOT itself) when she needs before/after evidence; a hearing-date tracking habit
  maintained entirely by hand.

deal_breakers: A single ward number that contradicts a source she already trusts (Ward Wise,
  Legistar, her own letters) that she cannot explain live in a room; a sponsorship field that reads
  as support when the real record includes a later no-vote; any synthetic/mock data that isn't
  unmistakably and permanently distinguishable from a real, named dataset (Bike Lane Uprising) she
  already knows in detail; an AI-assistant answer that invents a number instead of declining.

vocabulary: ward, alder, menu money, prerogative, KSI / "deaths and serious injuries," testimony,
  the committee, CDOT, "the portal," high crash corridor, "our letter," "who's the alder there?",
  sponsored vs. co-sponsored vs. voted no, safety index (used skeptically, not natively — she
  interrogates rather than adopts this term), proxy (used as a term of suspicion), volunteer-
  reviewed (used to flag an unresolved credibility question).
```
