# Interview: chi-ward-office (Marcus Webb, composite persona)

**Run date:** 2026-07-21
**Stimulus:** `02-data-inventory.md`, data contract **v1.14** (reflects `main` as of 2026-07-21 — home/orientation page, ward one-pager, methodology page, static agent API, news-coverage layer, proposed-projects roster, PeopleForBikes BNA score, obstructions moved to gated preview)
**Interviewer:** Lead Researcher (LR)
**Participant:** Marcus Webb — chief of staff, North-Side-lakefront-adjacent ward office (persona: `personas/chi-ward-office.md`)

*(This is a re-run of a prior interview against an earlier stimulus version. It
is written fresh against v1.14 rather than assuming continuity with any prior
transcript, since the study protocol treats each run as its own instrument.)*

---

## Transcript

### 1. Context

**LR:** Walk me through your role, and the last decision you tried to influence about street safety — what did that actually involve, step by step?

**Marcus:** Last one was three weeks ago. CDOT wants to do a road diet on a stretch near the Metra stop — one travel lane each direction instead of two, protected bike lane, left-turn pockets at the two signalized intersections. My alder's inclined to support it because it's on-brand, but we've got a CAPS meeting Thursday and a guy who owns the hardware store on that block has already printed flyers. So my job for two weeks was: get my alder a page she can hold in her hand that says what happens to crashes on that block if we do this, what it costs, whether parking actually goes away, and whether the hardware store guy has any data behind him or just a bad feeling. I pulled crash data off the city portal myself, called CDOT's liaison for the ward-level counts because the portal export doesn't do it by corridor cleanly, and built a slide in about four hours the night before.

**LR:** Who do you need to convince, and what does "convinced" look like for them?

**Marcus:** Two audiences, really. My alder — she needs to feel like she won't get outflanked by a challenger next cycle over "war on cars" stuff, so convinced for her means: I can defend this in a debate and it won't cost me votes. And the room Thursday — eighty, ninety people, half of whom already decided. Convinced for them mostly isn't going to happen in one meeting, but "she didn't dodge it and she had real numbers" buys credibility even from people who vote no.

**LR:** What information sources do you touch in a normal week for this?

**Marcus:** Constituent calls and emails — that's the real currency, I log volume by issue category. 311 counts for the ward, CDOT liaison when I can get her on the phone, the ATA ward letter that lands in my inbox once a year with crash numbers, Streetsblog and Block Club because my alder gets tagged on Twitter — sorry, X — whenever they run a story, and eLMS for committee agendas so I know when Ped and Traffic Safety is taking something up that touches us.

### 2. Current practice & workarounds

**LR:** Tell me about the last time you needed a number, map, or chart about bike safety. Where'd you go, what did you do with it, how long did it take?

**Marcus:** That road-diet slide I just described. City data portal, "Traffic Crashes — Crashes" dataset — I filtered by a lat/long box I eyeballed around the corridor because there's no clean "give me this street" filter, exported to CSV, opened in Excel, built a pivot table by year, then manually tagged which rows were actually cyclist involved because the injury classification field isn't intuitive. Probably ninety minutes just wrangling data, then another hour making it look like something my alder wouldn't be embarrassed to hold up. I do this more than I'd like to admit.

**LR:** What have you built yourself — spreadsheets, screenshots, FOIA requests, hand counts — because nothing gave it to you directly?

**Marcus:** I keep a running spreadsheet — has for three years — of every 311 bike-lane complaint in the ward with the block, so when someone says "nobody complains about that corner" I can show them six calls from four different addresses. I've also got a shared doc with two other chiefs of staff where we compare menu-money spend categories year over year because OBM's PDFs are garbage for that — you can't diff them, you have to manually re-key every line. And I keep screenshots of Streetsblog and Block Club articles that mention our ward by name, filed by year, because if a reporter calls asking "didn't your alder say X in 2024," I need to find it in under five minutes, not by scrolling Twitter.

