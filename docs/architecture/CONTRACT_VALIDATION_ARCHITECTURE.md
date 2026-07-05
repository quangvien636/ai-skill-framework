# Contract Validation Architecture

Version: 0.5
Status: Active
Last updated: 2026-07-05

## Purpose

Define a model-neutral validation pipeline that applies machine-readable schemas
and repository rules to framework artifacts before activation or execution.

## Scope

This architecture covers validation boundaries and diagnostics. Sprint 7 provides
schemas and documentation only; it does not implement a full validator, Runtime,
or CLI.

## Definitions

- **Structural validation:** JSON Schema checks over a parsed artifact.
- **Semantic validation:** rules not expressible reliably in JSON Schema.
- **Repository validation:** cross-file identity, reference, path, and lifecycle checks.
- **Normalized model / IR:** tool-neutral object produced from YAML or
  Markdown. Sprint 11 names this concept the Intermediate Representation
  (IR); see the [IR Architecture](IR_ARCHITECTURE.md) and
  [IR Specification](../specifications/IR_SPECIFICATION.md) for its pipeline
  position, lifecycle, and object model. This architecture keeps ownership
  of validation layers and diagnostics.
- **Diagnostic:** stable error or warning with artifact path and rule location.

## Design

### Pipeline

```text
Discover artifact
  -> Parse YAML or Markdown
  -> Normalize keys and sections
  -> Select schema by artifact type and schema_version
  -> JSON Schema Draft 2020-12 validation
  -> Semantic validation
  -> Repository-integrity validation
  -> Diagnostics and validation report
```

Parsing never mutates source. Schema validation is deterministic and offline.
Only artifacts with zero errors may become `active`; warnings require review but
do not automatically fail unless policy promotes the rule.

### Schema Authority

Markdown specifications define intent and normative behavior. Files under
`schemas/` encode machine-checkable structure. When they disagree, the repository
specification is authoritative and both artifacts must be reconciled in one
reviewed change. Schema `$id` values are stable logical identifiers, not network
dependencies.

### Source Adapters

- Skill and Workflow adapters parse canonical YAML manifests.
- Evaluation and Reflection schemas validate their embedded manifest objects.
- Knowledge adapters parse canonical Markdown headings, metadata, lists, and
  revision rows into `knowledge.schema.json`'s normalized model.

Knowledge Markdown remains the source of truth. The normalized object is transient
validation input and MUST NOT become a duplicate stored Knowledge artifact.

### Validation Layers

JSON Schema validates required/optional fields, primitive types, enums, patterns,
ranges, closed objects, and reusable `$ref` contracts.

Semantic validators handle:

- Skill ID/name/path agreement and one-responsibility review;
- Evaluation metric-name uniqueness and weights summing to `1.0`;
- Reflection/evaluation routing consistency;
- Workflow entrypoint, unique step IDs, acyclic graph, mapping availability, and
  type compatibility;
- Knowledge ID/taxonomy/path agreement and required Markdown sections;
- compatible version resolution and deprecation policy.

The implemented IR-level semantic core is
`scripts/asf_validator/semantic_validator.py`. It checks metric uniqueness and
weight totals, Evaluation/Reflection routing, reflectable gates, Workflow input
and output mapping availability and type equality, retry configuration, and
entrypoint reachability. It consumes successfully built IR and does not discover
files or duplicate Dependency/Version Graph rules. ID/taxonomy/path agreement
requires canonical repository context and remains coupled to Repository
Discovery.

Repository validators handle unique IDs, reference existence, lifecycle,
Knowledge Index membership, canonical paths, links, case-insensitive collisions,
secrets, and package file requirements.

The implemented repository layer uses `project_discovery.py` as its only
filesystem inventory. `repository_validator.py` checks canonical Skill,
Workflow, and Knowledge paths; required package files; Knowledge Index
membership/path agreement; and case-insensitive path collisions.
`validate_repository.py` composes discovery, IR, Dependency/Version Graph,
semantic, and repository checks without adding validation meaning of its own.
Machine-readable reporting remains a future thin-interface concern.

`content_integrity.py` completes the bounded content rules with local Markdown
file/anchor resolution, duplicate-anchor detection, ADR reference consistency,
an explicit stale-reference denylist, narrow credential signatures, and
lifecycle/orphan checks. Placeholder markers are errors only in active shipped
Skill, Workflow, and Knowledge packages; draft and template sources are
intentional exceptions. Active Skills require a Workflow consumer and active
Knowledge requires a Skill consumer. Workflows are valid entry roots, and
embedded Evaluation/Reflection inherit their owning Skill lifecycle.

### Diagnostics

Each diagnostic contains `code`, `severity`, `artifact`, `location`, `message`,
`rule_reference`, and optional `suggestion`. Validators do not silently repair
source. Stable codes use `ASF-<LAYER>-<NUMBER>`, such as `ASF-SCHEMA-001`.

### Compatibility and Security

Schema selection uses exact supported `schema_version`; unknown major versions
fail. Schema changes follow the Version Specification. Parsers disable unsafe YAML
features, do not resolve remote references, limit input size/depth, redact marked
sensitive values, and never execute artifact content.

### Extension Path

The future validator may expose library and CLI adapters over one validation core.
Exit behavior, output formats, caching, and editor integration belong to the
Validator Roadmap and must not change validation meaning.

## Examples

A Workflow may pass JSON Schema but fail semantic validation because its graph
contains a cycle. A Knowledge Markdown file may parse successfully but fail
repository validation because its ID is missing from the Knowledge Index.

## References

- [Schema Registry](../../schemas/README.md)
- [Validation Guide](../guides/VALIDATION_GUIDE.md)
- [Validator Roadmap](../roadmaps/VALIDATOR_ROADMAP.md)
- [AI Skill Specification](../specifications/AI_SKILL_SPECIFICATION.md)
- [Workflow Specification](../specifications/WORKFLOW_SPECIFICATION.md)
- [Knowledge Architecture](KNOWLEDGE_ARCHITECTURE.md)
- [IR Architecture](IR_ARCHITECTURE.md)
- [IR Specification](../specifications/IR_SPECIFICATION.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established layered contract validation architecture |
| 0.2 | 2026-07-04 | Aligned "normalized model" terminology with the Sprint 11 IR |
| 0.3 | 2026-07-05 | Documented the implemented IR-level semantic validator and repository-context boundary |
| 0.4 | 2026-07-05 | Documented Project Discovery integration and implemented repository integrity rules |
| 0.5 | 2026-07-05 | Added deterministic Markdown, ADR, stale-reference, placeholder, secret, and orphan policies |
