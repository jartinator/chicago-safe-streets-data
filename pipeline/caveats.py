"""The caveat co-location contract (caveat_contract v1) — vocabulary, generators,
and the two placement helpers emit_api.py calls.

Lands as: pipeline/caveats.py

Why this file exists
--------------------
A number and the qualifier that makes it honest must be the same JSON object, or
adjacent keys in one object. Never one fetch apart, never one object apart.

site/api/v1/citywide.json already does this right: every findings[] item carries
a `caveat` string next to its `stat`, so an agent summarizing the finding has to
actively delete a field it already loaded in order to drop the caveat.
site/api/v1/wards/ward-NN.json does not: its windows.recent_12mo counts and its
107-month series carry no provisional flag at all, and that caveat lives only in
llms.txt and index.json — one fetch away from the file a ward-scoped agent
fetches alone.

This module generalizes the citywide pattern so the whole namespace can obey it.

The rules, in short (full text in the architecture spec):
  CC-1  Co-location. Every quotable number sits in an object that directly
        carries its qualifier — either a block on that object (Form A) or a
        `<field>_caveat` / `<field>_caveat_tags` sibling pair (Form B).
  CC-2  Scope equality. A block applies to every number in its own object.
        If a caveat is true of some numbers but not others, split the object.
  CC-3  Self-containment. A caveat string names its own REFERENT — a date, a
        window, a field name from its own object — and reads correctly when
        quoted alone. Restating values that are already sibling keys is
        permitted, not required: it blocks the sharing CC-7 depends on.
  CC-4  Series. The qualifier sits on the array's container; items that differ
        carry their own partial block.
  CC-5  Structured twin. Machine-checkable state goes in `caveat_tags`, drawn
        from CAVEAT_TAG_VOCAB, not only in the prose.
  CC-6  No relocation. A qualifier for a number in file A appears in file A.
        It may be repeated in llms.txt; it may never live only there.
  CC-7  Budget exception. Where zero-hop placement would break
        API_SIZE_BUDGET_BYTES, a claim may carry `caveat_ref` resolving against
        a `caveats` map IN THE SAME FILE. Cross-file refs stay forbidden.
        The map is keyed by CONTENT, so identical caveats share one entry —
        without that, CC-7 is larger than the Form A it replaces. Use
        caveat_ref_key() and never build the key from a ward number.
  CC-8  Restatement fidelity. A caveat may restate a value that sits beside it,
        and every value it restates must EQUAL the co-located value. Restated
        values are written in one canonical form — a parenthetical that begins
        with the value, `(65 crashes)` — and only that form is a restatement.
        Enforced here at emit time by qualify()/pair(), and again on the shipped
        file by Check 5. See the CC-8 section below for why this rule exists.

CC-1 through CC-7 govern where a qualifier sits and how it reads. CC-8 is the
only one that governs whether it is TRUE, and it was missing from v1's first
draft. Co-location makes a caveat maximally credible: it arrives welded to the
number, in the same fetch, with a schema and a CI check behind it. That is the
mechanism's blind spot, so the mechanism has to carry its own truth check.

Enforcement lives in pipeline/check_api.py (Check 5), scoped by an explicit
allowlist of JSON CLAIM PATHS — not files — so migration is incremental one
claim at a time: land one claim's worth, add its path, stop whenever. A ward
file holds ~130 numbers and phase 1 qualifies five claims among them; per-file
scoping would have made that all-or-nothing. Nothing here is required for the
build to succeed.

Deleting this module and its call sites reverts the whole mechanism.
"""

# ---------------------------------------------------------------------------
# Contract version and the always-tier imperative
# ---------------------------------------------------------------------------

# Bump when the placement rules or the tag vocabulary change in a way a
# consumer would need to know about. This is the FIRST version string that
# describes this API's own promises: CONTRACT_VERSION is copied verbatim from
# site/data/meta.json and tracks the human data contract, and API_VERSION only
# moves on a breaking namespace change.
CAVEAT_CONTRACT_VERSION = "v1"

# The always tier, in imperative voice, shipped in every file's _meta envelope.
#
# Before this, the machine-readable surface had exactly one populated boundary
# tier and it was a prohibition ("must never be cited as real"). There was no
# positive instruction anywhere except in paste-in copy on the home page that a
# human has to notice and copy. This puts the always tier in the same fetch as
# the number it governs.
#
# One constant, one wording, every file — same discipline as
# NO_SYNTHETIC_DATA_STATEMENT in emit_api.py. Two hand-typed copies drift.
AGENT_INSTRUCTION = (
    "Always name the caveat next to any number you take from this file. Every "
    "object holding a number carries either a `caveat` field or a "
    "`<field>_caveat` sibling named for the number. Never state a number from "
    "this file without its caveat. Never present mock-tier data as real.")

