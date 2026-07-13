# Interview: dk-kpi-strategist (Søren Lindqvist)

## Round 1 transcript

**Interviewer:** Thanks for making time. Can you describe your role, and walk me through the last decision you influenced — or tried to — about street safety?

**Søren Lindqvist:** Of course. I should say first — I'm not Chicago. I spent nine years inside Copenhagen's mobility department building the Cykelregnskab, the Bicycle Account, and now I do this for a living: I get flown in by a city, or a delegation comes to us, and I help them figure out what to measure and how to say it out loud so a mayor will act on it. The last real one — March, I think — a mid-sized German city, I won't use the actual name, sent three planners and a press officer to Copenhagen for what we call a masterclass. Two days. The press officer's whole problem was this: her city had just spent four years building forty kilometers of protected track, genuinely good work, and nobody outside the department knew it existed. No press picked it up. I asked her the question I always ask first: who promised what number, by when, and where is that written down? She didn't have an answer. There was no target. So I walked her through how we structure the Account — you pick, say, five KPIs, you attach a number and a year to each one, you publish on a fixed date every two years so journalists build it into their calendar, and critically you report satisfaction, not just kilometers built, because kilometers built is an input, satisfaction is the outcome a voter can feel. She left with a one-page draft of a "mini-regnskab" to pitch her own council. I don't know if it survived contact with her budget officer, honestly — that's usually where these die.

**Interviewer:** Who do you need to convince in that kind of situation, and what does "convinced" look like for them?

**Søren:** Two audiences, always. The politician — in Copenhagen that's the technical-and-environment mayor, in these visiting delegations it's whoever holds the transport portfolio — and the press, because the press is how you reach the politician's own voters and put pressure back on them. Convinced for the politician means a number they can stand next to at a podium without a civil servant whispering a correction in their ear. Convinced for the press means a headline sentence that doesn't need three follow-up questions — "satisfaction with track width rose to 80%, hitting our 2025 target" is a sentence. "The dashboard shows several relevant metrics trending in different directions" is not a sentence, it's an apology. I sat through an internal review once — 2019, I think — where a junior analyst presented eleven charts to explain why modal share had plateaued. Eleven. The department head, Birgitte, stopped her at chart four and said, "give me the one chart I take to the borgmester tomorrow." That's the whole job in one sentence, really.

**Interviewer:** What information sources do you touch in a normal week for this kind of work?

**Søren:** The Bicycle Account itself when it's fresh — though it's biennial, so most weeks I'm working from the last published edition, not new numbers. SWOV's fact sheets for anything Dutch, because they're the centralized, trusted crash authority — no Dutch advocate I respect uses anything else for crash counts. Fietsbalans scores when I'm doing cross-city comparison work, because it's a named, defensible methodology, not just "we ranked cities." Copenhagenize Index, though I'll be honest with you — I have real ambivalence about it. It moves mayors, which is useful, but half the criteria are qualitative judgment calls by people I know personally, and I've watched a city's ranking swing eight places on essentially the same infrastructure because someone on the jury visited in the rain. I use it because it works, not because I fully trust it. And email, constantly — half my week is answering "can you send me the slide with the satisfaction chart again" from planners in cities I visited two years ago.

**Interviewer:** Tell me about the last time you needed a number, map, or chart about bike safety and where you went for it.

**Søren:** Two months ago — I was prepping the Copenhagen half of a joint presentation with a Utrecht colleague for a Nordic-Benelux mobility forum. I needed the current satisfaction-with-parking figure and the 2025 target side by side, plus the trend since 2016. I did not go hunting for it — I have the last three Bicycle Account PDFs saved locally, and I keep a personal spreadsheet, honestly just three columns — year, metric, value — that I've maintained since about 2015 because I got tired of re-opening 80-page PDFs to find one number. That took me maybe ten minutes, because the number was already in my own file. If it hadn't been, I'd have gone to the PDF, and that's a slower search — the Account isn't always indexed the way I want, and older editions used slightly different question wording on the survey, which matters enormously and which most people miss.

**Interviewer:** What have you built yourself because nothing gave it to you directly?

**Søren:** That spreadsheet I mentioned is the main one. I also keep — this sounds trivial but it isn't — a running slide deck of "before and after" photographs of specific intersections, because a photograph does more work in a room than any statistic. And I keep a private list, not published anywhere, of which cities' rankings I trust versus which I think are gamed — which is really a workaround for the fact that no single benchmarking body is fully independent of the cities that fund the study tours.

**Interviewer:** Tell me about a time data — or the lack of it — sank an argument you were making.

