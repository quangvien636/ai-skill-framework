# Intermediate Representation (IR) Specification

Version: 0.2
Status: Active
Last updated: 2026-07-04

## Purpose

Define the normative object model every IR adapter must produce, so the
Validator, Generator, CLI, and Runtime consume one shape per artifact type
instead of each reinterpreting Markdown or YAML independently.

## Scope

This specification defines the IR object model: Metadata IR, Reference IR,
Skill IR, Workflow IR, Knowledge IR, Dependency Graph, and Version Graph. It
does not define validation layers or diagnostics (owned by the
[Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)),
parsing/normalization process detail (owned by the
[IR Architecture](../architecture/IR_ARCHITECTURE.md)), or per-artifact
authoring rules (owned by the AI Skill, Workflow, and Knowledge
specifications/architectures, which remain authoritative for their
artifact's intent).

## Definitions

- **IR object:** one artifact's in-memory representation, conforming to a
  schema in `schemas/`.
- **Common fields:** the Metadata IR fields every IR object other than a
  graph includes.
- **Graph IR:** a derived object built from more than one IR object, not
  from a single source file.

## Design

### Metadata IR

Every Skill IR and Workflow IR includes the common artifact fields defined
by `metadata.schema.json#/$defs/commonArtifact` and the
[Metadata Specification](METADATA_SPECIFICATION.md): `schema_version`, `id`,
`name`, `display_name`, `description`, `version`, `status`, `owners`,
`tags`. Knowledge IR carries the equivalent identity fields in its own
shape (`id`, `title`, `category`, `domain`, `topic`, `version`,
`last_updated`) because Knowledge documents are authored as Markdown, not a
`commonArtifact`-shaped manifest — see Knowledge IR below. This
specification does not redefine either field set; it names them as the
Metadata IR to make clear both are the same conceptual layer.

### Reference IR

A Reference IR is one resolved-or-resolvable pointer from one artifact to
another:

| Reference kind | Shape | Owning contract |
| --- | --- | --- |
| Skill/tool/runtime dependency | `metadata.schema.json#/$defs/versionedReference` | Metadata Specification |
| Knowledge dependency | `id`, `version`, `required`, `purpose`, `sections` | [Knowledge Dependency Specification](KNOWLEDGE_DEPENDENCY_SPECIFICATION.md) |
| Workflow step -> Skill | `skill.id`, `skill.version` | Workflow Specification |
| Workflow step -> step | `depends_on` | Workflow Specification |
| Knowledge -> Knowledge | `related_knowledge` (ID list) | Knowledge Architecture |

A Reference IR is always `(target ID, version constraint)`; it never embeds
the target's content. Resolution (turning a Reference IR into one exact
artifact version) follows the owning contract's resolution rules, not this
specification.

### Skill IR

