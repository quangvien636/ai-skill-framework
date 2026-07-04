# Metadata Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define shared metadata fields and artifact-specific extensions so repository
artifacts can be discovered, validated, generated, and consumed consistently.

## Scope

This specification governs metadata for Skills, Workflows, Knowledge documents,
Templates, ADRs, and Runtime components. Content schemas remain owned by their
artifact specifications.

## Definitions

- **Artifact ID:** globally unique, stable identity with a type prefix.
- **Artifact name:** path-safe canonical name governed by the Naming Convention.
- **Display name:** human-readable label that may change without changing identity.
- **Lifecycle status:** state controlling whether normal consumers may use an
  artifact.
- **Owner:** accountable maintainer, team, or repository role.

## Design

### Common Metadata

Machine-consumable manifests MUST use these fields:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `schema_version` | string | Yes | Version of the artifact specification |
| `id` | string | Yes | Globally unique and immutable |
| `name` | string | Yes | Canonical `kebab-case` name |
| `display_name` | string | Yes | Concise human-readable title |
| `description` | string | Yes | One retrieval-oriented summary |
| `version` | string | Yes | Semantic version of artifact content |
| `status` | enum | Yes | `draft`, `active`, `deprecated`, or `archived` |
| `owners` | string array | Yes | At least one repository owner or role |
| `tags` | string array | No | Unique, sorted `kebab-case` discovery labels |

Unknown fields MUST fail strict validation unless the governing artifact
specification explicitly allows an extension namespace. Dates, generated hashes,
and environment state MUST NOT determine artifact identity.

### Artifact Extensions

| Artifact | ID form | Additional required metadata |
| --- | --- | --- |
| Skill | `skill:<name>` | `responsibility` |
| Workflow | `workflow:<name>` | `entrypoint`, `steps` |
| Knowledge | `kb:<category>:<domain>:<topic>:<subject>` | Category, domain, topic, last-updated metadata defined by Knowledge Architecture |
| Template | `template:<name>` | `artifact_type` |
| Runtime component | `runtime:<name>` | `component_type`, `compatibility` |
| ADR | `adr:<four-digit-number>` | Decision status and date |

ADRs remain Markdown decision records and do not require YAML manifests. Their
existing decision metadata is the canonical representation. ADR lifecycle values
are `proposed`, `accepted`, `rejected`, and `superseded`; accepted ADRs are never
rewritten merely to appear current.

Knowledge documents continue using the canonical Knowledge Template. Their field
placement is not redefined here.

### Lifecycle Rules

- `draft`: may be reviewed and tested, but MUST NOT be selected for production
  execution.
- `active`: validated and eligible for normal use.
- `deprecated`: usable only for compatibility; MUST identify a replacement or
  explain why none exists.
- `archived`: historical and excluded from resolution.

Only maintainers may promote an artifact to `active`. Consumers MUST reject
`archived` dependencies and SHOULD warn on `deprecated` dependencies.

### Ownership and Mutability

IDs are immutable. A rename changes `name`, path, and references in one change,
but preserves `id` unless the artifact's responsibility or meaning becomes a new
artifact. Descriptions, display names, owners, tags, and compatible content may
change according to the Version Specification.

## Examples

```yaml
schema_version: "1.0.0"
id: "skill:summarize-document"
name: "summarize-document"
display_name: "Summarize Document"
description: "Produces a bounded summary of one supplied document."
version: "1.2.0"
status: "active"
owners:
  - "framework-maintainers"
tags:
  - "summarization"
responsibility: "Summarize one document without external research."
```

## Validation

A conforming validator MUST verify required fields, types, enum values, unique
IDs, naming rules, version syntax, and artifact-specific fields. It MUST report
field paths and actionable errors without silently applying defaults to required
metadata.

## References

- [AI Skill Specification](AI_SKILL_SPECIFICATION.md)
- [Workflow Specification](WORKFLOW_SPECIFICATION.md)
- [Version Specification](VERSION_SPECIFICATION.md)
- [Naming Convention](../principles/NAMING_CONVENTION.md)
- [Knowledge Architecture](../architecture/KNOWLEDGE_ARCHITECTURE.md)
- [ADR-0001](../adr/ADR-0001-repository-is-the-source-of-truth.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established shared artifact metadata |
