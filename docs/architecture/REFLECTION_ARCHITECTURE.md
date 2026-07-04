# Reflection Engine Architecture

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define the bounded improvement loop, retry control, termination, and failure
handling for evaluated Skill and Workflow outputs.

## Scope

This architecture operationalizes the Reflection Specification. It does not
evaluate output, change contracts, orchestrate Skills, or implement an engine.

## Definitions

- **Candidate:** current output eligible for improvement.
- **Attempt:** one evidence-directed revision followed by re-evaluation.
- **Retry budget:** declared maximum reflection attempts.
- **Stagnation:** improvement below the declared minimum or unchanged findings.

## Design

### Trigger and Improvement Loop

```text
Failed evaluation report
  -> Eligibility and retry-budget check
  -> Select actionable findings
  -> Plan smallest corrections
  -> Revise candidate within original contract
  -> Record changes
  -> Re-evaluate with unchanged evaluator
  -> Pass | Retry | Fail | Manual review
```

Reflection receives immutable original inputs, resolved versions, current output,
and evaluation evidence. It preserves accepted content, addresses only supported
findings, and cannot add undeclared Knowledge, tools, side effects, or scope.

### Improvement Rules

Reflection never invents evidence, lowers thresholds, removes gates, changes
versions, or edits reports. Revised output must satisfy the original schema.
Every attempt records addressed/unresolved findings, changes, rationale, prior
and resulting scores, and terminal reason.

### Retry Policy

Artifacts explicitly declare `max_attempts` from 0 through 3,
`minimum_improvement`, and `on_exhausted`. Attempts use identical inputs,
dependencies, evaluator version, rubrics, and thresholds. Error retry is separate:
it handles transient execution failures, while reflection handles quality.

### Termination and Failure Handling

Stop on pass, exhausted budget, stagnation, recurring unchanged findings,
non-reflectable gates, manual-review routing, dependency/system error, or
reflection-engine failure. Preserve the last valid candidate and all reports.
No revised output is delivered without successful re-evaluation.

### Validation and Observability

Validation checks retry bounds, terminal actions, known reflectable gates, and a
matching evaluation route. Append-only attempt records correlate execution,
artifact, evaluation report, versions, findings, changes, scores, and termination.

## Examples

With two attempts and minimum improvement `5`, a change from `72` to `74` stops
for stagnation. A change from `72` to `81` may use the remaining attempt if the
acceptance threshold is `85`; passing at `88` terminates immediately.

## References

- [Reflection Specification](../specifications/REFLECTION_SPECIFICATION.md)
- [Evaluation Engine Architecture](EVALUATION_ARCHITECTURE.md)
- [Workflow Architecture](WORKFLOW_ARCHITECTURE.md)
- [Skill Architecture](SKILL_ARCHITECTURE.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established Reflection Engine architecture |