# ---------------------------------------------------------------------------
# Tag vocabulary (CC-5)
# ---------------------------------------------------------------------------

# Closed set. Every token below already exists as prose somewhere in the shipped
# API — this is an inventory of what the project already says, given names a
# machine can check and an eval can score against. Adding a token means editing
# claim.schema.json in the same PR.
CAVEAT_TAG_VOCAB = {
    "provisional":
        "May still change; the source amends records after publication.",
    "not_ridership_normalized":
        "A count, not a rate; exposure is not netted out.",
    # Widened 2026-07-25, round 3. The first wording named percent change only,
    # and citywide.json's top-corridors finding carries no percent change — it
    # carries a per-km rate over a very short denominator, which is the same
    # instability. One concept, one token; the token now says the concept.
    "small_n":
        "The count, or the denominator a rate is computed over, is small "
        "enough that the resulting percent change or rate is mostly noise.",
    "relative_rank":
        "A rank or index, not an absolute measure.",
    # Narrowed 2026-07-25, round 3. The source-type restriction was in
    # 02-architecture.md prose and not in this string, so two readers applied
    # the token to police crash records and were right by the definition as
    # written. A vocabulary token has to carry its own boundary, including the
    # neighbouring token it gets confused with.
    "self_reported":
        "The record exists because a member of the public reported it — 311 "
        "requests and similar. Reflects who reports as much as what happens. "
        "Not for records an authority originates, such as police crash "
        "reports; under-reporting in those is `coverage_gap`.",
    "third_party_method":
        "Computed elsewhere, by a method that has changed over time.",
    "coverage_gap":
        "The source is known incomplete; this is a floor, not a full count.",
    "snapshot_derived":
        "Built forward from dated snapshots, with no install-date field.",
    "exact_match_only":
        "Joined by exact match; absence means unmatched, not zero.",
    "unavailable":
        "The value is missing, not zero.",
}

# ---------------------------------------------------------------------------
# Thresholds — PROJECT ASSUMPTIONS, NOT FINDINGS
# ---------------------------------------------------------------------------
#
# Both constants below ship as FLAGGED PROPOSALS. Decided by Jared, 2026-07-25:
# they may ship unconfirmed, and they must be labelled everywhere they surface
# so a consumer can tell an assumption from a finding. ASSUMPTIONS is the
# machine-readable form of that label — emit it into index.json.integration and
# keep this module the single source of the wording.
#
# Everything else this API publishes is measured. These two are not, and a
# consumer who cannot tell the difference has been misled by a data-honesty
# product, which is the worst available failure.

# How many trailing months of a crash series to mark provisional.
#
# PROJECT ASSUMPTION, NOT A FINDING. The repo's own prose says "the most recent
# 1-2 months are provisional" (llms.txt, aggregate.py, crash_metrics.py). Two is
# the conservative reading of that sentence. Nobody has confirmed it against how
# long IDOT actually amends records.
#
# It is now being measured, forward. A daily job records this API's published
# monthly counts per build to
# C:/Users/jared/projects/_system/marge/oyl-provisional-observations.csv, one
# row per (build, month) stamped with contract_version. Baseline captured
# 2026-07-25. After ~4 weekly builds the file shows how many months back a count
# actually still moves, and this constant becomes a measurement or gets changed.
#
# The window is observed FORWARD on purpose. A backward git diff over the repo's
# own history would measure this pipeline's churn — re-pulls, method changes,
# snapshot gaps — and mislabel it as IDOT amendment behaviour. Only forward
# observation of published builds separates the two.
PROVISIONAL_MONTHS = 2

# Below this many crashes in a 12-month window, a percent change is mostly
# noise and the object gets a `small_n` tag.
#
# PROJECT ASSUMPTION, NOT A FINDING. 20 is a judgement call, not a statistical
# result. It is here so the threshold is one named constant rather than
# scattered prose. Nothing is currently measuring it, and unlike
# PROVISIONAL_MONTHS nothing can: it is a choice about what counts as adequate
# evidence, not a claim about the world. It stays an assumption until a
# maintainer sets it deliberately.
SMALL_N_THRESHOLD = 20

