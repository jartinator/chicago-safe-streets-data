# Agent-discovery hardening — making the agent layer *findable*

*Companion to the agent-first API plan
(`docs/superpowers/plans/2026-07-13-agent-api-layer.md`). That plan built the
contract (`llms.txt`, `site/api/v1/`, JSON Schemas). This doc is about the
other half of the problem: an agent that never learns the contract exists.*

## The problem this fixes

A post-mortem of a real hand-off found the site was configured correctly —
`llms.txt` existed, well-formed — yet an agent still failed to find it. The
failure was **discovery, not configuration**. When a fetch degrades to
head-only metadata (a very common partial-failure mode), the one channel that
survived carried no pointer to the contract: the meta-description said "open
JSON API for AI agents" but never said *where*.

The rule of thumb: **an agent contract is only as good as the weakest channel
through which an agent might learn it exists.** Put the pointer in the channel
that survives degradation — and then in every other channel too, because you
don't get to choose which one survives.

## The degradation ladder

An agent lands on exactly one rung; you don't control which. Design so every
rung has a pointer.

| Rung | What the agent gets | Pointer present? |
|---|---|---|
| 0 | Nothing — can't fetch (not indexed, harness restriction) | out of our control; mitigated by SEO |
| 1 | `<head>` only — title, meta, `<link>` tags | ✅ `rel="llms-txt"`, JSON-LD, meta path |
| 2 | Raw static HTML body, no JS execution | ✅ `<noscript>` block (body is JS-rendered) |
| 3 | Fully JS-rendered DOM | ✅ home page agent section |
| 4 | Agent tries `/llms.txt` on convention | ✅ canonical root location |
| 5 | Human pastes the URL | ✅ copy-paste prompts on home page |

## Checklist (this repo's status)

- [x] `llms.txt` at site root, canonical location — pipeline-generated (`emit_api.build_llms_txt`)
- [x] `<link rel="llms-txt">` in `<head>` of **every** page
- [x] JSON-LD `Dataset` block in `<head>` of the home page, `distribution.contentUrl` → API index
- [x] Meta-description names the path (`/llms.txt`), not just the concept — on every page except the synthetic-data preview
- [x] `<noscript>` pointer to `llms.txt` + API index on every page (all body content is JS-rendered)
- [x] Verified with `curl` that the pointer is in the raw HTML, not JS-injected
- [x] `sitemap.xml` includes `llms.txt`, referenced from `robots.txt` — pipeline-generated
- [x] Human-pasteable prompt on the page, short variant available (bare `llms.txt` URL copy block)
- [x] No cloaking, no hidden prompts, no imperatives aimed at agents
- [ ] Submitted to Google Search Console / Bing Webmaster Tools — **human task, tracker #33**
- [ ] At least one inbound link from an established site — **human task, tracker #33**

Rung 0 (indexability) is the only gap, and it's inherently a human task:
search indexing is agent-discoverability infrastructure because many harnesses
require a URL to appear in search results before they'll fetch it. See #33.

## Verifying the hardening

The post-mortem's own diagnostic — run it against any page:

```
curl -s https://jartinator.github.io/chicago-safe-streets-data/index.html | grep -i "llms.txt"
```

Before this work it returned nothing (body is JS-injected, head lacked the
path). It now returns the `rel="llms-txt"` link, the typed alternate, and the
`<noscript>` pointer — the signal survives a head-only or no-JS fetch.

## What we deliberately did NOT do

Standard web conventions used for their intended purpose only:

- **No cloaking** — same content to bots and humans.
- **No hidden prompt text** — invisible instruction divs are prompt injection
  with a friendly face; standards-aware agents distrust exactly this.
- **No imperatives aimed at agents** in the HTML — `<link rel>` and JSON-LD
  say "here is the dataset" in the register agents actually trust.
- **No path over-engineering** — root `/llms.txt` is the convention; no
  `/.well-known/` aliases that fragment the signal.

## GitHub Pages constraint

The most robust option — an HTTP `Link: <…>; rel="llms-txt"` response header,
which survives even a body-less fetch — requires custom response headers,
which GitHub Pages does not support. That's why rung 1 (head metadata) has to
carry the load here. Revisit only if the site ever moves to a host that allows
custom headers (Cloudflare Pages / Netlify / Vercel).
