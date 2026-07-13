# Interview: us-bna-analyst (PFB BNA proposal validation)

## 1. Context re-anchor

**Interviewer:** Before I show you anything — think about the last time you had to characterize the *quality* of a bike network, not crashes on it. Walk me through that.

**Dana:** Three weeks ago, actually, different engagement than the last one I told you about — a regional MPO asked me to help them figure out whether their "Complete Streets" self-assessment was worth anything. They'd scored themselves against a checklist their own staff wrote: does the corridor have a bike facility, yes or no. No stress classification, no connectivity question, just a binary. I pulled our BNA numbers for their three biggest member cities as a sanity check — none of them cracked 20, which if you know the scale means the low-stress network isn't really connecting anyone to anything yet — and their self-assessment had all three cities north of 70% "complete." That gap is the whole job, honestly. A facility existing and a facility being low-stress enough that an eight-year-old could ride it to school are two completely different claims, and checklists conflate them constantly. I spent most of that meeting explaining why "has a bike lane" isn't a quality metric, it's an existence metric.

**Interviewer:** And who were you answering to in that room?

**Dana:** Their planning director and one board member who represents a suburb that had scored itself well and did not want to hear otherwise. Same two audiences as always — methodology for staff, one defensible number for anyone elected.

## 2. Product recap

**Interviewer:** Let me ground you in what On Your Left actually is today, quickly, before I show you anything new. It's a Chicago-only, read-only bike-safety dashboard — crash points since 2017, the CDOT bikeway network graded by facility type, a ward table with coverage percentages, a findings page with sourced stat cards, and a derived ward safety index blending crash rate and bikeway-mile rate. Everything's tier-badged real, proxy, mock, crowdsourced, derived, or no-data-yet. No ridership data anywhere. That's the baseline you already reacted to once. Today I want to show you something they're considering adding on top of it.

**Dana:** Right, I remember the tour — the coverage columns I liked, the ward index I didn't, the mock obstruction layer I hated. Go ahead.

## 3. Stimulus walkthrough

### B1 — Citywide BNA scorecard

**Interviewer:** First piece. They'd pull PeopleForBikes' own City Ratings numbers — Chicago scored 11 out of 100 in 2026, national average is 36, and they'd publish a findings card: "6,267 miles of high-stress streets, 1,834 low-stress," with a trend line and a caveat that it's a third-party score computed from OpenStreetMap, measuring the network, not riders. What's your first reaction?

**Dana:** Immediate reaction: finally, somebody's citing an actual methodology instead of inventing one. That's my own field's number — I've pulled that exact cities-index endpoint for client comparisons more times than I can count. My gut says this is the single lowest-risk, highest-credibility thing on this whole list, because they're not computing anything, they're attributing. I'd use it tomorrow — it's exactly the kind of shocking top-line stat that survives a hostile question, the same job my "6% of the network, half the severe crashes" line does. "Eleven out of a hundred, national average thirty-six" doesn't need defending, it just needs a link to PFB's methodology page, which apparently it has.

**Interviewer:** What would you check before you'd put that card in front of a client?

**Dana:** Two things. First, which population tier Chicago's being compared against — BNA groups cities small, medium, large, and if that "national average of 36" is blended across all city sizes rather than Chicago's large-city peer group, that's a materially different comparison and I'd want the large-city number specifically before I cite it, because the first thing a sharp staffer does with a shocking stat is ask "compared to what." Second — you said trend line 2023 to 2026, but I only know of three data points, 2024, 2025, 2026 — nine, eleven, eleven-point-oh-eight. Where's the 2023 number? Either Chicago wasn't analyzed that year, in which case don't draw a line implying continuous history back to 2023, or there's a fourth number I haven't seen. That's a small thing, but it's exactly the kind of small thing that gets a whole card thrown out in a room with someone like me in it.

### B2 — Ward-level access scores

**Interviewer:** Next. Annual snapshot of PFB's census-block access scores, spatial-joined into wards, published as: "In Ward 35, X% of residents live on blocks with low-stress bike access to a grocery store." Framed as access, explicitly not a 0-100 danger ranking.

**Dana:** Okay, this is the one that actually worries me, and I want to say that plainly before I say anything positive. The access framing itself — genuinely good instinct, and I mean that, "access not danger" is exactly the lesson they should have taken from whatever killed the ward-danger-ranking version of this idea, because block-level connectivity really is a different claim than crash risk and conflating them was always going to blow up on someone eventually. So credit where it's due.

