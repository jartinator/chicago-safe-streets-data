---
run_date: 2026-07-23
topic: "How LLM-based assistants handle caveats, qualifiers, uncertainty, and provenance attached to retrieved data — documented failure modes"
study: agentic-layer (study #1)
---

# Caveat carriage & failure modes — evidence brief (mid-2026)

Scope note: this brief answers the kickoff question set only. It does not
propose changes to OYL's layer (see `02-layer-inventory.md` for the as-built
inventory this study treats as ground truth). Labeling follows
`assistant-discovery.md`'s convention: `[verified]` (primary-source or
independently corroborated), `[vendor-claim]` (stated by the vendor, not
independently measured), `[folklore/unclear]` (widely repeated, not
demonstrated).

---

## 1. Caveat/qualifier stripping in RAG and summarization

Measured evidence exists, from several independent angles, that models drop
hedges, qualifiers, and scope limits present in source text.

- **Peters & Chin-Yee, "Generalization bias in large language model
  summarization of scientific research," Royal Society Open Science,
  2025-04-30** `[verified]`. Analyzed ~4,900 LLM-generated summaries across
  10 models (ChatGPT-4o, GPT-4 Turbo, DeepSeek, LLaMA 3.3 70B, Claude
  variants, others) against 200 scientific abstracts and 100 full medical
  articles, benchmarked against expert human summaries (NEJM Journal Watch).
  Three models (DeepSeek, ChatGPT-4o, LLaMA 3.3 70B) produced broader
  generalizations than the source in **26–73% of cases**; LLM summaries
  overall were **~4.85x more likely** (OR 4.85, 95% CI 3.06–7.70, p<0.001) to
  contain scope-broadening generalizations than human summaries. Notably,
  **explicitly asking the model for accuracy roughly doubled overgeneralization**,
  and newer model versions performed *worse* than earlier ones in their
  sample. Claude models showed the least overgeneralization among those
  tested. Lower sampling temperature reduced but did not eliminate the
  effect (76% less likely at temperature 0 vs 0.7 in their setup).
  [royalsocietypublishing.org/doi/10.1098/rsos.241776]