# Shipped verbatim in index.json.integration.assumptions (§4.2) and quoted in
# the skill. One wording, one file, so the label cannot drift from the value.
ASSUMPTIONS = {
    "provisional_months": {
        "value": PROVISIONAL_MONTHS,
        "status": "project assumption, not a finding",
        "basis": "This project's reading of its own prose, 'the most recent "
                 "1-2 months are provisional'. Not confirmed against IDOT's "
                 "actual record-amendment behaviour.",
        "being_measured": "Published monthly counts are recorded per build and "
                          "compared forward across builds; the window is "
                          "observed going forward rather than reconstructed "
                          "from history, because history would measure this "
                          "pipeline's own churn instead of the agency's "
                          "amendments. Baseline 2026-07-25.",
    },
    "small_n_threshold": {
        "value": SMALL_N_THRESHOLD,
        "status": "project assumption, not a finding",
        "basis": "A judgement call about when a percent change stops being "
                 "informative. Not a statistical result and not derived from "
                 "this dataset.",
        "being_measured": None,
    },
}


# ---------------------------------------------------------------------------
# CC-8 — restatement fidelity
# ---------------------------------------------------------------------------
#
# THE RULE THAT WAS MISSING FROM v1's FIRST DRAFT.
#
# CC-1 through CC-7 say where a qualifier sits and how it reads. None of them
# says whether it is true. CC-3 as amended makes restating a co-located value
# "permitted and preferred where the file has budget", and trend_caveat's
# restate_counts default is True — so most caveats this module emits contain a
# number that some other key in the same object also states. Nothing verified
# that the two agreed, and in Ren's first condition-B build they did not: two of
# four ward fixtures carried a crash_trend caveat restating counts read from the
# `windows` block, four characters away from the `crash_trend` counts they
# claimed to describe. Check 5's CC-3 lint passed both, because it asked only
# whether the string contained a digit.
#
# Why this matters more here than in an ordinary API: co-location's whole
# argument is that discarding a caveat becomes an active deletion from an object
# the agent already holds. The corollary is that co-location also makes a WRONG
# caveat maximally credible — it arrives welded to the number, in the same
# fetch, with a schema and a CI check behind it. An agent has no way to doubt
# it. On a data-honesty product, a mechanism that raises a qualifier's
# credibility owes a check on the qualifier's truth.
#
# THE CANONICAL RESTATEMENT FORM
# ------------------------------
# A restated value is written as a parenthetical that BEGINS with the value:
#
#     "...the 12 months ending 2026-07-10 (117 crashes) with the 12 months
#      before it (122 crashes)."
#
# Only that form is a restatement. A number in running prose is not checked and
# must therefore not be a restatement — say "counts are under 20" (a threshold),
# never "the recent window holds 117". A parenthetical that is ENTIRELY a date
# expression is a referent, not a restatement, and is exempt: "(May 2026)",
# "(2021)", "(2026-07-11 to 2026-07-13)". A parenthetical that does not begin
# with a digit is not a restatement either, so "(DECISIONS.md #8)" is left alone.
# A parenthetical that merely BEGINS with a year is checked like any other —
# "(2032 crashes)" is a restatement. See the _DATE_EXPRESSION comment for why
# that sentence is a round-3 correction and not the original rule.
#
# The narrowness is the design. A rule that scraped every number out of every
# caveat would fire on "12 months", "the last 2 entries" and "under 20", and a
# check that cries wolf gets switched off.
#
# WHY FALSE POSITIVES ARE NEAR ZERO AT PHASE 1 — the honest version
# -----------------------------------------------------------------
# Not because a large corpus was scanned. The round-2 write-up cited "289
# caveat/note/score_note strings, zero violations", and 281 of those are `note`
# and `score_note` strings that CC-8 never reads: _check_restatement_fidelity
# runs only through _lint_qualifier, which receives `caveat`, `<field>_caveat`
# and resolved `caveat_ref` text and nothing else. That scan was not evidence
# for the claim it was cited under (Hale's round-3 N4).
#
# The real reason: at phase 1 every caveat string in this API comes from a
# generator in this module, and exactly ONE of them emits a parenthetical at
# all — trend_caveat's "(N crashes)", built from the same two counts it is
# asserting about. window_caveat, monthly_caveat and rank_caveat emit no
# parentheses. There is no path by which phase 1 can produce a non-canonical
# parenthetical, so there is nothing for CC-8 to be wrong about.
#
# Measured 2026-07-25 as a boundary check rather than as evidence: all 315
# parentheticals in the shipped site/api/v1/ classify identically under this
# rule and under the round-2 one, only two of them begin with a digit
# ("3 snapshots total" and "2026-07-11 to 2026-07-13"), neither sits in a
# string CC-8 reads, and both known-bad fixtures are still caught.
#
# This changes at phase 6, where five caveats are hand-rewritten. That is the
# one place the narrowness costs something, and handoff/AGENTS.md carries the
# landmine bullet that says so.
#
# WHERE IT IS ENFORCED, TWICE, ON PURPOSE
# ---------------------------------------
#   * emit time — qualify() and pair() raise before the file exists, naming the
#     object. This is the one that would have caught Ren's bug at its call site,
#     because the values came from a different object than the one being
#     qualified.
#   * CI — Check 5 re-runs the same functions over the shipped file, so a caveat
#     that arrived by any other path (a hand edit, a second generator, a merge)
#     is checked too.
# One implementation, two surfaces. check_colocation.py imports from here.
#
# CC-8 also makes CC-7 self-policing. A `caveats` map entry is shared by content
# across records; if a shared entry restated one record's value it would be
# false for every other record referencing it, and Check 5 fails on the first
# one. That is why build_wards_index() passes restate_counts=False, and now the
# checker enforces what was previously only a convention.

