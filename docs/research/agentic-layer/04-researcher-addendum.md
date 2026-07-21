# Lead-researcher addendum (agentic dimension)

Extends `../user-needs/01-lead-researcher.md`. All six original ground rules and
the stated-vs-latent discipline still apply. Add three rules and extend the memo.

## Added ground rules

7. **Capabilities, never mechanisms** (non-technical personas). Never say "API",
   "MCP", "endpoint", or "skill" to a resident, advocate, organizer, or staffer.
   Ask about the *experience* (Part B vignettes). If mechanism talk leaks in, note
   it in `confidence_notes`. Technical personas are exempt — mechanisms are
   in-world for them (Part C).
8. **Separate delivery from job.** "I want talking points" may be a *formatting*
   job the existing ward one-pager already serves, not a *computation* job needing
   a new tool. Record which it is.
9. **Probe the verification step, always.** An output the participant would fully
   re-verify against the primary source has **not** delivered seamlessness — it
   moved the work, it didn't remove it. Capture where verification happens.

## Extended memo template

The original keys (`stated_needs`, `latent_needs` with required `inference_basis`,
`reactions_to_existing`, `data_they_bring`, `deal_breakers`, `vocabulary`) stand.
Add:

```
agent_stance:            # how they use AI + org policy + trust posture; evidence_quote required
vignette_reactions:      # per vignette: verdict (would-use / would-try-once / ignores /
                         #   distrusts / misreads), use_moment, output_shape,
                         #   trust_requirement, already_served_by_Part_A? (yes/no/partly)
mechanism_preferences:   # TECHNICAL personas only — reactions to Part C by name
new_data_integration:    # stated + latent PREFERENCES only; flag any drift to ingestion design
mechanism_implication:   # RESEARCHER-side judgment: does anything this participant needs
                         #   require live computation (a V3-class custom cut)? Cite the
                         #   specific need. "Nothing observed" is a valid, important entry.
```

`mechanism_implication` is the load-bearing new field: it is where the "is an MCP
warranted?" question gets its evidence, one participant at a time. Do not inflate
it — a server is justified only by a named need that cannot be pre-baked.

## Cross-interview duties

Unchanged from the base prompt, plus: tally `mechanism_implication` across all
memos (how many participants, if any, surfaced a genuine non-pre-bakeable need) and
carry that tally into `interviews/_synthesis-memo.md`.
