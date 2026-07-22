# Interview: chi-cdot-planner

**Run date:** 2026-07-21 (re-run)
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** — NEW areas since the
prior run: home/orientation page, ward one-pager, methodology page, static
agent API (`/api/v1` + `llms.txt`), news-coverage layer, proposed-projects
roster, PeopleForBikes BNA score, obstructions moved off the main map to a
gated preview page.
**Participant:** Elena Kowalski (composite, fictional) — CDOT Complete
Streets/Bikeways project manager, 8 years.

## Transcript

### 1. Context

**Interviewer:** Describe your role, and walk me through the last decision you influenced — or tried to — about street safety. What did that actually involve, step by step?

**Elena:** Complete Streets, bikeways side, eight years in — I've outlasted two commissioners at this point. Most recent thing I'd call a "decision I influenced" wasn't even my project: 18th Street, Ald. Dowell's ward, protected intersection already built, and she ordered CDOT to rip pieces of it back out last fall after renewed community pushback. Not my corridor, but half my team got pulled into the after-action because everybody wanted to know "could this happen to us." What I actually did with that fear: I went back to my own Belmont Cragin segment, part of a Neighborhood Bike Network task force, and preemptively downgraded a planned protected lane to buffered-only because the task force chair got spooked. I didn't have anything that would've changed her mind. I had a High Injury Network corridor listing and a rendering. That's it.

**Interviewer:** Who did you need to convince there, and what does "convinced" look like for them?

**Elena:** The task force chair first, then eventually the alder's chief of staff, because nothing moves without the ward office. "Convinced" for the chair meant showing her that residents in her own neighborhood wanted safer crossings to named destinations — the library, two schools — not a crash percentage. Community process data did more work in that room than my crash dots ever could. The chief of staff wanted to know if it would generate 311 complaints and news coverage before it got built. Neither of us had a good way to forecast that, and I still don't.

**Interviewer:** What information sources do you touch in a normal week for this work?

**Elena:** Data Portal crash tables directly, I know the E-Crash sourcing well enough to spot provisional versus amended batches. Our internal GIS layers, which feed "the portal" — our own catalog, not some outside site. OBM menu-allotment PDFs. Whatever the current task force is producing, sign-in sheets, sticky-note maps. And the 2026 corridor economic study, which I now bring to every merchant meeting because it's the only ammunition I have against "bike lanes killed my parking."

### 2. Current practice & workarounds

**Interviewer:** Tell me about the last time you needed a number, map, or chart about bike safety. Where did you go, what did you do with it, how long did it take?

**Elena:** Two weeks ago, merchant meeting on a corridor I run. Someone stood up with the old Logan Square "bike lanes killed my business" story — not even about our street. I had the economic study memorized, that took me nothing. What took time: he asked for install dates nearby "to see how long till recovery," and our own published bikeways layer has no install dates. I had to dig through project-closeout memos and Street View history to reconstruct rough install timing for three blocks. Most of an afternoon, for three blocks.

**Interviewer:** What have you built yourself because nothing gave it to you directly?

**Elena:** A corridor-by-corridor shadow spreadsheet — design status, community-process notes, reconstructed install timing from closeout memos and my own site-visit photos, sometimes just asking my design engineer "when did this actually go in." Maybe sixty corridors logged out of several hundred we've built. It lives on my laptop. If I got hit by a bus tomorrow, sorry, bad line of work for that phrase, nobody could find it.

**Interviewer:** Tell me about a time data, or the lack of it, sank an argument you were making.

**Elena:** I tried to get budget for a second permanent counter, citing our one counter at Chicago/Wells from 2022 as proof of value. Got waved off — "we already have a counter, why do we need another." I couldn't show "this corridor moves X riders a day and deserves its own counter" because the data that would justify a second counter doesn't exist until you already have one. Circular. Lost that budget line two years running.

**Interviewer:** What data do you distrust, and what earned that distrust?

**Elena:** 311 bike-lane-blockage complaints, completely. They skew toward wards with residents who already file 311 tickets, which is not the same as where blockages happen. I've watched a staffer wave a 311 heat map like it proves something and had to gently explain it mostly proves who has time to complain.

### 3. Stimulus walkthrough

**Interviewer:** Let me walk through what OYL offers now. It's independent, read-only: crash, infrastructure, ward drill-down, real/proxy/mock/crowdsourced/derived badges on every layer, no ridership normalization and it says so, plus a new static agent API alongside the human site.

**Elena:** The badge system is the first thing I check, before anything else — that's the difference between a site I can point a staffer to and a site I have to spend an afternoon debunking. Saying "no ridership normalization" out loud instead of faking a rate buys real trust with me too. We don't have real ridership internally either.

