# Synthesis memo — proposed-projects concept validation (2026-07-13)

Four persona interviews, same research subjects as the round-1 news study
and the 2026-07 user-needs study (transcripts in this folder). Interviews on
Sonnet-class agents; synthesis by the orchestrating session.

## Verdict: SHIP v1, with amendments A–F

4/4 conditional use, zero rejections. The value is a *verified lead*, not an
authority: the ward office skims out-of-ward entries as a digest and
verifies in-ward ones; the advocate uses the citation-backed status as a
credibility prop with skeptical staffers; the organizer treats each entry as
a lead worth chasing, never repeated cold; the rider reads the plain status
sentence because it beats the CDOT PDF wall she already bounced off.

## Theme 1 — a status is only as good as its visible citation (4/4)

Ward office: a status he can't trace to a named CDOT source is unusable
in-ward, and "the date and the link protect the site's credibility with me —
they don't protect my afternoon." Organizer: "volunteer-written with a vague
or missing link is just a rumor with better formatting." Rider distinguishes
stale (tolerable, "like milk") from wrong-but-confident ("a wrong fact
sitting there looking exactly as confident as a true one").

**Amendment A:** every status requires ≥1 citation and the citation renders
*next to the status*, not in metadata ("per CDOT project page, May 2026").
**Amendment B (advocate):** the small status vocabulary will be read through
finer-grained real-world distinctions (which pot of money, which kind of
block) — `status_note` must carry the which-kind specifics, and status
citations should prefer official/primary documents over news articles
repeating the same vague word.
**Amendment F (rider):** the "volunteer-reviewed · official page is
authoritative" framing sits inline with the status, not in a footnote —
that's what keeps stale from masquerading as true.

## Theme 2 — roster selection is the equity surface (3/4)

Advocate: "if this list drifts toward whichever six projects have the most
news coverage… that's the same bias I already fight, just imported into a
new tool." Organizer: DLSD's prominence reads as glamour projects crowding
out West/South Side ones (didn't interest the advocate either — saturated,
no ward relevance). Rider reads her neighborhood's absence as "who
volunteers," not malice — still a trust cost.

**Amendment C:** roster criteria are published in the dataset note and the
sources card (official record exists + outcome unresolved + geographic
spread, explicitly including under-covered South/West projects), with an
invitation to propose additions via the repo. News volume is explicitly NOT
a selection criterion.

## Theme 3 — the empty coverage state carries meaning (organizer)

"No recent coverage found" on Englewood read two ways: a project dying
quietly, or an honest admission of a *press* gap (his preferred read,
parallel to the 311-undercount framing he already trusts OYL for).

**Amendment D:** empty-state copy says which it measures: "No recent news
coverage found — that measures press attention, not project activity."

## Theme 4 — placement: existing surfaces only (4/4)

Rider: a standalone page is a dead link ("I don't have a checking-back
habit"); ward office and organizer engage via the ward report. **Amendment
E:** citywide card on the action page + "Proposed here" line on the ward
report. No standalone page, no map lines (no honest geometry exists —
accepted by all four without pushback).

## Noted, not actioned

- Ward office's magic wand — CDOT pushing status changes — is the real gap;
  a volunteer tracker is inherently downstream. Out of scope, recorded.
- Advocate gets little direct value (her own tracking is better) — the
  feature is for residents and ward staff; she still uses it as a prop.
- Method limits: simulated participants; the stale-status tolerance and
  roster-fairness readings especially deserve real-human validation.
