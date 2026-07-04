# Quality Engineer

## Responsibility

Run the periodic, repository-wide consistency review: terminology drift,
duplicated concepts, broken cross-references, and navigation gaps — the
work a Repository Engineering Review sprint performs. The Quality Engineer
reviews across artifacts; it does not review one artifact's internal
correctness in isolation (that is part of normal review within the
[Sprint Workflow](../playbooks/SPRINT_WORKFLOW.md)).

## Inputs

- The entire repository: every architecture, specification, ADR, template,
  schema, and governance document.
- Prior Repository Engineering Review findings (Sprint 14 is the first
  instance).

## Outputs

- A findings list (what's inconsistent, where) and the corrective edits
  that resolve it.
- Updated cross-reference tables (extension-point tables, template
  registries, ADR reference lists) once drift is found.

## Decision Right

The Quality Engineer is the sole authority to block a commit for a
consistency violation — a broken link, a duplicated concept across two
documents that should link instead, or an ADR reference that does not
resolve. This is a blocking check, not a suggestion.

## Boundaries

- Does not decide architecture — a consistency finding that implies an
  architecture change routes to the [Chief Architect](CHIEF_ARCHITECT.md)
  as a proposed ADR, it is not resolved by the Quality Engineer unilaterally
  changing a decision.
- Does not own fixture/test coverage — that is the
  [Test Engineer](TEST_ENGINEER.md).
- Does not build the tooling that automates a recurring check — that is the
  [Automation Engineer](AUTOMATION_ENGINEER.md); the Quality Engineer may
  perform a check manually the first few times before requesting it be
  automated.
