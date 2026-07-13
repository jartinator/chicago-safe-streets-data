# Interview: chi-pro-advocate

## Round 1 transcript

**Interviewer:** Let's start with your role. Describe what you do, and walk me through the last decision you influenced — or tried to — about street safety. What did that actually involve, step by step?

**Reyna:** I'm the advocacy manager, basically the ward-liaison person, for a regional active-transportation nonprofit — think of us as the folks who send the ward letters. The last real fight was the citizen bike-lane-blockage ordinance back in February. It passed the Committee on Pedestrian and Traffic Safety — La Spata's committee — and I thought we had it. I'd sat in the gallery for that committee vote, I'd emailed testimony to three alders' chiefs of staff, and then it went to full Council and got wiped out, like 2-to-1 against. I remember standing outside Council chambers with our policy director, Marcus, both of us just — stunned, honestly, because everyone had told us committee passage was the hard part. That was the moment I learned the hard way: committee and full Council are not the same fight, and if you only track "did it pass committee," you will get blindsided. Now every legislative tracker I keep has two columns, not one.

More routine than that, though: every quarter I build the ward letters. Fifty of them, one per alderperson, each with current deaths and serious injuries by mode in their ward, framed against citywide trend — fatal crashes down 30 percent since 2021, but 72 percent of last year's fatalities involved speeding. I did the last batch in April for budget season, because that's when alders are thinking about menu money for the next fiscal year and you want your letter landing on a desk right when they're deciding whether protected bike lane resurfacing beats another round of alley repaving.

**Interviewer:** Who do you need to convince, and what does "convinced" look like for them?

**Reyna:** Two different audiences, honestly. There's the alderperson and their chief of staff — for them, convinced looks like a menu-money line item, or at minimum them showing up to co-sponsor something at committee. And then there's the room at a ward night — actual constituents, some of whom are furious that a bike lane took away street parking. For them, convinced looks like not walking out and calling their alderman's office the next morning to complain. Those two audiences want completely different things from the same number. The alderman's office wants something they can put in a press release. The community meeting wants something that doesn't feel like it's talking down to them or hiding something.

**Interviewer:** What information sources do you touch in a normal week for this work?

**Reyna:** The city's crash data portal — the Traffic Crashes dataset, I pull it via the Socrata query interface when I need something specific, or I go find whatever CDOT's Fall Traffic Crashes report says because that's the citation everyone recognizes. Ward Wise's menu-money map, when I need to check what an alderman actually spent versus what they promised at a community meeting. Bike Lane Uprising's dashboard, when I'm building the case that a particular corridor has a blockage problem. The City Clerk's Legistar system, God help me, to check hearing dates and bill status — it's clunky but it's the source of record. And a lot of texting other advocacy people — Better Streets folks, sometimes someone from Chi Hack Night — to sanity-check a number before I put it in front of an alderman's staff.

---

**Interviewer:** Tell me about the last time you needed a number, map, or chart about bike safety. Where did you go, what did you do with it, how long did it take?

**Reyna:** Two weeks ago. We had a ward night in the 15th Ward — Ald. Lopez's turf, the Archer Avenue fight — and I needed current KSI numbers for that ward specifically, not citywide, because if I show up with a citywide chart someone in that room is going to say "that's not my street." So I pulled the raw crash CSV from the city portal, filtered by the ward field, cross-referenced against the 2023 ward remap because the boundaries shifted and half my old saved queries were wrong, and built a one-page handout in about two and a half hours. That's actually fast for me — sometimes it's a full afternoon, especially if I have to double-check dooring numbers because I know those are undercounted and I don't want to say "there were only three dooring incidents this year" if I know it's really more like ten to fifteen unreported.

**Interviewer:** What have you built yourself — spreadsheets, saved searches, screenshots, FOIA requests, hand counts — because nothing gave it to you directly?

**Reyna:** Oh, the ward letter template itself is entirely homemade — it's a Google Sheet with a macro Marcus's predecessor built that pulls from a saved Socrata query and spits out fifty separate one-pagers, one per ward, with the alderman's name and district mail-merged in. I maintain a separate spreadsheet just tracking hearing dates by hand, because Legistar's calendar is not reliable for "is this actually happening this week" — I've shown up to City Hall for a hearing that got moved and nobody updated the page. I also keep a running doc of which alders have had bike lanes ripped out or stalled — Dowell and 18th Street is the big one on that list now — because that's the kind of thing that doesn't live in any dataset but comes up constantly in strategy meetings.

