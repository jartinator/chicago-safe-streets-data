"""Shared Socrata fetch helpers: paging, batched id lookups, GeoJSON pulls.

Every pull module goes through fetch_all()/fetch_by_ids() so paging, logging,
and politeness live in one place. Open JSON endpoints, no app token required
for modest volumes (a token can be supplied via SOCRATA_APP_TOKEN to raise
throttling limits).
"""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

import requests

from config import SOCRATA_DOMAIN, PAGE_SIZE, ID_BATCH_SIZE, ID_FETCH_WORKERS

_SESSION = requests.Session()
_TOKEN = os.environ.get("SOCRATA_APP_TOKEN")
if _TOKEN:
    _SESSION.headers["X-App-Token"] = _TOKEN


def _get(url, params, retries=4):
    delay = 2
    for attempt in range(retries + 1):
        try:
            resp = _SESSION.get(url, params=params, timeout=120)
        except requests.RequestException:
            # Issue #56: retry on transient network errors (ReadTimeout, ConnectionError, etc.)
            if attempt == retries:
                raise
            time.sleep(delay)
            delay *= 2
            continue
        if resp.status_code == 200:
            return resp
        if attempt == retries:
            resp.raise_for_status()
        time.sleep(delay)
        delay *= 2
    raise RuntimeError("unreachable")


def fetch_all(dataset_id, select=None, where=None, order=None, group=None,
              page_size=PAGE_SIZE, log=print):
    """Yield rows from a Socrata dataset, paging with $limit/$offset until exhausted."""
    url = f"{SOCRATA_DOMAIN}/resource/{dataset_id}.json"
    offset = 0
    total = 0
    while True:
        params = {"$limit": page_size, "$offset": offset}
        if select:
            params["$select"] = select
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order
        if group:
            params["$group"] = group
        rows = _get(url, params).json()
        total += len(rows)
        yield from rows
        if log:
            log(f"  ...page at offset {offset}: {len(rows)} rows (total {total})")
        if len(rows) < page_size:
            break
        offset += page_size


def fetch_by_ids(dataset_id, id_field, ids, select=None, extra_where=None,
                 batch_size=ID_BATCH_SIZE, max_workers=ID_FETCH_WORKERS, log=print):
    """Yield rows where id_field is in `ids`, batched to keep URLs within limits.

    Batches are fetched concurrently (max_workers threads) because these lookups are
    hundreds of small independent requests and were the pipeline's wall-clock bottleneck.
    Results are yielded in input-batch order (ThreadPoolExecutor.map preserves order), so
    output is identical to a sequential fetch — only faster.
    """
    url = f"{SOCRATA_DOMAIN}/resource/{dataset_id}.json"
    ids = list(ids)
    batches = [ids[i:i + batch_size] for i in range(0, len(ids), batch_size)]
    limit = batch_size * 20

    def fetch_batch(batch):
        quoted = ",".join("'" + str(x).replace("'", "''") + "'" for x in batch)
        where = f"{id_field} in({quoted})"
        if extra_where:
            where = f"({where}) AND ({extra_where})"
        params = {"$limit": limit, "$where": where}
        if select:
            params["$select"] = select
        return _get(url, params).json()

    total = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for idx, rows in enumerate(pool.map(fetch_batch, batches)):
            if log and len(rows) == limit:
                log(f"  WARNING: id batch {idx} returned exactly $limit={limit} rows "
                    f"-- results may be truncated; consider raising batch_size*20's multiplier")
            total += len(rows)
            yield from rows
            if log and idx % 20 == 0:
                log(f"  ...id batch {idx * batch_size}-{idx * batch_size + len(batches[idx])} "
                    f"of {len(ids)}: total rows {total}")


def fetch_geojson(dataset_id, limit=PAGE_SIZE):
    """Fetch a dataset's geometry export as a GeoJSON FeatureCollection (paged)."""
    url = f"{SOCRATA_DOMAIN}/resource/{dataset_id}.geojson"
    features = []
    offset = 0
    while True:
        resp = _get(url, {"$limit": limit, "$offset": offset})
        page = resp.json().get("features", [])
        features.extend(page)
        if len(page) < limit:
            break
        offset += limit
    return {"type": "FeatureCollection", "features": features}


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f)
    return path
