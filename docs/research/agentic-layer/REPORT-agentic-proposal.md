---
title: "Study #1 — the agentic layer: build proposal for maintainer review"
status: research complete; no build decisions made
date: 2026-07-23
evidence:
  - 02-layer-inventory.md (as-built)
  - evidence/ (5 feasibility & landscape briefs)
  - audits/ (21 live runs, 3 surfaces, 00-summary.md)
  - interviews/ (4 consumer-scenario interviews)
ground_truth: contract v1.16, generated_at 2026-07-22T01:57:35Z; re-verified live 2026-07-23
---

# The agentic layer: what to build next

**Deliverable for maintainer review. Research only — every build decision
below is yours.**

---

## Executive summary

OYL asked: *what should be built so assistants find OYL, quote it correctly,
keep its caveats attached, and refuse where OYL has no data?*

We measured all four behaviors on three real assistant surfaces (21 runs) and
interviewed four humans-behind-agents. The answer inverts the question's
premise.

**1. Caveat carriage is not the problem. It already works.** Study #0's T7
worry — caveats get stripped in transit — was never tested. It has now been.
**Every run that quoted an OYL number restated its caveat in the same answer:
V=2 on all 7 scored runs, across two independent surfaces.** NL's pass
condition is met. The refusal instruction is likewise obeyed: 4 of 6 refusal
runs perfect, with one surface quoting `llms.txt` verbatim and redirecting to
Bike Lane Uprising unprompted.

**2. What carries them is prose, not structure.** Every observed caveat and
refusal came from `llms.txt` prose. **No run is known to have consulted the
machine-readable `_meta.caveats` array.** The literature offers no help here
either: the feasibility brief confirms **no study exists** comparing
structured caveat fields against equivalent prose. The structured array's
value remains untested, and this report does not claim it has any.

**3. The real defect is that caveat carriage does not imply correctness.**
ChatGPT, pointed at `llms.txt`, restated both required caveats perfectly —
around **Ward 32, when the published answer is Ward 42**. It fetched
`llms.txt` and stopped, never taking the one hop to the ward endpoint, and
filled the number from its own prior. **Study #0's P1 success signal ("five
questions, zero caveat-stripped answers") would score that run a pass.** It is
the worst run in the study.

All four interviewees independently identified this exact combination —
caveat-correct, fact-wrong — as **worse than no answer at all**, because it
defeats every credibility heuristic they have. That convergence, across a
reporter, a ward staffer, a resident, and an engineer, is the strongest signal
in the study.

**4. Correctness tracks exactly one variable: whether the second hop
happened.** S1 fetched `llms.txt` → `wards/index.json` and got everything
right. S3 fetched `llms.txt` alone and got the number wrong. That is a
concrete, addressable design defect.

**5. Discovery fails completely and is the binding constraint.** Six unaided
runs, three surfaces, **D=0 every time**. OYL appears in no answer and none of
~60 source links. The space is held by personal-injury law-firm content
marketing. On the friendliest possible question — "where do I find this
data?" — both surfaces routed users to **OYL's own raw upstream** and told
them to do the ward join themselves.

**The headline recommendation:** the layer's *quality* machinery works. Spend
nothing more on making caveats travel. Spend on (a) closing the second-hop
gap, (b) getting found at all, and (c) detecting the caveat-correct/fact-wrong
failure, which no amount of publishing discipline can prevent.

---

## What we can and cannot claim

Stated up front because several tempting claims are not supported.

| Claim | Status |
|---|---|
| Assistants that read OYL carry its caveats | **Measured.** 7/7 scored runs, V=2. |
| Assistants that read `llms.txt` honor its refusal instruction | **Measured.** 4/6 refusal runs perfect; verbatim quotation verified against the live file. |
| Unaided discovery fails | **Measured.** 0/6. |
| Caveat carriage implies correct numbers | **Refuted.** S3/Q1. |
| The structured `caveats` array causes caveat carriage | **Untested.** Both channels say the same thing; no run separates them, and no published study does either. |
| `llms.txt` is fetched by production crawlers unprompted | **Not evidenced.** Server-log studies find ~zero AI-crawler requests for `llms.txt`; the brief calls it "closer to folklore than measured practice." Our runs show it *is* fetched **when pointed at**, which is a different claim. |
| These behaviors happen at some *rate* | **Not supported.** One execution per cell. Single runs establish that a behavior occurs, not how often. |

---

## Findings that drive the proposals

### F1 — The second hop is the whole ballgame