**LR:** Tell me about a time data — or the lack of it — sank an argument you were making.

**Marcus:** The 18th Street thing next door taught everybody in this business a lesson, even though it wasn't my ward. Ald. Dowell had a room of eighty angry people and CDOT's design work was already in the ground, but nobody in that room had cross-corridor before/after numbers ready to answer "prove it's safer," and there was no ward-level trend anybody could point to that said "wards that did this saw X." It got rolled back. My takeaway wasn't "the data didn't exist" — some of it probably did somewhere — it's that nobody had it *packaged* for that room, at that hour, in a form that wasn't going to get laughed at. That's the gap I live in every day.

**LR:** What data do you distrust, and what earned that distrust?

**Marcus:** 311 counts, and I use them constantly, so that's not a contradiction — it's a workload record, not a danger record. The blocks that generate calls are the ones with two or three organized residents who know how to use 311, not necessarily the most dangerous blocks. I've got silent intersections in the ward I'd bet money are worse than what's in the top of the 311 list. Also — anything that ranks wards against each other. My gut reaction to any "ward scorecard" is "who's going to screenshot this and hand it to my alder's next primary opponent," before I even look at the methodology.

### 3. Stimulus walkthrough

**LR:** Let me walk you through what's actually on the site now. First, the two maps — a geographic Leaflet map with crash density, bikeway grades, wards, cameras, and main routes; and a separate schematic "transit map" style network view with 21 named routes and comfort-floor filtering, no safety data on it.

**Marcus:** The geographic one, sure, I can see pulling that up live in a meeting if someone asks "what's actually there today" — better than me squinting at CDOT's PDF. The schematic transit-map thing, I don't know what I'd do with that in my job. It sounds like something a bike advocate shows another bike advocate. Nobody at a CAPS meeting is going to know what a "comfort floor" is, and if I said that phrase out loud in a community meeting people would think I was talking about a yoga mat.

**LR:** There's a home page now too — an orientation landing page explaining what OYL is, headline stats, who it's for, and how to ask an AI assistant questions using something called an agent layer.

**Marcus:** Fine for a first-time visitor, I guess, not something I'd come back to. The "ask an AI assistant" part — I'll be honest, that lands weird for me. Half my job is making sure a number that goes in front of my alder is one I can trace and defend if someone challenges it. If some resident, or worse a reporter, goes and asks a chatbot "is my ward dangerous for cyclists" and gets back a number pulled from this site with no context, and then calls my office asking why we're at 44th out of 50 — I didn't put that number in anyone's hands, an AI did, and I still have to answer for it. I don't have a strong read on whether that's good or bad yet, it's just a new way I can get blindsided that didn't exist before.

**LR:** Findings page — curated cards: KSI trend, protected-lane share, street coverage, top corridors, hit-and-run, ward concentration, dooring undercount, and a PeopleForBikes BNA citywide network score with national ranking context.

**Marcus:** The citywide KSI trend, top corridors, ward concentration — that's the stuff I'd actually screenshot into a slide. The BNA score I've genuinely never heard of before you said it. "National ranking" makes me nervous by default — is Chicago 40th out of 100 cities on this thing? Because if a reporter's got that number and I don't, that's exactly the blindside scenario I hate. I'd want to know before my alder does.

**LR:** Table page — ward rankings, sortable, CSV export, percent protected and percent-with-any-bikeway columns.

**Marcus:** Sortable and rankable is precisely the part that keeps me up. I will use the CSV — give me raw ward numbers all day, I'll build my own comparison in Excel where I control the framing. But a public, sortable, rankable table where anyone can click and put my ward at 44 out of 50? That's a press release waiting to happen, and it's not going to be mine.

**LR:** There's now a ward one-pager — printable, one URL per ward, safety index, trends, infra stats, alderman contact and sponsorship record, menu-money proxy, and recent ward-matched news — built to hand to an alderman or a neighbor.

