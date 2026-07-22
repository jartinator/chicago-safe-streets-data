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
attribution, a data_tier, and (as of Phase 4) `schema` — the URL of this
file's own hand-written JSON Schema under site/api/v1/schemas/, validated by
pipeline/check_api.py. Deliberately OMITTED from the envelope: `docs`/
llms.txt (Phase 5) — publishing a URL that 404s is worse than omitting the
key.

On Your Left! publishes NO obstruction data at all — not on the human site,
not in this API. Real blocked-bike-lane reports go to Bike Lane Uprising.
index.json's `no_synthetic_data` statement makes that explicit so agents
don't go looking for an obstruction endpoint here.

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
                    SITE_BASE_URL, SITE_DATA_DIR, SITE_DIR)
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

# Shared verbatim strings (Phase 5 — see llms.txt module docstring below):
# index.json's no_synthetic_data key and llms.txt's disclaimer section must
# say the exact same thing, so this lives in one place rather than two
# hand-typed copies that could drift apart.
NO_SYNTHETIC_DATA_STATEMENT = (
    "On Your Left! publishes NO obstruction data — not in this API, not on "
    "the human site. There is no obstruction endpoint here and never has "
    "been a real one. Real blocked-bike-lane reports go to Bike Lane "
    "Uprising (https://www.bikelaneuprising.com); do not cite anything on "
    "this site as an obstruction report.")

# Verbatim from README.md's "How to read this" section (minus its markdown
# bold markers, since llms.txt is plain text) — the raw-counts-not-
# ridership-normalized caveat, reused rather than re-paraphrased.
RAW_COUNTS_CAVEAT = (
    "Raw counts are not normalized by ridership (no public cyclist-volume "
    "data is joined yet), so busy corridors look worse than dangerous "
    "quiet ones.")

# Machine-readable caveat catalog (P1a) — a small, stable vocabulary of flag
# codes an agent can key off of programmatically instead of parsing prose.
# Each builder passes the codes that apply to its own payload to _envelope's
# `caveats` param (see the mapping in each builder's call below); the text
# here is the single source of truth an agent reads once it has a code.
# Plain-language register to match the rest of this file (RAW_COUNTS_CAVEAT
# above, NO_SYNTHETIC_DATA_STATEMENT) — not a terse machine-only string.
CAVEAT_TEXT = {
    "not_normalized_by_ridership": (
        "Crash counts are raw, not normalized by ridership (no public "
        "cyclist-volume data is joined yet), so busy corridors look worse "
        "than dangerous quiet ones."),
    "recent_months_provisional": (
        "Recent months are provisional — crash records get amended "
        "upstream, so the most recent 1-2 months of any trend may still "
        "move."),
    "dooring_undercounted": (
        "Dooring crashes are structurally undercounted in police crash "
        "reports (see the dooring-undercount finding)."),
    "sponsorship_proxy_not_vote_tally": (
        "Council sponsorship counts are a proxy for engagement, not a "
        "roll-call vote tally — most Chicago street-safety measures pass "
        "by voice vote with no individual vote recorded."),
}

# Canonical tier vocabulary, worded to match SCHEMA.md's table exactly (the
# published-data-contract source of truth) — llms.txt reuses this rather
# than inventing its own phrasing.
ANSWERING_GUIDANCE = (
    "When you quote a number from this API, restate its caveat in the "
    "same answer — most files carry machine-readable `caveats` in their "
    "`_meta` envelope, and every number carries a `data_tier`. If you "
    "are asked for something On Your Left! does not publish — cyclist "
    "ridership or exposure denominators, or real bike-lane obstruction "
    "/ blocked-lane reports — say plainly that it is not published "
    "here rather than estimating or guessing. A missing number is an "
    "honest answer; a fabricated one is not.")

DATA_TIER_VOCAB = [
    ("real", "From the named public source, raw counts (recent months provisional)"),
    ("proxy", "Correlated but biased signal (self-reports, sensor placement) — "
             "direction, not magnitude"),
    ("mock", "Synthetic demonstration data. Exists in the tier vocabulary in "
             "principle; not currently used by any published dataset"),
    ("crowdsourced", "Community-curated, unverified (Mellow Bike Map)"),
    ("derived", "Computed from real underlying data (a rate, trend, or automated "
                "topic tag) rather than sourced directly"),
]

