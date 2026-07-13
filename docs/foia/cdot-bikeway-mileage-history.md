# FOIA request — CDOT historical Bike Lane Mileage Tracker

**Purpose.** The public CDOT Bike Routes portal layer (`data.cityofchicago.org`, dataset
`hvv9-38ut`) is *current-state only* — no install date per segment — and the quarterly Bike
Lane Mileage Tracker on the Complete Streets "Existing Bike Network" page is overwritten each
quarter with no published archive. To build a bikeway-mileage time series (and correlate
infrastructure growth against crash trends), we need the historical quarterly values CDOT
retains internally. This request targets those records.

**How to submit.**
- Online portal (GovQA): https://www.chicago.gov/publicrecords → "All Other Departments" →
  Department of Transportation
- Or email the body below to **CDOTfoia@cityofchicago.org** (an officially listed channel)
- Statutory response: 5 business days (may be extended 5 more). First 50 B&W pages free;
  electronic records are typically provided at no or minimal cost.
- Note: in Chicago, the requester name and request text are published in the public CDOT FOIA log.

---

## Request body

To: Freedom of Information Officer, Chicago Department of Transportation (CDOT)
Re: FOIA request under the Illinois Freedom of Information Act, 5 ILCS 140

Dear FOIA Officer,

Under the Illinois Freedom of Information Act (5 ILCS 140), I request copies of the following
records held by CDOT, including those maintained by the Complete Streets / Bikeways program. Where a
record exists in an electronic format, **I request it in its native, machine-readable format**
(e.g., Excel `.xlsx`, `.csv`, Shapefile, or file geodatabase) rather than as a PDF or printout, and
delivered electronically by email or download link.

I am requesting the following:

1. **All versions of the Bike Lane Mileage Tracker.** Every version, iteration, or dated snapshot of
   the tabular bike lane mileage tracker that has been posted to, or used to populate, CDOT's
   "Existing Bike Network" / Complete Streets webpage, from the earliest date such a tracker exists
   through the present. This includes each quarterly update, in native spreadsheet format, showing
   mileage by bikeway type (e.g., protected/barrier-protected bike lane, buffered bike lane,
   conventional/painted bike lane, neighborhood greenway, marked shared lane/sharrow, and off-street
   trail).

2. **The source spreadsheet(s) or database used to generate the tracker.** The underlying working
   file(s), spreadsheet(s), or database export(s) CDOT uses to calculate and update the mileage
   tracker, including any columns or fields for bikeway facility type, segment mileage/centerline
   length, ward or community area, and installation or upgrade date.

3. **File version history and timestamps.** For the tracker file(s) and their source file(s) in
   requests 1–2, any available document-management or version-history records — for example
   SharePoint, OneDrive, or shared-drive version history — showing the date/time of each saved
   revision and, if available, the values at each revision. If full version history cannot be
   exported, I request the file-system or document-management metadata (created date, modified dates,
   and author) for each such file.

4. **GIS bikeway layer with installation dates.** Any GIS dataset — Shapefile, file geodatabase,
   GeoJSON, or KML — of the on-street and off-street bikeway network that includes a per-segment
   attribute for installation date, date built, year installed, date last modified, or comparable
   temporal field (the public open-data Bike Routes layer does not contain such a field).

5. **Annual and quarterly mileage-installed figures and backup.** Records showing the miles of
   bikeways installed or upgraded by facility type for each quarter and/or calendar year (for
   example, the "miles installed this year" figures CDOT reports publicly), together with the
   supporting calculations or segment lists behind those figures.

6. **Transmittal records for the quarterly updates (optional / narrowing).** To the extent it is not
   unduly burdensome, any emails, memoranda, or transmittal records that accompanied the posting of a
   quarterly mileage tracker update, whose subject or body contains the phrase "mileage tracker,"
   "bike lane mileage," or "bikeway mileage," for the period January 1, 2019 to the present. If items
   1–5 already capture the historical values, this item may be disregarded; I include it only to
   reach any historical figures not preserved in the tracker files themselves.

**Format and delivery.** Please provide all responsive records electronically. For spreadsheets and
GIS data, please provide the original file rather than a PDF or image, so the data remains usable.

**Fee waiver.** These records are requested for a noncommercial public-interest purpose — an open,
public dashboard analyzing cyclist safety and bicycle-infrastructure trends in Chicago — and not for
commercial use. I therefore request a waiver or reduction of any fees under 5 ILCS 140/6. If fees
will nonetheless exceed $25, please contact me for authorization before incurring them.

**Narrowing.** If any part of this request is deemed unduly burdensome under 5 ILCS 140/3(g), please
contact me so I can narrow it — for example, by limiting the date range or focusing on items 1, 2,
and 4, which are the core of what I am seeking. If any records are withheld in whole or in part,
please cite the specific statutory exemption for each redaction as required by 5 ILCS 140/9.

Thank you for your assistance. Please contact me if you have any questions.

Sincerely,
Jared Meyer
jaredthomasmeyer@gmail.com

---

## Notes for the requester

- **The core items are 1, 2, and 4.** They are the ones most likely to yield a clean historical time
  series. If you want to minimize the chance of a "burdensome" pushback, you can submit only those
  three and add the others later.
- **Why item 4 matters:** a GIS layer with a per-segment install date would let us reconstruct the
  full historical mileage-by-quarter series *retroactively* — something the overwritten tracker and
  the date-less public portal layer cannot give us. It is the single highest-value record here.
- **If CDOT says no historical versions are retained:** that answer is itself useful — it confirms
  the pipeline's forward-only snapshot approach (`data/snapshots/`, `infra_growth_trend()`) is the
  only viable path, and the FOIA log will document that the data does not exist.
- **Cross-reference:** see `DECISIONS.md` (#18) and `log.md` (this folder) for how any returned data would
  feed `bikeway_mileage_series.json` and the per-ward `infra_growth_trend`.
