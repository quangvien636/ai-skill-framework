# Repository Architecture Map

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Document the purpose, ownership, and lifecycle of every major repository
area, based on direct inspection of this repository, so a session never has
to guess what a directory is for or where new content belongs.

## Scope

Covers top-level directories and document categories as they exist today.
Where this document recommends structure that does not yet exist, it is
explicitly labeled **Proposed** — never presented as current fact, per this
Batch's "do not invent repository facts" rule.

## Design

### Verified current top-level structure

| Path | Purpose | Ownership (Decision Right) | Allowed contents | Prohibited contents | Authoritative status | Lifecycle |
| --- | --- | --- | --- | --- | --- | --- |
| `MASTER_OPERATOR.md`, `CLAUDE.md`, `AGENTS.md` | Operating manual and tool-auto-discovery routing | Documentation Engineer | Spine governance content; thin routing text | Chapter content (belongs under `docs/operator/`) | Authoritative for process/navigation only | Stable; changes on structural TOC changes |
| `PROJECT_CONTEXT.md` | Current architecture understanding and sprint-by-sprint focus narrative | Principal Engineer (Current Focus); any role (other sections) | Vision, architecture summary, working principles, current-focus narrative, revision history | Actionable per-item task tracking (belongs in `PROJECT_TRACKER.md`) | Authoritative for current narrative state | Updated every sprint |
| `PROJECT_TRACKER.md` | Actionable delivery state | Principal Engineer (opens/closes Current Sprint) | Current/Previous Sprint, backlog tables, Sprint History, Next Actions, Risks and Guardrails | Long-form architecture narrative (belongs in `PROJECT_CONTEXT.md` or `docs/architecture/`) | Authoritative for what is done/in-progress/blocked | Updated every sprint |
| `README.md` | Human-facing landing page and navigation index | Documentation Engineer | Vision summary, links to canonical documents | Duplicated content from linked documents | Authoritative for navigation only | Updated when major navigation changes |
| `.ai/` | Governance: roles, playbooks, standards, decision rights | Documentation Engineer (structure); Chief Architect (governance content) | Role definitions, playbooks, collaboration standards, decision rights | Executable code, `skill.yaml` files (ADR-0008 forbids this) | Authoritative for who decides what | Stable; changes rarely, each change is significant |
| `docs/adr/` | Architecture Decision Records | Chief Architect (content/acceptance) | One immutable file per decision, `ADR_TEMPLATE.md` | Edits to an already-`Accepted` ADR's Decision (must supersede instead) | Authoritative for accepted decisions | Append-only; superseded, never edited |
| `docs/architecture/` | System/component architecture specifications | Framework Engineer (content); Chief Architect (acceptance of structural changes) | One file per architectural component/subsystem | Governance content, sprint status | Authoritative for how components work | Updated as architecture evolves, reviewed against ADRs |
| `docs/specifications/` | Normative artifact contracts (Skill, Workflow, Knowledge, Evaluation, Reflection, Metadata, Version, IR) | Framework Engineer / Chief Architect | Contract rules producers/consumers must follow | Implementation detail, UI/CLI behavior | Authoritative for artifact shape/rules | Stable; versioned like any other document |
| `docs/principles/` | Cross-cutting design and naming rules | Chief Architect | Design Principles, Naming Convention, Knowledge Naming Convention | Component-specific rules (belong in architecture docs) | Authoritative cross-cutting | Very stable |
| `docs/guides/` | Operational how-to documents scoped to one task | Documentation Engineer / Automation Engineer | Validation Guide, Compiler Lifecycle, readiness/operator-plan guides | Architecture rationale (belongs in `docs/architecture/`) | Authoritative for the specific task named | Updated as the task's mechanics change |
| `docs/roadmaps/` | Strategic sequencing and longer-horizon intent | Principal Engineer | Ordered milestone summaries | Per-item actionable status (belongs in tracker) | Authoritative for strategic order | Updated per completed milestone |
| `docs/references/` | Cross-cutting reference material (currently only `GLOSSARY.md`, a stub — see [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)) | Documentation Engineer | Terminology, lookup tables | Normative rules (belong in principles/specifications) | Authoritative once populated | Stable |
| `docs/_templates/` | Generic document template | Documentation Engineer | `DOCUMENTATION_TEMPLATE.md` | Type-specific templates (see `docs/operator/_templates/`, `docs/adr/ADR_TEMPLATE.md`, `knowledge/_templates/`) | Authoritative shape for a generic doc | Stable |
| `docs/operator/` | Master Operator Manual chapter content (new, this Batch) | Documentation Engineer | One chapter file per `MASTER_OPERATOR.md` Table of Contents row, `_templates/` subdirectory | Normative rules that belong in an ADR, architecture doc, or specification | Authoritative for process/navigation synthesis only, per the Repository Truth Hierarchy | Grows progressively; each file versioned independently |
| `knowledge/` | Reusable domain knowledge consumed by Skills | Framework Engineer; Documentation Engineer (structure) | Category-organized knowledge documents, `KNOWLEDGE_INDEX.md`, `KNOWLEDGE_CATEGORIES.md`, `_templates/` | Prompts, Skill logic, workflow orchestration | Authoritative domain content for Skills | Extended per Contribution Rule: search before creating |
| `skills/` | Production Skill packages | Framework Engineer | `skill.yaml`, `instructions.md`, `README.md` per Skill | Roles, governance, ad hoc scripts | Authoritative Skill definitions | Lifecycle per `docs/specifications/AI_SKILL_SPECIFICATION.md` |
| `workflows/` | Production Workflow packages | Framework Engineer | `workflow.yaml`, `README.md` per Workflow | Skill logic itself | Authoritative Workflow definitions | Lifecycle per `docs/specifications/WORKFLOW_SPECIFICATION.md` |
| `runtime/`, `contracts/runtime/` | Runtime Contract examples/production bindings | Framework Engineer | `runtime.yaml` per contract | Adapter implementation code | Authoritative binding declarations | Lifecycle per ADR-0014 |
| `tools/` | Tool artifact declarations | Framework Engineer | `tool.yaml` per Tool | Adapter implementation code | Authoritative Tool contracts | Lifecycle per `docs/architecture/TOOL_CONNECTOR_ARCHITECTURE.md` |
| `schemas/` | Draft 2020-12 JSON Schemas | Framework Engineer / Test Engineer | One schema per artifact kind, `README.md` registry | Non-schema validation logic (belongs in `scripts/asf_validator/`) | Authoritative machine-checkable shape | Versioned; breaking changes need an ADR |
| `templates/` | Skill/Workflow scaffolding templates | Framework Engineer | `templates/skill/`, `templates/workflow/` | Populated production examples (belong in `skills/`/`workflows/`) | Authoritative starting scaffold | Stable |
| `scripts/` | Validator, IR, graph, semantic, runtime, CLI implementation | Framework Engineer / Test Engineer | `asf_validator/`, `asf_runtime/`, top-level `build_*.py`/`validate_*.py`/`asf.py`/`asf_cli.py` | Adapter-specific execution code (belongs in `adapters/`) | Authoritative validation/planning behavior | Covered by `tests/unit/` |
| `adapters/` | Execution-backend binding packages, one per Protocol seam | Framework Engineer | One subdirectory per adapter, own `requirements-<name>.txt`, own `tests/` | Imports of another adapter package (forbidden by ADR-0013) | Authoritative binding/execution code for its one seam | Each adapter independently tested and isolated |
| `tests/` | Core unit test suite | Test Engineer | `tests/unit/*.py`, `tests/fixtures/` | Adapter-specific tests (live in `adapters/<name>/tests/`) | Authoritative correctness evidence for core | Grows with every code change |
| `runs/` | Workflow execution run output (e.g., `content-workflow-<id>/`) | Automation Engineer | Generated run artifacts | Hand-maintained documentation | Not authoritative — generated evidence, not source | Reproducible; safe to regenerate |
| `examples/` | (present, not yet inventoried in depth this session) | Framework Engineer | Worked usage examples | — | — | — |
| `changelog/` | Reserved for framework-level release notes | Automation Engineer (per a planned future Release Engineering chapter, not yet written) | **Currently empty** — a real gap, see [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md) | — | Not yet populated; not yet authoritative for anything | Planned, Batch 2+ |
| `.claude/`, `.agents/` | Tool-local configuration (Claude Code settings, agent scratch) | N/A — tool-managed, not framework governance | Tool settings | Framework governance content | Not authoritative for anything framework-related | Tool-managed |