**Marcus:** [pause] Okay, this is the one I have real feelings about. Structurally, this is exactly the format I need — I told you, I build a slide like this by hand every time there's a fight. If it existed pre-built I'd save myself four hours. But you said "safety index" is on it, and you said "built to hand to an alderman" — so somebody else's staffer is going to hand MY alder's one-pager to a reporter, or worse, a challenger's campaign is going to print it. I need to know: does this page make my ward look worse than it is, and can I get in front of that before it's on somebody's desk? Also — "alderman sponsorship record" on the same page as a safety score — that's basically a report card on my boss sitting at a public URL with her name on it. I did not sign up to have that built for me by a third party I don't control.

**LR:** Say more about the sponsorship record specifically — how would you actually react if you found it?

**Marcus:** First thing I'd do is check whether it's "sponsorship counts" or "did she vote against something." Because those are wildly different stories. If it's counting bills she co-sponsored, that's a squishy proxy — plenty of alders co-sponsor things that never move, or don't sponsor things they still vote for. If a challenger's campaign shows up at a debate with "my alder sponsored zero bike-safety ordinances this term" printed off this page, and the truth is she voted yes on everything that reached the floor but the committee chair never gave her bill a hearing, that's a real problem, and it's a problem your dashboard created even if every number on it is technically accurate.

**LR:** And the recent ward-matched news on that same page — it matches headlines to your alderman by name?

**Marcus:** That's the one that actually worries me most, more than the safety index honestly. If it's pulling in any Streetsblog piece that name-drops my alder and slotting it onto her public one-pager next to a safety score, I need to know how good the matching is. Does it grab the article where she's quoted supporting a project, or does it also grab the one where a resident group blamed her for stalling something, and just... put both there with equal weight, no context? I keep my own screenshot archive precisely because I don't trust an algorithm to know which mentions are favorable, unfavorable, or just her name appearing in a caption. If this thing matches wrong — wrong ward, wrong "La Spata" versus a "La Spata" quote about something else entirely, or grabs a story about a totally different alder with a similar name — that's not just an error, that's the kind of error I get a call about from my alder at 9pm.

**LR:** There's also a proposed-projects roster now — hand-curated cards of active bikeway/trail proposals, status plus a note, official links, and auto-joined news. No map geometry, just cards.

**Marcus:** That one I'd actually use, and here's why — this is the "promised versus delivered" gap I already track by hand. If it's got a status and a status date on a project in my ward, that's a fact I can check against my own scar sheet instead of rebuilding it from memory. My only worry: who's doing the curating, and how fast does a status get updated when something actually moves? If CDOT tells me something in a briefing and this roster still says "proposed" three months later, a resident's going to trust their own eyes over your card, and honestly they should.

**LR:** Sources and Methodology pages — full provenance catalog and how every number's computed.

**Marcus:** Good that they exist. Realistically I'm not reading the methodology page cover to cover — I'm the guy who clicks through to it for four minutes when someone's already yelling at me about a number, to see if I can find the flaw fast. It needs to answer "is this a 3-year window or 1-year, weighted how" in the first screen, not buried.

**LR:** Action page — 311, Bike Lane Uprising, alderman contacts, hearings, recent news.

**Marcus:** Fine, unremarkable, this is basically what our own ward newsletter already links to.

**LR:** And there's an obstructions preview page now — gated, watermarked — showing a synthetic, mock version of a Bike Lane Uprising-style obstruction layer, kept off the main maps and out of the API entirely, pending an actual data-sharing conversation with Bike Lane Uprising.

**Marcus:** Walk me through "synthetic" again — you mean the dots on that page aren't real obstructions, someone made them up to show what it would look like?

**LR:** Correct — it's a mock-up of the format, not real reports.

