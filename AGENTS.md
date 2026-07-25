# AGENTS.md

Guidance for an AI agent making changes **inside this repository**.

If you are instead **building a product against the published data** and will
never clone this repo, you want the integration contract, not this file:
<https://jartinator.github.io/chicago-safe-streets-data/api/v1/index.json>.

Working in Claude Code? `CLAUDE.md` carries the session conventions that are
not in this file — concurrent-session handling via Marge, and the human-task
tracker and outbox conventions. This file is about the code.

---

## What this is

**On Your Left!** — Chicago bike-safety data, rebuilt weekly from the Chicago
Data Portal and other public sources, published as a static site plus a
versioned JSON API. A volunteer project. There is no server and no runtime:
GitHub Pages serves committed files.

```
pipeline/       Python. Pulls, joins, aggregates, emits. No web framework.
  config.py     Every dataset id, path, filter, threshold, mapping. Start here.
  pull_*.py     One dataset each. Deterministic fetching only.
  aggregate.py  Owns every published schema. Writes site/data/.
  emit_api.py   Writes the agent-facing API: site/api/v1/, llms.txt, sitemap.
  caveats.py    The caveat co-location contract: vocabulary and generators.
  check_*.py    CI guardrails. They are allowed to fail your PR.
site/           Static. Vanilla JS, vendored Leaflet, no build step.
  data/         The published human data contract. Committed output.
  api/v1/       The published agent API. Committed output. Has JSON Schemas.
tests/ui/       Plain node test files. No package.json, no runner.
SCHEMA.md       Source of truth for site/data/ contracts.
DECISIONS.md    Why things are the way they are. Newest last. Read before arguing.
CONTRIBUTING.md How to swap a data source or fork for another city.
```

---

## Commands

```bash
# Install
pip install -r pipeline/requirements.txt

# Tests — run both before proposing any change
python -m pytest pipeline/tests -q
for f in tests/ui/*.test.js; do node "$f"; done

# Guardrails — run both before proposing a pipeline or API change
python pipeline/check_provenance.py
python pipeline/check_api.py

# The caveat backlog: every number no selector covers yet. Never exits non-zero.
python pipeline/check_api.py --audit-colocation

# Regenerate the agent API from the committed site/data/ (no network)
cd pipeline && python emit_api.py

# Serve the site
cd site && python -m http.server 8000

# Full pipeline (slow, live network) — see "Ask first" below
cd pipeline && python run_all.py
cd pipeline && python run_all.py --fixtures   # offline, synthetic
```

There is no `package.json`. UI tests are plain files run under bare `node`.

---

## Never

