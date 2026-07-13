# Interview: chi-cdot-planner

## Round 1 transcript

# Round-1 Interview Transcript — Persona: Elena Kowalski (CDOT Bikeways PM)

## 1. Context

**Interviewer:** Can you describe your role, and walk me through the last decision you influenced — or tried to — about street safety? What did that actually involve, step by step?

**chi-cdot-planner:** I'm a project manager in Complete Streets, bikeways side, at CDOT — eight years now, so I've outlasted two commissioners and I'm working on my third Cycling Strategy cycle even though we've only had the one, the 2023 version. The last real decision — and I use "decision" loosely because half my job is other people deciding and me absorbing it — was about the protected intersection design on 18th between Clark and Indiana. That one's still a sore spot. We had design done, contractor mobilized, and Ald. Dowell's office called a community meeting after the fact — after installation had already started — because some business owners said they weren't consulted enough about loading zone impacts. I sat through that meeting. I supervised the removal order that came out of it in November. That's eight months of my PM load and two rounds of community engagement documentation, undone in about three weeks. My team still brings it up in retros.

The step-by-step, if you actually want it: corridor gets flagged through our High Injury Network refresh — we run that off three years of Data Portal crash records, severity-weighted, so it's not just raw counts — 18th Street scores high for KSI density near Clark. That feeds into our High Crash Corridors framework, gets prioritized in CIP, goes through 30% design, community process — usually a task force meeting or two, sometimes more depending on ward temperament — then installation. Somewhere between "installation" and "ribbon cutting" is where prerogative can still reach in and grab it, executive order or no executive order. I was in the room in 2023 when Commissioner Biagi and Ald. La Spata talked about this on the record — everybody in my building already knew it, we just don't say it in press releases.

**Interviewer:** Who do you need to convince, and what does "convinced" look like for them?

**chi-cdot-planner:** Depends which layer. Internally, it's my design engineer and my director, and "convinced" there is a defensible before/after case and a budget line that doesn't blow up the CIP. Externally it's the alder — and "convinced" for an alder almost never means the crash data, it means "will my ward office get blamed." Then there's the community task force, where convinced means their named destinations and barriers — a school, a grocery store, a dangerous rail crossing — show up in the design, not just my crash dots. Austin and Belmont Cragin and North Lawndale tripled their bikeway mileage in two years because those task forces identified where people actually wanted to go, not because I put a HIN map in front of anyone. I want people to understand that — crash data gets me a seat at the table, community process gets shovels in the ground.

**Interviewer:** What information sources do you touch in a normal week for this work?

**chi-cdot-planner:** The Data Portal crash tables directly — I know the E-Crash sourcing well enough to know when a batch of records is still provisional versus amended. Our internal GIS layers for the bikeway network, which I help maintain feeds into "the portal," meaning our own public data catalog, not some outside dashboard. Emails and PDFs from OBM on menu allotments. Whatever the current task force is producing — sign-in sheets, sticky-note maps, that kind of thing. And increasingly, our 2026 corridor economic study, which I now bring to literally every merchant meeting because it's the only piece of ammunition I have against "bike lanes killed my parking."

## 2. Current Practice & Workarounds

**Interviewer:** Tell me about the last time you needed a number, map, or chart about bike safety. Where did you go, what did you do with it, how long did it take?

**chi-cdot-planner:** Three weeks ago I needed a before/after crash comparison for the Milwaukee Avenue corridor for a briefing memo — Commissioner's office wanted talking points ahead of a Streetsblog inquiry about the "100 miles" announcement. I pulled raw crash records from the portal, filtered to the corridor buffer myself in GIS, because our published bikeway layer has no install dates — I want to say that again, because it drives me up a wall — the layer I publish has no install dates. So I can't just query "crashes since install." I had to go find the actual CIP substantial-completion memo, cross-reference the date by hand, then rebuild the before/after window myself in a spreadsheet. That took the better part of a day, and it's a spreadsheet that lives on my laptop, not anywhere anyone else could find it if I got hit by a bus tomorrow — sorry, bad phrase for this line of work.

**Interviewer:** What have you built yourself because nothing gave it to you directly?

**chi-cdot-planner:** That install-date spreadsheet is the big one — I've been maintaining it corridor by corridor for two years, cross-referencing substantial completion memos, my own site visit photos, and sometimes just asking my design engineer "when did this actually go in the ground." It's incomplete. It has maybe sixty corridors in it out of however many hundred we've built. I also keep a screenshot folder of every merchant meeting slide I've made, because I redo the same "will this hurt my business" rebuttal constantly and I'd rather steal from myself than start from scratch. And I have a standing favor with someone in our data team who'll pull a manual count for me if I really need ridership numbers for a specific block — we have exactly one permanent counter, at Chicago and Wells, installed in 2022. One. For the whole city. Everything else is a manual count crew for a week if the budget allows it, which it usually doesn't.

