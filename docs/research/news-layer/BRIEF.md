# In the news — what shipped, why, and how (plain language)

**Date:** 2026-07-13 · **Branch:** feat/news-coverage-layer · Companion to
the [design doc](../../superpowers/specs/2026-07-13-news-coverage-design.md)
and [decision #29](../../../DECISIONS.md).

## What shipped

The site now shows **recent news coverage next to the official record**:

- **Take Action page**: each ward's report gains a "Recent coverage for this
  ward" section — up to five recent headlines (last 90 days) that mention the
  ward, its alderperson, or a major street in it, right below the upcoming
  committee meetings.
- **Ward one-pager** (the printable brief): a new "In the news (90 days)"
  row with up to three headlines.
- Every line is just the **headline, the outlet's name, the date, and a
  link**. We never copy article text or images. If nothing was written about
  a ward, the section says so out loud ("No coverage found… outlets cover
  some neighborhoods more than others") instead of quietly disappearing.
- A new dataset ([news_items.json](../../../site/data/news_items.json), 56
  items in the first pull, 18 different outlets) and a new card on the
  Sources page explaining exactly where this comes from and what its limits
  are.

## Why

Our earlier user research kept finding the same thing: most people don't
meet civic data raw — they meet it through a Block Club or Streetsblog
story, and the people doing ward work track that coverage by hand (one
described a half-trusted Google Alert plus a network of texts). The site had
the official record — meetings, ordinances, alderperson records, routes —
but not the story that makes any of it mean something. An agenda line like
"O2026-0026797" tells you *what*; the news story tells you *why it matters*.

Before building, we ran the concept past the same four simulated Chicago
research subjects from the earlier study (everyday rider, ward-office
staffer, professional advocate, West Side organizer). All four said they'd
use it — and all four said the same two things, which shaped the build:

1. **One wrong match poisons everything.** A headline attached to the wrong
   ward doesn't just look bad; it makes people doubt the site's crash
   numbers too. So matching is deliberately conservative: it would rather
   miss a story than mislabel one, and **every match records exactly how it
   was made** (hover a headline to see it, e.g. "names Ald. Ramirez"). A
   wrong match is now something you can check, not something you have to
   take on faith.
2. **Don't guess which story goes with which meeting.** All four rejected
   auto-linking stories to specific ordinances or hearings, even as an
   option — so that idea is permanently dead, not postponed. Coverage sits
   *near* the meetings list; it never claims to be *about* a meeting.

## How it works

1. Once a week, alongside the other data pulls, a small script reads three
   **public RSS feeds**: Streetsblog Chicago, Block Club Chicago's
   transportation section, and a Google News search (which brings in the
   Tribune, Sun-Times, TV stations, and neighborhood outlets). Headlines and
   links only — the legally safe, outlet-friendly subset. The script
   identifies itself honestly (`OnYourLeftNewsBot`), and if an outlet ever
   blocks it, it skips that outlet rather than sneaking around.
2. The pipeline then matches each headline to things the site already
   tracks, using the outlets' own tags first (Streetsblog literally tags
   stories "35th Ward" and "Ald. Ruth Cruz"), then strict name rules:
   street names only count with "Avenue/Street/Boulevard…" after them, and
   an alderperson's bare last name never matches on its own.
3. Everything else is the site's normal machinery: the data ships as a
   versioned file with a provenance badge (headlines are **real**; the
   matching is marked **derived**), the Sources page documents the
   limitations, and if the feeds are down the pages degrade honestly.

## What to know / limits

- These are **independent editorial outlets** — listing a story is not an
  endorsement, and the outlet's name is always shown. That's also why the
  Google News supplement matters: it keeps the list from being one outlet's
  voice.
- Coverage is uneven across the city. The empty-state wording exists
  precisely because a quiet news box on the West Side usually means "nobody
  wrote about it," not "nothing happened."
- Matching will miss things (by design). The linked article is always the
  authority.
- Deliberately not built: story-to-meeting guessing (killed by research),
  article summaries (we never put words in outlets' mouths), and an
  agent-API endpoint for news (deferred to avoid colliding with the API
  work in flight; it's a small follow-up).