**Søren:** The delegation city I mentioned — the German one. Their press officer wanted to argue "we built more protected track than any comparable city in the region." I asked, compared to whom, using what boundary for "comparable," and by what mileage definition — because in my experience "protected" gets stretched to include painted lanes with a flexpost every thirty meters, which nobody in Copenhagen would call protected. She didn't have a source that would survive a journalist calling a rival city's press office for a counter-quote. The claim died in the room. That's the danger of an unaudited number — it doesn't fail when you say it, it fails three days later when someone checks.

**Interviewer:** What data do you distrust, and what earned that distrust?

**Søren:** Self-reported crowdsourced hazard counts without routing to an authority — I think of our own Fietsersbond Meldpunt system, which works because every report goes to a specific municipal office with a resolution status attached. A pin on a map with no accountable owner behind it is just noise with coordinates; it tells you where people are annoyed, not where the danger is. And I'm wary of any ranking — including Copenhagenize, which I use — where I can't see the raw sub-scores. If you can't show me the number under the number, I assume someone rounded in their own favor.

**Interviewer:** Let's look at what this Chicago project — "On Your Left," OYL — actually offers. It's an independent, open-source, read-only dashboard on bike-lane obstructions, infrastructure, and cyclist crashes, drillable ward to corridor to intersection. It takes no reports itself — it points people to 311 and Bike Lane Uprising. Every layer is badged real, proxy, mock, crowdsourced, derived, or no-data-yet. Raw counts are not normalized by ridership. Dooring is flagged as structurally undercounted. Let's go screen by screen. First, the transportation map — crash density, bikeway network colored by facility grade, wards, cameras, mock obstruction heat, main-route overlays.

**Søren:** This is the closest thing to something I'd actually open. A layered map with facility grade is the right instinct — CROW thinking, more or less, even if nobody there would use that word. I'd use it the way I use our own network maps: zoom to a corridor, see what grade of infrastructure sits under a crash cluster. What I'd check before I trusted it in front of an audience — the grading definitions. Is "protected" here the CROW-adjacent sense, physically separated, or is it America's looser usage where a row of plastic posts counts? I've been burned by that exact ambiguity before, and I'd ask before I'd put a screenshot on a slide.

**Interviewer:** The network map — a schematic transit-style diagram, 21 named main routes each in a single solid color, interchange nodes, an opt-in quality border, toggles for connecting infrastructure and crowdsourced "mellow routes." No safety data lives on this page.

**Søren:** Here's my honest misreading, and I'll tell you exactly what I did with it: my first instinct looking at "transit-style, 21 named routes, single solid color end to end" was that this was your equivalent of a modal-share map — that the lines represented ridership volume, the way a metro map's line thickness sometimes does. It took me a moment to realize it's schematic topology, not flow. That's a real trap for someone from my world — we're trained to read a colored network line as "this much traffic moves here," and if this map doesn't mean that, it should say so more loudly, because I'd have walked away from a quick glance thinking I'd found exposure data, which you've told me doesn't exist. Once I understood it's just "this route exists, here's its quality," it's fine, useful even for a network-cohesion argument — but separating safety data off this page entirely is the wrong call by my instincts. In Copenhagen we never draw the network without the danger sitting right on top of it; you cannot let politicians see the pretty finished network without also seeing where it's still lethal, or they conclude the job is done.

**Interviewer:** Findings — curated cards: KSI trend, protected share, street coverage, top corridors, hit-and-run, ward concentration, dooring undercount, each with a stat, a caveat, and a deep link to the map.

**Søren:** Now we're closer to what I actually need. This is the shape of a Bicycle Account page, more or less — a stat with a caveat attached, that's disciplined, I respect that. What's missing, and I'd say this immediately in the room: there's no target attached to any of these. "KSI trend" going up or down means nothing politically until someone says "we will get this to X by 2028" and a named official's name is under that promise. Without that, this is a well-produced press release, not an instrument — my persona file's words exactly, and it's the first thing I'd flag to whoever built this. I'd also want a satisfaction figure sitting among these cards, and there isn't one — nothing here asks a rider how safe they feel. That's the whole other half of a Bicycle Account, and it's just absent.

**Interviewer:** Table — ward rankings, sortable, with CSV export, including percent protected and percent of streets with bikeways.

**Søren:** This I'd actually export. Genuinely — a sortable ward table with a CSV button is the one screen so far that maps directly onto something I do weekly: I'd pull this into my own spreadsheet the same way I maintain my Bicycle Account numbers, sort by percent protected, and hand it to a visiting delegation as "here is your rough Fietsbalans-style comparison, city built it themselves." That's real value. What I'd check first: is "percent protected" measuring the same thing ward to ward, or does one ward's planner have looser standards for what counts as protected than another's? Ward-level self-reporting bias is exactly the kind of thing that undermines an otherwise good ranking.

**Interviewer:** Sources — a full provenance catalog with tier badges and stated limitations.