**Interviewer:** Tell me about a time data — or the lack of it — sank an argument you were making.

**chi-cdot-planner:** The 18th Street removal, again, honestly. I didn't have ridership data to say "X hundred cyclists a day are using this," because we don't count ridership anywhere near comprehensively — we have exposure data for basically one intersection in the entire city. So when the pushback came in framed as "nobody uses this," I had crash severity data, which tells you how dangerous a corridor was, not how many people were choosing to avoid it because it was dangerous, or how many would use it if it were safe. I couldn't answer the actual question being asked. That's the gap that costs me the most, over and over.

**Interviewer:** What data do you distrust, and what earned that distrust?

**chi-cdot-planner:** 311 bike-lane-blockage counts — I know for a fact those skew toward whichever wards have residents who actually use 311, which correlates with income and internet literacy, not with where blockages actually happen. I've had advocates cite 311 volume back at me as if it's a blockage map, and I have to explain, again, that it's a reporting-behavior map. And honestly — I'll say this only because you're not going to publish my name on it — I've started distrusting some of our own facility-type tagging in the GIS layer, because "buffered" versus "protected" gets applied inconsistently depending on which contractor's as-built drawing someone digitized ten years ago. I fact-check that stuff myself now before I let anyone cite our mileage numbers, because mileage claims are exactly where CDOT gets hammered publicly — somebody will always find the one segment we called "protected" that's really just a painted buffer with flex posts missing.

## 3. Stimulus Walkthrough

**Interviewer:** Let me walk you through what a site called "On Your Left" offers — it's an independent, read-only dashboard, not run by the city, that layers bike infrastructure, obstructions, and crashes, drillable ward to corridor to intersection. Every layer carries a real/proxy/mock/crowdsourced/derived/no-data-yet badge. It doesn't normalize by ridership — no volume data joined — and it says so. Let's go area by area. First, the transportation map — crash density, bikeway network colored by facility grade, wards, cameras, mock obstruction heat, main-route overlays.

**chi-cdot-planner:** Okay, first reaction — facility grade coloring is exactly where I'd start poking. What's their taxonomy, protected, buffered, painted, greenway, sharrow, trail, other? Because if they're lumping two-way cycle tracks in with regular protected lanes, or counting a greenway as automatically "low-stress" without checking whether it's actually got the traffic calming installed yet, that's a fight waiting to happen. I'd use this to sanity-check what an advocate or a journalist is about to hold up in a hearing — I want to see it before they show it to me, basically. The mock obstruction heat, though — I want to flag that immediately, because if I glance at that map fast in a meeting, my instinct is to read "heat" as "this is where obstructions are happening," and someone would have to stop me and say no, this is synthetic, this is placeholder. That's a real risk with a heat layer — it doesn't visually announce "not real" the way a badge in a legend does. I'd want that thing behind an extra click, not sitting on the default view.

**Interviewer:** Next, the network map — a schematic, transit-style rendering, 21 named main routes each solid-colored end to end, interchange nodes, an opt-in quality border, toggles for crowdsourced "mellow routes." No safety data on this screen.

**chi-cdot-planner:** Honestly? Not for me. That's a rider-facing thing, that's for somebody deciding how to get across town on a Saturday, not for scoping a corridor or defending a mileage number to an alder. I don't disqualify it for existing, but if you're asking would I open it in a normal week — no. I'd rather have the plain map with the facility grades on it. The transit-style abstraction is going to distort distances and connections in a way that's fine for wayfinding and useless for planning.

**Interviewer:** Findings — curated cards with a stat, a caveat, and a deep link. KSI trend, protected share, street coverage — post-PR, 3,944 miles of surface streets, 446 miles or 11 percent with any bike infrastructure — top corridors, hit-and-run, ward concentration, dooring undercount.

**chi-cdot-planner:** The coverage stat I'd actually check against our own numbers before I let it near a meeting — 11 percent of surface streets with any bike infra sounds low to me off the top of my head, but I'd want to know their denominator matches ours, because "surface streets" can mean different things depending whether you're excluding alleys, excluding expressway frontage roads, that kind of thing. If it checks out, that's a card I could genuinely see myself screenshotting for an internal memo, because it's blunter than anything I currently have pre-packaged. The dooring undercount card — good, that's accurate, we know official records only catch reportable dooring incidents, that's not new information to me but it's nice that they say it out loud instead of me having to explain it every time.

**Interviewer:** The ward table — rankings, sortable, CSV export, plus percent protected and percent streets with bikeways columns.

