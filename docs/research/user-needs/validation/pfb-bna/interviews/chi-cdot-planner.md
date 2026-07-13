# Interview: chi-cdot-planner (PFB/BNA validation)

# Interview Transcript — Persona: Elena Kowalski (CDOT Bikeways PM)

## 1. Context Re-anchor

**Interviewer:** Quick re-anchor before I show you anything. Same role as before — but this time, walk me through the last time you needed to characterize the *quality* of the bike network, not crashes on it. What triggered it, and what did you actually do?

**chi-cdot-planner:** That's a real distinction and I'm glad you're asking it that way, because it's a different muscle. Crashes I can pull from the portal in ten minutes. Quality — meaning is the network actually low-stress, not just "has paint" — that one's harder, and the last time was maybe six weeks ago. The Cycling Strategy set an 80% low-stress target citywide, and the Commissioner's office wanted a mid-cycle gut check ahead of a budget hearing: are we tracking toward it. We don't have a formal stress methodology internally — nothing that scores a segment for speed, lane count, parking, intersection exposure the way, say, a proper level-of-traffic-stress model would. What we have is our own facility taxonomy — protected, buffered, painted, greenway, sharrow — and an informal rule of thumb my team uses where protected and greenway count as "low-stress," everything else doesn't. I built that estimate by hand, exporting our GIS layer, tagging it against that rule, and it took the better part of two days because I also had to eyeball a chunk of greenways to check they actually had traffic calming installed and weren't just a street sign. I handed the Commissioner's office a single number — roughly 58% — with a footnote as long as the number itself explaining it's a facility-type proxy, not a real stress model, because I don't have one.

**Interviewer:** Who needed convincing with that number, and what would "convinced" have looked like?

**chi-cdot-planner:** The Commissioner's office, mostly, ahead of them facing City Council on the budget. Convinced there means: does this number survive a follow-up question. Nobody in that hearing has ever asked me to defend "low-stress" as a term before, because nobody outside my building has a competing number to hold up against mine. That's actually the thing that's different about what you're about to show me, isn't it — somebody else now has a number.

## 2. Product Recap

**Interviewer:** Right, that's exactly where I want to go. Quick grounding first — On Your Left today: independent, read-only, not run by the city, layers crash data, bikeway facility grades, and 311/camera proxies, drillable ward to corridor to intersection, everything badged real/proxy/mock/crowdsourced/derived, no ridership normalization yet, and it says so. You've used it before.

**chi-cdot-planner:** Right, I remember — the ward table I said I'd bookmark, the mock obstruction layer I said flatly don't publish standalone. I assume none of that changed. Go ahead.

## 3. Stimulus — Element by Element

**Interviewer:** First element, B1. A new findings card: "PeopleForBikes rates Chicago's bike network 11 out of 100. The average rated U.S. city scores 36. Chicago has 6,267 miles of high-stress streets and 1,834 low-stress." Trend line from 2024 to 2026. Immediate reaction?

**chi-cdot-planner:** My stomach drops a little, honestly, before my brain catches up — that's an 11, on my network, and it's going to land on my desk the same way the Vision Zero miss did, as a headline before it's a methodology. The Sun-Times piece on the missed target stung because it was fair, and my first instinct here is to ask who's citing this at me and when. That's before I even know anything about where the number comes from.

**Interviewer:** Take a beat with it now that you've had the first reaction — what would you actually do with a card like this?

**chi-cdot-planner:** Two different things, depending who's in the room. If it's internal — my director, maybe the Commissioner's office — I could actually use an outside 11 as leverage, the same way the corridor economic study became my go-to weapon against "bike lanes kill business." An independent group with a published method saying we're at 11 against a 36 average is exactly the kind of pressure that gets a budget line increased instead of flat-funded, because now it's not me asking for more money, it's an outside validator saying the city's behind. That's the same mechanic as the ward table being useful because it's not CDOT saying it about itself.

