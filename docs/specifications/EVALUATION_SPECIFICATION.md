# Evaluation Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define a deterministic quality-evaluation contract for Skill and Workflow outputs
before reflection or final delivery.

## Scope

This specification defines evaluation declarations, metrics, scoring, thresholds,
pipeline behavior, and failures. Domain-specific rubrics belong to the evaluating
artifact or referenced Knowledge, not in this framework-level document.

## Definitions

- **Metric:** one named quality dimension with a scoring rule.
- **Rubric:** observable criteria mapping evidence to a score.
- **Hard gate:** binary condition that cannot be offset by other scores.
- **Acceptance threshold:** minimum passing score.
- **Evaluation report:** structured scores, evidence, findings, and decision.

## Design

### Evaluation Declaration

Each evaluated artifact MUST define:

| Field | Required | Rule |
| --- | --- | --- |
| `metrics` | Yes | At least one uniquely named metric |
| `scoring.scale` | Yes | Framework scale `0..100` |
| `scoring.aggregate` | Yes | `weighted-mean` |
| `acceptance.minimum_score` | Yes | Number from 0 through 100 |
| `acceptance.hard_gates` | No | Binary pass conditions |
| `on_failure` | Yes | `fail`, `reflect`, or `manual-review` |

Each metric declares `name`, `description`, `weight`, and a rubric. Metric weights
MUST be positive and sum to `1.0`. Rubrics MUST describe observable evidence at
minimum for scores `0`, `50`, and `100`.

### Evaluation Pipeline

```text
Validate declaration
  -> Validate output shape
  -> Check hard gates
  -> Score each metric with evidence
  -> Calculate weighted score
  -> Apply acceptance thresholds
  -> Emit immutable evaluation report
  -> Pass, fail, reflect, or request manual review
```

Evaluation measures output; it MUST NOT rewrite output. Improvement belongs to the
Reflection Engine.

### Quality Metrics

Artifacts choose metrics relevant to their contract. Common names include
`accuracy`, `completeness`, `clarity`, `structure`, `usefulness`, `risk`, and
`actionability`, as introduced by System Architecture.

Metric names and descriptions MUST define measurable local meaning. A generic
metric name without a rubric is invalid. Safety, schema conformance, required
citations, and prohibited content SHOULD be hard gates when failure cannot be
compensated by quality elsewhere.

### Scoring and Acceptance

The aggregate score is:

```text
sum(metric score * metric weight)
```

Round only the final score to two decimal places. An output passes only when:

- every hard gate passes;
- every metric-specific minimum passes, when declared;
- the aggregate meets `minimum_score`.

The report MUST include evaluator version, evaluated artifact ID and version,
metric scores, weights, evidence, hard-gate results, aggregate, threshold, and
decision.

### Failure Handling

- Invalid evaluation configuration fails before execution.
- Missing evidence prevents a metric from passing; evaluators MUST NOT invent it.
- `fail` returns the report without improvement.
- `reflect` invokes the Reflection contract with actionable findings.
- `manual-review` stops automated delivery and preserves all evidence.
- Evaluator errors are system failures, not quality scores.

## Examples

```yaml
evaluation:
  metrics:
    - name: "accuracy"
      description: "Claims are supported by supplied input."
      weight: 0.6
      minimum_score: 80
      rubric:
        "0": "Material claims contradict the input."
        "50": "Most claims match, with unsupported details."
        "100": "Every material claim is supported."
    - name: "completeness"
      description: "All required output sections are present."
      weight: 0.4
      rubric:
        "0": "Required output is absent."
        "50": "Some required sections are missing."
        "100": "Every required section is complete."
  scoring:
    scale: "0..100"
    aggregate: "weighted-mean"
  acceptance:
    minimum_score: 85
    hard_gates:
      - "output-schema-valid"
  on_failure: "reflect"
```

## Validation

Validators MUST check unique metrics, complete rubrics, weight totals, threshold
ranges, known hard gates, valid failure actions, and compatibility with the
artifact's output schema.

## References

- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- [Reflection Specification](REFLECTION_SPECIFICATION.md)
- [Metadata Specification](METADATA_SPECIFICATION.md)
- [Version Specification](VERSION_SPECIFICATION.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established evaluation pipeline and scoring contract |
