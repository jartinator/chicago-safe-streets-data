"""Shape the raw PeopleForBikes BNA pull into published site data + the finding.

Pure functions over the raw/bna.json dict written by pull_bna.py — no I/O, no
geo dependencies — so the copy rules from the validation verdict
(docs/research/user-needs/validation/pfb-bna/VERDICT.md, B1) are testable:
context on the national average, reconciliation against our own crash data,
anti-discouragement + OSM-currency language in the caveat.
"""
from datetime import datetime

from caveats import finding_tags
from config import BNA_LARGE_CITY_MIN_POPULATION

# The verdict's master caveat: OSM-derived, uneven volunteer mapping — this
# travels with the data file itself, not just the UI (P4 traveling provenance).
OSM_CURRENCY_NOTE = (
    "Computed by PeopleForBikes from OpenStreetMap — only as current as "
    "volunteer mapping, which is uneven across neighborhoods; it can understate "
    "what a neighborhood has, or miss hazards nobody mapped. PFB's scoring "
    "methodology has changed over the years (notably 2020 and 2026), so history "
    "entries are not comparable across distant analysis versions."
)

# The trend sentence only compares analyses within this many years of the
# latest one: PFB's methodology shifts (2017-19 scores in the 30s became
# single digits after the 2020 rescoring) make older scores incomparable.
TREND_COMPARABLE_YEARS = 2


def _category_score(latest, name):
    cat = latest.get(name) or {}
    val = cat.get("score", cat.get(name))
    return val


def build_bna_scores(raw):
    """raw/bna.json -> site/data/bna_scores.json content."""
    latest = raw["latest"]
    history = sorted(raw.get("history") or [],
                     key=lambda r: r.get("created_at") or "")
    infra = latest.get("infrastructure") or {}

    subscores = {}
    for name in ("people", "opportunity", "core_services",
                 "recreation", "retail", "transit"):
        val = _category_score(latest, name)
        if val is not None:
            subscores[name] = val

    cities = raw.get("cities_index") or []
    scored = [c for c in cities if c.get("score") is not None]
    large = [c for c in scored
             if (c.get("population") or 0) >= BNA_LARGE_CITY_MIN_POPULATION]
    large_sorted = sorted(large, key=lambda c: -c["score"])
    city_id = (raw.get("city") or {}).get("id")
    large_rank = next((i + 1 for i, c in enumerate(large_sorted)
                       if c.get("id") == city_id), None)

    return {
        "data_tier": "crowdsourced",
        "as_of": (history[-1].get("created_at") or "")[:10],
        "version": latest.get("version"),
        "score": latest.get("score"),
        "subscores": subscores,
        "low_stress_miles": infra.get("low_stress_miles"),
        "high_stress_miles": infra.get("high_stress_miles"),
        "history": [{"version": h.get("version"), "score": h.get("score"),
                     "as_of": (h.get("created_at") or "")[:10]} for h in history],
        "context": {
            "cities_rated": len(scored),
            "mean_score": round(sum(c["score"] for c in scored) / len(scored), 1)
                          if scored else None,
            "large_city_count": len(large_sorted),
            "large_city_rank": large_rank,
            "large_city_min_population": BNA_LARGE_CITY_MIN_POPULATION,
        },
        "note": OSM_CURRENCY_NOTE,
    }


def build_bna_finding(scores):
    """bna_scores dict -> one findings.json card (verdict B1 copy rules)."""
    score_int = round(scores["score"])
    ctx = scores.get("context") or {}
    mean = ctx.get("mean_score")
    high = scores.get("high_stress_miles")
    low = scores.get("low_stress_miles")
    as_of = scores.get("as_of") or ""
    month_year = (datetime.strptime(as_of, "%Y-%m-%d").strftime("%B %Y")
                  if as_of else "")

    history = scores.get("history") or []
    trend = ""
    latest_year = int(as_of[:4]) if as_of else None
    if latest_year:
        comparable = [h for h in history
                      if h.get("as_of")
                      and latest_year - TREND_COMPARABLE_YEARS
                          <= int(h["as_of"][:4]) < latest_year]
        if comparable:
            base = comparable[0]  # history is ascending — earliest comparable
            direction = "up slightly from" if scores["score"] >= base["score"] \
                        else "down from"
            trend = (f" That's {direction} {round(base['score'])} in "
                     f"{base['as_of'][:4]}.")

    mean_part = (f" The average rated U.S. city scores {round(mean)}."
                 if mean is not None else "")
    rank = ctx.get("large_city_rank")
    count = ctx.get("large_city_count")
    if rank and count:
        place = "last" if rank == count else f"{rank}th"
        mean_part += (f" Among the {count} rated U.S. cities over "
                      f"{ctx.get('large_city_min_population', 300000):,} people, "
                      f"Chicago ranks {place}.")
    miles_part = ""
    if high is not None and low is not None:
        miles_part = (f" Behind the number: {high:,.0f} miles of high-stress "
                      f"streets versus {low:,.0f} low-stress.")

    description = (
        f"PeopleForBikes' Bicycle Network Analysis scores how much of Chicago "
        f"a person can reach on low-stress streets — and gives the city "
        f"{scores['score']} out of 100.{mean_part}{miles_part}{trend} "
        f"This grades the network, not crashes: it can move independently of "
        f"any crash trend, because it measures what's built, not what happened."
    )
    caveat = (
        f"Third-party score, analysis {scores.get('version')}"
        + (f" ({month_year})" if month_year else "") + ". "
        + scores.get("note", OSM_CURRENCY_NOTE) + " "
        "It grades the street network, not the people riding it — a low score "
        "is a case for building more, not a reason not to ride."
    )
    return {
        "id": "bna-score",
        "title": "How Chicago's bike network scores nationally",
        "stat": f"{score_int}/100",
        "description": description,
        "caveat": caveat,
        # Canonical table, 02-architecture.md §1.5: third_party_method for PFB's
        # changing methodology, coverage_gap for the uneven OSM base. Both facts
        # are already in the caveat prose above.
        "caveat_tags": finding_tags("bna-score"),
        "map_state": {"screen": "map", "layers": ["mainroutes"], "filters": {}},
        "data_tier": "crowdsourced",
    }
