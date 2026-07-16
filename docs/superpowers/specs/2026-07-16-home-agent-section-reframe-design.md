# Home page — reframe the agent section toward plain-language data access

## Problem

The home page's final section, rendered by `agentHTML()` in
`site/assets/js/home.js`, is written for developers. It is titled **"For AI
agents & builders: the machine-readable layer"** and leads with
"versioned JSON endpoint", "CORS-open", a `Start here` pair of raw URLs, and an
"Or from the shell" `curl` block.

Three problems, all from the same root — it assumes the reader fetches JSON:

1. The paste-in prompt duplicates guidance already inside `llms.txt` (it defines
   the data tiers and citation in `_meta`); the extra instructions do no work
   beyond telling the model to go read the file.
2. "Start here" lists **two** links — `llms.txt` and `api/v1/index.json` — but
   `llms.txt` already has its own `## Start here` pointing at `index.json`, so
   the second link is just the first link's next hop surfaced a level early.
3. "Or from the shell" is unexplained jargon.

Meanwhile the page never serves the reader who *isn't* a developer: someone who
just wants to ask questions about the data in plain language, or explore the
site with an assistant that can see the screen and talk it through with them.

## Goal

Retarget the section at plain-language data access, tied to the four user groups
the page already introduces (Journalists & researchers, Advocates & community
orgs, Elected officials & staff, Developers & AI agents). Keep the machine layer
discoverable for developers, but demote it to a single footer link.

## Non-goals

- No changes to `site/data/**`, `site/api/**`, or `site/llms.txt` (avoid the
  data-guard CI job; the section only *links* to these).
- No new section — this replaces the body of the existing `agentHTML()` only.
- No change to the four-persona "Find what you came for" block above it.

## Design

Rewrite `agentHTML()` in `site/assets/js/home.js`. New structure:

### Title
"For AI agents & builders: the machine-readable layer" →
**"Ask an AI assistant about this data"**

### Lead: two plain-language ways to use it
1. **Paste a link.** Give any assistant that can browse the `llms.txt` URL and
   ask questions in plain English — "Which ward is worst for hit-and-runs?" Each
   answer can tell you how reliable the number is (real vs. proxy vs. mock), so
   you know what to trust.
2. **Browse alongside.** Open the site with an assistant that can see the screen
   and talk through the map or a ward page with you while you look at it —
   nothing to copy. (Tool-agnostic phrasing: "an assistant that can browse
   alongside you", no product names.)

### Why it's useful — tied to the user groups
One concrete sentence, e.g.:
> A journalist can pull a headline stat with its caveat attached; an advocate
> can prep a ward one-pager for public comment; a staffer can check their ward's
> record — all by asking, instead of clicking through the site.

### The paste-in prompt (kept, de-jargoned)
Retain the one copy-block with the paste-in prompt. Rewrite the prompt text:
> Read `<llms.txt URL>` and answer questions about Chicago cyclist safety, bike
> infrastructure, and City Council accountability. Tell me how reliable each
> number is.

("Tell me how reliable each number is" replaces "citing the data tier of each
number.")

### Developer footer (demoted)
Remove the `Start here` link pair, the second `api/v1/index.json` copy-block, and
the entire "Or from the shell" / `curl` block. Replace with one line:
> Building something? Point code at the open JSON API — start at
> [Downloads & Docs](contributing.html). No key, no sign-up, rebuilt weekly.

This preserves discoverability of the API, kills the duplicate-link confusion
and the "from the shell" jargon, and keeps the "no key / rebuilt weekly" selling
points.

## Affected code

- `site/assets/js/home.js` — `agentHTML()` body only. The `oneLiner`, `llms`
  constants stay; `apiIndex` / `curl` constants and their copy-blocks are
  removed. `wireCopyButtons()` is unchanged (still wires the one remaining
  copy button).
- Possibly `site/assets/css/style.css` if `.home-agent` spacing assumed the
  removed sub-headings; verify visually, adjust only if needed.

## Verification

- `python -m http.server` on `site/`, load the home page in the browser pane.
- Confirm: new title; two-ways lead; user-group sentence; one working Copy
  button on the paste-in prompt; footer link resolves to `contributing.html`;
  no `curl` / no duplicate URL; no console errors.
- Check dark theme and mobile width for the trimmed section.

## Out of scope / risks

- `home.js` header comment references the "copy-paste access" intent; update the
  comment on `agentHTML()` to match the new framing so it doesn't mislead.