**Søren:** Good instinct, and frankly ahead of some cities I've advised. This is the page I'd read most carefully before I did anything with the rest of the site, because it tells me whether I can trust the crash numbers the way I trust SWOV. If the crash layer here is centrally sourced and consistently defined the way SWOV's is, I can use it in front of a hostile audience. If it's assembled ad hoc from several agencies with gaps stitched together, I say so out loud before anyone asks, because it will get asked.

**Interviewer:** Action — links to 311, Bike Lane Uprising, alderman contacts.

**Søren:** Fine, mechanically, but this isn't for me. I don't file complaints, I don't organize residents street by street — that's not my role in this world. I'd skip this page entirely in a normal week.

**Interviewer:** Contributing — how to swap data sources, fill stubs, fork for another city.

**Søren:** Also not mine. I'm not a developer. I'd never open this page unless someone on my team specifically asked me to look at what's forkable, and even then I'd hand it to them, not read the technical detail myself.

**Interviewer:** Now the council and alderman accountability data — Legistar-sourced bike-safety legislation, sponsorship counts, recorded no-votes, ward office contacts, upcoming Pedestrian and Traffic Safety committee hearings, and menu-money bike-safety spend per ward from a Chi Hack Night extract, not verified against source PDFs.

**Søren:** This is fascinating to me, honestly, mostly because it doesn't exist in my world in this form — we don't have fifty aldermen each with a discretionary menu budget. Fifty of them, each with something close to a personal veto over their own patch of street? That's extraordinary to someone from a unitary city council system; I'd want that explained twice before I used it. If I map it onto what I know — the alderman is something like your borough mayor, and sponsorship counts are something like tracking who actually shows up to vote for cycling infrastructure, which we don't need in Copenhagen because the political level there is more centralized. I can see the appeal: it's accountability data, and BYPAD does something adjacent by scoring named officials' engagement. But I'd flag the "not verified against source PDFs" line immediately — that's the kind of caveat that kills a claim in the room the moment someone asks "did you check the actual budget document," and the honest answer is no, this Chi Hack Night volunteer extract didn't either. I would not put an unverified menu-money figure in front of a hostile audience. That one I'd set aside entirely until someone verifies it against the PDFs.

**Interviewer:** And the badge system itself — real, proxy, mock, crowdsourced, derived, no-data-yet — plus the stated limitations: no ridership normalization, mock obstructions, dooring undercount, no bikeway install dates.

**Søren:** The badge system is the single best thing on this whole site, and I'd say that without qualification. It's more provenance discipline than most European dashboards I've seen, and it's exactly what my persona brief would call the missing piece in most crowdsourced hazard tools — you always need to know where the speculative data sits relative to the verified layer. "Mock" obstructions labeled honestly as synthetic — fine, I understand why you'd stub that in before a data-sharing conversation lands, but I want to be blunt: I would never use the mock obstruction layer for anything. Not in a slide, not in a private conversation, not even to gesture at a pattern. A synthetic layer with no floor under it is worse than an empty page, because someone in the audience might mistake the shape of it for a real pattern, and then I'm the one explaining afterward that it was invented. The dooring-undercount flag, though — that I respect. We have almost the identical problem with "reportable" crash thresholds in Danish data, so seeing it named explicitly here rather than buried in a footnote tells me whoever wrote this site understands what it means to under-report.

**Interviewer:** Let's move to gap probing, with a scenario for you: you're advising a city on setting network targets. You open OYL. What do you look for first, and where does it fail you?

**Søren:** First thing I look for is a target — a number tied to a year, printed somewhere on the Findings page, ideally right next to the current KSI trend. It isn't there. That's the immediate failure, and it's the one I'd name in the first five minutes of a call with whoever runs this. Second, I look for a satisfaction or perceived-safety time series, something I could show a city as "here's what riders themselves say, not just what the crash report says" — and there's nothing. Not one survey question anywhere on this site. Third, I'd look for a publication cadence — does this refresh on a rhythm journalists can set their calendar to, or is it just continuously live? It says weekly, human-reviewed. Weekly is too fast to be a political moment and not fast enough to be real-time; it's an odd middle ground. A city doesn't build anticipation around a weekly refresh. Copenhagen's Account works precisely because it's rare enough to be an event.

**Interviewer:** Of everything OYL does not have, what single absence costs you most?

**Søren:** The satisfaction survey, without question. Everything else on this site measures harm or infrastructure. Nothing measures how a rider actually feels on the street, and that is the number that moved Copenhagen's budget more than the crash count ever did. A dashboard that can't hear from riders is, in my language, half-blind — it can tell you someone was hurt, it cannot tell you whether people feel safe enough to keep cycling, which is the actual policy question underneath all of this.

**Interviewer:** If OYL handed you one export or artifact each week, what would it contain, and who would you forward it to?