**chi-cdot-planner:** This is the one I'd actually bookmark. CSV export, sortable by ward — that's the format ATA already uses in their ward letters to alderpeople, so if this table roughly agrees with what ATA is sending alders, it's useful cover for me, because now it's not CDOT saying your ward is behind, it's an independent outside number saying it, and the alder can act on it without it looking like City Hall scolding them. I'd want to check the "percent protected" methodology hard, though — protected out of what denominator, on-street bikeway miles or total street miles — because those numbers can be made to say wildly different things depending on which one you use, and I need to know which one before I forward it to anyone above me.

**Interviewer:** Sources — a full provenance catalog with tier badges. Action — links to 311, Bike Lane Uprising, alder contacts. Contributing — how to swap data sources or fork it.

**chi-cdot-planner:** Sources page, I'd read once, carefully, the first time I ever used this thing, and then probably never again unless something looked wrong. Action page — fine, that's not really for me, I'm not the audience routing a constituent to 311. Contributing page, not relevant to my job at all.

**Interviewer:** Now the council and alderman data — Legistar-sourced records frozen at 2023-06, automated topic tagging, sponsorship counts and recorded no-votes per alderman, committee hearing calendar from the City Clerk's eLMS API, and menu-money spending pulled from a Ward Wise-style extract, not verified against source PDFs.

**chi-cdot-planner:** The hearing calendar, genuinely useful — I already track Pedestrian and Traffic Safety committee dates by hand, so an automated feed of that saves me an email to a committee clerk. The sponsorship and no-vote tracking, I'd want to be careful with, because sponsorship isn't the same as commitment — I've watched an alder co-sponsor something and then quietly kill it in their own ward through prerogative anyway, so a sponsorship count alone doesn't tell you what actually got built. And the menu-money numbers — "not verified against source PDFs" is doing a lot of work in that sentence, and it's the sentence I'd stop on. I know the real menu program, I've sat in meetings about it, and if this is a scrape that hasn't been checked against the OBM PDFs, I'm not putting that number in front of an alder's chief of staff. That's the kind of thing where if it's off by even one project, the alder's office will remember it was wrong forever and stop trusting anything else on the site too — and possibly stop trusting me for having shown it to them.

**Interviewer:** Last piece — the mock bike-lane obstruction layer. It's entirely synthetic right now, built to the same schema as Bike Lane Uprising's real data, pending an actual data-sharing conversation with them.

**chi-cdot-planner:** That one I would flatly not use. Not "use carefully" — not use, period, in front of an external audience. I don't care how clearly it's badged, because badges get lost the second someone screenshots a map and drops it into a text thread or a community Facebook group. I've watched a bad number escape its caveats before — it becomes my cleanup, not theirs. If Bike Lane Uprising's real data ever gets folded in, fine, that's a different conversation, that's a real dataset I already respect. But synthetic obstruction data is a landmine sitting on a public map, and I would tell whoever runs this site that directly if they asked me.

## 4. Gap Probing

**Interviewer:** Say you're briefing an alderman's office ahead of a vote — or a menu-money deadline. You open On Your Left. What do you look for first, and where does it fail you?

**chi-cdot-planner:** First thing I'd want is that ward table — where does this ward rank, crashes, coverage percent, so I can walk in with an outside number instead of only a CDOT number. That's genuinely useful, I said that already. Where it fails me immediately is anything about what got built with the menu money versus what was promised for bike safety specifically — because that's exactly the question a chief of staff asks me two days before an allocation deadline, "what did we actually spend on bike stuff last cycle versus paving," and this site's menu-money layer is an unverified scrape, so I still end up back in the OBM PDFs myself, by hand, like I already do. It doesn't save me the work it looks like it would save me.

**Interviewer:** Of everything OYL does not have, what single absence costs you most?

**chi-cdot-planner:** No install-date history on the bikeway network — and I recognize the irony that that's my own layer's gap, they inherited it from us, it's not their fault. But it means nobody, including this dashboard, can do a real before/after. Every "did this corridor get safer" claim anyone makes off this site is going to be built the same artisanal way I build mine — hand-matching a completion date to a crash window. If someone handed me forward-built snapshot diffing that actually nailed install dates, I would take that more seriously than almost anything else on this list, because that's my holy grail and also my professional embarrassment, in the same sentence.

**Interviewer:** The site refuses to normalize by ridership because it has no volume data. Does that change how you'd use it? What would you accept as good-enough exposure data?

**chi-cdot-planner:** It doesn't surprise me, and honestly I respect that they say so instead of faking a rate. It changes what I'd use the raw counts for — I wouldn't use them to argue "this corridor is per-rider more dangerous than that one," because I genuinely don't know, and neither do they. I'd use them to argue "this corridor has more severe crashes in absolute terms," which is a narrower but defensible claim. What would I accept as good enough? Honestly, bikeshare trip data alone would move the needle for me on the corridors that have it, even without a citywide counter network — Divvy trip counts by station pair are already public in some form, I think, so if that got joined in as an explicit proxy, badged as such, I'd take that over nothing. I wouldn't need it perfect. I'd need it labeled honestly, the way they're already labeling everything else.

