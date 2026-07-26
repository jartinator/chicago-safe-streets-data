"""Pure crash-metric computations shared by aggregate.py and refresh_reporting.py.

No geopandas, no network, no file I/O — everything here operates on plain crash
tuples so both the live aggregate path and the offline refresh script compute the
exact same numbers (no logic drift between them).

A crash tuple is a dict:
    {"date": "YYYY-MM-DD", "severity": <published severity enum str>,
     "hit_and_run": bool, "dooring": bool, "ward": str|None}

Severity definitions (see SCHEMA.md):
    injury crashes = fatal + incapacitating + non_incapacitating
    KSI ("killed or seriously injured") = fatal + incapacitating
"""
from collections import defaultdict
from datetime import datetime, timedelta

from caveats import PROVISIONAL_MONTHS, finding_tags

INJURY_SEVERITIES = ("fatal", "incapacitating", "non_incapacitating")
KSI_SEVERITIES = ("fatal", "incapacitating")


def _month_range(start_month, end_month):
    y, m = int(start_month[:4]), int(start_month[5:7])
    ey, em = int(end_month[:4]), int(end_month[5:7])
    while (y, m) <= (ey, em):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def _new_counts():
    return {"crashes": 0, "injury_crashes": 0, "ksi": 0, "fatal": 0}


def _count(bucket, t):
    bucket["crashes"] += 1
    sev = t.get("severity")
    if sev in INJURY_SEVERITIES:
        bucket["injury_crashes"] += 1
    if sev in KSI_SEVERITIES:
        bucket["ksi"] += 1
    if sev == "fatal":
        bucket["fatal"] += 1


def monthly_counts(tuples, start_month, end_month):
    """Contiguous monthly buckets [{month, crashes, injury_crashes, ksi, fatal}] —
    a month with no crashes still appears, with zeros."""
    buckets = {m: dict(month=m, **_new_counts()) for m in _month_range(start_month, end_month)}
    for t in tuples:
        b = buckets.get((t.get("date") or "")[:7])
        if b is not None:
            _count(b, t)
    return list(buckets.values())


def per_ward_monthly(tuples, start_month, end_month):
    """{ward: monthly_counts list} for located crashes (ward is not None)."""
    by_ward = defaultdict(list)
    for t in tuples:
        if t.get("ward"):
            by_ward[t["ward"]].append(t)
    return {w: monthly_counts(ts, start_month, end_month) for w, ts in by_ward.items()}


def window_counts(tuples, anchor_date):
    """Trailing-365-days vs the prior 365 days, anchored at anchor_date.

    Same window boundaries as aggregate.crash_trend (recent: date > anchor-365;
    prior: anchor-730 < date <= anchor-365) so trend direction and these counts
    can never disagree about which window a crash falls in.
    """
    anchor = datetime.strptime(anchor_date, "%Y-%m-%d")
    recent_start = anchor - timedelta(days=365)
    prior_start = anchor - timedelta(days=730)
    recent, prior = _new_counts(), _new_counts()
    for t in tuples:
        try:
            d = datetime.strptime((t.get("date") or "")[:10], "%Y-%m-%d")
        except ValueError:
            continue
        if d > recent_start:
            _count(recent, t)
        elif prior_start < d <= recent_start:
            _count(prior, t)
    return {"recent_12mo": recent, "prior_12mo": prior, "window_end": anchor_date}


def check_trend_window_consistency(trend, windows, label):
    """Raise ValueError if a crash_trend block and a windows block disagree.

    Both blocks publish the same trailing-12mo-vs-prior-12mo comparison, so a
    shared anchor must give identical window_end and crash counts. Count
    comparison is skipped when trend has no counts (insufficient_data), but the
    anchors must still match. `label` names the record (e.g. "ward 35") in the
    error message.
    """
    if trend["window_end"] != windows["window_end"]:
        raise ValueError(
            f"{label}: crash_trend.window_end={trend['window_end']} != "
            f"windows.window_end={windows['window_end']}")
    if trend["recent_12mo"] is None:
        return
    for key in ("recent_12mo", "prior_12mo"):
        if trend[key] != windows[key]["crashes"]:
            raise ValueError(
                f"{label}: crash_trend.{key}={trend[key]} != "
                f"windows.{key}.crashes={windows[key]['crashes']}")


def hit_and_run_shares(tuples):
    """Hit-and-run share of all crashes and of injury crashes, pct rounded to 1 decimal."""
    total = len(tuples)
    hnr = sum(1 for t in tuples if t.get("hit_and_run"))
    injuries = [t for t in tuples if t.get("severity") in INJURY_SEVERITIES]
    injury_hnr = sum(1 for t in injuries if t.get("hit_and_run"))
    return {
        "total": total,
        "hit_and_run": hnr,
        "share_pct": round(100 * hnr / total, 1) if total else 0.0,
        "injury_total": len(injuries),
        "injury_hit_and_run": injury_hnr,
        "injury_share_pct": round(100 * injury_hnr / len(injuries), 1) if injuries else 0.0,
    }


