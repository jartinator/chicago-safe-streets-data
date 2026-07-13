"""Generate the agent-first static API (site/api/v1/) from committed site/data/ files.

No network, no pipeline/raw/, no recomputation — this module reads only the
already-committed site/data/* contract files.

This is a small, separate namespace of JSON files sized for LLM agents: fewer,
smaller, more self-describing files than the human site's site/data/
contract, each fetchable and citable on its own. The design goal is a cold
agent going from "never seen this site" to a cited answer in <=3 fetches of
<API_SIZE_BUDGET_BYTES each — see index.json's fetch_recipes. Phase 1 (index/
citywide/corridors) and Phase 2 (the per-ward layer: wards/index.json +
wards/ward-NN.json) are built here; see
docs/superpowers/plans/2026-07-13-agent-api-layer.md for the full phasing.

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

Phase 2 covers the per-ward layer: wards/index.json, wards/ward-NN.json (both
built from site/data/ward_safety_index.json etc.), and crashes/ward-NN.json
(built from site/data/crashes_cyclist.geojson) — columnar per-ward crash rows,
the one family allowed a bigger byte budget (API_CRASH_SLICE_BUDGET_BYTES).

Usage: python emit_api.py
"""
import argparse
import json
from collections import Counter, defaultdict

from config import (API_CRASH_SLICE_BUDGET_BYTES, API_SIZE_BUDGET_BYTES, API_VERSION,
                    CONTRACT_VERSION, CRASH_ID_PREFIX_LEN, CRASH_START_DATE, SITE_API_DIR,
                    SITE_BASE_URL, SITE_DATA_DIR)
from socrata import write_json

API_BASE_URL = f"{SITE_BASE_URL}/api/v1"

LICENSE = ("City of Chicago Data Portal Terms of Use (data.cityofchicago.org); "
          "derived analyses by On Your Left!")
ATTRIBUTION = ("On Your Left! — Chicago bike safety, on the record "
              "(https://github.com/jartinator/chicago-safe-streets-data)")

# The canonical description of comparable_danger_score, verbatim wherever the
# API describes that field (wards/index.json's note, each ward file's
# score_note, and index.json's ward fetch recipe) — see
# docs/superpowers/plans/2026-07-13-agent-api-layer.md §1 "Naming". The field
# name itself is contract and stays; only this description string is shared.
COMPARABLE_DANGER_SCORE_DESC = "relative concern rank among wards, higher = worse — not absolute risk"

