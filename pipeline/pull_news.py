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
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import requests

from config import (NEWS_FEEDS, NEWS_USER_AGENT, NEWS_FEED_MAX_BYTES, RAW_DIR,
                    PROPOSED_PROJECTS_PATH,
                    NEWS_PROJECT_QUERY_PHRASES_PER_PROJECT)
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


def resolve_redirect(url):
    """Final URL after redirects (Google News links are opaque redirectors),
    or the original URL on any failure — a working redirect link beats none."""
    try:
        resp = requests.head(url, headers={"User-Agent": NEWS_USER_AGENT},
                             timeout=15, allow_redirects=True)
        return resp.url or url
    except requests.RequestException:
        return url


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
    # outlet's own story are dropped before paying one HEAD request each to
    # resolve their opaque redirect links. A second pass after resolution
    # catches URL-level duplicates that only become visible once resolved.
    dedup_items(feeds)
    for feed in feeds:
        if feed["kind"] == "google_news":
            for item in feed["items"]:
                item["url"] = resolve_fn(item["url"])
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
