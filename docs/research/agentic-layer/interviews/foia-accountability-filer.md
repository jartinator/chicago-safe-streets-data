---
participant: foia-accountability-filer
scenario: professional accountability requester (policy analyst at a Chicago watchdog/transparency nonprofit — BGA/Illinois Answers/MuckRock-user world), transportation among their beats
interview_date: 2026-07-23
model_note: simulated persona agent, Sonnet-class model, per docs/research/user-needs/01-lead-researcher.md
---

## Transcript

**Interviewer:** Tell me about your role, and walk me through the last time
you tried to get a public agency to hand over records it didn't want to hand
over.

**Participant:** I'm a policy analyst — records requests are maybe a third of
my actual job, across whatever beat is hot, and transportation comes up more
than you'd think because there's real money and real crash data behind it.
Last contested one: I was working a story angle on whether the city's bike/bus
lane camera enforcement — the Smart Streets pilot — was actually hitting
delivery fleets the way officials claimed, or whether it was mostly
individuals. I filed with the Department of Finance in early June. Standard
FOIA: 5 ILCS 140, cite the statute, describe the records precisely, ask for
native format not PDFs.

**Interviewer:** What did "describe precisely" mean in practice — how did
you decide what to ask for?

**Participant:** You don't ask for "enforcement data," you ask for the actual
fields you think exist in their citation database — date, time, location,
violation type, warning vs. citation, fine amount, registrant name and
whether it's a business or individual, ward. If you're vague they'll either
sit on it trying to figure out what you mean, or they'll hand you a summary
PDF instead of the underlying rows, and then you've burned a request cycle
getting something useless. I only knew to ask for "registered owner, business
vs. individual" because I'd seen a Tribune story reference delivery-company
names, which told me the field exists and is disclosable — so I cited that
story in the request to preempt the "we don't maintain that" dodge.

**Interviewer:** What happened after you filed?

**Participant:** Acknowledged same day through their GovQA portal, got a
tracking number. Then, also same day, they invoked the five-business-day
extension under 3(e) — "consultation with another public body," which
usually means they're checking with CDOT or their camera vendor before they
answer. That's routine, not a red flag by itself. I also cc'd CDOT because I
wasn't 100% sure which department was the actual keeper of the records — DOF
administers the fines, CDOT co-owns the program. CDOT closed their copy same
day with the standard "not the keeper, most likely keeper is DOF" language,
citing Duncan Publishing. That's fine, expected, it just means my hedge cc
worked as insurance rather than getting me a second answer.

**Interviewer:** And after the extension — what did the tracking actually
cost you?

**Participant:** Everything after the file is just a calendar problem
multiplied across forty-some open requests at any given time. Statutory clock
starts on receipt, five business days, they almost always take the extension,
so you're really tracking a moving date per request, plus separately tracking
"did they actually respond by that date" because if they blow the deadline
you have grounds to escalate — either a denial-by-default framing in a nudge
email, or if it's a real fight, you appeal to the Public Access Counselor at
the AG's office. I keep a spreadsheet: agency, date filed, tracking number,
statutory due date, extension invoked y/n, follow-up date, appeal deadline.
That spreadsheet is the actual product of my FOIA practice — more than any
individual request.

**Interviewer:** Tell me about a time the records themselves, or the lack of
them, sank an angle you were working.

**Participant:** The city doesn't have a public bicycle count dataset — no
ongoing counter program on the open data portal, unlike New York or DC. I
wanted to write about whether bike infrastructure spending correlated with
actual ridership growth, and I couldn't, because there's no volume
denominator. CDOT cites a Replica-commissioned analysis for ridership growth,
but that's a vendor deliverable, not raw counts, and I couldn't get the
underlying trip tables without a separate ask. I ended up dropping the
ridership angle and writing about infrastructure mileage instead, which is a
weaker story — "miles built" isn't "people using it." That's the kind of gap
that just quietly reshapes what stories get written, because nobody flags
"this number doesn't exist" loudly enough for a reporter on deadline to
notice before they've already committed to an angle.