**Interviewer:** Tell me about a time data — or the lack of it — sank an argument you were making.

**Reyna:** The 18th Street thing, actually, was partly a data failure on our side. When Dowell started pushing to rip out the protected intersection, we scrambled to make the case that ridership on that corridor justified keeping it, and we had... nothing. No counter data, no bikeshare trip counts for that segment, nothing that showed usage. We had crash data, we had the design rationale from CDOT, but "how many people actually ride here" — we could not produce that number, and it let the removal argument stand unchallenged. I remember Marcus saying in the debrief, "we keep losing this fight because we can prove danger but we can't prove demand."

**Interviewer:** What data do you distrust, and what earned that distrust?

**Reyna:** 311. Full stop. Everybody in this world knows 311 bike-lane-blockage reports are basically decorative — CDOT has said publicly, repeatedly, that they use it for "aggregate hotspot identification," not enforcement. I've had constituents at ward nights ask me, "I called 311 six times about that same truck, why hasn't anything happened," and I have to explain that 311 isn't wired to any ticketing action. That's a genuinely demoralizing thing to say out loud to someone. It also means 311 volume is biased toward wards where people already know to call — so a low 311 count doesn't mean a safe corridor, it might just mean nobody there bothers calling anymore. I distrust it, but I still cite it sometimes, carefully, because it's the only thing available for some corridors.

---

**Interviewer:** I want to walk you through what a dashboard called On Your Left — OYL — actually has. It's independent, open-source, read-only — doesn't take reports itself, points people to 311 and Bike Lane Uprising instead. It's got two maps, a findings page, a ward table, a sources page, and so on. Let's go screen by screen. First, the transportation map — crash density, the bikeway network colored by facility grade, wards, cameras, and a mock obstruction layer, plus main-route overlays.

**Reyna:** Okay, the crash density and facility grade together, on one map — that's actually useful, that's the kind of overlay I'd screenshot for a one-pager if I could zoom to just my ward. I'd want to check the facility-grade categories match what CDOT itself calls things, because if I say "protected" and someone from CDOT engineering is in the room and their internal classification disagrees, I look sloppy. The camera layer — sure, fine, that's context. The mock obstruction heat, though — I want to be very clear about this, because it's a landmine. If I put something up that looks like Bike Lane Uprising data and it's actually synthetic, and someone in the audience happens to know Bike Lane Uprising — and in my rooms, someone always does, because Christina's org is well known here — I will get called out, publicly, for using fake data. That's not a small caveat for me, that's a "do not put this on a screen in front of an audience" flag, full stop, no matter how many times the badge says "mock."

**Interviewer:** Understood — hold that thought, we'll come back to it in the gap section. Next, the network map — this is the schematic transit-style map, 21 named routes each colored solid end to end, no safety data on that page at all.

**Reyna:** Honestly? I'd glance at it once and probably not come back. It's pretty, it's the kind of thing that's nice for a general-audience explainer post, but it has no crash data on it, which means it doesn't do anything for my actual job. My job is connecting infrastructure to danger and to money. A map that's just "here are the named corridors" without KSI numbers attached is a marketing map, not an advocacy tool. I'd use it maybe once, to orient a new intern who doesn't know the city's bike network yet, and then never open it again.

**Interviewer:** Findings page — curated cards, stat plus caveat plus deep link, things like KSI trend, protected share, street coverage, top corridors, hit-and-run, ward concentration, dooring undercount.

**Reyna:** Now this I like more, at least in concept. The dooring-undercount card especially — if it actually says out loud "official records only include reportable crashes," that's language I can use, because I already say that verbally at every hearing and having it written down somewhere citable saves me from being the only person in the room making that claim. The ward concentration card — I'd want to know exactly how it's computing "concentration," because if it's raw counts and not something like CDOT's High Injury Network weighting, severity-weighted over a few years, I'm going to get pushback from a CDOT engineer at a task force meeting who'll say "that's not how we define high-injury." I've had that exact argument before, at a Neighborhood Bike Network task force session for a different corridor, where an engineer took apart my citywide number because I hadn't weighted it the way CDOT does internally.

**Interviewer:** Table page — sortable ward rankings, CSV export, plus percent-protected and percent-streets-with-bikeways columns.

