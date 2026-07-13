"""pull_news.py — RSS parsing, dedup, and non-fatal degradation.

Network is never touched: fetch/resolve functions are dependency-injected
(same convention as test_pull_agenda_items.py)."""
import pull_news


RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>Streetsblog Chicago</title>
  <item>
    <title>Milwaukee Avenue protected bike lanes extended</title>
    <link>https://chi.streetsblog.org/2026/07/10/milwaukee-pbl</link>
    <pubDate>Fri, 10 Jul 2026 15:30:00 +0000</pubDate>
    <category>Milwaukee Avenue</category>
    <category>1st Ward</category>
    <category><![CDATA[Bicycling]]></category>
  </item>
  <item>
    <title>Untitled link stays out</title>
    <link></link>
  </item>
  <item>
    <title>Bad date survives with published null</title>
    <link>https://chi.streetsblog.org/2026/07/09/bad-date</link>
    <pubDate>not a date</pubDate>
  </item>
</channel></rss>"""

GOOGLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Chicago's Bike Lanes Don't Hurt Businesses - Block Club Chicago</title>
    <link>https://news.google.com/rss/articles/opaque123</link>
    <pubDate>Tue, 23 Jun 2026 12:00:00 +0000</pubDate>
    <source url="https://blockclubchicago.org">Block Club Chicago</source>
  </item>
</channel></rss>"""


def test_parse_feed_verbatim_fields():
    items = pull_news.parse_feed(RSS, "Streetsblog Chicago", "rss")
    assert [i["title"] for i in items] == [
        "Milwaukee Avenue protected bike lanes extended",
        "Bad date survives with published null",
    ]
    first = items[0]
    assert first["url"] == "https://chi.streetsblog.org/2026/07/10/milwaukee-pbl"
    assert first["source"] == "Streetsblog Chicago"
    assert first["published"] == "2026-07-10T15:30:00+00:00"
    assert first["categories"] == ["Milwaukee Avenue", "1st Ward", "Bicycling"]
    assert items[1]["published"] is None


def test_parse_feed_google_source_and_redirect_resolution():
    items = pull_news.parse_feed(
        GOOGLE_RSS, None, "google_news",
        resolve_fn=lambda url: "https://blockclubchicago.org/2026/06/23/bike-lanes")
    assert len(items) == 1
    assert items[0]["source"] == "Block Club Chicago"
    assert items[0]["url"] == "https://blockclubchicago.org/2026/06/23/bike-lanes"
    # Google's " - <outlet>" title suffix is stripped (headline stays the
    # outlet's own; enables cross-feed title dedup):
    assert items[0]["title"] == "Chicago's Bike Lanes Don't Hurt Businesses"


def test_parse_feed_malformed_xml_degrades_to_empty():
    assert pull_news.parse_feed(b"<rss><channel><item>", "X", "rss") == []


def test_build_feeds_dedups_across_feeds_direct_feed_wins():
    def fake_fetch(url):
        return GOOGLE_RSS if "google" in url else RSS

    feeds = pull_news.build_feeds(
        [{"url": "https://chi.streetsblog.org/feed/", "source": "Streetsblog Chicago",
          "kind": "rss"},
         {"url": "https://news.google.com/rss/search?q=x", "source": None,
          "kind": "google_news"}],
        fetch_fn=fake_fetch,
        # Resolve the Google item to a URL already seen from the direct feed:
        resolve_fn=lambda url: "https://chi.streetsblog.org/2026/07/10/milwaukee-pbl")
    assert feeds[0]["ok"] and len(feeds[0]["items"]) == 2
    assert feeds[1]["items"] == []  # duplicate URL dropped; aggregator loses


def test_build_feeds_dedups_same_title_different_url():
    rss_b = RSS.replace(b"chi.streetsblog.org/2026/07/10/milwaukee-pbl",
                        b"example.com/mirrored-story")
    feeds = pull_news.build_feeds(
        [{"url": "a", "source": "A", "kind": "rss"},
         {"url": "b", "source": "B", "kind": "rss"}],
        fetch_fn=lambda url: RSS if url == "a" else rss_b,
        resolve_fn=lambda url: url)
    assert len(feeds[0]["items"]) == 2
    assert feeds[1]["items"] == []  # same normalized titles


def test_build_feeds_failed_fetch_is_nonfatal():
    feeds = pull_news.build_feeds(
        [{"url": "a", "source": "A", "kind": "rss"},
         {"url": "b", "source": "B", "kind": "rss"}],
        fetch_fn=lambda url: RSS if url == "a" else None,
        resolve_fn=lambda url: url)
    assert feeds[0]["ok"] is True
    assert feeds[1] == {"url": "b", "source": "B", "kind": "rss",
                        "ok": False, "items": []}