If it's external — a hostile committee hearing, an alder's chief of staff who doesn't like me — that same 11 is a weapon pointed the other way, and I don't get to choose which room it shows up in first. Once it's public, it's public in both directions. So my honest answer is: I'd use it, but I'd want CDOT's own trend sitting right next to it before I'd ever forward it anywhere, because 150 miles installed and 80% low-stress target are real numbers I can point to that an isolated "11 out of 100" doesn't show at all.

**Interviewer:** Second, B2. Block-level access scores, aggregated to ward: "In Ward 35, X% of residents live on blocks with low-stress bike access to a grocery store." Not a danger ranking.

**chi-cdot-planner:** Okay — first read, and I'll be honest about this because you'll probably catch it anyway — my brain went straight to "so which ward comes out worst," like it's another version of the ward safety index, 0 to 100, somebody's at the bottom. That's just how I'm wired to read a per-ward number at this point, I've been staring at danger rankings for eight years. You're telling me it's not that — it's "percent of residents with access," framed positive, not a ranking of who's most dangerous.

Okay, once I actually sit with that framing — that's better for me, genuinely, not just politically better, better. This is closer to what a task force actually argues about: can a family get to a grocery store without riding somewhere terrifying. That's a Neighborhood Bike Network conversation, that's the thing residents in Austin and Belmont Cragin and North Lawndale kept naming — destinations, not crash dots. If this holds up, I'd bring it into a task force scoping meeting the way I bring the 2026 corridor study into a merchant meeting: this is why we're prioritizing this specific corridor, not because I said so, because an independent access score says households here can't reach a grocery store without a high-stress ride. I'd want to know the block-to-ward join method before I'd trust it in the room, though — is that a clean spatial join like our crash-to-ward pipeline, or something looser, because ward boundaries chop up census geography in ugly ways at the edges.

**Interviewer:** Third, B3. Segment-level stress cross-check: every street gets a stress grade from speed, lanes, parking, intersections — independent of facility type. Where OYL's own grade says "protected" and BNA says the segment is still high-stress, it gets flagged, possibly as a finding: "N miles of bikeways sit on streets BNA still rates high-stress."

**chi-cdot-planner:** [long pause] Okay, this is the one where I actually feel my shoulders go up. You're telling me somebody's going to run a model over infrastructure I personally fought for, that I sat through a task force for, and hand back a finding that says it's "still high-stress" — and I don't get a phone call first? That's my facility taxonomy fight, the one I already told you I fact-check myself because mileage claims are exactly where CDOT gets hammered. Now there's a second, independent taxonomy doing the same fact-check, and it might disagree with mine, and I don't control when that disagreement becomes a published sentence.

Here's the thing though — and I want to be fair about this, because you're the one who taught me to separate the discard from what earned it — professionally, quietly, this is close to useful to me. I've told you I don't fully trust our own "protected" label because it depends on a twenty-year-old digitized as-built drawing. An independent stress model that accounts for speed and intersection exposure, not just the facility category somebody wrote down once, could actually catch the exact gap I already suspect exists — a corridor that's "protected" on paper but has an uncontrolled crossing every two blocks that makes it feel like nothing changed. If that stayed internal, a QA signal I could review before anyone else saw it, I'd want it. Published as a finding with a segment count and no chance for me to say "that's a jurisdiction issue, IDOT owns that intersection, not us" — that's the version that keeps me up at night.

**Interviewer:** Last, B4. A peer-city strip on the findings page — Chicago's score next to NYC, LA, Philadelphia, Minneapolis, Seattle — same run, same methodology, no extra data pull.

**chi-cdot-planner:** Honestly? Shrug. That's not really built for me. I'm not in a room where "we're behind Minneapolis" changes what I do Monday morning — I already know roughly where we sit relative to peer cities from conference chatter and NACTO calls, I don't need a chart to tell me that. If anything it's a step removed from my actual job, which is one corridor and one alder and one task force at a time, not a national leaderboard. I could see it being useful one level up from me — the Commissioner's office loves a "peer cities" slide for a budget ask, that's a real genre of slide they already make — so I wouldn't kill it, I just wouldn't be the one opening that page in a normal week.