**Søren:** Genuinely, I wouldn't want it weekly — I'd want it timed to something. But if forced to answer inside your premise: one number, one trend line, one map thumbnail. The number would be citywide KSI year to date against last year. The trend line, protected-mile growth over the same window. The thumbnail, the ward table sorted worst-to-best on percent protected. I'd forward that to precisely the people I forward the Bicycle Account highlights to when I'm consulting — the client city's press officer and whichever planner owns the target, if one existed. Not a general list. Data goes to the person accountable for the number, always.

**Interviewer:** The site refuses to normalize by ridership because it has no volume data. Does that caveat change how you'd use it, and what would you accept as good-enough exposure data?

**Søren:** It changes everything, actually, and I'd tell whoever built this exactly that. A raw crash count without a rider-volume denominator is not a safety metric to me — it's an activity log. If a corridor has more crashes only because it has ten times more cyclists on it than a quiet ward corridor, and you rank them the same way, you've told your audience the popular route is more dangerous when it may be the safer one per rider. I built that mistake once myself, early on, comparing two Copenhagen districts on raw count before I had counter data, and a colleague caught it in review before it went to print — I still remember how close that was to an embarrassing publication. As for good-enough: I don't need Strava-grade precision. Even installing three or four fixed, visible counters at your highest-volume corridors and multiplying up would beat nothing, the way our first two counters did in 2009 before we had a citywide count program. Bikeshare trip counts, if Chicago has a public bikeshare system, would also be a reasonable proxy — imperfect, but declared and consistent, which is the standard I actually hold data to. I would not wait for perfect ridership data before doing something with it; I'd publish the caveat and use a rough proxy loudly labeled as such, the way this site already labels its mock layer.

**Interviewer:** Magic wand — one dataset that doesn't publicly exist appears, clean and current. What is it?

**Søren:** The satisfaction survey, run citywide, same standardized questions every year, cross-tabbed by ward. Not a one-off poll — a repeating instrument with the same wording each time, because the wording is what lets you compare 2024 to 2026 to 2028. That's the one thing that would let this site do what our Account does: turn a crash count into a political promise with a face on it.

**Interviewer:** One chart or map you could put in front of your hardest audience that ends an argument. Describe it.

**Søren:** Two lines on one small chart, nothing more. Line one: percent of surface-street miles with protected infrastructure, rising, year over year. Line two: KSI crashes per — and this is the part that doesn't exist yet here — per estimated rider-kilometer, falling, year over year. Progress up, danger down, on the same axis, in front of the same audience. That's the chart. If you can only show harm and never show progress alongside it, a politician sees only blame, and blame makes politicians defensive, not generous with budget. I've said this in every masterclass I've given: you must be able to show improvement as visibly as you show damage, or the room shuts down.

**Interviewer:** And last — what would make you stop using a site like this after trying it once?

**Søren:** If the mock obstruction layer weren't clearly and permanently labeled, and I got burned once using it as if it were real — I'd never trust the rest of the site again, even the parts that earned it. Or if I came back after the promised weekly refresh and found the same numbers three weeks running with no note explaining why — that tells me nobody's actually maintaining it, and a stale instrument is worse than no instrument, because at least an absence doesn't pretend to be current. One credibility failure like that, and I go back to building my own spreadsheet from the sources page, the way I always have.

## Follow-up round

**Interviewer:** You mentioned keeping "a private list, not published anywhere, of which cities' rankings I trust versus which I think are gamed." Walk me through how a city actually moves from one column to the other — what's the concrete test you apply? And would you want OYL's Sources page to let you attach that same kind of personal trust annotation to individual layers, or is that judgment something you'd never delegate to a site?

**Søren:** The test is simple and a little unfair: I ask for the raw sub-scores behind the headline rank, and I time how long it takes them to send it. A city that answers within a week with the actual spreadsheet — separated infrastructure kilometers, counter locations, survey N — moves into the trusted column, because they clearly produce that number for themselves already and the public version is just a translation of it. A city that sends back a polished one-pager restating the same rank in different words, or worse, goes quiet — that's the gamed column. Utrecht moved into my trusted column in maybe 2018 because their transport office sent me their internal counter methodology unprompted, before I'd even asked properly. A city I won't name stayed in the other column for three years because every time I asked "what's under the 'quality of cycling culture' score," I got a paragraph about vision, not a number.

As for OYL — no, I wouldn't want a trust annotation field on the Sources page, and I'd resist it if someone proposed it to me. That judgment is personal, it's built on who returned my emails, and the moment you formalize it into a badge on a public site, it becomes a claim the site is making about a city's honesty, which is a legal and political can of worms nobody building an open dashboard wants. What I *would* use the Sources page for is exactly what it already seems to do — show me the tier and the caveat — and I'd build my private judgment on top of that myself, the way I always have. Keep the badge factual, "real/proxy/mock." Leave the whispering to me.

