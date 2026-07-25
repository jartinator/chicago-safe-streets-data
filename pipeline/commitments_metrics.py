"""Pair the curated bikeway-commitments roster (data/commitments.json) against what
CDOT actually delivered, for the "promise vs. delivered" finding — user-needs P5.

Until 2026-07-24 this could only compare a pledge to a current network snapshot,
because the public Bike Routes layer carries no install date. FOIA S145367-071326
changed that: CDOT released its own Complete Streets dashboard, which reports miles
installed per year by facility type. `data/cdot_bikeway_history.json` carries those
figures, so delivery since the 2023 commitment is now directly measurable.

Two definitional traps live here, and both are stated in the finding's own text so
they travel with the data rather than only with this file.

**1. CDOT counts concrete upgrades of existing protected lanes inside "miles
installed."** Over 2023-2025 that is 22.04 of 125.89 miles. The pledge says *new*
bikeways, so the headline figure excludes upgrades; CDOT's own larger number is
published beside it rather than suppressed.

**2. CDOT does not count buffered lanes as low-stress.** Its dashboard's low-stress
row is protected + greenway + off-street only (config.CDOT_LOW_STRESS_CATEGORIES).
OYL's own network-level definition below is broader and does count buffered. The 80%
pledge is CDOT's, so it is scored on CDOT's definition; the network-level description
uses OYL's. Mixing them would be the easy mistake, so each number says which it uses.

Pure functions over already-parsed dicts — no I/O, no network — so this stays
testable and safe to call from aggregate.py once the inputs are loaded.
"""
from config import CDOT_LOW_STRESS_CATEGORIES

# OYL's network-level low-stress definition. Broader than CDOT's: it counts buffered
# lanes. Used to describe the network as it stands, never to score CDOT's pledge.
LOW_STRESS_CATEGORIES = ("protected", "buffered", "greenway", "trail")

HEADLINE_COMMITMENT_ID = "150-new-miles"
LOW_STRESS_COMMITMENT_ID = "80-percent-low-stress"

FOIA_REFERENCE = "CDOT FOIA S145367-071326, released 2026-07-24"


def _by_id(commitments, wanted):
    for c in commitments:
        if c.get("id") == wanted:
            return c
    return None


def _headline(commitments):
    return _by_id(commitments, HEADLINE_COMMITMENT_ID) or (commitments[0] if commitments else None)


def delivered_since(history_doc, start_year):
    """Miles installed from `start_year` onward, on both counting bases.

    Returns None when the released history isn't available, so callers can fall back
    to the older snapshot-only framing instead of publishing a hole.
    """
    installed = ((history_doc or {}).get("annual") or {}).get("installed") or []
    reported = (((history_doc or {}).get("annual") or {}).get("cdot_reported_totals")
                or {}).get("installed_on_street") or {}
    years = [p for p in installed if p.get("year", 0) >= start_year]
    if not years or not reported:
        return None

    cdot_counted = new_only = upgrades = 0.0
    low_stress_new = 0.0
    for point in years:
        year = str(point["year"])
        if year not in reported:
            continue
        upgrade = point.get("protected_concrete_upgrade", 0.0)
        cats = point.get("by_category") or {}
        cdot_counted += reported[year]
        upgrades += upgrade
        new_only += reported[year] - upgrade
        low_stress_new += sum(cats.get(c, 0.0) for c in CDOT_LOW_STRESS_CATEGORIES)

    if not cdot_counted:
        return None

    # CDOT counts its concrete upgrades as low-stress too (they are protected lanes),
    # so its own share uses the upgrade-inclusive numerator AND denominator.
    low_stress_cdot = low_stress_new + upgrades
    return {
        "since_year": start_year,
        "through_year": max(p["year"] for p in years),
        "cdot_counted_miles": round(cdot_counted, 2),
        "concrete_upgrade_miles": round(upgrades, 2),
        "new_miles": round(new_only, 2),
        "low_stress_share_new_basis": round(100 * low_stress_new / new_only, 1) if new_only else None,
        "low_stress_share_cdot_basis": round(100 * low_stress_cdot / cdot_counted, 1),
    }


def build_commitments_finding(commitments_doc, bikeway_series, history_doc=None):
    """-> one findings.json card, or None if the roster or series is empty."""
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

    ledger = delivered_since(history_doc, year) if year else None

    if not ledger:
        # Pre-FOIA framing, kept as an honest fallback for environments without the
        # released history (a fixtures run, or a fork that hasn't pulled it).
        description = (
            f"CDOT's {year} Chicago Cycling Strategy commits to {number} {unit} of "
            f"new bikeways, 80% of them low-stress. As of {as_of}, Chicago's on-street "
            f"bikeway network totals {total:,.0f} miles, of which {low_stress:,.0f} "
            f"miles ({low_stress_share}%) are low-stress by OYL's count (protected, "
            f"buffered, greenways, trails; painted lanes and sharrows are not). "
            f"Source: {source}."
        )
        caveat = ("This pairs the published commitment against the current network snapshot, "
                  "not against what has been delivered since the commitment — CDOT's released "
                  "install-date history is not available in this environment.")
        stat = f"{number} new {unit}"
    else:
        pct_new = round(100 * ledger["new_miles"] / number) if number else None
        pct_cdot = round(100 * ledger["cdot_counted_miles"] / number) if number else None
        span = (f"{ledger['since_year']}" if ledger["since_year"] == ledger["through_year"]
                else f"{ledger['since_year']}–{ledger['through_year']}")
        description = (
            f"CDOT's {year} Chicago Cycling Strategy commits to {number} {unit} of new "
            f"bikeways, 80% of them low-stress. Using CDOT's own year-by-year installation "
            f"figures ({span}), the city has built {ledger['new_miles']:,.1f} miles of "
            f"genuinely new bikeway — {pct_new}% of the pledge. CDOT itself reports "
            f"{ledger['cdot_counted_miles']:,.1f} miles ({pct_cdot}%) toward the same goal, "
            f"but {ledger['concrete_upgrade_miles']:,.1f} of those miles are concrete upgrades "
            f"to protected lanes that already existed, not new bikeway. On the low-stress "
            f"pledge, {ledger['low_stress_share_cdot_basis']}% of the miles CDOT counts are "
            f"low-stress by CDOT's definition; counting only genuinely new miles, "
            f"{ledger['low_stress_share_new_basis']}%. Source: {source}; installation figures "
            f"from {FOIA_REFERENCE}."
        )
        caveat = (
            "Both figures come from CDOT's own Complete Streets dashboard, so the gap is a "
            "counting difference, not a dispute about the underlying miles. The pledge says "
            "\"new bikeways,\" which is why the headline excludes the "
            f"{ledger['concrete_upgrade_miles']:,.1f} miles of concrete upgrades; CDOT's larger "
            "number is shown alongside so both countings are visible. The low-stress shares use "
            "CDOT's definition (protected lanes, neighborhood greenways, off-street) because the "
            "pledge is CDOT's — note that CDOT does not count buffered lanes as low-stress, "
            "while OYL's network-level figures elsewhere on this site do. The pledge carries no "
            "published deadline, so this is progress-to-date, not a verdict on whether CDOT will "
            "meet it."
        )
        stat = f"{ledger['new_miles']:,.1f} of {number} new {unit}"

    return {
        "id": "commitments-vs-delivered",
        "title": "Promised bikeway miles vs. what got built",
        "stat": stat,
        "description": description,
        "caveat": caveat,
        "map_state": {"screen": "table", "layers": [], "filters": {}},
        "data_tier": "derived",
    }
