# Claim Evidence Mapping

- **Knowledge ID:** `kb:foundational:research:evidence:claim-evidence-mapping`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `research`
- **Topic:** `evidence`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Defines how to extract atomic claims and preserve a traceable relationship
between claims, evidence notes, sources, contradictions, and gaps.

## Applies To

- skill:research
- workflow:research-topic-to-brief

## Scope

### Includes

- Claim bounding, evidence direction, provenance, contradiction, inference, and
  support status.

### Excludes

- Automatic information extraction and proof that supplied evidence is genuine.

## Guidance

Write each claim so it can be assessed independently. Preserve qualifiers,
population, period, comparison, and measurement. For every material claim,
record:

- a stable claim identifier and exact bounded wording;
- status: `supported`, `partially-supported`, `contradicted`, `mixed`, or
  `unsupported`;
- supporting and contradicting evidence-note identifiers;
- source identifiers and precise locators;
- whether the claim is a direct observation, source assertion, or inference;
- confidence and a short rationale;
- missing evidence needed to change the assessment.

Evidence can support one part of a compound statement and fail to support
another. Split the statement instead of averaging the support.

## Decision Rules

1. No material finding may exist without a claim-map entry.
2. Evidence direction must be explicit; a relevant source is not necessarily
   supporting evidence.
3. Preserve contradictory evidence unless a documented scope or method reason
   makes it inapplicable.
4. Label derived conclusions as inference and map the premises used.
5. If a citation cannot identify the evidence, mark the claim unsupported.

## Examples

### Good Example

“Setup tickets declined in June for Team A” links to a dated dashboard row and
does not become “the redesign reduced support demand.”

### Counterexample

“Customers prefer the redesign” cites an entire interview folder with no
locator, population, evidence note, or contrary observation.

## Limitations and Risks

- Traceability improves auditability but cannot repair weak source methods.
- Claim granularity requires judgment; overly broad and trivial claims both
  reduce usefulness.

## Related Knowledge

- kb:foundational:research:citations:citation-expectations
- kb:foundational:research:uncertainty:uncertainty-language

## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Research v1 claim mapping guidance. |
