# AI Skill Framework - Project Tracker

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 1 - Foundation**

Goal: establish the documentation-first foundation and governance needed before
framework implementation begins.

## Sprint Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Initialize Git repository and GitHub remote | Done | Repository history and `origin` |
| Add project README and `.gitignore` | Done | `README.md`, `.gitignore` |
| Create initial folder structure | Done | Repository directories |
| Define system architecture | Done | `docs/architecture/SYSTEM_ARCHITECTURE.md` |
| Define project context | Done | `PROJECT_CONTEXT.md` |
| Define design principles | Done | `docs/principles/DESIGN_PRINCIPLES.md` |
| Establish repository as source of truth | Done | `docs/adr/ADR-0001-repository-is-the-source-of-truth.md` |
| Establish project tracker | Done | `PROJECT_TRACKER.md` |
| Define naming convention | Planned | `docs/principles/NAMING_CONVENTION.md` |
| Specify repository folder structure | Planned | Architecture documentation |
| Write development guide | Planned | `docs/guides/DEVELOPMENT_GUIDE.md` |
| Complete getting-started guide | Planned | `docs/guides/GETTING_STARTED.md` |
| Define roadmap beyond Foundation | Planned | `docs/roadmaps/ROADMAP.md` |
| Define project glossary | Planned | `docs/references/GLOSSARY.md` |

## Sprint Exit Criteria

- Foundation documents contain no placeholders.
- Architecture, principles, context, tracker, and ADRs are mutually consistent.
- Contributor and documentation workflows are explicit.
- All Sprint 1 changes are reviewed, committed, and pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Complete the naming convention.
2. Document the intended folder structure.
3. Complete the development and getting-started guides.
4. Replace roadmap and glossary placeholders.
5. Review Sprint 1 exit criteria.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
