# Contract Validator Roadmap

Version: 0.7
Status: In Progress
Last updated: 2026-07-05

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

Status: **In Progress** — Dependency/Version Graph construction was completed
in Sprint 17; IR-level metric, routing, mapping, type, and topology rules were
completed in Sprint 21. Canonical ID/taxonomy/path agreement remains coupled to
Phase 4 discovery.

**Done (Sprint 17):**

- Built the Dependency Graph (`dependency_graph.py`): nodes from every
  loaded Skill/Workflow/Knowledge IR, edges for Skill -> Knowledge,
  Workflow step -> Skill, and Knowledge -> Knowledge (`related_knowledge`),
  per `docs/specifications/IR_SPECIFICATION.md`'s node/edge shape.
- Built the Version Graph (`version_graph.py`) on top of the Dependency
  Graph: version-range satisfaction (`version_satisfies_range`, added to
  `version_ir.py`), self-contradictory ranges, ambiguous version
  references, and deprecated/archived dependency detection.
- Factored cycle detection into a shared `graph.py` utility, reused by both
  the Dependency Graph and the Sprint 16 Workflow IR adapter (no duplicated
  cycle-detection logic).
- Added the `ASF-GRAPH-*` diagnostic prefix (`CLI_ARCHITECTURE.md`) for
  cross-artifact, graph-stage diagnostics, distinct from `ASF-PARSE-*`.
- Added `scripts/build_graph.py` (10/10 multi-artifact fixture scenarios)
  and 23 new `unittest` unit tests (53 total across all phases).

**Assumptions and documented gaps** (ADR-0010):

- Evaluation and Reflection are **not** Dependency/Version Graph nodes —
  they have no `id` and are embedded fields of a Skill's IR, not
  independent artifacts. Their graph edges "if specified" in an earlier
  sprint's brief are not specified anywhere, so they are not built.
- Skill `dependencies.runtime`/`.tools` references exist on the IR but are
  **not** Dependency Graph edges, since no Runtime/Tool IR adapter exists
  yet (`runtime/` is an empty placeholder; `tool` is not a defined artifact
  kind).
- Version comparison uses `(major, minor, patch)` only; SemVer 2.0.0
  pre-release precedence is not implemented (no current fixture or
  repository artifact uses a pre-release version).
- `range_is_self_contradictory` is a coarse check: it catches a lower bound
  exceeding an upper bound (`>=2.0.0 <1.0.0`) but not a range that excludes
  every version by squeezing between two adjacent versions with no integer
  triple between them (`>1.0.0 <1.0.1`).

**Done (Sprint 21):**

- Added `semantic_validator.py`, operating only on successful typed IR results.
- Added stable `ASF-SEMANTIC-001` through `ASF-SEMANTIC-009` diagnostics for
  duplicate Evaluation metric names, invalid weight totals,
  Evaluation/Reflection routing, unknown reflectable hard gates, Workflow
  mapping targets/sources/types, retry routing, and unreachable steps.
- Added `scripts/build_semantics.py` with three conformance scenarios and unit
  coverage. The validator does not rediscover graph relationships or mutate IR.

**Remaining:**

- Implement Skill and Knowledge ID/taxonomy/path agreement using canonical
  filesystem context from Phase 4 Repository Discovery.
- Keep one-responsibility assessment as human review until an objective,
  deterministic rule is specified.

Exit: all rules in Contract Validation Architecture are executable.

### Phase 4 - Repository Integrity

Status: **In Progress** — deterministic Workspace/Project Discovery, canonical
path checks, package requirements, Knowledge Index agreement, and
case-insensitive path collision checks completed in Sprint 22.

- Resolve local artifact references and lifecycle using the Sprint 17
  Dependency Graph as the underlying structure, extended with real
  filesystem discovery (Project Discovery, `CLI_ARCHITECTURE.md`) instead
  of an explicit fixture list.
- Validate Knowledge Index and package structure.
- Check case collisions, links, and duplicate IDs (duplicate-ID detection
  already exists at the fixture-set level in `dependency_graph.py`; Phase 4
  extends it to a full repository scan).

**Done (Sprint 22):**

- Implemented ADR-0007 Workspace Discovery and lazy Project Discovery for
  Skills, Workflows, Knowledge, embedded Evaluation/Reflection locations, and
  examples.
- Added an immutable deterministic `ProjectIndex` suitable for reuse by the
  future Runtime.
- Added canonical identity/path, package-file, Knowledge Index, and
  case-insensitive collision diagnostics (`ASF-REPOSITORY-001..005`).
- Added `validate_repository.py`, which composes all implemented validation
  layers across the real repository (42 locations, 24 loaded artifacts).

**Remaining:**

- Automate Markdown link/anchor and secret checks.
- Define any additional lifecycle/orphan policy before enforcing it.
- Add one stable machine-readable Reporter when thin interfaces begin.

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
`id` does not match its `name` (Phase 2); Phase 3's graph work connects a
Skill and a Knowledge document loaded together, detects that the Skill
requires a Knowledge version range no loaded version satisfies, and reports
`ASF-GRAPH-004` without generating or executing anything.

## References

- [Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](../architecture/IR_ARCHITECTURE.md)
- [IR Specification](../specifications/IR_SPECIFICATION.md)
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Schema Registry](../../schemas/README.md)
- ADR-0002: Prototype Contract Validator
- ADR-0005: Markdown Authoring Format, IR Internal Contract
- ADR-0009: IR Adapter Package and Scope
- ADR-0010: Dependency and Version Graph Scope

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established phased validator implementation roadmap |
| 0.2 | 2026-07-04 | Closed Phase 1 with fixtures for all five standalone schemas |
| 0.3 | 2026-07-04 | Aligned Phase 2 terminology with the Sprint 11 IR adapter concept |
| 0.4 | 2026-07-04 | Closed Phase 2 with implemented IR adapters (Sprint 16, ADR-0009) |
| 0.5 | 2026-07-04 | Phase 3 Dependency/Version Graph construction done (Sprint 17, ADR-0010); ID/path, weight-sum, mapping, routing rules remain |
| 0.6 | 2026-07-05 | Added Sprint 21 IR-level semantic rules; canonical path agreement remains with discovery |
| 0.7 | 2026-07-05 | Added Sprint 22 Workspace/Project Discovery and initial repository integrity validation |
