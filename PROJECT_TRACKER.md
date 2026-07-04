# AI Skill Framework - Project Tracker

Version: 0.2
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 2 - Knowledge Architecture**

Goal: establish a scalable, discoverable, and governed Knowledge Base that keeps
reusable knowledge separate from prompts and Skill logic.

Status: **Completed**

## Sprint 1 - Foundation

Status: **Completed**

Foundation established repository governance, system architecture, project
context, design principles, and ADR-0001. Remaining placeholder documents are
tracked as future documentation work and do not redefine the completed
architecture baseline.

## Sprint 2 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define scalable knowledge hierarchy | Done | `docs/architecture/KNOWLEDGE_ARCHITECTURE.md` |
| Define category standards and registry | Done | `knowledge/KNOWLEDGE_CATEGORIES.md` |
| Define domain and topic standards | Done | `docs/architecture/KNOWLEDGE_ARCHITECTURE.md` |
| Create canonical Knowledge Template | Done | `knowledge/_templates/KNOWLEDGE_TEMPLATE.md` |
| Create canonical Knowledge Index | Done | `knowledge/KNOWLEDGE_INDEX.md` |
| Define knowledge naming convention | Done | `docs/principles/KNOWLEDGE_NAMING_CONVENTION.md` |
| Add Knowledge Base navigation | Done | `knowledge/README.md` |
| Align system architecture and project context | Done | Architecture and context documents |
| Review consistency and duplication | Done | Sprint 2 acceptance review |
| Commit and push reviewed documentation | Done | Git history and `origin/main` |

## Sprint Exit Criteria

- Knowledge hierarchy scales through category, domain, topic, and document levels.
- Category, topic, metadata, lifecycle, naming, and indexing standards are
  explicit.
- Architecture, template, taxonomy, index, and naming responsibilities do not
  duplicate one another.
- Documentation is consistent with the Design Principles and ADR-0001.
- Review passes and all Sprint 2 changes are committed and pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Add the first real knowledge topic using the canonical template.
2. Define automated validation for knowledge metadata and index integrity.
3. Plan Skill-to-Knowledge consumption contracts.
4. Select and document the next sprint objective.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
