# AI Skill Framework - Project Tracker

Version: 0.17
Status: Active
Last updated: 2026-07-04

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 17 - Validator Roadmap Phase 3 (Dependency Graph + Version Graph)**

Goal: build the Dependency Graph and Version Graph on top of the Sprint 16
IR adapters, so later semantic validators can reason about references,
version constraints, and cycles across multiple artifacts — without
implementing Generator, Runtime, SDK, or a full CLI.

Status: **Completed**

### Sprint 17 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Record node-kind, excluded-edge, diagnostic-prefix, and SemVer-precedence decisions | Done | `docs/adr/ADR-0010-dependency-and-version-graph-scope.md` |
| Factor cycle detection into a shared, reusable utility (refactor, not duplicate) | Done | `scripts/asf_validator/graph.py`; `workflow_ir.py` now reuses it |
| Extend Version IR with range satisfaction and self-contradiction checks | Done | `scripts/asf_validator/version_ir.py` |
| Implement the Dependency Graph (nodes, edges, missing-dependency, cycle, duplicate-ID) | Done | `scripts/asf_validator/dependency_graph.py` |
| Implement the Version Graph (unsatisfiable range, ambiguous reference, deprecated/archived) | Done | `scripts/asf_validator/version_graph.py` |
| Add the ASF-GRAPH-* diagnostic prefix | Done | `docs/architecture/CLI_ARCHITECTURE.md` |
| Add a graph fixture-conformance script and 10 multi-artifact scenarios | Done | `scripts/build_graph.py`, `tests/fixtures/graph/` (10/10) |
| Add unit tests for graph/dependency_graph/version_graph | Done | `tests/unit/test_{graph,dependency_graph,version_graph}.py` (23 new tests) |
| Fix a spec/implementation inconsistency found while documenting (archived+required must be an error, not always a warning) | Done | `scripts/asf_validator/version_graph.py`, `docs/adr/ADR-0010-*.md` |
| Confirm zero regressions in Phase 1 and Phase 2 | Done | `validate_contracts.py` 10/10, `build_ir.py` 16/16 unchanged |
| Update Validator Roadmap, IR Specification, CLI Architecture | Done | `docs/roadmaps/VALIDATOR_ROADMAP.md`, `docs/specifications/IR_SPECIFICATION.md`, `docs/architecture/CLI_ARCHITECTURE.md` |
| Review, commit, and push | Done | Git history and `origin/main` |

### Sprint 17 Exit Criteria

- Dependency Graph nodes/edges match `docs/specifications/IR_SPECIFICATION.md`
  exactly (`skill:*`, `workflow:*`, `kb:*`); no Evaluation/Reflection nodes
  or Runtime/Tool edges were invented.
- `python scripts/validate_contracts.py` (Phase 1) still passes 10/10.
- `python scripts/build_ir.py` (Phase 2) still passes 16/16.
- `python scripts/build_graph.py` (Phase 3 graph) passes all declared
  multi-artifact scenarios.
- `python -m unittest discover -s tests/unit` passes all unit tests.
- No Generator, Runtime, SDK, or full CLI implementation is added.
- No repository Markdown link or ADR reference is broken.
- Review passes and Sprint 17 is pushed to `main`.

### Sprint 17 Deferred / Documented Gaps

(See `docs/roadmaps/VALIDATOR_ROADMAP.md` Phase 3 for full detail.)

- ID/path, weight-sum, mapping, and routing semantic rules — remaining
  Phase 3 work.
- Full repository-wide graph construction (real Project Discovery instead
  of an explicit fixture list) — Phase 4.
- SemVer pre-release precedence in version comparison — documented
  simplification (ADR-0010).
- `range_is_self_contradictory`'s coarse-only detection (misses adjacent-
  version squeeze cases like `>1.0.0 <1.0.1`).

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
| 17 | Validator Roadmap Phase 3 (Dependency/Version Graph) | `dependency_graph.py`, `version_graph.py`, `scripts/build_graph.py` (10/10), 53 unit tests, ADR-0010 |

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

1. Implement the remaining Phase 3 semantic validators (ID/path, weight-sum,
   mapping, routing rules) using the Sprint 17 Dependency/Version Graph.
2. Begin Phase 4: extend the Dependency Graph from an explicit fixture list
   to a real repository-wide scan (Project Discovery, `CLI_ARCHITECTURE.md`),
   plus Knowledge Index and package-structure validation.
3. When a CLI implementation sprint starts, choose and record its language
   and package layout in a new ADR that conforms to `CLI_ARCHITECTURE.md`,
   and wire `scripts/build_ir.py`/`scripts/build_graph.py`'s pipelines
   behind the `validate`/`generate` commands per `CLI_ARCHITECTURE.md`'s
   Validator/Generator Integration.
4. Add a lightweight link/anchor check to the fixture-conformance scripts
   (or a sibling script) so Sprint 14's manual broken-link scan does not
   need to be repeated by hand every sprint — an Automation Engineer task
   per `.ai/roles/AUTOMATION_ENGINEER.md`.
5. Consider whether `.ai/governance/DECISION_RIGHTS.md`'s ADR-acceptance
   convention needs a lighter-weight mechanical check (e.g., an ADR
   "Status" field the validator confirms is one of the allowed values).
6. Add precise line/column source-position tracking to IR adapter
   diagnostics (currently field/section names only) — Sprint 16's
   Deferred / Documented Gap, still open.
7. If pre-release versions are ever adopted, implement full SemVer
   pre-release precedence in `version_ir.py` (Sprint 17's documented
   simplification).

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
| 0.17 | 2026-07-04 | Completed Sprint 17 Validator Roadmap Phase 3 (Dependency/Version Graph) |
