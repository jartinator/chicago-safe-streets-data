# Interview-guide addendum (agentic dimension)

Layered onto `../user-needs/03-interview-guide.md`. Run that guide's structure;
apply these changes. The stimulus is `02-stimulus-access-experiences.md`.

## §2b (NEW — before the stimulus, so answers aren't anchored): your own AI, today

Everyone:
- When did you last ask an AI assistant a factual question about your city or
  work? What did you do with the answer — repeat it, check it, drop it?
- What would it take for you to repeat an AI-given number to [your hardest audience]?
- What does your organization say about using AI for work?
- What's the most repetitive data chore in your month?

Technical personas also: your current data-pulling workflow, what breaks it, and
what you would never build on.

## §3 (REPLACED): vignette walkthrough

Use stimulus Part B for everyone, then Part C for technical personas only. Per
vignette, fixed probes:
- **Use moment** — concretely, in what meeting/document/story would this land?
- **Trust requirement** — what must travel *with* it before you'd use it?
- **Output shape** — spoken prose / one-pager / table / raw CSV? Ask concretely,
  per vignette, never in the abstract.
- **Delegation** — would you let the assistant do this and just tell you, or must
  you see it yourself? Why?

## §4 (EXTENDED): gap probing

Add:
- **Verification** — "your assistant says Ward 25 is up 40%. What happens between
  hearing that and saying it out loud?"
- **New data** — stimulus Part D (preferences only; do not let it drift to
  ingestion design).

## §5 (ADAPTED): magic-wand close

- "You get to ask one question out loud and receive an answer you'd defend in front
  of your hardest audience. What's the question, and what must the answer look like
  to survive that room?"
- "What's the first thing an AI answer could get wrong that would make you never
  use this again?"

## Scenario-table additions (§4 substitutions)

| Persona class | Scenario |
|---|---|
| Data journalist | fact-checking a corridor story on deadline |
| Investigative reporter | reproducing a multi-week data story from primary sources |
| Civic-tech developer | building a weekend tool for a community org |
| Govtech vendor | scoping a data feature for a city-agency client |

Existing rows from the base guide are unchanged (the Europeans keep their
advising-a-city scenarios), now with the agentic overlay in force.
