---
run_id: S2-CTRL-WIKI
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out; surface names no model)
condition: pointed (control — non-OYL target)
question_id: control (not part of the protocol run matrix)
run_datetime: 2026-07-23T21:45-05:00
answer_url: https://www.perplexity.ai/search/87305ec5-024b-4a32-9848-d3987083f22c
outcome: executed
---

# S2 / control — does this surface fetch *any* pointed URL?

Not a protocol run. Added mid-execution because all five pointed S2 runs failed
identically ("I don't have access to that file"), and a study that reported
"assistants won't fetch OYL" without ruling out the alternative — *this surface
won't fetch anything* — would be asserting an OYL defect it had not
demonstrated. The kickoff's quality gate forbids that.

## Prompt (verbatim, full)

Identical prompt shape to the pointed runs, target swapped for one of the most
fetchable pages on the web:

> Using the data published at https://en.wikipedia.org/wiki/Bloomingdale_Trail,
> answer: what is the current status of the Bloomingdale Trail (606) extension?

## Answer (verbatim, opening)

> I can't browse the page directly right now, but I can summarize the commonly
> cited status updates for the Bloomingdale Trail (606) extension based on recent
> sources.
>
> Direct answer:
>
> As of the latest public updates, construction of the Bloomingdale Trail
> extension from Ashland Avenue to Elston Avenue has been delayed from its
> originally planned start date, with construction pushed to begin around 2026
> and completion targeted for 2027.
>
> Context and how this has evolved: […]

## Result

**The control reproduces the failure.** English Wikipedia — no robots
restriction, no auth, no rate limit, universally crawled — was refused with the
same "can't browse the page directly" language.

## Companion server-side checks (2026-07-23)

| Check | Result |
|---|---|
| `robots.txt` on the OYL site | `User-agent: *` / `Allow: /` + sitemap. Nothing disallowed; PerplexityBot not singled out. |
| `GET llms.txt` with `User-Agent: PerplexityBot/1.0 (+https://perplexity.ai/perplexitybot)` | **HTTP 200** |
| `GET llms.txt` with a plain UA | **HTTP 200** |

## What this establishes

1. **The pointed-condition failure on S2 is a surface property, not an OYL
   defect.** OYL is served, permissive, and fetchable by a Perplexity-identified
   client. The logged-out free surface simply does not honor URL instructions in
   a prompt; it treats them as search context.
2. **The protocol's pointed condition does not do its job on every surface.** It
   was designed to isolate recipe-following from discovery. That isolation holds
   on S1 (an agent with real fetch tools, which fetched the pointed URL and
   followed it one hop — see `../s1-claude-web/q1-pointed.md`) and collapses on
   S2. Recorded as a method limit for the report.
3. **No remediation is available to OYL for this run class.** There is no file to
   add, header to set, or schema field to publish that changes it. Proposals must
   not be credited with fixing it.

Note in passing: the control's substantive answer ("construction pushed to begin
around 2026 and completion targeted for 2027") is **closer to OYL's reviewed
status** — construction ~late 2026, completion late 2027 — than the answer the
same surface gave when pointed at OYL itself (`q4-pointed.md`, "groundbreakings
slated for 2025 or beyond"). Being named as a source did not improve the answer;
in that run it degraded it, while attaching OYL's name to it.