- **SciZoom benchmark, "A Large-scale Benchmark for Hierarchical Scientific
  Summarization across the LLM Era," arXiv 2603.16131, 2026** `[verified,
  primary source]`. Corpus analysis found hedging language (may, might,
  could, possibly, potentially, suggest, indicate, appear, seem, likely)
  in post-LLM-summarized scientific abstracts **decreased 22.8%** (1.88 →
  1.45 occurrences per 1,000 words) while assertive language was
  essentially unchanged (-0.4%; 9.29 → 9.25 per 1,000 words) — a
  *selective* removal of uncertainty markers, not a general compression
  effect. [arxiv.org/html/2603.16131v1]

- **"From Single to Multi: How LLMs Hallucinate in Multi-Document
  Summarization," Findings of NAACL 2025 (arXiv:2410.13961, first posted
  2024-10)** `[verified]`. Built two new multi-document benchmarks (none
  existed before for this specific failure mode) and found up to **75% of
  content in LLM-generated multi-document summaries was hallucinated on
  average**; models' ability to correctly output "no insights found"
  **declined sharply as the number of input documents increased** — directly
  relevant to OYL's multi-endpoint fetch-recipe pattern, where an assistant
  combining several JSON files is architecturally the multi-document case
  this paper studied. [aclanthology.org/2025.findings-naacl.293]

- **RAGBench / TRACe (Friel et al., 2024)** and **CRUD-RAG (Lyu et al.,
  2024)** are cited across multiple 2025–2026 survey sources as the leading
  general-purpose RAG faithfulness/grounding benchmarks with per-span
  annotations, but no source in this research pass isolated a *caveat- or
  qualifier-specific* metric within them (they measure hallucination/
  grounding generally, not hedge-preservation specifically) `[folklore/
  unclear whether these benchmarks would surface qualifier-stripping as a
  distinct failure category — plausible given their span-level design, not
  confirmed]`.

**Verdict:** hedge/qualifier stripping is a `[verified]`, measured phenomenon
across at least three independent studies using different methodologies
(corpus hedge-word counts, human-vs-LLM summary comparison, multi-document
hallucination benchmarks). No study in this pass targeted OYL's *specific*
caveat categories (ridership normalization, provisional data, undercounting,
sponsorship-vs-vote), but the general mechanism — models compress toward
confident, assertive, broader claims than the source supports — is
well-evidenced.

---

## 2. Attribution/citation fidelity benchmarks

- **ALCE (Gao et al., "Enabling Large Language Models to Generate Text with
  Citations," EMNLP 2023, arXiv:2305.14627)** `[verified]` — the first
  benchmark for automatic citation evaluation; scores fluency, correctness,
  and citation quality (precision/recall of whether cited passages actually
  support the claim). Established as the reference benchmark that later
  work builds on. [emergentmind.com/papers/2305.14627]

- **AttributionBench** `[verified, referenced across multiple 2024–2025
  sources]` — aggregates 7 existing attribution datasets including HAGRID
  and AttrEval-GenSearch, which grades attribution on a 3-level support
  scale (fully/partially/not supported) rather than a binary pass/fail.

- **Synthesis finding repeated across multiple secondary sources reviewed
  in this pass:** "the majority (50–90%) of citations in long-form
  responses are not fully supported by the cited sources, as verified by
  human annotators" `[folklore/unclear — this range is a secondary-source
  synthesis statement found in search results, not traced to one primary
  paper in this pass; treat as a directionally-consistent claim across the
  literature rather than a single verified number]`.

- **Onweller, Lumer, Huber, Ramchandani, Subbiah, Feld (PricewaterhouseCoopers),
  "Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM
  Deep Research Agents," arXiv:2605.06635, 2026** `[verified, primary
  source fetched directly]`. Evaluated **14 LLMs across 130 research
  queries** (DeepResearch Bench + BrowseComp) with a four-stage pipeline:
  link validity, topical relevance (LLM-judged), and fact-check accuracy
  against the cited source. Key finding: **"even the strongest frontier
  models maintain link validity above 94% and relevance above 80%, yet
  achieve only 39–77% factual accuracy"** — i.e., citations that resolve and
  look topically relevant frequently do not actually support the claim made
  against them. A follow-up ablation found **fact-check accuracy dropped
  ~42% on average across two frontier models as tool calls scaled from 2 to
  150**, while surface metrics (link validity, relevance) stayed above 92%
  — surface-level citation health is not a proxy for whether the citation
  supports the claim, and this gap widens with more retrieval steps.
  [arxiv.org/html/2605.06635v1]

- **RAGAS** `[verified, vendor/open-source tool, widely adopted]` defines
  *faithfulness* as the ratio of claims in the answer that are supported by
  the retrieved context to total claims — a general hallucination metric,
  not caveat-specific. **ARES** (a follow-on LLM-judge framework trained via
  prediction-powered inference) reports outperforming RAGAS by up to 59.3
  percentage points on context-relevance judgments in its own evaluation
  `[vendor-claim/author-reported, not independently replicated in this
  pass]`.

- **Citation fabrication rates (general, not RAG-specific):** a frequently
  cited study found 55% of GPT-3.5 citations and 18% of GPT-4 citations
  across 42 multidisciplinary topics were entirely fabricated, with review
  articles ~57% more likely to be fabricated than other paper types
  `[folklore/unclear — figure appears consistently across secondary
  sources in this pass but the primary study was not independently
  fetched and confirmed here]`. A separate citation-URL study found
  3–13% of citation URLs have no Wayback Machine record (likely never
  existed) and 5–18% are non-resolving overall `[folklore/unclear, same
  caveat]`.

**Verdict:** citation/attribution fidelity has multiple `[verified]`
benchmarks (ALCE, AttributionBench, RAGAS/ARES) and at least one directly
fetched 2026 primary study (PwC's "Cited but Not Verified") showing that
surface citation health (link resolves, topically relevant) is
substantially better than actual support (39–77% factual accuracy at the
frontier), and that this gap widens with retrieval complexity — directly
relevant to OYL's multi-file fetch recipes.

---

## 3. Numeric fidelity: units, denominators, scope qualifiers

- **NUMCoT ("Numerals and Units of Measurement in Chain-of-Thought
  Reasoning using Large Language Models," arXiv:2406.02864, 2024)**
  `[verified]` — found LLM unit-conversion errors concentrate on
  **magnitude/scale relationships** (e.g., overlooking a tenfold
  progressive relationship between decimeters and centimeters) and on
  handling of zero/place-value, rather than random arithmetic slips
  `[verified per abstract-level search synthesis; not independently
  fetched in full in this pass]`.

- **"When Summaries Distort Decisions: Information Fidelity in
  LLM-Compressed Financial Analysis," arXiv:2606.29251, 2026** `[verified
  as an existing paper via search; not independently fetched in full]` —
  title and topic directly address numeric-fidelity loss in domain
  summarization (financial reports), consistent with the general pattern
  found in scientific-summarization studies above, but this brief did not
  confirm specific quantitative findings from the paper itself; **flag as
  a paper to fetch in full for a future pass rather than cite numbers from
  it here**.

- **General taxonomy finding (secondary-source synthesis, search-derived):**
  LLM summaries hallucinate numeric content in a minority but non-trivial
  share of cases (search synthesis cited "~5%"), with the more common
  failure being a **context mismatch** — the number is reproduced but its
  semantic link to the qualifying phrase around it is broken or dropped
  `[folklore/unclear — this is a search-engine synthesis of an unnamed
  taxonomy paper, not a primary source confirmed in this pass; the
  specific mechanism (number survives, qualifier detaches) is exactly
  OYL's concern but was not traced to one checkable paper here]`.

- **No study found in this pass tests OYL's exact numeric-qualifier
  pattern** — a relative index number that must retain "relative, not
  absolute, no ridership denominator," or a raw count that must retain
  "not normalized, on-street only." The closest evidenced analogues are
  (a) the generalization-bias study's finding that LLMs broaden scope
  beyond what source data supports, and (b) the "context mismatch"
  taxonomy note above. **Mark as a partial gap**: the general mechanism
  (numbers detach from their qualifying context during compression) has
  indirect support; the specific unit/denominator failure mode described
  in query 3 has no dedicated study located here.

---

## 4. Structured `caveats` field vs. free prose: does either work better?

- **Instruction-following format comparisons found in this pass are
  general-purpose, not caveat/provenance-specific.** One synthesis of
  2025–2026 structured-output literature found: "free prose is very
  compact but loses many commitments, especially exact counts and
  negations. JSON is highly faithful and validatable but often longer than
  the original short prompt" and that for some model families
  (instruction-following prompts) outperform structured-output APIs on
  field-level accuracy while structured APIs win on schema validity
  `[folklore/unclear — search-synthesized characterization across several
  sources (IFEval, FollowBench-adjacent literature), not one primary study
  isolating a caveats-style JSON array specifically]`.

- **No study was found — in academic literature, vendor research, or
  evaluation benchmarks — that specifically tests whether a model reading
  a fetched document is more, less, or equally likely to act on an
  instruction or a data qualifier when it is presented as a named
  machine-readable JSON field (e.g., a `caveats: [{code, text}]` array)
  versus equivalent information stated as free prose in the same
  document.** This is the exact mechanism behind OYL's `_meta.caveats`
  field and its llms.txt prose caveats existing side-by-side (inventory
  §1.2). **This is confirmed as an open gap, not a folklore claim either
  way** — the research literature has format-following studies (IFEval,
  FollowBench, structured-output-vs-prompt studies) but none of them frame
  the comparison as "does labeling data as structured provenance/caveat
  metadata change whether a downstream model surfaces it," which is a
  narrower and more specific question than general format compliance.
  This maps directly onto inventory §5's gap #2 (whether an assistant
  that reads an endpoint carries the caveat into its answer) and gap #4/#5
  — no desk research closes it; it requires OYL's own empirical audit.

