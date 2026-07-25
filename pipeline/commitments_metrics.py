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

**2. Buffered lanes are not low-stress here.** `config.LOW_STRESS_CATEGORIES` is derived
from the main-route grade map, which has called buffered lanes "paint" since the
network-tiers work — paint and signs put nothing between a rider and traffic. That
resolves to protected + greenway + trail, which is also exactly CDOT's own definition,
so the pledge and the network are scored on one consistent basis rather than two.

Pure functions over already-parsed dicts — no I/O, no network — so this stays
testable and safe to call from aggregate.py once the inputs are loaded.
"""
from config import LOW_STRESS_CATEGORIES, ON_STREET_CATEGORIES

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
        low_stress_new += sum(cats.get(c, 0.0) for c in LOW_STRESS_CATEGORIES)

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
            f"miles ({low_stress_share}%) are low-stress: protected lanes and "
            f"neighborhood greenways. Buffered and painted lanes and sharrows are not — "
            f"they put paint and signs between a rider and traffic, nothing more. "
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
            f"low-stress; counting only genuinely new miles, "
            f"{ledger['low_stress_share_new_basis']}%. Source: {source}; installation figures "
            f"from {FOIA_REFERENCE}."
        )
        caveat = (
            "Both figures come from CDOT's own Complete Streets dashboard, so the gap is a "
            "counting difference, not a dispute about the underlying miles. The pledge says "
            "\"new bikeways,\" which is why the headline excludes the "
            f"{ledger['concrete_upgrade_miles']:,.1f} miles of concrete upgrades; CDOT's larger "
            "number is shown alongside so both countings are visible. Low-stress here means "
            "protected lanes, neighborhood greenways, and off-street trails — buffered and "
            "painted lanes and sharrows are excluded, the same way this site's network map "
            "grades them, and the same way CDOT's own dashboard counts them. The pledge carries "
            "no published deadline, so this is progress-to-date, not a verdict on whether CDOT "
            "will meet it."
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


# --- the ledger: score every roster entry against CDOT's own figures -----------------
#
# Added once FOIA S145367-071326 made delivery measurable. The roster spans
# administrations on purpose: the lens is the bikeway network, not who was in office,
# and a pledge is scored the same way regardless of who made it.

def _network(history):
    return {p["year"]: p["by_category"] for p in
            ((history or {}).get("annual") or {}).get("network") or []}


def _installed(history):
    return {p["year"]: p for p in
            ((history or {}).get("annual") or {}).get("installed") or []}


def _reported_installed(history):
    return (((history or {}).get("annual") or {}).get("cdot_reported_totals")
            or {}).get("installed_on_street") or {}


def _sum_cats(by_cat, categories):
    """Sum the named categories, or every on-street category when none are named."""
    if categories:
        return round(sum(by_cat.get(c, 0.0) for c in categories), 2)
    return round(sum(v for k, v in by_cat.items() if k in ON_STREET_CATEGORIES), 2)


def _measure(commitment, history, categories):
    """(actual_miles, window_label) for one reading of a commitment, or (None, reason)."""
    basis = commitment.get("basis")
    net, inst, rep = _network(history), _installed(history), _reported_installed(history)
    years = sorted(net)
    if not years:
        return None, "no history available"
    target = commitment.get("target_year") or years[-1]
    baseline = commitment.get("baseline_year")

    if basis == "network_state":
        if target not in net:
            return None, "no figures for %s" % target
        return _sum_cats(net[target], categories), "as of %s" % target

    if basis == "network_delta":
        if target not in net or baseline not in net:
            return None, "no figures for %s/%s" % (baseline, target)
        delta = _sum_cats(net[target], categories) - _sum_cats(net[baseline], categories)
        return round(delta, 2), "%s to %s" % (baseline, target)

    if basis == "miles_added":
        total = 0.0
        for year in years:
            if baseline is not None and year <= baseline:
                continue
            if year > target:
                continue
            point = inst.get(year)
            if not point:
                continue
            if categories:
                total += _sum_cats(point.get("by_category") or {}, categories)
            else:
                # CDOT's own on-street installed total, minus the concrete upgrades it
                # folds in (they add no new mileage - see DECISIONS.md #36).
                total += rep.get(str(year), 0.0) - point.get("protected_concrete_upgrade", 0.0)
        lo = (baseline + 1) if baseline is not None else years[0]
        return round(total, 2), "%s to %s" % (lo, target)

    return None, "not scored on this basis"


def score_commitment(commitment, history):
    """One roster entry -> a scored ledger row. Never invents a number it cannot compute."""
    row = {
        "id": commitment.get("id"),
        "text": commitment.get("text"),
        "claim_quote": commitment.get("claim_quote"),
        "target": commitment.get("number"),
        "unit": commitment.get("unit"),
        "year_committed": commitment.get("year_committed"),
        "deadline": commitment.get("deadline"),
        "basis": commitment.get("basis"),
        "categories": commitment.get("categories"),
        "source_name": commitment.get("source_name"),
        "source_record": commitment.get("source_record"),
        "citations": commitment.get("citations"),
        "data_tier": "derived",
    }
    basis = commitment.get("basis")

    if basis in (None, "not_measurable"):
        row.update({"measurable": False,
                    "reason": commitment.get("not_measurable_reason",
                                             "No basis defined for scoring this commitment.")})
        return row

    if basis == "low_stress_share":
        ledger = delivered_since(history, (commitment.get("baseline_year") or 0) + 1)
        if not ledger:
            row.update({"measurable": False, "reason": "CDOT install history unavailable."})
            return row
        target = commitment.get("number")
        row.update({"measurable": True,
                    "actual": ledger["low_stress_share_new_basis"],
                    "actual_as_claimed": ledger["low_stress_share_cdot_basis"],
                    "window": "%s to %s" % (ledger["since_year"], ledger["through_year"]),
                    "pct_of_target": round(100 * ledger["low_stress_share_new_basis"] / target)
                                     if target else None,
                    "met": bool(target) and ledger["low_stress_share_new_basis"] >= target,
                    "as_claimed_met": bool(target) and ledger["low_stress_share_cdot_basis"] >= target})
        return row

    actual, window = _measure(commitment, history, commitment.get("categories"))
    if actual is None:
        row.update({"measurable": False, "reason": window})
        return row

    target = commitment.get("number")
    row.update({"measurable": True, "actual": actual, "window": window,
                "pct_of_target": round(100 * actual / target) if target else None,
                "met": bool(target) and actual >= target})

    alt = commitment.get("alt_categories")
    if alt:
        alt_actual, _ = _measure(commitment, history, alt)
        if alt_actual is not None:
            row["actual_as_claimed"] = alt_actual
            row["as_claimed_categories"] = alt
            row["as_claimed_met"] = bool(target) and alt_actual >= target
            row["alt_note"] = commitment.get("alt_note")
    return row


def build_commitments_ledger(commitments_doc, history_doc):
    """Every roster commitment scored against CDOT's own figures, oldest first."""
    commitments = (commitments_doc or {}).get("commitments") or []
    if not commitments:
        return None
    rows = [score_commitment(c, history_doc) for c in commitments]
    rows.sort(key=lambda r: (r.get("year_committed") or 0, r.get("id") or ""))
    scored = [r for r in rows if r.get("measurable")]
    return {
        "data_tier": "derived",
        "note": (
            "Chicago's published bikeway commitments scored against CDOT's own year-by-year "
            "figures (FOIA S145367-071326). Both sides of every comparison are the City's own "
            "data. The roster spans administrations deliberately - the lens is the bikeway "
            "network, not who was in office, and every pledge is scored the same way. `basis` "
            "says how each was measured; `actual_as_claimed` appears where a claim is only "
            "reachable under a more generous reading of which facilities count, and both "
            "numbers are published rather than one being chosen. Commitments with "
            "measurable=false are listed with a reason and never given a number."
        ),
        "source": "CDOT FOIA S145367-071326, released 2026-07-24",
        "commitments": rows,
        "scored": len(scored),
        "met": sum(1 for r in scored if r.get("met")),
    }
