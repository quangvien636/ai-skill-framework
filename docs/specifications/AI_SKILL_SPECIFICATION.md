# AI Skill Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define the official contract for every AI Skill so future Workflows, Runtime
components, Generators, and CLI commands can create, validate, resolve, execute,
and test Skills consistently.

## Scope

This specification defines a Skill package and its behavior contract. It does not
implement Skills or allow a Skill to orchestrate other Skills. Multi-Skill
business processes belong to the Workflow Engine; the Master Skill remains a thin
orchestrator.

## Definitions

- **Skill:** versioned module performing one cohesive responsibility.
- **Manifest:** canonical machine-readable `skill.yaml`.
- **Instructions:** focused execution guidance that contains no reusable domain
  knowledge.
- **Contract test:** fixture asserting observable input, output, constraint, or
  failure behavior.
- **Skill procedure:** ordered internal actions for the Skill's one
  responsibility; it is not a multi-Skill Workflow.

## Design

### Package Layout

```text
skills/<skill-name>/
  skill.yaml
  instructions.md
  README.md
  examples/
  tests/
```

- `skill.yaml` is the canonical contract.
- `instructions.md` contains focused task instructions.
- `README.md` provides human guidance without redefining the manifest.
- `examples/` contains representative input/output pairs.
- `tests/` contains contract fixtures.

All files are required before promotion to `active`. A package MUST NOT vendor
Knowledge documents or another Skill.

### Metadata

The manifest MUST include all common Metadata fields and:

```yaml
responsibility: "One sentence describing the Skill's only responsibility."
```

The responsibility is observable, narrower than a Workflow, and has one primary
reason to change. The Skill ID, path, and name follow the Naming Convention.

### Inputs

`inputs` is a map of named fields. Every field declares:

| Field | Required | Description |
| --- | --- | --- |
| `type` | Yes | `string`, `number`, `integer`, `boolean`, `array`, or `object` |
| `required` | Yes | Whether the caller must provide the field |
| `description` | Yes | Semantic meaning, not merely the type |
| `constraints` | No | Bounds, pattern, enum, shape, or item rules |
| `default` | Optional fields only | Deterministic default matching the type |
| `sensitive` | No | Whether logs and reports must redact the value |

Inputs MUST be explicit and validated before execution. Skills MUST NOT depend on
undeclared conversation memory, global state, environment data, or implicit tool
results.

### Outputs

`outputs` uses the same named schema structure except `required` describes
successful output presence. Each output MUST be attributable to the Skill's
responsibility. The contract MUST distinguish successful output from structured
errors and evaluation reports.

Unknown output fields are rejected unless `additional_properties: true` is
explicitly declared. Sensitive outputs inherit redaction requirements.

### Dependencies

Dependencies are declared, versioned, and minimal:

| Group | Purpose |
| --- | --- |
| `runtime` | Required Runtime capabilities or adapters |
| `tools` | External tool interfaces; no embedded credentials |
| `knowledge` | Canonical references governed by Knowledge Dependency Specification |

A Skill MUST NOT depend on another Skill. Composition belongs to Workflows.
Dependencies MUST define required/optional behavior and compatible versions.

### Internal Workflow (Procedure)

The optional `procedure` lists deterministic internal stages for the single
responsibility:

```yaml
procedure:
  - id: "validate-input"
    action: "Validate input against the declared schema."
  - id: "produce-summary"
    action: "Apply instructions and resolved knowledge."
  - id: "validate-output"
    action: "Validate output against the declared schema."
```

Procedure stages MUST NOT reference or invoke other Skills, select Workflows, or
contain reusable domain knowledge. Branches, when necessary, use declared input
conditions and must converge on the same output contract.

### Constraints

`constraints` declares enforceable limits including:

- prohibited behavior and out-of-scope requests;
- maximum input or output size;
- allowed side effects and tool access;
- timeout or resource budget;
- privacy, safety, and redaction rules;
- determinism requirements where applicable.

Constraints are hard gates, not suggestions. A Skill fails safely when a required
constraint cannot be satisfied.

### Knowledge Dependencies