**Interviewer:** New: the home page — an orientation landing page, including a plain-language explainer on asking an AI assistant questions through the agent layer.

**Elena:** Not for me, I'll go straight to methodology, not ask a chatbot "is my corridor dangerous." But — reluctantly — my comms colleague would probably use that exact line in an alder briefing memo, "you can literally ask this thing." That plays well to a chief of staff who doesn't want to open a map.

**Interviewer:** New: the ward one-pager — printable, safety index, trends, infra stats, alderman contact and sponsorship record, menu-money proxy, ward-matched news.

**Elena:** This is the one I'd actually forward. It's shaped like the thing I already hand-build for every task force. The menu-money proxy is where I'd push hardest — is that itemized spend or an estimate? That's exactly the number Ward Wise built a whole project around getting right, and if this is looser, someone who knows Ward Wise catches it in ten seconds and stops trusting the rest of the page.

**Interviewer:** It's marked proxy — a Ward Wise-style extract, not verified against source PDFs.

**Elena:** Then say that ON the one-pager, not two clicks away in sources.html. If I hand this to an alderman and they ask "is this what we actually spent," I need the caveat on the same page as the number.

**Interviewer:** New: the methodology page — how every number is computed.

**Elena:** Show me the safety index formula specifically. Percentile-blended like a HIN, severity-weighted, or raw count per something? If it's a flat danger score with no severity weighting, I'd tell colleagues not to cite it — same as I'd push back on someone handing an alder a raw crash count instead of our HIN.

**Interviewer:** It's a percentile blend of crashes/10k population and crashes/bikeway-mile, plus 12-month crash trend and infra growth trend — explicitly relative, not absolute.

**Elena:** Better than I feared, but "relative" needs to be loud on the index itself, not a footnote. The second an alder's office treats a ward's score as absolute risk instead of a rank, someone asks "so is it dangerous or not" in a hearing room and "it's relative" sounds like a dodge. I've watched that exact conversation go sideways with our own HIN.

**Interviewer:** The bikeway network layer — facility category protected/buffered/painted/greenway/sharrow/trail/other, but no install dates.

**Elena:** [laughs, not happily] That's the one that gets under my skin, because it's our fault, not theirs — we don't publish install dates either, so they built forward-history from snapshots, the same workaround I use with Street View. But any before/after study built off snapshot-diffed install estimates is artisanal at best, and it's got my agency's facility taxonomy on the chart. I'd want a loud asterisk on any before/after claim from this, not a footnote in sources.html.

**Interviewer:** And the facility taxonomy itself — centerline versus lane miles, two-way tracks?

**Elena:** Exactly where I'd poke, because mileage claims are how CDOT gets publicly attacked. If the denominator is centerline miles like ours, say so right next to every mileage stat — a two-way protected track on a one-way street counts very differently depending on convention, and advocates will catch a mismatch and use it against CDOT, not against the dashboard.

**Interviewer:** New: the PeopleForBikes BNA citywide score — 0-100 network connectivity, low/high-stress miles, national ranking, "not a reason not to ride."

**Elena:** I know BNA, it's a real, respected LTS-based methodology, I've cited it in a grant application once. Genuinely useful for "how does Chicago compare to peer cities" with my director. Nearly useless for "should we prioritize this corridor over that one" — it's a citywide network score, my job is corridor-level. If a resident waves a citywide score at me as if it settles a specific street's need for a protected lane, I have to explain, again, those are different questions.

**Interviewer:** New: the news-coverage layer — recent headlines matched to wards, aldermen, routes, and projects, with an auditable "via" on every match.

**Elena:** Complicated feelings. Useful: if a reporter calls about coverage on my corridor, I don't have to remember it myself. Dangerous: news coverage isn't ground truth. Three sensational headlines about one bad crash makes a corridor look "hot" in a way a calmer corridor with the same crash rate won't. Does the news layer ever feed the safety index, even indirectly? Because if a headline can move a number, that's advocacy pressure dressed up as data.

**Interviewer:** It's a separate layer, matched and displayed alongside, not an index input.

**Elena:** Good, keep it that way, and say so somewhere prominent. The first thing a skeptical colleague asks is "does bad press make the number go up."

**Interviewer:** New: the proposed-projects roster — hand-curated, volunteer-reviewed status plus date and note, official links, citations, auto-joined news, no geometry.

**Elena:** [long pause] Have to be honest about how this lands for me specifically, not a resident. An outside site tracking the status of MY projects, reviewed by volunteers I don't know — my first reaction isn't "great, transparency," it's "who reviewed this, and what happens when it's wrong the week before a community meeting." If a status says "stalled" and it's really just waiting on utility relocation paperwork, and a resident cites your roster at my meeting, I spend the first ten minutes correcting your site instead of talking about the project.

