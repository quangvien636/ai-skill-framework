# Intermediate Representation (IR) Architecture

Version: 0.2
Status: Active

Last updated: 2026-07-04

## Purpose

Define one model-neutral internal representation that the Validator,
Generator, CLI, and future Runtime all consume, so none of them parses
Markdown or YAML directly. This names and generalizes a concept the
Contract Validation Architecture already used only for validation (the
"normalized model") into a cross-cutting internal contract.

## Scope

This architecture defines the IR's pipeline position, lifecycle,
serialization strategy, and parser/normalization strategy. The
[IR Specification](../specifications/IR_SPECIFICATION.md) defines the
object model itself (Skill IR, Workflow IR, Knowledge IR, Metadata IR,
Reference IR, Dependency Graph, Version Graph). This architecture does not
implement a Generator, CLI, or Runtime, and it does not change what
"valid" means — the [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)
remains authoritative for validation layers and diagnostics.

Sprint 16 (Validator Roadmap Phase 2) implements the Skill, Workflow,
Knowledge, Evaluation, and Reflection IR adapters this architecture
describes, in `scripts/asf_validator/`. The Dependency Graph and Version
Graph remain specification-only; no CLI or Generator consumes the IR yet.
See ADR-0009 and `docs/roadmaps/VALIDATOR_ROADMAP.md`.

## Definitions

- **IR (Intermediate Representation):** a tool-neutral, in-memory object
  produced from one artifact's authoring-format source, conforming to the
  IR Specification's object model.
- **Source:** the durable, human-authored, Git-tracked artifact (a
  `skill.yaml`, `workflow.yaml`, or Knowledge Markdown document).
- **Parser:** reads one source format into a raw parsed document (YAML node
  tree or Markdown AST), performing no framework-specific interpretation.
- **Normalizer:** maps a raw parsed document onto the IR object model for
  its artifact type.
- **IR adapter:** the parser+normalizer pair for one source format; the
  extension point plugins implement (see [CLI Architecture](CLI_ARCHITECTURE.md)).
- **Consumer:** the Validator, Generator, CLI, or Runtime component that
  reads IR to do its work.

## Design

### Pipeline Position

```text
Markdown / YAML (source, Git-tracked)
  -> Parser            (format-specific, no interpretation)
  -> Normalizer         (maps onto the IR object model)
  -> Intermediate Representation (in-memory, transient)
  -> Generator | Validator | CLI | Runtime
```

Every consumer sits downstream of the IR, never upstream of it. A Generator
MUST NOT read `skill.yaml` or Knowledge Markdown directly to make decisions;
it reads the IR the same adapter produced for the Validator. This is what
keeps Generator, Validator, CLI, and Runtime behaviorally consistent: they
disagree only if the shared IR is wrong, not because each parses source
differently.

### IR Lifecycle

```text
Source -> Parsed -> Normalized (IR) -> Validated -> Consumed -> Discarded
```

IR is rebuilt from source on every invocation that needs it and is never
itself the source of truth (per ADR-0001): it is discarded after use, exactly
as `knowledge.schema.json`'s normalized model already is for Knowledge
documents. A Skill or Workflow's YAML manifest is parsed directly into a
document that already matches its IR shape (see IR Specification); a
Knowledge Markdown document requires the two-stage Markdown-to-IR transform
the Contract Validation Architecture's Source Adapters section describes.
Either way, the IR itself is never committed, versioned, or treated as an
artifact in its own right.

### Serialization Strategy

IR is an in-memory object by default. A consumer MAY serialize IR to JSON
to hand it from one process to another (for example, a future CLI parsing
once and invoking a separate Generator process) or to cache it for a single
build. A serialized IR:

- MUST be reproducible byte-for-byte from source plus the adapter version
  that produced it (no hidden non-determinism);
- MUST NOT be committed to the repository or treated as authoritative —
  it is a disposable build artifact, not a new source of truth;
- MUST be invalidated and rebuilt whenever its source file or adapter
  version changes.

### Validation Strategy

The IR Architecture does not redefine validation. Structural validation is
JSON Schema applied to IR — the existing `schemas/*.schema.json` files are
already schemas for the IR object model, not merely for parsed YAML.
Semantic and repository-integrity validation, diagnostics shape, and
severity all remain owned by the
[Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md).
The only change this document makes is vocabulary: what that architecture
called the "normalized model" is the IR.