**Reyna:** This is the one I'd actually build my ward letters from, if the numbers check out. CSV export is the whole ballgame for me — I don't need a beautiful chart, I need something I can pull into my mail-merge sheet. But — and this is the thing that would kill it for me in about five minutes — the first thing I'd do is take three or four wards I already know cold from our own letters, like the 15th and the 3rd, and compare OYL's numbers against mine. If even one ward is off — and it will probably be off, because our letters use a slightly different date cutoff or count serious injuries differently than whatever the site's using — I now have to explain the discrepancy to my own team before I trust any of it. One unexplained mismatch and I stop using the table for anything I'd put in front of an alderman, and I go back to building it by hand. That's not me being precious, that's just what happens the first time your own boss asks "why does the website say 4 and our letter says 6."

**Interviewer:** Council and alderman accountability data — Legistar-based legislation records with an automated topic tag, contested roll-call votes, sponsorship counts, and separately, aldermen contacts and committee hearings from the City Clerk.

**Reyna:** Okay, this is where I get skeptical fast, because of the 18th Street thing and the February ordinance. If this shows me a single "status" field on a bill, that's actively dangerous for my work — I lived through committee-pass, full-Council-fail, and if a staffer or a volunteer looks at OYL and sees "passed" because it passed committee, and then repeats that to a reporter or at a community meeting, that's a real credibility problem for us, not just an abstraction. I need it to distinguish committee stage from full Council, and I need to see who voted no, because "who's the alder there, and did they vote against it" is basically the only currency I have when I'm trying to get an alderman to move. Sponsorship counts I'll use, cautiously, because I already know most safety stuff passes by voice vote — so sponsorship really is often all we get, and I appreciate that the caveat matches what I already tell people. The hearing dates and contacts, if they're accurate and current — that alone might replace my hand-kept spreadsheet, honestly, that's a real time-saver, assuming it doesn't go stale the way Legistar itself sometimes does.

**Interviewer:** Menu-money spending — a proxy layer, described as a Ward Wise extract, not verified against source PDFs.

**Reyna:** I already use Ward Wise directly for this, so an unverified extract of a thing I already go to the source for isn't adding much — unless it's joined to something Ward Wise doesn't do well, like tying a menu-money line to a specific crash corridor or a specific bikeway segment. If it's just "here's spending by ward" with a "not verified against source PDFs" disclaimer, I'll probably still go to Ward Wise directly, because at least I know exactly what they scraped and from where.

**Interviewer:** And the badge system generally — real, proxy, mock, crowdsourced, derived, no-data-yet — plus the stated limitations: no ridership normalization, mock obstructions, dooring undercount, no install dates on the bikeway network.

**Reyna:** The badges themselves, I actually appreciate as a concept — it's the right instinct, because half my job at a hearing is pre-empting the "where's this number from" question. But a badge only works if I can recite the provenance out loud without opening a laptop, and "derived" alone doesn't tell me enough — derived how? The ward safety index being described as "not absolute risk, just relative" — I'd want to interrogate that hard before I ever used it in a hearing, because a single opaque danger score is exactly the kind of thing that gets torn apart by a CDOT engineer who knows the real High Injury Network methodology weights by severity over a rolling window. If I can't explain the weighting out loud, I won't use the number, full stop — I'd rather cite a weaker number I understand than a stronger one I'd fumble defending. No install dates on the bikeway network is a real gap for me too — when I'm arguing that an alderman under-delivered on a promise, "when was this actually built" matters as much as "does it exist," and I don't have another good source for that either, so that's a limitation I'd just live with, not a dealbreaker.

---

**Interviewer:** Now the scenario. You're prepping to brief an alderman's office before a menu-money deadline — say, budget season, the kind of moment you described earlier. You open OYL. What do you look for first, and where does it fail you?

**Reyna:** First thing I do is find my ward filter, if there is one, and go straight for the ward table — I want the KSI numbers and the coverage percentage for that one ward, side by side, because that's the two-fact combo that makes an alderman's staffer sit up: "your ward has X serious injuries and only Y percent of your streets have any bike infrastructure." Where it fails me is the moment I try to cross-reference it against last quarter's actual spending on bike safety specifically — because from what you've described, the menu-money layer is a raw Ward Wise extract, not broken out into "safety-relevant" spending versus repaving or lighting or whatever else menu money covers. What I actually need in that meeting is "the alderman promised X, spent Y on bike-relevant projects, and here's the KSI trend since." Without that promised-versus-delivered slice, I still have to go build that comparison by hand in a spreadsheet, which is exactly what I do now. So it saves me the crash-data half of the prep and none of the money half.

