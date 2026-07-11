"""Shared Legistar Web API fetch helpers (OData-style query params).

webapi.legistar.com is the hosted API Chicago's council used before migrating
to eLMS in 2023 (see LEGISTAR_DATA_FROZEN_AT in config.py) — public, no auth,
paged with $top/$skip. Confirmed live 2026-07-11.
"""
import time

import requests

from config import LEGISTAR_API_URL

_SESSION = requests.Session()


def _get(path, params, retries=3):
    url = f"{LEGISTAR_API_URL}/{path.lstrip('/')}"
    delay = 2
    for attempt in range(retries + 1):
        resp = _SESSION.get(url, params=params, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        if attempt == retries:
            resp.raise_for_status()
        time.sleep(delay)
        delay *= 2
    raise RuntimeError("unreachable")


def fetch_all(path, filter_=None, orderby=None, page_size=1000, max_pages=50, log=print):
    """Yield rows from a Legistar endpoint, paging with $top/$skip."""
    skip = 0
    total = 0
    for _ in range(max_pages):
        params = {"$top": page_size, "$skip": skip}
        if filter_:
            params["$filter"] = filter_
        if orderby:
            params["$orderby"] = orderby
        rows = _get(path, params)
        total += len(rows)
        yield from rows
        if log:
            log(f"  ...{path} at skip={skip}: {len(rows)} rows (total {total})")
        if len(rows) < page_size:
            break
        skip += page_size


def fetch_one(path):
    return _get(path, {})


def keyword_filter(field, keywords):
    """Build an OData $filter OR'ing substringof(keyword, field) for each keyword."""
    return " or ".join(f"substringof('{kw}',{field})" for kw in keywords)
