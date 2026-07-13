# Validation protocol: PFB BNA proposal

A focused re-run of the user-needs study machinery to validate one
proposal (`docs/projects/pfb-bna-proposal.md`) before implementation.
Reuses six personas from the original roster (US, ADV, WARD, CDOT, RIDER,
ORG); international personas skipped as out-of-scope for a Chicago-source
decision. Same rules as the full study: `personas/_shared-rules.md` binds
every persona; the interviewer follows `01-lead-researcher.md` (never
lead, stories not opinions, probe workarounds, respect persona limits).

## Interview structure (validation variant)

1. **Context re-anchor (brief).** Role + the last time they needed to
   characterize the *quality* of the bike network (not crashes). Do not
   present anything yet.
2. **Product recap.** One-paragraph plain-language recap of OYL today
   (from `02-data-inventory.md`) so reactions are grounded.
3. **Stimulus, element by element.** Present B1 (citywide scorecard),
   B2 (ward access scores), B3 (segment stress cross-check), B4 (peer
   strip) in persona-appropriate language, one at a time. Capture the
   immediate reaction before explaining further. For each: what would
   you use it for, concretely (which meeting, document, conversation)?
   What would you check before trusting it in front of your audience?
4. **Trust probes (mandatory, every interview):**
   - It's computed from OpenStreetMap by a national advocacy org, updated
     once a year, and only as current as volunteer mapping. Change anything?
   - Chicago scores 11/100. Does that number help you or hurt you?
   - The ward number is access-framed ("X% of residents have low-stress
     access to groceries"), not a danger ranking. React.
   - Where OYL's own quality grade disagrees with BNA stress, which do
     you believe, and what should the site do about the disagreement?
5. **Forced choice.** Rank B1–B4 for your own work; then: should OYL do
   *none* of this and spend the effort elsewhere? (Name the elsewhere.)
6. **Kill question.** What single thing about this integration, done
   wrong, would make you stop trusting the site?

## Output per interview

`interviews/<persona-id>.md`: transcript, then the analysis memo using
the template in `01-lead-researcher.md` — with `reactions_to_existing`
replaced by `reactions_to_proposal` (one entry per element B1–B4,
verdict: uses / would-use / ignores / distrusts / misreads). Latent
needs still require an inference basis; a latent need without one is
discarded at synthesis.

## Synthesis

`VERDICT.md` (strongest model, main loop): per-element verdict
(advance / advance-with-changes / kill), the changes required, tensions
between audiences, and what this method cannot tell us. Elements only
advance if supported by named participants across at least two audiences.