**Marcus:** Then I don't want it near me, and honestly I'm a little uneasy it exists at all, gated or not. Here's my nightmare: somebody on my staff, or god forbid a reporter, finds that page, doesn't read "synthetic" carefully, and screenshots a fake obstruction pin on a corner in my ward. Now I'm fielding a call about a blocked bike lane that never happened. I get that it's watermarked and behind a gate, but gates get walked through — a link gets forwarded, a screenshot loses its caption. If this ever touched a public page with my ward's name attached before it's real Bike Lane Uprising data, I'd tell my alder to have nothing to do with the whole site, full stop, because now everything else on it is suspect too. The real Bike Lane Uprising data — 65,000 reports, ticket values — I'd trust because it's crowdsourced by actual people reporting actual blocked lanes. A synthetic stand-in with the same schema, sitting one click away from my ward's one-pager? That's the kind of thing that, once burned, I don't come back from. I will say — gating it and pulling it off the real maps is at least the right instinct. Two years ago I'd have expected them to just ship it live with a small badge and call it done. This is better than that. It's just not good enough yet for me to relax about it.

### 4. Gap probing

**LR:** Scenario: you're briefing your alder before Thursday's committee vote — actually, let's use your CAPS meeting scenario, since that's the live one. You open OYL. What do you look for first, and where does it fail you?

**Marcus:** First click is the ward one-pager for my ward, obviously, if it existed with real news matching I trusted. Second thing I look for — and it's not there — is the corridor itself, before/after. I need "this specific half-mile, this specific intersection, crashes in the two years before the lane went in versus the two years after," for a comparable corridor somewhere else in the city that already did this. Ward-level rollups don't answer "what happens on THIS block." The findings page has "top corridors" but that's about which corridors are worst, not about before/after on a corridor that got treatment. That's the single biggest hole for my Thursday-meeting use case.

**LR:** Of everything OYL does not have, what single absence costs you most?

**Marcus:** No business-impact data. Every fight I'm in eventually has a merchant standing up saying this kills parking and kills business. I heard there's some CDOT sales-tax study — I've seen it referenced — but if it's not on this site in some form, I still can't hand my alder anything on the economic question, and that's the question that actually swings undecided people in the room, more than the crash number does. Crash data convinces people who already care about safety. Business data convinces the people who don't.

**LR:** If OYL handed you one export or artifact each week, what would it contain, and who would you forward it to?

**Marcus:** Honestly — a one-page PDF, auto-generated, ward-specific: this week's new crashes in my ward with location, any council or committee action touching my ward, any new news mention of my alder with a flag for whether it reads favorable or not, and menu-money spend-to-date versus what got promised. I'd forward that to my alder every Monday morning before she does her rounds. That's worth something. What I would NOT forward automatically is anything with a ranking or score on it — I'd want to preview that myself first, every time, before it goes anywhere near her.

**LR:** The site refuses to normalize by ridership — there's no counter or bikeshare-trip data, so raw crash counts aren't divided by how many people are actually riding. Does that caveat change how you'd use it? What would you accept as good-enough exposure data?

**Marcus:** Honestly, I don't think about "normalization" in those words day to day — but yes, it matters, because I already know the argument that's coming at me: "your ward just has more riders, of course it has more crashes, that's not a danger problem." If the site can't answer that, someone in the room will raise it and I'll have nothing. I don't need Strava-level precision. Something like: CDOT or Divvy trip-start counts near a corridor, or even a rough census-commute-mode-share number by ward, would be enough to say "no, per rider this is still worse," or to honestly concede "yeah, we just have more riders." Either answer is useful to me. Silence on it isn't — silence just means the other side gets to assert whichever version helps them, and I can't rebut it. And I'll say — I'd rather the site keep saying "we don't know" loudly than quietly bury a shaky per-rider number that falls apart the first time someone asks how it was calculated. At least the honest caveat, I can work with. A fake-precise number I can't defend is worse than no number.

### 5. Magic-wand close

**LR:** One dataset that doesn't publicly exist appears, clean and current. What is it?

**Marcus:** Real installed-infrastructure history with actual dates — when a lane went in, when it changed, whether it was ever downgraded or ripped out, like what happened on 18th. Right now everybody's arguing from memory and press clips about what got installed when. A clean timeline, ward by ward, would settle more arguments in my job than any crash number, because half of my fights are actually about "what did we already promise and did we deliver it," not "is this street dangerous."