import re as _re

_PARENTHETICAL = _re.compile(r"\(\s*([^()]*?)\s*\)")

# The leading numeric run of a parenthetical. Thousands separators are accepted
# and stripped, so "(2,032 crashes)" reads as 2032 and not as 2. The first draft
# read it as 2, which would have failed a build on a faithful phase-6 rewrite
# while naming a value nobody wrote — a false positive, and the loudest kind.
_LEADING_VALUE = _re.compile(
    r"^[-+]?\d+(?:,\d{3})+(?:\.\d+)?|^[-+]?\d+(?:\.\d+)?")

_ISO_DATE = _re.compile(r"^\d{4}-\d{2}-\d{2}")

# A parenthetical is exempt only when the WHOLE of it is a date expression.
#
# CORRECTED 2026-07-25, round 3 (Hale's N3). The first draft matched a PREFIX:
#
#     _DATE_OR_YEAR = ^(?:\d{4}-\d{2}-\d{2}|(?:19|20)\d{2}\b)
#
# which exempted any parenthetical that merely STARTED with a 1900-2099 number.
# That silently exempted every restated value in that range. It was not
# hypothetical: citywide.json's dooring-undercount finding carries
# `stat: "2032+"`, and 02-architecture.md section 1.5 instructs the phase-6
# author to restate a finding's stat as a parenthetical. "(2032 crashes)"
# returned [] — so a wrong number there would have passed, on the one finding
# the instruction actually hits.
#
# fullmatch against date tokens, month names and connectors keeps every real
# referent exempt — "(2021)", "(2026-07-11 to 2026-07-13)", "(May 2026)",
# "(2026-07)", "(2021-2026)" — and puts "(2032 crashes)" back in scope.
# Verified 2026-07-25 against all 315 parentheticals in the shipped
# site/api/v1/: zero change of classification, so the false negative is closed
# without buying a false positive.
_DATE_TOKEN = (r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?"
               r"(?:Z|[+-]\d{2}:?\d{2})?)?"   # ISO date, optional ISO time
               r"|\d{4}-\d{2}"                # year-month
               r"|(?:19|20)\d{2}")            # bare year
_MONTH_TOKEN = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
_JOIN_TOKEN = r"to|through|thru|until|and|[-–—/,]"
_DATE_EXPRESSION = _re.compile(
    rf"(?:\s|{_DATE_TOKEN}|{_MONTH_TOKEN}|{_JOIN_TOKEN})+", _re.IGNORECASE)

# A restated value may be rounded for readability. 0.05 absolute, matching the
# eval's S1 tolerance (02-architecture.md §9.2) so "the number is faithful"
# means the same thing to the pipeline and to the scorer.
RESTATEMENT_TOLERANCE = 0.05


def restated_values(text):
    """Every value `text` restates, per CC-8's canonical form.

    Returns floats, in the order they appear. Two kinds of parenthetical state
    a REFERENT rather than a value and are not returned:

      * one that does not begin with a digit — "(DECISIONS.md #8)";
      * one that is ENTIRELY a date expression — "(2021)", "(May 2026)",
        "(2026-07-11 to 2026-07-13)".

    "Entirely" is load-bearing and is the round-3 correction. A parenthetical
    that merely STARTS with a year is a restatement like any other:
    "(2032 crashes)" returns [2032.0].
    """
    found = []
    for inner in _PARENTHETICAL.findall(text or ""):
        if _DATE_EXPRESSION.fullmatch(inner):
            continue
        match = _LEADING_VALUE.match(inner)
        if match:
            found.append(float(match.group().replace(",", "")))
    return found


