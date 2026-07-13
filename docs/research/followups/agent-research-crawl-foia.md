# New Idea: Agent-Based Research Crawl to Sharpen FOIA Requests
*Source: discussion following review of REPORT-ux-proposal.md, July 12, 2026*

## Core idea

Government agencies (state/local especially) are often overwhelmed, and
institutional knowledge about what data exists frequently lives in
individual staffers' heads rather than being centrally documented. A vague
FOIA request ("do you have bike counter data?") risks going nowhere because
no one internally knows where to look.

The proposal: before filing a FOIA, use research agents to **crawl and scan
public-facing agency materials** to find *specific, citable references* to
the data in question — a report name, a page number, a procurement line
item, a person's name tied to a publication. Then file the FOIA referencing
that specific artifact, so agency staff have a concrete lead instead of
having to search from scratch.

> "The closer that we can get to be like, it was this thing on this table...
> ideally you would know the name of the person that published the report...
> then they can be like, okay, well, let's check their email."

## Why this matters / ethos

This isn't about generating adversarial pressure through FOIA volume (though
that's acknowledged as a legitimate secondary strategy — repeated requests
can nudge an agency toward automating/publishing data as open data by
default). The primary framing discussed was **collaborative, not
adversarial**:

> "They're the ones with the power, and they want to [help]... The whole
> point of what I'm doing here is to help them help them get it done."

Government workers are often under-resourced, not unwilling. The goal is to
make it as easy as possible for them to fulfill requests and, ideally,
self-serve toward publishing open data going forward — including offering
guidance in the FOIA itself about how the data could be made available more
sustainably (e.g., open data portal vs. one-off PDF/spreadsheet exports).

## What the agent crawl would look for (example: CDOT bike counter data)

- CDOT's Bicycling section — publications, data pages, Chicago Cycling
  Strategy PDF, Bicycle Survey documents
- CDOT's existing Transportation FOIA request log
- Press releases or announcements referencing bike counts, monitoring, or
  sensor installations
- Specific hardware/vendor names (e.g. "Eco-Counter") appearing in budget or
  procurement documents
- CMAP or university partnership/research announcements that might include
  count data as a byproduct
- Any quarterly/annual tracker documents (e.g. bikeway mileage tracker)
  already flagged as existing in some form

**Explicitly scoped out for this pass:** full document comprehension or
OCR/parsing of every PDF found. The goal is targeted reference-finding, not
deep reading — deep reading only kicks in once a lead is confirmed worth
pursuing.

## Output format

A short list of specific citations (document name, date, page/section if
findable, associated staff name if public) to attach to or reference in the
FOIA request — not a full report.

## Open question raised (unresolved)

Whether it's possible/appropriate to include *guidance* in a FOIA request
about how the agency could make requested data available as open data going
forward (portal vs. ad hoc exports). Not standard FOIA practice, but
discussed as worth testing — framed as a resource/suggestion rather than
an instruction, to avoid coming across as telling government staff how to
do their job.

## Next steps

1. Scope this as a discrete agent task once a target dataset (starting with
   CDOT counter data) is confirmed as the priority.
2. Draft a lightweight "open data enablement" blurb to test attaching to the
   next FOIA request.
3. Consider building a running list of confirmed contacts within agencies
   (an "open data allies" list) for informal outreach alongside formal FOIA
   filings.