**Interviewer:** Of everything OYL does not have, what single absence costs you most?

**Reyna:** No ridership data, easily. It's the exact gap that cost us the 18th Street fight. Every time an alderman's office pushes back with "nobody actually uses this lane," I have nothing quantitative to counter with except crash counts, and crash counts alone let them say "well if nobody's riding there, of course there aren't many crashes, so it's not a priority." I need something — bikeshare trip counts, even counter data at a handful of locations — that lets me say "here's how many people are actually on this street." Without it I'm always half a step behind that argument.

**Interviewer:** If OYL handed you one export or artifact every single week, what would it contain and who would you forward it to?

**Reyna:** A one-page-per-ward PDF, auto-generated, with current KSI by mode, the coverage percentage, top crash corridor in that ward, and any hearing or menu-money deadline coming up in the next 30 days for that ward — basically my quarterly ward letter, but weekly and without me building the mail merge by hand. I'd forward it straight to whichever alder's chief of staff I'm currently working, and probably CC Marcus. That would save me actual days of work a quarter, if I trusted the numbers — which, again, hinges entirely on that first cross-check against our own letters coming back clean.

**Interviewer:** The site refuses to normalize by ridership because it has no volume data, and it says so. Does that caveat change how you'd use it? What would you accept as good-enough exposure data?

**Reyna:** It doesn't change whether I'd use the crash counts — I already use raw crash counts today, so I'm not worse off. But it means I can never use it to answer the "is this corridor actually dangerous per rider, or just busy" question, which is precisely the question that comes up in every merchant-objection meeting and every aldermanic-prerogative fight. Good enough for me wouldn't need to be perfect — divvy or bikeshare trip-start/end counts by station, or even just Chicago Department of Transportation's own counter-program numbers if they publish anything, would be miles better than nothing. I don't need Strava-level precision. I need something I can point to and say "ridership on this block is not zero," because that's usually the whole argument.

---

**Interviewer:** Magic wand — one dataset that doesn't publicly exist appears, clean and current. What is it?

**Reyna:** Verified menu-money spending, broken out by category, tied to ward, with a promised-versus-actually-completed field, refreshed close to real time instead of scraped from quarterly PDFs. That's the dataset that would change my job the most, because it's the one thing every alderman's office can be held to that isn't about crash trends at all — it's about whether they did what they said they'd do with their own discretionary money. Ward Wise built their whole project around this exact gap and it's still not really solved.

**Interviewer:** One chart or map you could put on a screen in front of your hardest audience that ends an argument. Describe it.

**Reyna:** Picture the 15th Ward, just that ward, one map. Crash markers sized by severity, dooring flagged separately with the undercount caveat printed right on the legend, overlaid on the bikeway network colored by facility grade — protected versus painted versus nothing — and a small callout box in the corner that says "X percent of surface streets here have any bike infrastructure, citywide average is Y." No danger index, no single score, just the layered facts side by side so a room full of skeptical residents and an aldermanic staffer can look at the same map and see: here's where people got hurt, here's what protection exists, here's how this ward stacks up. That's the picture that ends the "why do we need this bike lane" argument, because it doesn't ask anyone to trust a formula — they can see it.

**Interviewer:** What would make you stop using a site like this after trying it once?

**Reyna:** One bad number in front of an audience. If I pull up the ward table at a community meeting, someone in the room — and there's always someone, some retired engineer or a Bike Lane Uprising volunteer or just a very online resident — says "that number's wrong, I know because I FOIA'd this myself," and I can't explain the discrepancy on the spot, I will never open that tab again in public. I've had that exact kind of moment happen with other tools before, some well-meaning civic-tech project that showed up, demoed at a Hack Night, everyone got excited, and then six months later nobody maintained it and the numbers were two years stale and I'd already been burned once trusting it. I don't have room in my week to be the one re-verifying somebody else's dashboard before every hearing — if I have to do that anyway, I'll just keep building it myself the way I already do.

## Follow-up round

**Note on the follow-up items received**

