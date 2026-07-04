# AI Skill Framework - Project Tracker

Version: 0.6
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 6 - Evaluation and Reflection Architecture**

Goal: standardize evaluation metrics, scoring, thresholds, failure routing,
reflection improvement, retry, termination, and evidence.

Status: **Completed**

## Sprint 1 - Foundation

Status: **Completed**

Foundation established repository governance, system architecture, project
context, design principles, and ADR-0001. Remaining placeholder documents are
tracked as future documentation work and do not redefine the completed
architecture baseline.

## Sprint 2 - Knowledge Architecture

Status: **Completed**

Sprint 2 established the Knowledge hierarchy, taxonomy, document template,
discovery index, and naming rules.

## Sprint 3 - AI Skill Specification

Status: **Completed**

Sprint 3 established the normative artifact contracts and specification registry.

## Sprint 4 - Skill Architecture

Status: **Completed**

Sprint 4 established the Skill lifecycle, package architecture, and template.

## Sprint 5 - Workflow Architecture

Status: **Completed**

Sprint 5 established Workflow lifecycle, package, execution, and mapping design.

## Sprint 6 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define Evaluation Engine architecture | Done | `docs/architecture/EVALUATION_ARCHITECTURE.md` |
| Define Reflection Engine architecture | Done | `docs/architecture/REFLECTION_ARCHITECTURE.md` |
| Define metrics, scoring, and thresholds | Done | Evaluation architecture |
| Define retry and improvement loop | Done | Reflection architecture |
| Define failure handling and evidence | Done | Both quality architectures |
| Confirm specifications remain canonical schemas | Done | Cross-document review |
| Review, commit, and push | Done | Git history and `origin/main` |

## Sprint Exit Criteria

- Skills and Workflows share one deterministic quality model.
- Evaluation is read-only and Reflection is bounded and evidence-directed.
- Retry, stagnation, termination, and failure routing are explicit.
- No Runtime implementation is added.
- Review passes and Sprint 6 is pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Select the next Sprint through a documented planning checkpoint.
2. Recommend schema and validator implementation before production Skills.
3. Add conformance fixtures for Skill, Workflow, Evaluation, and Reflection.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
| 0.3 | 2026-07-04 | Completed Sprint 3 AI Skill Specification |
| 0.4 | 2026-07-04 | Completed Sprint 4 Skill Architecture |
| 0.5 | 2026-07-04 | Completed Sprint 5 Workflow Architecture |
| 0.6 | 2026-07-04 | Completed Sprint 6 quality architecture |
