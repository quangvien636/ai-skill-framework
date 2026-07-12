# Template Framework

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Index the reusable process templates this Batch introduces under
`docs/operator/_templates/`, alongside the existing templates this
repository already has, so a session never has to invent a document
structure from scratch.

## Scope

Covers where each template lives, when to use it, and how it relates to
existing templates (`docs/_templates/DOCUMENTATION_TEMPLATE.md`,
`docs/adr/ADR_TEMPLATE.md`, `knowledge/_templates/KNOWLEDGE_TEMPLATE.md`,
`templates/skill/`, `templates/workflow/`) — this chapter references those,
it does not duplicate them.

## Design

### Existing templates (unchanged, referenced not duplicated)

| Template | Location | Use for |
| --- | --- | --- |
| Generic document | `docs/_templates/DOCUMENTATION_TEMPLATE.md` | Any architecture doc, guide, principle, or `docs/operator/*.md` chapter |
| ADR | `docs/adr/ADR_TEMPLATE.md` | Any Architecture Decision Record |
| Knowledge document | `knowledge/_templates/KNOWLEDGE_TEMPLATE.md` | Any `knowledge/` domain content |
| Skill package | `templates/skill/` | Any new Skill |
| Workflow package | `templates/workflow/` | Any new Workflow |

### New templates this Batch introduces (`docs/operator/_templates/`)

| Template | File | Use for |
| --- | --- | --- |
| Design proposal | `docs/operator/_templates/DESIGN_PROPOSAL_TEMPLATE.md` | A Level 3 change too small for a full ADR but too consequential for a lightweight mental plan — e.g., a new validator rule's design before implementation |
| Implementation plan | `docs/operator/_templates/IMPLEMENTATION_PLAN_TEMPLATE.md` | The written form of the Planning Contract (see [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md)) when a task exceeds the lightweight-plan threshold |
| Investigation report | `docs/operator/_templates/INVESTIGATION_REPORT_TEMPLATE.md` | Recording the evidence and conclusion of a bounded exploration (an Experiment result, per [Knowledge Classification, Lifecycle & Capture](KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md)) |
| Validation report | `docs/operator/_templates/VALIDATION_REPORT_TEMPLATE.md` | Recording what was run and what passed/failed, per [Documentation Review Workflow & Quality Gates](DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md)'s Validation Report Standard |
| Incident report | `docs/operator/_templates/INCIDENT_REPORT_TEMPLATE.md` | A Security or Hard Stop class event (see [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)) |
| Recovery report | `docs/operator/_templates/RECOVERY_REPORT_TEMPLATE.md` | Documenting a [Recovery Procedures](RECOVERY_PROCEDURES.md) execution |
| Retrospective | `docs/operator/_templates/RETROSPECTIVE_TEMPLATE.md` | End of a Batch or major milestone |
| Knowledge capture | `docs/operator/_templates/KNOWLEDGE_CAPTURE_TEMPLATE.md` | Promoting a Reusable lesson per [Knowledge Classification, Lifecycle & Capture](KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md) |
| Roadmap item | `docs/operator/_templates/ROADMAP_ITEM_TEMPLATE.md` | Proposing a new `PROJECT_TRACKER.md` Next Action or roadmap entry |
| Blocker report | `docs/operator/_templates/BLOCKER_REPORT_TEMPLATE.md` | Any blocker per [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md) |
| Session handoff | `docs/operator/_templates/SESSION_HANDOFF_TEMPLATE.md` | End of any session, per [Multi-Session Continuity, Handover & Completion Checklist](MULTI_SESSION_CONTINUITY_AND_HANDOVER.md) |
| Release-readiness review | `docs/operator/_templates/RELEASE_READINESS_REVIEW_TEMPLATE.md` | Not yet applicable in this repository's current scope; reserved for a future Release Engineering chapter |

### Why a new `_templates/` directory rather than extending an existing one

This mirrors the repository's own established pattern of a `_templates/`
subdirectory colocated with the category it serves
(`docs/_templates/`, `knowledge/_templates/`, `templates/skill/`,
`templates/workflow/`) rather than a single shared template directory. The
new templates are all *operator-process* documents (reports, plans,
handoffs) distinct from architecture/guide documents
(`docs/_templates/DOCUMENTATION_TEMPLATE.md`'s domain) and from Skill/
Workflow/Knowledge artifacts — they get their own colocated directory for
the same reason those other categories already have theirs.

### Template completion standard

Every template below contains instructions in `<angle brackets>`, matching
`docs/_templates/DOCUMENTATION_TEMPLATE.md`'s existing convention. A filled
template MUST replace every bracketed instruction with real content or
explicitly state "N/A" with a one-clause reason — a template section left
as unfilled boilerplate is a Documentation Quality Gate failure (see
[Documentation Review Workflow & Quality Gates](DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md)).

## Examples

A session investigating why an adapter test intermittently fails would: (1)
use the Investigation Report template to record evidence and method while
exploring, (2) if the root cause reveals a real defect, fix it and add a
regression test per [Autonomous Development Lifecycle](AUTONOMOUS_DEVELOPMENT_LIFECYCLE.md),
(3) use the Knowledge Capture template only if the finding scores high
enough on the promotion threshold to warrant a permanent record beyond the
regression test and commit message itself.

## References

- `docs/_templates/DOCUMENTATION_TEMPLATE.md`
- `docs/adr/ADR_TEMPLATE.md`
- [Required Sections by Document Type](REQUIRED_SECTIONS_BY_DOCUMENT_TYPE.md)
- [Documentation Review Workflow & Quality Gates](DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 4) |
