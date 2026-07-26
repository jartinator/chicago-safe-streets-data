"""The one guard over hand-written caveat prose (phase 6, DECISIONS.md #43).

Every other caveat in this API comes out of a generator in pipeline/caveats.py
and cannot be phrased wrong. citywide.json's findings[] caveats are typed by a
person, in three metrics modules, and CC-8 — the only rule about whether a
caveat is TRUE — can only see a value restated in canonical parenthetical form.
A number written into running prose is checked by nothing, anywhere.

So this module runs the shipped CI rules over two surfaces:

  1. the committed site/data/findings.json — what is actually published today;
  2. the generators, over synthetic inputs — what the next build will produce,
     including the commitments fallback branch that only appears when CDOT's
     released install-date history is missing and therefore never reaches
     site/data/ for the checker in check_api.py to see.

The rules are imported from check_colocation, not restated here. Two copies of
a lint drift, and this whole contract exists because two copies of a tag table
already did.
"""
import json
from pathlib import Path

import pytest

import caveats
from bna_metrics import build_bna_finding
from caveats import FINDING_CAVEAT_TAGS, finding_tags
from check_colocation import (_check_restatement_fidelity,
                              _check_self_containment,
                              _check_tag_prose_agreement, _check_tags)
from commitments_metrics import build_commitments_finding
from crash_metrics import build_findings_core

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _lint(finding):
    """Run the shipped Check 5 qualifier rules over one finding. -> [problems].

    `map_state` is dropped first: emit_api strips it, so the object the caveat
    is welded to in the published file does not carry it, and neither should
    CC-8's value scope.
    """
    obj = {k: v for k, v in finding.items() if k != "map_state"}
    problems = []

    def fail(rel, path, message):
        problems.append(f"{finding.get('id')}: {message}")

    tags, text = obj.get("caveat_tags"), obj.get("caveat")
    _check_tags("findings", finding.get("id"), "caveat_tags", tags, fail)
    _check_self_containment("findings", finding.get("id"), "caveat", text,
                            set(obj), fail)
    _check_tag_prose_agreement("findings", finding.get("id"), tags, text, fail)
    _check_restatement_fidelity("findings", finding.get("id"), "caveat", text,
                                obj, fail)
    return problems


# --- the canonical table ------------------------------------------------------

def test_canonical_tags_are_all_in_the_vocabulary():
    for finding_id, tags in FINDING_CAVEAT_TAGS.items():
        assert tags, f"{finding_id} has an empty tag list; caveat_tags is minItems 1"
        unknown = [t for t in tags if t not in caveats.CAVEAT_TAG_VOCAB]
        assert not unknown, f"{finding_id} carries unknown tags {unknown}"


def test_finding_tags_refuses_an_unknown_id():
    """A new finding gets a row in the table, in the PR that adds the finding.

    Returning [] here would ship an unqualified number and fail check_api.py one
    step later with a message about JSON Schema instead of about the table.
    """
    with pytest.raises(ValueError, match="canonical caveat_tags"):
        finding_tags("a-finding-nobody-tagged")


def test_committed_findings_all_have_a_canonical_row():
    shipped = json.loads(
        (REPO_ROOT / "site" / "data" / "findings.json").read_text(encoding="utf-8"))
    missing = [f["id"] for f in shipped if f["id"] not in FINDING_CAVEAT_TAGS]
    assert not missing, (
        f"published findings {missing} have no row in FINDING_CAVEAT_TAGS — "
        f"decide their tags against their own caveat text and add them there")


# --- surface 1: what is published today ---------------------------------------

def test_every_published_finding_caveat_passes_the_contract():
    shipped = json.loads(
        (REPO_ROOT / "site" / "data" / "findings.json").read_text(encoding="utf-8"))
    assert len(shipped) >= 9, "findings.json shrank — the lint below would pass vacuously"

    problems = []
    for finding in shipped:
        assert finding.get("caveat_tags"), f"{finding['id']} carries no caveat_tags"
        assert finding["caveat_tags"] == FINDING_CAVEAT_TAGS[finding["id"]] or \
            set(FINDING_CAVEAT_TAGS[finding["id"]]).issubset(finding["caveat_tags"]), (
                f"{finding['id']} tags {finding['caveat_tags']} diverge from the "
                f"canonical table {FINDING_CAVEAT_TAGS[finding['id']]}")
        problems += _lint(finding)
    assert not problems, "\n".join(problems)


def test_dooring_caveat_restates_its_stat_in_canonical_form():
    """The landmine this phase was sequenced behind, asserted directly.

    `stat` is "2040+" and the caveat restates it as "(2040 crashes)". A leading
    year used to exempt that parenthetical from CC-8 entirely, so a wrong number
    there would have shipped on the one finding the instruction actually hits.
    """
    shipped = json.loads(
        (REPO_ROOT / "site" / "data" / "findings.json").read_text(encoding="utf-8"))
    dooring = next(f for f in shipped if f["id"] == "dooring-undercount")
    restated = caveats.restated_values(dooring["caveat"])
    assert restated, "the dooring caveat no longer restates its stat in canonical form"
    assert restated[0] == float(dooring["stat"].rstrip("+"))


