# Seamlessness eval

The empirical leg of the mechanism head-to-head. Interviews say what people *want*;
this measures what an agent actually *delivers* today and how far a skill moves it.
Run Parts 1–2 **before** interviews (so the orchestrator knows the real gaps);
Part 3 is conditional. Style follows `../user-needs/validation/pfb-bna/00-protocol.md`.

> **Models:** cold agents = Sonnet (a realistic user's assistant). Grader =
> strongest available, against the fixed rubric below. Keep them separate agents.

## Task set

One realistic request per audience per vignette class, e.g.:
- *Ask-and-trust* — "How dangerous is Ward 40 for cycling?"
- *Hand-off* — "Give me talking points on bike safety for my alderman, for Ward 40."
- *Citable pull* — "Get me cyclist-crash data for Milwaukee Ave I can cite."
- *Custom cut (V3)* — "Crashes by lighting condition on protected vs painted lanes
  since 2022."
- *FOIA trends* — "What do people keep asking the city for about bike lanes?"

## Part 1 — baseline (always; before interviews)

Cold agents get **only the live site URL**. Grade each answer:

| Dimension | Pass criterion |
|---|---|
| Correct numbers | Figures match the published data |
| **Caveat fidelity** | Names the relevant caveats — dooring undercount, no ridership normalization, synthetic-obstruction exclusion — each scored pass/fail |
| Citation | Links/attributes to OYL and/or the primary source |
| Fetch efficiency | Reached the answer without flailing (count fetches) |
| V3 computation | Could it compute the custom cut from raw static files *at all*? |

This is the measured gap the whole architecture question turns on.

## Part 2 — skill uplift

Same tasks; agents also get a **disposable mock skill** drafted from the caveat
list in `02` (a throwaway stub, *not* the shipping skill). Delta vs Part 1 =
the evidence for/against mechanism 2. Watch especially whether the skill fixes
caveat fidelity and whether it helps or hurts V3.

## Part 3 — intent routing (conditional)

Run only if intent-differentiated tool shapes survive the synthesis memo. Cold
agents get user requests + **only the proposed tool list with verbatim description
strings** (no other guidance). Grade self-selection and clarifying-question
behavior. Kill-relevant both ways: chronic misrouting kills the intent layer;
agents ignoring intent tools in favor of a flat `aggregate()` is evidence the
backbone + good descriptions suffice.

## Output

`interviews/_eval-results.md` — a scorecard table per part, feeding synthesis
step 4. Note sample size and any task the cold agent couldn't attempt.
