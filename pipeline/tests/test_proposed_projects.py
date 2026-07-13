"""Proposed-projects roster: phrase matching, coverage join, roster-driven
pull query (docs/superpowers/specs/2026-07-13-proposed-projects-design.md).
Phrase precision is the load-bearing rule: bare corridor tokens like "606"
are ~1/12 on-topic (evidence brief §2) and must never match."""
import json

import aggregate
import pull_news


PROJECTS = {"projects": [
    {"id": "bloomingdale-extension", "name": "Bloomingdale Trail (606) Extension",
     "status": "in design", "status_as_of": "2026-07-13",
     "news_phrases": ["Bloomingdale Trail extension", "606 extension"]},
    {"id": "weber-spur", "name": "Weber Spur Trail",
     "status": "funded in part", "status_as_of": "2026-07-13",
     "news_phrases": ["Weber Spur"]},
]}


def match(title, categories=()):
    return aggregate.match_news_item(
        {"title": title, "categories": list(categories)},
        [], [], aggregate._project_matchers(PROJECTS))


def test_phrase_match_with_via():
    m = match("City reveals updated timeline for the Bloomingdale Trail extension")
    assert m["projects"] == [{"id": "bloomingdale-extension",
                              "name": "Bloomingdale Trail (606) Extension",
                              "via": "'Bloomingdale Trail extension' in headline"}]


def test_bare_corridor_token_never_matches():
    # Routine 606 coverage (events, closures, crime) must not attach:
    assert match("Crowds pack The 606 for summer festival")["projects"] == []
    assert match("Bloomingdale Trail closed for repairs")["projects"] == []


def test_publisher_tag_beats_headline():
    m = match("A short trail news roundup", ["606 Extension"])
    assert m["projects"][0]["via"] == "publisher tag '606 Extension'"


def test_project_match_makes_item_relevant(tmp_path, monkeypatch):
    # A Weber Spur funding story has no SAFETY_TOPIC_KEYWORDS hit and no
    # topic category — the project match alone must keep it.
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    monkeypatch.setattr(aggregate, "SITE_DATA_DIR", site)
    (tmp_path / "news.json").write_text(json.dumps({
        "fetched_at": "2026-07-13T12:00:00+00:00",
        "feeds": [{"url": "u", "source": "Block Club Chicago", "kind": "rss",
                   "ok": True, "items": [
            {"title": "Weber Spur Secures Federal Funding", "url": "a",
             "source": "Block Club Chicago",
             "published": "2026-07-01T00:00:00+00:00", "categories": []},
        ]}],
    }))

    out = aggregate.build_news_items({"lines": []}, PROJECTS)
    assert [i["url"] for i in out["items"]] == ["a"]
    assert out["items"][0]["matches"]["projects"][0]["id"] == "weber-spur"


def test_build_proposed_projects_join_cap_and_empty():
    news = {"as_of": "2026-07-13T12:00:00+00:00", "items": [
        {"title": f"Extension story {i}", "url": f"u{i}", "source": "S",
         "published": f"2026-07-{i:02d}T00:00:00+00:00",
         "matches": {"projects": [{"id": "bloomingdale-extension",
                                   "name": "x", "via": "v"}]}}
        for i in range(1, 12)
    ]}
    out = aggregate.build_proposed_projects(PROJECTS, news)
    assert out["data_tier"] == "derived" and out["as_of"] == news["as_of"]
    bloom, weber = out["projects"]
    # Roster fields pass through verbatim; coverage joined, capped:
    assert bloom["status"] == "in design"
    assert len(bloom["coverage"]) == aggregate.PROPOSED_COVERAGE_CAP
    assert bloom["coverage"][0] == {"title": "Extension story 1", "url": "u1",
                                    "source": "S",
                                    "published": "2026-07-01T00:00:00+00:00",
                                    "via": "v"}
    # No coverage is an empty list (renders the press-gap empty state), and
    # a missing roster degrades honestly:
    assert weber["coverage"] == []
    missing = aggregate.build_proposed_projects(None, news)
    assert missing["projects"] == [] and "missing" in missing["note"]


def test_project_query_feed_built_from_roster(tmp_path):
    path = tmp_path / "proposed_projects.json"
    path.write_text(json.dumps(PROJECTS))
    feed = pull_news.project_query_feed(path)
    assert feed["kind"] == "google_news" and feed["source"] is None
    assert "%22Bloomingdale%20Trail%20extension%22" in feed["url"]
    assert "Weber%20Spur" in feed["url"]
    # Missing/empty roster -> no extra feed, never an error:
    assert pull_news.project_query_feed(tmp_path / "nope.json") is None
    path.write_text(json.dumps({"projects": []}))
    assert pull_news.project_query_feed(path) is None


CTX_PROJECTS = {"projects": [
    {"id": "grand-avenue", "name": "Grand Avenue Protected Bike Lanes (Phase 2)",
     "news_phrases": [], "news_phrases_ctx": ["Grand Avenue", "Grand Ave"]},
]}


def match_ctx(title):
    return aggregate.match_news_item(
        {"title": title, "categories": []},
        [], [], aggregate._project_matchers(CTX_PROJECTS))


def test_ctx_phrase_requires_safety_keyword_in_headline():
    # Live failure this rule fixes: bare "Grand Avenue" attached Phoenix and
    # Long Island stories and a daycare opening — corridor name alone says
    # nothing about the project.
    assert match_ctx("Grand Avenue neighbors help define a uniquely Phoenix block")["projects"] == []
    assert match_ctx("Daycare opens new location on Grand Avenue")["projects"] == []
    m = match_ctx("Grand Avenue bike lane barriers spark backlash")
    assert m["projects"][0]["id"] == "grand-avenue"
    assert m["projects"][0]["via"] == \
        "'Grand Avenue' in headline + safety keyword in headline"


def test_project_query_is_chicago_scoped():
    import json as _json
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "roster.json"
        path.write_text(_json.dumps(CTX_PROJECTS))
        feed = pull_news.project_query_feed(path)
        assert "Chicago" in feed["url"]


def test_cap_never_drops_project_matched_items(tmp_path, monkeypatch):
    # 3-item cap, 4 relevant items: the oldest is project-matched and must
    # survive the cap; the second-oldest (unmatched) is the one cut.
    monkeypatch.setattr(aggregate, "RAW_DIR", tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    monkeypatch.setattr(aggregate, "SITE_DATA_DIR", site)
    monkeypatch.setattr(aggregate, "NEWS_MAX_ITEMS", 3)
    items = [
        {"title": f"Fresh bike lane story {i}", "url": f"u{i}",
         "source": "S", "published": f"2026-07-{10 + i}T00:00:00+00:00",
         "categories": []} for i in range(3)
    ] + [
        {"title": "Old unmatched bike lane story", "url": "cut",
         "source": "S", "published": "2026-06-02T00:00:00+00:00",
         "categories": []},
        {"title": "Old Weber Spur bike milestone", "url": "kept",
         "source": "S", "published": "2026-06-01T00:00:00+00:00",
         "categories": []},
    ]
    (tmp_path / "news.json").write_text(json.dumps({
        "fetched_at": "2026-07-13T12:00:00+00:00",
        "feeds": [{"url": "u", "source": "S", "kind": "rss", "ok": True,
                   "items": items}],
    }))

    out = aggregate.build_news_items({"lines": []}, PROJECTS)
    urls = [i["url"] for i in out["items"]]
    assert "kept" in urls and "cut" not in urls and len(urls) == 4