I read `chi-pro-advocate.md`, `_shared-rules.md`, and `02-data-inventory.md` as instructed, and I'm ready to continue the interview in character as Reyna. But the four "follow-up questions" I was handed aren't round-2 interview probes — they're study-orchestration questions (drafting the analysis memo, checking mandatory-probe coverage, sequencing the next persona, deciding whether to run round 2 now). Per `docs/research/user-needs/01-lead-researcher.md`, that entire checklist — the structured memo with `stated_needs`/`latent_needs`/`reactions_to_existing`/etc., protocol compliance checks, and persona sequencing — is explicitly the **Lead Researcher's** job, not the **Persona Agent's**. I'm the persona agent: my only mandate under `_shared-rules.md` is to answer interview questions *as Reyna*, staying inside what she'd plausibly know.

Reyna has no in-world knowledge of "round 2 probes," "the lead-researcher protocol," "mandatory probes," "the next persona in the study," or an "analysis memo" — she doesn't know she's a simulated informant in a UX study at all. Forcing her to answer those four items in character would violate shared-rule 2 ("stay inside your knowledge... never suddenly acquire expertise your character wouldn't have") and would produce exactly the kind of fan-fiction the protocol warns against. So rather than fabricate an in-character non-answer, I'm flagging the mismatch instead of pretending to resolve it as Reyna.

What I can confirm from my own read of the docs, staying in my actual lane (persona agent, not orchestrator):

- No actual round-2 interview questions were included in this handoff — items 1-4 are all meta/process questions addressed to whoever runs the study loop, not to Reyna.
- If real round-2 probes are drafted (i.e., substantive follow-ups on her episodes — the 18th Street ridership gap, the February ordinance committee/floor split, the ward-table cross-check, the menu-money promised-vs-delivered ask), send those and I'll answer them in character with the same episodic/resistant craft as round 1.
- Decisions about whether round 1 already satisfies the two mandatory probes, whether to draft the `stated_needs`/`latent_needs` memo now, and whether to advance to the next persona (`chi-ward-office`, etc.) belong with the Lead Researcher role/human running the study, per `01-lead-researcher.md` — not with me, since I don't have visibility into what other persona interviews have or haven't been run, or into the study's tracking state.

No files were edited. Relevant paths reviewed: `/home/user/chicago-safe-streets-data/docs/research/user-needs/personas/chi-pro-advocate.md`, `/home/user/chicago-safe-streets-data/docs/research/user-needs/personas/_shared-rules.md`, `/home/user/chicago-safe-streets-data/docs/research/user-needs/02-data-inventory.md`, `/home/user/chicago-safe-streets-data/docs/research/user-needs/01-lead-researcher.md`.

## Analysis memo

