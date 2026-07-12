# Monthly Operator Plan

Version: 0.2
Status: Active
Last updated: 2026-07-12

This is the higher-level, month-scoped roadmap that sits above
`docs/guides/WEEKLY_OPERATOR_PLAN.md`. The weekly plan governs the two
standing infrastructure triggers (MCP SDK v2, SemVer pre-release) at
day-level granularity; this plan governs a four-week content-skill
readiness push at week-level granularity. Read the weekly plan first for
the current trigger state before starting any week below — this plan does
not repeat or override its gating logic, it only adds new, separately
gated content-skill work alongside it.

## 1. Purpose

This month's goal is to move the AI Skill Framework from "framework/
governance/adapters pass" — true today, verified repeatedly — to
**content-skill readiness**: a state where `skill:content-creation`'s
output quality can be *measured*, not just *validated for shape*.

Explicit non-goals, stated up front because they are the easiest things to
drift into by accident:

- **Not** replacing the Anthropic API in any production path this month.
  Nothing in this repository or in `video_pipeline` is switched to AI
  Skill Framework output as a live replacement during this plan.
- **Not** connecting `video_pipeline` to this repository's production
  output until a benchmark shows AI Skill output wins, or at minimum
  clears an explicit quality threshold — and even then, only into a
  shadow/offline/branch-only experiment, never straight into production
  (see Week 4).
- **Not** writing speculative code against a trigger that has not fired
  (MCP v2, SemVer pre-release — both still not actionable as of this
  writing) or against content requirements that do not yet have real data
  behind them.
- **Is** building the evaluation foundation, golden-sample intake process,
  content-skill contract, and integration plan this readiness push
  actually depends on — the four deliverables below exist because none of
  them exist in the repository today (verified by search before writing
  this plan).

## 2. Current Baseline

Verified 2026-07-12, the day this plan was written, not assumed from
memory:

- **Core framework validation:** all green — `validate_contracts.py`
  23/23, `build_ir.py` 47/47, `build_graph.py` 14/14, `build_semantics.py`
  4/4, `validate_repository.py` 0 errors/0 warnings, `unittest discover`
  168/168.
- **Adapter suites (isolated processes):** all green — `mcp_tools` 7/7,
  `llamaindex_retrieval` 15/15, `model_invokers` 20/20 (+1 opt-in skip),
  `publisher_adapters` 20/20, `langgraph_runtime` 23/23 (+1 opt-in skip),
  `ollama_execution` 107/107 (+1 opt-in skip).
- **Governance:** all 19 real ADRs `Accepted`; `docs/guides/
  WEEKLY_OPERATOR_PLAN.md` is the standing two-week infrastructure runbook.
- **MCP SDK v2 trigger:** not actionable — latest published is `1.28.1`,
  no `2.x` stable exists.
- **SemVer pre-release trigger:** not actionable — no artifact anywhere in
  the repository carries a `-alpha`/`-beta`/`-rc` version.
- **Anthropic API:** never integrated anywhere in this repository. ADR-0013
  names Anthropic only as one example of an "official provider SDK" the
  `ModelInvoker` seam *could* eventually support; ADR-0018 (Accepted)
  implemented only the local Ollama path, and cloud descriptors are
  designed to fail closed before any client is constructed. There is no
  code to "replace" — there is only a documented, deliberate absence.
- **Benchmark infrastructure:** does not exist. No file, script, or test
  anywhere in the repository compares AI Skill output quality against
  Claude/Anthropic output or against any reference standard (confirmed by
  repository-wide search before writing this plan).
- **Golden samples / content references:** do not exist. No intake
  workflow, schema, or stored reference content exists anywhere in the
  repository.
- **Existing content-generation foundation (the thing this plan builds on,
  not from zero):** `skill:content-creation` is already a real, Accepted,
  production Skill (`skills/content-creation/`) with five canonical
  Knowledge documents (format, tone, platform, hook, call-to-action) and
  an active production binding to `runtime:offline` (local Ollama,
  loopback-only, per Sprint 38). It has never been benchmarked against any
  external standard and has no golden-sample-driven evaluation — that gap
  is exactly what this plan closes.

