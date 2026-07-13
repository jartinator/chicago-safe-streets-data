"""Extract agenda items from committee agenda PDFs and attach City Clerk context.

pull_hearings.py already fetches upcoming committee meetings from the eLMS
public API, but the agenda itself only exists as a linked PDF — the API's
`agenda` field is empty even on published meetings (verified 2026-07-13).
"Approval of O2026-0025394" means nothing to a resident deciding whether to
attend, so this module:

  1. downloads each upcoming meeting's agenda PDF (from raw/hearings.json),
  2. extracts its text (pypdf) and parses it deterministically — section
     headings, ward numbers in parens, record numbers like O2026-0026797,
     verbatim item text; no LLM, no invented words (see CONTRIBUTING.md),
  3. looks each record number up in the eLMS matter API
     (GET /matter?filter=recordNumber eq '...') for the canonical title,
     sponsor, type, and status, plus a public detail-page link.

Output: raw/agenda_items.json keyed by agenda_url; aggregate.py merges items
into hearings.json per meeting. Same non-fatal posture as every third-party
pull: any failure (download, parse, lookup) degrades to fewer or plainer
items and never raises the pipeline. Idempotent: re-running overwrites cleanly.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from io import BytesIO

import requests

from config import RAW_DIR, ELMS_API_URL, ELMS_MATTER_PAGE_URL
from socrata import write_json

# Record numbers as they appear on agendas: a short type prefix (O ordinance,
# Or order, R resolution, SO/SR substitutes, A appointment, F filing, M misc,
# CL claim, PO/PR proposals, Doc) + file year + serial. Longer prefixes first
# so "Or2026-…" doesn't half-match as "O".
RECORD_NUMBER_RE = re.compile(
    r"\b(?:Doc|SO|SR|SA|CL|PO|PR|Or|O|R|A|F|M)\d{2,4}-\d{4,}\b")

# Leading ward tag on an item line: "(28) …" or the empty "() …" / "( ) …"
# used for citywide items.
_WARD_PREFIX_RE = re.compile(r"^\(\s*(\d{0,2})\s*\)\s*")

# En/em dashes and pypdf's occasional U+FFFD for them -> plain "-".
_DASH_RE = re.compile("[–—−�]")

_PAGE_NUMBER_RE = re.compile(r"^\d{1,3}$")

AGENDA_TEXT_MAX_CHARS = 600
PDF_MAX_BYTES = 10 * 1024 * 1024  # agendas are a few hundred KB; cap the odd blob


def _clean_line(line):
    return _DASH_RE.sub("-", line).strip()


def _is_all_caps(text):
    return bool(text) and text == text.upper() and any(c.isalpha() for c in text)


def _paragraphs(page_text):
    """Blank-line-separated paragraphs as lists of cleaned lines, dropping
    page numbers and the standalone WARD column header."""
    paras, cur = [], []
    for raw in page_text.splitlines():
        line = _clean_line(raw)
        if not line:
            if cur:
                paras.append(cur)
                cur = []
            continue
        if _PAGE_NUMBER_RE.match(line) or line == "WARD":
            continue
        cur.append(line)
    if cur:
        paras.append(cur)
    return paras


def _split_heading(lines):
    """Split a paragraph into (heading_lines, item_lines).

    Agenda section headings are ALL-CAPS lines at the top of a page's block
    ("MAYORAL", "RULE 45:", "ORDINANCES FOR VACATIONS, … ALLEYS:"), sometimes
    running straight into the first item with no blank line between. A leading
    caps line counts as heading when it ends with ":", is a single word, or
    the first non-caps-run line starts with a ward "(…)" tag.

    Known limitation: a multi-word, colon-less heading glued (no blank line)
    to an item that has no ward tag matches none of those terminators, so the
    heading text stays prepended to that item's verbatim agenda_text and
    `section` keeps its previous value — a cosmetic degradation, never
    invented text. Every heading style observed on real eLMS agendas so far
    is covered by the three rules above.
    """
    caps_run = 0
    while (caps_run < len(lines) and _is_all_caps(lines[caps_run])
           and not RECORD_NUMBER_RE.search(lines[caps_run])
           and not _WARD_PREFIX_RE.match(lines[caps_run])):
        caps_run += 1

    end = 0
    for i in range(caps_run):
        if lines[i].endswith(":"):
            end = i + 1
            break
        if i + 1 < len(lines) and _WARD_PREFIX_RE.match(lines[i + 1]):
            end = i + 1
            break
        if " " not in lines[i]:
            end = i + 1
            break
    return lines[:end], lines[end:]


def _para_text(lines):
    text = re.sub(r"\s+", " ", " ".join(lines)).strip()
    if len(text) > AGENDA_TEXT_MAX_CHARS:
        text = text[:AGENDA_TEXT_MAX_CHARS].rstrip() + "…"
    return text


def parse_agenda_pages(pages):
    """Deterministic parse of extracted agenda page texts.

    Returns {"amended": bool, "items": [{record_number|None, ward|None,
    section|None, agenda_text}]}. Page 1 is the cover (committee, date,
    optional AMENDED banner); items never appear on it.
    """
    amended = bool(pages) and "AMENDED" in pages[0].upper()
    items, seen_records, section = [], set(), None

    for page_text in pages[1:]:
        for para in _paragraphs(page_text):
            heading, rest = _split_heading(para)
            if heading:
                section = " ".join(heading).rstrip(":").strip()
            if not rest:
                continue
            m = _WARD_PREFIX_RE.match(rest[0])
            ward = int(m.group(1)) if m and m.group(1) else None
            if m:
                rest = [_WARD_PREFIX_RE.sub("", rest[0], count=1)] + rest[1:]
            text = _para_text(rest)
            if not text:
                continue
            records = RECORD_NUMBER_RE.findall(text)
            # A leftover all-caps run with no record number or ward tag is a
            # section heading that lacked a ":" terminator, not an item.
            if not records and ward is None and all(_is_all_caps(l) for l in rest):
                section = text.rstrip(":").strip()
                continue
            if records:
                for rn in records:
                    if rn in seen_records:
                        continue
                    seen_records.add(rn)
                    items.append({"record_number": rn, "ward": ward,
                                  "section": section, "agenda_text": text})
            else:
                items.append({"record_number": None, "ward": ward,
                              "section": section, "agenda_text": text})
    return {"amended": amended, "items": items}


def extract_pdf_pages(pdf_bytes):
    """Per-page text from a PDF, or None if it isn't parseable (scanned/corrupt)."""
    from pypdf import PdfReader  # imported here so a missing dep degrades, not crashes
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # pypdf raises a zoo of types on malformed files
        print(f"  WARNING: PDF text extraction failed ({exc}).", file=sys.stderr)
        return None
    return pages if any(p.strip() for p in pages) else None


