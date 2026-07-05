# Uncertainty Language

- **Knowledge ID:** `kb:foundational:research:uncertainty:uncertainty-language`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `research`
- **Topic:** `uncertainty`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines calibrated language for confidence, inference, disagreement,
limitations, and unknowns in research briefs.

## Applies To

- skill:research
- workflow:research-topic-to-brief

## Scope

### Includes

- Qualitative confidence and explicit uncertainty causes.

### Excludes

- Numeric probability estimates unsupported by a declared method.

## Guidance

State both the confidence level and its reason:

- **High confidence:** multiple applicable, independent, method-transparent
  sources converge and no material contradiction remains.
- **Moderate confidence:** useful evidence supports the claim, but coverage,
  independence, method, or applicability has a meaningful limitation.
- **Low confidence:** evidence is sparse, indirect, weakly applicable, or
  materially contradicted.
- **Unknown:** no supplied evidence can answer the question.

Use precise phrases such as “the supplied evidence indicates,” “this is an
inference from,” “sources disagree,” “evidence is limited to,” and “cannot be
determined from the supplied material.” Avoid “proves,” “obviously,” “all,” or
“never” unless the evidence and scope genuinely justify them.

## Decision Rules

1. Tie every uncertainty statement to a cause and decision consequence.
2. Describe disagreement before attempting reconciliation.
3. Never translate qualitative confidence into an invented percentage.
4. Distinguish absence of evidence from evidence of absence.
5. Narrow a conclusion when scope uncertainty can be removed by doing so.

## Examples

### Good Example

“Low confidence: one internal interview suggests fewer setup questions, but
categorized ticket data was not supplied.”

### Counterexample

“The redesign probably cut tickets by 70%” when neither the percentage nor a
probability model appears in the supplied evidence.

## Limitations and Risks

- Qualitative labels are still judgments and require an accompanying rationale.
- Calibrated wording does not replace collection of missing evidence.

## Related Knowledge


## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Research v1 uncertainty language. |