# Shared between index.json's own description and llms.txt's opening
# paragraph (Phase 5). Deliberately does NOT reuse README.md's opening
# paragraph verbatim — that paragraph describes the whole human site, which
# publishes no obstruction data at all (see NO_SYNTHETIC_DATA_STATEMENT);
# describing this API's actual contents avoids implying obstruction data is
# available here.
PROJECT_DESCRIPTION = (
    "Police-reported cyclist crash data, bikeway network quality, and City "
    "Council accountability for Chicago, rebuilt weekly from the Chicago "
    "Data Portal and other public sources.")

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
    {
        "path": "news.json",
        "description": ("Recent news coverage of Chicago bike/street safety, "
                        "matched to wards, alderpersons, main routes, and "
                        "proposed projects."),
        "example_questions": [
            "Is there recent news coverage about bike safety in a specific "
            "Chicago ward?",
            "What's the latest news about a Chicago bikeway project or corridor?",
        ],
    },
    {
        "path": "proposed.json",
        "description": ("Curated roster of proposed and in-progress Chicago "
                        "bikeway/trail projects with volunteer-reviewed status, "
                        "official links, and recent news coverage."),
        "example_questions": [
            "What bike or trail projects are proposed or under construction "
            "in Chicago?",
            "What is the current status of the 606 / Bloomingdale Trail extension?",
        ],
    },
    {
        "path": "routes/index.json",
        "description": ("All 21 Chicago main bike routes' mileage-by-grade "
                        "breakdown, crash totals, and protected-lane share, plus "
                        "network interchange points, with links to each route's "
                        "full segment-level detail file."),
        "example_questions": [
            "Which Chicago main bike routes are the most protected?",
            "How many miles of the 606 / Bloomingdale Trail are off-street?",
        ],
    },
    {
        "path": "council/index.json",
        "description": ("City Council committee hearings relevant to bike/street "
                        "safety and a derived summary of tagged legislative "
                        "activity, with links to the full records and aldermen "
                        "files."),
        "example_questions": [
            "Has Chicago City Council held any recent hearings on bike safety?",
            "How much bike-safety legislation has City Council introduced?",
        ],
    },
    {
        "path": "council/records.json",
        "description": ("Chicago City Council matters (ordinances, resolutions) "
                        "matched to bike/street-safety topics, with sponsors, "
                        "wards, status, and a link to the official record."),
        "example_questions": [
            "What bike-safety ordinances has City Council introduced recently?",
            "Which alderman sponsored the most bike-safety legislation?",
        ],
    },
    {
        "path": "council/aldermen.json",
        "description": ("Current 50-ward alderman roster with contact info, each "
                        "one's council bike-safety sponsorship record (where an "
                        "exact match exists) and ward menu-spending proxy."),
        "example_questions": [
            "Who is my alderman and what's their bike-safety record?",
            "Has my alderman sponsored any bike-safety legislation?",
        ],
    },
]


