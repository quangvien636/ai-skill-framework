# Evaluation Engine Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define how the Evaluation Engine validates, measures, scores, and routes Skill
and Workflow outputs consistently.

## Scope

This architecture operationalizes the Evaluation Specification. It does not
define domain rubrics, modify output, or implement an evaluator.

## Definitions

- **Evaluator:** versioned component applying a declared rubric.
- **Evidence:** input/output observation supporting a finding or score.
- **Gate:** non-compensable binary requirement.
- **Quality report:** immutable result of one evaluation.

## Design

### Pipeline

```text
Output + contract + resolved versions
  -> Configuration validation
  -> Output-schema validation
  -> Hard gates
  -> Metric evidence and scores
  -> Weighted aggregate
  -> Threshold decision
  -> Immutable report
  -> Pass | Fail | Reflect | Manual review
```

Evaluation is read-only. Each run pins artifact, evaluator, rubric, and Knowledge
versions. Re-evaluation creates a new report and never edits prior evidence.

### Quality Metrics and Scoring

Metrics have unique names, observable rubrics, positive weights totaling `1.0`,
and scores on `0..100`. The aggregate is the weighted mean, rounded once to two
decimal places. Common metric names are reusable vocabulary, not universal
rubrics; each artifact defines local evidence criteria.

### Acceptance Thresholds

Pass requires every hard gate, every declared metric minimum, and the aggregate
minimum. Thresholds are versioned with the evaluated contract and cannot change
during an execution. Safety, schema conformance, and mandatory provenance use
hard gates when compensation would be unsafe.

### Failure Handling

Invalid configuration and evaluator crashes are system failures, never score
zero. Missing evidence cannot pass. Quality failure follows the declared action:
terminal fail, eligible reflection, or manual review. Reports include actionable
findings without rewriting output or weakening criteria.

### Validation and Observability

Validation checks metric uniqueness, rubric anchors, weights, ranges, gates,
failure actions, and output-schema compatibility. Reports record execution ID,
artifact/evaluator versions, dependency resolutions, evidence, scores,
thresholds, decision, timestamp, and route.

## Examples

Scores `accuracy=90` at weight `0.6` and `completeness=80` at weight `0.4`
aggregate to `86`. With minimum `85` and all gates passed, the result passes; a
failed required-citation gate still fails regardless of aggregate.

## References

- [Evaluation Specification](../specifications/EVALUATION_SPECIFICATION.md)
- [Reflection Engine Architecture](REFLECTION_ARCHITECTURE.md)
- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Evaluation Engine architecture |