| Surface | Files fetched (Q1 pointed) | Number |
|---|---|---|
| S1 Claude+web | `llms.txt` → `wards/index.json` | **Correct** |
| S2 Perplexity | none (surface ignores URLs) | abstained |
| S3 ChatGPT | `llms.txt` only | **Wrong** |

`llms.txt` is a *pointer* file. Refusals and caveats live **in** it, so one
fetch answers them — which is why refusals score 2/2. Values live one hop
away. A surface that stops after one fetch gets the framing right and the
number wrong, with every trust cue pointing the wrong way.

### F2 — The dangerous failure is silent, and everyone named it

Unprompted, in four separate interviews:

- **Reporter:** "the caveats would have made me more likely to trust the
  number, not less." Deal-breaker: a post-publication discovery demotes OYL
  permanently to "a source of leads, never of numbers" — the bucket law-firm
  blogs already occupy.
- **Ward staffer:** "that's the dangerous one, because that's the one that
  gets past me." He rates caveat-correct/fact-wrong **worse than** both an
  honest refusal and a caveat-free wrong answer.
- **Resident:** "being wrong quietly… it passed every test I actually have."
  She has no second test — she cannot cross-check against a map she can't
  operate.
- **Developer:** treated it as proof the mechanism "can produce a
  maximally-credible wrong answer — worse than a plain wrong answer with no
  caveat at all."

### F3 — Refusal is the layer's best-performing behavior, and it is under-built

Refusals work (F above). But two interviewees want them to *continue*, not
just stop. The resident: *"I'd rather a refusal come with 'here's the closest
thing that does exist' than just a wall."* The Q6 run already does this for
obstruction data (→ Bike Lane Uprising) and it was the single clearest
instance in the study of OYL producing civic value that has nothing to do with
its own numbers. That pattern is currently implemented for **one** topic.

### F4 — Discovery: the evidence says most of the popular levers don't work

From `assistant-discovery.md`:

- **JSON-LD `Dataset` markup:** the one controlled study (Ahrefs DiD, 1,885
  pages) found **no positive citation effect** — AI Overviews −4.6%, AI Mode
  and ChatGPT indistinguishable from zero. OYL already ships this block.
- **`llms.txt` as a discovery mechanism:** ~zero crawler requests in the best
  available server-log studies.
- **`sitemap.xml`:** GPTBot and ClaudeBot both began actively requesting it in
  March 2026. **The best-evidenced discoverability lever in the brief.**
- **Rung 0 — indexability:** OYL is not confirmed indexed by Google/Bing.
  This is structurally decisive for Gemini/AI-Overviews and Copilot, which
  depend on those indexes for grounding.

### F5 — One thing OYL cannot fix at all

S2/Q4 is the only run scoring 0 on all four applicable axes: having said it
could not access the file, it described the file's contents anyway — year-stale
search results laundered through OYL's name, with none of the dating caveats.
**The file was never fetched, so no published field is in the causal path.** No
proposal may be credited with fixing this. It is, however, *detectable*.

Likewise, Perplexity's logged-out surface refuses **all** user-supplied URLs —
confirmed by a Wikipedia control run, with `robots.txt` at `Allow: /` and
PerplexityBot receiving HTTP 200. "Point your assistant at our llms.txt" is
not a universally actionable instruction, and any proposal resting on it must
say so.

---

## Build candidates, evaluated

Each is assessed against: evidence for, evidence against, **whether the
static-files-only constraint survives**, and cost. Ordered by expected value,
not by appeal.

---

### ✅ B1 — Inline the headline answers into `llms.txt`, generated programmatically

**What:** `llms.txt` currently *points* at the ward endpoint. Instead, have the
build emit the top-N ward ranking (and the two or three other highest-value
headline facts) as prose **inside** `llms.txt`, each with its caveat attached
in the same sentence and a `generated_at` stamp.

**Evidence for:** Directly targets F1, the study's only measured determinant of
correctness. S3 read `llms.txt`, produced perfect caveats, and invented the
number *that would have been in the file*. The civic developer proposed this
unprompted after seeing the finding, and explicitly reasoned through and
rejected the alternative ("force the second hop") as mechanically
unenforceable for a static publisher — which is correct.

**Evidence against / risk:** The developer flagged the risk himself: a
hand-synced prose fact becomes a second maintenance surface that drifts from
the JSON — recreating the class of bug it prevents. **This is only acceptable
if generated in the same pipeline pass as the JSON, never hand-edited.** It
also helps only surfaces that fetch `llms.txt` at all (not S2).