## 3. Month Goal

By the end of four weeks, the repository should have:

1. A documented content-skill readiness roadmap identifying the real gap
   between what `skill:content-creation` does today and what "ready to
   compare against Claude/Anthropic output" requires.
2. An evaluation contract for script/video content — a rubric with
   pass/fail thresholds, not just a schema shape check.
3. A golden-sample intake workflow — how an operator hands the repository
   real reference content, what can be learned from it, and what must
   never be copied from it.
4. A benchmark plan that can actually compare AI Skill output against
   Claude/Anthropic output or human-approved references **offline**, with
   no paid API call required to define or stage it.
5. An integration checklist against `video_pipeline` that is a plan, not a
   connection — shadow mode, offline compare mode, or branch-only
   experiment only, with an explicit rollback policy.
6. A stop/go decision rule stating plainly: when R&D continues, when a
   test-branch trial against Anthropic is permitted, and when replacing
   Anthropic is never permitted regardless of benchmark results (i.e.
   without explicit human approval, since that is a production-affecting
   decision under `.ai/governance/DECISION_RIGHTS.md`, not something any
   session can authorize itself).

None of the four weekly deliverables below require calling a paid API,
scraping content without permission, faking data to unlock work, or
touching `video_pipeline`'s production configuration.

## 4. Four-week Plan

### Week 1 — Baseline & Content Skill Readiness

**Allowed work:**

- Audit the current state of the framework, Skills, adapters, and test
  suites as they relate to content generation specifically.
- Identify what already exists to serve content generation (start from
  `skill:content-creation` and its five Knowledge documents).
- Create or update a content-skill readiness checklist.
- Identify the real gap between the current framework and the goal of
  generating video scripts that can be benchmarked.

**Forbidden:**

- No production content generator code.
- No connection to `video_pipeline`.

**Deliverables:**

- `docs/guides/CONTENT_SKILL_READINESS.md` (a dedicated file, not a
  section here, so it can grow its own checklist without bloating this
  roadmap).
- A gap list naming real files/paths, not abstractions.
- `PROJECT_TRACKER.md` updated only if a real, new Next Action was found.

**Stop condition:** No content-skill-related artifact/code is found to
audit; an operator scope decision is needed; the repository is found not
clean.

**Validation:** `python scripts/asf.py doctor`; the validation matrix in
`docs/guides/WEEKLY_OPERATOR_PLAN.md` Appendix B; `git diff --check`.

**Status (2026-07-12): Complete.** See `docs/guides/
CONTENT_SKILL_READINESS.md`. Key finding: `skill:content-creation` already
has a real declarative evaluation rubric (four weighted metrics,
`minimum_score: 85`), a real live local-Ollama execution path
(`adapters/ollama_execution`), and a real running topic-relevance gate —
but the rubric itself is never executed against real output, which is the
largest single gap toward a benchmarkable pipeline. No new Next Action was
needed beyond the Week 2-4 items already recorded; no code changed.

### Week 2 — Golden Sample & Reference Learning Plan

**Allowed work:**

- Design a workflow for taking in golden samples/reference content for
  content-skill learning.
- Define the minimum format an operator uses to hand over a link, video,
  or sample content — a schema/checklist, not a working ingester, since no
  real sample data exists yet.
- Define explicitly what can be learned from a reference (structure
  patterns, pacing, hook technique) versus what must never be copied
  (verbatim wording, close paraphrase of protected structure).
- Define a review gate with exactly three outcomes: `APPROVED`,
  `REJECTED`, `INSUFFICIENT_EVIDENCE`.

**Forbidden:**

- No scraping or downloading of content without explicit permission and a
  real input already provided by the operator.
- No fabricated sample data to make this deliverable look further along
  than it is.

**Deliverables:**

- `docs/guides/GOLDEN_SAMPLE_INTAKE_PLAN.md`.
- A schema/checklist, placed in an existing repository location if one
  fits (see `schemas/README.md` for precedent) rather than inventing a new
  top-level convention.