### Parser Strategy

A parser is format-specific and produces a raw parsed document with no
framework interpretation: a YAML node tree for `skill.yaml`/`workflow.yaml`,
or a Markdown AST (headings, lists, tables) for a Knowledge document.
Parsers:

- MUST disable unsafe format features (no arbitrary YAML tags, no Markdown
  script execution);
- MUST NOT resolve remote references or perform network access;
- MUST preserve source location (line/column or heading path) so downstream
  diagnostics can cite exact source positions;
- MUST NOT mutate the source file.

### Normalization Strategy

A normalizer maps a raw parsed document onto one artifact type's IR shape:

- The **YAML normalizer** for Skill and Workflow is close to an identity
  transform, because `skill.yaml`/`workflow.yaml` are already authored in
  the IR's shape; normalization mainly fills declared defaults (for
  example `tags: []`) and rejects unknown top-level keys.
- The **Markdown normalizer** for Knowledge extracts canonical headings,
  metadata fields, lists, and revision-history rows into the structured
  object `knowledge.schema.json` validates, per the Contract Validation
  Architecture's Source Adapters section. This is a real transform, not an
  identity mapping, because Markdown prose is not already field-shaped.

Both normalizers attach enough source-location metadata that a Validator or
Generator diagnostic can point at the authored file, not just the transient
IR.

### Extension Points

An IR adapter (parser + normalizer for one source format) is the concrete
implementation behind the "IR adapter" extension point in the
[CLI Architecture](CLI_ARCHITECTURE.md#extension-model) (that document's
prior "Validator adapter" row is broadened here to reflect that the same
adapter now serves the Generator and Runtime, not only `validate`). Adding a
new artifact type means adding one IR adapter and one schema, not one
adapter per consumer.

### Dependency Graph and Version Graph

Two graph-level IR constructs exist above individual artifact IR, built by
collecting resolved references across every IR in scope:

- **Dependency Graph:** nodes are artifact IDs (Skill, Workflow, Knowledge);
  edges are resolved references (Workflow step -> Skill, Skill -> Knowledge,
  Knowledge -> related Knowledge) per the resolution rules in the
  [Knowledge Dependency Specification](../specifications/KNOWLEDGE_DEPENDENCY_SPECIFICATION.md)
  and the Workflow Architecture's graph-building step. It supports orphan
  detection, cycle detection across artifact kinds, and breaking-change
  impact analysis (who depends on this ID before I change it).
- **Version Graph:** nodes are `(artifact ID, version)` pairs; edges are
  declared compatible ranges from dependents, per the
  [Version Specification](../specifications/VERSION_SPECIFICATION.md). It
  supports detecting a declared range no existing version satisfies, and
  flagging active dependents of a deprecated or archived version.

Both graphs are derived, read-only views over the IR of every artifact in
scope; they are not stored, and building them does not mutate any artifact's
IR. See the IR Specification for their exact structure.

## Examples

Parsing `skills/summarize-document/skill.yaml` and normalizing a
`kb:technical:...` Knowledge document both yield IR objects that
`Draft202012Validator` can check against `schemas/skill.schema.json` and
`schemas/knowledge.schema.json` respectively — the Sprint 8 fixture script
already exercises this without naming it "IR."

A future `AISkill.CLI generate skill <name>` command would build a Skill
IR from the filled Skill template (once the Template Engine's output is
normalized the same way authored `skill.yaml` is), not read the template
file a second time with different logic.

## References

- [IR Specification](../specifications/IR_SPECIFICATION.md)
- [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)
- [CLI Architecture](CLI_ARCHITECTURE.md)
- [Template Engine Architecture](TEMPLATE_ENGINE_ARCHITECTURE.md)
- [Knowledge Dependency Specification](../specifications/KNOWLEDGE_DEPENDENCY_SPECIFICATION.md)
- [Version Specification](../specifications/VERSION_SPECIFICATION.md)
- ADR-0005

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the IR pipeline, lifecycle, and adapter strategy |
| 0.2 | 2026-07-04 | Noted the Sprint 16 IR adapter implementation (ADR-0009) |
