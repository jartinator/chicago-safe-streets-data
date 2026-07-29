"""Tests for the Phase 5 discovery-layer builders in emit_api.py: site/llms.txt
and site/sitemap.xml. Reuses test_emit_api.py's fixture builders (same
pattern as test_api_schemas.py) so the synthetic site/data/ shape stays in
one place.
"""
import json
import re
import xml.etree.ElementTree as ET

import pytest

import emit_api
import test_emit_api as fx
from caveats import CAVEAT_CONTRACT_VERSION
from config import CONTRACT_VERSION, SITE_BASE_URL, SKILL_ENTRY_URL
from emit_api import API_BASE_URL, build_llms_txt, build_sitemap_xml, emit_all


def _meta(**overrides):
    return fx._meta(**overrides)


# --- 1. build_llms_txt ------------------------------------------------------

def test_llms_txt_header_has_generated_at_provenance_and_contract_version():
    meta = _meta(provenance="socrata", generated_at="2026-07-13T05:56:25+00:00")
    text = build_llms_txt(meta, fx._endpoint_bytes())
    assert "2026-07-13T05:56:25+00:00" in text
    assert "socrata" in text
    assert CONTRACT_VERSION in text


def test_llms_txt_header_reflects_fixtures_provenance():
    meta = _meta(provenance="fixtures", generated_at="2020-01-01T00:00:00+00:00")
    text = build_llms_txt(meta, fx._endpoint_bytes())
    assert "2020-01-01T00:00:00+00:00" in text
    assert "fixtures" in text


def test_llms_txt_no_synthetic_data_statement_present_verbatim():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert emit_api.NO_SYNTHETIC_DATA_STATEMENT in text


def test_llms_txt_raw_counts_caveat_present_verbatim():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert emit_api.RAW_COUNTS_CAVEAT in text


def test_llms_txt_no_mock_obstruction_leakage_outside_disclaimer():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert "obstructions_mock" not in text.lower()
    # "obstruction" is allowed ONLY inside the no-synthetic-data disclaimer,
    # or (P1c) the answering-guidance paragraph's own explicit "we don't
    # publish real obstruction reports either" caveat — a second,
    # deliberate, non-synthetic mention, not a leak of the mock layer.
    without_disclaimer = text.replace(emit_api.NO_SYNTHETIC_DATA_STATEMENT, "")
    without_disclaimer = without_disclaimer.replace(emit_api.ANSWERING_GUIDANCE, "")
    assert "obstruction" not in without_disclaimer.lower()


def test_llms_txt_header_carries_caveat_contract():
    """F2. _meta.caveat_contract is the one field an agent is told to watch for a
    breaking change, and llms.txt is the first file an orienting agent reads.
    Without this line it cannot see the break signal without a second fetch."""
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert f"caveat_contract: {CAVEAT_CONTRACT_VERSION}" in text


def test_llms_txt_advertises_the_skill_section_and_the_one_url():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert "## Answering guide (skill)" in text
    assert SKILL_ENTRY_URL in text


def test_llms_txt_skill_section_states_when_not_to_fetch():
    """tool-api-design 2: the when-NOT line prevents more misfires than any
    other. Without it an agent that needs one crash count pays a 10.8 KB fetch
    to be told to read a field it already has."""
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert "Skip it if you need one value" in text


def test_llms_txt_skill_section_carries_the_versioning_rule():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert "a 304 means unchanged" in text
    assert "A 200 does not mean changed" in text
    assert "skill.files[]" in text


def test_llms_txt_skill_section_carries_a_404_rule():
    """The only error guidance that survives the one reachable state where
    index.json's skill.errors is absent: a first-time agent that read llms.txt,
    fetched the URL, got a 404, and has never held the block."""
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert "If that URL 404s" in text
    assert "do not retry" in text
    assert "do not answer without caveats" in text
    assert "_meta.agent_instruction" in text


def test_llms_txt_skill_section_sits_above_the_endpoint_listing():
    """An agent that reads the top of the file and stops must have seen it. A
    trailing section below 38 lines of endpoints is written to be skipped."""
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert text.index("## Answering guide (skill)") < text.index("## Endpoints")
    assert text.index("## Start here") < text.index("## Answering guide (skill)")


