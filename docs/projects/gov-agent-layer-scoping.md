# Gov agent layer — policy landscape & scoping

Answers the open questions in `gov-agent-layer-proposal.md`. Sources were
gathered by web research agents in July 2026; **direct fetches to `.gov`
domains were proxy-blocked in the research environment, so operative
quotes come from search-indexed snippets of the primary documents** — every
document's existence and URL was multiply corroborated, but verify verbatim
language against the primary PDFs before citing to an agency contact.

## 1. What the policy landscape actually is

### City of Chicago — a vacuum, not a ban

- **No completed, binding employee generative-AI use policy could be
  verified to exist.** What exists:
  - **"City of Chicago Roadmap for AI"** (Dept. of Technology and
    Innovation): strategy + five guiding principles (equitable, inclusive,
    human-centered, accountable/transparent, safe-secure-privacy-preserving)
    — and it *itself recommends* the city "immediately issue a short, clear
    policy… to let employees safely use AI assistance." That policy's
    publication could not be confirmed.
    https://www.chicago.gov/city/en/sites/chitech/home/roadmap-for-AI.html
  - **Ordinance O2024-0008864** (Municipal Code Ch. 2-68, Art. II): requires
    the CIO to establish guidelines for responsible **AI systems** (pilots,
    knowledge-sharing, semi-annual public reporting). Governs city AI
    *programs*, not employees' use of external tools.
  - **Office of Privacy and AI Compliance (OPAC)**, Dept. of Law — the
    city's centralized privacy/AI legal authority.
  - No mayoral AI executive order found.
- **Implication:** the original premise ("weirdly restrictive rules") is
  likely wrong for Chicago specifically. The realistic constraint on a city
  staffer is *uncertainty*, not prohibition — which argues for a guide that
  helps a willing staffer act confidently inside the lines that do exist
  (the Roadmap principles, OPAC's remit), rather than a tool that implies
  the lines are obstacles.

### State of Illinois — permitted with guardrails

- **DoIT "Policy on the Acceptable and Responsible Use of Artificial
  Intelligence"** (effective 2025-04-01): AI use is not banned. Per the
  policy (snippet-sourced) and AP coverage: AI must not be discriminatory
  or illegal, must not make decisions without human oversight, and must not
  access **confidential or sensitive information without agency-head
  approval**; public-facing or decision-making AI must be disclosed;
  agencies designate a responsible employee and may adopt stricter rules.
- **Generative AI & NLP Task Force report** (Dec 2024, statutory):
  recommends identifying prohibited uses, transparency/accountability in
  public-service AI, ethical-use guidelines, resident redress.
- No AI executive order; SB 315 (2026) regulates frontier developers, not
  employee use.

### Comparable cities (the range the guide should anticipate)

| City | Posture | Operative rule for our purposes |
|---|---|---|
| Boston (2023 interim, v1.1) | Most permissive — encourages experimentation | "Never share confidential information in the prompts"; disclose AI use |
| Seattle (POL-209, 2023) | Structured | No data classified Confidential+ into gen-AI tools absent enterprise controls; approved procurement only |
| NYC (OTI guidance) | Structured | City-managed accounts only; no personal accounts; disclosure |
| San Jose (2023) | Most restrictive | Dedicated accounts, cite-and-record every use, prohibited use list |

### Cross-cutting legal note

Assume **prompts and outputs created by public employees in the course of
work are public records** (Illinois State Records Act / local records
retention apply; several cities' guidance points the same way). We found no
Illinois document squarely deciding FOIA-ability of AI prompts — treat
"write every prompt as if it will be FOIA'd" as the prudent default, and
flag it as an inference, not settled law.

## 2. Delivery-model assessment (the proposal's open question)

**Recommended: (b) a documented safe-use guide/prompt, distributed via
(c) known agency contacts. Not (a) a hosted product — for now.**

- A hosted product operated by us *for* government staff would itself look
  like an "AI system" in the sense of Chicago's ordinance and OPAC's remit,
  and NYC-style account rules (no personal/unmanaged accounts) show where
  municipal policy trends: staff may soon only be able to use tools their
  employer provisions. A guide travels through that door; our hosted tool
  doesn't.
- Chicago's own Roadmap already calls for exactly the artifact we can
  draft. A well-made external guide can serve as a reference
  implementation a friendly insider could adapt — the highest-leverage,
  lowest-presumption move, consistent with `collaboration-principles.md`
  (advisory not directive; relationships before launches).
- Cost of being wrong is near zero: a guide can graduate into a hosted
  offering later if contacts ask for one.

## 3. Draft: the minimal safe-use guide (v0, for known contacts)

> ### Using AI assistance for open-data work — a safe-harbor pattern
> For public-sector staff who want AI help with *public-facing* data work.
> Your employer's own policy always wins; this pattern is designed to be
> safe under the strictest policy we surveyed.
>
> **Three hard rules**
> 1. **Nothing non-public goes in.** No resident data, no internal
>    deliberations, no draft records, no credentials, no colleague names.
>    If you're unsure whether something is public, it isn't — describe it
>    generically instead ("a table of monthly counts by location").
> 2. **Write every prompt as if it will be FOIA'd.** It may be a public
>    record. This is a feature: it keeps the conversation on ground you
>    can defend.
> 3. **You are the author.** AI output is a draft for your judgment, not a
>    decision. Fact-check anything that will be published or relied on,
>    and follow your agency's disclosure norms.
>
> **What this is good for (all public-side):** how to structure a dataset
> for release (tidy format, data dictionary, update cadence); writing a
> dataset description or metadata; choosing between a portal dataset and a
> one-off export; drafting a plain-language explanation of a methodology;
> checking a proposed schema against common open-data standards.
>
> **Worked example prompt:**
> "I maintain a spreadsheet of bicycle counts: one row per location per
> month, columns for location name, month, count, equipment type. It's
> public information. How should I structure and document this for
> publication on an open-data portal so it's usable without my help —
> field naming, data dictionary, update process?"
>
> **What the assistant should refuse / you should never ask:** anything
> requiring the actual non-public records; anything about specific
> residents, personnel, or pending matters; anything your policy reserves
> for approved tools.

## 4. Next steps

1. Verify the operative quotes against primary PDFs (the one research gap;
   any machine outside the `.gov`-blocked proxy can do this in an hour).
2. Confirm whether Chicago ever published the employee policy its Roadmap
   recommends (an OPAC/DTI question — good first-contact conversation).
3. Test the v0 guide with one known contact (per
   `collaboration-principles.md` #5) before any wider distribution.
4. Revisit the hosted-product question only if contacts report their
   agencies won't accept a guide-based pattern.
