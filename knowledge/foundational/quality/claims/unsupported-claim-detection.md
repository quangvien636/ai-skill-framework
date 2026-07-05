# Unsupported Claim Detection

- **Knowledge ID:** `kb:foundational:quality:claims:unsupported-claim-detection`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `quality`
- **Topic:** `claims`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines how to identify unsupported, overstated, contradictory, fabricated, and
mis-cited claims using only caller-supplied evidence.

## Applies To

- skill:review-quality
- workflow:draft-to-reviewed-package

## Scope

### Includes

- Material claim extraction, support checks, citation alignment, qualifiers,
  inference, contradiction, and evidence gaps.

### Excludes

- Browsing, source retrieval, external fact-checking, and authenticity proof.

## Guidance

Extract material claims that affect audience belief or action: statistics,
causal statements, comparisons, quotations, capabilities, testimonials,
dates, predictions, safety assertions, and research conclusions. For each,
classify it as:

- `aligned` when supplied evidence supports the bounded wording;
- `overstated` when evidence supports a narrower claim;
- `contradicted` when supplied evidence materially disagrees;
- `unsupported` when no supplied evidence supports it;
- `not-assessable` when evidence identity, context, or locator is insufficient.

Check that citations resolve to supplied records and actually support the nearby
claim. Reliability of a source and support for a claim remain separate.

## Decision Rules

1. Never repair an unsupported claim by inventing evidence or a citation.
2. Preserve population, period, denominator, uncertainty, and comparison.
3. Label analyst inference and verify that all premises are supplied.
4. A material fabricated claim or citation is blocking.
5. Route external verification needs to an unresolved item.

## Examples

### Good Example

“Three interviews found terminology problems” is aligned; “customers prefer the
redesign” is flagged as an unsupported generalization.

### Counterexample

A plausible-looking publication is accepted because its title sounds credible.

## Limitations and Risks

- Review v1 checks alignment with supplied material, not real-world truth.
- Hidden or corrupted evidence cannot be detected reliably.

## Related Knowledge

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Review Quality v1 claim detection guidance. |