But here's my problem: BNA's whole value proposition is that connectivity is *hyperlocal*. A block two hundred feet from an arterial with no crossing can score near zero while the block behind it scores eighty, because one has a safe way across and one doesn't. The second you average that up to a ward — fifty thousand people, dozens of block-group variations — you've smoothed away the exact granularity that makes the metric mean anything. So my first question is always going to be: is that ward percentage a population-weighted average of block scores, or a simple mean, or something else, because those three answers can produce meaningfully different numbers for the same ward, and "X%" sounds precise in a way that hides a real methodology choice underneath it.

**Interviewer:** Say more about the worry, not just the methodology question.

**Dana:** The worry is what happens to that number six months after publication, in a room I'm not in. "Access framing, not a ranking" holds up exactly as long as everyone who touches the number reads the footnote. I've watched this movie before — you called it yourself, the original ward safety index, my own line was "a political-will score wearing a danger score's clothes" cited in a menu-money fight. A ward percentage is one screenshot away from becoming "Ward 35 only gives 40% of residents grocery access, worst in the city" in a press release, framing be damned, and once that happens nobody's going back to check whether it was population-weighted.

### B3 — Segment stress cross-check

**Interviewer:** Third. They'd pull PFB's per-segment stress classification — every street, not just bikeways — and buffer-match it onto the existing bikeway geometry, twenty-five meter tolerance, same technique they used to dedupe the Mellow layer. Where OYL calls a street "protected" but BNA still rates it high-stress, they'd flag the disagreement as a finding.

**Dana:** Now we're at the thing I actually asked for. Last time I saw this dashboard, the transit-diagram map had a "quality border" I mistook for a stress overlay, and when it turned out to just be facility category I told your researcher, verbatim, that if that border ever became a real LTS gradient I'd put a screenshot in a deck. So — immediate reaction — this is closer to that than anything else on today's list, and I want to be honest that I'm predisposed to like it.

That said, cross-examining it: buffer-match at twenty-five meters, on a dense urban grid with service drives and frontage roads running parallel to arterials a block apart, is exactly tight enough to be right most of the time and exactly loose enough to occasionally attribute a stress value from the wrong parallel street. I'd want to know their false-match rate, or at minimum see a handful of spot-checked segments before I trusted the flag logic citywide. And second — is "high-stress" here a true LTS 1-through-4 classification the Mekuria/Furth/Nixon way, or a binary bucket PFB reduced it to for the public files? Because "our protected lane sits on an LTS 3 street" and "our protected lane sits on an LTS 4 street" are very different findings and I don't want them both flattened into one flag icon.

**Interviewer:** And the finding itself — "N miles of bikeways sit on streets BNA still rates high-stress" — useful to you?

**Dana:** Extremely, if it survives my two questions above. That's a genuinely new capability, not a repackaging — nobody's handed me a stress grade for a Chicago street that doesn't already have a bike facility, and getting that for every street, not just the ones CDOT built something on, is the actual BNA connectivity question my clients ask me and that this dashboard currently can't answer at all. I said that explicitly last time — "there's nothing on this site that answers it" — so this is the fix for the exact gap I named.

### B4 — Peer-city strip

**Interviewer:** Last one. Same cities-index pull covers about three thousand cities — a findings-page comparison of Chicago against self-selected peers, NYC, LA, Philadelphia, Minneapolis, Seattle, same run.

**Dana:** Honestly? Shrug. Not because it's bad — it's fine, it's free, it rides on B1's pull. But I already do this myself, it's the same endpoint I've pulled for a decade of comparison-city slides, and picking five peer cities off the top of my head takes me ninety seconds in a spreadsheet. This doesn't save me anything I'm currently paying a cost for. If a reader who isn't me sees "Chicago: 11, Minneapolis: 45" and that reframes their sense of how bad eleven actually is, fine, that's a real public-communication value — but as a working tool for my job specifically, this is the one item today I'd never open twice.

## 4. Trust probes

**Interviewer:** Four things I need every persona to react to. First: it's computed from OpenStreetMap by a national advocacy org, updated once a year, only as current as volunteer mapping. Does that change anything for you?

**Dana:** Doesn't surprise me — I already know this about BNA, I've said the phrase "PFB runs mapathons because unmapped infrastructure lowers scores" to clients before. What I'd push OYL to say louder than they probably plan to: OSM mapping density in Chicago is not evenly distributed. Volunteer mappers cluster where volunteer mappers already live and bike, which correlates suspiciously well with the same North Side neighborhoods that already have better-mapped everything else. If a South or West Side block scores high-stress partly because nobody's gotten around to tagging a protected lane that's physically there, that's not a network gap, that's a mapping gap wearing a network gap's clothes — and it would land directly on top of the wards the rest of this dashboard already documents as underinvested. That's the "who's not in this data" question, just for infrastructure instead of crashes. If OYL runs with a BNA finding and doesn't say that part loudly, they risk reinforcing the exact inequity narrative they mean to expose, for the wrong reason.