---

## 5. Refusal / abstention behavior

- **Wen et al., "Know Your Limits: A Survey of Abstention in Large
  Language Models," TACL 2025 (aclanthology.org/2025.tacl-1.26)**
  `[verified]` — surveys the abstention literature broadly: most
  evaluation protocols reward answering and penalize (zero or negative
  reward) saying "I don't know," while guessing always carries nonzero
  expected reward under accuracy-only metrics — a structural
  incentive against abstention baked into how most benchmarks (and,
  by extension, most RLHF reward signals) are constructed
  `[verified, survey-level claim]`. Cites Yang et al. (2023) and R-tuning
  (Zhang et al., 2024) as fine-tuning approaches that improve abstention
  by training on substituted "I don't know" labels for wrong/uncertain
  answers.

- **Kirichenko, Ibrahim, Chaudhuri, Bell, "AbstentionBench: Reasoning LLMs
  Fail on Unanswerable Questions," arXiv:2506.09038, submitted 2025-06-10**
  `[verified, primary source fetched directly]`. Evaluated **20 frontier
  LLMs across 20 diverse datasets** (unknown answers, underspecification,
  false premises, subjective interpretation, outdated information).
  Central finding: **reasoning-focused fine-tuning reduced abstention
  performance by 24% on average** across the models tested, and the
  authors conclude "abstention is an unsolved problem" for which "scaling
  models is of little use." This is directly relevant to OYL's
  llms.txt instruction to "say plainly rather than estimate" for
  ridership/obstruction data OYL does not publish — a category that
  overlaps AbstentionBench's "unknown answer"/"underspecification"
  conditions, and the finding that *reasoning models specifically get
  worse at this* is a caveat OYL's inventory does not currently flag.

