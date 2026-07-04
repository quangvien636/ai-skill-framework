# Workflow Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define the declarative contract by which the Workflow Engine composes versioned
Skills into a validated execution order.

## Scope

This specification covers Workflow packages, metadata, steps, Skill references,
data mappings, validation, and failures. It does not define Skill internals,
domain knowledge, or Runtime implementation.

## Definitions

- **Workflow:** versioned business process composed from Skill invocations.
- **Step:** one invocation of one Skill.
- **Mapping:** explicit transfer from Workflow input or prior output into a step.
- **Dependency edge:** ordering relationship created by `depends_on`.
- **Execution order:** deterministic topological order of valid steps.

## Design

### Package Layout

```text
workflows/<workflow-name>/
  workflow.yaml
  README.md
  examples/
  tests/
```

`workflow.yaml` is the machine-readable contract. `README.md` explains intent and
human usage but MUST NOT redefine the manifest. Examples and tests are required
before promotion to `active`.

### Workflow Metadata

The manifest uses common Metadata fields plus:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `entrypoint` | string | Yes | First logical step ID |
| `inputs` | object | Yes | Workflow input schema |
| `outputs` | object | Yes | Workflow output schema and mappings |
| `steps` | array | Yes | At least one uniquely identified step |
| `error_handling` | object | Yes | Default failure behavior |

### Execution Order and Skill References

Each step MUST declare:

```yaml
- id: "summarize"
  skill:
    id: "skill:summarize-document"
    version: ">=1.2.0 <2.0.0"
  depends_on: []
  input_mapping: {}
  on_error: "fail"
```

Step IDs are unique `kebab-case`. `depends_on` forms a directed acyclic graph.
The engine executes a deterministic topological order; independent steps MAY run
concurrently only when mappings and declared side effects do not conflict.

One step invokes exactly one Skill. Multi-Skill logic belongs in the Workflow,
never inside a Skill or the Master Skill.

### Input Mapping

Mappings use explicit source paths:

```text
workflow.inputs.<field>
steps.<step-id>.outputs.<field>
```

Every required Skill input MUST resolve from exactly one available source before
the step runs. Implicit global state, positional mapping, and undeclared context
are prohibited. Mapping transformations MUST name a registered Runtime adapter;
inline business logic is prohibited.

### Output Mapping

Workflow outputs map from completed step outputs. A mapped value MUST conform to
both the producing Skill schema and Workflow output schema. Unmapped step output
remains internal and MUST NOT leak into final output.

### Error Handling

Allowed actions are:

- `fail`: stop dependent execution and return structured failure;
- `skip`: allowed only for an optional step with no required downstream mapping;
- `retry`: repeat the same Skill version under an explicit bounded retry policy;
- `manual-review`: pause automated delivery and retain execution state.

Error retries address transient system failures. Quality improvement uses the
Reflection Specification and MUST NOT be disguised as an error retry.

Every failure record includes workflow and step IDs/versions, error category,
attempt, dependency resolutions, and completed/skipped step state. Compensating
actions, if introduced later, require an explicit contract extension.

### Validation

Static validation MUST confirm:

- metadata, naming, and versions conform;
- all Skill references resolve to compatible active artifacts;
- step IDs are unique and the graph is acyclic;
- `entrypoint`, dependencies, and mappings resolve;
- input and output types are compatible;
- no required data depends on skipped or optional output;
- retry limits and error actions are valid;
- Knowledge, evaluation, and reflection declarations used by steps conform to
  their own specifications.

Runtime validation checks actual values against schemas at Workflow input, every
step boundary, and Workflow output.

### Version

`schema_version` identifies the Workflow contract and `version` identifies the
Workflow's mappings and behavior. Both follow the Version Specification.
Removing or reordering required steps, changing dependency semantics, making an
input mapping incompatible, or changing output meaning is breaking. Updating a
Skill reference within its already declared compatible range is not a Workflow
version change when observable behavior remains compatible.

## Examples

```yaml
schema_version: "1.0.0"
id: "workflow:summarize-and-review"
name: "summarize-and-review"
display_name: "Summarize and Review"
description: "Summarizes one document and reviews the result."
version: "1.0.0"
status: "draft"
owners: ["framework-maintainers"]
entrypoint: "summarize"
inputs:
  document:
    type: "string"
    required: true
steps:
  - id: "summarize"
    skill:
      id: "skill:summarize-document"
      version: ">=1.0.0 <2.0.0"
    depends_on: []
    input_mapping:
      document: "workflow.inputs.document"
    on_error: "fail"
  - id: "review"
    skill:
      id: "skill:review-summary"
      version: "1.0.0"
    depends_on: ["summarize"]
    input_mapping:
      summary: "steps.summarize.outputs.summary"
    on_error: "fail"
outputs:
  summary:
    type: "string"
    from: "steps.summarize.outputs.summary"
  review:
    type: "object"
    from: "steps.review.outputs.review"
error_handling:
  default: "fail"
```

## Tests

An active Workflow MUST include tests for valid execution, every mapping, invalid
input, Skill-resolution failure, step failure, output validation, and each
configured error action. Graph validation MUST include cycle and missing-step
cases.

## References

- [AI Skill Specification](AI_SKILL_SPECIFICATION.md)
- [Metadata Specification](METADATA_SPECIFICATION.md)
- [Version Specification](VERSION_SPECIFICATION.md)
- [Evaluation Specification](EVALUATION_SPECIFICATION.md)
- [Reflection Specification](REFLECTION_SPECIFICATION.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Workflow package and execution contract |