def protected_share(by_category_miles):
    """Protected/buffered share of ON-STREET bikeway miles.

    The `trail` category is excluded from both numerator and denominator: off-street
    trails live in the separate OSM layer at crowdsourced tier and must never enter
    real-tier statistics (see the OSM-trails constraint in the reporting plan).
    """
    cats = {k: v for k, v in by_category_miles.items() if k != "trail"}
    total = sum(cats.values())
    protected = cats.get("protected", 0.0)
    buffered = cats.get("buffered", 0.0)
    return {
        "protected_mi": round(protected, 2),
        "buffered_mi": round(buffered, 2),
        "total_mi": round(total, 2),
        "protected_pct": round(100 * protected / total, 1) if total else 0.0,
        "protected_plus_buffered_pct":
            round(100 * (protected + buffered) / total, 1) if total else 0.0,
    }


def build_findings_core(tuples, by_category_miles, corridors, ward_counts, as_of_date,
                        road_coverage=None):
    """Assemble findings.json from already-computed inputs — shared by
    aggregate.build_findings (live) and refresh_reporting.py (offline), so the
    published findings can be regenerated from committed data without logic drift.

    Order (checkpoint-1 approved): ksi-trend, protected-share, street-coverage,
    top-corridors, hit-and-run, ward-concentration, dooring-undercount.

    Every caveat here is hand-written prose welded to a number, which is the one
    place the caveat contract has no automated truth check (AGENTS.md landmines,
    DECISIONS.md #42/#43). Two rules bind anything written below:

      CC-3  The string names its own referent — a window, a date, a field from
            its own object — because a caveat travels quoted on its own.
      CC-8  A value the caveat restates goes in parentheses BEGINNING with the
            value, `(2040 crashes)`, and it must equal a value the finding
            object carries. A number in running prose is checked by nothing and
            must therefore never be a restatement.

    Tags come from caveats.FINDING_CAVEAT_TAGS, which is the canonical table
    (02-architecture.md §1.5). Do not re-derive a row here.
    """
    findings = []

    anchor_date = max((t["date"][:10] for t in tuples), default=None)

    # The window every whole-series finding below names, so each caveat carries
    # its own referent. Degrades to the start date rather than to the string
    # "None" when there are no crashes at all.
    span = (f"reported from September 2017 through {anchor_date}"
            if anchor_date else "reported since September 2017")
    if anchor_date:
        ksi = window_counts(tuples, anchor_date)
        findings.append({
            "id": "ksi-trend",
            "title": "Cyclists killed or seriously injured",
            "stat": str(ksi["recent_12mo"]["ksi"]),
            "description": (f"A cyclist was killed or seriously injured "
                            f"(\"incapacitating\" in police records) in "
                            f"{ksi['recent_12mo']['ksi']} crashes in the 12 months through "
                            f"{ksi['window_end']}, vs {ksi['prior_12mo']['ksi']} the prior "
                            "12 months. Vision Zero's goal is zero."),
            "caveat": (f"Police-reported crashes in which a cyclist was killed "
                       f"or seriously injured, counted over the 12 months "
                       f"ending {ksi['window_end']} "
                       f"({ksi['recent_12mo']['ksi']} crashes). The most recent "
                       f"{PROVISIONAL_MONTHS} months are provisional — police "
                       f"records are amended for weeks after a crash, so this "
                       f"figure can rise. Counts are not adjusted for how many "
                       f"people ride, so growth in cycling is not netted out."),
            "caveat_tags": finding_tags("ksi-trend"),
            "map_state": {"screen": "map", "layers": ["crashes"], "filters": {}},
            "data_tier": "real",
        })

    ps = protected_share(by_category_miles)
    if ps["total_mi"]:
        findings.append({
            "id": "protected-share",
            "title": "How much of the network protects riders",
            "stat": f"{ps['protected_pct']:.0f}%",
            "description": (f"Only {ps['protected_pct']:.0f}% of Chicago's {ps['total_mi']:.0f} "
                            f"on-street bikeway miles are physically protected lanes "
                            f"({ps['protected_mi']:.0f} mi); counting buffered lanes brings it to "
                            f"{ps['protected_plus_buffered_pct']:.0f}%. The rest is paint, "
                            "sharrows, and greenways. Off-street trails are tracked separately."),
            "caveat": (f"Share of current on-street network mileage as of {as_of_date}; "
                       "protected = barrier/curb-protected on-street lanes. Off-street trails "
                       "are excluded — they live in the separate OSM layer."),
            "caveat_tags": finding_tags("protected-share"),
            "map_state": {"screen": "map", "layers": ["mainroutes"], "filters": {}},
            "data_tier": "real",
        })

    if road_coverage and road_coverage.get("road_miles"):
        rc = road_coverage
        findings.append({
            "id": "street-coverage",
            "title": "How much of the street grid has bike infrastructure",
            "stat": f"{rc['pct_with_bike_infra']:.0f}%",
            "description": (f"Chicago has {rc['road_miles']:,.0f} miles of surface "
                            f"streets (arterials, collectors, and neighborhood "
                            f"streets). {rc['onstreet_bikeway_miles']:,.0f} miles — "
                            f"{rc['pct_with_bike_infra']:.0f}% — have any bike "
                            f"infrastructure at all, counting everything from "
                            f"sharrows to protected lanes."),
            "caveat": ("Centerline miles on both sides of the ratio. Expressways, "
                       "ramps, alleys, and river channels are excluded from street "
                       "miles; off-street trails are excluded from bikeway miles. "
                       "The street centerline layer was last updated in 2021 — the "
                       "grid changes slowly."),
            "caveat_tags": finding_tags("street-coverage"),
            "map_state": {"screen": "map", "layers": ["infrastructure"], "filters": {}},
            "data_tier": "real",
        })

    top = [c for c in corridors if c.get("crashes_per_km")][:5]
    if top:
        findings.append({
            "id": "top-corridors",
            "title": "Highest crash-density corridors",
            "stat": top[0]["street"].title(),
            "description": "Top corridors by cyclist crashes per km of bikeway: " +
                           "; ".join(f"{c['street'].title()} ({c['crashes_per_km']}/km)"
                                     for c in top) + ".",
            # No parenthetical restatement is possible here: `stat` is a street
            # name, so this finding object carries no numeric value at all and
            # CC-8 would reject any `(N ...)` form. The rates stay in running
            # prose in `description`.
            "caveat": (f"Cyclist crashes {span}, divided by each corridor's "
                       f"bikeway kilometres. Not adjusted for how many people "
                       f"ride, so a busier corridor can rank higher without "
                       f"being more dangerous per rider. Dooring is "
                       f"undercounted in police records, so every corridor's "
                       f"count here is a floor. The shortest corridors — "
                       f"{top[0]['street'].title()} among them — compute their "
                       f"rate over very few kilometres, which makes those rates "
                       f"unstable rather than a finding."),
            "caveat_tags": finding_tags("top-corridors"),
            "map_state": {"screen": "map", "layers": ["crashes", "infrastructure"],
                          "corridor": top[0]["street"], "filters": {}},
            "data_tier": "real",
        })

    hr = hit_and_run_shares(tuples)
    if hr["total"]:
        findings.append({
            "id": "hit-and-run",
            "title": "How often the driver leaves",
            "stat": f"{hr['share_pct']:.0f}%",
            "description": (f"In {hr['share_pct']:.0f}% of police-reported cyclist crashes since "
                            f"Sept 2017 ({hr['hit_and_run']} of {hr['total']}), the driver left "
                            f"the scene — {hr['injury_share_pct']:.0f}% when the cyclist was "
                            "injured."),
            "caveat": (f"Share of police-reported cyclist crashes {span} in "
                       f"which the driver left the scene. Crashes that were "
                       f"never reported to police are on neither side of this "
                       f"share, so it describes reported crashes only and the "
                       f"true rate is unknown."),
            "caveat_tags": finding_tags("hit-and-run"),
            "map_state": {"screen": "table", "layers": [], "filters": {}},
            "data_tier": "real",
        })

    total = sum(ward_counts.values())
    top_wards = sorted(ward_counts.items(), key=lambda kv: -kv[1])[:5]
    if total:
        share = 100 * sum(v for _, v in top_wards) / total
        findings.append({
            "id": "ward-concentration",
            "title": "Ward concentration",
            "stat": f"{share:.0f}%",
            "description": (f"5 of 50 wards account for {share:.0f}% of located cyclist crashes "
                            "since Sept 2017: "
                            + ", ".join(f"Ward {w} ({v})" for w, v in top_wards) + "."),
            "caveat": (f"Located cyclist crashes {span}, summed by ward — the "
                       f"five highest-count wards against all 50. Ward totals "
                       f"are not adjusted for how many people ride, so a ward "
                       f"with heavy bike traffic can top this list without "
                       f"having the most dangerous streets."),
            "caveat_tags": finding_tags("ward-concentration"),
            "wards": [w for w, _ in top_wards],
            "map_state": {"screen": "map", "layers": ["crashes", "wards"],
                          "ward": top_wards[0][0], "filters": {}},
            "data_tier": "real",
        })

    doorings = sum(1 for t in tuples if t.get("dooring"))
    findings.append({
        "id": "dooring-undercount",
        "title": "Dooring: structurally undercounted",
        "stat": f"{doorings}+",
        "description": (f"{doorings} crashes since Sept 2017 carry a dooring flag. Dooring is "
                        "structurally excluded from 'reportable' crash records unless damage/injury "
                        "thresholds are met, so the real number is higher than any count on this "
                        "site."),
        # CC-8 landmine: `stat` is "2040+", so the canonical restatement is
        # "(2040 crashes)" and the checker compares it against that stat. A bare
        # number in running prose here would be checked by nothing.
        "caveat": (f"Cyclist crashes {span} that carry a dooring flag in the "
                   f"police record ({doorings} crashes). Dooring is excluded "
                   f"from reportable crash records unless a damage or injury "
                   f"threshold is met, so this is a floor on dooring crashes "
                   f"and not a full count."),
        "caveat_tags": finding_tags("dooring-undercount"),
        "map_state": {"screen": "map", "layers": ["crashes"], "filters": {"dooring": True}},
        "data_tier": "real",
    })
    return findings
