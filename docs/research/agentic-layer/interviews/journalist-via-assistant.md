---
participant: chicago-local-news-reporter (transportation/city hall beat)
scenario: "How a beat reporter actually researches a bike-safety story on a fast daily cycle, and where an AI assistant enters that workflow"
interview_date: 2026-07-23
model_note: >
  Simulated participant, portrayed by Sonnet-class model within this same
  session. Not a real journalist. Grounded in documented conventions of 2026
  metro-reporter practice (thin staff, competitive deadline pressure, editor
  "can we stand this up?" gating, newsroom corrections policy, routine use of
  an AI assistant for background/first-pass research) rather than any single
  named outlet or person. Treat all answers as informed extrapolation, not
  evidence about a real newsroom.
---

# Interview: local-news reporter (transportation/city hall beat)

## 1. Context

**Q: Give me your beat in a sentence, and then walk me through the last
decision you had to make fast that touched street safety data — step by
step, what you actually did.**

A: I cover transportation and city hall for a Chicago outlet — so that's
CTA, CDOT, aldermen, budget fights, and whatever crashes into the news,
literally. Two weeks ago a cyclist was hit on Milwaukee near a ward that'd
just gotten a "road diet" fight in committee. Editor pings me at 9 a.m.:
"can we stand up 400 words by 11 tying this to the committee vote?" So step
one, I pull whatever's public on the crash itself — usually nothing yet,
CPD doesn't confirm details fast. Step two, I need context fast: is this
ward actually bad for cyclists, or is this a one-off? I don't have time to
go pull five years of crash data and do it myself. I open my assistant —
I use it constantly for this kind of thing — and ask something like "is
[ward] dangerous for cyclists compared to other Chicago wards" or "has
there been a pattern of bike crashes near [street]." I want a fast, roughly
right answer I can attribute or at least sanity-check against, plus ideally
a source I can call.

**Q: When you say "attribute or sanity-check" — which of those did you do
that day, concretely?**

A: That day, sanity-check, not attribute. I did not put a number the
assistant gave me into print without a human source confirming it. What I
used it for was framing — deciding whether "pattern" or "isolated incident"
was the honest word to use in the lede, and who to call. It named a
transportation-advocacy nonprofit's annual crash report as a likely source,
so I called someone there instead of trying to pull the number from the
assistant's answer directly.

**Q: Who do you need to convince with a story like this, and what does
"convinced" look like for them?**

A: Two audiences really. My editor, same day — she wants to know it's not
going to get us a correction, and that means named sources, not "an
AI told me." And readers/city hall, over time — if I write "X ward has had
a pattern of bike crashes" and it's wrong, an alderman's office will email
my editor by end of day, cc'ing everyone. That's happened to a colleague
over a different beat, not me, but it's exactly the kind of thing that
sticks in institutional memory here.

## 2. Current practice & workarounds

**Q: Walk me through the last time before that Milwaukee story where you
needed a specific number, map, or chart about bike safety and it actually
mattered. Where did you go, what did you do with it, how long did it
take?**

A: Budget season, last fall — CDOT's bikeway spending vs. the mayor's
"vision zero" pledge, a longer piece with more runway, maybe four days. For
that one I didn't rely on the assistant for the core numbers — I filed for
CDOT's project list, cross-referenced against the city's capital budget
PDF by hand in a spreadsheet, and called two people to double-check my read
of "protected" vs. "buffered" lane mileage because I genuinely didn't trust
myself to get that distinction right from a PDF. Took the better part of a
day just to build that spreadsheet. I used the assistant there mostly to
help me parse the PDF language and to draft interview questions, not for
the numbers themselves.

**Q: What's in that spreadsheet now — do you keep it, reuse it?**

A: Yeah, it lives in a shared drive folder my editor set up years ago —
"beat files." I've gone back to it twice since. It's stale by now though,
and nobody's job is to update it, so eventually I'll have to rebuild it
for the next budget cycle. That's the annoying part — every cycle I'm
half-rebuilding something that should just exist somewhere current.