## 4. Trust Probes

**Interviewer:** It's computed from OpenStreetMap by a national advocacy org, updated once a year, only as current as volunteer mapping. Does that change anything for you?

**chi-cdot-planner:** It changes a lot, actually, and it's the first thing I'd have wanted to know before B1 even landed on my desk. Here's my problem with it concretely: I don't know, right now, sitting here, whether the protected lane my team finished on Milwaukee last fall is even *in* OpenStreetMap yet. Nobody on my team has that as a job duty — pushing our as-builts into OSM isn't in anyone's PM load, it's whatever some volunteer mapper decides to do in their spare time, on their own schedule. So if BNA's score is only as current as that volunteer's Tuesday afternoon, then part of our "11" isn't measuring our streets, it's measuring OSM's backlog. That 9-to-11 trend line you showed me — I have no way of knowing how much of that is us actually building things versus somebody finally mapping something we built two years ago. That's not a hypothetical caveat to me, that's a real gap between what my team did and what the score says we did, and right now I have zero visibility into which one I'm looking at.

**Interviewer:** Chicago scores 11 out of 100. Does that number help you or hurt you?

**chi-cdot-planner:** Depends entirely on who controls the caveat when it leaves the building, and I don't get to control that once it's public. Internally, framed next to our own trend — miles installed, protected share growing — it helps, it's exactly the kind of outside pressure that gets budget moved, the same mechanic as the corridor study. Standing completely alone, no context, handed to a hostile alder's staffer two days before a hearing — it hurts, and it hurts in a way that's hard to walk back, because "11 out of 100" is a sentence that fits in a tweet and my footnote about OSM mapping lag does not. I've watched a bad number escape its caveats before. I don't think this is a bad number, necessarily — I think it's a number without a chaperone, and whether it helps or hurts me is really a question about whether OYL publishes it with the chaperone attached every single time, not just the first time.

**Interviewer:** The ward number is access-framed — percent of residents with low-stress access to a destination — not a danger ranking. React to that specifically.

**chi-cdot-planner:** I already told you my first instinct misread it as a ranking, so let me answer the corrected version. I actually prefer this framing to our own ward safety index, and that's not something I expected to say out loud. "X% of residents have low-stress access to groceries" is an investment case — it tells a task force and an alder what to build toward, not just who's currently losing. Our own index is a comparative danger score, and I've watched an alder's office get defensive about being ranked, because a ranking always implies somebody's fault. Access framing doesn't do that the same way. If I'm honest, I'd want OYL's own ward safety index to borrow this framing instinct, not just apply it to the BNA layer.

**Interviewer:** Where OYL's own quality grade disagrees with BNA stress, which do you believe, and what should the site do about the disagreement?

**chi-cdot-planner:** I believe my own taxonomy first, on the segments I've personally verified, because I know exactly which digitized as-built drawing produced that label and I know its weak points. But I already told you I don't fully trust my own taxonomy on the segments I *haven't* personally checked — there's maybe sixty corridors in my install-date spreadsheet out of several hundred, so most of the network is stuff I'm trusting secondhand too. So the honest answer isn't "I believe mine," it's "I believe mine is more likely right on the segments I know, and I have no strong prior on the rest, and BNA disagreeing there is actually information, not noise."

What should the site do — don't silently pick a winner, and don't publish "N miles still high-stress" as a flat finding with no path back to context. Show the disagreement as its own labeled thing — this segment is CDOT-graded protected, BNA-graded high-stress, here's why they might diverge: intersection exposure, speed limit, or possibly OSM hasn't caught up to the install yet. Give me, or whoever's defending that segment, the reason category, not just the flag. And give me a heads-up channel before a specific-segment disagreement becomes a public finding — even just a "here's what's about to publish" so I'm not finding out from an alder's staffer that my own bikeway is being called high-stress by somebody else's map.

