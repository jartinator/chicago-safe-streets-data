"""Shared Chicago Councilmatic (DataMade) fetch helper — read-only SQL over HTTP.

puddle.datamade.us republishes official Chicago City Council data as a public
Datasette instance whose JSON API accepts arbitrary read-only SQL. This is how
we cross the post-2023-06-21 gap the Legistar Web API cannot (see config.py).
Public, no auth. Confirmed live 2026-07-11.

COUNCILMATIC_DATASETTE_URL is the UN-hashed base; the DB lives under a
content-hashed route that changes on nightly rebuilds, and Datasette 302s the
un-hashed path to it. requests follows the redirect and preserves ?sql=.
"""
import time

import requests

from config import COUNCILMATIC_DATASETTE_URL

_SESSION = requests.Session()


def query(sql, retries=3):
    """Run read-only SQL against the Councilmatic Datasette; return list[dict]."""
    url = f"{COUNCILMATIC_DATASETTE_URL}.json"
    params = {"sql": sql, "_shape": "array"}
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