**Interviewer:** You said your first instinct on the network map was to read the single-color route lines as ridership volume before realizing it's schematic topology only. If OYL kept the map as-is but changed only the legend or line treatment, what specific visual change would have stopped you misreading it — and does that same instinct make you misread the "quality border" toggle too, or is that one unambiguous?

**Søren:** The simplest fix costs nothing — put the word "SCHEMATIC" or "topology, not volume" directly in the legend box, the way a metro map sometimes prints "not to scale" in the corner. I'd also want uniform line *weight* enforced visually, because right now a solid, confident, wide line reads as "important" to someone trained on flow diagrams, even without meaning to. If every route were drawn at the same stroke width with a small note — "line = route exists, not traffic volume" — I'd never have made the mistake. It's a one-line fix, not a redesign.

The quality border is different, and honestly less dangerous. Once I understood the base map wasn't showing volume, a border toggle marked "quality" read unambiguously as a grading overlay — it behaves the way a highlight layer behaves in every GIS tool I've used, on or off, binary. My mistake was entirely about the base layer pretending to be a flow map. The border toggle never triggered that instinct because it's presented as an addition, not as the primary geometry.

**Interviewer:** You said you've "been burned by that exact ambiguity before" on protected meaning physically separated versus a painted lane with an occasional flexpost. Tell me about that specific time.

**Søren:** 2021, a joint report with a French advocacy group comparing Paris and Copenhagen protected-lane growth for a EuroVelo funding pitch. I used their submitted figure — forty-some kilometers of "protégé" that year — without asking what the underlying standard was, because I was rushed and I trusted the partner organization. A Danish journalist covering the pitch, someone who actually rides in Paris, called it out in print two days later: half of that mileage was a painted lane with a post every twenty-five, thirty meters, which nobody riding it would call protected in a crash. It didn't kill the funding, but it cost me a correction and, worse, it cost me credibility with that journalist for the next two stories I pitched her — she fact-checked everything I sent her afterward, which is its own kind of tax.

It changed something concrete, yes. I now ask for the *cross-section*, not the adjective — literally, "send me a photo or a diagram of the barrier type at three random points," before I use anyone's protected-mileage figure in print or on a slide. It's not a trust exercise anymore, it's a documentation request, and I make it before the meeting, not during it.

**Interviewer:** You said you'd forward your weekly export only to "the client city's press officer and whichever planner owns the target, if one existed." OYL has no named Chicago official who owns a target the way your Copenhagen contacts do. Who, realistically in Chicago's structure, would you consider the accountable owner for a number like citywide KSI — and does that absence change whether producing this export is worth it at all?

**Søren:** From what little I understand of your structure, I'd guess the Commissioner of CDOT is the closest equivalent to Birgitte in my old department — the civil servant whose name would actually be attached to a target if one existed. But that's a guess, and I'd say so out loud in the room, because in Copenhagen the target-owner is unambiguous and here it sounds diffuse — fifty aldermen with menu money, a commissioner, a mayor's office, and apparently a Pedestrian and Traffic Safety committee that hears things but I don't know if it owns anything. That diffusion is itself the finding, frankly.

Does the absence make the export worthless? Not worthless — but it changes what I'd do with it. Without a named owner, I wouldn't forward it as an accountability document, I'd forward it as a diagnostic — "here is what a target-owner would need to say yes or no to, if Chicago had one." That's actually a useful pitch document for whoever is trying to get CDOT's commissioner to adopt something like a Bicycle Account. It's just not yet the artifact I described — a promise going back to the person who made it.

**Interviewer:** You floated Divvy trip data as a possible ridership proxy. Would you actually use it the way you used your first two fixed counters, or is bikeshare ridership too skewed toward tourists and short trips?

**Søren:** I'd use it, but loudly labeled, the way I said I'd use anything imperfect. It's not the same as a fixed counter — a counter catches every cyclist regardless of bike ownership, Divvy only catches people who chose that specific system, which skews toward exactly what you said: tourists, short commute hops, people without their own bike nearby. In Copenhagen that would be like estimating our modal share from bike-share dock swipes alone — you'd wildly undercount the ordinary commuter riding their own bicycle, who's the majority of our traffic. But undercounting consistently is still usable if you say what it's undercounting. I'd take Divvy trip density as a *floor*, not a true denominator — "at minimum this many rides happened here" — and I'd say explicitly in the caption that private-bike commuters aren't in it. That's a declared proxy, which meets my bar. What I would not do is silently present KSI-per-Divvy-trip as if it were KSI-per-rider-kilometer. That's the same sin as the flexpost lane — a real number wearing the wrong label.