## 5. Forced Choice

**Interviewer:** Rank B1 through B4 for your own work. Then: should OYL skip this entirely and spend the effort elsewhere? Name the elsewhere.

**chi-cdot-planner:** For my own work, B2 first — access framing fits directly into task force scoping, it's the closest thing to the destinations-and-barriers conversation that actually moves projects, and it doesn't have the ranking-as-liability problem. B1 second — real value, but only with the chaperone, and I'd never forward it without CDOT's own trend attached, so it's more work for me every time I use it, not less. B3 third — genuinely interesting to me professionally, possibly the most interesting thing on this list, but only if it stays internal-review-first; as a public finding it's currently the riskiest thing you've shown me, so it ranks low for how I'd actually deploy it today, even though I don't want you to kill it. B4 last — not nothing, but not mine; that's a Commissioner's-office slide, not a CDOT-PM tool.

Should you skip all of it? No — don't do that, B2 alone is worth building. But if you're asking me to trade effort, I'd trade B4 first, maybe B3's public-finding version too, for the thing I asked for last time and I'll ask for again: install-date history on our own bikeway network. None of this — not B1, not B2, not B3 — tells me whether a corridor's before/after actually worked, because none of it is anchored to when something went in the ground. You could build me the entire BNA integration and I'd still be doing before/after by hand with a spreadsheet and a favor. If I had to pick one elsewhere for the team's time, it's that, every time.

## 6. Kill Question

**Interviewer:** What single thing about this integration, done wrong, would make you stop trusting the site?

**chi-cdot-planner:** Publish a "still high-stress" flag on a specific segment I personally installed and defended — something I sat through a task force for, something I know cold — without giving me or my team any chance to add context first, and have it turn out to be an OSM mapping-lag artifact, not a real problem, something that would've resolved itself the next time a volunteer mapper updated the tags. That's the exact test I'm actually qualified to run, on my own domain, and if the site fails it once — publishes my work as still-dangerous when the real story is "OpenStreetMap hasn't caught up yet" — I stop trusting every other flag on the site I can't personally check, which is most of them. That's not a new rule for me, that's the same rule I already told you: I don't get a second look at a dashboard that fails the one test I'm qualified to run. B3 is just the version of that test with my name on it this time.

## Analysis Memo

participant: chi-cdot-planner
confidence_notes: The persona held its established voice and evidence base throughout — CIP/menu-money mechanics, the 18th Street and Milwaukee corridor references, the install-date spreadsheet, the Chicago/Wells counter, and the Cycling Strategy 80%-low-stress target were all reused consistently with the original-study interview rather than reinvented. The claim that "nobody on my team has [pushing as-builts into OSM] as a job duty" is plausible in-world color (CDOT has no stated OSM-liaison process in the evidence base) but is the persona's own invented institutional detail, not a documented fact — flag as low-confidence texture, not verified organizational reality. The B2 misread (reading an access-framed score as a danger ranking on first pass) was the required test of shared-rule #7 and reads as genuine pattern-matching from her established ward-safety-index vocabulary rather than a forced beat.

