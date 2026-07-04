# AI Skill Framework - Project Tracker

Version: 0.3
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 3 - AI Skill Specification**

Goal: establish normative, machine-consumable contracts for Skills, Workflows,
Knowledge dependencies, quality control, artifact metadata, naming, and versions
without implementing actual Skills.

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

## Sprint 3 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define AI Skill package and behavior contract | Done | `docs/specifications/AI_SKILL_SPECIFICATION.md` |
| Define Workflow execution and mapping contract | Done | `docs/specifications/WORKFLOW_SPECIFICATION.md` |
| Define Knowledge dependency and reuse contract | Done | `docs/specifications/KNOWLEDGE_DEPENDENCY_SPECIFICATION.md` |
| Define evaluation pipeline and scoring | Done | `docs/specifications/EVALUATION_SPECIFICATION.md` |
| Define reflection and retry contract | Done | `docs/specifications/REFLECTION_SPECIFICATION.md` |
| Standardize artifact metadata | Done | `docs/specifications/METADATA_SPECIFICATION.md` |
| Standardize framework naming | Done | `docs/principles/NAMING_CONVENTION.md` |
| Define versions and compatibility | Done | `docs/specifications/VERSION_SPECIFICATION.md` |
| Create canonical specification registry | Done | `docs/specifications/README.md` |
| Align architecture, context, and Knowledge template | Done | Updated repository contracts |
| Review consistency, links, and duplication | Done | Sprint 3 acceptance review |
| Commit and push reviewed documentation | Done | Git history and `origin/main` |

## Sprint Exit Criteria

- Every requested specification has purpose, scope, definitions, design,
  examples, references, and revision history.
- Skill and Workflow contracts preserve One Skill = One Responsibility and keep
  the Master Skill limited to orchestration.
- Knowledge references reuse Sprint 2 taxonomy, index, template, and naming
  authorities without duplicating them.
- Metadata, naming, version, evaluation, and reflection rules are internally
  consistent and testable.
- No actual Skill is implemented.
- Review passes and all Sprint 3 changes are committed and pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Plan Sprint 4 as contract validation and tooling.
2. Define machine-readable schemas for `skill.yaml` and `workflow.yaml`.
3. Implement validators for metadata, naming, versions, mappings, and Knowledge
   references.
4. Add specification conformance fixtures before generating actual Skills.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
| 0.3 | 2026-07-04 | Completed Sprint 3 AI Skill Specification |