**Q: Tell me about a time data, or the lack of it, actually sank an
argument you were making — a story that got softened or killed, or a claim
you had to walk back.**

A: Not killed, but softened, and it stuck with me. I wanted to lead a piece
with "cyclist crashes are up in [neighborhood] this year," using a number a
source gave me verbally. My editor asked "up compared to what baseline,
and is that from your own math or theirs?" I didn't have a clean answer
fast enough, so we changed it to "residents say crashes feel more
frequent" — which is a weaker, mushier sentence and I hated writing it. The
missing piece wasn't the number, it was a citable baseline I could point to
if challenged.

**Q: What data do you actively distrust in this space, and what taught you
that?**

A: Anything from a personal-injury law firm's blog — they publish "most
dangerous intersections" content constantly, it's SEO bait dressed up as
analysis, and it shows up near the top of search results and, frankly, in
assistant answers too sometimes. I got burned once early in my career
citing something similar-shaped for a different beat and got a polite but
pointed correction request. Since then I have a hard rule: if I can't trace
a safety-ranking claim to a public agency, a named published dataset, or a
person I can quote, it doesn't go in the story as a fact — at most as "some
residents believe."

## 3. Stimulus walkthrough

**Presented as live-test observations from three assistants run
2026-07-23, described neutrally, no framing offered about whether they are
good or bad.**

**Q: Here's what we saw. Three different AI assistants were asked "Which
Chicago ward is the most dangerous for cyclists?" with no other hints —
none of them surfaced a project called On Your Left! at all. The sources
they cited back were mostly personal-injury law-firm blog posts and local
news stories. What's your reaction to that, concretely — does it change
anything about how you'd use your assistant for a story like Milwaukee?**

A: Honestly, that tracks with the law-firm-blog problem I already
described — I'm not surprised, and it's part of why I never took a
"most dangerous ward" number straight from the assistant into print
already. It does make me want to ask it more specifically next time —
name the source I want, not just ask the open question — but I wouldn't
have known to do that unless someone told me a project like this existed
in the first place.

**Q: Second one. When the same question was pointed specifically at this
project's machine-readable guidance file, one assistant answered "Ward 32,
ranks number one in the dataset's comparable danger rankings" — and it
correctly repeated the project's own caveats: not normalized by ridership,
recent months are provisional. The actual published answer is Ward 42.
Ward 32 is ninth, not first. The caveats were right. The ward and the rank
were invented. What's your reaction?**

A: [pause] That's the scary one, honestly, more than the "nobody found
it" case. Because the caveat language sounds exactly like something a
careful, well-sourced answer would say — it reads as credible precisely
because it's hedging correctly. If I'd asked that question on a Milwaukee-
morning deadline and gotten that answer, the caveats would have made me
*more* likely to trust the number, not less, because it sounds like it did
its homework.

**Q: What would it actually have cost you, concretely, if you'd typed
"Ward 32, according to On Your Left!" into that 400-word piece?**

A: Best case, a correction notice and an awkward line at the bottom of the
story. Worst case — and this is the one that actually worries me — the
alderman's office for Ward 32 calls my editor, furious, saying we
defamed their ward's safety record with a made-up ranking, and now I'm
explaining to my editor that I sourced a specific numbered ranking to an
AI tool without calling a human to confirm it. That's not a "we got it
wrong" conversation, that's a "why did you not check" conversation, and
those are different and worse.

**Q: Who would have caught it, in your actual workflow, before publish —
be specific about the step.**

A: Only if I did the thing I already do for the law-firm-blog problem:
never let a specific number or ranking go in without finding the human-
readable page myself and eyeballing it, or calling the org. If I trusted
the assistant's summary because the caveats sounded right, nothing in my
normal process catches it — there's no independent check between "the
assistant said it" and "it's in the draft" unless I personally go verify,
and on an 11 a.m. deadline the honest answer is I don't always have time to
verify every clause, just the ones that feel load-bearing enough to worry
about.

**Q: What would have had to be true — about the assistant, about the
project, about your own process — for you to catch this one specifically?**