# --- surface 2: what the next build will produce -------------------------------

def _crash_tuples():
    """Two 12-month windows of crashes, with hit-and-run and dooring flags and
    five wards, so build_findings_core emits every finding it can."""
    rows = []
    for i in range(60):
        year, month = (2025, i % 12 + 1) if i < 30 else (2026, i % 6 + 1)
        rows.append({
            "date": f"{year}-{month:02d}-0{i % 9 + 1}",
            "severity": "fatal" if i % 4 == 0 else "incapacitating",
            "hit_and_run": i % 3 == 0,
            "dooring": i % 5 == 0,
            "ward": str(i % 5 + 1),
        })
    return rows


def _corridors():
    return [{"street": "KINZIE", "segments": 3, "length_m": 1355.6,
             "crashes": 105, "crashes_per_km": 77.46, "data_tier": "real"},
            {"street": "MILWAUKEE", "segments": 9, "length_m": 8100.0,
             "crashes": 130, "crashes_per_km": 16.05, "data_tier": "real"}]


def test_generated_crash_findings_pass_the_contract():
    findings = build_findings_core(
        _crash_tuples(), {"protected": 68.7, "painted": 138.5, "trail": 40.0},
        _corridors(), {"1": 12, "2": 10, "3": 9, "4": 8, "5": 7, "6": 3},
        "2026-07-22",
        road_coverage={"road_miles": 3800.0, "onstreet_bikeway_miles": 430.0,
                       "pct_with_bike_infra": 11.0})

    ids = [f["id"] for f in findings]
    assert ids == ["ksi-trend", "protected-share", "street-coverage",
                   "top-corridors", "hit-and-run", "ward-concentration",
                   "dooring-undercount"]

    problems = []
    for finding in findings:
        assert finding["caveat_tags"] == FINDING_CAVEAT_TAGS[finding["id"]]
        problems += _lint(finding)
    assert not problems, "\n".join(problems)


def test_top_corridors_caveat_names_the_real_top_corridor():
    """It used to say "Kinzie" whatever the data said. The corridor roster is
    rebuilt weekly and the name is not pinned, so the prose has to follow it."""
    findings = build_findings_core(
        _crash_tuples(), {"protected": 68.7, "painted": 138.5},
        [{"street": "MILWAUKEE", "crashes_per_km": 90.0}], {"1": 5},
        "2026-07-22")
    corridors = next(f for f in findings if f["id"] == "top-corridors")
    assert "Milwaukee" in corridors["caveat"]
    assert "Kinzie" not in corridors["caveat"]


def test_generated_crash_findings_survive_an_empty_dataset():
    """anchor_date is None with no crashes. The caveat must degrade to the start
    date, never to the string "None" — which would also fail CC-3."""
    findings = build_findings_core([], {"protected": 1.0}, [], {}, "2026-07-22")
    dooring = next(f for f in findings if f["id"] == "dooring-undercount")
    assert "None" not in dooring["caveat"]
    assert not _lint(dooring)


def test_generated_bna_finding_passes_the_contract():
    scores = json.loads(
        (REPO_ROOT / "site" / "data" / "bna_scores.json").read_text(encoding="utf-8"))
    finding = build_bna_finding(scores)
    assert finding["caveat_tags"] == FINDING_CAVEAT_TAGS["bna-score"]
    assert not _lint(finding)


def _commitment_inputs():
    commitments = json.loads(
        (REPO_ROOT / "data" / "commitments.json").read_text(encoding="utf-8"))
    series = json.loads(
        (REPO_ROOT / "site" / "data" / "bikeway_mileage_series.json").read_text(
            encoding="utf-8"))
    history = json.loads(
        (REPO_ROOT / "data" / "cdot_bikeway_history.json").read_text(encoding="utf-8"))
    return commitments, series, history


def test_generated_commitments_finding_passes_the_contract():
    commitments, series, history = _commitment_inputs()
    finding = build_commitments_finding(commitments, series, history)
    assert finding["caveat_tags"] == FINDING_CAVEAT_TAGS["commitments-vs-delivered"]
    assert not _lint(finding)


def test_commitments_fallback_branch_is_tagged_and_passes_the_contract():
    """The branch that never reaches site/data/, and therefore never reaches
    check_api.py. It compares against a network snapshot instead of against
    delivery, so it carries snapshot_derived on top of the canonical row.
    """
    commitments, series, _ = _commitment_inputs()
    finding = build_commitments_finding(commitments, series, history_doc=None)
    assert finding["caveat_tags"] == ["third_party_method", "snapshot_derived"]
    assert not _lint(finding)
