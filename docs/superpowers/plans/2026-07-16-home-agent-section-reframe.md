# Home Agent-Section Reframe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe the home page's final section from a developer-facing "machine-readable layer" pitch into plain-language data access tied to the site's user groups, demoting the API/curl details to one footer link.

**Architecture:** A single self-contained edit to the `agentHTML()` string-builder in `site/assets/js/home.js`, plus its header comment. No data, API, or model-logic changes. Verification is the browser preview (the changed code is HTML output below a `typeof document` guard and is not Node-unit-testable without an unwarranted file restructure).

**Tech Stack:** Vanilla JS string templating, static site served by `python -m http.server`, in-app browser pane for verification.

## Global Constraints

- No changes to `site/data/**`, `site/api/**`, or `site/llms.txt` (data-guard CI job must not trip — this section only links to these).
- Tool-agnostic phrasing for the "browse alongside" idea — no product names (Claude in Chrome, ChatGPT, etc.).
- Preserve the existing `.home-agent` section wrapper class and the `wireCopyButtons()` mechanism (one Copy button remains).
- Keep the paste-in prompt's `llms.txt` URL built from the existing `SITE_ORIGIN` constant — never hardcode the full URL.

---

### Task 1: Reframe `agentHTML()` and its header comment

**Files:**
- Modify: `site/assets/js/home.js` — `agentHTML()` body (currently lines ~185-212) and the file header comment (line 3).

**Interfaces:**
- Consumes: `SITE_ORIGIN` (const at line 111), `B.esc(text)` (BSD escape helper, browser-only), the `copyBlock(id, text)` local helper (defined at lines ~191-193), `wireCopyButtons(root)` (wires `.agent-copy-btn` clicks, unchanged).
- Produces: the same `<section class="section-gap home-agent">…</section>` string contract consumed by the render path and `wireCopyButtons()`. Exactly one `.agent-copy` / `#agent-oneliner` copy block remains.

- [x] **Step 1: Update the file header comment (line 3)**

Current line 3 reads:
```
 * it's for with a concrete next action per audience, and how to use the
 * machine-readable agent layer. Same structure as action.js — a pure,
```
Replace the phrase "how to use the machine-readable agent layer" with "how to ask an AI assistant about the data". Resulting lines 2-3:
```
 * it's for with a concrete next action per audience, and how to ask an AI
 * assistant about the data. Same structure as action.js — a pure,
```

- [x] **Step 2: Replace the `agentHTML()` body**

Replace the entire function (current lines ~183-212, from the `// The agent-layer promotion:` comment through the closing `}` of `agentHTML`) with:

```javascript
  // The data-access promotion: plain-language ways to ask about the data, tied
  // to the site's user groups, with the developer API demoted to one footer
  // link. The one-liner is exactly what a person would paste into an assistant.
  function agentHTML() {
    const llms = `${SITE_ORIGIN}/llms.txt`;
    const oneLiner = `Read ${llms} and answer questions about Chicago cyclist ` +
      `safety, bike infrastructure, and City Council accountability. Tell me how ` +
      `reliable each number is.`;
    const copyBlock = (id, text) =>
      `<div class="agent-copy"><code id="${id}">${B.esc(text)}</code>` +
      `<button type="button" class="btn agent-copy-btn" data-copy="${id}">Copy</button></div>`;
    return `<section class="section-gap home-agent">` +
      `<h2>Ask an AI assistant about this data</h2>` +
      `<p>Every number on this site is also written up in plain language for ` +
      `AI assistants, so you can get answers without reading a single spreadsheet. ` +
      `Two ways to use it:</p>` +
      `<ul class="home-agent-ways">` +
      `<li><strong>Paste a link and ask.</strong> Give any assistant that can ` +
      `browse the web the link below, then ask in plain English — ` +
      `&ldquo;Which ward is worst for hit-and-runs?&rdquo; Each answer can tell ` +
      `you how solid the number is: measured, estimated, or a stand-in.</li>` +
      `<li><strong>Browse alongside.</strong> Open this site with an assistant ` +
      `that can see the screen and talk you through the map or a ward page while ` +
      `you look at it together — nothing to copy or paste.</li>` +
      `</ul>` +
      `<p class="home-agent-why">A journalist can pull a headline stat with its ` +
      `caveat attached; an advocate can prep a ward one-pager for public comment; ` +
      `a council staffer can check their ward's record — all by asking, instead ` +
      `of clicking through the site.</p>` +
      `<p class="muted">Paste this into an assistant that can browse the web:</p>` +
      copyBlock("agent-oneliner", oneLiner) +
      `<p class="home-agent-foot">Building something? Point code at the open JSON ` +
      `API — no key, no sign-up, rebuilt weekly. Start at the ` +
      `<a href="contributing.html">Downloads &amp; Docs page</a>, where every ` +
      `response carries its own provenance, data tier, and license.</p>` +
      `</section>`;
  }