A Skill IR is the object `schemas/skill.schema.json` validates: Metadata IR
fields plus `responsibility`, `inputs`, `outputs`, `dependencies`
(Reference IR lists), `procedure`, `constraints`, `evaluation`, and
`reflection`. Parsing `skill.yaml` already yields this shape (see IR
Architecture's Normalization Strategy); no separate transform step exists
between "parsed YAML" and "Skill IR" beyond default-filling and
unknown-key rejection.

### Workflow IR

A Workflow IR is the object `schemas/workflow.schema.json` validates:
Metadata IR fields plus `entrypoint`, `inputs`, `steps` (each a Reference IR
to a Skill plus `depends_on` Reference IRs to other steps), `outputs`, and
`error_handling`. A Workflow IR additionally carries one derived property
not present in the raw manifest: the **built step graph** described by the
[Workflow Architecture](../architecture/WORKFLOW_ARCHITECTURE.md#execution-model)
Execution Model steps 1-3 (resolved versions, frozen input context, and the
validated acyclic graph). The built graph is part of the Workflow IR because
Generator and Runtime consumers both need it; recomputing it independently
per consumer would violate "one IR, many consumers."

### Knowledge IR

A Knowledge IR is the object `schemas/knowledge.schema.json` validates,
produced by the Markdown normalizer described in the IR Architecture: `id`,
`title`, `status`, `category`, `domain`, `topic`, `version`,
`last_updated`, `summary`, `applies_to`, `scope`, `guidance`,
`decision_rules`, `examples`, `limitations_and_risks`,
`related_knowledge`, `sources`, `revision_history`. The Knowledge Markdown
document remains the authoritative source (per ADR-0001 and ADR-0005); the
Knowledge IR is transient validation/generation input and MUST NOT become a
second stored copy.

### Dependency Graph

The Dependency Graph is a Graph IR built from every in-scope artifact's
Reference IR values:

```text
node: artifact ID (skill:*, workflow:*, kb:*)
edge: (source ID) -> (target ID), labeled with the Reference IR's
      version constraint and required/optional flag
```

Construction reads only already-produced IR objects; it does not re-parse
source. Consumers use it to:

- detect an artifact ID with no incoming edges outside its own kind's entry
  points (an orphan Knowledge document or unused Skill);
- detect a reference cycle (for example Knowledge A related to B related
  back to A when the relation is meant to be acyclic for a given use);
- answer "what depends on this ID" before a breaking change, per the
  Version Specification's breaking-change procedure.

A missing or unresolved required edge is a repository-validation error
attributed to the owning specification (Knowledge Dependency Specification
for Knowledge edges, Workflow Architecture for step edges); the Dependency
Graph itself only reports structure, not the resolution rule that made an
edge invalid.

Node kinds are exactly `skill:*`, `workflow:*`, `kb:*` — Evaluation and
Reflection are not graph nodes (they have no `id` and are validated as
fields embedded in a Skill's IR, not independent artifacts), and a Skill's
`dependencies.runtime`/`.tools` references are not graph edges because no
Runtime/Tool IR adapter exists yet. See ADR-0010 for the full resolution
and its alternatives.

### Version Graph

The Version Graph is a Graph IR built from every declared version
constraint in scope:

```text
node: (artifact ID, exact version) for every known version
edge: (dependent ID) -> (artifact ID, version constraint)
```

Consumers use it to:

- detect a declared range with zero satisfying known versions;
- detect an active dependent whose resolved version is `deprecated` or
  `archived`, surfacing the Version Specification's deprecation warning;
- simulate a proposed version bump's impact before publishing it (which
  dependents' ranges would stop resolving).

The Version Graph does not define compatibility rules itself; it applies
the [Version Specification](VERSION_SPECIFICATION.md)'s existing rules
across every known edge at once instead of one dependency at a time.

Version-range satisfaction (`version_satisfies_range` in
`scripts/asf_validator/version_ir.py`) compares `(major, minor, patch)`
only; SemVer pre-release precedence is not implemented (ADR-0010, a
documented simplification, not a silent gap).

## Examples

A Skill IR for `skill:summarize-document` and a Knowledge IR for
`kb:technical:writing:summarization:brevity` connected by a
`dependencies.knowledge` Reference IR produce one Dependency Graph edge:
`skill:summarize-document -> kb:technical:writing:summarization:brevity`.

If `kb:technical:writing:summarization:brevity` is archived while that edge
is still `required: true`, the Dependency Graph surfaces the edge and the
Knowledge Dependency Specification's failure-handling rule determines it is
an error, not a warning.

## References

- [IR Architecture](../architecture/IR_ARCHITECTURE.md)
- [Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [Metadata Specification](METADATA_SPECIFICATION.md)
- [Version Specification](VERSION_SPECIFICATION.md)
- [Knowledge Dependency Specification](KNOWLEDGE_DEPENDENCY_SPECIFICATION.md)
- [Workflow Architecture](../architecture/WORKFLOW_ARCHITECTURE.md)
- [Schema Registry](../../schemas/README.md)
- ADR-0005
- ADR-0010

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the IR object model and graph-level constructs |
| 0.2 | 2026-07-04 | Clarified Dependency/Version Graph node kinds and version-satisfaction scope (Sprint 17, ADR-0010) |
