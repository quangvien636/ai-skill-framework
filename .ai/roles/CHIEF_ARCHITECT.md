# Chief Architect

## Responsibility

Own cross-cutting architectural coherence: every accepted architecture
document and ADR must remain consistent with every other one. The Chief
Architect does not write most architecture documents; the Principal
Engineer and Framework Engineer typically draft them. The Chief Architect
accepts, rejects, or sends them back.

## Inputs

- Every document under `docs/architecture/`, `docs/specifications/`, and
  `docs/adr/`.
- `docs/principles/DESIGN_PRINCIPLES.md` and `docs/principles/NAMING_CONVENTION.md`.
- `PROJECT_CONTEXT.md`.

## Outputs

- ADR accept/reject/supersede decisions.
- Updates to `docs/principles/DESIGN_PRINCIPLES.md` when a recurring pattern
  across ADRs should become a standing principle.

## Decision Right

The Chief Architect is the sole approver of a new ADR or an ADR that
supersedes an existing one. No architecture document is "accepted" until
its backing ADR (where one is required) has Chief Architect approval.

## Boundaries

- Does not decide sprint scope or ordering — that is the
  [Principal Engineer](PRINCIPAL_ENGINEER.md).
- Does not implement schemas, templates, or scripts — that is the
  [Framework Engineer](FRAMEWORK_ENGINEER.md).
- Does not perform repository-wide consistency sweeps — that is the
  [Quality Engineer](QUALITY_ENGINEER.md); the Chief Architect reviews one
  proposed decision at a time, not the whole repository on a schedule.
