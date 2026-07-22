"""Pull public news-feed items about Chicago bike/street safety (RSS only).

The site publishes the official record (meetings, council records, alderman
records, main routes) but not the narrative around it. This module fetches a
small allowlist of public RSS feeds (config.NEWS_FEEDS — Streetsblog Chicago,
Block Club Chicago's transportation category, a Google News search) and stores
each item **verbatim**: headline, canonical link, outlet, publish date, and
the publisher's own category tags. Never body text, never images — see
docs/research/news-layer/evidence-feeds.md for the licensing evidence.

No analysis happens here (agenda-items precedent): relevance filtering and
ward/alderman/route matching live in aggregate.py. Same non-fatal posture as
every third-party pull — a failed feed is recorded ok:false and skipped, an
all-fail run writes an honest empty raw file, and nothing ever raises the
pipeline. A 403/429 means the outlet opted out: skip it, never work around.
Idempotent: re-running overwrites cleanly.
"""
import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote, urlparse

import requests

from config import (NEWS_FEEDS, NEWS_USER_AGENT, NEWS_FEED_MAX_BYTES, RAW_DIR,
                    PROPOSED_PROJECTS_PATH,
                    NEWS_PROJECT_QUERY_PHRASES_PER_PROJECT,
                    NEWS_RESOLVE_TIMEOUT_S, NEWS_RESOLVE_ATTEMPTS,
                    NEWS_RESOLVE_BACKOFF_S, GNEWS_ARTICLE_URL_TMPL,
                    GNEWS_BATCHEXECUTE_URL)
from socrata import write_json

_HEADERS = {
    "User-Agent": NEWS_USER_AGENT,
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}


