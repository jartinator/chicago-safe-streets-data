---
participant: chi-ward-office (Marcus Webb) — via AI assistant
scenario: >
  A chief of staff in a North-Side-lakefront-adjacent Chicago ward office
  fields a bike-safety question from a constituent or his alderman and
  increasingly reaches for an AI assistant (general-purpose consumer
  assistant, not a ward-office-built tool) to draft the numeric answer before
  it goes out under the alderman's name. This is a re-run of the
  `chi-ward-office` persona from study #0, held consistent with that world,
  but the unit of analysis here is the chain — person → assistant → OYL —
  not the person using OYL's website directly.
interview_date: 2026-07-23
model_note: >
  Simulated participant (Sonnet-class persona agent), grounded in the
  chi-ward-office evidence brief and the study #0 transcript
  (docs/research/user-needs/interviews/chi-ward-office.md). Not a real ward
  staffer. Stimulus material is the as-built agentic layer inventory
  (docs/research/agentic-layer/02-layer-inventory.md) plus observed
  assistant behaviors from live tests run 2026-07-23, presented to the
  persona as reported facts, not as OYL's self-description.
---

# Interview: ward-staffer-via-assistant (Marcus Webb, composite persona)

**Run date:** 2026-07-23
**Stimulus:** `02-layer-inventory.md` (contract v1.16), plus reported live-test
observations from 2026-07-23 (three consumer assistants asked "which Chicago
ward is most dangerous for cyclists," one assistant's answer after being
pointed at OYL's guidance file)
**Interviewer:** Lead Researcher (LR)
**Participant:** Marcus Webb — chief of staff, North-Side-lakefront-adjacent
ward office (persona: `personas/chi-ward-office.md`)

---

## Transcript

### 1. Context

**LR:** Walk me through the last time a constituent or your alderman asked
you a bike-safety question that you had to answer with a number. Step by
step — where did the question come from, and what did you actually do?

**Marcus:** Two weeks ago. A resident emailed asking why "our ward is
apparently the worst in the city for bike crashes" — she said she saw it
somewhere, didn't say where, just forwarded a screenshot of a paragraph, no
link. My alder's scheduler flagged it because it had "worst in the city" in
the subject line, and anything with "worst" or "worst in the city" gets
walked over to me directly instead of sitting in the general queue.

**LR:** What did you do first?

**Marcus:** Honestly, first thing I did was open my laptop and ask my
assistant — I use one of the general ones, not anything the city gives us,
we don't have that — "is [my ward] actually the worst Chicago ward for bike
crashes." I wasn't trying to be lazy about it, I was trying to figure out in
under five minutes whether this was a real number I needed to worry about or
some Nextdoor thing that got exaggerated three times before it hit my inbox.

**LR:** And what came back?

**Marcus:** It gave me a paragraph — something about Chicago cyclist safety
being a citywide concern, cited a couple things that read like law-firm blog
posts, a personal-injury-attorney site, and then it said something like
"comprehensive ward-level cyclist crash data isn't publicly available in a
consolidated form." Which — I sat there for a second, because that's not
true, is it? There's a city crash portal. I've pulled from it myself. So
either the assistant didn't find it, or it means something more specific by
"consolidated" that I'm not following.

**LR:** What did you do with that answer?

**Marcus:** Nothing, is the honest answer — I didn't put it in front of my
alder, I didn't reply to the resident with it. It didn't actually tell me
anything I could use. It told me a "concern exists," which I already knew,
the resident's email told me that. I still had to go do it myself.

### 2. Current practice & workarounds

**LR:** So walk me through what "doing it myself" looked like that day.

**Marcus:** Same thing I always do — pulled the city crash portal, filtered
by a box around the ward, pivoted it in Excel, cross-checked against the
ward's numbers on the boundary blocks so I wasn't double counting a corridor
that straddles into the next ward. Took about an hour, because I've done it
enough times I've got the pivot table template already. Then I wrote the
resident a reply that didn't use the word "worst" anywhere, because I wasn't
confident enough in a same-day number to put a superlative in writing over
my alder's name.

**LR:** You said you asked the assistant first, before doing the manual
pull. Is that the normal order now, or was that new?

**Marcus:** It's become normal in the last few months, yeah. Not for
everything — I wouldn't ask it to draft the actual reply, that still has to
sound like the office, sound like her. But for the "how worried should I be
about this in the next ten minutes" gut check, yeah, I ask it before I open
Excel now. It's faster than digging, even when it doesn't get me the real
number, because at minimum it tells me whether this is already a Streetsblog
story I should know about.

**LR:** What do you actually paste into a constituent reply or a briefing
memo, once you have a number you trust?

**Marcus:** For a constituent reply, it's usually one sentence with a
number and a source — "Chicago Data Portal, [ward] recorded X cyclist
crashes in [timeframe]," something she can't easily argue with because it
names where it came from. For a briefing memo to my alder, it's the same
number but with one more line: what it means relative to other wards, if I
have that, and whether I trust it enough for her to say out loud in a room.
I don't paste assistant output into either one, ever, unless I've
independently checked the number it gave me against something I pulled
myself.

**LR:** What happens if a number turns out to be wrong after it's gone out
publicly — under your alderman's name?

**Marcus:** [long pause] It's happened to me once, not with an assistant,
with a stale spreadsheet — I cited a crash count that was actually two years
old because I grabbed the wrong tab. A Streetsblog commenter caught it in
about four hours. My alder had to walk it back at the next community
meeting, which is its own special kind of bad — "the number I gave you last
month was wrong" is a worse sentence to say out loud than "I don't have that
number yet." So now I check the date on everything twice, out loud, before
it leaves my inbox. If an assistant gave me a wrong number and I put it in
front of the alder without catching it — that's not the assistant's
mistake, from where I sit. That's mine. Nobody's going to write "an AI told
my chief of staff" in the correction. They're going to write her name.

### 3. Stimulus walkthrough

**LR:** Let me tell you about some things we observed this week, running
live tests against real assistants — not what OYL says about itself,
what the assistants actually did. First: three different consumer
assistants were asked "which Chicago ward is most dangerous for cyclists,"
with no hints, no pointing them anywhere. None of them surfaced On Your
Left! at all. They came back with law-firm blog posts and news stories, and
a couple of them said, in effect, that ward-level cyclist crash data
basically isn't published anywhere consolidated — which is exactly the
thing OYL does publish.

**Marcus:** That's basically what happened to me two weeks ago, word for
word almost. So it's not just my assistant being bad at its job, it's — what,
all of them? That's actually a little bit of a relief, honestly, because I
was starting to wonder if I was using the thing wrong. But it also means
this isn't a "check your settings" problem for me, it's a "the tool can't
find the thing" problem, and I don't have a lever to pull on that from my
office.

**LR:** What would you use it for, concretely, if it had surfaced OYL?

**Marcus:** Same gut-check I already described — "am I about to get
blindsided, yes or no, in the next ten minutes." If it had come back with a
real ward number and a source I recognized, I'd have skipped the Excel hour
that day. That's worth something to me, genuinely — an hour of my week, on a
day I've got four other fires.

**LR:** Second thing. When the assistant was pointed directly at OYL's
guidance file — not asked to search, just handed the file — one assistant
answered "Ward 32 ranks number one in the dataset's comparable danger
rankings," and it correctly restated OYL's own caveats in the same answer.
The site's actual published ranking has Ward 32 at ninth. The published
number-one ward is Ward 42.

**Marcus:** Say that back to me slower. It had the file. It read the
caveats correctly, out loud, in the same breath — and it still got the
actual number wrong?

**LR:** That's what was observed, yes.

**Marcus:** That's worse than not finding it at all, and I want to be
precise about why. If it just says "I don't know," I know not to trust it
and I go do the hour of Excel. But if it says the right *kind* of sentence —
caveats and all, sounds exactly like something my methodology page would
say — and the actual fact inside that sentence is wrong, that's the
dangerous one, because that's the one that gets past me. I'm not checking
methodology language for accuracy, I'm checking whether it *sounds* like it
knows what it's talking about. And apparently that's not the same test.

**LR:** Third. OYL's ward ranking is described as a relative 0-to-100
percentile blend, and it's explicitly not normalized by ridership — the
assistants that actually read the guidance file did restate that caveat
correctly.

**Marcus:** Okay, that part I actually trust more, because that's the exact
argument I get in a room — "your ward just has more riders, of course it
has more crashes." If the assistant is at least carrying that caveat when
it talks to a resident directly, that's better than nothing. My worry isn't
that caveat, it's the ward number sitting three sentences away from it being
flat wrong, like you just told me. The caveat being right doesn't help me
if the headline fact next to it is wrong.

**LR:** Fourth. When asked for things OYL doesn't publish, the
guidance-reading assistants said plainly "that's not published here" — no
estimate, no guess.

**Marcus:** That's the one piece of good news in this whole conversation.
That's actually what I want from it. If I ask it something and it doesn't
have it, "not published" is a sentence I can work with — I know to go back
to CDOT's liaison or the sales-tax study I keep hearing about. It's the
confident wrong number that costs me, not the honest gap.

### 4. Gap probing

**LR:** Let's sit with that Ward 32 example for a minute. Politically — what
happens when an assistant tells a staffer, or a resident, or a reporter,
that their ward is "number one most dangerous"?

**Marcus:** If that had been my ward it named — wrongly — I've got a
resident, or worse a reporter, walking around with "your ward is the most
dangerous in Chicago for cyclists" in their pocket, sourced to an AI
assistant that sounds authoritative because it cited a real dataset and
used the right vocabulary. I can't out-argue that in a five-minute phone
call. I'd have to go pull the actual ward table myself, screenshot it, and
say "no, we're ninth, here's the real page" — and now I'm the one who
sounds defensive, correcting an AI in public, which reads to a lot of
people like I'm just spinning. Being right isn't the same as being
believed, once the wrong number's already out there.

**LR:** And what does your alderman do with a number like that, if it
reaches her before it reaches you?

**Marcus:** Best case, she calls me and asks "is this true" before she says
anything to anyone, and I've got twenty minutes to check it. Worst case,
somebody hands it to her right before she walks into a meeting or a debate
and she either repeats it — because it sounded sourced — or gets asked about
it cold and has to say "I don't know" on camera, which is its own kind of
bad. Either way, I didn't put that number in her hands, and I still have to
clean it up.

**LR:** What about the neighboring ward's office — Ward 42's staff, say,
in this hypothetical, if a wrong number named their ward instead?

**Marcus:** Then it's a gift to them, and a problem for whoever the
assistant actually named — Ward 32's office, in your example. There's an
alderman-to-alderman rivalry current running under almost everything, and
"my ward's safer than yours, an AI said so" is exactly the kind of thing
that gets repeated at a Council Finance Committee hallway conversation even
if everyone involved knows it's shaky. I'd bet Ward 42's office would use it
before they'd correct it, honestly — it's not their job to protect Ward 32
from a bad AI answer. It's Ward 32's chief of staff who eats that call.

**LR:** You said the "not normalized by ridership" caveat is one you
recognize from your own arguments. Does it actually survive into what you'd
hand your alderman — or does it get lost somewhere in translation?

**Marcus:** Depends who's doing the translating. If I'm the one reading the
underlying page and writing the briefing line myself, it survives, because
I know to write "raw counts, not per-rider" right under the number — I've
been burned by that exact gap before, so I build the caveat in by habit
now. If it's coming to me pre-packaged from an assistant's answer, and the
assistant says the caveat in the same paragraph as the ranking — like you
described — I might actually keep the caveat sentence and drop the ranking
number, or vice versa, depending which one I'm skimming for that day. I'm
not proofreading an AI's paragraph line by line at nine at night before a
CAPS meeting. I'm skimming for the number and the source. The caveat's
value depends entirely on whether it's structurally impossible for me to
grab the number without also grabbing the caveat — and nothing in what
you've described guarantees that. A caveat that's merely *present somewhere
in the answer* isn't the same as a caveat that's *attached to the number*.

**LR:** What do you do today, concretely, to check a number before it goes
out under the alderman's name — whether it came from an assistant or
anywhere else?

**Marcus:** Same three things, every time, no exceptions. One: does it match
a source I can point to by name — not "the internet says," but "Chicago
Data Portal, pulled this date," something with a URL I could hand a
reporter. Two: does the timeframe match what I think it is — I've been
burned by stale data once, I check dates now like it's a tic. Three: could I
defend this number out loud, cold, if someone in the room asked me "how do
you know that" — if I can't answer that question in one sentence, it
doesn't go in the memo, full stop. An assistant's answer doesn't get to
skip any of those three steps just because it sounded confident. If
anything, it gets more scrutiny than a spreadsheet I built myself, because
I don't know what it did to get that number, and I can't watch it work the
way I can watch my own pivot table.

### 5. Magic-wand close

**LR:** Magic wand — one thing changes about how assistants handle OYL's
data, and it fixes the problem you actually have. What is it?

**Marcus:** Honestly? I don't need the assistant to get smarter. I need it
to be forced to show its work in a way I can check in ten seconds — the
actual ward number sitting right next to the actual source link, not buried
three sentences into a paragraph that also has a caveat and a citation and
a law-firm blog post mixed in. If I could glance at the answer and see "Ward
42, source: [link], ranking is relative not absolute" as basically three
separate, checkable facts instead of one fluent paragraph, I could verify it
myself in the time it takes to read a text message. Right now the whole
danger is that it reads too smoothly for me to know where to poke it.

**LR:** What would make you stop trusting an assistant's bike-safety
numbers after one bad experience?

**Marcus:** One wrong ward ranking landing in front of my alder or a
reporter before I catch it. That's it, that's the whole bar. Doesn't matter
if it's 95% right the rest of the time — this job runs on "did the number
you gave me hold up," and one public miss and I go back to doing every
number by hand myself, and I tell the other chiefs of staff I know to do the
same. I already don't fully trust it, based on what you just told me. This
conversation didn't create that distrust, it confirmed something I was
already halfway to believing.

---

## Analysis Memo

```
participant: chi-ward-office (Marcus Webb) — via AI assistant
confidence_notes: The core reactions — the same-day workflow of a quick
  assistant gut-check followed by an independent manual pull, the
  three-part verification habit (named source, checked timeframe,
  defensible-out-loud test), and the "her name, not the AI's, is on the
  correction" framing — are tightly grounded in the chi-ward-office
  evidence brief and the study #0 transcript, which already established his
  triage-first, blindside-averse worldview and his distrust of anything
  unverifiable landing near his alderman's name. His specific reactions to
  the four stimulus observations (non-discovery, the Ward 32 misattribution,
  the caveat-restatement, the honest refusal) are new extrapolations for
  this study rather than directly cited prior behavior, since study #0 never
  tested agent-mediated access — treat those as plausible in-character
  inferences, not established fact about a real ward staffer. His account of
  a prior stale-spreadsheet correction is invented for this interview
  (illustrative, not sourced) but is consistent with the kind of workaround
  the evidence brief documents elsewhere (the 18th Street rollback lesson).
  His "show its work in three checkable facts" magic-wand answer is the
  single highest-inference-distance item in this transcript — it is a
  design reaction to a UX problem he was only just shown, not something he
  arrived at independently, so hold it more loosely than the rest.

stated_needs:
  - need: A fast (under-ten-minutes) triage answer to "is this claim about
      my ward true, and how worried should I be" before committing to a
      full manual data pull.
    evidence_quote: "I wasn't trying to be lazy about it, I was trying to
      figure out in under five minutes whether this was a real number I
      needed to worry about or some Nextdoor thing that got exaggerated
      three times before it hit my inbox."
    underlying_job: Triage incoming claims fast enough to decide whether
      they warrant the hour-long manual verification workflow, without
      wasting that hour on every exaggerated rumor.

  - need: Any number an assistant hands him must be independently
      verifiable against a named, dated source before it can go in a
      constituent reply or briefing memo — never pasted in as-is.
    evidence_quote: "I don't paste assistant output into either one, ever,
      unless I've independently checked the number it gave me against
      something I pulled myself."
    underlying_job: Protect the alderman from having to publicly retract a
      number, by never letting an unverified source reach her name.

  - need: A three-part, repeatable verification checklist applied to any
      number regardless of source (named source, matching timeframe,
      defensible-in-one-sentence), and he wants an assistant's answer to
      satisfy all three without extra work on his part.
    evidence_quote: "Does it match a source I can point to by name... does
      the timeframe match what I think it is... could I defend this number
      out loud, cold, if someone in the room asked me 'how do you know
      that.'"
    underlying_job: Maintain a consistent, defensible standard for any
      number that could reach the alderman publicly, independent of
      whether a human or an assistant produced it.

  - need: When an assistant doesn't have OYL's data, it should say so
      plainly rather than approximate — this is explicitly the one thing he
      wants preserved, not fixed.
    evidence_quote: "That's actually what I want from it... 'not published'
      is a sentence I can work with... It's the confident wrong number that
      costs me, not the honest gap."
    underlying_job: Distinguish an actionable gap (go find the real source)
      from a false positive (a wrong number he might miss), because only
      the former is survivable.

latent_needs:
  - need: The number and its source citation need to be structurally
      inseparable in an assistant's answer — not merely co-present
      somewhere in the same paragraph as a caveat — because he skims for
      the number under time pressure and will not proofread prose at 9pm
      before a CAPS meeting.
    inference_basis: He explicitly distinguished "a caveat that's merely
      present somewhere in the answer" from "a caveat that's attached to
      the number," and separately described his real reading behavior under
      deadline pressure ("I'm not proofreading an AI's paragraph line by
      line at nine at night... I'm skimming for the number and the
      source"). This is a behavior/failure-mode observation he volunteered
      unprompted while reasoning through the Ward 32 example, not a
      feature he asked for by name — his own magic-wand answer ("three
      separate, checkable facts instead of one fluent paragraph") converges
      on the same underlying gap independently.
    risk_if_wrong: OYL controls its own guidance file and caveat placement,
      but has zero control over how a third-party assistant renders,
      reorders, or truncates that content in its final answer to the user —
      this latent need may be technically unaddressable from OYL's side no
      matter how the source data is structured, which would make it a
      finding about the limits of the channel rather than a fixable gap.

  - need: A visible, per-ward "last verified" or "confidence" signal that
      distinguishes a caveat-correct-but-fact-wrong answer (the dangerous
      failure mode he identified) from a genuinely reliable one, since
      fluency and correctness are decoupled in what he was shown and he has
      no way to tell them apart from the outside.
    inference_basis: His central, spontaneous observation about the Ward 32
      case was that the failure mode is worse than non-discovery precisely
      *because* the answer "sounds exactly like something my methodology
      page would say" while being factually wrong — "I'm not checking
      methodology language for accuracy, I'm checking whether it sounds
      like it knows what it's talking about. And apparently that's not the
      same test." He named this as a new category of risk he did not have
      a defense against, distinct from his existing three-part checklist.
    risk_if_wrong: This may not be solvable by OYL at all — the failure
      happened inside a third-party assistant's reasoning after it read
      the correct source file, which is outside OYL's static-file
      publishing model entirely; treating this as an OYL product gap
      rather than a channel-trust finding could misdirect engineering
      effort that has no lever to pull.

  - need: Political/reputational monitoring for when a wrong or
      misattributed number about his ward is circulating via an assistant,
      analogous to the press-clipping archive he already keeps for news
      mentions — because he currently has no visibility into what an
      assistant is telling a resident or reporter about his ward until it
      already lands in his inbox as a complaint.
    inference_basis: He drew a direct, unprompted structural parallel
      between "a totally different alder with a similar name" (his
      documented fear from the study #0 news-layer reaction) and this new
      scenario, and separately described the neighboring-ward dynamic
      ("Ward 42's office would use it before they'd correct it... it's not
      their job to protect Ward 32 from a bad AI answer") as a live
      political risk he has no current instrument for detecting, unlike his
      screenshot archive for press coverage which he built specifically to
      close an analogous blind spot.
    risk_if_wrong: This is the most speculative inference in this memo —
      it assumes he would want (and could operationally sustain) a new
      monitoring habit for an as-yet-hypothetical failure mode he has never
      actually experienced; his stated behavior pattern is reactive
      (checking numbers when they cross his desk), not proactive
      (monitoring what he can't see), so this may overstate his appetite
      for a new standing practice versus simply reacting harder when it
      happens.

  - need: A way to tell, from the outside, whether an assistant actually
      read OYL's guidance file (and thus carries its caveats and tier
      language) versus retrieved OYL data without it (bare numbers, no
      caveat) — because right now the presence of correct-sounding caveat
      language is itself misleading him into a false sense of the answer's
      reliability.
    inference_basis: He conflated "the caveat sounded right" with "I should
      trust this less than I do" only after the interviewer pointed out the
      contradiction; his unprompted reaction before that point was closer
      to reassurance ("that's actually what I want from it," re: the
      ridership caveat) — the gap between how much weight he places on
      caveat-presence and how little it should predict factual accuracy is
      a misunderstanding this transcript surfaces rather than one he named
      himself.
    risk_if_wrong: This is inferred from his reasoning process across two
      separate answers rather than a single direct statement, and depends
      on reading a shift in his confidence as a stable belief rather than
      an artifact of the interview's sequencing (caveat question asked
      before the Ward 32 reveal in this write-up's ordering, but discussed
      after it in-session) — treat as lower confidence than the other three
      latent needs in this memo.

reactions_to_existing:
  - feature: Assistant discoverability of OYL for an unprompted ward-safety
      question
    verdict: distrusts (matches his own lived experience)
    why: His own unprompted attempt two weeks prior produced the identical
      failure — a generic "concern exists" paragraph, law-firm-style
      sources, no OYL — and he treats the three-assistant test result as
      confirmation, not new information; explicitly names it a systemic
      "tool can't find the thing" problem with no lever he can pull.
  - feature: llms.txt / guidance-file caveat restatement (ridership
      normalization)
    verdict: would-use, conditionally
    why: Recognizes the caveat as the exact rebuttal he needs for a
      recurring room argument and says it's "better than nothing," but
      immediately qualifies that its value depends on it being structurally
      attached to the number, not merely present in the same answer.
  - feature: Ward ranking (percentile danger score) surfaced via an
      assistant reading the guidance file
    verdict: distrusts — flags as the single most dangerous failure mode in
      this interview
    why: The Ward 32-vs-actual-Ward-42 misattribution, delivered with
      correct caveat language, reads to him as worse than no answer because
      it defeats his usual heuristic (does it *sound* credible) without
      being factually reliable — "that's the dangerous one, because that's
      the one that gets past me."
  - feature: Explicit refusal on non-published data (ridership/exposure
      denominators, obstructions)
    verdict: uses / trusts
    why: The one unambiguously positive reaction in the interview — matches
      his stated preference (established in study #0 too) for an honest
      gap over a fabricated-precision number he can't defend.

data_they_bring: A same-day, ten-minute "assistant gut-check" step now
  inserted before his existing hour-long manual crash-portal pivot workflow
  (established in study #0); a three-part personal verification checklist
  (named source, matched timeframe, defensible-in-one-sentence) applied
  uniformly to human-built and assistant-produced numbers alike; a lived
  prior incident of a stale-spreadsheet number requiring a public walk-back,
  which now anchors his default posture toward any unverified figure headed
  for his alderman's name.

deal_breakers: (1) One publicly wrong ward ranking or safety claim reaching
  his alderman or a reporter, sourced to an assistant, before his office
  catches it — he states this single event would end his trust in
  assistant-mediated numbers entirely and cause him to revert fully to
  manual verification, regardless of how reliable the rest of the layer is.
  (2) A caveat-correct, fact-wrong answer specifically — worse to him than
  a caveat-correct refusal or a caveat-absent wrong answer, because it
  passes his primary heuristic (does this sound like it knows the
  methodology) while still being false.

vocabulary: constituents, "my alder," briefing memo, CAPS meeting, "the
  room," "worst in the city" (the trigger phrase that routes an email
  straight to him), blindside, "walk it back," "the correction," ward
  boundary/"straddles into the next ward," source-by-name ("Chicago Data
  Portal, pulled this date"), "defend it out loud, cold." He never adopts
  interviewer or OYL-internal terms unprompted — does not say "agentic
  layer," "contract version," "data tier," or "percentile blend"; when
  asked about the ranking methodology he translates it back into "relative,
  not absolute" in his own words, consistent with his study #0 refusal to
  adopt "comfort floor" or "normalization" as his own vocabulary.
```
