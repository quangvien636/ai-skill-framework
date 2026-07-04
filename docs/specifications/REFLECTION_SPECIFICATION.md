# Reflection Specification

Version: 0.1
Status: Active
Last updated: 2026-07-04

## Purpose

Define controlled, bounded improvement after evaluation identifies correctable
quality failures.

## Scope

This specification governs reflection triggers, improvement inputs, retry policy,
termination, and traceability. Evaluation remains responsible for judging output;
Reflection may revise it but MUST NOT change acceptance criteria.

## Definitions

- **Reflection attempt:** one bounded revision based on one evaluation report.
- **Actionable finding:** evidence-linked defect with a target improvement.
- **Retry:** re-execution of evaluation after a reflected revision.
- **Terminal condition:** state after which automated reflection stops.

## Design

### Reflection Trigger

Reflection runs only when all are true:

- evaluation returns `fail`;
- evaluation configuration sets `on_failure: reflect`;
- every failed hard gate is declared reflectable;
- remaining retry budget is greater than zero;
- failure is a quality issue, not a system or dependency error.

Manual review, invalid configuration, unavailable required Knowledge, security
violations, and non-reflectable hard gates MUST NOT trigger automated reflection.

### Reflection Process

```text
Receive output and evaluation report
  -> Select actionable findings
  -> Preserve accepted content
  -> Plan the smallest corrections
  -> Produce a revised candidate
  -> Record changes and rationale
  -> Re-evaluate with the unchanged evaluator contract
```

Reflection receives the original inputs, current output, resolved dependency
versions, evaluation report, and retry state. It MUST NOT broaden the Skill's
responsibility, add undeclared Knowledge, or alter workflow mappings.

### Improvement Rules

- Address only evidence-backed findings.
- Preserve content that already passes unless a correction requires a local
  change.
- Prefer the smallest change capable of passing.
- Never fabricate evidence, citations, inputs, or successful tool results.
- Never lower thresholds, remove hard gates, or edit evaluator findings.
- Keep output compatible with the declared output schema.
- Record which findings changed, remained, or require human review.

### Retry Policy

Each declaration MUST define:

| Field | Type | Rule |
| --- | --- | --- |
| `max_attempts` | integer | From 0 through 3 |
| `minimum_improvement` | number | Required aggregate-score increase after an attempt |
| `on_exhausted` | enum | `fail` or `manual-review` |

The default is not implicit; every reflecting artifact declares its policy.
Automated reflection stops when output passes, attempts are exhausted, score
improvement is below the declared minimum, the same findings recur unchanged, or
a non-reflectable failure appears.

Each attempt uses the same evaluator version and thresholds. A configuration
change starts a new execution, not another attempt in the same reflection cycle.

### Reflection Record

Every attempt emits an append-only record containing artifact and execution IDs,
attempt number, evaluation report reference, selected findings, change summary,
resolved dependency versions, prior and resulting score, and terminal reason.

## Examples

```yaml
reflection:
  enabled: true
  max_attempts: 2
  minimum_improvement: 5
  on_exhausted: "manual-review"
  reflectable_hard_gates:
    - "output-schema-valid"
```

If attempt one improves a score from 72 to 74 while `minimum_improvement` is 5,
reflection stops instead of spending the second attempt on a stagnant revision.

## Failure Handling

Reflection-engine errors preserve the last valid output and evaluation report,
then follow `on_exhausted`. A reflected output is never delivered without a new
evaluation report.

## Validation

Validators MUST check retry bounds, allowed terminal actions, known hard gates,
and that reflection is declared only when evaluation can route failures to it.

## References

- [Evaluation Specification](EVALUATION_SPECIFICATION.md)
- [AI Skill Specification](AI_SKILL_SPECIFICATION.md)
- [Workflow Specification](WORKFLOW_SPECIFICATION.md)
- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- [Design Principles](../principles/DESIGN_PRINCIPLES.md)

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1 | 2026-07-04 | Established bounded reflection and retry contract |
