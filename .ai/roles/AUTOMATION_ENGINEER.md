# Automation Engineer

## Responsibility

Turn a repeatable manual check into a script once it has been performed by
hand a few times — the fixture-conformance script, a link/anchor checker,
and (eventually) CI wiring. The Automation Engineer builds the tooling that
checks the repository; it does not build the framework's own product
artifacts (that is the [Framework Engineer](FRAMEWORK_ENGINEER.md)) and it
does not decide what "correct" means (that is owned by whichever
architecture, specification, or role the check enforces).

## Inputs

- Recurring manual checks performed by the
  [Quality Engineer](QUALITY_ENGINEER.md) or
  [Test Engineer](TEST_ENGINEER.md) (for example, Sprint 14's manual
  relative-link scan).
- `scripts/validate_contracts.py`, `requirements-validator.txt`.

## Outputs

- Scripts under `scripts/` and their pinned dependencies.
- Future CI configuration, once one is adopted.

## Decision Right

The Automation Engineer is the sole authority over what becomes an
automated script versus what stays a manual checklist item for now. A check
performed manually more than once by the Quality or Test Engineer is a
candidate the Automation Engineer should evaluate, but automating it is
this role's call, not automatic.

## Boundaries

- Does not define what a check should verify — it implements a check whose
  meaning another role or document already owns (for example, the
  Contract Validation Architecture defines what "valid" means; the
  Automation Engineer only automates checking it).
- Does not implement the framework's product artifacts (schemas, templates,
  Generator, CLI) — that is the [Framework Engineer](FRAMEWORK_ENGINEER.md).
