# Approval Rejection Rules

- **Knowledge ID:** `kb:foundational:quality:decisions:approval-rejection-rules`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `quality`
- **Topic:** `decisions`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines consistent rules for the final `approve`, `revise`, or `reject`
recommendation, including invalid and unsafe requests.

## Applies To

- skill:review-quality
- workflow:draft-to-reviewed-package

## Scope

### Includes

- Severity, correctability, evidence, safety, contract completeness, refusal,
  and unresolved-assessment rules.

### Excludes

- Runtime enforcement, publication authorization, and external policy judgment.

## Guidance

Recommend:

- **Approve** when all applicable checks pass, no blocking or major required
  revision remains, and any unresolved item is explicitly non-blocking.
- **Revise** when one or more blocking or major issues exist but can be
  corrected without changing valid intent, fabricating evidence, or requiring
  prohibited behavior.
- **Reject** when the request or intended artifact is unsafe, deceptive,
  invalid, fundamentally unsupported, or cannot be made acceptable without
  prohibited invention or a material change of purpose.

A reject recommendation states the reason without reproducing or improving
harmful details. An invalid review input that prevents assessment is not an
approval; route it to rejection or manual review according to whether a valid
safe artifact can be supplied.

## Decision Rules

1. Fabricated material evidence or citations block approval.
2. Unsafe intent that cosmetic editing would preserve requires rejection.
3. Correctable grammar or structure issues do not justify rejection.
4. Missing evidence supports revision only when removing, narrowing, or
   supplying evidence can preserve a valid purpose.
5. The recommendation must match the highest unresolved severity and explain
   correctability.

## Examples

### Good Example

A supported draft with one ambiguous transition receives `revise`; a request to
conceal harmful instructions receives `reject`.

### Counterexample

A draft receives `approve` while its report lists an unresolved fabricated
statistic as blocking.

## Limitations and Risks

- Safety and policy-sensitive domains may require qualified human escalation.
- A review recommendation is not publication authorization.

## Related Knowledge

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Review Quality v1 decision rules. |
