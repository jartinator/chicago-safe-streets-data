# New Project Idea: AI Agent Layer for Government Workers
*Source: discussion following review of REPORT-ux-proposal.md, July 12, 2026*

## The problem

Many government employees are likely restricted from using AI tools in their
work — agency policy may prohibit putting government information into
external AI systems, even when the underlying task (e.g. figuring out how to
structure and publish a dataset) is benign and the data itself is meant to
be public.

> "They might be saying, oh, you can't put government stuff into AI at all.
> It might have weirdly restrictive rules."

This creates a gap: staff who *want* to make data more open and
accessible may lack any safe, sanctioned way to get help doing so.

## The idea

Build a dedicated, sandboxed AI agent layer specifically for government
workers — separate from (but complementary to) the activist/citizen-facing
side of the project. Positioned explicitly as a service *to* government
staff, not a workaround of their constraints:

> "As a... personally... we can provide resources... maybe that's what it
> is? We just literally produce an agent layer for governments... it's not
> a specific use case. In addition to the use case of the activists."

Key properties discussed:

- **Respects institutional restrictions.** Staff would not input restricted/
  sensitive information. The tool would be scoped to help with public-facing
  work: how to structure a dataset for release, how to think about an open
  data pipeline, general best-practice guidance.
- **Advisory, not directive.** The agent could explain what's possible and
  useful ("here's what a good open-data release looks like") while clearly
  declining anything that crosses into restricted territory:
  > "I can tell you this much, but... that's the limit, and you can't tell
  > me certain things."
- **Educational framing.** Could function like a consultant — staff describe
  what they have, the agent describes what could be done with it, without
  ever touching non-public information.
- **Dual-purpose civic value.** Serves as both (a) a genuine service that
  makes agency staff's jobs easier and (b) a soft lever for getting more
  public data released faster than it otherwise would be, because staff have
  a low-friction way to explore what "publishing this well" would look like.

## Ethos behind it

Raised explicitly in conversation: the goal is not to treat government as an
adversary. Most public servants want the system to work better and are
constrained by under-resourced institutions, not by personal unwillingness.

> "It's not them, it's the system... I want to make sure that if we're
> finding this stuff and we know that it exists, I don't want to be sending
> them on goose chases."

This project would extend that ethos from "make our FOIA requests easier for
them to fulfill" (see companion doc) to "give them a standing tool that
helps them move toward openness on their own terms."

## Open questions (unresolved, for team discussion)

- What's the actual legal/policy landscape for AI use by municipal/state
  employees in Illinois/Chicago specifically? Needs research before this
  goes further.
- Would this need to be a literal separate hosted product, or could it be a
  documented prompt/config that staff could run on any AI tool they're
  already cleared to use (e.g. "here's a prompt you can safely use — don't
  add your own agency's non-public info")?
- Distribution: how would agency staff even discover/trust this exists?
  Likely ties back to the personal-contact/relationship-building strategy
  discussed in the FOIA doc — this could be something offered directly to
  known contacts inside agencies first, rather than launched publicly.

## Next steps

1. Treat as a separate, early-stage project — not blocking on the OYL
   research proposal itself.
2. Research public-sector AI usage policy constraints before scoping further.
3. Consider starting minimal: a documented, safe prompt/guide rather than a
   hosted product, to test appetite with known contacts first.
