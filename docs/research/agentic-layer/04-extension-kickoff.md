# Extension kickoff — study #1b: the agentic layer as the *primary* experience

date: 2026-07-23
status: running
extends: 01-kickoff-prompt.md (study #1, complete — see REPORT-agentic-proposal.md)

## The reframe (maintainer-directed, 2026-07-23)

Study #1 treated the agentic layer defensively: do assistants find OYL, quote
it right, keep caveats, refuse honestly? Answered. The maintainer's actual
thesis is bigger:

> The website meets people where they're at, but we are also building the
> agentic layer so we can meet people's needs better and more effectively —
> making it a super easy and **superior** experience to using a traditional
> website. We want to make sure we can deliver on that by understanding the
> needs and functions.

The maintainer is themself the existence proof: they run the project's FOIA
program *through* an agent (drafts with verified anchors in `docs/outbox/`,
statutory-deadline tracking in `docs/foia/log.md`, acknowledgment booking).
Others might run periodic data checks, produce documents, chain
investigations. Study #1 measured whether the layer survives agents; this
extension asks **what work the layer lets agents do** — and what must be
built so that work succeeds.

Standing assumption, per the maintainer: **AI adoption is assumed.** Do not
re-litigate whether people will use assistants; study what they'll need when
they do. (Study #1's discovery findings stand, but discovery is no longer the
organizing constraint of this extension — the home page's agent section, per
`docs/superpowers/specs/2026-07-16-home-agent-section-reframe-design.md`,
already plans to teach arriving visitors to use their assistant.)

## Functions in scope (all four, maintainer-selected)

| # | Function | Archetype | Example |
|---|---|---|---|
| F-A | Monitoring & automation | advocate, staffer, maintainer | "check my ward weekly, tell me what changed" |
| F-B | Document production | FOIA filer, staffer, resident, advocate | FOIA letters, ward one-pagers, public-comment prep, alder emails |
| F-C | Multi-step investigations | journalist, advocate, researcher | "why is Ward 42 worst — what's driving it?" |
| F-D | Developer integrations | civic developer | agent-written code against the API |

## Method

Three evidence streams, same discipline as study #1 (verbatim transcripts,
graded against pinned live data, no proposal may assume behavior a probe
could have tested but didn't):

1. **Live capability probes (5).** Cold Sonnet agents, no study context,
   given realistic tasks against the live public layer only, tool logs
   captured. One per function, plus a dedicated FOIA probe (F-B splits into
   "brief" and "FOIA" — different failure surfaces). Grading axes per probe:
   **T** task completion, **C** correctness of numbers used, **V**
   caveat/provenance carriage into the artifact, **G** gap signals (what the
   agent had to invent, guess, or work around — each one is a build
   candidate).
2. **Consumer-scenario interviews (3 new).** Personas study #1 lacked, all
   selected for actually *using* data rather than reading it: an advocate
   (public comment + monitoring), a professional accountability/FOIA filer,
   an automation-minded researcher. Same protocol and memo format as before
   (`../user-needs/01-lead-researcher.md`).
3. **One real user: the maintainer.** Workflow reconstructed from repo
   artifacts (`docs/foia/log.md`, `docs/outbox/README.md` + letters, tracker
   #33 conventions), gaps filled by short written answers. The only
   non-simulated participant in the whole study; labeled accordingly.

## Deliverable

`REPORT-agentic-functions.md`: a function → needed-capability → gap matrix;
what to build so each function succeeds (with the probe evidence that
licenses it); what the website can't do that the layer can (the "superior
experience" claim, tested); revised sequencing superseding
REPORT-agentic-proposal.md §Sequencing. Same kill-list discipline.

## Quality gates

Inherited from study #1, plus: every claimed "superior to the website"
function must name the website equivalent and the measured or reconstructed
cost difference; every gap in the matrix must trace to a probe transcript,
an interview quote, or a maintainer artifact — no free-floating wishlist
items.
