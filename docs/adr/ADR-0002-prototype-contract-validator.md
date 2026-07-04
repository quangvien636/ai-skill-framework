# ADR-0002: Prototype Contract Validator Uses Python, jsonschema, and Fixture Manifests

- **Status:** Accepted
- **Date:** 2026-07-04
- **Decision owners:** Project maintainers

## Context

Sprint 7 defined the Contract Validation Architecture and seven Draft 2020-12
schemas but deliberately implemented no validator. The Validator Roadmap's
Phase 1 calls for conformance fixtures and a pinned Draft 2020-12
implementation before any semantic or repository validation logic is written.

The framework has no Runtime or CLI yet, so the first validator increment must
stay a small, offline, dependency-light script rather than a production tool.
It must prove that the schemas are structurally correct and that local `$ref`
resolution works, without pre-committing to a future CLI's language,
architecture, or distribution model.

## Decision

Sprint 8 adds a minimal, offline **prototype** validator:

- `scripts/validate_contracts.py` loads every `schemas/*.schema.json` file,
  validates each schema against the Draft 2020-12 meta-schema, builds a local
  `Registry` for `$ref` resolution, and checks a declared list of fixtures.
- `tests/fixtures/contracts/cases.json` is a fixture manifest: each case names
  a fixture file, the schema to validate against, and the expected
  `valid`/`invalid` outcome. Positive and negative fixtures exist for the
  Skill, Workflow, and Knowledge contracts (`tests/fixtures/contracts/<type>/`).
- `requirements-validator.txt` pins `jsonschema` and `PyYAML`; the script also
  depends on the `referencing` library for registry-based `$ref` resolution.
- `scripts/validate-contracts.ps1` is a thin Windows entry point that invokes
  the Python script and surfaces its exit code; it contains no validation
  logic of its own.

This is Phase 1 of the Validator Roadmap only. The script does not implement
semantic validation (Skill/Workflow/Knowledge business rules), repository
validation (ID uniqueness, references, Knowledge Index membership), a CLI, or
a Runtime. It never mutates source artifacts and performs no network access.

## Consequences

### Positive

- The schemas are now exercised by real conformance cases instead of manual
  review, catching schema regressions immediately (`python scripts/validate_contracts.py`).
- The pinned `jsonschema`/`referencing` stack resolves local `$ref` values the
  same way the future validator core will need to, retiring Phase 1 risk
  before Phase 2 (parser/normalization adapters) begins.
- The fixture manifest format (`cases.json`) is reusable: new artifact types
  or schema changes only require new fixture files and a manifest entry, not
  script changes.
- Keeping the script single-file and dependency-light avoids prematurely
  committing to the CLI architecture that Milestone 9 will design separately.

### Costs and Tradeoffs

- The prototype only validates fixtures named in `cases.json`; it is not yet
  wired to walk `skills/` or `workflows/` directories, so it does not replace
  manual repository review described in the Validation Guide.
- `referencing` is an additional dependency beyond `jsonschema` and `PyYAML`;
  it is required for spec-compliant Draft 2020-12 `$ref` resolution and is
  pinned in `requirements-validator.txt`.
- The script and its fixtures are prototype-quality: they intentionally have
  no CLI ergonomics, no JSON diagnostic output, and no repository-wide scan,
  matching the roadmap's "thin interfaces last" sequencing.

## Enforcement

Contributors who add or change a schema must add or update a matching fixture
pair (`valid` and `invalid`) under `tests/fixtures/contracts/<type>/` and a
`cases.json` entry, then run `python scripts/validate_contracts.py`
(or `scripts/validate-contracts.ps1` on Windows) before committing.

## Alternatives Considered

### Defer any validator code until the CLI architecture (Milestone 9) is designed

Rejected because Phase 1 of the Validator Roadmap explicitly calls for
conformance fixtures and a pinned schema implementation first, independent of
any future CLI shape, and because untested schemas are a growing risk the
longer they go unexercised.

### Implement semantic and repository validation now

Rejected because the Validator Roadmap sequences semantic rules (Phase 3) and
repository integrity (Phase 4) after fixtures and adapters, and because
combining them now would couple schema conformance testing to rules that are
still likely to change.

### Use a non-Python implementation

Rejected for the prototype because `jsonschema` is a mature, spec-compliant
Draft 2020-12 implementation and Python keeps the fixture checker consistent
with the repository's existing PowerShell/Python scripting split in
`scripts/`. The future validator core's language remains an open Milestone 9
decision, not fixed by this ADR.

## Related Documents

- `docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md`
- `docs/roadmaps/VALIDATOR_ROADMAP.md`
- `docs/guides/VALIDATION_GUIDE.md`
- `schemas/README.md`
- ADR-0001