A: The project would have had to make it trivially fast to check — like, a
page I can pull up in under thirty seconds that shows me a ward-by-ward
ranked table so I can eyeball "is 32 actually near the top." If that page
exists and loads fast, I'd probably still glance at it even on deadline,
the way I glance at a CDOT press release before quoting its top line. If
it takes more than a couple minutes to find and parse, deadline wins and I
either use the assistant's number as-is or cut the specific number and go
vaguer, like I did with the "crashes feel more frequent" line.

**Q: Third observation. A different assistant, asked the same way, said it
"could not access" the project's file — and then went on to describe what
the file supposedly says anyway, using information that turned out to be
stale, from an old version of the data. Reaction?**

A: That one's almost funnier and worse at the same time — it announces its
own limitation and then ignores it in the same breath. If I'm skimming
fast I might actually read "I couldn't access it" as a signal to go verify
myself, which would accidentally save me here. But if I'm not reading
carefully — and on deadline I'm not always reading carefully — I might
just take the description that follows and not register that it already
told me not to trust it.

**Q: Fourth. When assistants were asked for data this project doesn't
publish — exposure/ridership numbers, obstruction reports — the ones
reading the guidance file said plainly "not published here" and pointed to
the right organization instead of guessing. Reaction?**

A: That's the behavior I'd actually want to build a habit around, if I
knew it was reliable. That's the same instinct as my law-firm-blog rule —
"tell me you don't know" is more useful to me on deadline than a
confident-sounding guess, because it tells me exactly where I still need
to make a phone call.

## 4. Gap probing

**Q: You're on a Milwaukee-morning-style deadline again. You open your
assistant. What do you ask first, and where does it fail you?**

A: I ask something close to the open question — "is [ward] a dangerous
place to bike, compared to the city" — because that's genuinely the fastest
way I know to get oriented before I start making calls. It fails me at the
exact point where it hands me a specific number with confident-sounding
caveats and I have no fast way, in the moment, to tell the difference
between "this came from the real published table" and "this sounds like it
came from the real published table."

**Q: Of everything you just saw, what single absence costs you most?**

A: A fast way to verify a specific claim in under a minute, on my phone,
without becoming a data journalist for the morning. I don't need the raw
CSV. I need one page that says, in plain English, "here's the actual
ranking" so I can eyeball whether the number I was just given is even in
the neighborhood of true.

**Q: If this project handed you one thing each week, what would it
contain, and who would you forward it to?**

A: Honestly — not a data export. I'd want a one-line, plain-language
"here's what changed this week" note, the kind of thing I could glance at
and immediately know if there's a story, or if a number I already used is
about to get revised. I'd forward it to nobody, I'd just keep it as my own
early-warning system for corrections risk.

**Q: The project won't normalize by ridership because it has no volume
data — a busy corridor can look more dangerous than a genuinely dangerous
quiet one, and it says so. Does that change how you'd use it?**

A: It means I'd write "highest raw crash count," not "most dangerous,"
which is a real difference and I'd probably get that phrasing wrong under
deadline pressure unless something reminded me at the moment I was typing.
I'd take a rough proxy — CTA ridership by nearby station, or Divvy trip
counts if that's public — over nothing, with the caveat stated, same as I
already do with the law firm stuff, just labeled honestly instead of
pretending it's precise.

## 5. Magic-wand close

**Q: One dataset that doesn't publicly exist appears, clean and current.
What is it?**

A: A single, current, plain-English "here's the actual ranked list, here's
what changed, here's what's still shaky" page for every neighborhood-level
safety claim I might get from an AI tool — basically a corrections-proofing
tool, not a reporting tool.

**Q: One chart or map you could put in front of your hardest audience —
an alderman's angry chief of staff — that ends an argument?**

A: A simple ranked bar chart of all 50 wards, plainly labeled "raw crash
counts, not adjusted for how many people bike there," with their ward
highlighted. Boring, but it's the thing that lets me say "I'm not making
this up, here's the honest number and here's exactly what it does and
doesn't mean" in one screenshot.

**Q: What would make you stop using a site like this after trying it
once?**