```
participant: chi-pro-advocate
confidence_notes: >
  Interview stayed inside Reyna's documented world throughout — ward letters,
  menu money, Legistar, 311's no-enforcement policy, the Feb 2026 ordinance,
  the 2025 18th Street removal — and her reasoning tracked the persona brief's
  "how you think" bullets closely (committee-vs-floor, "one mismatch kills
  it," the mock-data landmine), which is reassuring but means some of that
  specificity should be read as the brief's texture restated, not new
  measurement. The ridership/demand gap recurs three separate times (stated
  need, magic-wand-adjacent scenario answer, deal-breaker discussion) with
  consistent framing — a good signal of a stable underlying need. The
  weakest, most speculative moment is her list of "good-enough exposure
  data" (Divvy trip counts, CDOT counter-program) — plausible for her role
  but reaches slightly past what the brief documents about her (which stops
  at "can prove danger, can't prove demand") into naming specific data
  sources; treat that specific list as lower-confidence texture rather than
  a verified want.

  The persona agent's "follow-up round" response declined to answer the
  four items sent to it, correctly identifying them as lead-researcher
  orchestration questions rather than round-2 interview probes. No new
  substantive data resulted from that round; this memo is built entirely
  from the round-1 transcript, which the persona agent flagged as already
  containing two rounds' worth of probing (open context, workarounds,
  stimulus walkthrough, gap probing, magic wand) in a single continuous
  session.

stated_needs:
  - need: Two-stage legislative status (committee vs. full Council), with roll-call no-votes visible
    evidence_quote: "I need it to distinguish committee stage from full Council, and I need to see who voted no, because 'who's the alder there, and did they vote against it' is basically the only currency I have when I'm trying to get an alderman to move."
    underlying_job: Avoid repeating the February-ordinance mistake — trusting a single "passed" signal that collapses committee and floor outcomes — and identify exactly which alder to pressure next.

  - need: Ward-level KSI + infrastructure-coverage percentage, filterable to one ward, side by side
    evidence_quote: "I want the KSI numbers and the coverage percentage for that one ward, side by side, because that's the two-fact combo that makes an alderman's staffer sit up."
    underlying_job: Build the single strongest fact-pair for a specific alderman's office in one glance, replacing a hand-built ward letter.

  - need: CSV export of ward rankings she can pull into her existing mail-merge sheet
    evidence_quote: "CSV export is the whole ballgame for me — I don't need a beautiful chart, I need something I can pull into my mail-merge sheet."
    underlying_job: Feed her homemade Google Sheet macro that mail-merges fifty ward letters, without rebuilding her production pipeline around a new tool.

  - need: Mock/synthetic data made unmistakable, not just badge-labeled, when it resembles a known real dataset (Bike Lane Uprising)
    evidence_quote: "If I put something up that looks like Bike Lane Uprising data and it's actually synthetic... that's a 'do not put this on a screen in front of an audience' flag, full stop, no matter how many times the badge says 'mock.'"
    underlying_job: Protect her personal and organizational credibility in rooms where a Bike Lane Uprising-literate attendee is statistically near-certain to be present.

  - need: Facility-grade classification that matches CDOT's own internal terminology
    evidence_quote: "I'd want to check the facility-grade categories match what CDOT itself calls things, because if I say 'protected' and someone from CDOT engineering is in the room and their internal classification disagrees, I look sloppy."
    underlying_job: Use the same vocabulary as the technical authority in the room so her framing can't be dismissed as amateur.

  - need: Transparent, recitable methodology behind any "ward concentration" or safety-index score (ideally severity-weighted like CDOT's High Injury Network)
    evidence_quote: "If it's raw counts and not something like CDOT's High Injury Network weighting... I'm going to get pushback from a CDOT engineer... I've had that exact argument before."
    underlying_job: Never bring a number to a task-force meeting she can't defend against an engineer who knows the real methodology.

  - need: Auto-generated weekly per-ward one-pager (KSI by mode, coverage %, top corridor, upcoming hearing/menu-money deadlines) she can forward directly
    evidence_quote: "A one-page-per-ward PDF, auto-generated... basically my quarterly ward letter, but weekly and without me building the mail merge by hand."
    underlying_job: Eliminate the manual, quarterly, stale-within-weeks ward-letter production cycle that is currently her team's single biggest recurring time cost.

  - need: Menu-money spending broken into safety-relevant category, tied to a specific corridor/bikeway segment, with a promised-vs-delivered field
    evidence_quote: "What I actually need in that meeting is 'the alderman promised X, spent Y on bike-relevant projects, and here's the KSI trend since.' Without that promised-versus-delivered slice, I still have to go build that comparison by hand."
    underlying_job: Hold a specific alderman accountable to their own stated commitment using their own discretionary spending, in the exact meeting where that leverage matters (budget season).

  - need: Some non-zero ridership/exposure proxy (bikeshare trip counts, corridor counter-program data), even if imprecise
    evidence_quote: "I need something I can point to and say 'ridership on this block is not zero,' because that's usually the whole argument."
    underlying_job: Counter the "nobody rides here, so it's not a priority" objection that directly cost her the 18th Street fight.

latent_needs:
  - need: A documented, checkable methodology (date cutoffs, injury-severity definitions) attached to every ward number, not just an accurate number
    inference_basis: >
      She described a specific verification ritual — comparing OYL's numbers
      against 3-4 wards she already knows cold from her own letters — and
      predicted the mismatch will come not from OYL being "wrong" but from a
      different date cutoff or injury-severity definition than her letters
      use. She said one unexplained mismatch, discoverable by her own boss,
      ends her use of the table entirely.
    risk_if_wrong: >
      If OYL's team optimizes only for numeric accuracy and not for
      surfacing *why* two legitimate methodologies disagree, she will hit an
      explainable-but-undocumented mismatch, be unable to resolve it on the
      spot in front of her team, and permanently discard the ward table —
      even though the underlying numbers may have been defensible.

  - need: Provenance/caveat text that travels with exported artifacts (PDF, CSV), not just displayed on the web page
    inference_basis: >
      She said a badge "only works if I can recite the provenance out loud
      without opening a laptop," and separately asked for the dooring
      undercount caveat to be "written down somewhere citable" so she isn't
      the only person in the room saying it. Her actual working artifacts are
      printed one-pagers and PDFs handed out at ward nights and school-gate-
      style meetings, not a browser tab she has open live.
    risk_if_wrong: >
      If caveats (dooring undercount, 311 bias, mock-vs-real, index
      methodology) exist only as web-page decoration and are stripped out
      when she exports to CSV or requests the weekly PDF, her downstream
      ward letters will present numbers as more precise/certain than OYL
      itself claims — reintroducing exactly the defensibility gap she is
      most anxious about.

  - need: Ward-boundary version handling (2023 remap) built into any ward-filtered query or export
    inference_basis: >
      She described having to manually cross-reference against the 2023
      ward remap because "the boundaries shifted and half my old saved
      queries were wrong" — an unprompted, specific workaround for a data
      versioning problem, not a hypothetical.
    risk_if_wrong: >
      If OYL's ward filter doesn't account for the remap (or doesn't say
      which boundary vintage it uses), she will get silently misassigned
      historical crashes for a ward, reproducing the exact error she
      currently catches by hand — and won't necessarily catch it a second
      time if she trusts the tool to have handled it.

  - need: A visible freshness/maintenance signal (last-updated date, active-maintenance indicator) surfaced prominently, not buried
    inference_basis: >
      Unprompted, she volunteered a story about "some well-meaning
      civic-tech project" that demoed at Hack Night, generated excitement,
      then went unmaintained for six months with numbers two years stale —
      and named this as the reason she'd stop using a new tool after one bad
      experience, before any accuracy problem even occurs.
    risk_if_wrong: >
      If OYL is accurate but doesn't visibly signal its own currency/
      maintenance status, she pattern-matches it to the dead civic-tech
      project from memory and never gives it a second try, independent of
      actual data quality.

  - need: Reliable, change-aware hearing/deadline data (not a mirror of Legistar's current unreliability)
    inference_basis: >
      She keeps a hand-maintained spreadsheet of hearing dates specifically
      because "Legistar's calendar is not reliable for 'is this actually
      happening this week'" and described showing up to City Hall for a
      hearing that had been moved with no page update.
    risk_if_wrong: >
      If OYL's hearing-date feature is built as a simple Legistar pass-
      through without a staleness check or independent verification signal,
      it inherits Legistar's exact failure mode, and she has no reason to
      retire her hand-kept spreadsheet even if the feature exists.

  - need: Audience-specific framings/exports of the same underlying number (press-release-ready vs. plain-language-for-residents)
    inference_basis: >
      She explicitly distinguished two audiences who "want completely
      different things from the same number" — an alderman's office that
      wants press-release material, and a ward-night room that wants
      language that doesn't feel like it's talking down to them or hiding
      something — implying a single generic export would still require her
      to manually rewrite it for whichever room she's walking into.
    risk_if_wrong: >
      If OYL ships one canonical artifact per ward with one register of
      language, she still does the audience-adaptation work by hand for
      every ward night, capturing only part of the time she currently
      spends building materials.

reactions_to_existing:
  - feature: Transportation map (crash density + facility-grade bikeway overlay)
    verdict: would-use
    why: "Screenshot for a one-pager if I could zoom to just my ward" — but conditional on facility-grade taxonomy matching CDOT's internal terms, or she risks looking sloppy in front of an engineer.

  - feature: Mock obstruction layer (on the transportation map)
    verdict: distrusts
    why: Explicitly named as a public-credibility landmine because it visually resembles real Bike Lane Uprising data; badge labeling alone does not neutralize the risk in her rooms, where a Bike Lane Uprising-literate attendee is near-certain to be present.

  - feature: Schematic network map (21 named routes, no safety data)
    verdict: ignores
    why: "A marketing map, not an advocacy tool" — no KSI data means it doesn't connect infrastructure to danger or money, the only two things her job runs on. Would use once for onboarding a new intern, then never again.

  - feature: Findings page — dooring undercount card
    verdict: would-use
    why: Gives her citable, written-down language for a caveat she already states verbally at every hearing, reducing her exposure as "the only person in the room making that claim."

  - feature: Findings page — ward concentration card
    verdict: distrusts (pending methodology disclosure)
    why: Will misread as CDOT's High Injury Network methodology if not explicitly severity-weighted; she has been publicly corrected on exactly this point before by a CDOT engineer at a task force session.

  - feature: Ward table (sortable rankings, CSV export, % protected, % streets with bikeways)
    verdict: would-use, conditionally
    why: Best fit to her actual production workflow (mail-merge feed) — but gated entirely on a clean cross-check against 3-4 wards she already knows from her own letters; one unexplained mismatch and she discards it for anything alderman-facing.

  - feature: Council/legislation records with single automated "status" field
    verdict: distrusts
    why: Named as "actively dangerous" — collapsing committee-pass and full-Council-fail into one status field is precisely the mistake that blindsided her org in February 2026 and could propagate false "passed" claims through her network.

  - feature: Roll-call votes, sponsorship counts, hearing dates/contacts (Legistar-derived)
    verdict: would-use
    why: Roll-call no-votes are "basically the only currency" she has with alders; sponsorship counts usable cautiously since she already tells people most safety items pass by voice vote; hearing dates/contacts could replace her hand-kept spreadsheet outright if accurate and not stale.

  - feature: Menu-money layer (unverified Ward Wise extract)
    verdict: ignores
    why: Duplicates a source she already goes to directly (Ward Wise) with no added trust; would become useful only if joined to a specific crash corridor or bikeway segment, which it currently is not.

  - feature: Badge system (real/proxy/mock/crowdsourced/derived/no-data-yet) + stated limitations
    verdict: would-use, with reservations
    why: Approves of the concept (pre-empts the "where's this number from" question she fields constantly) but "derived" alone is insufficient — she needs to be able to recite the provenance out loud without a laptop. No-install-dates gap is accepted as a limitation, not a dealbreaker.

  - feature: Ward safety index ("not absolute risk, just relative")
    verdict: distrusts
    why: An opaque single score is "exactly the kind of thing that gets torn apart" by a CDOT engineer familiar with real High Injury Network weighting; she will not use a number she can't defend, even if it's the stronger number.

data_they_bring: >
  City crash-data portal (Socrata query interface) and CDOT's Fall Traffic
  Crashes report as the recognized citation; Ward Wise's menu-money map;
  Bike Lane Uprising's dashboard for corridor blockage cases; the City
  Clerk's Legistar system as source-of-record for hearings/bill status,
  despite its unreliability; an informal cross-advocate texting network
  (Better Streets, Chi Hack Night) used to sanity-check numbers before they
  reach an alderman's staff; a homemade Google Sheet with a mail-merge macro
  that generates fifty ward letters from a saved Socrata query; a
  hand-maintained hearing-date spreadsheet built specifically because
  Legistar's own calendar is unreliable; a hand-kept running list of alders
  who have had bike lanes ripped out or stalled (not captured in any
  dataset); manual knowledge of the 2023 ward remap needed to correct stale
  saved queries.

deal_breakers: >
  (1) Any single ward number she can't explain when it's challenged live —
  by a resident, a CDOT engineer, or a Bike Lane Uprising volunteer —
  especially in front of her own boss or a hostile public room; one
  unexplained mismatch against her own ward letters ends her use of that
  data source, full stop.
  (2) A mock/synthetic layer that could be mistaken for real Bike Lane
  Uprising data on a shared screen — badge labeling alone does not clear
  this bar for her.
  (3) A single collapsed "status" field on legislation that hides the
  committee-vs-full-Council distinction — named as "actively dangerous"
  given the February 2026 ordinance's committee-pass/floor-fail split.
  (4) An opaque risk/danger index she cannot recite and defend the
  weighting of out loud against a CDOT engineer.
  (5) A tool that pattern-matches to the "demo-then-die" civic-tech
  lifecycle she's been burned by before — no visible signal of ongoing
  maintenance reads as a reason to distrust it pre-emptively, before any
  accuracy issue even surfaces.

vocabulary: >
  ward, alder / alderperson, chief of staff, menu money, aldermanic
  prerogative, KSI / "deaths and serious injuries," testimony, the
  committee (Committee on Pedestrian and Traffic Safety), full Council,
  roll-call vote, voice vote, CDOT, "the portal" (city crash-data portal),
  Vision Zero, high-crash corridor / High Injury Network, "our letter"
  (the ward letter), turnout, "who's the alder there?", ward night, dooring,
  KSI trend, protected / painted / no infrastructure, coverage percentage,
  promised-versus-delivered, "prove danger but can't prove demand,"
  citywide vs. ward-specific framing, aldermanic-prerogative fight,
  merchant-objection meeting.
```