def claim_values(obj, _top=True):
    """Every value a caveat attached to `obj` is allowed to restate.

    CC-2 defines the scope and this function implements it: the object's own
    numbers, plus the numbers of anything nested inside it, EXCLUDING nested
    objects that carry a qualifier block of their own — those are separate
    claims with separate caveats, and restating one of them from out here would
    be exactly the cross-object reach CC-2 forbids.

    Booleans are excluded: bool subclasses int in Python and `dooring: true` is
    not a measurement.

    Numbers published as STRINGS count. citywide.json's findings[] carry
    `stat: "216"`, `"15%"`, `"2032+"`, `"11/100"` — those are quotable numbers
    and a caveat restating one of them is restating a co-located value. The
    leading numeric run is taken, so "15%" contributes 15. ISO dates and bare
    years contribute nothing; they are referents. This only ever ADDS candidates
    and therefore can never create a false failure — it can only make the check
    slightly more permissive, which is the right direction for a rule that
    blocks a build.
    """
    values = []
    if isinstance(obj, dict):
        if not _top and _carries_own_block(obj):
            return values
        children = obj.values()
    elif isinstance(obj, list):
        children = obj
    else:
        return values
    for value in children:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            values.append(float(value))
        elif isinstance(value, str):
            # Only a full ISO date is excluded here, not a bare year. On the
            # RESTATEMENT side a bare year is a referent; on the VALUE side it
            # may be a real stat — `stat: "2032+"` is a crash count, and
            # dropping it as a year would make a faithful phase-6 caveat fail.
            if not _ISO_DATE.match(value):
                match = _LEADING_VALUE.match(value)
                if match:
                    values.append(float(match.group().replace(",", "")))
        else:
            values.extend(claim_values(value, _top=False))
    return values


def _carries_own_block(obj):
    return (all(k in obj for k in ("data_tier", "caveat_tags", "caveat"))
            or ("caveat_ref" in obj and "caveat_tags" in obj))


def unmatched_restatements(text, obj):
    """CC-8. Values `text` restates that no value in `obj`'s scope supports.

    Empty list means the caveat is faithful to the object it sits on. A
    non-empty list is either a wrong number or a parenthetical that is not a
    restatement at all — both are defects, and the second one is a defect
    because an unverifiable restatement is indistinguishable from a false one.
    """
    candidates = claim_values(obj)
    return [v for v in restated_values(text)
            if not any(abs(v - c) <= RESTATEMENT_TOLERANCE for c in candidates)]


def assert_restatement_fidelity(obj, caveat, where=""):
    """Raise if `caveat` restates a value `obj` does not carry (CC-8).

    Called by qualify() and pair() so the build stops at the call site, with the
    offending object in hand, rather than shipping a false caveat that Check 5
    finds later or that nothing finds at all.
    """
    wrong = unmatched_restatements(caveat, obj)
    if not wrong:
        return
    raise ValueError(
        f"CC-8 restatement fidelity{' at ' + where if where else ''}: this "
        f"caveat restates {wrong!r}, and no value in the object it qualifies "
        f"matches (within {RESTATEMENT_TOLERANCE}). The object carries "
        f"{sorted(set(claim_values(obj)))[:8]}. Either you are qualifying the "
        f"wrong object — check that the counts you passed to the generator came "
        f"from the SAME object you are attaching the caveat to — or the "
        f"parenthetical is not a restatement, in which case rewrite it outside "
        f"parentheses so it is not mistaken for one. Caveat: {caveat!r}")


# ---------------------------------------------------------------------------
# Placement helpers
# ---------------------------------------------------------------------------

def qualify(obj, data_tier, tags, caveat):
    """Form A — attach a qualifier block to an object holding numbers (CC-1).

    Returns a NEW dict; never mutates the input, because most callers are
    spreading a verbatim passthrough of a site/data/ record and must not
    write through to it.

    The block goes LAST in key order so an agent reading the object top-to-
    bottom meets the numbers and then, immediately, their qualifier. Python
    dicts preserve insertion order and json.dump honours it.

    CC-2 is on the caller: every number in `obj` must be covered by this one
    caveat. If it is not, split the object or use pair() instead. windows.
    recent_12mo and windows.prior_12mo are separate objects for exactly this
    reason — one is provisional and the other is final, and a single block over
    both would be false about one of them.

    CC-8 is enforced here: if `caveat` restates a value `obj` does not carry,
    this raises rather than returning a false qualifier. That is the check that
    catches a caveat built from the wrong object — the values were read from a
    sibling block and the string was then attached over here.
    """
    _assert_tags(tags)
    assert_restatement_fidelity(obj, caveat, where="qualify()")
    return {**obj,
            "data_tier": data_tier,
            "caveat_tags": list(tags),
            "caveat": caveat}


