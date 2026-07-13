"""Generates the agent-first static API (site/api/v1/) from the already-committed
site/data/* contract files — no network, no pipeline/raw/, no recomputation.

This is Phase 1 of a small, separate namespace of JSON files sized for LLM
agents: fewer, smaller, more self-describing files than the human site's
site/data/ contract, each fetchable and citable on its own. The design goal is
a cold agent going from "never seen this site" to a cited answer in <=3
fetches of <API_SIZE_BUDGET_BYTES each — see index.json's fetch_recipes.

Every emitted file opens with an `_meta` envelope (see `_envelope`) carrying
generated_at/provenance copied verbatim from site/data/meta.json (never a
fresh timestamp — deterministic rebuilds, honest provenance), plus license,
attribution, and a data_tier. Deliberately OMITTED from the envelope in Phase
1: `schema` (added in Phase 4, once JSON Schemas exist to point at) and
`docs`/llms.txt (Phase 5) — publishing a URL that 404s is worse than omitting
the key.

Synthetic data (the human site's obstruction map layer, provenance "mock") is
excluded from this namespace entirely; index.json's `no_synthetic_data`
statement makes that explicit so agents don't go looking for it.

Usage: python emit_api.py
"""
import argparse
import json

from config import (API_SIZE_BUDGET_BYTES, API_VERSION, CONTRACT_VERSION,
                    CRASH_START_DATE, SITE_API_DIR, SITE_BASE_URL, SITE_DATA_DIR)
from socrata import write_json

API_BASE_URL = f"{SITE_BASE_URL}/api/v1"

LICENSE = ("City of Chicago Data Portal Terms of Use (data.cityofchicago.org); "
          "derived analyses by On Your Left!")
ATTRIBUTION = ("On Your Left! — Chicago bike safety, on the record "
              "(https://github.com/jartinator/chicago-safe-streets-data)")

# Phase 1 publishes exactly these two data endpoints (plus index.json itself,
# which isn't self-listed). Hand-maintained: description/example_questions
# are editorial, not derivable from the source data.
_PHASE1_ENDPOINTS = [
    {
        "path": "citywide.json",
        "description": ("Citywide monthly cyclist crash trend, headline findings, "
                        "and bikeway mileage / protected-share stats."),
        "example_questions": [
            "How many cyclists were killed or seriously injured in Chicago recently?",
            "Is cyclist crash frequency in Chicago trending up or down?",
            "What share of Chicago's on-street bikeway network is protected?",
        ],
    },
    {
        "path": "corridors.json",
        "description": ("Per-street corridor crash rates and bikeway facility mix, "
                        "plus labeled crash hotspot intersections."),
        "example_questions": [
            "Which Chicago streets have the highest cyclist crash rate per km?",
            "Where are Chicago's worst cyclist crash hotspot intersections?",
        ],
    },
]


def _envelope(meta, data_tier, human_page, tier_note=None):
    """Build the `_meta` object every emitted API file opens with.

    generated_at/provenance are copied verbatim from site/data/meta.json — see
    the module docstring. tier_note is included only when data_tier == "mixed".
    """
    envelope = {
        "api_version": API_VERSION,
        "contract_version": CONTRACT_VERSION,
        "generated_at": meta["generated_at"],
        "provenance": meta["provenance"],
        "data_tier": data_tier,
    }
    if tier_note is not None:
        envelope["tier_note"] = tier_note
    envelope["license"] = LICENSE
    envelope["attribution"] = ATTRIBUTION
    envelope["human_page"] = human_page
    return envelope


def build_citywide(meta, citywide_trend, findings, mileage_series):
    """citywide.json: trend + findings + bikeway mileage, plus a derived
    protected_share convenience block computed from the latest mileage
    snapshot. Findings pass through verbatim except `map_state`, which is
    UI-only map routing state, meaningless to an agent.
    """
    stripped_findings = [{k: v for k, v in f.items() if k != "map_state"}
                         for f in findings]

    payload = {
        "trend": citywide_trend,
        "findings": stripped_findings,
        "bikeway_mileage": mileage_series,
    }

    series = mileage_series.get("series") or []
    if series:
        latest = series[-1]
        total = latest["total"]
        protected = latest["by_category"].get("protected", 0)
        payload["protected_share"] = {
            "as_of": latest["date"],
            "protected_miles": protected,
            "total_miles": total,
            "pct_protected": round(100 * protected / total, 1),
            "data_tier": "derived",
            "note": ("Protected share of on-street bikeway miles; excludes "
                    "off-street trails."),
        }

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("trend is real; findings each carry their own data_tier; "
                  "bikeway_mileage and protected_share are derived."),
        human_page=f"{SITE_BASE_URL}/findings.html")

    return {"_meta": envelope, **payload}


def build_corridors_api(meta, corridors, intersections):
    """corridors.json: the committed corridor table plus hotspot intersections,
    both passed through as-is — both sources are tier "real".
    """
    envelope = _envelope(meta, data_tier="real",
                         human_page=f"{SITE_BASE_URL}/index.html")
    return {"_meta": envelope, "corridors": corridors,
           "hotspot_intersections": intersections}


