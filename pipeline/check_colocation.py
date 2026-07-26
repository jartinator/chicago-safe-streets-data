"""Check 5 — the caveat co-location contract, for pipeline/check_api.py.

Lands as: pipeline/check_colocation.py, called from check_api.py's main()
after _check_version_coherence(). The studio's draft proposed pasting this into
check_api.py; it is a separate module instead, matching the repo's flat-module
convention (caveats.py, config.py) and keeping a 280-line CI entry point from
being dominated by a 600-line check. Abandonable by deleting one import.

Follows check_api.py's existing conventions: no network, first failure wins,
sys.exit(1) with a message naming the file, the JSON path, and the fix.

REVISION 2026-07-25 — SCOPE IS A JSON PATH, NOT A FILE
------------------------------------------------------
The first draft of this checker walked every object in an enforced file and
demanded a qualifier for every numeric key in it. Run against the real output of
caveats.py it produced 346 violations on four files, including all 107 `monthly`
items and every number phase 1 does not touch. It would have hard-stopped the
repo the moment `wards/ward-*.json` was added to the enforced list, and because
the scope was per FILE there was no partial enable — the only exits were
reverting or migrating the entire file in one PR.

Scope is now per JSON path. COLOCATION_ENFORCED_CLAIMS maps a file glob to the
list of claim paths inside it that have actually been migrated. Everything else
in the file is unenforced and passes untouched. That is what makes the migration
abandonable partway *and* resumable one claim at a time: land phase 1, list the
five paths phase 1 produces, stop. Phase 2 adds five more lines.

Two other defects from the same run are fixed here:

  * CC-4's container rule is implemented. A `<array>_caveat` pair on the object
    holding an array covers that array's items; items may carry a tags-only
    override, which is `$defs.item_override` in claim.schema.json. The first
    draft never referenced that $def and failed every item.
  * A CC-7 `caveat_ref` block may omit `data_tier` and inherit it from the
    nearest enclosing object that declares one. wards/index.json declares
    `data_tier` at the file root and again on each ward entry, so the tier is
    always resolvable inside the same fetch. Requiring it on every ref block
    spent ~3 KB in the one file that exists to save bytes.

SELECTOR GRAMMAR
----------------
    safety/crash_trend            an OBJECT claim. Every numeric key in that
                                  object must be covered by a Form A block, a
                                  CC-7 ref block, or per-key Form B pairs.
    wards[*]/crash_trend          `[*]` iterates an array. `*` alone matches any
                                  one key.
    safety#comparable_danger_score
                                  a FIELD claim. Only that one numeric key on
                                  the matched object must be covered.
    safety#monthly                a field claim whose value is an ARRAY. CC-4:
                                  the `monthly_caveat` pair on `safety` covers
                                  every item; items may add caveat_tags only.

A selector that matches nothing IN ANY FILE UNDER ITS GLOB is a failure. A
selector that matches nothing in ONE file is not — see the next section.

Run `python pipeline/check_api.py --audit-colocation` to list every numeric
claim in site/api/v1/ that no selector covers, deduplicated across files and
array indices. That is the migration backlog, and it never exits non-zero.

REVISION 2026-07-25 (round 2) — THREE CHANGES
---------------------------------------------
1. CC-8, restatement fidelity, is enforced (`_check_restatement_fidelity`).
   Every value a caveat restates must equal a value in the claim's own scope.
   This is the only check in the package capable of catching a caveat that is
   FALSE rather than merely misplaced, and the amended CC-3 — which made value
   restatement the default — created that class of defect without it. The
   extraction and comparison live in caveats.py so the emit-time assert and this
   CI check are one implementation, not two that can drift.

2. CC-2 is enforced where it was silently violable. A FIELD selector
   (`safety#monthly`) now requires a Form B pair named for that field. An
   enclosing Form A block no longer satisfies it. Before this, stapling one
   block onto `safety` — the architecture spec's own worked example of a scope
   violation — passed Check 5 for both of phase 1's field claims. A field
   selector exists precisely because that number needs its OWN qualifier; if the
   object's block genuinely covers it, use an object selector instead.
   CC-2 is still only PARTLY checkable: whether a block's caveat is true of
   every number in its object is a semantic question, and the guard for that is
   `test_ward_prior_window_is_not_tagged_provisional` plus review.

3. A missing selector is a per-glob failure, not a per-file failure. The old
   rule turned a legitimate data condition into a blocked Monday PR: a refresh
   that emits one ward without `crash_trend`, or that uses the repo's own
   `{"available": false}` shape for a missing window (DECISIONS.md, "never
   invent zeros"), made `check_api.py` exit 1 with no partial exit. Now a
   selector must resolve in AT LEAST ONE file matching its glob; files where it
   is absent are reported, not fatal. `{"available": false}` subtrees are
   skipped explicitly, because "this data is missing" is a stated condition and
   a missing number needs no caveat.

REVISION 2026-07-25 (round 3) — ONE CHANGE, IN caveats.py
---------------------------------------------------------
CC-8's date exemption matched a PREFIX and now requires a FULL match. A
parenthetical that merely began with a 1900-2099 number was exempt, which made
every restated value in that range invisible — "(2032 crashes)", the
dooring-undercount stat a phase-6 rewrite is instructed to restate, returned no
values at all. Nothing in this file changed except the wording of the CC-8
failure message; the fix is in caveats.restated_values(), which this file
imports rather than reimplements. That is the payoff of the one-implementation
decision: a false negative in a truth rule was fixed in one place.

WHAT THIS CHECK NEVER READS. `_check_restatement_fidelity` runs only through
`_lint_qualifier`, which receives `caveat`, `<field>_caveat` and resolved
`caveat_ref` text. `note` and `score_note` are never passed to it — they
describe what the data IS, not how it can mislead, and they are outside the
contract. Do not cite a corpus scan over them as evidence about this check.
"""
import fnmatch
import re
import sys

