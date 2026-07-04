# Contract Validator Roadmap

Version: 0.1
Status: Planned
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
- **Adapter:** parser/normalizer for one source format.

## Design

### Phase 1 - Conformance Fixtures

- Add positive and negative fixtures for every schema.
- Select and pin a Draft 2020-12 implementation.
- Test local `$ref` resolution and expected diagnostic paths.

Exit: each schema has representative automated conformance cases.

### Phase 2 - Parser and Normalization Adapters

- Add safe YAML adapters for Skill and Workflow manifests.
- Add a deterministic Knowledge Markdown adapter.
- Preserve source locations for diagnostics.

Exit: source artifacts normalize without mutation or execution.

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
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Schema Registry](../../schemas/README.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established phased validator implementation roadmap |
