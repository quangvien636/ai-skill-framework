# Content Skill Readiness

Version: 0.1
Status: Active
Last updated: 2026-07-12

This is the Week 1 deliverable of `docs/guides/MONTHLY_OPERATOR_PLAN.md`:
an audit of what already exists to serve content generation, and the real
gap between that and a benchmarkable content-skill pipeline. It names real
files and paths, not abstractions. It changes nothing — no code, no
schema, no lifecycle status — it only records what was found.

## What Already Exists (Verified 2026-07-12)

- **`skill:content-creation`** (`skills/content-creation/skill.yaml`,
  Accepted, production) generates short video scripts, social posts,
  long-form article outlines, captions/hashtags, and title/thumbnail
  ideas from a supplied brief. It drafts only — no research, media
  creation, publishing, or scheduling.
- **A real, declarative evaluation contract already exists** in
  `skill.yaml`'s `evaluation:` block: four weighted metrics —
  `brief-alignment` (0.30), `format-and-platform-fit` (0.25),
  `factual-integrity` (0.30), `clarity-and-actionability` (0.15) — each
  with 0/50/100 rubric anchors, `weighted-mean` aggregation, and an
  `acceptance.minimum_score: 85` threshold. This is a real, already-
  designed rubric, not something Week 3 has to invent from nothing.
- **Five canonical Knowledge documents** under `knowledge/creative/`
  (`conversion/`, `formats/`, `hooks/`, `platforms/`, `style/`) supply the
  format, tone, platform, hook, and call-to-action guidance the Skill
  drafts against.
- **`workflow:content-brief-to-package`**
  (`workflows/content-brief-to-package/`) is the validated end-to-end
  path from brief to content package.
- **`runtime:offline@1.0.0`** (`runtime/offline/runtime.yaml`) is the
  active, Accepted Runtime Contract `skill:content-creation` resolves in
  production — loopback-only local Ollama, no cloud, no credential
  (Sprint 38).
- **A real, live execution path already exists and has been run for
  real**: `adapters/ollama_execution` runs the full composite
  `workflow:research-content-review` (Research -> Content Creation ->
  Review Quality) through a local Ollama endpoint, dry-run by default,
  live-local by explicit opt-in only. It produces real generated text and
  persists deterministic per-step/whole-run reports under `runs/
  <execution-id>/`.
- **A real, executing topic-relevance gate already exists**:
  `adapters/ollama_execution/topic_relevance.py` performs lexical scoring
  and domain-drift detection on generated output — this is a real,
  running check, not a paper contract. See `adapters/ollama_execution/
  TOPIC_RELEVANCE.md`.
- **`skill:review-quality`** (`skills/review-quality/`, Accepted,
  production) defines a review contract — clarity, structure, logic, tone,
  platform fit, CTA, length, pacing, evidence/citation alignment,
  unsupported claims, safety — recommending `approve`/`revise`/`reject`.

## What Does Not Exist (The Real Gap)

- **`skill:content-creation`'s `evaluation:` block is never executed
  against real output.** Confirmed by search: no code anywhere in the
  repository (only `adapters/ollama_execution/topic_relevance.py` and
  `adapters/ollama_execution/semantic.py` implement anything resembling
  a scorer, and neither implements the four weighted metrics above).
  Today, that rubric is validated for *shape* only — `ASF-SEMANTIC-001`-
  `004` check that weights sum to `1.0` and metric names are unique — not
  *applied* to a real generated package. This is the single largest gap:
  the rubric to benchmark against already exists, but nothing runs it.
- **`skill:review-quality` does not execute.** Its own README states
  plainly: "does not execute an LLM, browse, externally fact-check,
  retrieve policy, or publish." It defines what a reviewer should assess;
  it is not itself an automated reviewer. There is no path from "Content
  Creation produced a package" to "Review Quality automatically scored
  it" today — a human or another process must supply the review content.