- A short prompt template an operator can paste a reference into.
- `PROJECT_TRACKER.md` updated only if a real, actionable follow-up
  exists.

**Stop condition:** No real sample exists to analyze; the work would
require scraping or another copyright-risk action; human approval is
needed.

**Validation:** `python scripts/asf.py doctor`; existing tests if a
schema/validator actually changed; `git diff --check`.

### Week 3 — Benchmark & Evaluation Contract

**Allowed work:**

- Design an **offline** benchmark comparing AI Skill output, Claude/
  Anthropic output, and human-approved golden references.
- Define a script-evaluation rubric: hook, retention, clarity,
  originality, emotional pacing, short-video fit, CTA safety, and a
  non-copying requirement.
- Define pass/fail thresholds.
- If an Anthropic comparison is part of the plan, write the plan/contract
  only — do not call the API.

**Forbidden:**

- No claim that AI Skill output is better than anything until a real test
  has actually run.
- No paid API call.
- No benchmark run that costs money.

**Deliverables:**

- `docs/guides/CONTENT_BENCHMARK_PLAN.md`.
- A clear rubric.
- Explicit pass/fail thresholds.
- A decision rule: when AI Skill output is eligible to be tried in a
  `video_pipeline` test branch (never production, per Section 1).

**Stop condition:** No sample output exists to benchmark; the rubric lacks
real data to anchor its thresholds; human review is needed before
finalizing pass/fail numbers that could later justify a production
decision.

**Validation:** `python scripts/asf.py doctor`; tests if an evaluator/
schema was actually added; `git diff --check`.

### Week 4 — Integration Readiness & Go/No-Go Decision

**Allowed work:**

- Design an integration plan between `ai-skill-framework` and
  `video_pipeline` — a checklist/contract only, never a live connection.
- Define experiment modes: shadow mode, offline compare mode,
  branch-only experiment.
- Define a rollback policy.
- State plainly: Anthropic is not replaced until the benchmark (Week 3)
  is actually passed **and** a human has approved the decision per
  `.ai/governance/DECISION_RIGHTS.md` — a benchmark pass alone is
  necessary, not sufficient.

**Forbidden:**

- No production connection.
- No dependency or config change in `video_pipeline` (out of scope for
  this repository's sessions regardless — see this session's own standing
  instruction not to switch repositories).

**Deliverables:**

- `docs/guides/VIDEO_PIPELINE_INTEGRATION_READINESS.md`.
- A Go/No-Go checklist.
- A rollback policy.
- A next-month roadmap if readiness is not yet met (the expected outcome
  unless Weeks 1-3 produce unusually fast, unusually conclusive results).

**Stop condition:** Benchmark results are missing; golden samples are
missing; a decision approval is missing; any real risk to `video_pipeline`
production is identified.

**Validation:** `python scripts/asf.py doctor`; the full validation matrix
(`docs/guides/WEEKLY_OPERATOR_PLAN.md` Appendix B); `git diff --check`.

## 5. Monthly Governance Rules

- Do not spend quota on a no-op loop.
- Do not do speculative work.
- Do not fabricate data to unlock a deliverable that has a real
  prerequisite it does not yet meet.
- Do not migrate MCP unless the MCP SDK v2 trigger has actually fired.
- Do not implement the SemVer pre-release comparator unless a real
  pre-release version has actually been adopted in the repository.
- Do not replace the Anthropic API in any production path.
- Only create docs/checklists/contracts while no real data exists yet —
  that is the correct output when a prerequisite is missing, not a
  consolation prize.
- Only write code when a real failing test, a real required schema, or a
  real requirement already exists in the repository — never "just in
  case."
- If a decision requires human judgment under
  `.ai/governance/DECISION_RIGHTS.md`, stop and report; do not proceed on
  the assumption that a later session will catch it.

## 6. Trigger Rules

The two standing infrastructure triggers from `docs/guides/
WEEKLY_OPERATOR_PLAN.md` remain unchanged and are not duplicated here —
that document is their single source of truth:

- MCP SDK v2 stable release.
- A real, adopted SemVer pre-release version.

