# Project board setup — one-time, in the browser (~3 minutes)

The label taxonomy, issue templates, PR template, and the `/board` Claude skill
are already committed. The only piece that must be created in GitHub's web UI is
the **Project (v2) board** itself. No CLI or token login required.

## 1. Create the board

1. Go to **https://github.com/jartinator?tab=projects** → **New project**.
2. Pick the **Board** template. Name it **On Your Left! — roadmap**. Create.

## 2. Set the Status columns

The board starts with `Todo / In Progress / Done`. Rename/extend to:

`Backlog → Ready → In Progress → In Review → Done`

(Click the column header ▾ → edit; use **+ New column** for the extra two.)

## 3. Add two custom fields

Project menu (▾ top-right) → **Settings** → **+ New field**:

- **Initiative** — type *Single select*. Options (match the registry):
  `core-site` `foia` `exposure-data` `blu-partnership` `gov-agent-layer`
  `agent-api` `ux-tranche2`
- **Human?** — type *Checkbox*. (Set it on anything that also has the
  `needs-human` label.)

## 4. Connect the repo + automation

1. Settings → **Workflows**: enable **Item added to project → Status: Backlog**,
   and **Item closed → Status: Done** (covers merged PRs / closed issues).
2. Settings → **Manage access / Add repository** isn't needed for a user project,
   but to auto-pull issues: Workflows → **Auto-add to project** → filter
   `repo:jartinator/chicago-safe-streets-data is:issue is:open`.
3. Optionally add a second **view**: *Table*, grouped by **Initiative**, for a
   roadmap-style read.

## 5. Backfill the two existing issues

On issue **#42** and **#33** (right sidebar → **Projects** → pick the board),
then set Status + Initiative:

- #42 → Status **Backlog**, Initiative **core-site**
- #33 → Status **In Progress**, Initiative **core-site**, **Human? ✓**

## 6. (Optional) let Claude drive the board from the CLI

If you later want future Claude sessions to add/move cards automatically, grant
the token scope once, in a terminal:

```bash
gh auth refresh -s project,read:project
```

That opens a one-time browser device login. After that, the `/board` skill's
`gh project …` commands work. Skipping this is fine — the board still works
fully from the web UI.

---

See `.claude/skills/board/SKILL.md` for the label + initiative conventions every
issue should follow.
