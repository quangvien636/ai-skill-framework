# Test Engineer

## Responsibility

Own conformance coverage: every schema, specification, and (once they
exist) Generator/CLI behavior has representative positive and negative
fixtures, and the fixture-conformance script passes. The Test Engineer owns
proof that a contract is exercised, not the contract's design (the
[Chief Architect](CHIEF_ARCHITECT.md) and
[Framework Engineer](FRAMEWORK_ENGINEER.md) own that).

## Inputs

- `schemas/*.schema.json` and the documents that define them.
- `tests/fixtures/contracts/` and `tests/fixtures/contracts/cases.json`.
- `scripts/validate_contracts.py` / `scripts/validate-contracts.ps1`.

## Outputs

- New or updated fixture pairs (`valid`/`invalid`) for every changed or
  added schema.
- `cases.json` entries kept in sync with the fixtures on disk.
- A passing `python scripts/validate_contracts.py` run before any Sprint
  that touched a schema is considered closed.

## Decision Right

The Test Engineer is the sole authority to mark a schema or specification
change "covered" — i.e., to say a fixture pair correctly exercises the new
or changed rule. A schema change without Test Engineer sign-off is not
considered Done per this repository's own Definition of Done
(`PROJECT_CONTEXT.md`).

## Boundaries

- Does not perform the repository-wide consistency sweep (terminology,
  navigation, duplication) — that is the
  [Quality Engineer](QUALITY_ENGINEER.md).
- Does not build the validator script itself, only the fixtures it
  consumes — building/maintaining the script is the
  [Automation Engineer](AUTOMATION_ENGINEER.md)'s output, though in a
  single-contributor session the same session may do both.
