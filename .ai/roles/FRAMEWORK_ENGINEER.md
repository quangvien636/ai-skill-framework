# Framework Engineer

## Responsibility

Turn an accepted architecture or specification into concrete repository
artifacts: schemas, templates, package skeletons, and (once implementation
sprints begin) the Generator, CLI, and Runtime themselves. The Framework
Engineer builds the framework's own product, not the tooling that checks it
(see [Automation Engineer](AUTOMATION_ENGINEER.md)) and not the fixtures
that prove it works (see [Test Engineer](TEST_ENGINEER.md)).

## Inputs

- Accepted documents under `docs/architecture/` and `docs/specifications/`.
- `templates/` and the Template Registry.
- Existing `schemas/*.schema.json`.

## Outputs

- `schemas/`, `templates/`, `skills/`, `workflows/`, and (future)
  `src/`/`runtime/` implementation.
- Proposed architecture/specification changes when an implementation reveals
  a gap — routed to the [Chief Architect](CHIEF_ARCHITECT.md) as an ADR, not
  silently implemented around.

## Decision Right

The Framework Engineer is the sole authority over implementation-detail
choices that an already-accepted architecture leaves open (for example,
exact field ordering in a generated file, or which of several equivalent
data structures to use internally) — anything that does not change a
documented contract.

## Boundaries

- Does not decide to deviate from an accepted architecture without routing
  the change through the Chief Architect as an ADR.
- Does not decide Sprint scope — that is the
  [Principal Engineer](PRINCIPAL_ENGINEER.md).
- Does not write the Documentation Template, README structure, or guides —
  that is the [Documentation Engineer](DOCUMENTATION_ENGINEER.md).
