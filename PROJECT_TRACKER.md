# AI Skill Framework - Project Tracker

Version: 0.9
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 9 - CLI Architecture**

Goal: design the command system, plugin model, extension points, dependency
injection, configuration, logging, and error handling for `AISkill.CLI`,
without implementing a CLI or choosing its language.

Status: **Completed**

## Sprint 9 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Design command system and plugin/extension model | Done | `docs/architecture/CLI_ARCHITECTURE.md` |
| Design dependency injection and configuration strategy | Done | `docs/architecture/CLI_ARCHITECTURE.md` |
| Design logging and error/exit-code handling | Done | `docs/architecture/CLI_ARCHITECTURE.md` |
| Record the architecture-first, language-deferred decision | Done | `docs/adr/ADR-0003-cli-architecture-before-implementation.md` |
| No CLI code or dependency added | Done | No `AISkill.CLI` package added this sprint |
| Update tracker, context, and README | Done | This document, `PROJECT_CONTEXT.md`, `README.md` |
| Review, commit, and push | Done | Git history and `origin/main` |

## Sprint 9 Exit Criteria

- CLI Architecture document covers command system, plugin model, extension
  points, DI, configuration precedence, logging, and error handling.
- The architecture references, but does not duplicate, the Contract
  Validation Architecture's diagnostics shape.
- No CLI implementation, package manifest, or language choice is committed.
- Review passes and Sprint 9 is pushed to `main`.

## Previous Sprint

**Sprint 8 - Validator Prototype**

Goal: implement Validator Roadmap Phase 1 (conformance fixtures pinned to a
Draft 2020-12 implementation) as a minimal offline script, without a CLI or
Runtime.

Status: **Completed**

## Sprint 8 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Pin a Draft 2020-12 implementation | Done | `requirements-validator.txt` (`jsonschema`, `referencing`, `PyYAML`) |
| Build a minimal fixture-conformance script | Done | `scripts/validate_contracts.py`, `scripts/validate-contracts.ps1` |
| Add positive/negative fixtures for every standalone schema | Done | `tests/fixtures/contracts/{skill,workflow,knowledge,evaluation,reflection}/` |
| Declare fixture cases and expected outcomes | Done | `tests/fixtures/contracts/cases.json` |
| Verify all fixtures match expectations | Done | `python scripts/validate_contracts.py` -> 10/10 |
| Record the prototype's scope and rationale as an ADR | Done | `docs/adr/ADR-0002-prototype-contract-validator.md` |
| Update Validation Guide and Validator Roadmap | Done | `docs/guides/VALIDATION_GUIDE.md`, `docs/roadmaps/VALIDATOR_ROADMAP.md` |
| Fix broken arrow glyphs in System Architecture | Done | `docs/architecture/SYSTEM_ARCHITECTURE.md` |
| Review, commit, and push | Done | Git history and `origin/main` |

## Sprint 8 Exit Criteria

- `python scripts/validate_contracts.py` passes for every declared fixture.
- Every standalone schema (Skill, Workflow, Knowledge, Evaluation, Reflection)
  has at least one valid and one invalid fixture.
- The prototype's scope, dependencies, and boundaries are recorded in an ADR.
- Validator Roadmap Phase 1 is marked Done; no semantic, repository, or CLI
  logic was added.
- Review passes and Sprint 8 is pushed to `main`.

## Previous Sprint

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

1. Design the Template Engine architecture (Milestone 10): reusable templates
   for Skill, Workflow, Knowledge, ADR, documentation, examples, and tests.
2. Begin Validator Roadmap Phase 2: safe YAML and Knowledge Markdown
   normalization adapters with preserved source locations.
3. Extend the fixture-conformance script toward Phase 3 semantic validators
   (weight sums, graph acyclicity, ID/path agreement) once adapters exist.
4. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`.

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
| 0.8 | 2026-07-04 | Completed Sprint 8 validator prototype |
| 0.9 | 2026-07-04 | Completed Sprint 9 CLI architecture |