# Concrete, always-present data endpoints (plus index.json itself, which
# isn't self-listed). Hand-maintained: description/example_questions are
# editorial, not derivable from the source data. Distinct from the *family*
# entries in build_index (wards/ward-NN.json etc.) — a family is 50 files
# sharing one template, too many to hand-list here.
_ENDPOINTS = [
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
    {
        "path": "wards/index.json",
        "description": ("All 50 Chicago wards' comparable danger scores, crash "
                        "counts, and bikeway stats in one file, ranked, with "
                        "links to each ward's full detail file."),
        "example_questions": [
            "Which Chicago ward is most dangerous for cyclists?",
            "How does my ward's bikeway mileage compare to other wards?",
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

    # Guard: omit protected_share entirely (never emit nulls or divide by
    # zero) when there's no usable latest snapshot — empty series or total 0.
    series = mileage_series.get("series") or []
    if series and series[-1]["total"]:
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


def build_wards_index(meta, ward_safety_index):
    """wards/index.json: all 50 ward_safety_index records verbatim, minus
    their `monthly` series (107 months each — too big for an index; an agent
    that wants a ward's month-by-month history fetches wards/ward-NN.json via
    the detail_url added here). Everything else (windows, trends,
    comparable_danger_score, ...) is kept as-is. Source order is already a
    meaningful ranking (see the source file's own note) and is preserved,
    never re-sorted here.
    """
    wards = []
    for w in ward_safety_index["wards"]:
        padded = w["ward"].zfill(2)
        entry = {k: v for k, v in w.items() if k != "monthly"}
        entry["detail_url"] = f"{API_BASE_URL}/wards/ward-{padded}.json"
        entry["crashes_url"] = f"{API_BASE_URL}/crashes/ward-{padded}.json"
        wards.append(entry)

    note = (f"{ward_safety_index['note']} comparable_danger_score is a "
           f"{COMPARABLE_DANGER_SCORE_DESC}.")

    envelope = _envelope(meta, data_tier="derived",
                         human_page=f"{SITE_BASE_URL}/table.html")

    return {
        "_meta": envelope,
        "data_tier": ward_safety_index["data_tier"],
        "note": note,
        "wards": wards,
    }


def build_ward_file(meta, ward_record, aldermen, safety_record, menu_spending, sr311):
    """wards/ward-NN.json: one ward's full safety record (including
    `monthly`), alderman contact info, council safety-sponsorship record, and
    311/menu-spending proxies, plus link-outs. `aldermen`, `safety_record`,
    `menu_spending`, `sr311` are the whole loaded site/data/*.json dicts (not
    pre-filtered per ward) — this function does its own per-ward lookup so
    emit_all's loop just calls it once per ward_safety_index record.

    Deliberate plan deviation (see task brief / DECISIONS.md): no "top
    corridors for this ward" section. corridors.json carries no ward id or
    geometry, so computing that here would mean inventing a linkage the
    source data doesn't have. `see_also.corridors` points agents at the
    citywide corridors endpoint instead.
    """
    ward = ward_record["ward"]
    padded = ward.zfill(2)

    alderman_entry = next((a for a in aldermen["wards"] if a["ward"] == ward), None)
    alderman_note = None
    if alderman_entry is not None:
        alderman = {**alderman_entry, "as_of": aldermen["as_of"], "source": aldermen["source"],
                   "data_tier": aldermen["data_tier"], "lookup_url": aldermen["lookup_url"]}
    else:
        alderman = None
        alderman_note = f"No aldermen.json roster entry found for ward {ward}."

    safety_record_entries = [a for a in safety_record["aldermen"] if a["ward"] == ward]

    if ward in menu_spending["wards"]:
        menu = {**menu_spending["wards"][ward], "data_tier": menu_spending["data_tier"],
               "note": menu_spending["note"]}
    else:
        # Never fabricate zeros: absence is a data gap, not "no spending".
        menu = {"available": False, "data_tier": menu_spending["data_tier"],
               "note": menu_spending["note"]}

    sr311_entry = next((w for w in sr311["wards"] if w["ward"] == ward), None)
    if sr311_entry is not None:
        sr311_out = {**sr311_entry, "data_tier": sr311["data_tier"], "note": sr311["note"]}
    else:
        sr311_out = {"available": False, "data_tier": sr311["data_tier"], "note": sr311["note"]}

    one_pager_url = f"{SITE_BASE_URL}/ward.html?ward={ward}"

    payload = {
        "ward": ward,
        "ward_padded": padded,
        "safety": {**ward_record,
                  "score_note": f"comparable_danger_score is a {COMPARABLE_DANGER_SCORE_DESC}."},
        "alderman": alderman,
        "safety_record": {"data_tier": safety_record["data_tier"], "note": safety_record["note"],
                          "entries": safety_record_entries},
        "menu_spending": menu,
        "sr311": sr311_out,
        "crashes_url": f"{API_BASE_URL}/crashes/ward-{padded}.json",
        "one_pager_url": one_pager_url,
        "see_also": {"corridors": f"{API_BASE_URL}/corridors.json",
                    "wards_index": f"{API_BASE_URL}/wards/index.json"},
    }
    if alderman_note is not None:
        payload["alderman_note"] = alderman_note

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("safety is derived; alderman is real; safety_record is derived "
                  "(council sponsorship aggregation); sr311 is proxy (self-reported "
                  "bias); menu_spending is proxy."),
        human_page=one_pager_url)

    return {"_meta": envelope, **payload}


def crash_id_prefixes(ids):
    """Map each full crash_id (128-hex-char strings) to the id emitted in
    crash slices: the leading CRASH_ID_PREFIX_LEN hex chars. Computed
    globally over `ids` — the caller passes every crash_id across all wards,
    not one ward's worth, so a prefix is unambiguous dataset-wide, not just
    ward-wide.

    If two ids in `ids` share that same prefix (astronomically unlikely
    across ~17k hex ids but not impossible), BOTH fall back to their full id
    in the returned map — a per-id fallback, not a build-wide abort, so a
    rare collision degrades one row's crash_id length instead of crashing
    the whole build. Falsy ids (a crash record with no crash_id at all) are
    skipped rather than sliced — same "don't crash the build" spirit; a
    missing crash_id is a data gap build_crash_slice reports as a null cell,
    not a builder-side crash.
    """
    real_ids = [full_id for full_id in ids if full_id]
    prefix_counts = Counter(full_id[:CRASH_ID_PREFIX_LEN] for full_id in real_ids)
    return {
        full_id: (full_id if prefix_counts[full_id[:CRASH_ID_PREFIX_LEN]] > 1
                 else full_id[:CRASH_ID_PREFIX_LEN])
        for full_id in real_ids
    }


def build_crash_slice(meta, ward, features_for_ward, id_prefix_map):
    """crashes/ward-NN.json: one ward's cyclist crash records as columnar
    rows (`{"columns": [...], "rows": [[...], ...]}`) instead of 1,000+
    individually-keyed GeoJSON features — cheaper for an agent to fetch and
    parse. Row order preserves source feature order (never re-sorted here).

    id_prefix_map (see crash_id_prefixes) supplies the emitted crash_id for
    each full id. lat/lng come from the feature's geometry `coordinates`
    ([lon, lat]) rounded to 5 decimal places — note the column order is
    lat-then-lng, the reverse of the source geometry. A missing or null
    source property becomes JSON null in its cell. Every ward gets a file
    (features_for_ward may be empty) so agents can always fetch by NN without
    a 404.

    crash_id-prefixing and coordinate-rounding are this slice's only lossy
    trims of record content (per the plan); `note` documents both, plus the
    three columns dropped entirely (crash_type, lighting, segment_id) — an
    agent wanting those fetches full_data_url instead.
    """
    columns = ["crash_id", "date", "lat", "lng", "injury_severity", "dooring",
              "hit_and_run", "street"]
    rows = []
    for feature in features_for_ward:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        full_id = props.get("crash_id")
        rows.append([
            id_prefix_map.get(full_id, full_id),
            props.get("date"),
            round(lat, 5),
            round(lon, 5),
            props.get("injury_severity"),
            props.get("dooring"),
            props.get("hit_and_run"),
            props.get("street"),
        ])

    padded = ward.zfill(2)
    note = (f"crash_id is a {CRASH_ID_PREFIX_LEN}-hex-char prefix of the full crash_id "
           "(full ids and the full field set are in site/data/crashes_cyclist.geojson, "
           "linked via full_data_url); lat/lng are rounded to 5 decimal places. "
           "Dropped columns crash_type, lighting, and segment_id are available in the "
           "full GeoJSON.")

    envelope = _envelope(meta, data_tier="real", human_page=f"{SITE_BASE_URL}/index.html")

    return {
        "_meta": envelope,
        "ward": ward,
        "ward_url": f"{API_BASE_URL}/wards/ward-{padded}.json",
        "columns": columns,
        "rows": rows,
        "count": len(rows),
        "note": note,
        "full_data_url": f"{SITE_BASE_URL}/data/crashes_cyclist.geojson",
    }


def build_index(meta, endpoint_bytes, ward_files_bytes=None, crash_files_bytes=None):
    """index.json: the discovery entry point. Hand-assembled manifest listing
    the endpoints and endpoint *families* that actually exist so far.

    endpoint_bytes: {path: actual on-disk byte size} for concrete endpoints
    (_ENDPOINTS), supplied by emit_all after writing them — index.json is
    written last so its bytes_approx values are real, not estimated.

    ward_files_bytes / crash_files_bytes: {"wards/ward-NN.json": actual
    on-disk byte size} / {"crashes/ward-NN.json": ...} for all 50 files in
    that family, or None/empty before they exist. A *family* entry
    (path_template + count + one example URL + bytes_approx_max, rather than
    50 individually hand-listed endpoints) is added only when files were
    actually written — crash_files_bytes reuses the same seam ward_files_bytes
    established, both keyed the same way emit_all's `written` dict already is.
    """
    endpoints = [
        {
            "path": ep["path"],
            "url": f"{API_BASE_URL}/{ep['path']}",
            "bytes_approx": endpoint_bytes[ep["path"]],
            "description": ep["description"],
            "example_questions": ep["example_questions"],
        }
        for ep in _ENDPOINTS
    ]

    families = []
    if ward_files_bytes:
        families.append({
            "path_template": "wards/ward-{NN}.json",
            "url_template": f"{API_BASE_URL}/wards/ward-{{NN}}.json",
            "count": len(ward_files_bytes),
            "example": f"{API_BASE_URL}/wards/ward-01.json",
            "bytes_approx_max": max(ward_files_bytes.values()),
            "description": ("Per-ward detail: full safety index (incl. the "
                            "107-month crash series), alderman contact, council "
                            "safety-sponsorship record, and 311/menu-spending "
                            "proxies for one ward. NN is zero-padded 01-50."),
            "example_questions": [
                "How dangerous is ward 40 for cyclists?",
                "Who is my alderman and what's their bike-safety record?",
            ],
        })
    if crash_files_bytes:
        families.append({
            "path_template": "crashes/ward-{NN}.json",
            "url_template": f"{API_BASE_URL}/crashes/ward-{{NN}}.json",
            "count": len(crash_files_bytes),
            "example": f"{API_BASE_URL}/crashes/ward-01.json",
            "bytes_approx_max": max(crash_files_bytes.values()),
            "description": ("Per-ward cyclist crash records as columnar rows: "
                            "crash_id, date, lat, lng, injury_severity, dooring, "
                            "hit_and_run, street. NN is zero-padded 01-50; every "
                            "ward has a file, even ones with zero crashes."),
            "example_questions": [
                "List recent cyclist crashes in ward 40",
                "How many dooring crashes happened in ward 27?",
            ],
        })

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
        {
            "question": "How dangerous is ward 40 for cyclists?",
            "fetch": [f"{API_BASE_URL}/wards/ward-40.json"],
            "then": (f"Read safety.comparable_danger_score ({COMPARABLE_DANGER_SCORE_DESC}), "
                    "safety.windows for recent counts, and alderman for who to contact."),
        },
        {
            "question": "List recent cyclist crashes in ward 40",
            "fetch": [f"{API_BASE_URL}/crashes/ward-40.json"],
            "then": ("Rows are columnar; zip columns with each row. Dates are ISO "
                    "strings — sort/filter client-side."),
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
        "families": families,
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
            "routes/ — main-route and network-map detail (not yet published)",
            "council/ — City Council safety-legislation tracking (not yet published)",
            "schemas/ — machine-readable JSON Schemas for these endpoints (not yet published)",
        ],
    }


def _load(name):
    return json.loads((SITE_DATA_DIR / name).read_text())


def _enforce_budget(written):
    """Hard-fail if any emitted file exceeds its size budget — that budget is
    the whole point of this being an agent-sized API, not a mirror of
    site/data/. Crash slices (crashes/ward-NN.json) are columnar rows, not
    hand-written prose, and get the larger API_CRASH_SLICE_BUDGET_BYTES;
    every other file keeps API_SIZE_BUDGET_BYTES. Budget chosen by relative
    path prefix — simplest thing that works with only one oversized family.
    """
    for path, size in written.items():
        is_crash_slice = path.startswith("crashes/")
        budget = API_CRASH_SLICE_BUDGET_BYTES if is_crash_slice else API_SIZE_BUDGET_BYTES
        if size > budget:
            budget_name = ("API_CRASH_SLICE_BUDGET_BYTES" if is_crash_slice
                          else "API_SIZE_BUDGET_BYTES")
            raise SystemExit(
                f"emit_api: {path} is {size:,} bytes, over the "
                f"{budget_name} budget of {budget:,} bytes")


def _print_size_table(written):
    """One line per emitted file, aligned — mirrors run_all.print_timings.
    Followed by a one-line min/median/max rollup per subdirectory (e.g.
    `wards/`) so the table stays scannable once a single directory holds 50+
    files, instead of drowning the top-level files in per-ward noise.
    """
    width = max(len(path) for path in written)
    print("\n=== site/api/v1 sizes ===")
    for path, size in written.items():
        print(f"  {path:<{width}}  {size:7,d} bytes")

    by_dir = {}
    for path, size in written.items():
        if "/" in path:
            by_dir.setdefault(path.split("/", 1)[0], []).append(size)
    if by_dir:
        print()
        for directory, sizes in sorted(by_dir.items()):
            sizes = sorted(sizes)
            n = len(sizes)
            median = sizes[n // 2] if n % 2 else (sizes[n // 2 - 1] + sizes[n // 2]) / 2
            print(f"  {directory}/ ({n} files)  min={sizes[0]:,}  "
                 f"median={median:,.0f}  max={sizes[-1]:,} bytes")


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
    """Load committed site/data/*, build every API file (Phase 1's three
    top-level files plus the wards and crashes layers), write them into
    SITE_API_DIR, print a size table, enforce the size budget, and prune
    stale output. Returns {relative path: byte size} for the files written
    this run.
    """
    meta = _load("meta.json")
    citywide_trend = _load("citywide_trend.json")
    findings = _load("findings.json")
    mileage_series = _load("bikeway_mileage_series.json")
    corridors = _load("corridors.json")
    intersections = _load("intersections.json")
    ward_safety_index = _load("ward_safety_index.json")
    aldermen = _load("aldermen.json")
    aldermen_safety_record = _load("aldermen_safety_record.json")
    menu_spending = _load("menu_spending.json")
    ward_311 = _load("ward_311.json")
    crashes = _load("crashes_cyclist.geojson")

    written = {}

    citywide = build_citywide(meta, citywide_trend, findings, mileage_series)
    write_json(SITE_API_DIR / "citywide.json", citywide)
    written["citywide.json"] = (SITE_API_DIR / "citywide.json").stat().st_size

    corridors_api = build_corridors_api(meta, corridors, intersections)
    write_json(SITE_API_DIR / "corridors.json", corridors_api)
    written["corridors.json"] = (SITE_API_DIR / "corridors.json").stat().st_size

    wards_index = build_wards_index(meta, ward_safety_index)
    write_json(SITE_API_DIR / "wards" / "index.json", wards_index)
    written["wards/index.json"] = (SITE_API_DIR / "wards" / "index.json").stat().st_size

    # Driven from ward_safety_index — all 50 wards are guaranteed present
    # there; other sources (aldermen, safety_record, menu_spending, sr311)
    # may be missing a given ward, which build_ward_file handles honestly.
    ward_files_bytes = {}
    for ward_record in ward_safety_index["wards"]:
        padded = ward_record["ward"].zfill(2)
        ward_file = build_ward_file(meta, ward_record, aldermen, aldermen_safety_record,
                                    menu_spending, ward_311)
        path = SITE_API_DIR / "wards" / f"ward-{padded}.json"
        write_json(path, ward_file)
        rel = f"wards/ward-{padded}.json"
        written[rel] = path.stat().st_size
        ward_files_bytes[rel] = written[rel]

    # Crash slices: group features by ward property. Features with no ward
    # (null or missing — unassigned in the spatial join) are excluded from
    # every slice, not silently dropped; crash_id prefixes are computed once,
    # globally across ALL crashes in the source file (not per ward, and not
    # only the ward-assigned ones) so a prefix stays unambiguous dataset-wide.
    features_by_ward = defaultdict(list)
    excluded = 0
    for feature in crashes["features"]:
        ward = feature["properties"].get("ward")
        if not ward:
            excluded += 1
            continue
        features_by_ward[ward].append(feature)
    if excluded:
        print(f"crashes: {excluded} features with no ward assignment excluded from slices")

    id_prefix_map = crash_id_prefixes(
        [f["properties"].get("crash_id") for f in crashes["features"]])

    # Same driving source as the ward-files loop above: every one of the 50
    # wards gets a crashes/ward-NN.json, even a ward with zero crashes.
    crash_files_bytes = {}
    for ward_record in ward_safety_index["wards"]:
        ward = ward_record["ward"]
        padded = ward.zfill(2)
        crash_slice = build_crash_slice(meta, ward, features_by_ward.get(ward, []),
                                        id_prefix_map)
        path = SITE_API_DIR / "crashes" / f"ward-{padded}.json"
        write_json(path, crash_slice)
        rel = f"crashes/ward-{padded}.json"
        written[rel] = path.stat().st_size
        crash_files_bytes[rel] = written[rel]

    index = build_index(meta, written, ward_files_bytes, crash_files_bytes)
    write_json(SITE_API_DIR / "index.json", index)
    written["index.json"] = (SITE_API_DIR / "index.json").stat().st_size

    # Size table first: on a budget trip the developer still sees the full
    # picture of what was written before the hard fail.
    _print_size_table(written)
    _enforce_budget(written)
    _prune_stale(set(written))

    return written


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    emit_all()


if __name__ == "__main__":
    main()