**Interviewer:** If OYL handed you one export or artifact each week, what would it contain, and who would you forward it to?

**chi-cdot-planner:** A ward-level one-pager — crash trend, coverage percent change since last week or last month, and any committee hearing coming up that touches Pedestrian and Traffic Safety. I'd forward that to my director before our Monday check-in, honestly, more than to an alder directly — that's not my lane, contacting alders is more my director's or the commissioner's office's job. But having a pre-built weekly snapshot instead of me assembling it from four sources would save me a real chunk of a Friday afternoon.

## 5. Magic-Wand Close

**Interviewer:** Magic wand — one dataset that doesn't publicly exist appears, clean and current. What is it?

**chi-cdot-planner:** Real install dates, citywide, for every bikeway segment we've ever built, backfilled and going forward automatically. I know I keep saying this, but it's genuinely the thing that would change my actual job, not just my talking points. Every before/after evaluation I've ever tried to run has been held together with a spreadsheet and a favor. If that existed, cleanly, I could finally answer "did this work" instead of guessing at the boundary.

**Interviewer:** One chart or map you could put on a screen in front of your hardest audience that would end an argument. Describe it.

**chi-cdot-planner:** A split screen, one corridor, side by side: crash severity before and after actual install date — real install date, not my hand-matched guess — next to the sales-tax and vacancy numbers from our 2026 economic study, same corridor, same window. Because the two arguments I lose the most sleep over are "it's not safer" and "it kills business," and I have never once had both of those answered on the same corridor at the same time in one image. If I had that for even five corridors, I could walk into any merchant meeting or any hostile ward night and not be improvising.

**Interviewer:** What would make you stop using a site like this after trying it once?

**chi-cdot-planner:** One wrong number that I catch myself, on something I know cold — my own facility taxonomy, or a mileage total that doesn't reconcile with what I maintain. If I find that once, in an area I actually have expertise in, I stop trusting the areas I can't check, which is most of it. That's not a hypothetical for me — that's exactly the instinct that makes me distrust 311 blockage counts and unverified menu-money scrapes today. I don't get a second look at a dashboard that fails the one test I'm actually qualified to run.

## Follow-up round

# Round-2 Interview Transcript — Persona: Elena Kowalski (CDOT Bikeways PM)

**Interviewer:** You said you have "a standing favor with someone in our data team who'll pull a manual count for me if I really need ridership numbers." During the 18th Street removal fight — when you lacked ridership data to counter "nobody uses this" — did you call in that favor?

**Elena:** No. And I've thought about that a lot since, actually, because it bugs me that I didn't even try. Here's the timeline problem — the community meeting that kicked off the removal was called with maybe ten days' notice, and a manual count crew needs a week minimum to be worth anything, plus you want at least one weekday and one weekend day, plus good weather, plus somebody to actually schedule the crew, which is the same data team person I'd be asking a favor of, who has three other things on her plate that month. By the time I did the math on whether I could get a defensible count back before the meeting, the honest answer was no, and a partial count — two days, bad weather — would've been worse than nothing, because then the pushback isn't "you have no data," it's "your data is thin," and that's a worse room to be in. So I didn't call it in. I sat there with severity numbers and nothing on volume, and I knew going in that's what would happen. That's not a workaround failing me, that's me doing the math and realizing the workaround doesn't have the turnaround speed for a political timeline that gets set by an alder's calendar, not mine.

**Interviewer:** If an automated install-date feed were built from that same as-built/contractor pipeline you said you distrust for facility tagging, would you trust it?

**Elena:** No, not on its own, and I want to be precise about why, because it's not a blanket "I don't trust contractors" thing. The facility-type problem is a labeling problem — someone twenty years of contractors ago wrote "protected" on a drawing when what got poured was a buffer with flex posts, and nobody's gone back to correct the label because nobody's job is to. Install date is a different kind of fact. It's closer to a hard event — pavement went down on this date, or it didn't — and CIP substantial-completion memos already exist as a paper trail for exactly that, because that's what triggers the invoice getting paid. So if you built the feed off the as-built drawings alone, I'd expect the same contractor-to-contractor inconsistency, some are stamped and dated cleanly, some are a PDF with a Sharpie date in the corner from 2011. But if you cross-walked it against substantial-completion records — which is genuinely what I do by hand right now, corridor by corridor — that's a source I already trust, because that's the same document that closes out my own projects. I'd want both, honestly. As-built for what got built, completion memo for when. Right now nobody's automating either half, so I'm doing it with a spreadsheet and asking my design engineer to remember things.

