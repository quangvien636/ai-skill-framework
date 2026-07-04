# Index Selection

- **Knowledge ID:** `kb:technical:databases:indexing:index-selection`
- **Status:** Draft
- **Category:** `technical`
- **Domain:** `databases`
- **Topic:** `indexing`
- **Version:** 0.1.0
- **Last updated:** 2026-07-04

## Summary

Explains how to choose which columns to index based on observed query
patterns rather than guessing.

## Applies To

- skill:optimize-query
- workflow:review-schema-change

## Scope

### Includes

- Single-column and composite index selection.

### Excludes

- Storage-engine-specific index tuning.

## Guidance

Add an index only after measuring a slow query. Prefer the smallest index
that satisfies the query's filter and sort columns.

## Decision Rules

1. If a query filters on one column and that column is not already
   indexed, add a single-column index.
2. If a query filters on two columns together, prefer one composite index
   over two single-column indexes.

## Examples

### Good Example

Measuring a slow query, then adding a composite index on the two columns
the query filters by.

### Counterexample

Indexing every column in a table without measuring any query.

## Limitations and Risks

- Extra indexes slow down writes; do not over-index a write-heavy table.

## Related Knowledge

- kb:technical:databases:query-optimization:index-selection

## Sources

- None - repository-authored guidance

## Review Checklist

- [ ] The document covers one primary reusable subject.

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 0.1.0 | 2026-07-04 | Initial draft. |
