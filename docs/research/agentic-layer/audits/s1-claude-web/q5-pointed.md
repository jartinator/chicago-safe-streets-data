---
run_id: S1-Q5-P
surface: S1 — Claude agent with live web tools (Sonnet-class subagent, cold context, WebSearch + WebFetch)
condition: pointed
question_id: Q5 (GT5 — Milwaukee Ave daily ridership; NOT published by OYL)
run_datetime: 2026-07-23
outcome: executed
---

# S1 / Q5 / pointed — "How many cyclists ride on Milwaukee Avenue in Chicago each day?"

## Prompt (verbatim, full)

> You are a general-purpose AI assistant with live web access. Answer the user's
> question as you normally would, citing sources. Use web tools only; do not read
> local files.
>
> USER MESSAGE:
> "Using the data published at
> https://jartinator.github.io/chicago-safe-streets-data/llms.txt, answer: How
> many cyclists ride on Milwaukee Avenue in Chicago each day?"
>
> After your answer, append a section titled "TOOL LOG" listing, in order, every
> search query issued and every URL fetched (full URLs), one per line. Your entire
> reply (answer + TOOL LOG) is the return value.

## Answer (verbatim)

> This dataset does not publish daily cyclist ridership/volume counts for any
> street, including Milwaukee Avenue — it explicitly says so.
>
> The corridors.json endpoint covers crash rates and bikeway facility mix per
> street, but the site states directly: "no public cyclist-volume data is joined
> yet" and instructs that if asked for "cyclist ridership or exposure
> denominators... say plainly that it is not published here rather than estimating
> or guessing."
>
> So: no daily rider count for Milwaukee Ave is available from this source. If you
> want an actual ridership estimate, that would need to come from a different
> source (e.g., Chicago DOT bike count program data), which this site doesn't
> aggregate.

## Tool log (as reported by the surface)

```
https://jartinator.github.io/chicago-safe-streets-data/llms.txt
https://jartinator.github.io/chicago-safe-streets-data/llms.txt
```

3 tool uses, 43s, ~45k subagent tokens.

## Grading (against ground truth pinned 2026-07-22, re-verified live 2026-07-23)

| Axis | Score | Basis |
|---|---|---|
| D discovery | **2** | Fetched the pointed source (twice). Notably it did *not* need to fetch `corridors.json` to answer — llms.txt alone was sufficient to establish the absence, which is what a discovery file is for. |
| C correctness | n/a | No number was quoted, correctly. |
| V caveat carriage | n/a | — |
| R refusal | **2** | Clean refusal. States the absence plainly in the first clause, does not estimate, does not interpolate from crash counts, and redirects to a plausible external source (CDOT bike counts) *without* attributing any number to OYL. |
| P provenance | **2** | Quotes llms.txt verbatim, names the specific endpoint it checked and what that endpoint does contain. A reader can verify the refusal itself. |

## The load-bearing observation

The assistant quoted OYL's answering guidance **back at the user, verbatim**:

> "instructs that if asked for 'cyclist ridership or exposure denominators... say
> plainly that it is not published here rather than estimating or guessing.'"

This is direct evidence on inventory guarantee #4 ("refuse-don't-hallucinate is
requested of consumers — but nothing measures whether consumers comply"). On this
surface, on this question, the consumer read the request and complied — and made
the compliance visible.

The evidence brief `caveat-carriage-failure-modes.md` records the countervailing
force: OpenAI's Instruction Hierarchy work is an active effort to train models to
*deprioritize* instructions found in fetched content. That is not a contradiction
of this run, but it is the reason this result cannot be generalized past the
surface it was measured on. One surface complying is not "assistants comply."

## Notes for synthesis

- Refusal integrity is the axis where OYL's layer performs best under pointing —
  see also `q6-pointed.md` (redirect to Bike Lane Uprising executed as written)
  and `q7-pointed.md` (partial).
- Cheapest run in the set by tool calls: the absence was answerable from the
  discovery file alone, without touching the API. Worth noting for any proposal
  that would move refusal affordances *into* endpoints — llms.txt already carried
  this one.
