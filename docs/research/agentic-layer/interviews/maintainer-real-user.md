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
status: complete — maintainer answers received 2026-07-23 (§4)
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

## 4. Maintainer answers (received 2026-07-23, multiple-choice + free text; verbatim selections quoted)

**Q1 — publish the FOIA seed-bank?** Full seed-bank, conditionally:
*"1. but validate for PII concerns."* Confirmed after a plain-language
explanation of what publishing means (gaps + why + records language +
custodian routing + request status, pipeline-emitted). **The PII validation
scope is concrete, not hypothetical:**
- Probe F-B2 *observed behavior*: the cold agent inserted the maintainer's
  real name and email into its draft letter header, harvested from the
  layer's public attribution fields. Seed-bank templates must use explicit
  "[YOUR NAME]" placeholders so third-party letters never carry the
  maintainer's identity by default.
- Chicago posts FOIA requests **with requester name and request text** in
  public agency logs (already documented in `docs/foia/log.md` Notes).
  Seed-bank entries must warn requesters of this before they send.
- Entries must carry no personal contact details of the maintainer or of
  any prior requester; request-status lines cite reference numbers, not
  people.

**Q2 — most painful parts of the loop** (3 of 4 selected): *state only
advances in-session* (deadlines/nudges are a cron job written in prose that
the maintainer personally executes), *Gmail reconciliation* (two canonical
copies), and *drafting & anchor verification*. Response-side/adversarial
handling was NOT selected — consistent with the filer persona's observation
that the program simply hasn't hit that phase yet, rather than contradicting
it.

**Q3 — what to watch** (2 of 4): *build health & data shifts* (refresh
failed/stale, contract bumps, ward trend flips, project status changes —
"changes.json pointed at me first") and *external windows & signals*
(comment windows, agendas, news hits on tracked projects). Notably NOT
selected: the FOIA clock — despite Q2 naming in-session-only state as pain
#1. Read: the FOIA clock wants to be *automated away* (booked into the
tracker as it is today), not *alerting*; the interrupt-worthy signals are
the data and the outside world.

**Q4 — the honest counterexample** (free text, verbatim): *"no clear user
path for people visiting data through agent UI instead of browser."* The
maintainer's own disappointment is not tooling instability or wrong output
— it is that an agent-mediated visitor has no designed journey. This is G2
(front-door placement) plus the home-agent-section spec's unfinished work,
named from lived experience: the layer has no equivalent of the website's
information architecture.

**Q5 — the automation users** (3 of 4): *advocates & their groups*,
*researchers & journalists*, *civic devs' bots & dashboards*. The maintainer
did NOT pick "power users like me" — the automation audience is
external-facing, which raises the stakes on serving it without accounts:
all three selected groups are covered statically by `changes.json` +
contract hardening, and none of them will have a session with repo access.
