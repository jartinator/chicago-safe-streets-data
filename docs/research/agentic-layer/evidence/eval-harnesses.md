---
run_date: 2026-07-23
topic: "Off-the-shelf eval harnesses for continuously testing whether an assistant quotes a published dataset correctly, carries its caveats, and refuses where data is absent"
study: agentic-layer (study #1)
---

# Evaluation harnesses for answer fidelity — feasibility brief (mid-2026)

Scope note: this brief answers the kickoff question set only. It does not
propose changes to OYL's layer (see `02-layer-inventory.md`, esp. §3
constraints, treated as ground truth). It is the automated-recurring-version
counterpart to `03-audit-protocol.md`, the study's own hand-run audit design.
Every claim below is labeled `[verified]` (primary-source or corroborated by
independent data), `[vendor-claim]` (stated by the vendor, not independently
measured), or `[folklore/unclear]` (widely repeated, not demonstrated).

---

## 1. Open-source eval frameworks that could run in CI

| Tool | What it actually does | License | Runs in GitHub Actions? | Can assert on a fixed question bank? |
|---|---|---|---|---|
| **promptfoo** | CLI + YAML config: define prompts/test cases, run them against one or more model providers, grade with deterministic assertions (regex, JSON schema, string contains) or model-graded assertions (LLM-as-judge, similarity). Exits non-zero on failure. | Open source (MIT-style; project repo `promptfoo/promptfoo`) `[verified — GitHub repo]` | Yes — official `promptfoo/promptfoo-action` posts a PR summary comment with pass/fail counts; documented CI/CD integration guide. `[verified, promptfoo.dev/docs/integrations/ci-cd/, accessed 2026-07-23]` | Yes — this is its core design: a static YAML "question bank" (prompts + expected-value assertions) run on every trigger, non-zero exit fails the build. `[verified, same source]` |
| **OpenAI Evals** (`openai/evals`) | Framework + registry of benchmark "evals"; supports custom evals via a "Completion Function Protocol" so it can evaluate prompt chains/tool-using agents, not just raw completions. Can also be run inside the OpenAI dashboard. | Open source (repo `openai/evals`, MIT) `[verified — GitHub repo]` | No dedicated first-party GitHub Action found; it's a Python CLI/library, so a bespoke workflow step (`pip install`, run, check exit code) is the integration path, not an off-the-shelf Action `[folklore/unclear — inferred from repo structure, no CI-specific doc found]` | Yes — evals are defined as declarative test-case sets (JSONL) against which model output is graded; this is the intended "fixed question bank" use case. `[verified]` |
| **DeepEval** (Confident AI) | Python library, 50+ "plug-and-play" metrics (answer relevancy, faithfulness, hallucination, contextual precision/recall, etc.) for RAG/agent/chatbot outputs; pytest-style test runner. | Apache 2.0, free; a paid "Confident AI" cloud layer exists for managed evals/observability but the core library is open and free `[verified — deepeval.com, pypi.org/project/deepeval, accessed 2026-07-23]` | Yes in principle — it's a pytest-compatible Python package, so it runs in any GitHub Actions Python job; no dedicated Action needed. `[folklore/unclear on GitHub-Actions-specific docs — inferred from pytest compatibility, not a vendor CI guide found]` | Yes — metrics take a fixed input/expected-output/actual-output triple; this is exactly a question-bank assertion model. `[verified]` |
| **Ragas** | Python library purpose-built for RAG evaluation: faithfulness (does the answer's claims trace to the retrieved context — closest existing metric to OYL's "carries the caveat" question), answer relevancy, context precision/recall. Reference-free scoring plus synthetic test-set generation. | Open source (Apache 2.0, repo under `explodinggradients/ragas`) `[verified — GitHub, standard for the project]` | Yes, by pattern — practitioner write-ups describe a GitHub Actions workflow running the RAG test suite on every PR and failing the build if faithfulness drops below a threshold; this is a documented pattern, not a first-party Ragas GitHub Action product `[folklore/unclear — practitioner pattern, not an Ragas-authored CI doc found]` | Yes for the RAG-answer-vs-context relationship; faithfulness is the metric most analogous to "does the answer misstate what the source said," but Ragas's metrics are about *context* the model was given, not independently about whether a caveat sentence specifically survived — would need a custom assertion layered on top. |
| **TruLens** | Snowflake-backed (post TruEra acquisition, 2024) open-source observability/eval framework; lets teams define custom "feedback functions" (quality dimensions) scored against LangChain/LlamaIndex traces. | MIT, open source, actively maintained by Snowflake engineering `[verified — atlan.com comparison page, mlflow.org TruLens integration doc, accessed 2026-07-23]` | Not confirmed via a dedicated Action; same pattern as DeepEval (Python package, runnable in any CI Python step). `[folklore/unclear]` | Yes, via custom feedback functions defined against fixed inputs. |
| **LangSmith (LangChain evals)** | Hosted tracing + evaluation platform tied to LangChain/LangGraph; dataset-based evals with LLM-graded or custom evaluators, regression comparison across runs. | Not open source — hosted SaaS. Free "Developer" tier: 5,000 traces/month, 1 user, 14-day retention, includes "basic evaluations." Paid Plus tier $39/seat/month, 10,000 base traces, overage $2.50/1,000 traces, full evaluations. `[verified — pricing pages via pecollective.com/margindash.com aggregation, accessed 2026-07-23; recommend re-verifying against smith.langchain.com/pricing directly before committing to it]` | Yes — has a documented CI integration pattern (run evals as part of a pipeline step calling the LangSmith SDK), but it is a hosted account + API key, not a local/offline tool. | Yes, dataset-based evals are exactly a fixed question bank. |
| **Braintrust** | Hosted eval-first LLM observability platform: datasets, "playgrounds," experiments, scoring functions, regression tracking across model/prompt versions. | Not open source — hosted SaaS. Free "Starter" plan: no platform fee, 1GB processed data/month, 10,000 scores/month, 14-day retention. Pro $249/month (~5GB, 50,000 scores, 30-day retention). Enterprise custom. Startups can apply for 6–12 months free Pro. `[verified — cekura.ai, truefoundry.com, costbench.com pricing aggregations, accessed 2026-07-23; verify against braintrust.dev pricing page directly before relying on exact figures]` | Yes, SDK-based CI integration is a documented pattern; again a hosted account. | Yes. |
| **Inspect AI** (UK AI Security Institute) | Full eval-authoring framework: dataset → Task → Solver → Scorer pipeline; multi-turn/agent workflows; one interface across OpenAI/Anthropic/Google/Bedrock/Azure/local models; sandboxing (Docker/K8s) for untrusted-code evals; ships 200+ pre-built evals. Built for AI-safety-grade rigor, not lightweight CI checks. | Open source (repo `UKGovernmentBEIS/inspect_ai`), MIT-style, "wide usage and contributions from the broader evals community," used internally by UK AISI and reportedly by Anthropic/DeepMind/others `[verified — aisi.gov.uk blog, GitHub repo, accessed 2026-07-23]` | Runnable in any CI as a Python CLI; no promptfoo-style dedicated GitHub Action found, and its sandboxing/Docker-K8s features are aimed at a much heavier compute environment than a volunteer static-site repo would want. | Yes, and rigorously — but it is the most heavyweight tool on this list; likely overkill for a 10-question fixed bank. |
| **lm-evaluation-harness** (EleutherAI) | Framework for standardized few-shot benchmark evaluation of language models (the backend of Hugging Face's Open LLM Leaderboard); designed for benchmark reproducibility (MMLU-style tasks), not for testing whether *a specific assistant answer* about *a specific published dataset* carries a caveat. | Open source, repo `EleutherAI/lm-evaluation-harness` `[verified — GitHub repo]` | No CI-specific documentation surfaced in this search; used as a library/CLI. | Not a good fit — it's built for standardized academic benchmarks (multiple-choice, perplexity-style tasks) rather than free-text answer-fidelity grading against a custom question bank. Flagged as **the wrong tool for this use case**, included for completeness because it was on the kickoff's named list. |
| **Anthropic's own eval tooling** | No dedicated hosted "Anthropic Evals" product found; what exists is documentation/education: the `claude-cookbooks` repo's `misc/building_evals.ipynb` notebook (patterns: code-graded / human-graded / model-graded evals, golden answers) and a "Tool evaluation" cookbook for grading tool-calling behavior. This is teaching material and copyable code, not a packaged CI product. | Cookbook repo is open (Anthropic-authored, standard permissive cookbook license) `[verified — github.com/anthropics/claude-cookbooks, accessed 2026-07-23]` | Not a product with its own Action; you'd adapt the notebook pattern into your own CI script. | Yes as a pattern (golden-answer comparison), but requires OYL to write the harness itself using the pattern, not install a product. |

**Net read for OYL's specific question ("quotes it correctly, carries its
caveats, refuses where absent"):** none of these tools ships an
out-of-the-box "caveat carriage" metric. The closest existing off-the-shelf
metric is Ragas's *faithfulness* (does the answer's claims trace to the
provided context) and DeepEval's *hallucination*/*faithfulness* metrics —
both would need a custom assertion or model-graded rubric layered on top to
check the specific thing OYL cares about (a named caveat sentence surviving
into the answer, verbatim or in substance). promptfoo's YAML-based
model-graded assertions are the most direct fit for a small, hand-written
10-question bank because they let you write the exact rubric ("does the
answer mention 'not normalized by ridership'?") without adopting a larger
RAG-evaluation framework `[analysis based on the verified tool descriptions
above, not itself independently benchmarked]`.

---

## 2. Cost and key management

**API cost of a small recurring suite.** Verified mid-2026 list prices:
Claude Sonnet 4.6 at **$3/$15 per million input/output tokens** (standard,
post-introductory-pricing; introductory $2/$10 ran through 2026-08-31), and
GPT-4o at **$2.50/$10 per million input/output tokens**
`[verified — platform.claude.com/docs pricing page and aggregation sites
pricepertoken.com/finout.io, cross-checked with metacto.com, all accessed
2026-07-23; the *official* platform.claude.com page is the primary source,
the others corroborate]`.

Arithmetic (not itself sourced — a calculation from the verified per-token
prices above): a 10-question × 2-model weekly suite, each call roughly
1,000 input + 500 output tokens (a typical grounded-answer length), costs
on the order of **$0.01–0.02 per call**, so **roughly $0.20–0.40/week**, or
**about $10–20/year** at these list prices. Adding a third LLM-as-judge
grading call per question roughly doubles that. This is negligible against
any volunteer-project budget threshold — the practical barrier is not
per-call cost, it is the human setup, key custody, and interpretation work
below, not the API bill itself.

**Key management for a volunteer OSS repo with public CI.**
- GitHub Actions secrets are the standard mechanism, but `pull_request`
  (as opposed to `pull_request_target`) workflows from **forks** do not
  receive repository secrets by default, and first-time contributors'
  workflow runs require maintainer approval before executing at all
  `[verified — GitHub Security Lab, "Keeping your GitHub Actions and
  workflows secure Part 1: Preventing pwn requests," securitylab.github.com,
  accessed 2026-07-23]`.
- The dangerous pattern is `pull_request_target` combined with checking out
  the fork's untrusted code: that trigger runs in the *base* repo's context
  with full secrets and a write-scoped `GITHUB_TOKEN` available, and — unlike
  plain `pull_request` — executes automatically without approval, which is
  exactly the pattern behind real supply-chain compromises documented at
  Microsoft, Google, and Nvidia `[verified — Orca Security "pull_request_
  nightmare" series and Wiz "Hardening GitHub Actions" blog, accessed
  2026-07-23]`.
- Practical implication for OYL specifically: an eval workflow that needs an
  Anthropic/OpenAI API key should run only on a trigger that does not expose
  secrets to arbitrary fork PRs (e.g., `push`/`schedule` on the trusted
  branch, or a `pull_request` trigger with no secrets passed, reserving the
  keyed run for a maintainer-triggered or scheduled job) — this is a
  standard, well-documented GitHub Actions security pattern, not something
  specific to eval tooling `[verified, same sources]`.

---

## 3. Determinism / flakiness of LLM-answer assertions

**Non-determinism persists even at temperature 0.** Independent technical
write-ups and at least one arXiv paper document that GPU floating-point
non-associativity and batch-processing effects mean temperature-0 output is
"necessary but not sufficient" for determinism — flip rates (the fraction of
repeated runs that produce a different answer/verdict) are reduced but not
eliminated by pinning temperature to zero, and this varies by model
`[verified via arxiv.org/pdf/2407.10457 "The Good, The Bad, and The Greedy:
Evaluation of LLMs Should Not Ignore Non-Determinism," and corroborating
practitioner write-up vincentschmalbach.com, accessed 2026-07-23]`.

**LLM-as-judge reliability, with numbers.** A 2026 arXiv paper ("The Coin
Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation,"
arxiv.org/abs/2606.13685, accessed 2026-07-23) found, across repeated
judge runs on identical inputs:
- Pairwise preference judgments **flip on average 13.6% of the time**
  across repeated runs; **28% of questions exceed a 20% flip rate**, and one
  question hit a 56% flip rate `[verified, primary source]`.
- One judge model (GPT-4o-mini) showed measurable **positional bias**
  (preferring the first-listed option 72% of the time, p = 0.024)
  `[verified, same source]`.
- Rewording the judge prompt with a semantically-equivalent template
  **changed the majority verdict in 25% of tested cases** `[verified, same
  source]`.
- Cross-judge agreement between two different judge models was **76%
  (Cohen's κ = 0.51)** — a moderate-agreement level, not near-perfect
  `[verified, same source]`.
- To reach 95% confidence in a verdict, the paper found **an average of 11
  repeated trials needed, rising to 15 for high-variance questions**
  `[verified, same source]`. The paper's own recommendation is multi-trial
  aggregation, position randomization, and explicit uncertainty reporting —
  not single-shot pass/fail judging.

**Contrasting, more favorable numbers exist too** (task-dependent): other
2026 papers report much higher judge-human agreement in narrower,
well-specified grading tasks — e.g., 92.31% raw agreement / Cohen's κ 0.85
on one benchmark's classification task, and a judge-human Pearson
correlation (0.799–0.820) that matched or exceeded measured human-human
agreement (0.742–0.780) on another `[verified as reported in the respective
arXiv papers surfaced by this search — D3-Gym and "Chain of Risk" papers,
accessed 2026-07-23; note these measure different task types than
open-ended caveat-carriage grading, so the more favorable numbers should not
be assumed to transfer directly to OYL's use case]`.

**What practitioners actually do, per the sources above and the tool
descriptions in §1:** rubric-constrained LLM-as-judge (a specific yes/no
question like "does the answer state the caveat X?" rather than an open
preference judgment) is described as more reliable than open-ended
preference judging; deterministic string/number assertions are used
wherever the expected answer is short and fixed (a number, a status string);
multiple samples with a majority vote or an explicit confidence threshold
are recommended over single-shot grading; and thresholds ("faithfulness
must stay above 0.8") rather than hard pass/fail gates are the documented
pattern in the Ragas/DeepEval CI write-ups in §1 `[folklore/unclear for the
"what practitioners do" synthesis — consistent across multiple sources, not
a single controlled study of practitioner behavior itself]`.

---

## 4. Can a harness test the real consumer surfaces, or only APIs?

**These are two different measurements, and the tools in §1 only do the
first one.** All of §1's frameworks operate against a **model API** (or a
locally-hosted model) that the harness itself calls directly with a
programmatic prompt. None of them drive **the actual consumer-facing
product surface** (chatgpt.com, claude.ai, perplexity.ai's web UI, or Google
Search's AI Overviews as an end user sees them) — that would require
browser automation against a logged-in or logged-out consumer web app, which
is exactly what this study's own `03-audit-protocol.md` does by hand (S1
Claude+web, S2 Perplexity, S3 ChatGPT) rather than what any of §1's CI tools
do automatically.

A **separate product category** exists for the real-surface question — "AI
brand visibility" / citation-tracking monitors — but these measure a
different thing again (whether/how often a brand or domain is *mentioned or
cited* across many real consumer queries at scale), not whether a specific
answer's caveat is intact:

| Tool | What it measures | Pricing (verified where noted) | Free tier? |
|---|---|---|---|
| **Otterly.ai** | Tracks brand/domain mentions across Google AI Overviews, ChatGPT, Perplexity, Microsoft Copilot on a set of tracked prompts, run daily. | Lite $25–29/month (15 prompts, daily); Standard $160/month (100 prompts, +$99/100-prompt add-on) `[vendor-claim, pricing aggregated from zapier.com/stackinsight.net/surmado.com, accessed 2026-07-23 — verify against otterly.ai/pricing directly]` | Free trial only, no permanent free tier found. |
| **Peec AI** | Competitive AI-visibility tracking (brand vs. named competitors) across AI answer surfaces. | From ~€89–99/month (3 competitors, 100 queries) up to $499/month (custom reporting, API access) `[vendor-claim, same aggregation sources]` | No free tier found; demo/trial only. |
| **Profound** | Enterprise-grade AI visibility/citation tracking; prompt-volume-tiered plans. | Starter ~$82.50/month (50 prompts, billed annually) up to Growth ~$332.50/month (100 prompts); no free trial, demo-only `[vendor-claim, same aggregation sources]` | No free trial (demo only, per source). |
| **Ahrefs Brand Radar** | AI-citation tracking bundled into Ahrefs' existing SEO suite; covers 6 named AI platforms, "260M+ prompts" claimed index. | Ahrefs Lite $129/month; Brand Radar AI indexes $199/month per platform or $699/month for all six bundled `[vendor-claim, ewrdigital.com/tryanalyze.ai aggregation, accessed 2026-07-23]` | A **free tier for AI-crawler-traffic monitoring** exists, plus a "free beta" for some Brand Radar AI indexes offering directional data at zero cost to existing paying Ahrefs customers `[vendor-claim]` — this is narrower than full citation tracking. |
| **Semrush AI Toolkit** | AI-visibility add-on to the existing Semrush suite; brand visibility score, prompt/query tracking, citation analysis, competitor benchmarking. | $99/month per domain, standalone add-on price `[vendor-claim, menra.ai/whitebunnie.com aggregation, accessed 2026-07-23]` | Not found as free; requires existing or new Semrush subscription. |

**Explicit distinction (load-bearing for OYL):** the §1 API-eval frameworks
answer "did the model, called programmatically with our exact prompt, give
a faithful answer?" The §4 brand-visibility tools answer "across many real
searches on real consumer surfaces, how often is our brand/domain named or
cited at all?" — a discovery/frequency metric, not a fidelity/caveat-
carriage metric. None of the brand-visibility tools surfaced in this search
claim to grade caveat carriage, numeric correctness against a ground-truth
value, or refusal behavior — they are citation-counting and competitive-
share tools, not answer-fidelity graders. Nothing in this search found a
tool that does both (real-surface reach *and* fidelity grading against a
specific publisher's pinned ground truth) in one product.

---

## 5. Precedents: does any dataset/API publisher run a public, recurring eval of how assistants answer from their data?

**None found.** This search (general web search across LangChain resource
pages, evaluation-dataset roundups, and "how to build an AI evals dataset"
guides) surfaced extensive tooling for **generic** LLM/RAG evaluation
(GAIA, TruthfulQA, and similar benchmark datasets; `continuous-eval` and
similar CI-oriented eval libraries) but **no example of a specific
dataset, API, or open-data publisher running a standing, public, recurring
eval measuring how third-party AI assistants answer questions from that
publisher's own data** — the pattern OYL's study is investigating whether
to build. This is reported here as a plain negative finding, not an
artifact of a narrow search: the search terms directly named the pattern
("dataset publisher," "runs recurring public eval," "how AI assistants
answer from our data") and returned only generic evaluation tooling and
academic benchmark literature, not a single case study of a publisher
doing this. `[folklore/unclear whether one exists but was simply not
surfaced by this search pass — treat as an open gap rather than a proven
absence, but no positive example was found]`.

---

## 6. Failure mode of the whole idea

What a CI-run eval suite of this kind would **not** tell OYL, even if built
and passing every week:

- **It tests one model you chose, not the population of consumer queries.**
  A promptfoo/DeepEval/Ragas suite calls a specific API model (e.g., Claude
  Sonnet via API) with a specific prompt template. It says nothing about
  ChatGPT's consumer web product, Perplexity's web surface, or Google AI
  Overviews — each of which, per this study's own `assistant-discovery.md`
  brief, uses different retrieval/grounding pipelines (Brave-backed for
  Claude.ai, Google-Search-index-grounded for Gemini/AI Overviews,
  contested Bing-vs-own-index for ChatGPT Search) and may not even fetch
  the same content the API model was given directly in a test harness.
- **It tests a prompt you wrote, not the phrasing a real user types.** The
  audit protocol's own U/P (Unaided/Pointed) distinction exists precisely
  because a "Pointed" prompt (one that hands the model the llms.txt URL)
  measures something structurally different from an "Unaided" real-world
  question — and a CI harness, to be deterministic and cheap, would almost
  certainly run Pointed-style prompts, the easier and less informative half
  of the study's own four measured behaviors (discovery, correctness,
  caveat carriage, refusal).
- **API-model behavior and consumer-product behavior are measurably
  different systems**, not the same system accessed two ways: the
  consumer product often adds its own system prompt, safety layer,
  retrieval/reranking step, and citation-formatting logic on top of the
  underlying model API call — none of which a direct-API eval harness
  exercises at all.
- **Passing/green CI is not proof of real-world fidelity** — per §3, even a
  well-designed rubric-constrained LLM-judge check carries measured flip
  rates (13.6% average, up to 56% on individual questions in the cited
  study) and moderate-only cross-judge agreement (κ = 0.51); a suite that is
  "green" this week is not a guarantee the underlying behavior didn't
  actually flip, only that the sampled trials happened to pass.
- **It cannot observe who is actually asking**, or how often OYL's data is
  even being surfaced in the wild, absent the citation-tracking tools in
  §4 — and none of those tools, per §4, grade fidelity either. The two
  measurement types (API-eval fidelity-testing and real-surface
  visibility-tracking) remain structurally separate; no tool found here
  does both.
- **A recurring green harness could create false confidence** that the
  layer's "refuse-don't-hallucinate" request (inventory §2.4) is actually
  honored by production assistants, when it would only have shown that one
  chosen model, called one chosen way, answered one fixed question bank
  correctly at the moment each run executed.

---

## Implications for OYL (facts only, no proposals)

- **Static-files-only constraint (inventory §3):** every tool surveyed in
  §1 is a CI-side tool that calls out to a model API from GitHub Actions —
  none require OYL to run a server, accept accounts, or add rate limiting;
  this class of tooling is structurally compatible with OYL's "static
  files only, GitHub Pages" constraint, because the eval workflow would run
  in CI, not on the served site.
- **Volunteer-run / must-survive-unattended-weeks constraint:** per §2, the
  API cost of a small weekly suite (~$10–20/year at verified list prices) is
  not the binding constraint; per §2's GitHub Actions security findings,
  correct trigger selection (avoiding `pull_request_target` with secrets
  exposed to forks) is a documented, standard requirement for any workflow
  that would need to hold an API key in a public OSS repo — this is the
  same category of unattended-operation risk the repo's existing session-
  guard and provenance-check tooling already manages, not a new risk class.
- **Independence framing / no preview-embargo channel (inventory §3):** none
  of the frameworks in §1, nor the brand-visibility tools in §4, require or
  imply any embargoed/preview access to a consumer AI product — all operate
  on public APIs or public consumer surfaces, consistent with this
  constraint.
- **Precision-over-recall culture (inventory §3) and the unmet P1 success
  signal (inventory §4, "five questions, zero caveat-stripped answers,"
  never run):** §1 found no off-the-shelf metric that directly grades
  "caveat carriage" as OYL defines it; the closest existing metrics
  (Ragas/DeepEval faithfulness/hallucination scores) test a different
  relationship (answer-vs-retrieved-context) than OYL's actual concern
  (a specific named caveat sentence surviving into a consumer-facing
  answer). Building that specific check, per §1, would mean writing a
  custom rubric inside a tool like promptfoo, not adopting a pre-built
  metric.
- **The empirical gaps this study exists to close (inventory §5):** per §4,
  no tool surveyed here — CI eval framework or brand-visibility monitor —
  answers inventory gap #2 ("does an assistant that reads an endpoint carry
  the caveat") on the real consumer surfaces (ChatGPT web, Perplexity,
  Claude.ai, Google AI Overviews) that gap #2 is actually about; that
  remains a hand-run, browser-driven audit task (`03-audit-protocol.md`'s
  own design), not something any surveyed off-the-shelf tool automates end
  to end.
- **No precedent found (§5):** inventory gap #2/#3 (caveat carriage,
  refusal integrity) is, per this brief's search, not something any other
  dataset/API publisher is known to test on a standing recurring public
  basis — OYL's `03-audit-protocol.md` would be establishing a novel
  pattern for a small civic open-data project, not adopting a proven one.

---

## Sources

- Promptfoo, "CI/CD Integration for LLM Eval and Security" — promptfoo.dev/docs/integrations/ci-cd/ (accessed 2026-07-23)
- GitHub, `promptfoo/promptfoo-action` — github.com/promptfoo/promptfoo-action (accessed 2026-07-23)
- GitHub, `openai/evals` — github.com/openai/evals (accessed 2026-07-23)
- DeepEval — deepeval.com and deepeval.com/docs/introduction (accessed 2026-07-23)
- DeepEval on PyPI — pypi.org/project/deepeval (accessed 2026-07-23)
- Confident AI, "RAG Evaluation Metrics" — confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more (accessed 2026-07-23)
- Atlan, "RAGAS, TruLens, DeepEval: LLM Evaluation Frameworks (2026)" — atlan.com/know/llm-evaluation-frameworks-compared (accessed 2026-07-23)
- MLflow, "TruLens" integration doc — mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/trulens (accessed 2026-07-23)
- GitHub, `UKGovernmentBEIS/inspect_ai` and AISI blog "Announcing Inspect Evals" — aisi.gov.uk/blog/inspect-evals (accessed 2026-07-23)
- GitHub, `EleutherAI/lm-evaluation-harness` (accessed 2026-07-23)
- Anthropic, `claude-cookbooks` repo, `misc/building_evals.ipynb` and Tool Evaluation cookbook — github.com/anthropics/claude-cookbooks (accessed 2026-07-23)
- Anthropic, Claude API pricing — platform.claude.com/docs/en/about-claude/pricing (accessed 2026-07-23)
- Pricing aggregation cross-checks: pricepertoken.com, finout.io, metacto.com (Claude); general GPT-4o pricing citation via same search pass (accessed 2026-07-23) — treat as corroboration, not primary source
- GitHub Security Lab, "Keeping your GitHub Actions and workflows secure Part 1: Preventing pwn requests" — securitylab.github.com/resources/github-actions-preventing-pwn-requests (accessed 2026-07-23)
- Orca Security, "pull_request_nightmare Part 1 & 2" — orca.security/resources/blog (accessed 2026-07-23)
- Wiz, "Hardening GitHub Actions: Lessons from Recent Attacks" — wiz.io/blog/github-actions-security-guide (accessed 2026-07-23)
- arXiv, "The Good, The Bad, and The Greedy: Evaluation of LLMs Should Not Ignore Non-Determinism" — arxiv.org/pdf/2407.10457 (accessed 2026-07-23)
- Vincent Schmalbach, "Does Temperature 0 Guarantee Deterministic LLM Outputs?" — vincentschmalbach.com (accessed 2026-07-23)
- arXiv, "The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation" — arxiv.org/abs/2606.13685 (accessed 2026-07-23)
- arXiv, D3-Gym paper (judge-human agreement figures) — arxiv.org/pdf/2604.27977 (accessed 2026-07-23)
- arXiv, "Chain of Risk: Safety Failures in Large Reasoning Models..." (judge-human correlation figures) — arxiv.org/pdf/2605.05678 (accessed 2026-07-23)
- Zapier, "The 8 best AI visibility tools in 2026" — zapier.com/blog/best-ai-visibility-tool (accessed 2026-07-23)
- Surmado, "Best AI Visibility Tools 2026: Profound vs Peec vs Otterly vs the Rest" — surmado.com/blog/best-ai-visibility-tools-2026 (accessed 2026-07-23)
- StackInsight, "Profound vs Otterly Ai" — stackinsight.net/profound-vs-otterly-ai-comparison (accessed 2026-07-23)
- EWR Digital, "Ahrefs Brand Radar Review & Alternatives" — ewrdigital.com/blog/ahrefs-brand-radar-review-alternatives-pricing-comparison (accessed 2026-07-23)
- tryanalyze.ai, "Ahrefs vs Semrush for AI Visibility: Pricing Compared" — tryanalyze.ai/blog/ahrefs-vs-semrush (accessed 2026-07-23)
- Menra, "Semrush AI Toolkit vs Ahrefs Brand Radar" — menra.ai/vs/semrush-ai-toolkit-vs-ahrefs-brand-radar (accessed 2026-07-23)
- LangChain, "LLM Evals: The Feedback Loop Behind Reliable AI Agents" — langchain.com/resources/llm-evals (accessed 2026-07-23)
- pecollective.com, "LangSmith Pricing 2026" and "LangChain Pricing 2026" (accessed 2026-07-23)
- Cekura, "Braintrust Pricing in 2026" — cekura.ai/blogs/braintrust-pricing (accessed 2026-07-23)
- CostBench, "Braintrust Pricing 2026: Free-$249/User Plans Compared" — costbench.com/software/ai-observability/braintrust (accessed 2026-07-23)

## Known limitations of this brief

- Desk research only (WebSearch/WebFetch); no tool in §1 was actually
  installed or run against OYL's own data during this brief — all
  capability claims are read from vendor docs and third-party write-ups,
  not hands-on verification.
- Several pricing figures (LangSmith, Braintrust, Otterly, Peec, Profound,
  Ahrefs Brand Radar, Semrush AI Toolkit) come from pricing-aggregation blog
  posts rather than the vendor's own pricing page fetched directly in this
  session; they are marked `[vendor-claim]` accordingly and should be
  re-verified against the vendor's own page before any purchase decision.
- The GitHub-Actions-specific integration claims for DeepEval, Ragas,
  TruLens, and Inspect AI are inferred from their being ordinary Python
  packages/pytest-compatible tools rather than from a vendor-authored
  "GitHub Actions guide" found for each — only promptfoo has a confirmed,
  named, first-party GitHub Action product.
- The judge-agreement numbers in §3 come from a small number of individual
  papers (one primary "Coin Flip Judge" study for the pessimistic numbers,
  two other individual papers for the more favorable numbers) rather than a
  meta-analysis; the tasks measured in each paper differ from OYL's actual
  use case (grading whether a specific caveat sentence survived), so none
  of these numbers should be read as a direct prediction of how reliable a
  caveat-carriage judge would be for OYL specifically.
- §5's "no precedent found" is a negative result from a general web search,
  not an exhaustive survey of every open-data or API publisher; it should
  be read as "not surfaced by this search," not as a certainty that no such
  precedent exists anywhere.
- No literature was found (and none was searched for beyond what's in §5)
  specifically on small civic/volunteer open-data projects running any kind
  of eval harness at all — this brief's cost and key-management analysis in
  §2 is a general GitHub Actions security synthesis applied to OYL's
  described situation, not a case study of a comparable project doing this.
