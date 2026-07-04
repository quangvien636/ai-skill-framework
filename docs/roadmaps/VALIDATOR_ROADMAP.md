# Contract Validator Roadmap

Version: 0.4
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

Status: **Done** (Sprint 16, `scripts/asf_validator/`, ADR-0009)

- Added typed IR adapters (`scripts/asf_validator/{skill,workflow,knowledge,
  evaluation,reflection}_ir.py`) that turn a schema-validated document (or,
  for Knowledge, a normalized Markdown document) into a strongly typed IR
  dataclass, per `docs/specifications/IR_SPECIFICATION.md`.
- Added a reusable pipeline (`scripts/asf_validator/pipeline.py`) with
  explicit stage separation: `loader.py` (file I/O only) ->
  `schema_registry.py` (Draft 2020-12 validation, factored out of Sprint
  8's script) -> per-kind adapter (typed IR) -> `diagnostics.py` (shared
  `Diagnostic` shape). No stage holds global/module-level mutable state.
- Added `scripts/build_ir.py` (16/16 fixture cases) and 30 `unittest`-based
  unit tests under `tests/unit/`, covering valid objects, missing required
  fields, unresolved within-document Workflow references, a dependency
  cycle, unsupported `schema_version` majors, and a Metadata id/name
  mismatch.
- Added a new `ASF-PARSE-*` diagnostic prefix (`CLI_ARCHITECTURE.md`) for
  failures at or before IR construction.

**Assumptions and documented gaps** (ADR-0009):

- Metadata and Version have no standalone file adapter — they are reusable
  functions (`extract_metadata_ir`, `parse_version`/`parse_version_range`)
  the Skill/Workflow adapters call, since no `metadata.yaml`/`version.yaml`
  file exists.
- The Workflow adapter resolves `depends_on`/`entrypoint`/mapping
  references and detects graph cycles **within one document only**; it
  does not resolve a Skill/Knowledge ID against the rest of the repository
  — that is the Dependency Graph, still Phase 3/4, not implemented.
- The Knowledge adapter requires all ten canonical sections and seven
  metadata bullets to be *present* to normalize at all; it does not check
  extracted values against the Knowledge Index or the file's own path
  (deeper "ID/taxonomy/path agreement" remains Phase 3).
- Diagnostic `location` values are field/section names (for example
  `steps.summarize.depends_on`, `## Sources`), not line/column source
  positions — precise source-position tracking through the YAML/Markdown
  parse is deferred; only the YAML loader's own malformed-syntax error
  reports a line number (from PyYAML itself).
- Version-range **satisfaction** (does version X satisfy range Y) is still
  not implemented; `parse_version_range` only parses and structures a
  range's comparators.

Exit: source artifacts normalize into IR without mutation or execution.

### Phase 3 - Semantic Validators

- Implement ID/path, weight sum, graph, mapping, routing, and version rules.
- Assign stable diagnostic codes (`ASF-SEMANTIC-*`, already reserved in
  `CLI_ARCHITECTURE.md`'s Diagnostics table).
- Add cross-rule tests.
- Build the Dependency Graph and Version Graph
  (`docs/specifications/IR_SPECIFICATION.md`) on top of the Phase 2
  adapters' IR objects; this is the natural next consumer of
  `scripts/asf_validator`.
- Implement version-range satisfaction (`parse_version_range`'s
  comparators currently structure a range but do not check whether a
  given version satisfies it).

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

The first implementation checkpoint validated a good Skill fixture and
rejected one missing `responsibility` (Phase 1); Phase 2 extended this to
building a typed `SkillIR` from that same fixture and rejecting one whose
`id` does not match its `name`. Neither phase generates or executes an
artifact.

## References

- [Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](../architecture/IR_ARCHITECTURE.md)
- [IR Specification](../specifications/IR_SPECIFICATION.md)
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Schema Registry](../../schemas/README.md)
- ADR-0002: Prototype Contract Validator
- ADR-0005: Markdown Authoring Format, IR Internal Contract
- ADR-0009: IR Adapter Package and Scope

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established phased validator implementation roadmap |
| 0.2 | 2026-07-04 | Closed Phase 1 with fixtures for all five standalone schemas |
| 0.3 | 2026-07-04 | Aligned Phase 2 terminology with the Sprint 11 IR adapter concept |
| 0.4 | 2026-07-04 | Closed Phase 2 with implemented IR adapters (Sprint 16, ADR-0009) |