**Interviewer:** What would change that reaction?

**Elena:** A visible "status as of [date], checked against [official link]" stamp on every card, so I can see at a glance whether it's fresh, and a public, fast correction path — not editorial control for CDOT, I get why you wouldn't want that, just a "flag this" link with a visible response time. Three weeks for a volunteer to review a correction isn't fast enough for a status shaping a meeting agenda.

**Interviewer:** The obstructions layer moved off the main map entirely, into a gated, watermarked preview page, excluded from the API, pending a data-sharing conversation with Bike Lane Uprising.

**Elena:** That is the single biggest trust-earning move since I last looked at this. Mock obstruction data on a live map next to real crash dots would have made me stop recommending this site — Bike Lane Uprising is real, respected, litigation-grade in this world, and synthetic data standing in for it risks becoming "CDOT's map shows fake bike lane blockages" in a screenshot. Gating it, watermarking it, keeping it out of the API tells me you understood the problem, not just badged over it. I'd still ask — can a screenshot circulate without the watermark or the gate context? Watermarks get cropped.

**Interviewer:** The agent API — static JSON, per-ward and per-route files, a `_meta` envelope with tier and provenance on every file, obstructions excluded entirely.

**Elena:** Not my problem directly, I'm not writing code against it. But if a consultant or intern on my team pulls a number out of an AI assistant quoting your API, the provenance envelope needs to survive that trip, not just exist in raw JSON nobody reads. Someone telling my director "the AI said ward 30 scores 71" with no caveat attached is a worse version of the danger-index problem, one layer further from anyone checking it.

### 4. Gap probing

**Interviewer:** You're briefing an alderman's chief of staff ahead of a menu-money deadline. Open OYL. What do you look for first, where does it fail you?

**Elena:** Ward one-pager first — safety index, sponsorship record, menu-money proxy, that's ninety percent of what a chief of staff wants in one page. Where it fails: I still can't show install-date-linked before/after for anything already built in that ward, and I can't show ridership. Those are the two questions every chief of staff eventually asks — "is it safer since we built it," "how many people use it" — and OYL, like CDOT, has no honest answer to either.

**Interviewer:** Of everything OYL does not have, what single absence costs you most?

**Elena:** Install dates, no question. Such a small, boring field, and its absence breaks every evaluation story anyone wants to tell about our own work. Ridership's the sexier gap everyone talks about — I've made peace with not having ridership. I have not made peace with not being able to say when our own lane went in.

**Interviewer:** The site refuses to normalize by ridership. Does that change how you'd use it? What would you accept as good-enough exposure data?

**Elena:** Doesn't change whether I'd use it — I already operate that way internally. In order of what I'd accept: our own counters if we ever get more than one, not happening soon; bikeshare trip data joined by nearest corridor, undercounts personal-bike riders but directional and real; at the bottom, something like Strava volume, crude but better than nothing — flagged as loud as the mock obstructions, because Strava riders skew toward certain demographics and corridors and that bias needs to travel with the number.

**Interviewer:** One export a week — what's in it, who gets it?

**Elena:** A one-page-per-active-corridor sheet: current facility grade, recent crash trend, any news mentions that week, and a flag if the proposed-projects roster status changed. I'd forward that to my own PM group every Monday instead of us each checking our corridors by hand over Slack, which is what we do now, badly.

### 5. Magic-wand close

**Interviewer:** One dataset that doesn't publicly exist appears, clean and current. What is it?

**Elena:** Install dates for every facility segment CDOT has ever built, with the as-built type at install time, not just current type. That field would let anyone run real before/after studies instead of the artisanal ones I do now with Street View and old memos. Less glamorous than ridership, but it would change more of my actual working life.

**Interviewer:** One chart that ends an argument in front of your hardest audience.

**Elena:** A corridor-level, install-date-anchored before/after panel: crash rate twelve months before versus twelve after install, next to the 2026 economic-impact numbers on the same corridor, same window. Right now I have the economic study and I have crash trend, never cleanly aligned to an install date on the same chart. If that existed and held up, I could stop reciting the same six-corridor study from memory every merchant meeting.

**Interviewer:** What would make you stop using a site like this after trying it once?

**Elena:** Catching one confidently-wrong number in front of an audience I can't walk back — a menu-money figure off by a category, a mileage number double-counting a two-way track — caught by someone in the room before I catch it myself. One public miss like that, even against an otherwise-solid site, and I quietly stop recommending it. Being wrong in front of an alderman isn't a mistake I get to make twice.

