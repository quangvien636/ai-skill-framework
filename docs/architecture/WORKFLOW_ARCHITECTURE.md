# Workflow Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define the lifecycle, package structure, deterministic execution model,
orchestration, mappings, failures, and validation for Workflows.

## Scope

This architecture operationalizes the Workflow Specification without implementing
a Runtime or production Workflow.

## Definitions

- **Graph:** directed acyclic set of Skill-invocation steps.
- **Ready step:** step whose dependencies completed successfully.
- **Execution state:** immutable inputs plus recorded step outcomes and mappings.
- **Terminal result:** success, failure, or manual-review state.

## Design

### Lifecycle and Folder Standard

```text
Proposed -> Draft -> Validated -> Active -> Deprecated -> Archived

workflows/<workflow-name>/
  workflow.yaml
  README.md
  examples/
  tests/
```

Only active Workflows are selected. Promotion requires contract validation,
resolvable active Skills, examples, tests, and architecture review.
`templates/workflow/` is the generator-ready neutral skeleton, not a Workflow.

### Execution Model

1. Resolve the exact Workflow and Skill versions.
2. Validate Workflow input and freeze execution context.
3. Build the graph and reject cycles or missing dependencies.
4. Select ready steps in manifest order for deterministic tie-breaking.
5. Map and validate inputs, invoke one Skill, validate its result, and record it.
6. Apply failure policy; never run a dependent step after failed prerequisites.
7. Map declared Workflow outputs and validate the terminal result.

Independent ready steps may run concurrently only when side effects and mappings
cannot conflict. Their recorded result order remains deterministic.

### Skill Orchestration

Each step invokes exactly one versioned Skill. Workflows own ordering and data
flow; Skills own specialized execution. The Master Skill selects a Workflow but
does not execute its business logic. Workflows never embed Skill instructions or
Knowledge content.

### Input and Output Mapping

Mappings use only `workflow.inputs.*` and `steps.<id>.outputs.*`. Every required
input has one source. Types are checked at source, step boundary, and final
output. Transformations name registered Runtime adapters; inline logic and hidden
global state are forbidden. Only explicitly mapped final outputs leave the graph.

### Failure Handling

Failures are categorized as validation, resolution, input, Skill, dependency,
output, timeout, or system failure. The declared action is `fail`, constrained
`skip`, bounded `retry`, or `manual-review`. Retry preserves versions and inputs;
quality failures use Reflection rather than error retry. Every terminal failure
retains completed state and structured evidence.

### Validation and Tests

Static validation checks package layout, metadata, versions, graph integrity,
Skill resolution, mapping existence/type compatibility, optional-step safety,
error policy, examples, and tests. Runtime validation checks values at each
boundary.

Tests cover linear and branching graphs, deterministic ordering, every mapping,
cycle/missing dependency rejection, Skill resolution, each error action, output
validation, and version compatibility.

## Examples

The neutral template models two dependent placeholder steps and explicit mapping.
A generator replaces all placeholders and keeps the result `draft`; it does not
invent Skill references or inline transformations.

## References

- [Workflow Specification](../specifications/WORKFLOW_SPECIFICATION.md)
- [Skill Architecture](SKILL_ARCHITECTURE.md)
- [Evaluation Specification](../specifications/EVALUATION_SPECIFICATION.md)
- [Reflection Specification](../specifications/REFLECTION_SPECIFICATION.md)
- [Workflow Template](../../templates/workflow/README.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Workflow execution architecture |