**Interviewer:** What data do you distrust, and what earned that distrust?

**Participant:** Anything an agency self-reports as a rolled-up summary
without the row-level backup, because I've had agencies hand me PDFs that
don't reconcile with numbers they gave a reporter in a press release the same
month. And "sponsorship counts" for legislation — you can sponsor something
performatively and never push it. I'd rather see recorded votes, and when
there aren't many recorded votes because most things pass on voice vote, that
absence itself is a finding, not a null result.

**Interviewer:** [Stimulus] Let me describe what On Your Left! publishes.
It's an open-source dashboard on Chicago bike safety — crashes, bikeway
network, ward rankings, alderman records, hearings. For every number it
states the source, the method, when it was built, and known caveats — and it
says plainly, in a few places, which data it does not have publicly: no
ridership/exposure counts, no real obstruction reports (that layer is
synthetic and gated off the main site), no install-date history on the
bikeway network, dooring flagged as structurally undercounted because
official crash records only capture "reportable" crashes. There's also a
static machine-readable API alongside the human site. What's your first
reaction?

**Participant:** The "here's what we explicitly don't have" framing is more
useful to me than the dashboard itself, honestly. Most public dashboards
either don't say what's missing, or bury it in a methodology footnote nobody
reads. If OYL is willing to say "no public ridership data exists" as a
first-class claim rather than a caveat, that's a targeting signal — it tells
me where a FOIA would actually produce something new versus where I'd be
asking for data that provably doesn't exist anywhere, public or otherwise. I
would use it to *not* waste a request. The dooring-undercount flag is
interesting for a different reason — it's not "we don't have the data," it's
"the data structurally can't capture this," which is itself a story: why
doesn't dooring get reported the way other crashes do, and what would it take
to fix the reporting requirement, not just the dataset.

**Interviewer:** Would you trust the "doesn't exist publicly" claim as
accurate, or would you verify it yourself first?

**Participant:** I'd verify before I built a pitch or a FOIA on it, the same
way I'd verify anything a source tells me — but "verify" here means
something specific and cheap: check the open data portal myself, maybe one
search, because absence claims age badly. A dataset that didn't exist in
March can get published in July and nobody updates a static claim on a
website. If OYL's claim came with a build date and I could see it was
checked recently, that's most of the way to trusting it without redoing the
work myself.

**Interviewer:** You mentioned the API. Would that change anything for you
specifically, versus the human site?

**Participant:** For my own request-drafting, not really — I'm reading
methodology pages and caveats, not machine-consuming a JSON feed by hand.
Where an API matters to me is if I start actually using an assistant to help
draft, which I do for some of this already — I use one to turn my messy notes
into the FOIA boilerplate and to keep the tracking spreadsheet current, remind
me of due dates. If that assistant could also read something like OYL's
methodology and gap pages reliably — not paraphrase them wrong — that's
useful, because right now I do that reading myself and it's slow.

**Interviewer:** Walk me through what you'd actually hand to an assistant
versus keep for yourself, on your last request.

**Participant:** I'd hand it the boring, mechanical parts. Compute the
statutory due date from the filing date and tell me if an extension was
invoked. Watch for the acknowledgment and flag if none arrives in a
reasonable window. Draft the follow-up nudge language when a deadline passes.
Maintain the tracker across all open requests so I'm not manually updating a
spreadsheet every morning. I would not hand it the actual scoping — deciding
which fields to ask for, which prior news story to cite as leverage, whether
to cc a second department as insurance, whether this is worth an appeal to
the PAC or not worth the fight. That's judgment built from knowing how these
agencies specifically behave — DOF stalls on consultation grounds, CDOT
bounces things it doesn't own, the Clerk is slower but more complete. An
assistant that hasn't filed forty of these doesn't have that pattern
recognition yet, and I wouldn't trust it to guess.