**Interviewer:** Given your zero-tolerance stance on the mock obstruction layer, would you want it removed from the map view entirely rather than toggled? And has a "lose trust in the whole instrument" collapse actually happened to you before?

**Søren:** Honestly, yes — I'd rather it didn't live on the *same map surface* at all, even off by default. Put it on a separate "preview / synthetic data" page entirely, something a user has to deliberately navigate to, not a layer sitting one click away from the real crash data in the same interface. A toggle implies parity — it tells the eye "these are both legitimate layers of this map, pick which you want." A separate page tells the eye "this is a different kind of thing." I understand why a small team stubs in mock data before a real feed lands — I'm not naive about how these projects get built — but the interface should make the seam obvious, not just labeled.

And yes, the collapse has happened to me, with Copenhagenize, more than once actually — not permanently, since I still cite it, but there was a year, 2017 I think, when a city I'd recommended it to used its ranking in a grant application and a rival city's consultant picked apart the jury's methodology in a public comment period, and for about six months I stopped putting Copenhagenize numbers in front of hostile audiences at all, only friendly ones. I came back to it because nothing better replaced it, not because my trust fully returned. That's the pattern — one bad exposure doesn't kill a source outright, it just moves it from "cite freely" to "cite only where I control the room," and it rarely moves back all the way.

## Analysis memo

participant: dk-kpi-strategist

confidence_notes: The persona stayed in-world well throughout — he correctly
flagged his own uncertainty when mapping Chicago's diffuse governance (CDOT
commissioner, fifty aldermen, mayor's office, Pedestrian and Traffic Safety
committee) onto Copenhagen's centralized target-owner model rather than
inventing a confident answer, which is the right behavior per ground rule 6.
The one place the simulation felt slightly thin: his answers on Divvy as a
ridership proxy and on fixed-counter deployment are plausible extrapolations
from his stated methodology (declared, consistent, labeled) rather than
things anchored in the documented evidence base, since his evidence file
doesn't mention bikeshare or counter-siting decisions specifically — treat
those as lower-confidence than his Bicycle Account and Copenhagenize material,
which tracks his evidence file closely (targets, satisfaction trend, jury
methodology controversy, cadence argument). His remarks on OYL's Chicago-
specific screens (council/alderman accountability) were appropriately hedged
as an outsider's reading rather than expert judgment.

stated_needs:
  - need: A stated numeric target with a deadline attached to every headline safety statistic.
    evidence_quote: "'KSI trend' going up or down means nothing politically until someone says 'we will get this to X by 2028' and a named official's name is under that promise. Without that, this is a well-produced press release, not an instrument."
    underlying_job: Convert a measurement into a political commodity — something a politician can be held to and a journalist can turn into a one-sentence headline, not just a fact a department knows.

  - need: A citywide, standardized, repeating rider-perceived-safety/satisfaction survey, cross-tabbed by ward, reported alongside crash data.
    evidence_quote: "The satisfaction survey, run citywide, same standardized questions every year, cross-tabbed by ward... That's the one thing that would let this site do what our Account does: turn a crash count into a political promise with a face on it."
    underlying_job: Give politicians and press an outcome measure that "a voter can feel," distinct from harm counts, so budget arguments aren't limited to blame.

  - need: Explicit, load-bearing definitions for ambiguous terms like "protected" (physically separated vs. paint-and-flexpost) before any figure is used publicly.
    evidence_quote: "I'd ask before I'd put a screenshot on a slide... 'protected' gets stretched to include painted lanes with a flexpost every thirty meters, which nobody in Copenhagen would call protected."
    underlying_job: Protect his own professional credibility — a figure that can't survive a journalist's follow-up call to a rival city costs him the argument and, per his 2021 Paris story, costs him a source's trust for months afterward.

  - need: A visible publication cadence / "annual moment," not continuous weekly refresh.
    evidence_quote: "A city doesn't build anticipation around a weekly refresh. Copenhagen's Account works precisely because it's rare enough to be an event."
    underlying_job: Manufacture a recurring press/political moment that journalists and officials build into their calendars, rather than data that's perpetually available and therefore never newsworthy.

  - need: Full sub-score/raw-data access behind any ranking or aggregate figure he might cite (e.g., ward "percent protected"), not just the headline number.
    evidence_quote: "If you can't show me the number under the number, I assume someone rounded in their own favor." / "is 'percent protected' measuring the same thing ward to ward... Ward-level self-reporting bias is exactly the kind of thing that undermines an otherwise good ranking."
    underlying_job: Perform due diligence before staking his reputation on a number in front of a hostile audience.

  - need: A ridership/exposure denominator — or an explicitly declared, consistent proxy for one — before treating crash counts as a comparative safety metric.
    evidence_quote: "A raw crash count without a rider-volume denominator is not a safety metric to me — it's an activity log... I built that mistake once myself... a colleague caught it in review before it went to print."
    underlying_job: Avoid publishing an inverted safety conclusion (calling the busier, statistically safer corridor "more dangerous") that would embarrass him professionally.

  - need: Permanent, structurally unmissable separation of synthetic/mock data from real data — not just a toggle or label on the same map surface.
    evidence_quote: "I'd rather it didn't live on the same map surface at all, even off by default... Put it on a separate 'preview / synthetic data' page entirely... A toggle implies parity."
    underlying_job: Eliminate the possibility of ever being caught having presented invented data as real, which for him is a categorical, not a matter-of-degree, credibility risk.