**Interviewer:** Second: Chicago scores 11 out of 100. Does that number help you or hurt you?

**Dana:** Helps, same category as my HIN line — small, shocking, survives a hostile question. The risk isn't the number, it's an unprepared staffer getting asked "eleven out of what possible" and not having the peer-tier answer ready, which is my B1 concern again. Handled right, it's ammunition. Handled without the population-tier context, it's a number someone gets embarrassed by in a meeting and blames the dashboard for.

**Interviewer:** Third: the ward number is framed as access, not a danger ranking. React.

**Dana:** Correct call, said so already. My only addition: framing choices don't survive contact with a headline writer. "Access, not danger" is the right instinct in the copy; it doesn't control what a reporter or a council staffer does with the percentage once it's out of context. I'd want it stated on every surface, not just the first one, the way OYL apparently already does its tier badges.

**Interviewer:** Fourth: where OYL's own facility grade disagrees with BNA stress, which do you believe, and what should the site do about it?

**Dana:** Neither one, categorically — I believe the disagreement itself, and the site should publish it as the finding rather than resolving it. Do not average them, do not quietly defer to whichever one is newer, do not pick a winner in the backend and only show me the winner. The disagreement is the data point — it either means the facility type on record is wrong, the BNA stress calc is working off stale or unmapped geometry, or the street genuinely has a protected lane sitting on an objectively high-stress corridor because the intersections are still terrible. Those are three different findings with three different fixes, and collapsing them into one reconciled number is the same failure mode as a vendor quietly blending two data sources and showing me one clean line. I've walked out on vendors for less.

## 5. Forced choice

**Interviewer:** Rank B1 through B4 for your own work.

**Dana:** B3 first, by a wide margin — it's the only one that gives me a capability I don't already have anywhere, a real stress grade on every street, not just the ones with facilities. B1 second — trivial to build, immediately citable, I'd use it in a deck this month. B2 third — real potential value, the access-deserts framing is the right instinct, but I'd want the granularity and weaponization questions answered before I'd cite a ward percentage in front of anyone. B4 last — nice for a reader, does nothing for my actual workflow that I can't already do myself in under two minutes.

**Interviewer:** Should OYL skip this entirely and put the effort elsewhere? Name the elsewhere.

**Dana:** No, don't skip it — B1 and B3 in particular are cheap relative to what they return. But if you're asking me to rank this against everything else OYL could spend a quarter on, I'd send the marginal hour toward exposure data before toward B2's ward rollup specifically — a single Divvy or Strava Metro pull, even with the skew caveat stated up front, does more for the site's core numerator-without-a-denominator problem than another ward percentage does. BNA integration is a real, additive improvement. It is not the thing that fixes the biggest hole in this dashboard, which is still that every crash number on it has no rider count under it.

## 6. Kill question

**Interviewer:** Last one. What single thing about this integration, done wrong, would make you stop trusting the site?

**Dana:** Silently reconciling the disagreement in B3 — picking one grade over the other in the pipeline and only ever showing me the merged result, with no visible flag that a disagreement even existed. That's not a hypothetical for me, it's the same pattern as a mock layer getting quietly promoted to real without a changelog note, which I already told you would burn every badge on the site retroactively for me, not just the one feature. The entire reason I'd trust this integration at all is that it's coming from a published, citable, independent methodology instead of something OYL invented — the moment they start editorializing between their number and PFB's number without telling me, I've lost the one thing that made this proposal different from the ward safety index I already don't trust.

## Analysis memo

