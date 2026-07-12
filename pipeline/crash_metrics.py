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


def build_findings_core(tuples, by_category_miles, corridors, ward_counts, as_of_date):
    """Assemble findings.json from already-computed inputs — shared by
    aggregate.build_findings (live) and refresh_reporting.py (offline), so the
    published findings can be regenerated from committed data without logic drift.

    Order (checkpoint-1 approved): ksi-trend, protected-share, top-corridors,
    hit-and-run, ward-concentration, dooring-undercount.
    """
    findings = []

    anchor_date = max((t["date"][:10] for t in tuples), default=None)
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
            "caveat": "Counts, not rates — ridership growth is not netted out. "
                      "Recent months are provisional.",
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
            "caveat": "Raw counts, not normalized by bike volume. Dooring is undercounted. "
                      "Per-km rates inflate short segments — Kinzie's rate rides on very few km.",
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
            "caveat": "Share of reported crashes; unreported crashes are not counted.",
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
            "caveat": "Ward totals reflect where people ride most, not only where streets are worst.",
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
        "caveat": "A floor, not a full count.",
        "map_state": {"screen": "map", "layers": ["crashes"], "filters": {"dooring": True}},
        "data_tier": "real",
    })
    return findings
