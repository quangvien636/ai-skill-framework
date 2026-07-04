# AI Skill Framework - Project Tracker

Version: 0.11
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 11 - Intermediate Representation (IR)**

Goal: name and generalize the existing "normalized model" concept into a
cross-cutting IR that the Validator, Generator, CLI, and future Runtime all
consume, and define the Dependency Graph / Version Graph built from it.

Status: **Completed**

### Sprint 11 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define IR pipeline, lifecycle, serialization, parser/normalization strategy | Done | `docs/architecture/IR_ARCHITECTURE.md` |
| Define Skill/Workflow/Knowledge/Metadata/Reference IR object model | Done | `docs/specifications/IR_SPECIFICATION.md` |
| Define Dependency Graph and Version Graph | Done | `docs/specifications/IR_SPECIFICATION.md`, `docs/architecture/IR_ARCHITECTURE.md` |
| Record the authoring-format-vs-IR decision | Done | `docs/adr/ADR-0005-markdown-authoring-ir-internal-contract.md` |
| Align existing terminology ("normalized model") with IR | Done | `docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md`, `schemas/README.md`, `docs/architecture/CLI_ARCHITECTURE.md` |
| Register IR Specification and update navigation | Done | `docs/specifications/README.md`, `docs/architecture/SYSTEM_ARCHITECTURE.md`, `README.md` |
| Consolidate tracker history to stop repeated "Previous Sprint" sections | Done | This document |
| Review, commit, and push | Done | Git history and `origin/main` |

### Sprint 11 Exit Criteria

- IR Architecture and IR Specification exist and reference, without
  duplicating, the Contract Validation, Metadata, Version, Knowledge
  Dependency, and Workflow contracts.
- Every existing reference to "normalized model" is aligned with the IR term
  without breaking a cross-reference.
- Dependency Graph and Version Graph are specified as derived, read-only
  constructs; no graph implementation or storage is added.
- No parser, Generator, or Runtime code is added.
- Review passes and Sprint 11 is pushed to `main`.

## Sprint History

Full per-sprint backlogs and exit criteria for completed sprints live in Git
history and the ADRs/architecture documents each sprint produced; this table
is the durable summary so this tracker does not grow one repeated section per
sprint indefinitely.

| Sprint | Title | Key Output |
| --- | --- | --- |
| 1 | Foundation | Repository governance, System Architecture, Design Principles, ADR-0001 |
| 2 | Knowledge Architecture | Knowledge hierarchy, taxonomy, template, discovery index, naming rules |
| 3 | AI Skill Specification | Normative artifact contracts, specification registry |
| 4 | Skill Architecture | Skill lifecycle, package architecture, `templates/skill/` |
| 5 | Workflow Architecture | Workflow lifecycle, package, execution, mapping design, `templates/workflow/` |
| 6 | Evaluation and Reflection Architecture | Quality evaluation and bounded reflection contracts |
| 7 | Machine-Readable Schemas | Draft 2020-12 schemas, Contract Validation Architecture, Validator Roadmap |
| 8 | Validator Prototype | `scripts/validate_contracts.py`, 10 fixture cases, ADR-0002 |
| 9 | CLI Architecture | `docs/architecture/CLI_ARCHITECTURE.md`, ADR-0003 |
| 10 | Template Engine | `docs/architecture/TEMPLATE_ENGINE_ARCHITECTURE.md`, `templates/README.md`, ADR-0004 |
| 11 | Intermediate Representation (IR) | `docs/architecture/IR_ARCHITECTURE.md`, `docs/specifications/IR_SPECIFICATION.md`, ADR-0005 |

## Risks and Guardrails

| Risk | Guardrail |
| --- | --- |
| Context becomes trapped in conversations | Record durable context in the repository |
| Master Skill becomes a giant prompt | Keep it limited to orchestration |
| Skills overlap and become hard to test | Enforce One Skill = One Responsibility |
| Knowledge is duplicated in prompts | Store reusable knowledge in the Knowledge Base |
| Implementation drifts from architecture | Update and review documentation first |
| Governance documents (this tracker) grow unbounded | Summarize completed sprints in Sprint History instead of repeating sections |

## Next Actions

1. Design the Generator Engine architecture (next sprint): the pipeline that
   consumes IR, `templates/`, and producer values to emit filled artifacts.
2. Begin Validator Roadmap Phase 2: safe YAML and Knowledge Markdown
   normalization (IR) adapters with preserved source locations.
3. Extend the fixture-conformance script toward Phase 3 semantic validators
   (weight sums, graph acyclicity, ID/path agreement) once adapters exist.
4. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`.
5. When the Generator Engine architecture lands, implement the Dependency
   Graph / Version Graph construction the IR Specification describes.

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
| 0.10 | 2026-07-04 | Completed Sprint 10 Template Engine |
| 0.11 | 2026-07-04 | Completed Sprint 11 IR; consolidated sprint history table |