def test_llms_txt_skill_url_is_not_hard_coded_in_build_llms_txt():
    """F1. The failure mode is a renamed SKILL_NAME that moves index.json and
    the published file while llms.txt keeps advertising the old URL."""
    import inspect
    source = inspect.getsource(build_llms_txt)
    assert "SKILL_ENTRY_URL" in source
    assert "chicago-bike-safety-data" not in source


def test_llms_txt_skill_section_carries_the_manifest_precedence_rule():
    """Hale round 3 4.3. index.json's skill.errors carries this rule in full, but
    the consumer most likely to act on a wrong figure in the guide is the one
    least likely to have fetched index.json. The 404 rule covers the guide being
    absent; this covers it being present and wrong, which is the state that
    exists: five prose restatements of families[].count survive commit 5a4ee58.
    Ordering is asserted because a rule below 38 lines of endpoints is a rule
    written to be skipped."""
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert "every count from families[].count" in text
    assert "every size from bytes_approx" in text
    assert "never from the guide's prose" in text
    assert text.index("never from the guide's prose") < text.index("## Endpoints")
    # The claim this rule replaces. It shipped on three surfaces and could never
    # have been made true: SKILL.md's worked answer is the guide's teaching
    # device. If it comes back anywhere in this file, the file contradicts itself.
    assert "publishes no numbers" not in text


def test_llms_txt_precedence_rule_names_the_same_fields_as_the_manifest_error():
    """One rule, two surfaces, one vocabulary. The defect under repair is two
    surfaces disagreeing about the same subject; a fix that leaves them naming
    different fields is that defect at a smaller size. Fails if either surface
    drops or renames a field."""
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    rule = emit_api._SKILL_ERRORS["on_the_guide_disagreeing_with_this_manifest"]
    for field in ("endpoints[].path", "families[].path_template",
                  "families[].count", "bytes_approx"):
        assert field in rule, f"{field} left skill.errors"
        assert field in text, f"{field} left llms.txt's precedence rule"


def test_llms_txt_lists_every_known_endpoint_with_description_and_questions():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    for ep in emit_api._ENDPOINTS:
        assert f"{API_BASE_URL}/{ep['path']}" in text
        assert ep["description"] in text
        for q in ep["example_questions"]:
            assert q in text


def test_llms_txt_start_here_points_at_index_json():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert f"{API_BASE_URL}/index.json" in text


def test_llms_txt_links_human_pages():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert f"{SITE_BASE_URL}/index.html" in text
    assert f"{SITE_BASE_URL}/methodology.html" in text
    assert f"{SITE_BASE_URL}/ward.html" in text


def test_llms_txt_mentions_tier_vocabulary():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    for tier in ("real", "proxy", "mock", "crowdsourced", "derived"):
        assert tier in text


def test_llms_txt_within_size_budget():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    assert len(text.encode("utf-8")) < emit_api.API_SIZE_BUDGET_BYTES


def test_llms_txt_is_plain_text_not_json():
    text = build_llms_txt(_meta(), fx._endpoint_bytes())
    with pytest.raises(json.JSONDecodeError):
        json.loads(text)


# --- 2. build_sitemap_xml ----------------------------------------------------

def _locs(xml_text):
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(xml_text)
    return [el.text for el in root.findall("s:url/s:loc", ns)]


def test_sitemap_xml_exact_url_set():
    meta = _meta()
    xml_text = build_sitemap_xml(meta)
    expected = {
        f"{SITE_BASE_URL}/index.html", f"{SITE_BASE_URL}/network.html",
        f"{SITE_BASE_URL}/findings.html", f"{SITE_BASE_URL}/table.html",
        f"{SITE_BASE_URL}/sources.html", f"{SITE_BASE_URL}/methodology.html",
        f"{SITE_BASE_URL}/action.html", f"{SITE_BASE_URL}/ward.html",
        f"{SITE_BASE_URL}/contributing.html", f"{SITE_BASE_URL}/llms.txt",
        f"{SITE_BASE_URL}/api/v1/index.json",
    }
    assert set(_locs(xml_text)) == expected


def test_sitemap_xml_excludes_obstructions_preview():
    xml_text = build_sitemap_xml(_meta())
    assert "obstructions-preview" not in xml_text