**LR:** One chart or map you could put on a screen in front of your hardest audience that ends an argument.

**Marcus:** Side-by-side, same corridor, before-and-after a treatment went in somewhere comparable — crash count, and right next to it, storefront vacancy or sales-tax trend, same time window. Two lines, one screen. If I can show "this happened elsewhere, safety went up, business didn't die," that's the whole meeting won in one slide. I don't need a ward score for that. I need one corridor's story told twice, safety and money, at once.

**LR:** What would make you stop using a site like this after trying it once?

**Marcus:** Getting burned by it in front of my alder. If I hand her a printout and a reporter or a challenger has a different number from the same site — because it updated, or because I grabbed a mock layer by mistake, or because the "sponsorship record" turns out to be measuring something totally different from what I assumed — I'm done, and I'll tell every other chief of staff I know to stay away too. This world runs on reputation between offices. One bad citation and the whole tool is radioactive for us, doesn't matter how good the other 90% is.

---

## Analysis Memo

```
participant: chi-ward-office (Marcus Webb)
confidence_notes: Reactions to menu-money/311/sponsorship dynamics, aldermanic
  prerogative, and the CDOT-briefing workflow are well-grounded in the evidence
  brief and stayed in-character throughout. The BNA-score, agent-API, and
  network-map reactions are thinner — the persona has no documented stance on
  cycling-network benchmarking or AI-assistant tooling, so his reactions
  ("never heard of it," unease about a chatbot surfacing a number he didn't
  vet) are plausible extrapolations from his general triage-first,
  blindside-averse worldview rather than directly cited behaviors. His
  proposed-projects and exposure-data answers are reasonable in-world guesses
  invented for this interview, not sourced from the evidence brief, so treat
  them as illustrative rather than strong findings. The two mandatory
  quality-gate probes (mock obstructions, no-ridership-normalization) landed
  solidly in-character and are the highest-confidence material in this run.

stated_needs:
  - need: A pre-built, ward-specific "defensive brief" artifact assembled
      before a contentious community meeting (crash before/after on the
      specific corridor, comparable-ward outcomes, cost, business impact).
    evidence_quote: "By Wednesday: crashes on that corridor before/after,
      what nearby wards did, what it cost, and something about business
      impact — in a format your alder can absorb in the car."
    underlying_job: Arm the alderman to survive a hostile public meeting
      without being blindsided, in a format consumable in transit, not at
      a desk.

  - need: A weekly, forwardable, ward-scoped digest (new crashes, council/
      committee action, alderman news mentions with a favorability flag,
      menu-money spend-to-date vs. promised) that excludes any ranking or
      score without his own preview first.
    evidence_quote: "I'd forward that to my alder every Monday morning
      before she does her rounds... What I would NOT forward automatically
      is anything with a ranking or score on it — I'd want to preview that
      myself first, every time."
    underlying_job: Stay ahead of constituents, press, and challengers on
      the alderman's own record while retaining personal narrative control
      over anything reputationally loaded before it reaches her.

  - need: Corridor-level before/after crash comparison tied to a specific
      infrastructure treatment, not just ward-level rollups.
    evidence_quote: "Ward-level rollups don't answer 'what happens on THIS
      block'... That's the single biggest hole for my Thursday-meeting
      use case."
    underlying_job: Answer the exact question a hostile room will ask about
      a specific, named intersection — not the citywide or ward-wide trend.

  - need: A business-impact / economic-indicator counter to the "bike lanes
      kill business" objection, available per corridor.
    evidence_quote: "Every fight I'm in eventually has a merchant standing
      up saying this kills parking and kills business... if it's not on
      this site in some form, I still can't hand my alder anything on the
      economic question."
    underlying_job: Neutralize the recurring merchant objection with data
      the alderman can cite in real time, not just safety data.

  - need: Exposure/ridership context (even rough) to rebut the "your ward
      just has more riders" argument — but only if it is defensible, never
      a fabricated-precision substitute for an honest "we don't know."
    evidence_quote: "I'd rather the site keep saying 'we don't know' loudly
      than quietly bury a shaky per-rider number that falls apart the first
      time someone asks how it was calculated. At least the honest caveat,
      I can work with."
    underlying_job: Preempt a specific, anticipated rebuttal without taking
      on the greater risk of citing a number he cannot defend under
      questioning.

  - need: Real installed-infrastructure history with install/change/removal
      dates, ward by ward.
    evidence_quote: "A clean timeline, ward by ward, would settle more
      arguments in my job than any crash number, because half of my fights
      are actually about 'what did we already promise and did we deliver
      it.'"
    underlying_job: Adjudicate promise-vs-delivery disputes, which he frames
      as more common in his job than pure safety disputes.

latent_needs:
  - need: A pre-publication or private "preview my ward's page" workflow
      before ward one-pagers, rankings, sponsorship data, or news matches
      go live/update, so his office isn't blindsided by its own dashboard.
    inference_basis: He repeatedly frames every ranked, scored, or
      auto-matched artifact (table rankings, the one-pager's safety index,
      the sponsorship record, the news-matching layer) through "who sees
      this before I do" and "I need to get in front of it before it's on
      somebody's desk" — not through accuracy concerns alone, but through
      control-of-narrative concerns. He never asked for this feature; it
      falls out of his stated fear pattern across four separate stimulus
      reactions (table, one-pager, sponsorship record, news layer) plus his
      explicit weekly-digest carve-out for anything scored.
    risk_if_wrong: If his actual objection is purely about score
      methodology or match-precision (not about advance notice), building a
      preview/embargo workflow would be substantial engineering effort
      solving the wrong problem — the real fix might just be clearer
      methodology exposure and higher match confidence.

  - need: A visible, auditable distinction between "sponsorship count" and
      "recorded vote," ideally surfaced without him having to click into
      methodology to find it.
    inference_basis: Unprompted, he immediately interrogated what
      "sponsorship record" measures ("is it counting bills she co-sponsored,
      or did she vote against something... wildly different stories") before
      forming any opinion of the feature — a spontaneous credibility check,
      not a request. This mirrors his stated distrust pattern for 311 counts
      ("workload record, not a danger record").
    risk_if_wrong: If the feature already surfaces this distinction clearly
      (the inventory does label it "sponsorship proxy, not a vote tally"),
      this latent need may already be satisfied and the real gap is
      discoverability/prominence, not the underlying data model.

  - need: A confidence/precision indicator on automated name-matching (news
      layer, alderman matching) that he can check before trusting a match,
      distinct from the general tier badge system — including whether a
      matched article is favorable, unfavorable, or merely incidental to
      the alderman.
    inference_basis: He spontaneously raised a specific failure mode
      unprompted by the interviewer — wrong-alderman name collisions
      ("a totally different alder with a similar name") and
      favorable/unfavorable-context blindness — and tied it to a concrete
      personal cost ("that's the kind of error I get a call about from my
      alder at 9pm"), going further than a simple "I'd double check it"
      answer. He separately asked for a "favorable or not" flag on news
      mentions in his ideal weekly digest, reinforcing that the gap is
      valence, not just identity-matching accuracy.
    risk_if_wrong: His specific failure scenario (name collision) may be
      an artifact of Chicago's real aldermanic namesake patterns rather
      than a documented behavior in his evidence base; if the matching
      system already has near-zero collision risk, this concern may be
      lower-priority than his emphasis suggests.

  - need: Corridor-tagged, ward-tagged linkage between infrastructure grade,
      menu-money history, and the proposed-projects roster (which project,
      which fiscal year, what was promised vs. spent vs. built).
    inference_basis: He independently maintains a cross-office shared doc
      re-keying OBM PDFs specifically to compare menu-spend categories,
      separately says half his fights are "promise vs. delivered," wants
      an install-date timeline, and reacted to the new proposed-projects
      roster by immediately asking whether its status field would be
      checkable against his own hand-kept scar sheet — four independent
      workarounds/wants converging on the same underlying join (project →
      ward → spend → status → date) that OYL's data model does not yet
      make explicit.
    risk_if_wrong: This may overlap heavily with the stated "installed-
      infrastructure history" magic-wand need rather than being a truly
      separate latent need — could be double-counting one underlying gap.

  - need: A visible update-cadence/freshness signal specifically on the new
      proposed-projects roster, since staleness there (not just inaccuracy)
      is what he expects to get caught out by.
    inference_basis: His only stated concern about the roster was not
      "is the curation biased" but "how fast does a status get updated
      when something actually moves... if a resident's going to trust
      their own eyes over your card, and honestly they should" — he
      volunteered the freshness failure mode without being asked about
      update frequency.
    risk_if_wrong: If the roster already updates on a fast, visible cadence
      (e.g., the weekly refresh cycle documented in the inventory), this
      need may already be met and the real gap is just surfacing the "last
      checked" date more prominently on the card itself.

  - need: Acknowledgment that gating/quarantining a synthetic layer (as OYL
      now does with the obstructions preview) is a partial trust repair,
      not a full one — he registers the change positively relative to a
      hypothetical worse design, which suggests incremental provenance
      improvements are legible to this audience and worth surfacing
      explicitly rather than assuming distrust is binary.
    inference_basis: Unprompted, he contrasted the current gated/watermarked
      design favorably against what he "expected" (a live badge-only
      version), saying "this is better than that" while still maintaining
      the layer as a deal-breaker risk — a nuanced, two-part reaction
      rather than a flat rejection.
    risk_if_wrong: This is a comparatively low-stakes, low-confidence
      inference — it rests on a single aside in an otherwise strongly
      negative reaction, and could simply reflect generic construction
      politeness within an otherwise resistive interview rather than a
      genuine, generalizable signal about incremental trust-building.

reactions_to_existing:
  - feature: Transportation map (map.html)
    verdict: would-use
    why: Plausible stand-in for squinting at CDOT PDFs in a live meeting;
      no resistance expressed.
  - feature: Network map (network.html) / schematic transit-style map
    verdict: ignores
    why: "I don't know what I'd do with that in my job"; reads it as built
      for advocates, not for his room; explicitly rejects the vocabulary
      ("comfort floor") as unusable in a CAPS meeting.
  - feature: Home / orientation page + "ask an AI assistant" agent-layer
      messaging
    verdict: ignores (first visit only) / distrusts the implication
    why: Rates it as fine for a first-time visitor but not something he'd
      return to; unprompted, reframes the AI-assistant framing as a new
      blindside vector — a number he never vetted reaching his alder or a
      reporter through a chatbot instead of through him.
  - feature: Findings cards (KSI trend, corridors, ward concentration,
      dooring undercount)
    verdict: would-use
    why: Directly maps to the slide he already builds by hand; would
      screenshot into briefings.
  - feature: PeopleForBikes BNA citywide score
    verdict: distrusts / misreads
    why: Unfamiliar with the metric; immediately reframes it as a
      blindside risk ("is Chicago 40th out of 100... if a reporter's got
      that number and I don't"). Never engages with what the score
      actually measures — treats any unfamiliar ranking as a press threat
      by reflex.
  - feature: Ward table + CSV export (sortable rankings)
    verdict: distrusts (CSV itself: would-use)
    why: Wants raw numbers for his own framing but rejects the public,
      sortable, rankable presentation as a "press release waiting to
      happen."
  - feature: Ward one-pager (ward.html)
    verdict: would-use AND distrusts simultaneously
    why: Format matches his exact defensive-brief workaround (saves him
      hours), but the bundling of safety index + sponsorship record +
      auto-matched news on one public, alderman-attributed URL reads as a
      third party publishing a report card on his boss he doesn't control.
  - feature: Alderman sponsorship record
    verdict: distrusts
    why: Immediately probes whether it's a sponsorship-count proxy or an
      actual vote tally, per his evidence-based distinction between
      "co-sponsored" and "voted no" — anticipates a challenger
      weaponizing the ambiguity.
  - feature: News-coverage layer (ward/alderman-matched)
    verdict: distrusts
    why: Names it as the single most worrying new feature — fears mismatched
      or context-blind matches (wrong alderman, unfavorable article
      surfaced without framing) landing on a page bearing his alderman's
      name.
  - feature: Proposed & in-progress projects roster
    verdict: would-use, conditionally
    why: Maps directly onto his hand-kept "promised vs. delivered" scar
      sheet; would check status/status-date against his own record, but
      distrusts it if the update cadence lags what he hears in CDOT
      briefings.
  - feature: Sources / Methodology pages
    verdict: would-use (narrowly)
    why: Values their existence as a rebuttal tool but would only consult
      them reactively, under fire, for the specific weighting/window
      question — not read proactively.
  - feature: Action page (311, BLU, alderman contacts, hearings, news)
    verdict: uses
    why: "Basically what our own ward newsletter already links to" — low
      excitement, unsurprising, already-familiar territory.
  - feature: Obstructions preview page (mock, gated, watermarked)
    verdict: distrusts (strongly — flagged as a deal-breaker category),
      with qualified acknowledgment of the gating as a partial improvement
    why: Immediately worried about a screenshot escaping the gate/watermark
      and being mistaken for a real obstruction in his ward; states this
      single failure mode alone would end his office's use of the entire
      site, not just this layer — while separately conceding the
      gated/quarantined design is better than the live-badge-only version
      he expected.
  - feature: No-ridership-normalization caveat
    verdict: uses (as an anticipated rebuttal, wants it filled — but
      explicitly prefers the honest caveat over a shaky substitute number)
    why: Does not use "normalization" as a term, but immediately maps the
      caveat onto a specific, already-anticipated opposing argument
      ("your ward just has more riders") and says silence on it costs him
      the room; would accept rough proxies (trip-start counts, commute
      mode share) as good enough, but explicitly ranks an honest "we don't
      know" above a fake-precise number he couldn't defend.

data_they_bring: A hand-built, block-level crash spreadsheet pivoted from
  the city crash portal by lat/long box (since there's no clean corridor
  filter); a running 311-complaint log by block used to counter "nobody
  complains about that corner"; a cross-office shared doc re-keying OBM
  menu-spend PDFs year over year (because the PDFs can't be diffed);
  a screenshots-by-year archive of press mentions of the alderman, kept
  for fast retrieval under a reporter's deadline.

deal_breakers: (1) Any mock/synthetic layer (the obstructions preview)
  being mistaken for real data and attributed to his ward, even once,
  even behind a gate — he says this alone ends his office's trust in the
  whole site. (2) Being blindsided by a reporter, challenger, neighboring
  office, or now an AI assistant citing a number from the site that his
  own office didn't have first, especially a ranking, score, or news
  match. (3) An ambiguous or misleading derived metric (sponsorship count
  read as a vote record) being weaponized by name against his alderman.
  (4) A fabricated-precision exposure/ridership number offered in place of
  an honest data gap — he would rather the site say nothing than say
  something indefensible.

vocabulary: constituents, "the ward," menu / menu money, CDOT, "the
  commissioner," committee, "my alder," briefing, one-pager, "the
  community process," CAPS meeting, ward night, "we got forty calls,"
  precinct, prerogative, "workload record" (his own coinage for 311, in
  deliberate contrast to "danger record"), "press liability," "blindside."
  He never adopts interviewer terms like "danger index," "normalization,"
  "agent layer," or "comfort floor" — flags "comfort floor" explicitly as
  meaningless outside advocacy circles and treats "agent layer" purely as
  the interviewer's jargon, translating it back to "an AI assistant
  answering questions" in his own words.
```
