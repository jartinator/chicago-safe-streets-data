---
surface: S2 — Perplexity (perplexity.ai, free web surface, logged out)
run_date: 2026-07-23
driver: Playwright (Chromium, headed), one fresh browser context per run
runs_executed: 7 protocol runs + 1 control + 1 replicate
---

# S2 surface notes — Perplexity, logged out

Recorded once for the whole surface so the individual transcripts don't repeat
it. Read this before grading any S2 run.

## How the runs were driven

The in-app Browser pane is banned in this repo (see `CLAUDE.md`), so every S2
run was driven with **Playwright** (Chromium, headed, `#ask-input`
contenteditable, Enter to submit, poll until the page text stops changing for
9s). One **fresh browser context per run** — no shared cookies, no shared
history — satisfying the protocol's contamination rule. The cookie banner was
dismissed with **"Only necessary"** on every run.

No login wall, CAPTCHA, or rate limit was encountered at any point; all nine
launches returned a normal answer page. Model label: the surface reports only
"Search" / an unnamed default model while logged out — it does not name a model,
so none is recorded.

## The finding that governs every pointed run on this surface

**Perplexity's logged-out free surface does not fetch user-supplied URLs at
all.** Every one of the five pointed runs answered with some variant of "I don't
have access to the specified file right now" and then searched the open web
instead. Zero runs fetched `llms.txt`.

This could have been an OYL defect — a robots.txt block, a GitHub Pages
bot-block, a fetcher-hostile content type. It is not. Two checks, both run
2026-07-23:

1. **robots.txt is permissive.** Live
   `https://jartinator.github.io/chicago-safe-streets-data/robots.txt` is
   `User-agent: *` / `Allow: /` plus a sitemap line. Nothing is disallowed, and
   PerplexityBot is not singled out.
2. **The file is fetchable by a Perplexity-identified client.** `curl` with
   `User-Agent: PerplexityBot/1.0 (+https://perplexity.ai/perplexitybot)`
   returns **HTTP 200** for `llms.txt`, as does a plain UA.
3. **Control run (`control-wikipedia.md`)** — the same pointed prompt shape
   aimed at `https://en.wikipedia.org/wiki/Bloomingdale_Trail`, one of the most
   fetchable pages on the web, got the same refusal: *"I can't browse the page
   directly right now."*

So the pointed condition on this surface measures **nothing about OYL**. It
measures a surface that ignores URL instructions. Graded honestly, D=0 on
pointed S2 runs is a property of Perplexity-logged-out, and the C/V/R axes on
those runs grade *what the surface did instead* — which turns out to be the more
interesting result.

**Consequence for the study:** the protocol's assumption that "pointed" isolates
recipe-following from discovery holds on S1 (an agent with real fetch tools) and
fails on S2. Any proposal that leans on "we can tell people to point their
assistant at our llms.txt" must survive the fact that on at least one major
consumer surface, pointing does nothing.

## Discovery result across the surface

**0 / 7.** OYL appears in zero answers and in zero of the 70 captured source
links, unaided or pointed. See `../00-summary.md` for the graded table.

The unaided source lists are dominated by **personal-injury law-firm content
marketing** (briskmanandbriskman.com, chicagolawyer.com, daveabels.com,
wallacemiller.com, chicagobikeinjurylawyers.com, dispartilaw.com,
natlawreview.com press release) plus local news and Reddit. On Q1 unaided, 4 of
10 sources were law-firm pages. That is the competitive set OYL is invisible
against — not other civic-data projects.

## Artifacts

Raw capture per run (JSON: verbatim prompt, full body text, source hrefs,
timestamps, answer URL; plus a full-page PNG) was produced by the Playwright
runner. The verbatim answer text and source lists are reproduced in each
transcript file here; the transcripts are the citable record.
