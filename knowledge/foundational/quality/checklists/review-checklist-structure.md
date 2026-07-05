# Review Checklist Structure

- **Knowledge ID:** `kb:foundational:quality:checklists:review-checklist-structure`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `quality`
- **Topic:** `checklists`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines a complete, traceable review sequence and the minimum information each
finding must contain.

## Applies To

- skill:review-quality
- workflow:draft-to-reviewed-package

## Scope

### Includes

- Applicability, structure, clarity, logic, evidence, citations, tone, platform
  fit, CTA, pacing, safety, revisions, and disposition.

### Excludes

- Live model execution, browsing, external verification, and publishing.

## Guidance

Start by recording the draft type, brief, audience, platform, evidence supplied,
and constraints. Mark every review dimension `pass`, `fail`, `not-applicable`,
or `not-assessable`; never treat a skipped check as a pass.

Each finding contains a stable identifier, dimension, location, severity,
observation, impact, evidence or rule, and recommended correction. Use severity:

- `blocking` for evidence, safety, contract, or usability failures that prevent
  release;
- `major` for material meaning, logic, structure, or audience-fit problems;
- `minor` for localized clarity, grammar, formatting, or polish issues.

Conclude with required revisions, optional improvements, unresolved items, and
exactly one recommendation.

## Decision Rules

1. Review only applicable dimensions, but explain every `not-assessable` result.
2. Keep observations separate from recommendations.
3. Give each material claim an evidence-alignment result.
4. Do not approve while a blocking or major required revision remains.
5. Preserve the original draft and identify every applied correction.

## Examples

### Good Example

A finding identifies paragraph two, marks its unsupported statistic blocking,
links the absent evidence record, and recommends removal or supplied support.

### Counterexample

“Needs improvement” appears without a location, reason, severity, or correction.

## Limitations and Risks

- Checklist completion does not prove factual truth or policy compliance.
- Domain-specific review may require qualified human expertise.

## Related Knowledge

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Review Quality v1 checklist structure. |