stated_needs:
  - need: Any citywide BNA score (B1) must ship paired with CDOT's own trend data (mileage installed, protected-share growth) on the same surface, not as an isolated number.
    evidence_quote: "I'd want CDOT's own trend sitting right next to it before I'd ever forward it anywhere, because 150 miles installed and 80% low-stress target are real numbers I can point to that an isolated '11 out of 100' doesn't show at all."
    underlying_job: Convert a number that can be used against her program into a number she can use for it — pre-empt the "gotcha quote in a hearing" failure mode before it happens, rather than responding to it after.

  - need: A CDOT-facing heads-up or review step before any segment-specific B3 "still high-stress" disagreement becomes a public finding.
    evidence_quote: "Give me... a heads-up channel before a specific-segment disagreement becomes a public finding — even just a 'here's what's about to publish' so I'm not finding out from an alder's staffer that my own bikeway is being called high-stress by somebody else's map."
    underlying_job: Preserve her ability to add jurisdictional/methodological context (e.g., an IDOT-owned intersection, an OSM-lag artifact) before a finding about her own installed work reaches a hostile audience, not after.

  - need: When OYL's own facility grade and BNA's stress grade disagree, show the disagreement itself with a reason category (intersection exposure, speed limit, or possible OSM lag) rather than silently choosing one or flatly reporting a mileage count.
    evidence_quote: "Show the disagreement as its own labeled thing... Give me, or whoever's defending that segment, the reason category, not just the flag."
    underlying_job: Let her (or whoever fields the resulting question) answer "why do these two maps disagree" in one sentence, the same survival bar she applies to every number she carries into a hostile room.

  - need: Methodological transparency on the B2 block-to-ward spatial join (denominator, boundary handling) before she'd cite it.
    evidence_quote: "I'd want to know the block-to-ward join method before I'd trust it in the room... ward boundaries chop up census geography in ugly ways at the edges."
    underlying_job: Same denominator-first habit she already applies to her own ward-table use — she cannot forward a number upward that she can't defend if asked "what's in this."

latent_needs:
  - need: Visibility into whether a specific CDOT-installed segment has actually been reflected in OpenStreetMap yet — i.e., a mapping-currency signal per segment, not just a general "annual, OSM-derived" caveat on the whole dataset.
    inference_basis: >
      Unprompted by a direct question about her own team's OSM practices, she volunteered that she
      doesn't know whether last fall's Milwaukee protected-lane install is in OSM yet, and that
      "pushing our as-builts into OSM isn't in anyone's PM load, it's whatever some volunteer mapper
      decides to do in their spare time." She then connected this directly to the 9→11→11.08 trend
      line, saying she has "zero visibility into" whether that movement reflects construction or
      backlog clearance. This is the same domain-expert instinct that made her fact-check facility
      taxonomy in the original interview, redirected at a new axis (currency, not category) that the
      generic OSM-lag caveat string in the proposal does not resolve for her.
    risk_if_wrong: A blanket "only as current as OSM mapping" caveat satisfies a methodologist but not a planner defending one specific corridor; without a per-segment or per-corridor mapping-currency signal, she has no way to tell whether a "still high-stress" flag on her own work is a real problem or a volunteer-mapping backlog — which is precisely the ambiguity that produces her stated kill scenario.

  - need: A single-image or single-card pairing pattern — an outside/critical number placed directly beside CDOT's own progress metric for the same geography and window — reusable across any external score the site introduces, not just BNA.
    inference_basis: >
      She independently reached for the same pairing logic she used unprompted in the original
      interview's magic-wand answer (crash severity before/after next to the economic-study numbers,
      "same corridor, same window") and applied it here to B1: "internally, framed next to our own
      trend... it helps... standing completely alone... it hurts." The mechanism she names both times
      is identical — an outside claim only survives her hostile-room test when a CDOT-owned number
      sits next to it in the same frame — which suggests this is a general requirement of hers for
      any third-party evidence layer, not a one-off reaction to BNA specifically.
    risk_if_wrong: If OYL treats the "pair it with CDOT context" fix as bespoke to B1's launch, the same failure will recur every time a new external, potentially unflattering metric is added (peer comparisons, future national indices) — each will need to be re-litigated as its own crisis instead of applying a pattern she has now named twice.

  - need: The ward-access framing rule (percent-with-access, not a 0–100 ranking) should retroactively inform OYL's own existing ward safety index, not stay scoped to the new BNA layer.
    inference_basis: >
      After correcting her own initial misread, she volunteered, unprompted: "If I'm honest, I'd
      want OYL's own ward safety index to borrow this framing instinct, not just apply it to the BNA
      layer." This goes beyond reacting to B2 as presented — it is a spontaneous cross-reference back
      to a feature from the original study (the 0–100 ward safety index) that she is now re-evaluating
      against a framing she just found preferable, unprompted by any question comparing the two.
    risk_if_wrong: If OYL ships B2's access framing as a one-off stylistic choice for the new BNA
      surface while leaving the existing ward safety index in ranking form, it creates exactly the
      internal-contradiction pattern she flagged as most dangerous in the original interview (two
      pages implying different things about the same ward) — except self-inflicted, between OYL's
      own two ward-level products.