def _envelope(meta, data_tier, human_page, schema_name, tier_note=None, caveats=None):
    """Build the `_meta` object every emitted API file opens with.

    generated_at/provenance are copied verbatim from site/data/meta.json — see
    the module docstring. tier_note is included only when data_tier == "mixed".
    schema_name is this file's own JSON Schema filename under
    site/api/v1/schemas/ (e.g. "citywide.schema.json"), threaded into `schema`
    (Phase 4 — see module docstring).

    caveats (P1a): an optional list of CAVEAT_TEXT codes applicable to this
    file's numbers. Only added to the envelope when non-empty — files with no
    applicable caveat stay clean rather than emitting an empty array.
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
    if caveats:
        envelope["caveats"] = [{"code": c, "text": CAVEAT_TEXT[c]} for c in caveats]
    envelope["license"] = LICENSE
    envelope["attribution"] = ATTRIBUTION
    envelope["human_page"] = human_page
    envelope["methodology"] = f"{SITE_BASE_URL}/methodology.html"
    envelope["schema"] = f"{API_BASE_URL}/schemas/{schema_name}"
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
        human_page=f"{SITE_BASE_URL}/findings.html",
        schema_name="citywide.schema.json",
        caveats=["not_normalized_by_ridership", "recent_months_provisional",
                "dooring_undercounted"])

    return {"_meta": envelope, **payload}


def build_corridors_api(meta, corridors, intersections):
    """corridors.json: the committed corridor table plus hotspot intersections,
    both passed through as-is — both sources are tier "real".
    """
    envelope = _envelope(meta, data_tier="real",
                         human_page=f"{SITE_BASE_URL}/index.html",
                         schema_name="corridors.schema.json",
                         caveats=["not_normalized_by_ridership"])
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
                         human_page=f"{SITE_BASE_URL}/table.html",
                         schema_name="wards-index.schema.json",
                         caveats=["not_normalized_by_ridership"])

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
        # File-level keys (as_of/source/data_tier/lookup_url/note, per merge)
        # win here and below: if a per-ward source record ever grows a
        # same-named key, it would be silently shadowed by this spread order.
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
        human_page=one_pager_url,
        schema_name="ward.schema.json",
        caveats=["not_normalized_by_ridership", "recent_months_provisional",
                "sponsorship_proxy_not_vote_tally"])

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

    envelope = _envelope(meta, data_tier="real", human_page=f"{SITE_BASE_URL}/index.html",
                         schema_name="crash-slice.schema.json",
                         caveats=["not_normalized_by_ridership", "recent_months_provisional",
                                 "dooring_undercounted"])

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


def build_news_api(meta, news_items):
    """news.json: the committed news_items roster, trimmed per item. Each
    item's `matches` sub-lists (wards/aldermen/routes/projects) are flattened
    to just the id/name an agent would filter or cite on — ward number,
    alderman name, route id, project id — dropping each match's `via` audit
    string (UI-facing provenance for the human site, not useful here). Every
    match key is always emitted, even as an empty list, so an agent can rely
    on the shape without a KeyError.
    """
    items = []
    for item in news_items["items"]:
        matches = item["matches"]
        items.append({
            "title": item["title"],
            "url": item["url"],
            "source": item["source"],
            "published": item["published"],
            "wards": [w["ward"] for w in matches["wards"]],
            "aldermen": [a["name"] for a in matches["aldermen"]],
            "routes": [r["id"] for r in matches["routes"]],
            "projects": [p["id"] for p in matches["projects"]],
        })

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("Headlines, links, dates, and outlet names are real "
                  "(verbatim from the outlets' public RSS feeds); the entity "
                  "matching (wards/aldermen/routes/projects) is derived and "
                  "best-effort."),
        human_page=f"{SITE_BASE_URL}/action.html",
        schema_name="news.schema.json")

    return {
        "_meta": envelope,
        "as_of": news_items["as_of"],
        "note": news_items["note"],
        "items": items,
    }


def build_proposed_api(meta, proposed_projects):
    """proposed.json: the committed proposed_projects roster, one record per
    project, dropping `news_phrases`/`news_phrases_ctx` (the internal
    matcher config used to attach `coverage` — meaningless to an agent) and
    each coverage entry's `via` audit string. Everything else — including
    `official_links` and `citations` — passes through verbatim.
    """
    projects = []
    for p in proposed_projects["projects"]:
        coverage = [{"title": c["title"], "url": c["url"], "source": c["source"],
                    "published": c["published"]} for c in p["coverage"]]
        projects.append({
            "id": p["id"],
            "name": p["name"],
            "status": p["status"],
            "status_as_of": p["status_as_of"],
            "status_note": p["status_note"],
            "description": p["description"],
            "wards": p["wards"],
            "official_links": p["official_links"],
            "citations": p["citations"],
            "coverage": coverage,
        })

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("The project roster and each status are curated/volunteer-"
                  "reviewed (derived); the attached news coverage headlines "
                  "are real (verbatim). The linked official page is "
                  "authoritative."),
        human_page=f"{SITE_BASE_URL}/action.html",
        schema_name="proposed.schema.json")

    return {
        "_meta": envelope,
        "as_of": proposed_projects["as_of"],
        "note": proposed_projects["note"],
        "projects": projects,
    }


GRADE_LEGEND = {
    "protected": "physically separated (post/curb-protected lane or barrier)",
    "paint": "painted or buffered lane — paint & signs only, no separation",
    "mellow": "low-stress neighborhood greenway / traffic-calmed street",
    "offstreet": "off-street trail, fully separated from traffic",
    "none": "no bike facility (shared lane / sharrow / gap)",
}


def build_routes_index(meta, main_routes, network_nodes):
    """routes/index.json: the 21 main-route report cards verbatim (source
    order preserved — never re-sorted) plus a detail_url per line, plus the
    network's interchange nodes (point wayfinding markers, not line
    geometry — allowed in this API). `network_nodes`' per-node data_tier is
    dropped since the whole file already carries one in `_meta`.
    """
    lines = [{**line, "detail_url": f"{API_BASE_URL}/routes/line-{line['id']}.json"}
             for line in main_routes["lines"]]

    interchanges = [
        {"id": n["id"], "kind": n["kind"], "lat": n["lat"], "lng": n["lng"],
         "label": n["label"], "lines": n["lines"]}
        for n in network_nodes["nodes"]
    ]

    envelope = _envelope(
        meta, data_tier="derived",
        tier_note=("line stats are derived from real CDOT segments (street lines) "
                  "and crowdsourced OSM trail geometry (trail lines); interchanges "
                  "are derived."),
        human_page=f"{SITE_BASE_URL}/network.html",
        schema_name="routes-index.schema.json")

    return {
        "_meta": envelope,
        "note": main_routes["note"],
        "grade_legend": GRADE_LEGEND,
        "lines": lines,
        "interchanges": interchanges,
        "count": len(lines),
    }


def build_line_file(meta, line, features, network_nodes):
    """routes/line-<id>.json: one main route's report card plus its member
    segments, aggregated by (label, grade) where label is the street name
    for CDOT bike-route segments or the segment_id slug for OSM trail
    segments (which carry no street name). length_m is summed per group and
    rounded to 1 decimal place; crashes is summed cyclist-crash-within-30m
    counts for street segments, or `null` for trail segments — those carry
    no crash join at all, a data gap rather than a true zero. Members are
    sorted by length_m descending (source feature order isn't meaningful
    once aggregated). Interchanges are filtered to nodes whose `lines` list
    includes this line's id; a line with none gets `[]`, not an omitted key.
    """
    line_id = line["id"]
    members = [f["properties"] for f in features if f["properties"]["line_id"] == line_id]

    agg = {}
    order = []
    for props in members:
        label = props.get("street") or props["segment_id"]
        grade = props["grade"]
        key = (label, grade)
        if key not in agg:
            has_crashes = "crashes_within_30m" in props
            agg[key] = {"length_m": 0.0, "crashes": 0 if has_crashes else None}
            order.append(key)
        agg[key]["length_m"] += props["length_m"]
        if "crashes_within_30m" in props:
            agg[key]["crashes"] += props["crashes_within_30m"]

    member_segments = [
        {"label": label, "grade": grade, "length_m": round(vals["length_m"], 1),
         "crashes": vals["crashes"]}
        for (label, grade), vals in ((k, agg[k]) for k in order)
    ]
    member_segments.sort(key=lambda m: m["length_m"], reverse=True)

    interchanges = [
        {"id": n["id"], "label": n["label"], "lines": n["lines"]}
        for n in network_nodes["nodes"] if line_id in n["lines"]
    ]

    envelope = _envelope(
        meta, data_tier="derived",
        tier_note=("line and member-segment stats are derived from real CDOT "
                  "bike-route segments (street lines) or crowdsourced OSM trail "
                  "geometry (trail lines)."),
        human_page=f"{SITE_BASE_URL}/network.html",
        schema_name="route-line.schema.json")

    return {
        "_meta": envelope,
        "id": line["id"], "name": line["name"], "termini": line["termini"],
        "source": line["source"], "miles_total": line["miles_total"],
        "miles_by_grade": line["miles_by_grade"],
        # Trail lines (source=="osm_trails") carry no pct_protected/
        # crashes_total at all in main_routes.geojson — those stats are
        # street-only. .get(...) surfaces that honestly as null rather than
        # KeyError-ing or fabricating a 0/None-that-looks-computed.
        "pct_protected": line.get("pct_protected"), "crashes_total": line.get("crashes_total"),
        "member_segments": member_segments,
        "interchanges": interchanges,
        "note": ("member_segments aggregate this line's published CDOT bike-route "
                "segments (or OSM trail ways) by street and grade; crashes counts "
                "police-reported cyclist crashes within 30 m of the segment (null "
                "for off-street trail geometry, which carries no crash join)."),
        "see_also": {"routes_index": f"{API_BASE_URL}/routes/index.json"},
    }


def build_council_index(meta, hearings, council_records):
    """council/index.json: committee hearings (real, City Clerk eLMS) plus a
    derived activity summary computed only over topic_relevant council
    records — status/type breakdowns and the most recent intro date.
    """
    topic_records = [r for r in council_records["records"] if r["topic_relevant"]]

    committees = [
        {"committee": c["committee"], "calendar_url": c["calendar_url"],
         "meeting_count": len(c["meetings"]), "meetings": c["meetings"]}
        for c in hearings["committees"]
    ]

    by_status = dict(Counter(r["status"] for r in topic_records))
    by_type = dict(Counter(r["type"] for r in topic_records))
    most_recent_intro_date = max((r["intro_date"] for r in topic_records), default=None)

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("hearings/meetings are real (City Clerk eLMS); the activity "
                  "summary is derived (counts over the topic-tagged council "
                  "records, whose topic tagging is a derived best-effort "
                  "classification)."),
        human_page=f"{SITE_BASE_URL}/action.html",
        schema_name="council-index.schema.json",
        caveats=["sponsorship_proxy_not_vote_tally"])

    hearings_out = {
        "as_of": hearings["as_of"], "note": hearings["note"],
        "structured_data_available": hearings["structured_data_available"],
        "committees": committees,
    }
    if "source" in hearings:
        hearings_out["source"] = hearings["source"]

    return {
        "_meta": envelope,
        "hearings": hearings_out,
        "activity_summary": {
            "topic_relevant_matters": len(topic_records),
            "by_status": by_status,
            "by_type": by_type,
            "most_recent_intro_date": most_recent_intro_date,
            "note": council_records["note"],
        },
        "records_url": f"{API_BASE_URL}/council/records.json",
        "aldermen_url": f"{API_BASE_URL}/council/aldermen.json",
    }


_COUNCIL_RECORD_FIELDS = ("matter_id", "title", "type", "status", "intro_date",
                          "sponsors", "sponsor_wards", "url", "source")


def build_council_records_api(meta, council_records):
    """council/records.json: every topic_relevant record, source order
    preserved, trimmed to the 9 agent-useful fields. Drops
    topic_relevant/topic_reason/topic_tagged_by/data_tier/topic_tag_tier —
    that tier information lives in the envelope + note instead.
    """
    records = [{k: r[k] for k in _COUNCIL_RECORD_FIELDS}
              for r in council_records["records"] if r["topic_relevant"]]

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("matter records (title/status/sponsors/dates) are real "
                  "(Legistar + Councilmatic); topic-relevance tagging is derived "
                  "(keyword net + classifier, best-effort)."),
        human_page=f"{SITE_BASE_URL}/action.html",
        schema_name="council-records.schema.json",
        caveats=["sponsorship_proxy_not_vote_tally"])

    return {
        "_meta": envelope,
        "as_of": meta["generated_at"],
        "note": council_records["note"],
        "count": len(records),
        "records": records,
    }


_SAFETY_AGGREGATE_FIELDS = ("safety_sponsorships", "total_matched_sponsorships",
                           "recorded_no_votes")
_UNMATCHED_SPONSOR_FIELDS = ("sponsor_name", "ward") + _SAFETY_AGGREGATE_FIELDS


def build_aldermen_api(meta, aldermen, safety_record, menu_spending):
    """council/aldermen.json: the current 50-ward roster as the spine (order
    preserved), each enriched with an EXACT (ward, name) safety-sponsorship
    aggregate and a menu-spending proxy. No fuzzy matching (DECISIONS.md #8):
    a safety_record entry whose (ward, sponsor_name) doesn't exactly match a
    current roster (ward, alderman) pair goes to `unmatched_sponsors`
    (which keeps sponsor_name/ward since it isn't nested under a ward
    entry) instead of being force-attached to a ward. Each entry's
    per-sponsor `records` list is dropped everywhere — huge, and
    council/records.json lets an agent cross-reference by sponsor name
    instead.
    """
    roster_keys = {(w["ward"], w["alderman"]) for w in aldermen["wards"]}

    safety_by_key = {}
    unmatched_sponsors = []
    for entry in safety_record["aldermen"]:
        key = (entry["ward"], entry["sponsor_name"])
        if key in roster_keys:
            safety_by_key[key] = {k: entry[k] for k in _SAFETY_AGGREGATE_FIELDS}
        else:
            unmatched_sponsors.append({k: entry[k] for k in _UNMATCHED_SPONSOR_FIELDS})

    aldermen_out = []
    for w in aldermen["wards"]:
        ward = w["ward"]
        safety = safety_by_key.get((ward, w["alderman"]))

        if ward in menu_spending["wards"]:
            menu = {**menu_spending["wards"][ward], "data_tier": menu_spending["data_tier"]}
        else:
            # Never fabricate zeros: absence is a data gap, not "no spending".
            menu = {"available": False}

        aldermen_out.append({
            "ward": ward, "alderman": w["alderman"], "email": w["email"],
            "phone": w["phone"], "website": w["website"],
            "safety_record": safety,
            "menu_spending": menu,
            "detail_url": f"{API_BASE_URL}/wards/ward-{ward.zfill(2)}.json",
        })

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("roster + contact info are real (city Ward Offices dataset); "
                  "safety_record aggregates are derived (council sponsorship "
                  "counts); menu_spending is a proxy."),
        human_page=f"{SITE_BASE_URL}/action.html",
        schema_name="council-aldermen.schema.json",
        caveats=["sponsorship_proxy_not_vote_tally"])

    return {
        "_meta": envelope,
        "as_of": aldermen["as_of"],
        "roster_note": aldermen["note"],
        "menu_note": menu_spending["note"],
        "safety_record_note": safety_record["note"],
        "aldermen": aldermen_out,
        "unmatched_sponsors": unmatched_sponsors,
        "unmatched_note": ("Sponsors from the council safety-sponsorship aggregate "
                          "whose (ward, name) does not exactly match the current "
                          "Ward Offices roster — mostly former alderpeople. Listed "
                          "verbatim, never fuzzy-matched to a current ward (see "
                          "DECISIONS.md #8). Drop the per-sponsor matter list; "
                          "cross-reference council/records.json by sponsor name."),
    }


def build_index(meta, endpoint_bytes, ward_files_bytes=None, crash_files_bytes=None,
                line_files_bytes=None):
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
    if line_files_bytes:
        families.append({
            "path_template": "routes/line-{id}.json",
            "url_template": f"{API_BASE_URL}/routes/line-{{id}}.json",
            "count": len(line_files_bytes),
            "example": f"{API_BASE_URL}/routes/line-milwaukee.json",
            "bytes_approx_max": max(line_files_bytes.values()),
            "description": ("Per-route detail: member street/trail segments "
                            "aggregated by street and grade with length and crash "
                            "counts, plus network interchanges on that route. id "
                            "is the route's kebab-case slug (see routes/index.json "
                            "for the full list)."),
            "example_questions": [
                "How protected is the Milwaukee Ave bike route?",
                "Which Chicago main bike routes are the most protected?",
            ],
        })

    envelope = _envelope(
        meta, data_tier="mixed",
        tier_note=("this index has no single data tier — each endpoint declares "
                  "its own data_tier(s) in its own _meta envelope and payload "
                  "sections; see the endpoint list below."),
        human_page=f"{SITE_BASE_URL}/index.html",
        schema_name="index.schema.json")

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
        {
            "question": "Is there recent news coverage about bike safety in a "
                        "specific Chicago ward?",
            "fetch": [f"{API_BASE_URL}/news.json"],
            "then": ("Filter items where wards (or aldermen) includes the ward "
                    "you care about; url is the outlet's own article link."),
        },
        {
            "question": "What is the current status of a Chicago bikeway or "
                        "trail project?",
            "fetch": [f"{API_BASE_URL}/proposed.json"],
            "then": ("Find the project by name in projects, then read status, "
                    "status_as_of, and status_note; coverage carries recent "
                    "news headlines about it."),
        },
        {
            "question": "Is the Milwaukee Avenue bike route protected?",
            "fetch": [f"{API_BASE_URL}/routes/line-milwaukee.json"],
            "then": ("Read pct_protected and miles_by_grade for the route-wide "
                    "mix, or member_segments for street-by-street detail."),
        },
        {
            "question": "What has the City Council done on bike safety, and who "
                        "sponsors it?",
            "fetch": [f"{API_BASE_URL}/council/index.json",
                     f"{API_BASE_URL}/council/records.json",
                     f"{API_BASE_URL}/council/aldermen.json"],
            "then": ("Start at council/index.json for hearings and the activity "
                    "summary, then fetch council/records.json for individual "
                    "matters or council/aldermen.json for a given alderman's "
                    "sponsorship record."),
        },
    ]

    return {
        "_meta": envelope,
        "title": "On Your Left! — Chicago bike safety, on the record",
        "description": PROJECT_DESCRIPTION,
        "endpoints": endpoints,
        "families": families,
        "fetch_recipes": fetch_recipes,
        "coverage_note": (
            f"Crash data is citywide-reliable only from {CRASH_START_DATE}; counts "
            "are raw, not ridership-normalized; recent months are provisional "
            "(records get amended)."),
        "no_synthetic_data": NO_SYNTHETIC_DATA_STATEMENT,
        "planned": [],
    }


def build_llms_txt(meta, endpoint_bytes):
    """site/llms.txt: the llms.txt convention discovery file — plain text
    (not JSON), for a cold LLM agent that has never seen this site to go
    from "what is this" to "here's the API" in one fetch.

    Reuses `_ENDPOINTS` (the exact same source build_index's own endpoint
    listing is built from) so the human-readable list here and index.json's
    list can never drift apart into two different rosters. Likewise reuses
    NO_SYNTHETIC_DATA_STATEMENT and RAW_COUNTS_CAVEAT verbatim rather than
    re-paraphrasing either (see those constants' docstrings above).

    endpoint_bytes: same {path: on-disk byte size} shape emit_all already
    threads into build_index — llms.txt is written right after index.json,
    so real sizes are available here too, not estimates.

    Sized against API_SIZE_BUDGET_BYTES (the same ceiling every other
    agent-facing file in this API is held to) — see emit_all's budget check
    for this file. Chosen because there's no separate "docs budget" in the
    plan; reusing the existing constant keeps one size policy instead of two.
    """
    lines = [
        "# On Your Left! — Chicago bike safety, on the record",
        "",
        PROJECT_DESCRIPTION,
        "",
        f"generated_at: {meta['generated_at']}",
        f"provenance: {meta['provenance']}",
        f"contract_version: {CONTRACT_VERSION}",
        "",
        "## Start here",
        f"{API_BASE_URL}/index.json",
        "The discovery entry point: the full endpoint list with byte sizes, "
        "endpoint *families* (e.g. one file per ward), and fetch recipes for "
        "common questions.",
        "",
        "## Endpoints",
    ]
    for ep in _ENDPOINTS:
        size = endpoint_bytes.get(ep["path"])
        size_note = f" ({size:,} bytes)" if size is not None else ""
        lines.append(f"- {API_BASE_URL}/{ep['path']}{size_note}")
        lines.append(f"  {ep['description']}")
        for q in ep["example_questions"]:
            lines.append(f'  e.g. "{q}"')
    lines += [
        "",
        "## Reading the data",
        "Every file (and often individual records within it) carries a "
        "data_tier:",
    ]
    for tier, desc in DATA_TIER_VOCAB:
        lines.append(f"- {tier}: {desc}")
    lines += [
        "",
        RAW_COUNTS_CAVEAT,
        "Recent months are provisional — crash records get amended after "
        "the fact, so the most recent 1-2 months of any trend may still "
        "move.",
        "",
        "Every file opens with a `_meta` envelope: api_version/"
        "contract_version identify this contract; generated_at/provenance "
        "say when and how the underlying data was built (copied verbatim "
        "from site/data/meta.json, never a fresh timestamp); data_tier (and "
        "tier_note, when mixed) says how much to trust it; license and "
        "attribution are how to cite it; human_page links the matching "
        "human-readable page; methodology links the methodology page; "
        "schema links this file's own JSON Schema under /api/v1/schemas/.",
        "",
        NO_SYNTHETIC_DATA_STATEMENT,
        "",
        "## When answering from this data",
        ANSWERING_GUIDANCE,
        "",
        "## Human pages",
        f"{SITE_BASE_URL}/index.html — interactive map",
        f"{SITE_BASE_URL}/methodology.html — how every number is computed",
        f"{SITE_BASE_URL}/ward.html?ward=NN — one ward's printable one-pager "
        "(query-param driven: one HTML file serves all 50 wards, NN is "
        "01-50)",
        f"{SITE_BASE_URL}/contributing.html — downloads and docs",
    ]
    return "\n".join(lines) + "\n"


# The site's human pages plus the two agent-facing discovery files, in
# sitemap order. Keep this in sync with the actual site/*.html file list
# (see build_sitemap_xml).
_SITEMAP_PAGES = [
    "index.html", "network.html", "findings.html", "table.html",
    "sources.html", "methodology.html", "action.html", "ward.html",
    "contributing.html", "llms.txt", "api/v1/index.json",
]


def build_sitemap_xml(meta):
    """site/sitemap.xml: a standard urlset sitemap (loc + lastmod per URL)
    for every human page plus llms.txt and api/v1/index.json — the two
    agent-facing discovery files, so a crawler that only reads sitemap.xml
    still finds them.

    lastmod is the date portion of meta.json's generated_at for every
    entry — the same provenance source as the JSON envelope, so a real data
    refresh moves it in lockstep and a doc-only PR doesn't.
    """
    lastmod = meta["generated_at"][:10]
    entries = "\n".join(
        f"  <url>\n    <loc>{SITE_BASE_URL}/{page}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n  </url>"
        for page in _SITEMAP_PAGES)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n")


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


def _enforce_llms_txt_budget(llms_txt):
    """Hard-fail if llms.txt exceeds API_SIZE_BUDGET_BYTES — same ceiling as
    every other agent-facing file (see build_llms_txt's docstring on that
    choice). A standalone helper (mirroring _enforce_budget) so it's testable
    without an emit_all() round-trip through the filesystem.
    """
    size = len(llms_txt.encode("utf-8"))
    if size > API_SIZE_BUDGET_BYTES:
        raise SystemExit(
            f"emit_api: llms.txt is {size:,} bytes, over the "
            f"API_SIZE_BUDGET_BYTES budget of {API_SIZE_BUDGET_BYTES:,} bytes")


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
    news_items = _load("news_items.json")
    proposed = _load("proposed_projects.json")
    main_routes = _load("main_routes.geojson")
    network_nodes = _load("network_nodes.json")
    council_records = _load("council_records.json")
    hearings = _load("hearings.json")

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

    news_api = build_news_api(meta, news_items)
    write_json(SITE_API_DIR / "news.json", news_api)
    written["news.json"] = (SITE_API_DIR / "news.json").stat().st_size

    proposed_api = build_proposed_api(meta, proposed)
    write_json(SITE_API_DIR / "proposed.json", proposed_api)
    written["proposed.json"] = (SITE_API_DIR / "proposed.json").stat().st_size

    routes_index = build_routes_index(meta, main_routes, network_nodes)
    write_json(SITE_API_DIR / "routes" / "index.json", routes_index)
    written["routes/index.json"] = (SITE_API_DIR / "routes" / "index.json").stat().st_size

    # One file per main route (21 today); every line in main_routes["lines"]
    # gets a file, in source order (never re-sorted).
    line_files_bytes = {}
    for line in main_routes["lines"]:
        line_file = build_line_file(meta, line, main_routes["features"], network_nodes)
        path = SITE_API_DIR / "routes" / f"line-{line['id']}.json"
        write_json(path, line_file)
        rel = f"routes/line-{line['id']}.json"
        written[rel] = path.stat().st_size
        line_files_bytes[rel] = written[rel]

    council_index = build_council_index(meta, hearings, council_records)
    write_json(SITE_API_DIR / "council" / "index.json", council_index)
    written["council/index.json"] = (SITE_API_DIR / "council" / "index.json").stat().st_size

    council_records_api = build_council_records_api(meta, council_records)
    write_json(SITE_API_DIR / "council" / "records.json", council_records_api)
    written["council/records.json"] = (SITE_API_DIR / "council" / "records.json").stat().st_size

    aldermen_api = build_aldermen_api(meta, aldermen, aldermen_safety_record, menu_spending)
    write_json(SITE_API_DIR / "council" / "aldermen.json", aldermen_api)
    written["council/aldermen.json"] = (SITE_API_DIR / "council" / "aldermen.json").stat().st_size

    index = build_index(meta, written, ward_files_bytes, crash_files_bytes, line_files_bytes)
    write_json(SITE_API_DIR / "index.json", index)
    written["index.json"] = (SITE_API_DIR / "index.json").stat().st_size

    # Size table first: on a budget trip the developer still sees the full
    # picture of what was written before the hard fail.
    _print_size_table(written)
    _enforce_budget(written)

    # llms.txt and sitemap.xml are siblings of index.html at the site root
    # (SITE_DIR), not part of the api/v1 namespace tree (SITE_API_DIR) — see
    # config.py's SITE_DIR comment. Written separately from `written`/
    # _enforce_budget/_prune_stale, which are all scoped to SITE_API_DIR;
    # `written` (returned to callers, e.g. run_all's size reporting) stays
    # exactly the api/v1 file set, so these two never leak into it. Checked
    # after _enforce_budget above so an over-budget api/v1 file is always
    # reported first (it's the more actionable failure).
    llms_txt = build_llms_txt(meta, written)
    _enforce_llms_txt_budget(llms_txt)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "llms.txt").write_text(llms_txt, encoding="utf-8")

    sitemap_xml = build_sitemap_xml(meta)
    (SITE_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    _prune_stale(set(written))

    return written


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    emit_all()


if __name__ == "__main__":
    main()
