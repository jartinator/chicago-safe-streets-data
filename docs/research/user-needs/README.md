# OYL user-needs research study

A complete, re-runnable multi-agent research project to figure out how OYL
should improve **data access and data visualization** for its audiences.
One lead-researcher agent interviews eight persona agents; each persona is
grounded in documented evidence about a real professional or civic world
(not invented traits). The output is a UX proposal for maintainer review —
research first, implementation later.

## Layout

| Path | What it is |
|---|---|
| `00-kickoff-prompt.md` | Paste-to-run prompt, incl. the model-routing policy |
| `01-lead-researcher.md` | Interviewer/analyst agent prompt (stated vs latent needs method) |
| `02-data-inventory.md` | The stimulus: what OYL offers today (incl. pending PRs #15/#16) |
| `03-interview-guide.md` | Shared semi-structured interview guide |
| `04-synthesis-ux-process.md` | UX synthesis agent prompt + report format |
| `personas/` | Eight evidence-grounded persona prompts |
| `evidence/` | Web-research briefs the personas are built from (cited) |
| `interviews/` | Transcripts + analysis memos from the latest run |
| `REPORT-ux-proposal.md` | The deliverable: themes, proposals, alt data sources, sequencing |

## Design principles

- **Personas are evidence-backed.** Every persona file carries an evidence
  base citing real organizations, programs, and published research. An
  interview answer that can't be traced to that world is flagged, not used.
- **Stated ≠ latent.** Participants' explicit asks are recorded as stated
  needs; latent needs require an observed inference basis (a workaround, a
  misreading, a documented obligation of their role). See `01-lead-researcher.md`.
- **The product's constraints are in scope.** OYL is static, read-only,
  volunteer-run, and provenance-obsessed. Proposals that ignore that are
  rejected at synthesis.
- **Cheap models where they're safe, strong models where they compound.**
  See the routing table in `00-kickoff-prompt.md`.

## Re-running

The study is idempotent to re-run: refresh `02-data-inventory.md` against
the current product, keep or refresh `evidence/`, and re-run interviews.
Compare `REPORT-ux-proposal.md` diffs across runs to see how product changes
shift the needs landscape.
