# AI Skill Framework - Project Tracker

Version: 0.15
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 15 - AI Team Architecture**

Goal: document human/AI collaboration on this repository itself — roles,
playbooks, standards, and governance — under `.ai/`, as governance
documentation rather than executable Skills.

Status: **Completed**

### Sprint 15 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Define seven roles (responsibility, inputs, outputs, one decision right, boundaries) | Done | `.ai/roles/*.md` |
| Define the Sprint Workflow and Handover playbooks | Done | `.ai/playbooks/SPRINT_WORKFLOW.md`, `.ai/playbooks/HANDOVER.md` |
| Define collaboration standards (ADR/tracker ownership, review gates) | Done | `.ai/standards/COLLABORATION_STANDARDS.md` |
| Define human vs. AI decision rights, consistent with ADR-0001 | Done | `.ai/governance/DECISION_RIGHTS.md` |
| Record the documentation-not-executable boundary decision | Done | `docs/adr/ADR-0008-ai-team-is-documentation-not-executable.md` |
| Add `.ai/README.md` index and link it from the repository README | Done | `.ai/README.md`, `README.md` |
| Review, commit, and push | Done | Git history and `origin/main` |

### Sprint 15 Exit Criteria

- Every role names one responsibility, its inputs/outputs, exactly one
  decision right, and explicit boundaries against the roles it could
  overlap with.
- No role has a `skill.yaml` or is referenced from a Workflow step or the
  Dependency Graph.
- The documentation-vs-executable boundary is recorded in an ADR that does
  not contradict ADR-0001.
- `.ai/README.md`'s links all resolve to files actually created.
- Review passes and Sprint 15 is pushed to `main`.
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
| 15 | AI Team Architecture | `.ai/roles/`, `.ai/playbooks/`, `.ai/standards/`, `.ai/governance/`, ADR-0008 |

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

1. Begin Validator Roadmap Phase 2: safe YAML and Knowledge Markdown IR
   adapters with preserved source locations.
2. Extend the fixture-conformance script toward Phase 3 semantic validators
   (weight sums, graph acyclicity, ID/path agreement) once adapters exist.
3. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`.
4. When a Generator implementation sprint starts, build the Dependency
   Graph / Version Graph construction the IR Specification describes.
5. Add a lightweight link/anchor check to the fixture-conformance script (or
   a sibling script) so Sprint 14's manual broken-link scan does not need to
   be repeated by hand every sprint — an Automation Engineer task per
   `.ai/roles/AUTOMATION_ENGINEER.md`.
6. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).

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
| 0.15 | 2026-07-04 | Completed Sprint 15 AI Team Architecture |