The `knowledge` dependency group uses canonical Knowledge IDs, compatible
versions, required flags, purpose, and optional sections. Skills reference
Knowledge; they MUST NOT copy it into instructions, examples, or manifests.

### Evaluation

Every active Skill declares an evaluation contract with at least one metric,
scoring, acceptance threshold, failure action, and any hard gates. Evaluation
checks output and emits a report; it does not rewrite output.

### Reflection

Reflection is optional. When enabled, it declares bounded attempts, minimum
improvement, terminal action, and reflectable hard gates. It runs only from an
eligible evaluation failure and never changes Skill scope, dependencies, or
thresholds.

### Example Requirements

An active Skill MUST include:

- one minimal valid case;
- one representative valid case;
- one boundary case;
- one invalid or refusal case.

Each example records input, expected output properties, expected evaluation
decision, and relevant dependency versions. Examples illustrate behavior but do
not replace tests.

### Tests

Contract tests MUST cover:

- metadata and schema validation;
- required, optional, boundary, and invalid inputs;
- successful output shape and required fields;
- each declared constraint and failure category;
- required and optional dependency resolution;
- evaluation pass and failure paths;
- reflection termination when reflection is enabled;
- backward compatibility promised by the current major version.

Tests MUST be deterministic or declare controlled fixtures for nondeterministic
components. Active Skills require all contract tests to pass.

### Versioning

`schema_version` identifies this contract; `version` identifies Skill behavior.
Both follow the Version Specification. Input/output removal, incompatible type or
meaning changes, tighter constraints that reject previously valid input, and
changed responsibility are breaking. A responsibility change SHOULD create a new
Skill ID.

## Examples

### Complete Manifest

This example is illustrative and does not create an actual Skill:

```yaml
schema_version: "1.0.0"
id: "skill:summarize-document"
name: "summarize-document"
display_name: "Summarize Document"
description: "Produces a bounded summary of one supplied document."
version: "1.0.0"
status: "draft"
owners: ["framework-maintainers"]
tags: ["summarization"]
responsibility: "Summarize one supplied document without external research."
inputs:
  document:
    type: "string"
    required: true
    description: "Document text to summarize."
    constraints:
      min_length: 1
  max_words:
    type: "integer"
    required: false
    description: "Maximum summary length."
    default: 200
outputs:
  summary:
    type: "string"
    required: true
    description: "Summary supported by the input document."
dependencies:
  runtime: []
  tools: []
  knowledge: []
procedure:
  - id: "validate-input"
    action: "Validate declared inputs."
  - id: "summarize"
    action: "Produce a bounded summary using instructions."
  - id: "validate-output"
    action: "Validate declared outputs."
constraints:
  side_effects: "none"
  prohibited:
    - "Introduce claims unsupported by the input."
evaluation:
  metrics:
    - name: "accuracy"
      description: "Summary claims are supported by input."
      weight: 1.0
      rubric:
        "0": "Material claims contradict the input."
        "50": "Some details are unsupported."
        "100": "Every material claim is supported."
  scoring:
    scale: "0..100"
    aggregate: "weighted-mean"
  acceptance:
    minimum_score: 90
    hard_gates: ["output-schema-valid"]
  on_failure: "reflect"
reflection:
  enabled: true
  max_attempts: 1
  minimum_improvement: 5
  on_exhausted: "fail"
  reflectable_hard_gates: ["output-schema-valid"]
```

## Validation

A conforming Skill passes static manifest, naming, version, dependency, schema,
evaluation, reflection, package-layout, and test-presence checks. Runtime
validation checks actual values and resolved versions. Errors MUST identify the
field or contract rule and MUST NOT be silently repaired.

## References

- [Specification Registry](README.md)
- [Workflow Specification](WORKFLOW_SPECIFICATION.md)
- [Knowledge Dependency Specification](KNOWLEDGE_DEPENDENCY_SPECIFICATION.md)
- [Evaluation Specification](EVALUATION_SPECIFICATION.md)
- [Reflection Specification](REFLECTION_SPECIFICATION.md)
- [Metadata Specification](METADATA_SPECIFICATION.md)
- [Version Specification](VERSION_SPECIFICATION.md)
- [Naming Convention](../principles/NAMING_CONVENTION.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established the official AI Skill contract |