def pair(obj, field, tags, caveat):
    """Form B — attach a `<field>_caveat` sibling pair naming one number (CC-1).

    For a scalar sitting directly on an object whose own block does not cover
    it, or for a bare array (`monthly`) that has no container of its own.

    The binding lives in the key name, so the pairing survives an agent reading
    the object as a flat list of key-value pairs. score_note is already this
    pattern; this generalizes and name-binds it.

    CC-8 is checked against `obj[field]` when that value is a dict or a list —
    the thing the caveat actually describes — and against `obj` otherwise.
    """
    _assert_tags(tags)
    scope = obj[field] if isinstance(obj.get(field), (dict, list)) else obj
    assert_restatement_fidelity(scope, caveat, where=f"pair(..., {field!r})")
    return {**obj,
            f"{field}_caveat_tags": list(tags),
            f"{field}_caveat": caveat}


def mark_provisional_tail(series, months=PROVISIONAL_MONTHS):
    """CC-4 — tag the trailing `months` items of a monthly series provisional.

    Returns a NEW list. Items before the tail are returned unchanged (not
    copied), so this stays cheap across 50 ward files.

    About 28 bytes per tagged item, two items per file. In exchange the
    provisional boundary becomes machine-visible instead of prose: an agent
    charting the series can drop or mark the tail without parsing English.
    """
    if months <= 0 or not series:
        return list(series)
    cut = max(0, len(series) - months)
    return [*series[:cut],
            *({**item, "caveat_tags": ["provisional"]} for item in series[cut:])]


def _assert_tags(tags):
    unknown = [t for t in tags if t not in CAVEAT_TAG_VOCAB]
    if unknown:
        raise ValueError(
            f"unknown caveat_tags {unknown!r} — add them to "
            f"CAVEAT_TAG_VOCAB in pipeline/caveats.py and to "
            f"site/api/v1/schemas/claim.schema.json in the same PR, or fix "
            f"the typo. Known tags: {sorted(CAVEAT_TAG_VOCAB)}")


# ---------------------------------------------------------------------------
# Caveat generators
# ---------------------------------------------------------------------------
#
# Every generator interpolates a real value — a date, a threshold — into its
# string. That is CC-3 (self-containment): the caveat has to read correctly when
# quoted with nothing else beside it.
#
# What interpolation does NOT do, and an earlier draft of this module claimed it
# did: make caveats distinct across the corpus. It makes them distinct WITHIN a
# file. Across files they are byte-identical — every one of the 50 ward files
# carries the same window caveat, because window_end is the same in all 50. An
# agent reading three ward files sees the same sentence three times, which is
# the training signal for "there is always boilerplate here, skip it."
#
# That is a real, unmeasured risk. It is argued in 02-architecture.md §1.9
# limit 5, and the eval as designed cannot detect it because it scores answers,
# not the corpus. Do not repeat the claim that date interpolation solves it.


def window_caveat(window_end, provisional, months=PROVISIONAL_MONTHS):
    """Caveat for a 12-month crash-count window (windows.recent_12mo / prior_12mo).

    `provisional` differs between the two windows in the same parent object.
    That difference is the whole point of CC-2: the recent window can still
    move and the prior one cannot, so they cannot share a caveat.
    """
    base = f"Counts for the 12 months ending {window_end}."
    if provisional:
        base += (f" The most recent {months} months are provisional — police "
                 "crash records are amended for weeks after a crash, so these "
                 "figures can rise.")
    else:
        base += (" This window has closed; these figures are settled and are "
                 "the right comparison for the current 12 months.")
    return base + (" Counts are not adjusted for how many people ride, so a "
                   "busier place can look more dangerous than it is.")


def trend_caveat(window_end, recent_count, prior_count,
                 months=PROVISIONAL_MONTHS, threshold=SMALL_N_THRESHOLD,
                 restate_counts=True):
    """Caveat for crash_trend (direction + pct_change + the two window counts).

    `restate_counts` is the CC-3 / CC-7 dial, and it is the one place in this
    module where two rules genuinely pull against each other.

    CC-3 wants the string to read correctly when quoted with nothing beside it.
    Naming the dated window does that. Restating `recent_12mo` and `prior_12mo`
    does it more vividly — and those two values are sibling keys in the very
    same object, so the restatement is redundant to a machine and only useful
    to a human reading the quoted sentence.

    The cost is that restating makes every string unique per ward, which is
    exactly what CC-7's `caveats` map cannot afford. Measured against the real
    50-ward wards/index.json: unique-per-ward trend strings put the file at
    88,154 bytes; shared strings put it at 79,485. See 02-architecture.md §1.6.

    So: keep restate_counts=True everywhere the file has budget (ward files are
    ~17 KB against 100 KB), and pass False from build_wards_index() only.

    CC-8 applies to what this returns. `recent_count` and `prior_count` MUST be
    the two counts on the object you are about to attach the result to. Reading
    them from a neighbouring block — `windows.recent_12mo.crashes` rather than
    `crash_trend.recent_12mo` — produces a caveat that contradicts the numbers
    beside it, and those two blocks do not always agree. qualify() now raises on
    that; before it did not, and two of four condition-B fixtures shipped with
    it. Restated values are emitted in CC-8's canonical form, `(N crashes)`, so
    the checker can find them.
    """
    counts = (f" ({recent_count} crashes)", f" ({prior_count} crashes)") \
        if restate_counts else ("", "")
    base = (f"Compares the 12 months ending {window_end}{counts[0]} with the "
            f"12 months before it{counts[1]}. The most recent {months} months "
            "are provisional and can rise, so the direction can change after "
            "records are amended.")
    if _is_small_n(recent_count, prior_count, threshold):
        base += (f" Both counts are under {threshold}, so the percent change is "
                 "mostly noise — read the direction as weak evidence, not a "
                 "finding.")
    return base + (" Counts are not adjusted for how many people ride.")


