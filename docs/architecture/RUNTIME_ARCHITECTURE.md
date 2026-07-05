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

Evaluation and Reflection remain embedded in Skill IR. `ArtifactCatalog` now
indexes Tool, Connector, and Runtime Contract artifacts alongside Skill,
Workflow, and Knowledge (ADR-0014) — Tool/Connector catalog entries closed a
latent gap: the Dependency Graph already supported those kinds, but the
planning catalog did not.

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
4. resolves each Skill's `dependencies.runtime` reference to a Runtime
   Contract, then that Runtime Contract's own `retriever.knowledge`,
   `tools.refs`, and (if enabled) `fallback_profile.fallback_runtime`
   references (ADR-0014) — `model`/`publisher` need no further resolution,
   since they are terminal inline descriptors already fully contained in
   the Runtime Contract's IR;
5. topologically orders steps;
6. groups independent ready steps into deterministic batches, using manifest
   order as the tie-breaker;
7. records mappings, error action, maximum attempts, the resolved Skill's
   declared `timeout_seconds` (if any), every resolution (Skill, Knowledge,
   and now Runtime/Tool/Knowledge-via-Runtime), and declared Workflow
   outputs in an immutable `ExecutionPlan`. `PlanStep.runtime` carries a
   step's own Runtime-chain resolutions, mirroring the existing
   `PlanStep.knowledge` field.

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
| `ASF-RUNTIME-PLAN-006` | Required Runtime Contract resolution failed |
| `ASF-RUNTIME-PLAN-007` | Required Runtime-referenced Knowledge resolution failed |
| `ASF-RUNTIME-PLAN-008` | Required Runtime-referenced Tool resolution failed |
| `ASF-RUNTIME-PLAN-009` | Required Runtime fallback resolution failed |

## Limitations and Next Steps

- No LLM, Skill, tool, browser, MCP, connector, or filesystem executor is
  implemented in this package, and per ADR-0013 none will be: execution is
  delegated to external backends (LangGraph, the MCP Python SDK, LlamaIndex,
  provider SDKs) through the adapter Protocol seams in
  [Execution Adapter Architecture](EXECUTION_ADAPTER_ARCHITECTURE.md), not a
  future native executor written here.
- No retry loop, optional-step state, manual-review pause, or persistence —
  these are LangGraph's `RetryPolicy` and checkpointer responsibility once a
  `PlanCompiler` adapter compiles an `ExecutionPlan`.
- No runtime output mapping or value validation after execution.
- No structural object subtyping or transformation adapters.
- Runtime/Tool graph nodes now exist (ADR-0012, ADR-0014); the next gap is
  that no compiled plan has ever been executed end-to-end against a live
  adapter.

## References

- [Workflow Architecture](WORKFLOW_ARCHITECTURE.md)
- [IR Architecture](IR_ARCHITECTURE.md)
- [CLI Architecture](CLI_ARCHITECTURE.md)
- [Execution Adapter Architecture](EXECUTION_ADAPTER_ARCHITECTURE.md)
- [Runtime Contract Architecture](RUNTIME_CONTRACT_ARCHITECTURE.md)
- [Workflow Specification](../specifications/WORKFLOW_SPECIFICATION.md)
- ADR-0005
- ADR-0010
- ADR-0011
- ADR-0013
- ADR-0014

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-05 | Established non-executing Runtime catalog, context, and planning architecture |
| 0.2 | 2026-07-05 | Pointed Limitations/Next-Steps and References at the Execution Adapter Architecture (ADR-0013) instead of an implied native executor |
| 0.3 | 2026-07-05 | `PlanStep` now carries the resolved Skill's `timeout_seconds`, needed by the `langgraph_runtime` PlanCompiler adapter to preserve timeout metadata |
| 0.4 | 2026-07-05 | Catalog now indexes Tool/Connector/Runtime; planner resolves Skill -> Runtime Contract -> Knowledge/Tool/fallback-Runtime (ADR-0014); added `ASF-RUNTIME-PLAN-006..009` |
