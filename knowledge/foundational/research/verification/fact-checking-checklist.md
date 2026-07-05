# Fact Checking Checklist

- **Knowledge ID:** `kb:foundational:research:verification:fact-checking-checklist`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `research`
- **Topic:** `verification`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Provides the pre-delivery checks for material claims in a Research v1 brief.

## Applies To

- skill:research
- workflow:research-topic-to-brief

## Scope

### Includes

- Identity, provenance, quotation, number, date, context, method, contradiction,
  inference, citation, and freshness checks on supplied material.

### Excludes

- Live verification, contacting authors, source retrieval, and specialist audit.

## Guidance

For each material claim, check:

1. **Identity:** source and author or organization are identifiable.
2. **Provenance:** how the source and note entered the brief is recorded.
3. **Fidelity:** quotations, numbers, units, dates, names, and locators match the
   supplied evidence note.
4. **Context:** qualifiers, denominator, comparison, population, period, and
   relevant exclusions are preserved.
5. **Method:** the source method is sufficient for the use claimed, or its
   limitation is explicit.
6. **Independence:** apparent corroboration is not circular or derivative.
7. **Contradiction:** credible contrary evidence is mapped and visible.
8. **Inference:** analysis is labeled and does not outrun its premises.
9. **Citation:** a reader can locate the supplied source record and evidence.
10. **Freshness and applicability:** staleness or scope mismatch is explicit.

The quality report must say `checked-against-supplied-material`, `incomplete`,
or `not-checkable`; it must not say independently verified.

## Decision Rules

1. A failed identity, fidelity, or citation check blocks a material claim.
2. A method or applicability limitation lowers confidence or narrows the claim.
3. Unresolved contradictions must appear in both the map and brief limitations.
4. High-stakes claims require qualified human review even when this checklist
   passes.

## Examples

### Good Example

A percentage is withheld because the evidence note omits its denominator, and
the gap requests the underlying table.

### Counterexample

A note labeled “industry report” is treated as independently verified despite
having no title, author, date, or locator.

## Limitations and Risks

- These checks evaluate supplied records, not inaccessible originals.
- Domain-specific verification requirements remain outside Research v1.

## Related Knowledge

- kb:foundational:research:sources:source-reliability-criteria
- kb:foundational:research:citations:citation-expectations

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Research v1 fact-checking checklist. |
