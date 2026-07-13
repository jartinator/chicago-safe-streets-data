# Kickoff prompt

Paste this to a Claude Code session at the repo root to run (or re-run) the
full study. It is self-contained; everything it references is checked in
under `docs/research/user-needs/`.

---

Run the OYL user-needs research study defined in `docs/research/user-needs/`.
Work on a dedicated branch so nothing collides with other sessions.

**Model usage policy — follow this, it is deliberate.** The most capable
model (Fable/Opus class) is scarce and slow; spend it only where inference
quality compounds. Route as follows:

| Stage | Model class | Why |
|---|---|---|
| Orchestration (you, the main loop) | strongest available | Judgment calls, quality control, final synthesis all live here. |
| Evidence web research (6 domain agents) | Sonnet | Search-and-summarize with citation discipline; Sonnet is reliable and ~5× cheaper. Parallelize. |
| Persona interviews (8 agents) | Sonnet | In-character reasoning grounded in a written evidence base. Sonnet holds character well; the evidence base does the heavy lifting. |
| Per-interview needs-extraction memos | Sonnet, escalate to strongest if an interview is rich/contradictory | Structured extraction against the memo template in `01-lead-researcher.md`. |
| Cross-interview synthesis + UX proposal | strongest available, ONE agent or the main loop itself | The deliverable. Never parallelize, never downgrade. |
| Mechanical formatting, file assembly, link checks | Haiku | No inference content. |

Do NOT run persona interviews on Haiku-class models (characters flatten into
agreeable feature wish-lists — exactly the failure this study is designed to
avoid), and do not burn strongest-model tokens on web search.

**Steps:**

1. Read `README.md` (repo root), `SCHEMA.md`, and any open PRs; refresh
   `docs/research/user-needs/02-data-inventory.md` if the product changed.
2. If `evidence/` is stale or empty, run the six evidence agents (domains
   and instructions embedded in the persona prompts' evidence bases and in
   `evidence/README` notes). Every claim must name a real org/source.
3. For each persona in `personas/`, run an interview: the persona agent gets
   its persona file + `02-data-inventory.md`; the interviewer follows
   `03-interview-guide.md` and the rules in `01-lead-researcher.md`. Write
   transcript + analysis memo to `interviews/<persona-id>.md`.
4. Write the cross-interview synthesis memo (`interviews/_synthesis-memo.md`).
5. Run the UX synthesis per `04-synthesis-ux-process.md` →
   `REPORT-ux-proposal.md`. Include the alternative-data-sources section —
   both sources participants raised and sources you independently judge
   likely to exist.
6. Commit everything and push. Present the executive summary and stop —
   implementation decisions belong to the maintainer after review.

**Quality gates:** every latent need has an inference basis; every proposal
traces to named participants; the mock-obstructions layer and the
no-ridership-normalization caveat must be explicitly probed in every expert
interview (they are the two biggest trust hazards); the report must contain
a kill list and a method-limits section.