- **No video-script-specific quality dimensions exist as distinct,
  measurable metrics.** The Monthly Plan's Week 3 rubric names hook,
  retention, clarity, originality, emotional pacing, short-video fit, CTA
  safety, and a non-copying requirement. Today's four metrics fold most of
  this generically into `clarity-and-actionability` and `format-and-
  platform-fit` — there is no `hook-strength` or `retention`-style metric,
  and `originality`/non-copying has no representation at all (unsurprising,
  since golden-sample-driven learning does not exist yet either — see
  Week 2 of the Monthly Plan).
- **No comparison/benchmark mechanism exists.** The acceptance rule
  (`minimum_score: 85`) is a single-output absolute threshold, not a
  comparison against Claude/Anthropic output or a human-approved
  reference. Nothing in the repository has ever produced or stored a
  Claude/Anthropic output for comparison — confirmed by the repository-
  wide search in `docs/guides/MONTHLY_OPERATOR_PLAN.md` Section 2.
- **No golden sample storage or intake path exists.** No directory,
  schema, or workflow anywhere accepts or stores reference content. This
  is Week 2 of the Monthly Plan, not started.
- **No benchmark harness exists.** Nothing stages, runs, or records a
  multi-output comparison (AI Skill vs. Claude/Anthropic vs. golden
  reference). This is Week 3 of the Monthly Plan, not started.

## Readiness Checklist

| Capability | Status | Evidence |
| --- | --- | --- |
| Content-generating Skill, Accepted, production | Done | `skills/content-creation/skill.yaml` |
| Declarative evaluation rubric with weights + threshold | Done | `skill.yaml` `evaluation:` block |
| Real local live-execution path (no cloud) | Done | `adapters/ollama_execution`, `runtime:offline` |
| Automated topic-relevance/on-topic guardrail | Done | `adapters/ollama_execution/topic_relevance.py` |
| Execution of the declarative evaluation rubric against real output | **Missing** | No scorer implementation found |
| Automated review-quality scoring | **Missing** | `skill:review-quality` is contract-only by design |
| Video-script-specific metrics (hook, retention, pacing, short-video fit) | **Missing** | Not represented as distinct metrics today |
| Originality / non-copying metric | **Missing** | No representation; depends on golden samples existing first |
| Golden sample storage/intake | **Missing** | Monthly Plan Week 2 |
| Claude/Anthropic comparison output storage | **Missing** | Monthly Plan Week 3 (no paid API call to produce it yet) |
| Benchmark harness (offline, multi-output comparison) | **Missing** | Monthly Plan Week 3 |
| video_pipeline integration plan | **Missing** | Monthly Plan Week 4 |

## Recommended Next Steps

This audit does not authorize starting any of the following — each is
still gated by its own week and, where named, its own content trigger in
`docs/guides/MONTHLY_OPERATOR_PLAN.md`:

1. **Week 2 (Golden Sample & Reference Learning Plan):** design the
   intake schema/checklist. Actually ingesting a sample is gated on
   Content Trigger A (a real sample provided by an operator).
2. **Week 3 (Benchmark & Evaluation Contract):** design how the existing
   `evaluation:` block's four metrics extend to cover hook/retention/
   pacing/originality, and how a benchmark would actually invoke and
   score `skill:content-creation` output through the already-real
   `adapters/ollama_execution` live-local path. Running the benchmark
   itself is gated on Content Trigger B (real sample outputs available on
   both sides of the comparison).
3. **Week 4 (Integration Readiness):** only after Weeks 2-3 produce a
   real, passed benchmark result.

## Related Documents

- `docs/guides/MONTHLY_OPERATOR_PLAN.md` (Section 4, Week 1 — this
  document is that week's deliverable)
- `skills/content-creation/skill.yaml` (the evaluation contract this
  audit is built around)
- `skills/review-quality/README.md`
- `adapters/ollama_execution/README.md` and `TOPIC_RELEVANCE.md`
- `docs/architecture/EVALUATION_ARCHITECTURE.md`

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Established the Week 1 content-skill readiness audit: catalogued what exists (a real declarative evaluation rubric, a real live local-Ollama execution path, a real topic-relevance gate) versus what does not (rubric execution, video-specific metrics, originality metric, golden samples, benchmark harness) |