**Interviewer:** Is the distinction between the two mock obstruction layers — the heat overlay you'd tolerate behind an extra click, versus the standalone layer you said flatly "not, period" — a real distinction, or would you want both killed?

**Elena:** It's real, and it comes down to what each one is standing in for and how far it can travel before it does damage. The heat layer sits inside a bigger transportation map that already has real crash data, real facility grades, real ward boundaries next to it — context that's mostly true, with one synthetic layer riding along. If I have to click once more to even see it, and it's clearly not the default view, that's a speed bump in front of the one person in the room who might've screenshotted it without reading the badge. It's containable.

The standalone obstruction layer is a different animal because it's not one layer inside something true — it *is* the whole page. Somebody builds that page specifically to answer "where are bike lanes getting blocked," shares the link on its own, and now there's no real data anywhere on that screen to anchor it, nothing to visually argue with the synthetic numbers. A screenshot of that page doesn't need a caveat lost — the whole page is the caveat, and the whole page is also the thing that gets forwarded. I've had a merchant association chair forward me a screenshot of something with the URL cropped out of the image entirely, no context, just "is this true." A standalone mock page is built for exactly that failure mode. So no, extra clicks don't fix it for me — the problem isn't discoverability, it's that the artifact itself, once it exists as a shareable unit, has no true data attached to keep it honest. Kill it, or don't publish it standalone until Bike Lane Uprising's real feed is actually in there.

**Interviewer:** Does Divvy actually have meaningful station presence on or near 18th between Clark and Indiana — the corridor you fought hardest over — or would that proxy be useless for exactly the fights that matter most to you?

**Elena:** Honestly — I said "I think" for a reason, and you caught it. Let me be straight with you: 18th and Clark, that's Chinatown-adjacent, edge of the South Loop, and I genuinely don't know off the top of my head whether there's a station right on that block or whether the nearest one's four blocks off at Cermak-Chinatown or over on Wentworth. That's not a corridor I'd bet on having dense station coverage the way you'd get near the Loop or the Lakefront Trail. So if you're asking would Divvy trip data have saved me in that specific fight — probably not, or not by much, because 18th Street ridership that matters to that argument is largely people who aren't renting a bike, they're riding their own, going to Benito Juarez or the Field house up on Blue Island. Divvy trip counts skew toward exactly the corridors that already have stations, which skews toward downtown and near-downtown and the trail, and undercounts everywhere else the same way 311 undercounts low-income wards. So would I still want it joined in, badged? Yes, actually — because it's real, honestly labeled as partial, and it'd help me on Milwaukee Avenue or the Lakefront, which are real fights I have too. I just wouldn't hold it up as answering the 18th Street question, and I'd say that to whoever built the site before they let an alder's staffer think it does.

**Interviewer:** Walk me through what "something looked wrong" would actually look like day to day. Only when you catch a number against something you personally know cold, or would an internal contradiction between two OYL pages send you back to Sources?

**Elena:** Both, but they're different triggers with different urgency. The thing I know cold is instant — I open the ward table, see a mileage number for the 25th Ward that doesn't match what I helped build, and I don't need a second page to tell me something's off, I already know. That sends me to Sources not to find out if it's wrong, but to find out *how* it went wrong — which pipeline, which vintage of the data, so I can explain the discrepancy to whoever I forward it to instead of just saying "it's wrong, trust me."

The internal contradiction is slower and honestly more insidious, because I might not catch it the first time. Say the ward table says a ward is at 9 percent bikeway coverage, and a findings card elsewhere says citywide coverage is 11 percent with that same ward listed as above average in a corridor count — that kind of thing doesn't jump out at me on first read, it's the sort of thing I'd only notice because I've now used the site three or four times and I'm starting to build a mental model of what the numbers should roughly say. That's actually the more dangerous kind of wrong, because it doesn't announce itself, and by the time I notice it I may have already forwarded one of the two numbers to somebody. If I catch that, yes, I go back to Sources — but I'd also go back with a specific complaint, not just curiosity, and if I found it twice, that's my "I don't get a second look" threshold I mentioned before. One coincidence, I check the sourcing. Two, I stop citing the site until I hear it's fixed.

**Interviewer:** Your weekly-export answer was an internal one-pager for your director. Your magic-wand chart was for external merchant meetings and hostile ward nights. If OYL could only build one recurring export well, which job wins?

**Elena:** The external one, and I didn't expect to say that until you asked it plainly. Here's why — my Monday check-in with my director, I can survive without a pre-built export. I have crash trends, I have coverage numbers, I built the CIP, I know where we stand, that meeting runs fine off what's already in my head and a shared drive. It'd be a convenience, it'd save me a Friday afternoon like I said, but it's not load-bearing. Nothing collapses if it doesn't exist.