participant: us-bna-analyst
confidence_notes: The persona stayed internally consistent with the original study's transcript — she referenced her own prior lines ("political-will score wearing a danger score's clothes," the schematic-map LTS misread, "who's not in this data") accurately and used them to license new reactions rather than restating them decoratively, which is the behavior that made the original interview credible. The B1 fact-check (three cited data points vs. a trend line implying a fourth) and the 3,944-vs-3,945-mile discrepancy she'd be primed to catch (flagged below as a latent need, since the stimulus as presented to her didn't surface the second number directly) both read as authentic "denominators or it didn't happen" behavior rather than invented nitpicking — they follow directly from her documented reflex of cross-examining any number before citing it. One soft spot: her population-tier-grouping objection to the national-average comparison is methodologically correct per the evidence base (BNA groups small/medium/large cities) but she asserts the specific mechanism with more confident precision than the evidence base actually states the grouping's effect on the "36" figure — plausible for a specialist, flagged as moderate confidence. No answer required knowledge outside her documented evidence base; the OSM-mapping-equity connection (B2/B3 worry) is a direct, licensed extension of both her own "who's not in this data" instinct and the evidence base's explicit note that "PFB themselves run OSM mapathons... Chicago's score is only as current as OSM tagging."

stated_needs:
  - need: The national-average comparison in B1 broken out by BNA's population-size tier (small/medium/large), not a single blended "36"
    evidence_quote: "which population tier Chicago's being compared against... if that 'national average of 36' is blended across all city sizes rather than Chicago's large-city peer group, that's a materially different comparison"
    underlying_job: Needs the comparison number to survive a staffer's first follow-up question ("compared to what?") without having to caveat it live in the room.

  - need: The B1 trend line's date range matched exactly to the data points actually cited (no implied history the source doesn't back)
    evidence_quote: "you said trend line 2023 to 2026, but I only know of three data points, 2024, 2025, 2026... Either Chicago wasn't analyzed that year... or there's a fourth number I haven't seen."
    underlying_job: Needs every axis label and date range on a citable chart to be independently verifiable against the underlying source before it goes in front of a hostile audience.

  - need: Disclosed spatial-join methodology for the B2 ward percentage (population-weighted average of block scores vs. simple mean vs. other)
    evidence_quote: "is that ward percentage a population-weighted average of block scores, or a simple mean, or something else, because those three answers can produce meaningfully different numbers for the same ward"
    underlying_job: Needs to defend the aggregation choice specifically, not just the source data, since he already knows ward-level rollups get cross-examined on their blend logic.

  - need: A stated false-match / spot-check rate for the B3 buffer-match between BNA segment stress and OYL's bikeway geometry
    evidence_quote: "buffer-match at twenty-five meters... is exactly loose enough to occasionally attribute a stress value from the wrong parallel street. I'd want to know their false-match rate, or at minimum see a handful of spot-checked segments"
    underlying_job: Needs assurance the cross-check flag isn't itself introducing false positives before citing "N miles of bikeways sit on high-stress streets" as a finding.

  - need: The true LTS 1-4 classification (Mekuria/Furth/Nixon scale) preserved in the B3 cross-check, not flattened to a single high-stress/low-stress binary flag
    evidence_quote: "is 'high-stress' here a true LTS 1-through-4 classification... or a binary bucket PFB reduced it to for the public files? Because 'our protected lane sits on an LTS 3 street' and 'our protected lane sits on an LTS 4 street' are very different findings"
    underlying_job: Needs granularity fine enough to distinguish "marginally high-stress" from "severely high-stress" facility conflicts, since the two imply different capital fixes.

  - need: Disagreements between OYL's own facility grade and BNA segment stress published as a standalone finding, never silently averaged or resolved to one value
    evidence_quote: "Do not average them, do not quietly defer to whichever one is newer, do not pick a winner in the backend and only show me the winner. The disagreement is the data point"
    underlying_job: Needs to see and interpret raw source conflict himself (mapping gap vs. stale facility record vs. genuinely bad intersection) rather than trust an editorial judgment call baked into the pipeline.