**Interviewer:** If OYL handed you one export or artifact a week, what would
it contain, and who would you send it to?

**Participant:** Honestly, a running "known gaps" list with dates — what
doesn't publicly exist as of this week, ranked by how many stories or
requests would become possible if it did — would be the single most useful
thing, more than any chart. I'd forward that internally, to whoever's
picking beats that week, not to a source or an official.

**Interviewer:** OYL's maintainer runs their own FOIA program partly through
an assistant already — a gap in the data triggers a draft, with the record
descriptions and source citations verified against live pages, a human sends
it, and then the assistant tracks acknowledgments and statutory deadlines and
schedules follow-ups. Three requests are in flight right now with CDOT and
the Clerk. Does that match how you'd run it, or is something missing?

**Participant:** That's the right shape for the mechanical half — draft from
a documented gap, verify anchors, human sends, track deadlines. What I don't
hear in that description is the adversarial half: what happens when an
agency narrows the request, or a portal makes you re-enter the whole thing in
a web form instead of accepting an email, or the response comes back with
records withheld under an exemption and you have to decide whether it's worth
a PAC appeal. Those are the moments that actually determine whether a request
produces anything, and they require someone who's seen an agency dodge before
to recognize the dodge. If the assistant is only tracking dates and drafting
the first ask, it's handling maybe 40 percent of the lifecycle — the
easy 40 percent. The other 60 is what makes me a professional at this instead
of someone who files one FOIA a year and gives up when they get a form
denial.

**Interviewer:** You said the assistant reliably carries caveats. Any
scenario where that alone isn't enough?

**Participant:** If it's citing my numbers correctly but inventing a specific
figure somewhere else in the same document, that's actually worse than being
wrong across the board, because I'd trust the parts I didn't personally check.
That's the same failure mode as an intern who gets the footnotes right and
fabricates one stat in the body text — you stop trusting the whole document,
but only after it's already gone out. I'd want the caveat to travel with
every individual number, not just live in a disclaimer at the top.

**Interviewer:** Would you want agencies' returned FOIA records folded back
into a public dataset like OYL's?

**Participant:** Cautiously, yes, if it's clearly labeled as "records
obtained via request, not agency-published" and dated to when it was
received, because that's a different tier than an open-data-portal feed —
it's a snapshot, not a live pipe, and someone should be able to tell at a
glance which is which. I'd also want to know it wasn't re-summarized in a way
that lost the original structure — I'd rather link to the raw production
myself than have OYL's version become the citation people quote instead of
the source record.

**Interviewer:** Magic wand — one dataset that doesn't publicly exist
appears, clean and current. What is it?

**Participant:** Citation-level enforcement data for every camera and
red-light program in the city, refreshed monthly, not just Smart Streets —
because right now every one of those requires its own FOIA fight and they're
all structured slightly differently depending on which vendor and which
department.

**Interviewer:** What would make you stop using a site like OYL after
trying it once?

**Participant:** If a number I could independently check against a primary
source turned out to be stale or wrong and there was no visible build date
to tell me it was outdated before I relied on it. I don't need it to be
perfect, I need it to be honest about its own age.

## Structured memo

confidence_notes: The persona's process knowledge (5-business-day clock,
3(e) consultation extensions, PAC appeals, "not the keeper" bounces, GovQA
portal mechanics, native-format vs. summary-PDF distinction) is grounded
directly in this project's own `docs/foia/log.md` and `docs/outbox/`
letters, so it stays in-world throughout — this is the persona whose
documented reality the project already operationalizes for itself, which
makes the interview unusually well-anchored but also means some answers may
overfit to OYL's own FOIA practice rather than a genuinely independent
professional's habits. The "known gaps" ranking answer and the "citation
data across all camera programs" magic wand are extrapolations beyond
anything OYL currently ships or any external evidence about MuckRock/BGA
workflows — flagged low-to-medium confidence as inference from role logic,
not documented behavior.