### Adapter test isolation (verified)

`adapters/<name>/tests/` suites run in their own isolated `pytest` process
each, because duplicate module names across adapter packages prevent safe
same-process collection even though each suite is independently green
(documented in `PROJECT_TRACKER.md` Sprint 42). This is current, verified
behavior, not a proposal.

### Proposed structure (not yet implemented)

- **`docs/operator/_templates/`** — proposed in this Batch's Phase 4 (see
  [Template Framework](TEMPLATE_FRAMEWORK.md), planned) to hold the new
  reusable process templates (design proposal, implementation plan,
  investigation report, and others this Batch defines). Not yet created as
  of this document's writing within the same Batch; created later in the
  same continuous session — check `docs/operator/_templates/` directly for
  current contents rather than trusting this note once time has passed.
- **A `docs/operator/` index file** (e.g., a `README.md` mirroring
  `docs/specifications/README.md`'s registry pattern) is not currently
  planned as a separate file, because `MASTER_OPERATOR.md`'s own Table of
  Contents already serves that role — adding a second index would violate
  [Duplication, Staleness & Conflict Detection](DUPLICATION_AND_STALENESS_DETECTION.md)'s
  duplication rule. If `docs/operator/` ever grows large enough that this
  becomes unwieldy, see [Repository Evolution Strategy](DEPRECATION_ARCHIVAL_AND_EVOLUTION_STRATEGY.md).

## Examples

A session needs to record a new reusable fact about a validator diagnostic
edge case discovered while fixing a bug. Per this map: it does not belong in
`PROJECT_TRACKER.md` (that is actionable status, not reusable knowledge), it
is not domain knowledge for a Skill (`knowledge/` is for Skill-consumed
content, not framework-internal facts), and it is not architecturally
significant enough for an ADR. It belongs in the relevant
`docs/architecture/*.md` or `docs/guides/VALIDATION_GUIDE.md` as a
documented edge case, per [Knowledge Classification, Lifecycle & Capture](KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md).

## References

- `README.md`
- `adapters/README.md`
- `knowledge/README.md`
- ADR-0007, ADR-0008, ADR-0013
- [Documentation Placement Rules](DOCUMENTATION_PLACEMENT_RULES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 2) |