from caveats import (CAVEAT_TAG_VOCAB, RESTATEMENT_TOLERANCE, claim_values,
                     restated_values, unmatched_restatements)

# Claim paths Check 5 enforces, per file glob. Grow one line per migration PR.
#
# Each line is a path someone has actually migrated. Adding a file to this map
# does NOT enforce the whole file — only the listed claims. That is deliberate:
# a ward file holds ~130 numbers and phase 1 qualifies five claims among them.
COLOCATION_ENFORCED_CLAIMS = {
    # Phase 1 — §1.4 items 1-5.
    "wards/ward-*.json": [
        "safety/windows/recent_12mo",       # Form A, provisional
        "safety/windows/prior_12mo",        # Form A, settled — the CC-2 pair
        "safety/crash_trend",               # Form A
        "safety#monthly",                   # Form B on the container (CC-4)
        "safety#comparable_danger_score",   # Form B on a scalar
    ],

    # Phase 2 — uncomment each line in the PR that emits it.
    #   "safety#crashes_per_10k_pop",
    #   "safety#crashes_per_bikeway_mile",
    #   "safety#bikeway_pct_protected",
    #   "safety#bikeway_pct_of_roads",
    #   "safety#road_miles",
    #   "sr311", "safety_record/entries[*]", "menu_spending",

    # Phase 6 — citywide.json.
    "citywide.json": [
        "trend",                            # Form A; CC-4 covers trend/months[*]
        "findings[*]",                      # Form A per item
    ],

    # Phase 8 — wards/index.json under CC-7. See §1.6.
    # "wards/index.json": [
    #     "wards[*]/windows/recent_12mo",
    #     "wards[*]/windows/prior_12mo",
    #     "wards[*]/crash_trend",
    # ],
}

# Keys that hold numbers which are not measurements. A version string, a byte
# budget, and a coordinate are not claims about the world, and demanding a
# caveat on them would be noise that teaches reviewers to ignore this check.
# Used by object claims and by the audit backlog.
NON_CLAIM_KEYS = {
    "api_version", "contract_version", "count", "bytes_approx",
    "bytes_approx_max", "lat", "lng", "ward", "ward_padded", "matter_id",
}

# CC-3 lint: a caveat must contain a referent. A four-digit year, an ISO date,
# any digit, or a key name from its own object. Heuristic, not proof — it
# catches "Recent months are provisional." and it costs fifteen lines.
_HAS_DIGIT = re.compile(r"\d")

_ARRAY_INDEX = re.compile(r"\[\d+\]")


# ---------------------------------------------------------------------------
# Shape predicates
# ---------------------------------------------------------------------------