latent_needs:
  - need: A single "headline chart" template pairing one progress metric against one danger metric on a shared axis/timeframe, distinct from the multi-card Findings layout OYL currently offers.
    inference_basis: Unprompted, he described a department head stopping an 11-chart internal review at chart four to demand "the one chart I take to the borgmester tomorrow," then separately, when asked for his single most persuasive artifact, spontaneously designed a specific two-line chart (percent protected rising vs. KSI-per-rider-km falling) rather than pointing to any existing OYL screen. Both a documented-world anecdote and an unprompted construction converge on the same unmet artifact.
    risk_if_wrong: If OYL assumes the multi-card Findings page already satisfies this need, it may never build the single combined progress-vs-harm chart he's describing, leaving the strongest persuasion-audience use case (the "end an argument" chart) permanently unserved even though the underlying data for both halves may already exist on the site.

  - need: A named accountable-owner field/mechanism attached to metrics, independent of whether Chicago's governance structure actually has one yet.
    inference_basis: He would only forward his weekly export "to the client city's press officer and whichever planner owns the target, if one existed" and, when told no such Chicago owner exists, reclassified the entire artifact from "accountability document" to "diagnostic/pitch document" — a downgrade in what the same data can do, driven entirely by the absence of a name attached to it.
    risk_if_wrong: If OYL treats "who owns this number" as out of scope (a Chicago governance question, not a dashboard feature), it forfeits the ability to ever function as the accountability instrument this persona's entire professional practice is built around — the site would remain permanently in his lower "diagnostic" tier rather than his "instrument" tier, no matter how good the underlying data gets.

  - need: A visible cross-section/definition disclosure (e.g., a photo or diagram of barrier type) attached to "protected" mileage claims, not just a text caveat.
    inference_basis: His concrete 2021 workaround for the exact ambiguity OYL's map raised is to demand "a photo or a diagram of the barrier type at three random points" before using anyone's protected-mileage figure — a documentation request he now makes routinely, before the meeting, as a direct consequence of a past public correction.
    risk_if_wrong: If OYL only fixes the ambiguity with a glossary-style text caveat, an expert user primed by past professional harm may still distrust or refuse to cite the protected-share figures, since his established remedy for this specific failure mode is visual/documentary evidence, not a definition in prose.

  - need: Route/network diagrams must visually encode "this is topology, not flow" at the base-layer level (uniform line weight + explicit legend language), not rely on users inferring it from a caveat elsewhere on the page.
    inference_basis: He is a domain expert who nonetheless demonstrably misread the network map on first exposure — "my first instinct... was that this was your equivalent of a modal-share map" — precisely because it uses transit-diagram conventions (solid colored lines, transit-style rendering) that, in his trained domain, encode volume. He also specified the exact minimal fix (uniform stroke width + "topology, not volume" in the legend) unprompted.
    risk_if_wrong: If OYL considers this "handled" by the general badge/caveat system, an expert audience trained on flow-diagram conventions will keep momentarily mistaking route existence for route volume, and — per his own account — may walk away from a quick glance having "found exposure data" that doesn't exist, then repeat that misreading in front of a client before self-correcting.

  - need: Declared, labeled proxy metrics (e.g., bikeshare trip density as an exposure floor) are acceptable and wanted now, rather than waiting for OYL to acquire ideal ridership data before shipping any ridership-normalized view.
    inference_basis: Twice, unprompted, he rejected the implicit choice of "wait for perfect data" — describing his own 2009 practice of multiplying up from three or four fixed counters before Copenhagen had a citywide count program, and explicitly stating "I would not wait for perfect ridership data before doing something with it; I'd publish the caveat and use a rough proxy loudly labeled as such."
    risk_if_wrong: If OYL's team reads "no ridership normalization" as a reason to keep raw counts as the only option until true volume data arrives, they forfeit a request this persona made twice independently: a labeled, imperfect proxy (Divvy trip density as a floor, not a denominator) would already clear his usability bar and materially change how he'd present crash data today.

