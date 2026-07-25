---
participant: automation-minded-researcher (new persona, study #1b)
scenario: >
  A transportation research analyst at a university transportation center
  (grounded as an MPO/UTC-adjacent research-world composite — grant-funded,
  IRB-irrelevant public secondary data, quarterly and annual reporting
  cycles) who maintains a standing crash-trend dashboard and a paper's
  replication dataset. Not a software engineer by identity — scripts in R,
  runs jobs via a shared server's cron because that's what campus IT allows,
  and has in the last year started delegating the glue work (re-checking
  sources, drafting changelog notes, chasing schema drift) to an AI
  assistant. This persona is new to study #1b; no prior interview or
  evidence brief exists for it. Interviewed per the agentic-layer extension
  kickoff (docs/research/agentic-layer/04-extension-kickoff.md), focused on
  functions — especially F-A, monitoring & automation — not discovery.
interview_date: 2026-07-23
model_note: >
  Simulated participant (Sonnet-class persona agent). Grounded in
  documented, generalizable research-world realities rather than a named
  prior evidence brief: grant reporting cadences (quarterly/annual),
  turnover of the RA/grad-student labor that builds and then abandons
  scripts, reviewer demands for provenance and replicability, and the
  well-documented problem of secondary administrative data (e.g. police
  crash records) being revised upstream after initial release. No claim is
  made that this maps to a specific real person or institution. Stimulus
  material is the as-built agentic-layer inventory
  (docs/research/agentic-layer/02-layer-inventory.md) plus the no-history
  fact and the 2026-07-23 live-test observations, presented as reported
  facts, not as OYL's self-description.
---

# Interview: automation-researcher (composite persona)

**Run date:** 2026-07-23
**Stimulus:** `02-layer-inventory.md` (contract v1.16); the no-published-history
fact; recent-months-provisional caveat; 2026-07-23 live-test observations
(caveat carried correctly by assistants reading the guidance file; one
assistant invented a specific number while still carrying correct caveats)
**Interviewer:** Lead Researcher (LR)
**Participant:** composite — research analyst, university transportation
center, maintains a standing bike/pedestrian crash-trend product

---

## Transcript

### 1. Context

**LR:** Describe your role and the last decision you influenced — or tried
to — about street safety. What did that actually involve, step by step?

**Analyst:** I run a small research group's crash-trend dashboard — it's
part of a grant we've had for going on three years now, transportation
safety analysis for the region, and one deliverable is a public dashboard
plus a quarterly PDF summary that goes to the state DOT program office as
part of our reporting. The last real decision — we had to decide whether to
flag a spike in reported cyclist crashes in one corridor as a finding in the
Q2 report, or hold it, because the most recent two months of the underlying
crash file looked unusually high and I wasn't sure yet whether that was real
or just under-reporting catching up. I ended up footnoting it instead of
headlining it. That's basically always the call I'm making — is this real,
or is this the data still settling.

**LR:** Who do you need to convince, and what does "convinced" look like for
them?

**Analyst:** Two audiences that want completely different things. The
program officer at the state DOT wants to see the deliverable exists, is
timely, and doesn't contradict what we told them last quarter without
explanation — they're not auditing my methodology, they're checking a box
that the grant is producing product. The other audience is whoever reviews
the paper that comes out of this eventually, and that one's brutal —
reviewer two always asks "how was this constructed, can I reproduce it,"
and if I can't answer that in the methods section I get a revise-and-resubmit
just for that.

**LR:** What information sources do you touch in a normal week for this
work?

**Analyst:** The city's open crash data portal is the backbone. A shapefile
of the bikeway network from the DOT that gets updated maybe twice a year,
irregularly, no announcement. Census/ACS for population and commute-mode
denominators. And increasingly whatever news or advocacy-org data I can find
to sanity-check the administrative numbers against, because the crash portal
undercounts things everyone knows it undercounts.

### 2. Current practice & workarounds

**LR:** Tell me about the last time you needed a number, map, or chart about
bike safety that you didn't already have on hand. Where did you go? What did
you do with it? How long did it take?

**Analyst:** A collaborator asked for ward-level crash rates for a
sub-analysis, which we don't normally slice by — we usually do it by
corridor or by our own study zones. So I had to go pull the raw crash file
again, join it to ward boundaries myself, because nobody publishes it
pre-joined at ward level in a form I trust, and then decide what to do about
crashes that fall exactly on a ward boundary line, which is its own little
rabbit hole. That took most of an afternoon, and then another hour arguing
with myself about whether the boundary-crash handling I picked was defensible
enough to write down in a footnote.

**LR:** What have you built yourself — spreadsheets, saved searches,
scripts, hand joins — because nothing gave it to you directly?

**Analyst:** The whole pipeline, basically. It's an R script, well, a set of
them now, that pulls the crash portal's CSV export, does field renames
because the column names have changed on us at least twice without warning,
recomputes a few rates, and spits out the figures for the dashboard and the
quarterly PDF. A grad student built the first version two summers ago. He
graduated. I inherited it with basically no comments in the code, and the
first month I owned it I broke the pipeline twice just figuring out what it
assumed. That's the single biggest tax on this job — not the analysis, the
archaeology of a script somebody else wrote and left.

**LR:** Tell me about a time data — or the lack of it — sank an argument you
were making, or cost you real time.

**Analyst:** The column-rename thing, twice. Once the crash portal renamed a
crash-severity field mid-quarter with zero notice, and my script silently
started returning nulls for severity instead of erroring, and it took me
embarrassingly long to notice — I want to say close to three weeks — because
the dashboard kept running, it just quietly stopped breaking down severity
right. Nobody outside caught it, thank God, but I did have to go back and
re-verify a full quarter's numbers before I trusted anything downstream of
that column again. That's the cost that never shows up in a time log —
verification after the fact, redoing work you already thought was done.

**LR:** What data do you distrust, and what earned that distrust?

**Analyst:** I distrust anything I can't re-pull and get the same answer
from a second time. We stopped using a regional advocacy group's crash
counts for anything quantitative in the paper — not because the numbers were
wrong, I actually think they were fine — but because when I went back to
cite the specific figure six months later for a revision, the page had
changed and the number wasn't the same anymore, and there was no version, no
date stamp I could point to, nothing I could put in a citation that a
reviewer could go verify. I still use it for framing, for "advocates have
raised concern about X," but never for a specific number that has to survive
peer review.

### 3. Stimulus walkthrough

**LR:** Let me describe what On Your Left! publishes. It's a static,
versioned JSON API — a machine-readable version of the same data the human
site shows. Every file, including a per-ward file, carries a contract
version number, a build timestamp, provenance, and a reliability tier —
whether a number is a real measured value, a proxy, or something else. There
are machine-readable caveat codes attached to individual numbers, and
published JSON Schemas for every file shape. It rebuilds weekly, no key, no
signup.

**Analyst:** Okay — that's already further than most sources I deal with.
The tier and the caveat codes being *machine-readable*, not just prose
somewhere on a page, is the part that actually changes what I could do with
it, because right now I have to read a paragraph and manually decide "does
this apply to my use," and that's exactly the kind of thing I'd want an
assistant doing instead of me. What's the versioning apply to — the schema,
or the data inside it?

**LR:** The contract version is the shape — it bumps when a field is added
or removed, additive changes don't bump it. The data itself is rebuilt
weekly and the previous build is overwritten. There's no published history:
no archived snapshots, no changelog of what numbers changed between builds,
no diffs.

**Analyst:** Say that again — overwritten, not archived?

**LR:** Correct. Each weekly build replaces the last one. If a number
changes from one week to the next, there's no record anywhere of what it
was before, unless something outside the site captured it.

**Analyst:** [pause] That's — okay, that's the thing that actually matters
more to me than almost anything else you've described. Let me think about
what that breaks, concretely. First, replication — if a reviewer asks me two
years from now "reproduce figure 3," and figure 3 pulled a number from this
site the week I built it, I have no way to point them at what the site said
that week. I'd have to have saved it myself. Second — and this is the one
that actually worries me more — trend claims. Half of what a transportation
safety paper argues is "this got better" or "this got worse" over time. If
the underlying source doesn't keep its own history, and if it revises
numbers silently as more crash reports come in — which you're telling me it
does, for recent months — then a trend line I built by re-pulling this
source every quarter isn't actually a trend line of reality, it's partly a
trend line of when I happened to look.

**LR:** How would you handle that today, with a source that behaves this
way?

**Analyst:** The honest answer is I'd have to build my own archive — pull it
on a schedule, myself, and keep every pull, timestamped, forever, the same
way I already have to do for the crash portal's raw export, because that one
revises silently too. Which is not a new problem for me, revision without
history is basically the normal condition of administrative data, but it
means this source doesn't save me the archiving work, it just gives me a
cleaner thing to archive.

**LR:** Would you trust an archive your own assistant built and kept
locally, or does the archive have to come from the publisher itself to count
for something like a citation?

**Analyst:** Different jobs, and I want to be careful about the difference.
For my own internal use — catching a spike, deciding whether this quarter's
number is a real trend before I write the footnote — an assistant-maintained
local archive is completely fine, honestly better than what I have now,
because right now that archiving is manual and it's the first thing that
slips when I'm busy. But for something that has to survive a reviewer
demanding I reproduce a cited figure, my own local file isn't good enough on
its own — a reviewer has no reason to trust a CSV that only exists on my
machine, timestamped by me. For that, I need something with a URL a stranger
can hit and get the same answer I got, which either has to be the
publisher's own archived snapshot, or a DOI'd deposit of my own pull in
something like a data repository — Zenodo, ICPSR, our own institutional
one — which is honestly what I already do for the crash portal exports I
use in a published paper. I archive my own pull and cite the archive, not
the live source, specifically because the live source doesn't keep history
itself.

**LR:** Recent months of crash data are provisional here too and get amended
upstream — the site says so explicitly.

**Analyst:** Good, that I can work with, because it's naming the exact
failure mode I already build around for the crash portal — I have a standing
rule in my pipeline to treat the trailing two months as provisional and
either exclude them from headline trend numbers or flag them, and I'd apply
the identical rule to this source without having to think about it twice.
What I'd actually want is for that provisional window to be a queryable
field, not just a sentence — tell me exactly which months are still
provisional as of this build, so I don't have to hardcode "always drop the
last sixty days" and hope that's still the right window.

### 4. Gap probing

**LR:** Here's a scenario. You maintain the standing crash-trend dashboard I
described. If scheduling something against a source like this were trivial —
you could just say "watch this and tell me" — what's the first thing you'd
schedule?

**Analyst:** A weekly diff against a locked reference — did the ward-level
crash counts for my study wards change since last week's pull, and if so, by
how much, and does the change look like normal provisional revision or
something structural, like a methodology change. That's the exact job I do
manually right now every time I re-run the pipeline before a quarterly
deliverable, and I do it by eyeballing summary stats against my last output,
which is not a rigorous process, it's just me pattern-matching "does this
number look about right." I would trust an assistant to flag "this changed
more than X percent, go look" way sooner than I'd trust it to tell me the
change is fine.

**LR:** What's the second thing?

**Analyst:** A contract-version watch — tell me immediately if the shape of
a file I depend on changes, don't make me find out three weeks later because
a column silently started returning nulls. That's precisely the failure that
cost me the worst verification tax I've had. If something had pinged me the
week the crash portal renamed that severity field, instead of three weeks
later when I happened to notice a chart looked wrong, that's most of a
month's work I get back.

**LR:** You mentioned the "recent months provisional" caveat and the tier
system. What would make a source like this actually *citable* in your
world — in a methods section, in a footnote a reviewer might chase?

**Analyst:** Three things, roughly in order. A stable identifier for the
specific version I used — not just "contract version 1.16," but something
that resolves to the actual data as of the day I pulled it, ideally with a
DOI or at minimum an archived, dated, publicly-fetchable snapshot I can put
a URL to. Second, a changelog — even a short one, "this build's numbers
differ from last week's here and here" — because right now if I want to know
whether a number moved I have to have kept my own copy to compare against,
and most people using a source like this for the first time won't have that.
Third — and this is the one people underestimate — I need to be able to say
in a methods section *why* a number might differ from another paper citing
the same nominal source at a different date, and right now I can't do that
without my own private archive doing the work the publisher didn't.

**LR:** What does "the data changed under me mid-study" actually cost you,
concretely, the last time something like that happened?

**Analyst:** The severity-field example is the cleanest one — call it three
weeks of not knowing, then most of a day re-verifying a full quarter's
output once I found it, then an uncomfortable conversation with my PI about
whether anything already sent to the state program office needed a
correction. It didn't, in the end, because the error only affected an
internal breakdown we hadn't published yet, but I spent that day not knowing
that yet, which is its own cost — the anxiety tax, not just the labor tax.
What would have prevented it is exactly what you described earlier — a
contract-version bump, or even just a machine-readable "this field's meaning
changed" flag I could have had my pipeline check for automatically instead
of relying on me eyeballing a chart.

**LR:** Of everything a source like this does *not* have — a published
history — what single absence costs you most?

**Analyst:** The history, full stop, more than any other gap you could name.
Tiers and caveats tell me how to treat a number today. History tells me
whether the trend I'm reporting is a trend in the world or a trend in when I
looked. For a safety researcher, that's not a nice-to-have, that's the
actual product — nobody's paying my grant to report a single week's snapshot,
they're paying it to report change over time, and change over time is
exactly the thing an overwrite-only source can't let me verify independently
of my own archiving discipline.

**LR:** The site refuses to normalize by ridership because it has no volume
data. Does that change how you'd use it?

**Analyst:** Not really, because I already don't trust anyone's ridership
denominator, including the ones I've used myself — count-based sensors that
cover six corridors and get extrapolated citywide, ACS commute-mode share
that undercounts recreational and short trips badly. An honest "we don't
have this" is more useful to me than a source that quietly bakes in a shaky
denominator and doesn't tell you. I'd rather bring my own exposure proxy,
footnoted with its own limitations, than inherit an unstated one. What I'd
actually want from this source isn't ridership data, it's raw counts I
trust are counted consistently over time — which loops right back to the
history problem, because "consistently over time" is unverifiable without
it.

### 5. Magic-wand close

**LR:** Magic wand — one dataset that doesn't publicly exist appears, clean
and current. What is it?

**Analyst:** An archived, versioned time series of every crash-data source I
touch — the city portal and this one both — where every past build is
retrievable by date, with a diff between any two dates. Not just for this
source, for the whole category of administrative safety data I depend on.
That one thing would eliminate probably a third of my pipeline's actual
code, the part that exists purely to defend against silent upstream change.

**LR:** One chart or automation you could put in front of your hardest
audience — reviewer two — that ends an argument?

**Analyst:** A provenance chain rendered automatically at the bottom of
every figure — source, contract version or build date, tier, and a link to
the archived snapshot the figure was built from — generated by the pipeline
itself, not hand-typed by me at 11pm before a submission deadline. Reviewer
two stops asking "how was this constructed" if the answer is already
sitting under the chart in a form they can click.

**LR:** What would make you stop using a source like this after trying it
once?

**Analyst:** Two things, and they're related. One — if I ever caught it
being wrong in a way that carried the right-sounding caveat language, the
way you described one assistant inventing a specific number while still
correctly restating the caveats. That's worse to me than a source with no
caveats at all, because a caveat-literate wrong answer passes the exact
credibility check I use to decide whether to trust something quickly. Two —
if using it required me to trust an assistant's memory of a number instead
of a URL I can put in a footnote and a reviewer can independently fetch.
I'll delegate the checking and the watching to an assistant happily. I won't
delegate the citing. The number in my paper has to trace to something a
stranger can go verify without asking me or my assistant to vouch for it.

---

## Analysis Memo

```
participant: automation-minded-researcher (new persona, study #1b)
confidence_notes: This is a new persona introduced for study #1b with no
  prior interview or dedicated evidence brief to ground it against, unlike
  the study-#0-derived personas re-run elsewhere in this study. It is
  grounded instead in generalizable, well-documented features of the
  research-data world named explicitly in the kickoff prompt: grant
  reporting cadences, RA/grad-student turnover on inherited pipelines,
  reviewer demands for provenance and reproducibility, and the standard
  practice (ICPSR/Zenodo-style archival citation of a specific pull) for
  citing administrative data that itself has no publisher-side history.
  Those grounding facts are broadly true of the research world this persona
  represents, not sourced to one named real institution, so treat the
  specific anecdotes (the severity-field rename, the boundary-crash
  afternoon, the advocacy-group citation drift) as illustrative composites
  in the tradition of this study's other personas, not documented incidents.
  The strongest, best-grounded material is everything about the no-history
  gap and archival citation practice — that maps tightly onto real,
  well-known research-data norms. The weakest material is the specific
  automation asks in section 4 (contract-version watch, weekly diff
  scheduling) — these are plausible extrapolations from her stated pain
  points, not independently corroborated by a documented world the way
  Marcus Webb's ward-office habits were in the prior interview.

stated_needs:
  - need: A machine-readable way to identify which time window of a
      dataset is still provisional, rather than a prose caveat she has to
      hardcode a guess around.
    evidence_quote: "What I'd actually want is for that provisional window
      to be a queryable field, not just a sentence... so I don't have to
      hardcode 'always drop the last sixty days' and hope that's still the
      right window."
    underlying_job: Build a pipeline rule that stays correct as the
      provisional window shifts, without manual re-checking each cycle.

  - need: A stable, dated, independently-fetchable identifier for the exact
      version of the data she used, suitable for a citation a reviewer can
      chase.
    evidence_quote: "A stable identifier for the specific version I
      used... ideally with a DOI or at minimum an archived, dated,
      publicly-fetchable snapshot I can put a URL to."
    underlying_job: Survive a reviewer's reproduce-this-figure challenge
      without her own private archive being the only proof a number existed.

  - need: A changelog or diff between builds, even a minimal one, so she
      does not have to maintain her own comparison copy just to know if a
      number moved.
    evidence_quote: "If I want to know whether a number moved I have to
      have kept my own copy to compare against, and most people using a
      source like this for the first time won't have that."
    underlying_job: Detect and explain quarter-to-quarter or paper-to-paper
      discrepancies in a cited figure without redoing archival work the
      publisher could have done once, centrally.

  - need: Early warning when a depended-on file's shape or field meaning
      changes, rather than discovering it weeks later via a broken
      downstream chart.
    evidence_quote: "Tell me immediately if the shape of a file I depend on
      changes, don't make me find out three weeks later because a column
      silently started returning nulls."
    underlying_job: Prevent silent pipeline corruption from propagating into
      a public deliverable before anyone notices.

  - need: An honest refusal/absence signal (e.g., no ridership data) over an
      unstated or shaky proxy baked silently into a number.
    evidence_quote: "An honest 'we don't have this' is more useful to me
      than a source that quietly bakes in a shaky denominator and doesn't
      tell you."
    underlying_job: Preserve her ability to choose and footnote her own
      exposure proxy rather than unknowingly inheriting an unstated one.

latent_needs:
  - need: A citation-grade archival tier, distinct from and additional to a
      convenience-grade local archive her own assistant could maintain —
      she needs the publisher (or a DOI-registered third party) to be the
      root of trust for anything that ends up in a methods section, even
      though an assistant-maintained local archive is fully sufficient for
      her day-to-day monitoring use.
    inference_basis: She drew this distinction unprompted and specifically:
      "For my own internal use... an assistant-maintained local archive is
      completely fine... But for something that has to survive a reviewer
      demanding I reproduce a cited figure, my own local file isn't good
      enough on its own — a reviewer has no reason to trust a CSV that only
      exists on my machine, timestamped by me." This tracks a real,
      documented norm in her world (archiving a specific pull to
      Zenodo/ICPSR/an institutional repository rather than citing a live
      URL) that she names as something she already does for the crash
      portal today.
    risk_if_wrong: OYL is a volunteer-run, static-file project with no
      accounts and an explicit constraint against anything resembling a
      preview/embargo channel; building or partnering for DOI-grade archival
      infrastructure is a materially heavier commitment than a caveat field
      or a changelog, and may be disproportionate to how many of OYL's
      actual users are publishing peer-reviewed work versus dashboards and
      memos — this need may apply narrowly to a small, high-rigor slice of
      the audience rather than the automation-minded audience broadly.

  - need: A "why did this number differ from what I cited last quarter"
      self-service explanation path — not just a raw diff of values, but
      enough context (methodology change vs. provisional-revision vs.
      genuine trend) to write the one sentence a reviewer or program officer
      will accept.
    inference_basis: She distinguished, unprompted, between a "normal
      provisional revision" and "something structural, like a methodology
      change" when describing what she'd want flagged in a weekly diff, and
      separately said she needs to "say in a methods section why a number
      might differ from another paper citing the same nominal source at a
      different date." A bare diff (what changed) does not on its own answer
      why it changed — she needs the second layer to actually write the
      sentence, which she named as a distinct, harder job than just noticing
      the change.
    risk_if_wrong: This may be asking OYL (a volunteer project) to encode
      causal/methodological metadata about its own revisions that requires
      human judgment to write accurately each time a number moves — a
      heavier standing commitment than a mechanical version bump, and one
      that could be systematically under-resourced given the project's
      weekly-unattended-build constraint, making this a need OYL structurally
      cannot fully satisfy rather than a straightforward build item.

  - need: A machine-checkable trust signal that distinguishes a
      caveat-correct answer from a caveat-correct-but-fact-wrong one — she
      cannot currently tell, from an assistant's fluent output alone,
      whether the specific number is grounded in a real fetch or invented
      while carrying otherwise-correct caveat language.
    inference_basis: She named the caveat-literate wrong answer as her
      single strongest deal-breaker, ranked explicitly above a source with
      no caveats at all: "That's worse to me than a source with no caveats
      at all, because a caveat-literate wrong answer passes the exact
      credibility check I use to decide whether to trust something
      quickly." This mirrors, independently, the same failure mode the
      ward-staffer interview flagged (a caveat-correct, fact-wrong answer as
      the worst case) — convergence across two differently-grounded personas
      strengthens rather than weakens this inference, but she did not
      propose any concrete mechanism for the signal, only the felt need for
      one.
    risk_if_wrong: Like the ward-staffer's parallel finding, this failure
      happens inside a third-party assistant's generation step, potentially
      outside anything OYL's static-file publishing model can directly
      instrument or fix — treating this as a buildable OYL feature rather
      than a channel-level limitation risks misallocating engineering effort
      OYL has no lever to pull on.

reactions_to_existing:
  - feature: Machine-readable caveats and per-number reliability tiers
    verdict: would-use
    why: Explicitly said this is "further than most sources I deal with"
      and specifically valued that the caveats are machine-readable rather
      than prose she'd have to interpret by hand — names it as something an
      assistant could act on directly instead of her doing the triage.
  - feature: `recent_months_provisional` caveat
    verdict: would-use, matches an existing personal practice
    why: Maps directly onto a standing rule she already has in her own
      pipeline for the city crash portal (exclude or flag the trailing
      window); adopts it without hesitation, but immediately asks for it as
      a queryable field rather than fixed prose.
  - feature: No published history / overwrite-only builds
    verdict: distrusts — names it as the single costliest absence in the
      whole inventory
    why: Breaks both replication (can't show a reviewer what a past build
      said) and trend claims (can't distinguish real change from
      when-she-looked artifact) — the two things her funded deliverable
      exists to produce; states this absence outweighs every other feature
      discussed.
  - feature: `not_normalized_by_ridership` caveat / no volume data
    verdict: would-use — treats the honest gap as a non-issue
    why: Already distrusts every ridership denominator she's used
      personally; prefers an explicit absence she can footnote her own proxy
      around over an unstated, shaky one baked into someone else's number.
  - feature: Contract versioning (shape changes require a version bump)
    verdict: would-use, but wants it as an active alert, not passive
      documentation
    why: Directly maps to her worst documented cost (the silent
      severity-field rename that cost roughly three weeks of undetected
      drift plus a day of re-verification); wants a push/watch mechanism
      built on top of the version field, not just the field's existence.

data_they_bring: A three-week-old undetected pipeline break from a silently
  renamed upstream field, and the re-verification cost that followed it,
  which now anchors her default posture toward any source that can change
  shape without notice; an inherited, under-documented R pipeline from a
  graduated RA that she treats as a standing tax on the job; an existing
  archival-citation practice (depositing a specific pull to a repository
  like Zenodo/ICPSR and citing that rather than a live URL) that she already
  applies to the city crash portal and would apply identically to a source
  like this one; a personal rule of thumb for handling provisional recent
  months that predates and generalizes beyond this specific source.

deal_breakers: (1) A caveat-literate wrong answer — an assistant that
  invents or misstates a specific number while still correctly restating
  the source's caveats — which she ranks as strictly worse than no caveats
  at all, because it defeats the exact fluency-based credibility check she
  uses to move quickly. (2) Any workflow that asks her to cite an
  assistant's memory of a number, or a source with no independently
  fetchable, dated proof, in a methods section — she will delegate
  monitoring and checking to an assistant but will not delegate the
  citation itself; the number in the paper must trace to something a
  stranger can verify without her or her assistant vouching for it.

vocabulary: standing dashboard, quarterly deliverable, program officer,
  reviewer two, revise-and-resubmit, methods section, footnote (as a verb
  and a hedge — "footnoted it instead of headlining it"), provisional
  window, silent rename, archaeology (of an inherited script), the
  verification tax / anxiety tax, archived snapshot, DOI'd deposit,
  boundary-crash handling, structural vs. provisional (revision types). She
  never adopts OYL-internal vocabulary unprompted — does not say "contract
  version," "data tier," or "caveat code" spontaneously; when discussing
  those concepts she translates them into her own terms ("shape," "the
  meaning of a field," "queryable field") consistent with someone who
  scripts for a living but does not think of herself as a software person.
```
