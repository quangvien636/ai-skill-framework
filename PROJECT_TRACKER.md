# AI Skill Framework - Project Tracker

Version: 0.4
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 4 - Skill Architecture**

Goal: make the Skill specification authorable and generator-ready through a
lifecycle, package architecture, neutral template, validation, tests, and examples.

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

## Sprint 4 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define Skill lifecycle | Done | `docs/architecture/SKILL_ARCHITECTURE.md` |
| Define Skill folder and template standards | Done | Architecture and `templates/skill/` |
| Define input/output architecture | Done | Skill Architecture and Skill Specification |
| Define validation rules | Done | `docs/architecture/SKILL_ARCHITECTURE.md` |
| Define testing and example standards | Done | Architecture and template guidance |
| Add generator-ready neutral template | Done | `templates/skill/` |
| Confirm no production Skill exists | Done | Empty `skills/` |
| Review, commit, and push | Done | Git history and `origin/main` |

## Sprint Exit Criteria

- A generator can create the required Skill package from `templates/skill/`.
- Lifecycle, folders, contracts, validation, testing, and examples are explicit.
- The architecture preserves One Skill = One Responsibility and Knowledge reuse.
- No production Skill is implemented.
- Review passes and all Sprint 4 changes are committed and pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Design Sprint 5 Workflow Architecture.
2. Add a neutral Workflow package template.
3. Define deterministic execution, mapping, and failure architecture.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
| 0.3 | 2026-07-04 | Completed Sprint 3 AI Skill Specification |
| 0.4 | 2026-07-04 | Completed Sprint 4 Skill Architecture |
