# AI Skill Framework Specifications

Version: 0.2
Status: Active
Last updated: 2026-07-04

## Purpose

Provide the canonical entrypoint for artifact contracts used by future Skills,
Workflows, Runtime components, Generators, and CLI commands.

## Scope

These documents define repository formats and validation rules. They do not
implement an artifact loader, execution engine, generator, CLI, or actual Skill.

## Definitions

- **Contract:** a normative structure that producers must emit and consumers may
  rely on.
- **Producer:** a contributor, generator, or CLI command that creates an artifact.
- **Consumer:** a runtime component, validator, Skill, Workflow, or tool that
  reads an artifact.
- **Normative:** required for conformance unless explicitly marked optional.

## Design

| Specification | Canonical responsibility |
| --- | --- |
| [AI Skill Specification](AI_SKILL_SPECIFICATION.md) | Skill package and execution contract |
| [Workflow Specification](WORKFLOW_SPECIFICATION.md) | Multi-Skill orchestration contract |
| [Knowledge Dependency Specification](KNOWLEDGE_DEPENDENCY_SPECIFICATION.md) | Knowledge declaration and resolution |
| [Evaluation Specification](EVALUATION_SPECIFICATION.md) | Quality measurement and acceptance |
| [Reflection Specification](REFLECTION_SPECIFICATION.md) | Controlled improvement and retry |
| [Metadata Specification](METADATA_SPECIFICATION.md) | Shared artifact identity and metadata |
| [Version Specification](VERSION_SPECIFICATION.md) | Versions, compatibility, and deprecation |
| [Naming Convention](../principles/NAMING_CONVENTION.md) | Framework-wide names, IDs, and paths |
| [IR Specification](IR_SPECIFICATION.md) | Shared Intermediate Representation object model and graphs |

Authority stays narrow: a specification references another contract instead of
copying its rules. Existing Knowledge Architecture documents remain authoritative
for taxonomy, hierarchy, knowledge-document structure, and Knowledge naming.

Machine-checkable structure is encoded in the
[Schema Registry](../../schemas/README.md). Markdown specifications remain
authoritative for intent and semantic rules that JSON Schema cannot express.

Normative keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY**
express requirement strength.

## Examples

A generator creating a Skill reads the Metadata, Naming, Version, and AI Skill
specifications. If that Skill declares knowledge or quality controls, the
generator also applies the Knowledge Dependency, Evaluation, and Reflection
specifications.

## References

- [Project Context](../../PROJECT_CONTEXT.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)
- [ADR-0001](../adr/ADR-0001-repository-is-the-source-of-truth.md)
- [Contract Validation Architecture](../architecture/CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](../architecture/IR_ARCHITECTURE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the specification registry |
| 0.2 | 2026-07-04 | Registered the IR Specification |