def _is_number(value):
    """True for a real measurement. bool subclasses int in Python and
    `dooring: true` is not a measurement, so exclude it explicitly."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _numeric_keys(obj):
    return [k for k, v in obj.items()
            if _is_number(v) and k not in NON_CLAIM_KEYS]


def _has_block(obj):
    """Form A."""
    return all(k in obj for k in ("data_tier", "caveat_tags", "caveat"))


def _has_ref_block(obj):
    """CC-7. `data_tier` is optional and inherits — see the module docstring."""
    return "caveat_ref" in obj and "caveat_tags" in obj


def _has_pair(obj, key):
    """Form B for one named key."""
    return f"{key}_caveat" in obj and f"{key}_caveat_tags" in obj


# ---------------------------------------------------------------------------
# Selector resolution
# ---------------------------------------------------------------------------

def _parse_selector(selector):
    """'safety#monthly' -> ('safety', 'monthly'); 'a/b[*]' -> ('a/b[*]', None)."""
    if "#" in selector:
        obj_path, field = selector.split("#", 1)
        return obj_path, field
    return selector, None


def _resolve(node, segments, path, tier):
    """Yield (json_path, obj, inherited_data_tier) for every match of the
    remaining path segments. `tier` is the nearest enclosing declared tier."""
    if isinstance(node, dict):
        # DECISIONS.md: never invent zeros — a missing value ships as
        # {"available": false}. That is a stated absence, not an unqualified
        # number, so nothing below it is an enforced claim and the selector
        # simply does not match here.
        if node.get("available") is False:
            return
        tier = node.get("data_tier", tier)
    if not segments:
        if isinstance(node, dict):
            yield path, node, tier
        return

    head, rest = segments[0], segments[1:]
    iterate = head.endswith("[*]")
    key = head[:-3] if iterate else head

    if not isinstance(node, dict):
        return
    candidates = node.keys() if key == "*" else ([key] if key in node else [])
    for k in candidates:
        child, child_path = node[k], f"{path}/{k}"
        if iterate:
            if not isinstance(child, list):
                continue
            for i, item in enumerate(child):
                yield from _resolve(item, rest, f"{child_path}[{i}]", tier)
        else:
            yield from _resolve(child, rest, child_path, tier)


def _coverage(data, selectors):
    """(fully_covered_paths, {path: covered_keys}) for the audit backlog.

    A field selector covers ONE key. It must not mark the whole object covered,
    or `safety`'s eight unqualified numbers would vanish from the backlog behind
    `safety#monthly` — which is exactly the phase-2 work the backlog exists to
    surface.
    """
    full, partial = set(), {}
    for selector in selectors:
        obj_path, field = _parse_selector(selector)
        for path, obj, _ in _resolve(data, obj_path.split("/"), "<root>", None):
            if field is None:
                full.add(path)
                # CC-4: a Form A block also covers items of arrays hanging off it.
                for k, v in obj.items():
                    if isinstance(v, list):
                        full.update(f"{path}/{k}[{i}]" for i in range(len(v)))
            else:
                partial.setdefault(path, set()).add(field)
                if isinstance(obj.get(field), list):
                    full.update(f"{path}/{field}[{i}]"
                                for i in range(len(obj[field])))
    return full, partial


# ---------------------------------------------------------------------------
# Lints shared by every form
# ---------------------------------------------------------------------------

def _check_tags(rel, path, where, tags, fail):
    if not isinstance(tags, list) or not tags:
        fail(rel, path, f"{where} must be a non-empty array. See "
                        f"CAVEAT_TAG_VOCAB in pipeline/caveats.py.")
        return
    unknown = [t for t in tags if t not in CAVEAT_TAG_VOCAB]
    if unknown:
        fail(rel, path,
             f"unknown {where} {unknown!r}. Known tags: "
             f"{sorted(CAVEAT_TAG_VOCAB)}. Add the token to CAVEAT_TAG_VOCAB "
             f"in pipeline/caveats.py and to claim.schema.json in the same PR, "
             f"or fix the typo.")


def _check_self_containment(rel, path, key, text, sibling_keys, fail):
    """CC-3. The caveat must name its own referent so it reads correctly when
    quoted alone. Naming a dated window counts; restating values that are
    already sibling keys is permitted but not required (see §1.6)."""
    if not isinstance(text, str):
        fail(rel, path, f"{key} must be a string, got {type(text).__name__}.")
        return
    if _HAS_DIGIT.search(text):
        return
    if any(sib in text for sib in sibling_keys if len(sib) > 3):
        return
    fail(rel, path,
         f"{key} names no referent: {text!r}. A caveat must read correctly "
         f"when quoted with nothing beside it — name the window, the date, the "
         f"count, or the field it qualifies. 'Recent months are provisional.' "
         f"fails; 'Counts for the 12 months ending 2026-07-11...' passes.")


def _check_restatement_fidelity(rel, path, key, text, scope, fail):
    """CC-8. Every value the caveat restates must equal a value in the claim.

    This is the only check here that can catch a caveat that is FALSE rather
    than merely misplaced, and it exists because CC-3's amendment made value
    restatement the default. The CC-3 lint above asks whether the string names a
    referent; it is satisfied by any digit, so a caveat restating the WRONG
    digits passes it trivially. Two of four condition-B ward fixtures did.

    Restatements are recognised only in CC-8's canonical form — a parenthetical
    beginning with the value, `(65 crashes)`. `scope` is the object the caveat
    qualifies; caveats.claim_values() walks it under CC-2 scope, excluding
    nested objects that carry their own block.
    """
    if not isinstance(text, str):
        return
    wrong = unmatched_restatements(text, scope)
    if not wrong:
        return
    available = sorted(set(claim_values(scope)))
    fail(rel, path,
         f"{key} restates {wrong!r}, and no value in the claim it qualifies "
         f"matches (tolerance {RESTATEMENT_TOLERANCE}). The claim carries "
         f"{available[:8]}. Two ways to be here and both are defects. (1) The "
         f"caveat was built from the wrong object — check that the values "
         f"passed to the generator in pipeline/caveats.py came from the SAME "
         f"object the caveat is attached to; crash_trend.recent_12mo and "
         f"windows.recent_12mo.crashes are different numbers and they do not "
         f"always agree. (2) The parenthetical is not a restatement at all, in "
         f"which case rewrite it outside parentheses — CC-8 treats a "
         f"parenthetical starting with a digit as a restatement, and an "
         f"unverifiable restatement is indistinguishable from a false one. "
         f"Only a parenthetical that is ENTIRELY a date expression is exempt — "
         f"'(2021)', '(2026-07-11 to 2026-07-13)'. '(2032 crashes)' is a "
         f"restatement, not a date. Caveat: {text!r}")


def _check_tag_prose_agreement(rel, path, tags, text, fail):
    """CC-6, applied within a file: a tag and its prose must not drift apart.
    Only `provisional` is checked — it is the one whose absence from prose has
    a verified, shipped precedent."""
    if not isinstance(text, str):
        return
    if "provisional" in (tags or []) and "provisional" not in text.lower():
        fail(rel, path,
             "caveat_tags contains 'provisional' but the caveat prose never "
             "says so. The tag is for CI and the eval; the prose is what an "
             "agent puts in its answer. Both must state it.")


def _lint_qualifier(rel, path, label, tags, text, obj, fail, scope=None):
    """`obj` supplies CC-3's sibling key names. `scope` is what the caveat
    qualifies for CC-8 — the same object by default, or the array/sub-object a
    Form B pair names."""
    _check_tags(rel, path, f"{label}_tags", tags, fail)
    _check_self_containment(rel, path, label, text, set(obj), fail)
    _check_tag_prose_agreement(rel, path, tags, text, fail)
    _check_restatement_fidelity(rel, path, label, text,
                                obj if scope is None else scope, fail)


# ---------------------------------------------------------------------------
# The three claim forms
# ---------------------------------------------------------------------------

def _check_form_a_or_ref(rel, path, obj, tier, caveats_map, fail):
    """Returns True if this object carries a block that covers all its numbers."""
    if _has_block(obj):
        _lint_qualifier(rel, path, "caveat", obj["caveat_tags"], obj["caveat"],
                        obj, fail)
        return True

    if _has_ref_block(obj):
        if obj.get("data_tier", tier) is None:
            fail(rel, path,
                 "caveat_ref block has no data_tier and no enclosing object "
                 "declares one. A CC-7 block may inherit data_tier from an "
                 "ancestor in the SAME file — add `data_tier` here, or to the "
                 "entry that contains this object, or to the file root.")
            return True
        _check_tags(rel, path, "caveat_tags", obj["caveat_tags"], fail)
        text = (caveats_map or {}).get(obj["caveat_ref"])
        if isinstance(text, str):
            _check_self_containment(rel, path, "the resolved caveat_ref text",
                                    text, set(obj), fail)
            _check_tag_prose_agreement(rel, path, obj["caveat_tags"], text, fail)
            # CC-8 against the REFERENCING object, not the map. A shared entry
            # that restates a value is false for every record but the first —
            # this is what stops CC-7's byte saving from buying a false caveat.
            _check_restatement_fidelity(
                rel, path, f"the caveat_ref text {obj['caveat_ref']!r}",
                text, obj, fail)
        return True

    return False


def _check_object_claim(rel, path, obj, tier, caveats_map, fail):
    """Every numeric key in this object must be covered (CC-1 + CC-2)."""
    if _check_form_a_or_ref(rel, path, obj, tier, caveats_map, fail):
        return

    numeric = _numeric_keys(obj)
    uncovered = [k for k in numeric if not _has_pair(obj, k)]
    if uncovered:
        fail(rel, path,
             f"numeric field(s) {', '.join(sorted(uncovered))} have no "
             f"qualifier. Add a qualifier block (data_tier + caveat_tags + "
             f"caveat) to this object, or a <field>_caveat and "
             f"<field>_caveat_tags sibling for each. If this path is not "
             f"migrated yet, remove it from COLOCATION_ENFORCED_CLAIMS rather "
             f"than weakening the contract. See caveat_contract v1 in "
             f"pipeline/caveats.py.")
        return

    for key in numeric:
        _lint_qualifier(rel, path, f"{key}_caveat",
                        obj[f"{key}_caveat_tags"], obj[f"{key}_caveat"],
                        obj, fail)


def _check_field_claim(rel, path, obj, field, tier, caveats_map, fail):
    """One named key on this object must be covered by a Form B pair NAMED FOR
    IT. If the key holds an array, CC-4's container rule applies and the pair
    covers every item.

    CC-2, enforced 2026-07-25. An enclosing Form A block does NOT satisfy a
    field claim. It used to, and that made the architecture spec's own worked
    example of a scope violation pass: staple one block onto `safety` — which
    holds a rank, four rates, two mileages and a 107-month series — and both of
    phase 1's field claims went green. A field selector exists because that
    number needs its own qualifier; if the object's block genuinely covers every
    number in the object, the claim is an OBJECT claim and the selector should
    drop its `#field`.
    """
    if field not in obj:
        fail(rel, path,
             f"enforced claim '{field}' is not present on this object. A path "
             f"in COLOCATION_ENFORCED_CLAIMS is a path someone migrated; if it "
             f"is gone the migration regressed. Restore the field, or remove "
             f"the selector in the same PR. If the field is legitimately absent "
             f"for this record, emit the repo's `{{\"available\": false}}` shape "
             f"rather than omitting it — a stated absence is skipped, a silent "
             f"one is a regression.")
        return

    value = obj[field]
    if _has_pair(obj, field):
        _lint_qualifier(rel, path, f"{field}_caveat",
                        obj[f"{field}_caveat_tags"], obj[f"{field}_caveat"],
                        obj, fail,
                        scope=value if isinstance(value, (dict, list)) else obj)
    else:
        shape = "array" if isinstance(value, list) else "number"
        extra = ""
        if _has_block(obj) or _has_ref_block(obj):
            extra = (" This object carries a qualifier block of its own, and "
                     "that is NOT enough: CC-2 says a block applies to every "
                     "number in its object, so a block here claims to be true "
                     f"of all of {', '.join(sorted(_numeric_keys(obj))[:6])} "
                     "as well. If that is genuinely true, change the selector "
                     f"from '<path>#{field}' to the object form and delete the "
                     "Form B expectation. If it is not true, the block is a "
                     "scope violation — split the object or push the qualifier "
                     "down to Form B.")
        fail(rel, path,
             f"{field} is an enforced {shape} claim with no Form B pair. Add "
             f"`{field}_caveat` and `{field}_caveat_tags` siblings on this "
             f"object. The binding lives in the key name so the pairing "
             f"survives an agent reading this object as a flat key-value "
             f"list.{extra}")
        return

    # CC-4: items of the covered array may add tags of their own, nothing else.
    # This is $defs.item_override in claim.schema.json.
    if isinstance(value, list):
        for i, item in enumerate(value):
            if isinstance(item, dict) and "caveat_tags" in item:
                _check_tags(rel, f"{path}/{field}[{i}]",
                            "caveat_tags (item override)",
                            item["caveat_tags"], fail)


# ---------------------------------------------------------------------------
# File-level checks
# ---------------------------------------------------------------------------

def _walk_objects(node, path="<root>"):
    """Yield (json_path, dict) for every object in the tree, depth first."""
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from _walk_objects(value, f"{path}/{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from _walk_objects(item, f"{path}[{i}]")


def _check_refs_resolve(rel, data, fail):
    """CC-7: every caveat_ref resolves inside this same file. Never across
    files — that is the failure this whole contract exists to stop. Run over
    the whole file regardless of scope: a dangling ref is always a bug."""
    available = set((data.get("caveats") or {}).keys())
    for path, obj in _walk_objects(data):
        ref = obj.get("caveat_ref")
        if ref is not None and ref not in available:
            fail(rel, path,
                 f"caveat_ref {ref!r} does not resolve against this file's "
                 f"top-level `caveats` map (has: "
                 f"{sorted(available)[:6] or 'none'}). A caveat_ref must "
                 f"resolve inside the same file — never against llms.txt, "
                 f"index.json, or any other file.")


def _check_envelope(rel, data, fail):
    """The always tier ships in every enforced file's envelope."""
    meta = data.get("_meta", {})
    for key in ("caveat_contract", "agent_instruction"):
        if key not in meta:
            fail(rel, "<root>/_meta",
                 f"missing {key!r}. Every file under the co-location contract "
                 f"carries the imperative in its own envelope, so an agent "
                 f"that fetched only this file still gets it. Add it in "
                 f"_envelope() in pipeline/emit_api.py and to "
                 f"envelope.schema.json's properties AND required list — that "
                 f"schema is additionalProperties:false.")


