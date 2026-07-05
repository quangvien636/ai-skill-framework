# Source Reliability Criteria

- **Knowledge ID:** `kb:foundational:research:sources:source-reliability-criteria`
- **Status:** Active
- **Category:** `foundational`
- **Domain:** `research`
- **Topic:** `sources`
- **Version:** 1.0.0
- **Last updated:** 2026-07-05

## Summary

Provides a consistent, explainable method for assessing supplied sources
without treating source reputation as proof of every claim.

## Applies To

- skill:research
- workflow:research-topic-to-brief

## Scope

### Includes

- Authority, proximity, method transparency, recency, independence, incentives,
  corroboration, completeness, and applicability.

### Excludes

- Automated reputation scores, domain blocklists, and live source inspection.

## Guidance

Assess each source on these dimensions:

- **Identity and provenance:** the creator, publisher, date, and route by which
  the source was supplied are identifiable.
- **Authority and proximity:** the creator has relevant expertise or direct
  access to the event, data, or population.
- **Method transparency:** collection, sample, definitions, analysis, and
  limitations are inspectable enough to evaluate.
- **Recency and applicability:** the evidence fits the question's period,
  geography, population, and context.
- **Independence and incentives:** funding, advocacy, commercial interest, and
  dependence on other cited sources are visible.
- **Corroboration and completeness:** independent evidence agrees, disagrees,
  or remains absent; material context is not selectively omitted.

Record a reasoned rank of `high`, `medium`, `low`, or `unassessable`. The rank
describes fitness for the current research use, not universal quality.

## Decision Rules

1. Mark a source `unassessable` when identity or provenance is insufficient.
2. Prefer primary evidence for what happened and qualified synthesis for what
   a body of evidence means.
3. Do not count several sources derived from one origin as independent
   corroboration.
4. Evaluate a high-reliability source's individual claims for relevance and
   support; do not inherit truth from reputation.

## Examples

### Good Example

An internal dashboard is ranked medium for a team-specific trend because it is
proximate and dated, while its definitions and extraction method remain
unclear.

### Counterexample

A source is ranked high solely because its publisher is well known.

## Limitations and Risks

- Caller-supplied metadata may itself be incomplete or inaccurate.
- Different questions can justify different rankings for the same source.

## Related Knowledge


## Sources

- None - repository-authored guidance

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-05 | Initial Research v1 reliability criteria. |
