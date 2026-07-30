---
status: sent
initiative: foia
to: cdotfoia@cityofchicago.org (or GovQA portal: chicago.gov/publicrecords → Transportation)
subject: FOIA follow-up to S145367-071326 — one incomplete GIS file and three narrower items
drafted: 2026-07-25
sent: 2026-07-25
tracking: filed under S145367-071326 — acknowledged 2026-07-27 by G. Rubenstein, FOIA Officer; new 10-day clock, response due 2026-08-10
tracker: #33
---

> **Acknowledged 2026-07-27.** CDOT did not treat this as a continuation of the
> granted request. G. Rubenstein (312-744-7335) wrote that the follow-up "has
> been forwarded for review" under a **new 10-day FOIA clock**, due on or before
> **August 10, 2026** — so the item-1 packaging fix gets a full fresh cycle
> rather than a quick correction. No extension was invoked; 10 days is the
> agency's own stated figure.
>
> The acknowledgment came to the personal address, not the project address,
> because it threads off S145367-071326 — a request filed before the
> project-identity rule took effect. Nothing to correct; noting it so the
> mismatch is not read later as a lapse.

# FOIA follow-up: gaps in the S145367-071326 release

*Follow-up to the granted request S145367-071326 (released 2026-07-24). Item 1 is
almost certainly a packaging slip and is the only item that matters much — it is
written so it can be answered on its own in a couple of minutes. Items 2–4 are
explicitly optional and each carries its own drop-it-if-burdensome line, per
`docs/projects/collaboration-principles.md` (no goose chases; make it cheap to say
yes). Send from the **onyourleftopensource@gmail.com** identity.*

*Sending note: keep bare domains out of the body. A scheme-less domain like
`data.cityofchicago.org` gets auto-linkified by Gmail into a
`google.com/url?q=...` redirect, which reads as a tracking link and is
routinely stripped or blocked by government mail filters. Name the portal and
cite the dataset ID instead — it is the more precise identifier anyway. Any URL
that genuinely must appear should carry an explicit `https://` scheme.*

*Detail behind every claim below: `data/foia/S145367-071326/README.md`.*

---

To: Freedom of Information Officer, Chicago Department of Transportation (CDOT)
Re: Follow-up to FOIA request S145367-071326 — request under 5 ILCS 140

Dear FOIA Officer,

Thank you for the response to S145367-071326, released on July 24. It was thorough and
genuinely useful — the Complete Streets program dashboard and the bikeway layers with
per-segment install years answered exactly what we were trying to establish, and we have
published an analysis built on them.

This is a short follow-up about **one file that appears to have been packaged
incompletely**, plus three smaller items. I have tried to make each one answerable on its
own, so nothing here needs to wait on anything else.

## 1. The 2025 bikeway layer is missing its `.shp` (the only item I'd call important)

In the released folder `2026-07-20 - Bike Lane Mileage Tracker`, the file
`GIS/2025_Bike Network_internal.shp.zip` contains six of the seven files a shapefile
needs:

- `2025_Bike Network_internal.dbf` (1,008 attribute rows — readable)
- `.shx`, `.prj`, `.cpg`, `.sbn`, `.sbx`
- **no `.shp`** — the file holding the geometry itself

So the 2025 attributes are usable but the lines are not. Every other year in the release
was complete; `GIS/Bikeway_Network_2024_Final.shp` and its siblings all arrived intact.
This looks like a zip that was assembled from a partial selection rather than any
deliberate withholding.

**Request:** a copy of the `.shp` for that 2025 layer, or simply a re-export of the same
layer as a complete shapefile (or a file geodatabase / GeoJSON, whichever is least work).

## 2. Bikeway network layers for 2011–2017 *(optional)*

The release included year layers for 2010 and then 2018 through 2025, with nothing
between. If year-end bikeway layers for any of **2011–2017** still exist in the program's
files or archives, I request those in their native format.

If they were not retained, please just say so — a "not retained" answer is a complete and
useful answer here, and I do not want anyone searching archives on my behalf. **If this
item alone would make the request burdensome, please disregard it and answer item 1.**

## 3. Quarterly tracker snapshots, if they exist as saved files *(optional)*

The original request's item 1 asked for each quarterly update of the mileage tracker. What
came back was annual (year-end) values in `CompleteStreets_Dashboard.xlsx`, which may
simply be the form in which the numbers exist.

To be precise about what I am asking: **only saved files that already exist** — dated
copies, quarterly exports, or archived versions of the tracker. I am not asking anyone to
reconstruct quarterly figures. If the dashboard is maintained in place and only year-end
values are retained, that answer fully resolves this item.

## 4. Document metadata for the dashboard file *(optional, narrowed)*

The original item 3 asked for version history, which was not addressed in the response. I
suspect that request was broader than necessary, so I am narrowing it to the smallest
useful form:

For `CompleteStreets_Dashboard.xlsx` only, the **file-system or document-management
metadata** — created date, last-modified date, and author/owner as recorded by SharePoint,
OneDrive, or the shared drive. A screenshot of the file's properties pane is fine. I am not
asking for a full revision export or for the contents of prior versions.

Purpose, so you can judge whether it is worth the effort: we cite figures from that
dashboard publicly, and a modified date lets us state accurately how current those figures
were when released. If retrieving it is not straightforward, please disregard this item.

## Format, fees, and narrowing

Electronic delivery, native format where one exists. These records are requested for a
noncommercial public-interest purpose — a free, open public dashboard on cyclist safety and
bicycle infrastructure — so I request a fee waiver under 5 ILCS 140/6. If fees would
exceed $25, please contact me before incurring them.

If any part of this is unduly burdensome under 5 ILCS 140/3(g), **please treat item 1 as
the entire request** and disregard items 2 through 4. If records are withheld in whole or
part, please cite the specific exemption per 5 ILCS 140/9.

## One optional note, offered as a resource

Items like these stop being necessary if the install-date attribute travels with the
published data. The public Bike Routes layer on the Chicago Data Portal
(dataset `hvv9-38ut`) carries facility type and geometry but no
install or upgrade date — yet CDOT's internal layers clearly maintain `BW_INST_YR` and
`BW_INST_MO` already. Publishing those two existing columns on the public layer would let
anyone reconstruct the network's history without asking CDOT for anything, and would likely
retire most future requests of this kind, including ours.

Offered only as a suggestion, and entirely your call — I recognize the decision involves
considerations outside this office.

Thank you again for the July 24 response, and for your time on this.

Sincerely,
On Your Left! — an open-source Chicago bike-safety data project
onyourleftopensource@gmail.com
https://jartinator.github.io/chicago-safe-streets-data/

---

## Sent

**Sent 2026-07-25, 05:23 UTC**, by email to `cdotfoia@cityofchicago.org`.

**First request filed under the project identity** — sent from
`onyourleftopensource@gmail.com`, per the 2026-07-23 standing rule. Requests #1
and #2 predate the rule and went out under the maintainer's personal name, which
is what appears in Chicago's public FOIA logs for those two.

No tracking number yet. Precedent (Smart Streets, 2026-07-21) is that email to a
department FOIA inbox is routed into GovQA and issued a reference the same day.

**Clock.** Sent on a Saturday, so CDOT will log receipt Monday **2026-07-27**.
Illinois allows 5 business days from receipt, extendable by 5 — so a response is
due around **2026-08-03**, and the +5 extension would move it to about
**2026-08-10**. Nudge if there is no acknowledgment at all by **2026-08-05**.
Update this file and `docs/foia/log.md` row 5 the moment a reference number lands.