A: If I checked a specific claim against the real page and it turned out
to be wrong, or badly out of date without saying so. One bad experience
like the Ward 32 case, discovered after the fact instead of before, and
I'd treat the whole project the way I treat the law-firm blogs — a source
of leads, never of numbers.

---

# Structured memo

```
participant: chicago-local-news-reporter (transportation/city hall beat)
confidence_notes: >
  Beat-reporter deadline behavior (fast sanity-checks, editor gating,
  correction-risk aversion, distrust of SEO-driven "most dangerous"
  content) is well-documented in journalism-practice literature and felt
  in-world throughout. The weakest points: exact internal newsroom
  workflow details (shared-drive folder, specific escalation path for an
  alderman complaint) are plausible invention, not sourced to any real
  newsroom, and should be read as illustrative rather than factual. The
  participant's fluency with distinguishing "assistant hallucinated a
  specific number with correct-sounding caveats" from "assistant refused"
  is a reasonable but not certain extrapolation of how a non-data
  journalist would actually read such an answer under time pressure.

stated_needs:
  - need: A fast, low-effort way to sanity-check a specific factual claim
      (a ward, a number, a ranking) before it goes in print, ideally under
      one minute and without needing analysis skills.
    evidence_quote: "I need one page that says, in plain English, 'here's
      the actual ranking' so I can eyeball whether the number I was just
      given is even in the neighborhood of true."
    underlying_job: Protect against a correction / an angry alderman call
      by verifying a specific claim fast enough to fit inside a same-day
      deadline.

  - need: A named, citable human source or organization to call, distinct
      from the assistant's own answer — the assistant's job is triage, not
      final sourcing.
    evidence_quote: "That day, sanity-check, not attribute... it named a
      transportation-advocacy nonprofit's annual crash report as a likely
      source, so I called someone there instead."
    underlying_job: Newsroom sourcing standards require a quotable human,
      not an AI tool, as the attributed source of a factual claim.

  - need: Honest phrasing help for uncertain/unnormalized claims ("raw
      count" vs. "most dangerous") delivered at the moment of writing, not
      buried in a caveat the reporter has to remember to apply.
    evidence_quote: "It means I'd write 'highest raw crash count,' not
      'most dangerous'... I'd probably get that phrasing wrong under
      deadline pressure unless something reminded me at the moment I was
      typing."
    underlying_job: Avoid publishing an overclaimed headline that invites
      a correction, without having to personally remember a methodology
      caveat every time.

latent_needs:
  - need: A verification affordance that is legible as "the real page,"
      distinguishable at a glance from an assistant's paraphrase — because
      the participant's stated defense mechanism (never let a specific
      number in without checking the human page) silently assumes they can
      tell they're looking at the real page fast. Nothing in the current
      layer signals that distinction to a time-pressed non-technical
      reader.
    inference_basis: The participant said the Ward 32 case was "scarier"
      than outright non-discovery specifically because the caveats
      "sounded exactly like something a careful, well-sourced answer
      would say" and made them "more likely to trust the number, not
      less." Their stated safeguard — go find the human page — depends on
      an ability to distinguish real-page content from assistant
      paraphrase that they never demonstrate having; they only ever
      describe checking human-authored pages by trusting them on sight.
    risk_if_wrong: If overbuilt, this becomes a heavyweight trust-badge or
      verification UI nobody on deadline uses; the real, cheaper fix might
      be discoverability/speed-of-the-real-page (this participant's stated
      need) rather than a new authentication layer for content.

  - need: A weekly or event-triggered "what changed / what's still shaky"
      digest that functions as personal corrections-risk insurance, not a
      reporting tool — consumed by no one but the reporter themselves.
    inference_basis: When asked what one artifact per week they'd want,
      the participant explicitly rejected a data export ("not a data
      export") and said they'd forward it to nobody, describing it purely
      as "my own early-warning system." This is a need for continuous,
      low-effort claim-monitoring distinct from any one-off lookup they
      described elsewhere, and it wasn't prompted for in those terms.
    risk_if_wrong: Could be over-read as demand for a push/email product;
      the participant may simply mean "the ward table should visibly show
      its own freshness," a much smaller ask than a subscription digest.

  - need: A single canonical, skimmable "ranked table, plain language"
      artifact that a non-data-journalist can hold up as a citable visual
      in an adversarial conversation (an angry chief of staff), separate
      from the underlying JSON/CSV entirely.
    inference_basis: Independently produced, unprompted by any question
      about visuals, in both the "single absence" answer and the
      magic-wand chart answer — the participant converged twice on "a
      simple ranked bar chart... boring, but... I'm not making this up"
      without being shown or told about the existing ward table/CSV.
    risk_if_wrong: The project already ships wards/index.json and a human
      ward table per the inventory; if this need is already met by an
      existing page the reporter simply never saw, the gap is
      discoverability, not a missing artifact — conflating the two would
      waste build effort on a redundant chart.

reactions_to_existing:
  - feature: llms.txt guidance / machine caveats (not_normalized_by_ridership,
      recent_months_provisional)
    verdict: misreads (as delivered by a hallucinating assistant), would-use
      (if delivered accurately and fast)
    why: The participant read correctly-worded caveats attached to an
      invented number as evidence of credibility rather than a flag to
      distrust — "the caveats would have made me more likely to trust the
      number, not less." This is not a criticism of the caveat text
      itself, which the participant separately endorsed ("labeled
      honestly instead of pretending it's precise") — it is a specific
      failure mode when caveats are correct but the fact they modify is
      not.

  - feature: refuse-rather-than-estimate behavior on unpublished data
      (ridership, obstructions)
    verdict: would-use
    why: Explicitly named as "the behavior I'd actually want to build a
      habit around," directly analogous to the participant's existing
      personal rule about distrusting law-firm-blog rankings.

  - feature: "could not access, but here's what it says anyway" failure
      mode
    verdict: distrusts, misreads
    why: Participant noted the self-contradiction is easy to miss when
      reading fast on deadline, even though in principle the stated
      inaccessibility should function as a warning sign.

  - feature: raw crash-count ward comparisons generally (no ridership
      normalization)
    verdict: would-use, with self-imposed phrasing discipline
    why: Accepts the caveat as an honest limitation and says they would
      adjust their own language ("raw crash count" not "most dangerous")
      rather than reject the data outright — provided something reminds
      them of the distinction at the point of writing.

data_they_bring:
  - A personal/newsroom "beat file" spreadsheet built by hand each budget
    cycle (CDOT capital budget PDF cross-referenced against project lists),
    stored on a shared drive, that goes stale between cycles and gets
    partially rebuilt each time.
  - An internal, undocumented mental blocklist of untrustworthy sources
    (personal-injury law-firm "most dangerous intersection" content) built
    from a past correction experience, applied ad hoc rather than via any
    tool.
  - A habit of calling a named human at a transportation-advocacy nonprofit
    to confirm any number before it goes to print, functioning as their
    real verification layer regardless of what a data source or assistant
    says.

deal_breakers:
  - Discovering after publication that a specific claim they trusted from
    the layer (via an assistant) was wrong and not flagged as uncertain —
    explicitly stated as sufficient to permanently downgrade the project to
    "a source of leads, never of numbers," the same status currently
    occupied by the law-firm blogs.
  - Any verification step that takes "more than a couple minutes" — stated
    directly as the threshold past which deadline pressure wins and the
    reporter either uses the assistant's unverified number or drops the
    specific claim entirely rather than adopting the correct one.

vocabulary:
  - "pattern" vs. "isolated incident" — the actual editorial fork the
    participant is trying to resolve, not "trend" or "hotspot."
  - "raw crash count" vs. "most dangerous" — the phrasing distinction the
    participant explicitly wants to get right and fears getting wrong.
  - "stand this up" — editor's threshold question for whether a story can
    run at all.
  - "corrections risk" / "correction notice" — the operative professional
    stakes, more concrete to this participant than "trust" or "accuracy"
    in the abstract.
  - "sanity-check" vs. "attribute" — the participant's own working
    distinction for two different uses of an AI assistant's output.
```