- **Never generate or guess an alderman name.** `site/data/aldermen.json` is
  filled from the city's own Ward Offices dataset or left `null`. Sponsor
  resolution is exact-match only — never fuzzy name similarity. A wrong
  auto-filled name is worse than no name. (DECISIONS.md #8)
- **Never add an LLM call to a `pull_*.py` module.** Pull modules are
  deterministic fetching. `classify_safety_topic.py` is the one documented
  exception and it runs *after* the pulls, tagging records that were already
  deterministically fetched. It labels; it never originates a matter, sponsor,
  vote, or date. (DECISIONS.md #15, CONTRIBUTING.md)
- **Never fabricate geometry to close a gap.** A corridor gap stays a hole in
  the line. The completion bar carries the message instead. (DECISIONS.md #19)
- **Never let synthetic or mock data reach `site/api/v1/`.** The obstruction
  layer is mock and is excluded from that namespace by rule. `index.json`'s
  `no_synthetic_data` field and `llms.txt` say so explicitly rather than
  silently omitting it. Both come from `NO_SYNTHETIC_DATA_STATEMENT` in
  `emit_api.py` — keep it one constant, never two wordings.
- **Never commit a fixtures build to main.** `meta.json.provenance` must be
  `"socrata"`. `check_provenance.py` and the data-guard workflow will catch it.
- **Never change `emit_api.py`'s output shape without updating the matching
  schema under `site/api/v1/schemas/` in the same PR.** `check_api.py` will
  fail you, but knowing where the source of truth lives is on you.
- **Never invent a zero for missing data.** Absence is a data gap, not "none."
  Use the honest-gap shape: `{"available": false, "data_tier": ..., "note": ...}`.
- **Never open the in-app Browser pane in this repo** — not `preview_start`,
  not any `mcp__Claude_Browser__*` tool. It crashes the desktop app's GPU
  process within about 5 seconds and takes the whole app down. Reproduced three
  times on 2026-07-23. Use Playwright against a local `http.server` instead.

## Ask first

- **Regenerating `site/data/`.** It is committed output; a local run dirties
  the tree. The weekly reviewed-PR refresh is the normal path.
- **Adding a data source, a dependency, or a new published field.**
- **Anything that bumps `CONTRACT_VERSION`** in `pipeline/config.py`. A
  contract bump means `SCHEMA.md` changes in the same PR.
- **Anything that removes or retypes a published field.** The API is
  additive-only within `api_version` 1.

## Always

- **Always run `pytest pipeline/tests` and `check_api.py`** before proposing a
  change to `pipeline/` or `site/api/`.
- **Always keep analysis in `aggregate.py`** and pull modules deterministic.
- **Always give a new layer or metric a `data_tier` and a visible badge.** Tier
  labelling goes through `BSD.badgeHTML()` / `BSD.noticeHTML()` in
  `site/assets/js/common.js` so "data quality is always visible" stays uniform.
  No exceptions — it is the product's credibility.
- **Always append to `DECISIONS.md`** rather than editing an existing entry.
  Newest last. Amendments are dated sub-bullets under the entry they amend.
- **Always check for a concurrent session before editing.** This repo is often
  open in several chats at once. If you see a concurrent-session warning, move
  to a worktree under `.claude/worktrees/` or confirm it is safe. The guard
  warns; it does not block. Acting on it is on you.
- **Always put the caveat next to the number.** Any new number published under
  `site/api/v1/` carries the qualifier that makes it honest **in its own JSON
  object** — not in `llms.txt`, not in `index.json`, not on a page. Generate it
  with `pipeline/caveats.py` rather than hand-writing it. If you hand-write the
  text, read the restatement landmine below first.
- **Always add the selector when you migrate a claim.** Enforcement is scoped
  per JSON path in `COLOCATION_ENFORCED_CLAIMS` (`pipeline/check_colocation.py`),
  so a claim nobody listed is a claim nobody checks. The emitter and the
  enforcement list are two halves of one change and belong in one PR.

---

## Landmines worth knowing before you touch them

**Never write a bare number into caveat prose.** A value a caveat restates goes
in parentheses, beginning with the value — `(65 crashes)` — or it is not written
at all. That is the only form CC-8 checks, and CC-8 is the only rule in the whole
caveat contract about whether a caveat is *true* rather than where it sits. It
compares each parenthesised value against the numbers in the object the caveat is
attached to and fails the build when they disagree.

It cannot see a number in running prose. `"Compares 117 crashes with 122
crashes"` is unchecked, and nothing distinguishes it from `"Compares 116 crashes
with 123 crashes"` — which is a false caveat that actually shipped once, four
characters away from the sibling keys it contradicted.

- Exempt: a parenthetical that is **entirely** a date expression — `(2021)`,
  `(May 2026)`, `(2026-07-11 to 2026-07-13)`.
- Not exempt: `(2032 crashes)`. It begins with a year and is still a number.
- Ask first before adding a value to a caveat in a `caveats` map (Form C).
  Those entries are shared across records, so a restatement true of one record
  is false for every other one, and the check fails on the first mismatch.

This bites when you **hand-edit** caveat text. The generators in
`pipeline/caveats.py` emit the canonical form and cannot get it wrong; a person
typing a sentence can. It is the reason the co-location work deliberately
migrated generated caveats first and left the hand-written ones for later.

**A caveat is not a `note`.** The repo uses both and the split is clean:
`note` describes what the data *is*; `caveat` states how the number can be
wrong or be misread. Existing `note` and `score_note` fields stay as they are —
the contract never reads them, so do not cite them as evidence about it.

**`crash_id` is a lossy prefix, by design.** `crashes/ward-NN.json` emits the
leading 16 hex characters of the source 128-character `CRASH_RECORD_ID`, or the
full id when two records in the same build share that prefix. The emitted value
is therefore *always a prefix of the record's full id, in every build*. Never
compare emitted ids for equality across builds; compare by prefix. Full ids and
the three dropped columns (`crash_type`, `lighting`, `segment_id`) live in
`site/data/crashes_cyclist.geojson`, linked from each slice as `full_data_url`.

**`site/data/` and `site/api/v1/` are both committed build output**, and they
are separate contracts. `emit_api.py` reads the first and writes the second and
never recomputes anything. **Nothing you ship to the agent API reaches the human
pages automatically**, and nothing you change on the human side reaches the API.

**`_meta.generated_at` and `provenance` are copied verbatim** from
`site/data/meta.json`. Never write a fresh timestamp — deterministic rebuilds
and honest provenance depend on it.

**Third-party pulls are non-fatal on purpose.** `pull_mellow.py`,
`pull_council_records.py`, `pull_hearings.py` and `pull_menu_spending.py` warn
and degrade to a stub or an honest gap rather than failing the run. Do not
"fix" one into a hard failure.

**`infra_growth_trend` is `null` until the pipeline has run twice.** It needs
two dated snapshots. That is not a bug.

**Size budgets are enforced at build time**, not just in CI:
`API_SIZE_BUDGET_BYTES` is 100,000 and `API_CRASH_SLICE_BUDGET_BYTES` is
150,000. `wards/index.json` is the tight one at **58,733 bytes** — check the
headroom before adding a per-ward field, and expect a per-record caveat there
to need the shared-map form rather than an inline block.

**A CI check that cries wolf gets switched off.** `check_colocation.py`
deliberately stays quiet on four legitimate conditions: a claim absent from some
files but not all, an `{"available": false}` subtree, a glob matching no file,
and any path nobody has migrated. Each prints a `NOTE:` instead of failing. If
you tighten one of these into a hard failure, you will block the Monday
auto-refresh PR, and a guardrail that blocks routine work does not survive.

---

## Where the truth lives

| Question | File |
|---|---|
| What does this field mean? | `SCHEMA.md` (site/data), `site/api/v1/schemas/` (API) |
| Why is it like this? | `DECISIONS.md` |
| Where is that knob? | `pipeline/config.py` |
| How do I swap a source or fork the project? | `CONTRIBUTING.md` |
| How do I verify a change? | `.claude/skills/verify/SKILL.md` |
| What is an agent supposed to do with a number? | `pipeline/caveats.py`, `site/llms.txt` |
| What is still unqualified? | `python pipeline/check_api.py --audit-colocation` |

When this file and `DECISIONS.md` disagree, `DECISIONS.md` wins and this file
is out of date. Say so rather than following it.
