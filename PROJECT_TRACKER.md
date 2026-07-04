# AI Skill Framework - Project Tracker

Version: 0.16
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 16 - Validator Roadmap Phase 2 (IR Adapters)**

Goal: implement typed IR adapters for Skill, Workflow, Knowledge,
Evaluation, and Reflection, extending the Sprint 8 validator prototype
without redesigning the CLI, Generator, or any specification.

Status: **Completed**

### Sprint 16 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Record package location, Metadata/Version scope, and new diagnostic prefix decisions | Done | `docs/adr/ADR-0009-ir-adapter-package-and-scope.md` |
| Build the reusable pipeline (loader, schema registry, per-kind adapters, diagnostics) | Done | `scripts/asf_validator/` |
| Implement Skill, Workflow, Knowledge, Evaluation, Reflection IR adapters | Done | `scripts/asf_validator/{skill,workflow,knowledge,evaluation,reflection}_ir.py` |
| Implement reusable Metadata/Version helpers (not standalone adapters) | Done | `scripts/asf_validator/metadata_ir.py`, `scripts/asf_validator/version_ir.py` |
| Add an IR fixture-conformance script and manifest | Done | `scripts/build_ir.py`, `tests/fixtures/ir/cases.json` (16/16) |
| Add fixtures for valid/missing-required/invalid-reference/unsupported-version/malformed-metadata/cycle | Done | `tests/fixtures/ir/{skill,workflow,knowledge,evaluation,reflection}/` |
| Add unit tests for every adapter | Done | `tests/unit/test_*.py` (30 tests, all pass) |
| Fix a bug the unit tests caught (`extract_metadata_ir` returning an object despite error diagnostics) | Done | `scripts/asf_validator/metadata_ir.py` |
| Add the ASF-PARSE-* diagnostic prefix | Done | `docs/architecture/CLI_ARCHITECTURE.md` |
| Confirm zero regressions in the Sprint 8 validator | Done | `python scripts/validate_contracts.py` still 10/10 |
| Update Validator Roadmap (Phase 2 Done, assumptions, deferred items) | Done | `docs/roadmaps/VALIDATOR_ROADMAP.md` |
| Review, commit, and push | Done | Git history and `origin/main` |

### Sprint 16 Exit Criteria

- Every Skill/Workflow/Knowledge/Evaluation/Reflection adapter builds a
  strongly typed IR object matching `docs/specifications/IR_SPECIFICATION.md`.
- Loading, schema validation, IR conversion, and diagnostics are separate
  modules with no duplicated parsing logic, no hardcoded repository paths,
  and no global mutable state.
- `python scripts/validate_contracts.py` (Phase 1) still passes 10/10 with
  no changes to its behavior.
- `python scripts/build_ir.py` (Phase 2) passes 16/16 fixture cases.
- `python -m unittest discover -s tests/unit` passes all unit tests.
- No Runtime, SDK, Generator rendering, or CLI implementation is added.
- No repository Markdown link or ADR reference is broken.
- Review passes and Sprint 16 is pushed to `main`.

### Sprint 16 Deferred / Documented Gaps

(See `docs/roadmaps/VALIDATOR_ROADMAP.md` Phase 2 for full detail.)

- Cross-repository reference resolution (Dependency Graph) — Phase 3/4.
- Version-range satisfaction checking — Phase 3.
- Precise line/column source-position tracking beyond YAML's own parse
  errors — not yet implemented.
- Knowledge ID/taxonomy/path agreement against the Knowledge Index —
  Phase 3, requires Project Discovery integration.

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
| 16 | Validator Roadmap Phase 2 (IR Adapters) | `scripts/asf_validator/`, `scripts/build_ir.py` (16/16), 30 unit tests, ADR-0009 |

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

1. Build the Dependency Graph and Version Graph (IR Specification) on top
   of the Sprint 16 adapters — the natural Phase 3 starting point.
2. Implement version-range satisfaction checking (Phase 3).
3. Extend the fixture-conformance script toward the remaining Phase 3
   semantic validators (weight sums, mapping/routing rules, ID/taxonomy/
   path agreement) once the Dependency Graph exists.
4. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`,
   and wire `scripts/build_ir.py`'s pipeline behind the `validate`/`generate`
   commands per `CLI_ARCHITECTURE.md`'s Validator/Generator Integration.
5. Add a lightweight link/anchor check to the fixture-conformance script (or
   a sibling script) so Sprint 14's manual broken-link scan does not need to
   be repeated by hand every sprint — an Automation Engineer task per
   `.ai/roles/AUTOMATION_ENGINEER.md`.
6. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).
7. Add precise line/column source-position tracking to IR adapter
   diagnostics (currently field/section names only) — see Sprint 16's
   Deferred / Documented Gaps in `docs/roadmaps/VALIDATOR_ROADMAP.md`.

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
| 0.16 | 2026-07-04 | Completed Sprint 16 Validator Roadmap Phase 2 (IR adapters); removed a stray duplicated "Previous Sprint" section left over from an earlier edit |
