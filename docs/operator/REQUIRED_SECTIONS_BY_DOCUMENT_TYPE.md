# Required Sections by Document Type

Version: 0.1
Status: Active
Last updated: 2026-07-12

## Purpose

Define the required sections for each document type this repository (and
this manual) produces, scaled so small documents are not forced into
oversized boilerplate.

## Scope

Extends `docs/_templates/DOCUMENTATION_TEMPLATE.md` (the existing generic
shape: Purpose, Scope, Definitions, Design, Examples, References, Revision
History) and `docs/adr/ADR_TEMPLATE.md` with type-specific variants.

## Design

### Generic document (existing, unchanged)

Purpose, Scope, Definitions, Design, Examples, References, Revision
History — per `docs/_templates/DOCUMENTATION_TEMPLATE.md`. This is the
default for every `docs/architecture/`, `docs/guides/`, `docs/principles/`,
and `docs/operator/` document, including every chapter this Batch wrote.

### ADR (existing, unchanged)

Status, Date, Decision owners, Context, Decision, Consequences
(Positive/Costs and Tradeoffs), Enforcement, Alternatives Considered,
Related Documents — per `docs/adr/ADR_TEMPLATE.md`.

### Technical specification

Purpose, Scope, Non-goals, Current behavior, Proposed behavior (if
applicable), Contracts, Failure modes, Validation, Migration (if
applicable), Open questions, Related decisions. This is the
`docs/_templates/DOCUMENTATION_TEMPLATE.md` shape with "Design" split into
Current/Proposed behavior and Contracts/Failure modes made explicit,
matching how `docs/specifications/*.md` already reads in practice even
though no separate template file exists for it today — this Batch does not
create a new template file for this type, since the existing specifications
already demonstrate the shape consistently; a future session may extract
one if divergence is observed.

### Runbook

Purpose, Prerequisites, Safety (what could go wrong, what to check first),
exact Procedure (numbered, executable steps), Expected outputs, Failure
handling, Rollback, Escalation, Last verified date. `docs/guides/*.md`
already approximates this; new guides should follow it explicitly.

### Investigation report

Question, Evidence, Method, Findings, Conclusions, Limitations, Next
action. See [Template Framework](TEMPLATE_FRAMEWORK.md) for the fillable
template.

### Validation report

Repository and branch, HEAD before/after, Commands run, Environment,
Results, Pass/fail counts, Skipped checks, Known warnings, Limitations,
Artifacts, Conclusion. See
[Template Framework](TEMPLATE_FRAMEWORK.md) and
[Documentation Review Workflow & Quality Gates](DOCUMENTATION_REVIEW_AND_QUALITY_GATES.md)'s
Validation Report Standard.

### Incident report

What happened, When detected, Impact, Root cause (if known), Immediate
response taken, Resolution, Prevention (follow-up action), Timeline. See
[Template Framework](TEMPLATE_FRAMEWORK.md).

### Recovery report

Which [Recovery Procedures](RECOVERY_PROCEDURES.md) situation applied,
Detection, What was preserved, What was inspected, Recovery action taken,
Validation after recovery, Any escalation.

### Retrospective

What was the goal, What went well, What did not, What would be done
differently, Concrete follow-up actions (each routed to a
`PROJECT_TRACKER.md` Next Action if it survives the promotion threshold in
[Knowledge Classification, Lifecycle & Capture](KNOWLEDGE_CLASSIFICATION_AND_LIFECYCLE.md)).

### Knowledge capture / lessons learned

The finding, Evidence, Class (per Knowledge Classification), Recurrence
risk / impact / generality (the promotion-threshold factors), Where it was
promoted to (if it was).

### Roadmap item

Title, Description, Depends on, Blocks, Priority tier (per
[Priority & Autonomous Planning Engine](PRIORITY_AND_PLANNING_ENGINE.md)),
Status.

### Blocker report

Class (per [Blocker Classification & Escalation](BLOCKER_CLASSIFICATION_AND_ESCALATION.md)),
Evidence, Workarounds considered, Resume trigger, Escalation path taken.

### Session handoff

Per [Multi-Session Continuity, Handover & Completion Checklist](MULTI_SESSION_CONTINUITY_AND_HANDOVER.md)'s
Handover Report shape: completed milestones with commit hashes, files
changed, new/proposed ADRs, remaining backlog, any stop condition hit, a
recommended next task.

### Release-readiness review

Not currently applicable — this repository has no release process in scope
(see [Human vs AI Responsibilities & Change Classification](HUMAN_AI_RESPONSIBILITIES_AND_CHANGE_CLASSIFICATION.md)'s
Release change row). The template exists (see
[Template Framework](TEMPLATE_FRAMEWORK.md)) so a future Batch's Release
Engineering chapter has a ready-made shape, but it has no current subject
to review.

### Scaling requirements so small documents are not bloated

A document needs only the sections its content actually has something to
say under. A one-paragraph correction to an existing document does not
need its own Purpose/Scope/Definitions frame — it is an edit to the
existing document's own sections, not a new document. The type-specific
shapes above apply only when creating a genuinely new document of that
type; see [Future Document Creation Rules](DOCUMENT_CREATION_RULES.md) for
when that is warranted at all.

## Examples

This document itself is a Generic document (this manual's own type),
following the standard seven-section shape, while its *content* documents
the shapes for nine other types — demonstrating the difference between "the
shape this document follows" and "the shapes this document is about."

## References

- `docs/_templates/DOCUMENTATION_TEMPLATE.md`
- `docs/adr/ADR_TEMPLATE.md`
- [Template Framework](TEMPLATE_FRAMEWORK.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-12 | Initial version (Batch 1, Phase 4) |