stated_needs:
  - need: A dated, explicit "what doesn't publicly exist" list to avoid
    filing requests for data that provably can't be produced.
    evidence_quote: "If OYL is willing to say 'no public ridership data
    exists' as a first-class claim rather than a caveat, that's a targeting
    signal... I would use it to not waste a request."
    underlying_job: Allocate a scarce request budget (each FOIA costs a
    cycle of drafting, tracking, and calendar risk) toward asks that can
    actually produce new records.
  - need: An assistant that owns the mechanical lifecycle — statutory
    deadline computation, acknowledgment tracking, follow-up drafting,
    cross-request tracker maintenance — without taking over scoping
    judgment.
    evidence_quote: "I would hand it the boring, mechanical parts... I would
    not hand it the actual scoping... that's judgment built from knowing how
    these agencies specifically behave."
    underlying_job: Scale personal capacity across dozens of simultaneous
    open requests without losing the pattern-recognition that makes
    requests succeed.
  - need: Provenance/build-date visibility on every published number so
    staleness is detectable before it's relied on.
    evidence_quote: "I don't need it to be perfect, I need it to be honest
    about its own age."
    underlying_job: Avoid citing a number publicly that turns out to be
    outdated, which damages personal and institutional credibility.
  - need: Any folded-in FOIA-derived records must be clearly tiered/dated as
    "obtained via request" and linkable to the original production, not
    silently blended with agency-published data.
    evidence_quote: "I'd rather link to the raw production myself than have
    OYL's version become the citation people quote instead of the source
    record."
    underlying_job: Preserve chain-of-custody so her own reporting/records
    citations remain defensible under scrutiny.

latent_needs:
  - need: The maintainer's current assistant-run FOIA workflow (gap →
    draft → send → track) needs an adversarial-response layer — narrowing
    fights, portal-form friction, exemption/denial triage, PAC-appeal
    judgment — to match professional practice; without it the workflow
    covers only the pre-response half of the lifecycle.
    inference_basis: The participant, unprompted, split the described
    maintainer workflow into "the easy 40 percent" (drafting from a gap,
    tracking dates) versus "the other 60" (recognizing an agency's dodge,
    deciding whether a narrowing counteroffer is acceptable, deciding
    whether to appeal), and grounded this in specific documented behavior
    she'd already seen in the stimulus's own log (DOF invoking a 3(e)
    extension, CDOT bouncing a cc as "not the keeper") — she reasoned from
    OYL's own artifacts, not a generic complaint.
    risk_if_wrong: If overbuilt, this becomes a large scope-creep item
    (essentially an agency-behavior expert system) chasing a need one
    persona voiced from general professional pattern-recognition rather
    than a demonstrated OYL failure; a lighter version (surface the
    narrowing/denial/appeal step as a checklist prompt, not automate the
    judgment) may satisfy the actual gap.
  - need: Per-number caveat/provenance carriage is necessary but
    insufficient — the failure mode that actually breaks trust is a
    fabricated number sitting *next to* correctly-caveated real ones in the
    same document, which is harder to catch than uniform unreliability.
    inference_basis: Participant volunteered, unprompted by a question about
    fabrication risk specifically, that inconsistent accuracy ("gets the
    footnotes right and fabricates one stat in the body") is "actually worse
    than being wrong across the board" because it defeats spot-checking —
    this tracks the stimulus's own stated finding (2026-07-23 tests: caveats
    carry correctly, but an assistant can still invent a specific number)
    and the participant reasoned to its exact professional consequence
    (loss of trust in an already-sent document) without being told that
    finding existed.
    risk_if_wrong: Overweighting this could push toward expensive
    per-number verification tooling; the participant's actual ask was
    narrower (numbers should carry a visible check/build date, not that
    every number needs cryptographic proof) — verify against her stated
    ask before building.
  - need: A ranked (not just enumerated) gap list — "if this existed, how
    many stories/requests would it unlock" — would function differently
    from a flat "we don't have X" list, because it does the triage work she
    currently does herself when picking which absence to chase.
    inference_basis: When asked what single weekly artifact she'd want, she
    reframed OYL's existing gap-documentation practice ("what OYL is
    deliberately NOT") into a ranked, dated, forward-looking product rather
    than repeating the stimulus's static caveat framing back — a
    spontaneous elaboration beyond what was presented, consistent with her
    stated editorial-triage job ("whoever's picking beats that week").
    risk_if_wrong: This is the most speculative inference in the interview —
    it assumes a newsroom/pitch-triage process this single persona
    described but that a lone simulated interview can't validate is typical
    of the professional-filer population; treat as a build hypothesis to
    test with a second real filer, not a committed requirement.