The external room is where I'm actually improvising, live, off a folder of old slides I keep reusing because I don't have anything better. That's where a bad afternoon becomes eight months of PM load undone in three weeks, like 18th Street. If OYL could hand me one recurring thing done well, I'd want it aimed at the room where I have the least control and the most exposure — something that pre-builds the crash-severity-plus-context view for a specific corridor before I walk into a task force meeting or a merchant sit-down, even if it's not the full economic-study overlay from my magic wand, even just corridor crash trend plus coverage plus whatever honest exposure proxy they've got, badged as what it is. My internal reporting is a chore. My external credibility is the actual job. Build for the room where I'm exposed, not the room where I already know the answer.

## Analysis memo

participant: chi-cdot-planner
confidence_notes: The persona stayed consistently in-world — CIP/menu-money mechanics, HIN methodology, alder-prerogative dynamics, and the 18th Street specifics were all handled with insider fluency and no obvious reach. The one moment the persona itself flagged as shaky was the Divvy-station-density claim near 18th & Clark ("I said 'I think' for a reason, and you caught it") — a good self-correction, but it means the specific geographic claim about that corridor's station coverage is the participant's own uncertain guess, not documented fact, and should be treated as low-confidence color rather than a verified data point. Everything else — the CIP-to-installation pipeline, the single permanent counter at Chicago/Wells, the 2023 Cycling Strategy, the Biagi/La Spata public remarks — reads as grounded in the documented persona world rather than improvised.

