---
participant: civic-developer
scenario: "Chicago civic-tech developer (Chi Hack Night world), interviewed about the last thing they built on public data, then walked through the OYL agentic layer as a builder deciding whether to depend on it"
interview_date: 2026-07-23
model_note: >
  Simulated participant, Sonnet-class model, grounded in documented civic-tech
  practice (Chi Hack Night culture, Socrata/Chicago Data Portal realities,
  volunteer-maintenance dynamics) and in this study's own evidence briefs
  (mcp-feasibility.md, eval-harnesses.md). Not a real person; treat all
  quotes as informant simulation, not testimony.
---

# Interview transcript — civic developer

**Q: Describe your role and the last decision you influenced (or tried to)
about street safety. What did that actually involve, step by step?**

A: I'm not on staff anywhere — I write software during the day for a
logistics company, and Chi Hack Night is where the civic stuff happens,
Tuesday nights, sometimes a Saturday hack day. The last street-safety thing
I actually shipped, not just talked about, was a small tool a few of us
called "Crash Radar" — you type a Chicago address or drop a pin, and it
tells you cyclist and pedestrian crash counts within a few blocks over the
last 3 years, plus a trend arrow. Built it because somebody's alderman
office asked at a hack night if there was "something like a Carfax but for
an intersection," half-joking, and I went home and had a rough version by
the weekend. It's not tied to any decision that actually moved policy — I
want to be honest about that, most of what I build doesn't. It moved one
Twitter/Bluesky thread and got shared in a ward Facebook group after a kid
got hit near a school, which is the realistic ceiling for something one guy
builds in a weekend.

**Q: Who did you need to convince, and what does "convinced" look like for
them?**

A: Honestly the audience for that tool was just "residents Googling their
own corner after something scary happened," not an alderman or a committee.
Convinced, for that audience, means the number on the screen matches what
they already believe from having lived there — if it looks wildly wrong
they bounce immediately and never trust the site again. I've watched people
close a tab in under five seconds when a number looks off. There's no
persuasion happening, there's a trust check happening, and you get one shot
at it.

**Q: What information sources do you touch in a normal week for this kind
of work?**