def _selectors_for(rel):
    """Every enforced selector whose file glob matches this file."""
    out = []
    for glob, selectors in COLOCATION_ENFORCED_CLAIMS.items():
        if fnmatch.fnmatch(rel, glob):
            out.extend(selectors)
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def check_colocation(parsed, audit_only=False):
    """Check 5. `parsed` is {rel_path: data} from _check_schema_conformance.

    audit_only=True never exits non-zero. It lists every numeric claim in
    site/api/v1/ that no selector in COLOCATION_ENFORCED_CLAIMS covers,
    deduplicated across array indices and across files that share a glob.
    That is the migration backlog.
    """
    violations = []

    def fail(rel, path, message):
        if audit_only:
            violations.append(f"  site/api/v1/{rel} at {path}: {message}")
        else:
            sys.exit(f"FAIL: site/api/v1/{rel} violates the caveat co-location "
                     f"contract at {path!r}: {message}")

    enforced_files, enforced_claims = set(), 0

    # A selector must resolve in AT LEAST ONE file under its glob, not in every
    # file. Per-file absence is a legitimate data condition — a ward with no
    # crash_trend, or a window shipped as {"available": false}. Per-glob absence
    # means the migration regressed. The old per-file rule turned the first into
    # the second and blocked the Monday auto-refresh PR with no partial exit.
    hits, absent = {}, {}

    for rel in sorted(parsed):
        data = parsed[rel]
        _check_refs_resolve(rel, data, fail)
        for glob, selectors in COLOCATION_ENFORCED_CLAIMS.items():
            if not fnmatch.fnmatch(rel, glob):
                continue
            if rel not in enforced_files:
                enforced_files.add(rel)
                _check_envelope(rel, data, fail)
            caveats_map = data.get("caveats") or {}

            for selector in selectors:
                obj_path, field = _parse_selector(selector)
                matches = list(
                    _resolve(data, obj_path.split("/"), "<root>", None))
                if not matches:
                    absent.setdefault((glob, selector), []).append(rel)
                    continue
                hits[(glob, selector)] = hits.get((glob, selector), 0) + 1
                for path, obj, tier in matches:
                    enforced_claims += 1
                    if field is None:
                        _check_object_claim(rel, path, obj, tier, caveats_map,
                                            fail)
                    else:
                        _check_field_claim(rel, path, obj, field, tier,
                                           caveats_map, fail)

    # A glob that matched NO FILE is not a regression — it is a tree that does
    # not contain that family. check_api.py already tolerates a wholly absent
    # api/v1 (main() returns early when index.json is missing), so a partially
    # emitted tree is an anticipated condition here, not a broken one. Failing
    # on it would be the same defect the per-glob rule was written to fix, one
    # level up: a legitimate data condition turned into a blocked PR.
    unmatched_globs = sorted(
        glob for glob in COLOCATION_ENFORCED_CLAIMS
        if not any(fnmatch.fnmatch(rel, glob) for rel in parsed))

    for glob, selectors in COLOCATION_ENFORCED_CLAIMS.items():
        if glob in unmatched_globs:
            continue
        for selector in selectors:
            if hits.get((glob, selector)):
                continue
            files = absent.get((glob, selector), [])
            fail(files[0] if files else glob, f"<root>/{selector}",
                 f"enforced claim path {selector!r} matches nothing in ANY of "
                 f"the {len(files)} file(s) under {glob!r}. A path in "
                 f"COLOCATION_ENFORCED_CLAIMS is a path someone migrated; if it "
                 f"is gone from every file the migration regressed. Restore it, "
                 f"or drop the selector in the same PR. If it is legitimately "
                 f"gone from SOME files only, that is fine and this check will "
                 f"not fire.")

    if audit_only:
        _report_backlog(parsed, violations)
        return

    partial = {k: v for k, v in absent.items() if hits.get(k)}
    print(f"OK: {enforced_claims} enforced claim(s) across "
          f"{len(enforced_files)} site/api/v1 file(s) satisfy the caveat "
          f"co-location contract ({len(parsed) - len(enforced_files)} file(s) "
          f"have no enforced claims yet — run --audit-colocation for the "
          f"backlog).")
    for (glob, selector), files in sorted(partial.items()):
        print(f"NOTE: {selector!r} is absent from {len(files)} file(s) under "
              f"{glob!r} (e.g. {files[0]}) and present elsewhere. Not a "
              f"failure — a stated absence or a record without that field.")
    for glob in unmatched_globs:
        # Say it out loud. A skipped glob means enforcement went quiet for a
        # whole family, and enforcement that goes quiet without saying so is
        # indistinguishable from enforcement that passed.
        print(f"NOTE: no file matches {glob!r}, so its "
              f"{len(COLOCATION_ENFORCED_CLAIMS[glob])} enforced claim(s) were "
              f"not checked. Expected for a partial tree; if this appears "
              f"against the committed tree, the family stopped being emitted.")