latent_needs:
  - need: An explicit statement that OSM mapping density in Chicago is spatially uneven, and that this unevenness plausibly tracks the same disinvested wards the rest of the site already documents as underserved
    inference_basis: Unprompted extension of the OSM-currency trust probe: "OSM mapping density in Chicago is not evenly distributed. Volunteer mappers cluster where volunteer mappers already live and bike... If a South or West Side block scores high-stress partly because nobody's gotten around to tagging a protected lane that's physically there, that's not a network gap, that's a mapping gap wearing a network gap's clothes." This is the same reflex documented in round one (she treats "who's not in this data" as a first-order concern for crash undercounting) applied without being asked to a completely different data source — evidence it's a general-purpose reflex, not a scripted crash-data answer.
    risk_if_wrong: If OYL cites a BNA-derived access or stress gap without this caveat, it risks manufacturing a false equity finding — attributing to real infrastructure absence what is actually a mapping-currency artifact — which is a more damaging failure than a null result, because it would misdirect advocacy attention toward the wrong fix (get it mapped, not get it built).

  - need: A single, sitewide-consistent surface for "which number wins" language whenever OYL and a third-party source disagree, generalized beyond just B3
    inference_basis: Her kill-question answer explicitly generalized past B3's specific case: "the moment they start editorializing between their number and PFB's number without telling me, I've lost the one thing that made this proposal different from the ward safety index I already don't trust" — she is pattern-matching this to her round-one deal-breaker about mock-to-real badge promotion without a changelog, showing she expects one consistent site-wide disclosure norm for any source conflict, not a one-off fix scoped to the stress cross-check.
    risk_if_wrong: A norm built only for B3 leaves every future third-party integration (peer benchmarks, future exposure data) exposed to the same trust failure one at a time, rather than solved once; for this participant specifically, one violation anywhere retroactively discredits tier badges sitewide, per her own stated logic.

  - need: Cross-reference / audit checks between OYL's own published numbers when two pages state the same denominator differently
    inference_basis: Not directly probed, but licensed by her documented behavior pattern: in the original interview she asked unprompted whether "3,945 centerline miles" was a real total or an approximation before trusting it on a slide, and her working method (`denominators.xlsx`, source-flag columns) exists specifically to catch inconsistent denominators across sources. The stimulus material itself carries this exact flaw — the findings-card copy in `02-data-inventory.md` states "3,944 mi of surface streets" while the coverage-metrics row two lines later states the denominator is "3,945 centerline miles" — a one-mile discrepancy between two of OYL's own pages. A participant with her documented reflex would catch this the moment she cross-referenced the two pages, even though this interview's stimulus presentation didn't put both numbers in front of her at once.
    risk_if_wrong: Low-probability but high-cost for this specific user type: if she ever opens both pages in the same session (which her working method makes likely — she already said she'd export the table CSV into her own cross-referencing spreadsheet), an internal inconsistency this small is enough, by her own stated logic, to make her stop trusting a card "on sight" the way she does the ward index.

reactions_to_proposal:
  - element: B1 — Citywide BNA scorecard
    verdict: would-use
    why: "The single lowest-risk, highest-credibility thing on this whole list" — pure attribution of her own field's published number, immediately citable. Conditional on population-tier context for the national average and an exact match between the trend line's date range and the actual cited data points.

  - element: B2 — Ward-level access scores
    verdict: distrusts (conditionally would-use)
    why: Approves of the access-not-danger framing as the correct lesson from the original ward-index feedback, but is explicitly worried the ward-level aggregation smooths away BNA's core value (hyperlocal connectivity) and that "access framing" will not survive contact with a headline or a council screenshot regardless of the copy — names this as her single biggest proposal-level worry.

  - element: B3 — Segment stress cross-check
    verdict: would-use
    why: Directly answers a gap she named unprompted in the original study ("if that border actually became a stress gradient... I'd absolutely put a screenshot of it in a deck") — the only element that gives her a capability she doesn't already have elsewhere. Conditional on buffer-match accuracy disclosure, true LTS granularity (not a binary), and disagreements with OYL's own facility grade being published as findings, never silently reconciled — the latter is also her kill-question answer.

  - element: B4 — Peer-city strip
    verdict: ignores
    why: "The one item today I'd never open twice" — she already pulls the same cities-index endpoint herself for comparison-city work in under two minutes; concedes public-communication value for a lay reader but states it adds nothing to her own workflow.

data_they_bring: The same BNA cities-index pull she already uses for client comparison-city slides (making B4 redundant for her specifically); working knowledge of BNA's population-size tier grouping (small/medium/large) that a bare "national average" figure omits; the Mekuria/Furth/Nixon LTS 1-4 scale as her reference granularity for any stress classification; a standing reflex (demonstrated, not stated) of cross-referencing denominators across sources/pages before citing either one, the same reflex that produced her round-one "3,945 centerline miles... does it include alleys" question.

deal_breakers: (1) OYL silently resolving a disagreement between its own facility grade and BNA's segment stress — averaging, deferring to the newer source, or otherwise picking a winner in the pipeline without surfacing the conflict — named explicitly as equivalent to the mock-badge-promotion deal-breaker from the original study and as the thing that would make her stop trusting the entire integration, not just B3. (2) A ward-level access percentage (B2) getting cited publicly as a ranking or "worst in the city" claim without the access-not-danger framing attached — she predicts this will happen regardless of how OYL words the copy, and treats it as a live risk rather than a hypothetical, consistent with her round-one account of having already watched a comparable number get weaponized in a menu-money fight.

vocabulary: LTS / Level of Traffic Stress, LTS 1 through 4 (Mekuria/Furth/Nixon), low-stress vs. high-stress, connectivity, "tipping point" (BNA score-50 usage, referenced but not re-explained), population-size tier (small/medium/large city grouping), "a mapping gap wearing a network gap's clothes" (coined this interview, mirrors her round-one "political-will score wearing a danger score's clothes"), buffer-match / false-match rate, "who's not in this data" (extended from crash undercounting to OSM mapping currency), denominator, exposure, "the disagreement is the data point."