def test_sitemap_xml_lastmod_matches_meta_generated_at_date_for_every_entry():
    meta = _meta(generated_at="2026-07-13T05:56:25+00:00")
    xml_text = build_sitemap_xml(meta)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(xml_text)
    lastmods = {el.text for el in root.findall("s:url/s:lastmod", ns)}
    assert lastmods == {"2026-07-13"}


def test_sitemap_xml_is_well_formed_xml():
    xml_text = build_sitemap_xml(_meta())
    ET.fromstring(xml_text)  # must not raise


# --- 3. emit_all wiring: llms.txt / sitemap.xml live at site root -----------

def test_emit_all_writes_llms_txt_and_sitemap_at_site_root_not_api_dir(
        tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "site" / "api" / "v1"
    site_dir = tmp_path / "site"
    fx._write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "SITE_DIR", site_dir)

    emit_all()

    assert (site_dir / "llms.txt").exists()
    assert (site_dir / "sitemap.xml").exists()
    assert not (api_dir / "llms.txt").exists()
    assert not (api_dir / "sitemap.xml").exists()


def test_emit_all_llms_txt_reflects_real_meta(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "site" / "api" / "v1"
    site_dir = tmp_path / "site"
    fx._write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "SITE_DIR", site_dir)

    emit_all()

    text = (site_dir / "llms.txt").read_text(encoding="utf-8")
    meta = json.loads((site_data / "meta.json").read_text())
    assert meta["generated_at"] in text
    assert meta["provenance"] in text


def test_emit_all_sitemap_lastmod_reflects_real_meta(tmp_path, monkeypatch):
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "site" / "api" / "v1"
    site_dir = tmp_path / "site"
    fx._write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "SITE_DIR", site_dir)

    emit_all()

    xml_text = (site_dir / "sitemap.xml").read_text(encoding="utf-8")
    meta = json.loads((site_data / "meta.json").read_text())
    expected_date = meta["generated_at"][:10]
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(xml_text)
    lastmods = {el.text for el in root.findall("s:url/s:lastmod", ns)}
    assert lastmods == {expected_date}


def test_enforce_llms_txt_budget_raises_naming_the_file(monkeypatch):
    monkeypatch.setattr(emit_api, "API_SIZE_BUDGET_BYTES", 10)
    with pytest.raises(SystemExit) as excinfo:
        emit_api._enforce_llms_txt_budget("x" * 100)
    message = str(excinfo.value)
    assert "llms.txt" in message
    assert "100" in message
    assert "10" in message


def test_enforce_llms_txt_budget_passes_under_budget():
    emit_api._enforce_llms_txt_budget("short text")  # must not raise


def test_emit_all_over_budget_reports_json_file_before_llms_txt_is_reached(
        tmp_path, monkeypatch):
    # llms.txt's own budget check runs AFTER _enforce_budget(written) inside
    # emit_all, so a global budget too small for the api/v1 json files fails
    # on the more actionable json-file message first, not llms.txt.
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "site" / "api" / "v1"
    site_dir = tmp_path / "site"
    fx._write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "SITE_DIR", site_dir)
    monkeypatch.setattr(emit_api, "API_SIZE_BUDGET_BYTES", 10)

    with pytest.raises(SystemExit) as excinfo:
        emit_all()
    assert "citywide.json" in str(excinfo.value)


def test_emit_all_written_return_value_excludes_llms_and_sitemap(tmp_path, monkeypatch):
    # written (the dict emit_all returns, and what _prune_stale/_enforce_budget
    # operate on) tracks only site/api/v1/* files; llms.txt/sitemap.xml are
    # siblings at the site root and must never leak into it.
    site_data = tmp_path / "site_data"
    api_dir = tmp_path / "site" / "api" / "v1"
    site_dir = tmp_path / "site"
    fx._write_site_data(site_data)
    monkeypatch.setattr(emit_api, "SITE_DATA_DIR", site_data)
    monkeypatch.setattr(emit_api, "SITE_API_DIR", api_dir)
    monkeypatch.setattr(emit_api, "SITE_DIR", site_dir)

    written = emit_all()

    assert "llms.txt" not in written
    assert "sitemap.xml" not in written