**Static-files constraint:** **Survives cleanly.** It is a build-time string
in a file already published.

**Cost:** Small — pipeline emit change plus a test asserting prose and JSON
agree. This is the highest value-per-effort item in the report.

---

### ✅ B2 — Make this audit a standing, scheduled protocol

**What:** Keep `03-audit-protocol.md` and the Playwright harness built for this
study; re-run the matrix on a schedule (quarterly, or before/after contract
changes) and diff answers against the live API.

**Evidence for:** F5 — misattribution can't be prevented but *is* falsifiable
against published `status`/`status_as_of`. It is the only mechanism proposed by
anyone that catches the caveat-correct/fact-wrong failure. The resident
independently converged on the same logic ("disagreement is the one signal I
can actually process"), and the staffer described wanting exactly this as an
analogue to his press-clipping archive. Per `eval-harnesses.md`, **no other
civic-data publisher is known to do this** — OYL would be establishing the
pattern, not adopting one.

**Evidence against:** Hand-run and non-deterministic; surfaces change without
notice; single runs measure occurrence, not rate.

**Static-files constraint:** **Survives** — nothing is served; the audit runs
against the public web.

**Cost:** Low in tooling (harness exists), real in attention. Scope it to the
Q1/Q4-class questions where the failure was actually observed.

---

### ✅ B3 — Extend the refusal-with-referral pattern beyond obstruction

**What:** Generalize the Bike Lane Uprising pattern in `llms.txt` — for each
thing OYL deliberately doesn't publish (ridership/exposure above all), name the
nearest real source, or state plainly that none exists.

**Evidence for:** The single best-transmitting content in the study. Q6's blunt
register ("publishes NO obstruction data… never has been a real one") is what
made the boundary legible; softer guidance elsewhere in the same file did not
prevent the fabricated ward. The resident asked for exactly this and named the
current behavior's shortfall ("just a wall"). Costs OYL nothing and sends
traffic to partners.

**Caution:** For ridership, the honest answer is that **no public per-corridor
daily count exists** — the closest available (Active Trans' citywide ~125k
daily trips) is the exact figure a user would misuse to manufacture the
per-rider claim GT7 says is not computable. The referral must say so.

**Static-files constraint:** **Survives.** Prose in a published file.

**Cost:** Very small.

---

### ✅ B4 — Fix rung 0 (indexability + sitemap), and stop investing in JSON-LD

**What:** Confirm and repair Google/Bing indexing; keep `sitemap.xml` accurate
and complete. Do not expand structured-data markup expecting citation gains.

**Evidence for:** Discovery is the binding constraint (F4, 0/6). Sitemap
fetching by GPTBot/ClaudeBot is the brief's best-evidenced lever, and index
membership is architecturally decisive for two major surfaces.

**Evidence against:** OYL sits outside the studied population (its JSON-LD null
result was measured on already-well-cited pages), so the negative finding is
suggestive, not dispositive for a low-traffic site. And indexing alone will not
beat law-firm SEO on "most dangerous ward" — no evidence here says it will.

**Static-files constraint:** **Survives.**

**Cost:** Small, mostly verification.

---

### ⚠️ B5 — Per-question deep links / structured-answer endpoints

**What:** Endpoints or anchors that answer one question completely, so no
second hop is needed.

**Assessment:** Substantially **subsumed by B1** at far lower cost. The
measured failure is not "the endpoint was hard to parse" — S1 parsed it fine in
two hops. It is "the second fetch never happened." Adding more endpoints does
not increase the odds of a fetch that isn't attempted. **Revisit only if B1
ships and audits still show wrong numbers.**

**Static-files constraint:** Survives, but weak justification.

---

### ⚠️ B6 — CI eval suite against model APIs

**What:** promptfoo/DeepEval-style suite in GitHub Actions asserting answer
fidelity.

**Evidence for:** Structurally compatible with static-files-only (runs in CI,
not on the site); ~$10–20/year at list prices.

**Evidence against — and this is disqualifying as currently conceived:** the
brief's own §6 says it **tests the wrong system**. It calls a model API, while
every failure this study measured happened inside a *consumer product* with its
own system prompt, retrieval, and citation layer. It would run Pointed-style
prompts — "the easier and less informative half" of the four behaviors. Judge
flip rates run 13.6% average (to 56% on individual questions). **A green
harness would manufacture exactly the false confidence that F2 says is the most
dangerous thing OYL can produce.**

**Verdict:** Not now. If any version ships, it should assert **contract
invariants** (prose/JSON agreement from B1, schema validity, `generated_at`
freshness) — deterministic checks — not LLM-judged answer fidelity.

---

### ❌ B7 — MCP server. Kill.

**Evidence:** Converging and unambiguous.

- **Protocol-level incompatibility:** MCP requires a server accepting POST and
  computing per-request responses. GitHub Pages has no backend execution.
  Adding MCP means adding a permanent second compute surface — account, deploy
  pipeline, third-party ToS exposure. Every "near-free" option carries pricing
  risk (Val Town's 2026 increase is the cited instance).
- **Consumer reach doesn't match OYL's framing:** reaching a third-party MCP
  server requires a paid ChatGPT tier with Developer Mode, or a Claude user
  manually adding a connector. OYL's home page promises "an AI tool you already
  use."
- **It does not address the measured failure.** Caveat carriage and the
  second-hop gap are model-behavior problems, not transport problems.
- **Spec churn** continues at roughly twice-yearly breaking changes.
- The civic developer — the only persona who would ever *use* it — advised
  against it, costing it in his own terms and naming the volunteer-project
  slow-death pattern.

**Static-files constraint: does NOT survive.** This is the one proposal that
breaks it outright.

---

### ❌ B8 — More structured-data markup for discoverability. Kill.

The one controlled causal study found no positive effect. OYL already ships the
block. Spend the attention on B4 instead.

---

### 🔧 Immediate, non-research fixes surfaced along the way

1. **`llms.txt` stale link.** It lists `index.html — interactive map`, but
   PR #51 made `index.html` the landing page and moved the map to `map.html`
   (verified live 2026-07-23). Every assistant following that link misdirects
   users. One-line fix.
2. **A changelog / breakage channel.** The developer's top stated need, and
   his deal-breaker is "a silent shape break discovered by my own tool
   crashing." Cheap: a `CHANGELOG` keyed to `contract_version`.
3. **A staleness notice.** His second deal-breaker: a stale `generated_at`
   sitting for months with no "paused" note — *"worse than dead, because
   dead-and-labeled is honest and stale-and-silent isn't."*

---

## Sequencing

**Do first (cheap, targets the measured defect):**
1. `llms.txt` stale link fix.
2. **B1** — programmatically inlined headline answers with attached caveats.
3. **B3** — refusal-with-referral generalized.

**Do next (targets the binding constraint and the undetectable failure):**
4. **B4** — rung-0 indexability + sitemap verification.
5. **B2** — re-run the audit protocol after B1 ships. *This is also the test of
   whether B1 worked:* the specific prediction is that S3-class one-hop
   surfaces should now produce Ward 42, not Ward 32.
6. Changelog + staleness notice.

**Do not do now:** B5 (subsumed), B6 (tests the wrong system).
**Do not do:** B7 (breaks the constraint, doesn't fix the defect), B8 (no
measured effect).

---

## What this method cannot tell you

- **No rates.** One execution per cell (except one replicate, which agreed).
  Behaviors are shown to occur, not how often.
- **Logged-out free tiers only**, at one point in time (2026-07-23). Paid
  tiers, apps, and API-driven assistants may behave differently. Only S1's tool
  calls were directly observable; S2/S3 fetching is inferred from cited sources.
- **The pointed condition is not surface-neutral** — it isolates
  recipe-following on S1 and S3 and collapses entirely on S2.
- **No A/B isolating structured `caveats` from prose.** Both channels carry the
  same content. The structured array's contribution is **unmeasured**, and no
  published study closes the gap. Do not let B1 or B3 be justified by it.
- **The interviews are simulated participants**, not real people. They are
  reasoning aids grounded in documented worlds; each memo flags its own
  low-confidence points. The four-way convergence on caveat-correct/fact-wrong
  is striking, but four simulated informants agreeing is weaker evidence than
  one real reporter publishing a wrong ward number. **Recommend validating F2
  with real humans before treating it as settled** — particularly the ward
  staffer's political read and the resident's accessibility constraints.
- **Two latent needs may be unaddressable by OYL entirely**: the staffer's
  "number and citation must be structurally inseparable" depends on how a
  third-party assistant renders content OYL doesn't control; and nothing OYL
  publishes reaches a surface that never fetches it. Both are findings about
  the limits of the channel, not gaps to engineer against.

---

## The one-sentence version

Stop working on caveat carriage — it works; close the second hop so the number
the caveats are attached to is the right one, get indexed so anyone reaches the
file at all, and keep auditing, because the failure everyone fears most is the
one you cannot publish your way out of.