## Analysis memo

```
participant: chi-cdot-planner
confidence_notes: The persona's reactions to methodology.html, facility
  taxonomy, and the BNA score are directly grounded in the evidence briefs
  and felt in-character. The reaction to the proposed-projects roster
  required extrapolation beyond the evidence brief (which documents CDOT's
  process reality and prerogative dynamics but says nothing about a
  third-party project tracker specifically); kept as plausible in-character
  inference from her documented "accountable for a network you can't
  unilaterally build" frustration, but flagged as the thinnest spot in this
  run. The agent-API reaction is necessarily speculative since no evidence
  material addresses AI-mediated data consumption in CDOT's world; kept
  brief and hedged ("not my problem directly") rather than manufacturing
  expertise she wouldn't have.

stated_needs:
  - need: Install-date history for every bikeway segment, joined to
      as-built facility type at install time, so before/after safety
      comparisons don't require manual reconstruction.
    evidence_quote: "Install dates for every facility segment CDOT has ever
      built, city-wide, with the as-built type at install time, not just the
      current type. That single field would let anyone... finally run real
      before/after studies."
    underlying_job: Produce a credible before/after evaluation story for any
      project without Street View archaeology, so evaluations stop being
      artisanal.

  - need: On-page (not sources.html-only) methodology disclosure for the
      safety index (severity-weighted/relative vs. absolute) and for
      mileage-stat denominators (centerline vs. lane miles).
    evidence_quote: "If it's a flat 0-100 'danger score' without severity
      weighting, I will tell every colleague I know not to cite it...
      'explicitly relative' needs to be loud, not a footnote."
    underlying_job: Vet a number before citing it to an audience she cannot
      walk it back from.

  - need: A visible freshness stamp and fast correction path on the
      proposed-projects roster.
    evidence_quote: "A visible 'status as of [date], last checked against
      [official link]' stamp on every card... a public, fast correction
      path... If corrections take a volunteer three weeks to review, that's
      not fast enough."
    underlying_job: Avoid having to spend the first ten minutes of her own
      meeting correcting an outside site's stale status on her own project.

  - need: The menu-money "not verified against source PDFs" caveat placed on
      the same page as the number, not two clicks away.
    evidence_quote: "If I hand this to an alderman and they ask 'is this
      what we actually spent,' I need the caveat on the same page as the
      number, not two clicks away."
    underlying_job: Hand a document upward without personally owning the
      risk of an unverified number being treated as official.

  - need: An explicit, prominent statement that the news-coverage layer
      never feeds the safety index.
    evidence_quote: "Does the news layer ever feed into the safety index,
      even indirectly? Because if a headline can move a number, that's a
      problem, that's advocacy pressure dressed up as data."
    underlying_job: Defend the index's legitimacy against the claim that
      press attention, not risk, drives the score.

latent_needs:
  - need: A corridor-level exposure/connectivity view distinct from the
      citywide BNA score, usable for prioritizing capital dollars between
      corridors.
    inference_basis: She drew this distinction unprompted — BNA is
      "genuinely useful" for citywide peer-city comparison with her director
      but "nearly useless" for corridor-level prioritization — and
      independently tied it to her lived experience losing a second-counter
      budget request twice for lack of a corridor-specific exposure case.
    risk_if_wrong: If OYL treats the BNA score as satisfying exposure-data
      needs broadly, corridor-level prioritization users get no usable
      substitute, and capital-dollar arguments continue with no exposure
      data at all, exactly as today.

  - need: An auditable, non-editorial flagging channel for CDOT (or any
      subject of a roster card) to contest a stale/incorrect
      proposed-project status without compromising the roster's
      independence.
    inference_basis: She explicitly pre-empted the obvious objection
      ("not to edit it, I get why you wouldn't want CDOT editing an
      independent tracker") while still naming a concrete operational cost
      (correcting the site live, mid-meeting, in front of a resident) —
      showing she'd already reasoned through the tension between wanting
      accuracy and respecting the tracker's independence.
    risk_if_wrong: A CDOT-facing edit/override channel would compromise the
      independence that gives OYL's corridor-danger claims their political
      cover (by her own framing of why an outside dashboard is useful); a
      channel that's too slow or opaque goes unused because no single PM can
      commit CDOT's institutional buy-in to it.

  - need: Explicit visual/textual separation between a corridor's news-
      mention volume and its safety metrics wherever the two are shown
      together, so press attention isn't mistaken for risk.
    inference_basis: Raised unprompted, tied to her documented reflex that
      mileage/safety claims are "where CDOT gets publicly attacked" and her
      lived experience that community sentiment (not crash data) moved the
      Belmont Cragin decision — she is primed to anticipate reputational
      harm from data that looks causal but isn't.
    risk_if_wrong: If news volume and the safety index are ever visually
      juxtaposed without a clear disclaimer of independence, a CDOT-adjacent
      user will assume (or fear others will assume) causation and actively
      discourage colleagues from using the ward one-pager — a reputational
      cost bigger than the feature's benefit.

  - need: The mileage-denominator convention (centerline vs. lane miles,
      two-way track counting) needs to be surfaced next to every mileage
      statistic itself, not only in methodology.html.
    inference_basis: Directly stated in her evidence base as a documented
      professional reflex ("You will fact-check the facility taxonomy...
      because mileage claims are where CDOT gets publicly attacked") and
      repeated unprompted when reacting to the facility-category layer in
      this run.
    risk_if_wrong: A denominator mismatch against CDOT's own public mileage
      claims will be read by advocates/journalists as either CDOT or OYL
      "inflating" numbers — exactly the reputational risk this persona is
      primed to anticipate and pre-empt.

reactions_to_existing:
  - feature: Real/proxy/mock/crowdsourced/derived badge system
    verdict: uses
    why: First thing she checks; precondition for recommending the site to
      colleagues at all.

  - feature: Home / orientation page, incl. AI-assistant explainer
    verdict: ignores (personally) / would-use (by proxy)
    why: Not her workflow, but she reframed it as a line her comms colleague
      would lift for an alder briefing memo.

  - feature: Ward one-pager
    verdict: would-use
    why: Matches a document she already hand-builds for every task force;
      would forward it once the menu-money caveat is on the page itself.

  - feature: Methodology page
    verdict: would-use (conditionally)
    why: Deciding factor for whether the safety index is citable; satisfied
      once told it's a percentile blend, but wants "relative not absolute"
      louder on the index itself.

  - feature: Bikeway network layer / facility taxonomy (no install dates)
    verdict: distrusts (for before/after use) / uses (for current
      facility-grade lookups)
    why: Same install-date gap she lives with internally; wants a loud
      caveat on any before/after claim from snapshot-diffed dates.

  - feature: PeopleForBikes BNA citywide score
    verdict: would-use (narrowly) / misreads-risk flagged
    why: Useful for citywide peer comparisons; flags that others will
      likely misapply a citywide score to corridor-level arguments.

  - feature: News-coverage layer
    verdict: would-use, with a specific distrust condition
    why: Useful for reporter-inquiry prep; would distrust it immediately if
      it fed the safety index; wants the separation stated explicitly.

  - feature: Proposed & in-progress projects roster
    verdict: distrusts (current form) / would-use (with freshness stamp +
      correction path)
    why: A government insider's specific discomfort at an outside party
      tracking her own projects' status; wants provenance/freshness and a
      correction channel before treating it as safe for residents to cite.

  - feature: Obstructions preview page (gated, watermarked, API-excluded)
    verdict: uses (approves of the mitigation)
    why: Named unprompted as "the single biggest trust-earning move" since
      the last review; the prior on-map mock layer would have been a
      deal-breaker; gating fixed it, though watermark-cropping remains a
      residual risk in her mind.

  - feature: Static agent API (/api/v1, llms.txt, _meta envelope)
    verdict: indifferent (personally) / latent concern (by proxy)
    why: Not her direct workflow; extrapolates a provenance-loss risk if an
      AI assistant quotes API data without the tier/caveat surviving the
      trip to a director.

data_they_bring: An internal shadow spreadsheet (corridor status,
  community-process notes, reconstructed install timing via project-closeout
  memos and Street View); the 2026 CDOT six-corridor economic-impact study,
  carried memorized to merchant meetings; the HIN / High Crash Corridors
  Framework as her working standard for a legitimate severity-weighted index;
  first-hand knowledge that CDOT's own bikeways layer lacks install dates
  internally too, not just in what it publishes.

deal_breakers: Catching one confidently-wrong number in public that she
  cannot walk back — a menu-money figure off due to a missed category, or a
  facility-mileage figure using a mismatched centerline/lane-mile
  denominator — surfaced by someone in the room before she catches it
  herself. A single public miss of that kind ends her willingness to
  recommend the site, even against an otherwise-solid track record.

vocabulary: corridor, facility type, low-stress, HIN, scoping, community
  process, "the alder's office," install season, centerline miles,
  before/after, counts, "the portal," CIP, "my PM load," menu money,
  prerogative, task force. Declined to adopt "danger index" without
  qualification, translating it back to "is it severity-weighted like our
  HIN or is it raw counts" every time the term came up.
```