def _report_backlog(parsed, violations):
    """Every numeric claim no selector covers, deduplicated. 50 ward files with
    the same gap are one line, not fifty, and 107 monthly items are one line,
    not 107. An unreadable backlog is an ignored backlog."""
    backlog = {}
    for rel in sorted(parsed):
        data = parsed[rel]
        selectors = _selectors_for(rel)
        full, partial = _coverage(data, selectors)
        glob = next((g for g in COLOCATION_ENFORCED_CLAIMS
                     if fnmatch.fnmatch(rel, g)), rel)
        for path, obj in _walk_objects(data):
            if path == "<root>/_meta" or path.startswith("<root>/_meta/"):
                continue
            if path in full or _has_block(obj) or _has_ref_block(obj):
                continue
            done = partial.get(path, set())
            uncovered = [k for k in _numeric_keys(obj)
                         if k not in done and not _has_pair(obj, k)]
            if not uncovered:
                continue
            key = (glob, _ARRAY_INDEX.sub("[*]", path), tuple(sorted(uncovered)))
            entry = backlog.setdefault(key, set())
            entry.add(rel)

    if violations:
        print(f"AUDIT: {len(violations)} problem(s) in already-enforced claims:")
        print("\n".join(violations))
    if not backlog:
        print("AUDIT: every numeric claim under site/api/v1/ is covered.")
        return
    print(f"AUDIT: {len(backlog)} unmigrated claim path(s). Each line is a "
          f"candidate selector for COLOCATION_ENFORCED_CLAIMS:")
    for (glob, path, keys), files in sorted(backlog.items()):
        selector = path.replace("<root>/", "").replace("[0]", "[*]")
        print(f"  {glob}  {selector}  ({len(keys)} number(s): "
              f"{', '.join(keys[:4])}{'…' if len(keys) > 4 else ''}) "
              f"— {len(files)} file(s)")


# In check_api.main(), after _check_version_coherence(index, parsed):
#
#     if "--audit-colocation" in sys.argv:
#         check_colocation(parsed, audit_only=True)
#     else:
#         check_colocation(parsed)