def fetch_feed(url):
    """Feed XML bytes, or None on any failure (non-fatal posture)."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=30)
        if resp.status_code in (403, 429):
            print(f"  WARNING: {url} returned {resp.status_code} — outlet "
                  f"opted out this run; skipping.", file=sys.stderr)
            return None
        if resp.status_code != 200 or len(resp.content) > NEWS_FEED_MAX_BYTES:
            return None
        return resp.content
    except requests.RequestException:
        return None


# Headers for the decode-params fetch below — looks like an ordinary reader:
# browser-like Accept headers, same honest bot User-Agent (issue #42).
_RESOLVE_HEADERS = {
    "User-Agent": NEWS_USER_AGENT,
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
}

_GNEWS_ARTICLE_ID_RE = re.compile(r"/rss/articles/([^/?]+)")
_GNEWS_SIG_RE = re.compile(r'data-n-a-sg="([^"]+)"')
_GNEWS_TS_RE = re.compile(r'data-n-a-ts="([^"]+)"')

# The batchexecute RPC id ("Fbv4je") and the literal garturlreq payload shape
# are undocumented, reverse-engineered from Google News' own front-end
# (issue #42) — preserved byte-for-byte except the interpolated id/ts/sig.
_GNEWS_RPC_ID = "Fbv4je"
_GNEWS_GARTURLREQ_TMPL = (
    '["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,'
    'null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{id}",'
    '{ts},"{sig}"]'
)


def _google_host(url):
    host = urlparse(url).netloc.lower()
    return host == "google.com" or host.endswith(".google.com")


def _gnews_article_id(url):
    """The opaque article id (query string stripped) from a
    news.google.com/rss/articles/<id> URL, or None if the url isn't that
    shape — nothing to decode (issue #42)."""
    match = _GNEWS_ARTICLE_ID_RE.search(url)
    return match.group(1) if match else None


def _gnews_decode_params(article_id, get_fn):
    """(sig, ts) scraped off the article's stub page, or None when either
    attribute is missing — decode isn't possible for this article (caller
    keeps the original redirect url). Raises requests.RequestException on a
    network failure so the caller's retry/backoff can catch it."""
    resp = get_fn(GNEWS_ARTICLE_URL_TMPL.format(article_id=article_id),
                  headers=_RESOLVE_HEADERS, timeout=NEWS_RESOLVE_TIMEOUT_S)
    sig_match = _GNEWS_SIG_RE.search(resp.text)
    ts_match = _GNEWS_TS_RE.search(resp.text)
    if not sig_match or not ts_match:
        return None
    return sig_match.group(1), ts_match.group(1)


def _gnews_batchexecute(article_id, ts, sig, post_fn):
    """The real publisher URL from the batchexecute RPC, or None if the
    response doesn't parse the way we expect. The response format is
    undocumented and may change without notice (issue #42) — every parsing
    step below is defensive and returns None rather than raising. Raises
    requests.RequestException on a network failure so the caller's
    retry/backoff can catch it."""
    inner = [_GNEWS_RPC_ID,
             _GNEWS_GARTURLREQ_TMPL.format(id=article_id, ts=ts, sig=sig)]
    envelope = [[inner]]
    payload = "f.req=" + quote(json.dumps(envelope))
    resp = post_fn(GNEWS_BATCHEXECUTE_URL,
                   headers={"Content-Type":
                            "application/x-www-form-urlencoded;charset=UTF-8",
                            "User-Agent": NEWS_USER_AGENT},
                   data=payload, timeout=NEWS_RESOLVE_TIMEOUT_S)
    # The body is NOT one JSON document: it's a sequence of length-prefixed
    # JSON-array chunks (")]}'" magic prefix, then repeating "<byte len>\n
    # <array>\n"), so parse it line by line rather than json.loads-ing the
    # whole thing. Scan each array-shaped line for the wrb.fr/Fbv4je envelope
    # whose element [2] is a JSON string holding the real URL at index [1].
    try:
        for line in resp.text.splitlines():
            line = line.strip()
            if not line.startswith("[["):
                continue
            try:
                chunk = json.loads(line)
            except ValueError:
                continue
            for entry in chunk:
                if (isinstance(entry, list) and len(entry) > 2
                        and entry[0] == "wrb.fr" and entry[1] == _GNEWS_RPC_ID):
                    return json.loads(entry[2])[1]
        return None
    except (IndexError, ValueError, KeyError, TypeError):
        return None


def _retry_network(fn, sleep_fn):
    """Call fn() up to NEWS_RESOLVE_ATTEMPTS times with NEWS_RESOLVE_BACKOFF_S
    backoff between tries, swallowing requests.RequestException. Returns
    fn()'s result (which may itself be None — a non-network decode miss is
    not retried), or None if every attempt raised."""
    for attempt in range(NEWS_RESOLVE_ATTEMPTS):
        if attempt:
            sleep_fn(NEWS_RESOLVE_BACKOFF_S)
        try:
            return fn()
        except requests.RequestException:
            continue
    return None


def resolve_redirect(url, get_fn=requests.get, post_fn=requests.post,
                      sleep_fn=time.sleep):
    """Publisher URL behind a Google News redirect, decoded via the
    batchexecute RPC Google's own front-end uses (issue #42 — following the
    redirect gets a JS interstitial from datacenter IPs), or the original URL
    on any failure — a working redirect link beats none."""
    article_id = _gnews_article_id(url)
    if article_id is None:
        return url  # not a /rss/articles/ link — nothing to decode

    params = _retry_network(lambda: _gnews_decode_params(article_id, get_fn),
                             sleep_fn)
    if not params:
        return url
    sig, ts = params

    real_url = _retry_network(
        lambda: _gnews_batchexecute(article_id, ts, sig, post_fn), sleep_fn)
    return real_url or url


def _iso_pubdate(text):
    """RFC-2822 pubDate -> UTC-normalized ISO 8601 string, or None if
    unparseable. Normalizing to UTC keeps the published strings lexically
    sortable across feeds that stamp different UTC offsets."""
    if not text:
        return None
    try:
        return (parsedate_to_datetime(text.strip())
                .astimezone(timezone.utc).isoformat(timespec="seconds"))
    except (TypeError, ValueError):
        return None


def parse_feed(xml_bytes, default_source, kind):
    """Verbatim items from one RSS document:
    [{title, url, source, published, categories: []}]. Returns None on a
    parse failure (distinct from a valid-but-empty feed's []). Google News
    items get their outlet name from the per-item <source> element; their
    opaque redirect links are resolved later, in build_feeds, after title
    dedup has dropped the ones we'd throw away anyway."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None
    items = []
    for node in root.iter("item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        if not title or not link:
            continue
        source = default_source
        if kind == "google_news":
            source = (node.findtext("source") or "").strip() or None
            # Google appends " - <outlet>" to every title; strip it so the
            # published headline is the outlet's own and cross-feed title
            # dedup can catch the same story arriving via the direct feed.
            if source and title.endswith(f" - {source}"):
                title = title[: -len(f" - {source}")].rstrip()
        items.append({
            "title": title,
            "url": link,
            "source": source,
            "published": _iso_pubdate(node.findtext("pubDate")),
            "categories": [c.text.strip() for c in node.findall("category")
                           if c.text and c.text.strip()],
        })
    return items


def _title_key(title):
    return " ".join(title.lower().split())


def dedup_items(feeds):
    """Drop repeat items across feeds in place (same URL, then same
    normalized title — Google News re-surfaces the allowlisted outlets' own
    stories). First feed listed wins, so direct feeds beat the aggregator."""
    seen_urls, seen_titles = set(), set()
    for feed in feeds:
        kept = []
        for item in feed["items"]:
            url, tkey = item["url"], _title_key(item["title"])
            if url in seen_urls or tkey in seen_titles:
                continue
            seen_urls.add(url)
            seen_titles.add(tkey)
            kept.append(item)
        feed["items"] = kept
    return feeds


def build_feeds(feed_configs, fetch_fn=fetch_feed, resolve_fn=resolve_redirect):
    """[{url, source, kind, ok, items: [...]}] — one entry per configured
    feed. ok means fetched AND parsed (a valid feed with zero items this
    week is still ok:true); a failed feed is ok:false with empty items."""
    feeds = []
    for cfg in feed_configs:
        raw = fetch_fn(cfg["url"])
        items = parse_feed(raw, cfg["source"], cfg["kind"]) if raw else None
        if raw is not None and items is None:
            print(f"  WARNING: {cfg['url']} fetched but did not parse as RSS.",
                  file=sys.stderr)
        feeds.append({"url": cfg["url"], "source": cfg["source"],
                      "kind": cfg["kind"],
                      "query_is_filter": bool(cfg.get("query_is_filter")),
                      "ok": items is not None,
                      "items": items or []})

    # Title dedup FIRST (direct feeds are listed before the aggregator, so
    # they win), so Google items that merely re-surface an allowlisted
    # outlet's own story are dropped before paying one resolution request
    # each for their opaque redirect links. A second pass after resolution
    # catches URL-level duplicates that only become visible once resolved.
    dedup_items(feeds)
    attempted = resolved = 0
    for feed in feeds:
        if feed["kind"] == "google_news":
            for item in feed["items"]:
                item["url"] = resolve_fn(item["url"])
                attempted += 1
                if not _google_host(item["url"]):
                    resolved += 1
    if attempted:
        # Keeps a resolution regression (issue #42: 54/57 items stuck on
        # redirect URLs) visible in every run's log.
        print(f"  {resolved}/{attempted} google links resolved")
    return dedup_items(feeds)


def project_query_feed(path=PROPOSED_PROJECTS_PATH):
    """One extra Google News feed config derived from the proposed-projects
    roster's curated phrases, or None when the roster is absent, unreadable,
    or empty (non-fatal — the base feeds still run). Several real projects'
    current coverage lives on outlets outside the base allowlist (evidence:
    docs/research/proposed-routes-news/evidence-proposals.md), so the query
    follows the roster instead of hard-coding more outlets."""
    try:
        roster = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    phrases = []
    for project in roster.get("projects") or []:
        # Strict phrases first; corridor-name (ctx) phrases fill remaining
        # slots — the query is Chicago-scoped below either way.
        pool = ((project.get("news_phrases") or [])
                + (project.get("news_phrases_ctx") or []))
        phrases.extend(pool[:NEWS_PROJECT_QUERY_PHRASES_PER_PROJECT])
    if not phrases:
        return None
    query = ("(" + " OR ".join(f'"{p}"' for p in phrases)
             + ") Chicago when:90d")
    # No query_is_filter: corridor-name phrases ("Grand Avenue") surface
    # unrelated stories — these items must pass the normal relevance gate
    # (safety keyword, topic category, or a project match).
    return {"url": ("https://news.google.com/rss/search?q=" + quote(query)
                    + "&hl=en-US&gl=US&ceid=US:en"),
            "source": None, "kind": "google_news"}


def news_feed_configs():
    """The base allowlist plus the roster-derived project query (when any)."""
    feeds = list(NEWS_FEEDS)
    extra = project_query_feed()
    if extra:
        feeds.append(extra)
    return feeds


def main():
    argparse.ArgumentParser(
        description="Pull public news-feed items (RSS) about Chicago bike safety."
    ).parse_args()

    feeds = build_feeds(news_feed_configs())
    write_json(RAW_DIR / "news.json", {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "feeds": feeds,
    })
    total = sum(len(f["items"]) for f in feeds)
    ok = sum(1 for f in feeds if f["ok"])
    print(f"news: {ok}/{len(feeds)} feeds fetched, {total} items (verbatim; "
          f"relevance/matching happens in aggregate)")


if __name__ == "__main__":
    main()