```

Note what is removed vs. the original: the `apiIndex` and `curl` constants, the `<h3>Point an AI assistant at it</h3>` / `<h3>Start here</h3>` / `<h3>Or from the shell</h3>` sub-headings, and the `agent-llms` / `agent-api` / `agent-curl` copy blocks. Only `agent-oneliner` survives.

- [x] **Step 3: Confirm no dangling references**

Run:
```bash
grep -n "agent-api\|agent-curl\|agent-llms\|apiIndex\|Or from the shell\|Start here" site/assets/js/home.js
```
Expected: no matches (all removed).

- [x] **Step 4: Node smoke-check the module still loads**

The model export must be unaffected. Run:
```bash
node tests/ui/home-model.test.js
```
Expected: `home-model.test.js: all assertions passed`

- [x] **Step 5: Commit**

```bash
git add site/assets/js/home.js
git commit -m "feat(home): reframe agent section as plain-language data access"
```

---

### Task 2: Verify in the browser and adjust CSS if needed

**Files:**
- Possibly modify: `site/assets/css/style.css` (only if the trimmed section has spacing/list-style issues; `.home-agent-ways`, `.home-agent-why` are new class hooks).

**Interfaces:**
- Consumes: the rendered `.home-agent` section from Task 1.
- Produces: a visually correct section in light + dark, desktop + mobile.

- [x] **Step 1: Serve and load the home page**

Start the `site` preview (port 8741) and load `http://localhost:8741` in the browser pane.

- [x] **Step 2: Confirm content and behavior**

Verify via read_page / screenshot:
- Title reads "Ask an AI assistant about this data".
- Two bulleted ways ("Paste a link and ask", "Browse alongside") render.
- The user-group sentence is present.
- Exactly one Copy button; clicking it flips to "Copied" (wired by `wireCopyButtons`).
- Footer line links to `contributing.html` and the link resolves.
- No `curl`, no duplicate URL, no "Start here"/"Or from the shell".

- [x] **Step 3: Check console for errors**

Run read_console_messages. Expected: no errors from `home.js`.

- [x] **Step 4: Check dark theme and mobile width**

Use resize_window (mobile preset) and dark colorScheme. Confirm the list and footer spacing look intentional. If `.home-agent-ways` bullets are cramped or unstyled inconsistently with the rest of the page, add minimal rules to `site/assets/css/style.css` (match existing list spacing conventions); otherwise change nothing.

- [x] **Step 5: Commit (only if CSS changed)**

```bash
git add site/assets/css/style.css
git commit -m "style(home): spacing for reframed agent section"
```

---

## Self-Review

- **Spec coverage:** Title change ✓ (Task 1 Step 2). Two plain-language ways incl. browse-alongside, tool-agnostic ✓. User-group sentence ✓. De-jargoned paste-in prompt ✓ ("Tell me how reliable each number is"). Removal of duplicate `index.json` link + `curl`/"Or from the shell" ✓. One-line demoted footer to `contributing.html` with "no key / rebuilt weekly" ✓. Header comment update ✓ (spec "Out of scope / risks"). No `data/**`/`api/**`/`llms.txt` edits ✓. Browser + dark/mobile verification ✓.
- **Placeholder scan:** none — full replacement code is inline.
- **Type consistency:** `copyBlock`, `SITE_ORIGIN`, `B.esc`, `wireCopyButtons`, `agent-oneliner` id all match existing names in `home.js`.
