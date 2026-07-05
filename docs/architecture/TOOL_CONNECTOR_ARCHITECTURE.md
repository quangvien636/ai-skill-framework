# Tool and Connector Contract Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-05

## Purpose

Define the architecture, scope, lifecycle, and validation responsibilities for Tool and Connector contracts.

## Scope

### Tool Scope
Tools define the declarative contract for operations that a Skill or Workflow can invoke (e.g., read file, search web, query database). They specify input parameters, expected outputs, and error states.

### Connector Scope
Connectors define the declarative contract for external system integrations and authentication boundaries that Tools or Skills rely on (e.g., database connection, REST API client, OAuth provider).

## Design

### Graph Visibility
Tools and Connectors are first-class nodes in the declarative dependency graph. They establish explicit edges (e.g., Skill depends on Tool, Tool depends on Connector). These nodes are declarative only and contain no execution logic or fake placeholder runtime behavior.

### Lifecycle
```text
Proposed -> Draft -> Validated -> Active -> Deprecated -> Archived
```
The lifecycle follows the same rigorous progression as Skills and Workflows, ensuring review and validation prior to activation.

### Validation Responsibilities
The validation engine is responsible for:
- Validating Tool and Connector schemas (inputs, outputs, manifests).
- Validating declarative graph references (e.g., preventing broken edges, duplicate IDs).
- Ensuring contracts contain no execution or runtime behavior.
- Verifying required documentation and metadata.

### Deferred Execution
All execution is strictly deferred. Tool and Connector contracts define *what* operations exist and their shape, not *how* they execute.

### Runtime Responsibilities
A future Runtime layer (currently out of scope) will be responsible for:
- Resolving Tool and Connector references dynamically.
- Managing authentication and connection pooling.
- Executing Tool operations and handling side effects.
- Enforcing resource limits and sandboxing.

### Non-Goals
- No placeholder runtime implementations.
- No execution logic or scripts within contracts.
- No fake graph nodes (nodes must map to real declarative definitions).
- No hardcoded secrets or credentials in contracts.

## References

- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Contract Validation Architecture](CONTRACT_VALIDATION_ARCHITECTURE.md)
- [IR Architecture](IR_ARCHITECTURE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-05 | Initial Tool and Connector contract architecture |
