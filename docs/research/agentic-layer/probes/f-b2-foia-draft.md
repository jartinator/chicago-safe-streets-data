---
probe_id: F-B2
function: Document production (records request)
task: identify OYL's most valuable missing dataset from public files and draft a send-ready Illinois FOIA request
agent: cold Sonnet subagent, web tools only, no study context
run_datetime: 2026-07-23
outcome: executed — task completed
grades: {T: 2, C: 2, V: 2}
note: independently converged on the maintainer's real 2026-07-12 CDOT request
---

# Probe F-B2 — "help me FOIA what this site says is missing"

## Prompt (verbatim task, as given)

> The site https://jartinator.github.io/chicago-safe-streets-data/ is honest
> about what data it doesn't have — I want to help fix that with a
> public-records request. Using what the site itself publishes about its own
> gaps and methods, figure out what the single most valuable missing dataset
> is, which City of Chicago agency would hold the records, and draft me a FOIA
> request under the Illinois Freedom of Information Act that I could actually
> send: specific enough that the agency can't dodge it, with the records
> described precisely, a fee-waiver request, and the right recipient. Tell me
> your reasoning for what to ask for before the letter.

## Deliverable — reasoning (verbatim)

> **What the site itself says is missing.** OYL's README and DECISIONS.md name
> five gaps: dooring undercounting (a legal-threshold artifact, not a records
> gap), no obstruction data (deliberately out of scope, redirected to Bike
> Lane Uprising), no cyclist-volume/exposure data ("neither CDOT nor the city
> publishes" it — likely doesn't exist as a clean record), CDOT's
> planned-bikeways layer being a spreadsheet+static-map rather than structured
> geometry (already public, just not machine-readable — not a FOIA problem),
> and **historical/dated bikeway installation records**.
>
> That last one is the one the project's own maintainers flagged as
> *FOIA-shaped*. DECISIONS.md #18, verbatim: **"The only route to a
> *retroactive* series is a records request for archived tracker versions or a
> GIS layer carrying install dates."** Everything else on that gap list is
> either a statutory artifact (dooring), an intentional scope exclusion
> (obstructions), or data that plausibly doesn't exist in city hands at all
> (ridership volume). This is the one gap where the site's own authors
> concluded "FOIA is literally the mechanism," named the record type
> precisely, and named the likely custodian (CDOT…).
>
> **Why it's valuable.** Without install dates, OYL (and anyone else) cannot
> compute "crashes per corridor before vs. after protected infrastructure went
> in" — the single most persuasive evidence-based argument for or against a
> given treatment. …
>
> **Why it's gettable.** CDOT visibly maintains exactly this kind of record
> already — … it isn't asking CDOT to create a new dataset, just to produce
> an existing one (or successive annual versions of it) in the format it's
> already kept.
>
> **Agency.** Chicago Department of Transportation (CDOT) … FOIA intake:
> **CDOTfoia@cityofchicago.org** (confirmed via the department's own FOIA
> page listing, cross-checked against Chicago Headline Club's
> Chicago-government FOIA contact roster).

## Deliverable — the letter (verbatim body, header elided)

> RE: Freedom of Information Act Request — Dated Bikeway Installation Records
>
> Dear FOIA Officer:
>
> Pursuant to the Illinois Freedom of Information Act, 5 ILCS 140/1 et seq., I
> request copies of the following public records held by the Chicago
> Department of Transportation (CDOT):
>
> 1. All versions, editions, or dated snapshots of CDOT's internal "Bikeways
>    Installations Tracker" (or any successor/differently-named internal
>    spreadsheet or tracking document serving the same function…) created or
>    in effect at any point from January 1, 2019 through the date this request
>    is processed. If the tracker is a living document rather than discrete
>    dated files, I request the most recent version available at the start of
>    each calendar year in that range…, or, in the alternative, whatever
>    periodic archived copies CDOT already retains in the ordinary course of
>    business.
>
> 2. Any GIS layer, shapefile, geodatabase, or geospatial export corresponding
>    to CDOT's public "Bike Routes" dataset (the dataset published at
>    https://data.cityofchicago.org/d/hvv9-38ut) that includes, for any
>    bikeway segment, a field or attribute recording an installation date,
>    completion date, construction date, or equivalent as-built date — whether
>    that field appears in the currently published public layer or only in an
>    internal/pre-publication version of the same geodatabase.
>
> 3. To the extent items 1 or 2 do not fully capture it: any other record —
>    spreadsheet, database export, work-order log, or GIS attribute table —
>    that CDOT maintains showing, for individual protected bike lane, buffered
>    bike lane, painted bike lane, neighborhood greenway, or
>    shared-lane-marking projects, the date on which construction/striping was
>    completed and the project was opened to public use.
>
> Format and delivery: … native electronic format (e.g., .xlsx, .csv, .shp,
> .geojson, or file geodatabase) rather than converted to PDF…
>
> Fee waiver request: I request a waiver of all fees under 5 ILCS 140/6(c).
> This request is made for a non-commercial, public-interest purpose… [names
> the OYL dashboard and repo, states the public-interest basis: letting the
> public evaluate whether infrastructure investments correlate with reduced
> crashes] … Any information obtained will not be used for commercial
> purposes.
>
> If you deny any portion of this request, please cite the specific statutory
> exemption(s) claimed for each withheld record or portion thereof, as
> required by 5 ILCS 140/9(a), and release all reasonably segregable
> non-exempt portions per 5 ILCS 140/7(1).
>
> Per 5 ILCS 140/3(d), I understand CDOT must respond within 5 business days
> of receipt (extendable by 5 additional business days with written notice
> under 5 ILCS 140/3(e)). Please confirm receipt of this request.