A: The Chicago Data Portal — Socrata — is basically the whole diet. Crashes,
311, building permits, sometimes Divvy trip data exports. Occasionally CTA's
real-time feeds (that's a real API, not Socrata, different pain entirely).
For bike-specific stuff there's also the crowdsourced layer — Bike Lane
Uprising for obstructions, Strava heatmaps unofficially, sometimes the
Mellow Bike Map. And GitHub issues on other people's civic-tech repos, which
is honestly where I learn about a Socrata dataset changing shape before I
learn about it by my own tool breaking.

---

**Q: Tell me about the last time you needed a number, map, or chart about
bike safety. Where did you go? What did you do with it? How long did it
take?**

A: Building Crash Radar itself is the answer — I needed "cyclist crashes
near a point, with dates," and the only real source is the Chicago Traffic
Crashes dataset on the Data Portal, joined against the People dataset to
filter for bike involvement, because the Crashes table alone doesn't tell
you a cyclist was involved — that's on a separate table keyed by
`CRASH_RECORD_ID`. First version took a weekend. Getting it *right* — the
join, the geocoding nulls, the bike-vs-not filter — took about three weeks
of evenings, on and off.

**Q: What broke, specifically, and what did you have to hand-fix?**

A: Two things, both boring and both expensive in attention. First: a
meaningful chunk of records have `LATITUDE`/`LONGITUDE` as null or as
`(0,0)` — "null island" — because the original geocoding failed at the
city's end. My first version silently plotted those at 0,0 in the Gulf of
Guinea, which I only caught because a coworker who does GIS pointed at the
map and asked why Chicago had a crash off the coast of Africa. I had to add
a filter step and a "coordinates unavailable" bucket instead of just
dropping them, because dropping them silently changes your counts without
telling anyone. That's a permanent hand-maintained filter now, not a
one-time fix — every refresh re-runs it.

Second, and this is the one that actually cost sleep: Socrata quietly
changed how a filtered `$where` query on the People dataset behaved — a
query that used to return bike-related person records the way I'd written
it started returning an empty set, no error, no deprecation notice, just
zero rows one Tuesday. My tool didn't crash, it just started showing "0
crashes near you" everywhere, silently, for about four days before someone
in the ward Facebook group said "this says zero crashes on a block where a
guy got doored last month," and that's how I found out. Not a monitoring
alert, not a changelog, a stranger on Facebook.

**Q: Walk me through fixing that — what did you actually do?**

A: First I assumed it was my bug, spent an evening on that. Then I diffed
the raw API response against a saved copy from months earlier and found the
field I was filtering on hadn't been renamed or typed differently — the
*semantics* of an existing filter clause had shifted, which is worse than a
renamed column because renamed columns throw a loud error and semantic
drift doesn't throw anything. I ended up switching to filtering client-side
after pulling a broader unfiltered set, which costs more bandwidth and more
Socrata request quota, purely so I control the filter logic myself instead
of trusting their query semantics to stay put. That's now just how I treat
Socrata permanently — never trust a server-side filter to keep meaning the
same thing next month.

**Q: What have you built yourself — spreadsheets, saved searches,
screenshots, hand counts — because nothing gave it to you directly?**

A: A personal Google Sheet, still alive, of "Socrata datasets that have
silently changed shape on me or someone I know," with the date and what
broke. It's not glamorous but it's the single most useful artifact I own
for this work, because it's the only record of which sources are safe to
build a dependency on versus which ones you check on every single build. I
also keep a local SQLite snapshot of the crash data from whenever I last
pulled it clean, specifically so if a future pull looks wrong I have
something to diff against that isn't "trust the new pull."

**Q: Tell me about a time data — or the lack of it — sank an argument you
were making.**

A: Ridership. Every single time cyclist crash counts come up, somebody
reasonable asks "sure, but is that street just busier, or actually more
dangerous per rider," and there is no public per-street cyclist volume
number for Chicago. CDOT has some counter data from specific locations, not
citywide, not current, and it's a PDF half the time. I've had to just say
"I don't have that" in front of people who then reasonably discount
everything else I said, because if you can't answer the most obvious
follow-up your whole presentation reads as naive. It's not that the raw
crash number is wrong, it's that the *comparison* people actually want to
make is unanswerable with public data, full stop.

**Q: What data do you distrust, and what earned that distrust?**

A: 311 data on bike-lane obstructions, completely — it's not a report of
where obstructions are, it's a report of where people who know 311 exists
and bother to call it are, which correlates more with neighborhood income
and civic-engagement than with actual obstruction frequency. I trust the
Data Portal's crash tables more than I trust most people expect, actually —
they're police-reported so they undercount certain things structurally
(dooring especially, because it often doesn't get a squad car), but at
least the undercount direction is roughly known and documented rather than
unknown. What I don't trust is anything self-reported without a stated
collection method — Strava heatmaps, unmoderated map pins — because I have
no way to reason about the bias.

---

## Stimulus: On Your Left!'s agentic layer (observed 2026-07-23)

**[Presented neutrally: static `/api/v1/` JSON with hand-written schemas, a
`_meta` envelope on every file — contract_version, generated_at, provenance,
data_tier, license, attribution, human_page, methodology, schema —
machine-readable `caveats` arrays, and an `llms.txt`. No server, no
accounts, no rate limits: files on GitHub Pages. From live tests: three
assistants asked an OYL-answerable question with no hints never surfaced
OYL at all. One assistant fetched only `llms.txt`, never took the one
further hop to the ward endpoint, and produced a wrong ward number while
correctly reciting OYL's caveats. Another assistant, with real fetch tools,
followed `llms.txt` → `wards/index.json` in two hops and got everything
right. Assistants that read `llms.txt` reliably honored its "say plainly
it's not published" instruction and its obstruction-data redirect.]**

**Q: First reaction — what would you use this for, concretely?**

A: Okay, this is unusually good for a volunteer static-site project, I'll
say that first. A hand-written JSON Schema per endpoint plus
`additionalProperties: false` on the envelope means I could point a
schema-validation step at it in my own CI and actually trust a shape break
would fail loudly instead of silently — which is exactly the opposite of my
Socrata story. That alone would make me trust it more than most city open
data, and that's not a low bar I'm setting, that's a genuinely high one
given what I just told you about Socrata drift. If I were rebuilding Crash
Radar today I'd seriously consider pulling ward-level danger scores from
`wards/index.json` instead of recomputing them myself from raw crash rows,
because the hard part — the ridership caveat, the "raw not normalized"
framing — is already stated for me, in the file, machine-readably. That
saves me the exact conversation that sank my own argument earlier.

**Q: What would you need to check before you'd trust it in front of your
audience?**

A: The `caveats` array and the schema are necessary but not sufficient —
what I actually need is a changelog and a stated breakage policy before I'd
wire it into anything that runs unattended. "Additive contract, shape
changes require a version bump" is a good sentence, but I need to know: is
there a version I can pin against, does an old `contract_version` stay
served forever or get overwritten, and is there a feed — even just a GitHub
Releases page or a CHANGELOG.md — I can watch instead of diffing the JSON
myself every week the way I currently do with Socrata. Right now, from what
you've described, I'd have to build my own drift-detector against this the
same way I built one against Socrata, which defeats a chunk of the value.

**Q: You mentioned the wrong-ward-number finding — one assistant fetched
only `llms.txt`, never took the second hop, and got the ward number wrong
while still reciting the caveats correctly. As an engineer, what would you
do about that?**

A: That's the finding that actually worries me, more than anything about
MCP. Reciting the caveat while stating a wrong number is *worse* than
stating a wrong number plainly, because it looks maximally credible — it's
got the disclaimer, it sounds careful, and it's still wrong. If I were
shipping this I'd treat "one-hop answers can be confidently wrong" as a
known failure mode of the whole approach, not a bug in one assistant. My
honest engineering instinct is: you can't fix a model's willingness to stop
at hop one from the publisher's side, full stop — you don't control the
agent's fetch budget. What you *can* do is make the single-hop answer less
wrong even when it's incomplete. Concretely: if `llms.txt` itself carried
the top-line danger-rank number for the single most commonly asked question
— "which ward is most dangerous" — inline, in prose, so a one-hop read gets
a *correct* headline number even if it never reaches the JSON, that closes
the gap for the one query you know gets asked. You can't generalize that to
every possible question, but you could close it for the two or three
`llms.txt` already lists as example questions. That's a real, scoped fix. A
general "assistants should always take the second hop" is not something you
can engineer around from a static-file publisher's side — that's on the
assistant vendor, and nobody here controls that.

**Q: Say more about why you'd stop there rather than trying to force the
second hop somehow.**

A: Because there's no mechanism. You're not running a server that can
inspect what the client already fetched and nudge it — you're a pile of
files, the client decides its own fetch budget, and different assistants
clearly have different budgets already, per what you just showed me — one
took two hops, one took one. Any "force the second hop" idea I can imagine
either requires server-side logic you don't have, or requires cramming so
much into `llms.txt` that it stops being a lightweight discovery pointer
and just becomes the whole dataset restated as prose, which has its own
staleness risk — now you have the JSON and a hand-synced prose copy of part
of it, and prose copies drift, that's a second maintenance surface for the
exact class of bug I've been telling you about all interview.

---

**Q: Chase this: get your honest read on whether a volunteer static project
should ship an MCP server. What would it cost to keep alive?**

A: No — and I want to cost that out rather than just assert it, because
"no" from a gut feeling isn't useful to you. MCP's remote transport is
Streamable HTTP: single endpoint, has to accept POST, has to compute a
response per request. GitHub Pages cannot do that at all, structurally, not
as a config thing — there's no code path for POST on a static host. So step
one is: you're not deploying "MCP" onto your current infrastructure, you're
standing up an entirely separate compute surface — a Cloudflare Worker or
similar — that duplicates data you already publish as flat files. That's
not a one-time cost, that's an ongoing second thing to keep alive next to
the thing you already keep alive, with its own account, its own secrets if
any, its own deploy pipeline, and its own dependency on a third-party free
tier not changing its terms — and free tiers do change, I've had a personal
project break because a host quietly killed a feature I depended on.

Then there's spec churn, which is the part that would actually make me say
no even if hosting were free. Two breaking changes in the trailing eighteen
months on the transport and protocol layers — that's not a mature, settled
spec yet, that's a spec still finding its shape. For a project with no paid
maintenance rotation, "the protocol you built against might require a
rewrite because the client library moved on" is exactly the failure mode
that kills volunteer projects — not lack of enthusiasm at launch, but
maintenance debt compounding quietly until nobody wants to touch it. I've
watched two other Chi Hack Night tools die exactly that way: not from a
dramatic failure, from the gap between "this used to work" and "someone
noticed it stopped" growing until fixing it stopped being a fun Tuesday
night and started being a chore, and chores are what kill volunteer
projects.

And even if you ate all that cost — what does it actually buy you? A typed
tool schema instead of prose fetch-recipes, and server-computed
parameterized queries you can't do with flat files. The second one is real
value, I won't pretend it isn't — "wards where crash rate rose AND
protected share rose, top 5" is a genuinely useful query your static files
can't answer today. But it doesn't touch the actual problem you just showed
me — an assistant reciting your caveat while stating a wrong number. MCP
gives the *client* a typed field to read; it does nothing to make the
*model* actually read it correctly before answering. That's not a
protocol-layer fix, that's a model-behavior problem, and shipping MCP
doesn't move that needle at all. So: no. Not because the tech is bad, but
because the cost is a second permanent compute surface plus a spec that's
still moving, and the thing it would fix isn't the thing that's actually
broken.

**Q: If someone on the project pushed back and said "we'll just try it and
see" — what's your response?**

A: My response is: cost the "keep alive" part before you cost the "build
it" part, because build is the cheap half. Ask: who owns the Cloudflare (or
whatever) account six months from now if the person who set it up stops
showing up to Tuesday nights? Every civic-tech project I've seen die had
that exact moment — a service only one person understood, that person
disengaged, and it sat broken for a year before someone finally ripped it
out. A static site surviving unattended weeks is a real property this
project already has; adding one live compute surface for a narrow win — and
narrow is being generous, since the free-tier gated ChatGPT/Claude
audience who'd even reach it is small right now — trades a property you
already have for a maintenance liability, for a benefit that doesn't touch
your actual measured failure mode. I'd log it as "revisit if usage or the
spec both stabilize," not "never," but not now.

---

**Q: Would you depend on OYL's contract for something you build? What would
you need to see first?**

A: For a side project, sure, cautiously, the way I'd depend on any
well-documented open dataset — pin the `contract_version` I built against,
validate the schema in my own CI on every fetch, and treat a schema
validation failure as a hard stop, not a warning I ignore. That's standard
practice for me now regardless of the source, it's just that most sources
don't hand me a schema to validate against, so I've had to write my own
guesses at one. Having the actual schema is most of what I need.

What I'd still want before treating it as load-bearing for anything
public-facing: a stated uptime/update-cadence commitment beyond "weekly, in
practice" — even a line saying "if a scheduled rebuild fails, here's what
you'll see" (stale `generated_at` I can detect myself, presumably, since
that field exists) — and ideally a place to watch for breaking changes that
isn't "diff the JSON yourself," which is the exact workaround I already do
for Socrata and would rather not duplicate for a second source. Honestly
the `generated_at`/`provenance` fields mostly solve the staleness-detection
half already — I can write my own "if generated_at is more than 10 days
old, warn" check client-side without OYL doing anything more. That's a
real, usable escape hatch. It's the breaking-change side that's still
manual.

---

**Q: The site refuses to normalize by ridership because it has no volume
data. Does that caveat change how you'd use it?**

A: It doesn't change whether I'd use the raw counts — I already work around
that gap myself, badly, the way I described. What it changes is whether I'd
let a UI I built show a ranked "most dangerous ward" list without also
showing the raw count next to it and a one-line version of that exact
caveat, because a ranked list implies a fair comparison whether you intend
that or not, and I've been burned exactly by that implication before on my
own tool. Good-enough exposure data, for me, would be something crude —
CDOT's traffic counter locations, even sparse and old, joined in as a
"partial exposure proxy, N locations only" — better than nothing stated
honestly beats nothing stated at all, same principle as the site's own
"missing number is honest, fabricated one isn't" line, which I'll say I
actually like as a stated policy, that's rare to see written down plainly.

## Magic-wand close

**Q: One dataset that doesn't publicly exist appears, clean and current.
What is it?**

A: Citywide per-corridor cyclist volume, even modeled rather than counted —
the way some cities use anonymized phone-mobility data as a volume proxy.
That single number retroactively fixes half the arguments I've watched die
in this space, including my own.

**Q: One chart or map you could put in front of your hardest audience that
ends an argument. Describe it.**

A: Not really a chart — a single reproducible link. Something I can send an
alderman's staffer that says "as of this exact timestamp, here is the crash
count near this exact corridor, here is the caveat, here is the source
query" — because the argument that actually kills my tools isn't "your
chart is wrong," it's "I can't tell if this number is current or if you
generated it once in March and forgot about it." A live `generated_at`
timestamp people can actually see, front and center, would do more for
trust than any visualization choice.

**Q: What would make you stop using a site like this after trying it
once?**

A: A silent shape break I catch by my own tool crashing instead of by a
changelog — that's the one thing that would make me route around it
permanently and never come back, because it's exactly the betrayal I
already catalog Socrata for. Second, slower burn: if the weekly rebuild
just... stopped, and `generated_at` sat stale for months with no note
anywhere saying "this project is paused" — I've bookmarked three civic-tech
tools that quietly died that way, still technically online, technically
"working," just wrong, and worse than dead because dead-and-labeled is
honest and stale-and-silent isn't.

---

# Structured memo

```
participant: civic-developer
confidence_notes: >
  The Socrata-drift and null-island stories are grounded in well-documented
  Chicago Data Portal realities (People/Crashes join requirement, geocoding
  nulls, undocumented server-side query-semantics drift) and are in-world for
  this persona class; treated as illustrative simulation, not a verified
  incident log. The MCP cost breakdown (compute surface, spec churn, "who
  owns the account in six months") tracks mcp-feasibility.md §2/§3/§6
  directly and does not go beyond it. The schema/CI-validation practice and
  the eval-harness reasoning are grounded in ordinary software-engineering
  norms for this persona class, not asserted from the eval-harnesses.md
  brief specifically (that brief was read for background but the participant
  was never shown it as stimulus, per the study's scope). Two claims are
  flagged low-confidence as simulation artifacts: the specific "two other
  Chi Hack Night tools died exactly that way" and "three civic-tech tools
  quietly died that way" are plausible-in-world texture, not evidence the
  simulation can source — treat as color, not data.

stated_needs:
  - need: A hand-written JSON Schema per endpoint, validated in the
      participant's own CI, with schema-validation failure as a hard stop.
    evidence_quote: >
      "pin the contract_version I built against, validate the schema in my
      own CI on every fetch, and treat a schema validation failure as a hard
      stop, not a warning I ignore... most sources don't hand me a schema to
      validate against, so I've had to write my own guesses at one."
    underlying_job: >
      Detect upstream shape breaks before they silently corrupt a
      downstream tool's output, rather than after a stranger reports it.

  - need: A changelog or breakage-notification channel distinct from the
      data files themselves.
    evidence_quote: >
      "a place to watch for breaking changes that isn't 'diff the JSON
      yourself,' which is the exact workaround I already do for Socrata and
      would rather not duplicate for a second source."
    underlying_job: >
      Avoid re-paying, for a second data source, the exact monitoring labor
      already sunk into surviving Socrata's silent drift.

  - need: A stated uptime / rebuild-failure policy beyond "weekly, in
      practice."
    evidence_quote: >
      "even a line saying 'if a scheduled rebuild fails, here's what you'll
      see'... It's the breaking-change side that's still manual."
    underlying_job: >
      Distinguish "the site is fine, just quiet" from "the site is
      silently broken" without having to build a custom staleness monitor —
      though the participant notes generated_at already substantially
      covers this.

latent_needs:
  - need: A scoped, single-hop-safe answer for OYL's own most-likely
      question ("which ward is most dangerous"), inlined as prose in
      llms.txt rather than requiring the ward JSON hop.
    inference_basis: >
      The participant was shown, not asked to imagine, the specific finding
      that one assistant fetched only llms.txt, never hopped to the ward
      endpoint, and produced a wrong ward number while still reciting the
      caveats correctly. Unprompted, they proposed inlining the single
      highest-value answer into llms.txt itself as a scoped fix, explicitly
      reasoning through and rejecting the more general "force the second
      hop" framing as mechanically impossible for a static-file publisher
      to enforce. This is a concrete, engineered proposal volunteered in
      response to observed behavior, not a feature they were asked to react
      to.
    risk_if_wrong: >
      If implemented uncritically, a hand-synced prose fact inside llms.txt
      becomes exactly the "second maintenance surface" the participant
      warned against elsewhere in the same answer (prose and JSON drifting
      apart) — the fix could recreate the class of bug it's meant to
      prevent if not generated programmatically alongside the JSON.

  - need: A visible, per-answer staleness signal (a prominent generated_at)
      treated as a first-class trust surface, not metadata.
    inference_basis: >
      Independently, in the "current practice" phase (own SQLite snapshot
      to diff against) and again unprompted in the magic-wand close (the
      "reproducible link" answer, and the stale-tool "worse than dead"
      answer), the participant repeatedly reached for recency/provenance as
      the actual trust lever, not chart design or number accuracy per se.
      They never asked to see this framed as a feature; it emerged three
      separate times from different questions.
    risk_if_wrong: >
      If OYL treats generated_at as already-solved because the field
      exists, it may miss that the participant's actual ask is about
      *visibility* and *staleness alerting* (a check they'd have to build
      themselves), not just field presence — the field existing and the
      need being met are not the same claim.

  - need: A drift-detection posture for OYL's own upstream (Socrata) that
      the participant would want disclosed, since OYL sits on the same
      unstable foundation the participant already distrusts.
    inference_basis: >
      The participant's entire current-practice narrative is about Socrata
      betraying query-semantics without notice. They never asked OYL "how
      do you protect yourselves from your own upstream," but their
      standard for what makes a source "safe to depend on" (client-side
      filtering, snapshot diffing, never trusting server-side query
      semantics) is a standard they would apply to anyone sitting on
      Socrata, including OYL, once the parasocial trust of "this looks
      well-built" wears off with use over months.
    risk_if_wrong: >
      OYL may already do exactly this (pipeline/emit_api.py's provenance
      handling is unread by this persona); the inference is about what the
      participant would eventually ask, not a confirmed gap in OYL's build
      process.

reactions_to_existing:
  - feature: JSON Schemas + additionalProperties:false envelope
    verdict: would-use
    why: >
      Directly addresses the participant's single biggest documented pain
      (silent Socrata shape drift); explicitly called "unusually good for a
      volunteer static-site project" and "a genuinely high bar."

  - feature: caveats array + data_tier + llms.txt answer-guidance
    verdict: would-use, with a named failure mode
    why: >
      Approved of the policy ("missing number is honest, a fabricated one
      isn't") but treated the wrong-ward/correct-caveat finding as proof
      the mechanism can produce a maximally-credible wrong answer — worse,
      in their words, than a plain wrong answer with no caveat at all.

  - feature: MCP server (proposed, not shipped)
    verdict: ignores / would actively advise against
    why: >
      Costed the compute-surface requirement, hosting/account-ownership
      risk, and 18-month spec churn explicitly against mcp-feasibility.md's
      own findings, and concluded it doesn't address the layer's actual
      measured failure (caveat-carriage), independent of hosting cost.

  - feature: generated_at / provenance fields
    verdict: would-use
    why: >
      Called out unprompted as "a real, usable escape hatch" that already
      lets them build their own staleness check client-side without OYL
      doing anything more — the one piece of the "depend on this" ask they
      consider already solved.

data_they_bring: >
  A personal changelog of Socrata datasets that have silently changed shape
  (source and date logged); a local snapshot (SQLite) of a clean pull kept
  specifically to diff future pulls against; a standing practice of
  client-side filtering because server-side query semantics are not trusted
  to stay stable. None of this exists in OYL's current inventory as a thing
  OYL offers a downstream builder — it is the participant's own workaround
  for exactly the failure class OYL's schema/contract-version machinery
  partially addresses.

deal_breakers: >
  (1) A silent shape break discovered by the participant's own tool
  crashing rather than by a changelog — named explicitly as the trigger
  that would make them route around OYL permanently. (2) A stale
  generated_at persisting for an extended period with no visible note that
  the project is paused — "worse than dead because dead-and-labeled is
  honest and stale-and-silent isn't."

vocabulary: >
  "Shape break" / "silently changed shape" (not "breaking change") for
  contract violations; "drift" for undocumented semantic changes to a
  filter or field; "null island" for bad geocoding; "danger score" used
  neutrally, matching OYL's own term; "load-bearing" for anything they'd
  depend on unattended; "hard stop" for a validation failure that should
  block a build rather than warn; "escape hatch" for a field that lets them
  self-monitor without publisher action.
```

