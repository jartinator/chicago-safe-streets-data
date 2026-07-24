"""Pair the curated bikeway-commitments roster (data/commitments.json) against the
citywide bikeway mileage series (site/data/bikeway_mileage_series.json) for the
"promise vs. delivered" finding — user-needs report P5.

Pure function over the two already-parsed dicts — no I/O, no crash data, no
network — so it is testable and safe to call from aggregate.py after both
inputs are loaded.

Low-stress definition used here (stated in the finding's own description so it
travels with the data, not just this file): protected + buffered + greenway +
trail miles count as low-stress; painted lanes and sharrows do not.
"""

LOW_STRESS_CATEGORIES = ("protected", "buffered", "greenway", "trail")

# The headline commitment this finding leads with — the 150-new-miles pledge
# from the 2023 Chicago Cycling Strategy. Falls back to the first roster entry
# if the roster is ever re-ordered or re-keyed.
HEADLINE_COMMITMENT_ID = "150-new-miles"

FOIA_NOTE = (
    "docs/outbox/2026-07-12--foia--cdot--bikeway-mileage-history.md"
)


def _headline(commitments):
    for c in commitments:
        if c.get("id") == HEADLINE_COMMITMENT_ID:
            return c
    return commitments[0] if commitments else None


def build_commitments_finding(commitments_doc, bikeway_series):
    """(parsed data/commitments.json, parsed site/data/bikeway_mileage_series.json)
    -> one findings.json card, or None if either input is empty.
    """
    commitments = (commitments_doc or {}).get("commitments") or []
    series = (bikeway_series or {}).get("series") or []
    if not commitments or not series:
        return None

    headline = _headline(commitments)
    latest = series[-1]
    by_cat = latest.get("by_category") or {}
    total = latest.get("total") or 0.0
    low_stress = round(sum(by_cat.get(c, 0.0) for c in LOW_STRESS_CATEGORIES), 2)
    low_stress_share = round((low_stress / total) * 100) if total else None
    as_of = latest.get("date") or ""

    number = headline.get("number")
    unit = headline.get("unit")
    year = headline.get("year_committed")
    source = headline.get("source_name")

    description = (
        f"CDOT's {year} Chicago Cycling Strategy commits to {number} {unit} of "
        f"new bikeways, 80% of them low-stress. As of {as_of}, Chicago's on-street "
        f"and trail bikeway network totals {total:,.0f} miles, of which "
        f"{low_stress:,.0f} miles ({low_stress_share}%) are low-stress by this "
        f"count (protected lanes, buffered lanes, neighborhood greenways, and "
        f"off-street trails; painted lanes and sharrows are not counted as "
        f"low-stress here). Source: {source}."
    )
    caveat = (
        "This pairs the published commitment against the current network "
        "snapshot, not against what's been delivered since the commitment: the "
        "CDOT Bike Routes layer has no install-date field, so the bikeway "
        "mileage series is built forward from snapshots (first snapshot "
        f"{series[0].get('date', '')}) with no way to attribute any of today's "
        "miles to construction before or after 2023. OYL cannot measure miles "
        f"delivered since the 2023 commitment until CDOT answers the pending "
        f"install-date FOIA ({FOIA_NOTE})."
    )

    return {
        "id": "commitments-vs-delivered",
        "title": "Promised bikeway miles vs. the network on the ground",
        "stat": f"{number} new {unit}",
        "description": description,
        "caveat": caveat,
        "map_state": {"screen": "table", "layers": [], "filters": {}},
        "data_tier": "derived",
    }
