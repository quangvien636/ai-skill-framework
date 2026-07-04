# AI Skill Framework - Project Tracker

Version: 0.14
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 14 - Repository Engineering Review**

Goal: a corrective, non-additive pass across the documents Sprints 8-13
produced: terminology, ADR cross-links, navigation, duplication, and broken
references.

Status: **Completed**

### Sprint 14 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Verify every ADR is referenced and every ADR reference resolves | Done | Repository-wide `ADR-\d{4}` grep against `docs/adr/` |
| Restructure README navigation into Foundation/Architecture/Specifications/Validation groups; add missing Skill/Workflow/Evaluation/Reflection/CLI/Generator/IR links | Done | `README.md` |
| Align Validator Roadmap Phase 2 and its Adapter definition with the Sprint 11 IR adapter term | Done | `docs/roadmaps/VALIDATOR_ROADMAP.md` |
| Cross-link the Validation Guide to the IR Architecture and ADR-0005 | Done | `docs/guides/VALIDATION_GUIDE.md` |
| Scan every Markdown file for broken relative links/anchors; fix the one found | Done | `docs/architecture/GENERATOR_ARCHITECTURE.md` (bad relative path to `IR_SPECIFICATION.md`) |
| Spot-check extension-point tables across CLI/Generator/Template Engine architectures for drift | Done | No drift found |
| Review, commit, and push | Done | Git history and `origin/main` |

### Sprint 14 Exit Criteria

- No dangling ADR reference; every existing ADR is linked from at least one
  architecture document.
- README's Documentation section reaches every Sprint 1-13 architecture
  document directly or via one clearly named hop.
- No broken relative Markdown link or heading anchor remains in `docs/`,
  `README.md`, `templates/`, or `schemas/`.
- Validator Roadmap and Validation Guide terminology agrees with the IR
  Architecture (ADR-0005) without deleting the "normalized model" synonym.
- No new architecture is introduced this sprint; changes are corrective only.
- Review passes and Sprint 14 is pushed to `main`.
- No CLI implementation is added.
- Review passes and Sprint 13 is pushed to `main`.

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
| 12 | Generator Engine Architecture | `docs/architecture/GENERATOR_ARCHITECTURE.md`, ADR-0006 |
| 13 | CLI Design Expansion | `docs/architecture/CLI_ARCHITECTURE.md` v0.4, ADR-0007 |
| 14 | Repository Engineering Review | README navigation rework, broken-link fix, IR terminology alignment |

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

1. Design the AI Team Architecture (`.ai/`): roles, playbooks, standards,
   and governance for human/AI collaboration on this repository.
2. Begin Validator Roadmap Phase 2: safe YAML and Knowledge Markdown IR
   adapters with preserved source locations.
3. Extend the fixture-conformance script toward Phase 3 semantic validators
   (weight sums, graph acyclicity, ID/path agreement) once adapters exist.
4. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`.
5. When a Generator implementation sprint starts, build the Dependency
   Graph / Version Graph construction the IR Specification describes.
6. Add a lightweight link/anchor check to the fixture-conformance script (or
   a sibling script) so Sprint 14's manual broken-link scan does not need to
   be repeated by hand every sprint.

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
| 0.12 | 2026-07-04 | Completed Sprint 12 Generator Engine architecture |
| 0.13 | 2026-07-04 | Completed Sprint 13 CLI Design Expansion |
| 0.14 | 2026-07-04 | Completed Sprint 14 Repository Engineering Review |