reactions_to_existing:
  - feature: The explicit "what OYL deliberately is NOT" gap list (no
    ridership data, no real obstruction reports, no install dates, dooring
    undercount)
    verdict: would-use
    why: Named it more valuable than the dashboard's positive content
    because it prevents wasted request cycles and surfaces the dooring
    undercount as a reportable structural story, not just a data limitation.
  - feature: Per-number source/method/build-date/caveat provenance
    verdict: would-use, with an added condition
    why: Necessary but wants build-date recency legible at a glance, since
    she'd verify any absence claim before acting and a stale claim is worse
    than no claim.
  - feature: The static agent API (`/api/v1/`)
    verdict: ignores (for herself directly)
    why: She reads methodology/caveat pages herself rather than
    machine-consuming JSON; the API only matters to her indirectly, through
    whatever assistant she already uses for drafting and tracking.
  - feature: Aldermen sponsorship-count records
    verdict: distrusts
    why: Sponsorship is a performative proxy in her experience; she wants
    recorded votes and treats the rarity of recorded votes (~1.4% per OYL's
    own inventory) as itself a finding, matching OYL's stated caveat almost
    exactly — a strong in-world alignment, not a gap.
  - feature: Maintainer's assistant-run FOIA workflow (gap → draft → send →
    track deadlines)
    verdict: would-use for the mechanical half; distrusts as a complete
    substitute
    why: Matches her own delegation split of "mechanical parts to an
    assistant, judgment kept for herself" but she assessed it as covering
    only the pre-response portion of a real contested request's lifecycle.

data_they_bring: A personal cross-request tracking spreadsheet (agency, date
filed, tracking number, statutory due date, extension flag, follow-up date,
appeal deadline) that she calls "the actual product of my FOIA practice" —
this is exactly the artifact `docs/foia/log.md` already mirrors for OYL's own
requests, suggesting the log's shape is validated against real professional
practice rather than invented. She also brings agency-specific behavioral
pattern recognition (DOF stalls on consultation grounds, CDOT reliably
bounces things it doesn't own, the Clerk is slower but more complete) that
lives nowhere in OYL's current documentation and that she explicitly said an
assistant lacks.

deal_breakers: A number she can independently verify turning out stale or
wrong with no visible build/check date to have warned her — she was explicit
this breaks trust in the whole site, not just that one number. Also implied:
an assistant or workflow presented as handling "the FOIA process" that
silently omits the narrowing/denial/appeal half would get flagged by her as
misrepresenting its own coverage, not just incomplete.

vocabulary: "keeper" of records (which department actually holds them,
distinct from which one is named in the ordinance); "the ask" (what a request
specifically requests); "native format" vs. a "newly created document" or
"summary PDF"; "consultation extension" / "3(e)"; "denial-by-default";
"the dodge" (an agency's move to avoid producing records — narrowing,
wrong-keeper bounce, exemption citation); "production" (the compiled set of
records an agency releases); "form denial"; "the 40 percent" / "the other
60" (mechanical vs. judgment portions of a request's lifecycle).
