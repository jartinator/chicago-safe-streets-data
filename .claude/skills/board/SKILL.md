---
name: board
description: Use when filing, labeling, or triaging GitHub issues/PRs for this repo, or adding items to the project board. Encodes this project's label taxonomy, initiative keys, the #33 human-task convention, and the board's Status/Initiative/Human fields.
---

# board — issue & project-board conventions for On Your Left!

This repo runs a **GitHub Project (v2)** board at the owner level (`@jartinator`),
plus a label taxonomy and issue templates. This skill keeps everything filed the
same way. Do NOT install third-party GitHub skills — use `gh` directly, guided by
this file.

## Labels (always apply at least a type + area)

- **type/** (exactly one): `type/bug` `type/feat` `type/docs` `type/data` `type/chore`
- **area/** (one or more): `area/pipeline` `area/site` `area/api` `area/foia` `area/news` `area/bna` `area/data` `area/infra`
- **priority/** (optional): `priority/p0` (blocker) `priority/p1` `priority/p2`
- **workflow**: `needs-human` (see below), `blocked` (waiting on an external dep),
  plus GitHub defaults `good first issue` / `help wanted` for contributor-friendly work.

## Initiative keys (registry of record: `docs/outbox/README.md`)

`core-site` · `foia` · `exposure-data` · `blu-partnership` · `gov-agent-layer` ·
`agent-api` · `ux-tranche2`

Every board item gets an **Initiative** value. Never invent a key — add to the
registry table first if a genuinely new initiative appears.

## The `needs-human` rule (binding — mirrors CLAUDE.md)

Tasks only a human can do (send a letter, submit an application, make a contact)
are tracked on **issue #33** with an `[initiative]` prefix and a link to the
`docs/outbox/` file or doc. When such a task surfaces:

1. Add/update the line on #33 in the same session.
2. If you also open a dedicated issue, give it the `needs-human` label so it shows
   in the board's **Human** view.
3. When the human reports it sent/answered: check the box on #33, update the
   outbox file's front matter, and (for FOIA) `docs/foia/log.md` — one pass.

## Filing an issue (CLI)

```bash
gh issue create \
  --title "pull_news: resolve Google News redirect URLs" \
  --label "type/bug,area/news,priority/p1" \
  --body "…"
```

Issue templates live in `.github/ISSUE_TEMPLATE/` (bug, feature, data). Prefer
them in the web UI so labels/fields auto-apply.

## Adding an item to the board (CLI — needs `project` scope once)

The board can't be driven by `gh` until the token has the scope. One-time grant:

```bash
gh auth refresh -s project,read:project   # opens a browser device login
```

Then, with the project number (find via `gh project list --owner jartinator`):

```bash
# add an existing issue/PR to the board
gh project item-add <PROJECT_NUMBER> --owner jartinator --url <ISSUE_URL>

# set the Status / Initiative fields
gh project item-edit --project-id <PID> --id <ITEM_ID> \
  --field-id <STATUS_FIELD_ID> --single-select-option-id <OPTION_ID>
```

If the scope isn't granted, do everything else (labels, #33, templates) and tell
the human the board add is the one step that needs the one-time login.

## Board shape (for reference)

- **Status**: Backlog → Ready → In Progress → In Review → Done
- **Initiative**: single-select, the keys above
- **Human?**: checkbox — set when `needs-human`
- Built-in workflows: new issues auto-add to Backlog; merged PR / closed issue → Done.