def build_index(meta, endpoint_bytes):
    """index.json: the discovery entry point. Hand-assembled manifest listing
    only the endpoints that actually exist in Phase 1.

    endpoint_bytes: {path: actual on-disk byte size}, supplied by emit_all
    after writing citywide.json/corridors.json (index.json is written last so
    its bytes_approx values are real, not estimated).
    """
    endpoints = [
        {
            "path": ep["path"],
            "url": f"{API_BASE_URL}/{ep['path']}",
            "bytes_approx": endpoint_bytes[ep["path"]],
            "description": ep["description"],
            "example_questions": ep["example_questions"],
        }
        for ep in _PHASE1_ENDPOINTS
    ]

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("this index has no single data tier — each endpoint declares "
                  "its own data_tier(s) in its own _meta envelope and payload "
                  "sections; see the endpoint list below."),
        human_page=f"{SITE_BASE_URL}/index.html")

    fetch_recipes = [
        {
            "question": "Are cyclist crashes in Chicago getting worse?",
            "fetch": [f"{API_BASE_URL}/citywide.json"],
            "then": ("Read trend.months for the monthly series and findings for "
                    "the headline killed-or-seriously-injured comparison."),
        },
        {
            "question": "What's the most dangerous street corridor for cyclists?",
            "fetch": [f"{API_BASE_URL}/corridors.json"],
            "then": "Sort corridors by crashes_per_km descending.",
        },
        {
            "question": ("How protected is Chicago's bike network, and where are "
                        "the crash hotspots?"),
            "fetch": [f"{API_BASE_URL}/citywide.json", f"{API_BASE_URL}/corridors.json"],
            "then": ("Take protected_share from citywide.json and "
                    "hotspot_intersections from corridors.json."),
        },
    ]

    return {
        "_meta": envelope,
        "title": "On Your Left! — Chicago bike safety, on the record",
        "description": (
            "Police-reported cyclist crash data, bikeway network quality, and "
            "City Council accountability for Chicago, rebuilt weekly from the "
            "Chicago Data Portal and other public sources."),
        "endpoints": endpoints,
        "fetch_recipes": fetch_recipes,
        "coverage_note": (
            f"Crash data is citywide-reliable only from {CRASH_START_DATE}; counts "
            "are raw, not ridership-normalized; recent months are provisional "
            "(records get amended)."),
        "no_synthetic_data": (
            "There is NO obstruction data in this API. The human site's "
            "obstruction map layer is synthetic mock data shown for UI preview "
            "purposes only, has no api/v1 endpoint, and must never be cited as "
            "real."),
        "planned": [
            "wards/ — per-ward danger scores and crash breakdowns (not yet published)",
            "crashes/ — individual crash records (not yet published)",
            "routes/ — main-route and network-map detail (not yet published)",
            "council/ — City Council safety-legislation tracking (not yet published)",
            "schemas/ — machine-readable JSON Schemas for these endpoints (not yet published)",
        ],
    }


def _load(name):
    return json.loads((SITE_DATA_DIR / name).read_text())


def _enforce_budget(written):
    """Hard-fail if any emitted file exceeds API_SIZE_BUDGET_BYTES — that
    budget is the whole point of this being an agent-sized API, not a mirror
    of site/data/.
    """
    for path, size in written.items():
        if size > API_SIZE_BUDGET_BYTES:
            raise SystemExit(
                f"emit_api: {path} is {size:,} bytes, over the "
                f"API_SIZE_BUDGET_BYTES budget of {API_SIZE_BUDGET_BYTES:,} bytes")


def _print_size_table(written):
    """One line per emitted file, aligned — mirrors run_all.print_timings."""
    width = max(len(path) for path in written)
    print("\n=== site/api/v1 sizes ===")
    for path, size in written.items():
        print(f"  {path:<{width}}  {size:7,d} bytes")


def _prune_stale(written_paths):
    """Delete any file under SITE_API_DIR this run didn't just write (e.g. a
    retired/renamed endpoint), except anything under schemas/ (hand-written,
    Phase 4), then remove any subdirectories left empty by that pruning.
    Implemented generically because later phases write nested paths like
    wards/ward-NN.json, not just Phase 1's three top-level files.
    """
    if not SITE_API_DIR.exists():
        return
    schemas_dir = SITE_API_DIR / "schemas"

    for path in SITE_API_DIR.rglob("*"):
        if not path.is_file():
            continue
        if schemas_dir in path.parents:
            continue
        rel = path.relative_to(SITE_API_DIR).as_posix()
        if rel not in written_paths:
            path.unlink()

    dirs = sorted((p for p in SITE_API_DIR.rglob("*") if p.is_dir()),
                 key=lambda p: len(p.parts), reverse=True)
    for d in dirs:
        if d == schemas_dir or schemas_dir in d.parents:
            continue
        try:
            d.rmdir()
        except OSError:
            pass  # not empty (or already gone) — leave it


def emit_all():
    """Load committed site/data/*, build the three Phase-1 API files, write
    them into SITE_API_DIR, enforce the size budget, print a size table, and
    prune stale output. Returns {relative path: byte size} for the files
    written this run.
    """
    meta = _load("meta.json")
    citywide_trend = _load("citywide_trend.json")
    findings = _load("findings.json")
    mileage_series = _load("bikeway_mileage_series.json")
    corridors = _load("corridors.json")
    intersections = _load("intersections.json")

    written = {}

    citywide = build_citywide(meta, citywide_trend, findings, mileage_series)
    write_json(SITE_API_DIR / "citywide.json", citywide)
    written["citywide.json"] = (SITE_API_DIR / "citywide.json").stat().st_size

    corridors_api = build_corridors_api(meta, corridors, intersections)
    write_json(SITE_API_DIR / "corridors.json", corridors_api)
    written["corridors.json"] = (SITE_API_DIR / "corridors.json").stat().st_size

    index = build_index(meta, written)
    write_json(SITE_API_DIR / "index.json", index)
    written["index.json"] = (SITE_API_DIR / "index.json").stat().st_size

    _enforce_budget(written)
    _print_size_table(written)
    _prune_stale(set(written))

    return written


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    emit_all()


if __name__ == "__main__":
    main()