Three new content-skill triggers gate the work above:

**Content Trigger A — Golden sample provided.** Fires when an operator
supplies a video, link, transcript, or sample content with enough evidence
to review. Allowed once fired: intake, classify, review, extract abstract
patterns. Forbidden regardless: copying wording, copying structure too
closely, unauthorized scraping.

**Content Trigger B — Benchmark sample available.** Fires when at least
three AI Skill outputs and three Claude/Anthropic or human-approved
reference outputs exist. Allowed once fired: run the offline rubric/
evaluation from Week 3. Forbidden regardless: claiming superiority without
evidence.

**Content Trigger C — Integration candidate ready.** Fires when the
benchmark from Week 3 actually clears its stated threshold. Allowed once
fired: prepare a shadow-mode integration plan (Week 4). Forbidden
regardless: any production replacement without explicit human approval.

None of these three triggers has fired as of this writing — Weeks 1-4
above are therefore entirely planning/checklist/contract work, never
implementation against real content, until an operator provides the
missing input each trigger names.

## 7. Validation Matrix

Match the validation to what actually changed. `docs/guides/
WEEKLY_OPERATOR_PLAN.md`'s "How to Use This Document" note applies here
too: a bare root-level `python -m pytest` fails at collection because
adapter test packages intentionally share module names across isolated
processes (verified 2026-07-12) — never use it as a validation command.

**Docs-only:**

```bash
python scripts/asf.py doctor
git diff --check
```

**Schema/contract changes:**

```bash
python scripts/asf.py doctor
python scripts/validate_contracts.py
git diff --check
```

**Core/framework changes:**

```bash
python scripts/asf.py doctor
python -m unittest discover -s tests/unit
git diff --check
```

If an adapter package is touched, additionally run that package's isolated
suite from inside its own directory (`cd adapters/<name> && python -m
pytest -q`) — see `docs/guides/WEEKLY_OPERATOR_PLAN.md` Appendix B for the
full per-package matrix and current pass counts.

## 8. Stop Conditions

Stop if:

- There is no actionable work.
- A relevant trigger (infrastructure or content) has not fired.
- Human approval is required.
- Validation is red.
- The working tree is abnormal.
- Local and origin have diverged unexpectedly.
- The only remaining action would repeat a check that was just run with a
  result that cannot plausibly have changed.
- Any action risks affecting `video_pipeline` production.

## 9. Monthly Closeout Report Template

```text
## Monthly Operator Report — <month/year>

Repo path:
Branch:
HEAD before -> after:
Commits:
Files changed:

What became more ready:
What is still blocked:

Trigger status:
  MCP SDK v2:
  SemVer pre-release:
  Content Trigger A (golden sample):
  Content Trigger B (benchmark sample):
  Content Trigger C (integration candidate):

Validation result:

Whether Anthropic replacement is allowed in production: yes/no
Why/why not:

Next month plan:
```

## Related Documents

- `docs/guides/WEEKLY_OPERATOR_PLAN.md` (the two-week infrastructure
  runbook this plan sits above; read it first for MCP/SemVer trigger
  state before starting any week here)
- `PROJECT_TRACKER.md` (Next Actions — authoritative live list)
- `PROJECT_CONTEXT.md` (Current Focus, Revision History)
- `.ai/governance/DECISION_RIGHTS.md`
- `skills/content-creation/README.md` (the existing production Skill this
  plan's readiness work is anchored to)
- ADR-0013 (Build vs Reuse — the source of the Anthropic-as-unimplemented-
  option baseline claim in Section 2)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Established the monthly operator plan: four-week content-skill readiness push (readiness audit, golden-sample intake plan, benchmark/evaluation contract, integration readiness), three new content triggers alongside the existing MCP/SemVer triggers, and an explicit no-Anthropic-replacement-in-production rule for the month |
| 0.2 | 2026-07-12 | Completed Week 1 the same day: `docs/guides/CONTENT_SKILL_READINESS.md` audited the real gap between today's framework and a benchmarkable content pipeline, finding a real declarative evaluation rubric that is validated for shape but never executed against real output |
