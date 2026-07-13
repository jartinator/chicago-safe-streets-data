"""aggregate.py news matching — precision rules from the news-coverage design
(docs/superpowers/specs/2026-07-13-news-coverage-design.md, amendments A/B):
publisher tags beat headline text, bare surnames never match, street names
need a type suffix, every match carries an auditable `via`."""
import json

import aggregate


ALDERMEN = [
    {"ward": "1", "alderman": "La Spata, Daniel"},
    {"ward": "3", "alderman": "Dowell, Pat"},
    {"ward": "30", "alderman": "Cruz, Ruth"},
    # Two share a surname -> full-name-only matching for both:
    {"ward": "10", "alderman": "Lopez, Maria"},
    {"ward": "15", "alderman": "Lopez, Raymond"},
]

ROSTER = {"lines": [
    {"id": "milwaukee", "name": "Milwaukee Line", "streets": ["MILWAUKEE", "RANDOLPH"]},
    {"id": "clark", "name": "Clark Line",
     "streets": ["CLARK", {"name": "DEARBORN", "clip_bbox": [0, 0, 1, 1]}]},
    {"id": "lakefront", "name": "Lakefront Trail", "name_tokens": ["lakefront"]},
    {"id": "bloomingdale", "name": "Bloomingdale Trail (606)",
     "name_tokens": ["bloomingdale", "606"]},
]}


def _matchers():
    return (aggregate._alderman_matchers(ALDERMEN),
            aggregate._route_matchers(ROSTER))


def match(title, categories=()):
    alds, routes = _matchers()
    return aggregate.match_news_item(
        {"title": title, "categories": list(categories)}, alds, routes)


def test_ward_from_publisher_tag_and_headline():
    m = match("New bikeway opens", ["35th Ward", "Bicycling"])
    assert m["wards"] == [{"ward": "35", "via": "publisher tag '35th Ward'"}]
    m = match("Crash reported in the 1st Ward")
    assert m["wards"][0]["ward"] == "1"
    assert "in headline" in m["wards"][0]["via"]


def test_alderman_honorific_surname_and_full_name():
    m = match("Ald. Dowell blocks protected lane")
    assert m["aldermen"] == [{"name": "Dowell, Pat", "ward": "3",
                              "via": "'Ald. Dowell' in headline"}]
    # The matched alderman's ward is attached, with its own audit trail:
    assert m["wards"][0]["ward"] == "3"
    assert "Ald. Dowell" in m["wards"][0]["via"]
    # Full name in a publisher tag (Streetsblog tags people by full name):
    m = match("Council roundup", ["Pat Dowell"])
    assert m["aldermen"][0]["via"] == "publisher tag 'Pat Dowell'"


def test_bare_surname_never_matches():
    assert match("Dowell speaks at rally")["aldermen"] == []


def test_shared_surname_requires_full_name():
    assert match("Ald. Lopez proposes ordinance")["aldermen"] == []
    m = match("Raymond Lopez proposes bike lane ordinance")
    assert [a["name"] for a in m["aldermen"]] == ["Lopez, Raymond"]


def test_street_requires_type_suffix():
    assert match("Milwaukee Avenue bike lanes extended")["routes"] == [
        {"id": "milwaukee", "name": "Milwaukee Line",
         "via": "'Milwaukee Avenue' in headline"}]
    # Bare street word (could be the city/brewery/anything) never matches:
    assert match("Milwaukee approves new bike plan")["routes"] == []
    # Dict-shaped street entries (clip_bbox form) still match by name:
    assert match("Dearborn St bridge closure")["routes"][0]["id"] == "clark"


def test_trail_tokens_match_without_suffix():
    assert match("Lakefront closure this weekend")["routes"][0]["id"] == "lakefront"
    assert match("New ramp for The 606")["routes"][0]["id"] == "bloomingdale"
    # Numeric token respects word boundaries:
    assert match("Route 6060 detour")["routes"] == []


def test_relevance_gate():
    RSS = {"kind": "rss"}
    assert aggregate._news_relevant(
        {"title": "New bike lane on Halsted", "categories": []}, RSS)
    assert aggregate._news_relevant(
        {"title": "Council transit roundup", "categories": ["Bicycling"]}, RSS)
    assert not aggregate._news_relevant(
        {"title": "Mayor announces housing plan", "categories": ["Housing"]}, RSS)
    # Only Google feeds whose query IS the filter get the free pass:
    assert aggregate._news_relevant(
        {"title": "Anything at all", "categories": []},
        {"kind": "google_news", "query_is_filter": True})
    # The roster-derived project query is NOT its own filter — its corridor
    # phrases surface daycare openings and out-of-state streets:
    assert not aggregate._news_relevant(
        {"title": "Daycare opens new location on Grand Avenue",
         "categories": []}, {"kind": "google_news"})
    # Streetsblog's daily link-digest posts are never items:
    assert not aggregate._news_relevant(
        {"title": "Today’s Headlines for Monday, July 13", "categories": []},
        RSS)


def test_build_news_items_window_cap_and_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    monkeypatch.setattr(aggregate, "SITE_DATA_DIR", site)
    (site / "aldermen.json").write_text(json.dumps({"wards": ALDERMEN}))
    (tmp_path / "news.json").write_text(json.dumps({
        "fetched_at": "2026-07-13T12:00:00+00:00",
        "feeds": [{"url": "u", "source": "Streetsblog Chicago", "kind": "rss",
                   "ok": True, "items": [
            {"title": "Milwaukee Avenue bike lanes extended", "url": "a",
             "source": "Streetsblog Chicago",
             "published": "2026-07-10T00:00:00+00:00",
             "categories": ["1st Ward"]},
            {"title": "Old bike lane story", "url": "b",
             "source": "Streetsblog Chicago",
             "published": "2026-01-01T00:00:00+00:00",  # outside 90d window
             "categories": []},
            {"title": "Undated bike lane story", "url": "c",
             "source": "Streetsblog Chicago", "published": None,
             "categories": []},
            {"title": "Housing roundup", "url": "d",  # irrelevant
             "source": "Streetsblog Chicago",
             "published": "2026-07-12T00:00:00+00:00", "categories": []},
        ]}],
    }))

    out = aggregate.build_news_items(ROSTER)

    assert out["data_tier"] == "real" and out["match_tier"] == "derived"
    assert out["as_of"] == "2026-07-13T12:00:00+00:00"
    assert [i["url"] for i in out["items"]] == ["a"]
    item = out["items"][0]
    assert item["matches"]["wards"][0]["ward"] == "1"
    assert item["matches"]["routes"][0]["id"] == "milwaukee"


def test_build_news_items_missing_raw_is_honest_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    out = aggregate.build_news_items(ROSTER)
    assert out["items"] == [] and out["as_of"] is None
    assert "did not run" in out["note"]