reactions_to_existing:
  - feature: Transportation map (crash density, bikeway facility grade, wards, cameras, mock obstruction heat, main-route overlays)
    verdict: would-use
    why: Matches his own network-map workflow (zoom to corridor, check infrastructure grade against a crash cluster), but he'd verify the "protected" grading definition against CROW-adjacent physical-separation standards before citing it publicly.

  - feature: Network map (schematic transit-style route diagram, no safety data)
    verdict: misreads
    why: Read the single-color route lines as a ridership/flow encoding on first exposure, consistent with transit-diagram conventions in his domain; also structurally objects to safety data being absent from this page at all, calling it "the wrong call by my instincts."

  - feature: Findings cards (KSI trend, protected share, corridors, hit-and-run, ward concentration, dooring undercount)
    verdict: uses
    why: Matches the "stat plus caveat" discipline of the Bicycle Account format he already trusts, but flags the absence of any target and any satisfaction/perceived-safety figure as first-order gaps he'd name immediately.

  - feature: Ward ranking table with CSV export (percent protected, percent streets with bikeways)
    verdict: would-use
    why: Directly maps onto his existing weekly practice of exporting into his personal three-column spreadsheet; the one existing screen he describes as something he'd "actually export" and hand to a delegation as a rough Fietsbalans-style comparison — contingent on resolving ward-to-ward measurement consistency.

  - feature: Sources / provenance catalog (tier badges, stated limitations)
    verdict: would-use
    why: Treats it as the page that determines whether he can trust the rest of the site, analogous to how he checks whether a crash source is centrally defined like SWOV before using it in front of a hostile audience.

  - feature: Action page (311, Bike Lane Uprising, alderman contact links)
    verdict: ignores
    why: Out of role — "I don't file complaints, I don't organize residents street by street"; would skip in a normal week.

  - feature: Contributing page (fork/swap data sources, fill stubs)
    verdict: ignores
    why: Not a developer; would delegate to a technical colleague rather than read it himself.

  - feature: Council/alderman accountability data (Legistar legislation, sponsorship, no-votes, menu-money spend)
    verdict: distrusts
    why: Structurally interesting to him as an accountability mechanism he doesn't have an equivalent of, but the "not verified against source PDFs" caveat on menu-money spend is an immediate disqualifier — "I would not put an unverified menu-money figure in front of a hostile audience."

  - feature: Badge system (real/proxy/mock/crowdsourced/derived/no-data-yet) and stated limitations (no ridership normalization, dooring undercount, etc.)
    verdict: uses
    why: Calls it "the single best thing on this whole site... more provenance discipline than most European dashboards I've seen"; explicitly praised the dooring-undercount flag as matching Denmark's own "reportable crash threshold" problem.

  - feature: Mock obstruction layer specifically
    verdict: distrusts
    why: Zero-tolerance stance regardless of labeling quality — "I would never use the mock obstruction layer for anything... A synthetic layer with no floor under it is worse than an empty page." Wants it moved off the primary map surface entirely, not just toggled off by default.

data_they_bring: A durable personal three-column (year/metric/value) spreadsheet built from Bicycle Account PDFs since 2015, used as his actual working reference rather than the primary source itself; a running "before/after" intersection photo deck used as a persuasion artifact more effective than any statistic; a private, unpublished trust ledger of which cities' benchmark rankings he believes versus which he thinks are gamed, tested by how fast and how raw a city's response is when he asks for sub-scores; a habit of demanding physical cross-section documentation (photo/diagram of barrier type at three points) before citing any "protected" mileage figure, adopted after a specific 2021 public correction; SWOV fact sheets as his standard for what a centralized, trusted crash authority looks like; Fietsbalans as his standard for a named, defensible cross-city comparison methodology; awareness of health-economics/cost-benefit framing for cycling investment (per his persona's known vocabulary, not directly evidenced in this transcript).

deal_breakers: (1) A false positive from the mock/synthetic layer — being burned once using it as if it were real would permanently destroy his trust in the entire site, including the parts that had earned it. (2) A stale "weekly refresh" that shows unchanged numbers for three consecutive weeks with no explanation — reads as an unmaintained instrument, which he considers worse than no instrument at all, and would send him back to building his own spreadsheet from the Sources page. (3) An unverified figure (e.g., the menu-money spend, flagged as not checked against source PDFs) being presented as usable — anything he can't defend against a journalist's counter-check, he refuses to touch, having been burned this way once already with the Paris protected-mileage figure.

vocabulary: bicycle account / "mini-regnskab", KPI, target (number + year + named owner), satisfaction survey, "the political level," press moment / headline sentence, cadence / "annual moment," protected vs. painted-with-flexpost (cross-section, not adjective), rider-kilometer / exposure denominator, floor (for a declared undercounting proxy, e.g. Divvy as a floor not a denominator), sub-scores / "the number under the number," instrument vs. press release, half-blind (a dashboard that can't hear from riders), borgmester / political portfolio-holder, accountable owner.
