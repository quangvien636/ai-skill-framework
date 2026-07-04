# Contract Validator Roadmap

Version: 0.3
Status: In Progress
Last updated: 2026-07-04

## Purpose

Sequence validator implementation without prematurely building a full CLI or
Runtime.

## Scope

This roadmap covers validation tooling after Sprint 7. Dates and implementation
language are intentionally undecided.

## Definitions

- **Core:** tool-neutral validation library.
- **Fixture:** valid or invalid artifact with expected diagnostics.
- **IR adapter:** parser/normalizer for one source format, producing the
  [Intermediate Representation](../architecture/IR_ARCHITECTURE.md) shared
  by the Validator, Generator, CLI, and future Runtime (see ADR-0005).

## Design

### Phase 1 - Conformance Fixtures

Status: **Done** (Sprint 8, `scripts/validate_contracts.py`, ADR-0002)

- Added positive and negative fixtures for the Skill, Workflow, Knowledge,
  Evaluation, and Reflection schemas under `tests/fixtures/contracts/`.
- Pinned `jsonschema` and `referencing` (via `requirements-validator.txt`) as
  the Draft 2020-12 implementation.
- Verified local `$ref` resolution through a schema `Registry` and expected
  diagnostic paths for each negative fixture (10/10 cases pass).

Metadata and Version have no standalone fixtures because they are shared
`$defs` consumed through the other five schemas' fixtures, not standalone
repository artifacts (see the Validation Guide's Schema Selection table).

Exit: each schema has representative automated conformance cases.

### Phase 2 - IR Adapters (Parser and Normalization)

- Add safe YAML IR adapters for Skill and Workflow manifests.
- Add a deterministic Knowledge Markdown IR adapter.
- Preserve source locations for diagnostics, per the
  [IR Architecture](../architecture/IR_ARCHITECTURE.md)'s Parser and
  Normalization Strategy.

Exit: source artifacts normalize into IR without mutation or execution.

### Phase 3 - Semantic Validators

- Implement ID/path, weight sum, graph, mapping, routing, and version rules.
- Assign stable diagnostic codes.
- Add cross-rule tests.

Exit: all rules in Contract Validation Architecture are executable.

### Phase 4 - Repository Integrity

- Resolve local artifact references and lifecycle.
- Validate Knowledge Index and package structure.
- Check case collisions, links, and duplicate IDs.

Exit: repository-wide validation is deterministic and offline.

### Phase 5 - Thin Interfaces

- Expose a library API first.
- Add a minimal CLI wrapper and machine-readable report only after core stability.
- Consider editor and CI integrations without duplicating validation logic.

Exit: interfaces delegate to one tested core.

## Examples

The first implementation checkpoint should validate a good Skill fixture and
reject one missing `responsibility`; it should not generate or execute either.

## References

- [Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](../architecture/IR_ARCHITECTURE.md)
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Schema Registry](../../schemas/README.md)
- ADR-0002: Prototype Contract Validator
- ADR-0005: Markdown Authoring Format, IR Internal Contract

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established phased validator implementation roadmap |
| 0.2 | 2026-07-04 | Closed Phase 1 with fixtures for all five standalone schemas |
| 0.3 | 2026-07-04 | Aligned Phase 2 terminology with the Sprint 11 IR adapter concept |
