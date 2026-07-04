# AI Skill Framework - Project Tracker

Version: 0.5
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 5 - Workflow Architecture**

Goal: define a generator-ready Workflow package and deterministic execution,
orchestration, mapping, failure, validation, and testing architecture.

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

## Sprint 5 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define Workflow lifecycle and folder standard | Done | `docs/architecture/WORKFLOW_ARCHITECTURE.md` |
| Add generator-ready Workflow template | Done | `templates/workflow/` |
| Define deterministic execution and orchestration | Done | Workflow Architecture |
| Define input/output mapping and failures | Done | Workflow Architecture |
| Define validation and testing | Done | Architecture and template guidance |
| Confirm no Runtime or production Workflow exists | Done | Repository review |
| Review, commit, and push | Done | Git history and `origin/main` |

## Sprint Exit Criteria

- A future Runtime can deterministically execute the documented Workflow model.
- A generator can create the required package from `templates/workflow/`.
- Orchestration remains outside Skills and the Master Skill stays thin.
- No Runtime or production Workflow is implemented.
- Review passes and Sprint 5 is pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Design Sprint 6 Evaluation and Reflection Architecture.
2. Unify quality metrics, scoring, thresholds, retry, and improvement flow.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
| 0.3 | 2026-07-04 | Completed Sprint 3 AI Skill Specification |
| 0.4 | 2026-07-04 | Completed Sprint 4 Skill Architecture |
| 0.5 | 2026-07-04 | Completed Sprint 5 Workflow Architecture |
