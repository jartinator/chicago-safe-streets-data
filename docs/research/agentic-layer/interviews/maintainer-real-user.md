---
participant: maintainer (Jared Meyer) — the study's only REAL user
scenario: >
  Runs the project's open-records (FOIA) program through an AI agent, and is
  the origin of the extension's thesis: the agentic layer as the primary,
  superior experience. Workflow reconstructed from repo artifacts
  2026-07-23; gaps filled by the maintainer's own written answers (marked).
interview_date: 2026-07-23
model_note: >
  NOT simulated. Reconstruction from docs/foia/log.md, docs/outbox/ (7
  artifacts + README lifecycle), tracker #33 conventions in CLAUDE.md, and
  the maintainer's direct answers. The one participant whose behavior is
  evidence rather than simulation.
status: reconstruction complete; awaiting maintainer answers to §4
---

# The maintainer as real user — the FOIA program run through an agent

## 1. The workflow, reconstructed from artifacts

The clearest evidence is request #4 (Smart Streets enforcement data), a
complete lifecycle executed in under 48 hours:

| Step | Actor | Evidence |
|---|---|---|
| A Tribune report (2026-07-19) reveals a compiled dataset exists (delivery-company fines under the Smart Streets camera pilot) | world | log.md row 4 |
| Gap identified: this would be OYL's "first real-tier obstruction-adjacent layer, with company-level attribution" | agent + maintainer | log.md "What each request seeks" |
| Request drafted: violation-level records precisely described (date/time, location, type, warning vs. citation, fine, commercial registrant name, ward), PLUS the already-compiled Tribune production and its data dictionary — a records description an agency cannot easily dodge | agent | outbox file 2026-07-21 |
| Filed under `docs/outbox/` with lifecycle front matter (status/to/subject/sent/tracking/tracker) | agent | outbox README conventions |
| **Sent by the human** (agent never sends) | maintainer | repo rule; front matter `sent: 2026-07-21` |
| Acknowledgments booked same day: DOF ref F146238-072126; the CDOT cc spawned its own ref S146292-072126, closed "not keeper → referred to DOF" — a routing outcome logged, not lost | agent | log.md row 4 |
| Statutory machinery computed: +5 extension under 5 ILCS 140/3(e) recognized, reply-due recalculated to **2026-08-04**, follow-up nudge scheduled **2026-08-06** | agent | log.md row 4 |
| Outcome log lives in the outbox file; the file is the permanent record | convention | outbox README lifecycle |

Around it, a standing program: three more requests staged (`ready` with
"anchors verified"), a fallback/corroboration pair (CDOT primary, City Clerk
backstop "if CDOT claims it does not retain old tracker versions"), an
integration plan for the data's return, and the explicit doctrine that **a
"no records" response is itself a documented result** feeding DECISIONS.md.

## 2. What this proves about the agentic layer (function evidence, not persona speculation)

- **F-B (document production) at professional grade is real.** The Smart
  Streets request pins records to a specific known production (the Tribune
  delivery), names the fee-waiver basis, anticipates the keeper question by
  cc'ing CDOT, and captures the referral outcome. This matches the craft
  standards a professional requester would recognize — drafted by an agent
  from a news signal in ~2 days.
- **F-A (monitoring) is being done by hand-convention.** Deadline tracking,
  extension arithmetic, nudge scheduling — the agent computes these, but
  nothing *watches*; the maintainer must open a session for the state to
  advance. The program's own follow-up rule ("+7 business days if no
  acknowledgment") is a cron job written in prose.
- **The loop closes into the data layer.** "On receipt" instructions route
  returned records into `data/foia/` → pipeline functions → published
  endpoints. FOIA is not adjacent to the data product; it is the data
  product's acquisition arm.
- **None of this is reachable from the public layer.** Everything above
  lives in repo docs. A member of the public with an assistant and the
  published site cannot replicate any of it — the methodology page documents
  method, not actionable gaps; probe P-FOIA (this study) tests how far an
  outside agent gets on public files alone.

## 3. The human/agent boundary as practiced

Agent: identify, draft, verify anchors, file, track, compute deadlines, book
outcomes. Human: **send**, and decide. The boundary is a hard convention
(outbox exists because sending is manual), matching the study-#1 personas'
unanimous "nothing goes out under my name unreviewed."

## 4. Maintainer answers (verbatim)

> _Pending — questions posed 2026-07-23:_
>
> **Q1.** _(public replicability)_ Should an outside person — an advocate
> with an assistant — be able to run your FOIA workflow from the public site
> alone? Is "OYL as FOIA seed-bank" (published gap list + records language +
> agency routing) something the layer SHOULD publish, or is this workflow
> intentionally internal?
>
> **Q2.** _(pain)_ What's the most manual/painful part of the loop today —
> Gmail reconciliation, deadline watching between sessions, something else?
>
> **Q3.** _(monitoring)_ You picked monitoring as a studied function. What
> do YOU want watched, and what should an alert contain to be worth an
> interruption?
>
> **Q4.** _(the superior-experience claim)_ What's one thing you've tried
> to do through the agent+layer that FAILED or disappointed — the honest
> counterexample to the thesis?
>
> **Q5.** _(automation users)_ When you picture "someone runs an automation
> to check data periodically," who is that concretely, and does serving them
> stay inside no-accounts/no-server?