def fetch_pdf(url):
    """Agenda PDF bytes, or None on any failure (non-fatal posture)."""
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200 or len(resp.content) > PDF_MAX_BYTES:
            return None
        return resp.content
    except requests.RequestException:
        return None


def fetch_matter(record_number):
    """The eLMS matter row for a record number, or None on failure/no match."""
    try:
        resp = requests.get(
            f"{ELMS_API_URL}/matter",
            params={"filter": f"recordNumber eq '{record_number}'", "limit": 1},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        rows = resp.json().get("data")
        return rows[0] if isinstance(rows, list) and rows else None
    except (requests.RequestException, ValueError, AttributeError):
        return None


def enrich_item(item, matter):
    """Attach canonical context from a fetched eLMS matter row (verbatim
    official fields only — a failed lookup leaves the PDF text to stand alone)."""
    if not matter:
        return item
    item.update({
        "title": matter.get("title") or None,
        "type": matter.get("type") or None,
        "status": matter.get("statusDescription") or matter.get("status") or None,
        "sponsor": matter.get("filingSponsor") or None,
        "category": matter.get("matterCategory") or None,
        "matter_url": (f"{ELMS_MATTER_PAGE_URL}{matter['matterId']}"
                       if matter.get("matterId") else None),
    })
    return item


def agenda_urls(hearings_raw):
    """Distinct agenda_urls across all upcoming meetings, in meeting order."""
    urls = []
    for committee in hearings_raw.get("committees") or []:
        for meeting in committee.get("meetings") or []:
            url = meeting.get("agenda_url")
            if url and url not in urls:
                urls.append(url)
    return urls


def build_agendas(urls, fetch_pdf_fn=fetch_pdf, fetch_matter_fn=fetch_matter):
    """{agenda_url: {"amended": bool, "items": [...]}} for every URL whose PDF
    downloaded and yielded text; failed URLs are simply absent."""
    agendas = {}
    matter_cache = {}
    for url in urls:
        pdf = fetch_pdf_fn(url)
        pages = extract_pdf_pages(pdf) if pdf else None
        if pages is None:
            print(f"  WARNING: no agenda text for {url} — meeting keeps its "
                  f"PDF link only.", file=sys.stderr)
            continue
        parsed = parse_agenda_pages(pages)
        for item in parsed["items"]:
            rn = item["record_number"]
            if rn:
                if rn not in matter_cache:
                    matter_cache[rn] = fetch_matter_fn(rn)
                enrich_item(item, matter_cache[rn])
        agendas[url] = parsed
    return agendas


def main():
    argparse.ArgumentParser(
        description="Extract agenda items from committee agenda PDFs (eLMS)."
    ).parse_args()

    hearings_path = RAW_DIR / "hearings.json"
    if not hearings_path.exists():
        print("agenda_items: raw/hearings.json absent (pull_hearings did not run) "
              "— nothing to do.", file=sys.stderr)
        return
    hearings_raw = json.loads(hearings_path.read_text())

    urls = agenda_urls(hearings_raw)
    agendas = build_agendas(urls)

    write_json(RAW_DIR / "agenda_items.json", {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agendas": agendas,
    })
    total = sum(len(a["items"]) for a in agendas.values())
    enriched = sum(1 for a in agendas.values() for i in a["items"] if i.get("title"))
    print(f"agenda_items: {len(agendas)}/{len(urls)} agenda PDFs parsed, "
          f"{total} items ({enriched} matched to City Clerk records)")


if __name__ == "__main__":
    main()