reactions_to_proposal:
  - element: B1 — Citywide BNA scorecard
    verdict: would-use
    why: Concrete internal use (budget-ask leverage, same mechanism as her existing corridor economic study) but only paired with CDOT's own trend; standing alone she considers it a live liability, "a number without a chaperone" — the verdict is conditional on OYL always shipping the pairing, not a clean uses/ignores split.

  - element: B2 — Ward-level access scores
    verdict: misreads (initially) / would-use (corrected)
    why: First-pass misread it as a danger ranking (her established ward-safety-index vocabulary defaulting), corrected once the access framing was restated. Once corrected, ranked it highest of all four elements for her own work — closest fit to task-force scoping and destination/barrier language — contingent on the block-to-ward join methodology checking out.

  - element: B3 — Segment stress cross-check
    verdict: distrusts
    why: Distrust is specific to the public-finding form ("N miles still high-stress" published without her review), which she treats as the highest-risk element shown — directly analogous to her original-interview deal-breaker pattern (one wrong number in her own domain of expertise ends trust in everything she can't check). She explicitly does not want it killed as an internal QA signal, only gated before it becomes a shareable finding.

  - element: B4 — Peer-city strip
    verdict: ignores
    why: Not her audience or working altitude ("that's not really built for me... I'm not in a room where 'we're behind Minneapolis' changes what I do Monday morning"); she defers it to the Commissioner's office as a budget-ask genre, not something she'd personally open.

data_they_bring: The 80%-low-stress Cycling Strategy target and her own hand-built facility-taxonomy proxy for "low-stress" (protected + greenway, informally), assembled by manual GIS export because CDOT has no formal stress methodology of its own — the internal artifact that BNA's segment-level model would either validate or embarrass. Direct, lived uncertainty about her own team's OSM-mapping practices (no one owns pushing as-builts into OpenStreetMap). The same install-date spreadsheet, corridor economic study, and "one wrong number ends trust" instinct carried over from the original interview, now applied to a second, independent data source.

deal_breakers:
  - Publishing a B3 "still high-stress" finding against a specific segment she personally installed and can verify, without any review or context channel, when the true cause turns out to be OSM mapping lag rather than a real infrastructure problem — stated explicitly as the version of her established "one test I'm qualified to run" rule that this proposal introduces.
  - An isolated "11/100" figure reaching a hostile audience (an alder's staffer, a committee hearing) with no CDOT trend context attached anywhere near it — the B1 analog of the Sun-Times sting she already lived through with the Vision Zero miss.

vocabulary: Carries all established terms (KSI, HIN, CIP, "the portal," "before/after," "prerogative," "menu money," "task force," "ward temperament") plus new terms surfaced this interview — "gut check" (an informal mid-cycle progress check, distinct from a formal report), "low-stress" as her own working term (from the Cycling Strategy target language, used before and independent of any BNA vocabulary), explicit rejection of unexplained methodology jargon ("I don't have [a formal stress model]... walk me through what feeds it" implied posture toward LTS-style terms she never adopts by name), "a number without a chaperone" (her coinage for an unpaired external statistic), "report card" used loosely for the B1 scorecard, "access score" vs. "danger ranking" as a distinction she now actively prefers and wants applied to OYL's own ward safety index.
