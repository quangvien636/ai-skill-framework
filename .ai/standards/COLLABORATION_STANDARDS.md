# Collaboration Standards

How the roles in `.ai/roles/` interact, escalate disagreements, and share
ownership of the repository's governing documents.

## Interaction Rules

- A role acts within its Decision Right (defined in its own document) and
  does not silently override another role's decision. A disagreement
  routes upward: an implementation disagreement escalates to the
  [Framework Engineer](../roles/FRAMEWORK_ENGINEER.md) and
  [Chief Architect](../roles/CHIEF_ARCHITECT.md); a scope disagreement
  escalates to the [Principal Engineer](../roles/PRINCIPAL_ENGINEER.md).
- A single contributor (human or AI) MAY act as more than one role in the
  same session — this repository has, in practice, been developed by one
  AI contributor acting as Principal Engineer, Framework Engineer, Test
  Engineer, and Quality Engineer across sprints. Holding multiple roles
  does not merge their Decision Rights into one undifferentiated authority;
  each decision still belongs to the role it falls under, and should be
  identifiable as such (for example, an ADR is a Chief Architect decision
  even if the same session drafted it as Framework Engineer).
- No role's Decision Right overrides ADR-0001, which establishes both that
  the repository is the source of truth and that AI models are
  contributors, not owners — see `governance/DECISION_RIGHTS.md`.

## ADR Ownership

- Any role may draft an ADR candidate.
- Only the [Chief Architect](../roles/CHIEF_ARCHITECT.md) accepts,
  supersedes, or rejects one.
- An accepted ADR is immutable; a change in direction is a new ADR that
  supersedes it, per the Version Specification's treatment of ADRs as
  non-versioned, superseded-not-edited records.

## Tracker Ownership

- Only the [Principal Engineer](../roles/PRINCIPAL_ENGINEER.md) opens or
  closes a Current Sprint entry in `PROJECT_TRACKER.md`.
- Any role may propose a Next Action; the Principal Engineer decides which
  become the next Sprint's goal.

## Review Gates

A change is not ready to commit until:

- the [Quality Engineer](../roles/QUALITY_ENGINEER.md) gate (no
  duplication, no broken reference, terminology consistent) passes;
- the [Test Engineer](../roles/TEST_ENGINEER.md) gate (coverage exists for
  any schema/spec change) passes, where applicable;
- the [Chief Architect](../roles/CHIEF_ARCHITECT.md) gate (no contradiction
  with an accepted ADR or principle) passes.

These gates are sequential in spirit but may be checked together in a
single-contributor session, as this repository's sprints have done.