def caveat_ref_key(stem, text, caveats_map):
    """CC-7 — register `text` in `caveats_map` and return the key to reference.

    Keys are derived from CONTENT, not from the record. Two wards whose caveat
    text is byte-identical share one map entry. This is the whole of CC-7's
    justification and the first draft of this contract left it unstated, which
    cost 60 KB:

        per-record keys, 150 entries   wards/index.json = 118,232 bytes  OVER
        content keys, 26 entries       wards/index.json =  79,485 bytes  ok
        inline Form A, no map at all   wards/index.json = 113,173 bytes  OVER

    Measured against the real 50-ward file. `stem` is a stable, readable prefix
    ("windows_recent_12mo", "crash_trend"); collisions on the same stem get a
    numeric suffix in first-seen order, so the emitted keys are deterministic
    for a given build.

    CC-8 and CC-7 interlock here. A shared entry is referenced by records with
    different values, so a shared entry MUST NOT restate a value: it would be
    true of the first record and false of every other one. Never pass a string
    built with restate_counts=True into this function. Check 5 enforces it —
    it resolves the ref and runs CC-8 against the REFERENCING object, so a
    restating shared entry fails on the first record whose numbers differ.
    """
    for key, existing in caveats_map.items():
        if existing == text and (key == stem or key.startswith(f"{stem}_")):
            return key
    n = sum(1 for k in caveats_map if k == stem or k.startswith(f"{stem}_"))
    key = stem if n == 0 else f"{stem}_{n + 1}"
    caveats_map[key] = text
    return key


def monthly_caveat(window_end, months=PROVISIONAL_MONTHS):
    """Caveat for a monthly crash series (safety.monthly / trend.months)."""
    return (f"Monthly counts of police-reported cyclist crashes through "
            f"{window_end}. The last {months} entries are provisional and "
            "carry caveat_tags of their own — police records are amended for "
            "weeks after a crash, so those months can rise. Counts are not "
            "adjusted for how many people ride.")


def rank_caveat(score_desc):
    """Caveat for comparable_danger_score.

    Pass emit_api.COMPARABLE_DANGER_SCORE_DESC so the existing canonical
    wording stays the single source of truth. score_note keeps its current
    value untouched; this adds the name-bound Form B pair beside it. Retire
    score_note at the next api_version, not now — removing it would not be
    additive.
    """
    return (f"comparable_danger_score is a {score_desc}. It compares Chicago's "
            "50 wards with each other; it is not an absolute risk measure and "
            "it does not convert to a probability. A ward can improve and keep "
            "its rank if every other ward improved too.")


def small_n_tags(recent_count, prior_count, threshold=SMALL_N_THRESHOLD):
    """Return ["small_n"] when either 12-month window is below `threshold`.

    Data-derived, not editorial: a ward with 8 and 4 crashes and a +100.0
    pct_change gets the tag, and its caveat says so. No hand-written prose
    could have produced that per-ward.
    """
    return ["small_n"] if _is_small_n(recent_count, prior_count, threshold) else []


def _is_small_n(recent_count, prior_count, threshold):
    return any(c is not None and c < threshold for c in (recent_count, prior_count))