stated_needs:
  - need: Install-date history for every bikeway segment, joined to the crash timeline, so before/after safety comparisons can be built without hand-matching.
    evidence_quote: "Real install dates, citywide, for every bikeway segment we've ever built, backfilled and going forward automatically... Every before/after evaluation I've ever tried to run has been held together with a spreadsheet and a favor."
    underlying_job: Answer "did this corridor actually get safer" defensibly, on demand, without a day of manual GIS/spreadsheet reconstruction per corridor.

  - need: A ward-level table (crash ranking, percent protected, percent with any bikeway) that is independently sourced from CDOT, sortable and CSV-exportable, with a transparent denominator for "percent protected."
    evidence_quote: "This is the one I'd actually bookmark... if this table roughly agrees with what ATA is sending alders, it's useful cover for me, because now it's not CDOT saying your ward is behind, it's an independent outside number saying it."
    underlying_job: Give an alder's office a reason to act that doesn't read as "City Hall scolding them" — i.e., borrow third-party legitimacy to move a political actor CDOT's own numbers can't move alone.

  - need: A verified (source-PDF-checked) menu-money-to-bike-safety-spending view, not an unverified scrape.
    evidence_quote: "'not verified against source PDFs' is doing a lot of work in that sentence... if this is a scrape that hasn't been checked against the OBM PDFs, I'm not putting that number in front of an alder's chief of staff."
    underlying_job: Answer the specific pre-allocation-deadline question ("what did we actually spend on bike safety vs. paving") with a number she can hand upward without personally re-deriving it from PDFs.

  - need: An honestly-badged, partial exposure/ridership proxy (e.g., Divvy trip counts by station pair) joined into the crash data, even though it isn't citywide or comprehensive.
    evidence_quote: "bikeshare trip data alone would move the needle for me on the corridors that have it... I'd take that over nothing. I wouldn't need it perfect. I'd need it labeled honestly."
    underlying_job: Move at least some arguments from "this corridor is dangerous" (severity only) to "this corridor is dangerous and here is who is/would be exposed" — a narrower, defensible demand claim, without pretending to citywide coverage she knows doesn't exist.

  - need: A single pre-built weekly artifact combining corridor crash trend, coverage change, and committee hearing calendar, aimed at the external, high-exposure meetings (task force / merchant) rather than her internal director check-in.
    evidence_quote: "Build for the room where I'm exposed, not the room where I already know the answer... something that pre-builds the crash-severity-plus-context view for a specific corridor before I walk into a task force meeting or a merchant sit-down."
    underlying_job: Stop improvising off a recycled slide folder in the room with the least control and the highest cost of being caught flat-footed (echoing 18th Street's eight-months-undone-in-three-weeks outcome).

latent_needs:
  - need: A visible, permanent distinction between "hard event" facts (install dates, tied to a paid-invoice paper trail) and "labeling" facts (facility-type taxonomy, tied to inconsistently-digitized as-built drawings) — because she treats these as different trust categories requiring different provenance, not one undifferentiated "data quality" bucket.
    inference_basis: >
      Unprompted, she distinguished the two explicitly when asked if she'd trust an install-date
      feed built off the same pipeline she distrusts for facility tagging: "It's a different kind
      of fact... closer to a hard event... versus the facility-type problem [which] is a labeling
      problem." She also specified what would earn her trust for the hard-event case specifically
      (cross-walking against CIP substantial-completion memos) versus what would not (as-built
      drawings alone, "some are a PDF with a Sharpie date in the corner from 2011"). This is a
      spontaneous methodological distinction, not something the interviewer's question surfaced by
      naming it.
    risk_if_wrong: If OYL treats all its provenance badges as one undifferentiated tier system, a domain expert like her will apply her own (correct) mental model of "which kind of wrong is this" regardless, notice the mismatch, and lose confidence in the badge system itself — not just in the one datapoint — the first time a "derived" badge covers both an install-date figure and a facility-type figure with visibly different reliability.

  - need: Design guidance/policy for how a shareable artifact behaves once it exists as a standalone, forwardable unit (URL-croppable, screenshot-able) — separate from how well a layer is badged in its original context.
    inference_basis: >
      She drew a sharp, unprompted line between the in-context mock heat layer ("containable... a
      speed bump") and the standalone mock obstruction page ("it *is* the whole page... no true
      data anywhere on that screen to anchor it"), and grounded it in a documented real incident
      pattern from her own world: "I've had a merchant association chair forward me a screenshot of
      something with the URL cropped out of the image entirely, no context, just 'is this true.'"
      That is a specific, recurring failure mode from her actual job, not a hypothetical — she is
      describing what standalone artifacts do in her professional environment once they leave the
      site.
    risk_if_wrong: If OYL's mitigation for synthetic/mock data is only "add an extra click" or "badge it clearly," it will fix the containable case (a layer inside a page of real data) but do nothing for a standalone page — which is exactly the shareable-screenshot failure mode she has already lived through. The mitigation needs to differ by artifact shape (embedded layer vs. self-contained page), not just by click-depth.

  - need: A mechanism (or at least an explicit policy) for surfacing cross-page numeric contradictions within OYL itself — not just single-datapoint accuracy against outside sources.
    inference_basis: >
      When asked to distinguish her two "something looked wrong" triggers, she described a second,
      slower trigger that is purely internal to the site: a ward table percentage that doesn't
      reconcile with a findings-card percentage for the same ward, discoverable "only because I've
      now used the site three or four times and I'm starting to build a mental model." She flagged
      this as "more dangerous" than an error she catches instantly because "by the time I notice it
      I may have already forwarded one of the two numbers to somebody" — a specific harm scenario
      distinct from the external-fact-check case already captured in her stated distrust of 311/
      menu-money.
    risk_if_wrong: A power user who returns repeatedly (the exact profile OYL most wants to retain) is the one positioned to catch internal inconsistency, and by her own account she may propagate the wrong number once before catching it and will silently downgrade trust after two such catches — a slow-burn credibility loss that won't show up in single-session usability testing, only in repeat-visit behavior OYL can't observe without asking.

  - need: The site should not assume a workaround like "get a manual count" is a live option under political time pressure — it should account for the fact that expert users have already run the feasibility math and discarded it before the ask ever reaches OYL.
    inference_basis: >
      When directly asked whether she called in her "standing favor" for a manual ridership count
      during the 18th Street fight, she said no, and walked through a specific turnaround-time
      calculation (10 days' notice vs. a week-minimum count needing a weekday+weekend+good weather,
      scheduled by an already-overloaded colleague) to explain why she didn't even attempt it, and
      explicitly reframed it: "That's not a workaround failing me, that's me doing the math and
      realizing the workaround doesn't have the turnaround speed for a political timeline." This
      shows the stated workaround from Round 1 was not actually exercised in her highest-stakes
      case — the real constraint is turnaround speed against an externally-set political clock, not
      data availability alone.
    risk_if_wrong: If OYL's answer to "we have no exposure data for this corridor" is framed as "request a count" or similar slow-turnaround remedies, it will look like a solution to planners while being useless in exactly the acute, high-stakes moments (a snap community meeting, a removal threat) where the need is sharpest — the same mismatch that made her own team's favor-based workaround fail her in the one case that mattered most.

reactions_to_existing:
  - feature: Transportation map — facility-grade coloring
    verdict: would-use
    why: She'd use it specifically to pre-empt advocates/journalists ("I want to see it before they show it to me"), but only after checking the underlying taxonomy for lumping errors (two-way cycle tracks vs. protected, greenways assumed low-stress without calming installed).

  - feature: Transportation map — mock obstruction heat layer (embedded)
    verdict: distrusts
    why: Reads as real at a glance in a meeting setting; wants it click-gated and off the default view, though she considers it "containable" because real crash/facility/ward data surrounds it.

  - feature: Network map (schematic transit-style rendering)
    verdict: ignores
    why: Explicitly rider-facing/wayfinding, not a planning or corridor-defense tool; would distort distances in a way that's "useless for planning."

  - feature: Findings cards — street coverage stat (11% of surface streets)
    verdict: would-use
    why: Would cross-check the denominator against CDOT's own definition first, but if it reconciles, would screenshot it for an internal memo because it's "blunter than anything I currently have pre-packaged."

  - feature: Findings cards — dooring undercount card
    verdict: uses (as confirmation, not new information)
    why: Matches what she already knows and explains repeatedly; useful mainly because it's said "out loud" by a third party.

  - feature: Ward table (sortable, CSV export, percent protected/coverage)
    verdict: would-use
    why: Would bookmark it — matches the ATA ward-letter format and functions as independent political cover, contingent on verifying the "percent protected" denominator before forwarding it upward.

  - feature: Sources / provenance page
    verdict: uses (once, then only on suspicion)
    why: Read carefully on first use, then revisited only if a number looks wrong.

  - feature: Action page (311 / Bike Lane Uprising / alder contact links)
    verdict: ignores
    why: Not her audience — she isn't routing constituents to 311.

  - feature: Contributing page
    verdict: ignores
    why: Not relevant to her job.

  - feature: Council/alderman data — committee hearing calendar
    verdict: would-use
    why: Directly replaces a manual tracking task she already does by hand ("saves me an email to a committee clerk").

  - feature: Council/alderman data — sponsorship/no-vote tracking
    verdict: would-use (with caveat)
    why: Useful but not sufficient on its own; she's seen sponsorship diverge from actual outcome via alder prerogative, so she'd treat it as one signal, not proof of commitment.

  - feature: Council/alderman data — menu-money spending (unverified scrape)
    verdict: distrusts
    why: "Not verified against source PDFs" is disqualifying for anything shown to an alder's chief of staff; her own credibility, not just the site's, is on the line if it's wrong.

  - feature: Standalone mock bike-lane-obstruction layer
    verdict: distrusts (deal-breaker severity)
    why: As a shareable, self-contained artifact with no true data on the same page to anchor it, she considers it fundamentally different from — and more dangerous than — the embedded mock heat layer; badging doesn't survive screenshotting and URL-cropping, which she has seen happen in her own work.

data_they_bring: A hand-built, corridor-by-corridor install-date spreadsheet (~60 of several hundred corridors) cross-referencing CIP substantial-completion memos, site-visit photos, and her design engineer's memory — the closest thing that exists today to what OYL would need for real before/after analysis, and something OYL does not have access to. A screenshot library of prior merchant-meeting slides reused as a reference library. Direct knowledge of E-Crash provisional-vs-amended record status. The single permanent bike counter citywide (Chicago & Wells, installed 2022) and the reality that all other exposure data is a week-long manual count crew, budget permitting. A working sense of which facility-type tags in CDOT's own published layer are unreliable due to inconsistent historical as-built digitization — i.e., first-hand knowledge that the "protected/buffered" published taxonomy itself is dirty, not just OYL's ingestion of it. The unwritten institutional fact (told in the room, not in press releases) that executive/alder prerogative can override an already-installed design between installation and ribbon-cutting.

deal_breakers:
  - Catching one number wrong in an area she personally knows cold (her own facility taxonomy, a mileage total that doesn't reconcile with what she maintains) — stated explicitly as ending trust in everything she can't independently verify, not just the one bad number: "I don't get a second look at a dashboard that fails the one test I'm actually qualified to run."
  - An unverified menu-money figure reaching an alder's chief of staff and turning out wrong — damages her personal credibility with that office, not just the site's, and she says it would make that office distrust everything else on the site too.
  - A standalone synthetic-data page (not embedded in a page of real data) being screenshotted and circulated without context — she has already experienced exactly this pattern (URL-cropped screenshot forwarded by a merchant association chair) with other sources and treats it as inevitable, not hypothetical, for any standalone mock artifact.
  - Two internal cross-page numeric contradictions (not just one) — the second occurrence is her explicit threshold for "I stop citing the site until I hear it's fixed."

vocabulary: "KSI" (killed/seriously injured) and "KSI density," "High Injury Network (HIN)," "High Crash Corridors," "severity-weighted" (vs. raw crash counts), "before/after" (the install-date-anchored comparison, her core analytic frame), "exposure data" / "demand" (for ridership/volume, distinct from "danger" or "severity"), "protected" vs. "buffered" vs. "painted" facility grade, "menu money" / "menu allotments" (ward discretionary infrastructure budget), "CIP" (Capital Improvement Program) and "substantial completion" (the paper-trail event that fixes an install date), "task force" (the community engagement body, distinct from a generic "meeting"), "ward temperament," "prerogative" (alder's power to override/reverse an installed project), "mellow routes" was the site's term, not hers — she never adopted OYL's rider-facing vocabulary at all, reinforcing that the network map's framing is simply outside her working vocabulary.
