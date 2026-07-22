"""resolve_redirect's batchexecute decode (issue #42) — network mocked via
injected get_fn/post_fn, same convention as test_pull_news.py. Following the
Google News redirect gets a JS interstitial from datacenter IPs, so decoding
replays the batchexecute RPC Google's own front-end uses instead."""
import json

import pull_news

ARTICLE_ID = "CBMiopaque123"
GOOGLE_URL = f"https://news.google.com/rss/articles/{ARTICLE_ID}?oc=5"
REAL_URL = "https://blockclubchicago.org/2026/06/23/real-story"


class _Resp:
    """Minimal stand-in for a requests Response — just the .text these
    helpers read."""
    def __init__(self, text):
        self.text = text


def _decode_page_html(sig="SIG123", ts="1699999999"):
    return (f'<html><body><c-wiz data-n-a-sg="{sig}" '
            f'data-n-a-ts="{ts}"></c-wiz></body></html>')


def _batchexecute_body(real_url, article_id=ARTICLE_ID):
    """A realistic batchexecute response whose wrb.fr/Fbv4je entry decodes to
    real_url — the real format is the )]}' magic prefix followed by
    length-prefixed JSON-array chunks (NOT one JSON document), so this mirrors
    that so the parser is guarded against the shape it actually meets."""
    inner_payload = json.dumps(["garturlreq", real_url, article_id])
    wrb_entry = ["wrb.fr", "Fbv4je", inner_payload, None, None, None,
                 "generic"]
    chunk1 = json.dumps([wrb_entry, ["di", 89], ["af.httprm", 89, "-1", 12]])
    chunk2 = json.dumps([["e", 4, None, None, 183]])  # trailing noise chunk
    return ")]}'\n\n" + f"{len(chunk1)}\n{chunk1}\n{len(chunk2)}\n{chunk2}\n"


def test_resolve_redirect_decodes_via_batchexecute():
    get_calls, post_calls = [], []

    def fake_get(url, headers=None, timeout=None):
        get_calls.append({"url": url, "headers": headers, "timeout": timeout})
        return _Resp(_decode_page_html())

    def fake_post(url, headers=None, data=None, timeout=None):
        post_calls.append({"url": url, "headers": headers, "data": data,
                            "timeout": timeout})
        return _Resp(_batchexecute_body(REAL_URL))

    out = pull_news.resolve_redirect(GOOGLE_URL, get_fn=fake_get,
                                      post_fn=fake_post,
                                      sleep_fn=lambda s: None)
    assert out == REAL_URL
    assert len(get_calls) == 1  # success on the first try — no retry
    assert get_calls[0]["url"] == pull_news.GNEWS_ARTICLE_URL_TMPL.format(
        article_id=ARTICLE_ID)
    assert get_calls[0]["headers"]["User-Agent"] == pull_news.NEWS_USER_AGENT
    assert get_calls[0]["timeout"] == pull_news.NEWS_RESOLVE_TIMEOUT_S
    assert len(post_calls) == 1
    assert post_calls[0]["url"] == pull_news.GNEWS_BATCHEXECUTE_URL
    assert post_calls[0]["headers"]["User-Agent"] == pull_news.NEWS_USER_AGENT
    assert post_calls[0]["data"].startswith("f.req=")


def test_resolve_redirect_missing_decode_params_returns_original():
    # HTML without the data-n-a-sg/data-n-a-ts attributes — decode isn't
    # possible for this article, so the original redirect url survives:
    def fake_get(url, **kwargs):
        return _Resp("<html><body>no attrs here</body></html>")

    def fake_post(url, **kwargs):
        raise AssertionError("batchexecute should never be called")

    out = pull_news.resolve_redirect(GOOGLE_URL, get_fn=fake_get,
                                      post_fn=fake_post,
                                      sleep_fn=lambda s: None)
    assert out == GOOGLE_URL


def test_resolve_redirect_batchexecute_network_failure_falls_back():
    # Decode params fetch succeeds, but every batchexecute POST fails — one
    # retry with backoff, then the original redirect url survives (non-fatal,
    # the item is never dropped):
    sleeps, post_attempts = [], []

    def fake_get(url, **kwargs):
        return _Resp(_decode_page_html())

    def fake_post(url, **kwargs):
        post_attempts.append(url)
        raise pull_news.requests.ReadTimeout("timed out")

    out = pull_news.resolve_redirect(GOOGLE_URL, get_fn=fake_get,
                                      post_fn=fake_post,
                                      sleep_fn=sleeps.append)
    assert out == GOOGLE_URL
    assert len(post_attempts) == pull_news.NEWS_RESOLVE_ATTEMPTS
    assert sleeps == [pull_news.NEWS_RESOLVE_BACKOFF_S] * (
        pull_news.NEWS_RESOLVE_ATTEMPTS - 1)


def test_resolve_redirect_unparseable_batchexecute_body_returns_original():
    def fake_get(url, **kwargs):
        return _Resp(_decode_page_html())

    def fake_post(url, **kwargs):
        return _Resp("garbage")

    out = pull_news.resolve_redirect(GOOGLE_URL, get_fn=fake_get,
                                      post_fn=fake_post,
                                      sleep_fn=lambda s: None)
    assert out == GOOGLE_URL


def test_resolve_redirect_non_article_google_url_returned_unchanged():
    # A Google News search-results link isn't a /rss/articles/ redirect —
    # nothing to decode:
    search_url = "https://news.google.com/rss/search?q=bike+lane&hl=en-US"

    def fail_get(url, **kwargs):
        raise AssertionError("should not fetch a non-article url")

    def fail_post(url, **kwargs):
        raise AssertionError("should not post for a non-article url")

    out = pull_news.resolve_redirect(search_url, get_fn=fail_get,
                                      post_fn=fail_post,
                                      sleep_fn=lambda s: None)
    assert out == search_url


def test_resolve_redirect_direct_publisher_url_returned_unchanged():
    # Already a direct outlet link (not google.com at all) — never touched:
    direct_url = "https://chi.streetsblog.org/2026/07/10/milwaukee-pbl"

    def fail_get(url, **kwargs):
        raise AssertionError("should not fetch a direct publisher url")

    def fail_post(url, **kwargs):
        raise AssertionError("should not post for a direct publisher url")

    out = pull_news.resolve_redirect(direct_url, get_fn=fail_get,
                                      post_fn=fail_post,
                                      sleep_fn=lambda s: None)
    assert out == direct_url
