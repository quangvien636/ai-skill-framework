# Revision Recommendation Patterns

- **Knowledge ID:** `kb:foundational:quality:revisions:revision-recommendation-patterns`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `quality`
- **Topic:** `revisions`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines actionable, bounded ways to recommend corrections without silently
changing material intent or inventing support.

## Applies To

- skill:review-quality
- workflow:draft-to-reviewed-package

## Scope

### Includes

- Remove, narrow, clarify, reorder, separate, support, label, replace, and
  escalate patterns.

### Excludes

- Full undeclared rewrites and evidence creation.

## Guidance

Use the smallest pattern that resolves the finding:

- **Remove** unsupported or unnecessary material.
- **Narrow** a claim to the population, period, or certainty supplied.
- **Clarify** ambiguous wording while preserving meaning.
- **Reorder** sections to restore logic or audience flow.
- **Separate** observation, inference, recommendation, and limitation.
- **Support** by requesting a specific missing evidence record or citation.
- **Label** assumptions, uncertainty, sponsorship, or unresolved verification.
- **Replace** a deceptive hook or vague CTA with a supported, proportional one.
- **Escalate** high-stakes, unsafe, policy-sensitive, or externally unverifiable
  issues to qualified human review.

Every recommendation states the location, required outcome, acceptable boundary,
and reason. It need not prescribe exact prose when several valid fixes exist.

## Decision Rules

1. Required revisions resolve blocking or major findings; optional improvements
   address minor polish.
2. Never request invented facts, quotations, citations, or policies.
3. Do not disguise a change in conclusion as copyediting.
4. Group duplicates but preserve distinct impacts.
5. Order required revisions by safety, factual integrity, contract, then craft.

## Examples

### Good Example

“Narrow paragraph three to the one-team, four-week pilot or supply evidence for
the organization-wide conclusion.”

### Counterexample

“Make it stronger and add some impressive statistics.”

## Limitations and Risks

- Some revisions require author or subject-matter-owner decisions.
- Mechanical corrections can still alter meaning if applied carelessly.

## Related Knowledge

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Review Quality v1 revision patterns. |
