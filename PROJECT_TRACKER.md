# AI Skill Framework - Project Tracker

Version: 0.7
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 7 - Machine-Readable Schemas and Contract Validators**

Goal: encode the established contracts as Draft 2020-12 schemas and define the
layered validation foundation without implementing a full CLI or Runtime.

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

## Sprint 6 - Evaluation and Reflection Architecture

Status: **Completed**

Sprint 6 established consistent quality evaluation and bounded reflection.

## Sprint 7 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Create Skill and Workflow schemas | Done | `schemas/skill.schema.json`, `schemas/workflow.schema.json` |
| Create Knowledge schema | Done | `schemas/knowledge.schema.json` |
| Create Evaluation and Reflection schemas | Done | `schemas/evaluation.schema.json`, `schemas/reflection.schema.json` |
| Create Metadata and Version schemas | Done | `schemas/metadata.schema.json`, `schemas/version.schema.json` |
| Document validation architecture | Done | `docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md` |
| Add validation guide | Done | `docs/guides/VALIDATION_GUIDE.md` |
| Add validator roadmap | Done | `docs/roadmaps/VALIDATOR_ROADMAP.md` |
| Verify JSON, refs, links, and contract alignment | Done | Sprint 7 review |
| Review, commit, and push | Done | Git history and `origin/main` |

## Sprint Exit Criteria

- All seven core schemas use JSON Schema Draft 2020-12.
- Schemas compose shared Metadata, Version, Evaluation, and Reflection contracts.
- Knowledge Markdown remains authoritative and validates through a normalized model.
- Structural, semantic, and repository validation boundaries are explicit.
- No production Skill, Runtime, or full CLI is implemented.
- Review passes and Sprint 7 is pushed to `main`.

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |

## Next Actions

1. Plan schema conformance fixtures as the next Sprint.
2. Select and pin a Draft 2020-12 validator implementation.
3. Implement safe YAML and Knowledge Markdown normalization adapters.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the Sprint 1 Foundation tracker |
| 0.2 | 2026-07-04 | Added Sprint 2 Knowledge Architecture progress |
| 0.3 | 2026-07-04 | Completed Sprint 3 AI Skill Specification |
| 0.4 | 2026-07-04 | Completed Sprint 4 Skill Architecture |
| 0.5 | 2026-07-04 | Completed Sprint 5 Workflow Architecture |
| 0.6 | 2026-07-04 | Completed Sprint 6 quality architecture |
| 0.7 | 2026-07-04 | Completed Sprint 7 schemas and validation foundation |
