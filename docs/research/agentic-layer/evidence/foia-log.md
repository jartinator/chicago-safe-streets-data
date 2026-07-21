# Evidence brief: Chicago public FOIA request log (`u9qt-tv7d`)

> **STATUS: STUB.** States the research question + method. The kickoff
> (`../01-kickoff-prompt.md`, step 2) fills it before the study runs, on a Sonnet
> evidence agent, live-verified, in the citation style of
> `../../user-needs/evidence/*.md`.

## Why this brief exists

`get_foia_trends()` (`00-concept.md`, vignette V7) proposes surfacing what the
public repeatedly asks the city for about bikes/streets but that isn't published
yet. This brief establishes whether that's real and useful, and gives the
`chi-data-journalist`, `chi-investigative-reporter`, and `govtech-vendor` personas
(and the synthesis) something concrete to react to.

## Scope fence — READ FIRST

This is the **public FOIA _request log_** — a dataset *about* records requests
(requester, description, dates). It is FOIA **activity** data, a public dataset like
any other. It is **not** FOIA-response ingestion — that (integrating data OYL
receives back from its own requests) is a **separate session's** work and is out of
scope here. Do not design ingestion.

## Questions to answer (with citations)

- **Existence & shape** — confirm dataset `u9qt-tv7d` ("FOIA Request Log —
  Transportation") on the Chicago Data Portal: fields (requester name/org, free-text
  description, dates), coverage (May 2010–present), API access, refresh cadence.
- **Bike relevance & classification** — how to filter bike/infrastructure-related
  requests from a corpus dominated by red-light/speed-camera video and insurance
  requests. What keyword/classification approach separates signal (e.g. "protected
  bike lanes," "Bikeways Year End Reports," Divvy contracts, bike/ped bridge
  records) from noise, and how noisy is it? (Sample rows already suggest bike-related
  is a small but real minority — keyword filtering does real work.)
- **What a trends output could truthfully show** — "frequently requested, not yet
  public" patterns mapped against OYL's existing datasets; and what it *can't* show
  (requester intent, outcomes).
- **Prior art** — municipal FOIA-log analysis precedents worth citing.

## Feeds

Vignette V7 in the stimulus; the `get_foia_trends` disposition in the synthesis kill
list; the three technical/vendor personas' reactions.
