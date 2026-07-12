"""Tag pulled council records as bike/street-safety-relevant, using an LLM.

This is a deliberate, documented exception to CONTRIBUTING.md's "pull modules
are deterministic, no LLMs" rule (see DECISIONS.md). It sits AFTER the
deterministic pull stage, never before: pull_council_records.py already fetched
real matters/sponsors from Legistar using a broad keyword net (config.py
SAFETY_TOPIC_KEYWORDS); this module only decides, per already-fetched record,
whether it's *actually* about street/bike safety (keyword matches include false
positives like "Bike the Boulevard" event permits) or is a distinct kind of
false negative (a bill that's substantively about safety but didn't use an
exact keyword — out of scope for now; the pull-time net is the recall backstop).

Guardrail: this NEVER invents a vote, sponsor, matter, or date — only labels
records that were already deterministically fetched, mirroring DECISIONS.md #8
("never auto-generate alderman names") applied to classification.

Caching: tags are cached to raw/safety_topic_tags.json keyed by matter_id, so
re-runs only classify new records (cost control). A hand-maintained
raw/safety_topic_corrections.json can override any tag — same manual-override
posture as aldermen.json.

Degradation: if ANTHROPIC_API_KEY is unset, the `anthropic` package is
missing, or any API call fails, this falls back to marking the record
topic_relevant=true with tagged_by="keyword_fallback" (since it already passed
the keyword net) rather than blocking the pipeline. aggregate.py badges
keyword_fallback tags distinctly from llm-reviewed ones.

Usage: python classify_safety_topic.py [--model claude-haiku-4-5-20251001]
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from config import RAW_DIR
from council_merge import load_all_council_records
from socrata import write_json

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

TAG_TOOL = {
    "name": "tag_safety_relevance",
    "description": "Record whether a piece of Chicago City Council legislation is "
                    "substantively about street or bike safety.",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic_relevant": {
                "type": "boolean",
                "description": "True if the matter is substantively about street/bike/"
                                "pedestrian safety infrastructure or policy (e.g. bike "
                                "lanes, traffic calming, Complete Streets, Vision Zero). "
                                "False for incidental keyword matches (e.g. a special "
                                "event permit for a bike race, a claim for bicycle theft).",
            },
            "topic_reason": {
                "type": "string",
                "description": "One short sentence explaining the call.",
            },
        },
        "required": ["topic_relevant", "topic_reason"],
    },
}


def load_cache(path):
    if path.exists():
        return {r["matter_id"]: r for r in json.loads(path.read_text())}
    return {}


def load_corrections(path):
    if path.exists():
        return {r["matter_id"]: r for r in json.loads(path.read_text())}
    return {}


def classify_with_llm(client, model, record):
    prompt = (
        f"Title: {record.get('title')}\n"
        f"Matter type: {record.get('type')}\n"
        f"Body: {record.get('body')}\n"
        f"Sponsors: {', '.join(record.get('sponsors') or []) or '(none listed)'}\n\n"
        "Is this substantively about street or bike safety (infrastructure or policy), "
        "as opposed to an incidental keyword match like an event permit or unrelated claim?"
    )
    resp = client.messages.create(
        model=model,
        max_tokens=300,
        tools=[TAG_TOOL],
        tool_choice={"type": "tool", "name": "tag_safety_relevance"},
        messages=[{"role": "user", "content": prompt}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "tag_safety_relevance":
            return block.input["topic_relevant"], block.input["topic_reason"]
    raise ValueError("model did not return a tool_use block")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    records, _ = load_all_council_records(RAW_DIR)
    if not records:
        print("classify_safety_topic: no council records (pull stage produced "
              "nothing or failed) — nothing to classify", file=sys.stderr)
        return
    cache_path = RAW_DIR / "safety_topic_tags.json"
    corrections_path = RAW_DIR / "safety_topic_corrections.json"
    cache = load_cache(cache_path)
    corrections = load_corrections(corrections_path)
    if not corrections_path.exists():
        write_json(corrections_path, [])

    to_classify = [r for r in records if r.get("matter_id") not in cache
                   and r.get("matter_id") not in corrections]

    client = None
    if to_classify:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("WARNING: anthropic package not installed — falling back to "
                      "keyword_fallback tags. See DECISIONS.md.", file=sys.stderr)
        else:
            print("WARNING: ANTHROPIC_API_KEY not set — falling back to keyword_fallback "
                  "tags. See DECISIONS.md.", file=sys.stderr)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    llm_tagged = fallback_tagged = 0
    for r in to_classify:
        mid = r["matter_id"]
        if client:
            try:
                relevant, reason = classify_with_llm(client, args.model, r)
                cache[mid] = {"matter_id": mid, "topic_relevant": relevant,
                              "topic_reason": reason, "tagged_by": "llm",
                              "model": args.model, "tagged_at": now}
                llm_tagged += 1
                continue
            except Exception as exc:  # API errors, malformed responses, rate limits
                print(f"WARNING: classification failed for matter {mid} ({exc}) — "
                      f"falling back to keyword_fallback tag", file=sys.stderr)
        cache[mid] = {"matter_id": mid, "topic_relevant": True,
                      "topic_reason": "Matched the keyword net; not yet reviewed by classifier.",
                      "tagged_by": "keyword_fallback", "model": None, "tagged_at": now}
        fallback_tagged += 1

    write_json(cache_path, list(cache.values()))
    print(f"classify_safety_topic: {llm_tagged} llm-tagged, {fallback_tagged} keyword_fallback, "
          f"{len(records) - len(to_classify)} already cached/corrected")


if __name__ == "__main__":
    main()