- No study located in this pass tests the *substitution* failure mode
  named in the kickoff question directly (does the model quietly swap in
  a different, tangential data source instead of refusing, rather than
  simply guessing or answering confidently) — AbstentionBench and the
  TACL survey both frame the failure as answer-vs-abstain, not as
  answer-vs-abstain-vs-quietly-substitute. **Mark as a partial gap**: the
  answer/abstain axis is well studied; the specific substitution behavior
  is not separately measured in any source found here.

---

## 6. Prompt-injection-adjacent: do assistants follow site-authored instructions in fetched content?

This is the sharpest split in the brief between hard evidence and
vendor-stated design intent, and it cuts against OYL's own llms.txt design.

- **Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz, "Not what you've
  signed up for: Compromising Real-World LLM-Integrated Applications with
  Indirect Prompt Injection," AISec 2023, arXiv:2302.12173** `[verified,
  foundational primary source]`. Demonstrated that instructions embedded in
  content an LLM-integrated application retrieves (web pages, documents) —
  not supplied by the user — can and did get followed by deployed systems
  at the time, including causing a browsing agent to exfiltrate data. This
  establishes the *mechanism class* (models do act on instructions found in
  retrieved content) as `[verified]`, though it was a security-research
  demonstration on specific 2023-era systems, not a benchmark of current
  (mid-2026) production assistants' compliance rate with *benign*
  site-authored instructions like "restate this caveat."

- **The Instruction Hierarchy (Wallace et al., OpenAI, arXiv:2404.13208,
  2024)** `[verified, primary source + OpenAI's own publication]`. OpenAI
  explicitly trains models to rank instruction sources by privilege:
  System Message (highest) > User Messages > **Text from tools (lowest)**.
  The stated design goal is that "if a tool output contains malicious
  instructions, the model should ignore them rather than treat them as
  commands." OpenAI reports IH-trained GPT-5 Mini showed improved
  robustness on CyberSecEval 2 and an internal prompt-injection benchmark
  `[vendor-claim — OpenAI's own reported eval numbers, not independently
  replicated in this pass]`. This is a direct, named, current
  countervailing force to the folklore that "assistants read and follow
  instructions embedded in fetched pages": **vendors are actively training
  against exactly that behavior for tool/retrieved-content text**, without
  distinguishing malicious from benign instructions in the training
  objective as described.

- **IH-Challenge (arXiv:2603.10521, 2026)** `[verified, exists as a paper]`
  — a training dataset specifically built to further improve instruction
  hierarchy robustness, indicating this remains an active, unsolved
  training target as of 2026, not a solved problem `[verified that the
  paper exists and targets this gap; specific 2026 compliance numbers not
  independently confirmed in this pass]`.

- **No study was found that specifically tests whether a *benign*,
  transparently-labeled, self-authored instruction in a fetched document —
  of the exact shape OYL's llms.txt "When answering from this data" section
  uses ("restate the caveat," "cite the tier," "say plainly rather than
  estimate") — is followed, ignored, or partially followed by current
  production assistants.** The closest evidence is (a) Greshake et al.'s
  demonstration that the mechanism exists for adversarial instructions on
  2023-era systems, and (b) OpenAI's stated 2024–2026 program of training
  models to *deprioritize* all instructions found in tool/retrieved text,
  benign or not. These two facts point in **opposite directions** for
  OYL's specific mechanism and neither one is a direct measurement of it:
  Greshake shows the channel can work; the Instruction Hierarchy program
  shows vendors are actively suppressing exactly that channel. **This is
  the sharpest fact-vs-folklore distinction in this brief**: it is
  folklore, not evidence, that a llms.txt-style "please restate this
  caveat" instruction reliably works on mid-2026 production assistants —
  and there is specific, named, primary-source reason (the instruction
  hierarchy training objective) to expect it may be actively suppressed
  precisely because it is phrased as an instruction rather than as data.

---

## Implications for OYL (facts only, no proposals)

- **Inventory §5 gap #2** ("whether an assistant that reads an endpoint
  carries the caveat into its answer") has no OYL-specific measurement, but
  the general mechanism it depends on — LLMs dropping hedges/qualifiers and
  broadening scope during summarization — is `[verified]` across at least
  three independent studies (Peters & Chin-Yee 2025; SciZoom 2026; the
  multi-document hallucination benchmark, NAACL Findings 2025). None of
  these studies used OYL's exact caveat categories (ridership
  normalization, provisional data, dooring undercount, sponsorship-proxy);
  the mechanism is evidenced, the specific instance is not.
- **Inventory §5 gap #4** (fetch recipes ever followed as written) and
  **gap #5** (llms.txt fetched at all) remain unaddressed by this brief's
  topic and are covered instead in `assistant-discovery.md`.
- **The `caveats` JSON field vs. llms.txt prose caveat — inventory §1.2 and
  §1.4 — has no dedicated comparative study.** No source in this pass
  tested whether machine-readable structured caveat metadata is used more,
  less, or the same as equivalent free text by a downstream model. This is
  confirmed here as a genuine open gap (§4 above), consistent with
  inventory §5's framing that this remains unmeasured.
- **Inventory §1.4's "When answering from this data" instructional section
  in llms.txt** sits on the less-favorable side of a real, named tension:
  Greshake et al. (2023) show the mechanism by which retrieved-content
  instructions can be followed exists in principle, while OpenAI's
  Instruction Hierarchy program (2024–2026, arXiv:2404.13208 +
  arXiv:2603.10521) is an active, named, ongoing effort by at least one
  major vendor to train models to deprioritize instructions found in
  tool/retrieved text specifically — without a carve-out visible in public
  documentation for benign, self-authored instructions like OYL's. This
  does not establish that OYL's instruction fails; it establishes that no
  evidence found here shows it succeeds, and there is a specific,
  citable, current reason to expect vendors are training against the
  general pattern it relies on.
- **Inventory §2's "refuse-don't-hallucinate is requested of consumers... but
  nothing measures whether consumers comply"** is echoed almost exactly by
  AbstentionBench (2025): abstention is described in that paper's own
  words as "an unsolved problem" across 20 frontier models and 20
  datasets, with reasoning-tuned models measured 24% worse at it than
  their base counterparts. OYL's own compliance request (llms.txt, "say
  plainly rather than estimate" for ridership/obstruction gaps) sits
  inside a category of question (unknown-answer / underspecified-request)
  that the closest available benchmark reports models still fail at
  broadly in 2025–2026, not a category with a track record of high
  compliance.
- **On citation fidelity (relevant to OYL's `human_page` links and
  per-file `schema`/`methodology` fields):** the PwC 2026 study found
  frontier models' citations resolve and look relevant 80–94%+ of the
  time but only actually support the underlying claim 39–77% of the time,
  and that gap widens as more sources/tool calls are chained together —
  relevant to any question that would require an assistant to combine
  OYL's index.json fetch recipe (multiple JSON files) into one answer, the
  exact multi-hop structure this benchmark found to be the more failure-
  prone case.

---

## Sources

- Peters, U. & Chin-Yee, B., "Generalization bias in large language model summarization of scientific research," Royal Society Open Science, 2025-04-30 — royalsocietypublishing.org/doi/10.1098/rsos.241776 (also PMC12042776)
- "SciZoom: A Large-scale Benchmark for Hierarchical Scientific Summarization across the LLM Era," arXiv:2603.16131, 2026
- "From Single to Multi: How LLMs Hallucinate in Multi-Document Summarization," Findings of NAACL 2025, arXiv:2410.13961 — aclanthology.org/2025.findings-naacl.293
- Gao, T. et al., "Enabling Large Language Models to Generate Text with Citations" (ALCE), EMNLP 2023, arXiv:2305.14627
- AttributionBench (aggregation of HAGRID, AttrEval-GenSearch and other attribution datasets) — referenced across 2024–2025 secondary sources
- Onweller, H., Lumer, E., Huber, A., Ramchandani, P., Subbiah, V.K., Feld, C. (PwC), "Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents," arXiv:2605.06635, 2026
- RAGAS — "RAGAs: Automated Evaluation of Retrieval Augmented Generation" (Es et al.); Superlinked blog, "Evaluating Retrieval Augmented Generation using RAGAS"
- ARES evaluation framework — cited via arXiv survey sources on RAG evaluation (2025–2026)
- Min, S. et al., "FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation," arXiv:2305.14251
- "NUMCoT: Numerals and Units of Measurement in Chain-of-Thought Reasoning using Large Language Models," arXiv:2406.02864, 2024
- "When Summaries Distort Decisions: Information Fidelity in LLM-Compressed Financial Analysis," arXiv:2606.29251, 2026 (title/topic confirmed only, not fetched in full)
- Wen, B. et al., "Know Your Limits: A Survey of Abstention in Large Language Models," TACL 2025 — aclanthology.org/2025.tacl-1.26
- Kirichenko, P., Ibrahim, M., Chaudhuri, K., Bell, S.J., "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions," arXiv:2506.09038, 2025-06-10
- Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., Fritz, M., "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," AISec 2023, arXiv:2302.12173
- Wallace, E. et al. (OpenAI), "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions," arXiv:2404.13208, 2024; also OpenAI blog "The Instruction Hierarchy" and "Improving instruction hierarchy in frontier LLMs," openai.com
- "IH-Challenge: A Training Dataset to Improve Instruction Hierarchy," arXiv:2603.10521, 2026

---

## Known limitations of this brief

- Desk research only (WebSearch/WebFetch); no OYL-specific empirical test
  was run against any live assistant — this brief characterizes the
  general literature, not OYL's actual layer in practice (that is the
  inventory's still-open empirical gap, §5).
- Several claims are marked `[folklore/unclear]` because they appeared as
  search-engine-synthesized summaries of a named study rather than
  content this pass independently confirmed by fetching the primary
  source (e.g., the 50–90% citation-support range, the 55%/18% GPT-3.5/
  GPT-4 fabrication figures, the "~5% numeric hallucination" figure, and
  the NUMCoT and financial-fidelity paper details). Where a source was
  fetched directly (AbstentionBench, "Cited but Not Verified," the
  Royal Society paper via PMC), figures are marked `[verified]` and
  quoted from the fetched text.
- No study located in this research pass tests OYL's *exact* caveat
  vocabulary (ridership normalization, dooring undercount, provisional
  recency, sponsorship-vs-vote proxy) or its exact numeric-qualifier
  pattern (relative danger index vs. absolute rate). All findings here
  are evidence about the general mechanism classes involved, applied by
  inference to OYL's case — not direct measurements of OYL's layer.
- The structured-vs-prose question (§4) and the benign-site-instruction-
  compliance question (§6) are both reported here as genuine, confirmed
  open gaps rather than settled findings in either direction; do not read
  the absence of a positive finding as a negative one.
- No academic paper access beyond what WebSearch snippets and WebFetch
  page-fetches surfaced; paywalled or non-indexed papers may exist that
  bear more directly on OYL's questions and were not visible to this
  research pass.
