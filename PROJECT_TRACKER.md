# AI Skill Framework - Project Tracker

Version: 0.19
Status: Active
Last updated: 2026-07-05

## Purpose

Track the repository-backed delivery state of the AI Skill Framework. A task is
complete only when its durable output exists in the repository and satisfies the
project's definition of done.

## Current Sprint

**Sprint 19 - Research Skill v1**

Goal: deliver a reusable production Research Skill and topic-to-brief Workflow
that future Content, SEO, Marketing, Business, and Coding skills can consume.

Status: **Completed**

### Sprint 19 Backlog

| Item | Status | Evidence / Output |
| --- | --- | --- |
| Add an active Skill covering questions, source requirements, evidence, reliability, claims, findings, uncertainty, gaps, and briefs | Done | `skills/research/` |
| Keep reusable research methodology outside the Skill | Done | Six documents under `knowledge/foundational/research/`; `KNOWLEDGE_INDEX.md` |
| Add the end-to-end topic-to-brief Workflow | Done | `workflows/research-topic-to-brief/` |
| Cover representative, minimal-evidence, contradictory, and invalid/refusal cases | Done | `skills/research/examples/` |
| Validate canonical production files without fixture-only copies | Done | `tests/fixtures/{contracts,ir,graph}/cases.json` reference production paths directly |
| Prove all Knowledge and Skill references resolve together | Done | `research-v1-production-artifacts` graph scenario |
| Document usage, validation, and execution boundaries | Done | Root and package READMEs; `PROJECT_CONTEXT.md` |
| Preserve IR architecture boundaries | Done | Empty runtime/tool dependencies; embedded Evaluation/Reflection only |

### Sprint 19 Exit Criteria

- `python scripts/validate_contracts.py` passes 14/14.
- `python scripts/build_ir.py` passes 31/31, including every production
  Research artifact.
- `python scripts/build_graph.py` passes 12/12, including the production package
  with all required Knowledge and Skill references.
- `python -m unittest discover` passes all 60 tests.
- No schema fields, standalone Evaluation/Reflection artifacts, Runtime/Tool
  graph nodes, source-fetching behavior, or unrelated refactors are introduced.
- Repository Markdown links and ADR references remain valid.

### Sprint 19 Deferred / Documented Gaps

- No Runtime or Generator executes the Skill yet; v1 is a validated framework
  contract, Knowledge package, examples, and Workflow.
- No browser, fetcher, connector, or external verification mechanism exists;
  v1 accepts only caller-supplied source records and evidence notes.
- The current schema validates supplied-source and evidence-note items as
  objects but cannot express their nested fields; the Knowledge and examples
  document the expected structure without inventing schema fields.
- Research reasoning and embedded Evaluation/Reflection cannot run until the
  planned Runtime exists.
- Repository-wide discovery remains Phase 4, so production artifacts are
  explicitly registered in the fixture manifests.

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
| 18 | Content Creation Skill v1 | Active Skill, five Knowledge documents, end-to-end Workflow, production graph scenario |
| 19 | Research Skill v1 | Active Skill, six methodology documents, topic-to-brief Workflow, production graph scenario |

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

1. Resume the remaining Phase 3 semantic validators (ID/path, weight-sum,
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
| 0.18 | 2026-07-05 | Completed Sprint 18 Content Creation Skill v1 |
| 0.19 | 2026-07-05 | Completed Sprint 19 Research Skill v1 |
