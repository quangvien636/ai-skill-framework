# Runtime Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-05

## Purpose

Define the preparation and execution boundaries for turning validated Workflow
IR into an immutable, dependency-resolved execution plan.

## Scope

The implemented v0.1 scope covers artifact cataloging, execution context,
dependency resolution, deterministic planning, and pipeline interfaces. It does
not execute a Skill, invoke an LLM, call a tool or connector, persist state, or
perform external side effects.

## Design

### Inputs and Ownership

Runtime consumes:

- the immutable Project Index from Project Discovery;
- successful Skill, Workflow, and Knowledge IR from the shared adapter pipeline;
- validation results from structural, graph, semantic, and repository layers;
- caller-supplied Workflow identity, exact version, execution ID, and inputs.

Runtime never parses YAML or Markdown independently. Validator IR remains the
single artifact interpretation per ADR-0005.

### Artifact Catalog

`ArtifactCatalog` indexes successful IR by artifact ID and version. Resolution
requires exactly one active artifact satisfying the declared version range.
Workflow-to-Skill and Skill-to-Knowledge resolutions preserve exact selected
versions in the plan.

Evaluation and Reflection remain embedded in Skill IR. Runtime and Tool
dependencies remain declarations only because no corresponding artifact
contracts or adapters exist.

### Execution Context

`ExecutionContext` contains an externally assigned execution ID, exact Workflow
identity/version, and deeply frozen input values. Planning rejects missing
required inputs, undeclared inputs, and values whose top-level Python shape does
not match the declared primitive type.

Full field-constraint evaluation, secret handling, and runtime value schemas are
not implemented yet.

### Execution Plan and Graph

Planning:

1. resolves one active exact Workflow;
2. validates and freezes its context;
3. resolves every referenced active Skill and required Knowledge dependency;
4. topologically orders steps;
5. groups independent ready steps into deterministic batches, using manifest
   order as the tie-breaker;
6. records mappings, error action, maximum attempts, exact resolutions, and
   declared Workflow outputs in an immutable `ExecutionPlan`.

The planner produces data only. A plan is not evidence that any step ran.

### Interfaces

Tool-neutral Protocol interfaces define Artifact Loader, Catalog Builder,
Workflow Planner, and Plan Store seams. No concrete Plan Store or Skill
executor exists. Future execution must introduce explicit state transitions,
boundary validation, failure records, and executor/tool contracts without
changing planning semantics silently.

## Failure Model

Planning failures use stable `ASF-RUNTIME-PLAN-*` codes:

| Code | Meaning |
| --- | --- |
| `ASF-RUNTIME-PLAN-001` | Workflow resolution failed |
| `ASF-RUNTIME-PLAN-002` | Execution context input is invalid |
| `ASF-RUNTIME-PLAN-003` | Skill resolution failed |
| `ASF-RUNTIME-PLAN-004` | Required Knowledge resolution failed |
| `ASF-RUNTIME-PLAN-005` | Workflow cannot be topologically planned |

## Limitations and Next Steps

- No LLM, Skill, tool, browser, MCP, connector, or filesystem executor.
- No retry loop, optional-step state, manual-review pause, or persistence.
- No runtime output mapping or value validation after execution.
- No structural object subtyping or transformation adapters.
- No Runtime/Tool graph nodes until their schemas and IR adapters exist.

## References

- [Workflow Architecture](WORKFLOW_ARCHITECTURE.md)
- [IR Architecture](IR_ARCHITECTURE.md)
- [CLI Architecture](CLI_ARCHITECTURE.md)
- [Workflow Specification](../specifications/WORKFLOW_SPECIFICATION.md)
- ADR-0005
- ADR-0010
- ADR-0011

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-05 | Established non-executing Runtime catalog, context, and planning architecture |