(The full verbatim letter, including the address block the agent flagged as
unconfirmed, is preserved in the probe's raw return; the elisions above are
formatting only.)

## Tool log (as reported)

```
WebFetch …github.io/chicago-safe-streets-data/
WebSearch site:jartinator.github.io chicago-safe-streets-data
WebFetch raw.githubusercontent.com …/main/README.md  (×2)
WebFetch github.com/jartinator/chicago-safe-streets-data
WebFetch …/map.html
WebFetch raw.githubusercontent.com …/main/DECISIONS.md
WebSearch: Chicago Department of Transportation FOIA officer request email address 2026
WebSearch: CDOT bike lane install date GIS "bike routes" history tracker
WebFetch chicago.gov …/cdot_foia.html          ← 403
WebFetch chicago.gov …/foia_contacts.html      ← 403
WebFetch headlineclub.org/foia/chicago/
WebSearch: "CDOT" Chicago FOIA officer mailing address "LaSalle"
```

## FRICTION (verbatim, key items)

> - The live site … is a JS-rendered SPA — WebFetch returned only the
>   `<title>` tag for both the homepage and map.html … I had to go to the
>   GitHub repo's raw README.md and DECISIONS.md instead.
> - Once I was in the raw markdown, the gaps were stated unusually clearly —
>   better than most public dashboards. … That's the opposite of friction —
>   it made identifying the target trivial once I found the right file.
> - Agency attribution required outside confirmation. The repo docs never say
>   "FOIA CDOT for this" in so many words…
> - `chicago.gov` pages … both returned HTTP 403 to WebFetch — I could not
>   directly verify CDOT's FOIA officer name or confirm the mailing address
>   from the primary source. I fell back to a secondary aggregator… flagged
>   as such in the letter.
> - No FOIA officer's name was locatable anywhere…

## Study verification & grading

The decisive comparison: the probe's letter vs the maintainer's **real**
request (`docs/outbox/2026-07-12--foia--cdot--bikeway-mileage-history.md`,
drafted 11 days earlier, which the probe could not have seen — it is not
served on the public site).

| Element | Maintainer's real letter | Cold probe |
|---|---|---|
| Target gap | historical mileage tracker + install dates | **same** |
| Agency | CDOT, FOIA intake email | **same** |
| Tracker versions, all/dated | item 1 | item 1 (adds a Jan-1-snapshot fallback narrowing) |
| GIS layer w/ install-date attribute | item 4, notes public layer lacks the field | item 2, cites the exact Socrata dataset ID and notes the same absence |
| Native-format demand | yes | yes |
| Source spreadsheet/DB + version history | items 2–3 | partially (item 3 catch-all; no SharePoint/version-history ask) |
| Transmittal-email narrowing option | item 6 | absent |
| Fee waiver w/ statutory cite | (in companion docs) | in-letter, 5 ILCS 140/6(c) |
| Exemption-citation + segregability demand | — | in-letter, 140/9(a) + 140/7(1) |

Two documents, same target, same custodian, overlapping records language —
drafted independently. The probe letter is somewhat *less* precise on
version-history mechanics and lacks the transmittal-records fallback; it is
*more* explicit on statutory boilerplate (fee waiver, exemptions,
segregability). A professional would send either.

One conduct note: the agent put the maintainer's real name and public email
in the letter header (both are public in the repo/site attribution it
fetched). Appropriate for the task as framed; noted for completeness.

| Axis | Score | Basis |
|---|---|---|
| T | **2** | Reasoned target selection + send-ready letter with fee waiver, statutory cites, format demands, and honest flags on the two facts it could not verify (officer name, mailing suite). |
| C | **2** | DECISIONS.md #18 quote is genuine; the Socrata dataset ID is the real Bike Routes layer; statute citations are correct; the gap analysis (which gaps are FOIA-shaped vs. not) matches the maintainer's own triage. |
| V | **2** | Provenance carried into the artifact itself — the letter's public-interest paragraph accurately describes OYL and its terms; unverifiable details flagged in-line rather than asserted. |
| G | high | G2 (found gaps via repo, not site — the *site* never told it; the noscript pointer didn't surface), plus a new one: **agency-contact verification is a weak link** (chicago.gov 403s to fetchers), which any "FOIA seed-bank" feature should compensate for by publishing the routing itself. |

**Function verdict:** the strongest probe result in the set. The layer's
honesty about its own gaps is *already* sufficient fuel for an outside agent
to reconstruct the maintainer's professional-grade records request — but only
by escaping the published site into the repo. Publishing the gap list where
agents actually look (per G2) converts this from a lucky path into a
capability — and it is the advocate interview's single most-wanted function
("a door that's closed to us").