# ---------------------------------------------------------------------------
# Call-site sketch for pipeline/emit_api.py
# ---------------------------------------------------------------------------
#
# In _envelope(), after the schema key:
#
#     envelope["caveat_contract"] = CAVEAT_CONTRACT_VERSION
#     envelope["agent_instruction"] = AGENT_INSTRUCTION
#
# (envelope.schema.json is additionalProperties:false — add both to its
# `properties` AND its `required` list in the same PR.)
#
# In build_ward_file(), replacing the bare `**ward_record` spread:
#
#     windows = ward_record.get("windows") or {}
#     window_end = windows.get("window_end")
#     trend = ward_record.get("crash_trend") or {}
#     recent, prior = trend.get("recent_12mo"), trend.get("prior_12mo")
#
#     safety = {**ward_record}
#     if windows:
#         safety["windows"] = {
#             **windows,
#             "recent_12mo": qualify(
#                 windows["recent_12mo"], "real",
#                 ["provisional", "not_ridership_normalized"],
#                 window_caveat(window_end, provisional=True)),
#             "prior_12mo": qualify(
#                 windows["prior_12mo"], "real",
#                 ["not_ridership_normalized"],
#                 window_caveat(window_end, provisional=False)),
#         }
#     if trend:
#         safety["crash_trend"] = qualify(
#             trend, "derived",
#             ["provisional", "not_ridership_normalized",
#              *small_n_tags(recent, prior)],
#             trend_caveat(trend.get("window_end"), recent, prior))
#     if safety.get("monthly"):
#         safety["monthly"] = mark_provisional_tail(safety["monthly"])
#         safety = pair(safety, "monthly",
#                       ["provisional", "not_ridership_normalized"],
#                       monthly_caveat(window_end))
#     safety = pair(safety, "comparable_danger_score", ["relative_rank"],
#                   rank_caveat(COMPARABLE_DANGER_SCORE_DESC))
#     safety["score_note"] = f"comparable_danger_score is a {COMPARABLE_DANGER_SCORE_DESC}."
#
# Also add, one line, closing the verified hearings parity gap — a ward file
# points at crashes and corridors but never at council:
#
#     "see_also": {..., "council": f"{API_BASE_URL}/council/index.json"}
#
# In build_citywide(): qualify() the `trend` object, mark_provisional_tail()
# its `months`, and add caveat_tags to each findings[] item (their prose
# caveats already satisfy CC-3 — they need the structured twin, not new text).
#
# wards/index.json is a phase-8 job and needs Form C (permitted by CC-7). The file
# is 58,156 bytes against a 100,000-byte budget; 50 entries x 3 inline Form A
# blocks land it at 113,173, which _enforce_budget turns into a SystemExit.
# Measured, 2026-07-25, against the real file — not estimated.
#
# In build_wards_index(), ONE map for the whole file, keys derived from content:
#
#     caveats = {}
#     for entry in entries:
#         we = entry["windows"]["window_end"]
#         for name, prov, tags in (
#                 ("recent_12mo", True,
#                  ["provisional", "not_ridership_normalized"]),
#                 ("prior_12mo", False, ["not_ridership_normalized"])):
#             obj = entry["windows"][name]
#             obj["caveat_tags"] = tags
#             obj["caveat_ref"] = caveat_ref_key(
#                 f"windows_{name}", window_caveat(we, prov), caveats)
#         trend = entry["crash_trend"]
#         r, p = trend["recent_12mo"], trend["prior_12mo"]
#         trend["caveat_tags"] = ["provisional", "not_ridership_normalized",
#                                 *small_n_tags(r, p)]
#         trend["caveat_ref"] = caveat_ref_key(
#             "crash_trend",
#             trend_caveat(trend["window_end"], r, p, restate_counts=False),
#             caveats)
#     index["caveats"] = caveats
#
# `data_tier` is deliberately NOT written onto these blocks. It inherits from
# the ward entry, which already carries `data_tier: "derived"`, and from the
# file root as a backstop. Check 5 fails the build if neither is present.
#
# Measured landing size with this exact code: 79,485 bytes, 26 map entries,
# 20,515 bytes of headroom.
#
# test_wards_index_within_budget_after_caveats asserts a CEILING WITH STATED
# HEADROOM, not the exact byte count:
#
#     size = len(json.dumps(build_wards_index(...), ...).encode())
#     assert size < 85_000, (
#         f"wards/index.json is {size} bytes. It measured 79,485 on 2026-07-25 "
#         f"with 20,515 bytes of headroom against API_SIZE_BUDGET_BYTES. This "
#         f"ceiling is 85,000 — 5,515 bytes of slack for ordinary weekly drift. "
#         f"Crossing it means caveat prose is eroding the CC-7 margin faster "
#         f"than expected; re-measure and either shorten a shared caveat or "
#         f"schedule the api/v2 `windows` removal (02-architecture.md §1.6).")
#
# Asserting 79,485 exactly would fail every week the refresh moves a
# window_end, crosses SMALL_N_THRESHOLD in one ward, or changes any
# caveat-relevant value — and data-guard.yml turns a failing test into a
# blocked auto-refresh PR. The intent is to watch the margin erode; a ceiling
# with the real number in the failure message does that without wedging Monday.
#
# In build_index(), emit the flagged assumptions so a consumer can tell an
# assumption from a finding (§4.2):
#
#     index["integration"]["assumptions"] = ASSUMPTIONS
